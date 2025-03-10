# src/tg_bot/handlers/message.py

import logging
from aiogram import types
from pathlib import Path
from aiogram.fsm.context import FSMContext

from src.tg_bot.handlers.command_handlers import cmd_start, cmd_auth
from src.tg_bot.utils import (UserState, 
    INITIAL_STATE_MESSAGES, 
    UNAUTHORIZED_STATE_MESSAGES, 
    AUTH_WAITING_MESSAGES, 
    AUTHORIZED_STATE_MESSAGES,
    start_keyboard, 
    auth_keyboard, 
    auth_waiting_keyboard, 
    authorized_keyboard)

from src.hh.auth import HHAuthService

log_dir = Path("LOGS")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "message_handlers.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("message_handlers")


# Создаём экземпляр сервиса
hh_auth_service = HHAuthService()
# Получаем URL для авторизации
auth_url = hh_auth_service.get_auth_url()


async def initial_greeting(message: types.Message, state: FSMContext):
    """Приветственное сообщение при первом входе."""
    user_id = message.from_user.id
    logger.info(f"Новый пользователь {user_id} начал взаимодействие с ботом")
    
    await message.answer(INITIAL_STATE_MESSAGES["greeting"], reply_markup=start_keyboard)
    await state.set_state(UserState.INITIAL)
    logger.info(f"Пользователь {user_id} переведен в состояние INITIAL")

async def handle_initial_message(message: types.Message):
    """Обработчик текстовых сообщений в начальном состоянии."""
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} отправил сообщение в начальном состоянии")
    
    await message.answer(INITIAL_STATE_MESSAGES["unauthorized"], reply_markup=start_keyboard)

async def handle_start_button(message: types.Message, state: FSMContext):
    """Обработчик нажатия кнопки 'Старт'."""
    await cmd_start(message, state)

async def handle_unauthorized_message(message: types.Message):
    """Обработчик сообщений в неавторизованном состоянии."""
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} отправил сообщение в неавторизованном состоянии")
    
    await message.answer(UNAUTHORIZED_STATE_MESSAGES["need_auth"], reply_markup=auth_keyboard)

async def handle_auth_button(message: types.Message, state: FSMContext):
    """Обработчик нажатия кнопки 'Авторизация'."""
    await cmd_auth(message, state)

async def handle_auth_waiting_message(message: types.Message):
    """Обработчик сообщений в состоянии ожидания авторизации."""
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} отправил сообщение в состоянии ожидания авторизации")
    
     # Формируем сообщение с инструкциями и ссылкой
    auth_message = f"{AUTH_WAITING_MESSAGES['reply_auth_instructions']}\n🔗 Ссылка для авторизации: {auth_url}"
    
    await message.answer(auth_message, reply_markup=auth_waiting_keyboard)
    
async def handle_authorized_message(message: types.Message):
    """Обработчик текстовых сообщений в авторизованном состоянии."""
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} отправил сообщение в авторизованном состоянии")
    
    await message.answer(AUTHORIZED_STATE_MESSAGES["text_message_reply"], reply_markup=authorized_keyboard)