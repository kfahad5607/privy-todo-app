from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, DateTime, Text, func
from sqlmodel import Field, Relationship, SQLModel
from pydantic import EmailStr
import uuid

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: EmailStr = Field(unique=True, index=True)
    name: str
    hashed_password: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    modified_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    )

    # Relationships
    todos: List["Todo"] = Relationship(back_populates="user")
    refresh_tokens: List["RefreshToken"] = Relationship(back_populates="user")

class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"

    jti: uuid.UUID = Field(primary_key=True)
    Field(
        sa_column=Column(Text, nullable=False)
    )
    token_hash: str = Field(sa_column=Column(Text, nullable=False))
    user_id: int = Field(foreign_key="users.id")
    expires_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True))
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    is_revoked: bool = Field(default=False)

    # Relationships
    user: User = Relationship(back_populates="refresh_tokens") 