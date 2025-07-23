# src/llm_resume_rewriter/formatter.py
"""
Модуль для форматирования данных резюме и GAP-анализа перед отправкой в LLM для рерайта.
"""

def format_resume_data(resume_data: dict) -> str:
    """
    Форматирует данные резюме в читаемый markdown формат.
    
    Args:
        resume_data: Словарь с данными резюме
        
    Returns:
        str: Форматированный markdown текст резюме
    """
    formatted_text = "# ТЕКУЩЕЕ РЕЗЮМЕ КАНДИДАТА\n\n"
    
    # Персональная информация
    formatted_text += "## Персональная информация\n"
    first_name = resume_data.get('first_name', '')
    last_name = resume_data.get('last_name', '')
    middle_name = resume_data.get('middle_name', '')
    
    if first_name or last_name or middle_name:
        full_name = f"{last_name} {first_name} {middle_name}".strip()
        formatted_text += f"ФИО: {full_name}\n"
    else:
        formatted_text += "ФИО: Не указано\n"
    
    # Общий опыт работы
    total_experience = resume_data.get('total_experience')
    if total_experience:
        years = total_experience // 12
        months = total_experience % 12
        exp_text = f"{years} лет {months} мес." if years > 0 else f"{months} мес."
        formatted_text += f"**Общий опыт работы:** {exp_text}\n"
    else:
        formatted_text += "**Общий опыт работы:** Не указан\n"
    
    formatted_text += "\n"
    
    # Основная информация
    formatted_text += "## Желаемая должность\n"
    formatted_text += f"{resume_data.get('title', 'Не указана')}\n\n"
    
    # Навыки и компетенции
    formatted_text += "## Описание навыков\n"
    skills = resume_data.get('skills', 'Не указаны')
    if isinstance(skills, list):
        skills = ', '.join(skills)
    formatted_text += f"{skills}\n\n"
    
    # Ключевые навыки
    formatted_text += "## Ключевые навыки\n"
    skill_set = resume_data.get('skill_set', [])
    if skill_set:
        for skill in skill_set:
            formatted_text += f"- {skill}\n"
    else:
        formatted_text += "Не указаны\n"
    formatted_text += "\n"
    
    # Опыт работы
    formatted_text += "## Опыт работы\n"
    experience_list = resume_data.get('experience', [])
    if experience_list:
        for i, exp in enumerate(experience_list, 1):
            position = exp.get('position', 'Должность не указана')
            company = exp.get('company', 'Компания не указана')
            start = exp.get('start', 'Дата не указана')
            end = exp.get('end', 'по настоящее время')
            description = exp.get('description', 'Описание отсутствует')
            
            formatted_text += f"### Опыт работы #{i}: {position}\n"
            formatted_text += f"**Компания:** {company}\n"
            formatted_text += f"**Период:** {start} - {end}\n"
            formatted_text += f"**Описание:**\n {description}\n\n"
    else:
        formatted_text += "Опыт работы не указан\n\n"
    
    # Образование
    education = resume_data.get('education')
    if education:
        formatted_text += "## Образование\n"
        
        # Уровень образования
        level = education.get('level')
        if level and level.get('name'):
            formatted_text += f"**Уровень:** {level.get('name')}\n\n"
        
        # Основное образование
        primary = education.get('primary', [])
        if primary:
            formatted_text += "### Основное образование\n"
            for edu in primary:
                name = edu.get('name', 'Учебное заведение не указано')
                organization = edu.get('organization', '')
                result = edu.get('result', '')
                year = edu.get('year', '')
                
                formatted_text += f"**{name}**"
                if year:
                    formatted_text += f" ({year})"
                formatted_text += "\n"
                
                if organization:
                    formatted_text += f"- Факультет/Организация: {organization}\n"
                if result:
                    formatted_text += f"- Специальность: {result}\n"
                formatted_text += "\n"
        
        # Дополнительное образование
        additional = education.get('additional', [])
        if additional:
            formatted_text += "### Дополнительное образование и сертификаты\n"
            for edu in additional:
                name = edu.get('name', 'Курс не указан')
                organization = edu.get('organization', '')
                result = edu.get('result', '')
                year = edu.get('year', '')
                
                formatted_text += f"**{name}**"
                if year:
                    formatted_text += f" ({year})"
                formatted_text += "\n"
                
                if organization:
                    formatted_text += f"- Организация: {organization}\n"
                if result:
                    formatted_text += f"- Результат: {result}\n"
                formatted_text += "\n"
    
    # Сертификаты
    certificates = resume_data.get('certificate', [])
    if certificates:
        formatted_text += "## Сертификаты\n"
        for cert in certificates:
            title = cert.get('title', 'Название сертификата не указано')
            url = cert.get('url')
            
            if url:
                formatted_text += f"- **{title}** ([ссылка]({url}))\n"
            else:
                formatted_text += f"- **{title}**\n"
        formatted_text += "\n"
    
    # Профессиональные роли
    formatted_text += "## Профессиональные роли\n"
    roles = resume_data.get('professional_roles', [])
    if roles:
        for role in roles:
            formatted_text += f"- {role.get('name', '')}\n"
    else:
        formatted_text += "Не указаны\n"
    formatted_text += "\n"
    
    return formatted_text


