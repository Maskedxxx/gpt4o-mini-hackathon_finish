# domain/user_state.py

from enum import Enum
from typing import Optional
from pydantic import BaseModel


class UserStateEnum(Enum):
    """Состояния пользователя в pipeline"""
    STARTED = "started"
    OAUTH_PENDING = "oauth_pending" 
    TOKEN_RECEIVED = "token_received"
    RESUME_PARSING = "resume_parsing"
    VACANCY_PARSING = "vacancy_parsing"
    GAP_ANALYSIS = "gap_analysis"
    RESUME_REWRITING = "resume_rewriting"
    UPDATING_RESUME = "updating_resume"
    COMPLETED = "completed"
    ERROR = "error"


class UserState(BaseModel):
    """Модель состояния пользователя"""
    user_id: int
    state: UserStateEnum
    payload: Optional[dict] = None  # Дополнительные данные состояния