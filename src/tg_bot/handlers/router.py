# src/tg_bot/handlers/router.py
import logging
from pathlib import Path
from aiogram import Dispatcher, F
from aiogram.filters import StateFilter, Command

from src.tg_bot.utils.states import UserState
from src.tg_bot.handlers.command_handlers import cmd_start, cmd_auth
from src.tg_bot.handlers.message_handlers import handle_interview_simulation_button, handle_interview_checklist_button, handle_gap_analysis_button, handle_cover_letter_button, initial_greeting, handle_initial_message, handle_unauthorized_message, handle_auth_waiting_message, handle_start_button, handle_auth_button, handle_authorized_message, handle_edit_resume_button, handle_resume_preparation_message, handle_vacancy_preparation_message
from src.utils import get_logger
logger = get_logger()


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
    dp.message.register(handle_gap_analysis_button, F.text == "📊 GAP-анализ резюме")
    dp.message.register(handle_cover_letter_button, F.text == "📧 Рекомендательное письмо")
    dp.message.register(handle_interview_checklist_button, F.text == "📋 Чек-лист подготовки к интервью")
    dp.message.register(handle_interview_simulation_button, F.text == "🎭 Симуляция интервью")


    
    # Регистрация обработчиков сообщений по состояниям
    dp.message.register(initial_greeting, StateFilter(None))
    dp.message.register(handle_initial_message, StateFilter(UserState.INITIAL))
    dp.message.register(handle_unauthorized_message, StateFilter(UserState.UNAUTHORIZED))
    dp.message.register(handle_auth_waiting_message, StateFilter(UserState.AUTH_WAITING))
    dp.message.register(handle_authorized_message, StateFilter(UserState.AUTHORIZED))
    dp.message.register(handle_resume_preparation_message, StateFilter(UserState.RESUME_PREPARATION))
    dp.message.register(handle_vacancy_preparation_message, StateFilter(UserState.VACANCY_PREPARATION))

    logger.info("Все обработчики успешно зарегистрированы")