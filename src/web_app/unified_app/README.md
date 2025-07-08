# AI Resume Assistant - Объединенное веб-приложение

Единое веб-приложение, объединяющее все 4 функции AI Resume Assistant в одном интерфейсе.

## Функции

### 🏠 Главная страница
- **URL**: `http://localhost:3000/`
- Навигация по всем функциям
- Авторизация HH.ru
- Современный адаптивный дизайн

### 📊 GAP-анализ резюме
- **URL**: `http://localhost:3000/gap-analysis`
- Анализ соответствия резюме вакансии
- Детальные рекомендации по улучшению
- PDF отчет с результатами

### ✉️ Сопроводительное письмо
- **URL**: `http://localhost:3000/cover-letter`
- Персонализированное письмо под вакансию
- Анализ качества и релевантности
- Готовый текст для отправки

### 📝 Чек-лист подготовки к интервью
- **URL**: `http://localhost:3000/interview-checklist`
- Персонализированный план подготовки
- Интерактивные чекбоксы с сохранением прогресса
- Оценка времени на подготовку

### 🎭 Симуляция интервью
- **URL**: `http://localhost:3000/interview-simulation`
- Интерактивное интервью с ИИ
- Настраиваемые параметры сложности
- Детальная обратная связь и оценки

## Запуск приложения

### Быстрый запуск (рекомендуется)
```bash
python run_unified_app.py
```

### Ручной запуск
```bash
python -m src.web_app.unified_app.main
```

### Обязательные предварительные шаги

1. **Запустите OAuth сервер** (ОБЯЗАТЕЛЬНО):
```bash
python -m src.callback_local_server.main
```

2. **Убедитесь, что настроены переменные окружения**:
```bash
export OPENAI_API_KEY=your_key
export HH_CLIENT_ID=your_id
export HH_CLIENT_SECRET=your_secret
```

## Архитектура

### Структура файлов
```
src/web_app/unified_app/
├── main.py                 # Основное FastAPI приложение
├── templates/              # HTML шаблоны
│   ├── index.html         # Главная страница с навигацией
│   ├── gap_analysis.html  # Страница GAP-анализа
│   ├── cover_letter.html  # Страница сопроводительного письма
│   ├── interview_checklist.html  # Страница чек-листа
│   └── interview_simulation.html # Страница симуляции
└── README.md              # Этот файл
```

### API эндпоинты

#### Навигация
- `GET /` - Главная страница
- `GET /gap-analysis` - Страница GAP-анализа
- `GET /cover-letter` - Страница сопроводительного письма
- `GET /interview-checklist` - Страница чек-листа
- `GET /interview-simulation` - Страница симуляции

#### Авторизация
- `POST /auth/hh` - Начало авторизации HH.ru
- `GET /auth/tokens` - Получение токенов из callback сервера

#### GAP-анализ
- `POST /gap-analysis` - Выполнение анализа
- `GET /download-gap-analysis/{analysis_id}` - Скачивание PDF

#### Сопроводительное письмо
- `POST /generate-cover-letter` - Генерация письма
- `GET /download-cover-letter/{letter_id}` - Скачивание PDF

#### Чек-лист интервью
- `POST /generate-interview-checklist` - Генерация чек-листа
- `GET /download-interview-checklist/{checklist_id}` - Скачивание PDF

#### Симуляция интервью
- `POST /start-interview-simulation` - Запуск симуляции
- `GET /simulation-progress/{simulation_id}` - Прогресс симуляции
- `GET /simulation-result/{simulation_id}` - Результаты симуляции

## Интеграция с существующими сервисами

Приложение использует все существующие LLM сервисы:
- `src.llm_gap_analyzer.llm_gap_analyzer.LLMGapAnalyzer`
- `src.llm_cover_letter.llm_cover_letter_generator.EnhancedLLMCoverLetterGenerator`
- `src.llm_interview_checklist.llm_interview_checklist_generator.LLMInterviewChecklistGenerator`
- `src.llm_interview_simulation.llm_interview_simulator.ProfessionalInterviewSimulator`

## Особенности

### Авторизация HH.ru
- Единая авторизация для всех функций
- Автоматическая проверка статуса при загрузке
- Хранение токенов в памяти (сессия)

### PDF генерация
- Использует существующие PDF генераторы из отдельных приложений
- Автоматическое создание временных файлов
- Уникальные имена файлов для скачивания

### Фоновые задачи
- Симуляция интервью выполняется в background
- Мониторинг прогресса в реальном времени
- Обработка ошибок и таймаутов

### Адаптивный дизайн
- Современный градиентный дизайн
- Адаптация под мобильные устройства
- Интерактивные элементы с анимациями

## Отладка

### Проверка зависимостей
```bash
python -c "from src.web_app.unified_app.main import app; print('OK')"
```

### Проверка отдельных сервисов
```bash
# GAP-анализ
python -c "from src.llm_gap_analyzer.llm_gap_analyzer import LLMGapAnalyzer; print('GAP OK')"

# Сопроводительное письмо  
python -c "from src.llm_cover_letter.llm_cover_letter_generator import EnhancedLLMCoverLetterGenerator; print('Letter OK')"

# Чек-лист
python -c "from src.llm_interview_checklist.llm_interview_checklist_generator import LLMInterviewChecklistGenerator; print('Checklist OK')"

# Симуляция
python -c "from src.llm_interview_simulation.llm_interview_simulator import ProfessionalInterviewSimulator; print('Simulation OK')"
```

### Логирование
Логи всех операций записываются через общую систему логирования проекта.

## Совместимость

- **Python**: 3.8+
- **FastAPI**: Совместимо с существующей версией
- **Браузеры**: Chrome, Firefox, Safari, Edge (современные версии)
- **OAuth сервер**: Требует запущенный `callback_local_server`

## Производительность

- Все LLM операции выполняются асинхронно
- Симуляция интервью - в фоновом режиме с мониторингом прогресса
- PDF генерация - по требованию
- Статические файлы кешируются браузером