# 🤝 Руководство для разработчиков

Добро пожаловать в AI Resume Assistant Bot! Это руководство поможет вам начать разработку и внести свой вклад в проект.

## 📋 Содержание

- [Начало работы](#начало-работы)
- [Структура проекта](#структура-проекта)
- [Стандарты кодирования](#стандарты-кодирования)
- [Процесс разработки](#процесс-разработки)
- [Тестирование](#тестирование)
- [Документация](#документация)
- [Создание Pull Request](#создание-pull-request)

## 🚀 Начало работы

### Требования для разработки

- **Python 3.8+**
- **Git**
- **Виртуальное окружение** (venv или conda)
- **IDE** (рекомендуется VS Code или PyCharm)

### Настройка окружения разработки

```bash
# 1. Форк репозитория
# Нажмите "Fork" на GitHub

# 2. Клонирование вашего форка
git clone https://github.com/YOUR_USERNAME/ai-resume-assistant-bot.git
cd ai-resume-assistant-bot

# 3. Добавление upstream репозитория
git remote add upstream https://github.com/ORIGINAL_OWNER/ai-resume-assistant-bot.git

# 4. Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate     # Windows

# 5. Установка зависимостей для разработки
pip install -r requirements.txt
pip install -r requirements-dev.txt  # если существует

# 6. Установка pre-commit хуков
pip install pre-commit
pre-commit install

# 7. Создание .env файла
cp .env.example .env
# Отредактируйте .env с вашими API ключами
```

### Структура окружения

```
ai-resume-assistant-bot/
├── .env                    # Ваши переменные окружения
├── .gitignore             # Игнорируемые файлы
├── requirements.txt       # Продакшн зависимости
├── requirements-dev.txt   # Зависимости для разработки
├── pytest.ini           # Конфигурация тестов
├── .pre-commit-config.yaml # Конфигурация pre-commit
├── src/                  # Исходный код
├── tests/               # Тесты
├── docs/               # Документация
└── scripts/           # Утилитарные скрипты
```

## 🏗️ Структура проекта

### Архитектура модулей

```
src/
├── config.py                   # Базовая конфигурация
├── callback_local_server/      # OAuth сервер
├── hh/                        # HeadHunter API интеграция
├── llm_gap_analyzer/          # GAP анализ резюме
├── llm_cover_letter/          # Генерация cover letter
├── llm_interview_checklist/   # Чек-листы подготовки
├── llm_interview_simulation/  # Симуляция интервью
├── models/                    # Pydantic модели данных
├── parsers/                   # Парсеры резюме и вакансий
└── tg_bot/                   # Telegram бот
    ├── bot/                  # Инициализация бота
    ├── handlers/             # Обработчики сообщений
    └── utils/                # Утилиты и константы
```

### Принципы архитектуры

1. **Модульность** — каждый компонент изолирован и независим
2. **Separation of Concerns** — разделение ответственности между модулями
3. **Dependency Injection** — использование настроек через переменные окружения
4. **Clean Code** — читаемый и поддерживаемый код
5. **Error Handling** — корректная обработка всех ошибок

## 📝 Стандарты кодирования

### Python Code Style

Мы следуем **PEP 8** с некоторыми дополнениями:

```python
# Импорты
import os
import sys
from typing import Dict, List, Optional

from pydantic import BaseModel
from aiogram import types

from src.models.resume_models import ResumeInfo
from src.utils.constants import DEFAULT_TIMEOUT

# Константы
MAX_RETRIES = 3
DEFAULT_MODEL = "gpt-4"

# Классы
class LLMServiceError(Exception):
    """Базовая ошибка LLM сервисов."""
    pass

class ResumeAnalyzer:
    """Анализатор резюме с использованием LLM."""
    
    def __init__(self, api_key: str):
        """
        Инициализация анализатора.
        
        Args:
            api_key: API ключ для OpenAI
        """
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
    
    async def analyze(self, resume: ResumeInfo) -> Optional[Dict[str, Any]]:
        """
        Анализ резюме.
        
        Args:
            resume: Данные резюме для анализа
            
        Returns:
            Результат анализа или None при ошибке
            
        Raises:
            LLMServiceError: При ошибках обращения к LLM
        """
        try:
            # Логика анализа
            pass
        except Exception as e:
            logger.error(f"Ошибка анализа резюме: {e}")
            raise LLMServiceError(f"Анализ невозможен: {e}")
```

### Инструменты форматирования

```bash
# Black для форматирования кода
black src/ tests/

# isort для сортировки импортов
isort src/ tests/

# flake8 для проверки стиля
flake8 src/ tests/

# mypy для проверки типов
mypy src/
```

### Конфигурация в pyproject.toml

```toml
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.mypy_cache
  | \.venv
  | venv
)/
'''

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

## 🔄 Процесс разработки

### Git Workflow

1. **Создание ветки**
   ```bash
   git checkout -b feature/amazing-new-feature
   ```

2. **Именование веток**
   - `feature/feature-name` — новая функциональность
   - `bugfix/bug-description` — исправление багов
   - `hotfix/critical-fix` — критические исправления
   - `docs/documentation-update` — обновление документации

3. **Коммиты**
   ```bash
   # Хорошие коммиты
   git commit -m "feat: добавить GAP анализ резюме"
   git commit -m "fix: исправить ошибку парсинга вакансий"
   git commit -m "docs: обновить README с инструкциями по установке"
   
   # Формат коммитов
   <type>: <description>
   
   # Типы коммитов:
   # feat: новая функциональность
   # fix: исправление бага
   # docs: изменения в документации
   # style: форматирование кода
   # refactor: рефакторинг
   # test: добавление тестов
   # chore: обновление зависимостей, конфигурации
   ```

### Добавление новой функциональности

#### 1. Создание нового LLM сервиса

```python
# src/llm_new_feature/__init__.py
from src.llm_new_feature.config import settings
from src.llm_new_feature.llm_new_feature_generator import LLMNewFeatureGenerator

# src/llm_new_feature/config.py
from src.config import BaseAppSettings

class OpenAIConfig(BaseAppSettings):
    api_key: str
    model_name: str 
    
    model_config = ConfigDict(
        env_file='.env',
        env_prefix="OPENAI_",
        extra='ignore'
    )

settings = OpenAIConfig()

# src/llm_new_feature/llm_new_feature_generator.py
class LLMNewFeatureGenerator:
    async def generate_feature(self, data: Dict[str, Any]) -> Optional[FeatureResult]:
        # Реализация
        pass
```

#### 2. Создание модели данных

```python
# src/models/new_feature_models.py
class FeatureResult(BaseModel):
    """Результат новой функции."""
    title: str = Field(..., description="Заголовок результата")
    content: str = Field(..., description="Основное содержимое")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        extra = "forbid"
```

#### 3. Создание обработчика Telegram

```python
# src/tg_bot/handlers/spec_handlers/new_feature_handler.py
async def start_new_feature_generation(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    logger.info(f"Запуск новой функции для пользователя {user_id}")
    
    # Получение данных
    user_data = await state.get_data()
    
    # Генерация
    result = await llm_generator.generate_feature(user_data)
    
    # Отправка результата
    await message.answer(format_result(result))
```

#### 4. Регистрация в системе

```python
# src/tg_bot/utils/states.py
class UserState(StatesGroup):
    # ... существующие состояния
    NEW_FEATURE_GENERATION = State()

# src/tg_bot/utils/keyboards.py
action_choice_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        # ... существующие кнопки
        [KeyboardButton(text="🆕 Новая функция")],
    ]
)

# src/tg_bot/handlers/router.py
dp.message.register(handle_new_feature_button, F.text == "🆕 Новая функция")
```

## 🧪 Тестирование

### Структура тестов

```
tests/
├── __init__.py
├── conftest.py              # Фикстуры pytest
├── unit/                    # Юнит тесты
│   ├── test_parsers.py
│   ├── test_llm_services.py
│   └── test_models.py
├── integration/             # Интеграционные тесты
│   ├── test_hh_api.py
│   └── test_telegram_bot.py
└── fixtures/               # Тестовые данные
    ├── resume_samples.json
    └── vacancy_samples.json
```

### Примеры тестов

```python
# tests/unit/test_parsers.py
import pytest
from src.parsers.resume_extractor import ResumeExtractor

class TestResumeExtractor:
    def setup_method(self):
        self.extractor = ResumeExtractor()
    
    def test_extract_valid_resume(self, sample_resume_data):
        """Тест извлечения валидного резюме."""
        result = self.extractor.extract_resume_info(sample_resume_data)
        
        assert result is not None
        assert result.title == "Python Developer"
        assert len(result.experience) > 0
    
    def test_extract_invalid_resume(self):
        """Тест обработки невалидных данных."""
        result = self.extractor.extract_resume_info({"invalid": "data"})
        
        assert result is None

# tests/conftest.py
@pytest.fixture
def sample_resume_data():
    return {
        "title": "Python Developer",
        "skills": "Python, Django, REST API",
        "experience": [
            {
                "position": "Senior Python Developer",
                "description": "Разработка веб-приложений",
                "start": "2020-01-01",
                "end": "2023-01-01"
            }
        ]
    }

@pytest.fixture
def mock_openai_client():
    """Mock клиент OpenAI для тестов."""
    class MockClient:
        async def chat_completions_create(self, **kwargs):
            return MockResponse({"content": "test response"})
    
    return MockClient()
```

### Запуск тестов

```bash
# Все тесты
pytest

# Юнит тесты
pytest tests/unit/

# С покрытием кода
pytest --cov=src --cov-report=html

# Конкретный тест
pytest tests/unit/test_parsers.py::TestResumeExtractor::test_extract_valid_resume

# Тесты с маркерами
pytest -m "not slow"  # исключить медленные тесты
pytest -m "integration"  # только интеграционные тесты
```

### Моки для внешних сервисов

```python
# tests/mocks/openai_mock.py
class MockOpenAIClient:
    def __init__(self, responses: Dict[str, str]):
        self.responses = responses
    
    async def chat_completions_create(self, messages, **kwargs):
        prompt = messages[-1]["content"]
        
        # Простая логика для мока
        if "gap analysis" in prompt.lower():
            return MockResponse(self.responses["gap_analysis"])
        elif "cover letter" in prompt.lower():
            return MockResponse(self.responses["cover_letter"])
        
        return MockResponse({"content": "default response"})

# Использование в тестах
@pytest.fixture
def mock_openai():
    responses = {
        "gap_analysis": '{"suggested_title": "Senior Python Developer"}',
        "cover_letter": '{"subject": "Application for Python Developer"}'
    }
    return MockOpenAIClient(responses)
```

## 📚 Документация

### Docstrings

Используйте Google стиль docstrings:

```python
def analyze_resume(resume_data: Dict[str, Any], vacancy_data: Dict[str, Any]) -> Optional[AnalysisResult]:
    """
    Анализирует соответствие резюме требованиям вакансии.
    
    Функция выполняет детальный анализ резюме кандидата относительно
    требований конкретной вакансии и возвращает структурированные
    рекомендации по улучшению.
    
    Args:
        resume_data: Структурированные данные резюме, включающие:
            - title: желаемая должность
            - skills: описание навыков
            - experience: список опыта работы
        vacancy_data: Данные вакансии, включающие:
            - description: описание вакансии
            - key_skills: требуемые навыки
    
    Returns:
        AnalysisResult объект с результатами анализа, содержащий:
            - gap_analysis: выявленные пробелы
            - recommendations: рекомендации по улучшению
        Возвращает None в случае ошибки анализа.
    
    Raises:
        ValueError: Если входные данные имеют неверный формат
        LLMServiceError: При ошибках обращения к языковой модели
        
    Example:
        >>> resume = {"title": "Python Developer", "skills": "Python, Django"}
        >>> vacancy = {"description": "Senior Python Developer needed"}
        >>> result = analyze_resume(resume, vacancy)
        >>> print(result.recommendations)
    """
```

### Обновление документации

При добавлении новых функций обновите:

1. **README.md** — основное описание
2. **docs/USER_GUIDE.md** — инструкции для пользователей
3. **docs/API.md** — техническую документацию API
4. **docs/ARCHITECTURE.md** — архитектурные изменения

## 📬 Создание Pull Request

### Чек-лист перед созданием PR

- [ ] Код проходит все тесты (`pytest`)
- [ ] Код соответствует стилю (`black`, `isort`, `flake8`)
- [ ] Добавлены тесты для новой функциональности
- [ ] Обновлена документация
- [ ] Коммиты имеют осмысленные сообщения
- [ ] Проверена работа в development окружении

### Шаблон Pull Request

```markdown
## Описание

Краткое описание изменений и их цели.

## Тип изменений

- [ ] 🐛 Исправление бага
- [ ] ✨ Новая функциональность
- [ ] 💥 Breaking change
- [ ] 📚 Обновление документации
- [ ] 🎨 Улучшение кода (рефакторинг)

## Тестирование

- [ ] Юнит тесты прошли
- [ ] Интеграционные тесты прошли
- [ ] Мануальное тестирование выполнено

## Чек-лист

- [ ] Код следует стилю проекта
- [ ] Самопроверка кода выполнена
- [ ] Код прокомментирован в сложных местах
- [ ] Изменения в документации сделаны
- [ ] Изменения не создают новых предупреждений
- [ ] Добавлены тесты для изменений
- [ ] Все тесты проходят

## Скриншоты (если применимо)

Добавьте скриншоты для демонстрации изменений UI.
```

### Процесс ревью

1. **Автоматические проверки** — CI/CD должны пройти
2. **Code Review** — минимум 1 аппрув от мейнтейнера
3. **Тестирование** — проверка работоспособности
4. **Merge** — слияние в основную ветку

## 🐛 Отладка и диагностика

### Полезные команды

```bash
# Проверка логов
tail -f LOGS/*.log

# Проверка конфигурации
python scripts/validate_config.py

# Запуск в режиме отладки
DEBUG=true python -m src.tg_bot.main

# Профилирование производительности
python -m cProfile -o profile.stats -m src.tg_bot.main
```

### Отладочные утилиты

```python
# Логирование для отладки
import logging
logger = logging.getLogger(__name__)

def debug_function(data):
    logger.debug(f"Input data: {data}")
    
    # Вывод промежуточных состояний
    logger.debug(f"Processing step 1: {intermediate_result}")
    
    return result

# Декоратор для измерения времени
import time
from functools import wraps

def measure_time(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start
        logger.info(f"{func.__name__} выполнился за {duration:.2f}s")
        return result
    return wrapper
```

## 🤝 Взаимодействие с сообществом

### Каналы связи

- **GitHub Issues** — баги и предложения функций
- **GitHub Discussions** — обсуждения и вопросы
- **Code Review** — обратная связь по коду

### Создание Issue

При создании issue используйте шаблоны:

**Bug Report:**
```markdown
**Описание бага**
Краткое и четкое описание проблемы.

**Шаги для воспроизведения**
1. Перейти в '...'
2. Нажать на '....'
3. Прокрутить до '....'
4. Увидеть ошибку

**Ожидаемое поведение**
Описание того, что должно было произойти.

**Скриншоты**
Приложите скриншоты если применимо.

**Среда:**
 - ОС: [например, iOS]
 - Версия: [например, 22]
```

### Менторство

Новые контрибьюторы всегда приветствуются! Если вы новичок:

1. Начните с issues помеченных `good first issue`
2. Читайте код других контрибьюторов
3. Задавайте вопросы в Discussions
4. Участвуйте в Code Review

---

🎉 **Спасибо за ваш вклад в развитие AI Resume Assistant Bot!**

Ваши идеи и код помогают делать инструмент лучше для всего IT-сообщества.