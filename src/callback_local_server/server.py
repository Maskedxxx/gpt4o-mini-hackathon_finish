# src/callback_local_server/server.py
import logging
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse

from src.utils import get_logger
logger = get_logger()
app = FastAPI(title = "callback_local_server")

# Сохраняем полученный код с timestamp
auth_code = None
auth_code_timestamp = None

@app.get("/callback")
async def callback_handler(code: str = Query(None)):
    """Обработчик callback запроса от OAuth2."""
    global auth_code, auth_code_timestamp
    
    if code:
        import time
        auth_code = code
        auth_code_timestamp = time.time()
        logger.info(f"Получен код авторизации: {code}")
        return HTMLResponse("Авторизация успешно завершена. Вы можете закрыть это окно и вернуться в приложение.")
    
    logger.error("Код авторизации отсутствует в запросе")
    return HTMLResponse("Ошибка авторизации. Пожалуйста, попробуйте снова.", status_code=400)

@app.get("/api/code")
async def get_auth_code_api():
    """API эндпоинт для получения кода авторизации."""
    import time
    
    if auth_code:
        # Проверяем что код не старше 10 минут
        if auth_code_timestamp and (time.time() - auth_code_timestamp) < 600:
            return JSONResponse({"code": auth_code})
        else:
            # Код устарел, очищаем его
            global auth_code, auth_code_timestamp
            auth_code = None
            auth_code_timestamp = None
            logger.info("Код авторизации устарел и был очищен")
    
    return JSONResponse({"code": None}, status_code=404)

@app.post("/api/reset_code")
async def reset_auth_code_api():
    """API эндпоинт для сброса кода авторизации."""
    global auth_code, auth_code_timestamp
    old_code = auth_code
    auth_code = None
    auth_code_timestamp = None
    logger.info(f"Код авторизации сброшен: {old_code}")
    return JSONResponse({"status": "success"})