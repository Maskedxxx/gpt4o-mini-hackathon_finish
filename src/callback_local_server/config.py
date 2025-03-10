# src/callback_local_server/config.py
from pydantic import ConfigDict
from src.config import BaseAppSettings

class CallbackServerSettings(BaseAppSettings):
    """
    Настройки для сервиса callback.
    """
    host: str = "0.0.0.0"
    port: int = 8080
    
    model_config = ConfigDict(
        env_file='.env',
        env_prefix='CALLBACK_LOCAL_'
    )

settings = CallbackServerSettings()