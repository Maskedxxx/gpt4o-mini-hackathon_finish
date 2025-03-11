# src/tg_bot/utils/keyboards.py
import logging
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

logger = logging.getLogger("keyboards")

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