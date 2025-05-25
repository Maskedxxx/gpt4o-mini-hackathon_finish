# src/llm_cover_letter/config.py
import logging
from pydantic import ConfigDict
from src.config import BaseAppSettings

logger = logging.getLogger("llm_cover_letter")

class OpenAIConfig(BaseAppSettings):
    """
    Настройки для сервиса OpenAI для генерации рекомендательных писем.
    """
    api_key: str
    model_name: str 
    
    model_config = ConfigDict(
        env_file='.env',
        env_prefix="OPENAI_",
        extra='ignore'
    )

settings = OpenAIConfig()