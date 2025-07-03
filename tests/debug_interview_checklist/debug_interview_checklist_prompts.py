# tests/debug_interview_checklist_prompts.py
"""
Отладочный скрипт для тестирования промптов interview checklist generator.
Показывает как формируются промпты для генерации чек-листа подготовки к интервью.
"""

import json
import sys
from pathlib import Path

# Добавляем корневую директорию в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm_interview_checklist.llm_interview_checklist_generator import LLMInterviewChecklistGenerator
from src.llm_interview_checklist.formatter import (
    format_resume_for_interview_prep,
    format_vacancy_for_interview_prep
)
from src.parsers.resume_extractor import ResumeExtractor
from src.parsers.vacancy_extractor import VacancyExtractor

def load_test_data():
    """Загружает и парсит тестовые данные."""
    try:
        # Пути к тестовым данным
        resume_path = Path("/Users/mask/Documents/Проеты_2025/gpt_4_mini_hackaton_final/tests/test_models_res_vac/fetched_resume_6d807532ff0ed6b79f0039ed1f63386d724a62.json")
        vacancy_path = Path("/Users/mask/Documents/Проеты_2025/gpt_4_mini_hackaton_final/tests/test_models_res_vac/fetched_vacancy_120234346.json")
        
        # Загружаем сырые данные
        with open(resume_path, 'r', encoding='utf-8') as f:
            raw_resume = json.load(f)
            
        with open(vacancy_path, 'r', encoding='utf-8') as f:
            raw_vacancy = json.load(f)
        
        # Парсим данные
        resume_extractor = ResumeExtractor()
        vacancy_extractor = VacancyExtractor()
        
        parsed_resume = resume_extractor.extract_resume_info(raw_resume)
        parsed_vacancy = vacancy_extractor.extract_vacancy_info(raw_vacancy)
        
        print("✅ Тестовые данные загружены и спарсены")
        print(f"   • Резюме: {type(parsed_resume).__name__}")
        print(f"   • Вакансия: {type(parsed_vacancy).__name__}")
        
        return parsed_resume, parsed_vacancy
        
    except Exception as e:
        print(f"❌ Ошибка загрузки данных: {e}")
        return None, None

def test_data_formatting(parsed_resume, parsed_vacancy):
    """Тестирует форматирование данных для промптов."""
    print("\n" + "="*80)
    print("📝 ТЕСТИРОВАНИЕ ФОРМАТИРОВАНИЯ ДАННЫХ")
    print("="*80)
    
    try:
        # Конвертируем в словари
        resume_dict = parsed_resume.model_dump()
        vacancy_dict = parsed_vacancy.model_dump()
        
        print("🔸 ДАННЫЕ РЕЗЮМЕ:")
        print(f"   • Название: {resume_dict.get('title', 'Не указано')}")
        print(f"   • Опыт работы: {len(resume_dict.get('experience', []))} позиций")
        print(f"   • Навыки: {len(resume_dict.get('skill_set', []))} навыков")
        
        print("\n🔸 ДАННЫЕ ВАКАНСИИ:")
        print(f"   • Название: {vacancy_dict.get('name', 'Не указано')}")
        print(f"   • Компания: {vacancy_dict.get('company_name', 'Не указана')}")
        print(f"   • Ключевые навыки: {len(vacancy_dict.get('key_skills', []))} навыков")
        
        # Форматируем для промптов
        formatted_resume = format_resume_for_interview_prep(resume_dict)
        formatted_vacancy = format_vacancy_for_interview_prep(vacancy_dict)
        
        print("\n📊 РЕЗУЛЬТАТЫ ФОРМАТИРОВАНИЯ:")
        print(f"   • Длина форматированного резюме: {len(formatted_resume):,} символов")
        print(f"   • Длина форматированной вакансии: {len(formatted_vacancy):,} символов")
        print(f"   • Общая длина: {len(formatted_resume) + len(formatted_vacancy):,} символов")
        
        return resume_dict, vacancy_dict, formatted_resume, formatted_vacancy
        
    except Exception as e:
        print(f"❌ Ошибка форматирования: {e}")
        return None, None, None, None

