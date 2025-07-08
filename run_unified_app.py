#!/usr/bin/env python3
"""
Запуск объединенного веб-приложения AI Resume Assistant

Это объединенное приложение включает все 4 функции:
- GAP-анализ резюме
- Генерация сопроводительного письма  
- Чек-лист подготовки к интервью
- Симуляция интервью

URL: http://localhost:3000
"""

import uvicorn
import sys
from pathlib import Path

# Добавляем корневую директорию в sys.path
root_dir = Path(__file__).parent
sys.path.append(str(root_dir))

# Импортируем приложение
from src.web_app.unified_app.main import app

if __name__ == "__main__":
    print("🚀 Запуск объединенного AI Resume Assistant...")
    print("📋 Включены все 4 функции:")
    print("  • GAP-анализ резюме")
    print("  • Генерация сопроводительного письма")
    print("  • Чек-лист подготовки к интервью")
    print("  • Симуляция интервью")
    print()
    print("🌐 Приложение будет доступно по адресу: http://localhost:3000")
    print("🔗 Не забудьте запустить OAuth сервер: python -m src.callback_local_server.main")
    print()
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=3000,
        reload=False,
        log_level="info"
    )