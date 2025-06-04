# src/utils/logging_config.py
import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler


class ModulePathFormatter(logging.Formatter):
    """Кастомный форматтер для логов с полным путем модуля без расширения."""
    
    def format(self, record):
        # Получаем полный путь к файлу
        pathname = record.pathname
        
        # Убираем расширение .py
        if pathname.endswith('.py'):
            pathname = pathname[:-3]
        
        # Заменяем разделители на точки для читаемости
        # /path/to/src/tg_bot/handlers/message_handlers.py -> src.tg_bot.handlers.message_handlers
        if 'src' in pathname:
            # Берем только часть после src/
            src_index = pathname.find('src')
            if src_index != -1:
                pathname = pathname[src_index:].replace(os.sep, '.')
        
        # Добавляем отформатированный путь в record
        record.module_path = pathname
        
        return super().format(record)


def setup_logging(
    log_level: str = "DEBUG",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    logs_dir: str = "LOGS"
) -> None:
    """
    Настройка централизованного логирования для всего приложения.
    
    Args:
        log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        max_bytes: Максимальный размер файла лога в байтах
        backup_count: Количество backup файлов для ротации
        logs_dir: Директория для файлов логов
    """
    # Создаем директории для логов
    logs_path = Path(logs_dir)
    logs_path.mkdir(exist_ok=True)
    
    legacy_path = logs_path / "legacy"
    legacy_path.mkdir(exist_ok=True)
    
    # Определяем модули приложения
    modules = [
        "callback_local_server",
        "hh", 
        "llm_cover_letter",
        "llm_gap_analyzer", 
        "llm_interview_checklist",
        "llm_interview_simulation",
        "parsers",
        "tg_bot"
    ]
    
    # Уровень логирования
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Формат логов: дата время, полный путь, функция, строка, уровень, сообщение
    log_format = "%(asctime)s - %(module_path)s - %(funcName)s:%(lineno)d - %(levelname)s - %(message)s"
    
    # Удаляем существующие handlers у root logger
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Настраиваем логгеры для каждого модуля
    for module in modules:
        logger = logging.getLogger(module)
        logger.setLevel(level)
        
        # Убираем старые handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Файл для логов модуля
        log_file = logs_path / f"{module}.log"
        
        # Создаем RotatingFileHandler с переносом в legacy
        file_handler = RotatingFileHandler(
            filename=str(log_file),
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        
        # Переносим ротированные файлы в legacy папку
        def namer(default_name):
            """Кастомная функция именования для перенаса в legacy папку."""
            base_name = os.path.basename(default_name)
            return str(legacy_path / base_name)
        
        file_handler.namer = namer
        
        # Устанавливаем форматтер
        formatter = ModulePathFormatter(log_format)
        file_handler.setFormatter(formatter)
        
        # Добавляем handler к логгеру
        logger.addHandler(file_handler)
        
        # Отключаем propagation чтобы избежать дублирования
        logger.propagate = False
    
    # Создаем консольный handler для вывода в терминал (опционально)
    console_handler = logging.StreamHandler()
    console_formatter = ModulePathFormatter(
        "%(asctime)s - %(module_path)s - %(funcName)s:%(lineno)d - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    
    # Добавляем консольный handler только к root logger для общих сообщений
    root_logger.addHandler(console_handler)
    root_logger.setLevel(level)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Получение логгера для модуля.
    
    Args:
        name: Имя логгера. Если None, определяется автоматически по имени модуля.
        
    Returns:
        Настроенный логгер
        
    Examples:
        # В модуле src/tg_bot/handlers/message_handlers.py
        logger = get_logger("tg_bot")
        
        # Или автоматическое определение
        logger = get_logger()  # автоматически определит tg_bot
    """
    if name is None:
        # Автоматическое определение модуля по стеку вызовов
        import inspect
        
        frame = inspect.currentframe()
        try:
            caller_frame = frame.f_back
            caller_filename = caller_frame.f_code.co_filename
            
            # Определяем модуль по пути к файлу
            if 'callback_local_server' in caller_filename:
                name = 'callback_local_server'
            elif 'tg_bot' in caller_filename:
                name = 'tg_bot'
            elif 'llm_cover_letter' in caller_filename:
                name = 'llm_cover_letter'
            elif 'llm_gap_analyzer' in caller_filename:
                name = 'llm_gap_analyzer'
            elif 'llm_interview_checklist' in caller_filename:
                name = 'llm_interview_checklist'
            elif 'llm_interview_simulation' in caller_filename:
                name = 'llm_interview_simulation'
            elif 'parsers' in caller_filename:
                name = 'parsers'
            elif 'hh' in caller_filename:
                name = 'hh'
            else:
                name = 'app'  # fallback
        finally:
            del frame
    
    return logging.getLogger(name)


# Функция для инициализации логирования с настройками из переменных окружения
def init_logging_from_env():
    """Инициализация логирования с настройками из переменных окружения."""
    log_level = os.getenv('LOG_LEVEL', 'DEBUG')
    max_bytes = int(os.getenv('LOG_MAX_BYTES', 10 * 1024 * 1024))  # 10MB по умолчанию
    backup_count = int(os.getenv('LOG_BACKUP_COUNT', 5))
    logs_dir = os.getenv('LOGS_PATH', 'LOGS')
    
    setup_logging(
        log_level=log_level,
        max_bytes=max_bytes,
        backup_count=backup_count,
        logs_dir=logs_dir
    )


# Дополнительная утилита для настройки специфичных логгеров
def configure_external_loggers():
    """Настройка логирования для внешних библиотек."""
    # Снижаем уровень логирования для внешних библиотек
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    logging.getLogger('aiogram').setLevel(logging.INFO)
    logging.getLogger('openai').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


if __name__ == "__main__":
    # Тестирование конфигурации
    setup_logging(log_level="DEBUG")
    
    # Тестируем разные модули
    tg_logger = get_logger("tg_bot")
    tg_logger.info("Тестовое сообщение от tg_bot")
    
    hh_logger = get_logger("hh")
    hh_logger.warning("Тестовое предупреждение от hh")
    
    llm_logger = get_logger("llm_gap_analyzer")
    llm_logger.error("Тестовая ошибка от llm_gap_analyzer")