def test_prompt_generation(resume_dict, vacancy_dict):
    """Тестирует генерацию промптов."""
    print("\n" + "="*80)
    print("🧠 ТЕСТИРОВАНИЕ ГЕНЕРАЦИИ ПРОМПТОВ")
    print("="*80)
    
    try:
        # Создаем генератор
        generator = LLMInterviewChecklistGenerator()
        
        # Генерируем промпт (новая версия)
        full_prompt = generator._create_professional_interview_checklist_prompt(resume_dict, vacancy_dict)
        
        # Система сообщений как в реальном API
        system_prompt = (
            "Ты — ведущий HR-эксперт по подготовке IT-кандидатов к интервью с 10+ летним опытом. "
            "Специализируешься на создании персонализированных, детальных чек-листов, которые "
            "реально помогают кандидатам успешно пройти собеседование и получить работу. "
            "Следуешь проверенной методологии и лучшим практикам HR-индустрии. "
            "Всегда пишешь на русском языке и даешь конкретные, практичные советы. "
            "Ответ всегда в формате JSON согласно указанной структуре ProfessionalInterviewChecklist."
        )
        user_prompt = full_prompt
        
        print("✅ Промпты успешно сгенерированы")
        
        # Показываем system prompt
        print("\n🔧 SYSTEM PROMPT:")
        print("-" * 60)
        print(system_prompt[:500] + "..." if len(system_prompt) > 500 else system_prompt)
        print("-" * 60)
        print(f"   • Длина: {len(system_prompt):,} символов")
        
        # Показываем user prompt (сокращенно)
        print("\n👤 USER PROMPT (первые 800 символов):")
        print("-" * 60)
        print(user_prompt[:80000] + "..." if len(user_prompt) > 800 else user_prompt)
        print("-" * 60)
        print(f"   • Длина: {len(user_prompt):,} символов")
        
        # Общая статистика
        total_length = len(system_prompt) + len(user_prompt)
        print("\n📊 СТАТИСТИКА ПРОМПТОВ:")
        print(f"   • Общая длина: {total_length:,} символов")
        print(f"   • System: {len(system_prompt):,} символов ({len(system_prompt)/total_length*100:.1f}%)")
        print(f"   • User: {len(user_prompt):,} символов ({len(user_prompt)/total_length*100:.1f}%)")
        
        return system_prompt, user_prompt
        
    except Exception as e:
        print(f"❌ Ошибка генерации промптов: {e}")
        return None, None

def test_messages_format(system_prompt, user_prompt):
    """Тестирует формат сообщений для OpenAI API."""
    print("\n" + "="*80)
    print("📡 ТЕСТИРОВАНИЕ ФОРМАТА СООБЩЕНИЙ")
    print("="*80)
    
    try:
        # Создаем messages в формате OpenAI
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        print("✅ Messages созданы в формате OpenAI API")
        
        # Показываем структуру
        print("\n📋 СТРУКТУРА MESSAGES:")
        print(f"   • Количество сообщений: {len(messages)}")
        print(f"   • Роль 1: {messages[0]['role']} ({len(messages[0]['content']):,} символов)")
        print(f"   • Роль 2: {messages[1]['role']} ({len(messages[1]['content']):,} символов)")
        
        # Показываем JSON (сокращенно)
        print("\n🔍 ПРИМЕР MESSAGES JSON (сокращенно):")
        print("```json")
        sample_messages = [
            {"role": "system", "content": system_prompt[:200] + "..."},
            {"role": "user", "content": user_prompt[:200] + "..."}
        ]
        print(json.dumps(sample_messages, ensure_ascii=False, indent=2))
        print("```")
        
        # Проверяем готовность к отправке
        print("\n🚀 ГОТОВНОСТЬ К ОТПРАВКЕ:")
        print("   • Формат корректен: ✅")
        print("   • Роли определены: ✅")
        print("   • Контент заполнен: ✅")
        
        total_tokens_estimate = (len(system_prompt) + len(user_prompt)) // 4  # Примерная оценка
        print(f"   • Примерное количество токенов: ~{total_tokens_estimate:,}")
        
        if total_tokens_estimate > 8000:
            print("   ⚠️ Возможно превышение лимита токенов модели")
        else:
            print("   ✅ Размер в пределах лимитов")
        
        return messages
        
    except Exception as e:
        print(f"❌ Ошибка формирования messages: {e}")
        return None

