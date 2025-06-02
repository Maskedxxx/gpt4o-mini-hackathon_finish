# src/llm_interview_checklist/formatter.py
"""
Модуль для форматирования данных резюме и вакансии для генерации чек-листа подготовки к интервью.
"""

def format_resume_for_interview_prep(resume_data: dict) -> str:
    """
    Форматирует данные резюме для анализа текущих компетенций кандидата.
    
    Args:
        resume_data: Словарь с данными резюме
        
    Returns:
        str: Форматированный текст резюме для анализа
    """
    formatted_text = "## ТЕКУЩИЕ КОМПЕТЕНЦИИ КАНДИДАТА\n\n"
    
    # Текущая специализация
    formatted_text += "### Текущая специализация\n"
    formatted_text += f"{resume_data.get('title', 'Не указана')}\n\n"
    
    # Описание навыков и опыта
    formatted_text += "### Общее описание профессиональных навыков\n"
    formatted_text += f"{resume_data.get('skills', 'Не указаны')}\n\n"
    
    # Технические навыки
    formatted_text += "### Текущие технические навыки\n"
    skill_set = resume_data.get('skill_set', [])
    if skill_set:
        for skill in skill_set:
            formatted_text += f"- {skill}\n"
    else:
        formatted_text += "Не указаны\n"
    formatted_text += "\n"
    
    # Детальный анализ опыта работы
    formatted_text += "### Профессиональный опыт (для оценки практических навыков)\n"
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
            formatted_text += f"Описание проектов и задач: {description}\n\n"
    else:
        formatted_text += "Опыт работы не указан\n\n"
    
    # Профессиональные роли
    professional_roles = resume_data.get('professional_roles', [])
    if professional_roles:
        formatted_text += "### Профессиональные роли\n"
        for role in professional_roles:
            formatted_text += f"- {role.get('name', '')}\n"
        formatted_text += "\n"
    
    # Языки (важно для некоторых позиций)
    languages = resume_data.get('languages', [])
    if languages:
        formatted_text += "### Знание языков\n"
        for lang in languages:
            name = lang.get('name', '')
            level = lang.get('level', {}).get('name', '')
            formatted_text += f"- {name}: {level}\n"
        formatted_text += "\n"
    
    return formatted_text


def format_vacancy_for_interview_prep(vacancy_data: dict) -> str:
    """
    Форматирует данные вакансии для понимания требований к кандидату.
    
    Args:
        vacancy_data: Словарь с данными вакансии
        
    Returns:
        str: Форматированный текст вакансии для анализа требований
    """
    formatted_text = "## ТРЕБОВАНИЯ ЦЕЛЕВОЙ ПОЗИЦИИ\n\n"
    
    # Полное описание вакансии
    formatted_text += "### Полное описание вакансии и требований\n"
    formatted_text += f"{vacancy_data.get('description', 'Не указано')}\n\n"
    
    # Ключевые технические навыки
    formatted_text += "### Требуемые ключевые навыки\n"
    key_skills = vacancy_data.get('key_skills', [])
    if key_skills:
        for skill in key_skills:
            formatted_text += f"- {skill}\n"
    else:
        formatted_text += "Не указаны\n"
    formatted_text += "\n"
    
    # Требуемый опыт работы
    experience = vacancy_data.get('experience', {})
    if experience and experience.get('id'):
        exp_mapping = {
            'noExperience': 'Без опыта (позиция для начинающих специалистов)',
            'between1And3': 'От 1 года до 3 лет (Junior/Middle уровень)',
            'between3And6': 'От 3 до 6 лет (Middle/Senior уровень)',
            'moreThan6': 'Более 6 лет (Senior+ уровень)'
        }
        exp_text = exp_mapping.get(experience.get('id'), experience.get('id'))
        formatted_text += f"### Требуемый уровень опыта\n{exp_text}\n\n"
    
    # Тип занятости и график (может влиять на вопросы об адаптации)
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
    
    schedule = vacancy_data.get('schedule', {})
    if schedule and schedule.get('id'):
        sch_mapping = {
            'fullDay': 'Полный день',
            'shift': 'Сменный график',
            'flexible': 'Гибкий график',
            'remote': 'Удаленная работа',
            'flyInFlyOut': 'Вахтовый метод'
        }
        sch_text = sch_mapping.get(schedule.get('id'), schedule.get('id'))
        formatted_text += f"### График работы\n{sch_text}\n\n"
    
    return formatted_text