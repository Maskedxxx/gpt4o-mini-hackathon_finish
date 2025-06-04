# src/tg_bot/handlers/spec_handlers/interview_checklist_handler.py
import logging
from aiogram import types
from aiogram.fsm.context import FSMContext

from src.tg_bot.utils import UserState
from src.tg_bot.utils import INTERVIEW_CHECKLIST_MESSAGES
from src.tg_bot.utils import authorized_keyboard
from src.llm_interview_checklist import LLMInterviewChecklistGenerator
from src.models.interview_checklist_models import (
    InterviewChecklist, 
    ProfessionalInterviewChecklist,
    CandidateLevel,
    VacancyType, 
    CompanyFormat,
    Priority
)

from src.utils import get_logger
logger = get_logger()

# Создаем экземпляр генератора
llm_interview_checklist_generator = LLMInterviewChecklistGenerator()

# =============================================================================
# Форматирование профессионального чек-листа
# =============================================================================

def format_professional_checklist_header(checklist: ProfessionalInterviewChecklist) -> str:
    """Форматирует заголовок профессионального чек-листа."""
    result = "📋 <b>ПРОФЕССИОНАЛЬНЫЙ ЧЕК-ЛИСТ ПОДГОТОВКИ К ИНТЕРВЬЮ</b>\n\n"
    
    # Основная информация
    result += f"🎯 <b>Позиция:</b> {checklist.position_title}\n"
    result += f"🏢 <b>Компания:</b> {checklist.company_name}\n\n"
    
    # Контекст персонализации
    context = checklist.personalization_context
    result += f"👤 <b>Уровень кандидата:</b> {context.candidate_level}\n"
    result += f"💼 <b>Тип вакансии:</b> {context.vacancy_type}\n"
    result += f"🏗 <b>Формат компании:</b> {context.company_format}\n\n"
    
    # Временные оценки
    time_est = checklist.time_estimates
    result += f"⏱ <b>Общее время подготовки:</b> {time_est.total_time_needed}\n"
    result += f"🔴 <b>Критические задачи:</b> {time_est.critical_tasks_time}\n"
    result += f"🟡 <b>Важные задачи:</b> {time_est.important_tasks_time}\n\n"
    
    return result

def format_executive_summary(checklist: ProfessionalInterviewChecklist) -> str:
    """Форматирует исполнительное резюме и стратегию."""
    result = "📊 <b>СТРАТЕГИЯ ПОДГОТОВКИ</b>\n\n"
    
    result += f"<b>📋 Резюме подготовки:</b>\n{checklist.executive_summary}\n\n"
    result += f"<b>🎯 Стратегия:</b>\n{checklist.preparation_strategy}\n\n"
    
    # Ключевые фокусные области
    context = checklist.personalization_context
    if context.critical_focus_areas:
        result += "<b>🔍 Критические области фокуса:</b>\n"
        for area in context.critical_focus_areas[:3]:  # Первые 3
            result += f"• {area}\n"
        result += "\n"
    
    return result

def format_technical_preparation(checklist: ProfessionalInterviewChecklist) -> str:
    """Форматирует блок технической подготовки."""
    if not checklist.technical_preparation:
        return ""
    
    result = "🛠 <b>БЛОК 1: ТЕХНИЧЕСКАЯ ПОДГОТОВКА</b>\n\n"
    
    # Группируем по категориям
    by_category = {}
    for item in checklist.technical_preparation:
        category = item.category
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(item)
    
    category_names = {
        "профильные_знания": "📚 Профильные знания",
        "недостающие_технологии": "🔧 Недостающие технологии", 
        "практические_задачи": "💻 Практические задачи",
        "проекты_код": "📂 Проекты и код",
        "дополнительные_материалы": "📖 Дополнительные материалы"
    }
    
    for category, items in by_category.items():
        if items:
            result += f"<b>{category_names.get(category, category.upper())}</b>\n"
            
            for i, item in enumerate(items[:2], 1):  # Показываем первые 2 в каждой категории
                priority_emoji = {"КРИТИЧНО": "🔴", "ВАЖНО": "🟡", "ЖЕЛАТЕЛЬНО": "🟢"}.get(item.priority, "⚪")
                
                result += f"{i}. <b>{item.task_title}</b> {priority_emoji}\n"
                result += f"   📝 {item.description[:100]}{'...' if len(item.description) > 100 else ''}\n"
                result += f"   ⏱ {item.estimated_time}\n"
                
                if item.specific_resources:
                    result += f"   🔗 {item.specific_resources[0]}\n"  # Первый ресурс
                result += "\n"
            
            if len(items) > 2:
                result += f"   ... и еще {len(items) - 2} задач\n\n"
    
    return result

