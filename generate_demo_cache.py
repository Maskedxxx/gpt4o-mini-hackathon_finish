#!/usr/bin/env python3
"""
Скрипт для генерации демо-кеша с тестовыми данными и PDF файлами.

Создает:
1. Тестовые профили резюме (junior, middle, senior)
2. Тестовую вакансию
3. Кешированные ответы от LLM сервисов
4. Заготовленные PDF файлы

Запуск:
    python generate_demo_cache.py

Требования:
    - Запуск в обычном режиме (DEMO_MODE=false)
    - Доступ к OpenAI API
    - Все сервисы должны быть функциональными
"""

import os
import sys
import asyncio
import json
from pathlib import Path

# Добавляем корень проекта в Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.demo_cache.demo_manager import DemoManager
from src.parsers.pdf_resume_parser import PDFResumeParser
from src.parsers.vacancy_extractor import VacancyExtractor
from src.llm_cover_letter.llm_cover_letter_generator import EnhancedLLMCoverLetterGenerator
from src.llm_interview_checklist.llm_interview_checklist_generator import LLMInterviewChecklistGenerator
from src.llm_interview_simulation.llm_interview_simulator import ProfessionalInterviewSimulator
from src.web_app.cover_letter.pdf_generator import CoverLetterPDFGenerator
from src.web_app.interview_checklist.pdf_generator import InterviewChecklistPDFGenerator
from src.llm_interview_simulation.pdf_generator import ProfessionalInterviewPDFGenerator
from src.utils import get_logger

logger = get_logger(__name__)

