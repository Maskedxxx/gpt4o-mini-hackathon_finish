# src/llm_interview_checklist/llm_interview_checklist_generator.py
import logging
from typing import Optional, Dict, Any
from openai import OpenAI
from pydantic import ValidationError

from src.llm_interview_checklist.config import settings
from src.models.interview_checklist_models import InterviewChecklist, ProfessionalInterviewChecklist
from src.llm_interview_checklist.formatter import format_resume_for_interview_prep, format_vacancy_for_interview_prep

from src.utils import get_logger
logger = get_logger()

class LLMInterviewChecklistGenerator:
    """Сервис для создания персонализированного чек-листа подготовки к интервью с помощью OpenAI API"""
    
    def __init__(self):
        """Инициализация клиента OpenAI."""
        self.config = settings
        self.client = OpenAI(api_key=self.config.api_key)
        self.model = self.config.model_name
    
    def _analyze_candidate_profile(self, parsed_resume: Dict[str, Any], parsed_vacancy: Dict[str, Any]) -> Dict[str, str]:
        """Анализирует профиль кандидата для определения контекста персонализации."""
        
        # Определение уровня кандидата по опыту
        experience_list = parsed_resume.get('experience', [])
        total_experience_years = len(experience_list)  # Упрощенная оценка
        
        candidate_level = "JUNIOR"
        if total_experience_years >= 6:
            candidate_level = "SENIOR"
        elif total_experience_years >= 3:
            candidate_level = "MIDDLE"
        
        # Определение типа вакансии
        vacancy_description = parsed_vacancy.get('description', '').lower()
        position_title = parsed_resume.get('title', '').lower()
        
        vacancy_type = "OTHER"
        if any(word in vacancy_description + position_title for word in ['разработчик', 'developer', 'программист', 'frontend', 'backend']):
            vacancy_type = "DEVELOPER"
        elif any(word in vacancy_description + position_title for word in ['тестировщик', 'qa', 'quality']):
            vacancy_type = "QA_ENGINEER"
        elif any(word in vacancy_description + position_title for word in ['данн', 'data', 'analyst', 'scientist']):
            vacancy_type = "DATA_SPECIALIST"
        elif any(word in vacancy_description + position_title for word in ['аналитик', 'analyst', 'бизнес']):
            vacancy_type = "BUSINESS_ANALYST"
        elif any(word in vacancy_description + position_title for word in ['дизайн', 'design', 'ux', 'ui']):
            vacancy_type = "DESIGNER"
        elif any(word in vacancy_description + position_title for word in ['devops', 'sre', 'администратор']):
            vacancy_type = "DEVOPS"
        elif any(word in vacancy_description + position_title for word in ['менеджер', 'manager', 'lead', 'руководитель']):
            vacancy_type = "MANAGER"
        
        # Определение формата компании
        company_format = "MEDIUM_COMPANY"  # default
        if any(word in vacancy_description for word in ['стартап', 'startup']):
            company_format = "STARTUP"
        elif any(word in vacancy_description for word in ['корпорация', 'enterprise', 'международн']):
            company_format = "LARGE_CORP"
        elif any(word in vacancy_description for word in ['international', 'global']):
            company_format = "INTERNATIONAL"
        
        return {
            'candidate_level': candidate_level,
            'vacancy_type': vacancy_type,
            'company_format': company_format
        }
    
    def _create_professional_interview_checklist_prompt(self, parsed_resume: Dict[str, Any], parsed_vacancy: Dict[str, Any]) -> str:
        """
        Создает профессиональный промпт на основе методологии HR-экспертов.
        """
        formatted_resume = format_resume_for_interview_prep(parsed_resume)
        formatted_vacancy = format_vacancy_for_interview_prep(parsed_vacancy)
        profile_context = self._analyze_candidate_profile(parsed_resume, parsed_vacancy)
        
        return f"""
        # РОЛЬ: Ты — ведущий HR-эксперт с 10+ летним опытом подготовки IT-кандидатов к интервью

        ## ЭКСПЕРТНАЯ КВАЛИФИКАЦИЯ
        - Специализация: составление персонализированных чек-листов подготовки к IT-интервью
        - Опыт: успешная подготовка 1000+ кандидатов разных уровней
        - Методология: следуешь лучшим практикам HR-индустрии и современным трендам
        - Подход: индивидуальная адаптация под каждого кандидата и вакансию

        ## ИСХОДНЫЕ ДАННЫЕ ДЛЯ АНАЛИЗА

        ### ПРОФИЛЬ КАНДИДАТА:
        <resume_start>
        {formatted_resume}
        </resume_end>

        ### ЦЕЛЕВАЯ ВАКАНСИЯ:
        <vacancy_start>
        {formatted_vacancy}
        </vacancy_end>

        ### ПРЕДВАРИТЕЛЬНЫЙ АНАЛИЗ:
        - Определенный уровень кандидата: {profile_context['candidate_level']}
        - Тип вакансии: {profile_context['vacancy_type']}
        - Формат компании: {profile_context['company_format']}

        ## МЕТОДОЛОГИЯ СОЗДАНИЯ ПРОФЕССИОНАЛЬНОГО ЧЕК-ЛИСТА

        ### ЭТАП 1: ПЕРСОНАЛИЗАЦИЯ И СООТВЕТСТВИЕ
        Создай чек-лист ИНДИВИДУАЛЬНО под этого кандидата и конкретную позицию:

        1. **Анализ GAP'ов**: выдели требуемые навыки vs имеющиеся у кандидата
        2. **Учет уровня**: адаптируй сложность под {profile_context['candidate_level']} уровень
        3. **Фокус на пробелах**: приоритизируй areas where candidate needs improvement
        4. **Leveraging strengths**: используй сильные стороны кандидата как преимущества

        ### ЭТАП 2: АДАПТАЦИЯ ПОД ТИП РОЛИ

        **Для {profile_context['vacancy_type']}:**
        - **DEVELOPER**: технический стек, алгоритмы, код-ревью, архитектурные паттерны
        - **QA_ENGINEER**: методологии тестирования, инструменты, критические баги, процессы QA
        - **DATA_SPECIALIST**: статистика, ML-алгоритмы, визуализация данных, бизнес-метрики
        - **BUSINESS_ANALYST**: требования, процессы, домен знания, коммуникация с бизнесом
        - **DESIGNER**: UX-метрики, портфолио, пользовательские исследования, design thinking
        - **DEVOPS**: автоматизация, надежность, мониторинг, infrastructure as code
        - **MANAGER**: лидерство, планирование, команда, процессы управления

        ### ЭТАП 3: АДАПТАЦИЯ ПОД ФОРМАТ КОМПАНИИ

        **Для {profile_context['company_format']}:**
        - **STARTUP**: гибкость, многозадачность, готовность к изменениям, ownership
        - **MEDIUM_COMPANY**: баланс процессов и гибкости, teamwork
        - **LARGE_CORP**: корпоративная культура, процессы, compliance, масштабируемость  
        - **INTERNATIONAL**: кросс-культурная коммуникация, английский, remote work

        ## 7 ОБЯЗАТЕЛЬНЫХ БЛОКОВ ПРОФЕССИОНАЛЬНОГО ЧЕК-ЛИСТА

        ### БЛОК 1: ТЕХНИЧЕСКАЯ ПОДГОТОВКА
        Включи 5 категорий:

        **1.1 Профильные знания** (повторение core knowledge)
        - Определи ключевые темы без которых не обойтись на данной позиции
        - Адаптируй под уровень: junior - основы, senior - углубленные вопросы
        - Укажи конкретные источники для повторения

        **1.2 Недостающие технологии** (gap filling)
        - Выяви технологии из вакансии, которых мало/нет в резюме
        - Составь план изучения основ (не стать экспертом, а понимать о чем речь)

        **1.3 Практические задачи** (hands-on preparation)
        - Подбери типичные задачи для данной роли и уровня
        - Конкретные платформы: LeetCode, HackerRank, Codewars и др.
        - Примеры задач с разбором решений

        **1.4 Проекты и код кандидата** (portfolio preparation)
        - Анализ имеющихся проектов в резюме
        - Подготовка к обсуждению: технические решения, архитектура, challenges

        **1.5 Дополнительные материалы** (advanced topics)
        - Специфичные для роли: паттерны, методологии, best practices
        - Актуальные тренды в области

        ### БЛОК 2: ПОВЕДЕНЧЕСКАЯ ПОДГОТОВКА (SOFT SKILLS)
        Включи 4 категории:

        **2.1 Типовые вопросы о кандидате**
        - "Расскажите о себе", сильные/слабые стороны, motivation
        - Подготовка STAR-историй для демонстрации качеств
        - Примеры вопросов и структура ответов

        **2.2 Тренировка самопрезентации**
        - 2-3 минутный pitch about experience
        - Презентация ключевого проекта
        - Практика: проговорить вслух, записать на видео

        **2.3 Поведенческое интервью**
        - Работа в команде, конфликты, leadership, неудачи, стресс
        - STAR method examples для каждой компетенции
        - Адаптация под культуру компании

        **2.4 Storytelling и позитивный настрой**
        - Фокус на достижения и вклад
        - Избегание негатива про предыдущих работодателей
        - Демонстрация growth mindset

        ### БЛОК 3: ИЗУЧЕНИЕ КОМПАНИИ И ПРОДУКТА
        Включи 3 категории:

        **3.1 Исследование компании**
        - Сайт, новости, пресс-релизы, ценности, миссия
        - LinkedIn профили команды и интервьюеров
        - История и достижения компании

        **3.2 Продукты и отрасль**
        - Изучение флагманского продукта, установка demo
        - Понимание бизнес-модели и target audience
        - Анализ конкурентов и позиционирования

        **3.3 Вопросы для работодателя**
        - 3-5 умных вопросов показывающих интерес и экспертизу
        - Избегание вопросов с очевидными ответами с сайта
        - Фокус на будущем развитии и возможностях

        ### БЛОК 4: ИЗУЧЕНИЕ ТЕХНИЧЕСКОГО СТЕКА И ПРОЦЕССОВ
        Включи 4 категории:

        **4.1 Разбор требований вакансии**
        - Детальный анализ JD, выписать все технологии
        - Сопоставление с experience кандидата
        - Приоритизация областей для изучения

        **4.2 Технологии компании**
        - Используемый stack (из вакансии, открытых источников)
        - Изучение основ незнакомых технологий
        - Подготовка к вопросам про architectural choices

        **4.3 Рабочие процессы и методологии**
        - Code review, CI/CD, testing practices
        - Agile/Scrum/Kanban processes
        - Development lifecycle в компании

        **4.4 Терминология и жаргон**
        - Специфичные термины из вакансии
        - Industry-specific vocabulary
        - Понимание acronyms и technical concepts

        ### БЛОК 5: ПРАКТИЧЕСКИЕ УПРАЖНЕНИЯ И КЕЙСЫ
        Включи 5 категорий:

        **5.1 Тренировочные задачи**
        - Конкретные задачи под уровень и специализацию
        - Платформы и ресурсы для практики
        - Daily practice routine до интервью

        **5.2 Кейсы из опыта**
        - 2-3 prepared stories демонстрирующих разные skills
        - STAR format для структурирования
        - Practice delivery: четкость, краткость, impact

        **5.3 Мок-интервью**
        - Симуляция с коллегой или другом
        - Запись на камеру для self-review
        - Feedback и iteration on answers

        **5.4 Тестовые задания**
        - Если известно о home assignment - подготовка environment
        - Review типичных тестовых заданий для роли
        - Time management и presentation подготовка

        **5.5 Портфолио и демо-материалы**
        - Ревизия проектов в GitHub/портфолио
        - Подготовка live demo (если применимо)
        - README и documentation update

        ### БЛОК 6: НАСТРОЙКА ОКРУЖЕНИЯ ДЛЯ ИНТЕРВЬЮ
        Включи 5 категорий:

        **6.1 Оборудование и связь**
        - Тестирование камеры, микрофона, интернета
        - Backup план при technical issues
        - Platform setup (Zoom, Teams, etc.)

        **6.2 Место проведения**
        - Quiet, professional environment
        - Lighting и background setup
        - Notifications отключение

        **6.3 Аккаунты и доступы**
        - Platform registration и testing
        - Contact information для emergency
        - Link testing и preparation

        **6.4 Резервные варианты**
        - Backup internet connection (mobile hotspot)
        - Alternative contact methods
        - Plan B при force majeure

        **6.5 Внешний вид и окружение**
        - Professional attire appropriate для company culture
        - Clean, organized space in camera view
        - Professional демeanor preparation

        ### БЛОК 7: ДОПОЛНИТЕЛЬНЫЕ ДЕЙСТВИЯ КАНДИДАТА
        Включи 5 категорий:

        **7.1 Рекомендации**
        - Подготовка списка references
        - Получение согласия на рекомендации
        - Briefing рекомендателей о позиции

        **7.2 Профили и онлайн-присутствие**
        - LinkedIn, GitHub, portfolio consistency check
        - Removal/hiding неподходящего content
        - Professional online image curation

        **7.3 Документы и сертификаты**
        - Copies сертификатов и дипломов
        - Updated resume final version
        - Portfolio/work samples preparation

        **7.4 Резюме и сопроводительное письмо**
        - Final resume review и customization
        - Cover letter адаптация (если требуется)
        - Consistency across materials

        **7.5 Настрой и отдых**
        - Mental preparation и confidence building
        - Rest и proper nutrition before interview
        - Stress management techniques

        ## КРИТЕРИИ КАЧЕСТВЕННОГО ЧЕК-ЛИСТА

        ✅ **Персонализация**: каждый пункт adapted под кандидата и вакансию
        ✅ **Конкретность**: четкие действия, ресурсы, временные рамки
        ✅ **Приоритизация**: критично/важно/желательно
        ✅ **Реалистичность**: выполнимо в имеющееся время
        ✅ **Полнота**: покрывает все аспекты подготовки
        ✅ **Actionable**: clear next steps для кандидата

        ## ИНСТРУКЦИИ ПО РЕЗУЛЬТАТУ

        1. **Анализируй контекст**: учитывай специфику кандидата, вакансии, компании
        2. **Персонализируй полностью**: никаких generic советов
        3. **Детализируй конкретно**: что, где, как, сколько времени
        4. **Приоритизируй разумно**: от critical к nice-to-have
        5. **Структурируй четко**: соблюдай все 7 блоков
        6. **Мотивируй кандидата**: positive tone, confidence building

        Создай professional interview checklist в формате JSON согласно модели ProfessionalInterviewChecklist.
        Пиши на русском языке. Будь максимально конкретным и практичным.
        """
    
    def _create_interview_checklist_prompt(self, parsed_resume: Dict[str, Any], parsed_vacancy: Dict[str, Any]) -> str:
        """
        Создает промпт для генерации чек-листа подготовки к интервью (старая версия для совместимости).
        """
        formatted_resume = format_resume_for_interview_prep(parsed_resume)
        formatted_vacancy = format_vacancy_for_interview_prep(parsed_vacancy)
        
        return f"""
        # Задача: Создание персонализированного чек-листа для подготовки к интервью
        
        Твоя задача - создать исчерпывающий, детальный чек-лист подготовки к интервью для IT-специалиста на основе анализа его текущих компетенций и требований целевой вакансии.
        
        ## Исходные данные
        <Данные резюме>
        {formatted_resume}
        </Данные резюме>
        ============
        <Данные вакансии>
        {formatted_vacancy}
        </Данные вакансии>
        
        ## Требования к чек-листу
        
        1. **Персонализация**: Учитывай текущий уровень кандидата и конкретные требования вакансии
        2. **Детальность**: Для каждого навыка указывай ЧТО именно изучать, ГДЕ изучать, СКОЛЬКО времени потратить
        3. **Практичность**: Включай конкретные задачи, примеры вопросов, ссылки на ресурсы
        4. **Приоритизация**: Разделяй по важности (высокий/средний/низкий приоритет)
        5. **Реалистичность**: Учитывай ограниченное время на подготовку
        6. **Структурированность**: Четкое разделение на категории подготовки
        
        ## Категории для анализа и рекомендаций
        
        ### Технические навыки
        - Проанализируй каждый требуемый навык из вакансии
        - Оцени текущий уровень кандидата по этому навыку
        - Предложи конкретный план изучения с ресурсами
        - Укажи приоритет изучения
        
        ### Теоретические знания
        - Основы компьютерных наук, алгоритмы, структуры данных
        - Специфические знания для данной области (веб-разработка, мобильная разработка, DevOps и т.д.)
        - Принципы проектирования, архитектурные паттерны
        
        ### Практические задачи
        - Типичные задачи на собеседованиях для данной позиции
        - Кодинг-задачи, системный дизайн, код-ревью
        - Конкретные примеры и ресурсы для практики
        
        ### Поведенческие вопросы
        - Типичные HR-вопросы для IT-сферы
        - Вопросы о работе в команде, решении конфликтов
        - Методики ответов (STAR-метод)
        
        ## Конкретные требования к ресурсам
        
        Для каждого ресурса указывай:
        - Конкретные названия книг, курсов, платформ
        - Примерное время изучения
        - Что именно изучить из этого ресурса
        - Приоритет ресурса
        
        Примеры качественных ресурсов:
        - Книги: "Cracking the Coding Interview", "System Design Interview"
        - Платформы: LeetCode, HackerRank, Codewars
        - Курсы: Coursera, Udemy, YouTube каналы
        - Документация: официальная документация технологий
        - Практика: GitHub проекты, хакатоны
        
        ## Формат ответа
        
        Верни ответ строго в формате JSON, соответствующий структуре Pydantic модели InterviewChecklist.
        
        ВАЖНО:
        - Пиши на русском языке
        - Будь максимально конкретным в рекомендациях
        - Для каждой категории создавай не менее 3-5 элементов
        - Указывай реалистичные временные рамки
        - Включай как бесплатные, так и платные ресурсы
        - Адаптируй сложность под уровень кандидата
        """
    
    async def generate_professional_interview_checklist(self, parsed_resume: Dict[str, Any], parsed_vacancy: Dict[str, Any]) -> Optional[ProfessionalInterviewChecklist]:
        """
        Генерирует профессиональный чек-лист подготовки к интервью на основе HR-экспертизы.
        
        Args:
            parsed_resume: Словарь с распарсенными данными резюме
            parsed_vacancy: Словарь с распарсенными данными вакансии
        
        Returns:
            ProfessionalInterviewChecklist: Объект с профессиональным чек-листом подготовки или None в случае ошибки
        """
        try:
            # 1. Формируем профессиональный промпт
            prompt_text = self._create_professional_interview_checklist_prompt(parsed_resume, parsed_vacancy)
            
            # 2. Подготавливаем сообщения для chat-completion
            messages = [
                {
                    "role": "system",
                    "content": (
                        "Ты — ведущий HR-эксперт по подготовке IT-кандидатов к интервью с 10+ летним опытом. "
                        "Специализируешься на создании персонализированных, детальных чек-листов, которые "
                        "реально помогают кандидатам успешно пройти собеседование и получить работу. "
                        "Следуешь проверенной методологии и лучшим практикам HR-индустрии. "
                        "Всегда пишешь на русском языке и даешь конкретные, практичные советы. "
                        "Ответ всегда в формате JSON согласно указанной структуре ProfessionalInterviewChecklist."
                    )
                },
                {
                    "role": "user",
                    "content": prompt_text
                }
            ]
            
            # 3. Вызов OpenAI API
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=messages,
                response_format=ProfessionalInterviewChecklist,
                temperature=0.3  # Более консервативный подход для professional контента
            )
            
            # 4. Извлекаем ответ
            raw_response_text = completion.choices[0].message.content
            if not raw_response_text:
                logger.error("Пустой ответ от модели при генерации профессионального чек-листа интервью.")
                return None
            
            # 5. Парсим JSON в модель ProfessionalInterviewChecklist
            professional_checklist = ProfessionalInterviewChecklist.model_validate_json(raw_response_text)
            logger.info("Профессиональный чек-лист подготовки к интервью успешно сгенерирован.")
            return professional_checklist
            
        except ValidationError as ve:
            logger.error(f"Ошибка валидации профессионального чек-листа интервью: {ve}")
            return None
        except Exception as e:
            logger.error(f"Ошибка при генерации профессионального чек-листа интервью: {e}")
            return None
    
    async def generate_interview_checklist(self, parsed_resume: Dict[str, Any], parsed_vacancy: Dict[str, Any]) -> Optional[InterviewChecklist]:
        """
        Генерирует персонализированный чек-лист подготовки к интервью (старая версия для совместимости).
        """
        try:
            # 1. Формируем промпт
            prompt_text = self._create_interview_checklist_prompt(parsed_resume, parsed_vacancy)
            
            # 2. Подготавливаем сообщения для chat-completion
            messages = [
                {
                    "role": "system",
                    "content": (
                        "Ты — эксперт по подготовке IT-специалистов к собеседованиям с многолетним опытом в "
                        "рекрутинге и обучении. Ты знаешь все актуальные тренды в IT-интервью, лучшие ресурсы "
                        "для изучения и эффективные методики подготовки. Твоя специализация — создание "
                        "персонализированных, детальных планов подготовки, которые реально помогают кандидатам "
                        "получить работу. Всегда пишешь на русском языке и даешь конкретные, практичные советы. "
                        "Ответ всегда в формате JSON согласно указанной структуре InterviewChecklist."
                    )
                },
                {
                    "role": "user",
                    "content": prompt_text
                }
            ]
            
            # 3. Вызов OpenAI API
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=messages,
                response_format=InterviewChecklist
            )
            
            # 4. Извлекаем ответ
            raw_response_text = completion.choices[0].message.content
            if not raw_response_text:
                logger.error("Пустой ответ от модели при генерации чек-листа интервью.")
                return None
            
            # 5. Парсим JSON в модель InterviewChecklist
            interview_checklist = InterviewChecklist.model_validate_json(raw_response_text)
            logger.info("Чек-лист подготовки к интервью успешно сгенерирован.")
            return interview_checklist
            
        except ValidationError as ve:
            logger.error(f"Ошибка валидации чек-листа интервью: {ve}")
            return None
        except Exception as e:
            logger.error(f"Ошибка при генерации чек-листа интервью: {e}")
            return None