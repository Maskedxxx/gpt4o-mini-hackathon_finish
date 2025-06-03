# src/tg_bot/handlers/gap_analyzer_handler.py
import logging
from aiogram import types
from aiogram.fsm.context import FSMContext
from langsmith import traceable, Client
import os

from src.tg_bot.utils import UserState
from src.tg_bot.utils import GAP_ANALYZE_MESSAGES
from src.tg_bot.utils import authorized_keyboard
from src.llm_gap_analyzer import LLMGapAnalyzer
from src.models.gap_analysis_models import EnhancedResumeTailoringAnalysis


from src.utils import get_logger
logger = get_logger()



# Создаём клиент LangSmith
def create_langsmith_client():
    api_key = os.getenv("LANGCHAIN_API_KEY")
    if not api_key:
        return print("LANGCHAIN_API_KEY не установлен, трейсинг будет отключен")
    return Client(api_key=api_key)

ls_client = create_langsmith_client()

# Создаем экземпляр анализатора
llm_analyzer = LLMGapAnalyzer()

def format_primary_screening(analysis) -> str:
    """Форматирует результаты первичного скрининга."""
    screening = analysis.primary_screening
    
    # Эмодзи для результатов
    def bool_emoji(value: bool) -> str:
        return "✅" if value else "❌"
    
    result_emoji = {
        "PASS": "✅",
        "MAYBE": "⚠️", 
        "REJECT": "❌"
    }
    
    result = "📋 ПЕРВИЧНЫЙ СКРИНИНГ (7-15 секунд)\n\n"
    
    result += f"{bool_emoji(screening.job_title_match)} Соответствие должности: {'Да' if screening.job_title_match else 'Нет'}\n"
    result += f"{bool_emoji(screening.experience_years_match)} Достаточно стажа: {'Да' if screening.experience_years_match else 'Нет'}\n"
    result += f"{bool_emoji(screening.key_skills_visible)} Ключевые навыки видны: {'Да' if screening.key_skills_visible else 'Нет'}\n"
    result += f"{bool_emoji(screening.location_suitable)} Локация подходит: {'Да' if screening.location_suitable else 'Нет'}\n"
    result += f"{bool_emoji(screening.salary_expectations_match)} Зарплатные ожидания: {'Совпадают' if screening.salary_expectations_match else 'Не совпадают'}\n\n"
    
    result += f"{result_emoji.get(screening.overall_screening_result, '❓')} ИТОГ СКРИНИНГА: {screening.overall_screening_result}\n\n"
    result += f"💬 Комментарии:\n{screening.screening_notes}"
    
    return result

def format_requirements_analysis(analysis) -> str:
    """Форматирует анализ требований."""
    if not analysis.requirements_analysis:
        return ""
    
    result = "🔍 АНАЛИЗ ТРЕБОВАНИЙ ВАКАНСИИ\n\n"
    
    # Группируем по типам требований
    must_have = [r for r in analysis.requirements_analysis if r.requirement_type == "MUST_HAVE"]
    nice_to_have = [r for r in analysis.requirements_analysis if r.requirement_type == "NICE_TO_HAVE"]
    bonus = [r for r in analysis.requirements_analysis if r.requirement_type == "BONUS"]
    
    def format_requirement_group(requirements, title, emoji):
        if not requirements:
            return ""
        
        group_result = f"{emoji} {title}\n"
        
        for req in requirements[:3]:  # Показываем только первые 3
            status_emoji = {
                "ПОЛНОЕ_СООТВЕТСТВИЕ": "✅",
                "ЧАСТИЧНОЕ_СООТВЕТСТВИЕ": "⚠️",
                "ОТСУТСТВУЕТ": "❌",
                "ТРЕБУЕТ_УТОЧНЕНИЯ": "🔍"
            }
            
            emoji_status = status_emoji.get(req.compliance_status, "❓")
            group_result += f"  {emoji_status} {req.requirement_text[:60]}{'...' if len(req.requirement_text) > 60 else ''}\n"
            
            if req.gap_description and req.compliance_status != "ПОЛНОЕ_СООТВЕТСТВИЕ":
                group_result += f"     💡 {req.gap_description[:80]}{'...' if len(req.gap_description) > 80 else ''}\n"
        
        if len(requirements) > 3:
            group_result += f"     ... и еще {len(requirements) - 3} требований\n"
        
        return group_result + "\n"
    
    result += format_requirement_group(must_have, "ОБЯЗАТЕЛЬНЫЕ ТРЕБОВАНИЯ", "🔴")
    result += format_requirement_group(nice_to_have, "ЖЕЛАТЕЛЬНЫЕ ТРЕБОВАНИЯ", "🟡")
    result += format_requirement_group(bonus, "ДОПОЛНИТЕЛЬНЫЕ ПЛЮСЫ", "🟢")
    
    return result

