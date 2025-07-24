"""
Объединенное веб-приложение для AI Resume Assistant

Единое приложение со всеми 4 функциями:
- Gap-анализ резюме
- Генерация сопроводительного письма
- Чек-лист подготовки к интервью
- Симуляция интервью

Запуск: python -m src.web_app.unified_app.main
URL: http://localhost:3000
"""

import os
import tempfile
import asyncio
from pathlib import Path
from fastapi import FastAPI, Form, File, UploadFile, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import aiohttp
from typing import List, Optional

# Импорты проекта
from src.parsers.pdf_resume_parser import PDFResumeParser
from src.parsers.vacancy_extractor import VacancyExtractor
from src.hh.api_client import HHApiClient
from src.hh.auth import HHAuthService
from src.hh.token_exchanger import HHCodeExchanger
from src.callback_local_server.config import settings as callback_settings
from src.llm_gap_analyzer.llm_gap_analyzer import LLMGapAnalyzer
from src.llm_cover_letter.llm_cover_letter_generator import EnhancedLLMCoverLetterGenerator
from src.llm_interview_checklist.llm_interview_checklist_generator import LLMInterviewChecklistGenerator
from src.llm_interview_simulation.llm_interview_simulator import ProfessionalInterviewSimulator
from src.llm_resume_rewriter.llm_resume_rewriter import LLMResumeRewriter
from src.utils import get_logger
from src.models.gap_analysis_models import EnhancedResumeTailoringAnalysis
from src.models.resume_models import ResumeInfo

# Импорт системы авторизации
from src.security.auth import SimpleAuth
from src.security.health_dashboard import add_health_dashboard_routes

# Импорт демо-системы
from src.demo_cache.demo_manager import DemoManager

# PDF генераторы
from src.web_app.gap_analysis.pdf_generator import GapAnalysisPDFGenerator
from src.web_app.cover_letter.pdf_generator import CoverLetterPDFGenerator
from src.web_app.interview_checklist.pdf_generator import InterviewChecklistPDFGenerator

logger = get_logger()

def extract_profile_from_session_or_id(request_id: str, default: str = "middle") -> str:
    """
    Извлекает уровень профиля из ID запроса или сессии.
    Для демо-режима пытается определить уровень по паттернам в ID.
    """
    if not request_id:
        return default
    
    request_id_lower = request_id.lower()
    
    # Ищем индикаторы уровня в ID
    if any(pattern in request_id_lower for pattern in ['junior', 'джуниор', 'начинающий']):
        return "junior"
    elif any(pattern in request_id_lower for pattern in ['senior', 'сеньор', 'старший', 'lead']):
        return "senior"
    elif any(pattern in request_id_lower for pattern in ['middle', 'мидл', 'средний']):
        return "middle"
    
    # Используем хеш от ID для детерминированного выбора
    id_hash = hash(request_id) % 3
    levels = ["junior", "middle", "senior"]
    return levels[id_hash]

app = FastAPI(title="AI Resume Assistant - Unified Web App")

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

# Статические файлы (если нужны)
static_dir = current_dir / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Создание экземпляров сервисов
pdf_parser = PDFResumeParser()
vacancy_extractor = VacancyExtractor()
hh_auth_service = HHAuthService()
token_exchanger = HHCodeExchanger()

# LLM сервисы
llm_gap_analyzer = LLMGapAnalyzer()
cover_letter_generator = EnhancedLLMCoverLetterGenerator(validate_quality=False)
checklist_generator = LLMInterviewChecklistGenerator()
interview_simulator = ProfessionalInterviewSimulator()
resume_rewriter = LLMResumeRewriter()

# Временное хранилище для токенов и результатов
user_tokens = {}
analysis_storage = {}
cover_letter_storage = {}
checklist_storage = {}
simulation_storage = {}
simulation_progress_storage = {}
adapted_resume_storage = {}

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
    """Главная страница с навигацией по всем функциям"""
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
        
        callback_url = f"{callback_settings.protocol}://{callback_settings.host}:{callback_settings.port}/api/code"
        
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

# ================== СТРАНИЦЫ ФУНКЦИЙ ==================

