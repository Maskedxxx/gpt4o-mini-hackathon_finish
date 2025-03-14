# src/tg_bot/handlers/spec_handlers/resume_update_handler.py
import logging
from aiogram import types
from aiogram.fsm.context import FSMContext

from src.tg_bot.utils import UserState
from src.tg_bot.utils import RESUME_UPDATE_MESSAGES
from src.tg_bot.utils import resume_rewrite_keyboard
from src.llm_update_resume import LLMResumeUpdater
from src.models.resume_update_models import ResumeUpdate
from src.models.gap_analysis_models import ResumeGapAnalysis

logger = logging.getLogger("resume_update_handler")

# Создаем экземпляр сервиса обновления резюме
llm_resume_updater = LLMResumeUpdater()

async def start_resume_update(message: types.Message, state: FSMContext):
    """
    Запускает процесс обновления резюме на основе GAP-анализа.
    
    Args:
        message: Сообщение пользователя
        state: Состояние пользователя FSM
    """
    user_id = message.from_user.id
    logger.info(f"Запуск обновления резюме для пользователя {user_id}")
    
    # Получаем данные из состояния пользователя
    user_data = await state.get_data()
    parsed_resume = user_data.get("parsed_resume")
    gap_analysis = user_data.get("gap_analysis")
    
    if not parsed_resume or not gap_analysis:
        logger.error(f"Недостаточно данных для обновления резюме пользователя {user_id}")
        await message.answer(RESUME_UPDATE_MESSAGES["update_error"])
        await state.set_state(UserState.AUTHORIZED)
        return
    
    # Преобразуем словарь gap_analysis в объект ResumeGapAnalysis
    try:
        gap_result = ResumeGapAnalysis.model_validate(gap_analysis)
    except Exception as e:
        logger.error(f"Ошибка при валидации gap-анализа: {e}")
        await message.answer(RESUME_UPDATE_MESSAGES["update_error"])
        await state.set_state(UserState.AUTHORIZED)
        return
    
    # Сообщаем пользователю о начале обновления резюме
    await message.answer(RESUME_UPDATE_MESSAGES["update_started"])
    
    try:
        # Запускаем обновление резюме
        resume_update_result = await llm_resume_updater.update_resume(parsed_resume, gap_result)
        
        if not resume_update_result:
            logger.error(f"Не удалось обновить резюме для пользователя {user_id}")
            await message.answer(RESUME_UPDATE_MESSAGES["update_error"])
            await state.set_state(UserState.AUTHORIZED)
            return
        
        # Сохраняем обновленное резюме в состоянии пользователя
        await state.update_data(updated_resume=resume_update_result.model_dump())
        
        # Формируем сообщение с результатами
        result_message = format_resume_update_result(resume_update_result)
        
        # Отправляем результаты пользователю
        await message.answer(f"{RESUME_UPDATE_MESSAGES['update_completed']}\n\n{result_message}", reply_markup=resume_rewrite_keyboard)
        await state.set_state(UserState.AUTHORIZED)
        
    except Exception as e:
        logger.error(f"Ошибка при обновлении резюме: {e}")
        await message.answer(RESUME_UPDATE_MESSAGES["update_error"])
        await state.set_state(UserState.AUTHORIZED)


# для тестирования?
def format_resume_update_result(resume_update: ResumeUpdate) -> str:
    """
    Форматирует результат обновления резюме для отправки пользователю.
    
    Args:
        resume_update: Объект с обновленным резюме
        
    Returns:
        str: Отформатированный текст сообщения
    """
    result = "📝 Ваше резюме было обновлено:\n\n"
    
    # Добавляем информацию о новой желаемой должности
    result += f"👨‍💼 Должность: {resume_update.title}\n\n"
    
    # Добавляем информацию о навыках
    result += f"🔧 Описание навыков:\n{resume_update.skills}\n\n"
    
    # Добавляем список ключевых навыков
    result += "🛠 Ключевые навыки:\n"
    for skill in resume_update.skill_set:
        result += f"• {skill}\n"
    result += "\n"
    
    # Добавляем профессиональные роли
    if resume_update.professional_roles:
        result += "👔 Профессиональные роли:\n"
        for role in resume_update.professional_roles:
            result += f"• {role.name}\n"
        result += "\n"
    
    result += "Для просмотра полного обновленного резюме перейдите на сайт hh.ru и используйте внесенные изменения."
    
    return result