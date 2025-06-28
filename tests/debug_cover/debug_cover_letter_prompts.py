#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для отладки промптов сопроводительного письма.
Использует готовые методы из приложения для создания промптов.

Показывает:
1. Системный промпт (system)
2. Пользовательский промпт (user) 
3. Полный массив messages для OpenAI API
4. Форматированные данные резюме и вакансии
5. Контекст для персонализации

Использование:
    python tests/debug_cover_letter/debug_cover_letter_prompts.py
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Добавляем корневую директорию проекта в Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Импорты из приложения
from src.parsers.resume_extractor import ResumeExtractor
from src.parsers.vacancy_extractor import VacancyExtractor
from src.llm_cover_letter.llm_cover_letter_generator import EnhancedLLMCoverLetterGenerator
from src.llm_cover_letter.formatter import (
    format_resume_for_cover_letter,
    format_vacancy_for_cover_letter,
    format_cover_letter_context
)
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

def debug_system_prompt(resume_json_path: str, vacancy_json_path: str) -> None:
    """Показывает системный промпт сопроводительного письма."""
    print("\n" + "="*80)
    print("🤖 СИСТЕМНЫЙ ПРОМПТ (SYSTEM)")
    print("="*80)
    
    # Загружаем и парсим данные для получения контекста
    raw_resume = load_json_file(resume_json_path)
    raw_vacancy = load_json_file(vacancy_json_path)
    
    if not (raw_resume and raw_vacancy):
        return
    
    # Парсим данные
    resume_extractor = ResumeExtractor()
    vacancy_extractor = VacancyExtractor()
    
    parsed_resume = resume_extractor.extract_resume_info(raw_resume)
    parsed_vacancy = vacancy_extractor.extract_vacancy_info(raw_vacancy)
    
    if not (parsed_resume and parsed_vacancy):
        print("❌ Ошибка парсинга данных")
        return
    
    try:
        # Создаем генератор
        cover_letter_generator = EnhancedLLMCoverLetterGenerator()
        
        # Получаем контекст и данные в dict формате
        resume_dict = parsed_resume.model_dump()
        vacancy_dict = parsed_vacancy.model_dump()
        context = cover_letter_generator._analyze_vacancy_context(vacancy_dict)
        
        # Используем новый метод для создания системного промпта с полным контекстом
        system_prompt = cover_letter_generator._create_system_prompt(context, resume_dict, vacancy_dict)
        
        print(system_prompt)
        print(f"\n📊 Длина системного промпта: {len(system_prompt)} символов")
        
    except Exception as e:
        print(f"❌ Ошибка создания системного промпта: {e}")

def debug_formatted_data(resume_json_path: str, vacancy_json_path: str) -> None:
    """Показывает форматированные данные резюме и вакансии."""
    print("\n" + "="*80)
    print("📄 ФОРМАТИРОВАННЫЕ ДАННЫЕ")
    print("="*80)
    
    # Загружаем и парсим данные
    raw_resume = load_json_file(resume_json_path)
    raw_vacancy = load_json_file(vacancy_json_path)
    
    if not (raw_resume and raw_vacancy):
        return
    
    # Парсим данные через существующие парсеры
    resume_extractor = ResumeExtractor()
    vacancy_extractor = VacancyExtractor()
    
    parsed_resume = resume_extractor.extract_resume_info(raw_resume)
    parsed_vacancy = vacancy_extractor.extract_vacancy_info(raw_vacancy)
    
    if not (parsed_resume and parsed_vacancy):
        print("❌ Ошибка парсинга данных")
        return
    
    try:
        # Конвертируем в dict как в реальном приложении
        resume_dict = parsed_resume.model_dump()
        vacancy_dict = parsed_vacancy.model_dump()
        
        # Форматируем данные через готовые форматтеры
        formatted_resume = format_resume_for_cover_letter(resume_dict)
        formatted_vacancy = format_vacancy_for_cover_letter(vacancy_dict)
        formatted_context = format_cover_letter_context(resume_dict, vacancy_dict)
        
        print("🔸 ФОРМАТИРОВАННОЕ РЕЗЮМЕ (в USER промпте):")
        print("-" * 40)
        print(formatted_resume)
        print(f"📊 Длина: {len(formatted_resume)} символов")
        
        print("\n🔸 ФОРМАТИРОВАННАЯ ВАКАНСИЯ (в USER промпте):")
        print("-" * 40)
        print(formatted_vacancy)
        print(f"📊 Длина: {len(formatted_vacancy)} символов")
        
        print("\n🔸 КОНТЕКСТ ДЛЯ ПЕРСОНАЛИЗАЦИИ (в SYSTEM промпте):")
        print("-" * 40)
        print(formatted_context)
        print(f"📊 Длина: {len(formatted_context)} символов")
        
        print("\n💡 ПРИМЕЧАНИЕ:")
        print("   • Резюме и вакансия идут в USER промпт")
        print("   • Контекст персонализации теперь в SYSTEM промпте")
        
    except Exception as e:
        print(f"❌ Ошибка форматирования данных: {e}")

