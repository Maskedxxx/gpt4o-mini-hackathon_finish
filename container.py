# container.py

"""Dependency Injection контейнер"""
from infra.hh_client import HHClient
from infra.token_storage import TokenStorage
from infra.user_state_storage import UserStateStorage
from llm.gap_analyzer import GapAnalyzer
from llm.resume_rewriter import ResumeRewriter
from usecases.run_pipeline import PipelineOrchestrator
from http_adapter.oauth_callback_handler import OAuthCallbackHandler


class Container:
    """DI контейнер для всех зависимостей"""
    
    def __init__(self):
        # Инфраструктура
        self.hh_client = HHClient()
        self.token_storage = TokenStorage()
        self.state_storage = UserStateStorage()
        
        # LLM агенты
        self.gap_analyzer = GapAnalyzer()
        self.resume_rewriter = ResumeRewriter()
        
        # Оркестратор
        self.pipeline = PipelineOrchestrator(
            hh_client=self.hh_client,
            token_storage=self.token_storage,
            state_storage=self.state_storage,
            gap_analyzer=self.gap_analyzer,
            resume_rewriter=self.resume_rewriter
        )
        
        # HTTP обработчики
        self.oauth_handler = OAuthCallbackHandler(self.pipeline)


# Глобальный экземпляр контейнера
container = Container()