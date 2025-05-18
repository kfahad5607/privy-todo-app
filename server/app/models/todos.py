from datetime import datetime
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel
from enum import Enum
from sqlalchemy import Column, DateTime, func

class TodoStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Todo(SQLModel, table=True):
    __tablename__ = "todos"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    status: TodoStatus = Field(default=TodoStatus.PENDING)
    is_bookmarked: bool = Field(default=False)
    order: int = Field(default=0)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    modified_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    )
    
    # Foreign Keys
    user_id: int = Field(foreign_key="users.id")
    parent_id: Optional[int] = Field(default=None, foreign_key="todos.id")

    # Relationships
    user: "User" = Relationship(back_populates="todos")
    subtasks: List["Todo"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={
            "primaryjoin": "Todo.id==Todo.parent_id",
            "cascade": "all, delete-orphan"
        }
    )
    parent: Optional["Todo"] = Relationship(
        back_populates="subtasks",
        sa_relationship_kwargs={
            "primaryjoin": "Todo.parent_id==Todo.id",
            "remote_side": "Todo.id"
        }
    ) 