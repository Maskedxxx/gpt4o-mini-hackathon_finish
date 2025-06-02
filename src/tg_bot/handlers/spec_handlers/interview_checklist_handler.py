# src/tg_bot/handlers/spec_handlers/interview_checklist_handler.py
import logging
from aiogram import types
from aiogram.fsm.context import FSMContext

from src.tg_bot.utils import UserState
from src.tg_bot.utils import INTERVIEW_CHECKLIST_MESSAGES
from src.tg_bot.utils import authorized_keyboard
from src.llm_interview_checklist import LLMInterviewChecklistGenerator
from src.models.interview_checklist_models import InterviewChecklist

from src.utils import get_logger
logger = get_logger()

# Создаем экземпляр генератора
llm_interview_checklist_generator = LLMInterviewChecklistGenerator()

def format_interview_checklist_result(checklist: InterviewChecklist) -> str:
    """Форматирует чек-лист подготовки к интервью для отображения пользователю."""
    result = "📋 <b>ПЕРСОНАЛИЗИРОВАННЫЙ ЧЕК-ЛИСТ ПОДГОТОВКИ К ИНТЕРВЬЮ</b>\n\n"
    
    # Основная информация
    result += f"🎯 <b>Позиция:</b> {checklist.position_title}\n\n"
    result += f"📊 <b>Обзор подготовки:</b>\n{checklist.preparation_overview}\n\n"
    result += f"⏱ <b>Рекомендуемое время подготовки:</b> {checklist.estimated_preparation_time}\n\n"
    
    return result

def format_technical_skills(checklist: InterviewChecklist) -> str:
    """Форматирует раздел технических навыков."""
    if not checklist.technical_skills:
        return ""
    
    result = "🛠 <b>ТЕХНИЧЕСКИЕ НАВЫКИ ДЛЯ ИЗУЧЕНИЯ</b>\n\n"
    
    for i, skill in enumerate(checklist.technical_skills, 1):
        priority_emoji = {"Высокий": "🔴", "Средний": "🟡", "Низкий": "🟢"}.get(skill.priority, "⚪")
        
        result += f"<b>{i}. {skill.skill_name}</b> {priority_emoji}\n"
        result += f"📈 Текущий уровень: {skill.current_level_assessment}\n"
        result += f"🎯 Требуемый уровень: {skill.required_level}\n"
        result += f"📚 План изучения: {skill.study_plan}\n"
        
        if skill.resources:
            result += "🔗 Ресурсы для изучения:\n"
            for res in skill.resources[:3]:  # Показываем только первые 3 ресурса
                result += f"   • {res.title} ({res.estimated_time})\n"
                if res.url:
                    result += f"     {res.url}\n"
        result += "\n"
    
    return result

def format_theory_topics(checklist: InterviewChecklist) -> str:
    """Форматирует раздел теоретических тем."""
    if not checklist.theory_topics:
        return ""
    
    result = "📖 <b>ТЕОРЕТИЧЕСКИЕ ТЕМЫ</b>\n\n"
    
    for i, topic in enumerate(checklist.theory_topics, 1):
        result += f"<b>{i}. {topic.topic_name}</b>\n"
        result += f"❗ Важность: {topic.importance}\n"
        result += f"📊 Глубина изучения: {topic.estimated_depth}\n"
        
        if topic.key_concepts:
            result += "🔑 Ключевые концепции:\n"
            for concept in topic.key_concepts[:5]:  # Первые 5 концепций
                result += f"   • {concept}\n"
        
        if topic.study_materials:
            result += "📚 Материалы:\n"
            for material in topic.study_materials[:2]:  # Первые 2 материала
                result += f"   • {material.title} ({material.estimated_time})\n"
        result += "\n"
    
    return result

def format_practical_tasks(checklist: InterviewChecklist) -> str:
    """Форматирует раздел практических задач."""
    if not checklist.practical_tasks:
        return ""
    
    result = "💻 <b>ПРАКТИЧЕСКИЕ ЗАДАЧИ</b>\n\n"
    
    for i, task in enumerate(checklist.practical_tasks, 1):
        difficulty_emoji = {"Начальный": "🟢", "Средний": "🟡", "Продвинутый": "🔴"}.get(task.difficulty_level, "⚪")
        
        result += f"<b>{i}. {task.task_title}</b> {difficulty_emoji}\n"
        result += f"📝 Описание: {task.description}\n"
        
        if task.examples:
            result += "🎯 Примеры задач:\n"
            for example in task.examples[:3]:  # Первые 3 примера
                result += f"   • {example}\n"
        
        if task.practice_resources:
            result += "🎮 Ресурсы для практики:\n"
            for res in task.practice_resources[:2]:  # Первые 2 ресурса
                result += f"   • {res.title}\n"
        result += "\n"
    
    return result

