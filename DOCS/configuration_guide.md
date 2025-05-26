# ⚙️ Конфигурация системы

Подробное руководство по настройке всех компонентов AI Resume Assistant Bot.

## 📋 Общие принципы конфигурации

Система использует **переменные окружения** для всех настроек:
- ✅ Безопасность секретных данных
- ✅ Гибкость развертывания
- ✅ Простота изменения без пересборки
- ✅ Поддержка разных окружений (dev/staging/prod)

## 📁 Структура конфигурации

### Файлы конфигурации

```
├── .env                    # Основные переменные окружения
├── .env.example           # Пример конфигурации
├── src/config.py          # Базовые настройки
├── src/*/config.py        # Специфичные настройки модулей
└── docs/CONFIGURATION.md  # Эта документация
```

### Иерархия настроек

```python
BaseAppSettings              # Базовые настройки
├── TelegramBotSettings     # Настройки Telegram бота
├── HHSettings              # Настройки HeadHunter API
├── OpenAIConfig            # Настройки OpenAI (для всех LLM сервисов)
└── CallbackServerSettings  # Настройки OAuth сервера
```

## 🔐 Обязательные параметры

### 1. Telegram Bot

```env
# Токен Telegram бота (обязательно)
TG_BOT_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Как получить:
# 1. Найдите @BotFather в Telegram
# 2. Создайте нового бота: /newbot
# 3. Скопируйте полученный токен
```

### 2. OpenAI API

```env
# API ключ OpenAI (обязательно)
OPENAI_API_KEY=sk-proj-ABCdefghijklmnopqrstuvwxyz123456789

# Модель для использования (обязательно)
OPENAI_MODEL_NAME=gpt-4

# Альтернативные модели:
# OPENAI_MODEL_NAME=gpt-4-turbo
# OPENAI_MODEL_NAME=gpt-3.5-turbo (дешевле, но менее качественно)

# Как получить:
# 1. Зарегистрируйтесь на platform.openai.com
# 2. Создайте API ключ в разделе "API Keys"
# 3. Убедитесь, что у вас есть кредиты на аккаунте
```

### 3. HeadHunter API

```env
# ID приложения HH.ru (обязательно)
HH_CLIENT_ID=your_client_id

# Секретный ключ приложения HH.ru (обязательно)
HH_CLIENT_SECRET=your_client_secret

# URI для OAuth callback (обязательно)
HH_REDIRECT_URI=http://localhost:8080/callback

# Как получить:
# 1. Зарегистрируйтесь на dev.hh.ru
# 2. Создайте новое приложение
# 3. Укажите redirect_uri: http://localhost:8080/callback
# 4. Получите client_id и client_secret
```

### 4. Callback Server

```env
# Хост для OAuth сервера (обязательно)
CALLBACK_LOCAL_HOST=0.0.0.0

# Порт для OAuth сервера (обязательно)
CALLBACK_LOCAL_PORT=8080

# Примечание: порт должен совпадать с HH_REDIRECT_URI
```

## 🎨 Опциональные параметры

### 1. Базовые настройки приложения

```env
# Название приложения (опционально)
APP_NAME="Resume Bot"

# Режим отладки (опционально)
DEBUG=false

# Возможные значения: true, false
# В режиме отладки больше логов, подробные ошибки
```

### 2. Настройки шрифтов для PDF

```env
# Путь к шрифтам DejaVu (опционально)
FONTS_PATH=/path/to/dejavu-fonts

# Автоматический поиск в стандартных местах:
# - /usr/share/fonts/truetype/dejavu (Linux)
# - /System/Library/Fonts (macOS)
# - ./fonts/dejavu-sans (локальная папка)
```

### 3. Расширенные настройки OpenAI

```env
# Температура для генерации (опционально)
OPENAI_TEMPERATURE=0.7

# Максимальное количество токенов (опционально)
OPENAI_MAX_TOKENS=2000

# Таймаут запросов в секундах (опционально)
OPENAI_TIMEOUT=60

# Количество попыток при ошибках (опционально)
OPENAI_MAX_RETRIES=3
```

