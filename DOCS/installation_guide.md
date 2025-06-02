# 📥 Руководство по установке

Подробное руководство по установке и настройке AI Resume Assistant Bot.

## 📋 Системные требования

### Минимальные требования

- **Python**: 3.8 или выше
- **ОС**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **RAM**: минимум 512 MB
- **Дисковое пространство**: 1 GB

### Рекомендуемые требования

- **Python**: 3.10+
- **RAM**: 2 GB или больше
- **CPU**: 2+ ядра
- **Дисковое пространство**: 5 GB

## 🛠️ Предварительная подготовка

### 1. Установка Python

#### Windows
```bash
# Скачайте Python с официального сайта
https://www.python.org/downloads/windows/

# Или через Chocolatey
choco install python

# Или через Microsoft Store
# Найдите "Python 3.x" в Microsoft Store
```

#### macOS
```bash
# Через Homebrew (рекомендуется)
brew install python@3.10

# Или скачайте с официального сайта
https://www.python.org/downloads/mac-osx/
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3.10 python3.10-pip python3.10-venv
```

#### CentOS/RHEL
```bash
sudo yum install python3 python3-pip
# или для новых версий
sudo dnf install python3 python3-pip
```

### 2. Проверка установки Python

```bash
python3 --version  # Должно показать Python 3.8+
pip3 --version     # Должно показать pip версию
```

## 📦 Установка проекта

### Метод 1: Клонирование из Git (рекомендуется)

```bash
# Клонирование репозитория
git clone https://github.com/your-username/ai-resume-assistant-bot.git
cd ai-resume-assistant-bot

# Создание виртуального окружения
python3 -m venv venv

# Активация виртуального окружения
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt
```

### Метод 2: Установка из архива

```bash
# Скачайте архив проекта и распакуйте
wget https://github.com/your-username/ai-resume-assistant-bot/archive/main.zip
unzip main.zip
cd ai-resume-assistant-bot-main

# Далее как в методе 1
python3 -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows
pip install -r requirements.txt
```

### Метод 3: Docker (продвинутый)

```bash
# Клонирование репозитория
git clone https://github.com/your-username/ai-resume-assistant-bot.git
cd ai-resume-assistant-bot

# Сборка Docker образа
docker build -t ai-resume-bot .

# Создание .env файла (см. раздел конфигурации)
cp .env.example .env
# Отредактируйте .env файл

# Запуск контейнера
docker run -d --name ai-resume-bot --env-file .env -p 8080:8080 ai-resume-bot
```

## ⚙️ Настройка конфигурации

### 1. Создание .env файла

```bash
# Копирование примера конфигурации
cp .env.example .env

# Редактирование конфигурации
nano .env  # или используйте любой текстовый редактор
```

### 2. Обязательные параметры

Отредактируйте файл `.env` и заполните следующие параметры:

```env
# ===================
# TELEGRAM BOT
# ===================
TG_BOT_BOT_TOKEN=your_telegram_bot_token_here

# ===================
# OPENAI API
# ===================
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL_NAME=gpt-4

# ===================
# HEADHUNTER API
# ===================
HH_CLIENT_ID=your_hh_client_id
HH_CLIENT_SECRET=your_hh_client_secret
HH_REDIRECT_URI=http://localhost:8080/callback

# ===================
# CALLBACK SERVER
# ===================
CALLBACK_LOCAL_HOST=0.0.0.0
CALLBACK_LOCAL_PORT=8080

# ===================
# FONTS (опционально)
# ===================
FONTS_PATH=/path/to/dejavu-fonts
```

## 🔑 Получение API ключей

### 1. Telegram Bot Token

