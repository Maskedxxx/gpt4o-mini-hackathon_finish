# src/models/resume_models.py
from typing import List, Optional
from pydantic import BaseModel, Field

class Level(BaseModel):
    """Модель уровня владения языком"""
    name: str = Field(..., description="Название уровня владения")

    class Config:
        extra = "forbid"

class RelocationType(BaseModel):
    """Модель типа релокации"""
    name: str = Field(..., description="Название типа релокации")

    class Config:
        extra = "forbid"

class Experience(BaseModel):
    """Модель опыта работы"""
    description: str = Field(..., description="Описание опыта работы")
    position: str = Field(..., description="Должность")
    start: Optional[str] = Field(None, description="Дата начала работы")
    end: Optional[str] = Field(None, description="Дата окончания работы")

    class Config:
        extra = "forbid"

class Language(BaseModel):
    """Модель языка и уровня владения им"""
    name: str = Field(..., description="Название языка")
    level: Level = Field(..., description="Уровень владения языком")

    class Config:
        extra = "forbid"

class Relocation(BaseModel):
    """Модель информации о релокации"""
    type: RelocationType = Field(..., description="Тип релокации")

    class Config:
        extra = "forbid"

class Salary(BaseModel):
    """Модель зарплатных ожиданий"""
    amount: int = Field(..., description="Сумма зарплатных ожиданий")

    class Config:
        extra = "forbid"

class ProfessionalRole(BaseModel):
    """Модель профессиональной роли"""
    name: str = Field(..., description="Название профессиональной роли")

    class Config:
        extra = "forbid"

class EducationLevel(BaseModel):
    """Модель уровня образования"""
    name: str = Field(..., description="Название уровня образования (Высшее, Среднее и т.д.)")

    class Config:
        extra = "forbid"

class PrimaryEducation(BaseModel):
    """Модель основного образования (университет, институт)"""
    name: str = Field(..., description="Название учебного заведения")
    organization: Optional[str] = Field(None, description="Факультет или организация")
    result: Optional[str] = Field(None, description="Специальность или квалификация")
    year: Optional[int] = Field(None, description="Год окончания")

    class Config:
        extra = "forbid"

class AdditionalEducation(BaseModel):
    """Модель дополнительного образования (курсы, сертификаты)"""
    name: str = Field(..., description="Название курса или сертификата")
    organization: Optional[str] = Field(None, description="Организация, выдавшая сертификат")
    result: Optional[str] = Field(None, description="Результат или квалификация")
    year: Optional[int] = Field(None, description="Год получения")

    class Config:
        extra = "forbid"

class Education(BaseModel):
    """Модель образования"""
    level: Optional[EducationLevel] = Field(None, description="Уровень образования")
    primary: List[PrimaryEducation] = Field(default_factory=list, description="Основное образование")
    additional: List[AdditionalEducation] = Field(default_factory=list, description="Дополнительное образование")

    class Config:
        extra = "forbid"

class ResumeInfo(BaseModel):
    """
    Модель данных резюме.
    
    Attributes:
        title: Желаемая должность
        skills: Дополнительная информация, описание навыков
        skill_set: Ключевые навыки (список уникальных строк)
        experience: Список опыта работы
        employments: Список предпочитаемых типов занятости
        schedules: Список предпочитаемых графиков работы
        languages: Список языков и уровней владения
        relocation: Информация о релокации
        salary: Зарплатные ожидания
        professional_roles: Список профессиональных ролей
        education: Образование
    """
    title: str = Field(..., description="Желаемая должность")
    skills: str = Field(..., description="Дополнительная информация, описание навыков в свободной подробной форме")
    skill_set: List[str] = Field(..., description="Ключевые навыки (список уникальных строк)")
    experience: List[Experience] = Field(..., description="Список опыта работы")
    employments: List[str] = Field(..., description="Список предпочитаемых типов занятости")
    schedules: List[str] = Field(..., description="Список предпочитаемых графиков работы")
    languages: List[Language] = Field(..., description="Список языков и уровней владения")
    relocation: Optional[Relocation] = Field(None, description="Информация о релокации")
    salary: Optional[Salary] = Field(None, description="Зарплатные ожидания")
    professional_roles: List[ProfessionalRole] = Field(..., description="Список профессиональных ролей")
    education: Optional[Education] = Field(None, description="Образование")

    class Config:
        extra = "forbid"
        title = "ResumeInfo"