### 4. Настройки логирования

```env
# Уровень логирования (опционально)
LOG_LEVEL=INFO

# Возможные значения: DEBUG, INFO, WARNING, ERROR, CRITICAL

# Путь к папке логов (опционально)
LOGS_PATH=./LOGS

# Ротация логов (опционально)
LOG_ROTATION=true
LOG_MAX_BYTES=10485760  # 10MB
LOG_BACKUP_COUNT=5
```

## 📄 Примеры конфигурации

### Разработка (Development)

```env
# .env для разработки
APP_NAME="Resume Bot Dev"
DEBUG=true
LOG_LEVEL=DEBUG

# Telegram
TG_BOT_BOT_TOKEN=123456789:YOUR_DEV_BOT_TOKEN

# OpenAI (используем более дешевую модель)
OPENAI_API_KEY=sk-proj-YOUR_DEV_API_KEY
OPENAI_MODEL_NAME=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.8

# HeadHunter
HH_CLIENT_ID=YOUR_DEV_CLIENT_ID
HH_CLIENT_SECRET=YOUR_DEV_CLIENT_SECRET
HH_REDIRECT_URI=http://localhost:8080/callback

# Callback Server
CALLBACK_LOCAL_HOST=127.0.0.1
CALLBACK_LOCAL_PORT=8080

# Fonts
FONTS_PATH=./fonts/dejavu-sans
```

### Тестирование (Staging)

```env
# .env для тестирования
APP_NAME="Resume Bot Staging"
DEBUG=false
LOG_LEVEL=INFO

# Telegram
TG_BOT_BOT_TOKEN=123456789:YOUR_STAGING_BOT_TOKEN

# OpenAI
OPENAI_API_KEY=sk-proj-YOUR_STAGING_API_KEY
OPENAI_MODEL_NAME=gpt-4
OPENAI_TEMPERATURE=0.7

# HeadHunter
HH_CLIENT_ID=YOUR_STAGING_CLIENT_ID
HH_CLIENT_SECRET=YOUR_STAGING_CLIENT_SECRET
HH_REDIRECT_URI=https://staging.yourdomain.com/callback

# Callback Server
CALLBACK_LOCAL_HOST=0.0.0.0
CALLBACK_LOCAL_PORT=8080

# Fonts
FONTS_PATH=/usr/share/fonts/truetype/dejavu
```

### Продакшн (Production)

```env
# .env для продакшна
APP_NAME="Resume Bot"
DEBUG=false
LOG_LEVEL=WARNING

# Telegram
TG_BOT_BOT_TOKEN=123456789:YOUR_PROD_BOT_TOKEN

# OpenAI
OPENAI_API_KEY=sk-proj-YOUR_PROD_API_KEY
OPENAI_MODEL_NAME=gpt-4
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=3000
OPENAI_TIMEOUT=120

# HeadHunter
HH_CLIENT_ID=YOUR_PROD_CLIENT_ID
HH_CLIENT_SECRET=YOUR_PROD_CLIENT_SECRET
HH_REDIRECT_URI=https://yourdomain.com/callback

# Callback Server
CALLBACK_LOCAL_HOST=0.0.0.0
CALLBACK_LOCAL_PORT=8080

# Fonts
FONTS_PATH=/usr/share/fonts/truetype/dejavu

# Logging
LOG_LEVEL=INFO
LOGS_PATH=/var/log/resume-bot
LOG_ROTATION=true
```

## 🐳 Docker конфигурация

### docker-compose.yml

