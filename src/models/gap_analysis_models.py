# src/models/gap_analysis_models.py
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from enum import Enum

class CriticalityLevel(str, Enum):
    """Уровень критичности рекомендации - точно соответствует промпту"""
    КРИТИЧНО = "CRITICAL"  # Без этого точно откажут  
    ВАЖНО = "IMPORTANT"    # Сильно влияет на решение
    ЖЕЛАТЕЛЬНО = "DESIRED" # Плюс, но не критично

class ComplianceStatus(str, Enum):
    """Статус соответствия требованию - эмодзи из промпта"""
    ПОЛНОЕ_СООТВЕТСТВИЕ = "FULL_MATCH"      # ✅ 
    ЧАСТИЧНОЕ_СООТВЕТСТВИЕ = "PARTIAL_MATCH" # ⚠️
    ОТСУТСТВУЕТ = "MISSING"                  # ❌
    ТРЕБУЕТ_УТОЧНЕНИЯ = "UNCLEAR"            # 🔍

# ИСПРАВЛЕНИЕ 1: Синхронизация терминологии требований
class RequirementType(str, Enum):
    """Тип требования - синхронизировано с промптом"""
    MUST_HAVE = "MUST_HAVE"                    # Без этого работа невозможна
    NICE_TO_HAVE = "NICE_TO_HAVE"              # Желательно, но можно развить  
    ДОПОЛНИТЕЛЬНЫЕ_ПЛЮСЫ = "ADDITIONAL_BONUS"  # Конкурентные преимущества

# ДОБАВЛЕНИЕ 2: Категоризация навыков из промпта
class SkillCategory(str, Enum):
    """Категория навыков для детального анализа"""
    HARD_SKILLS = "HARD_SKILLS"       # Технические навыки
    SOFT_SKILLS = "SOFT_SKILLS"       # Гибкие навыки
    EXPERIENCE = "EXPERIENCE"         # Опыт работы
    EDUCATION = "EDUCATION"           # Образование

class RequirementAnalysis(BaseModel):
    """Анализ одного требования вакансии - улучшенная версия"""
    requirement_text: str = Field(..., description="Текст требования из вакансии")
    
    # ИСПРАВЛЕНИЕ: Используем новый enum
    requirement_type: RequirementType = Field(..., description="Тип требования: MUST-HAVE, NICE-TO-HAVE или ДОПОЛНИТЕЛЬНЫЕ_ПЛЮСЫ")
    
    # ДОБАВЛЕНИЕ: Категория для лучшей связности с промптом
    skill_category: Optional[SkillCategory] = Field(None, description="К какой категории относится требование (Hard Skills, Soft Skills, Experience, Education)")
    
    compliance_status: ComplianceStatus = Field(..., description="Статус соответствия (✅⚠️❌🔍)")
    evidence_in_resume: Optional[str] = Field(None, description="Где в резюме найдено подтверждение (если есть)")
    gap_description: Optional[str] = Field(None, description="Описание разрыва, если соответствие неполное")
    impact_on_decision: str = Field(..., description="Как это влияет на решение о кандидате")

class PrimaryScreeningResult(BaseModel):
    """Результат первичного скрининга (7-15 секунд) - точно из промпта"""
    job_title_match: bool = Field(...,   description = "Соответствие должности в резюме и вакансии. Примеры: true - если в резюме указана должность 'Python Developer', а в вакансии требуется 'Python Developer'; false - если в резюме указана должность 'Frontend Developer', а в вакансии требуется 'Backend Developer'.")
    experience_years_match: bool = Field(..., description="Общий стаж в нужной сфере vs требуемый")
    key_skills_visible: bool = Field(..., description="Наличие критичных навыков, где все ключевые навыки совпадают с навыками в резюме. Пример: true - если критичные навыки 'Python', 'Django' указаны в резюме; false - если критичные навыки 'Python', 'Django', но в резюме указан только 'Python'.")
    location_suitable: bool = Field(..., description="Локация и готовность к работе")
    salary_expectations_match: bool = Field(..., description="Зарплатные ожидания vs бюджет вакансии")
    
    overall_screening_result: Literal["ПРИНЯТЬ", "ВОЗМОЖНО", "ОТКЛОНИТЬ"] = Field(..., description="Общий результат скрининга")
    screening_notes: str = Field(..., description="Комментарии по скринингу, которые лаконично указывают, что не хватает в скрининге")