def format_behavioral_preparation(checklist: ProfessionalInterviewChecklist) -> str:
    """Форматирует блок поведенческой подготовки."""
    if not checklist.behavioral_preparation:
        return ""
    
    result = "🗣 <b>БЛОК 2: ПОВЕДЕНЧЕСКАЯ ПОДГОТОВКА</b>\n\n"
    
    # Группируем по категориям
    by_category = {}
    for item in checklist.behavioral_preparation:
        category = item.category
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(item)
    
    category_names = {
        "типовые_вопросы": "❓ Типовые вопросы",
        "самопрезентация": "🎤 Самопрезентация",
        "поведенческое_интервью": "👥 Поведенческое интервью",
        "storytelling": "📖 Storytelling"
    }
    
    for category, items in by_category.items():
        if items:
            result += f"<b>{category_names.get(category, category.upper())}</b>\n"
            
            for item in items[:1]:  # По 1 примеру на категорию
                result += f"📌 <b>{item.task_title}</b>\n"
                result += f"   {item.description[:120]}{'...' if len(item.description) > 120 else ''}\n"
                
                if item.example_questions:
                    result += f"   💬 Пример: {item.example_questions[0]}\n"
                result += "\n"
    
    return result

def format_company_research(checklist: ProfessionalInterviewChecklist) -> str:
    """Форматирует блок изучения компании."""
    if not checklist.company_research:
        return ""
    
    result = "🏢 <b>БЛОК 3: ИЗУЧЕНИЕ КОМПАНИИ</b>\n\n"
    
    # Группируем по категориям
    by_category = {}
    for item in checklist.company_research:
        category = item.category
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(item)
    
    category_names = {
        "исследование_компании": "🔍 Исследование компании",
        "продукты_отрасль": "📱 Продукты и отрасль",
        "вопросы_работодателю": "❓ Вопросы работодателю"
    }
    
    for category, items in by_category.items():
        if items:
            result += f"<b>{category_names.get(category, category.upper())}</b>\n"
            
            for item in items[:1]:  # По 1 примеру на категорию
                priority_emoji = {"КРИТИЧНО": "🔴", "ВАЖНО": "🟡", "ЖЕЛАТЕЛЬНО": "🟢"}.get(item.priority, "⚪")
                
                result += f"📌 <b>{item.task_title}</b> {priority_emoji}\n"
                if item.specific_actions:
                    result += f"   • {item.specific_actions[0]}\n"
                result += f"   ⏱ {item.time_required}\n\n"
    
    return result

