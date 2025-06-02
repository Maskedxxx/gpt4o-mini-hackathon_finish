# src/tg_bot/utils/keyboards.py
import logging
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from src.utils import get_logger
logger = get_logger()

# Клавиатура для начального состояния (только кнопка Старт)
start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Старт")]
    ],
    resize_keyboard=True
)

# Клавиатура для неавторизованного состояния (кнопки Старт и Авторизация)
auth_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Авторизация")],
        [KeyboardButton(text="Старт")]
    ],
    resize_keyboard=True
)

# Клавиатура для состояния ожидания авторизации (только кнопка Старт)
auth_waiting_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Старт")]
    ],
    resize_keyboard=True
)

# Клавиатура для авторизованного состояния (кнопки Старт и Редактировать резюме)
authorized_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Редактировать резюме")],
        [KeyboardButton(text="Старт")]
    ],
    resize_keyboard=True
)

# Клавиатура для состояния подготовки резюме (только кнопка Старт)
resume_preparation_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Старт")]
    ],
    resize_keyboard=True
)

# Клавиатура для состояния подготовки вакансии (только кнопка Старт)
vacancy_preparation_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Старт")]
    ],
    resize_keyboard=True
)

# Клавиатура с выбором действий (GAP-анализ или Cover Letter)
action_choice_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 GAP-анализ резюме")],
        [KeyboardButton(text="📧 Рекомендательное письмо")],
        [KeyboardButton(text="📋 Чек-лист подготовки к интервью")],
        [KeyboardButton(text="🎭 Симуляция интервью")],
        [KeyboardButton(text="Старт")]
    ],
    resize_keyboard=True
)