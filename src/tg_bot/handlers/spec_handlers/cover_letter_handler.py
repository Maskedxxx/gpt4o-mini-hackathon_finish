import logging
from aiogram import types
from aiogram.fsm.context import FSMContext

from src.tg_bot.utils import UserState
from src.tg_bot.utils import COVER_LETTER_MESSAGES
from src.tg_bot.utils import authorized_keyboard
from src.llm_cover_letter.llm_cover_letter_generator import EnhancedLLMCoverLetterGenerator
from src.models.cover_letter_models import EnhancedCoverLetter

from src.utils import get_logger
logger = get_logger()

# Создаем экземпляр улучшенного генератора
enhanced_cover_letter_generator = EnhancedLLMCoverLetterGenerator()

def format_enhanced_cover_letter_preview(cover_letter: EnhancedCoverLetter) -> str:
    """Форматирует краткий предварительный просмотр письма с оценками."""
    result = "📧 <b>ПЕРСОНАЛИЗИРОВАННОЕ СОПРОВОДИТЕЛЬНОЕ ПИСЬМО</b>\n\n"
    
    # Оценки качества
    result += "📊 <b>Оценка качества:</b>\n"
    result += f"• Персонализация: {'⭐' * (cover_letter.personalization_score // 2)}/5\n"
    result += f"• Профессионализм: {'⭐' * (cover_letter.professional_tone_score // 2)}/5\n"
    result += f"• Релевантность: {'⭐' * (cover_letter.relevance_score // 2)}/5\n\n"
    
    # Информация о компании и роли
    result += f"🏢 <b>Компания:</b> {cover_letter.company_context.company_name}\n"
    result += f"💼 <b>Тип роли:</b> {cover_letter.role_type.value}\n"
    result += f"📏 <b>Размер письма:</b> {cover_letter.estimated_length}\n\n"
    
    return result

def format_skills_match_section(cover_letter: EnhancedCoverLetter) -> str:
    """Форматирует раздел соответствия навыков."""
    result = "🎯 <b>АНАЛИЗ СООТВЕТСТВИЯ</b>\n\n"
    
    skills_match = cover_letter.skills_match
    
    # Совпадающие навыки
    if skills_match.matched_skills:
        result += "✅ <b>Совпадающие навыки:</b>\n"
        for skill in skills_match.matched_skills[:5]:  # Показываем первые 5
            result += f"• {skill}\n"
        if len(skills_match.matched_skills) > 5:
            result += f"• и еще {len(skills_match.matched_skills) - 5} навыков...\n"
        result += "\n"
    
    # Релевантный опыт
    result += f"💼 <b>Ключевой опыт:</b>\n{skills_match.relevant_experience}\n\n"
    
    # Достижение с цифрами
    if skills_match.quantified_achievement:
        result += f"📈 <b>Главное достижение:</b>\n{skills_match.quantified_achievement}\n\n"
    
    # Готовность к развитию
    if skills_match.growth_potential:
        result += f"🌱 <b>Готовность к развитию:</b>\n{skills_match.growth_potential}\n\n"
    
    return result

def format_cover_letter_text(cover_letter: EnhancedCoverLetter) -> str:
    """Форматирует полный текст письма."""
    result = "📝 <b>ТЕКСТ ПИСЬМА</b>\n\n"
    
    result += f"<b>📌 Тема:</b> {cover_letter.subject_line}\n\n"
    result += f"{cover_letter.personalized_greeting}\n\n"
    result += f"{cover_letter.opening_hook}\n\n"
    result += f"{cover_letter.company_interest}\n\n"
    result += f"{cover_letter.relevant_experience}\n\n"
    result += f"{cover_letter.value_demonstration}\n\n"
    
    if cover_letter.growth_mindset:
        result += f"{cover_letter.growth_mindset}\n\n"
    
    result += f"{cover_letter.professional_closing}\n\n"
    result += f"{cover_letter.signature}\n\n"
    
    return result

def format_improvement_tips(cover_letter: EnhancedCoverLetter) -> str:
    """Форматирует рекомендации по улучшению."""
    if not cover_letter.improvement_suggestions:
        return ""
    
    result = "💡 <b>РЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ</b>\n\n"
    
    for i, suggestion in enumerate(cover_letter.improvement_suggestions, 1):
        result += f"{i}. {suggestion}\n"
    
    return result

