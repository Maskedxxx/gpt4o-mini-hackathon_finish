# llm/resume_rewriter.py

"""LLM агент для перезаписи резюме"""
from openai import AsyncOpenAI

from domain.dto import Resume, GapReport
from domain.services import IResumeRewriter
from llm.prompts import RESUME_REWRITE_PROMPT
from config import llm_settings
from loguru import logger


class ResumeRewriter(IResumeRewriter):
    """Переписыватель резюме на основе gap-анализа"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=llm_settings.api_key)
        self.model = llm_settings.model
    
    async def rewrite(self, resume: Resume, gap_report: GapReport) -> str:
        """Переписать резюме на основе gap-анализа"""
        # Форматируем промпт
        prompt = RESUME_REWRITE_PROMPT.format(
            resume=resume.model_dump_json(indent=2),
            gap_report=gap_report.model_dump_json(indent=2)
        )
        
        try:
            # Вызываем OpenAI
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты профессиональный HR-специалист, эксперт по написанию резюме."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Получаем текст нового резюме
            new_resume_text = response.choices[0].message.content
            logger.debug(f"Rewritten resume length: {len(new_resume_text)}")
            
            return new_resume_text
            
        except Exception as e:
            logger.error(f"Resume rewrite failed: {e}")
            raise
    
    async def process(self, *args, **kwargs) -> dict:
        """Общий интерфейс обработки"""
        result = await self.rewrite(*args, **kwargs)
        return {"rewritten_text": result}