def format_technical_stack_study(checklist: ProfessionalInterviewChecklist) -> str:
    """Форматирует блок изучения технического стека."""
    if not checklist.technical_stack_study:
        return ""
    
    result = "🔧 <b>БЛОК 4: ИЗУЧЕНИЕ ТЕХНИЧЕСКОГО СТЕКА</b>\n\n"
    
    # Группируем по категориям
    by_category = {}
    for item in checklist.technical_stack_study:
        category = item.category
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(item)
    
    category_names = {
        "требования_вакансии": "📋 Требования вакансии",
        "технологии_компании": "🏗 Технологии компании",
        "рабочие_процессы": "⚙️ Рабочие процессы",
        "терминология": "📚 Терминология"
    }
    
    for category, items in by_category.items():
        if items:
            result += f"<b>{category_names.get(category, category.upper())}</b>\n"
            
            for item in items[:2]:  # По 2 примера на категорию
                result += f"📌 <b>{item.task_title}</b>\n"
                result += f"   {item.description[:120]}{'...' if len(item.description) > 120 else ''}\n"
                result += f"   💡 {item.relevance_explanation[:80]}{'...' if len(item.relevance_explanation) > 80 else ''}\n\n"
    
    return result

def format_practical_exercises(checklist: ProfessionalInterviewChecklist) -> str:
    """Форматирует блок практических упражнений."""
    if not checklist.practical_exercises:
        return ""
    
    result = "💪 <b>БЛОК 5: ПРАКТИЧЕСКИЕ УПРАЖНЕНИЯ</b>\n\n"
    
    # Группируем по уровню сложности и показываем самые важные
    by_difficulty = {"базовый": [], "средний": [], "продвинутый": []}
    
    for item in checklist.practical_exercises:
        difficulty = item.difficulty_level
        if difficulty in by_difficulty:
            by_difficulty[difficulty].append(item)
    
    difficulty_emoji = {"базовый": "🟢", "средний": "🟡", "продвинутый": "🔴"}
    
    for difficulty, items in by_difficulty.items():
        if items:
            result += f"<b>{difficulty_emoji[difficulty]} {difficulty.upper()}</b>\n"
            
            for item in items[:2]:  # По 2 примера на уровень
                result += f"📌 <b>{item.exercise_title}</b>\n"
                result += f"   {item.description[:100]}{'...' if len(item.description) > 100 else ''}\n"
                if item.practice_resources:
                    result += f"   🔗 {item.practice_resources[0]}\n"
                result += "\n"
    
    return result

def format_interview_setup(checklist: ProfessionalInterviewChecklist) -> str:
    """Форматирует блок настройки окружения для интервью."""
    if not checklist.interview_setup:
        return ""
    
    result = "🖥 <b>БЛОК 6: НАСТРОЙКА ОКРУЖЕНИЯ ДЛЯ ИНТЕРВЬЮ</b>\n\n"
    
    # Группируем по категориям
    by_category = {}
    for item in checklist.interview_setup:
        category = item.category
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(item)
    
    category_names = {
        "оборудование_связь": "📱 Оборудование и связь",
        "место_проведения": "🏠 Место проведения",
        "аккаунты_доступы": "🔐 Аккаунты и доступы",
        "резервные_варианты": "🔄 Резервные варианты",
        "внешний_вид": "👔 Внешний вид"
    }
    
    for category, items in by_category.items():
        if items:
            result += f"<b>{category_names.get(category, category.upper())}</b>\n"
            
            for item in items[:1]:  # По 1 примеру на категорию
                result += f"📌 <b>{item.task_title}</b>\n"
                if item.checklist_items:
                    result += f"   ✅ {item.checklist_items[0]}\n"
                    if len(item.checklist_items) > 1:
                        result += f"   ✅ {item.checklist_items[1]}\n"
                result += "\n"
    
    return result

