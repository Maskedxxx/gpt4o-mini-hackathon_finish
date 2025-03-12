# src/tg_bot/handlers/resume_handler.py
import logging
import re
from aiogram import types
from pathlib import Path
from aiogram.fsm.context import FSMContext

from src.tg_bot.utils import UserState, vacancy_preparation_keyboard
from src.tg_bot.utils import RESUME_PREPARATION_MESSAGES, VACANCY_PREPARATION_MESSAGES
from src.hh.api_client import HHApiClient
from src.parsers.resume_extractor import ResumeExtractor 


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

# Создаем экземпляр экстрактора
entity_extractor = ResumeExtractor()


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
        await message.answer(f"{RESUME_PREPARATION_MESSAGES['auth_error']}")
        await state.set_state(UserState.UNAUTHORIZED)
        return
    
    # Создание клиента API и получение данных резюме
    try:
        hh_client = HHApiClient(access_token, refresh_token)
        resume_data = await hh_client.request(f'resumes/{resume_id}')
        
        logger.info(f"Успешно получены данные резюме {resume_id} для пользователя {user_id}")
        
        # Парсинг данных резюме с помощью ResumeExtractor
        parsed_resume = entity_extractor.extract_resume_info(resume_data)
        
        if not parsed_resume:
            logger.error(f"Не удалось распарсить данные резюме {resume_id}")
            await message.answer(RESUME_PREPARATION_MESSAGES["resume_fetch_error"])
            return
        
        # Сохранение информации о резюме в состоянии пользователя
        await state.update_data(resume_link=link, resume_id=resume_id, resume_data=resume_data, parsed_resume=parsed_resume.model_dump())
        
        # Отправка подтверждения пользователю
        await message.answer(
            f"{RESUME_PREPARATION_MESSAGES['link_accepted']}\n\nПолучено резюме с желаемой должностью: «{parsed_resume.title}»\n\n")
        
        # Переход к следующему этапу - запрос вакансии
        await message.answer(VACANCY_PREPARATION_MESSAGES["request_link"], reply_markup=vacancy_preparation_keyboard)
        await state.set_state(UserState.VACANCY_PREPARATION)
        logger.info(f"Пользователь {user_id} переведен в состояние VACANCY_PREPARATION")
        
    except Exception as e:
        logger.error(f"Ошибка при получении данных резюме: {e}")
        await message.answer(f"{RESUME_PREPARATION_MESSAGES['resume_fetch_error']}")

def is_valid_resume_link(link: str) -> bool:
    """Проверка, что ссылка ведет на резюме hh.ru."""
    # Проверяем, что ссылка содержит hh.ru и resume
    return bool(re.match(r'https?://(?:www\.)?hh\.ru/resume/\w+', link))

def extract_resume_id(link: str) -> str:
    """Извлечение ID резюме из ссылки."""
    # Извлекаем ID резюме (последний сегмент пути до параметров запроса)
    return link.split('/')[-1].split('?')[0]