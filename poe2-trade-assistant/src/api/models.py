"""
Модели данных для API
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class PriceData(BaseModel):
    """Модель данных о цене"""
    amount: float
    currency: str
    type: str = "fixed"  # fixed, negotiable, etc.


class ItemProperty(BaseModel):
    """Свойство предмета"""
    name: str
    values: List[List[Any]]
    display_mode: int = 0
    type: Optional[int] = None


class ItemRequirement(BaseModel):
    """Требования к предмету"""
    name: str
    values: List[List[Any]]
    display_mode: int = 0


class ItemSocket(BaseModel):
    """Сокет предмета"""
    group: int
    attr: str  # S, D, I, G (Strength, Dexterity, Intelligence, Generic)
    sColour: str  # R, G, B, W (Red, Green, Blue, White)


class Item(BaseModel):
    """Модель предмета"""
    id: str
    name: str
    type_line: str
    base_type: Optional[str] = None
    identified: bool = True
    ilvl: Optional[int] = None
    corrupted: bool = False
    
    # Свойства и требования
    properties: List[ItemProperty] = []
    requirements: List[ItemRequirement] = []
    implicit_mods: List[str] = []
    explicit_mods: List[str] = []
    
    # Сокеты и связи
    sockets: List[ItemSocket] = []
    socket_links: Optional[int] = None
    
    # Дополнительная информация
    flavour_text: List[str] = []
    frame_type: int = 0  # 0=normal, 1=magic, 2=rare, 3=unique, etc.
    category: Optional[str] = None
    
    # Метаданные
    league: Optional[str] = None
    stash_id: Optional[str] = None
    account_name: Optional[str] = None
    character_name: Optional[str] = None
    
    class Config:
        extra = "allow"


class SearchResult(BaseModel):
    """Результат поиска"""
    item: Item
    listing: Dict[str, Any]
    price: Optional[PriceData] = None
    indexed_at: Optional[datetime] = None
    
    @property
    def price_chaos(self) -> Optional[float]:
        """Цена в хаосах (примерная конвертация)"""
        if not self.price:
            return None
        
        # Простая конвертация валют (нужно будет улучшить)
        currency_rates = {
            "chaos": 1.0,
            "divine": 200.0,  # Примерный курс
            "exalted": 150.0,
            "ancient": 0.1,
            "fusing": 0.5,
            "chromatic": 0.1,
            "jeweller": 0.1,
            "alteration": 0.2,
        }
        
        rate = currency_rates.get(self.price.currency.lower(), 1.0)
        return self.price.amount * rate


class SearchQuery(BaseModel):
    """Запрос поиска предметов"""
    query: Dict[str, Any]
    sort: Dict[str, str] = {"price": "asc"}
    
    
class LeagueInfo(BaseModel):
    """Информация о лиге"""
    id: str
    realm: Optional[str] = None
    description: Optional[str] = None
    category: Optional[Dict[str, Any]] = None
    rules: List[Dict[str, Any]] = []
    register_at: Optional[datetime] = None
    event: bool = False
    url: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    delve_event: bool = False
    
    
class StaticData(BaseModel):
    """Статические данные игры"""
    result: List[Dict[str, Any]]
    
    
class TradeStats(BaseModel):
    """Статистика торговли"""
    total_found: int
    results_shown: int
    search_time: float
    complexity: Optional[int] = None