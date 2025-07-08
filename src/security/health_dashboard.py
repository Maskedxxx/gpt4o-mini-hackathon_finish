import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, Any, List
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.security.openai_control import openai_controller
from src.utils import get_logger

logger = get_logger()


class HealthDashboard:
    """Простая панель мониторинга состояния всех сервисов"""
    
    def __init__(self):
        self.services = {
            "unified_app": {
                "name": "Unified Web App",
                "url": "http://localhost:3000/health",
                "port": 3000
            },
            "gap_analysis": {
                "name": "Gap Analysis",
                "url": "http://localhost:8000/health",
                "port": 8000
            },
            "cover_letter": {
                "name": "Cover Letter",
                "url": "http://localhost:8001/health",
                "port": 8001
            },
            "interview_checklist": {
                "name": "Interview Checklist",
                "url": "http://localhost:8002/health",
                "port": 8002
            },
            "interview_simulation": {
                "name": "Interview Simulation",
                "url": "http://localhost:8003/health",
                "port": 8003
            },
            "oauth_server": {
                "name": "OAuth Server",
                "url": "http://localhost:8080/health",
                "port": 8080
            }
        }
    
    async def check_service_health(self, service_id: str, service_info: Dict[str, Any]) -> Dict[str, Any]:
        """Проверить состояние одного сервиса"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(service_info["url"]) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "service_id": service_id,
                            "name": service_info["name"],
                            "status": "healthy",
                            "port": service_info["port"],
                            "response_time": "< 5s",
                            "details": data.get("checks", {}),
                            "last_check": datetime.now().strftime("%H:%M:%S")
                        }
                    else:
                        return {
                            "service_id": service_id,
                            "name": service_info["name"],
                            "status": "unhealthy",
                            "port": service_info["port"],
                            "response_time": "timeout",
                            "error": f"HTTP {response.status}",
                            "last_check": datetime.now().strftime("%H:%M:%S")
                        }
        except Exception as e:
            return {
                "service_id": service_id,
                "name": service_info["name"],
                "status": "offline",
                "port": service_info["port"],
                "response_time": "timeout",
                "error": str(e),
                "last_check": datetime.now().strftime("%H:%M:%S")
            }
    
    async def get_all_services_status(self) -> Dict[str, Any]:
        """Получить статус всех сервисов"""
        # Проверяем все сервисы параллельно
        tasks = [
            self.check_service_health(service_id, service_info)
            for service_id, service_info in self.services.items()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        services_status = []
        healthy_count = 0
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Ошибка при проверке сервиса: {result}")
                continue
            
            services_status.append(result)
            if result["status"] == "healthy":
                healthy_count += 1
        
        # Получаем статистику OpenAI API
        openai_stats = openai_controller.get_usage_stats()
        
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "overall_status": "healthy" if healthy_count == len(services_status) else "degraded" if healthy_count > 0 else "critical",
            "healthy_services": healthy_count,
            "total_services": len(services_status),
            "services": services_status,
            "openai_stats": openai_stats
        }


# Создаем экземпляр dashboard
health_dashboard = HealthDashboard()


def add_health_dashboard_routes(app: FastAPI, templates: Jinja2Templates):
    """Добавить маршруты панели мониторинга в FastAPI приложение"""
    
    @app.get("/status", response_class=HTMLResponse)
    async def dashboard_page(request: Request):
        """Страница панели мониторинга"""
        status_data = await health_dashboard.get_all_services_status()
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "status_data": status_data
        })
    
    @app.get("/api/status")
    async def api_status():
        """API эндпоинт для получения статуса сервисов"""
        return await health_dashboard.get_all_services_status()