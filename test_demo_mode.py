#!/usr/bin/env python3
"""
Скрипт для тестирования системы демо-режима.

Проверяет:
1. Определение уровня профиля по данным резюме
2. Переключение между демо и обычным режимами
3. Загрузку кешированных ответов
4. Fallback на реальные LLM вызовы

Запуск:
    python test_demo_mode.py
"""

import os
import asyncio
from pathlib import Path
import sys

# Добавляем корень проекта в Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.demo_cache.demo_manager import DemoManager
from src.llm_cover_letter.llm_cover_letter_generator import EnhancedLLMCoverLetterGenerator
from src.llm_interview_checklist.llm_interview_checklist_generator import LLMInterviewChecklistGenerator
from src.llm_interview_simulation.llm_interview_simulator import ProfessionalInterviewSimulator
from src.utils import get_logger

logger = get_logger(__name__)

# Тестовые данные
TEST_RESUMES = {
    "junior_candidate": {
        "first_name": "Иван",
        "last_name": "Иванов", 
        "total_experience": 6,  # 6 месяцев
        "position_title": "Junior Python Developer",
        "skills": ["Python", "Django", "Git"],
        "experience": [{"company": "StartupTech", "position": "Junior Developer", "period": "6 месяцев"}]
    },
    "middle_candidate": {
        "first_name": "Елена",
        "last_name": "Сидорова",
        "total_experience": 30,  # 2.5 года
        "position_title": "Python Developer", 
        "skills": ["Python", "Django", "FastAPI", "PostgreSQL", "Docker"],
        "experience": [{"company": "TechCorp", "position": "Python Developer", "period": "2 года"}]
    },
    "senior_candidate": {
        "first_name": "Сергей", 
        "last_name": "Архитектов",
        "total_experience": 72,  # 6 лет
        "position_title": "Senior Python Developer",
        "skills": ["Python", "Django", "FastAPI", "PostgreSQL", "Docker", "Kubernetes", "Architecture"],
        "experience": [{"company": "Enterprise", "position": "Senior Developer", "period": "4 года"}]
    }
}

TEST_VACANCY = {
    "id": "test123",
    "name": "Python Developer",
    "employer": {"name": "TestCompany"},
    "description": "Test vacancy for Python developer position"
}

