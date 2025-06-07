#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Дебаггер хендлера GAP-анализа для Telegram.
Показывает как форматируются сообщения для пользователя.

Использует готовый результат GAP-анализа из JSON файла.
Два режима: с ограничениями и без ограничений.

Использование:
    python tests/debug_gap/debug_gap_handler.py
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Добавляем корневую директорию проекта в Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Импорты из приложения
from src.models.gap_analysis_models import EnhancedResumeTailoringAnalysis
from src.utils.logging_config import setup_logging

def load_gap_analysis_result(file_path: str) -> Optional[EnhancedResumeTailoringAnalysis]:
    """Загружает результат GAP-анализа из JSON файла."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Создаем Pydantic объект из JSON
        gap_result = EnhancedResumeTailoringAnalysis.model_validate(data)
        print(f"✅ Результат GAP-анализа загружен из {file_path}")
        return gap_result
        
    except FileNotFoundError:
        print(f"❌ Файл {file_path} не найден")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка парсинга JSON: {e}")
        return None
    except Exception as e:
        print(f"❌ Ошибка создания объекта: {e}")
        return None

def modify_display_limits_for_unlimited():
    """Временно изменяет лимиты отображения для показа без ограничений."""
    # Импортируем модуль хендлера для изменения его конфигурации
    from src.tg_bot.handlers.spec_handlers import gap_analyzer_handler
    
    # Сохраняем оригинальные лимиты
    original_limits = gap_analyzer_handler.DISPLAY_LIMITS.copy()
    original_symbols = gap_analyzer_handler.DISPLAY_SYMBOLS.copy()
    
    # Устанавливаем большие лимиты (фактически убираем ограничения)
    gap_analyzer_handler.DISPLAY_LIMITS.update({
        'max_requirements_per_group': 999,    # Показать все требования
        'max_recommendations_per_group': 999, # Показать все рекомендации
        'max_strengths_display': 999,         # Показать все сильные стороны
        'max_gaps_display': 999,              # Показать все пробелы
        'requirement_text_length': 999,       # Полный текст требований
        'gap_description_length': 999,        # Полное описание пробелов
        'example_wording_length': 999,        # Полные примеры
        'recommendation_issue_length': 999,   # Полные описания проблем
    })
    
    # Убираем многоточие
    gap_analyzer_handler.DISPLAY_SYMBOLS['ellipsis'] = ''
    
    return original_limits, original_symbols

def restore_display_limits(original_limits, original_symbols):
    """Восстанавливает оригинальные лимиты отображения."""
    from src.tg_bot.handlers.spec_handlers import gap_analyzer_handler
    
    gap_analyzer_handler.DISPLAY_LIMITS.update(original_limits)
    gap_analyzer_handler.DISPLAY_SYMBOLS.update(original_symbols)

def show_all_formatted_messages(gap_result: EnhancedResumeTailoringAnalysis, with_limits: bool = True):
    """Показывает все отформатированные сообщения как они будут отправлены пользователю."""
    
    # Импортируем функции форматирования из хендлера
    from src.tg_bot.handlers.spec_handlers.gap_analyzer_handler import (
        format_enhanced_gap_analysis_preview,
        format_primary_screening,
        format_requirements_analysis,
        format_quality_assessment,
        format_recommendations,
        format_final_conclusion
    )
    
    limit_status = "С ОГРАНИЧЕНИЯМИ" if with_limits else "БЕЗ ОГРАНИЧЕНИЙ"
    print(f"\n{'='*80}")
    print(f"📱 СООБЩЕНИЯ ДЛЯ ПОЛЬЗОВАТЕЛЯ ({limit_status})")
    print(f"{'='*80}")
    
    # Часть 1: Краткий обзор
    print(f"\n🔹 СООБЩЕНИЕ #1: КРАТКИЙ ОБЗОР")
    print("-" * 60)
    preview = format_enhanced_gap_analysis_preview(gap_result)
    print(preview)
    
    # Часть 2: Первичный скрининг
    print(f"\n🔹 СООБЩЕНИЕ #2: ПЕРВИЧНЫЙ СКРИНИНГ")
    print("-" * 60)
    screening = format_primary_screening(gap_result)
    print(screening)
    
    # Часть 3: Анализ требований
    print(f"\n🔹 СООБЩЕНИЕ #3: АНАЛИЗ ТРЕБОВАНИЙ")
    print("-" * 60)
    requirements = format_requirements_analysis(gap_result)
    if requirements:
        print(requirements)
    else:
        print("❌ Анализ требований пуст")
    
    # Часть 4: Оценка качества
    print(f"\n🔹 СООБЩЕНИЕ #4: ОЦЕНКА КАЧЕСТВА")
    print("-" * 60)
    quality = format_quality_assessment(gap_result)
    print(quality)
    
    # Часть 5: Рекомендации
    print(f"\n🔹 СООБЩЕНИЕ #5: РЕКОМЕНДАЦИИ")
    print("-" * 60)
    recommendations = format_recommendations(gap_result)
    print(recommendations)
    
    # Часть 6: Итоговые выводы
    print(f"\n🔹 СООБЩЕНИЕ #6: ИТОГОВЫЕ ВЫВОДЫ")
    print("-" * 60)
    conclusion = format_final_conclusion(gap_result)
    print(conclusion)

def show_statistics(gap_result: EnhancedResumeTailoringAnalysis):
    """Показывает статистику по результату GAP-анализа."""
    print(f"\n{'='*80}")
    print(f"📊 СТАТИСТИКА РЕЗУЛЬТАТА GAP-АНАЛИЗА")
    print(f"{'='*80}")
    
    print(f"📋 КОЛИЧЕСТВО ЭЛЕМЕНТОВ:")
    print(f"  • Всего требований: {len(gap_result.requirements_analysis)}")
    
    # Группировка требований по типам
    must_have = [r for r in gap_result.requirements_analysis if r.requirement_type == "MUST_HAVE"]
    nice_to_have = [r for r in gap_result.requirements_analysis if r.requirement_type == "NICE_TO_HAVE"]
    bonus = [r for r in gap_result.requirements_analysis if r.requirement_type == "BONUS"]
    
    print(f"    - MUST_HAVE: {len(must_have)}")
    print(f"    - NICE_TO_HAVE: {len(nice_to_have)}")
    print(f"    - BONUS: {len(bonus)}")
    
    print(f"  • Критичных рекомендаций: {len(gap_result.critical_recommendations)}")
    print(f"  • Важных рекомендаций: {len(gap_result.important_recommendations)}")
    print(f"  • Желательных рекомендаций: {len(gap_result.optional_recommendations)}")
    print(f"  • Сильных сторон: {len(gap_result.key_strengths)}")
    print(f"  • Основных пробелов: {len(gap_result.major_gaps)}")
    
    print(f"\n📏 ДЛИНА ТЕКСТОВ:")
    
    # Анализ длины текстов
    if gap_result.requirements_analysis:
        req_lengths = [len(r.requirement_text) for r in gap_result.requirements_analysis]
        print(f"  • Требования - макс: {max(req_lengths)}, мин: {min(req_lengths)}, среднее: {sum(req_lengths)//len(req_lengths)}")
        
        gap_descriptions = [len(r.gap_description or "") for r in gap_result.requirements_analysis if r.gap_description]
        if gap_descriptions:
            print(f"  • Описания пробелов - макс: {max(gap_descriptions)}, мин: {min(gap_descriptions)}, среднее: {sum(gap_descriptions)//len(gap_descriptions)}")
    
    if gap_result.critical_recommendations:
        issue_lengths = [len(r.issue_description) for r in gap_result.critical_recommendations]
        print(f"  • Описания проблем - макс: {max(issue_lengths)}, мин: {min(issue_lengths)}, среднее: {sum(issue_lengths)//len(issue_lengths)}")
    
    print(f"\n🎯 КЛЮЧЕВЫЕ ПОКАЗАТЕЛИ:")
    print(f"  • Процент соответствия: {gap_result.overall_match_percentage}%")
    print(f"  • Рекомендация по найму: {gap_result.hiring_recommendation}")
    print(f"  • Общее впечатление: {gap_result.quality_assessment.overall_impression}")
    print(f"  • Результат скрининга: {gap_result.primary_screening.overall_screening_result}")

def show_current_limits():
    """Показывает текущие лимиты отображения."""
    from src.tg_bot.handlers.spec_handlers.gap_analyzer_handler import DISPLAY_LIMITS, DISPLAY_SYMBOLS
    
    print(f"\n{'='*80}")
    print(f"⚙️ ТЕКУЩИЕ ЛИМИТЫ ОТОБРАЖЕНИЯ")
    print(f"{'='*80}")
    
    print(f"🔢 ЛИМИТЫ КОЛИЧЕСТВА:")
    print(f"  • Требований в группе: {DISPLAY_LIMITS['max_requirements_per_group']}")
    print(f"  • Рекомендаций в группе: {DISPLAY_LIMITS['max_recommendations_per_group']}")
    print(f"  • Сильных сторон: {DISPLAY_LIMITS['max_strengths_display']}")
    print(f"  • Пробелов: {DISPLAY_LIMITS['max_gaps_display']}")
    
    print(f"\n✂️ ЛИМИТЫ ДЛИНЫ ТЕКСТА:")
    print(f"  • Текст требования: {DISPLAY_LIMITS['requirement_text_length']} символов")
    print(f"  • Описание пробела: {DISPLAY_LIMITS['gap_description_length']} символов")
    print(f"  • Пример формулировки: {DISPLAY_LIMITS['example_wording_length']} символов")
    print(f"  • Описание проблемы: {DISPLAY_LIMITS['recommendation_issue_length']} символов")
    
    print(f"\n🎨 СИМВОЛЫ ОТОБРАЖЕНИЯ:")
    print(f"  • Заполненный блок: '{DISPLAY_SYMBOLS['progress_filled']}'")
    print(f"  • Пустой блок: '{DISPLAY_SYMBOLS['progress_empty']}'")
    print(f"  • Многоточие: '{DISPLAY_SYMBOLS['ellipsis']}'")

def main():
    """Основная функция для запуска дебаггера хендлера GAP-анализа."""
    
    # Настраиваем логирование
    setup_logging(log_level="INFO")
    
    print("🔍 ДЕБАГГЕР ХЕНДЛЕРА GAP-АНАЛИЗА")
    print("=" * 80)
    
    # ===============================================
    # НАСТРОЙКИ ОТЛАДКИ
    # ===============================================
    
    # ПУТЬ К JSON ФАЙЛУ С РЕЗУЛЬТАТОМ GAP-АНАЛИЗА
    gap_result_json_path = "/Users/mask/Documents/Проеты_2025/gpt_4_mini_hackaton_final/tests/debug_response_gap.json"    # 👈 УКАЖИТЕ ПУТЬ К JSON РЕЗУЛЬТАТУ
    
    # ФЛАГИ УПРАВЛЕНИЯ (True/False)
    show_with_limits = True        # 👈 Показать с ограничениями (как в реальном приложении)
    show_without_limits = True     # 👈 Показать без ограничений (полный текст)
    show_stats = True              # 👈 Показать статистику результата
    show_limits_config = True      # 👈 Показать текущие лимиты
    
    # ===============================================
    
    try:
        # Загружаем результат GAP-анализа
        gap_result = load_gap_analysis_result(gap_result_json_path)
        if not gap_result:
            return
        
        # Показываем статистику
        if show_stats:
            show_statistics(gap_result)
        
        # Показываем текущие лимиты
        if show_limits_config:
            show_current_limits()
        
        # Показываем сообщения С ограничениями (как в реальном приложении)
        if show_with_limits:
            show_all_formatted_messages(gap_result, with_limits=True)
        
        # Показываем сообщения БЕЗ ограничений (полный текст)
        if show_without_limits:
            # Временно убираем ограничения
            original_limits, original_symbols = modify_display_limits_for_unlimited()
            
            try:
                show_all_formatted_messages(gap_result, with_limits=False)
            finally:
                # Восстанавливаем оригинальные лимиты
                restore_display_limits(original_limits, original_symbols)
        
        print(f"\n{'='*80}")
        print("✅ ДЕБАГГЕР ХЕНДЛЕРА ЗАВЕРШЕН!")
        print("="*80)
        print("\n💡 РЕКОМЕНДАЦИИ:")
        print("1. Сравните сообщения с ограничениями и без ограничений")
        print("2. Убедитесь что важная информация не обрезается")
        print("3. Проверьте что сообщения читаемы в Telegram")
        print("4. При необходимости скорректируйте лимиты в DISPLAY_LIMITS")
        
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    main()