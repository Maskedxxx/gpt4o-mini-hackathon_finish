#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для отладки ответа LLM в GAP-анализе.
Вызывает реальный анализ и показывает структурированный результат.

Показывает:
1. Ответ от LLM в Pydantic структуре
2. JSON представление ответа
3. Детализацию по полям модели

Использование:
    python tests/debug_gap/debug_gap_response.py
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
from src.llm_gap_analyzer.llm_gap_analyzer import LLMGapAnalyzer
from src.models.gap_analysis_models import EnhancedResumeTailoringAnalysis
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

def show_gap_analysis_structure(gap_result: EnhancedResumeTailoringAnalysis) -> None:
    """Показывает структуру результата GAP-анализа по полям."""
    print("\n" + "="*80)
    print("📊 СТРУКТУРА РЕЗУЛЬТАТА GAP-АНАЛИЗА")
    print("="*80)
    
    try:
        print("🔸 ПЕРВИЧНЫЙ СКРИНИНГ:")
        ps = gap_result.primary_screening
        print(f"   • Соответствие должности: {ps.job_title_match}")
        print(f"   • Достаточный опыт: {ps.experience_years_match}")
        print(f"   • Видны ключевые навыки: {ps.key_skills_visible}")
        print(f"   • Подходящая локация: {ps.location_suitable}")
        print(f"   • Зарплатные ожидания: {ps.salary_expectations_match}")
        print(f"   • Общий результат: {ps.overall_screening_result}")
        
        print("\n🔸 АНАЛИЗ ТРЕБОВАНИЙ:")
        ra = gap_result.requirements_analysis
        must_have = [req for req in ra if req.requirement_type == "MUST_HAVE"]
        nice_to_have = [req for req in ra if req.requirement_type == "NICE_TO_HAVE"]
        bonus = [req for req in ra if req.requirement_type == "BONUS"]
        print(f"   • MUST-HAVE требований: {len(must_have)}")
        print(f"   • NICE-TO-HAVE требований: {len(nice_to_have)}")
        print(f"   • БОНУС требований: {len(bonus)}")
        print(f"   • Всего требований: {len(ra)}")
        
        print("\n🔸 ОЦЕНКА КАЧЕСТВА:")
        qa = gap_result.quality_assessment
        print(f"   • Структурированность: {qa.structure_clarity}/10")
        print(f"   • Релевантность содержания: {qa.content_relevance}/10")
        print(f"   • Фокус на достижения: {qa.achievement_focus}/10")
        print(f"   • Адаптация под вакансию: {qa.adaptation_quality}/10")
        print(f"   • Общее впечатление: {qa.overall_impression}")
        
        print("\n🔸 РЕКОМЕНДАЦИИ:")
        print(f"   • Критичных: {len(gap_result.critical_recommendations)}")
        print(f"   • Важных: {len(gap_result.important_recommendations)}")
        print(f"   • Желательных: {len(gap_result.optional_recommendations)}")
        
        print("\n🔸 ИТОГОВЫЕ ВЫВОДЫ:")
        print(f"   • Процент соответствия: {gap_result.overall_match_percentage}%")
        print(f"   • Рекомендация по найму: {gap_result.hiring_recommendation}")
        print(f"   • Ключевых сильных сторон: {len(gap_result.key_strengths)}")
        print(f"   • Основных пробелов: {len(gap_result.major_gaps)}")
        
    except Exception as e:
        print(f"❌ Ошибка отображения структуры: {e}")