# Тестовые данные резюме на основе реальных данных из pdf_feik
SAMPLE_RESUMES = {
    "junior": {
        # Основные поля согласно ResumeInfo модели
        "first_name": "Алексей",
        "last_name": "Петров",
        "title": "Junior Python Developer",
        "total_experience": 14,  # 1 год 2 месяца в месяцах
        
        # Навыки согласно модели ResumeInfo
        "skills": "Опытный Junior Python Developer с solid пониманием основ веб-разработки. Владею Django и Django REST Framework для создания RESTful API. Знаком с принципами Clean Code и написанием unit-тестов с pytest. Имею опыт работы с PostgreSQL и основами DevOps (Docker, Git). Активно изучаю микросервисную архитектуру и асинхронное программирование.",
        "skill_set": [
            "Python", "Django", "Django REST Framework", "Flask", "PostgreSQL", 
            "SQLAlchemy", "Git", "Docker", "pytest", "HTML/CSS", "JavaScript", 
            "Linux", "REST API", "Agile/Scrum"
        ],
        
        # Опыт работы согласно модели Experience
        "experience": [
            {
                "company": "ТехСтарт",
                "position": "Junior Python Developer", 
                "start": "2024-01",
                "end": None,
                "description": "Разработал REST API для внутренней системы учета на Django REST Framework. Написал автоматические тесты, покрытие кода увеличилось до 85%. Оптимизировал SQL-запросы, ускорив загрузку отчетов на 30%. Участвовал в code review и следовал принципам Clean Code."
            },
            {
                "company": "WebSolutions",
                "position": "Python Developer (стажировка)",
                "start": "2023-09",
                "end": "2023-12", 
                "description": "Изучение существующего кода и архитектуры проекта. Исправление багов и мелкие доработки функционала. Написание unit-тестов для legacy кода. Участие в ежедневных standup встречах команды."
            }
        ],
        
        # Дополнительные поля согласно ResumeInfo
        "employments": ["Полная занятость"],
        "schedules": ["Полный день", "Гибкий график"],
        "languages": [
            {"name": "Русский", "level": {"name": "Родной"}}, 
            {"name": "Английский", "level": {"name": "B1"}}
        ],
        "professional_roles": [{"name": "Backend-разработчик"}, {"name": "Python-разработчик"}],
        "salary": {"amount": 120000},
        "education": {
            "level": {"name": "Высшее"},
            "primary": [{
                "name": "Московский государственный технический университет им. Н.Э. Баумана",
                "organization": "Факультет информатики и систем управления",
                "result": "Бакалавр, Программная инженерия",
                "year": 2024
            }],
            "additional": []
        },
        
        # Контакты и сайты согласно модели
        "contact": [
            {"type": {"name": "Телефон"}, "value": "+7 (999) 123-45-67"},
            {"type": {"name": "Электронная почта"}, "value": "aleksey.petrov@gmail.com"}
        ],
        "site": [
            {"type": {"name": "GitHub"}, "url": "https://github.com/aleksey-petrov-dev"}
        ]
    },
    
    "middle": {
        # Основная информация - из middle_resume.html
        "first_name": "Екатерина", 
        "last_name": "Смирнова",
        "phone": "+7 (985) 234-56-78",
        "email": "ekaterina.smirnova@gmail.com", 
        "total_experience": 32,  # 2 года 8 месяцев в месяцах
        "position_title": "Middle Python Developer",
        
        # Расширенные навыки
        "skills": [
            "Python", "FastAPI", "Django", "Flask", "PostgreSQL", "Redis", "Celery",
            "Docker", "Kubernetes", "AWS", "Apache Airflow", "Prometheus", "Grafana",
            "pytest", "Git", "CI/CD", "Microservices", "REST API", "GraphQL", 
            "SQLAlchemy", "Pandas", "NumPy", "Linux", "Nginx"
        ],
        
        # Детальный опыт работы
        "experience": [
            {
                "company": "FinTech Solutions",
                "position": "Middle Python Developer",
                "period": "Апрель 2023 — настоящее время (1 год 4 месяца)",
                "description": "Разработала микросервисную архитектуру платежной системы на FastAPI. Увеличила производительность API на 250% через асинхронное программирование. Внедрила CI/CD pipeline с автоматическим деплоем в Docker-контейнерах. Менторила 2 junior разработчиков, провела 15+ code review. Оптимизировала базу данных, сократив время запросов на 60%."
            },
            {
                "company": "DataCorp Analytics",
                "position": "Python Developer", 
                "period": "Сентябрь 2021 — Март 2023 (1 год 7 месяцев)",
                "description": "Разработала ETL-пайплайны для обработки больших данных (10+ ГБ/день). Создала Django-приложение для визуализации аналитических отчетов. Автоматизировала процессы сбора данных, сократив ручную работу на 80%. Участвовала в проектировании архитектуры data warehouse."
            }
        ],
        
        # Образование
        "education": [
            {
                "institution": "Московский физико-технический институт (МФТИ)",
                "degree": "Магистр, Анализ данных и машинное обучение",
                "year": "2021",
                "faculty": "Факультет управления и прикладной математики"
            },
            {
                "institution": "Московский физико-технический институт (МФТИ)",
                "degree": "Бакалавр, Прикладная математика и информатика",
                "year": "2019",
                "faculty": "Факультет управления и прикладной математики"
            }
        ],
        
        # Крупные проекты
        "projects": [
            {
                "name": "Микросервисная платежная система",
                "description": "Высоконагруженная система обрабатывающая 10k+ транзакций/день с uptime 99.9%",
                "technologies": ["Python", "FastAPI", "PostgreSQL", "Redis", "Celery", "Docker", "Kubernetes", "Prometheus"],
                "achievements": ["5 независимых микросервисов", "Асинхронная обработка через Celery + Redis", "Мониторинг с Prometheus + Grafana", "Автоматическое тестирование с покрытием 95%"]
            },
            {
                "name": "Платформа бизнес-аналитики",
                "description": "Полноценная BI-платформа с интерактивными дашбордами для 200+ пользователей",
                "technologies": ["Python", "Django", "PostgreSQL", "Apache Airflow", "Redis", "Pandas", "Plotly"],
                "achievements": ["RESTful API на Django REST Framework", "Интеграция с Apache Airflow", "Real-time дашборды с WebSocket", "Кэширование с Redis"]
            }
        ],
        
        # Сертификации
        "certifications": [
            "AWS Certified Solutions Architect – Associate (2024)",
            "Certified Kubernetes Application Developer (CKAD) (2023)",
            "AWS Certified Developer (2022)"
        ],
        
        # Дополнительная информация
        "github": "https://github.com/kate-python-dev",
        "linkedin": "https://linkedin.com/in/ekaterina-smirnova-dev",
        "salary_expectations": 190000,
        "location": "Москва",
        "age": 27,
        "languages": [{"name": "Русский", "level": "Родной"}, {"name": "Английский", "level": "B2"}],
        "achievements": ["Докладчик на PyCon Russia 2024", "Участник хакатона FinTech Challenge 2023 (2 место)", "Контрибьютор в FastAPI, Celery"]
    },
    
    "senior": {
        # Основная информация - из senior_resume.html
        "first_name": "Дмитрий",
        "last_name": "Козлов", 
        "phone": "+7 (916) 345-67-89",
        "email": "dmitry.kozlov.senior@gmail.com",
        "total_experience": 84,  # 7+ лет в месяцах
        "position_title": "Senior Python Developer / Tech Lead",
        
        # Экспертные навыки + лидерство
        "skills": [
            "Python", "FastAPI", "Django", "Flask", "PostgreSQL", "MongoDB", "Redis", 
            "Celery", "Docker", "Kubernetes", "AWS", "GCP", "Terraform", "Apache Kafka",
            "RabbitMQ", "Elasticsearch", "Prometheus", "Grafana", "Jenkins", "GitLab CI",
            "pytest", "Git", "Architecture Design", "Team Leadership", "Microservices",
            "REST API", "GraphQL", "gRPC", "System Design", "Performance Optimization",
            "Code Review", "Mentoring", "Technical Interviews", "Agile/Scrum", "DevOps"
        ],
        
        # Лидерский опыт работы
        "experience": [
            {
                "company": "Enterprise Tech Solutions",
                "position": "Senior Python Developer / Tech Lead",
                "period": "Январь 2022 — настоящее время (2 года 7 месяцев)",
                "description": "Руководство командой из 8 разработчиков. Архитектура высоконагруженных распределенных систем обрабатывающих 1M+ запросов в день. Внедрение best practices разработки и code review процессов. Техническое интервьюирование кандидатов. Планирование технического развития продукта."
            },
            {
                "company": "FinTech Innovations",
                "position": "Senior Python Developer",
                "period": "Июнь 2020 — Декабрь 2021 (1 год 7 месяцев)", 
                "description": "Разработка криптовалютной торговой платформы с real-time обработкой данных. Оптимизация алгоритмов торговли, увеличение скорости обработки на 400%. Интеграция с 15+ криптобиржами через WebSocket и REST API. Ментиринг middle разработчиков."
            },
            {
                "company": "Data Analytics Corp",
                "position": "Python Developer",
                "period": "Март 2018 — Май 2020 (2 года 3 месяца)",
                "description": "Разработка ML-пайплайнов для обработки больших данных. Создание рекомендательных систем с использованием TensorFlow и scikit-learn. Проектирование и внедрение data lake архитектуры. Оптимизация ETL процессов."
            }
        ],
        
        # Высшее образование
        "education": [
            {
                "institution": "Московский государственный университет им. М.В. Ломоносова",
                "degree": "Магистр, Прикладная математика и информатика",
                "year": "2017",
                "faculty": "Факультет вычислительной математики и кибернетики"
            }
        ],
        
        # Архитектурные проекты
        "projects": [
            {
                "name": "Высоконагруженная платформа электронной коммерции",
                "description": "Масштабируемая e-commerce платформа обслуживающая 100k+ пользователей с peak нагрузкой 50k RPS",
                "technologies": ["Python", "FastAPI", "PostgreSQL", "Redis", "Kafka", "Kubernetes", "AWS", "Terraform"],
                "achievements": [
                    "Микросервисная архитектура из 25+ сервисов",
                    "Event-driven архитектура с Apache Kafka", 
                    "Auto-scaling в Kubernetes",
                    "Мониторинг с Prometheus/Grafana/ELK stack",
                    "99.99% uptime в production"
                ]
            },
            {
                "name": "ML-платформа для финансовой аналитики",
                "description": "Платформа машинного обучения для прогнозирования рыночных трендов с обработкой 10TB+ данных в день",
                "technologies": ["Python", "TensorFlow", "Kubernetes", "Apache Airflow", "Kafka", "ClickHouse", "Docker"],
                "achievements": [
                    "Real-time feature engineering pipeline",
                    "A/B testing framework для ML моделей",
                    "Автоматическое переобучение моделей",
                    "Model serving с latency < 10ms"
                ]
            }
        ],
        
        # Лидерские навыки и достижения
        "leadership_experience": {
            "team_size": "8 разработчиков",
            "mentoring": "15+ разработчиков за карьеру",
            "interviews_conducted": "50+ технических интервью",
            "talks_given": ["Python Meetup Moscow", "BackendConf 2024", "HighLoad++ 2023"],
            "open_source": ["Maintainer популярной Python библиотеки (5k+ stars)", "Contributor в FastAPI, Django"]
        },
        
        # Экспертные сертификации
        "certifications": [
            "AWS Certified Solutions Architect – Professional (2024)",
            "Certified Kubernetes Administrator (CKA) (2023)", 
            "Google Cloud Professional Data Engineer (2023)"
        ],
        
        # Дополнительная информация
        "github": "https://github.com/dmitry-senior-dev",
        "linkedin": "https://linkedin.com/in/dmitry-kozlov-senior",
        "salary_expectations": 350000,
        "location": "Москва",
        "age": 32,
        "languages": [{"name": "Русский", "level": "Родной"}, {"name": "Английский", "level": "C1"}],
        "achievements": [
            "Tech Lead года в Enterprise Tech Solutions (2023)",
            "Speaker на HighLoad++ 2023: 'Архитектура микросервисов на Python'",
            "Автор статей на Habr (50k+ просмотров)",
            "Maintainer open-source библиотеки с 5k+ stars на GitHub"
        ]
    }
}

