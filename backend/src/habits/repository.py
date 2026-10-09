import uuid
from datetime import date

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.habits.enums import InviteStatus
from src.habits.models import Habit, HabitLog, SharedHabitUser


class HabitLogRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def mark_completed(
        self,
        *,
        user_id: uuid.UUID,
        habit_id: uuid.UUID,
        completed_date: date,
    ) -> HabitLog:
        habit = await self.session.get(Habit, habit_id)
        if habit is None:
            raise ValueError(f"Привычка {habit_id} не найдена")

        if not await self._user_can_log_habit(user_id=user_id, habit=habit):
            raise ValueError(f"Habit {habit_id} not found")

        log = HabitLog(
            habit_id=habit_id,
            user_id=user_id,
            completed_date=completed_date,
        )
        self.session.add(log)
        try:
            await self.session.flush()
        except IntegrityError as exc:
            await self.session.rollback()
            raise ValueError(
                f"Habit {habit_id} already marked as completed on {completed_date}"
            ) from exc

        await self.session.refresh(log)
        return log