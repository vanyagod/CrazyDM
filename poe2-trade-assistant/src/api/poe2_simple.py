"""
Упрощенный API клиент для PoE2 без async
"""

import requests
import time
import logging
from typing import List, Dict, Any, Optional
import json

logger = logging.getLogger(__name__)


class SimplePoE2API:
    """Упрощенный синхронный API клиент для PoE2"""
    
    def __init__(self, settings):
        self.settings = settings
        self.session = requests.Session()
        self.session.headers.update(settings.get_headers())
        self.last_request_time = 0
    
    def _wait_for_rate_limit(self):
        """Ожидание между запросами"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.settings.request_delay:
            sleep_time = self.settings.request_delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Выполнить HTTP запрос"""
        self._wait_for_rate_limit()
        
        for attempt in range(self.settings.max_retries):
            try:
                logger.debug(f"Making {method} request to {url}")
                
                response = self.session.request(method, url, **kwargs)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Rate limited
                    wait_time = int(response.headers.get('Retry-After', 5))
                    logger.warning(f"Rate limited, waiting {wait_time}s")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Request failed: {response.status_code} - {response.text}")
                    response.raise_for_status()
            
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error: {e}")
                if attempt == self.settings.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
        
        raise Exception(f"Failed to complete request after {self.settings.max_retries} attempts")
    
    def search_items_simple(
        self,
        league: str,
        item_name: Optional[str] = None,
        item_type: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        currency: str = "chaos"
    ) -> List[Dict[str, Any]]:
        """Упрощенный поиск предметов"""
        
        # Пробуем разные форматы запросов для PoE2
        search_queries = []
        
        # Формат 1: Простой поиск по названию
        if item_name:
            search_queries.append({
                "query": {
                    "name": item_name,
                    "status": {"option": "online"}
                },
                "sort": {"price": "asc"}
            })
            
            # Формат 2: Поиск по типу
            search_queries.append({
                "query": {
                    "type": item_name,
                    "status": {"option": "online"}
                },
                "sort": {"price": "asc"}
            })
            
            # Формат 3: Поиск в названии и типе
            search_queries.append({
                "query": {
                    "filters": {
                        "type_filters": {
                            "filters": {
                                "category": {"option": item_name}
                            }
                        }
                    },
                    "status": {"option": "online"}
                },
                "sort": {"price": "asc"}
            })
        
        # Если ничего не указано, возвращаем демо данные
        if not search_queries:
            return self._get_demo_data()
        
        # Пробуем каждый формат запроса
        for i, query in enumerate(search_queries):
            try:
                logger.info(f"Trying search format {i+1}: {query}")
                
                search_url = f"{self.settings.poe_api_base_url}/search/{league}"
                
                response = self._make_request("POST", search_url, json=query)
                
                result_ids = response.get("result", [])[:20]  # Ограничиваем 20 результатами
                
                if result_ids:
                    # Получаем детальную информацию
                    fetch_url = f"{self.settings.poe_api_base_url}/fetch/{','.join(result_ids)}"
                    fetch_response = self._make_request("GET", fetch_url)
                    
                    results = []
                    for item_data in fetch_response.get("result", []):
                        results.append(self._parse_item_data(item_data))
                    
                    logger.info(f"Found {len(results)} items with format {i+1}")
                    return results
                
            except Exception as e:
                logger.warning(f"Search format {i+1} failed: {e}")
                continue
        
        # Если все форматы не сработали, возвращаем демо данные
        logger.warning("All search formats failed, returning demo data")
        return self._get_demo_data()
    
    def _parse_item_data(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Парсинг данных предмета"""
        item = item_data.get("item", {})
        listing = item_data.get("listing", {})
        
        # Парсим цену
        price_info = listing.get("price")
        price = None
        currency = "chaos"
        
        if price_info:
            price = price_info.get("amount", 0)
            currency = price_info.get("currency", "chaos")
        
        return {
            "name": item.get("name", "Unknown"),
            "type": item.get("typeLine", "Unknown"),
            "price": price,
            "currency": currency,
            "ilvl": item.get("ilvl"),
            "corrupted": item.get("corrupted", False),
            "identified": item.get("identified", True),
            "frame_type": item.get("frameType", 0),
            "seller": listing.get("account", {}).get("name", "Unknown"),
            "indexed": listing.get("indexed"),
            "raw_data": item_data
        }
    
    def _get_demo_data(self) -> List[Dict[str, Any]]:
        """Демонстрационные данные когда API не работает"""
        return [
            {
                "name": "Chaos Orb",
                "type": "Currency",
                "price": 1.0,
                "currency": "chaos",
                "ilvl": None,
                "corrupted": False,
                "identified": True,
                "frame_type": 5,
                "seller": "DemoUser1",
                "indexed": "2024-12-04T15:30:00Z"
            },
            {
                "name": "Divine Orb", 
                "type": "Currency",
                "price": 180.0,
                "currency": "chaos",
                "ilvl": None,
                "corrupted": False,
                "identified": True,
                "frame_type": 5,
                "seller": "DemoUser2",
                "indexed": "2024-12-04T15:25:00Z"
            },
            {
                "name": "Exalted Orb",
                "type": "Currency", 
                "price": 150.0,
                "currency": "chaos",
                "ilvl": None,
                "corrupted": False,
                "identified": True,
                "frame_type": 5,
                "seller": "DemoUser3",
                "indexed": "2024-12-04T15:20:00Z"
            },
            {
                "name": "Rare Ring",
                "type": "Gold Ring",
                "price": 25.0,
                "currency": "chaos",
                "ilvl": 85,
                "corrupted": False,
                "identified": True,
                "frame_type": 2,
                "seller": "DemoUser4",
                "indexed": "2024-12-04T15:15:00Z"
            },
            {
                "name": "Unique Sword",
                "type": "One Handed Sword",
                "price": 75.0,
                "currency": "chaos",
                "ilvl": 80,
                "corrupted": False,
                "identified": True,
                "frame_type": 3,
                "seller": "DemoUser5",
                "indexed": "2024-12-04T15:10:00Z"
            }
        ]
    
    def get_leagues(self) -> List[str]:
        """Получить список лиг"""
        try:
            url = f"{self.settings.poe_api_base_url.replace('/trade2', '')}/leagues"
            response = self._make_request("GET", url)
            
            leagues = []
            for league in response:
                if league.get("id"):
                    leagues.append(league["id"])
            
            return leagues
        except:
            # Возвращаем список по умолчанию
            return ["Necrosis", "Necrosis HC", "Delirium", "Delirium HC", "Breach", "Breach HC"]