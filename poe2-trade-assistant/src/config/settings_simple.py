"""
Упрощенные настройки без pydantic
"""

import os
from pathlib import Path
from typing import Optional


class Settings:
    """Упрощенный класс настроек без pydantic"""
    
    def __init__(self):
        # API настройки
        self.poe_api_base_url = os.getenv("POE_API_BASE_URL", "https://www.pathofexile.com/api/trade")
        self.poe2_api_base_url = os.getenv("POE2_API_BASE_URL", "https://www.pathofexile.com/api/trade2")
        self.request_delay = float(os.getenv("REQUEST_DELAY", "1.0"))
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        
        # База данных
        self.database_path = os.getenv("DATABASE_PATH", "data/trade_data.db")
        
        # Уведомления
        self.enable_notifications = os.getenv("ENABLE_NOTIFICATIONS", "true").lower() == "true"
        self.notification_sound = os.getenv("NOTIFICATION_SOUND", "true").lower() == "true"
        self.discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        
        # UI настройки
        self.theme = os.getenv("THEME", "dark")
        self.update_interval = int(os.getenv("UPDATE_INTERVAL", "30"))
        
        # Фильтры поиска
        max_price_str = os.getenv("MAX_PRICE", "100")
        self.max_price = float(max_price_str) if max_price_str else 100.0
        
        min_price_str = os.getenv("MIN_PRICE", "1")
        self.min_price = float(min_price_str) if min_price_str else 1.0
        
        self.league = os.getenv("LEAGUE", "Hardcore")
        
        # Отладка
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
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