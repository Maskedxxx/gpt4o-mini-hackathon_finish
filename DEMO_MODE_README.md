# 🎭 Система демо-режима для AI Resume Assistant

Система кеширования ответов LLM для быстрой демонстрации функций без реальных вызовов OpenAI API.

## 🎯 Назначение

Демо-режим позволяет:
- **Быстрые демонстрации** - ответы за < 5 секунд вместо 30-60 секунд
- **Экономия API токенов** - нет вызовов к OpenAI во время демо
- **Надежность демо** - предсказуемые качественные ответы
- **Fallback механизм** - автоматический переход к живому режиму при отсутствии кеша

## 📁 Структура файлов

```
demo_cache/
├── resume_profiles/           # Профили тестовых резюме
│   ├── junior_profile.json   # Джуниор резюме
│   ├── middle_profile.json   # Мидл резюме  
│   └── senior_profile.json   # Сеньор резюме
├── vacancy_data/              # Данные тестовой вакансии
│   └── target_vacancy.json   # Распарсенная вакансия
├── cached_responses/          # Кешированные ответы LLM
│   ├── cover_letter/         # Сопроводительные письма
│   │   ├── junior_response.json
│   │   ├── middle_response.json
│   │   └── senior_response.json
│   ├── interview_checklist/  # Чек-листы подготовки
│   │   ├── junior_response.json
│   │   ├── middle_response.json
│   │   └── senior_response.json
│   └── interview_simulation/ # Симуляции интервью
│       ├── junior_response.json
│       ├── middle_response.json
│       └── senior_response.json
└── generated_pdfs/           # Заготовленные PDF файлы
    ├── cover_letter/
    │   ├── junior_cover_letter.pdf
    │   ├── middle_cover_letter.pdf
    │   └── senior_cover_letter.pdf
    ├── interview_checklist/
    │   ├── junior_interview_checklist.pdf
    │   ├── middle_interview_checklist.pdf
    │   └── senior_interview_checklist.pdf
    └── interview_simulation/
        ├── junior_interview_simulation.pdf
        ├── middle_interview_simulation.pdf
        └── senior_interview_simulation.pdf
```

## 🚀 Быстрый старт

### 1. Генерация демо-кеша

```bash
# Убедитесь что API ключ настроен
export OPENAI_API_KEY="your-api-key"

# Отключите демо-режим для генерации
export DEMO_MODE=false

# Запустите генератор
python generate_demo_cache.py
```

### 2. Активация демо-режима

```bash
# Включите демо-режим
export DEMO_MODE=true

# Запустите приложение
python run_unified_app.py

# Откройте http://localhost:3000
```

### 3. Тестирование

```bash
# Запустите тесты
python test_demo_mode.py
```

## ⚙️ Управление режимами

### Переменная окружения DEMO_MODE

| Значение | Режим | Поведение |
|----------|-------|-----------|
| `true`, `1`, `yes`, `on` | 🎭 **DEMO** | Использует кешированные ответы |
| `false`, `0`, `no`, `off` | 🌐 **LIVE** | Делает реальные вызовы OpenAI |
| _не установлена_ | 🌐 **LIVE** | По умолчанию живой режим |

### Логика определения уровня профиля

Система автоматически определяет уровень кандидата по резюме:

**Junior индикаторы:**
- Ключевые слова: "junior", "джуниор", "начинающий", "стажер", "без опыта", "1 год"
- Опыт: < 2 лет

**Middle индикаторы:**
- Ключевые слова: "middle", "мидл", "опытный", "3+ года", "4+ года", "5+ лет"
- Опыт: 2-5 лет

**Senior индикаторы:**
- Ключевые слова: "senior", "lead", "architect", "team lead", "руководитель", "архитектор"
- Опыт: 5+ лет

## 🔧 Технические детали

### Интеграция в LLM сервисы

Каждый LLM сервис проверяет демо-режим:

