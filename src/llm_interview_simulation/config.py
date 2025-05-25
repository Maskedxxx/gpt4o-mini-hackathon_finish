# src/llm_interview_simulation/config.py
import logging
from pydantic import ConfigDict
from src.config import BaseAppSettings

logger = logging.getLogger("llm_interview_simulation")

class OpenAIConfig(BaseAppSettings):
    """
    Настройки для сервиса OpenAI для симуляции интервью.
    """
    api_key: str
    model_name: str 
    
    model_config = ConfigDict(
        env_file='.env',
        env_prefix="OPENAI_",
        extra='ignore'
    )

settings = OpenAIConfig()