def debug_vacancy_context(resume_json_path: str, vacancy_json_path: str) -> None:
    """Показывает анализ контекста вакансии."""
    print("\n" + "="*80)
    print("🎯 АНАЛИЗ КОНТЕКСТА ВАКАНСИИ")
    print("="*80)
    
    # Загружаем и парсим данные
    raw_resume = load_json_file(resume_json_path)
    raw_vacancy = load_json_file(vacancy_json_path)
    
    if not (raw_resume and raw_vacancy):
        return
    
    # Парсим данные
    resume_extractor = ResumeExtractor()
    vacancy_extractor = VacancyExtractor()
    
    parsed_resume = resume_extractor.extract_resume_info(raw_resume)
    parsed_vacancy = vacancy_extractor.extract_vacancy_info(raw_vacancy)
    
    if not (parsed_resume and parsed_vacancy):
        print("❌ Ошибка парсинга данных")
        return
    
    try:
        # Создаем генератор
        cover_letter_generator = EnhancedLLMCoverLetterGenerator()
        
        # Анализируем контекст через приватный метод
        vacancy_dict = parsed_vacancy.model_dump()
        context = cover_letter_generator._analyze_vacancy_context(vacancy_dict)
        
        print("🔸 РЕЗУЛЬТАТ АНАЛИЗА КОНТЕКСТА:")
        print(f"   • Размер компании: {context['company_size']}")
        print(f"   • Тип роли: {context['role_type']}")
        print(f"   • Название компании: {context['company_name']}")
        print(f"   • Название позиции: {context['position_title']}")
        
        print("\n🔸 ЛОГИКА ОПРЕДЕЛЕНИЯ:")
        description = vacancy_dict.get('description', '').lower()
        position = vacancy_dict.get('title', '').lower()
        
        print(f"   • Описание содержит ({len(description)} символов)")
        print(f"   • Название позиции: '{position}'")
        
        # Показываем ключевые слова для определения размера компании
        startup_words = ['стартап', 'startup', 'молодая команда']
        enterprise_words = ['крупная компания', 'enterprise', 'корпорация']
        large_words = ['международная', 'global', 'более 1000']
        
        print(f"\n🔸 КЛЮЧЕВЫЕ СЛОВА В ОПИСАНИИ:")
        for word_list, category in [(startup_words, "STARTUP"), (enterprise_words, "ENTERPRISE"), (large_words, "LARGE")]:
            found_words = [word for word in word_list if word in description]
            if found_words:
                print(f"   • {category}: {found_words}")
        
    except Exception as e:
        print(f"❌ Ошибка анализа контекста: {e}")

def debug_user_prompt(resume_json_path: str, vacancy_json_path: str) -> None:
    """Показывает пользовательский промпт сопроводительного письма."""
    print("\n" + "="*80)
    print("👤 ПОЛЬЗОВАТЕЛЬСКИЙ ПРОМПТ (USER)")
    print("="*80)
    
    # Загружаем и парсим данные
    raw_resume = load_json_file(resume_json_path)
    raw_vacancy = load_json_file(vacancy_json_path)
    
    if not (raw_resume and raw_vacancy):
        return
    
    # Парсим данные через существующие парсеры
    resume_extractor = ResumeExtractor()
    vacancy_extractor = VacancyExtractor()
    
    parsed_resume = resume_extractor.extract_resume_info(raw_resume)
    parsed_vacancy = vacancy_extractor.extract_vacancy_info(raw_vacancy)
    
    if not (parsed_resume and parsed_vacancy):
        print("❌ Ошибка парсинга данных")
        return
    
    try:
        # Создаем генератор
        cover_letter_generator = EnhancedLLMCoverLetterGenerator()
        
        # Конвертируем в dict как в реальном приложении
        resume_dict = parsed_resume.model_dump()
        vacancy_dict = parsed_vacancy.model_dump()
        
        # Используем новый метод для создания пользовательского промпта
        user_prompt = cover_letter_generator._create_user_prompt(resume_dict, vacancy_dict)
        
        print(user_prompt)
        print(f"\n📊 Длина пользовательского промпта: {len(user_prompt)} символов")
        
    except Exception as e:
        print(f"❌ Ошибка создания пользовательского промпта: {e}")

