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
            raise ValueError(f"Привычка {habit_id} не найдена")

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
                f"Привычка {habit_id} уже отмечена выполненной на {completed_date}"
            ) from exc
        await self.session.refresh(log)
        return log

    async def get_logs_in_range(
        self,
        *,
        user_id: uuid.UUID,
        date_from: date,
        date_to: date,
        habit_id: uuid.UUID | None = None,
    ) -> list[HabitLog]:
        if date_from > date_to:
            raise ValueError("Первая дата не может быть больше последней")

        stmt = (
            select(HabitLog)
            .where(
                HabitLog.user_id == user_id,
                HabitLog.completed_date >= date_from,
                HabitLog.completed_date <= date_to,
            )
            .order_by(HabitLog.completed_date.asc(), HabitLog.id.asc())
        )
        if habit_id is not None:
            stmt = stmt.where(HabitLog.habit_id == habit_id)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_completed_habits_by_date(
        self,
        *,
        user_id: uuid.UUID,
        target_date: date,
    ) -> list[Habit]:
        stmt = (
            select(Habit)
            .join(HabitLog, HabitLog.habit_id == Habit.id)
            .where(
                HabitLog.user_id == user_id,
                HabitLog.completed_date == target_date,
            )
            .order_by(Habit.title.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_uncompleted_habits_by_date(
        self,
        *,
        user_id: uuid.UUID,
        target_date: date,
    ) -> list[Habit]:
        created_ids = (
            select(Habit.id)
            .where(
                Habit.creator_id == user_id,
                Habit.start_date <= target_date,
            )
        )
        shared_ids = (
            select(Habit.id)
            .join(SharedHabitUser, SharedHabitUser.habit_id == Habit.id)
            .where(
                SharedHabitUser.user_id == user_id,
                SharedHabitUser.status == InviteStatus.ACCEPTED,
                Habit.start_date <= target_date,
            )
        )
        completed_subq = (
            select(HabitLog.habit_id)
            .where(
                HabitLog.user_id == user_id,
                HabitLog.completed_date == target_date,
            )
        )
        stmt = (
            select(Habit)
            .where(
                Habit.id.in_(created_ids.union(shared_ids)),
                Habit.id.not_in(completed_subq),
            )
            .order_by(Habit.title.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def delete_log(
        self,
        *,
        user_id: uuid.UUID,
        log_id: uuid.UUID,
    ) -> bool:
        stmt = (
            delete(HabitLog)
            .where(
                HabitLog.id == log_id,
                HabitLog.user_id == user_id,
            )
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0

    async def _user_can_log_habit(
        self,
        *,
        user_id: uuid.UUID,
        habit: Habit,
    ) -> bool:
        """Проверить, что юзер — создатель привычки или принятый партнёр."""
        if habit.creator_id == user_id:
            return True

        stmt = select(SharedHabitUser.id).where(
            SharedHabitUser.habit_id == habit.id,
            SharedHabitUser.user_id == user_id,
            SharedHabitUser.status == InviteStatus.ACCEPTED,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
