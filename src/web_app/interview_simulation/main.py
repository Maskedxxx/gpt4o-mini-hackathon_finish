"""
Веб-приложение для симуляции интервью

Интерактивная веб-форма для настройки и проведения симуляции интервью
с персонализированными настройками и генерацией PDF отчета.
"""

import os
import tempfile
from pathlib import Path
from fastapi import FastAPI, Form, File, UploadFile, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
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
from src.llm_interview_simulation.llm_interview_simulator import ProfessionalInterviewSimulator
from src.utils import get_logger

logger = get_logger()

app = FastAPI(title="AI Resume Assistant - Interview Simulation")

# Настройка шаблонов
templates = Jinja2Templates(directory="src/web_app/interview_simulation/templates")

# Создание экземпляров сервисов
pdf_parser = PDFResumeParser()
vacancy_extractor = VacancyExtractor()
hh_auth_service = HHAuthService()
token_exchanger = HHCodeExchanger()
interview_simulator = ProfessionalInterviewSimulator()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Главная страница с формой настройки симуляции интервью"""
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

@app.post("/start-simulation")
async def start_interview_simulation(
    resume_file: UploadFile = File(...),
    vacancy_url: str = Form(...),
    hh_access_token: str = Form(...),
    hh_refresh_token: str = Form(...),
    # Настройки симуляции
    target_rounds: int = Form(5, ge=3, le=7),
    difficulty_level: str = Form("medium"),
    hr_persona: str = Form("professional"),
    focus_areas: Optional[str] = Form(None),  # JSON строка с массивом
    include_behavioral: bool = Form(True),
    include_technical: bool = Form(True),
    temperature: float = Form(0.7, ge=0.1, le=1.0)
):
    """Запуск симуляции интервью с настройками"""
    
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
            logger.info(f"Тип parsed_resume: {type(parsed_resume)}")
            logger.info(f"Содержимое parsed_resume: {parsed_resume}")
            
            # Извлечение ID вакансии из URL
            vacancy_id = extract_vacancy_id(vacancy_url)
            if not vacancy_id:
                raise HTTPException(400, "Некорректная ссылка на вакансию")
            
            # Получение данных вакансии
            logger.info(f"Получение данных вакансии {vacancy_id}...")
            hh_client = HHApiClient(hh_access_token, hh_refresh_token)
            vacancy_data = await hh_client.request(f'vacancies/{vacancy_id}')
            logger.info(f"Тип vacancy_data: {type(vacancy_data)}")
            
            # Парсинг данных вакансии
            parsed_vacancy = vacancy_extractor.extract_vacancy_info(vacancy_data)
            logger.info(f"Тип parsed_vacancy: {type(parsed_vacancy)}")
            
            # Проверяем, что парсинг прошел успешно
            if parsed_vacancy is None:
                raise HTTPException(400, "Не удалось распарсить данные вакансии")
            
            # Подготовка настроек симуляции
            simulation_config = prepare_simulation_config(
                target_rounds=target_rounds,
                difficulty_level=difficulty_level,
                hr_persona=hr_persona,
                focus_areas=focus_areas,
                include_behavioral=include_behavioral,
                include_technical=include_technical,
                temperature=temperature
            )
            
            # Запуск симуляции
            logger.info("Запуск симуляции интервью...")
            
            # Преобразуем в словари с проверкой типов
            if hasattr(parsed_resume, 'model_dump'):
                resume_dict = parsed_resume.model_dump()
            elif isinstance(parsed_resume, dict):
                resume_dict = parsed_resume
            else:
                resume_dict = dict(parsed_resume) if parsed_resume else {}
                
            if hasattr(parsed_vacancy, 'model_dump'):
                vacancy_dict = parsed_vacancy.model_dump()
            elif isinstance(parsed_vacancy, dict):
                vacancy_dict = parsed_vacancy
            else:
                vacancy_dict = dict(parsed_vacancy) if parsed_vacancy else {}
            
            
            # Возвращаем идентификатор для отслеживания прогресса
            try:
                simulation_id = f"sim_{hash(str(resume_dict) + str(vacancy_dict))}"
                logger.info(f"Создан simulation_id: {simulation_id}")
            except Exception as e:
                logger.error(f"Ошибка создания simulation_id: {e}")
                simulation_id = f"sim_{hash(str(type(resume_dict)) + str(type(vacancy_dict)))}"
            
            # Запускаем симуляцию в фоне
            import asyncio
            asyncio.create_task(run_simulation_background(
                simulation_id, resume_dict, vacancy_dict, simulation_config
            ))
            
            return JSONResponse({
                "status": "started",
                "simulation_id": simulation_id,
                "config": simulation_config
            })
            
        finally:
            # Удаляем временный файл
            os.unlink(tmp_file_path)
            
    except Exception as e:
        logger.error(f"Ошибка при запуске симуляции: {e}")
        raise HTTPException(500, f"Ошибка симуляции: {str(e)}")

@app.get("/simulation-progress/{simulation_id}")
async def get_simulation_progress(simulation_id: str):
    """Получение прогресса симуляции"""
    # Проверяем статус из временного хранилища
    progress = simulation_progress_storage.get(simulation_id, {})
    return JSONResponse(progress)

@app.get("/download-report/{simulation_id}")
async def download_report(simulation_id: str):
    """Скачивание PDF отчета симуляции"""
    try:
        # Проверяем готовность отчета
        report_path = f"/tmp/interview_report_{simulation_id}.pdf"
        if not os.path.exists(report_path):
            raise HTTPException(404, "Отчет не найден или еще не готов")
        
        # Определяем имя файла для скачивания
        filename = f"Interview_Simulation_Report_{simulation_id[:8]}.pdf"
        
        return FileResponse(
            path=report_path,
            filename=filename,
            media_type='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Ошибка при скачивании отчета: {e}")
        raise HTTPException(500, f"Ошибка скачивания: {str(e)}")

# Временное хранилище для прогресса симуляций (в продакшене использовать Redis)
simulation_progress_storage = {}

async def run_simulation_background(simulation_id: str, resume_dict: dict, vacancy_dict: dict, config: dict):
    """Фоновое выполнение симуляции интервью"""
    try:
        
        
        # Обновляем прогресс
        simulation_progress_storage[simulation_id] = {
            "status": "analyzing",
            "progress": 10,
            "message": "Анализ профиля кандидата..."
        }
        
        # Создаем прогресс-колбэк
        async def progress_callback(current_round: int, total_rounds: int):
            progress = int((current_round / total_rounds) * 80)  # 80% для симуляции
            simulation_progress_storage[simulation_id] = {
                "status": "simulating",
                "progress": 10 + progress,
                "message": f"Раунд {current_round} из {total_rounds}..."
            }
        
        # Устанавливаем пользовательские настройки
        interview_simulator.set_custom_config(config)
        
        # Запускаем симуляцию
        simulation_result = await interview_simulator.simulate_interview(
            resume_dict, vacancy_dict, progress_callback
        )
        
        # Проверяем результат симуляции
        if simulation_result is None:
            raise Exception("Симуляция вернула пустой результат")
        
        simulation_progress_storage[simulation_id] = {
            "status": "generating_pdf",
            "progress": 90,
            "message": "Генерация PDF отчета..."
        }
        
        # Генерируем PDF отчет
        from src.llm_interview_simulation.pdf_generator import ProfessionalInterviewPDFGenerator
        pdf_generator = ProfessionalInterviewPDFGenerator()
        
        report_path = f"/tmp/interview_report_{simulation_id}.pdf"
        pdf_buffer = pdf_generator.generate_pdf(simulation_result)
        
        # Сохраняем PDF в файл
        if pdf_buffer:
            with open(report_path, 'wb') as f:
                f.write(pdf_buffer.getvalue())
        else:
            raise Exception("Не удалось сгенерировать PDF отчет")
        
        # Завершаем
        simulation_progress_storage[simulation_id] = {
            "status": "completed",
            "progress": 100,
            "message": "Симуляция завершена!",
            "report_ready": True,
            "simulation_summary": format_simulation_summary(simulation_result)
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
    pattern = r'https?://(?:www\.)?hh\.ru/vacancy/(\d+)'
    match = re.search(pattern, vacancy_url)
    return match.group(1) if match else None

def prepare_simulation_config(
    target_rounds: int,
    difficulty_level: str,
    hr_persona: str,
    focus_areas: Optional[str],
    include_behavioral: bool,
    include_technical: bool,
    temperature: float
) -> dict:
    """Подготовка конфигурации симуляции"""
    
    # Парсинг областей фокуса
    focus_areas_list = []
    if focus_areas:
        import json
        try:
            focus_areas_list = json.loads(focus_areas)
        except json.JSONDecodeError:
            focus_areas_list = []
    
    return {
        "target_rounds": target_rounds,
        "difficulty_level": difficulty_level,
        "hr_persona": hr_persona,
        "focus_areas": focus_areas_list,
        "include_behavioral": include_behavioral,
        "include_technical": include_technical,
        "temperature": temperature
    }

def format_simulation_summary(simulation_result) -> dict:
    """Форматирование краткого резюме симуляции"""
    try:
        assessment = simulation_result.assessment
        return {
            "overall_recommendation": assessment.overall_recommendation,
            "total_rounds": len(simulation_result.dialog_messages) // 2,
            "average_score": sum(msg.response_quality for msg in simulation_result.dialog_messages 
                               if hasattr(msg, 'response_quality') and msg.response_quality) / 
                           max(1, len([msg for msg in simulation_result.dialog_messages 
                                     if hasattr(msg, 'response_quality') and msg.response_quality])),
            "top_competencies": [comp.area.value for comp in assessment.competency_scores[:3]],
            "red_flags_count": len(assessment.red_flags) if hasattr(assessment, 'red_flags') else 0
        }
    except Exception as e:
        logger.error(f"Ошибка форматирования резюме: {e}")
        return {
            "overall_recommendation": "Не определено",
            "total_rounds": 0,
            "average_score": 0,
            "top_competencies": [],
            "red_flags_count": 0
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)