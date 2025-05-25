# src/llm_interview_simulation/formatter.py
"""
Модуль для форматирования данных резюме и вакансии для симуляции интервью.
"""

def format_resume_for_interview_simulation(resume_data: dict) -> str:
    """
    Форматирует данные резюме для симуляции интервью.
    
    Args:
        resume_data: Словарь с данными резюме
        
    Returns:
        str: Форматированный текст резюме для симуляции
    """
    formatted_text = "## ИНФОРМАЦИЯ О КАНДИДАТЕ\n\n"
    
    # Желаемая должность
    formatted_text += "### Специализация кандидата\n"
    formatted_text += f"{resume_data.get('title', 'Не указана')}\n\n"
    
    # Профессиональное описание
    formatted_text += "### Профессиональное описание навыков\n"
    formatted_text += f"{resume_data.get('skills', 'Не указаны')}\n\n"
    
    # Ключевые навыки
    formatted_text += "### Технические навыки кандидата\n"
    skill_set = resume_data.get('skill_set', [])
    if skill_set:
        for skill in skill_set:
            formatted_text += f"- {skill}\n"
    else:
        formatted_text += "Не указаны\n"
    formatted_text += "\n"
    
    # Детальный опыт работы для глубоких вопросов
    formatted_text += "### Профессиональный опыт кандидата\n"
    experience_list = resume_data.get('experience', [])
    if experience_list:
        for i, exp in enumerate(experience_list, 1):
            company = exp.get('company', 'Компания не указана')
            position = exp.get('position', 'Должность не указана')
            start = exp.get('start', '')
            end = exp.get('end', 'по настоящее время')
            description = exp.get('description', 'Описание отсутствует')
            
            formatted_text += f"#### Опыт работы #{i}: {position} в {company}\n"
            formatted_text += f"Период работы: {start} - {end}\n"
            formatted_text += f"Описание деятельности: {description}\n\n"
    else:
        formatted_text += "Опыт работы не указан\n\n"
    
    # Профессиональные роли
    professional_roles = resume_data.get('professional_roles', [])
    if professional_roles:
        formatted_text += "### Профессиональные роли\n"
        for role in professional_roles:
            formatted_text += f"- {role.get('name', '')}\n"
        formatted_text += "\n"
    
    # Знание языков
    languages = resume_data.get('languages', [])
    if languages:
        formatted_text += "### Знание языков\n"
        for lang in languages:
            name = lang.get('name', '')
            level = lang.get('level', {}).get('name', '')
            formatted_text += f"- {name}: {level}\n"
        formatted_text += "\n"
    
    # Предпочитаемые условия работы
    employments = resume_data.get('employments', [])
    if employments:
        formatted_text += "### Предпочитаемый тип занятости\n"
        for employment in employments:
            formatted_text += f"- {employment}\n"
        formatted_text += "\n"
    
    schedules = resume_data.get('schedules', [])
    if schedules:
        formatted_text += "### Предпочитаемый график работы\n"
        for schedule in schedules:
            formatted_text += f"- {schedule}\n"
        formatted_text += "\n"
    
    # Зарплатные ожидания
    salary = resume_data.get('salary', {})
    if salary and salary.get('amount'):
        formatted_text += f"### Зарплатные ожидания\n{salary.get('amount')} руб.\n\n"
    
    return formatted_text


def format_vacancy_for_interview_simulation(vacancy_data: dict) -> str:
    """
    Форматирует данные вакансии для симуляции интервью.
    
    Args:
        vacancy_data: Словарь с данными вакансии
        
    Returns:
        str: Форматированный текст вакансии для симуляции
    """
    formatted_text = "## ИНФОРМАЦИЯ О ВАКАНСИИ И ТРЕБОВАНИЯХ\n\n"
    
    # Полное описание вакансии для контекста
    formatted_text += "### Описание вакансии и требования к кандидату\n"
    formatted_text += f"{vacancy_data.get('description', 'Не указано')}\n\n"
    
    # Ключевые навыки для технических вопросов
    formatted_text += "### Ключевые требуемые навыки\n"
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
            'noExperience': 'Без опыта (Junior позиция)',
            'between1And3': 'От 1 года до 3 лет (Junior/Middle)',
            'between3And6': 'От 3 до 6 лет (Middle/Senior)',
            'moreThan6': 'Более 6 лет (Senior/Lead)'
        }
        exp_text = exp_mapping.get(experience.get('id'), experience.get('id'))
        formatted_text += f"### Требуемый опыт работы\n{exp_text}\n\n"
    
    # Условия работы для соответствующих вопросов
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


def format_dialog_history(dialog_messages: list) -> str:
    """
    Форматирует историю диалога для передачи в LLM.
    
    Args:
        dialog_messages: Список сообщений диалога
        
    Returns:
        str: Форматированная история диалога
    """
    if not dialog_messages:
        return "## ИСТОРИЯ ДИАЛОГА\n\nДиалог только начинается.\n\n"
    
    formatted_text = "## ИСТОРИЯ ПРЕДЫДУЩЕГО ДИАЛОГА\n\n"
    
    for msg in dialog_messages:
        speaker_name = "HR-менеджер" if msg.speaker == "HR" else "Кандидат"
        formatted_text += f"**{speaker_name} (раунд {msg.round_number}):**\n{msg.message}\n\n"
    
    return formatted_text