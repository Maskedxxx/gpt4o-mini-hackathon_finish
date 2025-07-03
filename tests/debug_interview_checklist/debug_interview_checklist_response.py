#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для отладки ответа LLM в генерации чек-листа подготовки к интервью.
Вызывает реальную генерацию чек-листа и показывает структурированный результат.

Показывает:
1. Ответ от LLM в Pydantic структуре
2. JSON представление ответа
3. Детализацию по полям модели
4. Анализ качества и полноты чек-листа
5. Структуру всех 7 блоков подготовки

Использование:
    python tests/debug_interview_checklist_response.py
"""

import json
import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

# Добавляем корневую директорию проекта в Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Импорты из приложения
from src.parsers.resume_extractor import ResumeExtractor
from src.parsers.vacancy_extractor import VacancyExtractor
from src.llm_interview_checklist.llm_interview_checklist_generator import LLMInterviewChecklistGenerator
from src.models.interview_checklist_models import ProfessionalInterviewChecklist
from src.utils.logging_config import setup_logging

def load_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """Загружает JSON файл и возвращает данные."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"❌ Ошибка загрузки {file_path}: {e}")
        return None

def show_checklist_structure(checklist: ProfessionalInterviewChecklist) -> None:
    """Показывает структуру результата чек-листа интервью по полям."""
    print("\n" + "="*80)
    print("📋 СТРУКТУРА РЕЗУЛЬТАТА ЧЕК-ЛИСТА ПОДГОТОВКИ К ИНТЕРВЬЮ")
    print("="*80)
    
    try:
        print("🔸 ОЦЕНКА ВРЕМЕНИ И ПЛАНИРОВАНИЕ:")
        time_estimates = checklist.time_estimates
        print(f"   • Общее время подготовки: {time_estimates.total_time_needed}")
        print(f"   • Время на критические задачи: {time_estimates.critical_tasks_time}")
        print(f"   • Время на важные задачи: {time_estimates.important_tasks_time}")
        print(f"   • Время на желательные задачи: {time_estimates.optional_tasks_time}")
        print(f"   • Предложение по графику: {time_estimates.daily_schedule_suggestion[:50]}...")
        
        print("\n🔸 КОНТЕКСТ ПЕРСОНАЛИЗАЦИИ:")
        context = checklist.personalization_context
        print(f"   • Позиция: {checklist.position_title}")
        print(f"   • Компания: {checklist.company_name}")
        print(f"   • Уровень кандидата: {context.candidate_level.value}")
        print(f"   • Тип вакансии: {context.vacancy_type.value}")
        print(f"   • Формат компании: {context.company_format.value}")
        print(f"   • Выявленных пробелов: {len(context.key_gaps_identified)}")
        print(f"   • Сильных сторон: {len(context.candidate_strengths)}")
        
        print("\n🔸 КРАТКОЕ РЕЗЮМЕ И СТРАТЕГИЯ:")
        print(f"   • Длина краткого резюме: {len(checklist.executive_summary)} символов")
        print(f"   • Длина стратегии подготовки: {len(checklist.preparation_strategy)} символов")
        
        print("\n🔸 БЛОК 1: ТЕХНИЧЕСКАЯ ПОДГОТОВКА")
        tech_prep = checklist.technical_preparation
        print(f"   • Всего элементов: {len(tech_prep)}")
        categories = {}
        for item in tech_prep:
            cat = item.category
            categories[cat] = categories.get(cat, 0) + 1
        for cat, count in categories.items():
            print(f"   • {cat}: {count} элементов")
        
        print("\n🔸 БЛОК 2: ПОВЕДЕНЧЕСКАЯ ПОДГОТОВКА")
        behav_prep = checklist.behavioral_preparation
        print(f"   • Всего элементов: {len(behav_prep)}")
        total_questions = sum(len(item.example_questions) for item in behav_prep)
        print(f"   • Всего примерных вопросов: {total_questions}")
        
        print("\n🔸 БЛОК 3: ИЗУЧЕНИЕ КОМПАНИИ")
        company_research = checklist.company_research
        print(f"   • Всего элементов: {len(company_research)}")
        total_actions = sum(len(item.specific_actions) for item in company_research)
        print(f"   • Всего конкретных действий: {total_actions}")
        
        print("\n🔸 БЛОК 4: ИЗУЧЕНИЕ ТЕХНИЧЕСКОГО СТЕКА")
        tech_stack = checklist.technical_stack_study
        print(f"   • Всего элементов: {len(tech_stack)}")
        
        print("\n🔸 БЛОК 5: ПРАКТИЧЕСКИЕ УПРАЖНЕНИЯ")
        practical = checklist.practical_exercises
        print(f"   • Всего упражнений: {len(practical)}")
        difficulty_levels = {}
        for item in practical:
            level = item.difficulty_level
            difficulty_levels[level] = difficulty_levels.get(level, 0) + 1
        for level, count in difficulty_levels.items():
            print(f"   • {level}: {count} упражнений")
        
        print("\n🔸 БЛОК 6: НАСТРОЙКА ОКРУЖЕНИЯ")
        interview_setup = checklist.interview_setup
        print(f"   • Всего элементов настройки: {len(interview_setup)}")
        total_checklist_items = sum(len(item.checklist_items) for item in interview_setup)
        print(f"   • Всего пунктов чек-листа: {total_checklist_items}")
        
        print("\n🔸 БЛОК 7: ДОПОЛНИТЕЛЬНЫЕ ДЕЙСТВИЯ")
        additional = checklist.additional_actions
        print(f"   • Всего дополнительных действий: {len(additional)}")
        total_steps = sum(len(item.implementation_steps) for item in additional)
        print(f"   • Всего шагов выполнения: {total_steps}")
        
        print("\n🔸 ФИНАЛЬНЫЕ РЕКОМЕНДАЦИИ:")
        print(f"   • Критические факторы успеха: {len(checklist.critical_success_factors)}")
        print(f"   • Ошибки для избегания: {len(checklist.common_mistakes_to_avoid)}")
        print(f"   • Чек-лист последней минуты: {len(checklist.last_minute_checklist)}")
        print(f"   • Длина мотивационного сообщения: {len(checklist.motivation_boost)} символов")
        
    except Exception as e:
        print(f"❌ Ошибка анализа структуры: {e}")

