"""
Веб-приложение для гап-анализа резюме

Простая веб-форма для загрузки PDF резюме и анализа вакансий.
"""

import os
import tempfile
from pathlib import Path
from fastapi import FastAPI, Form, File, UploadFile, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
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
from src.llm_gap_analyzer.llm_gap_analyzer import LLMGapAnalyzer
from src.utils import get_logger
from .pdf_generator import GapAnalysisPDFGenerator

# Импорт системы авторизации
from src.security.auth import SimpleAuth

logger = get_logger()

app = FastAPI(title="AI Resume Assistant - Gap Analysis")

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
llm_analyzer = LLMGapAnalyzer()

# Временное хранилище для токенов (в реальном приложении использовать Redis/DB)
user_tokens = {}

# Временное хранилище для результатов анализа (для PDF генерации)
analysis_storage = {}

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
    """Главная страница с формой гап-анализа"""
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

# ================== GAP ANALYSIS ==================

@app.post("/gap-analysis")
async def perform_gap_analysis(
    resume_file: UploadFile = File(...),
    vacancy_url: str = Form(...),
    _: bool = Depends(auth_system.require_auth)
):
    """Выполнение гап-анализа резюме"""
    
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
            
            # Выполнение гап-анализа (преобразуем модели в словари)
            logger.info("Выполнение гап-анализа...")
            resume_dict = parsed_resume.model_dump()
            vacancy_dict = parsed_vacancy.model_dump()
            analysis_result = await llm_analyzer.gap_analysis(resume_dict, vacancy_dict)
            
            # Сохраняем результат для генерации PDF
            analysis_id = f"gap_{hash(str(resume_dict) + str(vacancy_dict))}"
            analysis_storage[analysis_id] = analysis_result
            
            # Форматирование результатов для веб-отображения
            formatted_result = format_analysis_for_web(analysis_result)
            
            return JSONResponse({
                "status": "success",
                "analysis": formatted_result,
                "analysis_id": analysis_id
            })
            
        finally:
            # Удаляем временный файл
            os.unlink(tmp_file_path)
            
    except Exception as e:
        logger.error(f"Ошибка при выполнении гап-анализа: {e}")
        raise HTTPException(500, f"Ошибка анализа: {str(e)}")

@app.get("/download-gap-analysis/{analysis_id}")
async def download_gap_analysis_pdf(analysis_id: str, _: bool = Depends(auth_system.require_auth)):
    """Скачивание PDF отчета гап-анализа"""
    try:
        # Проверяем наличие результата
        if analysis_id not in analysis_storage:
            raise HTTPException(404, "Анализ не найден")
        
        analysis_result = analysis_storage[analysis_id]
        
        # Генерируем PDF отчет
        pdf_generator = GapAnalysisPDFGenerator()
        pdf_buffer = pdf_generator.generate_pdf(analysis_result)
        
        # Сохраняем PDF в файл
        report_path = f"/tmp/gap_analysis_report_{analysis_id}.pdf"
        with open(report_path, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        # Определяем имя файла для скачивания
        filename = f"Gap_Analysis_Report_{analysis_id[:8]}.pdf"
        
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

def format_analysis_for_web(analysis) -> dict:
    """Форматирование результатов анализа для веб-отображения"""
    return {
        "primary_screening": {
            "overall_result": analysis.primary_screening.overall_screening_result,
            "job_title_match": analysis.primary_screening.job_title_match,
            "experience_match": analysis.primary_screening.experience_years_match,
            "skills_visible": analysis.primary_screening.key_skills_visible,
            "location_suitable": analysis.primary_screening.location_suitable,
            "salary_match": analysis.primary_screening.salary_expectations_match,
            "notes": analysis.primary_screening.screening_notes
        },
        "requirements_analysis": [
            {
                "requirement_text": req.requirement_text,
                "requirement_type": req.requirement_type,
                "compliance_status": req.compliance_status,
                "evidence_in_resume": req.evidence_in_resume,
                "gap_description": req.gap_description,
                "impact_on_decision": req.impact_on_decision
            } for req in analysis.requirements_analysis
        ],
        "quality_assessment": {
            "structure_clarity": analysis.quality_assessment.structure_clarity,
            "content_relevance": analysis.quality_assessment.content_relevance,
            "achievement_focus": analysis.quality_assessment.achievement_focus,
            "adaptation_quality": analysis.quality_assessment.adaptation_quality,
            "overall_impression": analysis.quality_assessment.overall_impression,
            "quality_notes": analysis.quality_assessment.quality_notes
        },
        "critical_recommendations": [
            {
                "section": rec.section,
                "criticality": rec.criticality,
                "issue_description": rec.issue_description,
                "specific_actions": rec.specific_actions,
                "example_wording": rec.example_wording,
                "business_rationale": rec.business_rationale
            } for rec in analysis.critical_recommendations
        ],
        "important_recommendations": [
            {
                "section": rec.section,
                "criticality": rec.criticality,
                "issue_description": rec.issue_description,
                "specific_actions": rec.specific_actions,
                "example_wording": rec.example_wording,
                "business_rationale": rec.business_rationale
            } for rec in analysis.important_recommendations
        ],
        "optional_recommendations": [
            {
                "section": rec.section,
                "criticality": rec.criticality,
                "issue_description": rec.issue_description,
                "specific_actions": rec.specific_actions,
                "example_wording": rec.example_wording,
                "business_rationale": rec.business_rationale
            } for rec in analysis.optional_recommendations
        ],
        "match_percentage": analysis.overall_match_percentage,
        "hiring_recommendation": analysis.hiring_recommendation,
        "key_strengths": analysis.key_strengths,
        "major_gaps": analysis.major_gaps,
        "next_steps": analysis.next_steps
    }

# ================== МОНИТОРИНГ ==================

@app.get("/health")
async def health_check():
    """Health check endpoint для мониторинга"""
    try:
        return {
            "status": "healthy",
            "service": "ai-resume-assistant-gap-analysis",
            "version": "1.0.0",
            "port": 8000,
            "checks": {
                "auth_system": "ok",
                "templates": "ok",
                "storage": "ok"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "ai-resume-assistant-gap-analysis",
            "error": str(e)
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)