async def start_cover_letter_generation(message: types.Message, state: FSMContext):
    """Запускает процесс генерации улучшенного сопроводительного письма."""
    user_id = message.from_user.id
    logger.info(f"Запуск генерации улучшенного cover letter для пользователя {user_id}")
    
    # Получаем данные из состояния пользователя
    user_data = await state.get_data()
    parsed_resume = user_data.get("parsed_resume")
    parsed_vacancy = user_data.get("parsed_vacancy")
    
    if not parsed_resume or not parsed_vacancy:
        logger.error(f"Отсутствуют данные резюме или вакансии для пользователя {user_id}")
        await message.answer(COVER_LETTER_MESSAGES['generation_error'])
        await state.set_state(UserState.AUTHORIZED)
        return
    
    # Сообщаем пользователю о начале генерации
    progress_msg = await message.answer(
        "📧 Создаю персонализированное сопроводительное письмо...\n\n"
        "🔍 Анализирую вакансию и компанию\n"
        "🎯 Подбираю релевантные навыки\n"
        "✍️ Формирую уникальный текст\n"
        "📊 Оцениваю качество\n\n"
        "⏱ Это займет 1-2 минуты...",
        reply_markup=authorized_keyboard
    )
    await state.set_state(UserState.COVER_LETTER_GENERATION)
    
    try:
        # Запускаем генерацию улучшенного cover letter
        cover_letter_result = await enhanced_cover_letter_generator.generate_enhanced_cover_letter(
            parsed_resume, parsed_vacancy
        )
        
        if not cover_letter_result:
            logger.error(f"Не удалось сгенерировать enhanced cover letter для пользователя {user_id}")
            await progress_msg.edit_text(COVER_LETTER_MESSAGES["generation_error"])
            await state.set_state(UserState.AUTHORIZED)
            return
        
        # Сохраняем результат в состоянии пользователя
        await state.update_data(enhanced_cover_letter=cover_letter_result.model_dump())
        
        # Отправляем результат по частям
        await send_enhanced_cover_letter_in_parts(message, cover_letter_result, progress_msg)
        
        await state.set_state(UserState.AUTHORIZED)
        logger.info(f"Enhanced cover letter успешно сгенерирован для пользователя {user_id}")
        
    except Exception as e:
        logger.error(f"Ошибка при генерации enhanced cover letter: {e}")
        await progress_msg.edit_text(COVER_LETTER_MESSAGES["generation_error"])
        await state.set_state(UserState.AUTHORIZED)

async def send_enhanced_cover_letter_in_parts(
    message: types.Message, 
    cover_letter: EnhancedCoverLetter,
    progress_msg: types.Message
):
    """Отправляет улучшенное письмо по частям."""
    
    # Удаляем сообщение о прогрессе
    try:
        await progress_msg.delete()
    except:
        pass
    
    # Часть 1: Предварительный просмотр с оценками
    preview = format_enhanced_cover_letter_preview(cover_letter)
    await message.answer(preview, parse_mode="HTML")
    
    # Часть 2: Анализ соответствия
    skills_match = format_skills_match_section(cover_letter)
    await message.answer(skills_match, parse_mode="HTML")
    
    # Часть 3: Текст письма
    letter_text = format_cover_letter_text(cover_letter)
    
    # Если текст слишком длинный, разбиваем на части
    if len(letter_text) > 4000:
        # Находим подходящее место для разбивки
        parts = []
        current_part = ""
        
        for paragraph in letter_text.split('\n\n'):
            if len(current_part + paragraph) < 3500:
                current_part += paragraph + '\n\n'
            else:
                parts.append(current_part.strip())
                current_part = paragraph + '\n\n'
        
        if current_part:
            parts.append(current_part.strip())
        
        for part in parts:
            await message.answer(part, parse_mode="HTML")
    else:
        await message.answer(letter_text, parse_mode="HTML")
    
    # Часть 4: Рекомендации по улучшению (если есть)
    improvements = format_improvement_tips(cover_letter)
    if improvements:
        await message.answer(improvements, reply_markup=authorized_keyboard, parse_mode="HTML")
    else:
        # Если нет рекомендаций, отправляем финальное сообщение с клавиатурой
        await message.answer(
            "✅ <b>Письмо готово к отправке!</b>\n\n"
            "💡 Совет: перед отправкой еще раз проверьте имя HR-менеджера и название компании.",
            reply_markup=authorized_keyboard,
            parse_mode="HTML"
        )