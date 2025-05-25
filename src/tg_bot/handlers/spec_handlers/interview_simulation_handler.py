# src/tg_bot/handlers/spec_handlers/interview_simulation_handler.py
import logging
from aiogram import types
from aiogram.fsm.context import FSMContext

from src.tg_bot.utils import UserState
from src.tg_bot.utils import INTERVIEW_SIMULATION_MESSAGES
from src.tg_bot.utils import authorized_keyboard
from src.llm_interview_simulation import LLMInterviewSimulator
from src.llm_interview_simulation.pdf_generator import InterviewSimulationPDFGenerator
from src.models.interview_simulation_models import InterviewSimulation

logger = logging.getLogger("interview_simulation_handler")

# Создаем экземпляры сервисов
llm_interview_simulator = LLMInterviewSimulator()
pdf_generator = InterviewSimulationPDFGenerator()

def format_simulation_preview(simulation: InterviewSimulation) -> str:
    """Форматирует краткий предварительный просмотр симуляции."""
    result = "🎭 <b>СИМУЛЯЦИЯ ИНТЕРВЬЮ ЗАВЕРШЕНА</b>\n\n"
    
    result += f"🎯 <b>Позиция:</b> {simulation.position_title}\n"
    result += f"👤 <b>Кандидат:</b> {simulation.candidate_name}\n"
    result += f"🔄 <b>Проведено раундов:</b> {simulation.simulation_metadata.get('rounds_completed', 'N/A')}\n\n"
    
    # Краткий пример из диалога
    if simulation.dialog_messages:
        result += "<b>📝 Пример из диалога:</b>\n"
        first_hr_msg = next((msg for msg in simulation.dialog_messages if msg.speaker == "HR"), None)
        if first_hr_msg:
            preview_text = first_hr_msg.message[:100] + "..." if len(first_hr_msg.message) > 100 else first_hr_msg.message
            result += f"<i>HR: {preview_text}</i>\n\n"
    
    # Краткая оценка
    result += "<b>📋 Краткая оценка HR:</b>\n"
    assessment_preview = simulation.hr_assessment[:150] + "..." if len(simulation.hr_assessment) > 150 else simulation.hr_assessment
    result += f"<i>{assessment_preview}</i>\n\n"
    
    result += "📄 <b>Полный отчет симуляции будет отправлен в PDF формате</b>"
    
    return result

async def start_interview_simulation(message: types.Message, state: FSMContext):
    """Запускает процесс симуляции интервью."""
    user_id = message.from_user.id
    logger.info(f"Запуск симуляции интервью для пользователя {user_id}")
    
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
        progress_msg = await message.answer("🔄 Инициализация симуляции...")
        
        # Запускаем симуляцию интервью
        simulation_result = await llm_interview_simulator.simulate_interview(parsed_resume, parsed_vacancy)
        
        if not simulation_result:
            logger.error(f"Не удалось провести симуляцию для пользователя {user_id}")
            await message.answer(INTERVIEW_SIMULATION_MESSAGES["generation_error"])
            await state.set_state(UserState.AUTHORIZED)
            return
        
        # Обновляем статус
        await progress_msg.edit_text("📄 Создание PDF отчета...")
        
        # Генерируем PDF
        pdf_buffer = pdf_generator.generate_pdf(simulation_result)
        if not pdf_buffer:
            logger.error(f"Не удалось создать PDF для пользователя {user_id}")
            await message.answer("❌ Ошибка при создании PDF отчета")
            await state.set_state(UserState.AUTHORIZED)
            return
        
        # Сохраняем результат в состоянии пользователя
        await state.update_data(interview_simulation=simulation_result.model_dump())
        
        # Отправляем предварительный просмотр
        preview_text = format_simulation_preview(simulation_result)
        await progress_msg.edit_text(preview_text, parse_mode="HTML")
        
        # Отправляем PDF файл
        filename = pdf_generator.generate_filename(simulation_result)
        
        # Создаем InputFile для отправки
        pdf_file = types.BufferedInputFile(
            file=pdf_buffer.getvalue(),
            filename=filename
        )
        
        await message.answer_document(
            document=pdf_file,
            caption=f"📄 <b>Полный отчет симуляции интервью</b>\n\n"
                   f"В документе содержится:\n"
                   f"• Полный диалог интервью ({simulation_result.simulation_metadata.get('rounds_completed', 0)} раундов)\n"
                   f"• Оценка HR-менеджера\n"
                   f"• Анализ выступления кандидата\n"
                   f"• Рекомендации по улучшению\n\n"
                   f"💡 Используйте этот отчет для подготовки к реальным интервью!",
            parse_mode="HTML",
            reply_markup=authorized_keyboard
        )
        
        await state.set_state(UserState.AUTHORIZED)
        logger.info(f"Симуляция интервью успешно завершена для пользователя {user_id}")
        
    except Exception as e:
        logger.error(f"Ошибка при симуляции интервью: {e}")
        await message.answer(INTERVIEW_SIMULATION_MESSAGES["generation_error"])
        await state.set_state(UserState.AUTHORIZED)

async def send_simulation_progress_update(message: types.Message, round_number: int, total_rounds: int):
    """Отправляет обновление прогресса симуляции."""
    progress_text = "🎭 Проводится симуляция интервью...\n\n"
    progress_text += f"📊 Прогресс: {round_number}/{total_rounds} раундов\n"
    progress_text += f"{'▓' * round_number}{'░' * (total_rounds - round_number)}\n\n"
    
    if round_number == 1:
        progress_text += "🎯 Знакомство и первые вопросы..."
    elif round_number == 2:
        progress_text += "🔧 Технические вопросы..."
    elif round_number == 3:
        progress_text += "💼 Обсуждение опыта работы..."
    elif round_number == 4:
        progress_text += "🧩 Ситуационные задачи..."
    elif round_number == 5:
        progress_text += "🎯 Финальные вопросы..."
    
    try:
        await message.edit_text(progress_text)
    except Exception:
        # Если не удалось отредактировать, отправляем новое сообщение
        await message.answer(progress_text)