# src/models/gap_analysis_models.py
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from enum import Enum

class CriticalityLevel(str, Enum):
    """Уровень критичности рекомендации"""
    КРИТИЧНО = "CRITICAL"  # Без этого точно откажут
    ВАЖНО = "IMPORTANT"    # Сильно влияет на решение
    ЖЕЛАТЕЛЬНО = "DESIRED" # Плюс, но не критично

class ComplianceStatus(str, Enum):
    """Статус соответствия требованию"""
    ПОЛНОЕ_СООТВЕТСТВИЕ = "FULL_MATCH"
    ЧАСТИЧНОЕ_СООТВЕТСТВИЕ = "PARTIAL_MATCH"
    ОТСУТСТВУЕТ = "MISSING"
    ТРЕБУЕТ_УТОЧНЕНИЯ = "UNCLEAR"

class RequirementAnalysis(BaseModel):
    """Анализ одного требования вакансии"""
    requirement_text: str = Field(..., description="Текст требования из вакансии")
    requirement_type: Literal["ОБЯЗАТЕЛЬНО", "ЖЕЛАТЕЛЬНО", "БОНУС"] = Field(...,  description="Тип требования: обязательное, желательное или бонус")
    compliance_status: ComplianceStatus = Field(..., description="Статус соответствия")
    evidence_in_resume: Optional[str] = Field(None, description="Где в резюме найдено подтверждение (если есть)")
    gap_description: Optional[str] = Field(None, description="Описание разрыва, если соответствие неполное")
    impact_on_decision: str = Field(..., description="Как это влияет на решение о кандидате")

class PrimaryScreeningResult(BaseModel):
    """Результат первичного скрининга (7-15 секунд)"""
    job_title_match: bool = Field(..., description="Соответствует ли должность")
    experience_years_match: bool = Field(..., description="Достаточно ли стажа")
    key_skills_visible: bool = Field(..., description="Видны ли ключевые навыки")
    location_suitable: bool = Field(..., description="Подходит ли локация")
    salary_expectations_match: bool = Field(..., description="Совпадают ли зарплатные ожидания")
    overall_screening_result: Literal["ПРИНЯТЬ", "ВОЗМОЖНО", "ОТКЛОНИТЬ"] = Field(..., description="Общий результат скрининга")
    screening_notes: str = Field(..., description="Комментарии по скринингу")

class DetailedRecommendation(BaseModel):
    """Детальная рекомендация по улучшению"""
    section: Literal["загаловок", "навыки", "опыт", "образование", "структура"] = Field(..., description="Раздел резюме для улучшения")
    criticality: CriticalityLevel = Field(..., description="Критичность рекомендации")
    issue_description: str = Field(..., description="Описание проблемы")
    specific_actions: List[str] = Field(..., min_items=1, description="Конкретные действия для исправления")
    example_wording: Optional[str] = Field(None, description="Пример формулировки, если применимо")
    business_rationale: str = Field(..., description="Почему это важно для данной вакансии")

class ResumeQualityAssessment(BaseModel):
    """Оценка качества презентации резюме"""
    structure_clarity: int = Field(..., ge=1, le=10, description="Структурированность (1-10)")
    content_relevance: int = Field(..., ge=1, le=10, description="Релевантность содержания (1-10)")
    achievement_focus: int = Field(..., ge=1, le=10, description="Фокус на достижения vs обязанности (1-10)")
    adaptation_quality: int = Field(..., ge=1, le=10, description="Адаптация под вакансию (1-10)")
    overall_impression: Literal["СИЛЬНЫЙ", "СРЕДНИЙ", "СЛАБЫЙ"] = Field(..., description="Общее впечатление от резюме")
    quality_notes: str = Field(..., description="Комментарии по качеству")

class EnhancedResumeTailoringAnalysis(BaseModel):
    """Расширенный анализ соответствия резюме вакансии"""
    
    # Результат первичного скрининга
    primary_screening: PrimaryScreeningResult = Field(..., description="Результаты первичного скрининга")
    
    # Детальный анализ требований
    requirements_analysis: List[RequirementAnalysis] = Field(..., description="Анализ каждого требования вакансии")

    # Оценка качества резюме
    quality_assessment: ResumeQualityAssessment = Field(..., description="Оценка качества презентации")
    
    # Приоритизированные рекомендации
    critical_recommendations: List[DetailedRecommendation] = Field(..., description="Критичные рекомендации (must-fix)")
    important_recommendations: List[DetailedRecommendation] = Field(..., description="Важные рекомендации (сильно улучшат)")
    optional_recommendations: List[DetailedRecommendation] = Field(..., description="Желательные улучшения")
    
    # Итоговые выводы
    overall_match_percentage: int = Field(..., ge=0, le=100, description="Общий процент соответствия вакансии")
    hiring_recommendation: Literal["СИЛЬНО_ДА", "ДА", "ВОЗМОЖНО", "НЕТ", "СИЛЬНО_НЕТ"] = Field(..., description="Рекомендация по найму")
    key_strengths: List[str] = Field(..., min_items=1, description="Ключевые сильные стороны кандидата")
    major_gaps: List[str] = Field(...,  description="Основные пробелы")
    next_steps: str = Field(..., description="Следующие шаги в процессе найма")

    class Config:
        extra = "forbid"
        title = "EnhancedResumeTailoringAnalysis"