# src/callback_local_server/server.py
import logging
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse

logger = logging.getLogger("callback_local_server")

app = FastAPI(title = "callback_local_server")

# Сохраняем полученный код
auth_code = None

@app.get("/callback")
async def callback_handler(code: str = Query(None)):
    """Обработчик callback запроса от OAuth2."""
    global auth_code
    
    if code:
        auth_code = code
        logger.info(f"Получен код авторизации: {code}")
        return HTMLResponse("Авторизация успешно завершена. Вы можете закрыть это окно и вернуться в бот.")
    
    logger.error("Код авторизации отсутствует в запросе")
    return HTMLResponse("Ошибка авторизации. Пожалуйста, попробуйте снова.", status_code=400)

@app.get("/api/code")
async def get_auth_code_api():
    """API эндпоинт для получения кода авторизации."""
    if auth_code:
        return JSONResponse({"code": auth_code})
    return JSONResponse({"code": None}, status_code=404)