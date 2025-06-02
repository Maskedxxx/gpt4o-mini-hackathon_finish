# src/parsers/vacancy_extractor.py
import re
import logging
from typing import Dict, Any, Optional
from src.models.vacancy_models import (
    VacancyInfo, EmploymentForm, ExperienceVac, 
    Schedule, Employment
)

from src.utils import get_logger
logger = get_logger()

class VacancyExtractor:
    """Класс для извлечения информации из данных резюме и вакансий"""
    
    def __init__(self):
        self._clean_tag_pattern = re.compile(r"<.*?>")
    
    def _remove_html_tags(self, text: Optional[str]) -> str:
        """Удаляет HTML-теги из текста"""
        if not text:
            return ""
        return re.sub(self._clean_tag_pattern, "", text).strip()
        
    def extract_vacancy_info(self, data: Dict[str, Any]) -> Optional[VacancyInfo]:
        """
        Извлекает информацию из вакансии.
        
        Args:
            data: Словарь с данными вакансии
            
        Returns:
            Optional[VacancyInfo]: Объект с данными вакансии или None в случае ошибки
        """
        if not isinstance(data, dict):
            logger.error(f"Некорректный формат данных вакансии: {type(data)}")
            return None
            
        try:
            # Обработка формы занятости
            employment_form_data = data.get("employment_form")
            employment_form = (
                EmploymentForm(id=employment_form_data.get("id", ""))
                if isinstance(employment_form_data, dict) else None
            )
            
            # Обработка опыта работы
            experience_data = data.get("experience")
            experience = (
                ExperienceVac(id=experience_data.get("id", ""))
                if isinstance(experience_data, dict) else None
            )
            
            # Обработка графика работы
            schedule_data = data.get("schedule")
            schedule = (
                Schedule(id=schedule_data.get("id", ""))
                if isinstance(schedule_data, dict) else None
            )
            
            # Обработка типа занятости
            employment_data = data.get("employment")
            employment = (
                Employment(id=employment_data.get("id", ""))
                if isinstance(employment_data, dict) else None
            )
            
            return VacancyInfo(
                description=self._remove_html_tags(data.get("description", "")),
                key_skills=[
                    skill.get("name", "") 
                    for skill in data.get("key_skills", [])
                    if isinstance(skill, dict)
                ],
                employment_form=employment_form,
                experience=experience,
                schedule=schedule,
                employment=employment
            )
        except Exception as e:
            logger.error(f"Ошибка при разборе данных вакансии: {e}")
            logger.exception("Полный traceback ошибки:")
            return None