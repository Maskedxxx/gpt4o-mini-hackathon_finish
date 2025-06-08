# src/llm_cover_letter/formatter.py
"""
Модуль для форматирования данных резюме и вакансии для генерации рекомендательного письма.
Фокус на персонализации и создании убедительного контента.
"""

def format_resume_for_cover_letter(resume_data: dict) -> str:
    """
    Форматирует данные резюме для создания персонализированного рекомендательного письма.
    
    Args:
        resume_data: Словарь с данными резюме
        
    Returns:
        str: Форматированный текст резюме для генерации письма
    """
    formatted_text = "## ПРОФИЛЬ КАНДИДАТА\n\n"
    
    # Персональная информация для обращения
    formatted_text += "### Личная информация\n"
    first_name = resume_data.get('first_name', '')
    last_name = resume_data.get('last_name', '')
    middle_name = resume_data.get('middle_name', '')
    
    if first_name or last_name:
        full_name = f"{last_name} {first_name} {middle_name}".strip()
        formatted_text += f"**ФИО:** {full_name}\n"
    else:
        formatted_text += "**ФИО:** Не указано\n"
    
    # Общий опыт работы (важно для позиционирования)
    total_experience = resume_data.get('total_experience')
    if total_experience:
        years = total_experience // 12
        months = total_experience % 12
        if years > 0:
            exp_text = f"{years} лет {months} мес." if months > 0 else f"{years} лет"
        else:
            exp_text = f"{months} мес."
        formatted_text += f"**Общий опыт работы:** {exp_text}\n"
    else:
        formatted_text += "**Общий опыт работы:** Не указан\n"
    
    formatted_text += "\n"
    
    # Специализация и желаемая позиция
    formatted_text += "### Профессиональная специализация\n"
    formatted_text += f"**Желаемая должность:** {resume_data.get('title', 'Не указана')}\n\n"
    
    # Профессиональные навыки и описание
    formatted_text += "### Профессиональные компетенции\n"
    skills = resume_data.get('skills', 'Не указаны')
    formatted_text += f"**Профессиональное описание:**\n{skills}\n\n"
    
    # Ключевые технические навыки
    formatted_text += "### Технические навыки и технологии\n"
    skill_set = resume_data.get('skill_set', [])
    if skill_set:
        for skill in skill_set:
            formatted_text += f"- {skill}\n"
    else:
        formatted_text += "Не указаны\n"
    formatted_text += "\n"
    
    # Профессиональный опыт (с акцентом на достижения и компании)
    formatted_text += "### Карьерная история и ключевые достижения\n"
    experience_list = resume_data.get('experience', [])
    if experience_list:
        for i, exp in enumerate(experience_list, 1):
            company = exp.get('company', 'Компания не указана')
            position = exp.get('position', 'Должность не указана')
            start = exp.get('start', '')
            end = exp.get('end', 'по настоящее время')
            description = exp.get('description', 'Описание отсутствует')
            
            # Форматируем период работы
            period = f"{start} - {end}" if start else end
            
            formatted_text += f"**{i}. {position}** | *{company}*\n"
            formatted_text += f"Период: {period}\n"
            formatted_text += f"Ключевые достижения и обязанности:\n{description}\n\n"
    else:
        formatted_text += "Карьерная история не указана\n\n"
    
    # Сертификаты и дополнительная квалификация
    certificates = resume_data.get('certificate', [])
    if certificates:
        formatted_text += "### Сертификаты и дополнительная квалификация\n"
        for cert in certificates:
            title = cert.get('title', 'Название сертификата не указано')
            url = cert.get('url')
            
            if url:
                formatted_text += f"- **{title}** (подтверждение: {url})\n"
            else:
                formatted_text += f"- **{title}**\n"
        formatted_text += "\n"
    
    # Знание языков (может быть критично для позиции)
    languages = resume_data.get('languages', [])
    if languages:
        formatted_text += "### Языковые компетенции\n"
        for lang in languages:
            name = lang.get('name', '')
            level = lang.get('level', {}).get('name', '')
            formatted_text += f"- **{name}:** {level}\n"
        formatted_text += "\n"
        
    # Контактная информация (для подписи в письме)
    contacts = resume_data.get('contact', [])
    if contacts:
        formatted_text += "### Контактная информация\n"
        for contact in contacts:
            contact_type = contact.get('type', {}).get('name', 'Контакт')
            contact_value = contact.get('value', '')
            
            # Обрабатываем значение контакта (может быть строкой или объектом)
            if isinstance(contact_value, dict):
                contact_value = contact_value.get('formatted', str(contact_value))
            elif not isinstance(contact_value, str):
                contact_value = str(contact_value)
            
            formatted_text += f"- **{contact_type}:** {contact_value}\n"
        formatted_text += "\n"
    
    return formatted_text


