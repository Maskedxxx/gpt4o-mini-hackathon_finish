# src/tg_bot/handlers/message_handlers.py

from aiogram import types
from aiogram.fsm.context import FSMContext

from src.tg_bot.handlers.command_handlers import cmd_start, cmd_auth
from src.tg_bot.utils import (UserState, 
    INITIAL_STATE_MESSAGES, 
    UNAUTHORIZED_STATE_MESSAGES, 
    AUTH_WAITING_MESSAGES, 
    AUTHORIZED_STATE_MESSAGES,
    RESUME_PREPARATION_MESSAGES,
    start_keyboard, 
    auth_keyboard, 
    auth_waiting_keyboard, 
    authorized_keyboard,
    resume_preparation_keyboard)

from src.hh.auth import HHAuthService

from src.utils import get_logger
logger = get_logger()

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
    
    
# Добавим обработчик для кнопки "Редактировать резюме"
async def handle_edit_resume_button(message: types.Message, state: FSMContext):
    """Обработчик нажатия кнопки 'Редактировать резюме'."""
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} запросил редактирование резюме (нажал кнопку)")
    
    await message.answer(RESUME_PREPARATION_MESSAGES["request_link"], reply_markup=resume_preparation_keyboard)
    await state.set_state(UserState.RESUME_PREPARATION)
    logger.info(f"Пользователь {user_id} переведен в состояние RESUME_PREPARATION")
    
    
async def handle_resume_preparation_message(message: types.Message, state: FSMContext):
    """Обработчик текстовых сообщений в состоянии подготовки резюме."""
    # Делегируем обработку специализированному обработчику из resume_handler
    from src.tg_bot.handlers.spec_handlers.resume_handler import handle_resume_link
    await handle_resume_link(message, state)
    
async def handle_vacancy_preparation_message(message: types.Message, state: FSMContext):
    """Обработчик текстовых сообщений в состоянии подготовки вакансии."""
    # Делегируем обработку специализированному обработчику
    from src.tg_bot.handlers.spec_handlers.vacancy_handler import handle_vacancy_link
    await handle_vacancy_link(message, state)
    
async def handle_gap_analysis_button(message: types.Message, state: FSMContext):
    """Обработчик нажатия кнопки 'GAP-анализ резюме'."""
    from src.tg_bot.handlers.spec_handlers.gap_analyzer_handler import start_gap_analysis
    await start_gap_analysis(message, state)

async def handle_cover_letter_button(message: types.Message, state: FSMContext):
    """Обработчик нажатия кнопки 'Рекомендательное письмо'."""
    from src.tg_bot.handlers.spec_handlers.cover_letter_handler import start_cover_letter_generation
    await start_cover_letter_generation(message, state)
    
async def handle_interview_checklist_button(message: types.Message, state: FSMContext):
    """Обработчик нажатия кнопки 'Чек-лист подготовки к интервью'."""
    from src.tg_bot.handlers.spec_handlers.interview_checklist_handler import start_interview_checklist_generation
    await start_interview_checklist_generation(message, state)
    
async def handle_interview_simulation_button(message: types.Message, state: FSMContext):
    """Обработчик нажатия кнопки 'Симуляция интервью'."""
    from src.tg_bot.handlers.spec_handlers.interview_simulation_handler import start_interview_simulation
    await start_interview_simulation(message, state)