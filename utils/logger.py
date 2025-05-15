# utilities/logger.py

"""Настройка логирования"""
import sys
from loguru import logger


def setup_logger():
    """Настроить логирование для приложения"""
    # Удаляем стандартный обработчик
    logger.remove()
    
    # Добавляем консольный вывод
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG",
        colorize=True
    )
    
    # Добавляем файловый вывод для ошибок
    logger.add(
        "logs/error.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="10 MB"
    )
    
    # Добавляем файловый вывод для всех логов
    logger.add(
        "logs/app.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="100 MB"
    )


# Настраиваем логгер при импорте
setup_logger()