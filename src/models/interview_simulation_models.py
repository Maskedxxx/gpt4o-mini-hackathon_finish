# src/models/interview_simulation_models.py
from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class CandidateLevel(str, Enum):
    """Уровень кандидата."""
    JUNIOR = "junior"
    MIDDLE = "middle" 
    SENIOR = "senior"
    LEAD = "lead"
    UNKNOWN = "unknown"

class ITRole(str, Enum):
    """Тип IT-роли."""
    DEVELOPER = "developer"
    QA = "qa"
    DEVOPS = "devops"
    ANALYST = "analyst"
    PROJECT_MANAGER = "project_manager"
    DESIGNER = "designer"
    DATA_SCIENTIST = "data_scientist"
    SYSTEM_ADMIN = "system_admin"
    OTHER = "other"

class QuestionType(str, Enum):
    """Типы вопросов в интервью."""
    INTRODUCTION = "introduction"           # Знакомство и общие вопросы
    TECHNICAL_SKILLS = "technical_skills"   # Проверка технических навыков
    EXPERIENCE_DEEP_DIVE = "experience"     # Глубокое обсуждение опыта
    BEHAVIORAL_STAR = "behavioral"          # Поведенческие вопросы (STAR)
    PROBLEM_SOLVING = "problem_solving"     # Решение проблем и кейсы
    MOTIVATION = "motivation"               # Мотивация и цели
    CULTURE_FIT = "culture_fit"            # Соответствие культуре
    LEADERSHIP = "leadership"               # Лидерские качества
    FINAL = "final"                        # Финальные вопросы

class CompetencyArea(str, Enum):
    """Области компетенций для оценки."""
    TECHNICAL_EXPERTISE = "technical_expertise"
    PROBLEM_SOLVING = "problem_solving"
    COMMUNICATION = "communication"
    TEAMWORK = "teamwork"
    ADAPTABILITY = "adaptability"
    LEADERSHIP = "leadership"
    LEARNING_ABILITY = "learning_ability"
    MOTIVATION = "motivation"
    CULTURAL_FIT = "cultural_fit"

class DialogMessage(BaseModel):
    """Сообщение в диалоге между HR и кандидатом."""
    speaker: Literal["HR", "Candidate"] = Field(..., description="Кто говорит: HR или кандидат")
    message: str = Field(..., description="Текст сообщения")
    round_number: int = Field(..., description="Номер раунда диалога")
    question_type: Optional[QuestionType] = Field(None, description="Тип вопроса (только для HR)")
    response_quality: Optional[int] = Field(None, description="Качество ответа 1-5 (только для Candidate)")
    key_points: List[str] = Field(default_factory=list, description="Ключевые моменты из ответа")
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

class CompetencyScore(BaseModel):
    """Оценка по конкретной компетенции."""
    area: CompetencyArea = Field(..., description="Область компетенции")
    score: int = Field(..., ge=1, le=5, description="Оценка от 1 до 5")
    evidence: List[str] = Field(default_factory=list, description="Доказательства/примеры из ответов")
    improvement_notes: str = Field("", description="Заметки по улучшению")

class InterviewAssessment(BaseModel):
    """Детальная оценка результатов интервью."""
    overall_recommendation: Literal["hire", "conditional_hire", "reject"] = Field(..., description="Общая рекомендация")
    competency_scores: List[CompetencyScore] = Field(..., description="Оценки по компетенциям")
    strengths: List[str] = Field(..., description="Сильные стороны кандидата")
    weaknesses: List[str] = Field(..., description="Слабые стороны кандидата")
    red_flags: List[str] = Field(default_factory=list, description="Красные флаги")
    cultural_fit_score: int = Field(..., ge=1, le=5, description="Соответствие культуре компании")
    
class CandidateProfile(BaseModel):
    """Профиль кандидата, извлеченный из резюме."""
    detected_level: CandidateLevel = Field(..., description="Определенный уровень кандидата")
    detected_role: ITRole = Field(..., description="Определенная IT-роль")
    years_of_experience: Optional[int] = Field(None, description="Лет опыта")
    key_technologies: List[str] = Field(default_factory=list, description="Ключевые технологии")
    education_level: Optional[str] = Field(None, description="Уровень образования")
    previous_companies: List[str] = Field(default_factory=list, description="Предыдущие компании")
    management_experience: bool = Field(False, description="Есть ли опыт управления")

class InterviewConfiguration(BaseModel):
    """Конфигурация интервью."""
    target_rounds: int = Field(default=5, ge=3, le=7, description="Целевое количество раундов")
    focus_areas: List[CompetencyArea] = Field(default_factory=list, description="Приоритетные области оценки")
    include_behavioral: bool = Field(True, description="Включать поведенческие вопросы")
    include_technical: bool = Field(True, description="Включать технические вопросы") 
    difficulty_level: Literal["easy", "medium", "hard"] = Field("medium", description="Уровень сложности вопросов")

class InterviewSimulation(BaseModel):
    """
    Результат симуляции интервью между HR и кандидатом.
    """
    # Базовая информация
    position_title: str = Field(..., description="Название позиции для интервью")
    candidate_name: str = Field(..., description="Имя кандидата")
    company_context: str = Field(..., description="Контекст компании и позиции")
    
    # Профиль и конфигурация
    candidate_profile: CandidateProfile = Field(..., description="Профиль кандидата")
    interview_config: InterviewConfiguration = Field(..., description="Конфигурация интервью")
    
    # Диалог
    dialog_messages: List[DialogMessage] = Field(..., description="Сообщения диалога в хронологическом порядке")
    
    # Результаты оценки
    assessment: InterviewAssessment = Field(..., description="Детальная оценка результатов")
    
    # Текстовые рекомендации (для совместимости)
    hr_assessment: str = Field(..., description="Итоговая текстовая оценка HR")
    candidate_performance_analysis: str = Field(..., description="Анализ выступления кандидата")
    improvement_recommendations: str = Field(..., description="Рекомендации кандидату")
    
    # Метаданные
    simulation_metadata: Dict[str, Any] = Field(default_factory=dict, description="Метаданные симуляции")
    
    @property
    def total_rounds_completed(self) -> int:
        """Общее количество завершенных раундов."""
        if not self.dialog_messages:
            return 0
        return max((msg.round_number for msg in self.dialog_messages), default=0)
    
    @property
    def average_response_quality(self) -> float:
        """Средняя оценка качества ответов кандидата."""
        candidate_scores = [
            msg.response_quality for msg in self.dialog_messages 
            if msg.speaker == "Candidate" and msg.response_quality is not None
        ]
        return sum(candidate_scores) / len(candidate_scores) if candidate_scores else 0.0
    
    @property
    def covered_question_types(self) -> List[QuestionType]:
        """Типы вопросов, которые были заданы."""
        return list(set(
            msg.question_type for msg in self.dialog_messages 
            if msg.speaker == "HR" and msg.question_type is not None
        ))
    
    class Config:
        extra = "forbid"
        title = "InterviewSimulation"
        use_enum_values = True