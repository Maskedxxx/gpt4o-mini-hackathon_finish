# src/hh/token_manager.py
import logging
import time
from pathlib import Path
from typing import Dict, Optional, Tuple

from src.hh.token_refresher import HHTokenRefresher

# Настройка логирования
log_dir = Path("LOGS")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "hh_token_manager.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("hh_token_manager")

class HHTokenManager:
    """Менеджер для управления токенами доступа HH.ru."""
    
    def __init__(self, access_token: str, refresh_token: str, expires_in: int):
        """
        Инициализация менеджера токенов.
        
        Args:
            access_token: Токен доступа
            refresh_token: Токен обновления
            expires_in: Время жизни токена в секундах
        """
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_at = time.time() + expires_in
        self.token_refresher = HHTokenRefresher(refresh_token)
        
    async def get_valid_tokens(self) -> Tuple[str, str]:
        """
        Получение действительных токенов, при необходимости с обновлением.
        
        Returns:
            Tuple[str, str]: Пара (access_token, refresh_token)
        """
        # Проверяем, не истекает ли токен в ближайшие 5 минут
        if time.time() + 300 >= self.expires_at:
            logger.info("Токен скоро истечет, выполняется обновление")
            tokens = await self.token_refresher.refresh()
            
            self.access_token = tokens['access_token']
            self.refresh_token = tokens['refresh_token']
            self.expires_at = time.time() + tokens['expires_in']
            self.token_refresher = HHTokenRefresher(self.refresh_token)
            
            logger.info("Токены успешно обновлены")
            
        return self.access_token, self.refresh_token