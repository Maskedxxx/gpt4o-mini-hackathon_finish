# src/hh/token_refresher.py
import logging
import aiohttp
from pathlib import Path
from typing import Dict

from src.hh.config import settings
from src.utils import get_logger
logger = get_logger()

class HHTokenRefresher:
    """Сервис для обновления токена доступа."""
    
    def __init__(self, refresh_token: str):
        """Инициализация с текущим refresh токеном."""
        self.refresh_token = refresh_token
        self.client_id = settings.client_id
        self.client_secret = settings.client_secret
        self.token_url = "https://hh.ru/oauth/token"
    
    async def refresh(self) -> Dict[str, str]:
        """Обновление токена доступа."""
        if not self.refresh_token:
            raise ValueError("Отсутствует refresh_token")
            
        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.token_url, data=payload) as response:
                if response.status != 200:
                    logger.error(f"Ошибка обновления токена: {response.status}")
                    raise Exception(f"Ошибка обновления токена: {response.status}")
                
                tokens = await response.json()
                logger.info("Токен успешно обновлен")
                return tokens