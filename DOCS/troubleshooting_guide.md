# 🐛 Устранение неполадок

Руководство по диагностике и решению проблем в AI Resume Assistant Bot.

## 🔍 Диагностика проблем

### 1. Проверка статуса системы

```bash
# Проверка процессов
ps aux | grep python | grep "src\."

# Проверка портов
netstat -tulpn | grep 8080

# Проверка логов
tail -f LOGS/*.log

# Проверка дискового пространства
df -h

# Проверка памяти
free -h
```

### 2. Быстрая диагностика

```bash
# Скрипт быстрой проверки
#!/bin/bash
echo "=== Resume Bot Health Check ==="

# Проверка Python
python3 --version || echo "❌ Python не найден"

# Проверка виртуального окружения
if [ -d "venv" ]; then
    echo "✅ Virtual environment exists"
else
    echo "❌ Virtual environment not found"
fi

# Проверка .env файла
if [ -f ".env" ]; then
    echo "✅ .env file exists"
else
    echo "❌ .env file missing"
fi

# Проверка зависимостей
pip list | grep -E "(aiogram|openai|pydantic|reportlab)" || echo "❌ Some dependencies missing"

echo "=== End Health Check ==="
```

## 🚨 Частые проблемы и решения

### 1. Проблемы запуска

#### Ошибка: `ModuleNotFoundError: No module named 'src'`

**Проблема:** Python не может найти модули проекта.

**Решения:**
```bash
# Убедитесь, что запускаете из корня проекта
pwd  # должно показать путь к ai-resume-assistant-bot

# Активируйте виртуальное окружение
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate     # Windows

# Переустановите зависимости
pip install -r requirements.txt

# Проверьте PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### Ошибка: `ImportError: cannot import name 'settings'`

**Проблема:** Неправильная конфигурация или отсутствие .env файла.

**Решения:**
```bash
# Создайте .env файл из примера
cp .env.example .env

# Заполните обязательные поля в .env
nano .env

# Проверьте конфигурацию
python scripts/validate_config.py
```

### 2. Telegram Bot проблемы

#### Ошибка: `Telegram Bot API: Unauthorized`

**Проблема:** Неверный токен бота.

**Решения:**
```env
# Проверьте токен в .env
TG_BOT_BOT_TOKEN=123456789:ABC...

# Создайте нового бота у @BotFather если нужно
# /newbot в Telegram
```

#### Ошибка: `Bot doesn't respond to messages`

**Проблема:** Бот запущен, но не отвечает.

**Диагностика:**
```bash
# Проверьте логи
tail -f LOGS/run_bot.log

# Проверьте подключение к интернету
ping api.telegram.org

# Проверьте, что процесс бота запущен
ps aux | grep "src.tg_bot.main"
```

**Решения:**
```bash
# Перезапустите бота
pkill -f "src.tg_bot.main"
python -m src.tg_bot.main

# Проверьте webhook (если использовался)
curl https://api.telegram.org/bot$BOT_TOKEN/getWebhookInfo
```

### 3. OAuth / HH.ru проблемы

#### Ошибка: `OAuth callback not working`

**Проблема:** Callback сервер недоступен или неправильно настроен.

**Диагностика:**
```bash
# Проверьте, что callback сервер запущен
curl http://localhost:8080/api/code

# Проверьте порт
netstat -tulpn | grep 8080
```

**Решения:**
```bash
# Запустите callback сервер
python -m src.callback_local_server.main

# Проверьте конфигурацию
echo $HH_REDIRECT_URI
# Должно быть: http://localhost:8080/callback

# Проверьте настройки приложения на dev.hh.ru
```

#### Ошибка: `Invalid client_id or client_secret`

**Проблема:** Неверные учетные данные HH.ru.

**Решения:**
```env
# Проверьте настройки в .env
HH_CLIENT_ID=your_client_id
HH_CLIENT_SECRET=your_client_secret

# Создайте новое приложение на dev.hh.ru если нужно
```

### 4. OpenAI API проблемы

#### Ошибка: `OpenAI API: Insufficient quota`

