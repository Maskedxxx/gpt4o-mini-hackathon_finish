"""
Веб-приложение для генерации чек-листа подготовки к интервью

Простая веб-форма для загрузки PDF резюме и генерации персонализированного 
чек-листа подготовки к интервью на основе целевой вакансии.
"""

import os
import tempfile
from pathlib import Path
from fastapi import FastAPI, Form, File, UploadFile, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import aiohttp

# Импорты проекта
from src.parsers.pdf_resume_parser import PDFResumeParser
from src.parsers.vacancy_extractor import VacancyExtractor
from src.hh.api_client import HHApiClient
from src.hh.auth import HHAuthService
from src.hh.token_exchanger import HHCodeExchanger
from src.callback_local_server.config import settings as callback_settings
from src.llm_interview_checklist.llm_interview_checklist_generator import LLMInterviewChecklistGenerator
from src.utils import get_logger

logger = get_logger()

app = FastAPI(title="AI Resume Assistant - Interview Checklist")

# Настройка шаблонов
templates = Jinja2Templates(directory="src/web_app/interview_checklist/templates")

# Создание экземпляров сервисов
pdf_parser = PDFResumeParser()
vacancy_extractor = VacancyExtractor()
hh_auth_service = HHAuthService()
token_exchanger = HHCodeExchanger()
checklist_generator = LLMInterviewChecklistGenerator()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Главная страница с формой генерации чек-листа"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/auth/hh")
async def start_hh_auth():
    """Начало авторизации HH.ru"""
    auth_url = hh_auth_service.get_auth_url()
    return {"auth_url": auth_url}

@app.get("/auth/tokens")
async def get_tokens_from_callback():
    """Получение токенов из callback сервера"""
    try:
        callback_url = f"http://{callback_settings.host}:{callback_settings.port}/api/code"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(callback_url) as response:
                if response.status == 200:
                    data = await response.json()
                    code = data.get("code")
                    
                    if code:
                        # Обмениваем код на токены
                        tokens = await token_exchanger.exchange_code(code)
                        
                        # Очищаем код на сервере
                        await session.post(f"http://{callback_settings.host}:{callback_settings.port}/api/reset_code")
                        
                        return {
                            "success": True,
                            "access_token": tokens["access_token"],
                            "refresh_token": tokens["refresh_token"]
                        }
                    
                return {"success": False, "message": "Код авторизации не найден"}
                
    except Exception as e:
        logger.error(f"Ошибка получения токенов: {e}")
        return {"success": False, "message": f"Ошибка: {str(e)}"}

@app.post("/generate-checklist")
async def generate_interview_checklist(
    resume_file: UploadFile = File(...),
    vacancy_url: str = Form(...),
    hh_access_token: str = Form(...),
    hh_refresh_token: str = Form(...)
):
    """Генерация чек-листа подготовки к интервью"""
    
    try:
        # Валидация файла
        if not resume_file.filename.endswith('.pdf'):
            raise HTTPException(400, "Файл должен быть в формате PDF")
        
        # Сохранение загруженного файла
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            content = await resume_file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        try:
            # Парсинг PDF резюме
            logger.info("Парсинг PDF резюме...")
            parsed_resume = pdf_parser.parse_pdf_resume(tmp_file_path)
            
            # Извлечение ID вакансии из URL
            vacancy_id = extract_vacancy_id(vacancy_url)
            if not vacancy_id:
                raise HTTPException(400, "Некорректная ссылка на вакансию")
            
            # Получение данных вакансии
            logger.info(f"Получение данных вакансии {vacancy_id}...")
            hh_client = HHApiClient(hh_access_token, hh_refresh_token)
            vacancy_data = await hh_client.request(f'vacancies/{vacancy_id}')
            
            # Парсинг данных вакансии
            parsed_vacancy = vacancy_extractor.extract_vacancy_info(vacancy_data)
            
            # Генерация чек-листа (преобразуем модели в словари)
            logger.info("Генерация чек-листа подготовки к интервью...")
            resume_dict = parsed_resume.model_dump()
            vacancy_dict = parsed_vacancy.model_dump()
            
            # Пробуем новую профессиональную версию, fallback на старую
            try:
                checklist_result = await checklist_generator.generate_professional_interview_checklist(resume_dict, vacancy_dict)
            except Exception as e:
                logger.warning(f"Не удалось использовать профессиональную версию: {e}")
                checklist_result = await checklist_generator.generate_interview_checklist(resume_dict, vacancy_dict)
            
            if not checklist_result:
                logger.error("Не удалось сгенерировать чек-лист")
                raise HTTPException(500, "Не удалось сгенерировать чек-лист")
            
            # Форматирование результатов для веб-отображения
            formatted_result = format_checklist_for_web(checklist_result)
            
            return JSONResponse({
                "status": "success",
                "checklist": formatted_result
            })
            
        finally:
            # Удаляем временный файл
            os.unlink(tmp_file_path)
            
    except Exception as e:
        logger.error(f"Ошибка при генерации чек-листа: {e}")
        raise HTTPException(500, f"Ошибка генерации: {str(e)}")

