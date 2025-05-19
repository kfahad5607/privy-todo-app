from typing import Any, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_active_user
from app.db.database import get_db
from app.models.users import User
from app.schemas.todos import (
    TodoCreate,
    TodoReorderRequest,
    TodoUpdate,
    TodoResponse,
    TodoFilter,
    PaginationParams
)
from app.core.logging import get_logger
from app.services.todos import TodoService

logger = get_logger(__name__)

router = APIRouter()

@router.post("", response_model=TodoResponse)
async def create_todo(
    *,
    db: AsyncSession = Depends(get_db),
    todo_in: TodoCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    todo_service = TodoService(db)
    return await todo_service.create_todo(todo_in, current_user)

@router.get("")
async def list_todos(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    filters: TodoFilter = Depends(),
    pagination: PaginationParams = Depends()
) -> Any:
    todo_service = TodoService(db)
    return await todo_service.list_todos(current_user, filters, pagination)

@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(
    *,
    db: AsyncSession = Depends(get_db),
    todo_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    todo_service = TodoService(db)
    return await todo_service.get_todo(todo_id, current_user)

@router.patch("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    *,
    db: AsyncSession = Depends(get_db),
    todo_id: int,
    todo_in: TodoUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    todo_service = TodoService(db)
    return await todo_service.update_todo(todo_id, todo_in, current_user)

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    *,
    db: AsyncSession = Depends(get_db),
    todo_id: int,
    current_user: User = Depends(get_current_active_user)
) -> None:
    todo_service = TodoService(db)
    await todo_service.delete_todo(todo_id, current_user)

@router.post("/reorder", response_model=List[TodoResponse])
async def reorder_todos(
    *,
    db: AsyncSession = Depends(get_db),
    reorder_request: TodoReorderRequest,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    todo_service = TodoService(db)
    return await todo_service.reorder_todos(reorder_request, current_user)