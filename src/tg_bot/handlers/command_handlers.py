# src/tg_bot/handlers/command_handlers.py

import logging
from aiogram import types
from pathlib import Path
from aiogram.fsm.context import FSMContext
import asyncio
from src.tg_bot.handlers.spec_handlers.auth_handler import start_auth_polling

from src.tg_bot.utils import UserState, UNAUTHORIZED_STATE_MESSAGES, AUTH_WAITING_MESSAGES, auth_keyboard, auth_waiting_keyboard
from src.hh.auth import HHAuthService

from src.utils import get_logger
logger = get_logger()

# Создаём экземпляр сервиса авторизации
hh_auth_service = HHAuthService()
# Получаем URL для авторизации
auth_url = hh_auth_service.get_auth_url()


async def cmd_start(message: types.Message, state: FSMContext):
    """Обработчик команды /start."""
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} выполнил команду /start")
    
    await message.answer(UNAUTHORIZED_STATE_MESSAGES["greeting"], reply_markup=auth_keyboard)
    await state.set_state(UserState.UNAUTHORIZED)
    logger.info(f"Пользователь {user_id} переведен в состояние UNAUTHORIZED")


async def cmd_auth(message: types.Message, state: FSMContext):
    """Обработчик команды авторизации."""
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} запросил авторизацию")
    
    # Формируем сообщение с инструкциями и ссылкой
    auth_message = f"{AUTH_WAITING_MESSAGES['auth_instructions']}\n🔗 Ссылка для авторизации: {auth_url}"
    
    await message.answer(auth_message, reply_markup=auth_waiting_keyboard )
    await state.set_state(UserState.AUTH_WAITING)
    logger.info(f"Пользователь {user_id} переведен в состояние AUTH_WAITING")
    
    asyncio.create_task(start_auth_polling(user_id, state))