#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Дебаггер форматтера рекомендательного письма.
Показывает как форматируются данные резюме и вакансии для cover letter.

Использование:
    python tests/debug_cover_letter_formatter.py
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
from src.llm_cover_letter.formatter import (
    format_resume_for_cover_letter,
    format_vacancy_for_cover_letter
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

def debug_resume_formatting(resume_json_path: str) -> None:
    """Отладка форматирования резюме для cover letter."""
    print("\n" + "="*80)
    print("👤 ФОРМАТИРОВАНИЕ РЕЗЮМЕ ДЛЯ РЕКОМЕНДАТЕЛЬНОГО ПИСЬМА")
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
    
    print("✅ Резюме успешно распарсено")
    
    # Форматируем для cover letter
    try:
        resume_dict = parsed_resume.model_dump()
        formatted_text = format_resume_for_cover_letter(resume_dict)
        
        print("\n📄 ОТФОРМАТИРОВАННОЕ РЕЗЮМЕ ДЛЯ COVER LETTER:")
        print("-" * 60)
        print(formatted_text)
        
        # Статистика
        print(f"📊 Длина отформатированного текста: {len(formatted_text)} символов")
        
        # Проверяем какие поля использованы
        used_fields = []
        if resume_dict.get('first_name') or resume_dict.get('last_name'):
            used_fields.append("ФИО")
        if resume_dict.get('total_experience'):
            used_fields.append("Общий опыт")
        if resume_dict.get('title'):
            used_fields.append("Специализация")
        if resume_dict.get('skills'):
            used_fields.append("Профессиональное описание")
        if resume_dict.get('skill_set'):
            used_fields.append("Технические навыки")
        if resume_dict.get('experience'):
            used_fields.append("Карьерная история")
        if resume_dict.get('certificate'):
            used_fields.append("Сертификаты")
        if resume_dict.get('languages'):
            used_fields.append("Языки")
        
        print(f"\n✅ Использованные поля ({len(used_fields)}):")
        for field in used_fields:
            print(f"  • {field}")
        
    except Exception as e:
        print(f"❌ Ошибка форматирования: {e}")

def debug_vacancy_formatting(vacancy_json_path: str) -> None:
    """Отладка форматирования вакансии для cover letter."""
    print("\n" + "="*80)
    print("🎯 ФОРМАТИРОВАНИЕ ВАКАНСИИ ДЛЯ РЕКОМЕНДАТЕЛЬНОГО ПИСЬМА")
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
    
    print("✅ Вакансия успешно распарсена")
    
    # Форматируем для cover letter
    try:
        vacancy_dict = parsed_vacancy.model_dump()
        formatted_text = format_vacancy_for_cover_letter(vacancy_dict)
        
        print("\n📄 ОТФОРМАТИРОВАННАЯ ВАКАНСИЯ ДЛЯ COVER LETTER:")
        print("-" * 60)
        print(formatted_text)
        
        # Статистика
        print(f"📊 Длина отформатированного текста: {len(formatted_text)} символов")
        
        # Проверяем какие поля использованы
        used_fields = []
        if vacancy_dict.get('name'):
            used_fields.append("Название позиции")
        if vacancy_dict.get('professional_roles'):
            used_fields.append("Профессиональные роли")
        if vacancy_dict.get('description'):
            used_fields.append("Описание позиции")
        if vacancy_dict.get('key_skills'):
            used_fields.append("Требуемые навыки")
        if vacancy_dict.get('experience'):
            used_fields.append("Требования к опыту")
        
        print(f"\n✅ Использованные поля ({len(used_fields)}):")
        for field in used_fields:
            print(f"  • {field}")
        
    except Exception as e:
        print(f"❌ Ошибка форматирования: {e}")

def main():
    """Основная функция для запуска дебаггера форматтера cover letter."""
    
    # Настраиваем логирование
    setup_logging(log_level="INFO")
    
    print("🔍 ДЕБАГГЕР РЕЗУЛЬТАТОВ ФОРМАТТЕРА COVER LETTER")
    print("=" * 80)
    
    # ===============================================
    # НАСТРОЙКИ ОТЛАДКИ
    # ===============================================
    
    # ПУТИ К JSON ФАЙЛАМ
    resume_json_path = "/Users/mask/Documents/Проеты_2025/gpt_4_mini_hackaton_final/tests/test_models_res_vac/fetched_resume_6d807532ff0ed6b79f0039ed1f63386d724a62.json"      # 👈 УКАЖИТЕ ПУТЬ К РЕЗЮМЕ
    vacancy_json_path = "/Users/mask/Documents/Проеты_2025/gpt_4_mini_hackaton_final/tests/test_models_res_vac/fetched_vacancy_120234346.json"    # 👈 УКАЖИТЕ ПУТЬ К ВАКАНСИИ
    
    # ФЛАГИ УПРАВЛЕНИЯ (True/False)
    debug_resume_fmt = True       # 👈 Отладить форматирование резюме
    debug_vacancy_fmt = True      # 👈 Отладить форматирование вакансии
    
    # ===============================================
    
    try:
        # Форматирование резюме
        if debug_resume_fmt:
            debug_resume_formatting(resume_json_path)
        
        # Форматирование вакансии
        if debug_vacancy_fmt:
            debug_vacancy_formatting(vacancy_json_path)
        
        print("\n" + "="*80)
        print("✅ ДЕБАГГЕР ФОРМАТТЕРА ЗАВЕРШЕН!")
        print("="*80)
        print("\n💡 РЕЗУЛЬТАТ:")
        print("1. Проверьте отформатированные данные резюме")
        print("2. Проверьте отформатированные данные вакансии")
        print("3. Убедитесь что все новые поля корректно обрабатываются")
        
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    main()