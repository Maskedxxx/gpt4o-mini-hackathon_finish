#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для отладки промптов GAP-анализа.
Использует готовые методы из приложения для создания промптов.

Показывает:
1. Системный промпт (system)
2. Пользовательский промпт (user) 
3. Полный массив messages для OpenAI API

Использование:
    python tests/debug_gap/debug_gap_prompts.py
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
from src.llm_gap_analyzer.llm_gap_analyzer import LLMGapAnalyzer
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

def debug_system_prompt() -> None:
    """Показывает системный промпт GAP-анализа."""
    print("\n" + "="*80)
    print("🤖 СИСТЕМНЫЙ ПРОМПТ (SYSTEM)")
    print("="*80)
    
    try:
        # Создаем экземпляр анализатора
        gap_analyzer = LLMGapAnalyzer()
        
        # Используем приватный метод для создания системного промпта
        system_prompt = gap_analyzer._create_system_prompt()
        
        print(system_prompt)
        print(f"\n📊 Длина системного промпта: {len(system_prompt)} символов")
        
    except Exception as e:
        print(f"❌ Ошибка создания системного промпта: {e}")

def debug_user_prompt(resume_json_path: str, vacancy_json_path: str) -> None:
    """Показывает пользовательский промпт GAP-анализа."""
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
        # Создаем экземпляр анализатора
        gap_analyzer = LLMGapAnalyzer()
        
        # Конвертируем в dict как в реальном приложении
        resume_dict = parsed_resume.model_dump()
        vacancy_dict = parsed_vacancy.model_dump()
        
        # Используем приватный метод для создания пользовательского промпта
        user_prompt = gap_analyzer._create_user_prompt(resume_dict, vacancy_dict)
        
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
        # Создаем экземпляр анализатора
        gap_analyzer = LLMGapAnalyzer()
        
        # Конвертируем в dict
        resume_dict = parsed_resume.model_dump()
        vacancy_dict = parsed_vacancy.model_dump()
        
        # Создаем промпты как в gap_analysis методе
        system_prompt = gap_analyzer._create_system_prompt()
        user_prompt = gap_analyzer._create_user_prompt(resume_dict, vacancy_dict)
        
        # Формируем messages как в gap_analysis
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
        total_length = len(system_prompt) + len(user_prompt)
        print("\n📊 СТАТИСТИКА MESSAGES:")
        print(f"  • Количество сообщений: {len(messages)}")
        print(f"  • Длина system промпта: {len(system_prompt)} символов")
        print(f"  • Длина user промпта: {len(user_prompt)} символов")
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
        # Создаем экземпляр анализатора
        gap_analyzer = LLMGapAnalyzer()
        
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
        print("   • gap_analyzer._create_system_prompt()")
        print("   • gap_analyzer._create_user_prompt(resume_dict, vacancy_dict)")
        
        print("\n🔸 4. ПРОМПТЫ ГОТОВЫ К ОТПРАВКЕ В:")
        print(f"   • Модель: {gap_analyzer.model}")
        print("   • Temperature: 0.2")
        print("   • Response format: EnhancedResumeTailoringAnalysis")
        
    except Exception as e:
        print(f"❌ Ошибка анализа компонентов: {e}")

def main():
    """Основная функция для запуска отладки промптов GAP-анализа."""
    
    # Настраиваем логирование
    setup_logging(log_level="INFO")
    
    print("🔍 ОТЛАДКА ПРОМПТОВ GAP-АНАЛИЗА")
    print("=" * 80)
    
    # ===============================================
    # НАСТРОЙКИ ОТЛАДКИ
    # ===============================================
    
    # ПУТИ К JSON ФАЙЛАМ
    resume_json_path = "/Users/mask/Documents/Проеты_2025/gpt_4_mini_hackaton_final/tests/test_models_res_vac/fetched_resume_6d807532ff0ed6b79f0039ed1f63386d724a62.json"    # 👈 УКАЖИТЕ ПУТЬ К РЕЗЮМЕ
    vacancy_json_path = "/Users/mask/Documents/Проеты_2025/gpt_4_mini_hackaton_final/tests/test_models_res_vac/fetched_vacancy_120234346.json"    # 👈 УКАЖИТЕ ПУТЬ К ВАКАНСИИ
    
    # ФЛАГИ УПРАВЛЕНИЯ (True/False)
    show_system_prompt = True      # 👈 Показать системный промпт
    show_user_prompt = True        # 👈 Показать пользовательский промпт  
    show_messages = True           # 👈 Показать полный массив messages
    show_components = True         # 👈 Показать компоненты промпта
    
    # ===============================================
    
    try:
        # Системный промпт
        if show_system_prompt:
            debug_system_prompt()
        
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