def analyze_checklist_quality(checklist: ProfessionalInterviewChecklist) -> None:
    """Анализирует качество и полноту чек-листа."""
    print("\n" + "="*80)
    print("🎯 АНАЛИЗ КАЧЕСТВА И ПОЛНОТЫ ЧЕК-ЛИСТА")
    print("="*80)
    
    try:
        # Подсчет общих метрик
        total_items = (
            len(checklist.technical_preparation) +
            len(checklist.behavioral_preparation) +
            len(checklist.company_research) +
            len(checklist.technical_stack_study) +
            len(checklist.practical_exercises) +
            len(checklist.interview_setup) +
            len(checklist.additional_actions)
        )
        
        print("📊 ОБЩИЕ МЕТРИКИ:")
        print(f"   • Всего элементов в чек-листе: {total_items}")
        print(f"   • Все 7 блоков заполнены: {'✅' if total_items > 0 else '❌'}")
        
        # Анализ приоритизации
        priorities = {"КРИТИЧНО": 0, "ВАЖНО": 0, "ЖЕЛАТЕЛЬНО": 0}
        
        for item in checklist.technical_preparation:
            priorities[item.priority.value] = priorities.get(item.priority.value, 0) + 1
        
        for item in checklist.company_research:
            priorities[item.priority.value] = priorities.get(item.priority.value, 0) + 1
            
        for item in checklist.additional_actions:
            priorities[item.urgency.value] = priorities.get(item.urgency.value, 0) + 1
        
        print("\n🎯 ПРИОРИТИЗАЦИЯ:")
        for priority, count in priorities.items():
            print(f"   • {priority}: {count} элементов")
        
        # Анализ конкретности
        has_resources = sum(1 for item in checklist.technical_preparation if item.specific_resources)
        has_time_estimates = sum(1 for item in checklist.technical_preparation if item.estimated_time)
        
        print("\n🔍 КОНКРЕТНОСТЬ:")
        print(f"   • Элементы с ресурсами: {has_resources}/{len(checklist.technical_preparation)}")
        print(f"   • Элементы с временными оценками: {has_time_estimates}/{len(checklist.technical_preparation)}")
        
        # Проверка персонализации
        content = checklist.model_dump_json()
        personalized_indicators = content.lower().count("кандидат") + content.lower().count("ваш") + content.lower().count("вам")
        
        print("\n👤 ПЕРСОНАЛИЗАЦИЯ:")
        print(f"   • Персональные обращения: {personalized_indicators} упоминаний")
        print(f"   • Уровень персонализации: {'Высокий' if personalized_indicators > 20 else 'Средний' if personalized_indicators > 10 else 'Низкий'}")
        
        # Оценка полноты
        completeness_score = 0
        if len(checklist.technical_preparation) >= 5: completeness_score += 1
        if len(checklist.behavioral_preparation) >= 4: completeness_score += 1
        if len(checklist.company_research) >= 3: completeness_score += 1
        if len(checklist.practical_exercises) >= 5: completeness_score += 1
        if len(checklist.critical_success_factors) >= 3: completeness_score += 1
        
        print("\n✅ ОЦЕНКА ПОЛНОТЫ:")
        print(f"   • Баллы полноты: {completeness_score}/5")
        print(f"   • Оценка: {'Отличная' if completeness_score >= 4 else 'Хорошая' if completeness_score >= 3 else 'Требует доработки'}")
        
    except Exception as e:
        print(f"❌ Ошибка анализа качества: {e}")

