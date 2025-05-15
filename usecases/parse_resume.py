# usecases/parse_resume.py

"""Use case для парсинга резюме"""
from domain.dto import Resume, UserToken
from domain.services import IHHClient, ITokenStorage
from loguru import logger


class ParseResumeUseCase:
    """Сценарий получения резюме"""
    
    def __init__(self, hh_client: IHHClient, token_storage: ITokenStorage):
        self.hh_client = hh_client
        self.token_storage = token_storage
    
    async def execute(self, user_id: int, resume_url: str) -> Resume:
        """Получить резюме по URL"""
        try:
            # Получаем токен пользователя
            token = await self.token_storage.get_token(user_id)
            if not token:
                raise Exception("User token not found")
            
            # Получаем резюме
            resume = await self.hh_client.get_resume(resume_url, token.access_token)
            logger.info(f"Successfully parsed resume {resume.id} for user {user_id}")
            
            return resume
            
        except Exception as e:
            logger.error(f"Failed to parse resume for user {user_id}: {e}")
            raise