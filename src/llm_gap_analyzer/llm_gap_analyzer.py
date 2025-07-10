# src/llm_gap_analyzer/llm_gap_analyzer.py
import os
from typing import Optional, Dict, Any
from openai import OpenAI
from pydantic import ValidationError
import instructor

# ДОБАВИТЬ импорты LangSmith
from langsmith.wrappers import wrap_openai
from langsmith import traceable, Client

from src.utils import get_logger
from src.llm_gap_analyzer import settings
from src.models.gap_analysis_models import EnhancedResumeTailoringAnalysis
from src.llm_gap_analyzer.formatter import format_resume_data, format_vacancy_data
from src.security.openai_control import openai_controller

logger = get_logger()

# LangSmith клиент (без изменений)
def create_langsmith_client():
    """Создаёт клиента LangSmith для трейсинга."""
    api_key = os.getenv("LANGCHAIN_API_KEY")
    if not api_key:
        logger.warning("LANGCHAIN_API_KEY не установлен, трейсинг будет отключен")
        return None
    return Client(api_key=api_key)

ls_client = create_langsmith_client()


class LLMGapAnalyzer:
    """Сервис для анализа резюме с помощью OpenAI API"""
    
    def __init__(self):
        """Инициализация клиента OpenAI с LangSmith трейсингом."""
        self.config = settings
        self.model = self.config.model_name
        self.client = self._create_traced_client()
        logger.info(f"Инициализирован GAP анализатор с моделью {self.model}")
    
    def _create_traced_client(self) -> OpenAI:
        """Создает OpenAI клиент с LangSmith трейсингом."""
        base_client = OpenAI(api_key=self.config.api_key)
        
        if ls_client:
            logger.info("LangSmith трейсинг активирован для GAP анализа")
            wrapped_client = wrap_openai(base_client)
            return wrapped_client
        else:
            logger.info("LangSmith трейсинг недоступен, используется базовый клиент")
            return base_client
    
    def _create_system_prompt(self) -> str:
        """ОБНОВЛЕННЫЙ системный промпт с синхронизированной терминологией."""
        return """# РОЛЬ: Ты — эксперт HR с 10+ летним опытом GAP-анализа резюме в IT-сфере

## КОНТЕКСТ ЗАДАЧИ
Ты проводишь профессиональный GAP-анализ резюме кандидата относительно конкретной вакансии. 
Твоя задача — имитировать реальный процесс оценки, который используют опытные рекрутеры.

## МЕТОДОЛОГИЯ АНАЛИЗА (следуй строго по этапам)

### ЭТАП 1: ПЕРВИЧНЫЙ СКРИНИНГ (7-15 секунд) → PrimaryScreeningResult
Проанализируй базовые критерии, которые HR проверяет в первые секунды:
- Соответствие должности в резюме и вакансии → job_title_match
- Общий стаж в нужной сфере vs требуемый → experience_years_match  
- Наличие критичных навыков (видны ли ключевые слова) → key_skills_visible
- Локация и готовность к работе → location_suitable
- Зарплатные ожидания vs бюджет вакансии → salary_expectations_match

### ЭТАП 2: КЛАССИФИКАЦИЯ ТРЕБОВАНИЙ → RequirementAnalysis.requirement_type
⚠️ ВАЖНО: Используй ТОЧНУЮ терминологию для requirement_type:
- **MUST_HAVE** - без этого работа невозможна
- **NICE_TO_HAVE** - желательно, но можно развить  
- **ADDITIONAL_BONUS** - конкурентные преимущества (дополнительные плюсы)

### ЭТАП 3: ДЕТАЛЬНЫЙ АНАЛИЗ СООТВЕТСТВИЯ → RequirementAnalysis.compliance_status
Для каждого требования определи ТОЧНЫЙ статус:
- **FULL_MATCH** (✅ ПОЛНОЕ СООТВЕТСТВИЕ) - требование выполнено
- **PARTIAL_MATCH** (⚠️ ЧАСТИЧНОЕ СООТВЕТСТВИЕ) - есть упоминание, но недостаточно глубоко
- **MISSING** (❌ ОТСУТСТВУЕТ) - требование не отражено в резюме
- **UNCLEAR** (🔍 ТРЕБУЕТ УТОЧНЕНИЯ) - неясно из резюме

### ЭТАП 4: АНАЛИЗ КАЧЕСТВА ПРЕЗЕНТАЦИИ → ResumeQualityAssessment
Оцени КАК кандидат подает информацию:
- Структурированность и читабельность → structure_clarity (1-10)
- Релевантность описанного опыта → content_relevance (1-10)
- Наличие конкретных достижений vs общие обязанности → achievement_focus (1-10)
- Адаптация под вакансию → adaptation_quality (1-10)

## КРИТЕРИИ КАЧЕСТВЕННОГО АНАЛИЗА

### Hard Skills → skill_category: "HARD_SKILLS":
- Проверь ТОЧНОЕ совпадение названий технологий (Django vs "веб-фреймворки")
- Оцени глубину опыта по описанию проектов
- Сопоставь уровень задач в резюме с уровнем вакансии

### Soft Skills → skill_category: "SOFT_SKILLS":
- Ищи подтверждения через факты, а не декларации
- Анализируй качество самого резюме как показатель навыков
- Оценивай соответствие манеры изложения культуре компании

### Опыт → skill_category: "EXPERIENCE":
- Релевантность сферы и задач
- Карьерная траектория (рост, стагнация, скачки)
- Масштаб проектов и ответственности

### Образование → skill_category: "EDUCATION":
- Соответствие специальности требованиям вакансии
- Актуальность и релевантность дополнительного образования
- Непрерывное обучение и развитие навыков

## ФОРМАТ РЕКОМЕНДАЦИЙ → DetailedRecommendation
⚠️ ВАЖНО: Точная связь criticality с группировкой:
- **CRITICAL** → попадет в critical_recommendations
- **IMPORTANT** → попадет в important_recommendations  
- **DESIRED** → попадет в optional_recommendations

Для каждой рекомендации указывай:
1. **Критичность**: CRITICAL / IMPORTANT / DESIRED
2. **Обоснование**: почему это важно для данной вакансии → business_rationale
3. **Конкретные действия**: что именно добавить/изменить/убрать → specific_actions
4. **Примеры формулировок**: как лучше написать → example_wording

## ДОПОЛНИТЕЛЬНЫЕ ТРЕБОВАНИЯ
- Используй профессиональную терминологию HR
- Учитывай специфику российского IT-рынка
- Давай actionable советы, а не общие рекомендации
- Приоритизируй рекомендации по влиянию на решение о приглашении

Проведи анализ и верни результат в формате JSON согласно модели EnhancedResumeTailoringAnalysis."""
    
    def _create_user_prompt(self, parsed_resume: Dict[str, Any], parsed_vacancy: Dict[str, Any]) -> str:
        """ОБНОВЛЕННЫЙ пользовательский промпт с уточненными инструкциями."""
        formatted_resume = format_resume_data(parsed_resume)
        formatted_vacancy = format_vacancy_data(parsed_vacancy)
        
        return f"""<resume_data>
{formatted_resume}
</resume_data>

<vacancy_data>
{formatted_vacancy}
</vacancy_data>

## ИНСТРУКЦИЯ ДЛЯ GAP-АНАЛИЗА

Проведи профессиональный GAP-анализ по следующим этапам:

1. **ПЕРВИЧНЫЙ СКРИНИНГ** (7-15 секунд) → заполни PrimaryScreeningResult
2. **КЛАССИФИКАЦИЯ ТРЕБОВАНИЙ** → для каждого requirement_type используй: MUST_HAVE / NICE_TO_HAVE / ADDITIONAL_BONUS
3. **ДЕТАЛЬНЫЙ АНАЛИЗ СООТВЕТСТВИЯ** → для каждого compliance_status используй: FULL_MATCH / PARTIAL_MATCH / MISSING / UNCLEAR
4. **ОЦЕНКА КАЧЕСТВА ПРЕЗЕНТАЦИИ** → заполни ResumeQualityAssessment (все поля 1-10)
5. **ПРИОРИТИЗИРОВАННЫЕ РЕКОМЕНДАЦИИ** → распредели по criticality: CRITICAL/IMPORTANT/DESIRED
6. **ИТОГОВЫЕ ВЫВОДЫ** → процент соответствия, рекомендация по найму

⚠️ КРИТИЧНО: Используй ТОЧНУЮ терминологию из enum'ов модели! 

Результат верни в формате JSON согласно модели EnhancedResumeTailoringAnalysis."""
    
    @traceable(client=ls_client, project_name="llamaindex_test", run_type="retriever")
    async def gap_analysis(self, parsed_resume: Dict[str, Any], parsed_vacancy: Dict[str, Any]) -> Optional[EnhancedResumeTailoringAnalysis]:
        """Выполняет расширенный GAP-анализ резюме относительно вакансии с трейсингом."""
        # Проверка разрешения использования OpenAI API
        openai_controller.check_api_permission()
        
        try:
            logger.info("Начат расширенный GAP анализ резюме с обновленной моделью")
            
            # 1. Создаем обновленные промпты
            system_prompt = self._create_system_prompt()
            user_prompt = self._create_user_prompt(parsed_resume, parsed_vacancy)
            
            # 2. Подготовить сообщения для chat-completion
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user", 
                    "content": user_prompt
                }
            ]
            
            logger.debug(f"Отправка запроса к OpenAI API с обновленной моделью {self.model}")
            
            # 3. Вызвать OpenAI API (без изменений)
            completion = self.client.beta.chat.completions.parse(
                temperature=0.2,
                model=self.model,
                messages=messages,
                response_format=EnhancedResumeTailoringAnalysis,
            )

            # Записать статистику использования API
            tokens_used = completion.usage.total_tokens if completion.usage else 0
            openai_controller.record_request(success=True, tokens=tokens_used)

            # 4. Извлечь ответ
            raw_response_text = completion.choices[0].message.content
            if not raw_response_text:
                logger.error("Пустой ответ от модели при расширенном GAP-анализе")
                openai_controller.record_request(success=False, error="Пустой ответ от модели")
                return None
            
            # 5. Попробовать распарсить JSON в ОБНОВЛЕННУЮ модель
            gap_result = EnhancedResumeTailoringAnalysis.model_validate_json(raw_response_text)
            logger.info("Расширенный GAP-анализ успешно выполнен с обновленной моделью")
            
            # ДОБАВИТЬ: Логирование информации о новых полях
            if ls_client:
                # Подсчитаем статистику по новым enum'ам для мониторинга
                requirement_types = [req.requirement_type for req in gap_result.requirements_analysis]
                skill_categories = [req.skill_category for req in gap_result.requirements_analysis if req.skill_category]
                
                logger.info("Трейсинг: анализ завершен")
                logger.info(f"- Процент соответствия: {gap_result.overall_match_percentage}%")
                logger.info(f"- Типы требований: {set(requirement_types)}")
                logger.info(f"- Категории навыков: {set(skill_categories)}")
                logger.info(f"- Критичных рекомендаций: {len(gap_result.critical_recommendations)}")
                logger.info(f"- Важных рекомендаций: {len(gap_result.important_recommendations)}")
                logger.info(f"- Желательных рекомендаций: {len(gap_result.optional_recommendations)}")
            
            return gap_result

        except ValidationError as ve:
            logger.error(f"Ошибка валидации обновленной GAP-модели: {ve}")
            openai_controller.record_request(success=False, error=f"Ошибка валидации: {ve}")
            
            # УЛУЧШЕННОЕ логирование ошибок валидации
            if ls_client:
                # Логируем детали ошибки для отладки новых enum'ов
                logger.error(f"Трейсинг: ошибка валидации модели - {ve}")
                logger.error("Возможно модель использует старую терминологию, проверьте enum значения")
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при расширенном GAP-анализе: {e}", exc_info=True)
            openai_controller.record_request(success=False, error=str(e))
            
            if ls_client:
                logger.error(f"Трейсинг: общая ошибка - {e}")
            return None