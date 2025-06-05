# СИСТЕМА: AI Job Assistant

## ОБЩЕЕ ОПИСАНИЕ [#OVERVIEW]
**Назначение**: Telegram-бот для помощи в поиске работы через интеграцию с HeadHunter и AI-генерацию контента
**Основные функции**:
1. GAP-анализ резюме относительно вакансии
2. Генерация персонализированных сопроводительных писем
3. Создание чек-листа подготовки к интервью
4. Симуляция интервью с оценкой компетенций

**Технологический стек**:
- Python, aiogram (Telegram Bot API)
- HeadHunter API (OAuth2, REST)
- OpenAI API (GPT для генерации контента)
- Pydantic (валидация данных)
- LangSmith (опциональный мониторинг)

## ТОЧКА ВХОДА [#ENTRY_POINT]
**Запуск**: `src/tg_bot/main.py`
- Функция: `main()` - инициализация и запуск polling
- Регистрация: `register_handlers(dp)` из `src/tg_bot/handlers/router.py`
**Технология**: aiogram (Telegram Bot API)
**Хранилище**: MemoryStorage (in-memory FSM)

## СОСТОЯНИЯ ПОЛЬЗОВАТЕЛЯ [#USER_STATES]
**Файл**: `src/tg_bot/utils/states.py`
**Класс**: `UserState(StatesGroup)`

Переходы состояний:
- INITIAL -> UNAUTHORIZED (после /start)
- UNAUTHORIZED -> AUTH_WAITING (начало OAuth)
- AUTH_WAITING -> AUTHORIZED (успешная авторизация)
- AUTHORIZED -> RESUME_PREPARATION (кнопка "Редактировать резюме")
- RESUME_PREPARATION -> VACANCY_PREPARATION (после загрузки резюме)
- VACANCY_PREPARATION -> [GAP_ANALYZE, COVER_LETTER, INTERVIEW_CHECKLIST, INTERVIEW_SIMULATION]

## FLOW АВТОРИЗАЦИИ [#AUTH_FLOW]
**Файлы**:
- `src/tg_bot/handlers/command_handlers.py`: `cmd_auth()`
- `src/tg_bot/handlers/spec_handlers/auth_handler.py`: `start_auth_polling()`, `check_auth_code()`
- `src/hh/auth.py`: `HHAuthService.get_auth_url()`

**Процесс**:
1. **Запрос**: Пользователь нажимает кнопку авторизации
2. **OAuth**: Отправка ссылки на hh.ru для входа
3. **Callback**: HH отправляет код на локальный сервер
4. **Polling**: Бот проверяет наличие кода каждые 3 сек (макс. 5 мин)
5. **Exchange**: `HHCodeExchanger.exchange_code()` обменивает код на токены
6. **Сохранение**: Токены сохраняются в FSM состоянии
7. **Результат**: Пользователь получает доступ к функциям бота

## ОСНОВНЫЕ WORKFLOW [#MAIN_WORKFLOWS]

### 1. Подготовка данных [#DATA_PREPARATION]
**Файлы обработчиков**:
- `src/tg_bot/handlers/spec_handlers/resume_handler.py`: `handle_resume_link()`
- `src/tg_bot/handlers/spec_handlers/vacancy_handler.py`: `handle_vacancy_link()`

**Процесс загрузки резюме**:
1. **Ввод ссылки**: Пользователь отправляет ссылку на резюме hh.ru
2. **Валидация**: `is_valid_resume_link()` - проверка формата ссылки
3. **Извлечение ID**: `extract_resume_id()` - получение ID из URL
4. **API запрос**: `HHApiClient.request()` получает данные по ID
5. **Парсинг**: `ResumeExtractor.extract_resume_info()` извлекает структурированные данные
6. **Сохранение**: Данные сохраняются в FSM состоянии
7. **Переход**: Состояние -> VACANCY_PREPARATION

**Процесс загрузки вакансии**:
1. **Ввод ссылки**: Пользователь отправляет ссылку на вакансию hh.ru
2. **Валидация**: `is_valid_vacancy_link()` - проверка формата
3. **Извлечение ID**: `extract_vacancy_id()` - получение ID
4. **API запрос**: `HHApiClient.request()` получает данные
5. **Парсинг**: `VacancyExtractor.extract_vacancy_info()` извлекает данные
6. **Показ меню**: Отображается `action_choice_keyboard` с 4 функциями
7. **Переход**: Состояние -> AUTHORIZED