1. Откройте Telegram и найдите [@BotFather](https://t.me/botfather)
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен в `.env` файл

```
Пример токена: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

### 2. OpenAI API Key

1. Зарегистрируйтесь на [platform.openai.com](https://platform.openai.com)
2. Перейдите в раздел "API Keys"
3. Создайте новый API ключ
4. Скопируйте ключ в `.env` файл

```
Пример ключа: sk-proj-ABCdefghijklmnopqrstuvwxyz123456789
```

**💰 Важно**: Убедитесь, что у вас есть кредиты на аккаунте OpenAI для использования API.

### 3. HeadHunter API

1. Зарегистрируйтесь на [dev.hh.ru](https://dev.hh.ru)
2. Создайте новое приложение
3. Укажите redirect URI: `http://localhost:8080/callback`
4. Получите Client ID и Client Secret
5. Добавьте их в `.env` файл

## 🖼️ Настройка шрифтов для PDF

### Вариант 1: Автоматический поиск

Система автоматически найдет шрифты DejaVu в стандартных местах:
- `/usr/share/fonts/truetype/dejavu` (Linux)
- `/System/Library/Fonts` (macOS)

### Вариант 2: Скачивание шрифтов

```bash
# Создание папки для шрифтов
mkdir -p fonts

# Скачивание шрифтов DejaVu
wget https://github.com/dejavu-fonts/dejavu-fonts/releases/download/version_2_37/dejavu-fonts-ttf-2.37.zip
unzip dejavu-fonts-ttf-2.37.zip
mv dejavu-fonts-ttf-2.37/ttf/* fonts/

# Указание пути в .env
echo "FONTS_PATH=$(pwd)/fonts" >> .env
```

### Вариант 3: Использование системных шрифтов

#### Ubuntu/Debian
```bash
sudo apt install fonts-dejavu-core
```

#### CentOS/RHEL
```bash
sudo yum install dejavu-sans-fonts
```

#### macOS
```bash
brew install --cask font-dejavu
```

## 🚀 Запуск приложения

### 1. Проверка установки

```bash
# Активация виртуального окружения
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate     # Windows

# Проверка зависимостей
pip list | grep -E "(aiogram|openai|pydantic|reportlab)"
```

### 2. Запуск в режиме разработки

```bash
# Терминал 1: Запуск callback сервера
python -m src.callback_local_server.main

# Терминал 2: Запуск Telegram бота
python -m src.tg_bot.main
```

### 3. Проверка работоспособности

1. Найдите вашего бота в Telegram
2. Отправьте команду `/start`
3. Убедитесь, что бот отвечает

## 🐳 Docker установка (альтернативный метод)

### 1. Установка Docker

#### Ubuntu
```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

#### CentOS/RHEL
```bash
sudo yum install docker docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

#### Windows/macOS
Скачайте Docker Desktop с [docker.com](https://www.docker.com/products/docker-desktop)

### 2. Создание Dockerfile

Создайте файл `Dockerfile` в корне проекта:

```dockerfile
FROM python:3.10-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY src/ ./src/

# Создание папки для логов
RUN mkdir -p LOGS

# Установка переменной окружения для шрифтов
ENV FONTS_PATH=/usr/share/fonts/truetype/dejavu

# Экспорт порта для callback сервера
EXPOSE 8080

# Команда запуска (потребуется docker-compose для запуска двух сервисов)
CMD ["python", "-m", "src.tg_bot.main"]
```

### 3. Создание docker-compose.yml

```yaml
version: '3.8'

services:
  callback-server:
    build: .
    command: python -m src.callback_local_server.main
    ports:
      - "8080:8080"
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

### 4. Запуск через Docker Compose

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка сервисов
docker-compose down
```

## 🔧 Производственное развертывание

### 1. Настройка systemd (Linux)

Создайте файл `/etc/systemd/system/ai-resume-bot.service`:

```ini
[Unit]
Description=AI Resume Assistant Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/ai-resume-assistant-bot
Environment=PATH=/path/to/ai-resume-assistant-bot/venv/bin
ExecStart=/path/to/ai-resume-assistant-bot/venv/bin/python -m src.tg_bot.main
EnvironmentFile=/path/to/ai-resume-assistant-bot/.env
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Активация сервиса:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-resume-bot
sudo systemctl start ai-resume-bot
sudo systemctl status ai-resume-bot
```

### 2. Настройка Nginx (опционально)

Если нужен reverse proxy для callback сервера:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /callback {
        proxy_pass http://localhost:8080/callback;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🧪 Тестирование установки

### 1. Проверка компонентов

```bash
# Проверка импорта модулей
python -c "import src.tg_bot.main; print('✅ Telegram bot OK')"
python -c "import src.callback_local_server.main; print('✅ Callback server OK')"
python -c "import openai; print('✅ OpenAI OK')"
python -c "import reportlab; print('✅ ReportLab OK')"
```

### 2. Проверка шрифтов

```bash
python -c "
from src.llm_interview_simulation.pdf_generator import InterviewSimulationPDFGenerator
gen = InterviewSimulationPDFGenerator()
print(f'✅ Fonts: {gen.font_family}')
"
```

### 3. Проверка конфигурации

```bash
python -c "
from src.tg_bot.bot.config import settings as tg_settings
from src.hh.config import settings as hh_settings
from src.llm_gap_analyzer.config import settings as ai_settings
print('✅ All configs loaded successfully')
"
```

## 🚨 Устранение проблем

### Частые ошибки

#### 1. ModuleNotFoundError
```bash
# Убедитесь, что виртуальное окружение активировано
source venv/bin/activate

# Переустановите зависимости
pip install -r requirements.txt
```

#### 2. Ошибки шрифтов в PDF
```bash
# Установите шрифты DejaVu
sudo apt install fonts-dejavu-core  # Ubuntu
brew install --cask font-dejavu     # macOS

# Или укажите путь в .env
export FONTS_PATH=/path/to/fonts
```

#### 3. Ошибки OAuth HH.ru
Проверьте, что:
- Callback сервер запущен на порту 8080
- В настройках HH.ru указан правильный redirect URI
- Порт 8080 не заблокирован файрволом

#### 4. Ошибки OpenAI API
- Проверьте баланс на аккаунте OpenAI
- Убедитесь, что API ключ действителен
- Проверьте лимиты использования

### Логи для диагностики

```bash
# Просмотр логов
tail -f LOGS/run_bot.log
tail -f LOGS/callback_local_server.log

# Поиск ошибок
grep ERROR LOGS/*.log
```

## 📊 Мониторинг

### 1. Проверка статуса сервисов

```bash
# Проверка процессов
ps aux | grep python | grep "src\."

# Проверка портов
netstat -tulpn | grep 8080

# Проверка логов
tail -f LOGS/*.log
```

### 2. Настройка мониторинга (опционально)

Для продакшн развертывания рекомендуется настроить:
- **Prometheus + Grafana** для метрик
- **ELK Stack** для логов  
- **Uptime Robot** для мониторинга доступности

---

✅ **Поздравляем! Установка завершена.**

Теперь вы можете использовать AI Resume Assistant Bot. Если возникли проблемы, обратитесь к разделу [Troubleshooting](TROUBLESHOOTING.md) или создайте issue в GitHub.