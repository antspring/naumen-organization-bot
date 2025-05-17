from typing import List, Optional
from sqlalchemy import ForeignKey, String, Text, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime, timezone

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String())
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))

    role: Mapped["Role"] = relationship(back_populates="users")

    user_events: Mapped[List["EventParticipants"]] = relationship("EventParticipants", back_populates="user")


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String())
    users: Mapped[List["User"]] = relationship(
        back_populates="role", cascade="all, delete-orphan"
    )

    ADMIN = 1
    ORGANIZATOR = 2
    PARTICIPANT = 3

    NAMES = {
        "admin": "Администратор",
        "organizator": "Организатор",
        "participant": "Участник"
    }


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String())
    description: Mapped[Optional[str]] = mapped_column(Text())
    map: Mapped[str] = mapped_column(String())
    schedule: Mapped[str] = mapped_column(Text())
    start_time: Mapped[datetime] = mapped_column(DateTime())
    end_time: Mapped[datetime] = mapped_column(DateTime())

    user_events: Mapped[List["EventParticipants"]] = relationship("EventParticipants", back_populates="event")


class EventParticipants(Base):
    __tablename__ = "event_paticipants"

    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

    joined_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now(timezone.utc))

    user: Mapped["User"] = relationship("User", back_populates="user_events")
    event: Mapped["Event"] = relationship("Event", back_populates="user_events")