# src/llm_gap_analyzer/formatter.py
"""
Модуль для форматирования данных резюме и вакансии перед отправкой в LLM.
"""

def format_resume_data(resume_data: dict) -> str:
    """
    Форматирует данные резюме в читаемый текстовый формат.
    
    Args:
        resume_data: Словарь с данными резюме
        
    Returns:
        str: Форматированный текст резюме
    """
    formatted_text = "## РЕЗЮМЕ\n\n"
    
    # Основная информация
    formatted_text += "### Желаемая должность\n"
    formatted_text += f"{resume_data.get('title', 'Не указана')}\n\n"
    
    # Навыки и компетенции
    formatted_text += "### Описание навыков\n"
    formatted_text += f"{resume_data.get('skills', 'Не указаны')}\n\n"
    
    # Ключевые навыки
    formatted_text += "### Ключевые навыки\n"
    skill_set = resume_data.get('skill_set', [])
    if skill_set:
        for skill in skill_set:
            formatted_text += f"- {skill}\n"
    else:
        formatted_text += "Не указаны\n"
    formatted_text += "\n"
    
    # Опыт работы
    formatted_text += "### Опыт работы\n"
    experience_list = resume_data.get('experience', [])
    if experience_list:
        for i, exp in enumerate(experience_list, 1):
            position = exp.get('position', 'Должность не указана')
            start = exp.get('start', 'Дата не указана')
            end = exp.get('end', 'по настоящее время')
            description = exp.get('description', 'Описание отсутствует')
            
            formatted_text += f"#### Опыт работы #{i}: {position}\n"
            formatted_text += f"Период: {start} - {end}\n"
            formatted_text += f"Описание: {description}\n\n"
    else:
        formatted_text += "Опыт работы не указан\n\n"
    
    # Профессиональные роли
    formatted_text += "### Профессиональные роли\n"
    roles = resume_data.get('professional_roles', [])
    if roles:
        for role in roles:
            formatted_text += f"- {role.get('name', '')}\n"
    else:
        formatted_text += "Не указаны\n"
    formatted_text += "\n"
    
    # Дополнительная информация
    formatted_text += "### Предпочитаемые типы занятости\n"
    employments = resume_data.get('employments', [])
    if employments:
        for employment in employments:
            formatted_text += f"- {employment}\n"
    else:
        formatted_text += "Не указаны\n"
    formatted_text += "\n"
    
    formatted_text += "### Предпочитаемый график работы\n"
    schedules = resume_data.get('schedules', [])
    if schedules:
        for schedule in schedules:
            formatted_text += f"- {schedule}\n"
    else:
        formatted_text += "Не указан\n"
    formatted_text += "\n"
    
    # Языки
    formatted_text += "### Знание языков\n"
    languages = resume_data.get('languages', [])
    if languages:
        for lang in languages:
            name = lang.get('name', '')
            level = lang.get('level', {}).get('name', '')
            formatted_text += f"- {name}: {level}\n"
    else:
        formatted_text += "Не указаны\n"
    formatted_text += "\n"
    
    # Зарплатные ожидания
    salary = resume_data.get('salary', {})
    if salary and salary.get('amount'):
        formatted_text += f"### Зарплатные ожидания\n{salary.get('amount')} руб.\n\n"
    
    return formatted_text


def format_vacancy_data(vacancy_data: dict) -> str:
    """
    Форматирует данные вакансии в читаемый текстовый формат.
    
    Args:
        vacancy_data: Словарь с данными вакансии
        
    Returns:
        str: Форматированный текст вакансии
    """
    formatted_text = "## ВАКАНСИЯ\n\n"
    
    # Описание вакансии
    formatted_text += "### Описание вакансии\n"
    formatted_text += f"{vacancy_data.get('description', 'Не указано')}\n\n"
    
    # Ключевые навыки
    formatted_text += "### Ключевые навыки (требуемые)\n"
    key_skills = vacancy_data.get('key_skills', [])
    if key_skills:
        for skill in key_skills:
            formatted_text += f"- {skill}\n"
    else:
        formatted_text += "Не указаны\n"
    formatted_text += "\n"
    
    # Требуемый опыт
    experience = vacancy_data.get('experience', {})
    if experience and experience.get('id'):
        exp_id = experience.get('id')
        exp_text = ""
        
        # Маппинг идентификаторов опыта на человекочитаемые значения
        if exp_id == 'noExperience':
            exp_text = "Без опыта"
        elif exp_id == 'between1And3':
            exp_text = "От 1 года до 3 лет"
        elif exp_id == 'between3And6':
            exp_text = "От 3 до 6 лет"
        elif exp_id == 'moreThan6':
            exp_text = "Более 6 лет"
        else:
            exp_text = exp_id
            
        formatted_text += f"### Требуемый опыт работы\n{exp_text}\n\n"
    
    # Тип занятости
    employment = vacancy_data.get('employment', {})
    if employment and employment.get('id'):
        emp_id = employment.get('id')
        emp_text = ""
        
        # Маппинг идентификаторов занятости на человекочитаемые значения
        if emp_id == 'full':
            emp_text = "Полная занятость"
        elif emp_id == 'part':
            emp_text = "Частичная занятость"
        elif emp_id == 'project':
            emp_text = "Проектная работа"
        elif emp_id == 'volunteer':
            emp_text = "Волонтерство"
        elif emp_id == 'probation':
            emp_text = "Стажировка"
        else:
            emp_text = emp_id
            
        formatted_text += f"### Тип занятости\n{emp_text}\n\n"
    
    # График работы
    schedule = vacancy_data.get('schedule', {})
    if schedule and schedule.get('id'):
        sch_id = schedule.get('id')
        sch_text = ""
        
        # Маппинг идентификаторов графика на человекочитаемые значения
        if sch_id == 'fullDay':
            sch_text = "Полный день"
        elif sch_id == 'shift':
            sch_text = "Сменный график"
        elif sch_id == 'flexible':
            sch_text = "Гибкий график"
        elif sch_id == 'remote':
            sch_text = "Удаленная работа"
        elif sch_id == 'flyInFlyOut':
            sch_text = "Вахтовый метод"
        else:
            sch_text = sch_id
            
        formatted_text += f"### График работы\n{sch_text}\n\n"
    
    return formatted_text