def format_quality_assessment(analysis) -> str:
    """Форматирует оценку качества резюме."""
    quality = analysis.quality_assessment
    
    def score_bar(score: int) -> str:
        """Создает визуальную полоску оценки."""
        filled = "▓" * score
        empty = "░" * (10 - score)
        return f"{filled}{empty} {score}/10"
    
    impression_emoji = {
        "STRONG": "🔥",
        "AVERAGE": "👍",
        "WEAK": "👎"
    }
    
    result = "📊 ОЦЕНКА КАЧЕСТВА РЕЗЮМЕ\n\n"
    
    result += f"🏗 Структурированность:\n{score_bar(quality.structure_clarity)}\n\n"
    result += f"🎯 Релевантность:\n{score_bar(quality.content_relevance)}\n\n"
    result += f"🏆 Фокус на достижения:\n{score_bar(quality.achievement_focus)}\n\n"
    result += f"🔧 Адаптация под вакансию:\n{score_bar(quality.adaptation_quality)}\n\n"
    
    emoji = impression_emoji.get(quality.overall_impression, "❓")
    result += f"{emoji} ОБЩЕЕ ВПЕЧАТЛЕНИЕ: {quality.overall_impression}\n\n"
    result += f"💬 {quality.quality_notes}"
    
    return result

def format_recommendations(analysis) -> str:
    """Форматирует рекомендации по улучшению."""
    result = "💡 РЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ\n\n"
    
    def format_recommendation_group(recommendations, title, emoji):
        if not recommendations:
            return ""
        
        group_result = f"{emoji} {title}\n"
        
        for i, rec in enumerate(recommendations[:3], 1):  # Показываем только первые 3
            group_result += f"{i}. {rec.section.upper()}: {rec.issue_description}\n"
            
            # Показываем первое действие
            if rec.specific_actions:
                group_result += f"   📝 {rec.specific_actions[0]}\n"
            
            # Показываем пример, если есть
            if rec.example_wording:
                example = rec.example_wording[:80] + "..." if len(rec.example_wording) > 80 else rec.example_wording
                group_result += f"   💡 Пример: {example}\n"
            
            group_result += "\n"
        
        if len(recommendations) > 3:
            group_result += f"... и еще {len(recommendations) - 3} рекомендаций\n\n"
        
        return group_result
    
    result += format_recommendation_group(analysis.critical_recommendations, "КРИТИЧНЫЕ (ОБЯЗАТЕЛЬНО)", "🔴")
    result += format_recommendation_group(analysis.important_recommendations, "ВАЖНЫЕ", "🟡")
    result += format_recommendation_group(analysis.optional_recommendations, "ЖЕЛАТЕЛЬНЫЕ", "🟢")
    
    return result

def format_final_conclusion(analysis) -> str:
    """Форматирует итоговые выводы."""
    hiring_emoji = {
        "STRONG_YES": "🔥",
        "YES": "✅",
        "MAYBE": "🤔",
        "NO": "❌", 
        "STRONG_NO": "🚫"
    }
    
    result = "🎯 ИТОГОВЫЕ ВЫВОДЫ\n\n"
    
    # Процент соответствия с визуализацией
    percentage = analysis.overall_match_percentage
    filled_blocks = percentage // 10
    progress_bar = "▓" * filled_blocks + "░" * (10 - filled_blocks)
    result += f"📊 Соответствие вакансии: {progress_bar} {percentage}%\n\n"
    
    # Рекомендация по найму
    emoji = hiring_emoji.get(analysis.hiring_recommendation, "❓")
    result += f"{emoji} РЕКОМЕНДАЦИЯ ПО НАЙМУ: {analysis.hiring_recommendation}\n\n"
    
    # Сильные стороны
    if analysis.key_strengths:
        result += "💪 КЛЮЧЕВЫЕ СИЛЬНЫЕ СТОРОНЫ:\n"
        for strength in analysis.key_strengths[:3]:  # Показываем первые 3
            result += f"• {strength}\n"
        if len(analysis.key_strengths) > 3:
            result += f"• ... и еще {len(analysis.key_strengths) - 3}\n"
        result += "\n"
    
    # Основные пробелы
    if analysis.major_gaps:
        result += "⚠️ ОСНОВНЫЕ ПРОБЕЛЫ:\n"
        for gap in analysis.major_gaps[:3]:  # Показываем первые 3
            result += f"• {gap}\n"
        if len(analysis.major_gaps) > 3:
            result += f"• ... и еще {len(analysis.major_gaps) - 3}\n"
        result += "\n"
    
    # Следующие шаги
    result += f"👣 СЛЕДУЮЩИЕ ШАГИ:\n{analysis.next_steps}"
    
    return result