def debug_full_messages(resume_json_path: str, vacancy_json_path: str) -> None:
    """Показывает полный массив messages как он отправляется в OpenAI API."""
    print("\n" + "="*80)
    print("📨 ПОЛНЫЙ МАССИВ MESSAGES ДЛЯ OPENAI API")
    print("="*80)
    
    # Загружаем и парсим данные
    raw_resume = load_json_file(resume_json_path)
    raw_vacancy = load_json_file(vacancy_json_path)
    
    if not (raw_resume and raw_vacancy):
        return
    
    # Парсим данные
    resume_extractor = ResumeExtractor()
    vacancy_extractor = VacancyExtractor()
    
    parsed_resume = resume_extractor.extract_resume_info(raw_resume)
    parsed_vacancy = vacancy_extractor.extract_vacancy_info(raw_vacancy)
    
    if not (parsed_resume and parsed_vacancy):
        print("❌ Ошибка парсинга данных")
        return
    
    try:
        # Создаем генератор
        cover_letter_generator = EnhancedLLMCoverLetterGenerator()
        
        # Конвертируем в dict
        resume_dict = parsed_resume.model_dump()
        vacancy_dict = parsed_vacancy.model_dump()
        
        # Анализируем контекст и создаем промпты как в generate_enhanced_cover_letter
        context = cover_letter_generator._analyze_vacancy_context(vacancy_dict)
        system_prompt = cover_letter_generator._create_system_prompt(context, resume_dict, vacancy_dict)
        user_prompt = cover_letter_generator._create_user_prompt(resume_dict, vacancy_dict)
        
        # Формируем messages как в generate_enhanced_cover_letter
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
        
        # Выводим в JSON формате как отправляется в API
        print("```json")
        print(json.dumps(messages, ensure_ascii=False, indent=2))
        print("```")
        
        # Статистика
        system_length = len(system_prompt)
        user_length = len(user_prompt)
        total_length = system_length + user_length
        
        print(f"\n📊 СТАТИСТИКА MESSAGES:")
        print(f"  • Количество сообщений: {len(messages)}")
        print(f"  • Длина system промпта: {system_length} символов")
        print(f"  • Длина user промпта: {user_length} символов")
        print(f"  • Общая длина: {total_length} символов")
        
    except Exception as e:
        print(f"❌ Ошибка создания messages: {e}")

