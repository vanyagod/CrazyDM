"""
Автономные настройки без внешних зависимостей
"""

import os
from pathlib import Path
from typing import Optional


class Settings:
    """Автономный класс настроек без pydantic"""
    
    def __init__(self):
        # Загружаем .env файл если есть
        self._load_env_file()
        
        # API настройки для PoE2
        self.poe_api_base_url = os.getenv("POE_API_BASE_URL", "https://www.pathofexile.com/api/trade2")
        self.poe2_api_base_url = os.getenv("POE2_API_BASE_URL", "https://www.pathofexile.com/api/trade2")
        self.request_delay = float(os.getenv("REQUEST_DELAY", "2.0"))
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
        
        self.league = os.getenv("LEAGUE", "Necrosis")
        
        # Отладка
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # Создаем директории если их нет
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _load_env_file(self):
        """Загрузка .env файла без python-dotenv"""
        env_path = Path(".env")
        if env_path.exists():
            try:
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            os.environ[key] = value
            except Exception as e:
                print(f"Warning: Could not load .env file: {e}")
    
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