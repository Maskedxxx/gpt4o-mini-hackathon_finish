# ===========================================
# AI Resume Assistant Bot Configuration
# ===========================================

# ===================
# APPLICATION SETTINGS
# ===================
APP_NAME="Resume Bot"
DEBUG=false

# ===================
# TELEGRAM BOT
# ===================
# Получите токен у @BotFather в Telegram
TG_BOT_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# ===================
# OPENAI API
# ===================
# Получите API ключ на platform.openai.com
OPENAI_API_KEY=sk-proj-ABCdefghijklmnopqrstuvwxyz123456789

# Модель для использования (gpt-4 рекомендуется для лучшего качества)
OPENAI_MODEL_NAME=gpt-4

# Флаг разрешения использования OpenAI API (true/false)
# Установите false для отключения всех запросов к OpenAI
OPENAI_API_ENABLED=true

# Опциональные настройки OpenAI
# OPENAI_TEMPERATURE=0.7
# OPENAI_MAX_TOKENS=2000
# OPENAI_TIMEOUT=60

# ===================
# HEADHUNTER API
# ===================
# Зарегистрируйте приложение на dev.hh.ru
HH_CLIENT_ID=your_hh_client_id
HH_CLIENT_SECRET=your_hh_client_secret

# ВАЖНО: Этот URL должен совпадать с redirect_uri в настройках приложения HH.ru
HH_REDIRECT_URI=http://localhost:8080/callback

# ===================
# CALLBACK SERVER
# ===================
# Сервер для обработки OAuth callback от HH.ru
CALLBACK_LOCAL_HOST=0.0.0.0
CALLBACK_LOCAL_PORT=8080

# ===================
# FONTS CONFIGURATION
# ===================
# Путь к шрифтам DejaVu для корректного отображения русского текста в PDF
# Оставьте пустым для автоматического поиска
FONTS_PATH=

# Примеры путей:
# macOS: FONTS_PATH=/Users/username/Desktop/dejavu-sans
# Linux: FONTS_PATH=/usr/share/fonts/truetype/dejavu
# Windows: FONTS_PATH=C:\Windows\Fonts
# Локальная папка: FONTS_PATH=./fonts/dejavu-sans

# ===================
# LOGGING
# ===================
# Уровень логирования: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# Путь к папке логов (по умолчанию: ./LOGS)
# LOGS_PATH=./LOGS

# ===================
# SECURITY SETTINGS
# ===================
# Пароль для демо-доступа к веб-приложениям
DEMO_PASSWORD=demo2025

# Таймаут сессии авторизации (в часах)
SESSION_TIMEOUT_HOURS=24

# Секретный ключ для подписи сессий (генерируется автоматически если не указан)
# AUTH_SECRET_KEY=your_secret_key_here

# ===================
# ADVANCED SETTINGS
# ===================
# Максимальное количество одновременных пользователей
# MAX_CONCURRENT_USERS=100

# Таймаут для LLM запросов (в секундах)
# LLM_REQUEST_TIMEOUT=300

# Режим отладки для подробных логов
# DEBUG=true

# ===================
# PRODUCTION SETTINGS
# ===================
# Для продакшн развертывания раскомментируйте и настройте:

# Домен для OAuth callback (вместо localhost)
# HH_REDIRECT_URI=https://yourdomain.com/callback

# Настройки безопасности
# ALLOWED_CALLBACK_DOMAINS=yourdomain.com,localhost
# SESSION_TIMEOUT=3600

# Настройки прокси (если требуется)
# HTTP_PROXY=http://proxy.company.com:8080
# HTTPS_PROXY=https://proxy.company.com:8080
# NO_PROXY=localhost,127.0.0.1,api.openai.com

# ===========================================
# ИНСТРУКЦИИ ПО НАСТРОЙКЕ
# ===========================================

# 1. TELEGRAM BOT TOKEN:
#    - Найдите @BotFather в Telegram
#    - Отправьте /newbot и следуйте инструкциям
#    - Скопируйте полученный токен в TG_BOT_BOT_TOKEN

# 2. OPENAI API KEY:
#    - Зарегистрируйтесь на platform.openai.com
#    - Создайте API ключ в разделе "API Keys"
#    - Убедитесь, что у вас есть кредиты на аккаунте

# 3. HEADHUNTER API:
#    - Зарегистрируйтесь на dev.hh.ru
#    - Создайте новое приложение
#    - Укажите redirect_uri: http://localhost:8080/callback
#    - Скопируйте client_id и client_secret

# 4. ШРИФТЫ:
#    - Скачайте шрифты DejaVu с https://dejavu-fonts.github.io/
#    - Или установите системные: sudo apt install fonts-dejavu-core
#    - Укажите путь в FONTS_PATH или оставьте пустым для автопоиска

# 5. ПРОВЕРКА КОНФИГУРАЦИИ:
#    После заполнения всех параметров запустите:
#    python scripts/validate_config.py