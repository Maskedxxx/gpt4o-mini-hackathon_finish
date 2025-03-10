# src/tg_bot/main.py
import asyncio
import logging
from pathlib import Path
from aiogram.fsm.storage.memory import MemoryStorage

from src.tg_bot.bot.instance import bot, dp
from src.tg_bot.handlers.router import register_handlers

# Настройка логирования: вывод в консоль и в файл
log_dir = Path("LOGS")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "run_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("run_bot")


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