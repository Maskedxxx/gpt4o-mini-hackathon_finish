# src/parsers/resume_extractor.py
import re
import logging
from typing import Dict, Any, Optional, Union
from src.models.resume_models import (
    ResumeInfo, Experience, Language, Level, 
    Relocation, RelocationType, Salary, ProfessionalRole,
    Education, EducationLevel, PrimaryEducation, AdditionalEducation,
    Certificate, Contact, ContactType, ContactValue, Site, SiteType
)

from src.utils import get_logger
logger = get_logger()

class ResumeExtractor:
    """Класс для извлечения информации из данных резюме"""
    
    def __init__(self):
        self._clean_tag_pattern = re.compile(r"<.*?>")
    
    def _remove_html_tags(self, text: Optional[str]) -> str:
        """Удаляет HTML-теги из текста"""
        if not text:
            return ""
        return re.sub(self._clean_tag_pattern, "", text).strip()
    
    def _extract_certificates(self, data: Dict[str, Any]) -> list[Certificate]:
        """Извлекает информацию о сертификатах"""
        certificates = []
        certificate_data = data.get("certificate", [])
        
        for cert in certificate_data:
            if isinstance(cert, dict):
                certificates.append(Certificate(
                    title=cert.get("title", ""),
                    url=cert.get("url")
                ))
        
        return certificates
    
    def _extract_contacts(self, data: Dict[str, Any]) -> list[Contact]:
        """Извлекает контактную информацию"""
        contacts = []
        contact_data = data.get("contact", [])
        
        for contact in contact_data:
            if isinstance(contact, dict):
                # Парсим тип контакта
                type_data = contact.get("type", {})
                if isinstance(type_data, dict):
                    contact_type = ContactType(name=type_data.get("name", ""))
                    
                    # Парсим значение контакта
                    value_data = contact.get("value")
                    if isinstance(value_data, dict):
                        # Если value - объект с formatted
                        contact_value = ContactValue(formatted=value_data.get("formatted", ""))
                    elif isinstance(value_data, str):
                        # Если value - строка
                        contact_value = value_data
                    else:
                        continue  # Пропускаем некорректные данные
                    
                    contacts.append(Contact(
                        type=contact_type,
                        value=contact_value
                    ))
        
        return contacts
    
    def _extract_sites(self, data: Dict[str, Any]) -> list[Site]:
        """Извлекает информацию о сайтах"""
        sites = []
        site_data = data.get("site", [])
        
        for site in site_data:
            if isinstance(site, dict):
                # Парсим тип сайта
                type_data = site.get("type", {})
                if isinstance(type_data, dict):
                    site_type = SiteType(name=type_data.get("name", ""))
                    
                    sites.append(Site(
                        type=site_type,
                        url=site.get("url", "")
                    ))
        
        return sites
    
    def _extract_education(self, data: Dict[str, Any]) -> Optional[Education]:
        """Извлекает информацию об образовании из данных резюме."""
        education_data = data.get("education")
        if not education_data or not isinstance(education_data, dict):
            return None
        
        try:
            # Уровень образования
            level = None
            level_data = education_data.get("level")
            if level_data and isinstance(level_data, dict):
                level = EducationLevel(name=level_data.get("name", ""))
            
            # Основное образование
            primary_education = []
            primary_data = education_data.get("primary", [])
            for edu in primary_data:
                if isinstance(edu, dict):
                    primary_education.append(PrimaryEducation(
                        name=edu.get("name", ""),
                        organization=edu.get("organization"),
                        result=edu.get("result"),
                        year=edu.get("year")
                    ))
            
            # Дополнительное образование
            additional_education = []
            additional_data = education_data.get("additional", [])
            for edu in additional_data:
                if isinstance(edu, dict):
                    additional_education.append(AdditionalEducation(
                        name=edu.get("name", ""),
                        organization=edu.get("organization"),
                        result=edu.get("result"),
                        year=edu.get("year")
                    ))
            
            return Education(
                level=level,
                primary=primary_education,
                additional=additional_education
            )
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге образования: {e}")
            return None
    
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
                        company=exp.get("company"),  # Новое поле
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
            
            # Обработка образования
            education = self._extract_education(data)
            
            # Новые поля
            certificates = self._extract_certificates(data)
            contacts = self._extract_contacts(data)
            sites = self._extract_sites(data)
                
            return ResumeInfo(
                # Новые персональные поля
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                middle_name=data.get("middle_name"),
                
                # Основная информация
                title=data.get("title", ""),
                total_experience=data.get("total_experience", {}).get("months") if data.get("total_experience") else None,
                skills=data.get("skills", ""),
                skill_set=data.get("skill_set", []),
                experience=experience,
                employments=[emp.get("name", "") for emp in data.get("employments", [])],
                schedules=[sch.get("name", "") for sch in data.get("schedules", [])],
                languages=languages,
                relocation=relocation,
                salary=salary,
                professional_roles=professional_roles,
                education=education,
                
                # Новые поля
                certificate=certificates,
                contact=contacts,
                site=sites
            )
        except Exception as e:
            logger.error(f"Ошибка при разборе данных резюме: {e}")
            logger.exception("Полный traceback ошибки:")
            return None