import uuid
from datetime import time, date
from pydantic import BaseModel, Field, ConfigDict

from src.habits.enums import Visibility


class HabitCreateSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    title: str = Field(min_length=1, max_length=100)
    color_hex: str = Field(default="#4F46E5", pattern=r"^#[0-9A-Fa-f]{6}$")
    visibility: Visibility = Visibility.FRIENDS
    notification_times: list[time] = Field(default_factory=list, max_length=3)


class HabitUpdateSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    title: str | None = Field(default=None, min_length=1, max_length=100)
    color_hex: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    visibility: Visibility | None = None
    notification_times: list[time] | None = Field(default=None, max_length=3)


class HabitOutputSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    color_hex: str
    visibility: Visibility
    start_date: date
    notification_times: list[time]