def format_enhanced_gap_analysis_preview(analysis) -> str:
    """Форматирует краткий обзор анализа."""
    result = "📊 РАСШИРЕННЫЙ GAP-АНАЛИЗ ЗАВЕРШЕН\n\n"
    
    screening_result = analysis.primary_screening.overall_screening_result
    screening_emoji = {"PASS": "✅", "MAYBE": "⚠️", "REJECT": "❌"}
    
    result += f"{screening_emoji.get(screening_result, '❓')} Скрининг: {screening_result}\n"
    result += f"📊 Соответствие: {analysis.overall_match_percentage}%\n"
    result += f"🎯 Рекомендация: {analysis.hiring_recommendation}\n\n"
    
    result += f"🔴 Критичных рекомендаций: {len(analysis.critical_recommendations)}\n"
    result += f"🟡 Важных рекомендаций: {len(analysis.important_recommendations)}\n"
    result += f"🟢 Желательных улучшений: {len(analysis.optional_recommendations)}\n\n"
    
    result += "📱 Детальный анализ будет отправлен по частям..."
    
    return result

@traceable(client=ls_client, project_name="llamaindex_test", run_type = "retriever")
async def start_gap_analysis(message: types.Message, state: FSMContext):
    """Запускает процесс расширенного gap-анализа резюме."""
    user_id = message.from_user.id
    logger.info(f"Запуск расширенного gap-анализа для пользователя {user_id}")
    
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
        # Запускаем расширенный gap-анализ
        gap_analysis_result = await llm_analyzer.gap_analysis(parsed_resume, parsed_vacancy)
        
        if not gap_analysis_result:
            logger.error(f"Не удалось выполнить расширенный gap-анализ для пользователя {user_id}")
            await message.answer(GAP_ANALYZE_MESSAGES["analysis_error"])
            await state.set_state(UserState.AUTHORIZED)
            return
        
        # Сохраняем результаты анализа в состоянии пользователя
        await state.update_data(gap_analysis=gap_analysis_result.model_dump())
        
        # Отправляем результаты по частям
        await send_enhanced_gap_analysis_in_parts(message, gap_analysis_result)
        
        await state.set_state(UserState.AUTHORIZED)
        logger.info(f"Расширенный gap-анализ успешно завершен для пользователя {user_id}")
        
    except Exception as e:
        logger.error(f"Ошибка при выполнении расширенного gap-анализа: {e}")
        await message.answer(GAP_ANALYZE_MESSAGES["analysis_error"])
        await state.set_state(UserState.AUTHORIZED)

async def send_enhanced_gap_analysis_in_parts(message: types.Message, analysis: EnhancedResumeTailoringAnalysis):
    """Отправляет результаты расширенного анализа по частям."""
    
    # Часть 1: Краткий обзор
    preview = format_enhanced_gap_analysis_preview(analysis)
    await message.answer(preview)
    
    # Небольшая пауза между сообщениями
    import asyncio
    await asyncio.sleep(1)
    
    # Часть 2: Первичный скрининг
    screening = format_primary_screening(analysis)
    await message.answer(screening)
    
    await asyncio.sleep(1)
    
    # Часть 3: Анализ требований
    requirements = format_requirements_analysis(analysis)
    if requirements:
        await message.answer(requirements)
        await asyncio.sleep(1)
    
    # Часть 4: Оценка качества
    quality = format_quality_assessment(analysis)
    await message.answer(quality)
    
    await asyncio.sleep(1)
    
    # Часть 5: Рекомендации
    recommendations = format_recommendations(analysis)
    await message.answer(recommendations)
    
    await asyncio.sleep(1)
    
    # Часть 6: Итоговые выводы (с клавиатурой)
    conclusion = format_final_conclusion(analysis)
    await message.answer(conclusion, reply_markup=authorized_keyboard)
