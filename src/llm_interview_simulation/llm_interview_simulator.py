# src/llm_interview_simulation/llm_interview_simulator.py
import logging
from typing import Optional, Dict, Any, List
from openai import OpenAI
from pydantic import ValidationError

from src.llm_interview_simulation.config import settings
from src.models.interview_simulation_models import InterviewSimulation, DialogMessage
from src.llm_interview_simulation.formatter import (
    format_resume_for_interview_simulation, 
    format_vacancy_for_interview_simulation,
    format_dialog_history
)

from src.utils import get_logger
logger = get_logger()

class LLMInterviewSimulator:
    """Сервис для создания симуляции интервью между HR и кандидатом с помощью OpenAI API"""
    
    def __init__(self):
        """Инициализация клиента OpenAI."""
        self.config = settings
        self.client = OpenAI(api_key=self.config.api_key)
        self.model = self.config.model_name
        self.dialog_rounds = 5  # Количество раундов диалога
    
    def _create_hr_prompt(self, resume_data: Dict[str, Any], vacancy_data: Dict[str, Any], 
                         dialog_history: List[DialogMessage], round_number: int) -> str:
        """
        Создает промпт для HR-менеджера.
        
        Args:
            resume_data: Данные резюме кандидата
            vacancy_data: Данные вакансии
            dialog_history: История предыдущего диалога
            round_number: Номер текущего раунда
        
        Returns:
            str: Промпт для HR
        """
        formatted_resume = format_resume_for_interview_simulation(resume_data)
        formatted_vacancy = format_vacancy_for_interview_simulation(vacancy_data)
        formatted_history = format_dialog_history(dialog_history)
        
        return f"""
        # Роль: Строгий и требовательный HR-менеджер
        
        Ты — опытный HR-менеджер IT-компании с 10+ лет опыта. Ты известен своей строгостью, 
        внимательностью к деталям и умением выявлять слабые места кандидатов. Твоя цель — 
        тщательно проверить компетенции кандидата и его соответствие вакансии.
        
        ## Твои характеристики как HR:
        - Задаешь конкретные технические вопросы
        - Проверяешь глубину знаний, а не поверхностное понимание
        - Обращаешь внимание на несоответствия в резюме
        - Требуешь примеры из реального опыта
        - Не принимаешь общие ответы, нуждаешься в деталях
        - Профессионален, но строг в оценках
        
        ## Контекст интервью:
        
        {formatted_resume}
        
        {formatted_vacancy}
        
        {formatted_history}
        
        ## Текущая ситуация:
        - Раунд интервью: {round_number} из {self.dialog_rounds}
        - Твоя задача: задать ОДИН конкретный вопрос кандидату
        
        ## Инструкции для текущего раунда:
        
        {"Начни интервью. Поприветствуй кандидата и задай первый вопрос." if round_number == 1 else "Проанализируй ответ кандидата из предыдущего раунда и задай следующий вопрос, основываясь на его ответе или переходи к новой теме."}
        
        ## Типы вопросов по раундам:
        - Раунд 1: Общее знакомство и первый технический вопрос
        - Раунд 2: Глубокий технический вопрос по ключевым навыкам вакансии
        - Раунд 3: Вопрос о конкретном опыте из резюме с требованием примеров
        - Раунд 4: Ситуационный вопрос или сложная техническая задача
        - Раунд 5: Вопросы о мотивации, планах развития или финальная проверка знаний
        
        ## Требования к ответу:
        - Один конкретный вопрос (не более 2-3 предложений)
        - Вопрос должен соответствовать требованиям вакансии
        - Используй информацию из резюме кандидата
        - Будь строгим, но профессиональным
        - На русском языке
        
        Ответь только текстом вопроса, без дополнительных пояснений.
        """
    
    def _create_candidate_prompt(self, resume_data: Dict[str, Any], vacancy_data: Dict[str, Any], 
                               dialog_history: List[DialogMessage], hr_question: str) -> str:
        """
        Создает промпт для кандидата.
        
        Args:
            resume_data: Данные резюме кандидата
            vacancy_data: Данные вакансии
            dialog_history: История предыдущего диалога
            hr_question: Последний вопрос от HR
        
        Returns:
            str: Промпт для кандидата
        """
        formatted_resume = format_resume_for_interview_simulation(resume_data)
        formatted_vacancy = format_vacancy_for_interview_simulation(vacancy_data)
        formatted_history = format_dialog_history(dialog_history[:-1])  # Исключаем последний вопрос HR
        
        return f"""
        # Роль: Мотивированный кандидат на IT-позицию
        
        Ты — IT-специалист, который очень хочет получить работу на данную позицию. 
        Ты хорошо подготовился к интервью, знаешь свои сильные стороны и честно 
        признаешь области для развития. Ты профессионален, уверен в себе, но не высокомерен.
        
        ## Твои характеристики как кандидата:
        - Отвечаешь конкретно и по существу
        - Приводишь примеры из реального опыта
        - Честно признаешь, если чего-то не знаешь
        - Показываешь энтузиазм к изучению нового
        - Демонстрируешь понимание требований позиции
        - Говоришь уверенно, но не преувеличиваешь свои способности
        
        ## Твоя информация (резюме):
        
        {formatted_resume}
        
        ## Информация о целевой позиции:
        
        {formatted_vacancy}
        
        ## История интервью:
        
        {formatted_history}
        
        ## Текущий вопрос от HR-менеджера:
        
        "{hr_question}"
        
        ## Инструкции для ответа:
        
        1. Внимательно проанализируй вопрос HR
        2. Основывай ответ на информации из своего резюме
        3. Если вопрос технический — демонстрируй знания, но будь честным о пределах
        4. Если вопрос о опыте — приводи конкретные примеры из резюме
        5. Если не знаешь ответа — честно признайся, но покажи готовность изучать
        6. Связывай свой ответ с требованиями вакансии
        7. Будь лаконичным, но информативным (3-5 предложений)
        
        ## Требования к ответу:
        - Отвечай только на заданный вопрос
        - Используй профессиональную лексику
        - Будь конкретным, избегай общих фраз
        - На русском языке
        - Не задавай встречных вопросов в этом ответе
        
        Ответь только текстом ответа, без дополнительных пояснений.
        """
    
    async def _get_hr_question(self, resume_data: Dict[str, Any], vacancy_data: Dict[str, Any], 
                             dialog_history: List[DialogMessage], round_number: int) -> Optional[str]:
        """Получает вопрос от HR-менеджера."""
        try:
            prompt = self._create_hr_prompt(resume_data, vacancy_data, dialog_history, round_number)
            
            messages = [
                {
                    "role": "system",
                    "content": "Ты — опытный HR-менеджер, проводящий техническое интервью. Задавай конкретные, релевантные вопросы."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1500
            )
            
            return completion.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Ошибка при получении вопроса HR: {e}")
            return None
    
    async def _get_candidate_answer(self, resume_data: Dict[str, Any], vacancy_data: Dict[str, Any], 
                                  dialog_history: List[DialogMessage], hr_question: str) -> Optional[str]:
        """Получает ответ от кандидата."""
        try:
            prompt = self._create_candidate_prompt(resume_data, vacancy_data, dialog_history, hr_question)
            
            messages = [
                {
                    "role": "system", 
                    "content": "Ты — мотивированный IT-кандидат на собеседовании. Отвечай профессионально и по существу."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.8,
                max_tokens=4000
            )
            
            return completion.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Ошибка при получении ответа кандидата: {e}")
            return None
    
    async def _generate_final_assessment(self, resume_data: Dict[str, Any], vacancy_data: Dict[str, Any], 
                                       dialog_messages: List[DialogMessage]) -> Dict[str, str]:
        """Генерирует финальную оценку интервью."""
        try:
            formatted_resume = format_resume_for_interview_simulation(resume_data)
            formatted_vacancy = format_vacancy_for_interview_simulation(vacancy_data)
            formatted_history = format_dialog_history(dialog_messages)
            
            assessment_prompt = f"""
            # Задача: Анализ результатов интервью
            
            Проанализируй прошедшее интервью и предоставь оценку.
            
            ## Информация о кандидате:
            {formatted_resume}
            
            ## Информация о вакансии:
            {formatted_vacancy}
            
            ## Полный диалог интервью:
            {formatted_history}
            
            ## Требуется предоставить:
            
            1. **HR Assessment** (оценка HR): Краткая оценка кандидата с точки зрения HR (2-3 предложения)
            2. **Performance Analysis** (анализ выступления): Детальный анализ сильных и слабых сторон ответов кандидата (3-4 предложения)
            3. **Improvement Recommendations** (рекомендации): Конкретные советы кандидату для улучшения (3-4 предложения)
            
            Отвечай на русском языке, будь объективным и конструктивным.
            
            Формат ответа:
            HR_ASSESSMENT: [текст оценки]
            PERFORMANCE_ANALYSIS: [текст анализа]
            IMPROVEMENT_RECOMMENDATIONS: [текст рекомендаций]
            """
            
            messages = [
                {
                    "role": "system",
                    "content": "Ты — эксперт по HR-анализу, оцениваешь результаты технических интервью."
                },
                {
                    "role": "user",
                    "content": assessment_prompt
                }
            ]
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=8000
            )
            
            response = completion.choices[0].message.content.strip()
            
            # Парсим ответ
            assessment = {}
            lines = response.split('\n')
            current_key = None
            current_text = []
            
            for line in lines:
                if line.startswith('HR_ASSESSMENT:'):
                    if current_key:
                        assessment[current_key] = ' '.join(current_text).strip()
                    current_key = 'hr_assessment'
                    current_text = [line.replace('HR_ASSESSMENT:', '').strip()]
                elif line.startswith('PERFORMANCE_ANALYSIS:'):
                    if current_key:
                        assessment[current_key] = ' '.join(current_text).strip()
                    current_key = 'performance_analysis'
                    current_text = [line.replace('PERFORMANCE_ANALYSIS:', '').strip()]
                elif line.startswith('IMPROVEMENT_RECOMMENDATIONS:'):
                    if current_key:
                        assessment[current_key] = ' '.join(current_text).strip()
                    current_key = 'improvement_recommendations'
                    current_text = [line.replace('IMPROVEMENT_RECOMMENDATIONS:', '').strip()]
                elif current_key and line.strip():
                    current_text.append(line.strip())
            
            if current_key:
                assessment[current_key] = ' '.join(current_text).strip()
            
            return assessment
            
        except Exception as e:
            logger.error(f"Ошибка при генерации финальной оценки: {e}")
            return {
                'hr_assessment': 'Ошибка при генерации оценки',
                'performance_analysis': 'Ошибка при анализе выступления',
                'improvement_recommendations': 'Ошибка при создании рекомендаций'
            }
    
    async def simulate_interview(self, parsed_resume: Dict[str, Any], parsed_vacancy: Dict[str, Any]) -> Optional[InterviewSimulation]:
        """
        Запускает полную симуляцию интервью между HR и кандидатом.
        
        Args:
            parsed_resume: Словарь с распарсенными данными резюме
            parsed_vacancy: Словарь с распарсенными данными вакансии
        
        Returns:
            InterviewSimulation: Объект с результатами симуляции или None в случае ошибки
        """
        try:
            dialog_messages = []
            position_title = parsed_vacancy.get('description', 'IT позиция')[:100] + "..."
            candidate_name = "Кандидат"  # Можно извлечь из резюме если есть
            
            # Проводим диалог по раундам
            for round_num in range(1, self.dialog_rounds + 1):
                logger.info(f"Начинаем раунд {round_num} симуляции интервью")
                
                # HR задает вопрос
                hr_question = await self._get_hr_question(parsed_resume, parsed_vacancy, dialog_messages, round_num)
                if not hr_question:
                    logger.error(f"Не удалось получить вопрос HR в раунде {round_num}")
                    break
                
                hr_message = DialogMessage(
                    speaker="HR",
                    message=hr_question,
                    round_number=round_num
                )
                dialog_messages.append(hr_message)
                
                # Кандидат отвечает
                candidate_answer = await self._get_candidate_answer(parsed_resume, parsed_vacancy, dialog_messages, hr_question)
                if not candidate_answer:
                    logger.error(f"Не удалось получить ответ кандидата в раунде {round_num}")
                    break
                
                candidate_message = DialogMessage(
                    speaker="Candidate", 
                    message=candidate_answer,
                    round_number=round_num
                )
                dialog_messages.append(candidate_message)
                
                logger.info(f"Раунд {round_num} завершен успешно")
            
            # Генерируем финальную оценку
            assessment = await self._generate_final_assessment(parsed_resume, parsed_vacancy, dialog_messages)
            
            # Создаем объект симуляции
            simulation = InterviewSimulation(
                position_title=position_title,
                candidate_name=candidate_name,
                company_context=f"Интервью на позицию из вакансии: {parsed_vacancy.get('description', '')[:200]}...",
                dialog_messages=dialog_messages,
                hr_assessment=assessment.get('hr_assessment', 'Оценка не доступна'),
                candidate_performance_analysis=assessment.get('performance_analysis', 'Анализ не доступен'),
                improvement_recommendations=assessment.get('improvement_recommendations', 'Рекомендации не доступны'),
                simulation_metadata={
                    'rounds_completed': len(dialog_messages) // 2,
                    'total_rounds_planned': self.dialog_rounds,
                    'model_used': self.model
                }
            )
            
            logger.info("Симуляция интервью успешно завершена")
            return simulation
            
        except Exception as e:
            logger.error(f"Ошибка при симуляции интервью: {e}")
            return None