# domain/dto.py

from typing import List, Optional
from pydantic import BaseModel


class Resume(BaseModel):
    """DTO для резюме"""
    id: str
    fullname: str
    contacts: dict
    skills: List[str]
    work_experience: List[dict]
    education: List[dict]
    summary: Optional[str] = None


class Vacancy(BaseModel):
    """DTO для вакансии"""
    id: str
    title: str
    company: str
    requirements: List[str]
    responsibilities: List[str]
    salary: Optional[str] = None


class GapReport(BaseModel):
    """Результат gap-анализа"""
    missing_skills: List[str]
    weak_experience: List[str]
    recommendations: List[str]


class UserToken(BaseModel):
    """Токены пользователя для HH API"""
    user_id: int
    access_token: str
    refresh_token: str
    expires_at: int