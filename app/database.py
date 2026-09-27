from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

from .config import get_settings

settings = get_settings()

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100))
    age: Mapped[int] = mapped_column(Integer)
    weight: Mapped[float] = mapped_column(Float)
    goal: Mapped[str] = mapped_column(String(50))
    intensity: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    plans: Mapped[list["Plan"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    original_plan: Mapped[str] = mapped_column(Text)
    updated_plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    nutrition_tip: Mapped[str] = mapped_column(Text)
    latest_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    user: Mapped[User] = relationship(back_populates="plans")

def init_db() -> None:
    Base.metadata.create_all(bind=engine)

def save_user(data: dict) -> User:
    with SessionLocal() as db:
        user = User(**data)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

def save_plan(user_pk: int, original_plan: str, nutrition_tip: str) -> Plan:
    with SessionLocal() as db:
        plan = Plan(
            user_id=user_pk,
            original_plan=original_plan,
            nutrition_tip=nutrition_tip,
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return plan

def get_user(user_id: str) -> User | None:
    with SessionLocal() as db:
        return db.query(User).filter(User.user_id == user_id).first()

def get_latest_plan(user_id: str) -> Plan | None:
    with SessionLocal() as db:
        return (
            db.query(Plan)
            .join(User)
            .filter(User.user_id == user_id)
            .order_by(Plan.id.desc())
            .first()
        )

def update_plan(user_id: str, updated_plan: str, feedback: str) -> Plan | None:
    with SessionLocal() as db:
        plan = (
            db.query(Plan)
            .join(User)
            .filter(User.user_id == user_id)
            .order_by(Plan.id.desc())
            .first()
        )
        if not plan:
            return None
        plan.updated_plan = updated_plan
        plan.latest_feedback = feedback
        db.commit()
        db.refresh(plan)
        return plan

def get_all_users() -> list[User]:
    with SessionLocal() as db:
        return db.query(User).order_by(User.created_at.desc()).all()