```python
demo_manager = DemoManager()

if demo_manager.is_demo_mode():
    profile_level = demo_manager.detect_profile_level(resume_data)
    cached_response = demo_manager.load_cached_response(service_type, profile_level)
    
    if cached_response:
        return Model.model_validate(cached_response)

# Fallback на реальную генерацию
return await generate_real_response(...)
```

### Поддерживаемые сервисы

✅ **Cover Letter Generator** - кеширование + демо PDF
✅ **Interview Checklist Generator** - кеширование + демо PDF  
✅ **Interview Simulator** - кеширование + демо PDF
❌ **GAP Analyzer** - всегда живой режим (согласно ТЗ)

### PDF демо-файлы

- Заготовленные PDF возвращаются вместо генерации на лету
- Быстрая отдача файлов через `FileResponse`
- Автоматическое определение уровня по ID запроса

## 📊 Мониторинг и статистика

### Получение статистики

```python
from src.demo_cache.demo_manager import DemoManager

demo_manager = DemoManager()
stats = demo_manager.get_cache_stats()

print(f"Режим: {'DEMO' if stats['demo_mode_active'] else 'LIVE'}")
print(f"Кешированных ответов: {stats['total_cached_responses']}")
print(f"PDF файлов: {stats['total_generated_pdfs']}")
```

### Логирование

Система логирует все операции с демо-кешем:

```
🎭 Demo mode is ACTIVE - using cached responses
📥 Loaded cached response: cover_letter/junior_response.json
🎭 Using cached cover letter response for junior profile
📄 Found pre-generated PDF: cover_letter/junior_cover_letter.pdf
🎭 Serving demo PDF: /path/to/demo_cache/generated_pdfs/...
```

## 🛠️ Обслуживание

### Обновление кеша

Для обновления кеша с новыми данными:

```bash
# Переключитесь в живой режим
export DEMO_MODE=false

# Перегенерируйте кеш
python generate_demo_cache.py

# Вернитесь в демо-режим
export DEMO_MODE=true
```

### Очистка кеша

```bash
# Удалите директорию кеша
rm -rf demo_cache/

# Регенерируйте
python generate_demo_cache.py
```

### Добавление новых профилей

1. Отредактируйте `SAMPLE_RESUMES` в `generate_demo_cache.py`
2. Перегенерируйте кеш
3. Протестируйте новые профили

## 🚨 Важные ограничения

### Что НЕ кешируется

- **GAP-анализ** - всегда делает реальные вызовы OpenAI
- **Ошибки валидации** - при некорректном кеше fallback на реальную генерацию
- **Новые типы запросов** - если профиль не распознан, используется middle как fallback

### Требования

- **Python 3.8+**
- **OpenAI API ключ** - для первичной генерации кеша
- **Все зависимости** - см. `requirements.txt`
- **Доступ к файловой системе** - для чтения/записи кеша

## 🔍 Диагностика проблем

### Проблема: Демо-режим не активируется

```bash
# Проверьте переменную окружения
echo $DEMO_MODE

# Убедитесь что значение корректное
export DEMO_MODE=true
```

### Проблема: Кеш не найден

```bash
# Проверьте существование файлов
ls -la demo_cache/cached_responses/

# Регенерируйте кеш
python generate_demo_cache.py
```

### Проблема: PDF не отдаются

```bash
# Проверьте PDF файлы
ls -la demo_cache/generated_pdfs/

# Проверьте права доступа
chmod -R 755 demo_cache/
```

### Проблема: Fallback не работает

- Убедитесь что OpenAI API ключ настроен
- Проверьте логи на ошибки валидации
- Убедитесь что `OPENAI_API_ENABLED=true`

## 📞 Поддержка

При возникновении проблем:

1. **Запустите тесты:** `python test_demo_mode.py`
2. **Проверьте логи** приложения
3. **Убедитесь в корректности** переменных окружения
4. **Регенерируйте кеш** если файлы повреждены

---

**🎭 Система демо-режима готова к использованию!**

Наслаждайтесь быстрыми демонстрациями без ожидания OpenAI API! 🚀