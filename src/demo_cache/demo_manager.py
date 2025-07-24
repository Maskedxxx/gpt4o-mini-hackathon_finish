"""
Demo Manager для управления кешированными ответами LLM в демо-режиме.
Обеспечивает быструю демонстрацию функций без реальных вызовов OpenAI API.
"""
import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class DemoManager:
    """Управляет демо-режимом и кешированными ответами"""
    
    def __init__(self):
        """Инициализация с путями к директориям кеша"""
        self.project_root = Path(__file__).parent.parent.parent
        self.demo_cache_dir = self.project_root / "demo_cache"
        
        # Пути к основным директориям
        self.resume_profiles_dir = self.demo_cache_dir / "resume_profiles"
        self.vacancy_data_dir = self.demo_cache_dir / "vacancy_data"
        self.cached_responses_dir = self.demo_cache_dir / "cached_responses"
        self.generated_pdfs_dir = self.demo_cache_dir / "generated_pdfs"
        
        # Создаем директории если их нет
        self._ensure_directories_exist()
    
    def _ensure_directories_exist(self) -> None:
        """Создает необходимые директории если они не существуют"""
        directories = [
            self.resume_profiles_dir,
            self.vacancy_data_dir,
            self.cached_responses_dir / "cover_letter",
            self.cached_responses_dir / "interview_checklist", 
            self.cached_responses_dir / "interview_simulation",
            self.generated_pdfs_dir / "cover_letter",
            self.generated_pdfs_dir / "interview_checklist",
            self.generated_pdfs_dir / "interview_simulation"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def is_demo_mode(self) -> bool:
        """
        Проверка активности демо-режима через переменную DEMO_MODE=true
        
        Returns:
            bool: True если демо-режим активен, False иначе
        """
        demo_mode = os.getenv("DEMO_MODE", "false").lower()
        is_active = demo_mode in ("true", "1", "yes", "on")
        
        if is_active:
            logger.info("🎭 Demo mode is ACTIVE - using cached responses")
        else:
            logger.info("🌐 Live mode is ACTIVE - making real OpenAI API calls")
            
        return is_active
    
    def save_response(self, service_type: str, profile_level: str, response_data: dict) -> str:
        """
        Сохраняет ответ LLM в соответствующий JSON файл
        
        Args:
            service_type: Тип сервиса ('cover_letter', 'interview_checklist', 'interview_simulation')  
            profile_level: Уровень профиля ('junior', 'middle', 'senior')
            response_data: Данные ответа для сохранения
            
        Returns:
            str: Путь к сохраненному файлу
        """
        if service_type not in ["cover_letter", "interview_checklist", "interview_simulation"]:
            raise ValueError(f"Invalid service_type: {service_type}")
            
        if profile_level not in ["junior", "middle", "senior"]:
            raise ValueError(f"Invalid profile_level: {profile_level}")
        
        file_path = self.cached_responses_dir / service_type / f"{profile_level}_response.json"
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(response_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 Saved cached response: {service_type}/{profile_level}_response.json")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"❌ Failed to save response for {service_type}/{profile_level}: {e}")
            raise
    
    def load_cached_response(self, service_type: str, profile_level: str) -> Optional[dict]:
        """
        Загружает кешированный ответ по ключу
        
        Args:
            service_type: Тип сервиса
            profile_level: Уровень профиля
            
        Returns:
            Optional[dict]: Кешированный ответ или None если не найден
        """
        if service_type not in ["cover_letter", "interview_checklist", "interview_simulation"]:
            logger.warning(f"⚠️ Invalid service_type: {service_type}")
            return None
            
        if profile_level not in ["junior", "middle", "senior"]:
            logger.warning(f"⚠️ Invalid profile_level: {profile_level}")
            return None
        
        file_path = self.cached_responses_dir / service_type / f"{profile_level}_response.json"
        
        if not file_path.exists():
            logger.warning(f"📂 Cached response not found: {file_path}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"📥 Loaded cached response: {service_type}/{profile_level}_response.json")
            return data
            
        except Exception as e:
            logger.error(f"❌ Failed to load cached response {service_type}/{profile_level}: {e}")
            return None
    
    def get_pdf_path(self, service_type: str, profile_level: str) -> Optional[str]:
        """
        Возвращает путь к заготовленному PDF файлу
        
        Args:
            service_type: Тип сервиса
            profile_level: Уровень профиля
            
        Returns:
            Optional[str]: Путь к PDF файлу или None если не найден
        """
        if service_type not in ["cover_letter", "interview_checklist", "interview_simulation"]:
            logger.warning(f"⚠️ Invalid service_type: {service_type}")
            return None
            
        if profile_level not in ["junior", "middle", "senior"]:
            logger.warning(f"⚠️ Invalid profile_level: {profile_level}")
            return None
        
        file_path = self.generated_pdfs_dir / service_type / f"{profile_level}_{service_type}.pdf"
        
        if not file_path.exists():
            logger.warning(f"📂 Pre-generated PDF not found: {file_path}")
            return None
        
        logger.info(f"📄 Found pre-generated PDF: {service_type}/{profile_level}_{service_type}.pdf")
        return str(file_path)
    
    def detect_profile_level(self, resume_data: dict) -> str:
        """
        Определяет уровень профиля (junior/middle/senior) по данным резюме
        
        Args:
            resume_data: Словарь с данными резюме
            
        Returns:
            str: Уровень профиля ('junior', 'middle', 'senior')
        """
        if not isinstance(resume_data, dict):
            logger.warning("⚠️ resume_data is not a dict, defaulting to junior")
            return "junior"
        
        # Конвертируем весь объект резюме в строку для анализа
        resume_text = json.dumps(resume_data, ensure_ascii=False).lower()
        
        # Ключевые индикаторы уровня
        senior_indicators = [
            "senior", "lead", "architect", "team lead", "руководитель", "архитектор",
            "principal", "staff", "главный", "ведущий", "тимлид", "техлид"
        ]
        
        middle_indicators = [
            "middle", "мидл", "опытный", "3+ года", "4+ года", "5+ лет", 
            "три года", "четыре года", "пять лет", "средний", "intermediate"
        ]
        
        junior_indicators = [
            "junior", "джуниор", "начинающий", "стажер", "без опыта", "1 год",
            "год опыта", "junior developer", "entry level", "trainee"
        ]
        
        # Подсчет совпадений
        senior_score = sum(1 for indicator in senior_indicators if indicator in resume_text)
        middle_score = sum(1 for indicator in middle_indicators if indicator in resume_text)
        junior_score = sum(1 for indicator in junior_indicators if indicator in resume_text)
        
        # Дополнительная логика на основе опыта работы
        total_experience = resume_data.get('total_experience', 0)
        if isinstance(total_experience, dict):
            months = total_experience.get('months', 0)
        elif isinstance(total_experience, (int, float)):
            months = total_experience
        else:
            months = 0
        
        # Опыт в годах для дополнительной оценки
        years_experience = months / 12 if months > 0 else 0
        
        # Бонусы к скорам на основе опыта
        if years_experience >= 5:
            senior_score += 2
        elif years_experience >= 2:
            middle_score += 2
        elif years_experience < 2:
            junior_score += 1
        
        # Определение уровня по максимальному скору
        if senior_score >= max(middle_score, junior_score):
            detected_level = "senior"
        elif middle_score >= junior_score:
            detected_level = "middle"  
        else:
            detected_level = "junior"
        
        logger.info(f"🎯 Profile level detected: {detected_level} "
                   f"(scores: senior={senior_score}, middle={middle_score}, junior={junior_score}, "
                   f"experience={years_experience:.1f} years)")
        
        return detected_level
    
    def save_resume_profile(self, profile_level: str, resume_data: dict) -> str:
        """
        Сохраняет профиль тестового резюме
        
        Args:
            profile_level: Уровень профиля
            resume_data: Данные резюме
            
        Returns:
            str: Путь к сохраненному файлу
        """
        if profile_level not in ["junior", "middle", "senior"]:
            raise ValueError(f"Invalid profile_level: {profile_level}")
        
        file_path = self.resume_profiles_dir / f"{profile_level}_profile.json"
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(resume_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 Saved resume profile: {profile_level}_profile.json")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"❌ Failed to save resume profile {profile_level}: {e}")
            raise
    
    def save_vacancy_data(self, vacancy_data: dict) -> str:
        """
        Сохраняет данные тестовой вакансии
        
        Args:
            vacancy_data: Данные вакансии
            
        Returns:
            str: Путь к сохраненному файлу
        """
        file_path = self.vacancy_data_dir / "target_vacancy.json"
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(vacancy_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 Saved vacancy data: target_vacancy.json")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"❌ Failed to save vacancy data: {e}")
            raise
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Возвращает статистику кеширования
        
        Returns:
            Dict: Статистика по количеству кешированных ответов и PDF файлов
        """
        stats = {
            "demo_mode_active": self.is_demo_mode(),
            "cached_responses": {},
            "generated_pdfs": {},
            "total_cached_responses": 0,
            "total_generated_pdfs": 0
        }
        
        # Подсчет кешированных ответов
        for service_type in ["cover_letter", "interview_checklist", "interview_simulation"]:
            service_responses = 0
            service_pdfs = 0
            
            for profile_level in ["junior", "middle", "senior"]:
                # Проверяем наличие кешированных ответов
                response_file = self.cached_responses_dir / service_type / f"{profile_level}_response.json"
                if response_file.exists():
                    service_responses += 1
                
                # Проверяем наличие PDF файлов
                pdf_file = self.generated_pdfs_dir / service_type / f"{profile_level}_{service_type}.pdf"
                if pdf_file.exists():
                    service_pdfs += 1
            
            stats["cached_responses"][service_type] = service_responses
            stats["generated_pdfs"][service_type] = service_pdfs
            stats["total_cached_responses"] += service_responses
            stats["total_generated_pdfs"] += service_pdfs
        
        return stats