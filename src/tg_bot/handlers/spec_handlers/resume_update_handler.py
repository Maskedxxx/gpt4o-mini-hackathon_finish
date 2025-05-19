# src/tg_bot/handlers/spec_handlers/resume_update_handler.py
import logging
import copy
import json
from aiogram import types
from aiogram.fsm.context import FSMContext

from src.tg_bot.utils import UserState
from src.hh.api_client import HHApiClient
from src.tg_bot.utils import RESUME_UPDATE_MESSAGES
from src.tg_bot.utils import resume_rewrite_keyboard
from src.llm_update_resume import LLMResumeUpdater
from src.models.resume_update_models import ResumeUpdate
from src.models.gap_analysis_models import ResumeTailoringAnalysis

logger = logging.getLogger("resume_update_handler")

# Создаем экземпляр сервиса обновления резюме
llm_resume_updater = LLMResumeUpdater()

def _update_title_and_skills(payload: dict, llm_updates: dict) -> None:
    """Обновляет заголовок и навыки в резюме."""
    if "title" in llm_updates:
        payload["title"] = llm_updates["title"]
    
    if "skills" in llm_updates:
        payload["skills"] = llm_updates["skills"]
    
    if "skill_set" in llm_updates:
        payload["skill_set"] = llm_updates["skill_set"]

def _update_experience(payload: dict, llm_updates: dict, resume_id: str) -> None:
    """Обновляет опыт работы в резюме."""
    if "experience" not in llm_updates or not isinstance(llm_updates["experience"], list):
        return
        
    llm_experience_list = llm_updates["experience"]
    original_experience_list = payload.get("experience")
        
    if not isinstance(original_experience_list, list) or len(original_experience_list) != len(llm_experience_list):
        logger.warning(
            f"Не удалось обновить секцию 'experience' для резюме {resume_id}. "
            f"LLM предложил {len(llm_experience_list)} записей, в оригинале было "
            f"{len(original_experience_list) if isinstance(original_experience_list, list) else 'N/A'}."
        )
        return
        
    for i, exp_update_item in enumerate(llm_experience_list):
        if "position" in exp_update_item:
            original_experience_list[i]["position"] = exp_update_item["position"]
        if "description" in exp_update_item:
            original_experience_list[i]["description"] = exp_update_item["description"]

def _clean_payload(payload: dict, resume_id: str) -> None:
    """Очищает payload от ненужных полей и устанавливает значения по умолчанию."""
    # Удаляем устаревшее поле 'specialization'
    if "specialization" in payload:
        logger.info(f"Удаление устаревшего поля 'specialization' из payload для резюме {resume_id}")
        payload.pop("specialization")
    
    # Проверяем и при необходимости устанавливаем корректную форму занятости
    DEFAULT_EMPLOYMENT_FORM_ID = "full"
    
    ef_value = payload.get("employment_form")
    is_ef_valid_object = isinstance(ef_value, dict) and ef_value.get("id")
    
    if not is_ef_valid_object:
        logger.warning(
            f"Поле 'employment_form' некорректно в payload для резюме {resume_id}. "
            f"Установка значения по умолчанию: {{'id': '{DEFAULT_EMPLOYMENT_FORM_ID}'}}."
        )
        payload["employment_form"] = {"id": DEFAULT_EMPLOYMENT_FORM_ID}

def _prepare_hh_api_payload(original_data: dict, llm_updates: dict, resume_id: str) -> dict:
    """
    Готовит данные (payload) для обновления резюме через API hh.ru.
    Объединяет оригинальные данные резюме с изменениями от LLM.
    """
    payload = copy.deepcopy(original_data)
    
    # Обновляем заголовок и навыки
    _update_title_and_skills(payload, llm_updates)
    
    # Обновляем опыт работы
    _update_experience(payload, llm_updates, resume_id)
    
    # Игнорируем обновления профессиональных ролей, так как LLM не предоставляет ID
    if "professional_roles" in llm_updates:
        logger.warning(
            f"LLM предложил изменения для 'professional_roles' резюме {resume_id}, "
            "но они будут проигнорированы, так как требуется поле 'id' для каждой роли."
        )
    
    # Очищаем payload от ненужных полей
    _clean_payload(payload, resume_id)
    
    return payload

async def _get_user_data(state: FSMContext) -> tuple:
    """Получает необходимые данные из состояния пользователя."""
    user_data = await state.get_data()
    
    parsed_resume = user_data.get("parsed_resume")
    gap_analysis = user_data.get("gap_analysis")
    
    resume_id = user_data.get("resume_id")
    access_token = user_data.get("access_token")
    refresh_token = user_data.get("refresh_token")
    original_resume_data = user_data.get("resume_data")
    
    return parsed_resume, gap_analysis, resume_id, access_token, refresh_token, original_resume_data

async def _validate_gap_analysis(gap_analysis_data: dict) -> ResumeTailoringAnalysis:
    """Валидирует данные gap-анализа."""
    try:
        return ResumeTailoringAnalysis.model_validate(gap_analysis_data)
    except Exception as e:
        logger.error(f"Ошибка валидации gap-анализа: {e}")
        raise ValueError("Невалидные данные gap-анализа")

