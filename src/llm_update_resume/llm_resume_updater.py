# src/llm_update_resume/llm_resume_updater.py
import logging
from typing import Optional, Dict, Any
from openai import OpenAI
from pydantic import ValidationError

from src.llm_update_resume.config import settings
from src.models.gap_analysis_models import ResumeTailoringAnalysis
from src.models.resume_update_models import ResumeUpdate
from src.llm_update_resume.formatter import format_resume_for_rewrite, format_gap_analysis_report_for_rewriter

logger = logging.getLogger("llm_resume_updater")

class LLMResumeUpdater:
    """Сервис для обновления резюме с помощью OpenAI API на основе GAP-анализа"""
    
    def __init__(self):
        """Инициализация клиента OpenAI."""
        self.config = settings
        self.client = OpenAI(api_key=self.config.api_key)
        self.model = self.config.model_name
    
    def _create_final_rewrite_prompt(self, parsed_resume: Dict[str, Any], gap_result: ResumeTailoringAnalysis) -> str:
        """
        Создает промпт для финального переписывания резюме.
        
        Args:
            parsed_resume: Словарь с распарсенными данными резюме
            gap_result: Результат GAP-анализа
        
        Returns:
            str: Текст промпта
        """
        # Форматируем данные резюме и результаты gap-анализа для улучшения промпта
        formatted_resume = format_resume_for_rewrite(parsed_resume)
        formatted_gap_analysis = format_gap_analysis_report_for_rewriter(gap_result)
        
        return f"""
        # ЗАДАЧА: УЛУЧШЕНИЕ РЕЗЮМЕ НА ОСНОВЕ GAP-АНАЛИЗА
        
        Твоя задача - переписать резюме соискателя, учитывая рекомендации из GAP-анализа, чтобы повысить его шансы на получение желаемой позиции.
        
        {formatted_resume}
        
        {formatted_gap_analysis}
        
        ## ИНСТРУКЦИИ ПО УЛУЧШЕНИЮ
        
        1. Переработай каждый раздел резюме согласно рекомендациям выше
        2. Сохрани структуру и количество элементов опыта работы - их должно быть столько же, сколько в исходном резюме
        3. Используй профессиональный деловой стиль в описаниях
        4. Сфокусируйся на конкретных достижениях и релевантном опыте
        5. Используй ключевые слова из рекомендаций
        
        ## ФОРМАТ ОТВЕТА
        
        Верни ответ строго в формате JSON, соответствующий структуре Pydantic модели ResumeUpdate:
        
        ```json
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
        
        ВАЖНО: Раздел "experience" должен содержать ровно {len(parsed_resume.get('experience', []))} объектов - столько же, сколько в исходном резюме.
        """
    
    async def update_resume(self, parsed_resume: Dict[str, Any], gap_result: ResumeTailoringAnalysis) -> Optional[ResumeUpdate]:
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
                        "Ты — эксперт HR с глубоким пониманием IT-сферы. "
                        "Твоя задача - улучшить резюме соискателя, учитывая рекомендации из GAP-анализа. "
                        "Создавай профессиональное резюме, подчеркивающее релевантный опыт и навыки. "
                        "ВСЕГДА ОТВЕЧАЙ НА РУССКОМ ЯЗЫКЕ! "
                        "Выполни изменения в резюме точно по указанным рекомендациям, сохраняя структуру исходного резюме."
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