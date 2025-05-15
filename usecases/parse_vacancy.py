# usecases/parse_vacancy.py

"""Use case для парсинга вакансии"""
from domain.dto import Vacancy
from domain.services import IHHClient
from loguru import logger


class ParseVacancyUseCase:
    """Сценарий получения вакансии"""
    
    def __init__(self, hh_client: IHHClient):
        self.hh_client = hh_client
    
    async def execute(self, vacancy_url: str) -> Vacancy:
        """Получить вакансию по URL"""
        try:
            # Получаем вакансию (токен не нужен)
            vacancy = await self.hh_client.get_vacancy(vacancy_url)
            logger.info(f"Successfully parsed vacancy {vacancy.id}")
            
            return vacancy
            
        except Exception as e:
            logger.error(f"Failed to parse vacancy: {e}")
            raise