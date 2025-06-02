# src/tg_bot/handlers/auth_handler.py
import logging
import asyncio
import aiohttp
from aiogram import types
from pathlib import Path
from aiogram.fsm.context import FSMContext

from src.tg_bot.utils import UserState, authorized_keyboard
from src.tg_bot.utils.text_constants import AUTHORIZED_STATE_MESSAGES
from src.tg_bot.bot.instance import bot
from src.hh.token_exchanger import HHCodeExchanger
from src.callback_local_server.config import settings as callback_settings
from src.utils import get_logger
logger = get_logger()

# Инициализация обменщика кодов
code_exchanger = HHCodeExchanger()

# Переменная для отслеживания использованного кода
last_processed_code = None

async def check_auth_code(user_id: int, state: FSMContext):
    """Проверяет наличие кода авторизации на callback-сервере."""
    global last_processed_code
    callback_url = f"http://{callback_settings.host}:{callback_settings.port}/api/code"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(callback_url) as response:
                if response.status == 200:
                    data = await response.json()
                    code = data.get("code")
                    
                    # Проверяем, что код новый и не был обработан ранее
                    if code and code != last_processed_code:
                        logger.info(f"Получен новый код авторизации для пользователя {user_id}")
                        last_processed_code = code
                        
                        try:
                            # Обмен кода на токены
                            tokens = await code_exchanger.exchange_code(code)
                            
                            # Сохранение токенов в состоянии пользователя
                            await state.update_data(access_token=tokens["access_token"], refresh_token=tokens["refresh_token"], expires_in=tokens["expires_in"])
                            
                            # Переключение состояния пользователя
                            await state.set_state(UserState.AUTHORIZED)
                            
                            # Отправляем сообщение об успешной авторизации
                            await bot.send_message(user_id, f"{AUTHORIZED_STATE_MESSAGES['auth_success']}\n\n{AUTHORIZED_STATE_MESSAGES['resume_instructions']}", reply_markup=authorized_keyboard)
                            
                            # После успешной обработки кода, очищаем его на сервере
                            async with session.post(f"http://{callback_settings.host}:{callback_settings.port}/api/reset_code") as reset_response:
                                if reset_response.status == 200:
                                    logger.info("Код авторизации успешно сброшен на сервере")
                                
                            return True
                        except Exception as e:
                            logger.error(f"Ошибка при обмене кода: {e}")
                            
    except Exception as e:
        logger.error(f"Ошибка при проверке кода авторизации: {e}")
    
    return False

async def start_auth_polling(user_id: int, state: FSMContext):
    """Запускает периодическую проверку статуса авторизации."""
    # Запускаем проверку кода с интервалом в 3 секунды, максимум 300 секунд (100 попыток)
    for _ in range(100):
        if await check_auth_code(user_id, state):
            return
        await asyncio.sleep(3)
    
    # Если код не был получен за отведенное время
    await bot.send_message(user_id, AUTHORIZED_STATE_MESSAGES["auth_timeout"])