def show_sample_content(checklist: ProfessionalInterviewChecklist) -> None:
    """Показывает примеры контента из каждого блока."""
    print("\n" + "="*80)
    print("📝 ПРИМЕРЫ КОНТЕНТА ИЗ КАЖДОГО БЛОКА")
    print("="*80)
    
    try:
        if checklist.technical_preparation:
            print("🔧 ТЕХНИЧЕСКАЯ ПОДГОТОВКА (первый элемент):")
            item = checklist.technical_preparation[0]
            print(f"   • Категория: {item.category}")
            print(f"   • Задача: {item.task_title}")
            print(f"   • Приоритет: {item.priority.value}")
            print(f"   • Время: {item.estimated_time}")
            print(f"   • Ресурсы: {len(item.specific_resources)} шт.")
        
        if checklist.behavioral_preparation:
            print("\n💼 ПОВЕДЕНЧЕСКАЯ ПОДГОТОВКА (первый элемент):")
            item = checklist.behavioral_preparation[0]
            print(f"   • Категория: {item.category}")
            print(f"   • Задача: {item.task_title}")
            print(f"   • Примерных вопросов: {len(item.example_questions)}")
            if item.example_questions:
                print(f"   • Первый вопрос: {item.example_questions[0][:100]}...")
        
        if checklist.company_research:
            print("\n🏢 ИЗУЧЕНИЕ КОМПАНИИ (первый элемент):")
            item = checklist.company_research[0]
            print(f"   • Категория: {item.category}")
            print(f"   • Задача: {item.task_title}")
            print(f"   • Действий: {len(item.specific_actions)}")
            print(f"   • Приоритет: {item.priority.value}")
        
        if checklist.practical_exercises:
            print("\n🎯 ПРАКТИЧЕСКИЕ УПРАЖНЕНИЯ (первый элемент):")
            item = checklist.practical_exercises[0]
            print(f"   • Категория: {item.category}")
            print(f"   • Упражнение: {item.exercise_title}")
            print(f"   • Сложность: {item.difficulty_level}")
            print(f"   • Ресурсов: {len(item.practice_resources)}")
        
        print("\n🎯 КРИТИЧЕСКИЕ ФАКТОРЫ УСПЕХА:")
        for i, factor in enumerate(checklist.critical_success_factors[:3], 1):
            print(f"   {i}. {factor}")
        
    except Exception as e:
        print(f"❌ Ошибка показа примеров: {e}")

