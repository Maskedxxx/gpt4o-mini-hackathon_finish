# src/hh/auth.py
import logging
from pathlib import Path
from src.hh.config import settings
from src.utils import get_logger
logger = get_logger()

class HHAuthService:
    """Сервис для работы с авторизацией в HH.ru."""
    
    def __init__(self):
        """Инициализация сервиса авторизации."""
        self.client_id = settings.client_id
        self.redirect_uri = settings.redirect_uri
        logger.info("Инициализирован сервис авторизации HH")
        
    def get_auth_url(self) -> str:
        """Генерация URL для авторизации пользователя."""
        auth_url = (
            f'https://hh.ru/oauth/authorize?'
            f'response_type=code&'
            f'client_id={self.client_id}&'
            f'redirect_uri={self.redirect_uri}'
        )
        logger.info("Сгенерирован URL авторизации")
        return auth_url