**Проблема:** Превышен лимит использования OpenAI API.

**Решения:**
```bash
# Проверьте баланс на platform.openai.com
# Пополните счет или смените API ключ

# Временно используйте более дешевую модель
OPENAI_MODEL_NAME=gpt-3.5-turbo
```

#### Ошибка: `OpenAI API: Rate limit exceeded`

**Проблема:** Слишком много запросов к API.

**Решения:**
```python
# Добавьте retry механизм
import time
import random

def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if "rate limit" in str(e).lower():
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait_time)
            else:
                raise
    raise Exception("Max retries exceeded")
```

#### Ошибка: `OpenAI API: Invalid API key`

**Проблема:** Неверный или истекший API ключ.

**Решения:**
```env
# Обновите API ключ в .env
OPENAI_API_KEY=sk-proj-новый_ключ

# Создайте новый ключ на platform.openai.com
```

### 5. PDF генерация проблемы

#### Ошибка: `ReportLab: Can't find font`

**Проблема:** Отсутствуют шрифты для поддержки русского языка.

**Решения:**
```bash
# Ubuntu/Debian
sudo apt install fonts-dejavu-core

# macOS
brew install --cask font-dejavu

# Или скачайте шрифты вручную
wget https://github.com/dejavu-fonts/dejavu-fonts/releases/download/version_2_37/dejavu-fonts-ttf-2.37.zip
unzip dejavu-fonts-ttf-2.37.zip
mkdir -p fonts
cp dejavu-fonts-ttf-2.37/ttf/* fonts/

# Укажите путь в .env
FONTS_PATH=$(pwd)/fonts
```

#### Ошибка: `PDF contains squares instead of text`

**Проблема:** Шрифты найдены, но не зарегистрированы правильно.

**Диагностика:**
```python
# Проверьте регистрацию шрифтов
python -c "
from src.llm_interview_simulation.pdf_generator import InterviewSimulationPDFGenerator
gen = InterviewSimulationPDFGenerator()
print(f'Font family: {gen.font_family}')
"
```

**Решения:**
```bash
# Убедитесь, что путь к шрифтам правильный
ls -la /usr/share/fonts/truetype/dejavu/

# Проверьте переменную окружения
echo $FONTS_PATH

# Перезапустите приложение после изменения путей
```

### 6. Проблемы с памятью и производительностью

#### Ошибка: `Memory usage too high`

**Проблема:** Высокое потребление памяти.

**Диагностика:**
```bash
# Проверьте использование памяти
ps aux --sort=-%mem | grep python | head -5

# Проверьте системную память
free -h

# Мониторинг в реальном времени
top -p $(pgrep -f "src.tg_bot.main")
```

**Решения:**
```python
# Очистка данных пользователя после обработки
async def cleanup_user_data(state: FSMContext):
    await state.clear()

# Ограничение размера данных в состоянии
MAX_RESUME_SIZE = 50000  # 50KB
MAX_VACANCY_SIZE = 30000  # 30KB
```

#### Ошибка: `Process killed (OOM)`

**Проблема:** Недостаточно памяти, процесс убит системой.

**Решения:**
```bash
# Увеличьте swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Или увеличьте RAM сервера
# Или оптимизируйте код для использования меньше памяти
```

## 📊 Мониторинг и логи

### 1. Структура логов

```
LOGS/
├── run_bot.log                    # Основной лог бота
├── callback_local_server.log      # OAuth сервер
├── hh_api_client.log             # HH API клиент
├── llm_gap_analyzer.log          # GAP анализ
├── llm_cover_letter.log          # Cover letter
├── llm_interview_checklist.log   # Чек-листы
└── llm_interview_simulation.log  # Симуляция интервью
```

### 2. Полезные команды для анализа логов

```bash
# Поиск ошибок
grep -i error LOGS/*.log

# Поиск по пользователю
grep "user_id=12345" LOGS/*.log

# Последние ошибки
tail -f LOGS/*.log | grep -i error

# Статистика по логам
grep -c "ERROR" LOGS/*.log
grep -c "WARNING" LOGS/*.log

# Анализ производительности
grep "Duration" LOGS/*.log | tail -20
```

