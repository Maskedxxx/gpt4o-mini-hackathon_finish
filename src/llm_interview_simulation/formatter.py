# src/llm_interview_simulation/formatter.py
"""
Модуль для интеллектуального форматирования данных резюме и вакансии для симуляции интервью.
"""
import re
from typing import Dict, List, Any, Optional, Tuple
from src.models.interview_simulation_models import (
    CandidateLevel, ITRole, CandidateProfile, InterviewConfiguration, 
    QuestionType, CompetencyArea
)

class SmartCandidateAnalyzer:
    """Анализатор профиля кандидата на основе резюме."""
    
    # Ключевые слова для определения IT-ролей
    ROLE_KEYWORDS = {
        ITRole.DEVELOPER: [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js', 'django', 
            'flask', 'spring', 'разработчик', 'программист', 'developer', 'backend', 'frontend',
            'fullstack', 'software engineer', 'web developer'
        ],
        ITRole.DATA_SCIENTIST: [
            'data scientist', 'машинное обучение', 'machine learning', 'ml', 'ai', 'нейронные сети',
            'pytorch', 'tensorflow', 'pandas', 'numpy', 'scikit-learn', 'llm', 'nlp', 'computer vision',
            'дата-сайентист', 'data science', 'искусственный интеллект', 'deep learning', 'langchain'
        ],
        ITRole.QA: [
            'тестировщик', 'qa', 'quality assurance', 'тестирование', 'автотесты', 'selenium',
            'cypress', 'junit', 'testing', 'test automation', 'manual testing'
        ],
        ITRole.DEVOPS: [
            'devops', 'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'terraform', 'ansible',
            'jenkins', 'gitlab', 'ci/cd', 'мониторинг', 'инфраструктура', 'администратор'
        ],
        ITRole.ANALYST: [
            'аналитик', 'analyst', 'бизнес-аналитик', 'системный аналитик', 'product analyst',
            'data analyst', 'bi', 'tableau', 'power bi', 'sql', 'аналитика'
        ],
        ITRole.PROJECT_MANAGER: [
            'менеджер проектов', 'project manager', 'scrum master', 'product manager',
            'руководитель проектов', 'agile', 'scrum', 'kanban', 'управление проектами'
        ],
        ITRole.DESIGNER: [
            'дизайнер', 'designer', 'ui/ux', 'web design', 'graphic design', 'figma',
            'sketch', 'adobe', 'веб-дизайн', 'интерфейс'
        ]
    }
    
    # Технологии по категориям
    TECH_CATEGORIES = {
        'languages': ['python', 'java', 'javascript', 'c++', 'c#', 'go', 'rust', 'php', 'ruby'],
        'frameworks': ['django', 'flask', 'fastapi', 'react', 'angular', 'vue', 'spring', 'laravel'],
        'databases': ['postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'sql'],
        'ml_ai': ['pytorch', 'tensorflow', 'scikit-learn', 'pandas', 'numpy', 'langchain', 'llm', 'nlp'],
        'devops': ['docker', 'kubernetes', 'aws', 'azure', 'terraform', 'jenkins', 'gitlab'],
        'tools': ['git', 'jira', 'confluence', 'postman', 'swagger']
    }
    
    def analyze_candidate_profile(self, resume_data: Dict[str, Any]) -> CandidateProfile:
        """Анализирует резюме и создает профиль кандидата."""
        
        # Определяем уровень кандидата
        level = self._determine_candidate_level(resume_data)
        
        # Определяем IT-роль
        role = self._determine_it_role(resume_data)
        
        # Извлекаем годы опыта
        years_exp = self._extract_years_of_experience(resume_data)
        
        # Извлекаем ключевые технологии
        technologies = self._extract_key_technologies(resume_data)
        
        # Анализируем образование
        education = self._analyze_education(resume_data)
        
        # Извлекаем предыдущие компании
        companies = self._extract_companies(resume_data)
        
        # Проверяем опыт управления
        has_management = self._check_management_experience(resume_data)
        
        return CandidateProfile(
            detected_level=level,
            detected_role=role,
            years_of_experience=years_exp,
            key_technologies=technologies,
            education_level=education,
            previous_companies=companies,
            management_experience=has_management
        )
    
    def _determine_candidate_level(self, resume_data: Dict[str, Any]) -> CandidateLevel:
        """Определяет уровень кандидата на основе опыта и навыков."""
        
        # Получаем опыт в месяцах
        total_exp_months = resume_data.get('total_experience', {}).get('months', 0)
        years_exp = total_exp_months / 12
        
        # Определяем по опыту
        base_level_by_experience = CandidateLevel.UNKNOWN
        if years_exp < 1:
            base_level_by_experience = CandidateLevel.JUNIOR
        elif years_exp < 3:
            base_level_by_experience = CandidateLevel.MIDDLE
        elif years_exp < 6:
            base_level_by_experience = CandidateLevel.SENIOR
        else:
            base_level_by_experience = CandidateLevel.LEAD
            
        result = base_level_by_experience
        print(f"DEBUG: base_level_by_experience = {result}")
        return result
    
    def _determine_it_role(self, resume_data: Dict[str, Any]) -> ITRole:
        """Определяет IT-роль кандидата."""
        
        # Собираем текст для анализа
        text_to_analyze = []
        text_to_analyze.append(resume_data.get('title', '').lower())
        text_to_analyze.append(resume_data.get('skills', '').lower())
        
        # Добавляем навыки
        skill_set = resume_data.get('skill_set', [])
        text_to_analyze.extend([skill.lower() for skill in skill_set])
        
        # Добавляем описания должностей
        for exp in resume_data.get('experience', []):
            text_to_analyze.append(exp.get('position', '').lower())
            text_to_analyze.append(exp.get('description', '').lower())
        
        # Добавляем профессиональные роли
        for role in resume_data.get('professional_roles', []):
            text_to_analyze.append(role.get('name', '').lower())
        
        full_text = ' '.join(text_to_analyze)
        
        # Подсчитываем совпадения для каждой роли
        role_scores = {}
        for role, keywords in self.ROLE_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in full_text)
            role_scores[role] = score
        
        # Возвращаем роль с наивысшим скором
        if role_scores:
            best_role = max(role_scores, key=role_scores.get)
            return best_role if role_scores[best_role] > 0 else ITRole.OTHER
        
        return ITRole.OTHER
    
    def _extract_years_of_experience(self, resume_data: Dict[str, Any]) -> Optional[int]:
        """Извлекает количество лет опыта."""
        total_exp_months = resume_data.get('total_experience', {}).get('months', 0)
        return round(total_exp_months / 12) if total_exp_months > 0 else None
    
    def _extract_key_technologies(self, resume_data: Dict[str, Any]) -> List[str]:
        """Извлекает ключевые технологии из резюме."""
        technologies = set()
        
        # Из skill_set
        skill_set = resume_data.get('skill_set', [])
        for skill in skill_set:
            skill_lower = skill.lower()
            # Проверяем во всех категориях технологий
            for category, techs in self.TECH_CATEGORIES.items():
                for tech in techs:
                    if tech in skill_lower:
                        technologies.add(skill)
        
        # Из описания навыков
        skills_text = resume_data.get('skills', '').lower()
        for category, techs in self.TECH_CATEGORIES.items():
            for tech in techs:
                if tech in skills_text:
                    technologies.add(tech.title())
        
        return list(technologies)[:15]  # Ограничиваем количество
    
    def _analyze_education(self, resume_data: Dict[str, Any]) -> Optional[str]:
        """Анализирует уровень образования."""
        education = resume_data.get('education', {})
        level = education.get('level', {})
        
        if level:
            level_name = level.get('name', '')
            return level_name
        
        return None
    
    def _extract_companies(self, resume_data: Dict[str, Any]) -> List[str]:
        """Извлекает список предыдущих компаний."""
        companies = []
        for exp in resume_data.get('experience', []):
            company = exp.get('company', '')
            if company and company not in companies:
                companies.append(company)
        
        return companies[:5]  # Ограничиваем количество
    
    def _check_management_experience(self, resume_data: Dict[str, Any]) -> bool:
        """Проверяет наличие опыта управления."""
        management_keywords = [
            'руководитель', 'менеджер', 'lead', 'head', 'manager', 'team lead',
            'управление командой', 'управление проектами', 'scrum master'
        ]
        
        # Проверяем в должности
        title = resume_data.get('title', '').lower()
        if any(keyword in title for keyword in management_keywords):
            return True
        
        # Проверяем в опыте работы
        for exp in resume_data.get('experience', []):
            position = exp.get('position', '').lower()
            description = exp.get('description', '').lower()
            
            if any(keyword in position for keyword in management_keywords):
                return True
            if any(keyword in description for keyword in management_keywords):
                return True
        
        return False