# Тестовая вакансия соответствующая модели VacancyInfo
SAMPLE_VACANCY = {
    # Основные поля согласно VacancyInfo модели
    "name": "Middle/Senior Python Developer", 
    "company_name": "InnovateTech Solutions",
    "description": """
    <h3>О компании</h3>
    <p><strong>InnovateTech Solutions</strong> — динамично развивающаяся IT-компания, специализирующаяся на создании высоконагруженных веб-сервисов и микросервисных архитектур. Мы работаем с клиентами из финтеха, e-commerce и медиатеха, создавая решения, которыми пользуются миллионы пользователей.</p>
    
    <h3>Что мы ищем</h3>
    <p>В нашу команду Backend-разработки требуется <strong>Middle/Senior Python Developer</strong> для работы над высоконагруженными проектами. Идеальный кандидат имеет опыт создания масштабируемых API, работы с микросервисами и оптимизации производительности.</p>
    
    <h3>Основные обязанности</h3>
    <ul>
        <li>Разработка и поддержка высоконагруженных API на Python (FastAPI/Django)</li>
        <li>Проектирование микросервисной архитектуры</li>
        <li>Оптимизация производительности и масштабируемости системы</li>
        <li>Code review и менторинг junior разработчиков</li>
        <li>Участие в архитектурных решениях и технических дискуссиях</li>
        <li>Интеграция с внешними API и сервисами</li>
        <li>Работа с базами данных (PostgreSQL, Redis)</li>
        <li>Настройка CI/CD пайплайнов и деплоя в контейнерах</li>
    </ul>
    
    <h3>Обязательные требования</h3>
    <ul>
        <li><strong>Python 3.8+</strong> — глубокое знание языка и его экосистемы</li>
        <li><strong>FastAPI или Django</strong> — опыт разработки веб-приложений и API</li>
        <li><strong>PostgreSQL</strong> — проектирование схем БД, оптимизация запросов</li>
        <li><strong>Docker</strong> — контейнеризация приложений</li>
        <li><strong>Git</strong> — опыт работы в команде с системами контроля версий</li>
        <li><strong>REST API</strong> — понимание принципов и лучших практик</li>
        <li><strong>Linux</strong> — уверенная работа в командной строке</li>
        <li>Опыт коммерческой разработки <strong>от 2 лет</strong></li>
    </ul>
    
    <h3>Желательные навыки</h3>
    <ul>
        <li><strong>Kubernetes</strong> — оркестрация контейнеров</li>
        <li><strong>Redis</strong> — кеширование и очереди</li>
        <li><strong>Celery</strong> — асинхронная обработка задач</li>
        <li><strong>AWS/GCP</strong> — облачные платформы</li>
        <li><strong>Microservices</strong> — опыт проектирования микросервисной архитектуры</li>
        <li><strong>GraphQL</strong> — альтернатива REST API</li>
        <li><strong>pytest</strong> — автоматическое тестирование</li>
        <li><strong>Monitoring</strong> — Prometheus, Grafana, ELK</li>
    </ul>
    
    <h3>Что мы предлагаем</h3>
    <ul>
        <li>💰 <strong>Зарплата:</strong> 180 000 - 350 000 ₽ на руки (в зависимости от уровня)</li>
        <li>🏠 <strong>Формат работы:</strong> гибридный/удаленка</li>
        <li>📈 <strong>Профессиональный рост:</strong> менторинг, конференции, курсы</li>
        <li>🎯 <strong>Интересные задачи:</strong> высокие нагрузки, современные технологии</li>
        <li>🏥 <strong>ДМС</strong> для сотрудника и семьи</li>
        <li>🏖️ <strong>Отпуск:</strong> 28 рабочих дней + дополнительные дни</li>
        <li>💻 <strong>Оборудование:</strong> MacBook Pro/мощный PC на выбор</li>
        <li>🎓 <strong>Обучение:</strong> бюджет на курсы и конференции</li>
    </ul>
    
    <h3>Процесс отбора</h3>
    <ol>
        <li>Техническое интервью с тимлидом (45 мин)</li>
        <li>Архитектурное интервью (system design, 60 мин)</li>
        <li>Культурное интервью с HR (30 мин)</li>
        <li>Финальное интервью с CTO (30 мин)</li>
    </ol>
    
    <p><strong>Локация:</strong> Москва, БЦ "Белая Площадь" (м. Белорусская)<br>
    <strong>Занятость:</strong> полная<br>
    <strong>График:</strong> гибкий, core time 11:00-16:00</p>
    """,
    
    # Ключевые навыки (список строк согласно модели)
    "key_skills": [
        "Python", "FastAPI", "Django", "PostgreSQL", "Docker", "Git", 
        "REST API", "Linux", "Redis", "Celery", "Kubernetes", "AWS", 
        "Microservices", "GraphQL", "pytest", "CI/CD", "System Design"
    ],
    
    # Профессиональные роли
    "professional_roles": [
        {"name": "Backend-разработчик"},
        {"name": "Python-разработчик"},
    ],
    
    # Дополнительные поля (опциональные согласно модели)
    "employment_form": {"id": "full"},
    "experience": {"id": "between1And3"}, 
    "schedule": {"id": "flexible"},
    "employment": {"id": "full"}
}

