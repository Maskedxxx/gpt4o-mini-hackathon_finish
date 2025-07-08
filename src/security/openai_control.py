import os
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from src.utils import get_logger

logger = get_logger()


@dataclass
class APIUsageStats:
    """Статистика использования API"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens: int = 0
    last_request_time: Optional[datetime] = None


class OpenAIController:
    """Контроллер для управления доступом к OpenAI API"""
    
    def __init__(self):
        self.enabled = self._get_api_enabled_flag()
        self.usage_stats = APIUsageStats()
        logger.info(f"OpenAI API контроллер инициализирован. Статус: {'ВКЛЮЧЕН' if self.enabled else 'ВЫКЛЮЧЕН'}")
    
    def _get_api_enabled_flag(self) -> bool:
        """Получить флаг разрешения использования OpenAI API"""
        flag = os.getenv("OPENAI_API_ENABLED", "true").lower()
        return flag in ("true", "1", "yes", "on", "enabled")
    
    def is_api_enabled(self) -> bool:
        """Проверить, разрешено ли использование OpenAI API"""
        return self.enabled
    
    def check_api_permission(self) -> None:
        """Проверить разрешение на использование API и выбросить исключение если запрещено"""
        if not self.enabled:
            raise PermissionError(
                "OpenAI API отключен. Для включения установите OPENAI_API_ENABLED=true в переменных окружения."
            )
    
    def record_request(self, success: bool = True, tokens: int = 0, error: Optional[str] = None):
        """Записать статистику запроса к API"""
        self.usage_stats.total_requests += 1
        self.usage_stats.last_request_time = datetime.now()
        
        if success:
            self.usage_stats.successful_requests += 1
            self.usage_stats.total_tokens += tokens
            logger.info(f"OpenAI API запрос успешен. Токенов использовано: {tokens}")
        else:
            self.usage_stats.failed_requests += 1
            logger.warning(f"OpenAI API запрос неудачен: {error}")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Получить статистику использования API"""
        return {
            "api_enabled": self.enabled,
            "total_requests": self.usage_stats.total_requests,
            "successful_requests": self.usage_stats.successful_requests,
            "failed_requests": self.usage_stats.failed_requests,
            "success_rate": (
                self.usage_stats.successful_requests / self.usage_stats.total_requests * 100
                if self.usage_stats.total_requests > 0 else 0
            ),
            "total_tokens_used": self.usage_stats.total_tokens,
            "last_request_time": (
                self.usage_stats.last_request_time.isoformat()
                if self.usage_stats.last_request_time else None
            )
        }
    
    def toggle_api(self, enabled: bool) -> None:
        """Включить/выключить API программно (не рекомендуется для production)"""
        old_status = self.enabled
        self.enabled = enabled
        logger.info(f"OpenAI API статус изменен с {old_status} на {enabled}")
    
    def reset_stats(self) -> None:
        """Сбросить статистику использования"""
        self.usage_stats = APIUsageStats()
        logger.info("Статистика использования OpenAI API сброшена")


# Глобальный экземпляр контроллера
openai_controller = OpenAIController()


def require_openai_api():
    """Декоратор для проверки разрешения использования OpenAI API"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            openai_controller.check_api_permission()
            try:
                result = func(*args, **kwargs)
                # Пытаемся извлечь количество токенов из результата
                tokens = 0
                if hasattr(result, 'usage') and hasattr(result.usage, 'total_tokens'):
                    tokens = result.usage.total_tokens
                
                openai_controller.record_request(success=True, tokens=tokens)
                return result
            except Exception as e:
                openai_controller.record_request(success=False, error=str(e))
                raise
        return wrapper
    return decorator


async def require_openai_api_async():
    """Async декоратор для проверки разрешения использования OpenAI API"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            openai_controller.check_api_permission()
            try:
                result = await func(*args, **kwargs)
                # Пытаемся извлечь количество токенов из результата
                tokens = 0
                if hasattr(result, 'usage') and hasattr(result.usage, 'total_tokens'):
                    tokens = result.usage.total_tokens
                
                openai_controller.record_request(success=True, tokens=tokens)
                return result
            except Exception as e:
                openai_controller.record_request(success=False, error=str(e))
                raise
        return wrapper
    return decorator