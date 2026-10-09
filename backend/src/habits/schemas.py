import uuid
from datetime import date, timedelta

from pydantic import BaseModel, ConfigDict, Field, field_validator


class HabitLogCreateSchema(BaseModel):
    """Схема создания отметки о выполнении привычки."""
    completed_date: date | None = Field(
        default=None,
        description="Календарный день в TZ пользователя. Если None — сервис подставит сегодня.",
    )

    @field_validator("completed_date")
    @classmethod
    def not_in_future(cls, v: date | None) -> date | None:
        if v is not None and v > date.today():
            raise ValueError("Дата не может быть в будущем")
        return v


class HabitLogOutputSchema(BaseModel):
    """Output-схема отметки о выполнении."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    habit_id: uuid.UUID
    user_id: uuid.UUID
    completed_date: date