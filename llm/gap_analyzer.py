# llm/gap_analyzer.py

"""LLM агент для gap-анализа"""
import json
from openai import AsyncOpenAI

from domain.dto import Resume, Vacancy, GapReport
from domain.services import IGapAnalyzer
from llm.prompts import GAP_ANALYSIS_PROMPT
from config import llm_settings
from loguru import logger


class GapAnalyzer(IGapAnalyzer):
    """Анализатор разрывов между резюме и вакансией"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=llm_settings.api_key)
        self.model = llm_settings.model
    
    async def analyze(self, resume: Resume, vacancy: Vacancy) -> GapReport:
        """Анализировать разрыв между резюме и вакансией"""
        # Форматируем промпт
        prompt = GAP_ANALYSIS_PROMPT.format(
            resume=resume.model_dump_json(indent=2),
            vacancy=vacancy.model_dump_json(indent=2)
        )
        
        try:
            # Вызываем OpenAI
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты эксперт по анализу резюме и вакансий."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            # Парсим JSON ответ
            content = response.choices[0].message.content
            logger.debug(f"Gap analysis response: {content}")
            
            # Очищаем ответ от markdown если есть
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            gap_data = json.loads(content.strip())
            
            return GapReport(
                missing_skills=gap_data.get('missing_skills', []),
                weak_experience=gap_data.get('weak_experience', []),
                recommendations=gap_data.get('recommendations', [])
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse gap analysis JSON: {e}")
            # Возвращаем пустой отчёт в случае ошибки
            return GapReport(
                missing_skills=[],
                weak_experience=[],
                recommendations=["Не удалось провести анализ"]
            )
        except Exception as e:
            logger.error(f"Gap analysis failed: {e}")
            raise
    
    async def process(self, *args, **kwargs) -> dict:
        """Общий интерфейс обработки"""
        result = await self.analyze(*args, **kwargs)
        return result.model_dump()