def format_additional_actions(checklist: ProfessionalInterviewChecklist) -> str:
    """Форматирует блок дополнительных действий кандидата."""
    if not checklist.additional_actions:
        return ""
    
    result = "📝 <b>БЛОК 7: ДОПОЛНИТЕЛЬНЫЕ ДЕЙСТВИЯ</b>\n\n"
    
    # Группируем по категориям
    by_category = {}
    for item in checklist.additional_actions:
        category = item.category
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(item)
    
    category_names = {
        "рекомендации": "👥 Рекомендации",
        "профили": "💼 Профили и онлайн-присутствие",
        "документы": "📄 Документы и сертификаты",
        "резюме_письмо": "📋 Резюме и письмо",
        "настрой_отдых": "🧘 Настрой и отдых"
    }
    
    for category, items in by_category.items():
        if items:
            result += f"<b>{category_names.get(category, category.upper())}</b>\n"
            
            for item in items[:1]:  # По 1 примеру на категорию
                urgency_emoji = {"КРИТИЧНО": "🔴", "ВАЖНО": "🟡", "ЖЕЛАТЕЛЬНО": "🟢"}.get(item.urgency, "⚪")
                
                result += f"📌 <b>{item.action_title}</b> {urgency_emoji}\n"
                result += f"   {item.description[:100]}{'...' if len(item.description) > 100 else ''}\n"
                if item.implementation_steps:
                    result += f"   🔸 {item.implementation_steps[0]}\n"
                result += "\n"
    
    return result

def format_critical_success_factors(checklist: ProfessionalInterviewChecklist) -> str:
    """Форматирует критические факторы успеха и финальные рекомендации."""
    result = "🎯 <b>КРИТИЧЕСКИЕ ФАКТОРЫ УСПЕХА</b>\n\n"
    
    # Критические факторы
    if checklist.critical_success_factors:
        for i, factor in enumerate(checklist.critical_success_factors[:3], 1):
            result += f"{i}. {factor}\n"
        result += "\n"
    
    # Ошибки, которых следует избегать
    if checklist.common_mistakes_to_avoid:
        result += "<b>⚠️ ИЗБЕГАЙТЕ ЭТИХ ОШИБОК:</b>\n"
        for mistake in checklist.common_mistakes_to_avoid[:3]:
            result += f"• {mistake}\n"
        result += "\n"
    
    # Чек-лист последней минуты
    if checklist.last_minute_checklist:
        result += "<b>⏰ ПОСЛЕДНЯЯ МИНУТА:</b>\n"
        for item in checklist.last_minute_checklist[:3]:
            result += f"✅ {item}\n"
        result += "\n"
    
    # Мотивационное сообщение
    result += f"<b>🚀 МОТИВАЦИЯ:</b>\n{checklist.motivation_boost}"
    
    return result

# =============================================================================
# Функции для старой модели (обратная совместимость)
# =============================================================================

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

# =============================================================================
# Основные функции обработки
# =============================================================================

async def start_interview_checklist_generation(message: types.Message, state: FSMContext):
    """Запускает процесс генерации профессионального чек-листа подготовки к интервью."""
    user_id = message.from_user.id
    logger.info(f"Запуск генерации профессионального чек-листа интервью для пользователя {user_id}")
    
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
    progress_msg = await message.answer(
        "📋 Создаю профессиональный чек-лист подготовки к интервью...\n\n"
        "🔍 Анализирую профиль кандидата и тип вакансии\n"
        "📊 Определяю стратегию подготовки\n"
        "🎯 Формирую персонализированные рекомендации\n"
        "⏱ Рассчитываю временные рамки\n\n"
        "⏳ Это займет 1-2 минуты...",
        reply_markup=authorized_keyboard
    )
    await state.set_state(UserState.INTERVIEW_CHECKLIST_GENERATION)
    
    try:
        # Пробуем сначала новую профессиональную версию
        try:
            checklist_result = await llm_interview_checklist_generator.generate_professional_interview_checklist(
                parsed_resume, parsed_vacancy
            )
            
            if checklist_result:
                # Сохраняем результат в состоянии пользователя
                await state.update_data(professional_interview_checklist=checklist_result.model_dump())
                
                # Отправляем результат по частям
                await send_professional_checklist_in_parts(message, checklist_result, progress_msg)
                
                await state.set_state(UserState.AUTHORIZED)
                logger.info(f"Профессиональный чек-лист интервью успешно сгенерирован для пользователя {user_id}")
                return
            
        except Exception as e:
            logger.warning(f"Ошибка при генерации профессионального чек-листа, пробуем старую версию: {e}")
        
        # Fallback на старую версию
        logger.info(f"Использование старой версии чек-листа для пользователя {user_id}")
        await progress_msg.edit_text("📋 Создаю чек-лист подготовки к интервью...")
        
        checklist_result = await llm_interview_checklist_generator.generate_interview_checklist(
            parsed_resume, parsed_vacancy
        )
        
        if not checklist_result:
            logger.error(f"Не удалось сгенерировать чек-лист для пользователя {user_id}")
            await progress_msg.edit_text(INTERVIEW_CHECKLIST_MESSAGES["generation_error"])
            await state.set_state(UserState.AUTHORIZED)
            return
        
        # Сохраняем результат в состоянии пользователя
        await state.update_data(interview_checklist=checklist_result.model_dump())
        
        # Удаляем сообщение прогресса
        try:
            await progress_msg.delete()
        except:
            pass
        
        # Отправляем результат по частям (старая версия)
        await send_checklist_in_parts(message, checklist_result)
        
        await state.set_state(UserState.AUTHORIZED)
        logger.info(f"Чек-лист интервью (старая версия) успешно сгенерирован для пользователя {user_id}")
        
    except Exception as e:
        logger.error(f"Критическая ошибка при генерации чек-листа интервью: {e}")
        await progress_msg.edit_text(INTERVIEW_CHECKLIST_MESSAGES["generation_error"])
        await state.set_state(UserState.AUTHORIZED)

