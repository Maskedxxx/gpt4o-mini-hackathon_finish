# src/tg_bot/utils/text_constants.py
import logging

logger = logging.getLogger("text_constants")
logger.info("Инициализация словарей с текстами сообщений")

# Сообщения для начального состояния
INITIAL_STATE_MESSAGES = {
    "greeting": (
        "✨ Добро пожаловать в ИИ-ассистент по созданию резюме! ✨\n\n"
        "Мы поможем вам создать профессиональное и привлекательное резюме, "
        "подчеркивающее ваши сильные стороны и достижения.\n\n"
        "Нажмите кнопку 'Старт', чтобы начать работу."
    ),
    "unauthorized": "Пожалуйста, нажмите кнопку 'Старт', чтобы начать работу с ботом."
}

# Сообщения для неавторизованного состояния
UNAUTHORIZED_STATE_MESSAGES = {
    "greeting": (
        "Для продолжения работы необходимо авторизоваться.\n"
        "Пожалуйста, нажмите кнопку 'Авторизация'."
    ),
    "need_auth": "Чтобы продолжить, пожалуйста, нажмите кнопку 'Авторизация'."
}

# Сообщения для состояния ожидания авторизации
AUTH_WAITING_MESSAGES = {
    "auth_instructions": (
        "🔐 Для доступа к функциям бота необходима авторизация.\n\n"
        "1. Перейдите по ссылке ниже\n"
        "2. Разрешите доступ приложению\n"
        "3. Дождитесь сообщения об успешной авторизации\n\n"
    ),
    "reply_auth_instructions": (
        "⚠️ Пожалуйста, пройдите авторизацию, перейдя по предоставленной ссылке.\n\n "
        "Это необходимо для полноценной работы бота.\n\n    "
    )
}

# Сообщения для авторизованного состояния
AUTHORIZED_STATE_MESSAGES = {
    "auth_success": "✅ Авторизация успешно завершена! Теперь вы можете использовать все функции бота.",
    "auth_timeout": "⏱ Время ожидания авторизации истекло. Пожалуйста, попробуйте снова.",
    "resume_instructions": "Теперь вам доступна функция редактирования резюме с помощью ИИ. Нажмите кнопку «Редактировать резюме», чтобы начать.",
    "text_message_reply": "Чтобы начать пользоваться ИИ для редактирования резюме, нажмите кнопку «Редактировать резюме»."
}