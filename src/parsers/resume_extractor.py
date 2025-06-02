# src/parsers/resume_extractor.py
import re
import logging
from typing import Dict, Any, Optional
from src.models.resume_models import (
    ResumeInfo, Experience, Language, Level, 
    Relocation, RelocationType, Salary, ProfessionalRole
)

from src.utils import get_logger
logger = get_logger()

class ResumeExtractor:
    """Класс для извлечения информации из данных резюме и вакансий"""
    
    def __init__(self):
        self._clean_tag_pattern = re.compile(r"<.*?>")
    
    def _remove_html_tags(self, text: Optional[str]) -> str:
        """Удаляет HTML-теги из текста"""
        if not text:
            return ""
        return re.sub(self._clean_tag_pattern, "", text).strip()
    
    def extract_resume_info(self, data: Dict[str, Any]) -> Optional[ResumeInfo]:
        """
        Извлекает информацию из резюме.
        
        Args:
            data: Словарь с данными резюме
            
        Returns:
            Optional[ResumeInfo]: Объект с данными резюме или None в случае ошибки
        """
        if not isinstance(data, dict):
            logger.error(f"Некорректный формат данных резюме: {type(data)}")
            return None
            
        try:
            # Обработка опыта работы
            experience = []
            for exp in data.get("experience", []):
                if isinstance(exp, dict):
                    experience.append(Experience(
                        description=self._remove_html_tags(exp.get("description", "")),
                        position=exp.get("position", ""),
                        start=exp.get("start"),
                        end=exp.get("end")
                    ))
            
            # Обработка языков
            languages = []
            for lang in data.get("language", []):
                if isinstance(lang, dict):
                    languages.append(Language(
                        name=lang.get("name", ""),
                        level=Level(name=lang.get("level", {}).get("name", ""))
                    ))
            
            # Обработка релокации
            relocation_data = data.get("relocation")
            relocation = None
            if relocation_data and isinstance(relocation_data, dict) and relocation_data.get("type"):
                relocation = Relocation(
                    type=RelocationType(
                        name=relocation_data.get("type", {}).get("name", "")
                    )
                )
            
            # Обработка зарплаты
            salary_data = data.get("salary")
            salary = None
            if salary_data and isinstance(salary_data, dict) and salary_data.get("amount") is not None:
                salary = Salary(amount=salary_data.get("amount"))
            
            # Обработка профессиональных ролей
            professional_roles = []
            for role in data.get("professional_roles", []):
                if isinstance(role, dict):
                    professional_roles.append(ProfessionalRole(
                        name=role.get("name", "")
                    ))
                
            return ResumeInfo(
                title=data.get("title", ""),
                skills=data.get("skills", ""),
                skill_set=data.get("skill_set", []),
                experience=experience,
                employments=[emp.get("name", "") for emp in data.get("employments", [])],
                schedules=[sch.get("name", "") for sch in data.get("schedules", [])],
                languages=languages,
                relocation=relocation,
                salary=salary,
                professional_roles=professional_roles
            )
        except Exception as e:
            logger.error(f"Ошибка при разборе данных резюме: {e}")
            logger.exception("Полный traceback ошибки:")
            return None