```yaml
version: '3.8'

services:
  callback-server:
    build: .
    command: python -m src.callback_local_server.main
    ports:
      - "${CALLBACK_LOCAL_PORT}:${CALLBACK_LOCAL_PORT}"
    environment:
      - CALLBACK_LOCAL_HOST=${CALLBACK_LOCAL_HOST}
      - CALLBACK_LOCAL_PORT=${CALLBACK_LOCAL_PORT}
    env_file:
      - .env
    volumes:
      - ./LOGS:/app/LOGS

  telegram-bot:
    build: .
    command: python -m src.tg_bot.main
    depends_on:
      - callback-server
    env_file:
      - .env
    volumes:
      - ./LOGS:/app/LOGS
    restart: unless-stopped
```

### Dockerfile с конфигурацией

```dockerfile
FROM python:3.10-slim

# Установка системных зависимостей и шрифтов
RUN apt-get update && apt-get install -y \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копирование и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY src/ ./src/

# Создание папки для логов
RUN mkdir -p LOGS

# Установка переменных окружения по умолчанию
ENV FONTS_PATH=/usr/share/fonts/truetype/dejavu
ENV LOGS_PATH=/app/LOGS
ENV LOG_LEVEL=INFO

EXPOSE 8080
```

## ⚙️ Продвинутая конфигурация

### 1. Настройка прокси (если требуется)

```env
# HTTP прокси (опционально)
HTTP_PROXY=http://proxy.company.com:8080
HTTPS_PROXY=https://proxy.company.com:8080

# Исключения для прокси
NO_PROXY=localhost,127.0.0.1,api.openai.com
```

### 2. Настройки производительности

```env
# Максимальное количество одновременных пользователей
MAX_CONCURRENT_USERS=100

# Таймаут для LLM запросов
LLM_REQUEST_TIMEOUT=300

# Максимальный размер файла логов
MAX_LOG_FILE_SIZE=50MB

# Количество worker процессов
WORKER_PROCESSES=2
```

### 3. Настройки безопасности

```env
# Разрешенные домены для callback
ALLOWED_CALLBACK_DOMAINS=localhost,yourdomain.com

# Максимальное время жизни сессии (в секундах)
SESSION_TIMEOUT=3600

# Шифрование данных в памяти
ENCRYPT_MEMORY_DATA=true
```

## 🔍 Валидация конфигурации

### Автоматическая проверка

Система автоматически проверяет корректность конфигурации при запуске:

```python
# Пример валидации в src/config.py
class BaseAppSettings(BaseSettings):
    app_name: str = "Resume Bot"
    debug: bool = False
    
    @validator('app_name')
    def validate_app_name(cls, v):
        if len(v) < 3:
            raise ValueError('App name must be at least 3 characters')
        return v
```

### Скрипт проверки конфигурации

Создайте файл `scripts/validate_config.py`:

```python
#!/usr/bin/env python3
"""Скрипт проверки конфигурации"""

import sys
from pathlib import Path

# Добавляем src в PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent / 'src'))

def validate_config():
    """Проверка всех конфигураций"""
    try:
        from src.tg_bot.bot.config import settings as tg_settings
        print(f"✅ Telegram Bot: {tg_settings.bot_token[:10]}...")
        
        from src.hh.config import settings as hh_settings
        print(f"✅ HeadHunter: Client ID configured")
        
        from src.llm_gap_analyzer.config import settings as ai_settings
        print(f"✅ OpenAI: {ai_settings.model_name}")
        
        from src.callback_local_server.config import settings as cb_settings
        print(f"✅ Callback Server: {cb_settings.host}:{cb_settings.port}")
        
        print("\n🎉 Все конфигурации корректны!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return False

if __name__ == "__main__":
    success = validate_config()
    sys.exit(0 if success else 1)
```

Запуск проверки:

```bash
python scripts/validate_config.py
```

## 🔧 Настройка для разных сред

### 1. Использование .env файлов

```bash
# Разработка
cp .env.example .env.dev
# Отредактируйте .env.dev

# Запуск с конкретным файлом
export ENV_FILE=.env.dev
python -m src.tg_bot.main

# Или через переменную окружения
ENV_FILE=.env.dev python -m src.tg_bot.main
```

### 2. Профили конфигурации

Создайте файл `src/config_profiles.py`:

