#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для отладки парсинга резюме и вакансий из JSON файлов HeadHunter API.

Использование:
    python tests/debug_parsing.py
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Добавляем корневую директорию проекта в Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Импорты парсеров и моделей
from src.parsers.resume_extractor import ResumeExtractor
from src.parsers.vacancy_extractor import VacancyExtractor
from src.utils.logging_config import setup_logging, get_logger

def load_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """Загружает JSON файл и возвращает данные."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"❌ Ошибка загрузки {file_path}: {e}")
        return None

def debug_resume_parsing(resume_json_path: str) -> None:
    """Отладка парсинга резюме."""
    print("\n" + "="*80)
    print("🔍 ОТЛАДКА ПАРСИНГА РЕЗЮМЕ")
    print("="*80)
    
    # Загружаем JSON данные
    raw_data = load_json_file(resume_json_path)
    if not raw_data:
        return
    
    print("\n📄 ИСХОДНЫЙ JSON РЕЗЮМЕ:")
    print(json.dumps(raw_data, ensure_ascii=False, indent=2))
    
    # Создаем парсер и обрабатываем данные
    extractor = ResumeExtractor()
    parsed_resume = extractor.extract_resume_info(raw_data)
    
    if parsed_resume:
        print("\n✅ РЕЗУЛЬТАТ ПАРСИНГА РЕЗЮМЕ:")
        print(json.dumps(parsed_resume.model_dump(), ensure_ascii=False, indent=2))
    else:
        print("\n❌ Ошибка при парсинге резюме!")

def debug_vacancy_parsing(vacancy_json_path: str) -> None:
    """Отладка парсинга вакансии."""
    print("\n" + "="*80)
    print("🎯 ОТЛАДКА ПАРСИНГА ВАКАНСИИ")
    print("="*80)
    
    # Загружаем JSON данные
    raw_data = load_json_file(vacancy_json_path)
    if not raw_data:
        return
    
    print("\n📄 ИСХОДНЫЙ JSON ВАКАНСИИ:")
    print(json.dumps(raw_data, ensure_ascii=False, indent=2))
    
    # Создаем парсер и обрабатываем данные
    extractor = VacancyExtractor()
    parsed_vacancy = extractor.extract_vacancy_info(raw_data)
    
    if parsed_vacancy:
        print("\n✅ РЕЗУЛЬТАТ ПАРСИНГА ВАКАНСИИ:")
        print(json.dumps(parsed_vacancy.model_dump(), ensure_ascii=False, indent=2))
    else:
        print(f"\n❌ Ошибка при парсинге вакансии!")

def main():
    """Основная функция для запуска отладки."""
    
    # Настраиваем логирование
    setup_logging(log_level="INFO")
    
    print("🚀 СКРИПТ ОТЛАДКИ ПАРСИНГА РЕЗЮМЕ И ВАКАНСИЙ")
    print("=" * 80)
    
    # ===============================================
    # НАСТРОЙКИ ОТЛАДКИ
    # ===============================================
    
    # ПУТИ К JSON ФАЙЛАМ
    resume_json_path = "/Users/mask/Documents/Проеты_2025/gpt_4_mini_hackaton_final/tests/test_models_res_vac/fetched_resume_6d807532ff0ed6b79f0039ed1f63386d724a62.json"      # 👈 УКАЖИТЕ ПУТЬ К РЕЗЮМЕ
    vacancy_json_path = "/Users/mask/Documents/Проеты_2025/gpt_4_mini_hackaton_final/tests/test_models_res_vac/fetched_vacancy_120234346.json"    # 👈 УКАЖИТЕ ПУТЬ К ВАКАНСИИ
    
    # ФЛАГИ УПРАВЛЕНИЯ (True/False)
    debug_resume = False      # 👈 Отлаживать резюме
    debug_vacancy = True     # 👈 Отлаживать вакансию
    
    # ===============================================
    
    try:
        # Отладка резюме
        if debug_resume:
            debug_resume_parsing(resume_json_path)
        
        # Отладка вакансии  
        if debug_vacancy:
            debug_vacancy_parsing(vacancy_json_path)
        
        print("\n" + "="*80)
        print("🎉 ОТЛАДКА ЗАВЕРШЕНА!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    main()