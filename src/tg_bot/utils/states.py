# src/tg_bot/utils/states.py
import logging
from aiogram.fsm.state import State, StatesGroup

logger = logging.getLogger("states")

logger.info("Инициализация состояний пользователя")
class UserState(StatesGroup):
    """Состояния пользователя в боте."""
    INITIAL = State()           # Начальное состояние (нулевое)
    UNAUTHORIZED = State()      # Состояние после нажатия /start (не авторизован)
    AUTH_WAITING = State()      # Ожидание авторизации
    AUTHORIZED = State()        # Состояние после успешной авторизации
    RESUME_PREPARATION = State() # Подготовка данных для обновления резюме
    VACANCY_PREPARATION = State() # Подготовка данных о вакансии
    RESUME_REWRITE = State()     # Состояние переписывания резюме