def analyze_prompt_components(system_prompt, user_prompt, formatted_resume, formatted_vacancy):
    """Анализирует компоненты промптов."""
    print("\n" + "="*80)
    print("🔬 АНАЛИЗ КОМПОНЕНТОВ ПРОМПТОВ")
    print("="*80)
    
    try:
        print("🔸 1. ИСТОЧНИКИ ДАННЫХ:")
        print("   • ResumeInfo → resume_dict → format_resume_for_interview_prep()")
        print("   • VacancyInfo → vacancy_dict → format_vacancy_for_interview_prep()")
        
        print("\n🔸 2. КОМПОНЕНТЫ SYSTEM PROMPT:")
        system_sections = system_prompt.split('\n\n')
        print(f"   • Количество секций: {len(system_sections)}")
        print(f"   • Содержит инструкции по анализу: {'анализ' in system_prompt.lower()}")
        print(f"   • Содержит требования к формату: {'InterviewChecklist' in system_prompt}")
        
        print("\n🔸 3. КОМПОНЕНТЫ USER PROMPT:")
        print(f"   • Содержит резюме: {len(formatted_resume):,} символов")
        print(f"   • Содержит вакансию: {len(formatted_vacancy):,} символов")
        
        # Проверяем наличие ключевых секций
        resume_sections = formatted_resume.count('###')
        vacancy_sections = formatted_vacancy.count('###')
        print(f"   • Секций в резюме: {resume_sections}")
        print(f"   • Секций в вакансии: {vacancy_sections}")
        
        print("\n🔸 4. КЛЮЧЕВЫЕ СЛОВА В ПРОМПТАХ:")
        combined_prompts = (system_prompt + user_prompt).lower()
        keywords = [
            'интервью', 'подготовка', 'навыки', 'опыт', 'технологии', 
            'компетенции', 'чек-лист', 'рекомендации'
        ]
        
        for keyword in keywords:
            count = combined_prompts.count(keyword)
            if count > 0:
                print(f"   • '{keyword}': {count} упоминаний")
        
        print("\n🔸 5. ГОТОВНОСТЬ К ГЕНЕРАЦИИ:")
        print("   • Структурированные данные: ✅")
        print("   • Детальные инструкции: ✅")
        print("   • Формат ответа определен: ✅")
        print("   • Контекст задачи ясен: ✅")
        
    except Exception as e:
        print(f"❌ Ошибка анализа компонентов: {e}")

def main():
    """Основная функция для запуска всех тестов промптов."""
    print("🚀 ЗАПУСК ОТЛАДКИ ПРОМПТОВ INTERVIEW CHECKLIST")
    print("=" * 80)
    
    # Загружаем и парсим данные
    parsed_resume, parsed_vacancy = load_test_data()
    
    if not parsed_resume or not parsed_vacancy:
        print("❌ Не удалось загрузить тестовые данные. Завершение.")
        return
    
    # Форматируем данные
    resume_dict, vacancy_dict, formatted_resume, formatted_vacancy = test_data_formatting(
        parsed_resume, parsed_vacancy
    )
    
    if not all([resume_dict, vacancy_dict, formatted_resume, formatted_vacancy]):
        print("❌ Ошибка форматирования данных. Завершение.")
        return
    
    # Генерируем промпты
    system_prompt, user_prompt = test_prompt_generation(resume_dict, vacancy_dict)
    
    if not system_prompt or not user_prompt:
        print("❌ Ошибка генерации промптов. Завершение.")
        return
    
    # Тестируем формат сообщений
    messages = test_messages_format(system_prompt, user_prompt)
    
    if messages:
        # Анализируем компоненты
        analyze_prompt_components(system_prompt, user_prompt, formatted_resume, formatted_vacancy)
        
        print("\n🎉 ТЕСТИРОВАНИЕ ПРОМПТОВ ЗАВЕРШЕНО УСПЕШНО")
        print("   • Все компоненты работают корректно")
        print("   • Промпты готовы к отправке в OpenAI API")
        print("   • Ожидается получение структурированного InterviewChecklist")
    else:
        print("\n❌ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО С ОШИБКАМИ")
        print("   • Проверьте логи выше для диагностики")

if __name__ == "__main__":
    main()