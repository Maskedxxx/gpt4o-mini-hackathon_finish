# src/config.py
from pydantic_settings import BaseSettings

class BaseAppSettings(BaseSettings):
    """
    Базовый класс настроек для всех сервисов приложения.
    """
    app_name: str = "Resume Bot"
    debug: bool = False
    
    class Config:
        extra = "ignore" 