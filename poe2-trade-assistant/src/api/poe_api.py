"""
API клиент для взаимодействия с торговой системой Path of Exile
"""

import asyncio
import aiohttp
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

from .models import Item, SearchResult, SearchQuery, LeagueInfo, PriceData, TradeStats
from config.settings import Settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Ограничитель скорости запросов"""
    
    def __init__(self, delay: float = 1.0):
        self.delay = delay
        self.last_request = datetime.min
    
    async def wait(self):
        """Ждем перед следующим запросом"""
        now = datetime.now()
        time_since_last = (now - self.last_request).total_seconds()
        
        if time_since_last < self.delay:
            wait_time = self.delay - time_since_last
            await asyncio.sleep(wait_time)
        
        self.last_request = datetime.now()


class PoEAPI:
    """Клиент для работы с API Path of Exile"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.rate_limiter = RateLimiter(settings.request_delay)
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Кэш для статических данных
        self._leagues_cache = None
        self._stats_cache = None
        self._cache_time = None
        self._cache_duration = timedelta(hours=1)
    
    async def __aenter__(self):
        """Асинхронный контекст-менеджер"""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрытие сессии"""
        if self.session:
            await self.session.close()
    
    async def _ensure_session(self):
        """Создать сессию если её нет"""
        if not self.session or self.session.closed:
            connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
            timeout = aiohttp.ClientTimeout(total=30)
            
            self.session = aiohttp.ClientSession(
                headers=self.settings.get_headers(),
                connector=connector,
                timeout=timeout
            )
    
    async def _make_request(
        self, 
        method: str, 
        url: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """Выполнить HTTP запрос с ограничением скорости"""
        await self._ensure_session()
        await self.rate_limiter.wait()
        
        for attempt in range(self.settings.max_retries):
            try:
                logger.debug(f"Making {method} request to {url}")
                
                async with self.session.request(method, url, **kwargs) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.debug(f"Request successful: {response.status}")
                        return data
                    
                    elif response.status == 429:  # Rate limited
                        wait_time = int(response.headers.get('Retry-After', 5))
                        logger.warning(f"Rate limited, waiting {wait_time}s")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    else:
                        error_text = await response.text()
                        logger.error(f"Request failed: {response.status} - {error_text}")
                        response.raise_for_status()
            
            except asyncio.TimeoutError:
                logger.warning(f"Request timeout (attempt {attempt + 1})")
                if attempt == self.settings.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
            
            except aiohttp.ClientError as e:
                logger.error(f"Request error: {e}")
                if attempt == self.settings.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
        
        raise Exception(f"Failed to complete request after {self.settings.max_retries} attempts")
    
    async def get_leagues(self, type_filter: str = "main") -> List[LeagueInfo]:
        """Получить список лиг"""
        # Проверяем кэш
        if (self._leagues_cache and self._cache_time and 
            datetime.now() - self._cache_time < self._cache_duration):
            return self._leagues_cache
        
        url = f"{self.settings.poe_api_base_url}/leagues"
        params = {"type": type_filter}
        
        data = await self._make_request("GET", url, params=params)
        leagues = [LeagueInfo(**league) for league in data]
        
        # Обновляем кэш
        self._leagues_cache = leagues
        self._cache_time = datetime.now()
        
        return leagues
    
    async def get_stats(self) -> Dict[str, Any]:
        """Получить статические данные (моды, базовые типы и т.д.)"""
        if (self._stats_cache and self._cache_time and 
            datetime.now() - self._cache_time < self._cache_duration):
            return self._stats_cache
        
        url = f"{self.settings.poe_api_base_url}/stats"
        data = await self._make_request("GET", url)
        
        self._stats_cache = data
        self._cache_time = datetime.now()
        
        return data
    
    async def search_items(
        self,
        league: str,
        name: Optional[str] = None,
        type_filter: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        currency: str = "chaos",
        **filters
    ) -> List[SearchResult]:
        """Поиск предметов"""
        
        # Формируем запрос поиска
        query = {
            "status": {"option": "online"},  # Только онлайн продавцы
            "stats": [{"type": "and", "filters": []}]
        }
        
        # Фильтр по имени
        if name:
            query["name"] = name
        
        # Фильтр по типу
        if type_filter:
            query["type"] = type_filter
        
        # Фильтр по цене
        if min_price is not None or max_price is not None:
            price_filter = {"filters": {"price": {}}}
            
            if min_price is not None:
                price_filter["filters"]["price"]["min"] = min_price
            if max_price is not None:
                price_filter["filters"]["price"]["max"] = max_price
            
            price_filter["filters"]["price"]["option"] = currency
            query["stats"][0]["filters"].append(price_filter)
        
        # Дополнительные фильтры
        for key, value in filters.items():
            if value is not None:
                query["filters"][key] = value
        
        search_query = SearchQuery(query=query)
        
        # Выполняем поиск
        search_url = f"{self.settings.poe_api_base_url}/search/{league}"
        
        logger.info(f"Searching items in {league} with query: {search_query.query}")
        
        search_response = await self._make_request(
            "POST", 
            search_url, 
            json=search_query.dict()
        )
        
        # Получаем ID найденных предметов
        result_ids = search_response.get("result", [])[:50]  # Ограничиваем первыми 50
        
        if not result_ids:
            logger.info("No items found")
            return []
        
        # Получаем детальную информацию о предметах
        fetch_url = f"{self.settings.poe_api_base_url}/fetch/{','.join(result_ids)}"
        
        fetch_response = await self._make_request("GET", fetch_url)
        
        # Парсим результаты
        results = []
        for item_data in fetch_response.get("result", []):
            try:
                item = Item(**item_data["item"])
                
                # Парсим цену
                price = None
                if "listing" in item_data and "price" in item_data["listing"]:
                    price_data = item_data["listing"]["price"]
                    price = PriceData(
                        amount=price_data.get("amount", 0),
                        currency=price_data.get("currency", "chaos"),
                        type=price_data.get("type", "fixed")
                    )
                
                # Создаем результат
                result = SearchResult(
                    item=item,
                    listing=item_data.get("listing", {}),
                    price=price,
                    indexed_at=datetime.fromisoformat(
                        item_data["listing"]["indexed"].replace("Z", "+00:00")
                    ) if "listing" in item_data and "indexed" in item_data["listing"] else None
                )
                
                results.append(result)
                
            except Exception as e:
                logger.warning(f"Failed to parse item: {e}")
                continue
        
        logger.info(f"Found {len(results)} items")
        return results
    
    async def get_item_details(self, item_id: str) -> Optional[Item]:
        """Получить детальную информацию о предмете"""
        url = f"{self.settings.poe_api_base_url}/fetch/{item_id}"
        
        try:
            data = await self._make_request("GET", url)
            
            if data.get("result") and len(data["result"]) > 0:
                item_data = data["result"][0]["item"]
                return Item(**item_data)
            
        except Exception as e:
            logger.error(f"Failed to get item details for {item_id}: {e}")
        
        return None
    
    async def get_exchange_rates(self, league: str) -> Dict[str, float]:
        """Получить курсы валют"""
        # Это упрощенная версия - в реальности нужно парсить данные с торговой площадки
        # или использовать сторонние API для получения актуальных курсов
        
        default_rates = {
            "chaos": 1.0,
            "divine": 200.0,
            "exalted": 150.0,
            "ancient": 0.1,
            "fusing": 0.5,
            "chromatic": 0.1,
            "jeweller": 0.1,
            "alteration": 0.2,
            "alchemy": 0.3,
            "blessed": 0.5,
            "regret": 2.0,
            "regal": 1.5,
            "vaal": 1.0,
            "chisel": 0.5,
        }
        
        # TODO: Реализовать получение актуальных курсов
        logger.warning("Using default exchange rates - implement actual rate fetching")
        
        return default_rates
    
    async def close(self):
        """Закрыть соединение"""
        if self.session:
            await self.session.close()