**Парсер резюме [#RESUME_PARSER]**:
**Файл**: `src/parsers/resume_extractor.py`
**Класс**: `ResumeExtractor`
**Методы**:
- `extract_resume_info()` - основной метод парсинга
- `_remove_html_tags()` - очистка от HTML
- `_extract_education()` - парсинг образования

**Извлекаемые данные из резюме**:
- title - желаемая должность
- skills, skill_set - навыки
- experience - опыт работы (позиция, период, описание)
- education - образование (уровень, основное, дополнительное)
- languages - знание языков
- salary - зарплатные ожидания
- professional_roles - профессиональные роли
- employments, schedules - типы занятости и графики
- relocation - готовность к релокации

**Парсер вакансий [#VACANCY_PARSER]**:
**Файл**: `src/parsers/vacancy_extractor.py`
**Класс**: `VacancyExtractor`
**Методы**:
- `extract_vacancy_info()` - основной метод парсинга
- `_remove_html_tags()` - очистка от HTML

**Извлекаемые данные из вакансии**:
- description - описание вакансии (очищенное от HTML)
- key_skills - требуемые ключевые навыки
- employment_form - форма занятости
- experience - требуемый опыт работы
- schedule - график работы
- employment - тип занятости

### 2. GAP-анализ резюме [#GAP_ANALYSIS_FLOW]
**Точка входа**: `handle_gap_analysis_button()` -> `start_gap_analysis()`
**Обработчик**: `src/tg_bot/handlers/spec_handlers/gap_analyzer_handler.py`

**Компоненты**:
- `LLMGapAnalyzer` (`src/llm_gap_analyzer/llm_gap_analyzer.py`)
- Модель данных: `EnhancedResumeTailoringAnalysis` (`src/models/gap_analysis_models.py`)
- Форматтеры: `format_resume_data()`, `format_vacancy_data()` (`src/llm_gap_analyzer/formatter.py`)

**Процесс**:
1. **Извлечение данных**: Получение `parsed_resume` и `parsed_vacancy` из FSM
2. **Подготовка промптов**: 
   - Системный промпт с методологией HR-анализа
   - Форматирование данных резюме и вакансии в Markdown
3. **LLM обработка**: 
   - OpenAI API (модель из конфига)
   - Structured output через `response_format`
   - LangSmith трейсинг для мониторинга
4. **Форматирование результата**:
   - `format_primary_screening()` - первичный скрининг (7-15 сек)
   - `format_requirements_analysis()` - анализ MUST/NICE/BONUS требований
   - `format_quality_assessment()` - оценка качества резюме (шкала 1-10)
   - `format_recommendations()` - критичные/важные/желательные рекомендации
   - `format_final_conclusion()` - процент соответствия и рекомендация по найму
5. **Отправка результата**: По частям с паузами через `send_enhanced_gap_analysis_in_parts()`

### 3. Генерация рекомендательного письма [#COVER_LETTER_FLOW]
**Точка входа**: `handle_cover_letter_button()` -> `start_cover_letter_generation()`
**Обработчик**: `src/tg_bot/handlers/spec_handlers/cover_letter_handler.py`

**Компоненты**:
- `EnhancedLLMCoverLetterGenerator` (`src/llm_cover_letter/llm_cover_letter_generator.py`)
- Модель данных: `EnhancedCoverLetter` (`src/models/cover_letter_models.py`)

**Процесс**:
1. **Анализ**: Компания, вакансия, соответствие навыков
2. **Генерация**: Персонализированное письмо с оценками качества
3. **Структура письма**:
   - Subject line и приветствие
   - Opening hook (захват внимания)
   - Company interest (интерес к компании)
   - Relevant experience (релевантный опыт)
   - Value demonstration (демонстрация ценности)
   - Growth mindset (готовность к развитию)
   - Professional closing и подпись
4. **Оценки качества**: персонализация, профессионализм, релевантность (1-10)
5. **Форматирование**: По частям с preview, анализом соответствия, текстом и рекомендациями

### 4. Чек-лист подготовки к интервью [#INTERVIEW_CHECKLIST_FLOW]
**Точка входа**: `handle_interview_checklist_button()` -> `start_interview_checklist_generation()`
**Обработчик**: `src/tg_bot/handlers/spec_handlers/interview_checklist_handler.py`

**Компоненты**:
- `LLMInterviewChecklistGenerator` (`src/llm_interview_checklist/llm_interview_checklist_generator.py`)
- Модели: `InterviewChecklist`, `ProfessionalInterviewChecklist`

**Профессиональная версия (7 блоков)**:
1. **Техническая подготовка**: профильные знания, недостающие технологии, практические задачи
2. **Поведенческая подготовка**: типовые вопросы, самопрезентация, STAR-методика
3. **Изучение компании**: исследование, продукты, вопросы работодателю
4. **Технический стек**: требования вакансии, технологии компании, терминология
5. **Практические упражнения**: по уровням сложности (базовый/средний/продвинутый)
6. **Настройка окружения**: оборудование, место, аккаунты, внешний вид
7. **Дополнительные действия**: рекомендации, профили, документы, настрой

**Метаданные**: временные оценки, приоритеты (критично/важно/желательно), персонализация по уровню кандидата

### 5. Симуляция интервью [#INTERVIEW_SIMULATION_FLOW]
**Точка входа**: `handle_interview_simulation_button()` -> `start_interview_simulation()`
**Обработчик**: `src/tg_bot/handlers/spec_handlers/interview_simulation_handler.py`

**Компоненты**:
- `ProfessionalInterviewSimulator` (`src/llm_interview_simulation/llm_interview_simulator.py`)
- `ProfessionalInterviewPDFGenerator` (`src/llm_interview_simulation/pdf_generator.py`)
- Модель: `InterviewSimulation` (`src/models/interview_simulation_models.py`)

**Процесс**:
1. **Анализ профиля**: определение уровня и роли кандидата
2. **Многораундовая симуляция** (до 6 раундов):
   - Знакомство и коммуникация
   - Техническая экспертиза
   - Поведенческие вопросы (STAR)
   - Решение проблем
   - Культурное соответствие
   - Лидерские качества
3. **Оценка компетенций** (9 областей): техническая экспертиза, коммуникация, решение проблем, командная работа, лидерство, адаптивность, обучаемость, мотивация, культурное соответствие
4. **Генерация PDF отчета**: полный диалог, оценки, рекомендации, визуализация
5. **Результат**: рекомендация (hire/conditional_hire/reject), средний балл, сильные/слабые стороны

## UI КОМПОНЕНТЫ [#UI_COMPONENTS]
**Файл**: `src/tg_bot/utils/keyboards.py`

**Клавиатуры по состояниям**:
- `start_keyboard`: [Старт]
- `auth_keyboard`: [Авторизация, Старт]
- `auth_waiting_keyboard`: [Старт]
- `authorized_keyboard`: [Редактировать резюме, Старт]
- `action_choice_keyboard`: [GAP-анализ, Письмо, Чек-лист, Симуляция, Старт]

## LLM КОМПОНЕНТЫ [#LLM_MODULES]

### GAP Analyzer [#LLM_GAP_ANALYZER]
**Файл**: `src/llm_gap_analyzer/llm_gap_analyzer.py`
**Класс**: `LLMGapAnalyzer`
**Методы**:
- `gap_analysis()` - основной метод анализа
- `_create_system_prompt()` - промпт с методологией HR
- `_create_user_prompt()` - данные резюме и вакансии

**Особенности**:
- Structured output через Pydantic модели
- Temperature: 0.2 (для стабильности)
- LangSmith трейсинг для мониторинга
- Методология: скрининг → классификация → анализ → рекомендации

### Cover Letter Generator [#LLM_COVER_LETTER]
**Файл**: `src/llm_cover_letter/llm_cover_letter_generator.py`
**Класс**: `EnhancedLLMCoverLetterGenerator`
**Особенности**:
- Генерация персонализированных писем с оценками качества
- Анализ соответствия навыков и опыта
- Структурированный вывод с 7 секциями письма
- Оценки: персонализация, профессионализм, релевантность (1-10)

### Interview Checklist Generator [#LLM_INTERVIEW_CHECKLIST]
**Файл**: `src/llm_interview_checklist/llm_interview_checklist_generator.py`
**Класс**: `LLMInterviewChecklistGenerator`
**Версии**:
- `generate_interview_checklist()` - базовая версия
- `generate_professional_interview_checklist()` - расширенная с 7 блоками

**Особенности**:
- Персонализация по уровню кандидата и типу вакансии
- Временные оценки для каждого блока подготовки
- Приоритизация задач (критично/важно/желательно)
- 7 блоков подготовки в профессиональной версии

### Interview Simulator [#LLM_INTERVIEW_SIMULATOR]
**Файл**: `src/llm_interview_simulation/llm_interview_simulator.py`
**Класс**: `ProfessionalInterviewSimulator`
**Дополнительно**: `ProfessionalInterviewPDFGenerator` для создания отчетов

**Особенности**:
- Многораундовая симуляция (до 6 раундов)
- Оценка 9 компетенций с баллами 1-5
- Генерация PDF отчета с полным диалогом
- Progress callback для отображения прогресса
- Рекомендации: hire/conditional_hire/reject

**Интеграции всех LLM модулей**:
- OpenAI API (GPT модель из конфига)
- LangSmith для трейсинга (опционально в GAP analyzer)
- Instructor для structured output
- Pydantic модели для валидации выходных данных

## ГРАФ ЗАВИСИМОСТЕЙ [#DEPENDENCY_GRAPH]

### Семантическое описание потока данных:

**1. Точка входа и инициализация**
- Пользователь взаимодействует через Telegram
- `tg_bot/main.py` запускает приложение и инициализирует `bot.instance` и регистрирует обработчики через `handlers.router`
- Все обработчики используют FSM (Finite State Machine) для управления состояниями через `utils/states.py`

**2. Поток авторизации**
- `command_handlers.py` обрабатывает команду `/start` и переводит в состояние UNAUTHORIZED
- При нажатии кнопки авторизации вызывается `auth_handler.py`
- `auth_handler.py` использует `HHAuthService` из модуля `hh/auth.py` для получения OAuth URL
- Пользователь авторизуется на сайте HH, код возвращается на `LOCAL_CALLBACK_SERVER`
- `auth_handler.py` запускает polling и проверяет наличие кода каждые 3 секунды
- При получении кода `HHCodeExchanger` из `hh/token_exchanger.py` обменивает его на токены
- Токены сохраняются в FSM состоянии, пользователь переходит в состояние AUTHORIZED

**3. Поток подготовки данных**
- В состоянии AUTHORIZED доступна кнопка "Редактировать резюме"
- `resume_handler.py` получает ссылку на резюме, валидирует её и извлекает ID
- `HHApiClient` из `hh/api_client.py` делает запрос к HH API для получения данных резюме
- `ResumeExtractor` из `parsers/resume_extractor.py` парсит данные в структуру `ResumeInfo`
- Аналогично `vacancy_handler.py` обрабатывает вакансию через `VacancyExtractor`
- Распарсенные данные сохраняются в FSM как `parsed_resume` и `parsed_vacancy`

**4. Поток LLM обработки (4 параллельных workflow)**

**4.1 GAP-анализ**:
- `gap_analyzer_handler.py` извлекает данные из FSM
- Передает их в `LLMGapAnalyzer` из `llm_gap_analyzer/llm_gap_analyzer.py`
- `LLMGapAnalyzer` форматирует данные через `formatter.py` и отправляет в OpenAI API
- Ответ парсится в модель `EnhancedResumeTailoringAnalysis`
- Результат форматируется и отправляется пользователю по частям

**4.2 Сопроводительное письмо**:
- `cover_letter_handler.py` вызывает `EnhancedLLMCoverLetterGenerator`
- Генерируется письмо с оценками качества
- Результат структурирован как `EnhancedCoverLetter`

**4.3 Чек-лист подготовки**:
- `interview_checklist_handler.py` вызывает `LLMInterviewChecklistGenerator`
- Генерируется профессиональный чек-лист с 7 блоками
- Используется модель `ProfessionalInterviewChecklist`

**4.4 Симуляция интервью**:
- `interview_simulation_handler.py` вызывает `ProfessionalInterviewSimulator`
- Проводится многораундовая симуляция с оценкой компетенций
- `ProfessionalInterviewPDFGenerator` создает PDF отчет
- Используется модель `InterviewSimulation`

### Компонентные зависимости:

**Слой представления (UI Layer)**:
- Все handlers зависят от: `utils/states.py` (состояния), `utils/keyboards.py` (клавиатуры), `utils/text_constants.py` (тексты)
- `message_handlers.py` делегирует обработку специализированным handlers в `spec_handlers/`

**Слой бизнес-логики (Business Logic Layer)**:
- Все spec_handlers зависят от соответствующих LLM модулей
- Все spec_handlers используют parsers для предварительной обработки данных
- Все spec_handlers взаимодействуют с HH API через модуль `hh/`

**Слой внешних сервисов (External Services Layer)**:
- `hh/auth.py` зависит от `callback_local_server/` для OAuth
- `hh/api_client.py` использует `token_manager.py` и `token_refresher.py` для управления токенами
- Все LLM модули зависят от OpenAI API
- `llm_gap_analyzer` опционально использует LangSmith для трейсинга

**Слой обработки данных (Data Processing Layer)**:
- `resume_extractor.py` преобразует JSON от HH API в `models/resume_models.py`
- `vacancy_extractor.py` преобразует JSON от HH API в `models/vacancy_models.py`
- Все LLM модули используют соответствующие модели из `models/` для структурирования выходных данных

### Поток изменения состояний FSM:
1. INITIAL - начальное состояние при первом запуске
2. UNAUTHORIZED - после команды /start, доступна авторизация
3. AUTH_WAITING - ожидание завершения OAuth авторизации
4. AUTHORIZED - авторизован, доступно редактирование резюме
5. RESUME_PREPARATION - ввод ссылки на резюме
6. VACANCY_PREPARATION - ввод ссылки на вакансию
7. Из VACANCY_PREPARATION возможен переход в один из четырех состояний:
   - RESUME_GAP_ANALYZE - выполнение GAP-анализа
   - COVER_LETTER_GENERATION - генерация письма
   - INTERVIEW_CHECKLIST_GENERATION - создание чек-листа
   - INTERVIEW_SIMULATION_GENERATION - симуляция интервью
8. После завершения любого из workflow возврат в AUTHORIZED

### Внешние зависимости и интеграции:
- **HeadHunter API**: OAuth2 авторизация, получение данных резюме и вакансий через REST API
- **OpenAI API**: GPT модель для генерации контента во всех LLM модулях
- **LangSmith API**: опциональный трейсинг и мониторинг для GAP-анализа
- **Telegram Bot API**: взаимодействие с пользователем через библиотеку aiogram
- **Локальный callback сервер**: принимает OAuth коды на localhost для авторизации
- [#LOCAL_CALLBACK_SERVER]: Принимает OAuth код от HH
  - `src/callback_local_server/server.py`
  - Endpoints: `/api/code`, `/api/reset_code`
- [#TOKEN_EXCHANGER]: Обменивает код на токены
  - `src/hh/token_exchanger.py`: `HHCodeExchanger.exchange_code()`
- [#AUTH_POLLING]: Фоновая проверка статуса (100 попыток × 3 сек)
  - `check_auth_code()`, `start_auth_polling()`
- [#HH_API]: Интеграция с HeadHunter API
  - `src/hh/api_client.py`: `HHApiClient` - основной клиент
  - `src/hh/auth.py`: `HHAuthService` - OAuth авторизация
  - `src/hh/token_manager.py`: управление токенами
  - `src/hh/token_refresher.py`: обновление токенов
- [#PARSERS]: Извлечение данных из резюме/вакансий
  - `src/parsers/resume_extractor.py`: `ResumeExtractor`
  - `src/parsers/vacancy_extractor.py`: `VacancyExtractor`
- [#MODELS]: Pydantic модели для валидации
  - `src/models/resume_models.py`: ResumeInfo, Experience, Education, Language
  - `src/models/vacancy_models.py`: VacancyInfo, Employment, Schedule
  - `src/models/gap_analysis_models.py`: EnhancedResumeTailoringAnalysis, PrimaryScreening, RequirementAnalysis
  - `src/models/cover_letter_models.py`: EnhancedCoverLetter, SkillsMatch, CompanyContext
  - `src/models/interview_checklist_models.py`: InterviewChecklist, ProfessionalInterviewChecklist, ChecklistItem
  - `src/models/interview_simulation_models.py`: InterviewSimulation, CompetencyScore, DialogMessage
- [#LLM_MODULES]: 4 модуля генерации контента через AI
  - GAP анализ (`llm_gap_analyzer/`): детальный анализ соответствия резюме вакансии
  - Сопроводительное письмо (`llm_cover_letter/`): персонализированные письма с оценками
  - Чек-лист подготовки (`llm_interview_checklist/`): 7-блочный план подготовки
  - Симуляция интервью (`llm_interview_simulation/`): многораундовое интервью с PDF отчетом