### 3. Скрипт анализа логов

Создайте `scripts/analyze_logs.py`:

```python
#!/usr/bin/env python3
"""Анализ логов системы"""

import re
import glob
from collections import defaultdict, Counter
from datetime import datetime, timedelta

def analyze_logs():
    """Анализ всех логов"""
    log_files = glob.glob("LOGS/*.log")
    
    errors = []
    warnings = []
    user_activity = defaultdict(int)
    
    for log_file in log_files:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                # Поиск ошибок
                if 'ERROR' in line:
                    errors.append(line.strip())
                
                # Поиск предупреждений
                if 'WARNING' in line:
                    warnings.append(line.strip())
                
                # Активность пользователей
                user_match = re.search(r'пользователя (\d+)', line)
                if user_match:
                    user_activity[user_match.group(1)] += 1
    
    # Отчет
    print("=== Анализ логов ===")
    print(f"Ошибок: {len(errors)}")
    print(f"Предупреждений: {len(warnings)}")
    print(f"Активных пользователей: {len(user_activity)}")
    
    if errors:
        print("\nПоследние ошибки:")
        for error in errors[-5:]:
            print(f"  {error}")
    
    if user_activity:
        print("\nТоп пользователей по активности:")
        for user_id, count in Counter(user_activity).most_common(5):
            print(f"  {user_id}: {count} действий")

if __name__ == "__main__":
    analyze_logs()
```

### 4. Настройка ротации логов

```bash
# Создайте конфигурацию logrotate
sudo tee /etc/logrotate.d/resume-bot << EOF
/path/to/resume-bot/LOGS/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 resume-bot resume-bot
    postrotate
        # Отправьте сигнал приложению для переоткрытия логов
        pkill -USR1 -f "src.tg_bot.main"
    endscript
}
EOF
```

## 🔧 Инструменты диагностики

### 1. Скрипт проверки системы

Создайте `scripts/system_check.py`:

```python
#!/usr/bin/env python3
"""Комплексная проверка системы"""

import os
import sys
import subprocess
import requests
from pathlib import Path

def check_python():
    """Проверка Python"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (требуется 3.8+)")
        return False

def check_dependencies():
    """Проверка зависимостей"""
    required = ['aiogram', 'openai', 'pydantic', 'reportlab', 'aiohttp']
    
    for package in required:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} не установлен")
            return False
    return True

def check_config():
    """Проверка конфигурации"""
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env файл не найден")
        return False
    
    required_vars = [
        'TG_BOT_BOT_TOKEN',
        'OPENAI_API_KEY',
        'HH_CLIENT_ID',
        'HH_CLIENT_SECRET'
    ]
    
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var}")
        else:
            print(f"❌ {var} не установлен")
            return False
    return True

def check_network():
    """Проверка сетевого подключения"""
    urls = [
        'https://api.telegram.org',
        'https://api.openai.com',
        'https://api.hh.ru'
    ]
    
    for url in urls:
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ {url} доступен")
        except:
            print(f"❌ {url} недоступен")
            return False
    return True

def check_ports():
    """Проверка портов"""
    import socket
    
    port = 8080
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    
    if result == 0:
        print(f"⚠️  Порт {port} уже занят")
    else:
        print(f"✅ Порт {port} свободен")
    
    return True

def main():
    """Основная проверка"""
    print("=== Проверка системы Resume Bot ===\n")
    
    checks = [
        ("Python версия", check_python),
        ("Зависимости", check_dependencies),
        ("Конфигурация", check_config),
        ("Сеть", check_network),
        ("Порты", check_ports)
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\n{name}:")
        if not check_func():
            all_passed = False
    
    print("\n" + "="*40)
    if all_passed:
        print("🎉 Все проверки пройдены! Система готова к работе.")
    else:
        print("❌ Обнаружены проблемы. Исправьте их перед запуском.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
```

### 2. Мониторинг в реальном времени

