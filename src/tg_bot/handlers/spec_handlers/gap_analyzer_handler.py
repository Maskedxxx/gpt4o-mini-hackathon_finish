# src/tg_bot/handlers/gap_analyzer_handler.py
import logging
from aiogram import types
from aiogram.fsm.context import FSMContext

from src.tg_bot.utils import UserState
from src.tg_bot.utils import GAP_ANALYZE_MESSAGES
from src.tg_bot.utils import resume_rewrite_keyboard
from src.llm_gap_analyzer import LLMGapAnalyzer

logger = logging.getLogger("gap_analyzer_handler")

# Создаем экземпляр анализатора
llm_analyzer = LLMGapAnalyzer()

async def start_gap_analysis(message: types.Message, state: FSMContext):
    """Запускает процесс gap-анализа резюме."""
    user_id = message.from_user.id
    logger.info(f"Запуск gap-анализа для пользователя {user_id}")
    
    # Получаем данные из состояния пользователя
    user_data = await state.get_data()
    parsed_resume = user_data.get("parsed_resume")
    parsed_vacancy = user_data.get("parsed_vacancy")
    
    if not parsed_resume or not parsed_vacancy:
        logger.error(f"parser_error для {user_id}")
        await message.answer(GAP_ANALYZE_MESSAGES['analysis_error'])
        await state.set_state(UserState.AUTHORIZED)
        return
    
    # Сообщаем пользователю о начале анализа
    await message.answer(GAP_ANALYZE_MESSAGES["analysis_started"], reply_markup=resume_rewrite_keyboard)
    await state.set_state(UserState.RESUME_GAP_ANALYZE)
    
    try:
        # Запускаем gap-анализ
        gap_analysis_result = await llm_analyzer.gap_analysis(parsed_resume, parsed_vacancy)
        
        if not gap_analysis_result:
            logger.error(f"Не удалось выполнить gap-анализ для пользователя {user_id}")
            await message.answer(GAP_ANALYZE_MESSAGES["analysis_error"])
            return
        
        # Сохраняем результаты анализа в состоянии пользователя
        await state.update_data(gap_analysis=gap_analysis_result.model_dump())
        
        # Отправляем результаты пользователю
        await message.answer(f"{GAP_ANALYZE_MESSAGES['analysis_completed']}", reply_markup=resume_rewrite_keyboard)
        
        # Переходим к обновлению резюме
        from src.tg_bot.handlers.spec_handlers.resume_update_handler import start_resume_update
        await start_resume_update(message, state)
        
    except Exception as e:
        logger.error(f"Ошибка при выполнении gap-анализа: {e}")
        await message.answer(GAP_ANALYZE_MESSAGES["analysis_error"])
