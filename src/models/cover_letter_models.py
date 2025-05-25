# src/models/cover_letter_models.py
from pydantic import BaseModel, Field

class CoverLetter(BaseModel):
    """
    Модель рекомендательного письма.
    """
    subject_line: str = Field(..., description="Тема письма для отклика на вакансию")
    greeting: str = Field(..., description="Приветствие (например, 'Уважаемый HR-менеджер!')")
    opening_paragraph: str = Field(..., description="Вводный абзац с упоминанием вакансии и краткой самопрезентацией")
    body_paragraphs: str = Field(..., description="Основная часть письма с описанием релевантного опыта, навыков и достижений")
    closing_paragraph: str = Field(..., description="Заключительный абзац с призывом к действию")
    signature: str = Field(..., description="Подпись письма")
    
    class Config:
        extra = "forbid"
        title = "CoverLetter"