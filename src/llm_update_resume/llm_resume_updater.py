# src/llm_update_resume/llm_resume_updater.py
import logging
from typing import Optional, Dict, Any
from openai import OpenAI
from pydantic import ValidationError

from src.llm_update_resume.config import settings
from src.models.gap_analysis_models import ResumeGapAnalysis
from src.models.resume_update_models import ResumeUpdate

logger = logging.getLogger("llm_resume_updater")

class LLMResumeUpdater:
    """Сервис для обновления резюме с помощью OpenAI API на основе GAP-анализа"""
    
    def __init__(self):
        """Инициализация клиента OpenAI."""
        self.config = settings
        self.client = OpenAI(api_key=self.config.api_key)
        self.model = self.config.model_name
    
    def _create_final_rewrite_prompt(self, parsed_resume: Dict[str, Any], gap_result: ResumeGapAnalysis) -> str:
        """
        Создает промпт для финального переписывания резюме.
        
        Args:
            parsed_resume: Словарь с распарсенными данными резюме
            gap_result: Результат GAP-анализа
        
        Returns:
            str: Текст промпта
        """
        return f"""
        Перепиши резюме, учитывая результаты GAP-анализа.
        
        Данные текущего резюме:
        {parsed_resume}
        
        Результаты GAP-анализа:
        {gap_result.model_dump()}
        
        Выполни следующие задачи:
        1. Измени заголовок резюме (title) в соответствии с рекомендациями
        2. Улучши описание навыков (skills) и список ключевых навыков (skill_set)
        3. Перепиши опыт работы (experience) согласно рекомендациям
        4. Обнови список профессиональных ролей (professional_roles) при необходимости
        
        Пожалуйста, используй профессиональный деловой стиль в описаниях.
        Перепиши ТОЛЬКО разделы, указанные в GAP-анализе, без изменения структуры резюме.
        
        Возврати ответ в формате JSON, соответствующий следующей структуре:
        ```
        {{
            "title": "Обновленная должность",
            "skills": "Обновленное описание навыков...",
            "skill_set": ["Навык 1", "Навык 2", ...],
            "experience": [
                {{
                    "position": "Должность 1",
                    "description": "Обновленное описание опыта работы..."
                }},
                ...
            ],
            "professional_roles": [
                {{
                    "name": "Название профессиональной роли"
                }},
                ...
            ]
        }}
        ```
        ВАЖНО: В разделе "experience" должно быть РОВНО столько же объектов, сколько их в исходном резюме!
        """
    
    async def update_resume(self, parsed_resume: Dict[str, Any], gap_result: ResumeGapAnalysis) -> Optional[ResumeUpdate]:
        """
        Выполняет финальный рерайт резюме, используя результаты GAP-анализа.
        
        Args:
            parsed_resume: Исходные данные резюме (dict).
            gap_result: Результат GAP-анализа (ResumeGapAnalysis).
        
        Returns:
            Объект ResumeUpdate, если всё OK, иначе None.
        """
        try:
            # 1. Формируем промпт с учётом gap_result
            prompt_text = self._create_final_rewrite_prompt(parsed_resume, gap_result)

            # 2. Подготавливаем сообщения для chat-completion
            messages = [
                {
                    "role": "system",
                    "content": (
                        "Ты — эксперт HR. Учитывай GAP-анализ и требования вакансии для переписывания резюме. "
                        "Выполни изменение разделов резюме, указанных в gap-анализе. "
                        "ЦЕЛЬ результата: переписанные секции резюме выполненные по рекомендациям из gap-анализа. "
                        "ALWAYS ANSWER IN RUSSIAN, IT'S IMPORTANT! "
                        "ALWAYS CONSIDER CHANGES IN ALL OBJECTS <experience>"
                    )
                },
                {
                    "role": "user",
                    "content": prompt_text
                }
            ]

            # 3. Запрашиваем у OpenAI финальный рерайт
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=messages,
                response_format=ResumeUpdate  # парсим сразу в модель ResumeUpdate
            )

            # 4. Извлекаем текст ответа
            raw_response_text = completion.choices[0].message.content
            if not raw_response_text:
                logger.error("Пустой ответ при финальном рерайте.")
                return None

            # 5. Парсим JSON в модель ResumeUpdate
            final_resume = ResumeUpdate.model_validate_json(raw_response_text)
            logger.info("Финальный рерайт выполнен успешно.")
            return final_resume

        except ValidationError as ve:
            logger.error(f"Ошибка валидации JSON финального рерайта: {ve}")
            return None
        except Exception as e:
            logger.error(f"Ошибка при обращении к OpenAI API (финальный рерайт): {e}")
            return None