class InterviewConfigurationBuilder:
    """Строитель конфигурации интервью на основе профиля кандидата и вакансии."""
    
    def build_interview_config(self, candidate_profile: CandidateProfile, 
                             vacancy_data: Dict[str, Any]) -> InterviewConfiguration:
        """Создает конфигурацию интервью."""
        
        # Определяем количество раундов
        target_rounds = self._calculate_target_rounds(candidate_profile)
        
        # Определяем приоритетные области
        focus_areas = self._determine_focus_areas(candidate_profile, vacancy_data)
        
        # Определяем уровень сложности
        difficulty = self._determine_difficulty_level(candidate_profile, vacancy_data)
        
        return InterviewConfiguration(
            target_rounds=target_rounds,
            focus_areas=focus_areas,
            include_behavioral=True,
            include_technical=True,
            difficulty_level=difficulty
        )
    
    def _calculate_target_rounds(self, profile: CandidateProfile) -> int:
        """Вычисляет оптимальное количество раундов."""
        base_rounds = {
            CandidateLevel.JUNIOR: 4,
            CandidateLevel.MIDDLE: 5,
            CandidateLevel.SENIOR: 6,
            CandidateLevel.LEAD: 7
        }
        
        rounds = base_rounds.get(profile.detected_level, 5)
        
        # Добавляем раунд для управленцев
        if profile.management_experience and profile.detected_level in [CandidateLevel.SENIOR, CandidateLevel.LEAD]:
            rounds += 1
        
        return min(rounds, 7)  # Максимум 7 раундов
    
    def _determine_focus_areas(self, profile: CandidateProfile, 
                             vacancy_data: Dict[str, Any]) -> List[CompetencyArea]:
        """Определяет приоритетные области оценки."""
        focus_areas = [
            CompetencyArea.TECHNICAL_EXPERTISE,
            CompetencyArea.COMMUNICATION,
            CompetencyArea.MOTIVATION
        ]
        
        # Добавляем области в зависимости от уровня
        if profile.detected_level in [CandidateLevel.MIDDLE, CandidateLevel.SENIOR, CandidateLevel.LEAD]:
            focus_areas.extend([
                CompetencyArea.PROBLEM_SOLVING,
                CompetencyArea.TEAMWORK
            ])
        
        if profile.detected_level in [CandidateLevel.SENIOR, CandidateLevel.LEAD]:
            focus_areas.append(CompetencyArea.LEADERSHIP)
        
        if profile.management_experience:
            focus_areas.append(CompetencyArea.LEADERSHIP)
        
        # Добавляем специфичные области для ролей
        if profile.detected_role == ITRole.DATA_SCIENTIST:
            focus_areas.append(CompetencyArea.LEARNING_ABILITY)
        
        return list(set(focus_areas))  # Убираем дубликаты
    
    def _determine_difficulty_level(self, profile: CandidateProfile, 
                                  vacancy_data: Dict[str, Any]) -> str:
        """Определяет уровень сложности вопросов."""
        
        # Получаем требуемый опыт из вакансии
        vacancy_experience = vacancy_data.get('experience', {}).get('id', '')
        
        # Сопоставляем с уровнем кандидата
        if profile.detected_level == CandidateLevel.JUNIOR:
            return "easy"
        elif profile.detected_level == CandidateLevel.MIDDLE:
            return "medium"
        else:
            return "hard"


