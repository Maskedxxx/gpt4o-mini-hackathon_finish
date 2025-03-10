# src/tg_bot/bot/instance.py

from aiogram import Bot, Dispatcher
from src.tg_bot.bot.config import settings

# Создаем экземпляры бота и диспетчера
bot = Bot(token=settings.bot_token)
dp = Dispatcher()