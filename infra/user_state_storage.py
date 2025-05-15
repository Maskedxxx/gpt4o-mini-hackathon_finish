# infra/user_state_storage.py

"""Реализация хранилища состояний пользователя"""
from typing import Optional
from datetime import datetime
from sqlalchemy import select

from domain.user_state import UserState, UserStateEnum
from domain.services import IUserStateStorage
from infra.database import UserStateModel, async_session


class UserStateStorage(IUserStateStorage):
    """Реализация хранилища состояний в SQLite"""
    
    async def save_state(self, user_state: UserState) -> None:
        """Сохранить состояние"""
        async with async_session() as session:
            # Проверяем существующую запись
            result = await session.execute(
                select(UserStateModel).where(UserStateModel.user_id == user_state.user_id)
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                # Обновляем существующую запись
                existing.state = user_state.state.value
                existing.payload = user_state.payload
                existing.updated_at = datetime.now()
            else:
                # Создаём новую запись
                state_model = UserStateModel(
                    user_id=user_state.user_id,
                    state=user_state.state.value,
                    payload=user_state.payload,
                    updated_at=datetime.now()
                )
                session.add(state_model)
            
            await session.commit()
    
    async def get_state(self, user_id: int) -> Optional[UserState]:
        """Получить состояние"""
        async with async_session() as session:
            result = await session.execute(
                select(UserStateModel).where(UserStateModel.user_id == user_id)
            )
            state_model = result.scalar_one_or_none()
            
            if not state_model:
                return None
            
            return UserState(
                user_id=state_model.user_id,
                state=UserStateEnum(state_model.state),
                payload=state_model.payload
            )
    
    async def update_state(self, user_id: int, state: UserStateEnum, payload: dict = None) -> None:
        """Обновить состояние"""
        user_state = UserState(
            user_id=user_id,
            state=state,
            payload=payload
        )
        await self.save_state(user_state)