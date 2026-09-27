import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

class Settings(BaseModel):
    app_name: str = "FitBuddy"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./fitbuddy.db")
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    workout_model: str = os.getenv("GEMINI_WORKOUT_MODEL", "gemini-3.8-flash")
    tip_model: str = os.getenv("GEMINI_TIP_MODEL", "gemini-3.8-flash")
    admin_token: str = os.getenv("ADMIN_TOKEN", "change-this-admin-token")
    max_feedback_length: int = Field(default=1500, ge=100, le=5000)

@lru_cache
def get_settings() -> Settings:
    return Settings()
