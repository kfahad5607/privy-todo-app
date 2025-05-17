from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.models.todo import TodoStatus

class TodoBase(BaseModel):
    title: str
    status: TodoStatus = TodoStatus.PENDING
    is_bookmarked: bool = False
    order: int = 0
    parent_id: Optional[int] = None

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[TodoStatus] = None
    is_bookmarked: Optional[bool] = None
    order: Optional[int] = None
    parent_id: Optional[int] = None

class TodoResponse(TodoBase):
    id: int
    user_id: int
    created_at: datetime
    modified_at: datetime
    subtasks: List['TodoResponse'] = []

    class Config:
        from_attributes = True

# Update forward references
TodoResponse.model_rebuild()

class TodoFilter(BaseModel):
    status: Optional[TodoStatus] = None
    is_bookmarked: Optional[bool] = None
    search: Optional[str] = None
    parent_id: Optional[int] = None
    columns: Optional[str] = None,

class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 10
    order_by: str = "created_at"
    order_direction: str = "desc" 