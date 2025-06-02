# src/llm_interview_checklist/llm_interview_checklist_generator.py
import logging
from typing import Optional, Dict, Any
from openai import OpenAI
from pydantic import ValidationError

from src.llm_interview_checklist.config import settings
from src.models.interview_checklist_models import InterviewChecklist
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
    
    def _create_interview_checklist_prompt(self, parsed_resume: Dict[str, Any], parsed_vacancy: Dict[str, Any]) -> str:
        """
        Создает промпт для генерации чек-листа подготовки к интервью.
        
        Args:
            parsed_resume: Словарь с распарсенными данными резюме
            parsed_vacancy: Словарь с распарсенными данными вакансии
        
        Returns:
            str: Текст промпта
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
    
    async def generate_interview_checklist(self, parsed_resume: Dict[str, Any], parsed_vacancy: Dict[str, Any]) -> Optional[InterviewChecklist]:
        """
        Генерирует персонализированный чек-лист подготовки к интервью.
        
        Args:
            parsed_resume: Словарь с распарсенными данными резюме
            parsed_vacancy: Словарь с распарсенными данными вакансии
        
        Returns:
            InterviewChecklist: Объект с чек-листом подготовки или None в случае ошибки
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