def format_resume_for_interview_simulation(resume_data: Dict[str, Any]) -> str:
    """
    Форматирует данные резюме для симуляции интервью с интеллектуальным анализом.
    """
    # Создаем анализатор и анализируем профиль
    analyzer = SmartCandidateAnalyzer()
    profile = analyzer.analyze_candidate_profile(resume_data)
    
    formatted_text = "## ИНФОРМАЦИЯ О КАНДИДАТЕ\n\n"
    
    # Базовая информация
    name = f"{resume_data.get('first_name', '')} {resume_data.get('last_name', '')}".strip()
    if name:
        formatted_text += f"### Кандидат\n{name}\n\n"
    
    # Определенный профиль
    formatted_text += "### Профиль кандидата (автоматический анализ)\n"
    formatted_text += f"**Уровень:** {profile.detected_level.value.title()}\n"
    formatted_text += f"**IT-роль:** {profile.detected_role.value.replace('_', ' ').title()}\n"
    if profile.years_of_experience:
        formatted_text += f"**Опыт работы:** {profile.years_of_experience} лет\n"
    if profile.management_experience:
        formatted_text += "**Управленческий опыт:** Да\n"
    formatted_text += "\n"
    
    # Желаемая должность
    formatted_text += "### Специализация кандидата\n"
    formatted_text += f"{resume_data.get('title', 'Не указана')}\n\n"
    
    # Профессиональное описание
    formatted_text += "### Профессиональное описание навыков\n"
    formatted_text += f"{resume_data.get('skills', 'Не указаны')}\n\n"
    
    # Ключевые технологии (умный анализ)
    if profile.key_technologies:
        formatted_text += "### Ключевые технологии кандидата\n"
        for tech in profile.key_technologies:
            formatted_text += f"- {tech}\n"
        formatted_text += "\n"
    
    # Технические навыки из skill_set
    formatted_text += "### Технические навыки кандидата\n"
    skill_set = resume_data.get('skill_set', [])
    if skill_set:
        for skill in skill_set:
            formatted_text += f"- {skill}\n"
    else:
        formatted_text += "Не указаны\n"
    formatted_text += "\n"
    
    # Детальный опыт работы
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
    
    # Образование
    education = resume_data.get('education', {})
    if education:
        formatted_text += "### Образование\n"
        level = education.get('level', {}).get('name', '')
        if level:
            formatted_text += f"**Уровень образования:** {level}\n"
        
        primary = education.get('primary', [])
        if primary:
            for edu in primary:
                name = edu.get('name', '')
                result = edu.get('result', '')
                year = edu.get('year', '')
                if name:
                    formatted_text += f"- {name}"
                    if result:
                        formatted_text += f", {result}"
                    if year:
                        formatted_text += f" ({year})"
                    formatted_text += "\n"
        formatted_text += "\n"
    
    # Зарплатные ожидания
    salary = resume_data.get('salary', {})
    if salary and salary.get('amount'):
        formatted_text += f"### Зарплатные ожидания\n{salary.get('amount')} {salary.get('currency', 'RUR')}\n\n"
    
    return formatted_text


