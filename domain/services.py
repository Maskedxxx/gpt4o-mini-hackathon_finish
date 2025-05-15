# domain/services.py

from abc import ABC, abstractmethod
from typing import Optional
from domain.dto import Resume, Vacancy, GapReport, UserToken
from domain.user_state import UserState, UserStateEnum


class IHHClient(ABC):
    """Интерфейс для работы с HH API"""
    
    @abstractmethod
    async def get_auth_url(self, state: str) -> str:
        """Получить URL для OAuth авторизации"""
        pass
    
    @abstractmethod
    async def exchange_code(self, code: str) -> UserToken:
        """Обменять authorization code на токены"""
        pass
    
    @abstractmethod
    async def get_resume(self, resume_id: str, access_token: str) -> Resume:
        """Получить резюме по ID"""
        pass
    
    @abstractmethod
    async def get_vacancy(self, vacancy_id: str) -> Vacancy:
        """Получить вакансию по ID"""
        pass
    
    @abstractmethod
    async def update_resume(self, resume_id: str, new_text: str, access_token: str) -> bool:
        """Обновить резюме"""
        pass


class ILLMAgent(ABC):
    """Базовый интерфейс для LLM агентов"""
    
    @abstractmethod
    async def process(self, *args, **kwargs) -> dict:
        """Обработать данные"""
        pass


class IGapAnalyzer(ILLMAgent):
    """Интерфейс для gap-анализа"""
    
    @abstractmethod
    async def analyze(self, resume: Resume, vacancy: Vacancy) -> GapReport:
        """Анализировать разрыв между резюме и вакансией"""
        pass


class IResumeRewriter(ILLMAgent):
    """Интерфейс для перезаписи резюме"""
    
    @abstractmethod
    async def rewrite(self, resume: Resume, gap_report: GapReport) -> str:
        """Переписать резюме на основе gap-анализа"""
        pass


class ITokenStorage(ABC):
    """Интерфейс для хранения токенов"""
    
    @abstractmethod
    async def save_token(self, user_id: int, token: UserToken) -> None:
        """Сохранить токены пользователя"""
        pass
    
    @abstractmethod
    async def get_token(self, user_id: int) -> Optional[UserToken]:
        """Получить токены пользователя"""
        pass
    
    @abstractmethod
    async def refresh_token(self, user_id: int) -> Optional[UserToken]:
        """Обновить токены"""
        pass


class IUserStateStorage(ABC):
    """Интерфейс для хранения состояния пользователя"""
    
    @abstractmethod
    async def save_state(self, user_state: UserState) -> None:
        """Сохранить состояние"""
        pass
    
    @abstractmethod
    async def get_state(self, user_id: int) -> Optional[UserState]:
        """Получить состояние"""
        pass
    
    @abstractmethod
    async def update_state(self, user_id: int, state: UserStateEnum, payload: dict = None) -> None:
        """Обновить состояние"""
        pass