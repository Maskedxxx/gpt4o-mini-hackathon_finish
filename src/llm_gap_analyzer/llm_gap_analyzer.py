# src/llm_gap_analyzer/llm_gap_analyzer.py
import logging
from typing import Optional, Dict, Any
from openai import OpenAI
from pydantic import ValidationError
from src.llm_gap_analyzer import settings

from src.models.gap_analysis_models import ResumeTailoringAnalysis
from src.llm_gap_analyzer.formatter import format_resume_data, format_vacancy_data

from src.utils import get_logger
logger = get_logger()


class LLMGapAnalyzer:
    """Сервис для анализа резюме с помощью OpenAI API"""
    
    def __init__(self):
        """Инициализация клиента OpenAI."""
        self.config = settings
        self.client = OpenAI(api_key=self.config.api_key)
        self.model = self.config.model_name
    
    def _create_gap_analysis_prompt(self, parsed_resume: Dict[str, Any], parsed_vacancy: Dict[str, Any]) -> str:
        """
        Создает промпт для gap-анализа с форматированными данными.
        
        Args:
            parsed_resume: Словарь с распарсенными данными резюме
            parsed_vacancy: Словарь с распарсенными данными вакансии
        
        Returns:
            str: Текст промпта
        """
        # Форматируем данные резюме и вакансии для лучшего понимания LLM
        formatted_resume = format_resume_data(parsed_resume)
        formatted_vacancy = format_vacancy_data(parsed_vacancy)
        
        # Создаем структурированный промпт
        return f"""
        # Задача: Анализ соответствия резюме требованиям вакансии
        
        Твоя задача - провести детальный анализ соответствия резюме соискателя требованиям вакансии и предоставить конкретные рекомендации по улучшению резюме для повышения шансов на получение данной позиции.
        
        ## Исходные данные
        
        {formatted_resume}
        
        {formatted_vacancy}
        
        ## Инструкции по анализу
        
        Проанализируй следующие разделы:
        
        1. **Заголовок резюме (title)** - соответствует ли заголовок названию вакансии и ключевым требованиям
        2. **Навыки (skills, skill_set)** - присутствуют ли все требуемые навыки из вакансии, какие навыки стоит добавить или выделить
        3. **Опыт работы (experience)** - соответствует ли опыт работы требуемому, насколько хорошо описаны релевантные проекты и достижения
        4. **Профессиональные роли (professional_roles)** - соответствуют ли указанные профессиональные роли требуемой позиции
        
        Для каждого раздела определи, что необходимо добавить, изменить или удалить для улучшения соответствия вакансии.
        
        ## Требования к формату ответа
        
        Верни ответ строго в формате JSON, соответствующий следующей структуре Pydantic модели ResumeTailoringAnalysis:
        
        
        
        ВАЖНО: Для каждого раздела (title, skills, skill_set, experience, professional_roles) должна быть как минимум одна рекомендация. Каждая рекомендация должна содержать не менее 3 конкретных пунктов в списке details. Рекомендации должны быть детальными и практичными.
        """
    
    async def gap_analysis(self, parsed_resume: Dict[str, Any], parsed_vacancy: Dict[str, Any]) -> Optional[ResumeTailoringAnalysis]:
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
            # 1. Сформировать промпт для GAP-анализа с форматированными данными
            prompt_text = self._create_gap_analysis_prompt(parsed_resume, parsed_vacancy)
            
            # 2. Подготовить сообщения для chat-completion
            messages = [
                {
                    "role": "system",
                    "content": (
                        "Ты — эксперт по рекрутингу и HR с глубоким пониманием IT-индустрии. "
                        "Твоя специализация — анализ соответствия резюме требованиям вакансий и предоставление "
                        "конкретных рекомендаций по улучшению. Всегда отвечай строго в формате JSON согласно "
                        "указанной структуре ResumeGapAnalysis. Рекомендации должны быть конкретными, "
                        "практичными и детальными, чтобы соискатель мог сразу применить их для улучшения резюме."
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
                response_format=ResumeTailoringAnalysis
            )

            # 4. Извлечь ответ
            raw_response_text = completion.choices[0].message.content
            if not raw_response_text:
                logger.error("Пустой ответ от модели при GAP-анализе.")
                return None
            
            # 5. Попробовать распарсить JSON в модель ResumeGapAnalysis
            gap_result = ResumeTailoringAnalysis.model_validate_json(raw_response_text)
            logger.info("GAP-анализ успешно выполнен.")
            return gap_result

        except ValidationError as ve:
            logger.error(f"Ошибка валидации GAP-анализа: {ve}")
            return None
        except Exception as e:
            logger.error(f"Ошибка при GAP-анализе: {e}")
            return None