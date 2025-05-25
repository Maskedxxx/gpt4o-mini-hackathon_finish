# src/llm_cover_letter/llm_cover_letter_generator.py
import logging
from typing import Optional, Dict, Any
from openai import OpenAI
from pydantic import ValidationError

from src.llm_cover_letter.config import settings
from src.models.cover_letter_models import CoverLetter
from src.llm_cover_letter.formatter import format_resume_for_cover_letter, format_vacancy_for_cover_letter

logger = logging.getLogger("llm_cover_letter_generator")

class LLMCoverLetterGenerator:
    """Сервис для создания рекомендательного письма с помощью OpenAI API"""
    
    def __init__(self):
        """Инициализация клиента OpenAI."""
        self.config = settings
        self.client = OpenAI(api_key=self.config.api_key)
        self.model = self.config.model_name
    
    def _create_cover_letter_prompt(self, parsed_resume: Dict[str, Any], parsed_vacancy: Dict[str, Any]) -> str:
        """
        Создает промпт для генерации рекомендательного письма.
        
        Args:
            parsed_resume: Словарь с распарсенными данными резюме
            parsed_vacancy: Словарь с распарсенными данными вакансии
        
        Returns:
            str: Текст промпта
        """
        formatted_resume = format_resume_for_cover_letter(parsed_resume)
        formatted_vacancy = format_vacancy_for_cover_letter(parsed_vacancy)
        
        return f"""
        # Задача: Создание персонализированного рекомендательного письма
        
        Твоя задача - написать профессиональное, убедительное и персонализированное рекомендательное письмо (cover letter) для соискателя, который хочет откликнуться на конкретную вакансию.
        
        ## Исходные данные
        <Данные резюме>
        {formatted_resume}
        </Данные резюме>
        ============
        <Данные вакансии>
        {formatted_vacancy}
        </Данные вакансии>
        ## Требования к письму
        
        1. **Персонализация**: Письмо должно быть специально написано под эту вакансию и компанию
        2. **Профессиональный тон**: Используй деловой, но дружелюбный стиль общения
        3. **Конкретность**: Упоминай конкретные навыки, проекты и достижения из резюме, релевантные для вакансии
        4. **Структурированность**: Четкая структура с логичным переходом между абзацами
        5. **Призыв к действию**: Четкое приглашение к дальнейшему общению
        6. **Краткость**: Письмо должно быть информативным, но не слишком длинным
        
        ## Инструкции по содержанию
        
        - **Тема письма**: Профессиональная и запоминающаяся
        - **Приветствие**: Вежливое обращение к HR-менеджеру или руководителю
        - **Вводный абзац**: Упомяни вакансию, где ты ее увидел и краткую самопрезентацию
        - **Основная часть**: Расскажи о релевантном опыте, навыках и достижениях, которые подходят для этой роли
        - **Заключение**: Выражение заинтересованности в собеседовании и контактная информация
        - **Подпись**: Профессиональная подпись
        
        ## Формат ответа
        
        Верни ответ строго в формате JSON, соответствующий структуре Pydantic модели CoverLetter.
        
        ВАЖНО: 
        - Пиши на русском языке
        - Используй профессиональную лексику IT-сферы
        - Подчеркни именно те навыки и опыт, которые важны для данной вакансии
        - Сделай письмо живым и убедительным, но не преувеличивай
        """
    
    async def generate_cover_letter(self, parsed_resume: Dict[str, Any], parsed_vacancy: Dict[str, Any]) -> Optional[CoverLetter]:
        """
        Генерирует рекомендательное письмо на основе резюме и вакансии.
        
        Args:
            parsed_resume: Словарь с распарсенными данными резюме
            parsed_vacancy: Словарь с распарсенными данными вакансии
        
        Returns:
            CoverLetter: Объект с рекомендательным письмом или None в случае ошибки
        """
        try:
            # 1. Формируем промпт
            prompt_text = self._create_cover_letter_prompt(parsed_resume, parsed_vacancy)
            
            # 2. Подготавливаем сообщения для chat-completion
            messages = [
                {
                    "role": "system",
                    "content": (
                        "Ты — эксперт по написанию рекомендательных писем с глубоким пониманием IT-индустрии. "
                        "Твоя специализация — создание персонализированных, убедительных cover letter, которые "
                        "помогают соискателям выделиться среди других кандидатов. Всегда пишешь на русском языке "
                        "и используешь профессиональный, но приятный тон. Ответ всегда в формате JSON согласно "
                        "указанной структуре CoverLetter."
                    )
                },
                {
                    "role": "user",
                    "content": prompt_text
                }
            ]
            
            # 3. Вызов OpenAI API
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=messages,
                response_format=CoverLetter
            )
            
            # 4. Извлекаем ответ
            raw_response_text = completion.choices[0].message.content
            if not raw_response_text:
                logger.error("Пустой ответ от модели при генерации cover letter.")
                return None
            
            # 5. Парсим JSON в модель CoverLetter
            cover_letter = CoverLetter.model_validate_json(raw_response_text)
            logger.info("Рекомендательное письмо успешно сгенерировано.")
            return cover_letter
            
        except ValidationError as ve:
            logger.error(f"Ошибка валидации рекомендательного письма: {ve}")
            return None
        except Exception as e:
            logger.error(f"Ошибка при генерации рекомендательного письма: {e}")
            return None