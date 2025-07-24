# src/llm_interview_simulation/llm_interview_simulator.py
import logging
from typing import Optional, Dict, Any, List, Tuple, Callable, Awaitable
from openai import OpenAI
from pydantic import ValidationError

from src.llm_interview_simulation.config import settings
from src.models.interview_simulation_models import (
    InterviewSimulation, DialogMessage, CandidateLevel, ITRole, QuestionType,
    CompetencyArea, CandidateProfile, InterviewConfiguration, InterviewAssessment,
    CompetencyScore
)
from src.llm_interview_simulation.formatter import (
    format_resume_for_interview_simulation, 
    format_vacancy_for_interview_simulation,
    format_dialog_history,
    create_candidate_profile_and_config
)
from src.security.openai_control import openai_controller
from src.demo_cache.demo_manager import DemoManager

from src.utils import get_logger
logger = get_logger()

class ProfessionalInterviewSimulator:
    """Профессиональный симулятор интервью с адаптивными промптами и STAR-методикой"""
    
    def __init__(self):
        """Инициализация симулятора."""
        self.config = settings
        self.client = OpenAI(api_key=self.config.api_key)
        self.model = self.config.model_name
        self.custom_config = None  # Для хранения пользовательских настроек
        
        # Карта типов вопросов по раундам
        self.round_question_mapping = {
            1: [QuestionType.INTRODUCTION],
            2: [QuestionType.TECHNICAL_SKILLS, QuestionType.EXPERIENCE_DEEP_DIVE],
            3: [QuestionType.BEHAVIORAL_STAR, QuestionType.PROBLEM_SOLVING],
            4: [QuestionType.MOTIVATION, QuestionType.CULTURE_FIT],
            5: [QuestionType.FINAL],
            6: [QuestionType.LEADERSHIP],  # Для сеньоров
            7: [QuestionType.FINAL]        # Расширенное интервью
        }
    
    def set_custom_config(self, config: Dict[str, Any]):
        """Устанавливает пользовательские настройки симуляции."""
        self.custom_config = config
    
    def _select_question_type_for_round(self, round_number: int, candidate_profile: CandidateProfile,
                                      previous_types: List[QuestionType]) -> QuestionType:
        """Выбирает тип вопроса для текущего раунда."""
        
        # Получаем возможные типы для раунда
        possible_types = self.round_question_mapping.get(round_number, [QuestionType.FINAL])
        
        # Добавляем leadership вопросы для управленцев
        if (candidate_profile.management_experience and 
            candidate_profile.detected_level in [CandidateLevel.SENIOR, CandidateLevel.LEAD] and
            QuestionType.LEADERSHIP not in previous_types):
            possible_types.append(QuestionType.LEADERSHIP)
        
        # Убираем уже использованные типы
        available_types = [qt for qt in possible_types if qt not in previous_types]
        
        if not available_types:
            return QuestionType.FINAL
        
        # Выбираем первый доступный (можно добавить логику приоритизации)
        return available_types[0]
    
    def _create_adaptive_hr_prompt(self, resume_data: Dict[str, Any], vacancy_data: Dict[str, Any], 
                                 dialog_history: List[DialogMessage], round_number: int,
                                 candidate_profile: CandidateProfile, 
                                 interview_config: InterviewConfiguration) -> Tuple[str, QuestionType]:
        """Создает адаптивный промпт для HR-менеджера."""
        
        # Определяем тип вопроса для текущего раунда
        previous_types = [msg.question_type for msg in dialog_history if msg.speaker == "HR" and msg.question_type]
        question_type = self._select_question_type_for_round(round_number, candidate_profile, previous_types)
        
        formatted_resume = format_resume_for_interview_simulation(resume_data)
        formatted_vacancy = format_vacancy_for_interview_simulation(vacancy_data)
        formatted_history = format_dialog_history(dialog_history)
        
        # Базовая характеристика HR
        hr_persona = self._get_hr_persona(candidate_profile.detected_level)
        
        # Специфичные инструкции по типу вопроса
        question_instructions = self._get_question_type_instructions(question_type, candidate_profile)
        
        # Адаптация под уровень кандидата
        level_adaptation = self._get_level_specific_approach(candidate_profile.detected_level)
        
        # Технические детали для IT-роли
        role_specific_guidance = self._get_role_specific_guidance(candidate_profile.detected_role)
        
        prompt = f"""
# Роль: {hr_persona}

Ты — опытный HR-менеджер IT-компании с 10+ лет опыта. {level_adaptation}

## Контекст интервью:

{formatted_resume}

{formatted_vacancy}

{formatted_history}

## Текущая ситуация:
- Раунд интервью: {round_number} из {interview_config.target_rounds}
- Тип вопроса: {question_type.value}
- Профиль кандидата: {candidate_profile.detected_level.value} {candidate_profile.detected_role.value}

## Специфичные инструкции для этого раунда:

{question_instructions}

{role_specific_guidance}

## Профессиональные принципы интервьюирования:

1. **Структурированный подход**: Используй методику STAR для поведенческих вопросов
2. **Глубина vs. Деликатность**: Докапывайся до сути, но дружелюбно
3. **Конкретика**: Требуй примеры и детали, не принимай общие ответы
4. **Баланс**: Оценивай как hard skills, так и soft skills
5. **Уважение**: Поддерживай профессиональный, но теплый тон

## Требования к вопросу:
- ОДИН конкретный вопрос (2-3 предложения максимум)
- Соответствует уровню кандидата и типу раунда
- Позволяет глубоко оценить компетенцию
- Профессиональный, но дружелюбный тон
- На русском языке

{"Начни интервью с приветствия и первого вопроса." if round_number == 1 else "Задай следующий вопрос, основываясь на предыдущих ответах."}

Ответь только текстом вопроса.
"""
        
        return prompt, question_type
    
    def _get_hr_persona(self, level: CandidateLevel) -> str:
        """Возвращает персону HR в зависимости от уровня кандидата."""
        personas = {
            CandidateLevel.JUNIOR: "Поддерживающий наставник и строгий оценщик базовых навыков",
            CandidateLevel.MIDDLE: "Профессиональный эксперт, проверяющий глубину знаний",
            CandidateLevel.SENIOR: "Опытный лидер, оценивающий экспертизу и лидерский потенциал",
            CandidateLevel.LEAD: "Senior Partner, проводящий стратегическое интервью на равных"
        }
        return personas.get(level, "Профессиональный HR-специалист")
    
    def _get_question_type_instructions(self, question_type: QuestionType, 
                                      candidate_profile: CandidateProfile) -> str:
        """Возвращает инструкции для конкретного типа вопроса."""
        
        instructions = {
            QuestionType.INTRODUCTION: """
**ЗНАКОМСТВО И ВВЕДЕНИЕ**
- Поприветствуй кандидата тепло и профессионально
- Кратко представь себя и процесс интервью
- Задай открытый вопрос о кандидате или его мотивации
- Цель: снизить напряжение, оценить коммуникативные навыки
""",
            
            QuestionType.TECHNICAL_SKILLS: f"""
**ПРОВЕРКА ТЕХНИЧЕСКИХ НАВЫКОВ**
- Фокусируйся на ключевых технологиях для роли {candidate_profile.detected_role.value}
- Спрашивай о конкретном опыте, а не теоретических знаниях
- Проси примеры реального использования технологий
- Цель: оценить глубину и применимость технических знаний
""",
            
            QuestionType.EXPERIENCE_DEEP_DIVE: """
**ГЛУБОКИЙ АНАЛИЗ ОПЫТА**
- Выбери один значимый проект из резюме
- Используй воронку вопросов: контекст → задача → действия → результат
- Проверяй роль кандидата, его конкретный вклад
- Цель: понять реальный уровень и стиль работы
""",
            
            QuestionType.BEHAVIORAL_STAR: """
**ПОВЕДЕНЧЕСКИЕ ВОПРОСЫ (STAR)**
- Задавай ситуационные вопросы: "Расскажите о случае, когда..."
- Требуй структуры STAR: Ситуация → Задача → Действие → Результат
- Фокусируйся на сложных/конфликтных ситуациях
- Цель: оценить soft skills и стиль решения проблем
""",
            
            QuestionType.PROBLEM_SOLVING: """
**РЕШЕНИЕ ПРОБЛЕМ**
- Предложи гипотетическую рабочую ситуацию или кейс
- Попроси объяснить подход к решению пошагово
- Оценивай логику мышления, а не правильность ответа
- Цель: понять аналитические способности
""",
            
            QuestionType.MOTIVATION: """
**МОТИВАЦИЯ И ЦЕЛИ**
- Выясни причины смены работы и интерес к компании
- Спроси о долгосрочных планах развития
- Проверь знание о компании и позиции
- Цель: оценить искренность мотивации и культурное соответствие
""",
            
            QuestionType.CULTURE_FIT: """
**СООТВЕТСТВИЕ КУЛЬТУРЕ**
- Спроси о предпочитаемом стиле работы и команды
- Выясни ценности и принципы в работе
- Обсуди ожидания от рабочей среды
- Цель: определить культурное соответствие
""",
            
            QuestionType.LEADERSHIP: """
**ЛИДЕРСКИЕ КАЧЕСТВА**
- Спроси о опыте управления людьми/проектами
- Выясни стиль руководства и подход к конфликтам
- Проверь навыки развития команды
- Цель: оценить лидерский потенциал
""",
            
            QuestionType.FINAL: """
**ЗАВЕРШАЮЩИЕ ВОПРОСЫ**
- Предложи кандидату задать вопросы о компании/роли
- Уточни ожидания по зарплате и срокам выхода
- Поблагодари за интервью
- Цель: закрыть оставшиеся вопросы, показать уважение
"""
        }
        
        return instructions.get(question_type, "Задай релевантный вопрос по теме интервью.")
    
    def _get_level_specific_approach(self, level: CandidateLevel) -> str:
        """Возвращает подход, специфичный для уровня кандидата."""
        
        approaches = {
            CandidateLevel.JUNIOR: """
Помни: кандидат может нервничать. Будь поддерживающим, но не снижай планку.
Фокусируйся на потенциале, обучаемости и базовых навыках.
Приводи примеры и давай подсказки при необходимости.
""",
            
            CandidateLevel.MIDDLE: """
Ожидай уверенные ответы и конкретные примеры.
Проверяй глубину знаний и способность работать самостоятельно.
Оценивай готовность брать на себя больше ответственности.
""",
            
            CandidateLevel.SENIOR: """
Веди диалог как с экспертом. Задавай сложные вопросы.
Проверяй способность принимать архитектурные решения.
Оценивай потенциал менторства и технического лидерства.
""",
            
            CandidateLevel.LEAD: """
Общайся как с равным. Фокусируйся на стратегическом мышлении.
Проверяй опыт управления людьми и процессами.
Оценивай способность влиять на техническое направление компании.
"""
        }
        
        return approaches.get(level, "Адаптируй подход под уровень кандидата.")
    
    def _get_role_specific_guidance(self, role: ITRole) -> str:
        """Возвращает рекомендации, специфичные для IT-роли."""
        
        guidance = {
            ITRole.DEVELOPER: """
**Специфика для разработчиков:**
- Проверяй понимание архитектурных паттернов
- Спрашивай о code review, тестировании, CI/CD
- Интересуйся подходом к отладке и оптимизации
""",
            
            ITRole.DATA_SCIENTIST: """
**Специфика для Data Scientists:**
- Фокусируйся на понимании бизнес-задач через данные
- Проверяй знание ML pipeline и model validation
- Спрашивай о работе с большими данными и stakeholders
""",
            
            ITRole.QA: """
**Специфика для QA:**
- Проверяй понимание разных видов тестирования
- Спрашивай о построении тест-планов и автоматизации
- Интересуйся подходом к поиску и документированию багов
""",
            
            ITRole.DEVOPS: """
**Специфика для DevOps:**
- Фокусируйся на понимании инфраструктуры и мониторинга
- Проверяй опыт с containerization и orchestration
- Спрашивай о подходе к обеспечению надежности системы
""",
            
            ITRole.PROJECT_MANAGER: """
**Специфика для Project Managers:**
- Проверяй знание методологий (Agile, Scrum, Kanban)
- Спрашивай о управлении рисками и stakeholders
- Интересуйся подходом к планированию и контролю
"""
        }
        
        return guidance.get(role, "Учитывай специфику IT-роли в вопросах.")
    
    def _create_adaptive_candidate_prompt(self, resume_data: Dict[str, Any], vacancy_data: Dict[str, Any], 
                                        dialog_history: List[DialogMessage], hr_question: str,
                                        candidate_profile: CandidateProfile) -> str:
        """Создает адаптивный промпт для кандидата."""
        
        formatted_resume = format_resume_for_interview_simulation(resume_data)
        formatted_vacancy = format_vacancy_for_interview_simulation(vacancy_data)
        formatted_history = format_dialog_history(dialog_history[:-1])  # Исключаем последний вопрос HR
        
        # Определяем стиль ответа в зависимости от уровня
        response_style = self._get_candidate_response_style(candidate_profile.detected_level)
        
        prompt = f"""
# Роль: {candidate_profile.detected_level.value.title()} {candidate_profile.detected_role.value.replace('_', ' ').title()}

Ты — IT-специалист уровня {candidate_profile.detected_level.value}, который проходит интервью на позицию, 
описанную в вакансии. Ты хорошо подготовился и очень заинтересован в получении этой работы.

## Твоя информация (резюме):

{formatted_resume}

## Информация о целевой позиции:

{formatted_vacancy}

## История интервью:

{formatted_history}

## Текущий вопрос от HR-менеджера:

"{hr_question}"

## Твой стиль ответа:

{response_style}

## Принципы ответа:

1. **Основывайся на резюме**: Используй только информацию из своего профиля
2. **STAR для поведенческих вопросов**: Структурируй ответы как Ситуация → Задача → Действие → Результат  
3. **Конкретика**: Приводи числа, технологии, реальные примеры
4. **Честность**: Если не знаешь чего-то — признайся, но покажи готовность изучать
5. **Связь с вакансией**: Подчеркивай соответствие требованиям позиции
6. **Профессионализм**: Говори уверенно, но без высокомерия

## Требования к ответу:
- Отвечай только на заданный вопрос
- 3-5 предложений (2-3 для технических деталей)
- Профессиональная лексика соответствующего уровня
- На русском языке
- Не задавай встречных вопросов в этом ответе

Ответь только текстом ответа.
"""
        
        return prompt
    
    def _get_candidate_response_style(self, level: CandidateLevel) -> str:
        """Определяет стиль ответов в зависимости от уровня кандидата."""
        
        styles = {
            CandidateLevel.JUNIOR: """
- Показывай энтузиазм и готовность учиться
- Признавай ограничения опыта, но демонстрируй потенциал
- Приводи примеры из учебы, pet-проектов, стажировок
- Задавай уточняющие вопросы при сложных темах
""",
            
            CandidateLevel.MIDDLE: """
- Демонстрируй уверенность в своих навыках
- Приводи конкретные примеры из рабочих проектов
- Показывай понимание бизнес-контекста задач
- Упоминай опыт работы в команде и с разными технологиями
""",
            
            CandidateLevel.SENIOR: """
- Говори как эксперт в своей области
- Демонстрируй системное мышление и архитектурный подход
- Упоминай опыт принятия технических решений
- Показывай понимание влияния решений на бизнес
""",
            
            CandidateLevel.LEAD: """
- Общайся как технический лидер
- Фокусируйся на управлении людьми и процессами
- Демонстрируй стратегическое мышление
- Показывай опыт влияния на техническое направление
"""
        }
        
        return styles.get(level, "Отвечай профессионально и по существу.")
    
    async def _get_hr_question(self, resume_data: Dict[str, Any], vacancy_data: Dict[str, Any], 
                             dialog_history: List[DialogMessage], round_number: int,
                             candidate_profile: CandidateProfile, 
                             interview_config: InterviewConfiguration) -> Tuple[Optional[str], Optional[QuestionType]]:
        """Получает вопрос от HR-менеджера."""
        # Проверка разрешения использования OpenAI API
        openai_controller.check_api_permission()
        
        try:
            prompt, question_type = self._create_adaptive_hr_prompt(
                resume_data, vacancy_data, dialog_history, round_number,
                candidate_profile, interview_config
            )
            
            messages = [
                {
                    "role": "system",
                    "content": "Ты — профессиональный HR-менеджер, проводящий структурированное интервью с использованием лучших практик."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1500
            )
            
            # Записать статистику использования API
            tokens_used = completion.usage.total_tokens if completion.usage else 0
            openai_controller.record_request(success=True, tokens=tokens_used)
            
            return completion.choices[0].message.content.strip(), question_type
            
        except Exception as e:
            logger.error(f"Ошибка при получении вопроса HR: {e}")
            openai_controller.record_request(success=False, error=str(e))
            return None, None
    
    async def _get_candidate_answer(self, resume_data: Dict[str, Any], vacancy_data: Dict[str, Any], 
                                  dialog_history: List[DialogMessage], hr_question: str,
                                  candidate_profile: CandidateProfile) -> Optional[str]:
        """Получает ответ от кандидата."""
        # Проверка разрешения использования OpenAI API
        openai_controller.check_api_permission()
        
        try:
            prompt = self._create_adaptive_candidate_prompt(
                resume_data, vacancy_data, dialog_history, hr_question, candidate_profile
            )
            
            messages = [
                {
                    "role": "system", 
                    "content": f"Ты — {candidate_profile.detected_level.value} {candidate_profile.detected_role.value} на собеседовании. Отвечай профессионально, основываясь на своем резюме."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.8,
                max_tokens=4000
            )
            
            # Записать статистику использования API
            tokens_used = completion.usage.total_tokens if completion.usage else 0
            openai_controller.record_request(success=True, tokens=tokens_used)
            
            return completion.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Ошибка при получении ответа кандидата: {e}")
            openai_controller.record_request(success=False, error=str(e))
            return None
    
    def _evaluate_response_quality(self, answer: str, question_type: QuestionType, 
                                 candidate_profile: CandidateProfile) -> int:
        """Оценивает качество ответа кандидата от 1 до 5."""
        
        # Базовая оценка по длине и структуре
        score = 3  # средняя оценка
        
        if len(answer) < 50:  # Слишком короткий ответ
            score -= 1
        elif len(answer) > 300:  # Детальный ответ
            score += 1
        
        # Бонусы за конкретику
        if any(keyword in answer.lower() for keyword in ['например', 'конкретно', 'проект', 'результат']):
            score += 1
        
        # Проверка STAR структуры для поведенческих вопросов
        if question_type == QuestionType.BEHAVIORAL_STAR:
            star_keywords = ['ситуация', 'задача', 'действие', 'результат', 'проблема', 'решение']
            if sum(1 for kw in star_keywords if kw in answer.lower()) >= 3:
                score += 1
        
        return max(1, min(5, score))  # Ограничиваем 1-5
    
    async def _generate_comprehensive_assessment(self, resume_data: Dict[str, Any], 
                                               vacancy_data: Dict[str, Any], 
                                               dialog_messages: List[DialogMessage],
                                               candidate_profile: CandidateProfile) -> InterviewAssessment:
        """Генерирует всестороннюю оценку интервью с использованием продвинутого Assessment Engine."""
        
        # Импортируем Assessment Engine
        from src.llm_interview_simulation.assessment_engine import ProfessionalAssessmentEngine
        
        # Создаем экземпляр движка оценки
        assessment_engine = ProfessionalAssessmentEngine()
        
        # Генерируем детальную оценку
        assessment = await assessment_engine.generate_comprehensive_assessment(
            resume_data, vacancy_data, dialog_messages, candidate_profile
        )
        
        return assessment
    
    async def simulate_interview(self, parsed_resume: Dict[str, Any], 
                           parsed_vacancy: Dict[str, Any],
                           progress_callback: Optional[Callable[[int, int], Awaitable[None]]] = None,
                           config_overrides: Optional[Dict[str, Any]] = None) -> Optional[InterviewSimulation]:
        """
        Args:
        parsed_resume: Данные резюме
        parsed_vacancy: Данные вакансии
        progress_callback: Функция для обновления прогресса (current_round, total_rounds)
        """
        demo_manager = DemoManager()
        
        # Проверяем демо-режим
        if demo_manager.is_demo_mode():
            profile_level = demo_manager.detect_profile_level(parsed_resume)
            cached_response = demo_manager.load_cached_response("interview_simulation", profile_level)
            
            if cached_response:
                logger.info(f"🎭 Using cached interview simulation response for {profile_level} profile")
                try:
                    # Симулируем прогресс для демо
                    if progress_callback:
                        total_rounds = cached_response.get('configuration', {}).get('target_rounds', 5)
                        for round_num in range(1, total_rounds + 1):
                            await progress_callback(round_num, total_rounds)
                    
                    return InterviewSimulation.model_validate(cached_response)
                except ValidationError as ve:
                    logger.error(f"❌ Invalid cached response format: {ve}")
                    # Fallback to real generation if cache is corrupted
        
        # Продолжаем с реальной генерацией (живой режим или fallback)
        return await self._simulate_real_interview(parsed_resume, parsed_vacancy, progress_callback, config_overrides, demo_manager)
    
    async def _simulate_real_interview(self, parsed_resume: Dict[str, Any], 
                                     parsed_vacancy: Dict[str, Any],
                                     progress_callback: Optional[Callable[[int, int], Awaitable[None]]] = None,
                                     config_overrides: Optional[Dict[str, Any]] = None,
                                     demo_manager: DemoManager = None) -> Optional[InterviewSimulation]:
        """
        Выполняет реальную симуляцию интервью через OpenAI API
        
        Args:
        parsed_resume: Данные резюме
        parsed_vacancy: Данные вакансии
        progress_callback: Функция для обновления прогресса (current_round, total_rounds)
        demo_manager: Менеджер демо-режима для сохранения ответов
        """
        # Проверка разрешения использования OpenAI API
        openai_controller.check_api_permission()
        
        try:
            
            # Создаем профиль кандидата и конфигурацию
            candidate_profile, interview_config = create_candidate_profile_and_config(
                parsed_resume, parsed_vacancy
            )
            
            # Применяем пользовательские настройки, если они есть
            if self.custom_config:
                if 'target_rounds' in self.custom_config:
                    interview_config.target_rounds = self.custom_config['target_rounds']
                if 'difficulty_level' in self.custom_config:
                    # Преобразуем строку в CandidateLevel если нужно
                    from src.models.interview_simulation_models import CandidateLevel
                    level_mapping = {
                        'easy': CandidateLevel.JUNIOR,
                        'medium': CandidateLevel.MIDDLE, 
                        'hard': CandidateLevel.SENIOR
                    }
                    if self.custom_config['difficulty_level'] in level_mapping:
                        candidate_profile.detected_level = level_mapping[self.custom_config['difficulty_level']]
            
            logger.info(f"Создан профиль: {candidate_profile.detected_level.value} {candidate_profile.detected_role.value}")
            logger.info(f"Конфигурация: {interview_config.target_rounds} раундов")
            
            dialog_messages = []
            
            
            position_title = parsed_vacancy.get('name', 'IT позиция')
            candidate_name = f"{parsed_resume.get('first_name', '')} {parsed_resume.get('last_name', '')}".strip() or "Кандидат"
            
            # Проводим адаптивный диалог
            for round_num in range(1, interview_config.target_rounds + 1):
                logger.info(f"Начинаем раунд {round_num}/{interview_config.target_rounds}")
                
                # Отправляем обновление прогресса
                if progress_callback:
                    await progress_callback(round_num, interview_config.target_rounds)
                
                # HR задает адаптивный вопрос
                hr_question, question_type = await self._get_hr_question(
                    parsed_resume, parsed_vacancy, dialog_messages, round_num,
                    candidate_profile, interview_config
                )
                
                if not hr_question:
                    logger.error(f"Не удалось получить вопрос HR в раунде {round_num}")
                    break
                
                hr_message = DialogMessage(
                    speaker="HR",
                    message=hr_question,
                    round_number=round_num,
                    question_type=question_type
                )
                dialog_messages.append(hr_message)
                
                # Кандидат отвечает адаптивно
                candidate_answer = await self._get_candidate_answer(
                    parsed_resume, parsed_vacancy, dialog_messages, hr_question, candidate_profile
                )
                
                if not candidate_answer:
                    logger.error(f"Не удалось получить ответ кандидата в раунде {round_num}")
                    break
                
                # Оцениваем качество ответа
                response_quality = self._evaluate_response_quality(
                    candidate_answer, question_type, candidate_profile
                )
                
                candidate_message = DialogMessage(
                    speaker="Candidate", 
                    message=candidate_answer,
                    round_number=round_num,
                    response_quality=response_quality
                )
                dialog_messages.append(candidate_message)
                
                logger.info(f"Раунд {round_num} завершен (качество ответа: {response_quality}/5)")
                
            # Финальное обновление прогресса - завершение диалога
            if progress_callback:
                await progress_callback(interview_config.target_rounds, interview_config.target_rounds)
            
            # Генерируем всестороннюю оценку
            assessment = await self._generate_comprehensive_assessment(
                parsed_resume, parsed_vacancy, dialog_messages, candidate_profile
            )
            
            # Генерируем детальную обратную связь с помощью Assessment Engine
            from src.llm_interview_simulation.assessment_engine import ProfessionalAssessmentEngine
            assessment_engine = ProfessionalAssessmentEngine()
            feedback = await assessment_engine.generate_detailed_feedback(assessment, candidate_profile)
            
            # Извлекаем текстовые рекомендации
            hr_assessment = feedback.get('hr_assessment', 'Оценка не доступна')
            performance_analysis = feedback.get('performance_analysis', 'Анализ не доступен')
            improvement_recommendations = feedback.get('improvement_recommendations', 'Рекомендации не доступны')
            
            # Создаем объект симуляции
            simulation = InterviewSimulation(
                position_title=position_title,
                candidate_name=candidate_name,
                company_context=f"Интервью на позицию {position_title} в компании {parsed_vacancy.get('employer', {}).get('name', 'Компания')}",
                candidate_profile=candidate_profile,
                interview_config=interview_config,
                dialog_messages=dialog_messages,
                assessment=assessment,
                hr_assessment=hr_assessment,
                candidate_performance_analysis=performance_analysis,
                improvement_recommendations=improvement_recommendations,
                simulation_metadata={
                    'rounds_completed': len(dialog_messages) // 2,
                    'total_rounds_planned': interview_config.target_rounds,
                    'model_used': self.model,
                    'candidate_level': candidate_profile.detected_level.value,
                    'candidate_role': candidate_profile.detected_role.value
                }
            )
            
            # Сохраняем результат для демо-режима (если активен)
            if demo_manager and demo_manager.is_demo_mode():
                try:
                    profile_level = demo_manager.detect_profile_level(parsed_resume)
                    demo_manager.save_response("interview_simulation", profile_level, simulation.model_dump())
                    logger.info(f"💾 Saved interview simulation response for demo cache: {profile_level}")
                except Exception as save_error:
                    logger.warning(f"⚠️ Failed to save response to demo cache: {save_error}")
            
            logger.info("Профессиональная симуляция интервью успешно завершена")
            return simulation
            
        except Exception as e:
            logger.error(f"Ошибка при симуляции интервью: {e}")
            openai_controller.record_request(success=False, error=str(e))
            return None

# Для обратной совместимости
LLMInterviewSimulator = ProfessionalInterviewSimulator