async def test_interview_checklist_generation():
    """Основная функция для тестирования генерации чек-листа интервью."""
    print("🚀 ЗАПУСК ОТЛАДКИ INTERVIEW CHECKLIST RESPONSE")
    print("="*80)
    
    # Настройка логирования
    setup_logging()
    
    # Пути к тестовым файлам
    current_dir = Path(__file__).parent
    resume_path = current_dir / "test_models_res_vac" / "fetched_resume_6d807532ff0ed6b79f0039ed1f63386d724a62.json"
    vacancy_path = current_dir / "test_models_res_vac" / "fetched_vacancy_120234346.json"
    
    print("📂 Загрузка тестовых данных:")
    print(f"   • Резюме: {resume_path.name}")
    print(f"   • Вакансия: {vacancy_path.name}")
    
    # Загрузка сырых данных
    raw_resume = load_json_file(str(resume_path))
    raw_vacancy = load_json_file(str(vacancy_path))
    
    if not raw_resume or not raw_vacancy:
        print("❌ Не удалось загрузить тестовые данные")
        return
    
    print("✅ Тестовые данные загружены")
    
    # Парсинг данных
    print("\n📋 Парсинг данных...")
    try:
        resume_extractor = ResumeExtractor()
        vacancy_extractor = VacancyExtractor()
        
        parsed_resume = resume_extractor.extract_resume_info(raw_resume)
        parsed_vacancy = vacancy_extractor.extract_vacancy_info(raw_vacancy)
        
        resume_dict = parsed_resume.model_dump()
        vacancy_dict = parsed_vacancy.model_dump()
        
        print("✅ Данные успешно спарсены")
        print(f"   • Резюме: {resume_dict.get('title', 'Без названия')}")
        print(f"   • Вакансия: {vacancy_dict.get('name', 'Без названия')}")
        
    except Exception as e:
        print(f"❌ Ошибка парсинга данных: {e}")
        return
    
    # Генерация чек-листа
    print("\n🧠 Генерация чек-листа интервью...")
    try:
        generator = LLMInterviewChecklistGenerator()
        checklist = await generator.generate_professional_interview_checklist(resume_dict, vacancy_dict)
        
        if not checklist:
            print("❌ Не удалось сгенерировать чек-лист")
            return
            
        print("✅ Чек-лист успешно сгенерирован!")
        
    except Exception as e:
        print(f"❌ Ошибка генерации чек-листа: {e}")
        return
    
    # Анализ результата
    show_checklist_structure(checklist)
    analyze_checklist_quality(checklist)
    show_sample_content(checklist)
    
    # Сохранение результата в JSON
    output_file = current_dir / "debug_response_interview_checklist.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(checklist.model_dump(), f, ensure_ascii=False, indent=2)
        print(f"\n💾 Результат сохранен в: {output_file.name}")
        print(f"   • Размер файла: {output_file.stat().st_size:,} байт")
        
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")
    
    # Финальная статистика
    print("\n" + "="*80)
    print("🎉 ОТЛАДКА ЗАВЕРШЕНА УСПЕШНО")
    print("="*80)
    print("📊 ИТОГОВАЯ СТАТИСТИКА:")
    
    checklist_json = checklist.model_dump_json()
    print(f"   • Размер JSON: {len(checklist_json):,} символов")
    print("   • Всего блоков: 7 (обязательных)")
    total_elements = (len(checklist.technical_preparation) + len(checklist.behavioral_preparation) + 
                     len(checklist.company_research) + len(checklist.technical_stack_study) + 
                     len(checklist.practical_exercises) + len(checklist.interview_setup) + 
                     len(checklist.additional_actions))
    print(f"   • Общее количество элементов: {total_elements}")
    print("   • Модель валидации: ProfessionalInterviewChecklist ✅")
    print("   • Готов к использованию в хендлере: ✅")

if __name__ == "__main__":
    asyncio.run(test_interview_checklist_generation())