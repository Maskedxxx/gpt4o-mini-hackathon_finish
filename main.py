# main.py

"""Точка входа в приложение"""
import asyncio
from utils.logger import setup_logger
from infra.database import init_db
from container import container
from bot_adapter.telegram_bot import TelegramBotAdapter
from http_adapter.oauth_callback_handler import start_webhook_server
from config import server_settings
from loguru import logger


async def main():
    """Главная функция"""
    # Инициализация БД
    await init_db()
    logger.info("Database initialized")
    
    # Создаём бота
    bot = TelegramBotAdapter(container.pipeline)
    
    # Запускаем webhook сервер для OAuth
    webhook_runner = await start_webhook_server(
        container.oauth_handler,
        server_settings.host,
        server_settings.port
    )
    
    try:
        # Запускаем бота
        await bot.start()
    finally:
        # Останавливаем webhook сервер при завершении
        await webhook_runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())