import uuid
from datetime import time
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.habits.enums import Visibility
from src.habits.models import Habit


class HabitsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_habit(
        self,
        creator_id: uuid.UUID,
        title: str,
        color_hex: str,
        visibility: Visibility,
        notification_times: list[time],
    ) -> Habit:
        new_habit = Habit(
            creator_id=creator_id,
            title=title,
            color_hex=color_hex,
            visibility=visibility,
            notification_times=notification_times,
        )
        self.session.add(new_habit)
        await self.session.commit()
        return new_habit

    async def get_habit_by_id(self, habit_id: uuid.UUID, creator_id: uuid.UUID) -> Habit | None:
        habit = select(Habit).where(Habit.id == habit_id, Habit.creator_id == creator_id)
        result = await self.session.execute(habit)
        return result.scalar_one_or_none()

    async def get_all_habits(self, creator_id: uuid.UUID) -> list[Habit]:
        habits = select(Habit).where(Habit.creator_id == creator_id)
        result = await self.session.execute(habits)
        return list(result.scalars().all())

    async def update_habit(
        self,
        habit_id: uuid.UUID,
        creator_id: uuid.UUID,
        updates: dict[str, Any],
    ) -> Habit | None:
        habit = await self.get_habit_by_id(habit_id=habit_id, creator_id=creator_id)

        if habit is None:
            return None

        for field, value in updates.items():
            setattr(habit, field, value)

        await self.session.commit()
        return habit

    async def delete_habit(self, habit_id: uuid.UUID, creator_id: uuid.UUID) -> bool:
        habit = await self.get_habit_by_id(habit_id=habit_id, creator_id=creator_id)
        if habit is None:
            return False

        await self.session.delete(habit)
        await self.session.commit()
        return True
