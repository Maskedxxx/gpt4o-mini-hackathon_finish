#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для отладки ответа LLM в генерации сопроводительного письма.
Вызывает реальную генерацию письма и показывает структурированный результат.

Показывает:
1. Ответ от LLM в Pydantic структуре
2. JSON представление ответа
3. Детализацию по полям модели
4. Валидацию качества
5. Форматированное письмо для email

Использование:
    python tests/debug_cover_letter/debug_cover_letter_response.py
"""

import json
import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

# Добавляем корневую директорию проекта в Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Импорты из приложения
from src.parsers.resume_extractor import ResumeExtractor
from src.parsers.vacancy_extractor import VacancyExtractor
from src.llm_cover_letter.llm_cover_letter_generator import EnhancedLLMCoverLetterGenerator
from src.models.cover_letter_models import EnhancedCoverLetter
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

def show_cover_letter_structure(cover_letter: EnhancedCoverLetter) -> None:
    """Показывает структуру результата сопроводительного письма по полям."""
    print("\n" + "="*80)
    print("📧 СТРУКТУРА РЕЗУЛЬТАТА СОПРОВОДИТЕЛЬНОГО ПИСЬМА")
    print("="*80)
    
    try:
        print("🔸 МЕТА-ИНФОРМАЦИЯ:")
        print(f"   • Тип роли: {cover_letter.role_type}")
        print(f"   • Название компании: {cover_letter.company_context.company_name}")
        print(f"   • Размер компании: {cover_letter.company_context.company_size}")
        print(f"   • Оценка длины: {cover_letter.estimated_length}")
        
        print("\n🔸 АНАЛИЗ СООТВЕТСТВИЯ НАВЫКОВ:")
        skills = cover_letter.skills_match
        print(f"   • Совпадающих навыков: {len(skills.matched_skills)}")
        print(f"   • Навыки: {', '.join(skills.matched_skills)}")
        print(f"   • Релевантный опыт: {skills.relevant_experience[:100]}...")
        if skills.quantified_achievement:
            print(f"   • Количественное достижение: {skills.quantified_achievement[:100]}...")
        if skills.growth_potential:
            print(f"   • Потенциал роста: {skills.growth_potential[:100]}...")
        
        print("\n🔸 СТРАТЕГИЯ ПЕРСОНАЛИЗАЦИИ:")
        pers = cover_letter.personalization
        print(f"   • Крючок компании: {pers.company_hook[:100]}...")
        print(f"   • Мотивация роли: {pers.role_motivation[:100]}...")
        print(f"   • Ценностное предложение: {pers.value_proposition[:100]}...")
        if pers.company_knowledge:
            print(f"   • Знание компании: {pers.company_knowledge[:100]}...")
        
        print("\n🔸 СТРУКТУРА ПИСЬМА:")
        print(f"   • Тема письма: {cover_letter.subject_line}")
        print(f"   • Приветствие: {cover_letter.personalized_greeting}")
        print(f"   • Длина зацепки: {len(cover_letter.opening_hook)} символов")
        print(f"   • Длина интереса к компании: {len(cover_letter.company_interest)} символов")
        print(f"   • Длина релевантного опыта: {len(cover_letter.relevant_experience)} символов")
        print(f"   • Длина демонстрации ценности: {len(cover_letter.value_demonstration)} символов")
        if cover_letter.growth_mindset:
            print(f"   • Длина готовности к развитию: {len(cover_letter.growth_mindset)} символов")
        print(f"   • Длина завершения: {len(cover_letter.professional_closing)} символов")
        print(f"   • Подпись: {cover_letter.signature}")
        
        print("\n🔸 ОЦЕНКИ КАЧЕСТВА:")
        print(f"   • Персонализация: {cover_letter.personalization_score}/10")
        print(f"   • Профессиональный тон: {cover_letter.professional_tone_score}/10")
        print(f"   • Релевантность: {cover_letter.relevance_score}/10")
        avg_score = (cover_letter.personalization_score + cover_letter.professional_tone_score + cover_letter.relevance_score) / 3
        print(f"   • Средняя оценка: {avg_score:.1f}/10")
        
        print("\n🔸 РЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ:")
        for i, suggestion in enumerate(cover_letter.improvement_suggestions, 1):
            print(f"   {i}. {suggestion}")
        
        # Подсчет общей длины письма
        total_length = (
            len(cover_letter.opening_hook) + 
            len(cover_letter.company_interest) + 
            len(cover_letter.relevant_experience) + 
            len(cover_letter.value_demonstration) + 
            len(cover_letter.professional_closing) +
            (len(cover_letter.growth_mindset) if cover_letter.growth_mindset else 0)
        )
        print(f"\n📊 ОБЩАЯ ДЛИНА ПИСЬМА: {total_length} символов")
        
    except Exception as e:
        print(f"❌ Ошибка отображения структуры: {e}")

def show_detailed_letter_content(cover_letter: EnhancedCoverLetter) -> None:
    """Показывает детальное содержание всех секций письма."""
    print("\n" + "="*80)
    print("📝 ДЕТАЛЬНОЕ СОДЕРЖАНИЕ ПИСЬМА")
    print("="*80)
    
    try:
        print("📧 ТЕМА ПИСЬМА:")
        print(f"   {cover_letter.subject_line}")
        
        print("\n👋 ПРИВЕТСТВИЕ:")
        print(f"   {cover_letter.personalized_greeting}")
        
        print("\n🎣 ЗАЦЕПЛЯЮЩЕЕ НАЧАЛО:")
        print(f"   {cover_letter.opening_hook}")
        
        print("\n🏢 ИНТЕРЕС К КОМПАНИИ:")
        print(f"   {cover_letter.company_interest}")
        
        print("\n💼 РЕЛЕВАНТНЫЙ ОПЫТ:")
        print(f"   {cover_letter.relevant_experience}")
        
        print("\n💎 ДЕМОНСТРАЦИЯ ЦЕННОСТИ:")
        print(f"   {cover_letter.value_demonstration}")
        
        if cover_letter.growth_mindset:
            print("\n🌱 ГОТОВНОСТЬ К РАЗВИТИЮ:")
            print(f"   {cover_letter.growth_mindset}")
        
        print("\n🤝 ПРОФЕССИОНАЛЬНОЕ ЗАВЕРШЕНИЕ:")
        print(f"   {cover_letter.professional_closing}")
        
        print("\n✍️ ПОДПИСЬ:")
        print(f"   {cover_letter.signature}")
        
    except Exception as e:
        print(f"❌ Ошибка отображения содержания: {e}")

def show_quality_validation(cover_letter: EnhancedCoverLetter, generator: EnhancedLLMCoverLetterGenerator, vacancy_dict: Dict[str, Any]) -> None:
    """Показывает результат валидации качества письма."""
    print("\n" + "="*80)
    print("🔍 ВАЛИДАЦИЯ КАЧЕСТВА ПИСЬМА")
    print("="*80)
    
    try:
        # Вызываем метод валидации
        is_valid = generator._validate_quality(cover_letter, vacancy_dict)
        
        print(f"🔸 ОБЩИЙ РЕЗУЛЬТАТ ВАЛИДАЦИИ: {'✅ ПРОШЛО' if is_valid else '❌ НЕ ПРОШЛО'}")
        
        # Проверяем каждый критерий отдельно
        company_name = vacancy_dict.get('company_name', '').lower()
        full_text = (
            cover_letter.opening_hook + " " +
            cover_letter.company_interest + " " +
            cover_letter.relevant_experience
        ).lower()
        
        print("\n🔸 ДЕТАЛЬНЫЕ ПРОВЕРКИ:")
        
        # Упоминание компании
        company_mentioned = company_name in full_text if company_name else True
        print(f"   • Упоминание компании: {'✅' if company_mentioned else '❌'} ({company_name})")
        
        # Оценки
        print(f"   • Персонализация ≥ 6: {'✅' if cover_letter.personalization_score >= 6 else '❌'} ({cover_letter.personalization_score})")
        print(f"   • Профессионализм ≥ 7: {'✅' if cover_letter.professional_tone_score >= 7 else '❌'} ({cover_letter.professional_tone_score})")
        print(f"   • Релевантность ≥ 6: {'✅' if cover_letter.relevance_score >= 6 else '❌'} ({cover_letter.relevance_score})")
        
        # Навыки
        has_skills = len(cover_letter.skills_match.matched_skills) >= 1
        print(f"   • Есть совпадающие навыки: {'✅' if has_skills else '❌'} ({len(cover_letter.skills_match.matched_skills)})")
        
        # Ценностное предложение
        has_value_prop = len(cover_letter.personalization.value_proposition) >= 50
        print(f"   • Ценностное предложение ≥ 50 символов: {'✅' if has_value_prop else '❌'} ({len(cover_letter.personalization.value_proposition)})")
        
    except Exception as e:
        print(f"❌ Ошибка валидации качества: {e}")

def show_formatted_email(cover_letter: EnhancedCoverLetter, generator: EnhancedLLMCoverLetterGenerator) -> None:
    """Показывает письмо отформатированное для email."""
    print("\n" + "="*80)
    print("📨 ПИСЬМО ДЛЯ ОТПРАВКИ ПО EMAIL")
    print("="*80)
    
    try:
        formatted_email = generator.format_for_email(cover_letter)
        print(formatted_email)
        print(f"\n📊 Общая длина email: {len(formatted_email)} символов")
        
    except Exception as e:
        print(f"❌ Ошибка форматирования email: {e}")

async def debug_cover_letter_response(resume_json_path: str, vacancy_json_path: str) -> None:
    """Вызывает реальную генерацию сопроводительного письма и показывает результат."""
    print("\n" + "="*80)
    print("🤖 РЕЗУЛЬТАТ ГЕНЕРАЦИИ СОПРОВОДИТЕЛЬНОГО ПИСЬМА ОТ LLM")
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
    
    print("✅ Данные подготовлены, запускаем генерацию сопроводительного письма...")
    
    try:
        # Создаем экземпляр генератора
        cover_letter_generator = EnhancedLLMCoverLetterGenerator(validate_quality=False)
        
        # Конвертируем в dict как в реальном приложении
        resume_dict = parsed_resume.model_dump()
        vacancy_dict = parsed_vacancy.model_dump()
        
        # ВЫЗЫВАЕМ РЕАЛЬНУЮ ГЕНЕРАЦИЮ ПИСЬМА
        cover_letter = await cover_letter_generator.generate_enhanced_cover_letter(resume_dict, vacancy_dict)
        
        if not cover_letter:
            print("❌ Генерация письма вернула пустой результат")
            return
        
        print("✅ Сопроводительное письмо успешно сгенерировано!")
        
        # Показываем результат в JSON формате
        print("\n📄 РЕЗУЛЬТАТ В JSON ФОРМАТЕ:")
        print("-" * 60)
        result_json = cover_letter.model_dump()
        print(json.dumps(result_json, ensure_ascii=False, indent=2))
        
        # Показываем структуру
        show_cover_letter_structure(cover_letter)
        
        # Показываем детальное содержание
        show_detailed_letter_content(cover_letter)
        
        # Показываем валидацию качества
        show_quality_validation(cover_letter, cover_letter_generator, vacancy_dict)
        
        # Показываем форматированное письмо
        show_formatted_email(cover_letter, cover_letter_generator)
        
    except Exception as e:
        print(f"❌ Ошибка генерации сопроводительного письма: {e}")
        import traceback
        traceback.print_exc()

async def debug_pydantic_model_info() -> None:
    """Показывает информацию о Pydantic модели результата."""
    print("\n" + "="*80)
    print("📚 ИНФОРМАЦИЯ О МОДЕЛИ EnhancedCoverLetter")
    print("="*80)
    
    try:
        # Получаем схему модели
        schema = EnhancedCoverLetter.model_json_schema()
        
        print("🔸 ОСНОВНЫЕ ПОЛЯ МОДЕЛИ:")
        properties = schema.get('properties', {})
        for field_name, field_info in properties.items():
            field_type = field_info.get('type', 'unknown')
            description = field_info.get('description', 'Описание отсутствует')
            # Обрезаем длинные описания
            short_desc = description[:100] + "..." if len(description) > 100 else description
            print(f"   • {field_name} ({field_type}): {short_desc}")
        
        print(f"\n🔸 ВСЕГО ПОЛЕЙ В МОДЕЛИ: {len(properties)}")
        
        # Показываем required поля
        required = schema.get('required', [])
        print(f"🔸 ОБЯЗАТЕЛЬНЫХ ПОЛЕЙ: {len(required)}")
        for field in required:
            print(f"   • {field}")
        
        # Показываем структуру вложенных моделей
        print("\n🔸 ВЛОЖЕННЫЕ МОДЕЛИ:")
        if 'company_context' in properties:
            print("   • CompanyContext (контекст компании)")
        if 'skills_match' in properties:
            print("   • SkillsMatchAnalysis (анализ соответствия навыков)")
        if 'personalization' in properties:
            print("   • PersonalizationStrategy (стратегия персонализации)")
            
    except Exception as e:
        print(f"❌ Ошибка анализа модели: {e}")

async def main():
    """Основная функция для запуска отладки ответа генерации сопроводительного письма."""
    
    # Настраиваем логирование
    setup_logging(log_level="INFO")
    
    print("📧 ОТЛАДКА ОТВЕТА LLM В ГЕНЕРАЦИИ СОПРОВОДИТЕЛЬНОГО ПИСЬМА")
    print("=" * 80)
    
    # ===============================================
    # НАСТРОЙКИ ОТЛАДКИ
    # ===============================================
    
    # ПУТИ К JSON ФАЙЛАМ
    resume_json_path = "/Users/mask/Documents/Проеты_2025/gpt_4_mini_hackaton_final/tests/test_models_res_vac/fetched_resume_6d807532ff0ed6b79f0039ed1f63386d724a62.json"      # 👈 УКАЖИТЕ ПУТЬ К РЕЗЮМЕ
    vacancy_json_path = "/Users/mask/Documents/Проеты_2025/gpt_4_mini_hackaton_final/tests/test_models_res_vac/fetched_vacancy_120234346.json"    # 👈 УКАЖИТЕ ПУТЬ К ВАКАНСИИ
    
    # ФЛАГИ УПРАВЛЕНИЯ (True/False)
    run_cover_letter_generation = True  # 👈 Запустить реальную генерацию письма
    show_model_info = True              # 👈 Показать информацию о Pydantic модели
    
    # ===============================================
    
    try:
        # Информация о модели
        if show_model_info:
            await debug_pydantic_model_info()
        
        # Реальная генерация сопроводительного письма
        if run_cover_letter_generation:
            await debug_cover_letter_response(resume_json_path, vacancy_json_path)
        
        print("\n" + "="*80)
        print("✅ ОТЛАДКА ОТВЕТА ГЕНЕРАЦИИ СОПРОВОДИТЕЛЬНОГО ПИСЬМА ЗАВЕРШЕНА!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())