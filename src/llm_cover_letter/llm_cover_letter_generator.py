# src/llm_cover_letter/enhanced_llm_cover_letter_generator.py
import logging
from typing import Optional, Dict, Any
from openai import OpenAI
from pydantic import ValidationError

from src.llm_cover_letter.config import settings
from src.models.cover_letter_models import EnhancedCoverLetter
from src.llm_cover_letter.formatter import (
    format_resume_for_cover_letter, 
    format_vacancy_for_cover_letter
)

from src.utils import get_logger
logger = get_logger()

class EnhancedLLMCoverLetterGenerator:
    """
    Улучшенный сервис для создания профессиональных сопроводительных писем 
    на основе лучших практик HR-экспертов
    """
    
    def __init__(self):
        """Инициализация клиента OpenAI."""
        self.config = settings
        self.client = OpenAI(api_key=self.config.api_key)
        self.model = self.config.model_name
    
    def _analyze_vacancy_context(self, parsed_vacancy: Dict[str, Any]) -> Dict[str, str]:
        """
        Анализирует контекст вакансии для персонализации письма.
        
        Args:
            parsed_vacancy: Данные вакансии
            
        Returns:
            Dict с контекстной информацией
        """
        # Определение размера компании по описанию
        company_size = "MEDIUM"  # default
        description = parsed_vacancy.get('description', '').lower()
        
        if any(word in description for word in ['стартап', 'startup', 'молодая команда']):
            company_size = "STARTUP"
        elif any(word in description for word in ['крупная компания', 'enterprise', 'корпорация']):
            company_size = "ENTERPRISE"
        elif any(word in description for word in ['международная', 'global', 'более 1000']):
            company_size = "LARGE"
            
        # Определение типа роли
        position = parsed_vacancy.get('title', '').lower()
        role_type = "OTHER"
        
        if any(word in position for word in ['разработчик', 'developer', 'программист']):
            role_type = "DEVELOPER"
        elif any(word in position for word in ['тестировщик', 'qa', 'quality']):
            role_type = "QA_ENGINEER"
        elif any(word in position for word in ['аналитик', 'analyst']):
            role_type = "ANALYST"
        elif any(word in position for word in ['devops', 'sre', 'системный администратор']):
            role_type = "DEVOPS"
        elif any(word in position for word in ['дизайнер', 'designer', 'ux', 'ui']):
            role_type = "DESIGNER"
        elif any(word in position for word in ['менеджер', 'manager', 'lead', 'руководитель']):
            role_type = "MANAGER"
            
        return {
            'company_size': company_size,
            'role_type': role_type,
            'company_name': parsed_vacancy.get('company_name', 'Компания'),
            'position_title': parsed_vacancy.get('title', 'Позиция')
        }
    
    def _create_enhanced_cover_letter_prompt(self, parsed_resume: Dict[str, Any], parsed_vacancy: Dict[str, Any]) -> str:
        """
        Создает профессиональный промпт на основе лучших практик HR-экспертов.
        
        Args:
            parsed_resume: Словарь с данными резюме
            parsed_vacancy: Словарь с данными вакансии
        
        Returns:
            str: Профессиональный промпт
        """
        formatted_resume = format_resume_for_cover_letter(parsed_resume)
        formatted_vacancy = format_vacancy_for_cover_letter(parsed_vacancy)
        context = self._analyze_vacancy_context(parsed_vacancy)
        
        return f"""
# РОЛЬ: Ты — эксперт по написанию сопроводительных писем с 10+ летним опытом в IT-рекрутинге

## КРИТИЧЕСКАЯ СТАТИСТИКА
- 83% работодателей готовы рассмотреть кандидата с отличным письмом, даже если резюме не идеально
- 45% рекрутеров отказываются от кандидатов БЕЗ сопроводительного письма
- HR тратят 7-15 секунд на первичный просмотр письма
- Шаблонные письма распознаются мгновенно и идут в корзину

## ИСХОДНЫЕ ДАННЫЕ

### РЕЗЮМЕ КАНДИДАТА:
{formatted_resume}

### ВАКАНСИЯ:
{formatted_vacancy}

### КОНТЕКСТ:
- Тип роли: {context['role_type']}
- Размер компании: {context['company_size']}
- Название компании: {context['company_name']}
- Позиция: {context['position_title']}

## МЕТОДОЛОГИЯ СОЗДАНИЯ ПИСЬМА

### ЭТАП 1: ПЕРСОНАЛИЗАЦИЯ
Создай уникальные элементы для ЭТОЙ компании:

1. **Компанейский hook** - конкретный интерес к компании:
   - Продукт, технологии, недавние новости
   - Ценности или подходы, которые резонируют
   - НЕ общие фразы типа "лидер рынка"

2. **Ролевая мотивация** - почему именно ЭТА позиция интересна

### ЭТАП 2: ДОКАЗАТЕЛЬСТВА ЦЕННОСТИ
Выбери из резюме:
1. **1-2 самых релевантных достижения** с конкретными цифрами
2. **Точные совпадения навыков** из требований вакансии
3. **Опыт**, который решает задачи данной позиции

### ЭТАП 3: СТРУКТУРА (500-1000 символов)

**1. Зацепляющее начало:**
- Краткая история успеха ИЛИ достижение с цифрами
- Связь с продуктом/компанией
- НЕ "Меня заинтересовала ваша вакансия"

**2. Интерес к компании:**
- Конкретное знание о компании/продукте
- Личная связь с ценностями/подходами

**3. Ценностное предложение:**
- КАК навыки решат задачи работодателя
- Релевантные достижения с метриками
- Совпадения с ключевыми требованиями

**4. Профессиональное завершение:**
- Энтузиазм и call-to-action
- Готовность к интервью

## АДАПТАЦИЯ ПО ТИПУ РОЛИ

**DEVELOPER**: технический стек, проекты, производительность, code review
**QA_ENGINEER**: внимание к деталям, критические баги, инструменты тестирования
**ANALYST**: требования, процессы, домен, улучшения бизнес-метрик
**DEVOPS**: автоматизация, надежность, экономия времени/ресурсов
**DESIGNER**: UX-метрики, портфолио, влияние на конверсию
**MANAGER**: команда, процессы, результаты, лидерство

## ОБЯЗАТЕЛЬНЫЕ КРИТЕРИИ

✅ Упоминание конкретного названия компании и позиции
✅ Персонализация под компанию (продукт, новости, ценности)
✅ Конкретные достижения с цифрами
✅ Ответ на "Что получит работодатель?"
✅ Профессиональный, но живой тон

❌ Шаблонные фразы и клише
❌ Повторение резюме без ценности
❌ Общие качества без доказательств
❌ Фокус на желаниях кандидата

## ТОНАЛЬНОСТЬ ПО РАЗМЕРУ КОМПАНИИ
- **STARTUP**: более неформально, энтузиазм, готовность к вызовам
- **MEDIUM/LARGE**: баланс профессионализма и человечности
- **ENTERPRISE**: максимально профессионально, стабильность

Создай письмо в формате JSON согласно модели EnhancedCoverLetter, строго следуя всем принципам.
"""
    
    async def generate_enhanced_cover_letter(self, parsed_resume: Dict[str, Any], parsed_vacancy: Dict[str, Any]) -> Optional[EnhancedCoverLetter]:
        """
        Генерирует профессиональное сопроводительное письмо.
        
        Args:
            parsed_resume: Словарь с данными резюме
            parsed_vacancy: Словарь с данными вакансии
        
        Returns:
            EnhancedCoverLetter или None в случае ошибки
        """
        try:
            # 1. Создаем профессиональный промпт
            prompt_text = self._create_enhanced_cover_letter_prompt(parsed_resume, parsed_vacancy)
            
            # 2. Подготавливаем сообщения
            messages = [
                {
                    "role": "system",
                    "content": (
                        "Ты — ведущий эксперт по сопроводительным письмам в IT с 10+ летним опытом. "
                        "Специализируешься на создании персонализированных писем, которые проходят "
                        "7-15 секундный скрининг HR и выделяют кандидатов среди конкурентов. "
                        "Знаешь психологию рекрутеров и понимаешь, что ищут работодатели. "
                        "Всегда отвечаешь в формате JSON согласно модели EnhancedCoverLetter. "
                        "Пишешь на русском языке профессионально, но живо."
                    )
                },
                {
                    "role": "user",
                    "content": prompt_text
                }
            ]
            
            # 3. Вызов OpenAI API с новой моделью
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=messages,
                response_format=EnhancedCoverLetter,
                temperature=0.5  # Немного креативности для уникальности
            )
            
            # 4. Извлекаем и валидируем ответ
            raw_response_text = completion.choices[0].message.content
            if not raw_response_text:
                logger.error("Пустой ответ от модели при генерации сопроводительного письма.")
                return None
            
            # 5. Парсим в модель
            cover_letter = EnhancedCoverLetter.model_validate_json(raw_response_text)
            
            # 6. Дополнительная валидация качества
            if not self._validate_quality(cover_letter, parsed_vacancy):
                logger.warning("Письмо не прошло проверку качества")
                return None
                
            logger.info("Профессиональное сопроводительное письмо успешно сгенерировано.")
            return cover_letter
            
        except ValidationError as ve:
            logger.error(f"Ошибка валидации сопроводительного письма: {ve}")
            return None
        except Exception as e:
            logger.error(f"Ошибка при генерации сопроводительного письма: {e}")
            return None
    
    def _validate_quality(self, cover_letter: EnhancedCoverLetter, parsed_vacancy: Dict[str, Any]) -> bool:
        """
        Дополнительная валидация качества письма.
        
        Args:
            cover_letter: Сгенерированное письмо
            parsed_vacancy: Данные вакансии
            
        Returns:
            bool: True если письмо качественное
        """
        company_name = parsed_vacancy.get('company_name', '').lower()
        
        # Проверяем персонализацию
        full_text = (
            cover_letter.opening_hook + " " +
            cover_letter.company_interest + " " +
            cover_letter.relevant_experience
        ).lower()
        
        # Минимальные требования к качеству
        quality_checks = [
            # Упоминание компании
            company_name in full_text if company_name else True,
            # Минимальная оценка персонализации
            cover_letter.personalization_score >= 6,
            # Профессиональность
            cover_letter.professional_tone_score >= 7,
            # Релевантность
            cover_letter.relevance_score >= 6,
            # Есть конкретные навыки
            len(cover_letter.skills_match.matched_skills) >= 1,
            # Есть ценностное предложение
            len(cover_letter.personalization.value_proposition) >= 50
        ]
        
        return all(quality_checks)
    
    def format_for_email(self, cover_letter: EnhancedCoverLetter) -> str:
        """
        Форматирует письмо для отправки по email.
        
        Args:
            cover_letter: Объект письма
            
        Returns:
            str: Отформатированный текст письма
        """
        return f"""Тема: {cover_letter.subject_line}

{cover_letter.personalized_greeting}

{cover_letter.opening_hook}

{cover_letter.company_interest}

{cover_letter.relevant_experience}

{cover_letter.value_demonstration}

{cover_letter.growth_mindset or ""}

{cover_letter.professional_closing}

{cover_letter.signature}"""