# src/tg_bot/handlers/spec_handlers/interview_simulation_handler.py
import logging
from aiogram import types
from aiogram.fsm.context import FSMContext

from src.tg_bot.utils import UserState
from src.tg_bot.utils import INTERVIEW_SIMULATION_MESSAGES
from src.tg_bot.utils import authorized_keyboard

# Обновленные импорты
from src.llm_interview_simulation.llm_interview_simulator import ProfessionalInterviewSimulator
from src.llm_interview_simulation.pdf_generator import ProfessionalInterviewPDFGenerator
from src.models.interview_simulation_models import InterviewSimulation

from src.utils import get_logger
logger = get_logger()

# Создаем экземпляры обновленных сервисов
llm_interview_simulator = ProfessionalInterviewSimulator()
pdf_generator = ProfessionalInterviewPDFGenerator()

def format_simulation_preview(simulation: InterviewSimulation) -> str:
    """Форматирует краткий предварительный просмотр симуляции."""
    result = "🎭 <b>ПРОФЕССИОНАЛЬНАЯ СИМУЛЯЦИЯ ИНТЕРВЬЮ ЗАВЕРШЕНА</b>\n\n"
    
    result += f"🎯 <b>Позиция:</b> {simulation.position_title}\n"
    result += f"👤 <b>Кандидат:</b> {simulation.candidate_name}\n"
    result += f"📊 <b>Уровень:</b> {simulation.candidate_profile.detected_level.value.title()}\n"
    result += f"💼 <b>Роль:</b> {simulation.candidate_profile.detected_role.value.replace('_', ' ').title()}\n"
    result += f"🔄 <b>Проведено раундов:</b> {simulation.total_rounds_completed} из {simulation.interview_config.target_rounds}\n\n"
    
    # Общая рекомендация с эмодзи
    recommendation_emoji = {
        "hire": "✅",
        "conditional_hire": "⚡", 
        "reject": "❌"
    }
    emoji = recommendation_emoji.get(simulation.assessment.overall_recommendation, "❓")
    recommendation_text = {
        "hire": "Рекомендовать к найму",
        "conditional_hire": "Условно рекомендовать", 
        "reject": "Не рекомендовать"
    }
    rec_text = recommendation_text.get(simulation.assessment.overall_recommendation, "Неопределено")
    
    result += f"🎯 <b>Общая рекомендация:</b> {emoji} {rec_text}\n"
    result += f"⭐ <b>Средняя оценка ответов:</b> {simulation.average_response_quality:.1f}/5.0\n\n"
    
    # Топ компетенции
    if simulation.assessment.competency_scores:
        top_competencies = sorted(simulation.assessment.competency_scores, key=lambda x: x.score, reverse=True)[:3]
        result += "<b>🏆 Лучшие компетенции:</b>\n"
        for comp in top_competencies:
            comp_name = _translate_competency_name(comp.area)
            result += f"• {comp_name}: {comp.score}/5\n"
        result += "\n"
    
    # Краткий пример из диалога
    if simulation.dialog_messages:
        result += "<b>📝 Пример из диалога:</b>\n"
        first_hr_msg = next((msg for msg in simulation.dialog_messages if msg.speaker == "HR"), None)
        if first_hr_msg:
            preview_text = first_hr_msg.message[:100] + "..." if len(first_hr_msg.message) > 100 else first_hr_msg.message
            result += f"<i>HR: {preview_text}</i>\n\n"
    
    result += "📄 <b>Полный профессиональный отчет будет отправлен в PDF формате</b>"
    
    return result

def _translate_competency_name(competency) -> str:
    """Переводит название компетенции на русский."""
    from src.models.interview_simulation_models import CompetencyArea
    
    translations = {
        CompetencyArea.TECHNICAL_EXPERTISE: "Техническая экспертиза",
        CompetencyArea.COMMUNICATION: "Коммуникация",
        CompetencyArea.PROBLEM_SOLVING: "Решение проблем",
        CompetencyArea.TEAMWORK: "Командная работа",
        CompetencyArea.LEADERSHIP: "Лидерство",
        CompetencyArea.ADAPTABILITY: "Адаптивность",
        CompetencyArea.LEARNING_ABILITY: "Обучаемость",
        CompetencyArea.MOTIVATION: "Мотивация",
        CompetencyArea.CULTURAL_FIT: "Культурное соответствие"
    }
    return translations.get(competency, competency.value)