def format_gap_analysis_data(gap_analysis_data: dict) -> str:
    """
    Форматирует данные GAP-анализа в читаемый markdown формат.
    
    Args:
        gap_analysis_data: Словарь с результатами GAP-анализа
        
    Returns:
        str: Форматированный markdown текст GAP-анализа
    """
    formatted_text = "# РЕЗУЛЬТАТЫ GAP-АНАЛИЗА\n\n"
    
    # Общий вердикт
    overall_verdict = gap_analysis_data.get('overall_verdict', {})
    if overall_verdict:
        formatted_text += "## Общий вердикт\n"
        formatted_text += f"**Статус:** {overall_verdict.get('status', 'Не указан')}\n"
        formatted_text += f"**Описание:** {overall_verdict.get('explanation', 'Не указано')}\n\n"
    
    # Анализ компетенций
    competency_analysis = gap_analysis_data.get('competency_analysis', [])
    if competency_analysis:
        formatted_text += "## Анализ компетенций\n"
        for comp in competency_analysis:
            area = comp.get('area', {}).get('value', 'Неизвестная область')
            score = comp.get('score', 0)
            explanation = comp.get('explanation', 'Нет пояснений')
            
            formatted_text += f"### {area}\n"
            formatted_text += f"**Оценка:** {score}/10\n"
            formatted_text += f"**Пояснение:** {explanation}\n\n"
    
    # Анализ навыков
    skills_analysis = gap_analysis_data.get('skills_analysis', {})
    if skills_analysis:
        formatted_text += "## Анализ навыков\n"
        
        # Соответствующие навыки
        matching_skills = skills_analysis.get('matching_skills', [])
        if matching_skills:
            formatted_text += "### ✅ Соответствующие навыки\n"
            for skill in matching_skills:
                formatted_text += f"- {skill}\n"
            formatted_text += "\n"
        
        # Недостающие навыки
        missing_skills = skills_analysis.get('missing_skills', [])
        if missing_skills:
            formatted_text += "### ❌ Недостающие навыки\n"
            for skill in missing_skills:
                formatted_text += f"- {skill}\n"
            formatted_text += "\n"
        
        # Дополнительные навыки
        additional_skills = skills_analysis.get('additional_skills', [])
        if additional_skills:
            formatted_text += "### ➕ Дополнительные навыки кандидата\n"
            for skill in additional_skills:
                formatted_text += f"- {skill}\n"
            formatted_text += "\n"
    
    # Рекомендации по улучшению
    improvement_suggestions = gap_analysis_data.get('improvement_suggestions', [])
    if improvement_suggestions:
        formatted_text += "## 🚀 Рекомендации по улучшению резюме\n"
        for i, suggestion in enumerate(improvement_suggestions, 1):
            formatted_text += f"{i}. {suggestion}\n"
        formatted_text += "\n"
    
    # Сильные стороны
    strong_points = gap_analysis_data.get('strong_points', [])
    if strong_points:
        formatted_text += "## 💪 Сильные стороны кандидата\n"
        for point in strong_points:
            formatted_text += f"- {point}\n"
        formatted_text += "\n"
    
    # Слабые стороны
    weak_points = gap_analysis_data.get('weak_points', [])
    if weak_points:
        formatted_text += "## ⚠️ Слабые стороны\n"
        for point in weak_points:
            formatted_text += f"- {point}\n"
        formatted_text += "\n"
    
    return formatted_text