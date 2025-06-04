# src/llm_interview_checklist/formatter.py
"""
Модуль для форматирования данных резюме и вакансии для генерации чек-листа подготовки к интервью.
Расширенная версия с детальным анализом согласно HR-методологии.
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


def format_detailed_resume_analysis(resume_data: dict) -> str:
    """
    Создает детальный анализ резюме для профессионального GAP-анализа.
    
    Args:
        resume_data: Словарь с данными резюме
        
    Returns:
        str: Детальный анализ компетенций кандидата
    """
    formatted_text = "## ДЕТАЛЬНЫЙ АНАЛИЗ КОМПЕТЕНЦИЙ КАНДИДАТА\n\n"
    
    # Анализ стажа и карьерной траектории
    experience_list = resume_data.get('experience', [])
    total_positions = len(experience_list)
    
    formatted_text += "### Карьерная траектория и стаж\n"
    formatted_text += f"Общее количество позиций: {total_positions}\n"
    
    if experience_list:
        latest_position = experience_list[0] if experience_list else {}
        formatted_text += f"Последняя позиция: {latest_position.get('position', 'Не указана')}\n"
        
        # Анализ прогрессии в карьере
        if total_positions > 1:
            formatted_text += "Карьерная прогрессия:\n"
            for i, exp in enumerate(experience_list[:3], 1):  # Первые 3 позиции
                formatted_text += f"  {i}. {exp.get('position', 'Не указана')} - {exp.get('company', 'Компания не указана')}\n"
    formatted_text += "\n"
    
    # Анализ технологического стека
    skill_set = resume_data.get('skill_set', [])
    formatted_text += "### Технологический стек кандидата\n"
    
    if skill_set:
        # Группировка навыков по категориям (упрощенная)
        tech_skills = [skill for skill in skill_set if any(word in skill.lower() 
                      for word in ['python', 'javascript', 'java', 'c++', 'c#', 'php', 'go', 'rust', 'kotlin', 'swift'])]
        
        frameworks = [skill for skill in skill_set if any(word in skill.lower() 
                     for word in ['react', 'vue', 'angular', 'django', 'flask', 'spring', 'laravel', 'express'])]
        
        databases = [skill for skill in skill_set if any(word in skill.lower() 
                    for word in ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch'])]
        
        if tech_skills:
            formatted_text += f"Языки программирования: {', '.join(tech_skills)}\n"
        if frameworks:
            formatted_text += f"Фреймворки: {', '.join(frameworks)}\n"
        if databases:
            formatted_text += f"Базы данных: {', '.join(databases)}\n"
        
        # Остальные навыки
        other_skills = [skill for skill in skill_set 
                       if skill not in tech_skills + frameworks + databases]
        if other_skills:
            formatted_text += f"Другие технологии: {', '.join(other_skills[:5])}\n"
    else:
        formatted_text += "Технические навыки не указаны\n"
    formatted_text += "\n"
    
    # Анализ образования и сертификации
    education = resume_data.get('education')
    if education:
        formatted_text += "### Образование и сертификация\n"
        
        # Основное образование
        primary = education.get('primary', [])
        if primary:
            for edu in primary:
                name = edu.get('name', 'Учебное заведение не указано')
                result = edu.get('result', '')
                year = edu.get('year', '')
                formatted_text += f"Высшее образование: {name}"
                if result:
                    formatted_text += f" - {result}"
                if year:
                    formatted_text += f" ({year})"
                formatted_text += "\n"
        
        # Дополнительное образование и сертификаты
        additional = education.get('additional', [])
        if additional:
            formatted_text += "Сертификаты и курсы:\n"
            for edu in additional[:3]:  # Первые 3
                name = edu.get('name', 'Курс не указан')
                organization = edu.get('organization', '')
                year = edu.get('year', '')
                formatted_text += f"  - {name}"
                if organization:
                    formatted_text += f" ({organization})"
                if year:
                    formatted_text += f" - {year}"
                formatted_text += "\n"
    formatted_text += "\n"
    
    # Анализ предпочтений в работе
    formatted_text += "### Предпочтения и требования кандидата\n"
    
    employments = resume_data.get('employments', [])
    if employments:
        formatted_text += f"Предпочитаемый тип занятости: {', '.join(employments)}\n"
    
    schedules = resume_data.get('schedules', [])
    if schedules:
        formatted_text += f"Предпочитаемый график: {', '.join(schedules)}\n"
    
    salary = resume_data.get('salary', {})
    if salary and salary.get('amount'):
        formatted_text += f"Зарплатные ожидания: {salary.get('amount')} руб.\n"
    
    return formatted_text


def format_detailed_vacancy_analysis(vacancy_data: dict) -> str:
    """
    Создает детальный анализ вакансии для понимания всех требований и контекста.
    
    Args:
        vacancy_data: Словарь с данными вакансии
        
    Returns:
        str: Детальный анализ требований вакансии
    """
    formatted_text = "## ДЕТАЛЬНЫЙ АНАЛИЗ ТРЕБОВАНИЙ ВАКАНСИИ\n\n"
    
    # Анализ описания на предмет скрытых требований
    description = vacancy_data.get('description', '')
    formatted_text += "### Полный анализ описания вакансии\n"
    formatted_text += f"Описание: {description}\n\n"
    
    # Попытка извлечь дополнительную информацию из описания
    description_lower = description.lower()
    
    # Анализ упоминаемых технологий в описании
    formatted_text += "### Анализ требований из описания\n"
    
    # Определение уровня сложности задач
    if any(word in description_lower for word in ['архитектур', 'проектирование', 'system design', 'lead']):
        formatted_text += "Обнаружены требования архитектурного уровня\n"
    
    if any(word in description_lower for word in ['алгоритм', 'оптимизация', 'performance', 'высокие нагрузки']):
        formatted_text += "Требуются навыки оптимизации и работы с алгоритмами\n"
    
    if any(word in description_lower for word in ['команд', 'лидерство', 'менторство', 'team lead']):
        formatted_text += "Требуются лидерские и командные навыки\n"
    
    if any(word in description_lower for word in ['английский', 'english', 'международн']):
        formatted_text += "Требуется знание английского языка\n"
    formatted_text += "\n"
    
    # Анализ ключевых навыков
    key_skills = vacancy_data.get('key_skills', [])
    formatted_text += "### Детальный анализ ключевых навыков\n"
    
    if key_skills:
        # Категоризация навыков
        programming_languages = []
        frameworks_tools = []
        methodologies = []
        soft_skills = []
        
        for skill in key_skills:
            skill_lower = skill.lower()
            if any(lang in skill_lower for lang in ['python', 'javascript', 'java', 'c++', 'c#', 'go', 'rust']):
                programming_languages.append(skill)
            elif any(tool in skill_lower for tool in ['react', 'vue', 'django', 'spring', 'docker', 'kubernetes']):
                frameworks_tools.append(skill)
            else:
                soft_skills.append(skill)
        
        if programming_languages:
            formatted_text += f"Языки программирования: {', '.join(programming_languages)}\n"
        if frameworks_tools:
            formatted_text += f"Фреймворки и инструменты: {', '.join(frameworks_tools)}\n"
        if methodologies:
            formatted_text += f"Методологии: {', '.join(methodologies)}\n"
        if soft_skills:
            formatted_text += f"Дополнительные навыки: {', '.join(soft_skills)}\n"
    else:
        formatted_text += "Ключевые навыки не указаны в вакансии\n"
    formatted_text += "\n"
    
    # Анализ требований к опыту и условий работы
    formatted_text += "### Требования к опыту и условия работы\n"
    
    experience = vacancy_data.get('experience', {})
    if experience and experience.get('id'):
        exp_id = experience.get('id')
        if exp_id == 'noExperience':
            formatted_text += "Позиция для начинающих специалистов - акцент на потенциал и обучаемость\n"
        elif exp_id in ['between1And3', 'between3And6']:
            formatted_text += "Позиция для специалистов с опытом - важны практические навыки\n"
        elif exp_id == 'moreThan6':
            formatted_text += "Senior позиция - требуются экспертные знания и лидерские качества\n"
    
    # Анализ формата работы
    schedule = vacancy_data.get('schedule', {})
    if schedule and schedule.get('id'):
        sch_id = schedule.get('id')
        if sch_id == 'remote':
            formatted_text += "Удаленная работа - важны навыки самоорганизации и коммуникации\n"
        elif sch_id == 'flexible':
            formatted_text += "Гибкий график - требуется ответственность и планирование\n"
    
    return formatted_text