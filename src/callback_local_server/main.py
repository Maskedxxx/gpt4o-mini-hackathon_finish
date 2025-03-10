# src/callback_local_server/main.py
import uvicorn
import logging
from pathlib import Path
from src.callback_local_server.config import settings
from src.callback_local_server.server import app

# Настройка логирования
log_dir = Path("LOGS")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "callback_local_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("callback_local_server")

def start_server():
    """Запуск сервера обратного вызова."""
    logger.info(f"Запуск callback сервера на {settings.host}:{settings.port}")
    uvicorn.run(app, host=settings.host, port=settings.port,)

if __name__ == "__main__":
    start_server()