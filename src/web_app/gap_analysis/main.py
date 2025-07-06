"""
Веб-приложение для гап-анализа резюме

Простая веб-форма для загрузки PDF резюме и анализа вакансий.
"""

import os
import tempfile
from pathlib import Path
from fastapi import FastAPI, Form, File, UploadFile, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
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

logger = get_logger()

app = FastAPI(title="AI Resume Assistant - Web")

# Настройка шаблонов
current_dir = Path(__file__).parent
templates = Jinja2Templates(directory=str(current_dir / "templates"))

# Создание экземпляров сервисов
pdf_parser = PDFResumeParser()
vacancy_extractor = VacancyExtractor()
hh_auth_service = HHAuthService()
token_exchanger = HHCodeExchanger()
llm_analyzer = LLMGapAnalyzer()

# Временное хранилище для токенов (в реальном приложении использовать Redis/DB)
user_tokens = {}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Главная страница с формой гап-анализа"""
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
        import aiohttp
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

@app.post("/gap-analysis")
async def perform_gap_analysis(
    resume_file: UploadFile = File(...),
    vacancy_url: str = Form(...),
    hh_access_token: str = Form(...),
    hh_refresh_token: str = Form(...)
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
            
            # Получение данных вакансии
            logger.info(f"Получение данных вакансии {vacancy_id}...")
            hh_client = HHApiClient(hh_access_token, hh_refresh_token)
            vacancy_data = await hh_client.request(f'vacancies/{vacancy_id}')
            
            # Парсинг данных вакансии
            parsed_vacancy = vacancy_extractor.extract_vacancy_info(vacancy_data)
            
            # Выполнение гап-анализа (преобразуем модели в словари)
            logger.info("Выполнение гап-анализа...")
            resume_dict = parsed_resume.model_dump()
            vacancy_dict = parsed_vacancy.model_dump()
            analysis_result = await llm_analyzer.gap_analysis(resume_dict, vacancy_dict)
            
            # Форматирование результатов для веб-отображения
            formatted_result = format_analysis_for_web(analysis_result)
            
            return JSONResponse({
                "status": "success",
                "analysis": formatted_result
            })
            
        finally:
            # Удаляем временный файл
            os.unlink(tmp_file_path)
            
    except Exception as e:
        logger.error(f"Ошибка при выполнении гап-анализа: {e}")
        raise HTTPException(500, f"Ошибка анализа: {str(e)}")

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)