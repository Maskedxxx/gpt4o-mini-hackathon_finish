# src/models/interview_checklist_models.py
from typing import List, Optional
from pydantic import BaseModel, Field

class StudyResource(BaseModel):
    """Ресурс для изучения."""
    title: str = Field(..., description="Название ресурса или источника")
    url: Optional[str] = Field(None, description="Ссылка на ресурс (если есть)")
    description: str = Field(..., description="Описание того, что можно изучить из этого ресурса")
    estimated_time: str = Field(..., description="Примерное время изучения (например, '2-3 часа', '1 неделя')")

class TechnicalSkill(BaseModel):
    """Технический навык для изучения."""
    skill_name: str = Field(..., description="Название технического навыка")
    current_level_assessment: str = Field(..., description="Оценка текущего уровня кандидата по этому навыку")
    required_level: str = Field(..., description="Требуемый уровень для вакансии")
    study_plan: str = Field(..., description="Детальный план изучения этого навыка")
    resources: List[StudyResource] = Field(..., description="Список ресурсов для изучения")
    priority: str = Field(..., description="Приоритет изучения: 'Высокий', 'Средний', 'Низкий'")

class PracticalTask(BaseModel):
    """Практическая задача для подготовки."""
    task_title: str = Field(..., description="Название типа задач")
    description: str = Field(..., description="Описание задач этого типа")
    examples: List[str] = Field(..., description="Конкретные примеры задач для тренировки")
    practice_resources: List[StudyResource] = Field(..., description="Ресурсы для практики")
    difficulty_level: str = Field(..., description="Уровень сложности: 'Начальный', 'Средний', 'Продвинутый'")

class TheoryTopic(BaseModel):
    """Теоретическая тема для изучения."""
    topic_name: str = Field(..., description="Название теоретической темы")
    importance: str = Field(..., description="Важность темы для вакансии")
    key_concepts: List[str] = Field(..., description="Ключевые концепции для изучения")
    study_materials: List[StudyResource] = Field(..., description="Материалы для изучения теории")
    estimated_depth: str = Field(..., description="Необходимая глубина изучения")

class BehavioralQuestion(BaseModel):
    """Поведенческий вопрос и подготовка к нему."""
    question_category: str = Field(..., description="Категория вопроса (например, 'Работа в команде', 'Решение конфликтов')")
    example_questions: List[str] = Field(..., description="Примеры вопросов этой категории")
    preparation_tips: str = Field(..., description="Советы по подготовке ответов")
    star_method_examples: Optional[str] = Field(None, description="Примеры применения STAR метода для ответов")

class InterviewChecklist(BaseModel):
    """
    Персонализированный чек-лист для подготовки к интервью.
    """
    position_title: str = Field(..., description="Название позиции, на которую готовится кандидат")
    preparation_overview: str = Field(..., description="Общий обзор подготовки и ключевые фокусные области")
    estimated_preparation_time: str = Field(..., description="Общее рекомендуемое время подготовки")
    
    technical_skills: List[TechnicalSkill] = Field(..., description="Технические навыки для изучения/повторения")
    theory_topics: List[TheoryTopic] = Field(..., description="Теоретические темы для изучения")
    practical_tasks: List[PracticalTask] = Field(..., description="Практические задачи для тренировки")
    behavioral_questions: List[BehavioralQuestion] = Field(..., description="Поведенческие вопросы и подготовка к ним")
    
    company_research_tips: str = Field(..., description="Советы по изучению компании и подготовке вопросов")
    final_recommendations: str = Field(..., description="Финальные рекомендации и план действий")
    
    class Config:
        extra = "forbid"
        title = "InterviewChecklist"