# src/llm_cover_letter/formatter.py
"""
Модуль для форматирования данных резюме и вакансии для генерации рекомендательного письма.
"""

def format_resume_for_cover_letter(resume_data: dict) -> str:
    """
    Форматирует данные резюме для создания рекомендательного письма.
    
    Args:
        resume_data: Словарь с данными резюме
        
    Returns:
        str: Форматированный текст резюме
    """
    formatted_text = "## ДАННЫЕ СОИСКАТЕЛЯ\n\n"
    
    # Желаемая должность
    formatted_text += "### Специализация соискателя\n"
    formatted_text += f"{resume_data.get('title', 'Не указана')}\n\n"
    
    # Навыки и компетенции
    formatted_text += "### Профессиональное описание\n"
    formatted_text += f"{resume_data.get('skills', 'Не указаны')}\n\n"
    
    # Ключевые навыки
    formatted_text += "### Технические навыки и компетенции\n"
    skill_set = resume_data.get('skill_set', [])
    if skill_set:
        for skill in skill_set:
            formatted_text += f"- {skill}\n"
    else:
        formatted_text += "Не указаны\n"
    formatted_text += "\n"
    
    # Опыт работы (основные достижения)
    formatted_text += "### Профессиональный опыт и достижения\n"
    experience_list = resume_data.get('experience', [])
    if experience_list:
        for i, exp in enumerate(experience_list, 1):
            company = exp.get('company', 'Компания не указана')
            position = exp.get('position', 'Должность не указана')
            start = exp.get('start', '')
            end = exp.get('end', 'по настоящее время')
            description = exp.get('description', 'Описание отсутствует')
            
            formatted_text += f"#### Опыт #{i}: {position} в {company}\n"
            formatted_text += f"Период: {start} - {end}\n"
            formatted_text += f"Ключевые достижения: {description}\n\n"
    else:
        formatted_text += "Опыт работы не указан\n\n"
    
    # Языки
    languages = resume_data.get('languages', [])
    if languages:
        formatted_text += "### Знание языков\n"
        for lang in languages:
            name = lang.get('name', '')
            level = lang.get('level', {}).get('name', '')
            formatted_text += f"- {name}: {level}\n"
        formatted_text += "\n"
    
    return formatted_text


def format_vacancy_for_cover_letter(vacancy_data: dict) -> str:
    """
    Форматирует данные вакансии для создания рекомендательного письма.
    
    Args:
        vacancy_data: Словарь с данными вакансии
        
    Returns:
        str: Форматированный текст вакансии
    """
    formatted_text = "## ИНФОРМАЦИЯ О ЦЕЛЕВОЙ ВАКАНСИИ\n\n"
    
    # Требования вакансии
    formatted_text += "### Описание вакансии и требования\n"
    formatted_text += f"{vacancy_data.get('description', 'Не указано')}\n\n"
    
    # Ключевые навыки
    formatted_text += "### Требуемые навыки\n"
    key_skills = vacancy_data.get('key_skills', [])
    if key_skills:
        for skill in key_skills:
            formatted_text += f"- {skill}\n"
    else:
        formatted_text += "Не указаны\n"
    formatted_text += "\n"
    
    # Опыт работы
    experience = vacancy_data.get('experience', {})
    if experience and experience.get('id'):
        exp_mapping = {
            'noExperience': 'Без опыта',
            'between1And3': 'От 1 года до 3 лет',
            'between3And6': 'От 3 до 6 лет',
            'moreThan6': 'Более 6 лет'
        }
        exp_text = exp_mapping.get(experience.get('id'), experience.get('id'))
        formatted_text += f"### Требуемый опыт\n{exp_text}\n\n"
    
    # Тип занятости и график
    employment = vacancy_data.get('employment', {})
    if employment and employment.get('id'):
        emp_mapping = {
            'full': 'Полная занятость',
            'part': 'Частичная занятость',
            'project': 'Проектная работа',
            'volunteer': 'Волонтерство',
            'probation': 'Стажировка'
        }
        emp_text = emp_mapping.get(employment.get('id'), employment.get('id'))
        formatted_text += f"### Тип занятости\n{emp_text}\n\n"
    
    return formatted_text