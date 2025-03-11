# src/tg_bot/handlers/resume_handler.py
import logging
import re
from aiogram import types
from pathlib import Path
from aiogram.fsm.context import FSMContext

from src.tg_bot.utils import UserState
from src.tg_bot.utils import RESUME_PREPARATION_MESSAGES
from src.hh.api_client import HHApiClient


log_dir = Path("LOGS")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "resume_handler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("resume_handler")


async def handle_resume_link(message: types.Message, state: FSMContext):
    """Обработчик ссылки на резюме."""
    user_id = message.from_user.id
    link = message.text.strip()
    
    # Проверка, что ссылка корректная (направлена на hh.ru и содержит resume)
    if not is_valid_resume_link(link):
        logger.info(f"Пользователь {user_id} отправил некорректную ссылку на резюме: {link}")
        await message.answer(RESUME_PREPARATION_MESSAGES["invalid_link"])
        return
    
    # Извлечение ID резюме из ссылки
    resume_id = extract_resume_id(link)
    logger.info(f"Пользователь {user_id} отправил корректную ссылку на резюме. ID резюме: {resume_id}")
    
    # Получение данных пользователя из состояния
    user_data = await state.get_data()
    access_token = user_data.get("access_token")
    refresh_token = user_data.get("refresh_token")
    
    if not access_token or not refresh_token:
        logger.error(f"Отсутствуют токены доступа для пользователя {user_id}")
        await message.answer("Произошла ошибка авторизации. Пожалуйста, выполните авторизацию повторно.")
        await state.set_state(UserState.UNAUTHORIZED)
        return
    
    # Создание клиента API и получение данных резюме
    try:
        hh_client = HHApiClient(access_token, refresh_token)
        resume_data = await hh_client.request(f'resumes/{resume_id}')
        
        logger.info(f"Успешно получены данные резюме {resume_id} для пользователя {user_id}")
        
        # Сохранение информации о резюме в состоянии пользователя
        await state.update_data(resume_link=link, resume_id=resume_id, resume_data=resume_data)
        
        # Отправка подтверждения пользователю
        resume_title = resume_data.get('title', 'Резюме')
        await message.answer(f"{RESUME_PREPARATION_MESSAGES['link_accepted']} Получено резюме: «{resume_title}»")
        
        # В будущем здесь будет переход к следующему этапу редактирования резюме
        
    except Exception as e:
        logger.error(f"Ошибка при получении данных резюме: {e}")
        await message.answer("Не удалось получить данные резюме. Пожалуйста, проверьте ссылку и попробуйте снова.")

def is_valid_resume_link(link: str) -> bool:
    """Проверка, что ссылка ведет на резюме hh.ru."""
    # Проверяем, что ссылка содержит hh.ru и resume
    return bool(re.match(r'https?://(?:www\.)?hh\.ru/resume/\w+', link))

def extract_resume_id(link: str) -> str:
    """Извлечение ID резюме из ссылки."""
    # Извлекаем ID резюме (последний сегмент пути до параметров запроса)
    return link.split('/')[-1].split('?')[0]