def show_detailed_analysis(gap_result: EnhancedResumeTailoringAnalysis) -> None:
    """Показывает детальный анализ всех разделов."""
    print("\n" + "="*80)
    print("📋 ДЕТАЛЬНЫЙ АНАЛИЗ РЕЗУЛЬТАТОВ")
    print("="*80)
    
    try:
        # Анализ требований по типам
        requirements = gap_result.requirements_analysis
        
        # MUST-HAVE требования
        must_have_reqs = [req for req in requirements if req.requirement_type == "MUST_HAVE"]
        if must_have_reqs:
            print("🔴 MUST-HAVE ТРЕБОВАНИЯ:")
            for req in must_have_reqs:
                status_icon = "✅" if req.compliance_status == "ПОЛНОЕ_СООТВЕТСТВИЕ" else \
                             "⚠️" if req.compliance_status == "ЧАСТИЧНОЕ_СООТВЕТСТВИЕ" else \
                             "❓" if req.compliance_status == "ТРЕБУЕТ_УТОЧНЕНИЯ" else "❌"
                print(f"   {status_icon} {req.requirement_text}")
                print(f"      Статус: {req.compliance_status}")
                if req.evidence_in_resume:
                    print(f"      Подтверждение: {req.evidence_in_resume}")
                if req.gap_description:
                    print(f"      Пробел: {req.gap_description}")
        
        # NICE-TO-HAVE требования
        nice_to_have_reqs = [req for req in requirements if req.requirement_type == "NICE_TO_HAVE"]
        if nice_to_have_reqs:
            print("\n🟡 NICE-TO-HAVE ТРЕБОВАНИЯ:")
            for req in nice_to_have_reqs:
                status_icon = "✅" if req.compliance_status == "ПОЛНОЕ_СООТВЕТСТВИЕ" else \
                             "⚠️" if req.compliance_status == "ЧАСТИЧНОЕ_СООТВЕТСТВИЕ" else \
                             "❓" if req.compliance_status == "ТРЕБУЕТ_УТОЧНЕНИЯ" else "❌"
                print(f"   {status_icon} {req.requirement_text}")
                print(f"      Статус: {req.compliance_status}")
                if req.evidence_in_resume:
                    print(f"      Подтверждение: {req.evidence_in_resume}")
        
        # BONUS требования
        bonus_reqs = [req for req in requirements if req.requirement_type == "BONUS"]
        if bonus_reqs:
            print("\n🟢 БОНУС ТРЕБОВАНИЯ:")
            for req in bonus_reqs:
                status_icon = "✅" if req.compliance_status == "ПОЛНОЕ_СООТВЕТСТВИЕ" else \
                             "⚠️" if req.compliance_status == "ЧАСТИЧНОЕ_СООТВЕТСТВИЕ" else \
                             "❓" if req.compliance_status == "ТРЕБУЕТ_УТОЧНЕНИЯ" else "❌"
                print(f"   {status_icon} {req.requirement_text}")
                print(f"      Статус: {req.compliance_status}")
        
        # Критичные рекомендации
        if gap_result.critical_recommendations:
            print("\n🚨 КРИТИЧНЫЕ РЕКОМЕНДАЦИИ:")
            for rec in gap_result.critical_recommendations:
                print(f"   • Секция: {rec.section}")
                print(f"     Проблема: {rec.issue_description}")
                print(f"     Критичность: {rec.criticality}")
                if rec.specific_actions:
                    print(f"     Действия:")
                    for action in rec.specific_actions:
                        print(f"       - {action}")
                if rec.example_wording:
                    print(f"     Пример: {rec.example_wording}")
        
        # Важные рекомендации
        if gap_result.important_recommendations:
            print("\n⚠️ ВАЖНЫЕ РЕКОМЕНДАЦИИ:")
            for rec in gap_result.important_recommendations:
                print(f"   • Секция: {rec.section}")
                print(f"     Проблема: {rec.issue_description}")
                print(f"     Критичность: {rec.criticality}")
                if rec.specific_actions:
                    print(f"     Действия:")
                    for action in rec.specific_actions:
                        print(f"       - {action}")
        
        # Желательные рекомендации
        if gap_result.optional_recommendations:
            print("\n💡 ЖЕЛАТЕЛЬНЫЕ РЕКОМЕНДАЦИИ:")
            for rec in gap_result.optional_recommendations:
                print(f"   • Секция: {rec.section}")
                print(f"     Проблема: {rec.issue_description}")
                if rec.specific_actions:
                    print(f"     Действия:")
                    for action in rec.specific_actions:
                        print(f"       - {action}")
        
        # Сильные стороны и пробелы
        print(f"\n💪 КЛЮЧЕВЫЕ СИЛЬНЫЕ СТОРОНЫ:")
        for strength in gap_result.key_strengths:
            print(f"   • {strength}")
        
        if gap_result.major_gaps:
            print(f"\n🔍 ОСНОВНЫЕ ПРОБЕЛЫ:")
            for gap in gap_result.major_gaps:
                print(f"   • {gap}")
        
        print(f"\n📋 СЛЕДУЮЩИЕ ШАГИ:")
        print(f"   {gap_result.next_steps}")
        
    except Exception as e:
        print(f"❌ Ошибка детального анализа: {e}")

