# src/tg_bot/handlers/spec_handlers/cover_letter_handler.py
import logging
from aiogram import types
from aiogram.fsm.context import FSMContext

from src.tg_bot.utils import UserState
from src.tg_bot.utils import COVER_LETTER_MESSAGES
from src.tg_bot.utils import authorized_keyboard
from src.llm_cover_letter import LLMCoverLetterGenerator
from src.models.cover_letter_models import CoverLetter

from src.utils import get_logger
logger = get_logger()

# Создаем экземпляр генератора
llm_cover_letter_generator = LLMCoverLetterGenerator()

def format_cover_letter_result(cover_letter: CoverLetter) -> str:
    """Форматирует рекомендательное письмо для отображения пользователю."""
    result = "📧 <b>ВАШЕ РЕКОМЕНДАТЕЛЬНОЕ ПИСЬМО</b>\n\n"
    
    result += f"<b>📌 Тема письма:</b>\n{cover_letter.subject_line}\n\n"
    result += f"<b>👋 Приветствие:</b>\n{cover_letter.greeting}\n\n"
    result += f"<b>📝 Вводная часть:</b>\n{cover_letter.opening_paragraph}\n\n"
    result += f"<b>💼 Основная часть:</b>\n{cover_letter.body_paragraphs}\n\n"
    result += f"<b>🎯 Заключение:</b>\n{cover_letter.closing_paragraph}\n\n"
    result += f"<b>✍️ Подпись:</b>\n{cover_letter.signature}\n\n"
    result += "💡 <b>Это письмо готово к отправке работодателю!</b>"
    
    return result

async def start_cover_letter_generation(message: types.Message, state: FSMContext):
    """Запускает процесс генерации рекомендательного письма."""
    user_id = message.from_user.id
    logger.info(f"Запуск генерации cover letter для пользователя {user_id}")
    
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
    await message.answer(COVER_LETTER_MESSAGES["generation_started"], reply_markup=authorized_keyboard)
    await state.set_state(UserState.COVER_LETTER_GENERATION)
    
    try:
        # Запускаем генерацию cover letter
        cover_letter_result = await llm_cover_letter_generator.generate_cover_letter(parsed_resume, parsed_vacancy)
        
        if not cover_letter_result:
            logger.error(f"Не удалось сгенерировать cover letter для пользователя {user_id}")
            await message.answer(COVER_LETTER_MESSAGES["generation_error"])
            await state.set_state(UserState.AUTHORIZED)
            return
        
        # Сохраняем результат в состоянии пользователя
        await state.update_data(cover_letter=cover_letter_result.model_dump())
        
        # Форматируем и отправляем результат пользователю
        formatted_result = format_cover_letter_result(cover_letter_result)
        
        # Отправляем результат (разбиваем на части если сообщение слишком длинное)
        max_length = 4000  # Telegram лимит ~4096 символов
        if len(formatted_result) <= max_length:
            await message.answer(formatted_result, reply_markup=authorized_keyboard, parse_mode="HTML")
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
                    await message.answer(part, reply_markup=authorized_keyboard, parse_mode="HTML")
                else:
                    await message.answer(part, parse_mode="HTML")
        
        await state.set_state(UserState.AUTHORIZED)
        logger.info(f"Cover letter успешно сгенерирован для пользователя {user_id}")
        
    except Exception as e:
        logger.error(f"Ошибка при генерации cover letter: {e}")
        await message.answer(COVER_LETTER_MESSAGES["generation_error"])
        await state.set_state(UserState.AUTHORIZED)