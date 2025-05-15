# usecase/run_pipeline.py

"""Главный оркестратор pipeline"""
from typing import Optional

from domain.dto import Resume, Vacancy, GapReport
from domain.user_state import UserStateEnum
from domain.services import (
    IHHClient, ITokenStorage, IUserStateStorage,
    IGapAnalyzer, IResumeRewriter
)
from loguru import logger


class PipelineOrchestrator:
    """Координатор всех шагов обработки"""
    
    def __init__(
        self,
        hh_client: IHHClient,
        token_storage: ITokenStorage,
        state_storage: IUserStateStorage,
        gap_analyzer: IGapAnalyzer,
        resume_rewriter: IResumeRewriter
    ):
        self.hh_client = hh_client
        self.token_storage = token_storage
        self.state_storage = state_storage
        self.gap_analyzer = gap_analyzer
        self.resume_rewriter = resume_rewriter
    
    async def start_oauth(self, user_id: int) -> str:
        """Начать процесс OAuth авторизации"""
        try:
            # Обновляем состояние
            await self.state_storage.update_state(
                user_id, UserStateEnum.OAUTH_PENDING
            )
            
            # Генерируем URL для авторизации
            auth_url = await self.hh_client.get_auth_url(str(user_id))
            logger.info(f"Generated auth URL for user {user_id}")
            
            return auth_url
            
        except Exception as e:
            logger.error(f"Failed to start OAuth for user {user_id}: {e}")
            await self.state_storage.update_state(
                user_id, UserStateEnum.ERROR, {"error": str(e)}
            )
            raise
    
    async def handle_oauth_callback(self, user_id: int, code: str) -> bool:
        """Обработать OAuth callback"""
        try:
            # Обмениваем код на токены
            token = await self.hh_client.exchange_code(code)
            token.user_id = user_id
            
            # Сохраняем токены
            await self.token_storage.save_token(user_id, token)
            
            # Обновляем состояние
            await self.state_storage.update_state(
                user_id, UserStateEnum.TOKEN_RECEIVED
            )
            
            logger.info(f"Successfully exchanged code for tokens for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to handle OAuth callback for user {user_id}: {e}")
            await self.state_storage.update_state(
                user_id, UserStateEnum.ERROR, {"error": str(e)}
            )
            raise
    
    async def parse_resume(self, user_id: int, resume_url: str) -> Resume:
        """Парсить резюме"""
        try:
            # Обновляем состояние
            await self.state_storage.update_state(
                user_id, UserStateEnum.RESUME_PARSING
            )
            
            # Получаем токен
            token = await self.token_storage.get_token(user_id)
            if not token:
                raise Exception("User token not found")
            
            # Парсим резюме
            resume = await self.hh_client.get_resume(resume_url, token.access_token)
            
            # Сохраняем ID резюме в состоянии
            await self.state_storage.update_state(
                user_id, 
                UserStateEnum.RESUME_PARSING,
                {"resume_id": resume.id}
            )
            
            logger.info(f"Successfully parsed resume {resume.id} for user {user_id}")
            return resume
            
        except Exception as e:
            logger.error(f"Failed to parse resume for user {user_id}: {e}")
            await self.state_storage.update_state(
                user_id, UserStateEnum.ERROR, {"error": str(e)}
            )
            raise
    
    async def parse_vacancy(self, user_id: int, vacancy_url: str) -> Vacancy:
        """Парсить вакансию"""
        try:
            # Обновляем состояние
            await self.state_storage.update_state(
                user_id, UserStateEnum.VACANCY_PARSING
            )
            
            # Парсим вакансию
            vacancy = await self.hh_client.get_vacancy(vacancy_url)
            
            # Сохраняем ID вакансии в состоянии
            state = await self.state_storage.get_state(user_id)
            payload = state.payload or {}
            payload["vacancy_id"] = vacancy.id
            
            await self.state_storage.update_state(
                user_id,
                UserStateEnum.VACANCY_PARSING,
                payload
            )
            
            logger.info(f"Successfully parsed vacancy {vacancy.id} for user {user_id}")
            return vacancy
            
        except Exception as e:
            logger.error(f"Failed to parse vacancy for user {user_id}: {e}")
            await self.state_storage.update_state(
                user_id, UserStateEnum.ERROR, {"error": str(e)}
            )
            raise
    
    async def analyze_gap(self, user_id: int, resume: Resume, vacancy: Vacancy) -> GapReport:
        """Провести gap-анализ"""
        try:
            # Обновляем состояние
            await self.state_storage.update_state(
                user_id, UserStateEnum.GAP_ANALYSIS
            )
            
            # Проводим анализ
            gap_report = await self.gap_analyzer.analyze(resume, vacancy)
            
            logger.info(f"Successfully completed gap analysis for user {user_id}")
            return gap_report
            
        except Exception as e:
            logger.error(f"Failed gap analysis for user {user_id}: {e}")
            await self.state_storage.update_state(
                user_id, UserStateEnum.ERROR, {"error": str(e)}
            )
            raise
    
    async def rewrite_resume(self, user_id: int, resume: Resume, gap_report: GapReport) -> str:
        """Переписать резюме"""
        try:
            # Обновляем состояние
            await self.state_storage.update_state(
                user_id, UserStateEnum.RESUME_REWRITING
            )
            
            # Переписываем резюме
            new_resume_text = await self.resume_rewriter.rewrite(resume, gap_report)
            
            logger.info(f"Successfully rewrote resume for user {user_id}")
            return new_resume_text
            
        except Exception as e:
            logger.error(f"Failed to rewrite resume for user {user_id}: {e}")
            await self.state_storage.update_state(
                user_id, UserStateEnum.ERROR, {"error": str(e)}
            )
            raise
    
    async def update_resume(self, user_id: int, resume_id: str, new_text: str) -> bool:
        """Обновить резюме на HH"""
        try:
            # Обновляем состояние
            await self.state_storage.update_state(
                user_id, UserStateEnum.UPDATING_RESUME
            )
            
            # Получаем токен
            token = await self.token_storage.get_token(user_id)
            if not token:
                raise Exception("User token not found")
            
            # Обновляем резюме
            success = await self.hh_client.update_resume(resume_id, new_text, token.access_token)
            
            if success:
                # Обновляем состояние на завершённое
                await self.state_storage.update_state(
                    user_id, UserStateEnum.COMPLETED
                )
                logger.info(f"Successfully updated resume {resume_id} for user {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update resume for user {user_id}: {e}")
            await self.state_storage.update_state(
                user_id, UserStateEnum.ERROR, {"error": str(e)}
            )
            raise
    
    async def run_full_pipeline(
        self, 
        user_id: int, 
        resume_url: str, 
        vacancy_url: str
    ) -> dict:
        """Запустить полный pipeline от начала до конца"""
        try:
            # 1. Парсим резюме
            resume = await self.parse_resume(user_id, resume_url)
            
            # 2. Парсим вакансию
            vacancy = await self.parse_vacancy(user_id, vacancy_url)
            
            # 3. Проводим gap-анализ
            gap_report = await self.analyze_gap(user_id, resume, vacancy)
            
            # 4. Переписываем резюме
            new_resume_text = await self.rewrite_resume(user_id, resume, gap_report)
            
            # 5. Обновляем резюме на HH
            success = await self.update_resume(user_id, resume.id, new_resume_text)
            
            return {
                "success": success,
                "resume_id": resume.id,
                "vacancy_id": vacancy.id,
                "gap_report": gap_report.model_dump(),
                "new_resume_text": new_resume_text
            }
            
        except Exception as e:
            logger.error(f"Pipeline failed for user {user_id}: {e}")
            raise