async def debug_gap_analysis_response(resume_json_path: str, vacancy_json_path: str) -> None:
    """Вызывает реальный GAP-анализ и показывает результат."""
    print("\n" + "="*80)
    print("🤖 РЕЗУЛЬТАТ GAP-АНАЛИЗА ОТ LLM")
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
    
    print("✅ Данные подготовлены, запускаем GAP-анализ...")
    
    try:
        # Создаем экземпляр анализатора и запускаем анализ
        gap_analyzer = LLMGapAnalyzer()
        
        # Конвертируем в dict как в реальном приложении
        resume_dict = parsed_resume.model_dump()
        vacancy_dict = parsed_vacancy.model_dump()
        
        # ВЫЗЫВАЕМ РЕАЛЬНЫЙ GAP-АНАЛИЗ
        gap_result = await gap_analyzer.gap_analysis(resume_dict, vacancy_dict)
        
        if not gap_result:
            print("❌ GAP-анализ вернул пустой результат")
            return
        
        print("✅ GAP-анализ успешно выполнен!")
        
        # Показываем результат в JSON формате
        print(f"\n📄 РЕЗУЛЬТАТ В JSON ФОРМАТЕ:")
        print("-" * 60)
        result_json = gap_result.model_dump()
        print(json.dumps(result_json, ensure_ascii=False, indent=2))
        
        # Показываем структуру
        show_gap_analysis_structure(gap_result)
        
        # Показываем детальный анализ
        show_detailed_analysis(gap_result)
        
    except Exception as e:
        print(f"❌ Ошибка выполнения GAP-анализа: {e}")

async def debug_pydantic_model_info() -> None:
    """Показывает информацию о Pydantic модели результата."""
    print("\n" + "="*80)
    print("📚 ИНФОРМАЦИЯ О МОДЕЛИ EnhancedResumeTailoringAnalysis")
    print("="*80)
    
    try:
        # Получаем схему модели
        schema = EnhancedResumeTailoringAnalysis.model_json_schema()
        
        print("🔸 ОСНОВНЫЕ ПОЛЯ МОДЕЛИ:")
        properties = schema.get('properties', {})
        for field_name, field_info in properties.items():
            field_type = field_info.get('type', 'unknown')
            description = field_info.get('description', 'Описание отсутствует')
            print(f"   • {field_name} ({field_type}): {description}")
        
        print(f"\n🔸 ВСЕГО ПОЛЕЙ В МОДЕЛИ: {len(properties)}")
        
        # Показываем required поля
        required = schema.get('required', [])
        print(f"🔸 ОБЯЗАТЕЛЬНЫХ ПОЛЕЙ: {len(required)}")
        for field in required:
            print(f"   • {field}")
            
    except Exception as e:
        print(f"❌ Ошибка анализа модели: {e}")

async def main():
    """Основная функция для запуска отладки ответа GAP-анализа."""
    
    # Настраиваем логирование
    setup_logging(log_level="INFO")
    
    print("🔍 ОТЛАДКА ОТВЕТА LLM В GAP-АНАЛИЗЕ")
    print("=" * 80)
    
    # ===============================================
    # НАСТРОЙКИ ОТЛАДКИ
    # ===============================================
    
    # ПУТИ К JSON ФАЙЛАМ
    resume_json_path = "path/to/your/resume.json"      # 👈 УКАЖИТЕ ПУТЬ К РЕЗЮМЕ
    vacancy_json_path = "path/to/your/vacancy.json"    # 👈 УКАЖИТЕ ПУТЬ К ВАКАНСИИ
    
    # ФЛАГИ УПРАВЛЕНИЯ (True/False)
    run_gap_analysis = True        # 👈 Запустить реальный GAP-анализ
    show_model_info = True         # 👈 Показать информацию о Pydantic модели
    
    # ===============================================
    
    try:
        # Информация о модели
        if show_model_info:
            await debug_pydantic_model_info()
        
        # Реальный GAP-анализ
        if run_gap_analysis:
            await debug_gap_analysis_response(resume_json_path, vacancy_json_path)
        
        print("\n" + "="*80)
        print("✅ ОТЛАДКА ОТВЕТА GAP-АНАЛИЗА ЗАВЕРШЕНА!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())