async def start_interview_simulation(message: types.Message, state: FSMContext):
    """Запускает процесс профессиональной симуляции интервью."""
    user_id = message.from_user.id
    logger.info(f"Запуск профессиональной симуляции интервью для пользователя {user_id}")
    
    # Получаем данные из состояния пользователя
    user_data = await state.get_data()
    parsed_resume = user_data.get("parsed_resume")
    parsed_vacancy = user_data.get("parsed_vacancy")
    
    if not parsed_resume or not parsed_vacancy:
        logger.error(f"Отсутствуют данные резюме или вакансии для пользователя {user_id}")
        await message.answer(INTERVIEW_SIMULATION_MESSAGES['generation_error'])
        await state.set_state(UserState.AUTHORIZED)
        return
    
    # Сообщаем пользователю о начале симуляции
    await message.answer(INTERVIEW_SIMULATION_MESSAGES["generation_started"], reply_markup=authorized_keyboard)
    await state.set_state(UserState.INTERVIEW_SIMULATION_GENERATION)
    
    try:
        # Уведомляем о прогрессе
        progress_msg = await message.answer("🔄 Анализ профиля кандидата...")
        
        # Создаем callback функцию для обновления прогресса
        async def progress_callback(current_round: int, total_rounds: int):
            await send_simulation_progress_update(progress_msg, current_round, total_rounds)
        
        # Запускаем профессиональную симуляцию интервью с колбеком прогресса
        simulation_result = await llm_interview_simulator.simulate_interview(
            parsed_resume, 
            parsed_vacancy,
            progress_callback=progress_callback
        )
        
        if not simulation_result:
            logger.error(f"Не удалось провести симуляцию для пользователя {user_id}")
            await message.answer(INTERVIEW_SIMULATION_MESSAGES["generation_error"])
            await state.set_state(UserState.AUTHORIZED)
            return
        
        # Финальные этапы
        await progress_msg.edit_text("📊 Проведение оценки компетенций...")
        await progress_msg.edit_text("📄 Создание профессионального PDF отчета...")
        
        # Генерируем PDF с новым генератором
        pdf_buffer = pdf_generator.generate_pdf(simulation_result)
        if not pdf_buffer:
            logger.error(f"Не удалось создать PDF для пользователя {user_id}")
            await message.answer("❌ Ошибка при создании PDF отчета")
            await state.set_state(UserState.AUTHORIZED)
            return
        
        # Сохраняем результат в состоянии пользователя
        await state.update_data(interview_simulation=simulation_result.model_dump())
        
        # Отправляем улучшенный предварительный просмотр
        preview_text = format_simulation_preview(simulation_result)
        await progress_msg.edit_text(preview_text, parse_mode="HTML")
        
        # Отправляем PDF файл с обновленным именем
        filename = pdf_generator.generate_filename(simulation_result)
        
        # Создаем InputFile для отправки
        pdf_file = types.BufferedInputFile(
            file=pdf_buffer.getvalue(),
            filename=filename
        )
        
        # Обновленное описание отчета
        caption_text = f"📄 <b>Профессиональный отчет симуляции интервью</b>\n\n"
        caption_text += f"📊 <b>Результаты оценки:</b>\n"
        caption_text += f"• Уровень кандидата: {simulation_result.candidate_profile.detected_level.value.title()}\n"
        caption_text += f"• Проведено раундов: {simulation_result.total_rounds_completed}\n"
        caption_text += f"• Оценка компетенций: {len(simulation_result.assessment.competency_scores)} областей\n"
        caption_text += f"• Средний балл: {simulation_result.average_response_quality:.1f}/5.0\n\n"
        
        caption_text += f"📋 <b>В отчете содержится:</b>\n"
        caption_text += f"• Полный диалог интервью с типизацией вопросов\n"
        caption_text += f"• Детальная оценка по {len(simulation_result.assessment.competency_scores)} компетенциям\n"
        caption_text += f"• Анализ сильных и слабых сторон\n"
        caption_text += f"• Профессиональные рекомендации HR\n"
        caption_text += f"• Визуализация результатов оценки\n\n"
        caption_text += f"💡 <b>Используйте этот отчет для целевой подготовки к интервью!</b>"
        
        await message.answer_document(
            document=pdf_file,
            caption=caption_text,
            parse_mode="HTML",
            reply_markup=authorized_keyboard
        )
        
        await state.set_state(UserState.AUTHORIZED)
        logger.info(f"Профессиональная симуляция интервью успешно завершена для пользователя {user_id}")
        
    except Exception as e:
        logger.error(f"Ошибка при симуляции интервью: {e}")
        await message.answer(INTERVIEW_SIMULATION_MESSAGES["generation_error"])
        await state.set_state(UserState.AUTHORIZED)

async def send_simulation_progress_update(message: types.Message, round_number: int, total_rounds: int):
    """Отправляет обновление прогресса профессиональной симуляции."""
    progress_text = "🎭 Проводится профессиональная симуляция интервью...\n\n"
    progress_text += f"📊 Прогресс: {round_number}/{total_rounds} раундов\n"
    progress_text += f"{'▓' * round_number}{'░' * (total_rounds - round_number)}\n\n"
    
    # Более детальные статусы раундов
    if round_number == 1:
        progress_text += "👋 Знакомство и оценка коммуникации..."
    elif round_number == 2:
        progress_text += "🔧 Техническая экспертиза и навыки..."
    elif round_number == 3:
        progress_text += "💼 Поведенческие вопросы (STAR-методика)..."
    elif round_number == 4:
        progress_text += "🧩 Решение проблем и мотивация..."
    elif round_number == 5:
        progress_text += "🎯 Культурное соответствие..."
    elif round_number >= 6:
        progress_text += "👑 Лидерские качества и финальные вопросы..."
    
    try:
        await message.edit_text(progress_text)
    except Exception:
        # Если не удалось отредактировать, отправляем новое сообщение
        await message.answer(progress_text)