# http_adapter/oauth_callback_handler.py

"""OAuth callback обработчик"""
from aiohttp import web
from urllib.parse import parse_qs

from domain.services import ITokenStorage, IUserStateStorage, IHHClient
from usecases.run_pipeline import PipelineOrchestrator
from loguru import logger


class OAuthCallbackHandler:
    """Обработчик OAuth callback от HH"""
    
    def __init__(self, pipeline: PipelineOrchestrator):
        self.pipeline = pipeline
    
    async def handle_callback(self, request: web.Request) -> web.Response:
        """Обработать OAuth callback"""
        try:
            # Получаем параметры из query string
            query = parse_qs(request.query_string)
            
            code = query.get('code', [None])[0]
            state = query.get('state', [None])[0]  # user_id
            error = query.get('error', [None])[0]
            
            if error:
                logger.error(f"OAuth error: {error}")
                return web.Response(
                    text=f"Ошибка авторизации: {error}",
                    status=400
                )
            
            if not code or not state:
                return web.Response(
                    text="Отсутствуют обязательные параметры",
                    status=400
                )
            
            # state содержит user_id
            user_id = int(state)
            
            # Обрабатываем callback
            success = await self.pipeline.handle_oauth_callback(user_id, code)
            
            if success:
                return web.Response(
                    text="Авторизация успешна! Вернитесь в бот и отправьте ссылку на резюме.",
                    status=200
                )
            else:
                return web.Response(
                    text="Ошибка при обработке авторизации",
                    status=500
                )
                
        except Exception as e:
            logger.error(f"OAuth callback error: {e}")
            return web.Response(
                text=f"Внутренняя ошибка: {str(e)}",
                status=500
            )


async def start_webhook_server(handler: OAuthCallbackHandler, host: str, port: int):
    """Запустить веб-сервер для обработки callback"""
    app = web.Application()
    app.router.add_get('/callback', handler.handle_callback)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, host, port)
    await site.start()
    
    logger.info(f"OAuth callback server started on {host}:{port}")
    
    return runner