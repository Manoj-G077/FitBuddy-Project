from typing import Literal

from pydantic import BaseModel, Field, field_validator

Goal = Literal["weight_loss", "muscle_gain", "general_wellness"]
Intensity = Literal["low", "medium", "high"]

class UserInput(BaseModel):
    username: str = Field(min_length=2, max_length=100)
    user_id: str = Field(min_length=2, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")
    age: int = Field(ge=18, le=100)
    weight: float = Field(gt=20, lt=400)
    goal: Goal
    intensity: Intensity

    @field_validator("username")
    @classmethod
    def clean_username(cls, value: str) -> str:
        return " ".join(value.strip().split())

class FeedbackRequest(BaseModel):
    user_id: str = Field(min_length=2, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")
    feedback: str = Field(min_length=3, max_length=1500)

class Exercise(BaseModel):
    name: str
    sets_reps_or_duration: str
    rest: str

class WorkoutDay(BaseModel):
    day: str
    focus: str
    warmup: str
    exercises: list[Exercise]
    cooldown: str

class WorkoutPlan(BaseModel):
    summary: str
    safety_note: str
    days: list[WorkoutDay] = Field(min_length=7, max_length=7)

class NutritionTip(BaseModel):
    tip: str
    recovery_note: str

class PlanUpdate(BaseModel):
    summary: str
    safety_note: str
    days: list[WorkoutDay] = Field(min_length=7, max_length=7)
