# src/models/resume_update_models.py
from typing import List
from pydantic import BaseModel, Field

class ProfessionalRole(BaseModel):
    """Модель профессиональной роли"""
    name: str = Field(..., description="Название профессиональной роли")

    class Config:
        extra = "forbid"

class ExperienceUpdate(BaseModel):
    """Модель опыта работы"""
    description: str = Field(..., description="Описание опыта работы")
    position: str = Field(..., description="Должность")

    class Config:
        extra = "forbid"

class ResumeUpdate(BaseModel):
    """
    Модель данных обновленного резюме.
    
    Attributes:
        title: Желаемая должность
        skills: Дополнительная информация, описание навыков
        skill_set: Ключевые навыки (список уникальных строк)
        experience: Список опыта работы
        professional_roles: Список профессиональных ролей
    """
    title: str = Field(..., description="Желаемая IT должность")
    skills: str = Field(..., description="Дополнительная информация, описание навыков в свободной подробной форме перечисляя все ключевые навыки и скилы")
    skill_set: List[str] = Field(..., description="Ключевые навыки (список уникальных строк)")
    experience: List[ExperienceUpdate] = Field(..., description="Список опыта работы. ВНИМАНИЕ! ВОЗВРАЩАЙТЕ КОЛЛИЧЕСТВО ОБЬЕКТОВ ExperienceUpdate РАВНОЕ КОЛЛИЧЕСТВУ ОБЬЕКТОВ Experience В ПЕРЕДАННОМ РЕЗЮМЕ")
    professional_roles: List[ProfessionalRole] = Field(..., description="Список профессиональных ролей")

    class Config:
        extra = "forbid"
        title = "ResumeUpdate"