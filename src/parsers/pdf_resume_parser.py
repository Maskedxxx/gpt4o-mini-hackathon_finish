"""
PDF Resume Parser

Парсит PDF резюме и извлекает структурированную информацию
используя OpenAI API для преобразования в модель ResumeInfo.
"""

import os
import logging
from typing import Optional
from pathlib import Path

import pdfplumber
from openai import OpenAI
from pydantic import ValidationError

from src.models.resume_models import ResumeInfo

logger = logging.getLogger(__name__)


class PDFResumeParser:
    """Парсер PDF резюме с использованием OpenAI structured output"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Инициализация парсера
        
        Args:
            openai_api_key: API ключ OpenAI (если None, берется из переменной окружения)
        """
        self.client = OpenAI(api_key=openai_api_key or os.getenv("OPENAI_API_KEY"))
        self.model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini-2024-07-18")
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Извлекает текст из PDF файла
        
        Args:
            pdf_path: Путь к PDF файлу
            
        Returns:
            Извлеченный текст
            
        Raises:
            FileNotFoundError: Если файл не найден
            Exception: При ошибке извлечения текста
        """
        if not Path(pdf_path).exists():
            raise FileNotFoundError(f"PDF файл не найден: {pdf_path}")
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                if not text.strip():
                    raise Exception("Не удалось извлечь текст из PDF")
                
                return text.strip()
                
        except Exception as e:
            logger.error(f"Ошибка при извлечении текста из PDF {pdf_path}: {e}")
            raise
    
    def parse_text_to_resume(self, text: str) -> ResumeInfo:
        """
        Парсит текст резюме в структурированную модель ResumeInfo
        
        Args:
            text: Текст резюме
            
        Returns:
            Структурированная информация о резюме
            
        Raises:
            ValidationError: При ошибке валидации модели
            Exception: При ошибке API OpenAI
        """
        system_prompt = """
        Ты опытный HR-специалист. Твоя задача - извлечь и структурировать информацию из текста резюме.
        
        Внимательно проанализируй предоставленный текст резюме и извлеки всю доступную информацию.
        
        Требования:
        1. Если информация не найдена, оставь поле пустым (None/[] в зависимости от типа)
        2. Для списков навыков (skill_set) выдели ключевые технические навыки
        3. Для experience заполни все доступные поля (описание, должность, компания, даты)
        4. Для education укажи все образование (основное и дополнительное)
        5. Для языков укажи названия и уровни владения
        6. Тщательно ищи контактную информацию и сайты
        7. Если зарплатные ожидания не указаны, не придумывай их
        8. Опыт работы в total_experience указывай в месяцах
        """
        
        try:
            completion = self.client.beta.chat.completions.parse(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Проанализируй и структурируй это резюме:\n\n{text}"}
                ],
                response_format=ResumeInfo,
                temperature=0.1
            )
            
            if completion.choices[0].message.parsed is None:
                raise Exception("OpenAI не смог распарсить резюме")
            
            return completion.choices[0].message.parsed
            
        except ValidationError as e:
            logger.error(f"Ошибка валидации модели ResumeInfo: {e}")
            raise
        except Exception as e:
            logger.error(f"Ошибка при парсинге текста через OpenAI: {e}")
            raise
    
    def parse_pdf_resume(self, pdf_path: str) -> ResumeInfo:
        """
        Парсит PDF резюме в структурированную модель
        
        Args:
            pdf_path: Путь к PDF файлу резюме
            
        Returns:
            Структурированная информация о резюме
            
        Raises:
            FileNotFoundError: Если файл не найден
            ValidationError: При ошибке валидации модели
            Exception: При других ошибках парсинга
        """
        logger.info(f"Начинаем парсинг PDF резюме: {pdf_path}")
        
        # Извлекаем текст из PDF
        text = self.extract_text_from_pdf(pdf_path)
        logger.info(f"Извлечен текст длиной {len(text)} символов")
        
        # Парсим текст в модель
        resume_info = self.parse_text_to_resume(text)
        logger.info(f"Успешно распарсено резюме для: {resume_info.first_name} {resume_info.last_name}")
        
        return resume_info


def main():
    """Пример использования парсера"""
    parser = PDFResumeParser()
    
    # Пример использования
    pdf_path = input("Введите путь к PDF резюме: ")
    
    try:
        resume = parser.parse_pdf_resume(pdf_path)
        print("\nУспешно распарсено резюме:")
        print(f"Имя: {resume.first_name} {resume.last_name}")
        print(f"Должность: {resume.title}")
        print(f"Опыт: {resume.total_experience} месяцев")
        print(f"Ключевые навыки: {', '.join(resume.skill_set)}")
        print(f"Опыт работы: {len(resume.experience)} записей")
        
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()