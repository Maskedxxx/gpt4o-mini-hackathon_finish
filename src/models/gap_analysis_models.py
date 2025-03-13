# src/models/gap_analysis_models.py
from pydantic import BaseModel, Field
from typing import List

class Recommendation(BaseModel):
    """Модель рекомендации по улучшению резюме"""
    section: str = Field(..., description="Name of the section to which the recommendation applies (enum: 'title', 'skills', 'skill_set', 'experience', 'professional_roles')")
    recommendation_type: str = Field(..., description="Type of recommendation (enum: 'add', 'update', 'remove')")
    details: List[str] = Field(..., description="Detailed and precise description of step-by-step necessary changes (updates) in the summary, according to the GAP-analysis instructions. PS: minimum 3 item")
    
    class Config:
        extra = "forbid"

class ResumeGapAnalysis(BaseModel):
    """Модель результатов gap-анализа резюме"""
    recommendations: List[Recommendation] = Field(..., description="Cписок рекомендаций по улучшению резюме (Колличевство обьектов если section --> 'Experience' равно их общему количевству представленных в резюме.)")
    
    class Config:
        extra = "forbid"