```python
import os
from typing import Dict, Any

PROFILES: Dict[str, Dict[str, Any]] = {
    'development': {
        'debug': True,
        'log_level': 'DEBUG',
        'openai_model': 'gpt-3.5-turbo',
        'temperature': 0.8,
    },
    'staging': {
        'debug': False,
        'log_level': 'INFO',
        'openai_model': 'gpt-4',
        'temperature': 0.7,
    },
    'production': {
        'debug': False,
        'log_level': 'WARNING',
        'openai_model': 'gpt-4',
        'temperature': 0.7,
    }
}

def get_profile_config(profile_name: str = None) -> Dict[str, Any]:
    """Получение конфигурации для профиля"""
    profile = profile_name or os.getenv('PROFILE', 'development')
    return PROFILES.get(profile, PROFILES['development'])
```

### 3. Переменные окружения через systemd

Для продакшн развертывания создайте `resume-bot.service`:

```ini
[Unit]
Description=AI Resume Assistant Bot
After=network.target

[Service]
Type=simple
User=resume-bot
WorkingDirectory=/opt/resume-bot
ExecStart=/opt/resume-bot/venv/bin/python -m src.tg_bot.main

# Переменные окружения
Environment=PROFILE=production
Environment=APP_NAME="Resume Bot Production"
Environment=DEBUG=false
Environment=LOG_LEVEL=INFO

# Загрузка из файла
EnvironmentFile=/opt/resume-bot/.env

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 📊 Мониторинг конфигурации

### Логирование настроек при старте

```python
# В src/tg_bot/main.py
async def main():
    logger.info("=== Resume Bot Starting ===")
    logger.info(f"App Name: {settings.app_name}")
    logger.info(f"Debug Mode: {settings.debug}")
    logger.info(f"OpenAI Model: {ai_settings.model_name}")
    logger.info(f"Callback Server: {cb_settings.host}:{cb_settings.port}")
    logger.info("==============================")
    
    # Запуск бота...
```

### Endpoint для проверки конфигурации

Добавьте в `callback_local_server/server.py`:

```python
@app.get("/health")
async def health_check():
    """Проверка работоспособности"""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "timestamp": datetime.now().isoformat(),
        "config": {
            "debug": settings.debug,
            "callback_host": settings.host,
            "callback_port": settings.port
        }
    }
```

## 🔒 Безопасность конфигурации

### 1. Защита .env файлов

```bash
# Установка правильных прав доступа
chmod 600 .env
chown app:app .env

# Исключение из git
echo ".env" >> .gitignore
echo ".env.*" >> .gitignore
```

### 2. Использование secrets в продакшне

```bash
# Для Docker Swarm
echo "your_secret_token" | docker secret create bot_token -
echo "your_openai_key" | docker secret create openai_key -

# В docker-compose.yml
services:
  bot:
    secrets:
      - bot_token
      - openai_key
    environment:
      - TG_BOT_BOT_TOKEN_FILE=/run/secrets/bot_token
      - OPENAI_API_KEY_FILE=/run/secrets/openai_key
```

### 3. Ротация ключей

Создайте скрипт `scripts/rotate_keys.py`:

```python
#!/usr/bin/env python3
"""Скрипт ротации API ключей"""

import os
import shutil
from datetime import datetime

def rotate_keys():
    """Ротация ключей с бэкапом старых"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Бэкап текущих настроек
    if os.path.exists('.env'):
        shutil.copy('.env', f'.env.backup.{timestamp}')
        print(f"✅ Создан бэкап: .env.backup.{timestamp}")
    
    # Здесь логика обновления ключей
    print("🔄 Обновите ключи в .env файле")
    print("🔄 Перезапустите сервисы")

if __name__ == "__main__":
    rotate_keys()
```

---

⚙️ **Правильная конфигурация — основа стабильной работы системы.**

Убедитесь, что все обязательные параметры настроены корректно, и регулярно проверяйте актуальность API ключей.