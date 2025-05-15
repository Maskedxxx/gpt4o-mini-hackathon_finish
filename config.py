# config.py

"""Конфигурация приложения"""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class BaseAppSettings(BaseSettings):
    model_config = ConfigDict(
        env_file='.env',
        extra='allow',
        env_prefix=''
    )


class TelegramSettings(BaseAppSettings):
    """Настройки Telegram бота"""
    model_config = ConfigDict(
        env_file='.env',
        extra='allow',
        env_prefix='TELEGRAM_'
    )
    
    bot_token: str


class HHSettings(BaseAppSettings):
    """Настройки HH API"""
    model_config = ConfigDict(
        env_file='.env',
        extra='allow',
        env_prefix='HH_'
    )
    
    client_id: str
    client_secret: str
    redirect_uri: str
    api_base_url: str


class LLMSettings(BaseAppSettings):
    """Настройки LLM"""
    model_config = ConfigDict(
        env_file='.env',
        extra='allow',
        env_prefix='OPENAI_'
    )
    
    api_key: str
    model: str


class DatabaseSettings(BaseAppSettings):
    """Настройки базы данных"""
    model_config = ConfigDict(
        env_file='.env',
        extra='allow',
        env_prefix='DB_'
    )
    
    url: str


class ServerSettings(BaseAppSettings):
    """Настройки сервера"""
    model_config = ConfigDict(
        env_file='.env',
        extra='allow',
        env_prefix='SERVER_'
    )
    
    host: str
    port: int


# Создание экземпляров настроек
telegram_settings = TelegramSettings()
hh_settings = HHSettings()
llm_settings = LLMSettings()
db_settings = DatabaseSettings()
server_settings = ServerSettings()