def format_vacancy_for_interview_simulation(vacancy_data: Dict[str, Any]) -> str:
    """
    Форматирует данные вакансии для симуляции интервью.
    """
    formatted_text = "## ИНФОРМАЦИЯ О ВАКАНСИИ И ТРЕБОВАНИЯХ\n\n"
    
    # Название вакансии
    formatted_text += f"### Позиция\n{vacancy_data.get('name', 'Не указано')}\n\n"
    
    # Компания
    employer = vacancy_data.get('employer', {})
    if employer:
        formatted_text += f"### Компания\n{employer.get('name', 'Не указано')}\n\n"
    
    # Полное описание вакансии
    formatted_text += "### Описание вакансии и требования к кандидату\n"
    description = vacancy_data.get('description', 'Не указано')
    # Убираем HTML теги для чистоты
    import re
    clean_description = re.sub(r'<[^>]+>', '', description)
    formatted_text += f"{clean_description}\n\n"
    
    # Ключевые навыки для технических вопросов
    formatted_text += "### Ключевые требуемые навыки\n"
    key_skills = vacancy_data.get('key_skills', [])
    if key_skills:
        for skill in key_skills:
            skill_name = skill.get('name', '') if isinstance(skill, dict) else str(skill)
            formatted_text += f"- {skill_name}\n"
    else:
        formatted_text += "Не указаны\n"
    formatted_text += "\n"
    
    # Требуемый опыт работы
    experience = vacancy_data.get('experience', {})
    if experience and experience.get('name'):
        formatted_text += f"### Требуемый опыт работы\n{experience.get('name')}\n\n"
    
    # Условия работы
    employment = vacancy_data.get('employment', {})
    if employment and employment.get('name'):
        formatted_text += f"### Тип занятости\n{employment.get('name')}\n\n"
    
    schedule = vacancy_data.get('schedule', {})
    if schedule and schedule.get('name'):
        formatted_text += f"### График работы\n{schedule.get('name')}\n\n"
    
    # Зарплата
    salary = vacancy_data.get('salary')
    if salary:
        formatted_text += f"### Зарплата\n{salary}\n\n"
    
    return formatted_text


def format_dialog_history(dialog_messages: list) -> str:
    """
    Форматирует историю диалога для передачи в LLM.
    """
    if not dialog_messages:
        return "## ИСТОРИЯ ДИАЛОГА\n\nДиалог только начинается.\n\n"
    
    formatted_text = "## ИСТОРИЯ ПРЕДЫДУЩЕГО ДИАЛОГА\n\n"
    
    for msg in dialog_messages:
        speaker_name = "HR-менеджер" if msg.speaker == "HR" else "Кандидат"
        question_type_info = ""
        if msg.speaker == "HR" and msg.question_type:
            question_type_info = f" ({msg.question_type.value})"
        
        formatted_text += f"**{speaker_name} (раунд {msg.round_number}{question_type_info}):**\n{msg.message}\n\n"
    
    return formatted_text


def create_candidate_profile_and_config(resume_data: Dict[str, Any], 
                                       vacancy_data: Dict[str, Any]) -> Tuple[CandidateProfile, InterviewConfiguration]:
    """
    Создает профиль кандидата и конфигурацию интервью.
    """
    analyzer = SmartCandidateAnalyzer()
    profile = analyzer.analyze_candidate_profile(resume_data)
    
    config_builder = InterviewConfigurationBuilder()
    config = config_builder.build_interview_config(profile, vacancy_data)
    
    return profile, config