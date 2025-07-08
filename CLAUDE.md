# CLAUDE.md

AI Resume Assistant - полная система помощи соискателям с анализом резюме, генерацией сопроводительных писем и подготовкой к интервью.

## Архитектура системы

### Фронтенды
- **Telegram Bot** (`src/tg_bot/`) - основной интерфейс, aiogram 3.x + FSM
- **Unified Web App** (`src/web_app/unified_app/`) - объединенное FastAPI приложение (порт 3000):
  - Единая навигация по всем функциям
  - GAP-анализ резюме
  - Генерация сопроводительного письма
  - Чек-лист подготовки к интервью
  - Симуляция интервью
- **Individual Web Apps** (`src/web_app/`) - 4 отдельных FastAPI приложения:
  - Gap Analysis (8000) - анализ соответствия резюме вакансии
  - Cover Letter (8001) - генерация сопроводительных писем
  - Interview Checklist (8002) - чек-листы подготовки к интервью  
  - Interview Simulation (8003) - симуляция интервью с PDF отчетами

### Бэкенд сервисы
- **OAuth Server** (`src/callback_local_server/`) - FastAPI сервер для HH.ru OAuth (порт 8080)
- **HH Integration** (`src/hh/`) - клиент API, авторизация, управление токенами
- **LLM Services** (`src/llm_*/`) - специализированные AI процессоры:
  - `llm_gap_analyzer` - анализ разрыва резюме-вакансия
  - `llm_cover_letter` - персонализированные письма  
  - `llm_interview_checklist` - планы подготовки к интервью
  - `llm_interview_simulation` - симуляция интервью с агентами

### Данные и парсинг
- **Models** (`src/models/`) - Pydantic модели для валидации данных
- **Parsers** (`src/parsers/`) - извлечение данных:
  - `pdf_resume_parser.py` - парсинг PDF резюме через OpenAI structured output
  - `vacancy_extractor.py` - извлечение данных вакансий из HH.ru API

## Критические особенности данных

### Резюме (через pdf_resume_parser.py)
```python
# total_experience приходит как int (месяцы), НЕ как dict
total_experience: int = 27  # 27 месяцев опыта

# skills может быть list или string
skills: Union[List[str], str] = ["Python", "Django"] или "Python, Django"
```

### Вакансии (через HH.ru API)
```python
# experience может быть dict или int
experience: Union[Dict, int] = {"id": "between1And3"} или 1

# key_skills всегда list of dict
key_skills: List[Dict] = [{"name": "Python"}, {"name": "Django"}]
```

## Потоки данных

### Telegram Bot поток
1. User OAuth → HH.ru access_token
2. User загружает PDF → `pdf_resume_parser.parse_pdf_resume()` → ResumeInfo
3. User дает ссылку на вакансию → `HHApiClient.request()` → `vacancy_extractor.extract_vacancy_info()` → VacancyInfo  
4. ResumeInfo + VacancyInfo → LLM Service → обработанный результат
5. Результат форматируется для Telegram

### Web App поток  
1. User OAuth через web → callback на localhost:8080
2. PDF upload → `pdf_resume_parser.parse_pdf_resume()` → ResumeInfo
3. Vacancy URL → HH API → VacancyInfo
4. `.model_dump()` → dict для передачи в LLM Service
5. Background task для длительных операций (симуляция)
6. HTML результаты + PDF генерация

## LLM Service архитектура

### Общий паттерн
```python
# Все LLM сервисы имеют:
config.py          # OpenAI настройки
formatter.py        # Подготовка данных для промптов  
main_service.py     # Основная логика + API взаимодействие
```

### Interview Simulation особенности
```python
# Поддерживает кастомные настройки через:
simulator.set_custom_config({
    "target_rounds": 5,
    "difficulty_level": "medium", 
    "hr_persona": "professional"
})

# Использует агентную архитектуру:
HR Agent ↔ Candidate Agent → Dialog → Assessment → PDF Report
```

## Запуск системы

### Environment Setup
```bash
# Копировать env_example.sh → .env
OPENAI_API_KEY=sk-...
HH_CLIENT_ID=...
HH_CLIENT_SECRET=...
HH_REDIRECT_URI=http://localhost:8080/callback
```

### Production запуск
```bash
# 1. OAuth сервер (ОБЯЗАТЕЛЬНО первым)
python -m src.callback_local_server.main

# 2. Telegram bot
python -m src.tg_bot.main

# 3. Unified Web App (рекомендуется для демо)
python run_unified_app.py                    # :3000 - все функции в одном приложении

# 4. Individual Web apps (опционально, альтернатива unified)
python -m src.web_app.gap_analysis.main      # :8000
python -m src.web_app.cover_letter.main      # :8001  
python -m src.web_app.interview_checklist.main   # :8002
python -m src.web_app.interview_simulation.main  # :8003
```

## Debug и разработка

### Debug scripts
```bash
# Каждый LLM сервис имеет debug утилиты в tests/debug_*/
python tests/debug_gap/debug_formatter.py        # Тест форматирования
python tests/debug_gap/debug_gap_response.py     # Тест LLM ответов
```

### Важные паттерны кода

#### Type Safety для данных
```python
# ВСЕГДА проверять типы перед .get()
total_experience = resume_data.get('total_experience', {})
if isinstance(total_experience, dict):
    months = total_experience.get('months', 0)
elif isinstance(total_experience, (int, float)):
    months = total_experience
else:
    months = 0
```

#### Web App Background Tasks
```python
# Длительные операции в background
asyncio.create_task(run_simulation_background(id, resume_dict, vacancy_dict, config))

# Прогресс через in-memory storage
simulation_progress_storage[id] = {"status": "running", "progress": 50}
```

## Состояния и ошибки

### Telegram Bot States
- `UNAUTHORIZED` → OAuth required
- `AUTHORIZED` → Готов к работе
- `*_PREPARATION` → Обработка данных
- `*_GENERATION` → LLM обработка

### Частые ошибки и решения
```python
# 'int' object has no attribute 'get' 
# → Проверить isinstance() перед .get()

# 'NoneType' object has no attribute 'position_title'
# → Проверить что LLM service вернул результат

# 'CompetencyScore' object has no attribute 'name'  
# → Использовать comp.area.value вместо comp.name
```

## Deployment заметки

- OAuth сервер ДОЛЖЕН быть запущен первым
- Web apps независимы, могут запускаться в любом порядке
- PDF генерация требует шрифты в `fonts/`
- Логи пишутся в `LOGS/` с разделением по сервисам
- Нет persistent storage - все в памяти