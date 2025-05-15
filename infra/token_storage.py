# infra/token_storage.py

"""Реализация хранилища токенов"""
import time
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from domain.dto import UserToken
from domain.services import ITokenStorage
from infra.database import UserTokenModel, async_session


class TokenStorage(ITokenStorage):
    """Реализация хранилища токенов в SQLite"""
    
    async def save_token(self, user_id: int, token: UserToken) -> None:
        """Сохранить токены пользователя"""
        async with async_session() as session:
            # Проверяем существующую запись
            result = await session.execute(
                select(UserTokenModel).where(UserTokenModel.user_id == user_id)
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                # Обновляем существующую запись
                existing.access_token = token.access_token
                existing.refresh_token = token.refresh_token
                existing.expires_at = token.expires_at
            else:
                # Создаём новую запись
                token_model = UserTokenModel(
                    user_id=user_id,
                    access_token=token.access_token,
                    refresh_token=token.refresh_token,
                    expires_at=token.expires_at
                )
                session.add(token_model)
            
            await session.commit()
    
    async def get_token(self, user_id: int) -> Optional[UserToken]:
        """Получить токены пользователя, обновить если истекли"""
        async with async_session() as session:
            result = await session.execute(
                select(UserTokenModel).where(UserTokenModel.user_id == user_id)
            )
            token_model = result.scalar_one_or_none()
            
            if not token_model:
                return None
            
            token = UserToken(
                user_id=token_model.user_id,
                access_token=token_model.access_token,
                refresh_token=token_model.refresh_token,
                expires_at=token_model.expires_at
            )
            
            # Проверяем срок действия токена
            if token.expires_at < time.time():
                logger.info(f"Token expired for user {user_id}, refreshing...")
                # Токен истёк, обновляем
                return await self.refresh_token(user_id)
            
            return token
    
    async def refresh_token(self, user_id: int) -> Optional[UserToken]:
        """Обновить токены через refresh_token"""
        # Получаем текущие токены
        current_token = await self.get_token(user_id)
        if not current_token:
            return None
        
        # Импортируем HH клиент здесь чтобы избежать циклических импортов
        from infra.hh_client import HHClient
        hh_client = HHClient()
        
        try:
            # Обмениваем refresh_token на новые токены
            new_token = await hh_client.refresh_access_token(current_token.refresh_token)
            new_token.user_id = user_id
            
            # Сохраняем новые токены
            await self.save_token(user_id, new_token)
            return new_token
        except Exception as e:
            logger.error(f"Failed to refresh token for user {user_id}: {e}")
            return None