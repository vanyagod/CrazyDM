"""
Менеджер уведомлений
"""

import asyncio
import logging
import platform
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from enum import Enum

from api.models import SearchResult
from config.settings import Settings

logger = logging.getLogger(__name__)


class NotificationType(str, Enum):
    """Типы уведомлений"""
    GOOD_DEAL = "good_deal"
    PRICE_DROP = "price_drop"
    NEW_LISTING = "new_listing"
    SEARCH_COMPLETE = "search_complete"
    ERROR = "error"
    INFO = "info"


class NotificationManager:
    """Менеджер уведомлений"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.enabled = settings.enable_notifications
        self.callbacks: Dict[NotificationType, List[Callable]] = {}
        
        # Инициализация системных уведомлений
        self._init_system_notifications()
    
    def _init_system_notifications(self):
        """Инициализация системных уведомлений"""
        try:
            if platform.system() == "Windows":
                try:
                    import win10toast
                    self.toaster = win10toast.ToastNotifier()
                    self.system_notifications = True
                except ImportError:
                    logger.warning("win10toast not available, system notifications disabled")
                    self.system_notifications = False
            
            elif platform.system() == "Linux":
                try:
                    import subprocess
                    # Проверяем наличие notify-send
                    result = subprocess.run(["which", "notify-send"], capture_output=True)
                    self.system_notifications = result.returncode == 0
                except:
                    self.system_notifications = False
            
            elif platform.system() == "Darwin":  # macOS
                try:
                    import subprocess
                    # Проверяем наличие osascript
                    result = subprocess.run(["which", "osascript"], capture_output=True)
                    self.system_notifications = result.returncode == 0
                except:
                    self.system_notifications = False
            
            else:
                self.system_notifications = False
                
        except Exception as e:
            logger.error(f"Failed to initialize system notifications: {e}")
            self.system_notifications = False
    
    def add_callback(self, notification_type: NotificationType, callback: Callable):
        """Добавить колбэк для типа уведомления"""
        if notification_type not in self.callbacks:
            self.callbacks[notification_type] = []
        
        self.callbacks[notification_type].append(callback)
    
    def remove_callback(self, notification_type: NotificationType, callback: Callable):
        """Удалить колбэк"""
        if notification_type in self.callbacks:
            try:
                self.callbacks[notification_type].remove(callback)
            except ValueError:
                pass
    
    async def notify(
        self, 
        notification_type: NotificationType,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ):
        """Отправить уведомление"""
        if not self.enabled:
            return
        
        logger.info(f"Notification [{notification_type}]: {title} - {message}")
        
        # Вызываем колбэки
        if notification_type in self.callbacks:
            for callback in self.callbacks[notification_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(notification_type, title, message, data)
                    else:
                        callback(notification_type, title, message, data)
                except Exception as e:
                    logger.error(f"Error in notification callback: {e}")
        
        # Системное уведомление
        if self.system_notifications:
            await self._send_system_notification(title, message)
        
        # Discord webhook (если настроен)
        if self.settings.discord_webhook_url:
            await self._send_discord_notification(title, message, notification_type)
        
        # Звуковое уведомление
        if self.settings.notification_sound:
            self._play_notification_sound()
    
    async def _send_system_notification(self, title: str, message: str):
        """Отправить системное уведомление"""
        try:
            if platform.system() == "Windows" and hasattr(self, 'toaster'):
                # Windows Toast
                self.toaster.show_toast(
                    title=title,
                    msg=message,
                    duration=5,
                    threaded=True
                )
            
            elif platform.system() == "Linux":
                # Linux notify-send
                import subprocess
                subprocess.Popen([
                    "notify-send", 
                    title, 
                    message,
                    "--expire-time=5000"
                ])
            
            elif platform.system() == "Darwin":
                # macOS osascript
                import subprocess
                script = f'display notification "{message}" with title "{title}"'
                subprocess.Popen(["osascript", "-e", script])
                
        except Exception as e:
            logger.error(f"Failed to send system notification: {e}")
    
    async def _send_discord_notification(
        self, 
        title: str, 
        message: str, 
        notification_type: NotificationType
    ):
        """Отправить уведомление в Discord"""
        try:
            import aiohttp
            
            # Цвета для разных типов уведомлений
            colors = {
                NotificationType.GOOD_DEAL: 0x00ff00,  # Зеленый
                NotificationType.PRICE_DROP: 0x0099ff,  # Синий
                NotificationType.NEW_LISTING: 0xffff00,  # Желтый
                NotificationType.ERROR: 0xff0000,  # Красный
                NotificationType.INFO: 0x888888,  # Серый
            }
            
            embed = {
                "title": title,
                "description": message,
                "color": colors.get(notification_type, 0x888888),
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {
                    "text": "PoE2 Trade Assistant"
                }
            }
            
            payload = {
                "embeds": [embed]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.settings.discord_webhook_url, 
                    json=payload
                ) as response:
                    if response.status != 204:
                        logger.warning(f"Discord webhook failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"Failed to send Discord notification: {e}")
    
    def _play_notification_sound(self):
        """Воспроизвести звук уведомления"""
        try:
            if platform.system() == "Windows":
                import winsound
                winsound.MessageBeep(winsound.MB_OK)
            
            elif platform.system() == "Darwin":
                import subprocess
                subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"])
            
            elif platform.system() == "Linux":
                import subprocess
                # Попробуем несколько вариантов
                for cmd in [["paplay", "/usr/share/sounds/alsa/Front_Left.wav"],
                           ["aplay", "/usr/share/sounds/alsa/Front_Left.wav"],
                           ["canberra-gtk-play", "-i", "message"]]:
                    try:
                        subprocess.run(cmd, check=True, capture_output=True)
                        break
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
                        
        except Exception as e:
            logger.debug(f"Could not play notification sound: {e}")
    
    async def notify_good_deal(self, item: SearchResult):
        """Уведомление о выгодном предложении"""
        title = "🎯 Выгодное предложение!"
        
        item_name = item.item.name or "Unknown Item"
        price_str = f"{item.price.amount:.1f} {item.price.currency}" if item.price else "N/A"
        
        message = f"{item_name} за {price_str}"
        
        await self.notify(
            NotificationType.GOOD_DEAL,
            title,
            message,
            {"item": item}
        )
    
    async def notify_price_drop(self, item: SearchResult, old_price: float, new_price: float):
        """Уведомление о снижении цены"""
        title = "📉 Снижение цены!"
        
        item_name = item.item.name or "Unknown Item"
        drop_percent = ((old_price - new_price) / old_price) * 100
        
        message = f"{item_name}: {old_price:.1f} → {new_price:.1f} (-{drop_percent:.1f}%)"
        
        await self.notify(
            NotificationType.PRICE_DROP,
            title,
            message,
            {"item": item, "old_price": old_price, "new_price": new_price}
        )
    
    async def notify_new_listing(self, item: SearchResult):
        """Уведомление о новом объявлении"""
        title = "🆕 Новое объявление"
        
        item_name = item.item.name or "Unknown Item"
        price_str = f"{item.price.amount:.1f} {item.price.currency}" if item.price else "N/A"
        
        message = f"{item_name} за {price_str}"
        
        await self.notify(
            NotificationType.NEW_LISTING,
            title,
            message,
            {"item": item}
        )
    
    async def notify_search_complete(self, results_count: int, search_query: str):
        """Уведомление о завершении поиска"""
        title = "✅ Поиск завершен"
        message = f"Найдено {results_count} предметов для запроса: {search_query}"
        
        await self.notify(
            NotificationType.SEARCH_COMPLETE,
            title,
            message,
            {"results_count": results_count, "query": search_query}
        )
    
    async def notify_error(self, error_message: str):
        """Уведомление об ошибке"""
        title = "❌ Ошибка"
        
        await self.notify(
            NotificationType.ERROR,
            title,
            error_message
        )
    
    async def notify_info(self, info_message: str):
        """Информационное уведомление"""
        title = "ℹ️ Информация"
        
        await self.notify(
            NotificationType.INFO,
            title,
            info_message
        )
    
    def enable(self):
        """Включить уведомления"""
        self.enabled = True
        logger.info("Notifications enabled")
    
    def disable(self):
        """Отключить уведомления"""
        self.enabled = False
        logger.info("Notifications disabled")
    
    def is_enabled(self) -> bool:
        """Проверить, включены ли уведомления"""
        return self.enabled