@app.get("/gap-analysis", response_class=HTMLResponse)
async def gap_analysis_page(request: Request, _: bool = Depends(auth_system.require_auth)):
    """Страница гап-анализа"""
    return templates.TemplateResponse("gap_analysis.html", {"request": request})

@app.get("/cover-letter", response_class=HTMLResponse)
async def cover_letter_page(request: Request, _: bool = Depends(auth_system.require_auth)):
    """Страница генерации сопроводительного письма"""
    return templates.TemplateResponse("cover_letter.html", {"request": request})

@app.get("/interview-checklist", response_class=HTMLResponse)
async def interview_checklist_page(request: Request, _: bool = Depends(auth_system.require_auth)):
    """Страница чек-листа подготовки к интервью"""
    return templates.TemplateResponse("interview_checklist.html", {"request": request})

@app.get("/interview-simulation", response_class=HTMLResponse)
async def interview_simulation_page(request: Request, _: bool = Depends(auth_system.require_auth)):
    """Страница симуляции интервью"""
    return templates.TemplateResponse("interview_simulation.html", {"request": request})

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
            
            # Выполнение гап-анализа
            logger.info("Выполнение гап-анализа...")
            resume_dict = parsed_resume.model_dump()
            vacancy_dict = parsed_vacancy.model_dump()
            analysis_result = await llm_gap_analyzer.gap_analysis(resume_dict, vacancy_dict)
            
            # Сохраняем результат для генерации PDF и адаптации резюме
            analysis_id = f"gap_{hash(str(resume_dict) + str(vacancy_dict))}"
            analysis_storage[analysis_id] = {
                'analysis_result': analysis_result,
                'resume_data': resume_dict,
                'vacancy_data': vacancy_dict
            }
            
            # Форматирование результатов для веб-отображения
            formatted_result = format_gap_analysis_for_web(analysis_result)
            
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
        if analysis_id not in analysis_storage:
            raise HTTPException(404, "Анализ не найден")
        
        analysis_data = analysis_storage[analysis_id]
        analysis_result = analysis_data['analysis_result'] if isinstance(analysis_data, dict) else analysis_data
        
        # Генерируем PDF отчет
        pdf_generator = GapAnalysisPDFGenerator()
        pdf_buffer = pdf_generator.generate_pdf(analysis_result)
        
        # Сохраняем PDF в файл
        report_path = f"/tmp/gap_analysis_report_{analysis_id}.pdf"
        with open(report_path, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        filename = f"Gap_Analysis_Report_{analysis_id[:8]}.pdf"
        
        return FileResponse(
            path=report_path,
            filename=filename,
            media_type='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Ошибка при генерации PDF: {e}")
        raise HTTPException(500, f"Ошибка генерации PDF: {str(e)}")

# ================== RESUME REWRITER ==================

@app.post("/adapt-resume/{analysis_id}")
async def adapt_resume(analysis_id: str, _: bool = Depends(auth_system.require_auth)):
    """Адаптация резюме на основе GAP-анализа"""
    try:
        if analysis_id not in analysis_storage:
            raise HTTPException(404, "Анализ не найден")
        
        # Извлекаем данные из хранилища
        analysis_data = analysis_storage[analysis_id]
        if isinstance(analysis_data, dict):
            resume_data = analysis_data['resume_data']
            gap_analysis_data = analysis_data['analysis_result'].model_dump()
        else:
            raise HTTPException(400, "Для адаптации резюме требуются исходные данные резюме")
        
        logger.info(f"Начало адаптации резюме для анализа {analysis_id}")
        
        # Вызов LLM сервиса для адаптации резюме
        adapted_resume = await resume_rewriter.rewrite_resume(resume_data, gap_analysis_data)
        
        if adapted_resume is None:
            raise HTTPException(500, "Не удалось адаптировать резюме")
        
        # Сохраняем адаптированное резюме
        adaptation_id = f"adapted_{analysis_id}_{hash(str(adapted_resume.model_dump()))}"
        adapted_resume_storage[adaptation_id] = {
            'adapted_resume': adapted_resume,
            'original_resume': resume_data,
            'gap_analysis_id': analysis_id
        }
        
        logger.info(f"Резюме успешно адаптировано: {adaptation_id}")
        
        return JSONResponse({
            "status": "success",
            "message": "Резюме успешно адаптировано под требования вакансии",
            "adaptation_id": adaptation_id
        })
        
    except Exception as e:
        logger.error(f"Ошибка при адаптации резюме: {e}")
        raise HTTPException(500, f"Ошибка адаптации резюме: {str(e)}")

@app.get("/download-adapted-resume/{adaptation_id}")
async def download_adapted_resume_pdf(adaptation_id: str, _: bool = Depends(auth_system.require_auth)):
    """Скачивание PDF адаптированного резюме"""
    try:
        if adaptation_id not in adapted_resume_storage:
            raise HTTPException(404, "Адаптированное резюме не найдено")
        
        adaptation_data = adapted_resume_storage[adaptation_id]
        adapted_resume = adaptation_data['adapted_resume']
        
        logger.info(f"Генерация PDF для адаптированного резюме {adaptation_id}")
        
        # Генерируем PDF с адаптированным резюме
        # Используем тот же PDF генератор, что и для обычных резюме
        from src.web_app.gap_analysis.pdf_generator import GapAnalysisPDFGenerator
        pdf_generator = GapAnalysisPDFGenerator()
        
        # Создаем временную структуру для PDF генератора
        temp_analysis = {
            'resume_info': adapted_resume,
            'match_percentage': 95,  # Высокий процент для адаптированного резюме
            'hiring_recommendation': 'Рекомендуется к найму - резюме адаптировано под требования вакансии',
            'key_strengths': ['Адаптированное резюме', 'Соответствует требованиям вакансии'],
            'major_gaps': ['Минимальные'],
            'next_steps': 'Отправить резюме работодателю'
        }
        
        pdf_buffer = pdf_generator.generate_adapted_resume_pdf(adapted_resume)
        
        # Сохраняем PDF в файл
        report_path = f"/tmp/adapted_resume_{adaptation_id}.pdf"
        with open(report_path, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        filename = f"Adapted_Resume_{adaptation_id[:8]}.pdf"
        
        return FileResponse(
            path=report_path,
            filename=filename,
            media_type='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Ошибка при генерации PDF адаптированного резюме: {e}")
        raise HTTPException(500, f"Ошибка генерации PDF: {str(e)}")

# ================== COVER LETTER ==================

@app.post("/generate-cover-letter")
async def generate_cover_letter(
    resume_file: UploadFile = File(...),
    vacancy_url: str = Form(...),
    _: bool = Depends(auth_system.require_auth)
):
    """Генерация сопроводительного письма"""
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
            
            # Генерация сопроводительного письма
            logger.info("Генерация сопроводительного письма...")
            resume_dict = parsed_resume.model_dump()
            vacancy_dict = parsed_vacancy.model_dump()
            cover_letter_result = await cover_letter_generator.generate_enhanced_cover_letter(resume_dict, vacancy_dict)
            
            if not cover_letter_result:
                logger.error("Не удалось сгенерировать сопроводительное письмо")
                raise HTTPException(500, "Не удалось сгенерировать сопроводительное письмо")
            
            # Сохраняем результат для генерации PDF
            letter_id = f"letter_{hash(str(resume_dict) + str(vacancy_dict))}"
            cover_letter_storage[letter_id] = cover_letter_result
            
            # Форматирование результатов для веб-отображения
            formatted_result = format_cover_letter_for_web(cover_letter_result)
            
            return JSONResponse({
                "status": "success",
                "cover_letter": formatted_result,
                "letter_id": letter_id
            })
            
        finally:
            # Удаляем временный файл
            os.unlink(tmp_file_path)
            
    except Exception as e:
        logger.error(f"Ошибка при генерации сопроводительного письма: {e}")
        raise HTTPException(500, f"Ошибка генерации: {str(e)}")

@app.get("/download-cover-letter/{letter_id}")
async def download_cover_letter_pdf(letter_id: str, _: bool = Depends(auth_system.require_auth)):
    """Скачивание PDF сопроводительного письма"""
    try:
        demo_manager = DemoManager()
        
        # Проверяем демо-режим
        if demo_manager.is_demo_mode():
            # Определяем уровень профиля по letter_id (или используем сессию)
            profile_level = extract_profile_from_session_or_id(letter_id, "middle")  # default fallback
            demo_pdf_path = demo_manager.get_pdf_path("cover_letter", profile_level)
            
            if demo_pdf_path and os.path.exists(demo_pdf_path):
                filename = f"Cover_Letter_{profile_level}.pdf"
                logger.info(f"🎭 Serving demo PDF: {demo_pdf_path}")
                return FileResponse(
                    path=demo_pdf_path,
                    filename=filename,
                    media_type='application/pdf'
                )
        
        # Обычный режим
        if letter_id not in cover_letter_storage:
            raise HTTPException(404, "Сопроводительное письмо не найдено")
        
        cover_letter_result = cover_letter_storage[letter_id]
        
        # Генерируем PDF отчет
        pdf_generator = CoverLetterPDFGenerator()
        pdf_buffer = pdf_generator.generate_pdf(cover_letter_result)
        
        # Сохраняем PDF в файл
        report_path = f"/tmp/cover_letter_report_{letter_id}.pdf"
        with open(report_path, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        filename = f"Cover_Letter_{letter_id[:8]}.pdf"
        
        return FileResponse(
            path=report_path,
            filename=filename,
            media_type='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Ошибка при генерации PDF: {e}")
        raise HTTPException(500, f"Ошибка генерации PDF: {str(e)}")

# ================== INTERVIEW CHECKLIST ==================

@app.post("/generate-interview-checklist")
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
            
            # Генерация чек-листа
            logger.info("Генерация чек-листа подготовки к интервью...")
            resume_dict = parsed_resume.model_dump()
            vacancy_dict = parsed_vacancy.model_dump()
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

@app.get("/download-interview-checklist/{checklist_id}")
async def download_interview_checklist_pdf(checklist_id: str, _: bool = Depends(auth_system.require_auth)):
    """Скачивание PDF чек-листа"""
    try:
        demo_manager = DemoManager()
        
        # Проверяем демо-режим
        if demo_manager.is_demo_mode():
            profile_level = extract_profile_from_session_or_id(checklist_id, "middle")
            demo_pdf_path = demo_manager.get_pdf_path("interview_checklist", profile_level)
            
            if demo_pdf_path and os.path.exists(demo_pdf_path):
                filename = f"Interview_Checklist_{profile_level}.pdf"
                logger.info(f"🎭 Serving demo PDF: {demo_pdf_path}")
                return FileResponse(
                    path=demo_pdf_path,
                    filename=filename,
                    media_type='application/pdf'
                )
        
        # Обычный режим
        if checklist_id not in checklist_storage:
            raise HTTPException(404, "Чек-лист не найден")
        
        checklist_result = checklist_storage[checklist_id]
        
        # Генерируем PDF отчет
        pdf_generator = InterviewChecklistPDFGenerator()
        pdf_buffer = pdf_generator.generate_pdf(checklist_result)
        
        # Сохраняем PDF в файл
        report_path = f"/tmp/interview_checklist_report_{checklist_id}.pdf"
        with open(report_path, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        filename = f"Interview_Checklist_{checklist_id[:8]}.pdf"
        
        return FileResponse(
            path=report_path,
            filename=filename,
            media_type='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Ошибка при генерации PDF: {e}")
        raise HTTPException(500, f"Ошибка генерации PDF: {str(e)}")

# ================== INTERVIEW SIMULATION ==================

@app.post("/start-interview-simulation")
async def start_interview_simulation(
    resume_file: UploadFile = File(...),
    vacancy_url: str = Form(...),
    target_rounds: int = Form(5, ge=3, le=7),
    temperature: float = Form(0.7, ge=0.1, le=1.0),
    difficulty_level: str = Form("medium"),
    hr_persona: str = Form("professional"),
    focus_areas: str = Form("[]"),  # JSON строка с массивом
    include_behavioral: bool = Form(True),
    include_technical: bool = Form(True),
    _: bool = Depends(auth_system.require_auth)
):
    """Запуск симуляции интервью"""
    try:
        # Валидация файла
        if not resume_file.filename.endswith('.pdf'):
            raise HTTPException(400, "Файл должен быть в формате PDF")
        
        # Валидация параметров
        if difficulty_level not in ["easy", "medium", "hard"]:
            raise HTTPException(400, "Неверный уровень сложности. Доступны: easy, medium, hard")
        
        if hr_persona not in ["professional", "friendly", "strict", "technical"]:
            raise HTTPException(400, "Неверный тип HR. Доступны: professional, friendly, strict, technical")
        
        # Валидация focus_areas JSON
        try:
            import json
            focus_areas_list = json.loads(focus_areas)
            if not isinstance(focus_areas_list, list):
                raise ValueError("focus_areas должно быть массивом")
            
            valid_focus_areas = ["leadership", "teamwork", "communication", "problem_solving"]
            for area in focus_areas_list:
                if area not in valid_focus_areas:
                    raise ValueError(f"Неверная область фокуса: {area}")
        except (json.JSONDecodeError, ValueError) as e:
            raise HTTPException(400, f"Ошибка в параметре focus_areas: {str(e)}")
        
        # Проверяем что хотя бы один тип вопросов включен
        if not include_behavioral and not include_technical:
            raise HTTPException(400, "Должен быть включен хотя бы один тип вопросов (поведенческие или технические)")
        
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
            
            # Создание идентификатора симуляции
            simulation_id = f"sim_{hash(str(parsed_resume.model_dump()) + str(parsed_vacancy.model_dump()) + str(target_rounds))}"
            
            # Инициализация прогресса
            simulation_progress_storage[simulation_id] = {
                "status": "starting",
                "progress": 0,
                "message": "Инициализация симуляции..."
            }
            
            # Запуск симуляции в фоновом режиме
            config = {
                "target_rounds": target_rounds,
                "temperature": temperature,
                "difficulty_level": difficulty_level,
                "hr_persona": hr_persona,
                "focus_areas": focus_areas,
                "include_behavioral": include_behavioral,
                "include_technical": include_technical
            }
            
            asyncio.create_task(run_simulation_background(
                simulation_id,
                parsed_resume.model_dump(),
                parsed_vacancy.model_dump(),
                config
            ))
            
            return JSONResponse({
                "status": "started",
                "simulation_id": simulation_id,
                "message": "Симуляция интервью запущена"
            })
            
        finally:
            # Удаляем временный файл
            os.unlink(tmp_file_path)
            
    except Exception as e:
        logger.error(f"Ошибка при запуске симуляции: {e}")
        raise HTTPException(500, f"Ошибка запуска: {str(e)}")

@app.get("/simulation-progress/{simulation_id}")
async def get_simulation_progress(simulation_id: str, _: bool = Depends(auth_system.require_auth)):
    """Получение прогресса симуляции"""
    if simulation_id not in simulation_progress_storage:
        raise HTTPException(404, "Симуляция не найдена")
    
    return simulation_progress_storage[simulation_id]

@app.get("/simulation-result/{simulation_id}")
async def get_simulation_result(simulation_id: str, _: bool = Depends(auth_system.require_auth)):
    """Получение результатов симуляции"""
    if simulation_id not in simulation_storage:
        raise HTTPException(404, "Результаты симуляции не найдены")
    
    result = simulation_storage[simulation_id]
    formatted_result = format_simulation_for_web(result)
    
    return JSONResponse({
        "status": "success",
        "simulation": formatted_result,
        "simulation_id": simulation_id
    })

@app.get("/download-interview-simulation/{simulation_id}")
async def download_interview_simulation_pdf(simulation_id: str, _: bool = Depends(auth_system.require_auth)):
    """Скачивание PDF отчета симуляции интервью"""
    try:
        demo_manager = DemoManager()
        
        # Проверяем демо-режим
        if demo_manager.is_demo_mode():
            profile_level = extract_profile_from_session_or_id(simulation_id, "middle")
            demo_pdf_path = demo_manager.get_pdf_path("interview_simulation", profile_level)
            
            if demo_pdf_path and os.path.exists(demo_pdf_path):
                filename = f"Interview_Simulation_{profile_level}.pdf"
                logger.info(f"🎭 Serving demo PDF: {demo_pdf_path}")
                return FileResponse(
                    path=demo_pdf_path,
                    filename=filename,
                    media_type='application/pdf'
                )
        
        # Обычный режим
        if simulation_id not in simulation_storage:
            raise HTTPException(404, "Результаты симуляции не найдены")
        
        simulation_result = simulation_storage[simulation_id]
        
        # Импортируем PDF генератор
        from src.llm_interview_simulation.pdf_generator import ProfessionalInterviewPDFGenerator
        
        # Генерируем PDF отчет
        pdf_generator = ProfessionalInterviewPDFGenerator()
        pdf_buffer = pdf_generator.generate_pdf(simulation_result)
        
        # Сохраняем PDF в файл
        report_path = f"/tmp/interview_simulation_report_{simulation_id}.pdf"
        with open(report_path, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        filename = f"Interview_Simulation_{simulation_id[:8]}.pdf"
        
        return FileResponse(
            path=report_path,
            filename=filename,
            media_type='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Ошибка при генерации PDF симуляции: {e}")
        raise HTTPException(500, f"Ошибка генерации PDF: {str(e)}")

# ================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==================

async def update_simulation_progress(simulation_id: str, round_num: int, total_rounds: int):
    """Обновление прогресса симуляции"""
    progress = int((round_num / total_rounds) * 80) + 10  # 10-90% для раундов
    simulation_progress_storage[simulation_id] = {
        "status": "running",
        "progress": progress,
        "message": f"Раунд {round_num}/{total_rounds}: генерация вопросов и ответов..."
    }

async def run_simulation_background(simulation_id: str, resume_dict: dict, vacancy_dict: dict, config: dict):
    """Запуск симуляции в фоновом режиме"""
    try:
        # Обновляем прогресс
        simulation_progress_storage[simulation_id] = {
            "status": "running",
            "progress": 10,
            "message": "Настройка симулятора..."
        }
        
        # Настройка симулятора
        logger.info(f"Настройка симулятора с конфигурацией: {config}")
        
        # Валидация конфигурации перед передачей симулятору
        validated_config = {}
        if config.get("target_rounds"):
            validated_config["target_rounds"] = max(3, min(7, config["target_rounds"]))
        if config.get("temperature"):
            validated_config["temperature"] = max(0.1, min(1.0, config["temperature"]))
        if config.get("difficulty_level") in ["easy", "medium", "hard"]:
            validated_config["difficulty_level"] = config["difficulty_level"]
        if config.get("hr_persona") in ["professional", "friendly", "strict", "technical"]:
            validated_config["hr_persona"] = config["hr_persona"]
        
        # Парсим focus_areas если это строка JSON
        if config.get("focus_areas"):
            try:
                import json
                if isinstance(config["focus_areas"], str):
                    validated_config["focus_areas"] = json.loads(config["focus_areas"])
                else:
                    validated_config["focus_areas"] = config["focus_areas"]
            except (json.JSONDecodeError, TypeError):
                logger.warning("Ошибка парсинга focus_areas, используем пустой список")
                validated_config["focus_areas"] = []
        
        validated_config["include_behavioral"] = config.get("include_behavioral", True)
        validated_config["include_technical"] = config.get("include_technical", True)
        
        interview_simulator.set_custom_config(validated_config)
        
        simulation_progress_storage[simulation_id] = {
            "status": "running",
            "progress": 30,
            "message": "Запуск симуляции интервью..."
        }
        
        # Создаем async progress callback
        async def progress_callback(round_num: int, total_rounds: int):
            logger.info(f"Прогресс симуляции: {round_num}/{total_rounds}")
            await update_simulation_progress(simulation_id, round_num, total_rounds)
        
        # Запуск симуляции
        logger.info("Запуск метода simulate_interview...")
        simulation_result = await interview_simulator.simulate_interview(
            resume_dict, 
            vacancy_dict,
            progress_callback=progress_callback,
            config_overrides=config
        )
        
        logger.info(f"Результат симуляции: {type(simulation_result)}")
        
        simulation_progress_storage[simulation_id] = {
            "status": "running",
            "progress": 90,
            "message": "Завершение симуляции..."
        }
        
        # Проверяем результат симуляции
        if simulation_result is None:
            raise Exception("Симуляция не дала результата. Возможны причины: некорректные данные резюме/вакансии, проблемы с OpenAI API, или неподдерживаемые параметры.")
        
        # Проверяем что симуляция содержит нужные данные
        if not hasattr(simulation_result, 'dialog_messages') or not simulation_result.dialog_messages:
            raise Exception("Симуляция завершилась без диалога. Проверьте корректность резюме и вакансии.")
        
        if not hasattr(simulation_result, 'assessment') or not simulation_result.assessment:
            logger.warning("Симуляция завершилась без оценки, но содержит диалог - это нормально.")
        
        logger.info(f"Симуляция успешно завершена: {len(simulation_result.dialog_messages)} сообщений, оценка: {hasattr(simulation_result, 'assessment') and simulation_result.assessment is not None}")
        
        # Сохраняем результат
        simulation_storage[simulation_id] = simulation_result
        
        simulation_progress_storage[simulation_id] = {
            "status": "completed",
            "progress": 100,
            "message": "Симуляция завершена"
        }
        
    except Exception as e:
        logger.error(f"Ошибка в фоновой симуляции: {e}")
        simulation_progress_storage[simulation_id] = {
            "status": "error",
            "progress": 0,
            "message": f"Ошибка: {str(e)}"
        }

def extract_vacancy_id(vacancy_url: str) -> str:
    """Извлечение ID вакансии из URL"""
    import re
    pattern = r'https?://(?:(?:www\.|[a-z]+\.)?)?hh\.ru/vacancy/(\d+)'
    match = re.search(pattern, vacancy_url)
    return match.group(1) if match else None

def format_gap_analysis_for_web(analysis: EnhancedResumeTailoringAnalysis) -> dict:
    """Форматирование результатов гап-анализа для веб-отображения"""
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
                "skill_category": req.skill_category,
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

def format_cover_letter_for_web(cover_letter) -> dict:
    """Форматирование результатов сопроводительного письма для веб-отображения"""
    return {
        "company_context": {
            "company_name": cover_letter.company_context.company_name,
            "position_title": cover_letter.subject_line,
            "company_size": cover_letter.company_context.company_size,
            "role_type": cover_letter.role_type,
            "key_requirements": [cover_letter.skills_match.relevant_experience]
        },
        "skills_match": {
            "matching_skills": cover_letter.skills_match.matched_skills,
            "relevant_achievements": [cover_letter.skills_match.quantified_achievement] if cover_letter.skills_match.quantified_achievement else [],
            "unique_selling_points": [cover_letter.personalization.value_proposition],
            "experience_relevance_score": cover_letter.relevance_score
        },
        "personalization": {
            "tone": "профессиональный",
            "key_motivations": [cover_letter.personalization.role_motivation],
            "company_research_points": [cover_letter.personalization.company_knowledge] if cover_letter.personalization.company_knowledge else [],
            "customization_level": "высокий" if cover_letter.personalization_score >= 8 else "средний"
        },
        "letter_structure": {
            "opening_hook": cover_letter.opening_hook,
            "value_proposition": cover_letter.personalization.value_proposition,
            "specific_examples": [cover_letter.relevant_experience],
            "company_alignment": cover_letter.company_interest,
            "call_to_action": cover_letter.professional_closing
        },
        "final_letter": assemble_full_letter_text(cover_letter),
        "quality_assessment": {
            "personalization_score": cover_letter.personalization_score,
            "relevance_score": cover_letter.relevance_score,
            "engagement_score": cover_letter.professional_tone_score,
            "overall_quality": "EXCELLENT" if cover_letter.personalization_score >= 8 else "GOOD" if cover_letter.personalization_score >= 6 else "AVERAGE",
            "improvement_suggestions": cover_letter.improvement_suggestions
        }
    }

def assemble_full_letter_text(cover_letter) -> str:
    """Собирает полный текст письма из отдельных компонентов"""
    parts = [
        f"Тема: {cover_letter.subject_line}",
        "",
        cover_letter.personalized_greeting,
        "",
        cover_letter.opening_hook,
        "",
        cover_letter.company_interest,
        "",
        cover_letter.relevant_experience,
        "",
        cover_letter.value_demonstration,
    ]
    
    if cover_letter.growth_mindset:
        parts.extend(["", cover_letter.growth_mindset])
    
    parts.extend([
        "",
        cover_letter.professional_closing,
        "",
        cover_letter.signature
    ])
    
    return "\n".join(parts)

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

def format_simulation_for_web(simulation) -> dict:
    """Форматирование результатов симуляции для веб-отображения"""
    if simulation is None:
        return {
            "interview_rounds": [],
            "final_assessment": {
                "overall_score": 0,
                "strengths": ["Не определено"],
                "areas_for_improvement": ["Симуляция не завершена"],
                "hiring_recommendation": "Нет данных",
                "detailed_feedback": "Симуляция не дала результата"
            },
            "summary": {
                "total_rounds": 0,
                "average_score": 0,
                "simulation_duration": "прервана",
                "key_insights": ["Симуляция не завершена"]
            }
        }
    
    # Конвертируем dialog_messages в раунды интервью
    interview_rounds = []
    hr_messages = [msg for msg in simulation.dialog_messages if msg.speaker == "HR"]
    candidate_messages = [msg for msg in simulation.dialog_messages if msg.speaker == "Candidate"]
    
    for hr_msg in hr_messages:
        round_num = hr_msg.round_number
        # Находим соответствующий ответ кандидата
        candidate_msg = next(
            (msg for msg in candidate_messages if msg.round_number == round_num), 
            None
        )
        
        interview_rounds.append({
            "round_number": round_num,
            "question": hr_msg.message,
            "candidate_response": candidate_msg.message if candidate_msg else "Нет ответа",
            "hr_feedback": "",  # Убираем дублирующуюся обратную связь
            "score": candidate_msg.response_quality if candidate_msg and candidate_msg.response_quality else 0,
            "improvement_notes": ""  # Убираем повторяющиеся рекомендации
        })
    
    # Расчет средней оценки
    scores = [r["score"] for r in interview_rounds if r["score"] > 0]
    average_score = sum(scores) / len(scores) if scores else 0
    
    return {
        "interview_rounds": interview_rounds,
        "final_assessment": {
            "overall_score": int(average_score * 2),  # Приводим к шкале 1-10
            "strengths": simulation.assessment.strengths if simulation.assessment else ["Не определено"],
            "areas_for_improvement": simulation.assessment.weaknesses if simulation.assessment else ["Не определено"],
            "hiring_recommendation": simulation.assessment.overall_recommendation if simulation.assessment else "Нет данных",
            "detailed_feedback": simulation.hr_assessment if hasattr(simulation, 'hr_assessment') else "Детальная оценка недоступна"
        },
        "summary": {
            "total_rounds": len(interview_rounds),
            "average_score": round(average_score, 1),
            "simulation_duration": "завершена",
            "key_insights": simulation.assessment.weaknesses[:3] if simulation.assessment and simulation.assessment.weaknesses else ["Нет инсайтов"]
        }
    }

# ================== МОНИТОРИНГ ==================

@app.get("/health")
async def health_check():
    """Health check endpoint для мониторинга"""
    try:
        return {
            "status": "healthy",
            "service": "ai-resume-assistant-unified",
            "version": "1.0.0",
            "port": 3000,
            "checks": {
                "auth_system": "ok",
                "templates": "ok",
                "storage": "ok"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "ai-resume-assistant-unified",
            "error": str(e)
        }

# Добавляем маршруты панели мониторинга
add_health_dashboard_routes(app, auth_system.templates)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)