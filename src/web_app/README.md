# Веб-приложения AI Resume Assistant

Набор веб-приложений для работы с резюме и вакансиями с использованием AI.

## Структура приложений

### 1. Гап-анализ резюме (`gap_analysis/`)
- **Порт**: 8000
- **Функция**: Анализ соответствия резюме требованиям вакансии
- **Результат**: Детальный анализ с рекомендациями по улучшению

### 2. Сопроводительное письмо (`cover_letter/`)
- **Порт**: 8001  
- **Функция**: Генерация персонализированного сопроводительного письма
- **Результат**: Готовый текст письма с анализом качества

### 3. Чек-лист подготовки к интервью (`interview_checklist/`)
- **Порт**: 8002
- **Функция**: Персонализированный план подготовки к интервью
- **Результат**: 7 блоков подготовки с приоритизацией и временными оценками

### 4. Симуляция интервью (`interview_simulation/`)
- **Порт**: 8003
- **Функция**: Интерактивная симуляция интервью с AI-интервьюером
- **Результат**: PDF-отчет с полной транскрипцией и анализом
- **Особенности**: Расширенные настройки симуляции

## Общая функциональность

1. **Авторизация HH.ru** - OAuth авторизация для получения данных вакансий
2. **Парсинг PDF резюме** - извлечение данных из загруженных файлов
3. **Анализ вакансий** - получение данных через HH.ru API
4. **AI обработка** - использование соответствующих LLM сервисов
5. **Веб-интерфейс** - удобное отображение результатов

## Установка и запуск

### 1. Установка зависимостей

```bash
pip install fastapi uvicorn jinja2 python-multipart aiohttp
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

### 4. Запуск веб-приложений

#### Гап-анализ (порт 8000):
```bash
python -m src.web_app.gap_analysis.main
```

#### Сопроводительное письмо (порт 8001):
```bash
python -m src.web_app.cover_letter.main
```

#### Чек-лист подготовки к интервью (порт 8002):
```bash
python -m src.web_app.interview_checklist.main
```

#### Симуляция интервью (порт 8003):
```bash
python -m src.web_app.interview_simulation.main
```

## Использование

### Гап-анализ: http://localhost:8000
1. Авторизация на HH.ru
2. Загрузка PDF резюме
3. Ввод ссылки на вакансию
4. Получение детального анализа соответствия

### Сопроводительное письмо: http://localhost:8001
1. Авторизация на HH.ru
2. Загрузка PDF резюме
3. Ввод ссылки на целевую вакансию
4. Получение персонализированного письма

### Чек-лист подготовки к интервью: http://localhost:8002
1. Авторизация на HH.ru
2. Загрузка PDF резюме
3. Ввод ссылки на целевую вакансию
4. Получение персонализированного плана подготовки

### Симуляция интервью: http://localhost:8003
1. Авторизация на HH.ru
2. Загрузка PDF резюме
3. Ввод ссылки на целевую вакансию
4. Настройка параметров симуляции:
   - Количество раундов (3-7)
   - Уровень сложности
   - Тип HR-интервьюера
   - Области фокуса
   - Креативность AI (температура)
5. Получение PDF-отчета с полной транскрипцией

## Архитектура

```
src/web_app/
├── gap_analysis/           # Гап-анализ резюме
│   ├── main.py            # FastAPI приложение (порт 8000)
│   └── templates/
│       └── index.html     # HTML интерфейс
├── cover_letter/          # Сопроводительное письмо
│   ├── main.py            # FastAPI приложение (порт 8001)
│   ├── templates/
│   │   └── index.html     # HTML интерфейс
│   └── README.md          # Документация
├── interview_checklist/   # Чек-лист подготовки к интервью
│   ├── main.py            # FastAPI приложение (порт 8002)
│   ├── templates/
│   │   └── index.html     # HTML интерфейс
│   └── README.md          # Документация
├── interview_simulation/  # Симуляция интервью
│   ├── main.py            # FastAPI приложение (порт 8003)
│   ├── templates/
│   │   └── index.html     # HTML интерфейс
│   └── static/            # Статические файлы
└── README.md              # Общая документация
```

## Используемые компоненты

**Общие:**
- `src.parsers.pdf_resume_parser.PDFResumeParser` - парсинг PDF резюме
- `src.parsers.vacancy_extractor.VacancyExtractor` - извлечение данных вакансии
- `src.hh.api_client.HHApiClient` - работа с HH.ru API
- `src.hh.auth.HHAuthService` - авторизация HH.ru

**Специализированные:**
- `src.llm_gap_analyzer.LLMGapAnalyzer` - анализ соответствия резюме
- `src.llm_cover_letter.EnhancedLLMCoverLetterGenerator` - генерация писем
- `src.llm_interview_checklist.LLMInterviewChecklistGenerator` - чек-листы подготовки
- `src.llm_interview_simulation.LLMInterviewSimulator` - симуляция интервью

## Дополнительные возможности

### Симуляция интервью - Расширенные настройки
- **Количество раундов:** 3-7 раундов интервью
- **Уровень сложности:** Легкий, средний, сложный
- **Тип HR-интервьюера:** Профессиональный, дружелюбный, строгий, технический
- **Области фокуса:** Поведенческие вопросы, технические вопросы, лидерство, командная работа, коммуникация, решение проблем
- **Креативность AI:** Настройка температуры для разнообразия ответов
- **Прогресс в реальном времени:** Отслеживание выполнения симуляции
- **PDF-отчет:** Детальная транскрипция с анализом и рекомендациями

## Технические особенности

- Полное разделение логики между приложениями
- Использование одинаковой архитектуры OAuth
- Единый стиль интерфейса с разными цветовыми схемами
- Независимые порты для параллельной работы