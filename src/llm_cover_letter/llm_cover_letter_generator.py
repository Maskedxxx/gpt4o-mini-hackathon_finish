# src/llm_cover_letter/enhanced_llm_cover_letter_generator.py
import logging
from typing import Optional, Dict, Any
from openai import OpenAI
from pydantic import ValidationError

from src.llm_cover_letter.config import settings
from src.models.cover_letter_models import EnhancedCoverLetter
from src.llm_cover_letter.formatter import (
    format_resume_for_cover_letter, 
    format_vacancy_for_cover_letter,
    format_cover_letter_context
)

from src.utils import get_logger
logger = get_logger()

class EnhancedLLMCoverLetterGenerator:
    """
    Улучшенный сервис для создания профессиональных сопроводительных писем 
    на основе лучших практик HR-экспертов
    """
    
    def __init__(self, validate_quality: bool = True):
        """Инициализация клиента OpenAI."""
        self.config = settings
        self.client = OpenAI(api_key=self.config.api_key)
        self.model = self.config.model_name
        self.validate_quality = validate_quality
    
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
        
        if any(word in description for word in ['стартап', 'startup', 'молодая команда', 'начинающая компания', 'растущая команда']):
            company_size = "STARTUP"
        elif any(word in description for word in ['крупная компания', 'enterprise', 'корпорация', 'холдинг', 'группа компаний']):
            company_size = "ENTERPRISE"
        elif any(word in description for word in ['международная', 'global', 'более 1000', 'multinational', 'мировой лидер']):
            company_size = "LARGE"
      
            
        return {
            'company_size': company_size,
            'company_name': parsed_vacancy.get('company_name', ''),
            'position_title': parsed_vacancy.get('title', 'Позиция')
        }
    
    def _create_system_prompt(self, context: Dict[str, str], resume_dict: Dict[str, Any], vacancy_dict: Dict[str, Any]) -> str:
        """
        Создает системный промпт с ролью, инструкцией и полным контекстом.
        
        Args:
            context: Контекст вакансии (размер компании, тип роли и т.д.)
            resume_dict: Данные резюме для анализа соответствия
            vacancy_dict: Данные вакансии для анализа соответствия
        
        Returns:
            str: Системный промпт
        """
        # Получаем контекст персонализации через форматтер
        personalization_context = format_cover_letter_context(resume_dict, vacancy_dict)
        
        return f"""# РОЛЬ: Ты — эксперт по написанию сопроводительных писем с 10+ летним опытом в IT-рекрутинге

            ## КРИТИЧЕСКАЯ СТАТИСТИКА
            - 83% работодателей готовы рассмотреть кандидата с отличным письмом, даже если резюме не идеально
            - 45% рекрутеров отказываются от кандидатов БЕЗ сопроводительного письма
            - HR тратят 7-15 секунд на первичный просмотр письма
            - Шаблонные письма распознаются мгновенно и идут в корзину

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

            ## АДАПТАЦИЯ и ОПРЕДЕЛЕНИЕ ПО ТИПУ РОЛИ

            **DEVELOPER**:
            **Определение:** Backend/Frontend/Mobile разработчик, программист, software engineer.
            **Адаптация:** Фокусируйтесь на техническом стеке, проектах, производительности, code review, архитектуре.

            **ML_ENGINEER**:
            **Определение:** ML engineer, AI engineer, machine learning, deep learning, computer vision.
            **Адаптация:** Фокусируйтесь на алгоритмах ML, моделях, пайплайнах, экспериментах, метриках качества.

            **DATA_SCIENTIST**:
            **Определение:** Data scientist, аналитик данных, исследователь данных, big data.
            **Адаптация:** Фокусируйтесь на исследованиях, статистике, инсайтах, A/B тестах, бизнес-метриках.

            **QA_ENGINEER**:
            **Определение:** Тестировщик, QA, quality assurance, автотестировщик, test engineer.
            **Адаптация:** Фокусируйтесь на внимании к деталям, критических багах, инструментах тестирования, качестве.

            **ANALYST**:
            **Определение:** Бизнес-аналитик, системный аналитик, product analyst, BI analyst.
            **Адаптация:** Фокусируйтесь на требованиях, процессах, домене, улучшениях бизнес-метрик, аналитике.

            **DEVOPS**:
            **Определение:** DevOps, SRE, системный администратор, infrastructure, cloud engineer.
            **Адаптация:** Фокусируйтесь на автоматизации, надежности, экономии времени/ресурсов, инфраструктуре.

            **DESIGNER**:
            **Определение:** UI/UX дизайнер, продуктовый дизайнер, веб-дизайнер, motion designer.
            **Адаптация:** Фокусируйтесь на UX-метриках, портфолио, влиянии на конверсию, пользовательском опыте.

            **MANAGER**:
            **Определение:** Project manager, team lead, product manager, scrum master, руководитель.
            **Адаптация:** Фокусируйтесь на команде, процессах, результатах, лидерстве, управлении проектами.

            **OTHER**:
            **Определение:** Если не подходит ни один из вышеперечисленных.
            **Адаптация:** Опишите ключевые аспекты, специфичные для данной роли.
            
            Выбери НАИБОЛЕЕ ПОДХОДЯЩИЙ тип роли для позиции: {context['position_title']}

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

            ## КОНТЕКСТ ДЛЯ ПЕРСОНАЛИЗАЦИИ

            ### КОНТЕКСТ КОМПАНИИ:
            - Размер компании: {context['company_size']}
            - Название компании: {context['company_name']}
            - Позиция: {context['position_title']}
            {personalization_context}
            
            ## ОБЯЗАТЕЛЬНО ИСПОЛЬЗУЙ СГЕНЕРИРОВАННЫЕ ДАННЫЕ
            ### Обязательно заполни поля company_context на основе описания вакансии:
              - company_culture: особенности культуры компании (если упомянуты)
              - product_info: информация о продукте/сервисе компании
            ### В письме АКТИВНО используй данные из skills_match и personalization:
              - **opening_hook** - ОБЯЗАТЕЛЬНО включи quantified_achievement из skills_match
              - **company_interest** - используй company_hook и company_knowledge из personalization  
              - **relevant_experience** - развивай relevant_experience из skills_match
              - **value_demonstration** - конкретизируй value_proposition из personalization
            """

    def _create_user_prompt(self, parsed_resume: Dict[str, Any], parsed_vacancy: Dict[str, Any]) -> str:
        """
        Создает пользовательский промпт с данными резюме и вакансии.
        
        Args:
            parsed_resume: Словарь с данными резюме
            parsed_vacancy: Словарь с данными вакансии
        
        Returns:
            str: Пользовательский промпт
        """
        formatted_resume = format_resume_for_cover_letter(parsed_resume)
        formatted_vacancy = format_vacancy_for_cover_letter(parsed_vacancy)
        
        return f"""## ИСХОДНЫЕ ДАННЫЕ

    ### РЕЗЮМЕ КАНДИДАТА:
    <resume_start>
    {formatted_resume}
    </resume_end>
    
    ### ВАКАНСИЯ:
    <vacancy_start>
    {formatted_vacancy}
    </vacancy_end>

    ## ИНСТРУКЦИЯ

    Создай профессиональное сопроводительное письмо, строго следуя методологии из системного промпта:

    1. **Определи тип роли** - выбери подходящий role_type из enum значений
    2. **Анализируй контекст** - учитывай тип роли и размер компании
    3. **Персонализируй под компанию** - найди уникальный hook
    4. **Демонстрируй ценность** - покажи конкретные достижения и соответствие навыков
    5. **Соблюдай структуру** - зацепка, интерес к компании, ценность, завершение
    6. **Адаптируй тональность** - под размер компании и тип роли

    Верни результат в формате JSON согласно модели **EnhancedCoverLetter**."""
    
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
            # 1. Анализируем контекст вакансии
            context = self._analyze_vacancy_context(parsed_vacancy)
            
            # 2. Создаем системный и пользовательский промпты
            system_prompt = self._create_system_prompt(context, parsed_resume, parsed_vacancy)
            user_prompt = self._create_user_prompt(parsed_resume, parsed_vacancy)
            
            # 3. Подготавливаем сообщения
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
            
            # 4. Вызов OpenAI API с новой моделью
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=messages,
                response_format=EnhancedCoverLetter,
                temperature=0.5  # Немного креативности для уникальности
            )
            
            # 5. Извлекаем и валидируем ответ
            raw_response_text = completion.choices[0].message.content
            print(f"Raw response text: {raw_response_text}")  # Для отладки
            if not raw_response_text:
                logger.error("Пустой ответ от модели при генерации сопроводительного письма.")
                return None
            
            # 6. Парсим в модель
            cover_letter = EnhancedCoverLetter.model_validate_json(raw_response_text)
            
            # 7. Дополнительная валидация качества
            if self.validate_quality and not self._validate_quality(cover_letter, parsed_vacancy):
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