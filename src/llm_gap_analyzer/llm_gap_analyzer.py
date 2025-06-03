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

logger = get_logger()

# ДОБАВИТЬ создание LangSmith клиента
def create_langsmith_client():
    """Создаёт клиента LangSmith для трейсинга."""
    api_key = os.getenv("LANGCHAIN_API_KEY")
    if not api_key:
        logger.warning("LANGCHAIN_API_KEY не установлен, трейсинг будет отключен")
        return None
    return Client(api_key=api_key)

# Создаём глобальный клиент для трейсинга
ls_client = create_langsmith_client()


class LLMGapAnalyzer:
    """Сервис для анализа резюме с помощью OpenAI API"""
    
    def __init__(self):
        """Инициализация клиента OpenAI с LangSmith трейсингом."""
        self.config = settings
        self.model = self.config.model_name
        
        # ЗАМЕНИТЬ создание клиента на версию с трейсингом
        self.client = self._create_traced_client()
        logger.info(f"Инициализирован GAP анализатор с моделью {self.model}")
    
    def _create_traced_client(self) -> OpenAI:
        """Создает OpenAI клиент с LangSmith трейсингом."""
        # Создаём базовый OpenAI клиент
        base_client = OpenAI(api_key=self.config.api_key)
        
        # Если LangSmith доступен, оборачиваем клиент
        if ls_client:
            logger.info("LangSmith трейсинг активирован для GAP анализа")
            wrapped_client = wrap_openai(base_client)
            return wrapped_client
        else:
            logger.info("LangSmith трейсинг недоступен, используется базовый клиент")
            return base_client
    
    def _create_gap_analysis_prompt(self, parsed_resume: Dict[str, Any], parsed_vacancy: Dict[str, Any]) -> str:
        """Создает промпт для gap-анализа с форматированными данными."""
        formatted_resume = format_resume_data(parsed_resume)
        formatted_vacancy = format_vacancy_data(parsed_vacancy)
        
        logger.debug("Создан промпт для расширенного GAP анализа")
        
        return f"""
# РОЛЬ: Ты — эксперт HR с 10+ летним опытом GAP-анализа резюме в IT-сфере

## КОНТЕКСТ ЗАДАЧИ
Ты проводишь профессиональный GAP-анализ резюме кандидата относительно конкретной вакансии. 
Твоя задача — имитировать реальный процесс оценки, который используют опытные рекрутеры.

## ИСХОДНЫЕ ДАННЫЕ

{formatted_resume}

{formatted_vacancy}

## МЕТОДОЛОГИЯ АНАЛИЗА (следуй строго по этапам)

### ЭТАП 1: ПЕРВИЧНЫЙ СКРИНИНГ (7-15 секунд)
Проанализируй базовые критерии, которые HR проверяет в первые секунды:
- Соответствие должности в резюме и вакансии
- Общий стаж в нужной сфере vs требуемый
- Наличие критичных навыков (видны ли ключевые слова)
- Локация и готовность к работе
- Зарплатные ожидания vs бюджет вакансии

### ЭТАП 2: КЛАССИФИКАЦИЯ ТРЕБОВАНИЙ
Раздели ВСЕ требования вакансии на:
- **MUST-HAVE** (без этого работа невозможна)
- **NICE-TO-HAVE** (желательно, но можно развить)
- **ДОПОЛНИТЕЛЬНЫЕ ПЛЮСЫ** (конкурентные преимущества)

### ЭТАП 3: ДЕТАЛЬНЫЙ АНАЛИЗ СООТВЕТСТВИЯ
Для каждого требования определи:
- ✅ **ПОЛНОЕ СООТВЕТСТВИЕ** - требование выполнено
- ⚠️ **ЧАСТИЧНОЕ СООТВЕТСТВИЕ** - есть упоминание, но недостаточно глубоко
- ❌ **ОТСУТСТВУЕТ** - требование не отражено в резюме
- 🔍 **ТРЕБУЕТ УТОЧНЕНИЯ** - неясно из резюме

### ЭТАП 4: АНАЛИЗ КАЧЕСТВА ПРЕЗЕНТАЦИИ
Оцени КАК кандидат подает информацию:
- Наличие конкретных достижений vs общие обязанности
- Структурированность и читабельность
- Релевантность описанного опыта
- Адаптация под вакансию

## КРИТЕРИИ КАЧЕСТВЕННОГО АНАЛИЗА

### Hard Skills:
- Проверь ТОЧНОЕ совпадение названий технологий (Django vs "веб-фреймворки")
- Оцени глубину опыта по описанию проектов
- Сопоставь уровень задач в резюме с уровнем вакансии

### Soft Skills:
- Ищи подтверждения через факты, а не декларации
- Анализируй качество самого резюме как показатель навыков
- Оценивай соответствие манеры изложения культуре компании

### Опыт:
- Релевантность сферы и задач
- Карьерная траектория (рост, стагнация, скачки)
- Масштаб проектов и ответственности

## ФОРМАТ РЕКОМЕНДАЦИЙ
Для каждой рекомендации указывай:
1. **Критичность**: КРИТИЧНО / ВАЖНО / ЖЕЛАТЕЛЬНО
2. **Обоснование**: почему это важно для данной вакансии
3. **Конкретные действия**: что именно добавить/изменить/убрать
4. **Примеры формулировок**: как лучше написать

## ДОПОЛНИТЕЛЬНЫЕ ТРЕБОВАНИЯ
- Используй профессиональную терминологию HR
- Учитывай специфику российского IT-рынка
- Давай actionable советы, а не общие рекомендации
- Приоритизируй рекомендации по влиянию на решение о приглашении

Проведи анализ и верни результат в формате JSON согласно модели EnhancedResumeTailoringAnalysis.
"""
    
    @traceable(client=ls_client, project_name="llamaindex_test", run_type = "retriever")
    async def gap_analysis(self, parsed_resume: Dict[str, Any], parsed_vacancy: Dict[str, Any]) -> Optional[EnhancedResumeTailoringAnalysis]:
        """Выполняет расширенный GAP-анализ резюме относительно вакансии с трейсингом."""
        try:
            logger.info("Начат расширенный GAP анализ резюме с трейсингом")
            
            # 1. Сформировать промпт для GAP-анализа
            prompt_text = self._create_gap_analysis_prompt(parsed_resume, parsed_vacancy)
            
            # 2. Подготовить сообщения для chat-completion
            messages = [
                {
                    "role": "system",
                    "content": (
                        "Ты — эксперт по рекрутингу и HR с глубоким пониманием IT-индустрии. "
                        "Твоя специализация — профессиональный GAP-анализ резюме с детальными "
                        "рекомендациями. Всегда отвечай строго в формате JSON согласно "
                        "указанной структуре EnhancedResumeTailoringAnalysis. Анализ должен быть "
                        "максимально профессиональным и практичным."
                    )
                },
                {
                    "role": "user",
                    "content": prompt_text
                }
            ]
            
            logger.debug(f"Отправка запроса к OpenAI API с моделью {self.model}")
            
            # 3. Вызвать OpenAI API (теперь с трейсингом)
            completion = self.client.beta.chat.completions.parse(
                temperature=0.2,
                model=self.model,
                messages=messages,
                response_format=EnhancedResumeTailoringAnalysis,
            )

            # 4. Извлечь ответ
            raw_response_text = completion.choices[0].message.content
            if not raw_response_text:
                logger.error("Пустой ответ от модели при расширенном GAP-анализе")
                return None
            
            # 5. Попробовать распарсить JSON в модель
            gap_result = EnhancedResumeTailoringAnalysis.model_validate_json(raw_response_text)
            logger.info("Расширенный GAP-анализ успешно выполнен с трейсингом")
            
            # ДОБАВИТЬ логирование метрик для трейсинга
            if ls_client:
                logger.info(f"Трейсинг: анализ завершен, процент соответствия: {gap_result.overall_match_percentage}%")
            
            return gap_result

        except ValidationError as ve:
            logger.error(f"Ошибка валидации расширенного GAP-анализа: {ve}")
            # Логируем ошибку в трейсинг
            if ls_client:
                logger.error(f"Трейсинг: ошибка валидации - {ve}")
            return None
        except Exception as e:
            logger.error(f"Ошибка при расширенном GAP-анализе: {e}", exc_info=True)
            # Логируем ошибку в трейсинг
            if ls_client:
                logger.error(f"Трейсинг: общая ошибка - {e}")
            return None