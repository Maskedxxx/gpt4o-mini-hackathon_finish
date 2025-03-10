# src/tg_bot/handlers/router.py
import logging
from aiogram import Dispatcher, F
from aiogram.filters import StateFilter, Command

from src.tg_bot.utils.states import UserState
from src.tg_bot.handlers.command import cmd_start, cmd_auth
from src.tg_bot.handlers.message import (
    initial_greeting, 
    handle_initial_message,
    handle_unauthorized_message,
    handle_auth_waiting_message,
    handle_start_button,
    handle_auth_button
)

logger = logging.getLogger("router")

def register_handlers(dp: Dispatcher):
    """Регистрация всех обработчиков."""
    logger.info("Начало регистрации обработчиков")
    
    # Регистрация обработчиков команд
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_auth, Command("auth"))
    
    # Обработчики кнопок
    dp.message.register(handle_start_button, F.text == "Старт")
    dp.message.register(handle_auth_button, F.text == "Авторизация")
    
    # Регистрация обработчиков сообщений по состояниям
    dp.message.register(initial_greeting, StateFilter(None))
    dp.message.register(handle_initial_message, StateFilter(UserState.INITIAL))
    dp.message.register(handle_unauthorized_message, StateFilter(UserState.UNAUTHORIZED))
    dp.message.register(handle_auth_waiting_message, StateFilter(UserState.AUTH_WAITING))
    
    logger.info("Все обработчики успешно зарегистрированы")