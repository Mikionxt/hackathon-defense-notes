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
        # +1 день — запас на разницу TZ (юзер в UTC+14 может быть на день впереди сервера).
        if v is not None and v > date.today() + timedelta(days=1):
            raise ValueError("completed_date не может быть в будущем")
        return v


class HabitLogOutputSchema(BaseModel):
    """Output-схема отметки о выполнении."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    habit_id: uuid.UUID
    user_id: uuid.UUID
    completed_date: date