def debug_prompt_components(resume_json_path: str, vacancy_json_path: str) -> None:
    """Показывает компоненты промпта по частям для детального анализа."""
    print("\n" + "="*80)
    print("🔍 КОМПОНЕНТЫ ПРОМПТА ПО ЧАСТЯМ")
    print("="*80)
    
    # Загружаем и парсим данные
    raw_resume = load_json_file(resume_json_path)
    raw_vacancy = load_json_file(vacancy_json_path)
    
    if not (raw_resume and raw_vacancy):
        return
    
    # Парсим данные
    resume_extractor = ResumeExtractor()
    vacancy_extractor = VacancyExtractor()
    
    parsed_resume = resume_extractor.extract_resume_info(raw_resume)
    parsed_vacancy = vacancy_extractor.extract_vacancy_info(raw_vacancy)
    
    if not (parsed_resume and parsed_vacancy):
        print("❌ Ошибка парсинга данных")
        return
    
    try:
        # Создаем генератор
        cover_letter_generator = EnhancedLLMCoverLetterGenerator()
        
        # Конвертируем в dict
        resume_dict = parsed_resume.model_dump()
        vacancy_dict = parsed_vacancy.model_dump()
        
        print("🔸 1. ДАННЫЕ ПОСЛЕ ПАРСИНГА:")
        print(f"   • ResumeInfo: {type(parsed_resume)}")
        print(f"   • VacancyInfo: {type(parsed_vacancy)}")
        
        print("\n🔸 2. ДАННЫЕ ПОСЛЕ model_dump():")
        print(f"   • resume_dict ключи: {list(resume_dict.keys())}")
        print(f"   • vacancy_dict ключи: {list(vacancy_dict.keys())}")
        
        print("\n🔸 3. ИСПОЛЬЗУЕМЫЕ МЕТОДЫ КЛАССА:")
        print(f"   • cover_letter_generator._analyze_vacancy_context(vacancy_dict)")
        print(f"   • cover_letter_generator._create_system_prompt(context, resume_dict, vacancy_dict)")
        print(f"   • cover_letter_generator._create_user_prompt(resume_dict, vacancy_dict)")
        
        print("\n🔸 4. ИСПОЛЬЗУЕМЫЕ ФОРМАТТЕРЫ:")
        print(f"   • format_resume_for_cover_letter(resume_dict)")
        print(f"   • format_vacancy_for_cover_letter(vacancy_dict)")
        print(f"   • format_cover_letter_context(resume_dict, vacancy_dict) - В СИСТЕМНОМ ПРОМПТЕ")
        
        print("\n🔸 5. ПРОМПТЫ ГОТОВЫ К ОТПРАВКЕ В:")
        print(f"   • Модель: {cover_letter_generator.model}")
        print(f"   • Temperature: 0.5")
        print(f"   • Response format: EnhancedCoverLetter")
        print(f"   • API: beta.chat.completions.parse")
        
        print("\n🔸 6. СТРУКТУРА ОТВЕТА:")
        print(f"   • Модель данных: EnhancedCoverLetter")
        print(f"   • Валидация: _validate_quality()")
        print(f"   • Форматирование: format_for_email()")
        
    except Exception as e:
        print(f"❌ Ошибка анализа компонентов: {e}")

def main():
    """Основная функция для запуска отладки промптов сопроводительного письма."""
    
    # Настраиваем логирование
    setup_logging(log_level="INFO")
    
    print("📧 ОТЛАДКА ПРОМПТОВ СОПРОВОДИТЕЛЬНОГО ПИСЬМА")
    print("=" * 80)
    
    # ===============================================
    # НАСТРОЙКИ ОТЛАДКИ
    # ===============================================
    
    # ПУТИ К JSON ФАЙЛАМ
    resume_json_path = "/Users/mask/Documents/Проеты_2025/gpt_4_mini_hackaton_final/tests/test_models_res_vac/fetched_resume_6d807532ff0ed6b79f0039ed1f63386d724a62.json"      # 👈 УКАЖИТЕ ПУТЬ К РЕЗЮМЕ
    vacancy_json_path = "/Users/mask/Documents/Проеты_2025/gpt_4_mini_hackaton_final/tests/test_models_res_vac/fetched_vacancy_120234346.json"    # 👈 УКАЖИТЕ ПУТЬ К ВАКАНСИИ
    
    # ФЛАГИ УПРАВЛЕНИЯ (True/False)
    show_system_prompt = False       # 👈 Показать системный промпт
    show_formatted_data = False      # 👈 Показать форматированные данные
    show_vacancy_context = False     # 👈 Показать анализ контекста вакансии
    show_user_prompt = False         # 👈 Показать пользовательский промпт  
    show_messages = True            # 👈 Показать полный массив messages
    show_components = True          # 👈 Показать компоненты промпта
    
    # ===============================================
    
    try:
        # Системный промпт
        if show_system_prompt:
            debug_system_prompt(resume_json_path, vacancy_json_path)
        
        # Форматированные данные
        if show_formatted_data:
            debug_formatted_data(resume_json_path, vacancy_json_path)
        
        # Анализ контекста вакансии
        if show_vacancy_context:
            debug_vacancy_context(resume_json_path, vacancy_json_path)
        
        # Пользовательский промпт
        if show_user_prompt:
            debug_user_prompt(resume_json_path, vacancy_json_path)
        
        # Полный массив messages
        if show_messages:
            debug_full_messages(resume_json_path, vacancy_json_path)
        
        # Компоненты промпта
        if show_components:
            debug_prompt_components(resume_json_path, vacancy_json_path)
        
        print("\n" + "="*80)
        print("✅ ОТЛАДКА ПРОМПТОВ ЗАВЕРШЕНА!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    main()