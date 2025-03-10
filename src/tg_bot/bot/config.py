# src/tg_bot/bot/config.py
from pydantic import ConfigDict
from src.config import BaseAppSettings

class TelegramBotSettings(BaseAppSettings):
    """
    Настройки для Telegram бота.
    """
    bot_token: str
    
    model_config = ConfigDict(
        env_file='.env',
        env_prefix='TG_BOT_',
        extra='ignore'
    )

settings = TelegramBotSettings()