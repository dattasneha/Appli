from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.orm import declared_attr
from sqlalchemy import Column
import sqlalchemy.dialects.postgresql as pg
from enum import Enum
from datetime import datetime
import uuid
from typing import Optional, List

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class ApplicationStatus(str, Enum):
    SUBMITTED = "submitted"
    SHORTLISTED = "shortlisted"
    APPROVED = "approved"
    REJECTED = "rejected"

class TimestampMixin:

    @declared_attr
    def created_at(cls):
        return Field(
            sa_column=Column(pg.TIMESTAMP, default=datetime.utcnow)
        )

    @declared_attr
    def updated_at(cls):
        return Field(
            sa_column=Column(
                pg.TIMESTAMP,
                default=datetime.utcnow,
                onupdate=datetime.utcnow
            )
        )
    
class User(SQLModel, TimestampMixin, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4
        )
    )

    email: str = Field(unique=True, index=True)
    hashed_password: str
    role: UserRole = Field(default=UserRole.USER)

    applications: List["Application"] = Relationship(back_populates="user")

class Job(SQLModel, TimestampMixin, table=True):
    __tablename__ = "jobs"

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4
        )
    )

    title: str
    description: str
    is_active: bool = Field(default=True)

    applications: List["Application"] = Relationship(back_populates="job")

class Application(SQLModel, TimestampMixin, table=True):
    __tablename__ = "applications"

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4
        )
    )

    user_id: uuid.UUID = Field(foreign_key="users.id")
    job_id: uuid.UUID = Field(foreign_key="jobs.id")

    resume_url: str
    cover_letter: Optional[str] = None

    status: ApplicationStatus = Field(
        default=ApplicationStatus.SUBMITTED,
        index=True
    )

    user: Optional[User] = Relationship(back_populates="applications")
    job: Optional[Job] = Relationship(back_populates="applications")

    history: List["ApplicationStatusHistory"] = Relationship(
        back_populates="application"
    )

class ApplicationStatusHistory(SQLModel, table=True):
    __tablename__ = "application_status_history"

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4
        )
    )

    application_id: uuid.UUID = Field(
        foreign_key="applications.id",
        index=True
    )

    old_status: ApplicationStatus
    new_status: ApplicationStatus

    changed_by: uuid.UUID

    changed_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.now)
    )

    application: Optional[Application] = Relationship(
        back_populates="history"
    )
