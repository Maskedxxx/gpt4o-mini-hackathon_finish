# Веб-приложение AI Resume Assistant

Простое веб-приложение для выполнения гап-анализа резюме с использованием всей существующей логики проекта.

## Функциональность

1. **Авторизация HH.ru** - OAuth авторизация для получения токена доступа
2. **Загрузка PDF резюме** - использует `PDFResumeParser` для обработки
3. **Анализ вакансии** - получает данные через HH.ru API
4. **Гап-анализ** - использует существующий `LLMGapAnalyzer`
5. **Результаты** - веб-интерфейс для просмотра анализа

## Установка и запуск

### 1. Установка зависимостей

```bash
pip install fastapi uvicorn jinja2 python-multipart
```

### 2. Настройка окружения

Убедитесь, что файл `.env` содержит:
```bash
OPENAI_API_KEY=your_openai_api_key
HH_CLIENT_ID=your_hh_client_id
HH_CLIENT_SECRET=your_hh_client_secret
HH_REDIRECT_URI=http://localhost:8080/callback
```

### 3. Запуск OAuth сервера

В одном терминале:
```bash
python -m src.callback_local_server.main
```

### 4. Запуск веб-приложения

В другом терминале:
```bash
python -m src.web_app.main
```

Приложение будет доступно по адресу: http://localhost:8000

## Использование

1. Откройте http://localhost:8000 в браузере
2. Нажмите "Авторизоваться на HH.ru" для получения токена
3. Загрузите PDF резюме
4. Введите ссылку на вакансию HH.ru
5. Нажмите "Выполнить гап-анализ"
6. Дождитесь результатов

## Архитектура

```
src/web_app/
├── main.py              # FastAPI приложение
├── templates/
│   └── index.html       # HTML шаблон
└── README.md           # Документация
```

## Используемые компоненты проекта

- `src.parsers.pdf_resume_parser.PDFResumeParser` - парсинг PDF резюме
- `src.parsers.vacancy_extractor.VacancyExtractor` - извлечение данных вакансии
- `src.hh.api_client.HHApiClient` - работа с HH.ru API
- `src.hh.auth.HHAuthService` - авторизация HH.ru
- `src.llm_gap_analyzer.LLMGapAnalyzer` - анализ резюме

## Упрощения

Для простоты в текущей версии:
- Токены хранятся в памяти (не в базе данных)
- Простой HTML/CSS без фреймворков
- Минимальная обработка ошибок
- Нет персистентности данных

## Возможные улучшения

1. Добавить базу данных для пользователей и токенов
2. Реализовать полноценный OAuth flow
3. Добавить React/Vue.js фронтенд
4. Кэширование результатов анализа
5. Расширенная обработка ошибок
6. Логирование и мониторинг