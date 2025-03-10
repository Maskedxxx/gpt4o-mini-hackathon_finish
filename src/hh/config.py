# src/hh/config.py
import logging
from pydantic import ConfigDict
from src.config import BaseAppSettings

logger = logging.getLogger("hh_config")

class HHSettings(BaseAppSettings):
    """
    Настройки для сервиса HH.ru.
    """
    client_id: str
    client_secret: str
    redirect_uri: str
    
    model_config = ConfigDict(
        env_file='.env',
        env_prefix='HH_',
        extra='ignore'
    )

settings = HHSettings()
