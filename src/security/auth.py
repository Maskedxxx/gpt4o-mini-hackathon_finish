import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Request, HTTPException, status, Depends, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class SimpleAuthConfig:
    """Конфигурация простой авторизации для демо"""
    
    def __init__(self):
        self.demo_password = os.getenv("DEMO_PASSWORD", "demo2025")
        self.session_timeout_hours = int(os.getenv("SESSION_TIMEOUT_HOURS", "24"))
        self.cookie_name = "auth_session"
        self.secret_key = os.getenv("AUTH_SECRET_KEY", secrets.token_hex(32))


class SessionManager:
    """Менеджер сессий для простой авторизации"""
    
    def __init__(self, config: SimpleAuthConfig):
        self.config = config
        self.active_sessions = {}
    
    def create_session(self) -> str:
        """Создать новую сессию"""
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=self.config.session_timeout_hours)
        
        self.active_sessions[session_id] = {
            "created_at": datetime.now(),
            "expires_at": expires_at,
            "last_accessed": datetime.now()
        }
        
        return session_id
    
    def validate_session(self, session_id: str) -> bool:
        """Проверить валидность сессии"""
        if not session_id or session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        now = datetime.now()
        
        if now > session["expires_at"]:
            del self.active_sessions[session_id]
            return False
        
        session["last_accessed"] = now
        return True
    
    def delete_session(self, session_id: str):
        """Удалить сессию"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
    
    def cleanup_expired_sessions(self):
        """Очистка истёкших сессий"""
        now = datetime.now()
        expired_sessions = [
            sid for sid, session in self.active_sessions.items()
            if now > session["expires_at"]
        ]
        
        for sid in expired_sessions:
            del self.active_sessions[sid]


class SimpleAuthMiddleware(BaseHTTPMiddleware):
    """Middleware для простой авторизации"""
    
    def __init__(self, app, config: SimpleAuthConfig, session_manager: SessionManager, templates: Jinja2Templates):
        super().__init__(app)
        self.config = config
        self.session_manager = session_manager
        self.templates = templates
        
        self.excluded_paths = {
            "/login",
            "/logout",
            "/health",
            "/static",
            "/favicon.ico"
        }
    
    async def dispatch(self, request: Request, call_next):
        """Обработка запроса с проверкой авторизации"""
        path = request.url.path
        
        if self._is_excluded_path(path):
            return await call_next(request)
        
        session_id = request.cookies.get(self.config.cookie_name)
        
        if not self.session_manager.validate_session(session_id):
            if path == "/login":
                return await call_next(request)
            
            redirect_url = f"/login?redirect={path}"
            return RedirectResponse(url=redirect_url, status_code=302)
        
        return await call_next(request)
    
    def _is_excluded_path(self, path: str) -> bool:
        """Проверить, нужно ли исключить путь из авторизации"""
        return any(path.startswith(excluded) for excluded in self.excluded_paths)


class SimpleAuth:
    """Основной класс для простой авторизации"""
    
    def __init__(self, templates_dir: str = "templates"):
        self.config = SimpleAuthConfig()
        self.session_manager = SessionManager(self.config)
        self.templates = Jinja2Templates(directory=templates_dir)
    
    def get_middleware(self):
        """Получить middleware для FastAPI приложения"""
        return SimpleAuthMiddleware(
            app=None,
            config=self.config,
            session_manager=self.session_manager,
            templates=self.templates
        )
    
    async def login_page(self, request: Request, error: Optional[str] = None):
        """Страница логина"""
        redirect_url = request.query_params.get("redirect", "/")
        
        return self.templates.TemplateResponse("login.html", {
            "request": request,
            "error": error,
            "redirect_url": redirect_url
        })
    
    async def login_post(self, request: Request, password: str = Form(...)):
        """Обработка POST запроса логина"""
        redirect_url = request.query_params.get("redirect", "/")
        
        if password != self.config.demo_password:
            return await self.login_page(request, "Неверный пароль")
        
        session_id = self.session_manager.create_session()
        
        response = RedirectResponse(url=redirect_url, status_code=302)
        response.set_cookie(
            key=self.config.cookie_name,
            value=session_id,
            max_age=self.config.session_timeout_hours * 3600,
            httponly=True,
            secure=False,  # В продакшене должно быть True с HTTPS
            samesite="lax"
        )
        
        return response
    
    async def logout(self, request: Request):
        """Выход из системы"""
        session_id = request.cookies.get(self.config.cookie_name)
        if session_id:
            self.session_manager.delete_session(session_id)
        
        response = RedirectResponse(url="/login", status_code=302)
        response.delete_cookie(self.config.cookie_name)
        
        return response
    
    def require_auth(self, request: Request):
        """Dependency для проверки авторизации в эндпоинтах"""
        session_id = request.cookies.get(self.config.cookie_name)
        
        if not self.session_manager.validate_session(session_id):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Требуется авторизация"
            )
        
        return True
    
    def cleanup_sessions(self):
        """Очистка истёкших сессий"""
        self.session_manager.cleanup_expired_sessions()


def create_auth_instance(templates_dir: str = "templates") -> SimpleAuth:
    """Фабрика для создания экземпляра авторизации"""
    return SimpleAuth(templates_dir)