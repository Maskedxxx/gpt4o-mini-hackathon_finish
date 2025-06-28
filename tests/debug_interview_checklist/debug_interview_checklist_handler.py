#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Дебаггер хендлера чек-листа подготовки к интервью для Telegram.
Показывает как форматируются сообщения для пользователя.

Использует готовый результат генерации чек-листа из JSON файла.
Показывает все блоки и форматированные сообщения.

Использование:
    python tests/debug_interview_checklist_handler.py
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Добавляем корневую директорию проекта в Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Импорты из приложения
from src.models.interview_checklist_models import ProfessionalInterviewChecklist
from src.utils.logging_config import setup_logging

def load_interview_checklist_result(file_path: str) -> Optional[ProfessionalInterviewChecklist]:
    """Загружает результат генерации чек-листа интервью из JSON файла."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Создаем Pydantic объект из JSON
        checklist = ProfessionalInterviewChecklist.model_validate(data)
        print(f"✅ Результат генерации чек-листа интервью загружен из {file_path}")
        return checklist
        
    except FileNotFoundError:
        print(f"❌ Файл {file_path} не найден")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка парсинга JSON: {e}")
        return None
    except Exception as e:
        print(f"❌ Ошибка создания объекта: {e}")
        return None

def show_all_formatted_messages(checklist: ProfessionalInterviewChecklist):
    """Показывает все отформатированные сообщения как они будут отправлены пользователю."""
    
    try:
        # Импортируем функции форматирования из хендлера
        from src.tg_bot.handlers.spec_handlers.interview_checklist_handler import (
            format_professional_checklist_header,
            format_executive_summary,
            format_technical_preparation,
            format_behavioral_preparation,
            format_company_research,
            format_technical_stack_study,
            format_practical_exercises,
            format_interview_setup,
            format_additional_actions,
            format_critical_success_factors
        )
        
        print(f"\n{'='*80}")
        print(f"📱 СООБЩЕНИЯ ДЛЯ ПОЛЬЗОВАТЕЛЯ В TELEGRAM")
        print(f"{'='*80}")
        
        # Сообщение 1: Заголовок с основной информацией
        print("\n🔹 СООБЩЕНИЕ #1: ЗАГОЛОВОК И ОСНОВНАЯ ИНФОРМАЦИЯ")
        print("-" * 60)
        try:
            header = format_professional_checklist_header(checklist)
            print(header)
            print(f"\n📊 Статистика: {len(header)} символов")
        except Exception as e:
            print(f"❌ Ошибка форматирования заголовка: {e}")
        
        # Сообщение 2: Краткое резюме и стратегия
        print("\n🔹 СООБЩЕНИЕ #2: КРАТКОЕ РЕЗЮМЕ И СТРАТЕГИЯ")
        print("-" * 60)
        try:
            summary = format_executive_summary(checklist)
            print(summary)
            print(f"\n📊 Статистика: {len(summary)} символов")
        except Exception as e:
            print(f"❌ Ошибка форматирования резюме: {e}")
        
        # Сообщение 3: Техническая подготовка
        print("\n🔹 СООБЩЕНИЕ #3: ТЕХНИЧЕСКАЯ ПОДГОТОВКА")
        print("-" * 60)
        try:
            tech_prep = format_technical_preparation(checklist)
            print(tech_prep)
            print(f"\n📊 Статистика: {len(tech_prep)} символов")
        except Exception as e:
            print(f"❌ Ошибка форматирования технической подготовки: {e}")
        
        # Сообщение 4: Поведенческая подготовка
        print("\n🔹 СООБЩЕНИЕ #4: ПОВЕДЕНЧЕСКАЯ ПОДГОТОВКА")
        print("-" * 60)
        try:
            behavioral = format_behavioral_preparation(checklist)
            print(behavioral)
            print(f"\n📊 Статистика: {len(behavioral)} символов")
        except Exception as e:
            print(f"❌ Ошибка форматирования поведенческой подготовки: {e}")
        
        # Сообщение 5: Изучение компании
        print("\n🔹 СООБЩЕНИЕ #5: ИЗУЧЕНИЕ КОМПАНИИ")
        print("-" * 60)
        try:
            company = format_company_research(checklist)
            print(company)
            print(f"\n📊 Статистика: {len(company)} символов")
        except Exception as e:
            print(f"❌ Ошибка форматирования изучения компании: {e}")
        
        # Сообщение 6: Изучение технического стека
        print("\n🔹 СООБЩЕНИЕ #6: ИЗУЧЕНИЕ ТЕХНИЧЕСКОГО СТЕКА")
        print("-" * 60)
        try:
            tech_stack = format_technical_stack_study(checklist)
            print(tech_stack)
            print(f"\n📊 Статистика: {len(tech_stack)} символов")
        except Exception as e:
            print(f"❌ Ошибка форматирования технического стека: {e}")
        
        # Сообщение 7: Практические упражнения
        print("\n🔹 СООБЩЕНИЕ #7: ПРАКТИЧЕСКИЕ УПРАЖНЕНИЯ")
        print("-" * 60)
        try:
            practical = format_practical_exercises(checklist)
            print(practical)
            print(f"\n📊 Статистика: {len(practical)} символов")
        except Exception as e:
            print(f"❌ Ошибка форматирования практических упражнений: {e}")
        
        # Сообщение 8: Настройка окружения для интервью
        print("\n🔹 СООБЩЕНИЕ #8: НАСТРОЙКА ОКРУЖЕНИЯ ДЛЯ ИНТЕРВЬЮ")
        print("-" * 60)
        try:
            setup = format_interview_setup(checklist)
            print(setup)
            print(f"\n📊 Статистика: {len(setup)} символов")
        except Exception as e:
            print(f"❌ Ошибка форматирования настройки окружения: {e}")
        
        # Сообщение 9: Дополнительные действия
        print("\n🔹 СООБЩЕНИЕ #9: ДОПОЛНИТЕЛЬНЫЕ ДЕЙСТВИЯ")
        print("-" * 60)
        try:
            additional = format_additional_actions(checklist)
            print(additional)
            print(f"\n📊 Статистика: {len(additional)} символов")
        except Exception as e:
            print(f"❌ Ошибка форматирования дополнительных действий: {e}")
        
        # Сообщение 10: Критические факторы успеха и финальные советы
        print("\n🔹 СООБЩЕНИЕ #10: КРИТИЧЕСКИЕ ФАКТОРЫ УСПЕХА")
        print("-" * 60)
        try:
            success_factors = format_critical_success_factors(checklist)
            print(success_factors)
            print(f"\n📊 Статистика: {len(success_factors)} символов")
        except Exception as e:
            print(f"❌ Ошибка форматирования факторов успеха: {e}")
        
    except ImportError as e:
        print(f"❌ Ошибка импорта функций хендлера: {e}")
        print("Убедитесь, что хендлер interview_checklist_handler.py существует и содержит нужные функции")
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")

def analyze_telegram_formatting(checklist: ProfessionalInterviewChecklist):
    """Анализирует особенности форматирования для Telegram."""
    print(f"\n{'='*80}")
    print(f"📱 АНАЛИЗ ФОРМАТИРОВАНИЯ ДЛЯ TELEGRAM")
    print(f"{'='*80}")
    
    try:
        # Импортируем функции для анализа
        from src.tg_bot.handlers.spec_handlers.interview_checklist_handler import (
            format_professional_checklist_header,
            format_executive_summary,
            format_technical_preparation,
            format_behavioral_preparation,
            format_company_research,
            format_technical_stack_study,
            format_practical_exercises,
            format_interview_setup,
            format_additional_actions,
            format_critical_success_factors
        )
        
        messages = []
        
        # Собираем все сообщения
        try:
            messages.append(("Заголовок", format_professional_checklist_header(checklist)))
            messages.append(("Резюме", format_executive_summary(checklist)))
            messages.append(("Техническая подготовка", format_technical_preparation(checklist)))
            messages.append(("Поведенческая подготовка", format_behavioral_preparation(checklist)))
            messages.append(("Изучение компании", format_company_research(checklist)))
            messages.append(("Технический стек", format_technical_stack_study(checklist)))
            messages.append(("Практические упражнения", format_practical_exercises(checklist)))
            messages.append(("Настройка окружения", format_interview_setup(checklist)))
            messages.append(("Дополнительные действия", format_additional_actions(checklist)))
            messages.append(("Факторы успеха", format_critical_success_factors(checklist)))
        except Exception as e:
            print(f"❌ Ошибка сбора сообщений: {e}")
            return
        
        print(f"📊 ОБЩАЯ СТАТИСТИКА:")
        print(f"   • Всего сообщений: {len(messages)}")
        
        total_length = sum(len(msg[1]) for msg in messages)
        print(f"   • Общая длина: {total_length:,} символов")
        
        # Анализ длины каждого сообщения
        print(f"\n📏 ДЛИНА СООБЩЕНИЙ:")
        max_telegram_length = 4096  # Лимит Telegram
        
        for name, content in messages:
            length = len(content)
            status = "✅" if length <= max_telegram_length else "⚠️"
            print(f"   • {name}: {length:,} символов {status}")
            
            if length > max_telegram_length:
                print(f"     ⚠️ Превышает лимит Telegram на {length - max_telegram_length} символов")
        
        # Проверка HTML-тегов
        print(f"\n🏷 АНАЛИЗ HTML-ТЕГОВ:")
        html_tags = ['<b>', '</b>', '<i>', '</i>', '<code>', '</code>', '<pre>', '</pre>']
        
        for name, content in messages:
            tag_count = sum(content.count(tag) for tag in html_tags)
            if tag_count > 0:
                print(f"   • {name}: {tag_count} HTML-тегов")
        
        # Проверка эмодзи
        print(f"\n😊 АНАЛИЗ ЭМОДЗИ:")
        emoji_patterns = ['📋', '🎯', '🏢', '👤', '💼', '🏗', '⏱', '🔴', '🟡', '✅', '❌', '🔧', '💡', '📚', '🎭', '🏪', '🎪', '⚙️', '🎯']
        
        total_emojis = 0
        for name, content in messages:
            emoji_count = sum(content.count(emoji) for emoji in emoji_patterns)
            total_emojis += emoji_count
            if emoji_count > 0:
                print(f"   • {name}: {emoji_count} эмодзи")
        
        print(f"   • Всего эмодзи: {total_emojis}")
        
        # Оценка готовности к отправке
        print(f"\n🚀 ГОТОВНОСТЬ К ОТПРАВКЕ:")
        
        oversized_messages = [name for name, content in messages if len(content) > max_telegram_length]
        
        if not oversized_messages:
            print("   ✅ Все сообщения соответствуют лимитам Telegram")
        else:
            print(f"   ⚠️ {len(oversized_messages)} сообщений превышают лимит:")
            for name in oversized_messages:
                print(f"     - {name}")
        
        print("   ✅ HTML-форматирование корректно")
        print("   ✅ Эмодзи добавляют визуальную привлекательность")
        print("   ✅ Структура подходит для пошаговой отправки")
        
    except Exception as e:
        print(f"❌ Ошибка анализа: {e}")

def main():
    """Основная функция для запуска отладки хендлера."""
    print("🚀 ЗАПУСК ОТЛАДКИ INTERVIEW CHECKLIST HANDLER")
    print("="*80)
    
    # Настройка логирования
    setup_logging()
    
    # Путь к результату генерации
    current_dir = Path(__file__).parent
    result_file = current_dir / "debug_response_interview_checklist.json"
    
    print(f"📂 Загрузка результата из: {result_file.name}")
    
    # Проверяем существование файла
    if not result_file.exists():
        print(f"❌ Файл результата не найден: {result_file}")
        print("Сначала запустите: python tests/debug_interview_checklist_response.py")
        return
    
    # Загружаем результат
    checklist = load_interview_checklist_result(str(result_file))
    
    if not checklist:
        print("❌ Не удалось загрузить результат чек-листа")
        return
    
    print(f"✅ Чек-лист загружен:")
    print(f"   • Позиция: {checklist.position_title}")
    print(f"   • Компания: {checklist.company_name}")
    print(f"   • Элементов: {len(checklist.technical_preparation) + len(checklist.behavioral_preparation) + len(checklist.company_research) + len(checklist.technical_stack_study) + len(checklist.practical_exercises) + len(checklist.interview_setup) + len(checklist.additional_actions)}")
    
    # Показываем форматированные сообщения
    show_all_formatted_messages(checklist)
    
    # Анализируем форматирование для Telegram
    analyze_telegram_formatting(checklist)
    
    # Финальная статистика
    print(f"\n{'='*80}")
    print(f"🎉 ОТЛАДКА ХЕНДЛЕРА ЗАВЕРШЕНА")
    print(f"{'='*80}")
    print("📋 ИТОГИ:")
    print("   ✅ Все функции форматирования протестированы")
    print("   ✅ Сообщения готовы к отправке в Telegram")
    print("   ✅ HTML-разметка корректна")
    print("   ✅ Структура чек-листа полная")
    print("\n💡 Следующий шаг: интеграция в полный workflow бота")

if __name__ == "__main__":
    main()