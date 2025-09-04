"""
Модуль настроек приложения
"""

import os
from pathlib import Path
from typing import Optional
try:
    from pydantic_settings import BaseSettings
    from pydantic import Field
except ImportError:
    from pydantic import BaseSettings, Field

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        pass

# Загружаем переменные окружения
load_dotenv()

class Settings(BaseSettings):
    """Класс настроек приложения"""
    
    # API настройки
    poe_api_base_url: str = Field(
        default="https://www.pathofexile.com/api/trade",
        env="POE_API_BASE_URL"
    )
    poe2_api_base_url: str = Field(
        default="https://www.pathofexile.com/api/trade2", 
        env="POE2_API_BASE_URL"
    )
    request_delay: float = Field(default=1.0, env="REQUEST_DELAY")
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    
    # База данных
    database_path: str = Field(default="data/trade_data.db", env="DATABASE_PATH")
    
    # Уведомления
    enable_notifications: bool = Field(default=True, env="ENABLE_NOTIFICATIONS")
    notification_sound: bool = Field(default=True, env="NOTIFICATION_SOUND")
    discord_webhook_url: Optional[str] = Field(default=None, env="DISCORD_WEBHOOK_URL")
    
    # UI настройки
    theme: str = Field(default="dark", env="THEME")
    update_interval: int = Field(default=30, env="UPDATE_INTERVAL")
    
    # Фильтры поиска
    max_price: Optional[float] = Field(default=100, env="MAX_PRICE")
    min_price: Optional[float] = Field(default=1, env="MIN_PRICE")
    league: str = Field(default="Hardcore", env="LEAGUE")
    
    # Отладка
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Создаем директории если их нет
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
    
    @property
    def data_dir(self) -> Path:
        """Путь к директории данных"""
        return Path(self.database_path).parent
    
    @property
    def config_dir(self) -> Path:
        """Путь к директории конфигурации"""
        return Path("config")
    
    def get_headers(self) -> dict:
        """Получить заголовки для API запросов"""
        return {
            "User-Agent": "PoE2TradeAssistant/1.0 (Educational Purpose Only)",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }