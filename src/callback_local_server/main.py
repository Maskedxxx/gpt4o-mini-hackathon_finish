# src/callback_local_server/main.py

### ЛОГИРОВАНИЕ ###
from src.utils import init_logging_from_env, get_logger

# Инициализируем логирование
init_logging_from_env()
logger = get_logger()

import uvicorn
import logging
from pathlib import Path
from src.callback_local_server.config import settings
from src.callback_local_server.server import app

def start_server():
    """Запуск сервера обратного вызова."""
    logger.info(f"Запуск callback сервера на {settings.host}:{settings.port}")
    uvicorn.run(app, host=settings.host, port=settings.port,)

if __name__ == "__main__":
    start_server()