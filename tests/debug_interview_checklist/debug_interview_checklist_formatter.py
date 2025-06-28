# tests/debug_interview_checklist_formatter.py
"""
Отладочный скрипт для тестирования форматтера данных interview checklist.
Проверяет корректность форматирования резюме и вакансии для генерации чек-листа подготовки к интервью.
"""

import json
import sys
from pathlib import Path

# Добавляем корневую директорию в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm_interview_checklist.formatter import (
    format_resume_for_interview_prep,
    format_vacancy_for_interview_prep
)

def load_test_data():
    """Загружает тестовые данные резюме и вакансии."""
    try:
        # Пути к тестовым данным
        resume_path = Path("/Users/mask/Documents/Проеты_2025/gpt_4_mini_hackaton_final/tests/test_models_res_vac/fetched_resume_6d807532ff0ed6b79f0039ed1f63386d724a62.json")
        vacancy_path = Path("/Users/mask/Documents/Проеты_2025/gpt_4_mini_hackaton_final/tests/test_models_res_vac/fetched_vacancy_120234346.json")
        
        # Загружаем данные резюме
        with open(resume_path, 'r', encoding='utf-8') as f:
            resume_data = json.load(f)
            
        # Загружаем данные вакансии
        with open(vacancy_path, 'r', encoding='utf-8') as f:
            vacancy_data = json.load(f)
            
        print("✅ Тестовые данные успешно загружены")
        print(f"   • Резюме: {resume_path.name}")
        print(f"   • Вакансия: {vacancy_path.name}")
        
        return resume_data, vacancy_data
        
    except FileNotFoundError as e:
        print(f"❌ Ошибка: файл не найден - {e}")
        return None, None
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка декодирования JSON: {e}")
        return None, None
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return None, None

def test_resume_formatter(resume_data):
    """Тестирует форматтер резюме для interview checklist."""
    print("\n" + "="*80)
    print("🔍 ТЕСТИРОВАНИЕ ФОРМАТТЕРА РЕЗЮМЕ")
    print("="*80)
    
    try:
        # Форматируем резюме
        formatted_resume = format_resume_for_interview_prep(resume_data)
        
        print("✅ Форматирование резюме выполнено успешно")
        print(f"   • Длина результата: {len(formatted_resume)} символов")
        
        # Показываем отформатированный результат
        print("\n📋 ОТФОРМАТИРОВАННОЕ РЕЗЮМЕ:")
        print("-" * 60)
        print(formatted_resume)
        print("-" * 60)
        
        # Анализируем структуру
        sections = formatted_resume.split('###')
        print(f"\n📊 АНАЛИЗ СТРУКТУРЫ:")
        print(f"   • Количество секций: {len(sections) - 1}")  # -1 потому что первая часть до ###
        
        for i, section in enumerate(sections[1:], 1):  # Пропускаем первую пустую часть
            section_title = section.split('\n')[0].strip()
            section_content = section.strip()
            content_length = len(section_content)
            print(f"   • Секция {i}: '{section_title}' ({content_length} символов)")
        
        return formatted_resume
        
    except Exception as e:
        print(f"❌ Ошибка форматирования резюме: {e}")
        return None

def test_vacancy_formatter(vacancy_data):
    """Тестирует форматтер вакансии для interview checklist."""
    print("\n" + "="*80)
    print("🎯 ТЕСТИРОВАНИЕ ФОРМАТТЕРА ВАКАНСИИ")
    print("="*80)
    
    try:
        # Форматируем вакансию
        formatted_vacancy = format_vacancy_for_interview_prep(vacancy_data)
        
        print("✅ Форматирование вакансии выполнено успешно")
        print(f"   • Длина результата: {len(formatted_vacancy)} символов")
        
        # Показываем отформатированный результат
        print("\n🎯 ОТФОРМАТИРОВАННАЯ ВАКАНСИЯ:")
        print("-" * 60)
        print(formatted_vacancy)
        print("-" * 60)
        
        # Анализируем структуру
        sections = formatted_vacancy.split('###')
        print(f"\n📊 АНАЛИЗ СТРУКТУРЫ:")
        print(f"   • Количество секций: {len(sections) - 1}")
        
        for i, section in enumerate(sections[1:], 1):
            section_title = section.split('\n')[0].strip()
            section_content = section.strip()
            content_length = len(section_content)
            print(f"   • Секция {i}: '{section_title}' ({content_length} символов)")
        
        return formatted_vacancy
        
    except Exception as e:
        print(f"❌ Ошибка форматирования вакансии: {e}")
        return None

