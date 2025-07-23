#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для отладки форматтера GAP-анализа.
Показывает только результат форматирования резюме и вакансии.

Использование:
    python tests/debug_gap/debug_formatter.py
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Добавляем корневую директорию проекта в Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Импорты
from src.parsers.resume_extractor import ResumeExtractor
from src.parsers.vacancy_extractor import VacancyExtractor
from src.llm_gap_analyzer.formatter import format_resume_data, format_vacancy_data
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

def debug_resume_formatter(resume_json_path: str) -> None:
    """Показывает результат форматирования резюме."""
    print("\n" + "="*80)
    print("📄 РЕЗУЛЬТАТ ФОРМАТИРОВАНИЯ РЕЗЮМЕ")
    print("="*80)
    
    # Загружаем и парсим резюме
    raw_data = load_json_file(resume_json_path)
    if not raw_data:
        return
    
    extractor = ResumeExtractor()
    parsed_resume = extractor.extract_resume_info(raw_data)
    
    if not parsed_resume:
        print("❌ Ошибка парсинга резюме!")
        return
    
    # Форматируем и выводим
    try:
        resume_dict = parsed_resume.model_dump()
        formatted_text = format_resume_data(resume_dict)
        print("Результат фнукции форматировании ниже")
        print(formatted_text)
        
    except Exception as e:
        print(f"❌ Ошибка форматирования: {e}")

def debug_vacancy_formatter(vacancy_json_path: str) -> None:
    """Показывает результат форматирования вакансии."""
    print("\n" + "="*80)
    print("🎯 РЕЗУЛЬТАТ ФОРМАТИРОВАНИЯ ВАКАНСИИ")
    print("="*80)
    
    # Загружаем и парсим вакансию
    raw_data = load_json_file(vacancy_json_path)
    if not raw_data:
        return
    
    extractor = VacancyExtractor()
    parsed_vacancy = extractor.extract_vacancy_info(raw_data)
    
    if not parsed_vacancy:
        print("❌ Ошибка парсинга вакансии!")
        return
    
    # Форматируем и выводим
    try:
        vacancy_dict = parsed_vacancy.model_dump()
        formatted_text = format_vacancy_data(vacancy_dict)
        print(formatted_text)
        
    except Exception as e:
        print(f"❌ Ошибка форматирования: {e}")



def main():
    """Основная функция для запуска отладки форматтера."""
    
    # Настраиваем логирование
    setup_logging(log_level="INFO")
    
    print("🔍 ОТЛАДКА РЕЗУЛЬТАТОВ ФОРМАТТЕРА")
    print("=" * 80)
    
    # ===============================================
    # НАСТРОЙКИ ОТЛАДКИ
    # ===============================================
    
    # ПУТИ К JSON ФАЙЛАМ
    resume_json_path = "/Users/mask/Documents/Проеты_2025/gpt_4_mini_hackaton_final/tests/test_models_res_vac/resume_nlp.json"      # 👈 УКАЖИТЕ ПУТЬ К РЕЗЮМЕ
    vacancy_json_path = "/Users/mask/Documents/Проеты_2025/gpt_4_mini_hackaton_final/tests/test_models_res_vac/fetched_vacancy_120234346.json"    # 👈 УКАЖИТЕ ПУТЬ К ВАКАНСИИ
    
    # ФЛАГИ УПРАВЛЕНИЯ (True/False)
    show_resume = True        # 👈 Показать форматированное резюме
    show_vacancy = False       # 👈 Показать форматированную вакансию
    
    # ===============================================
    
    try:
        # Форматированное резюме
        if show_resume:
            debug_resume_formatter(resume_json_path)
        
        # Форматированная вакансия
        if show_vacancy:
            debug_vacancy_formatter(vacancy_json_path)
        
        print("\n" + "="*80)
        print("✅ ОТЛАДКА ЗАВЕРШЕНА!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    main()