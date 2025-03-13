# src/hh/token_exchanger.py
import logging
import aiohttp
from pathlib import Path
from typing import Dict

from src.hh.config import settings

# Настройка логирования
log_dir = Path("LOGS")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "hh_token_exchanger.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("hh_token_exchanger")

class HHCodeExchanger:
    """Сервис для обмена кода авторизации на токены доступа."""
    
    def __init__(self):
        """Инициализация сервиса обмена кодов."""
        self.client_id = settings.client_id
        self.client_secret = settings.client_secret
        self.redirect_uri = settings.redirect_uri
        self.token_url = "https://hh.ru/oauth/token"
        
    async def exchange_code(self, code: str) -> Dict[str, str]:
        """Обмен кода авторизации на токены доступа."""
        payload = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri
        }
        
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive"
    }
        
        logger.info("Отправка запроса на обмен кода авторизации")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.token_url, data=payload, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Ошибка при обмене кода: {response.status}, {error_text}")
                    raise Exception(f"Ошибка обмена кода: {response.status}")
                
                tokens = await response.json()
                logger.info("Код успешно обменен на токены")
                return tokens
            