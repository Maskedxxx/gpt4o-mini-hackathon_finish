# 🚀 Руководство по развертыванию

Подробное руководство по развертыванию AI Resume Assistant Bot в производственной среде.

## 📋 Предварительные требования

### Минимальные системные требования

- **CPU**: 2+ ядра
- **RAM**: 4 GB (рекомендуется 8 GB)
- **Диск**: 20 GB свободного места
- **ОС**: Ubuntu 20.04+, CentOS 8+, или аналогичная
- **Python**: 3.8+
- **Сеть**: Статический IP или домен

### Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка необходимых пакетов
sudo apt install -y python3 python3-pip python3-venv git nginx certbot python3-certbot-nginx

# Создание пользователя для приложения
sudo useradd -m -s /bin/bash resume-bot
sudo usermod -aG sudo resume-bot

# Переключение на пользователя приложения
sudo su - resume-bot
```

## 🐳 Docker развертывание (рекомендуется)

### 1. Установка Docker

```bash
# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER
```

### 2. Подготовка проекта

```bash
# Клонирование репозитория
git clone https://github.com/your-username/ai-resume-assistant-bot.git
cd ai-resume-assistant-bot

# Создание .env файла
cp .env.example .env
nano .env  # Отредактируйте конфигурацию
```

### 3. Создание docker-compose.yml

```yaml
version: '3.8'

services:
  callback-server:
    build: .
    image: resume-bot:latest
    command: python -m src.callback_local_server.main
    ports:
      - "8080:8080"
    environment:
      - CALLBACK_LOCAL_HOST=0.0.0.0
      - CALLBACK_LOCAL_PORT=8080
    env_file:
      - .env
    volumes:
      - ./LOGS:/app/LOGS
      - ./fonts:/app/fonts
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  telegram-bot:
    build: .
    image: resume-bot:latest
    command: python -m src.tg_bot.main
    depends_on:
      - callback-server
    env_file:
      - .env
    volumes:
      - ./LOGS:/app/LOGS
      - ./fonts:/app/fonts
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('https://api.telegram.org')"]
      interval: 60s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - callback-server
    restart: unless-stopped

volumes:
  logs:
  fonts:
```

### 4. Настройка Nginx

Создайте `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream callback_backend {
        server callback-server:8080;
    }

    # HTTP редирект на HTTPS
    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS сервер
    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        # SSL сертификаты
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        # SSL настройки
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # Проксирование на callback сервер
        location /callback {
            proxy_pass http://callback_backend/callback;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check
        location /health {
            proxy_pass http://callback_backend/health;
        }

        # Основная страница (опционально)
        location / {
            return 200 'Resume Bot is running';
            add_header Content-Type text/plain;
        }
    }
}
```

### 5. Запуск приложения

```bash
# Сборка и запуск
docker-compose up --build -d

# Проверка логов
docker-compose logs -f

# Проверка статуса
docker-compose ps
```

## 🔧 Развертывание без Docker

### 1. Подготовка окружения

```bash
# Создание директории приложения
sudo mkdir -p /opt/resume-bot
sudo chown resume-bot:resume-bot /opt/resume-bot
cd /opt/resume-bot

# Клонирование репозитория
git clone https://github.com/your-username/ai-resume-assistant-bot.git .

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Установка шрифтов
sudo apt install fonts-dejavu-core
```

### 2. Конфигурация

```bash
# Создание .env файла
cp .env.example .env
nano .env

# Создание директорий
mkdir -p LOGS
mkdir -p /var/log/resume-bot
sudo chown resume-bot:resume-bot /var/log/resume-bot
```

### 3. Создание systemd сервисов

#### Callback Server (`/etc/systemd/system/resume-bot-callback.service`)

```ini
[Unit]
Description=Resume Bot Callback Server
After=network.target

[Service]
Type=simple
User=resume-bot
Group=resume-bot
WorkingDirectory=/opt/resume-bot
Environment=PATH=/opt/resume-bot/venv/bin
ExecStart=/opt/resume-bot/venv/bin/python -m src.callback_local_server.main
EnvironmentFile=/opt/resume-bot/.env

