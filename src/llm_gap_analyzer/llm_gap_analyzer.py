# src/services/llm_gap_analyzer.py
import logging
from typing import Optional, Dict, Any
from openai import OpenAI
from pydantic import ValidationError
from src.llm_gap_analyzer import settings

from src.models.gap_analysis_models import ResumeGapAnalysis

logger = logging.getLogger("llm_gap_analyzer")


class LLMGapAnalyzer:
    """Сервис для анализа резюме с помощью OpenAI API"""
    
    def __init__(self):
        """Инициализация клиента OpenAI."""
        self.config = settings
        self.client = OpenAI(api_key=self.config.api_key)
        self.model = self.config.model_name
    
    def _create_gap_analysis_prompt(self, parsed_resume: Dict[str, Any], parsed_vacancy: Dict[str, Any]) -> str:
        """
        Создает промпт для gap-анализа.
        
        Args:
            parsed_resume: Словарь с распарсенными данными резюме
            parsed_vacancy: Словарь с распарсенными данными вакансии
        
        Returns:
            str: Текст промпта
        """
        return f"""
        Проведи анализ соответствия резюме требованиям вакансии и предоставь рекомендации по улучшению резюме.
        
        Данные резюме:
        {parsed_resume}
        
        Данные вакансии:
        {parsed_vacancy}
        
        Проанализируй следующие разделы:
        1. Заголовок резюме (title)
        2. Навыки (skills, skill_set)
        3. Опыт работы (experience)
        4. Профессиональные роли (professional_roles)
        
        Для каждого раздела определи, что нужно добавить, изменить или удалить.
        
        Возврати ответ согласно схеме Pydantic ResumeGapAnalysis, соответствующий следующей структуре:
        ```
        {{
            "recommendations": [
                {{
                    "section": "title",
                    "recommendation_type": "update",
                    "details": ["Изменить заголовок на...", "Добавить ключевые слова...", "Сделать акцент на..."]
                }},
                ...
            ]
        }}
        ```
        """
    
    async def gap_analysis(self, parsed_resume: Dict[str, Any], parsed_vacancy: Dict[str, Any]) -> Optional[ResumeGapAnalysis]:
        """
        Выполняет GAP-анализ резюме относительно вакансии.
        
        Args:
            parsed_resume: Словарь с распарсенными данными резюме.
            parsed_vacancy: Словарь с распарсенными данными вакансии.
        
        Returns:
            Объект ResumeGapAnalysis, если удалось распарсить корректный JSON-ответ.
            Иначе None.
        """
        try:
            # 1. Сформировать промпт для GAP-анализа
            prompt_text = self._create_gap_analysis_prompt(parsed_resume, parsed_vacancy)
            
            # 2. Подготовить сообщения для chat-completion
            messages = [
                {
                    "role": "system",
                    "content": (
                        "Ты — эксперт, который анализирует соответствие резюме и вакансии. "
                        "Возвращай только валидный JSON по заданной структуре (ResumeGapAnalysis)."
                    )
                },
                {
                    "role": "user",
                    "content": prompt_text
                }
            ]
            
            # 3. Вызвать OpenAI API
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=messages,
                response_format=ResumeGapAnalysis
            )

            # 4. Извлечь ответ
            raw_response_text = completion.choices[0].message.content
            if not raw_response_text:
                logger.error("Пустой ответ от модели при GAP-анализе.")
                return None
            
            # 5. Попробовать распарсить JSON в модель ResumeGapAnalysis
            gap_result = ResumeGapAnalysis.model_validate_json(raw_response_text)
            logger.info("GAP-анализ успешно выполнен.")
            return gap_result

        except ValidationError as ve:
            logger.error(f"Ошибка валидации GAP-анализа: {ve}")
            return None
        except Exception as e:
            logger.error(f"Ошибка при GAP-анализе: {e}")
            return None