```bash
# Скрипт мониторинга
#!/bin/bash

watch_logs() {
    echo "=== Мониторинг Resume Bot ==="
    
    # Статус процессов
    echo "Процессы:"
    ps aux | grep -E "(tg_bot|callback_local_server)" | grep -v grep
    
    # Использование ресурсов
    echo -e "\nИспользование ресурсов:"
    echo "Память:"
    free -h | grep -E "(Mem|Swap)"
    
    echo "Диск:"
    df -h | grep -E "(/$|/home)"
    
    # Последние логи
    echo -e "\nПоследние ошибки:"
    grep -h "ERROR" LOGS/*.log | tail -3
    
    echo -e "\n$(date)"
    echo "================================"
}

# Запуск мониторинга каждые 10 секунд
while true; do
    clear
    watch_logs
    sleep 10
done
```

## 🆘 Получение помощи

### 1. Сбор информации для поддержки

Создайте `scripts/collect_debug_info.py`:

```python
#!/usr/bin/env python3
"""Сбор отладочной информации"""

import os
import sys
import platform
import subprocess
from datetime import datetime

def collect_debug_info():
    """Сбор всей необходимой информации"""
    info = []
    
    # Системная информация
    info.append("=== СИСТЕМНАЯ ИНФОРМАЦИЯ ===")
    info.append(f"ОС: {platform.system()} {platform.release()}")
    info.append(f"Python: {sys.version}")
    info.append(f"Дата: {datetime.now()}")
    
    # Переменные окружения (без секретов)
    info.append("\n=== КОНФИГУРАЦИЯ ===")
    safe_vars = ['APP_NAME', 'DEBUG', 'LOG_LEVEL', 'OPENAI_MODEL_NAME']
    for var in safe_vars:
        value = os.getenv(var, 'НЕ УСТАНОВЛЕНО')
        info.append(f"{var}: {value}")
    
    # Установленные пакеты
    try:
        result = subprocess.run(['pip', 'list'], capture_output=True, text=True)
        info.append("\n=== УСТАНОВЛЕННЫЕ ПАКЕТЫ ===")
        info.append(result.stdout)
    except:
        info.append("\n❌ Не удалось получить список пакетов")
    
    # Последние ошибки
    info.append("\n=== ПОСЛЕДНИЕ ОШИБКИ ===")
    try:
        with open('LOGS/run_bot.log', 'r') as f:
            lines = f.readlines()
            error_lines = [line for line in lines if 'ERROR' in line]
            info.extend(error_lines[-10:])  # Последние 10 ошибок
    except:
        info.append("Лог файл недоступен")
    
    return '\n'.join(info)

def save_debug_info():
    """Сохранение информации в файл"""
    info = collect_debug_info()
    
    filename = f"debug_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(info)
    
    print(f"Отладочная информация сохранена в {filename}")
    print("Отправьте этот файл в службу поддержки")
    
    return filename

if __name__ == "__main__":
    save_debug_info()
```

### 2. Контакты поддержки

- 🐛 **GitHub Issues**: [github.com/your-repo/issues](https://github.com/your-repo/issues)
- 💬 **Discussions**: [github.com/your-repo/discussions](https://github.com/your-repo/discussions)
- 📧 **Email**: support@your-domain.com
- 💬 **Telegram**: @your_support_channel

### 3. Шаблон обращения в поддержку

```markdown
## Описание проблемы
[Кратко опишите проблему]

## Шаги для воспроизведения
1. [Первый шаг]
2. [Второй шаг]
3. [Результат]

## Ожидаемое поведение
[Что должно было произойти]

## Фактическое поведение
[Что произошло на самом деле]

## Окружение
- ОС: [Windows/macOS/Linux + версия]
- Python: [версия]
- Версия бота: [версия или коммит]

## Логи
```
[Вставьте релевантные логи]
```

## Дополнительная информация
[Любая дополнительная информация]
```

---

🔧 **Помните**: большинство проблем решается проверкой логов и правильной настройкой конфигурации.

При обращении в поддержку всегда прикладывайте логи и результат выполнения `scripts/collect_debug_info.py`.