def extract_vacancy_id(vacancy_url: str) -> str:
    """Извлечение ID вакансии из URL"""
    import re
    pattern = r'https?://(?:www\.)?hh\.ru/vacancy/(\d+)'
    match = re.search(pattern, vacancy_url)
    return match.group(1) if match else None

def format_checklist_for_web(checklist) -> dict:
    """Форматирование результатов чек-листа для веб-отображения"""
    
    # Проверяем тип модели - профессиональная или старая версия
    if hasattr(checklist, 'executive_summary'):
        # Профессиональная версия
        return {
            "type": "professional",
            "candidate_level": checklist.personalization_context.candidate_level,
            "vacancy_type": checklist.personalization_context.vacancy_type,
            "company_format": checklist.personalization_context.company_format,
            "executive_summary": {
                "preparation_strategy": checklist.preparation_strategy,
                "key_focus_areas": checklist.personalization_context.critical_focus_areas,
                "estimated_prep_time": checklist.time_estimates.total_time_needed,
                "priority_recommendations": checklist.personalization_context.key_gaps_identified
            },
            "technical_preparation": [
                {
                    "category": item.category,
                    "priority": item.priority,
                    "tasks": [item.task_title, item.description],
                    "time_estimate": item.estimated_time,
                    "resources": item.specific_resources
                } for item in checklist.technical_preparation
            ],
            "behavioral_preparation": [
                {
                    "category": item.category,
                    "priority": "ВАЖНО",  # По умолчанию для поведенческой подготовки
                    "tasks": [item.task_title, item.description] + item.example_questions,
                    "time_estimate": "1-2 часа",  # По умолчанию
                    "resources": [item.practice_tips]
                } for item in checklist.behavioral_preparation
            ],
            "company_research": [
                {
                    "category": item.category,
                    "priority": item.priority,
                    "tasks": [item.task_title] + item.specific_actions,
                    "time_estimate": item.time_required,
                    "resources": []
                } for item in checklist.company_research
            ],
            "technical_stack_study": [
                {
                    "category": item.category,
                    "priority": "ВАЖНО",  # По умолчанию
                    "tasks": [item.task_title, item.description, item.study_approach],
                    "time_estimate": "2-4 часа",  # По умолчанию
                    "resources": []
                } for item in checklist.technical_stack_study
            ],
            "practical_exercises": [
                {
                    "category": item.category,
                    "priority": "ВАЖНО",  # По умолчанию
                    "tasks": [item.exercise_title, item.description, f"Уровень: {item.difficulty_level}"],
                    "time_estimate": "3-5 часов",  # По умолчанию
                    "resources": item.practice_resources
                } for item in checklist.practical_exercises
            ],
            "interview_setup": [
                {
                    "category": item.category,
                    "priority": "КРИТИЧНО",  # По умолчанию для настройки
                    "tasks": [item.task_title] + item.checklist_items,
                    "time_estimate": "30 минут",  # По умолчанию
                    "resources": []
                } for item in checklist.interview_setup
            ],
            "additional_actions": [
                {
                    "category": item.category,
                    "priority": item.urgency,
                    "tasks": [item.action_title, item.description] + item.implementation_steps,
                    "time_estimate": "1-2 часа",  # По умолчанию
                    "resources": []
                } for item in checklist.additional_actions
            ],
            "critical_success_factors": checklist.critical_success_factors
        }
    else:
        # Старая версия (совместимость)
        return {
            "type": "basic",
            "technical_preparation": [
                {
                    "category": "техническая_подготовка",
                    "priority": skill.priority,
                    "tasks": [skill.skill_name, skill.study_plan, f"Текущий уровень: {skill.current_level_assessment}"],
                    "time_estimate": getattr(skill, 'estimated_time', 'Не указано'),
                    "resources": [r.title for r in skill.resources]
                } for skill in checklist.technical_skills
            ],
            "behavioral_preparation": [
                {
                    "category": q.question_category,
                    "priority": "ВАЖНО",
                    "tasks": q.example_questions + [q.preparation_tips],
                    "time_estimate": "1-2 часа",
                    "resources": [q.star_method_examples] if q.star_method_examples else []
                } for q in checklist.behavioral_questions
            ],
            "company_research": [
                {
                    "category": "исследование_компании",
                    "priority": "ВАЖНО",
                    "tasks": [checklist.company_research_tips],
                    "time_estimate": "2-3 часа",
                    "resources": []
                }
            ],
            "general_recommendations": [checklist.final_recommendations] if hasattr(checklist, 'final_recommendations') else []
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)