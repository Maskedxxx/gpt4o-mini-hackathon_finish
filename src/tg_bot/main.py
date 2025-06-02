# src/tg_bot/main.py
import asyncio
import logging
from pathlib import Path
from aiogram.fsm.storage.memory import MemoryStorage

### ЛОГИРОВАНИЕ ###
from src.utils import init_logging_from_env, configure_external_loggers, get_logger
# Инициализируем логирование
init_logging_from_env()
configure_external_loggers()
logger = get_logger()

from src.tg_bot.bot.instance import bot, dp
from src.tg_bot.handlers.router import register_handlers


async def main():
    """Функция запуска бота."""
    logger.info("Инициализация бота")
    
    # Регистрация обработчиков
    register_handlers(dp)
    
    # Запуск бота
    await dp.start_polling(bot, storage=MemoryStorage())

if __name__ == "__main__":
    try:
        logger.info("Запуск приложения бота")
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"Критическая ошибка при запуске бота: {e}", exc_info=True)
    finally:
        logger.info("Завершение работы бота")