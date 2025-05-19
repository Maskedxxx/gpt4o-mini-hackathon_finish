# src/llm_update_resume/formatter.py
"""
Модуль для форматирования данных резюме и результатов анализа перед отправкой в LLM.
"""
# Вам нужно будет импортировать вашу новую модель отчета здесь
# from src.models.your_new_models import ResumeTailoringAnalysisReport, ModificationInstruction # Пример

# Для type hinting, если вы вынесли модели в отдельный файл.
# Если нет, то можно использовать 'Any' или строковый литерал с названием класса, если он определен позже.
# В данном примере я предполагаю, что ResumeTailoringAnalysisReport будет доступен.
# Если вы его не импортируете, замените ResumeTailoringAnalysisReport на Any или соответствующий класс.
from typing import Any # Замените Any на вашу модель, если она импортируется

# Допустим, ваша модель отчета называется ResumeTailoringAnalysisReport
# и содержит вложенные модели ExperienceRecommendationsReport и ModificationInstruction.
# Эти классы должны быть определены где-то в ваших моделях.
# Для примера я не буду их импортировать, а использую Any для gap_result,
# но в реальном коде лучше использовать точные типы.


def format_resume_for_rewrite(resume_data: dict) -> str:
    """
    Форматирует данные резюме для анализа первым LLM (аналитиком).
    
    Args:
        resume_data: Словарь с данными резюме. 
                     Ожидается, что каждый элемент в resume_data['experience'] 
                     содержит ключ 'company'.
        
    Returns:
        str: Форматированный текст резюме для LLM-аналитика.
    """
    formatted_text = "## ТЕКУЩЕЕ РЕЗЮМЕ ДЛЯ АНАЛИЗА\n\n"
    
    formatted_text += "### Желаемая должность\n"
    formatted_text += f"{resume_data.get('title', 'Не указана')}\n\n"
    
    formatted_text += "### Описание навыков (общее)\n"
    formatted_text += f"{resume_data.get('skills', 'Не указаны')}\n\n"
    
    formatted_text += "### Ключевые навыки (список)\n"
    skill_set = resume_data.get('skill_set', [])
    if skill_set:
        for skill in skill_set:
            formatted_text += f"- {skill}\n"
    else:
        formatted_text += "Не указаны\n"
    formatted_text += "\n"
    
    formatted_text += "### Опыт работы\n"
    experience_list = resume_data.get('experience', [])
    if experience_list:
        for i, exp in enumerate(experience_list, 1):
            company = exp.get('company', 'Компания не указана') 
            position = exp.get('position', 'Должность не указана')
            start = exp.get('start', 'Дата не указана')
            end = exp.get('end', 'по настоящее время')
            description = exp.get('description', 'Описание отсутствует')
            
            experience_id = f"ОПЫТ_ID_{i} [{company} - {position}]"
            
            formatted_text += f"#### Опыт работы (ID: {experience_id})\n"
            formatted_text += f"Период: {start} - {end}\n"
            formatted_text += f"Оригинальное описание: {description}\n\n"
    else:
        formatted_text += "Опыт работы не указан\n\n"
    
    if 'professional_roles' in resume_data: # Проверка на наличие ключа
        formatted_text += "### Профессиональные роли\n"
        roles = resume_data.get('professional_roles', [])
        if roles:
            for role in roles:
                formatted_text += f"- {role.get('name', '')}\n"
        else:
            formatted_text += "Не указаны\n"
        formatted_text += "\n"
    
    return formatted_text


def format_gap_analysis_report_for_rewriter(gap_report: Any) -> str: # Замените Any на ResumeTailoringAnalysisReport
    """
    Форматирует отчет от LLM-аналитика для LLM-копирайтера.
    
    Args:
        gap_report: Объект с результатами анализа (например, ResumeTailoringAnalysisReport).
        
    Returns:
        str: Форматированный текст отчета с инструкциями для LLM-копирайтера.
    """
    formatted_text = "## ЗАДАНИЕ НА АДАПТАЦИЮ РЕЗЮМЕ (ОТЧЕТ ОТ LLM-АНАЛИТИКА)\n\n"
    
    if hasattr(gap_report, 'suggested_resume_title'):
        formatted_text += "### 1. Предлагаемый заголовок резюме (Желаемая должность):\n"
        formatted_text += f"{gap_report.suggested_resume_title}\n\n"
    
    if hasattr(gap_report, 'suggested_skills_description_for_rewriter'):
        formatted_text += "### 2. Рекомендации для 'Описания навыков' (общее summary):\n"
        formatted_text += f"Предлагаемая основа для переписывания:\n{gap_report.suggested_skills_description_for_rewriter}\n\n"

    if hasattr(gap_report, 'suggested_skill_set_for_rewriter') and gap_report.suggested_skill_set_for_rewriter:
        formatted_text += "### 3. Рекомендуемый 'Ключевой набор навыков' (список):\n"
        for skill in gap_report.suggested_skill_set_for_rewriter:
            formatted_text += f"- {skill}\n"
        formatted_text += "\n"
    
    if hasattr(gap_report, 'experience_reports') and gap_report.experience_reports:
        formatted_text += "### 4. Инструкции по адаптации опыта работы:\n"
        for i, report_item in enumerate(gap_report.experience_reports, 1):
            formatted_text += f"\n#### 4.{i} Для опыта (ID: {report_item.experience_identifier})\n"
            
            if hasattr(report_item, 'original_description'):
                formatted_text += f"**Оригинальное описание (для контекста LLM-копирайтера):**\n{report_item.original_description}\n\n"
            
            if hasattr(report_item, 'overall_assessment'):
                formatted_text += f"**Общая оценка и стратегия адаптации от LLM-аналитика:**\n{report_item.overall_assessment}\n\n"
            
            if hasattr(report_item, 'modification_instructions') and report_item.modification_instructions:
                formatted_text += "**Конкретные инструкции по изменению от LLM-аналитика:**\n"
                for instr_num, instruction in enumerate(report_item.modification_instructions, 1):
                    formatted_text += f"  Инструкция #{instr_num}:\n"
                    formatted_text += f"    Действие: {instruction.action}\n"
                    if hasattr(instruction, 'target_description_fragment') and instruction.target_description_fragment:
                        formatted_text += f"    Целевой фрагмент (из оригинала): \"{instruction.target_description_fragment}\"\n"
                    formatted_text += f"    Детали инструкции: {instruction.instruction_details}\n"
                    if hasattr(instruction, 'vacancy_relevance_reason'):
                         formatted_text += f"    Обоснование (релевантность вакансии): {instruction.vacancy_relevance_reason}\n"
                    formatted_text += "\n" # Пустая строка после каждой инструкции
            else:
                formatted_text += "- Конкретных инструкций по изменению нет.\n\n"
    
    return formatted_text

# Старые вспомогательные функции _get_section_name и _get_recommendation_type
# больше не нужны для format_gap_analysis_report_for_rewriter, если вы напрямую выводите данные.
# Если они используются где-то еще, их можно оставить. 
# В данном контексте они удалены, так как новая функция их не использует.