# Logging
StandardOutput=append:/var/log/resume-bot/callback.log
StandardError=append:/var/log/resume-bot/callback.error.log

# Restart policy
Restart=always
RestartSec=10

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/opt/resume-bot/LOGS /var/log/resume-bot

[Install]
WantedBy=multi-user.target
```

#### Telegram Bot (`/etc/systemd/system/resume-bot-telegram.service`)

```ini
[Unit]
Description=Resume Bot Telegram Bot
After=network.target resume-bot-callback.service
Requires=resume-bot-callback.service

[Service]
Type=simple
User=resume-bot
Group=resume-bot
WorkingDirectory=/opt/resume-bot
Environment=PATH=/opt/resume-bot/venv/bin
ExecStart=/opt/resume-bot/venv/bin/python -m src.tg_bot.main
EnvironmentFile=/opt/resume-bot/.env

# Logging
StandardOutput=append:/var/log/resume-bot/telegram.log
StandardError=append:/var/log/resume-bot/telegram.error.log

# Restart policy
Restart=always
RestartSec=10

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/opt/resume-bot/LOGS /var/log/resume-bot

[Install]
WantedBy=multi-user.target
```

### 4. Запуск сервисов

```bash
# Перезагрузка systemd
sudo systemctl daemon-reload

# Включение автозапуска
sudo systemctl enable resume-bot-callback.service
sudo systemctl enable resume-bot-telegram.service

# Запуск сервисов
sudo systemctl start resume-bot-callback.service
sudo systemctl start resume-bot-telegram.service

# Проверка статуса
sudo systemctl status resume-bot-callback.service
sudo systemctl status resume-bot-telegram.service
```

## 🔐 SSL/TLS настройка

### 1. Получение SSL сертификата

```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Проверка автоматического обновления
sudo certbot renew --dry-run
```

### 2. Настройка автоматического обновления

```bash
# Добавление в crontab
sudo crontab -e

# Добавить строку:
0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Мониторинг и логирование

### 1. Настройка logrotate

```bash
# Создание конфигурации
sudo tee /etc/logrotate.d/resume-bot << EOF
/var/log/resume-bot/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 resume-bot resume-bot
    postrotate
        systemctl reload resume-bot-callback.service
        systemctl reload resume-bot-telegram.service
    endscript
}

/opt/resume-bot/LOGS/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 resume-bot resume-bot
}
EOF
```

### 2. Мониторинг с помощью systemd

```bash
# Проверка статуса сервисов
sudo systemctl status resume-bot-*

# Просмотр логов
sudo journalctl -u resume-bot-callback.service -f
sudo journalctl -u resume-bot-telegram.service -f

# Статистика ресурсов
sudo systemctl show resume-bot-telegram.service --property=MemoryCurrent
```

### 3. Скрипт мониторинга

Создайте `/opt/resume-bot/scripts/monitor.sh`:

```bash
#!/bin/bash

LOG_FILE="/var/log/resume-bot/monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Функция логирования
log_message() {
    echo "[$DATE] $1" >> $LOG_FILE
}

# Проверка сервисов
check_services() {
    for service in resume-bot-callback resume-bot-telegram; do
        if ! systemctl is-active --quiet $service; then
            log_message "ERROR: $service is not running"
            systemctl restart $service
            log_message "INFO: Restarted $service"
        else
            log_message "INFO: $service is running"
        fi
    done
}

# Проверка дискового пространства
check_disk_space() {
    USAGE=$(df /opt/resume-bot | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ $USAGE -gt 80 ]; then
        log_message "WARNING: Disk usage is ${USAGE}%"
    fi
}

# Проверка памяти
check_memory() {
    MEM_USAGE=$(free | awk 'NR==2{printf "%.2f", $3*100/$2}')
    if (( $(echo "$MEM_USAGE > 80" | bc -l) )); then
        log_message "WARNING: Memory usage is ${MEM_USAGE}%"
    fi
}

# Основной цикл
main() {
    log_message "Starting health check"
    check_services
    check_disk_space
    check_memory
    log_message "Health check completed"
}

main
```

