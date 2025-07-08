"""
Веб-приложение для генерации чек-листа подготовки к интервью

Простая веб-форма для загрузки PDF резюме и генерации персонализированного 
чек-листа подготовки к интервью на основе целевой вакансии.
"""

import os
import tempfile
from pathlib import Path
from fastapi import FastAPI, Form, File, UploadFile, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
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
from .pdf_generator import InterviewChecklistPDFGenerator

# Импорт системы авторизации
from src.security.auth import SimpleAuth

logger = get_logger()

app = FastAPI(title="AI Resume Assistant - Interview Checklist")

# Настройка системы авторизации
current_dir = Path(__file__).parent
auth_system = SimpleAuth(templates_dir=str(current_dir.parent.parent / "security" / "templates"))

# Добавляем middleware авторизации
app.add_middleware(
    auth_system.get_middleware().__class__,
    config=auth_system.config,
    session_manager=auth_system.session_manager,
    templates=auth_system.templates
)

# Настройка шаблонов
templates = Jinja2Templates(directory=str(current_dir / "templates"))

# Создание экземпляров сервисов
pdf_parser = PDFResumeParser()
vacancy_extractor = VacancyExtractor()
hh_auth_service = HHAuthService()
token_exchanger = HHCodeExchanger()
checklist_generator = LLMInterviewChecklistGenerator()

# Временное хранилище для токенов и результатов
user_tokens = {}
checklist_storage = {}

# ================== АВТОРИЗАЦИЯ ==================

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Страница авторизации"""
    return await auth_system.login_page(request)

@app.post("/login")
async def login_post(request: Request, password: str = Form(...)):
    """Обработка авторизации"""
    return await auth_system.login_post(request, password)

@app.get("/logout")
async def logout(request: Request):
    """Выход из системы"""
    return await auth_system.logout(request)

# ================== ГЛАВНАЯ СТРАНИЦА ==================

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, _: bool = Depends(auth_system.require_auth)):
    """Главная страница с формой генерации чек-листа"""
    return templates.TemplateResponse("index.html", {"request": request})

# ================== HH.RU АВТОРИЗАЦИЯ ==================

@app.post("/auth/hh")
async def start_hh_auth(_: bool = Depends(auth_system.require_auth)):
    """Начало авторизации HH.ru"""
    auth_url = hh_auth_service.get_auth_url()
    return {"auth_url": auth_url}

@app.get("/auth/tokens")
async def get_tokens_from_callback(_: bool = Depends(auth_system.require_auth)):
    """Получение токенов из callback сервера"""
    try:
        # Сначала проверяем, есть ли уже сохраненные токены
        if "hh_access_token" in user_tokens and "hh_refresh_token" in user_tokens:
            return {
                "success": True,
                "message": "Авторизация уже выполнена"
            }
        
        callback_url = f"http://{callback_settings.host}:{callback_settings.port}/api/code"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(callback_url) as response:
                if response.status == 200:
                    data = await response.json()
                    code = data.get("code")
                    
                    if code:
                        logger.info(f"Получен код авторизации, обмениваем на токены...")
                        
                        # Обмениваем код на токены
                        tokens = await token_exchanger.exchange_code(code)
                        
                        # Сохраняем токены во временном хранилище
                        user_tokens["hh_access_token"] = tokens["access_token"]
                        user_tokens["hh_refresh_token"] = tokens["refresh_token"]
                        
                        logger.info("Токены успешно сохранены")
                        
                        # Только после успешного сохранения очищаем код на сервере
                        await session.post(f"http://{callback_settings.host}:{callback_settings.port}/api/reset_code")
                        
                        return {
                            "success": True,
                            "message": "Авторизация успешна"
                        }
                    
                return {"success": False, "message": "Код авторизации не найден"}
                
    except Exception as e:
        logger.error(f"Ошибка получения токенов: {e}")
        return {"success": False, "message": f"Ошибка: {str(e)}"}

# ================== CHECKLIST GENERATION ==================

@app.post("/generate-checklist")
async def generate_interview_checklist(
    resume_file: UploadFile = File(...),
    vacancy_url: str = Form(...),
    _: bool = Depends(auth_system.require_auth)
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
            
            # Проверяем наличие токенов
            if "hh_access_token" not in user_tokens or "hh_refresh_token" not in user_tokens:
                raise HTTPException(400, "Необходима авторизация HH.ru")
            
            # Получение данных вакансии
            logger.info(f"Получение данных вакансии {vacancy_id}...")
            hh_client = HHApiClient(user_tokens["hh_access_token"], user_tokens["hh_refresh_token"])
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
            
            # Сохраняем результат для генерации PDF
            checklist_id = f"checklist_{hash(str(resume_dict) + str(vacancy_dict))}"
            checklist_storage[checklist_id] = checklist_result
            
            # Форматирование результатов для веб-отображения
            formatted_result = format_checklist_for_web(checklist_result)
            
            return JSONResponse({
                "status": "success",
                "checklist": formatted_result,
                "checklist_id": checklist_id
            })
            
        finally:
            # Удаляем временный файл
            os.unlink(tmp_file_path)
            
    except Exception as e:
        logger.error(f"Ошибка при генерации чек-листа: {e}")
        raise HTTPException(500, f"Ошибка генерации: {str(e)}")

@app.get("/download-checklist/{checklist_id}")
async def download_checklist_pdf(checklist_id: str, _: bool = Depends(auth_system.require_auth)):
    """Скачивание PDF чек-листа подготовки к интервью"""
    try:
        # Проверяем наличие результата
        if checklist_id not in checklist_storage:
            raise HTTPException(404, "Чек-лист не найден")
        
        checklist_result = checklist_storage[checklist_id]
        
        # Генерируем PDF отчет
        pdf_generator = InterviewChecklistPDFGenerator()
        pdf_buffer = pdf_generator.generate_pdf(checklist_result)
        
        # Сохраняем PDF в файл
        report_path = f"/tmp/interview_checklist_{checklist_id}.pdf"
        with open(report_path, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        # Определяем имя файла для скачивания
        filename = f"Interview_Checklist_{checklist_id[:8]}.pdf"
        
        return FileResponse(
            path=report_path,
            filename=filename,
            media_type='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Ошибка при генерации PDF: {e}")
        raise HTTPException(500, f"Ошибка генерации PDF: {str(e)}")

def extract_vacancy_id(vacancy_url: str) -> str:
    """Извлечение ID вакансии из URL"""
    import re
    # Учитываем префиксы городов (например: nn.hh.ru, spb.hh.ru, ekb.hh.ru)
    pattern = r'https?://(?:(?:www\.|[a-z]+\.)?)?hh\.ru/vacancy/(\d+)'
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

# ================== МОНИТОРИНГ ==================

@app.get("/health")
async def health_check():
    """Health check endpoint для мониторинга"""
    try:
        return {
            "status": "healthy",
            "service": "ai-resume-assistant-interview-checklist",
            "version": "1.0.0",
            "port": 8002,
            "checks": {
                "auth_system": "ok",
                "templates": "ok",
                "storage": "ok"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "ai-resume-assistant-interview-checklist",
            "error": str(e)
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)