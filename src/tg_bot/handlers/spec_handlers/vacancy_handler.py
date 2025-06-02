# src/tg_bot/handlers/vacancy_handler.py
import logging
import re
from aiogram import types
from aiogram.fsm.context import FSMContext

from src.tg_bot.utils import UserState
from src.tg_bot.utils.text_constants import VACANCY_PREPARATION_MESSAGES
from src.hh.api_client import HHApiClient
from src.parsers.vacancy_extractor import VacancyExtractor

from src.utils import get_logger
logger = get_logger()

# Используем тот же экземпляр экстрактора
entity_extractor = VacancyExtractor()

async def handle_vacancy_link(message: types.Message, state: FSMContext):
    """Обработчик ссылки на вакансию."""
    user_id = message.from_user.id
    link = message.text.strip()
    
    # Проверка, что ссылка корректная (направлена на hh.ru и содержит vacancy)
    if not is_valid_vacancy_link(link):
        logger.info(f"Пользователь {user_id} отправил некорректную ссылку на вакансию: {link}")
        await message.answer(VACANCY_PREPARATION_MESSAGES["invalid_link"])
        return
    
    # Извлечение ID вакансии из ссылки
    vacancy_id = extract_vacancy_id(link)
    logger.info(f"Пользователь {user_id} отправил корректную ссылку на вакансию. ID вакансии: {vacancy_id}")
    
    # Получение данных пользователя из состояния
    user_data = await state.get_data()
    access_token = user_data.get("access_token")
    refresh_token = user_data.get("refresh_token")
    
    if not access_token or not refresh_token:
        logger.error(f"Отсутствуют токены доступа для пользователя {user_id}")
        await message.answer(VACANCY_PREPARATION_MESSAGES["auth_error"])
        await state.set_state(UserState.UNAUTHORIZED)
        return
    
    # Создание клиента API и получение данных вакансии
    try:
        hh_client = HHApiClient(access_token, refresh_token)
        vacancy_data = await hh_client.request(f'vacancies/{vacancy_id}')
        
        logger.info(f"Успешно получены данные вакансии {vacancy_id} для пользователя {user_id}")
        
        # Парсинг данных вакансии с помощью EntityExtractor
        parsed_vacancy = entity_extractor.extract_vacancy_info(vacancy_data)
        
        if not parsed_vacancy:
            logger.error(f"Не удалось распарсить данные вакансии {vacancy_id}")
            await message.answer(VACANCY_PREPARATION_MESSAGES["vacancy_fetch_error"])
            return
        
        # Сохранение информации о вакансии в состоянии пользователя
        await state.update_data(vacancy_link=link, vacancy_id=vacancy_id, vacancy_data=vacancy_data, parsed_vacancy=parsed_vacancy.model_dump())
        
        # Отправка подтверждения пользователю
        skills_text = ", ".join(parsed_vacancy.key_skills[:5]) if parsed_vacancy.key_skills else "Не указаны"
        
        await message.answer(
            f"{VACANCY_PREPARATION_MESSAGES['link_accepted']}\n\n"
            f"Получено вакансия с требуемой навыками: {skills_text}...")
        
        # Импортируем здесь чтобы избежать циклических импортов
        from src.tg_bot.utils.text_constants import COVER_LETTER_MESSAGES
        from src.tg_bot.utils.keyboards import action_choice_keyboard
        
        # Предлагаем выбор действий
        await message.answer(COVER_LETTER_MESSAGES["choice_prompt"], reply_markup=action_choice_keyboard)
        await state.set_state(UserState.AUTHORIZED)
                
    except Exception as e:
        logger.error(f"Ошибка при получении данных вакансии: {e}")
        await message.answer(VACANCY_PREPARATION_MESSAGES["vacancy_fetch_error"])

def is_valid_vacancy_link(link: str) -> bool:
    """Проверка, что ссылка ведет на вакансию hh.ru."""
    return bool(re.match(r'https?://(?:www\.)?hh\.ru/vacancy/\d+', link))

def extract_vacancy_id(link: str) -> str:
    """Извлечение ID вакансии из ссылки."""
    return link.split('/')[-1].split('?')[0]