def format_behavioral_questions(checklist: InterviewChecklist) -> str:
    """Форматирует раздел поведенческих вопросов."""
    if not checklist.behavioral_questions:
        return ""
    
    result = "🗣 <b>ПОВЕДЕНЧЕСКИЕ ВОПРОСЫ</b>\n\n"
    
    for i, behavior in enumerate(checklist.behavioral_questions, 1):
        result += f"<b>{i}. {behavior.question_category}</b>\n"
        result += f"💡 Советы по подготовке: {behavior.preparation_tips}\n"
        
        if behavior.example_questions:
            result += "❓ Примеры вопросов:\n"
            for question in behavior.example_questions[:2]:  # Первые 2 вопроса
                result += f"   • {question}\n"
        result += "\n"
    
    return result

def format_final_recommendations(checklist: InterviewChecklist) -> str:
    """Форматирует финальные рекомендации."""
    result = "🏢 <b>ИЗУЧЕНИЕ КОМПАНИИ</b>\n"
    result += f"{checklist.company_research_tips}\n\n"
    
    result += "🎯 <b>ФИНАЛЬНЫЕ РЕКОМЕНДАЦИИ</b>\n"
    result += f"{checklist.final_recommendations}\n\n"
    
    result += "🍀 <b>Удачи на интервью!</b>"
    
    return result

async def start_interview_checklist_generation(message: types.Message, state: FSMContext):
    """Запускает процесс генерации чек-листа подготовки к интервью."""
    user_id = message.from_user.id
    logger.info(f"Запуск генерации чек-листа интервью для пользователя {user_id}")
    
    # Получаем данные из состояния пользователя
    user_data = await state.get_data()
    parsed_resume = user_data.get("parsed_resume")
    parsed_vacancy = user_data.get("parsed_vacancy")
    
    if not parsed_resume or not parsed_vacancy:
        logger.error(f"Отсутствуют данные резюме или вакансии для пользователя {user_id}")
        await message.answer(INTERVIEW_CHECKLIST_MESSAGES['generation_error'])
        await state.set_state(UserState.AUTHORIZED)
        return
    
    # Сообщаем пользователю о начале генерации
    await message.answer(INTERVIEW_CHECKLIST_MESSAGES["generation_started"], reply_markup=authorized_keyboard)
    await state.set_state(UserState.INTERVIEW_CHECKLIST_GENERATION)
    
    try:
        # Запускаем генерацию чек-листа
        checklist_result = await llm_interview_checklist_generator.generate_interview_checklist(parsed_resume, parsed_vacancy)
        
        if not checklist_result:
            logger.error(f"Не удалось сгенерировать чек-лист для пользователя {user_id}")
            await message.answer(INTERVIEW_CHECKLIST_MESSAGES["generation_error"])
            await state.set_state(UserState.AUTHORIZED)
            return
        
        # Сохраняем результат в состоянии пользователя
        await state.update_data(interview_checklist=checklist_result.model_dump())
        
        # Отправляем результат по частям
        await send_checklist_in_parts(message, checklist_result)
        
        await state.set_state(UserState.AUTHORIZED)
        logger.info(f"Чек-лист интервью успешно сгенерирован для пользователя {user_id}")
        
    except Exception as e:
        logger.error(f"Ошибка при генерации чек-листа интервью: {e}")
        await message.answer(INTERVIEW_CHECKLIST_MESSAGES["generation_error"])
        await state.set_state(UserState.AUTHORIZED)

async def send_checklist_in_parts(message: types.Message, checklist: InterviewChecklist):
    """Отправляет чек-лист по частям, чтобы не превысить лимит Telegram."""
    
    # Часть 1: Основная информация
    part1 = format_interview_checklist_result(checklist)
    await message.answer(part1, parse_mode="HTML")
    
    # Часть 2: Технические навыки
    part2 = format_technical_skills(checklist)
    if part2:
        await message.answer(part2, parse_mode="HTML")
    
    # Часть 3: Теоретические темы
    part3 = format_theory_topics(checklist)
    if part3:
        await message.answer(part3, parse_mode="HTML")
    
    # Часть 4: Практические задачи
    part4 = format_practical_tasks(checklist)
    if part4:
        await message.answer(part4, parse_mode="HTML")
    
    # Часть 5: Поведенческие вопросы
    part5 = format_behavioral_questions(checklist)
    if part5:
        await message.answer(part5, parse_mode="HTML")
    
    # Часть 6: Финальные рекомендации
    part6 = format_final_recommendations(checklist)
    await message.answer(part6, reply_markup=authorized_keyboard, parse_mode="HTML")