### 4. Автоматический мониторинг

```bash
# Добавление в crontab
sudo crontab -e

# Проверка каждые 5 минут
*/5 * * * * /opt/resume-bot/scripts/monitor.sh

# Ежедневная очистка старых логов
0 2 * * * find /opt/resume-bot/LOGS -name "*.log" -mtime +7 -delete
```

## 🔄 Непрерывная интеграция и развертывание

### 1. GitHub Actions workflow

Создайте `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to server
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          cd /opt/resume-bot
          git pull origin main
          docker-compose down
          docker-compose up --build -d
          docker-compose logs --tail=50
```

### 2. Автоматическое развертывание

```bash
# Скрипт обновления
#!/bin/bash
cd /opt/resume-bot

# Резервное копирование
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# Обновление кода
git pull origin main

# Перезапуск сервисов
if [ -f "docker-compose.yml" ]; then
    docker-compose down
    docker-compose up --build -d
else
    sudo systemctl restart resume-bot-callback.service
    sudo systemctl restart resume-bot-telegram.service
fi

echo "Deployment completed"
```

## 🔒 Безопасность

### 1. Настройка файрвола

```bash
# UFW (Ubuntu)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Опционально: ограничение SSH по IP
sudo ufw allow from YOUR_IP to any port ssh
```

### 2. Защита от DDoS

```bash
# Fail2ban для защиты SSH
sudo apt install fail2ban

# Конфигурация fail2ban
sudo tee /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3
EOF

sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Безопасность приложения

```bash
# Установка правильных прав доступа
sudo chown -R resume-bot:resume-bot /opt/resume-bot
sudo chmod 600 /opt/resume-bot/.env
sudo chmod +x /opt/resume-bot/scripts/*.sh

# Ограничение доступа к логам
sudo chmod 640 /var/log/resume-bot/*.log
```

## 📈 Масштабирование

### 1. Горизонтальное масштабирование

```yaml
# docker-compose.scale.yml
version: '3.8'

services:
  telegram-bot:
    deploy:
      replicas: 3
    depends_on:
      - redis
      - postgres

  redis:
    image: redis:alpine
    volumes:
      - redis_data:/data

  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: resume_bot
      POSTGRES_USER: resume_bot
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  redis_data:
  postgres_data:
```

### 2. Load Balancer

```nginx
upstream telegram_bots {
    server telegram-bot-1:8080;
    server telegram-bot-2:8080;
    server telegram-bot-3:8080;
}

server {
    location /webhook {
        proxy_pass http://telegram_bots;
    }
}
```

## 🆘 Восстановление после сбоев

### 1. Резервное копирование

```bash
# Скрипт ежедневного бэкапа
#!/bin/bash
BACKUP_DIR="/backup/resume-bot"
DATE=$(date +%Y%m%d)

mkdir -p $BACKUP_DIR

# Бэкап конфигурации
tar -czf $BACKUP_DIR/config_$DATE.tar.gz /opt/resume-bot/.env /opt/resume-bot/nginx.conf

# Бэкап логов
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz /var/log/resume-bot/ /opt/resume-bot/LOGS/

# Удаление старых бэкапов (>30 дней)
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

### 2. План восстановления

```bash
# 1. Остановка сервисов
sudo systemctl stop resume-bot-*
docker-compose down

# 2. Восстановление конфигурации
tar -xzf /backup/resume-bot/config_YYYYMMDD.tar.gz -C /

# 3. Перезапуск сервисов
sudo systemctl start resume-bot-*
docker-compose up -d

# 4. Проверка работоспособности
curl -f http://localhost:8080/health
```

---

🚀 **Поздравляем! Ваш Resume Bot готов к работе в продакшне.**

Не забудьте настроить мониторинг, регулярные бэкапы и обновления безопасности.