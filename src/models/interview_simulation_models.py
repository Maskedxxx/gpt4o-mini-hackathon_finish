# src/models/interview_simulation_models.py
from typing import List, Literal
from pydantic import BaseModel, Field
from datetime import datetime

class DialogMessage(BaseModel):
    """Сообщение в диалоге между HR и кандидатом."""
    speaker: Literal["HR", "Candidate"] = Field(..., description="Кто говорит: HR или кандидат")
    message: str = Field(..., description="Текст сообщения")
    round_number: int = Field(..., description="Номер раунда диалога (1-5)")
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"), description="Время сообщения")

class InterviewSimulation(BaseModel):
    """
    Результат симуляции интервью между HR и кандидатом.
    """
    position_title: str = Field(..., description="Название позиции для интервью")
    candidate_name: str = Field(..., description="Имя кандидата (из резюме или 'Кандидат')")
    company_context: str = Field(..., description="Контекст компании и позиции для интервью")
    
    dialog_messages: List[DialogMessage] = Field(..., description="Список сообщений диалога в хронологическом порядке")
    
    hr_assessment: str = Field(..., description="Итоговая оценка HR по результатам интервью")
    candidate_performance_analysis: str = Field(..., description="Анализ выступления кандидата: сильные и слабые стороны")
    improvement_recommendations: str = Field(..., description="Рекомендации кандидату для улучшения")
    
    simulation_metadata: dict = Field(default_factory=dict, description="Метаданные симуляции (настройки, время создания и т.д.)")
    
    class Config:
        extra = "forbid"
        title = "InterviewSimulation"