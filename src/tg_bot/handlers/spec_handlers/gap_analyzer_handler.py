# src/tg_bot/handlers/gap_analyzer_handler.py
import logging
from aiogram import types
from aiogram.fsm.context import FSMContext

from src.tg_bot.utils import UserState
from src.tg_bot.utils import GAP_ANALYZE_MESSAGES
from src.tg_bot.utils import authorized_keyboard
from src.llm_gap_analyzer import LLMGapAnalyzer
from src.models.gap_analysis_models import ResumeTailoringAnalysis

from src.utils import get_logger
logger = get_logger()

# Создаем экземпляр анализатора
llm_analyzer = LLMGapAnalyzer()

def format_gap_analysis_result(gap_analysis: ResumeTailoringAnalysis) -> str:
    """Форматирует результат gap-анализа для отображения пользователю."""
    result = "📊 <b>РЕЗУЛЬТАТЫ АНАЛИЗА РЕЗЮМЕ</b>\n\n"
    
    # Предлагаемый заголовок
    result += f"🎯 <b>Рекомендуемая должность:</b>\n{gap_analysis.suggested_resume_title}\n\n"
    
    # Предлагаемое описание навыков
    result += f"📝 <b>Рекомендуемое описание навыков:</b>\n{gap_analysis.suggested_skills_description_for_rewriter}\n\n"
    
    # Рекомендуемые ключевые навыки
    result += "🛠 <b>Рекомендуемые ключевые навыки:</b>\n"
    for skill in gap_analysis.suggested_skill_set_for_rewriter:
        result += f"• {skill}\n"
    result += "\n"
    
    # Рекомендации по опыту работы
    result += "💼 <b>РЕКОМЕНДАЦИИ ПО ОПЫТУ РАБОТЫ:</b>\n\n"
    
    for i, exp_report in enumerate(gap_analysis.experience_reports, 1):
        result += f"<b>{i}. {exp_report.experience_identifier}</b>\n"
        result += f"📋 Оценка: {exp_report.overall_assessment}\n\n"
        
        if exp_report.modification_instructions:
            result += "🔧 Рекомендации по улучшению:\n"
            for j, instruction in enumerate(exp_report.modification_instructions, 1):
                action_emoji = {
                    "ADD": "➕",
                    "UPDATE": "✏️", 
                    "DELETE": "❌",
                    "HIGHLIGHT": "⭐"
                }.get(instruction.action, "📌")
                
                result += f"{action_emoji} {instruction.action}: {instruction.instruction_details}\n"
                result += f"   💡 Обоснование: {instruction.vacancy_relevance_reason}\n"
            result += "\n"
    
    result += "💡 <b>Используйте эти рекомендации для самостоятельного улучшения вашего резюме!</b>"
    return result

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
    await message.answer(GAP_ANALYZE_MESSAGES["analysis_started"], reply_markup=authorized_keyboard)
    await state.set_state(UserState.RESUME_GAP_ANALYZE)
    
    try:
        # Запускаем gap-анализ
        gap_analysis_result = await llm_analyzer.gap_analysis(parsed_resume, parsed_vacancy)
        
        if not gap_analysis_result:
            logger.error(f"Не удалось выполнить gap-анализ для пользователя {user_id}")
            await message.answer(GAP_ANALYZE_MESSAGES["analysis_error"])
            await state.set_state(UserState.AUTHORIZED)
            return
        
        # Сохраняем результаты анализа в состоянии пользователя
        await state.update_data(gap_analysis=gap_analysis_result.model_dump())
        
        # Форматируем и отправляем результаты пользователю
        formatted_result = format_gap_analysis_result(gap_analysis_result)
        
        # Отправляем результаты (разбиваем на части если сообщение слишком длинное)
        max_length = 4000  # Telegram лимит ~4096 символов
        if len(formatted_result) <= max_length:
            await message.answer(formatted_result, reply_markup=authorized_keyboard, parse_mode="Markdown")
        else:
            # Разбиваем на части
            parts = []
            current_part = ""
            lines = formatted_result.split('\n')
            
            for line in lines:
                if len(current_part + line + '\n') <= max_length:
                    current_part += line + '\n'
                else:
                    if current_part:
                        parts.append(current_part.strip())
                    current_part = line + '\n'
            
            if current_part:
                parts.append(current_part.strip())
            
            # Отправляем части
            for i, part in enumerate(parts):
                if i == len(parts) - 1:  # Последняя часть с клавиатурой
                    await message.answer(part, reply_markup=authorized_keyboard, parse_mode="Markdown")
                else:
                    await message.answer(part, parse_mode="Markdown")
        
        await state.set_state(UserState.AUTHORIZED)
        logger.info(f"Gap-анализ успешно завершен для пользователя {user_id}")
        
    except Exception as e:
        logger.error(f"Ошибка при выполнении gap-анализа: {e}")
        await message.answer(GAP_ANALYZE_MESSAGES["analysis_error"])
        await state.set_state(UserState.AUTHORIZED)