async def _update_resume_with_llm(parsed_resume: dict, gap_result: ResumeTailoringAnalysis) -> ResumeUpdate:
    """Обновляет резюме с помощью LLM."""
    resume_update_model = await llm_resume_updater.update_resume(parsed_resume, gap_result)
    if not resume_update_model:
        logger.error("Не удалось получить обновленное резюме от LLM")
        raise ValueError("Ошибка обновления резюме через LLM")
    return resume_update_model

async def _update_resume_on_hh(resume_id: str, access_token: str, refresh_token: str, 
                              original_resume_data: dict, llm_updates_dict: dict) -> bool:
    """Обновляет резюме на сайте hh.ru."""
    try:
        hh_client = HHApiClient(access_token, refresh_token)
        prepared_payload = _prepare_hh_api_payload(
            original_resume_data, llm_updates_dict, resume_id
        )
        
        api_response = await hh_client.request(
            endpoint=f'resumes/{resume_id}',
            method='PUT',
            data=prepared_payload
        )
        
        logger.info(f"Ответ API hh.ru на обновление резюме {resume_id}: {api_response if api_response else 'Успешно (204 No Content)'}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при API вызове обновления резюме: {e}", exc_info=True)
        return False

async def start_resume_update(message: types.Message, state: FSMContext):
    """Запускает процесс обновления резюме на основе GAP-анализа."""
    user_id = message.from_user.id
    logger.info(f"Запуск обновления резюме для пользователя {user_id}")

    try:
        # Получаем и проверяем данные пользователя
        parsed_resume, gap_analysis, resume_id, access_token, refresh_token, original_resume_data = await _get_user_data(state)
        
        if not parsed_resume or not gap_analysis:
            logger.error(f"Недостаточно данных для обновления резюме пользователя {user_id}")
            await message.answer(RESUME_UPDATE_MESSAGES["update_error"])
            await state.set_state(UserState.AUTHORIZED)
            return
        
        # Валидируем gap-анализ
        gap_result_model = await _validate_gap_analysis(gap_analysis)
        
        # Сообщаем о начале обновления
        await message.answer(RESUME_UPDATE_MESSAGES["update_started"])
        
        # Обновляем резюме через LLM
        resume_update_model = await _update_resume_with_llm(parsed_resume, gap_result_model)
        
        # Сохраняем результат в состоянии пользователя
        await state.update_data(updated_resume_llm=resume_update_model.model_dump())
        
        # Форматируем результат для отображения
        result_message_text = format_resume_update_result(resume_update_model)
        
        # Пытаемся обновить резюме на HH.ru, если есть все необходимые данные
        if all([resume_id, access_token, refresh_token, original_resume_data]):
            is_updated = await _update_resume_on_hh(
                resume_id, access_token, refresh_token, 
                original_resume_data, resume_update_model.model_dump()
            )
            
            if is_updated:
                await message.answer(
                    f"{RESUME_UPDATE_MESSAGES['update_completed']}\n\n"
                    f"✅ Ваше резюме на hh.ru также было успешно обновлено!\n\n"
                    f"{result_message_text}",
                    reply_markup=resume_rewrite_keyboard
                )
            else:
                await message.answer(
                    f"{RESUME_UPDATE_MESSAGES['update_completed']} (но произошла ошибка при обновлении на hh.ru)\n\n"
                    f"Пожалуйста, проверьте и обновите ваше резюме на сайте hh.ru вручную.\n\n"
                    f"{result_message_text}",
                    reply_markup=resume_rewrite_keyboard
                )
        else:
            # Если нет необходимых данных для API, просто показываем результат
            await message.answer(
                f"{RESUME_UPDATE_MESSAGES['update_completed']}\n\n"
                f"⚠️ Не удалось автоматически обновить резюме на hh.ru из-за отсутствия необходимых данных.\n"
                f"Пожалуйста, попробуйте пройти авторизацию заново или обратитесь в поддержку.\n\n"
                f"{result_message_text}",
                reply_markup=resume_rewrite_keyboard
            )
        
        await state.set_state(UserState.AUTHORIZED)
        
    except Exception as e:
        logger.error(f"Непредвиденная ошибка в процессе обновления резюме: {e}", exc_info=True)
        await message.answer(RESUME_UPDATE_MESSAGES["update_error"])
        await state.set_state(UserState.AUTHORIZED)

def format_resume_update_result(resume_update: ResumeUpdate) -> str:
    """Форматирует результат обновления резюме для отправки пользователю."""
    result = "📝 Ваше резюме было обновлено:\n\n"
    result += f"👨‍💼 Должность: {resume_update.title}\n\n"
    result += f"🔧 Описание навыков:\n{resume_update.skills}\n\n"
    result += "🛠 Ключевые навыки:\n"
    for skill in resume_update.skill_set:
        result += f"• {skill}\n"
    result += "\n"
    if resume_update.professional_roles:
        result += "👔 Профессиональные роли:\n"
        for role in resume_update.professional_roles:
            result += f"• {role.name}\n"
        result += "\n"
    result += "Для просмотра полного обновленного резюме перейдите на сайт hh.ru и используйте внесенные изменения, если автоматическое обновление не удалось."
    return result