#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Дебаггер хендлера сопроводительного письма для Telegram.
Показывает как форматируются сообщения для пользователя.

Использует готовый результат генерации письма из JSON файла.
Два режима: с ограничениями и без ограничений.

Использование:
    python tests/debug_cover_letter/debug_cover_letter_handler.py
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Добавляем корневую директорию проекта в Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Импорты из приложения
from src.models.cover_letter_models import EnhancedCoverLetter
from src.utils.logging_config import setup_logging

def load_cover_letter_result(file_path: str) -> Optional[EnhancedCoverLetter]:
    """Загружает результат генерации сопроводительного письма из JSON файла."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Создаем Pydantic объект из JSON
        cover_letter = EnhancedCoverLetter.model_validate(data)
        print(f"✅ Результат генерации сопроводительного письма загружен из {file_path}")
        return cover_letter
        
    except FileNotFoundError:
        print(f"❌ Файл {file_path} не найден")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка парсинга JSON: {e}")
        return None
    except Exception as e:
        print(f"❌ Ошибка создания объекта: {e}")
        return None

# Убираем функции лимитов - в хендлере их нет

def show_all_formatted_messages(cover_letter: EnhancedCoverLetter):
    """Показывает все отформатированные сообщения как они будут отправлены пользователю."""
    
    try:
        # Импортируем функции форматирования из хендлера
        from src.tg_bot.handlers.spec_handlers.cover_letter_handler import (
            format_enhanced_cover_letter_preview,
            format_skills_match_section,
            format_cover_letter_text,
            format_improvement_tips
        )
        
        limit_status = "ПОЛНОЕ ОТОБРАЖЕНИЕ"
        print(f"\n{'='*80}")
        print(f"📱 СООБЩЕНИЯ ДЛЯ ПОЛЬЗОВАТЕЛЯ ({limit_status})")
        print(f"{'='*80}")
        
        # Часть 1: Предварительный просмотр с оценками
        print("\n🔹 СООБЩЕНИЕ #1: ПРЕДВАРИТЕЛЬНЫЙ ПРОСМОТР")
        print("-" * 60)
        try:
            preview = format_enhanced_cover_letter_preview(cover_letter)
            print(preview)
        except Exception as e:
            print(f"❌ Ошибка форматирования предварительного просмотра: {e}")
        
        # Часть 2: Анализ соответствия навыков
        print("\n🔹 СООБЩЕНИЕ #2: АНАЛИЗ СООТВЕТСТВИЯ НАВЫКОВ")
        print("-" * 60)
        try:
            skills_match = format_skills_match_section(cover_letter)
            print(skills_match)
        except Exception as e:
            print(f"❌ Ошибка форматирования анализа навыков: {e}")
        
        # Часть 3: Текст письма
        print("\n🔹 СООБЩЕНИЕ #3: ПОЛНЫЙ ТЕКСТ ПИСЬМА")
        print("-" * 60)
        try:
            letter_text = format_cover_letter_text(cover_letter)
            print(letter_text)
            print(f"\n📊 Длина текста письма: {len(letter_text)} символов")
            if len(letter_text) > 4000:
                print("⚠️ Текст превышает 4000 символов - будет разбит на части")
        except Exception as e:
            print(f"❌ Ошибка форматирования текста письма: {e}")
        
        # Часть 4: Рекомендации по улучшению
        print("\n🔹 СООБЩЕНИЕ #4: РЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ")
        print("-" * 60)
        try:
            improvements = format_improvement_tips(cover_letter)
            if improvements:
                print(improvements)
            else:
                print("✅ Рекомендации отсутствуют - письмо готово к отправке!")
        except Exception as e:
            print(f"❌ Ошибка форматирования рекомендаций: {e}")
            
    except ImportError as e:
        print(f"❌ Не удалось импортировать функции хендлера: {e}")
        print("💡 Возможно хендлер еще не создан или имеет другие названия функций")
        
        # Показываем базовое форматирование
        show_basic_formatting(cover_letter)

def show_basic_formatting(cover_letter: EnhancedCoverLetter):
    """Показывает базовое форматирование если хендлер недоступен."""
    print("\n📧 БАЗОВОЕ ФОРМАТИРОВАНИЕ ПИСЬМА")
    print("="*80)
    
    print("🔸 МЕТА-ИНФОРМАЦИЯ:")
    print(f"Тип роли: {cover_letter.role_type}")
    print(f"Компания: {cover_letter.company_context.company_name}")
    print(f"Размер компании: {cover_letter.company_context.company_size}")
    print(f"Длина письма: {cover_letter.estimated_length}")
    
    print("\n🔸 ОЦЕНКИ КАЧЕСТВА:")
    print(f"Персонализация: {cover_letter.personalization_score}/10")
    print(f"Профессиональность: {cover_letter.professional_tone_score}/10")
    print(f"Релевантность: {cover_letter.relevance_score}/10")
    
    print("\n🔸 АНАЛИЗ НАВЫКОВ:")
    print(f"Совпадающие навыки: {', '.join(cover_letter.skills_match.matched_skills)}")
    
    print("\n🔸 ПОЛНОЕ ПИСЬМО:")
    print(f"Тема: {cover_letter.subject_line}")
    print(f"Приветствие: {cover_letter.personalized_greeting}")
    print(f"Зацепка: {cover_letter.opening_hook}")
    print(f"Интерес к компании: {cover_letter.company_interest}")
    print(f"Опыт: {cover_letter.relevant_experience}")
    print(f"Ценность: {cover_letter.value_demonstration}")
    if cover_letter.growth_mindset:
        print(f"Развитие: {cover_letter.growth_mindset}")
    print(f"Завершение: {cover_letter.professional_closing}")
    print(f"Подпись: {cover_letter.signature}")

def show_statistics(cover_letter: EnhancedCoverLetter):
    """Показывает статистику по результату генерации письма."""
    print(f"\n{'='*80}")
    print("📊 СТАТИСТИКА РЕЗУЛЬТАТА ГЕНЕРАЦИИ ПИСЬМА")
    print(f"{'='*80}")
    
    print("📋 ОСНОВНЫЕ ПОКАЗАТЕЛИ:")
    print(f"  • Тип роли: {cover_letter.role_type}")
    print(f"  • Размер компании: {cover_letter.company_context.company_size}")
    print(f"  • Оценка длины: {cover_letter.estimated_length}")
    
    print("\n🎯 ОЦЕНКИ КАЧЕСТВА:")
    print(f"  • Персонализация: {cover_letter.personalization_score}/10")
    print(f"  • Профессиональность: {cover_letter.professional_tone_score}/10")
    print(f"  • Релевантность: {cover_letter.relevance_score}/10")
    avg_score = (cover_letter.personalization_score + cover_letter.professional_tone_score + cover_letter.relevance_score) / 3
    print(f"  • Средняя оценка: {avg_score:.1f}/10")
    
    print("\n📏 ДЛИНА СЕКЦИЙ ПИСЬМА:")
    print(f"  • Тема письма: {len(cover_letter.subject_line)} символов")
    print(f"  • Приветствие: {len(cover_letter.personalized_greeting)} символов")
    print(f"  • Зацепка: {len(cover_letter.opening_hook)} символов")
    print(f"  • Интерес к компании: {len(cover_letter.company_interest)} символов")
    print(f"  • Релевантный опыт: {len(cover_letter.relevant_experience)} символов")
    print(f"  • Демонстрация ценности: {len(cover_letter.value_demonstration)} символов")
    if cover_letter.growth_mindset:
        print(f"  • Готовность к развитию: {len(cover_letter.growth_mindset)} символов")
    print(f"  • Завершение: {len(cover_letter.professional_closing)} символов")
    print(f"  • Подпись: {len(cover_letter.signature)} символов")
    
    # Общая длина письма
    total_length = (
        len(cover_letter.opening_hook) + 
        len(cover_letter.company_interest) + 
        len(cover_letter.relevant_experience) + 
        len(cover_letter.value_demonstration) + 
        len(cover_letter.professional_closing) +
        (len(cover_letter.growth_mindset) if cover_letter.growth_mindset else 0)
    )
    print(f"  • Общая длина основного текста: {total_length} символов")
    
    print("\n🔧 АНАЛИЗ СООТВЕТСТВИЯ:")
    print(f"  • Совпадающих навыков: {len(cover_letter.skills_match.matched_skills)}")
    if cover_letter.skills_match.matched_skills:
        print(f"    - Навыки: {', '.join(cover_letter.skills_match.matched_skills)}")
    
    print(f"  • Длина релевантного опыта: {len(cover_letter.skills_match.relevant_experience)} символов")
    
    if cover_letter.skills_match.quantified_achievement:
        print(f"  • Длина количественного достижения: {len(cover_letter.skills_match.quantified_achievement)} символов")
    
    print("\n💡 РЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ:")
    print(f"  • Количество рекомендаций: {len(cover_letter.improvement_suggestions)}")
    for i, suggestion in enumerate(cover_letter.improvement_suggestions, 1):
        print(f"    {i}. {suggestion[:100]}{'...' if len(suggestion) > 100 else ''}")
    
    print("\n🏢 КОНТЕКСТ КОМПАНИИ:")
    if cover_letter.company_context.company_culture:
        print(f"  • Культура компании: {cover_letter.company_context.company_culture[:100]}{'...' if len(cover_letter.company_context.company_culture) > 100 else ''}")
    if cover_letter.company_context.product_info:
        print(f"  • Информация о продукте: {cover_letter.company_context.product_info[:100]}{'...' if len(cover_letter.company_context.product_info) > 100 else ''}")

# Убираем показ лимитов - в хендлере их нет

def main():
    """Основная функция для запуска дебаггера хендлера сопроводительного письма."""
    
    # Настраиваем логирование
    setup_logging(log_level="INFO")
    
    print("📧 ДЕБАГГЕР ХЕНДЛЕРА СОПРОВОДИТЕЛЬНОГО ПИСЬМА")
    print("=" * 80)
    
    # ===============================================
    # НАСТРОЙКИ ОТЛАДКИ
    # ===============================================
    
    # ПУТЬ К JSON ФАЙЛУ С РЕЗУЛЬТАТОМ ГЕНЕРАЦИИ ПИСЬМА
    cover_letter_result_json_path = "/Users/mask/Documents/Проеты_2025/gpt_4_mini_hackaton_final/tests/debug_response_cover_letter.json"    # 👈 УКАЖИТЕ ПУТЬ К JSON РЕЗУЛЬТАТУ
    
    # ФЛАГИ УПРАВЛЕНИЯ (True/False)
    show_messages = True           # 👈 Показать отформатированные сообщения
    show_stats = True              # 👈 Показать статистику результата
    
    # ===============================================
    
    try:
        # Загружаем результат генерации письма
        cover_letter = load_cover_letter_result(cover_letter_result_json_path)
        if not cover_letter:
            return
        
        # Показываем статистику
        if show_stats:
            show_statistics(cover_letter)
        
        # Показываем отформатированные сообщения
        if show_messages:
            show_all_formatted_messages(cover_letter)
        
        print(f"\n{'='*80}")
        print("✅ ДЕБАГГЕР ХЕНДЛЕРА ЗАВЕРШЕН!")
        print("="*80)
        print("\n💡 РЕКОМЕНДАЦИИ:")
        print("1. Проверьте что все секции письма корректно форматируются")
        print("2. Убедитесь что HTML теги отображаются правильно в Telegram")
        print("3. Проверьте что письмо не превышает лимиты сообщений Telegram")
        print("4. Убедитесь что рекомендации по улучшению полезны")
        print("5. Проверьте что письмо корректно форматируется для копирования")
        
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()