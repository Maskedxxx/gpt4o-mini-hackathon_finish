# src/tg_bot/handlers/router.py
import logging
from pathlib import Path
from aiogram import Dispatcher, F
from aiogram.filters import StateFilter, Command

from src.tg_bot.utils.states import UserState
from src.tg_bot.handlers.command_handlers import cmd_start, cmd_auth
from src.tg_bot.handlers.message_handlers import initial_greeting, handle_initial_message, handle_unauthorized_message, handle_auth_waiting_message, handle_start_button, handle_auth_button, handle_authorized_message, handle_edit_resume_button, handle_resume_preparation_message


log_dir = Path("LOGS")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s", handlers=[logging.FileHandler(log_dir / "router.log"), logging.StreamHandler()])
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
    dp.message.register(handle_edit_resume_button, F.text == "Редактировать резюме")

    
    # Регистрация обработчиков сообщений по состояниям
    dp.message.register(initial_greeting, StateFilter(None))
    dp.message.register(handle_initial_message, StateFilter(UserState.INITIAL))
    dp.message.register(handle_unauthorized_message, StateFilter(UserState.UNAUTHORIZED))
    dp.message.register(handle_auth_waiting_message, StateFilter(UserState.AUTH_WAITING))
    dp.message.register(handle_authorized_message, StateFilter(UserState.AUTHORIZED))
    dp.message.register(handle_resume_preparation_message, StateFilter(UserState.RESUME_PREPARATION))

    
    logger.info("Все обработчики успешно зарегистрированы")