# src/llm_interview_checklist/__init__.py
from src.llm_interview_checklist.config import settings
from src.llm_interview_checklist.llm_interview_checklist_generator import LLMInterviewChecklistGenerator

# Экспорт моделей для внешнего использования
from src.models.interview_checklist_models import (
    InterviewChecklist, 
    ProfessionalInterviewChecklist,
    CandidateLevel,
    VacancyType,
    CompanyFormat,
    Priority
)