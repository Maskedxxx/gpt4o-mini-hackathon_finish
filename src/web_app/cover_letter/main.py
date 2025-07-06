"""
Веб-приложение для генерации сопроводительного письма

Простая веб-форма для загрузки PDF резюме и генерации персонализированного сопроводительного письма.
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
from src.llm_cover_letter.llm_cover_letter_generator import EnhancedLLMCoverLetterGenerator
from src.utils import get_logger

logger = get_logger()

app = FastAPI(title="AI Resume Assistant - Cover Letter")

# Настройка шаблонов
templates = Jinja2Templates(directory="src/web_app/cover_letter/templates")

# Создание экземпляров сервисов
pdf_parser = PDFResumeParser()
vacancy_extractor = VacancyExtractor()
hh_auth_service = HHAuthService()
token_exchanger = HHCodeExchanger()
cover_letter_generator = EnhancedLLMCoverLetterGenerator(validate_quality=False)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Главная страница с формой генерации сопроводительного письма"""
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

@app.post("/generate-cover-letter")
async def generate_cover_letter(
    resume_file: UploadFile = File(...),
    vacancy_url: str = Form(...),
    hh_access_token: str = Form(...),
    hh_refresh_token: str = Form(...)
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
            
            # Получение данных вакансии
            logger.info(f"Получение данных вакансии {vacancy_id}...")
            hh_client = HHApiClient(hh_access_token, hh_refresh_token)
            vacancy_data = await hh_client.request(f'vacancies/{vacancy_id}')
            
            # Парсинг данных вакансии
            parsed_vacancy = vacancy_extractor.extract_vacancy_info(vacancy_data)
            
            # Генерация сопроводительного письма (преобразуем модели в словари)
            logger.info("Генерация сопроводительного письма...")
            resume_dict = parsed_resume.model_dump()
            vacancy_dict = parsed_vacancy.model_dump()
            cover_letter_result = await cover_letter_generator.generate_enhanced_cover_letter(resume_dict, vacancy_dict)
            
            if not cover_letter_result:
                logger.error("Не удалось сгенерировать сопроводительное письмо")
                raise HTTPException(500, "Не удалось сгенерировать сопроводительное письмо")
            
            # Форматирование результатов для веб-отображения
            formatted_result = format_cover_letter_for_web(cover_letter_result)
            
            return JSONResponse({
                "status": "success",
                "cover_letter": formatted_result
            })
            
        finally:
            # Удаляем временный файл
            os.unlink(tmp_file_path)
            
    except Exception as e:
        logger.error(f"Ошибка при генерации сопроводительного письма: {e}")
        raise HTTPException(500, f"Ошибка генерации: {str(e)}")

def extract_vacancy_id(vacancy_url: str) -> str:
    """Извлечение ID вакансии из URL"""
    import re
    pattern = r'https?://(?:www\.)?hh\.ru/vacancy/(\d+)'
    match = re.search(pattern, vacancy_url)
    return match.group(1) if match else None

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

def format_cover_letter_for_web(cover_letter) -> dict:
    """Форматирование результатов сопроводительного письма для веб-отображения"""
    return {
        "company_context": {
            "company_name": cover_letter.company_context.company_name,
            "position_title": cover_letter.subject_line,  # Используем тему как позицию
            "company_size": cover_letter.company_context.company_size,
            "role_type": cover_letter.role_type,
            "key_requirements": [cover_letter.skills_match.relevant_experience]  # Используем как требования
        },
        "skills_match": {
            "matching_skills": cover_letter.skills_match.matched_skills,
            "relevant_achievements": [cover_letter.skills_match.quantified_achievement] if cover_letter.skills_match.quantified_achievement else [],
            "unique_selling_points": [cover_letter.personalization.value_proposition],
            "experience_relevance_score": cover_letter.relevance_score
        },
        "personalization": {
            "tone": "профессиональный",  # Дефолтное значение
            "key_motivations": [cover_letter.personalization.role_motivation],
            "company_research_points": [cover_letter.personalization.company_knowledge] if cover_letter.personalization.company_knowledge else [],
            "customization_level": "высокий" if cover_letter.personalization_score >= 8 else "средний"
        },
        "letter_structure": {
            "opening_hook": cover_letter.opening_hook,
            "value_proposition": cover_letter.personalization.value_proposition,
            "specific_examples": [cover_letter.relevant_experience],  # Используем как примеры
            "company_alignment": cover_letter.company_interest,
            "call_to_action": cover_letter.professional_closing
        },
        "final_letter": assemble_full_letter_text(cover_letter),
        "quality_assessment": {
            "personalization_score": cover_letter.personalization_score,
            "relevance_score": cover_letter.relevance_score,
            "engagement_score": cover_letter.professional_tone_score,  # Используем как аналог
            "overall_quality": "EXCELLENT" if cover_letter.personalization_score >= 8 else "GOOD" if cover_letter.personalization_score >= 6 else "AVERAGE",
            "improvement_suggestions": cover_letter.improvement_suggestions
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)