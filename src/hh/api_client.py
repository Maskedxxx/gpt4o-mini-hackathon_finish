# src/hh/api_client.py
import logging
import aiohttp
from pathlib import Path
from typing import Dict, Any, Optional

# Настройка логирования
log_dir = Path("LOGS")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "hh_api_client.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("hh_api_client")


class HHApiClient:
    """Клиент для работы с API HeadHunter."""
    
    def __init__(self, access_token: str, refresh_token: str):
        """Инициализация клиента API."""
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.base_url = "https://api.hh.ru/"
        
        # Импортируем здесь, чтобы избежать циклических импортов
        from src.hh.token_refresher import HHTokenRefresher
        self.token_refresher = HHTokenRefresher(refresh_token)
    
    async def request(self, endpoint: str, method: str = 'GET', data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Выполнение запроса к API с автоматическим обновлением токена."""
        if not self.access_token:
            raise ValueError("Отсутствует access_token")

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'User-Agent': 'ResumeBot/1.0'
        }
        url = f'{self.base_url}{endpoint}'
        
        async with aiohttp.ClientSession() as session:
            # Выбор HTTP метода
            if method == 'GET':
                request_func = session.get
            elif method == 'POST':
                request_func = session.post
            elif method == 'PUT':
                request_func = session.put
            elif method == 'DELETE':
                request_func = session.delete
            else:
                raise ValueError(f"Неподдерживаемый HTTP метод: {method}")
            
            # Выполнение запроса
            async with request_func(url, headers=headers, params=params, json=data) as response:
                logger.info(f"Запрос: {method} {url}, Статус: {response.status}")
                
                # Обработка истекшего токена
                if response.status == 401:
                    logger.info("Токен истёк, выполняется обновление")
                    tokens = await self.token_refresher.refresh()
                    self.access_token = tokens.get('access_token')
                    self.refresh_token = tokens.get('refresh_token')
                    return await self.request(endpoint, method, data, params)
                
                # Проверка на успешный ответ
                if response.status >= 400:
                    error_text = await response.text()
                    logger.error(f"Ошибка API: {response.status}, {error_text}")
                    raise Exception(f"Ошибка API {response.status}: {error_text}")
                
                # Обработка успешных ответов без тела
                if response.status == 204:
                    return {}
                
                # Парсинг JSON ответа
                try:
                    return await response.json()
                except Exception:
                    logger.info("Получен пустой или невалидный JSON")
                    return {}