async def send_professional_checklist_in_parts(
    message: types.Message, 
    checklist: ProfessionalInterviewChecklist,
    progress_msg: types.Message
):
    """Отправляет профессиональный чек-лист по частям со всеми 7 блоками."""
    
    # Удаляем сообщение о прогрессе
    try:
        await progress_msg.delete()
    except:
        pass
    
    # Часть 1: Заголовок и контекст
    header = format_professional_checklist_header(checklist)
    await message.answer(header, parse_mode="HTML")
    
    # Часть 2: Стратегия подготовки
    summary = format_executive_summary(checklist)
    await message.answer(summary, parse_mode="HTML")
    
    # Часть 3: БЛОК 1 - Техническая подготовка
    technical = format_technical_preparation(checklist)
    if technical:
        await message.answer(technical, parse_mode="HTML")
    
    # Часть 4: БЛОК 2 - Поведенческая подготовка
    behavioral = format_behavioral_preparation(checklist)
    if behavioral:
        await message.answer(behavioral, parse_mode="HTML")
    
    # Часть 5: БЛОК 3 - Изучение компании
    company = format_company_research(checklist)
    if company:
        await message.answer(company, parse_mode="HTML")
    
    # Часть 6: БЛОК 4 - Изучение технического стека 🆕
    tech_stack = format_technical_stack_study(checklist)
    if tech_stack:
        await message.answer(tech_stack, parse_mode="HTML")
    
    # Часть 7: БЛОК 5 - Практические упражнения
    exercises = format_practical_exercises(checklist)
    if exercises:
        await message.answer(exercises, parse_mode="HTML")
    
    # Часть 8: БЛОК 6 - Настройка окружения для интервью 🆕
    setup = format_interview_setup(checklist)
    if setup:
        await message.answer(setup, parse_mode="HTML")
    
    # Часть 9: БЛОК 7 - Дополнительные действия 🆕
    additional = format_additional_actions(checklist)
    if additional:
        await message.answer(additional, parse_mode="HTML")
    
    # Часть 10: Критические факторы успеха (финальная с клавиатурой)
    success_factors = format_critical_success_factors(checklist)
    await message.answer(success_factors, reply_markup=authorized_keyboard, parse_mode="HTML")

async def send_checklist_in_parts(message: types.Message, checklist: InterviewChecklist):
    """Отправляет чек-лист по частям, чтобы не превысить лимит Telegram (старая версия)."""
    
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