# УЛУЧШЕНИЕ 3: Более точные описания полей
class DetailedRecommendation(BaseModel):
    """Детальная рекомендация по улучшению - связана с форматом из промпта"""
    section: Literal["заголовок", "навыки", "опыт", "образование", "структура"] = Field(..., description="Раздел резюме для улучшения")
    
    # Явная связь с prompt: КРИТИЧНО попадает в critical_recommendations
    criticality: CriticalityLevel = Field(..., description="Критичность: КРИТИЧНО (попадет в critical_recommendations), ВАЖНО (important_recommendations), ЖЕЛАТЕЛЬНО (optional_recommendations)")
    
    issue_description: str = Field(..., description="Описание проблемы")
    
    # Точное соответствие промпту: "Конкретные действия: что именно добавить/изменить/убрать"
    specific_actions: List[str] = Field(..., min_items=1, description="Конкретные действия: что именно добавить/изменить/убрать")
    
    # Точное соответствие промпту: "Примеры формулировок: как лучше написать"
    example_wording: Optional[str] = Field(None, description="Примеры формулировок: как лучше написать")
    
    # Точное соответствие промпту: "Обоснование: почему это важно для данной вакансии"
    business_rationale: str = Field(..., description="Обоснование: почему это важно для данной вакансии")

class ResumeQualityAssessment(BaseModel):
    """Оценка качества презентации резюме - ЭТАП 4 из промпта"""
    # Точное соответствие: "Структурированность и читабельность"
    structure_clarity: int = Field(..., ge=1, le=10, description="Структурированность и читабельность (1-10)")
    
    # Точное соответствие: "Релевантность описанного опыта"
    content_relevance: int = Field(..., ge=1, le=10, description="Релевантность описанного опыта (1-10)")
    
    # Точное соответствие: "Наличие конкретных достижений vs общие обязанности"
    achievement_focus: int = Field(..., ge=1, le=10, description="Наличие конкретных достижений vs общие обязанности (1-10)")
    
    # Точное соответствие: "Адаптация под вакансию"
    adaptation_quality: int = Field(..., ge=1, le=10, description="Адаптация под вакансию (1-10)")
    
    overall_impression: Literal["СИЛЬНЫЙ", "СРЕДНИЙ", "СЛАБЫЙ"] = Field(..., description="Общее впечатление от резюме")
    quality_notes: str = Field(..., description="Комментарии по качеству презентации")

# УЛУЧШЕНИЕ 4: Более детальные описания итоговых полей
class EnhancedResumeTailoringAnalysis(BaseModel):
    """Расширенный анализ соответствия резюме вакансии - главная модель"""
    
    # ЭТАП 1: Результат первичного скрининга
    primary_screening: PrimaryScreeningResult = Field(..., description="ЭТАП 1: Результаты первичного скрининга (7-15 секунд)")
    
    # ЭТАП 2-3: Детальный анализ требований  
    requirements_analysis: List[RequirementAnalysis] = Field(..., description="ЭТАП 2-3: Анализ каждого требования (MUST-HAVE/NICE-TO-HAVE/БОНУСЫ + статус соответствия)")

    # ЭТАП 4: Оценка качества резюме
    quality_assessment: ResumeQualityAssessment = Field(..., description="ЭТАП 4: Оценка качества презентации резюме")
    
    # Приоритизированные рекомендации - точная связь с criticality
    critical_recommendations: List[DetailedRecommendation] = Field(..., description="Рекомендации уровня КРИТИЧНО (must-fix)")
    important_recommendations: List[DetailedRecommendation] = Field(..., description="Рекомендации уровня ВАЖНО (сильно улучшат)")
    optional_recommendations: List[DetailedRecommendation] = Field(..., description="Рекомендации уровня ЖЕЛАТЕЛЬНО (nice-to-have)")
    
    # Итоговые выводы
    overall_match_percentage: int = Field(..., ge=0, le=100, description="Общий процент соответствия вакансии")
    hiring_recommendation: Literal["СИЛЬНО_ДА", "ДА", "ВОЗМОЖНО", "НЕТ", "СИЛЬНО_НЕТ"] = Field(..., description="Рекомендация по найму")
    key_strengths: List[str] = Field(..., min_items=1, description="Ключевые сильные стороны кандидата")
    major_gaps: List[str] = Field(..., description="Основные пробелы")
    next_steps: str = Field(..., description="Следующие шаги в процессе найма")

    class Config:
        extra = "forbid"
        title = "EnhancedResumeTailoringAnalysis"