class DemoCacheGenerator:
    """Генератор демо-кеша"""
    
    def __init__(self):
        self.demo_manager = DemoManager()
        self.cover_letter_generator = EnhancedLLMCoverLetterGenerator()
        self.checklist_generator = LLMInterviewChecklistGenerator()
        self.simulation_generator = ProfessionalInterviewSimulator()
        
    async def generate_all(self):
        """Генерирует полный демо-кеш"""
        logger.info("🚀 Начинаем генерацию демо-кеша...")
        
        # Проверяем что мы НЕ в демо-режиме
        if self.demo_manager.is_demo_mode():
            logger.error("❌ Скрипт должен запускаться в ОБЫЧНОМ режиме (DEMO_MODE=false)")
            return False
        
        try:
            # 1. Сохраняем тестовые данные
            await self.save_test_data()
            
            # 2. Генерируем кешированные ответы
            await self.generate_cached_responses()
            
            # 3. Генерируем PDF файлы
            await self.generate_pdf_files()
            
            # 4. Показываем статистику
            self.show_statistics()
            
            logger.info("✅ Генерация демо-кеша завершена успешно!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка при генерации демо-кеша: {e}")
            return False
    
    async def save_test_data(self):
        """Сохраняет тестовые данные"""
        logger.info("💾 Сохраняем тестовые данные...")
        
        # Сохраняем профили резюме
        for level, resume_data in SAMPLE_RESUMES.items():
            self.demo_manager.save_resume_profile(level, resume_data)
            logger.info(f"  ✓ Сохранен профиль: {level}")
        
        # Сохраняем вакансию
        self.demo_manager.save_vacancy_data(SAMPLE_VACANCY)
        logger.info("  ✓ Сохранена тестовая вакансия")
    
    async def generate_cached_responses(self):
        """Генерирует кешированные ответы от LLM сервисов"""
        logger.info("🤖 Генерируем кешированные ответы LLM...")
        
        for level, resume_data in SAMPLE_RESUMES.items():
            logger.info(f"  🔄 Обрабатываем профиль: {level}")
            
            try:
                # Cover Letter
                logger.info("    📝 Генерируем сопроводительное письмо...")
                cover_letter = await self.cover_letter_generator.generate_enhanced_cover_letter(
                    resume_data, SAMPLE_VACANCY
                )
                if cover_letter:
                    self.demo_manager.save_response("cover_letter", level, cover_letter.model_dump())
                    logger.info(f"    ✓ Сохранено сопроводительное письмо для {level}")
                
                # Interview Checklist
                logger.info(f"    📋 Генерируем чек-лист...")
                checklist = await self.checklist_generator.generate_professional_interview_checklist(
                    resume_data, SAMPLE_VACANCY
                )
                if checklist:
                    self.demo_manager.save_response("interview_checklist", level, checklist.model_dump())
                    logger.info(f"    ✓ Сохранен чек-лист для {level}")
                
                # Interview Simulation
                logger.info("    🎭 Генерируем симуляцию интервью...")
                simulation = await self.simulation_generator.simulate_interview(
                    resume_data, SAMPLE_VACANCY
                )
                if simulation:
                    self.demo_manager.save_response("interview_simulation", level, simulation.model_dump())
                    logger.info(f"    ✓ Сохранена симуляция для {level}")
                
            except Exception as e:
                logger.error(f"    ❌ Ошибка при генерации для {level}: {e}")
                continue
    
    async def generate_pdf_files(self):
        """Генерирует PDF файлы"""
        logger.info("📄 Генерируем PDF файлы...")
        
        for level in ["junior", "middle", "senior"]:
            logger.info(f"  🔄 Генерируем PDF для {level}...")
            
            try:
                # Cover Letter PDF
                cover_letter_data = self.demo_manager.load_cached_response("cover_letter", level)
                if cover_letter_data:
                    from src.models.cover_letter_models import EnhancedCoverLetter
                    cover_letter = EnhancedCoverLetter.model_validate(cover_letter_data)
                    
                    pdf_generator = CoverLetterPDFGenerator()
                    pdf_buffer = pdf_generator.generate_pdf(cover_letter)
                    
                    pdf_path = self.demo_manager.generated_pdfs_dir / "cover_letter" / f"{level}_cover_letter.pdf"
                    with open(pdf_path, 'wb') as f:
                        f.write(pdf_buffer.getvalue())
                    logger.info(f"    ✓ Сохранен PDF сопроводительного письма: {pdf_path}")
                
                # Interview Checklist PDF
                checklist_data = self.demo_manager.load_cached_response("interview_checklist", level)
                if checklist_data:
                    from src.models.interview_checklist_models import ProfessionalInterviewChecklist
                    checklist = ProfessionalInterviewChecklist.model_validate(checklist_data)
                    
                    pdf_generator = InterviewChecklistPDFGenerator()
                    pdf_buffer = pdf_generator.generate_pdf(checklist)
                    
                    pdf_path = self.demo_manager.generated_pdfs_dir / "interview_checklist" / f"{level}_interview_checklist.pdf"
                    with open(pdf_path, 'wb') as f:
                        f.write(pdf_buffer.getvalue())
                    logger.info(f"    ✓ Сохранен PDF чек-листа: {pdf_path}")
                
                # Interview Simulation PDF
                simulation_data = self.demo_manager.load_cached_response("interview_simulation", level)
                if simulation_data:
                    from src.models.interview_simulation_models import InterviewSimulation
                    simulation = InterviewSimulation.model_validate(simulation_data)
                    
                    pdf_generator = ProfessionalInterviewPDFGenerator()
                    pdf_buffer = pdf_generator.generate_pdf(simulation)
                    
                    pdf_path = self.demo_manager.generated_pdfs_dir / "interview_simulation" / f"{level}_interview_simulation.pdf"
                    with open(pdf_path, 'wb') as f:
                        f.write(pdf_buffer.getvalue())
                    logger.info(f"    ✓ Сохранен PDF симуляции: {pdf_path}")
                
            except Exception as e:
                logger.error(f"    ❌ Ошибка при генерации PDF для {level}: {e}")
                continue
    
    def show_statistics(self):
        """Показывает статистику сгенерированного кеша"""
        logger.info("📊 Статистика демо-кеша:")
        
        stats = self.demo_manager.get_cache_stats()
        
        logger.info(f"  Режим: {'🎭 DEMO' if stats['demo_mode_active'] else '🌐 LIVE'}")
        logger.info(f"  Кешированных ответов: {stats['total_cached_responses']}")
        logger.info(f"  Заготовленных PDF: {stats['total_generated_pdfs']}")
        
        for service_type in ["cover_letter", "interview_checklist", "interview_simulation"]:
            cached = stats["cached_responses"][service_type]
            pdfs = stats["generated_pdfs"][service_type]
            logger.info(f"    {service_type}: {cached} ответов, {pdfs} PDF")

async def main():
    """Главная функция"""
    print("🎯 AI Resume Assistant - Demo Cache Generator")
    print("=" * 50)
    
    # Проверяем переменные окружения
    if os.getenv("DEMO_MODE", "false").lower() == "true":
        print("❌ Ошибка: Установите DEMO_MODE=false для генерации кеша")
        return
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Ошибка: Не установлена переменная OPENAI_API_KEY")
        return
    
    generator = DemoCacheGenerator()
    success = await generator.generate_all()
    
    if success:
        print("\n🎉 Демо-кеш готов! Теперь можно использовать DEMO_MODE=true")
        print("📋 Для активации демо-режима:")
        print("   export DEMO_MODE=true")
        print("   python run_unified_app.py")
    else:
        print("\n💥 Генерация не удалась. Проверьте логи.")

if __name__ == "__main__":
    asyncio.run(main())