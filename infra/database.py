# infra/database.py

"""Настройка базы данных"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from config import db_settings

# Базовый класс для моделей
Base = declarative_base()


class UserTokenModel(Base):
    """Модель для хранения токенов пользователя"""
    __tablename__ = "user_tokens"
    
    user_id = Column(Integer, primary_key=True)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
    expires_at = Column(Integer, nullable=False)


class UserStateModel(Base):
    """Модель для хранения состояния пользователя"""
    __tablename__ = "user_states"
    
    user_id = Column(Integer, primary_key=True)
    state = Column(String, nullable=False)
    payload = Column(JSON, nullable=True)
    updated_at = Column(DateTime, nullable=False)


# Создание движка БД
engine = create_async_engine(
    db_settings.url.replace("sqlite:///", "sqlite+aiosqlite:///"),
    echo=False
)

# Фабрика сессий
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def init_db():
    """Инициализация БД"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Получить сессию БД"""
    async with async_session() as session:
        yield session