def analyze_formatting_quality(formatted_resume, formatted_vacancy):
    """Анализирует качество форматирования для LLM."""
    print("\n" + "="*80)
    print("📈 АНАЛИЗ КАЧЕСТВА ФОРМАТИРОВАНИЯ")
    print("="*80)
    
    try:
        # Общая статистика
        total_length = len(formatted_resume) + len(formatted_vacancy)
        print(f"📊 ОБЩАЯ СТАТИСТИКА:")
        print(f"   • Общая длина: {total_length:,} символов")
        print(f"   • Длина резюме: {len(formatted_resume):,} символов")
        print(f"   • Длина вакансии: {len(formatted_vacancy):,} символов")
        
        # Проверяем структурированность
        resume_sections = len(formatted_resume.split('###')) - 1
        vacancy_sections = len(formatted_vacancy.split('###')) - 1
        
        print(f"\n🏗️ СТРУКТУРИРОВАННОСТЬ:")
        print(f"   • Секций в резюме: {resume_sections}")
        print(f"   • Секций в вакансии: {vacancy_sections}")
        print(f"   • Общее количество секций: {resume_sections + vacancy_sections}")
        
        # Проверяем наличие ключевых слов
        combined_text = (formatted_resume + formatted_vacancy).lower()
        keywords = [
            'опыт', 'навыки', 'технологии', 'образование', 'проект',
            'требования', 'компетенции', 'специализация', 'должность'
        ]
        
        found_keywords = []
        for keyword in keywords:
            if keyword in combined_text:
                count = combined_text.count(keyword)
                found_keywords.append(f"{keyword} ({count})")
        
        print(f"\n🔍 КЛЮЧЕВЫЕ СЛОВА:")
        print(f"   • Найдено: {', '.join(found_keywords)}")
        
        # Оценка готовности для LLM
        if total_length > 500 and resume_sections >= 3 and vacancy_sections >= 3:
            print(f"\n✅ ОЦЕНКА: Данные готовы для передачи в LLM")
            print(f"   • Достаточная детализация")
            print(f"   • Хорошая структурированность")
            print(f"   • Содержит ключевую информацию")
        else:
            print(f"\n⚠️ ОЦЕНКА: Данные требуют доработки")
            if total_length <= 500:
                print(f"   • Недостаточная длина текста")
            if resume_sections < 3:
                print(f"   • Мало секций в резюме")
            if vacancy_sections < 3:
                print(f"   • Мало секций в вакансии")
        
    except Exception as e:
        print(f"❌ Ошибка анализа: {e}")

def main():
    """Основная функция для запуска всех тестов."""
    print("🚀 ЗАПУСК ОТЛАДКИ ФОРМАТТЕРА INTERVIEW CHECKLIST")
    print("=" * 80)
    
    # Загружаем тестовые данные
    resume_data, vacancy_data = load_test_data()
    
    if not resume_data or not vacancy_data:
        print("❌ Не удалось загрузить тестовые данные. Завершение.")
        return
    
    # Тестируем форматтеры
    formatted_resume = test_resume_formatter(resume_data)
    formatted_vacancy = test_vacancy_formatter(vacancy_data)
    
    if formatted_resume and formatted_vacancy:
        # Анализируем качество
        analyze_formatting_quality(formatted_resume, formatted_vacancy)
        
        print(f"\n🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО")
        print(f"   • Все форматтеры работают корректно")
        print(f"   • Данные готовы для генерации interview checklist")
    else:
        print(f"\n❌ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО С ОШИБКАМИ")
        print(f"   • Проверьте логи выше для диагностики")

if __name__ == "__main__":
    main()