def format_vacancy_for_cover_letter(vacancy_data: dict) -> str:
    """
    Форматирует данные вакансии для создания персонализированного рекомендательного письма.
    Фокус на требованиях и ожиданиях работодателя.
    
    Args:
        vacancy_data: Словарь с данными вакансии
        
    Returns:
        str: Форматированный текст вакансии для генерации письма
    """
    formatted_text = "## ЦЕЛЕВАЯ ПОЗИЦИЯ И ТРЕБОВАНИЯ\n\n"
    
    # Название позиции (критично для персонализации)
    formatted_text += "### Информация о позиции\n"
    position_name = vacancy_data.get('name', 'Не указано')
    company_name = vacancy_data.get('company_name', 'Не указано')
    formatted_text += f"**Название позиции:** {position_name}\n\n"
    formatted_text += f"**Компания:** {company_name}\n\n"
    
    # Профессиональные роли (ожидания работодателя)
    professional_roles = vacancy_data.get('professional_roles', [])
    if professional_roles:
        formatted_text += "### Требуемые профессиональные роли\n"
        for role in professional_roles:
            role_name = role.get('name', '') if isinstance(role, dict) else str(role)
            formatted_text += f"- {role_name}\n"
        formatted_text += "\n"
    
    # Описание вакансии и задач
    formatted_text += "### Описание позиции и ключевые задачи\n"
    description = vacancy_data.get('description', 'Не указано')
    formatted_text += f"{description}\n\n"
    
    # Требуемые навыки (для демонстрации соответствия)
    formatted_text += "### Требуемые навыки и технологии\n"
    key_skills = vacancy_data.get('key_skills', [])
    if key_skills:
        for skill in key_skills:
            skill_name = skill if isinstance(skill, str) else skill.get('name', '')
            formatted_text += f"- {skill_name}\n"
    else:
        formatted_text += "Не указаны\n"
    formatted_text += "\n"
    
    # Требуемый опыт работы (влияет на позиционирование кандидата)
    experience = vacancy_data.get('experience', {})
    if experience and experience.get('id'):
        formatted_text += "### Требования к опыту работы\n"
        
        exp_mapping = {
            'noExperience': 'Без опыта работы',
            'between1And3': 'От 1 года до 3 лет опыта',
            'between3And6': 'От 3 до 6 лет опыта',
            'moreThan6': 'Более 6 лет опыта'
        }
        
        exp_id = experience.get('id')
        exp_text = exp_mapping.get(exp_id, f"Требование: {exp_id}")
        formatted_text += f"**Минимальный опыт:** {exp_text}\n\n"
    
    return formatted_text


def format_cover_letter_context(resume_data: dict, vacancy_data: dict) -> str:
    """
    Создает контекстную информацию для более персонализированного письма.
    
    Args:
        resume_data: Словарь с данными резюме
        vacancy_data: Словарь с данными вакансии
        
    Returns:
        str: Контекстная информация для генерации письма
    """
    context_text = "## КОНТЕКСТ ДЛЯ ПЕРСОНАЛИЗАЦИИ\n\n"
    
    # Анализ соответствия навыков
    resume_skills = set(skill.lower() for skill in resume_data.get('skill_set', []))
    vacancy_skills = set(skill.lower() for skill in vacancy_data.get('key_skills', []))
    matching_skills = resume_skills & vacancy_skills
    
    context_text += "### Анализ соответствия навыков\n"
    if matching_skills:
        context_text += f"**Совпадающие навыки ({len(matching_skills)}):**\n"
        for skill in sorted(matching_skills):
            context_text += f"- {skill.title()}\n"
    else:
        context_text += "Прямых совпадений навыков не найдено\n"
    
    missing_skills = vacancy_skills - resume_skills
    if missing_skills:
        context_text += f"\n**Навыки вакансии отсутствующие в резюме ({len(missing_skills)}):**\n"
        for skill in sorted(list(missing_skills)[:5]):  # Показываем первые 5
            context_text += f"- {skill.title()}\n"
        if len(missing_skills) > 5:
            context_text += f"... и еще {len(missing_skills) - 5}\n"
    
    context_text += "\n"
    
    # Анализ уровня позиции
    context_text += "### Позиционирование кандидата\n"
    
    total_exp = resume_data.get('total_experience', 0)
    required_exp = vacancy_data.get('experience', {}).get('id', '')
    
    if total_exp:
        years_exp = total_exp // 12
        if years_exp == 0:
            level = "Junior / Начинающий специалист"
        elif years_exp <= 2:
            level = "Junior+ / Младший специалист"
        elif years_exp <= 5:
            level = "Middle / Средний специалист"
        elif years_exp <= 10:
            level = "Senior / Старший специалист"
        else:
            level = "Lead / Ведущий специалист"
        
        context_text += f"**Уровень кандидата по опыту:** {level}\n"
    
    if required_exp:
        exp_mapping = {
            'noExperience': 'Junior позиция',
            'between1And3': 'Junior/Middle позиция',
            'between3And6': 'Middle позиция',
            'moreThan6': 'Senior+ позиция'
        }
        context_text += f"**Уровень вакансии:** {exp_mapping.get(required_exp, required_exp)}\n"
    
    context_text += "\n"
    
    return context_text