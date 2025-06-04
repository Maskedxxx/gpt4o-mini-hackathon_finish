# src/llm_interview_simulation/assessment_engine.py
"""
Продвинутая система оценки результатов интервью с использованием LLM и профессиональных HR-методик.
"""
import re
import os
from typing import Dict, List, Any, Optional, Tuple
from openai import OpenAI
from src.models.interview_simulation_models import (
    DialogMessage, InterviewAssessment, CompetencyScore, CompetencyArea, 
    CandidateProfile, CandidateLevel, ITRole, QuestionType
)
from src.llm_interview_simulation.config import settings
from src.utils import get_logger

logger = get_logger()

class ProfessionalAssessmentEngine:
    """Система профессиональной оценки результатов интервью."""
    
    def __init__(self):
        try:
            self.client = OpenAI(api_key=settings.api_key)
            self.model = settings.model_name
        except Exception:
            # Fallback если настройки не найдены
            import os
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OpenAI API key не найден. Установите переменную окружения OPENAI_API_KEY или настройте settings.py")
            self.client = OpenAI(api_key=api_key)
            self.model = os.getenv('OPENAI_MODEL')
    
    async def generate_comprehensive_assessment(self, 
                                              resume_data: Dict[str, Any],
                                              vacancy_data: Dict[str, Any],
                                              dialog_messages: List[DialogMessage],
                                              candidate_profile: CandidateProfile) -> InterviewAssessment:
        """Генерирует всестороннюю оценку интервью."""
        
        # 1. Анализируем каждую компетенцию детально
        competency_scores = await self._assess_competencies(
            dialog_messages, candidate_profile, vacancy_data
        )
        
        # 2. Определяем общую рекомендацию
        overall_recommendation = self._determine_overall_recommendation(competency_scores)
        
        # 3. Выявляем сильные и слабые стороны
        strengths, weaknesses = await self._analyze_strengths_weaknesses(
            dialog_messages, candidate_profile
        )
        
        # 4. Ищем красные флаги
        red_flags = self._detect_red_flags(dialog_messages, candidate_profile)
        
        # 5. Оцениваем культурное соответствие
        cultural_fit_score = await self._assess_cultural_fit(
            dialog_messages, vacancy_data
        )
        
        return InterviewAssessment(
            overall_recommendation=overall_recommendation,
            competency_scores=competency_scores,
            strengths=strengths,
            weaknesses=weaknesses,
            red_flags=red_flags,
            cultural_fit_score=cultural_fit_score
        )
    
    async def _assess_competencies(self, 
                                 dialog_messages: List[DialogMessage],
                                 candidate_profile: CandidateProfile,
                                 vacancy_data: Dict[str, Any]) -> List[CompetencyScore]:
        """Оценивает каждую компетенцию отдельно."""
        
        competencies_to_assess = self._get_relevant_competencies(candidate_profile)
        competency_scores = []
        
        for competency in competencies_to_assess:
            score_data = await self._assess_single_competency(
                competency, dialog_messages, candidate_profile, vacancy_data
            )
            competency_scores.append(score_data)
        
        return competency_scores
    
    def _get_relevant_competencies(self, candidate_profile: CandidateProfile) -> List[CompetencyArea]:
        """Определяет релевантные компетенции для оценки."""
        
        # Базовые компетенции для всех
        competencies = [
            CompetencyArea.TECHNICAL_EXPERTISE,
            CompetencyArea.COMMUNICATION,
            CompetencyArea.PROBLEM_SOLVING,
            CompetencyArea.MOTIVATION
        ]
        
        # Добавляем в зависимости от уровня
        if candidate_profile.detected_level in [CandidateLevel.MIDDLE, CandidateLevel.SENIOR, CandidateLevel.LEAD]:
            competencies.extend([
                CompetencyArea.TEAMWORK,
                CompetencyArea.ADAPTABILITY
            ])
        
        if candidate_profile.detected_level in [CandidateLevel.SENIOR, CandidateLevel.LEAD]:
            competencies.append(CompetencyArea.LEADERSHIP)
        
        # Специфичные для ролей
        if candidate_profile.detected_role in [ITRole.DATA_SCIENTIST, ITRole.DEVELOPER]:
            competencies.append(CompetencyArea.LEARNING_ABILITY)
        
        # Всегда оцениваем культурное соответствие
        competencies.append(CompetencyArea.CULTURAL_FIT)
        
        return list(set(competencies))  # Убираем дубликаты
    
    async def _assess_single_competency(self, 
                                      competency: CompetencyArea,
                                      dialog_messages: List[DialogMessage],
                                      candidate_profile: CandidateProfile,
                                      vacancy_data: Dict[str, Any]) -> CompetencyScore:
        """Оценивает одну конкретную компетенцию."""
        
        # Собираем релевантные ответы
        relevant_answers = self._extract_relevant_answers(dialog_messages, competency)
        
        # Создаем промпт для оценки
        assessment_prompt = self._create_competency_assessment_prompt(
            competency, relevant_answers, candidate_profile, vacancy_data
        )
        
        try:
            # Получаем оценку от LLM
            response = await self._get_llm_assessment(assessment_prompt)
            
            # Парсим ответ LLM
            score, evidence, improvement_notes = self._parse_competency_response(response)
            
            return CompetencyScore(
                area=competency,
                score=score,
                evidence=evidence,
                improvement_notes=improvement_notes
            )
            
        except Exception as e:
            logger.error(f"Ошибка при оценке компетенции {competency}: {e}")
            # Fallback оценка
            return self._create_fallback_competency_score(competency, relevant_answers)
    
    def _extract_relevant_answers(self, 
                                dialog_messages: List[DialogMessage], 
                                competency: CompetencyArea) -> List[DialogMessage]:
        """Извлекает ответы, релевантные для конкретной компетенции."""
        
        # Карта типов вопросов к компетенциям
        question_competency_map = {
            CompetencyArea.TECHNICAL_EXPERTISE: [QuestionType.TECHNICAL_SKILLS, QuestionType.EXPERIENCE_DEEP_DIVE],
            CompetencyArea.COMMUNICATION: [QuestionType.INTRODUCTION, QuestionType.FINAL],
            CompetencyArea.PROBLEM_SOLVING: [QuestionType.PROBLEM_SOLVING, QuestionType.BEHAVIORAL_STAR],
            CompetencyArea.TEAMWORK: [QuestionType.BEHAVIORAL_STAR],
            CompetencyArea.LEADERSHIP: [QuestionType.LEADERSHIP, QuestionType.BEHAVIORAL_STAR],
            CompetencyArea.ADAPTABILITY: [QuestionType.BEHAVIORAL_STAR, QuestionType.PROBLEM_SOLVING],
            CompetencyArea.LEARNING_ABILITY: [QuestionType.TECHNICAL_SKILLS, QuestionType.MOTIVATION],
            CompetencyArea.MOTIVATION: [QuestionType.MOTIVATION, QuestionType.INTRODUCTION],
            CompetencyArea.CULTURAL_FIT: [QuestionType.CULTURE_FIT, QuestionType.MOTIVATION]
        }
        
        relevant_question_types = question_competency_map.get(competency, [])
        
        relevant_answers = []
        for i, msg in enumerate(dialog_messages):
            if msg.speaker == "Candidate":
                # Находим соответствующий вопрос HR
                hr_question = dialog_messages[i-1] if i > 0 and dialog_messages[i-1].speaker == "HR" else None
                
                if hr_question and hr_question.question_type in relevant_question_types:
                    relevant_answers.append(msg)
                elif not relevant_question_types:  # Если нет специфичных типов, берем все
                    relevant_answers.append(msg)
        
        return relevant_answers
    
    def _create_competency_assessment_prompt(self, 
                                           competency: CompetencyArea,
                                           relevant_answers: List[DialogMessage],
                                           candidate_profile: CandidateProfile,
                                           vacancy_data: Dict[str, Any]) -> str:
        """Создает промпт для оценки конкретной компетенции."""
        
        competency_descriptions = {
            CompetencyArea.TECHNICAL_EXPERTISE: {
                "description": "Глубина технических знаний, понимание технологий, способность применять знания на практике",
                "criteria": "Оцени: конкретность примеров, понимание технологий, способность объяснить сложные концепции, соответствие требованиям вакансии"
            },
            CompetencyArea.COMMUNICATION: {
                "description": "Способность ясно излагать мысли, слушать, структурировать информацию",
                "criteria": "Оцени: ясность изложения, структурированность ответов, способность донести сложную информацию простым языком"
            },
            CompetencyArea.PROBLEM_SOLVING: {
                "description": "Аналитическое мышление, подход к решению проблем, логика",
                "criteria": "Оцени: структурированность подхода, логичность рассуждений, способность разбить проблему на части"
            },
            CompetencyArea.TEAMWORK: {
                "description": "Способность работать в команде, сотрудничать, разрешать конфликты",
                "criteria": "Оцени: примеры командной работы, подход к конфликтам, способность к компромиссам"
            },
            CompetencyArea.LEADERSHIP: {
                "description": "Лидерские качества, способность вести за собой, принимать решения",
                "criteria": "Оцени: опыт руководства, стиль лидерства, способность мотивировать и развивать других"
            },
            CompetencyArea.ADAPTABILITY: {
                "description": "Гибкость, способность адаптироваться к изменениям, обучаемость",
                "criteria": "Оцени: примеры адаптации к изменениям, открытость к новому, скорость обучения"
            },
            CompetencyArea.LEARNING_ABILITY: {
                "description": "Способность и желание учиться, развиваться профессионально",
                "criteria": "Оцени: примеры самообучения, интерес к новым технологиям, инвестиции в развитие"
            },
            CompetencyArea.MOTIVATION: {
                "description": "Мотивация к работе, интерес к компании и роли, карьерные амбиции",
                "criteria": "Оцени: искренность интереса, знание компании, соответствие целей кандидата и роли"
            },
            CompetencyArea.CULTURAL_FIT: {
                "description": "Соответствие ценностям и культуре компании",
                "criteria": "Оцени: совпадение ценностей, стиль работы, способность влиться в команду"
            }
        }
        
        comp_info = competency_descriptions.get(competency, {
            "description": "Профессиональная компетенция",
            "criteria": "Оцени общий уровень проявления данной компетенции"
        })
        
        # Формируем текст ответов
        answers_text = ""
        for i, answer in enumerate(relevant_answers, 1):
            answers_text += f"**Ответ {i} (раунд {answer.round_number}):**\n{answer.message}\n\n"
        
        if not answers_text:
            answers_text = "Релевантные ответы для данной компетенции не найдены."
        
        vacancy_name = vacancy_data.get('name', 'IT позиция')
        company_name = vacancy_data.get('employer', {}).get('name', 'Компания')
        
        prompt = f"""
# Задача: Оценка компетенции "{competency.value}"

## Описание компетенции:
{comp_info['description']}

## Критерии оценки:
{comp_info['criteria']}

## Контекст кандидата:
- Уровень: {candidate_profile.detected_level.value}
- Роль: {candidate_profile.detected_role.value}
- Опыт: {candidate_profile.years_of_experience or 'не указан'} лет
- Целевая позиция: {vacancy_name} в {company_name}

## Ответы кандидата для анализа:
{answers_text}

## Инструкции по оценке:

1. **Оценка (1-5 баллов):**
   - 5: Превосходный уровень, значительно превышает ожидания
   - 4: Хороший уровень, соответствует или немного превышает ожидания  
   - 3: Достаточный уровень, базовые требования выполнены
   - 2: Ниже ожиданий, есть существенные пробелы
   - 1: Неудовлетворительный уровень, серьезные проблемы

2. **Доказательства:** Конкретные цитаты или примеры из ответов
3. **Рекомендации:** Как улучшить данную компетенцию

Учитывай уровень кандидата - ожидания для Junior и Senior должны отличаться.

## Формат ответа:
SCORE: [число от 1 до 5]
EVIDENCE: [конкретные примеры и цитаты из ответов]
IMPROVEMENT: [конкретные рекомендации по улучшению]
"""
        
        return prompt
    
    async def _get_llm_assessment(self, prompt: str) -> str:
        """Получает оценку от LLM."""
        
        messages = [
            {
                "role": "system",
                "content": "Ты — эксперт HR с 15+ лет опыта оценки IT-кандидатов. Твоя задача — объективно оценить компетенции на основе ответов в интервью."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ]
        
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,  # Низкая температура для консистентности
            max_tokens=2000
        )
        
        return completion.choices[0].message.content.strip()
    
    def _parse_competency_response(self, response: str) -> Tuple[int, List[str], str]:
        """Парсит ответ LLM для извлечения оценки."""
        
        try:
            # Извлекаем оценку
            score_match = re.search(r'SCORE:\s*(\d+)', response, re.IGNORECASE)
            score = int(score_match.group(1)) if score_match else 3
            score = max(1, min(5, score))  # Ограничиваем 1-5
            
            # Извлекаем доказательства
            evidence_match = re.search(r'EVIDENCE:\s*(.+?)(?=IMPROVEMENT:|$)', response, re.IGNORECASE | re.DOTALL)
            evidence_text = evidence_match.group(1).strip() if evidence_match else "Доказательства не найдены"
            evidence = [evidence_text] if evidence_text else []
            
            # Извлекаем рекомендации
            improvement_match = re.search(r'IMPROVEMENT:\s*(.+?)$', response, re.IGNORECASE | re.DOTALL)
            improvement = improvement_match.group(1).strip() if improvement_match else "Рекомендации по улучшению не предоставлены"
            
            return score, evidence, improvement
            
        except Exception as e:
            logger.error(f"Ошибка парсинга ответа LLM: {e}")
            return 3, ["Ошибка анализа"], "Требуется дополнительная оценка"
    
    def _create_fallback_competency_score(self, 
                                        competency: CompetencyArea, 
                                        relevant_answers: List[DialogMessage]) -> CompetencyScore:
        """Создает fallback оценку при ошибке LLM."""
        
        # Простая оценка на основе качества ответов
        if relevant_answers:
            avg_quality = sum(msg.response_quality or 3 for msg in relevant_answers) / len(relevant_answers)
            score = max(1, min(5, round(avg_quality)))
        else:
            score = 3  # Нейтральная оценка
        
        return CompetencyScore(
            area=competency,
            score=score,
            evidence=[f"Ответ в раунде {msg.round_number}" for msg in relevant_answers[:2]],
            improvement_notes=f"Требуется дополнительная оценка компетенции {competency.value}"
        )
    
    def _determine_overall_recommendation(self, competency_scores: List[CompetencyScore]) -> str:
        """Определяет общую рекомендацию на основе оценок компетенций."""
        
        if not competency_scores:
            return "conditional_hire"
        
        # Вычисляем средний балл
        avg_score = sum(cs.score for cs in competency_scores) / len(competency_scores)
        
        # Проверяем критичные компетенции
        technical_score = next((cs.score for cs in competency_scores 
                              if cs.area == CompetencyArea.TECHNICAL_EXPERTISE), 3)
        communication_score = next((cs.score for cs in competency_scores 
                                  if cs.area == CompetencyArea.COMMUNICATION), 3)
        
        # Логика принятия решения
        if avg_score >= 4.0 and technical_score >= 4 and communication_score >= 3:
            return "hire"
        elif avg_score >= 3.0 and technical_score >= 3 and communication_score >= 3:
            return "conditional_hire"
        else:
            return "reject"
    
    async def _analyze_strengths_weaknesses(self, 
                                          dialog_messages: List[DialogMessage],
                                          candidate_profile: CandidateProfile) -> Tuple[List[str], List[str]]:
        """Анализирует сильные и слабые стороны кандидата."""
        
        candidate_answers = [msg.message for msg in dialog_messages if msg.speaker == "Candidate"]
        
        if not candidate_answers:
            return ["Недостаточно данных"], ["Требуется дополнительная оценка"]
        
        # Создаем промпт для анализа
        analysis_prompt = f"""
Проанализируй ответы кандидата уровня {candidate_profile.detected_level.value} {candidate_profile.detected_role.value} и определи:

## Ответы кандидата:
{chr(10).join([f"{i+1}. {answer}" for i, answer in enumerate(candidate_answers)])}

Определи:
1. **Сильные стороны** (3-4 конкретных пункта)
2. **Слабые стороны** (2-3 конкретных пункта)

Фокусируйся на:
- Технические навыки и их применение
- Коммуникативные способности  
- Опыт и достижения
- Подход к решению проблем
- Мотивация и цели

Формат ответа:
STRENGTHS: [список сильных сторон через точку с запятой]
WEAKNESSES: [список слабых сторон через точку с запятой]
"""
        
        try:
            response = await self._get_llm_assessment(analysis_prompt)
            
            # Парсим ответ
            strengths_match = re.search(r'STRENGTHS:\s*(.+?)(?=WEAKNESSES:|$)', response, re.IGNORECASE | re.DOTALL)
            weaknesses_match = re.search(r'WEAKNESSES:\s*(.+?)$', response, re.IGNORECASE | re.DOTALL)
            
            strengths = []
            if strengths_match:
                strengths = [s.strip() for s in strengths_match.group(1).split(';') if s.strip()]
            
            weaknesses = []  
            if weaknesses_match:
                weaknesses = [w.strip() for w in weaknesses_match.group(1).split(';') if w.strip()]
            
            return strengths or ["Хорошие базовые навыки"], weaknesses or ["Требует развития"]
            
        except Exception as e:
            logger.error(f"Ошибка анализа сильных/слабых сторон: {e}")
            return ["Хорошие базовые навыки"], ["Требует дополнительной оценки"]
    
    def _detect_red_flags(self, 
                         dialog_messages: List[DialogMessage], 
                         candidate_profile: CandidateProfile) -> List[str]:
        """Выявляет красные флаги в ответах кандидата."""
        
        red_flags = []
        candidate_answers = [msg.message for msg in dialog_messages if msg.speaker == "Candidate"]
        
        # Паттерны красных флагов
        red_flag_patterns = {
            "Негатив о прошлых работодателях": [
                r"ужасн\w+", r"кошмар\w+", r"идиот\w+", r"плох\w+\s+(начальник|руководитель|команда)",
                r"не\s+умел\w*", r"не\s+понимал\w*"
            ],
            "Отсутствие конкретики": [
                r"^(да|нет|не знаю|может быть)\.?\s*$",
                r"что-то\s+такое", r"как-то\s+так", r"ну\s+в\s+общем"
            ],
            "Завышенные ожидания": [
                r"минимум\s+\d+\s*тысяч", r"не\s+меньше\s+\d+", r"только\s+senior",
                r"не\s+готов\s+на\s+меньше"
            ],
            "Неготовность к развитию": [
                r"не\s+хочу\s+учить", r"зачем\s+это\s+нужно", r"это\s+не\s+мое",
                r"не\s+интересно"
            ]
        }
        
        full_text = " ".join(candidate_answers).lower()
        
        for flag_type, patterns in red_flag_patterns.items():
            for pattern in patterns:
                if re.search(pattern, full_text):
                    red_flags.append(flag_type)
                    break  # Один флаг этого типа достаточно
        
        # Проверяем слишком короткие ответы
        short_answers = [msg for msg in dialog_messages 
                        if msg.speaker == "Candidate" and len(msg.message) < 50]
        if len(short_answers) >= 3:
            red_flags.append("Слишком краткие ответы на большинство вопросов")
        
        return red_flags
    
    async def _assess_cultural_fit(self, 
                                 dialog_messages: List[DialogMessage],
                                 vacancy_data: Dict[str, Any]) -> int:
        """Оценивает культурное соответствие кандидата."""
        
        # Извлекаем ответы на вопросы о мотивации и культуре
        relevant_messages = [
            msg for msg in dialog_messages 
            if msg.speaker == "Candidate" and 
            msg.round_number >= 3  # Поздние раунды более показательны
        ]
        
        if not relevant_messages:
            return 3  # Нейтральная оценка
        
        try:
            company_name = vacancy_data.get('employer', {}).get('name', 'компании')
            
            cultural_prompt = f"""
Оцени культурное соответствие кандидата для работы в {company_name} на основе его ответов:

## Ответы кандидата:
{chr(10).join([f"Раунд {msg.round_number}: {msg.message}" for msg in relevant_messages])}

Оцени по шкале 1-5:
- 5: Отличное соответствие, разделяет ценности и подход
- 4: Хорошее соответствие, легко впишется в команду
- 3: Нейтрально, адаптируется со временем
- 2: Слабое соответствие, могут быть трения
- 1: Плохое соответствие, высокий риск конфликтов

Учитывай:
- Мотивацию и интерес к компании
- Стиль коммуникации
- Подход к работе и сотрудничеству
- Ценности и принципы

Ответь только числом от 1 до 5.
"""
            
            response = await self._get_llm_assessment(cultural_prompt)
            score = int(re.search(r'\d+', response).group()) if re.search(r'\d+', response) else 3
            return max(1, min(5, score))
            
        except Exception as e:
            logger.error(f"Ошибка оценки культурного соответствия: {e}")
            return 3

    async def generate_detailed_feedback(self, 
                                       assessment: InterviewAssessment,
                                       candidate_profile: CandidateProfile) -> Dict[str, str]:
        """Генерирует детальную обратную связь для кандидата."""
        
        try:
            feedback_prompt = f"""
Создай детальную обратную связь для кандидата уровня {candidate_profile.detected_level.value} {candidate_profile.detected_role.value} на основе результатов интервью:

## Результаты оценки:
- Общая рекомендация: {assessment.overall_recommendation}
- Оценки по компетенциям: {[f"{cs.area.value}: {cs.score}/5" for cs in assessment.competency_scores]}
- Сильные стороны: {', '.join(assessment.strengths)}
- Слабые стороны: {', '.join(assessment.weaknesses)}
- Культурное соответствие: {assessment.cultural_fit_score}/5

Создай:
1. **HR Assessment** - краткая профессиональная оценка (2-3 предложения)
2. **Performance Analysis** - детальный анализ выступления (4-5 предложений)  
3. **Improvement Recommendations** - конкретные рекомендации по улучшению (4-5 пунктов)

Формат ответа:
HR_ASSESSMENT: [краткая оценка]
PERFORMANCE_ANALYSIS: [детальный анализ]
IMPROVEMENT_RECOMMENDATIONS: [конкретные рекомендации]
"""
            
            response = await self._get_llm_assessment(feedback_prompt)
            
            # Парсим ответ
            hr_assessment = self._extract_section(response, "HR_ASSESSMENT")
            performance_analysis = self._extract_section(response, "PERFORMANCE_ANALYSIS")  
            improvement_recommendations = self._extract_section(response, "IMPROVEMENT_RECOMMENDATIONS")
            
            return {
                'hr_assessment': hr_assessment,
                'performance_analysis': performance_analysis,
                'improvement_recommendations': improvement_recommendations
            }
            
        except Exception as e:
            logger.error(f"Ошибка генерации обратной связи: {e}")
            return self._create_fallback_feedback(assessment)
    
    def _extract_section(self, text: str, section_name: str) -> str:
        """Извлекает секцию из текста."""
        pattern = f"{section_name}:\\s*(.+?)(?=[A-Z_]+:|$)"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else f"Информация о {section_name} недоступна"
    
    def _create_fallback_feedback(self, assessment: InterviewAssessment) -> Dict[str, str]:
        """Создает fallback обратную связь."""
        
        avg_score = sum(cs.score for cs in assessment.competency_scores) / len(assessment.competency_scores)
        
        hr_assessment = f"Кандидат показал {self._score_to_text(avg_score)} результат. "
        hr_assessment += f"Рекомендация: {assessment.overall_recommendation}."
        
        performance_analysis = f"Сильные стороны: {', '.join(assessment.strengths[:2])}. "
        if assessment.weaknesses:
            performance_analysis += f"Области для развития: {', '.join(assessment.weaknesses[:2])}."
        
        improvement_recommendations = "; ".join([
            cs.improvement_notes for cs in assessment.competency_scores[:3]
        ])
        
        return {
            'hr_assessment': hr_assessment,
            'performance_analysis': performance_analysis, 
            'improvement_recommendations': improvement_recommendations
        }
    
    def _score_to_text(self, score: float) -> str:
        """Конвертирует численную оценку в текстовое описание."""
        if score >= 4.5:
            return "отличный"
        elif score >= 3.5:
            return "хороший"
        elif score >= 2.5:
            return "удовлетворительный"
        else:
            return "требующий улучшения"