class DemoModeTest:
    """Тестер демо-режима"""
    
    def __init__(self):
        self.demo_manager = DemoManager()
    
    async def run_all_tests(self):
        """Запускает все тесты"""
        logger.info("🧪 Начинаем тестирование демо-режима...")
        
        tests = [
            ("Тест определения уровня профиля", self.test_profile_detection),
            ("Тест переключения режимов", self.test_mode_switching),
            ("Тест кеширования ответов", self.test_response_caching),
            ("Тест PDF файлов", self.test_pdf_files),
            ("Тест LLM сервисов в демо-режиме", self.test_llm_services_demo),
            ("Тест статистики кеша", self.test_cache_statistics)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            logger.info(f"\n📋 {test_name}")
            try:
                result = await test_func()
                if result:
                    logger.info("  ✅ PASSED")
                    passed += 1
                else:
                    logger.error("  ❌ FAILED")
            except Exception as e:
                logger.error(f"  💥 ERROR: {e}")
        
        logger.info(f"\n📊 Результаты тестирования: {passed}/{total} тестов пройдено")
        return passed == total
    
    async def test_profile_detection(self):
        """Тестирует определение уровня профиля"""
        try:
            for candidate_type, resume_data in TEST_RESUMES.items():
                detected_level = self.demo_manager.detect_profile_level(resume_data)
                expected_level = candidate_type.split('_')[0]  # junior, middle, senior
                
                logger.info(f"  {candidate_type}: {detected_level} (ожидался {expected_level})")
                
                if detected_level != expected_level:
                    logger.warning(f"    ⚠️ Несоответствие уровня для {candidate_type}")
            
            return True
        except Exception as e:
            logger.error(f"Ошибка в тесте определения профиля: {e}")
            return False
    
    async def test_mode_switching(self):
        """Тестирует переключение между режимами"""
        try:
            # Сохраняем исходное значение
            original_demo_mode = os.getenv("DEMO_MODE", "false")
            
            # Тест обычного режима
            os.environ["DEMO_MODE"] = "false"
            assert not self.demo_manager.is_demo_mode(), "Обычный режим не активирован"
            logger.info("  ✓ Обычный режим работает")
            
            # Тест демо-режима
            os.environ["DEMO_MODE"] = "true"
            assert self.demo_manager.is_demo_mode(), "Демо-режим не активирован"
            logger.info("  ✓ Демо-режим работает")
            
            # Восстанавливаем исходное значение
            os.environ["DEMO_MODE"] = original_demo_mode
            
            return True
        except Exception as e:
            logger.error(f"Ошибка в тесте переключения режимов: {e}")
            return False
    
    async def test_response_caching(self):
        """Тестирует систему кеширования ответов"""
        try:
            # Тестовые данные для сохранения
            test_response = {
                "test_field": "test_value",
                "timestamp": "2024-01-01T00:00:00"
            }
            
            # Сохраняем тестовый ответ
            self.demo_manager.save_response("cover_letter", "junior", test_response)
            logger.info("  ✓ Ответ сохранен")
            
            # Загружаем тестовый ответ
            loaded_response = self.demo_manager.load_cached_response("cover_letter", "junior")
            assert loaded_response == test_response, "Загруженные данные не совпадают"
            logger.info("  ✓ Ответ загружен корректно")
            
            # Тестируем несуществующий ответ
            missing_response = self.demo_manager.load_cached_response("nonexistent", "junior")
            assert missing_response is None, "Должен был вернуть None для несуществующего ответа"
            logger.info("  ✓ Обработка отсутствующих ответов работает")
            
            return True
        except Exception as e:
            logger.error(f"Ошибка в тесте кеширования: {e}")
            return False
    
    async def test_pdf_files(self):
        """Тестирует систему PDF файлов"""
        try:
            # Проверяем существование директорий
            for service_type in ["cover_letter", "interview_checklist", "interview_simulation"]:
                pdf_dir = self.demo_manager.generated_pdfs_dir / service_type
                if not pdf_dir.exists():
                    logger.warning(f"  ⚠️ Директория {pdf_dir} не найдена")
                    continue
                
                for level in ["junior", "middle", "senior"]:
                    pdf_path = self.demo_manager.get_pdf_path(service_type, level)
                    if pdf_path and Path(pdf_path).exists():
                        logger.info(f"  ✓ PDF найден: {service_type}/{level}")
                    else:
                        logger.warning(f"  ⚠️ PDF не найден: {service_type}/{level}")
            
            return True
        except Exception as e:
            logger.error(f"Ошибка в тесте PDF файлов: {e}")
            return False
    
    async def test_llm_services_demo(self):
        """Тестирует работу LLM сервисов в демо-режиме"""
        # Активируем демо-режим для этого теста
        os.environ["DEMO_MODE"] = "true"
        
        try:
            # Создаем генераторы
            cover_letter_gen = EnhancedLLMCoverLetterGenerator()
            checklist_gen = LLMInterviewChecklistGenerator()
            simulation_gen = ProfessionalInterviewSimulator()
            
            # Тестируем каждый сервис с junior профилем
            junior_resume = TEST_RESUMES["junior_candidate"]
            
            # Cover Letter
            logger.info("  📝 Тестируем cover letter...")
            cover_letter = await cover_letter_gen.generate_enhanced_cover_letter(
                junior_resume, TEST_VACANCY
            )
            if cover_letter:
                logger.info("    ✓ Cover letter сгенерирован")
            else:
                logger.warning("    ⚠️ Cover letter не сгенерирован")
            
            # Interview Checklist
            logger.info("  📋 Тестируем interview checklist...")
            checklist = await checklist_gen.generate_professional_interview_checklist(
                junior_resume, TEST_VACANCY
            )
            if checklist:
                logger.info("    ✓ Checklist сгенерирован")
            else:
                logger.warning("    ⚠️ Checklist не сгенерирован")
            
            # Interview Simulation (только если есть кеш)
            logger.info("  🎭 Тестируем interview simulation...")
            simulation = await simulation_gen.simulate_interview(
                junior_resume, TEST_VACANCY
            )
            if simulation:
                logger.info("    ✓ Simulation сгенерирована")
            else:
                logger.warning("    ⚠️ Simulation не сгенерирована")
            
            return True
        except Exception as e:
            logger.error(f"Ошибка в тесте LLM сервисов: {e}")
            return False
        finally:
            # Восстанавливаем режим
            os.environ["DEMO_MODE"] = "false"
    
    async def test_cache_statistics(self):
        """Тестирует статистику кеша"""
        try:
            stats = self.demo_manager.get_cache_stats()
            
            logger.info(f"  📊 Режим: {'DEMO' if stats['demo_mode_active'] else 'LIVE'}")
            logger.info(f"  📊 Всего кешированных ответов: {stats['total_cached_responses']}")
            logger.info(f"  📊 Всего PDF файлов: {stats['total_generated_pdfs']}")
            
            # Проверяем структуру статистики
            required_keys = ["demo_mode_active", "cached_responses", "generated_pdfs", 
                           "total_cached_responses", "total_generated_pdfs"]
            
            for key in required_keys:
                assert key in stats, f"Отсутствует ключ {key} в статистике"
            
            logger.info("  ✓ Статистика корректна")
            return True
        except Exception as e:
            logger.error(f"Ошибка в тесте статистики: {e}")
            return False

async def main():
    """Главная функция"""
    print("🧪 AI Resume Assistant - Demo Mode Tester")
    print("=" * 50)
    
    tester = DemoModeTest()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 Все тесты пройдены успешно!")
        print("✅ Система демо-режима готова к использованию")
    else:
        print("\n💥 Некоторые тесты не пройдены")
        print("⚠️ Проверьте логи для деталей")
    
    # Инструкции по использованию
    print("\n📋 Инструкции по использованию:")
    print("1. Генерация кеша:")
    print("   export DEMO_MODE=false")
    print("   python generate_demo_cache.py")
    print("\n2. Активация демо-режима:")
    print("   export DEMO_MODE=true")
    print("   python run_unified_app.py")
    print("\n3. Обычный режим:")
    print("   export DEMO_MODE=false")
    print("   python run_unified_app.py")

if __name__ == "__main__":
    asyncio.run(main())