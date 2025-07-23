# src/llm_resume_rewriter/llm_resume_rewriter.py
import os
from typing import Optional, Dict, Any
from openai import OpenAI
from pydantic import ValidationError
import instructor

# LangSmith импорты
from langsmith.wrappers import wrap_openai
from langsmith import traceable, Client

from src.utils import get_logger
from src.llm_resume_rewriter.config import settings
from src.models.resume_models import ResumeInfo
from src.llm_resume_rewriter.formatter import format_resume_data, format_gap_analysis_data
from src.security.openai_control import openai_controller

logger = get_logger()

# LangSmith клиент
def create_langsmith_client():
    """Создаёт клиента LangSmith для трейсинга."""
    api_key = os.getenv("LANGCHAIN_API_KEY")
    if not api_key:
        logger.warning("LANGCHAIN_API_KEY не установлен, трейсинг будет отключен")
        return None
    return Client(api_key=api_key)

ls_client = create_langsmith_client()


class LLMResumeRewriter:
    """Сервис для переписывания резюме на основе GAP-анализа с помощью OpenAI API"""
    
    def __init__(self):
        """Инициализация клиента OpenAI с LangSmith трейсингом."""
        self.config = settings
        self.model = self.config.model_name
        self.client = self._create_traced_client()
        logger.info(f"Инициализирован Resume Rewriter с моделью {self.model}")
    
    def _create_traced_client(self) -> OpenAI:
        """Создает OpenAI клиент с LangSmith трейсингом."""
        base_client = OpenAI(api_key=self.config.api_key)
        
        if ls_client:
            logger.info("LangSmith трейсинг активирован для Resume Rewriter")
            wrapped_client = wrap_openai(base_client)
            return wrapped_client
        else:
            logger.info("LangSmith трейсинг недоступен, используется базовый клиент")
            return base_client
    
    def _create_system_prompt(self) -> str:
        """Системный промпт для рерайта резюме."""
        return """# РОЛЬ: Ты — эксперт по рекрутингу и карьерному консультированию

## ЗАДАЧА
Ты должен переписать и улучшить резюме кандидата на основе результатов GAP-анализа для конкретной вакансии. 
Твоя цель — максимально адаптировать резюме под требования работодателя, устранив слабые места и подчеркнув сильные стороны.

## ПРИНЦИПЫ РЕРАЙТА

### 1. АНАЛИЗ РЕКОМЕНДАЦИЙ GAP-АНАЛИЗА
- Внимательно изучи все рекомендации по улучшению (improvement_suggestions)
- Обрати особое внимание на недостающие навыки (missing_skills)
- Используй информацию о сильных сторонах (strong_points) для их усиления
- Учти слабые места (weak_points) для их исправления

### 2. СТРАТЕГИЯ УЛУЧШЕНИЯ
- **Навыки**: Переформулируй описание навыков, включив ключевые слова из GAP-анализа
- **Опыт работы**: Переакцентируй описания проектов под требования вакансии
- **Достижения**: Добавь количественные показатели и результаты там, где это уместно
- **Ключевые слова**: Интегрируй отсутствующие важные термины в естественном контексте

### 3. ТЕХНИКИ ОПТИМИЗАЦИИ
- Используй активные глаголы и конкретные примеры
- Подчеркни релевантный опыт, переместив его в начало описаний
- Адаптируй профессиональные роли под требования вакансии
- Переформулируй навыки, используя терминологию из вакансии

### 4. СОХРАНЕНИЕ ДОСТОВЕРНОСТИ
- НЕ добавляй навыки или опыт, которых у кандидата нет
- НЕ указывай ложную информацию о компаниях или должностях
- Улучшай ТОЛЬКО формулировки и подачу существующего опыта
- Можешь предлагать переформулировки, но в рамках правдивости

## ФОРМАТ ОТВЕТА
Верни ТОЛЬКО JSON, строго соответствующий Pydantic-схеме ResumeInfo. 
Все поля должны быть заполнены согласно исходной структуре данных.

## ВАЖНЫЕ ТРЕБОВАНИЯ
- Сохрани ВСЕ обязательные поля из исходного резюме
- Улучши формулировки, но сохрани фактическую точность
- Интегрируй рекомендации GAP-анализа естественным образом
- Результат должен быть валидным JSON для модели ResumeInfo"""

    def _create_user_prompt(self, resume_data: dict, gap_analysis_data: dict) -> str:
        """Создает пользовательский промпт с данными резюме и GAP-анализа."""
        
        # Форматируем данные
        formatted_resume = format_resume_data(resume_data)
        formatted_gap_analysis = format_gap_analysis_data(gap_analysis_data)
        
        prompt = f"""# ДАННЫЕ ДЛЯ АНАЛИЗА

{formatted_resume}

---

{formatted_gap_analysis}

---

# ИНСТРУКЦИИ ПО РЕРАЙТУ

На основе представленных данных, переписать резюме, учитывая следующие ключевые моменты:

1. **Недостающие навыки**: Если в GAP-анализе указаны missing_skills, попытайся найти способы подчеркнуть похожие или смежные навыки в резюме, используя более подходящую терминологию.

2. **Рекомендации по улучшению**: Следуй каждой рекомендации из improvement_suggestions, адаптируя соответствующие разделы резюме.

3. **Сильные стороны**: Усиль формулировки в тех областях, которые отмечены как strong_points.

4. **Слабые места**: Переформулируй или дополни информацию в областях, указанных как weak_points.

5. **Компетенции с низкими оценками**: Обрати особое внимание на области с оценкой менее 7/10 в competency_analysis.

## РЕЗУЛЬТАТ
Верни улучшенное резюме в формате JSON, полностью соответствующем структуре ResumeInfo."""

        return prompt

    @traceable(client=ls_client, project_name="resume_rewriter", run_type="llm")
    async def rewrite_resume(self, resume_dict: dict, gap_analysis_dict: dict) -> Optional[ResumeInfo]:
        """
        Основной метод для рерайта резюме на основе GAP-анализа.
        
        Args:
            resume_dict: Словарь с данными резюме (из ResumeInfo.model_dump())
            gap_analysis_dict: Словарь с результатами GAP-анализа (из GapAnalysisResult.model_dump())
            
        Returns:
            ResumeInfo: Улучшенная версия резюме или None в случае ошибки
        """
        try:
            # Проверка доступности OpenAI API
            openai_controller.check_api_permission()
            
            logger.info("Начало рерайта резюме на основе GAP-анализа")
            
            # Создание промптов
            system_prompt = self._create_system_prompt()
            user_prompt = self._create_user_prompt(resume_dict, gap_analysis_dict)
            
            logger.info("Отправка запроса к OpenAI для рерайта резюме")
            
            # Настройка instructor для структурированного вывода
            instructor_client = instructor.from_openai(self.client)
            
            # Вызов OpenAI API
            response = instructor_client.chat.completions.create(
                model=self.model,
                response_model=ResumeInfo,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Низкая температура для более консистентных результатов
                max_tokens=4000
            )
            
            # Учет использования токенов
            if hasattr(response, '_raw_response') and hasattr(response._raw_response, 'usage'):
                tokens_used = response._raw_response.usage.total_tokens
                openai_controller.record_request(success=True, tokens=tokens_used)
                logger.info(f"Использовано токенов: {tokens_used}")
            else:
                openai_controller.record_request(success=True, tokens=0)
            
            logger.info("Рерайт резюме успешно завершен")
            return response
            
        except ValidationError as ve:
            logger.error(f"Ошибка валидации ответа от LLM: {ve}")
            openai_controller.record_request(success=False, error=f"Validation error: {str(ve)}")
            
            # Попытка повторного запроса с более строгими инструкциями
            try:
                logger.info("Попытка повторного запроса с уточненными инструкциями")
                
                retry_prompt = user_prompt + f"""

ВАЖНО: Предыдущий ответ содержал ошибки валидации: {str(ve)}
Пожалуйста, убедись, что JSON строго соответствует схеме ResumeInfo и все обязательные поля заполнены корректно."""
                
                retry_response = instructor_client.chat.completions.create(
                    model=self.model,
                    response_model=ResumeInfo,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": retry_prompt}
                    ],
                    temperature=0.1,
                    max_tokens=4000
                )
                
                if hasattr(retry_response, '_raw_response') and hasattr(retry_response._raw_response, 'usage'):
                    tokens_used = retry_response._raw_response.usage.total_tokens
                    openai_controller.record_request(success=True, tokens=tokens_used)
                else:
                    openai_controller.record_request(success=True, tokens=0)
                
                logger.info("Повторный рерайт резюме успешно завершен")
                return retry_response
                
            except Exception as retry_e:
                logger.error(f"Ошибка при повторном запросе: {retry_e}")
                openai_controller.record_request(success=False, error=f"Retry error: {str(retry_e)}")
                return None
            
        except Exception as e:
            logger.error(f"Общая ошибка при рерайте резюме: {e}", exc_info=True)
            openai_controller.record_request(success=False, error=str(e))
            return None


# Функция для создания экземпляра сервиса
def create_resume_rewriter() -> LLMResumeRewriter:
    """Создает экземпляр сервиса рерайта резюме."""
    return LLMResumeRewriter()