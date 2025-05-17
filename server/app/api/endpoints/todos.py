from collections import defaultdict
from typing import Any, List, Tuple
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc, asc

from app.core.deps import get_current_active_user
from app.db.database import get_db
from app.models.todo import Todo
from app.models.user import User
from app.schemas.todos import (
    TodoCreate,
    TodoUpdate,
    TodoResponse,
    TodoFilter,
    PaginationParams
)
from app.core.exceptions import (BaseAppException, ResourceNotFoundException, ValidationException)
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

def nest_subtasks(todo_pairs: List[Tuple[Todo, Todo]]) -> List[Todo]:
    todos_dict = {}
    subtasks_map = defaultdict(list)

    for parent, sub in todo_pairs:
        parent_response = TodoResponse(**parent.model_dump())
        if parent.id not in todos_dict:
            todos_dict[parent.id] = parent_response
        if sub:
            subtasks_map[parent.id].append(sub)
    
    for parent_id, subtasks in subtasks_map.items():
        todos_dict[parent_id].subtasks.extend(subtasks)

    return list(todos_dict.values())

@router.post("", response_model=TodoResponse)
async def create_todo(
    *,
    db: AsyncSession = Depends(get_db),
    todo_in: TodoCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    try:
        # If parent_id is provided, verify it exists and belongs to the user
        if todo_in.parent_id < 1:
            todo_in.parent_id = None

        if todo_in.parent_id:
            parent = await db.get(Todo, todo_in.parent_id)
            if not parent or parent.user_id != current_user.id:
                raise ValidationException(
                    message="Parent todo not found"
                )
            # Verify parent doesn't have a parent (one-level nesting only)
            if parent.parent_id:
                raise ValidationException(
                    message="Cannot add subtask to a subtask"
                )

        todo = Todo(
            **todo_in.model_dump(),
            user_id=current_user.id
        )
        db.add(todo)
        await db.commit()
        await db.refresh(todo)

        return TodoResponse(**todo.model_dump())
    except ValidationException:
        raise
    except Exception as e:
        logger.error(f"Error creating todo: {e}", exc_info=True)
        raise BaseAppException("Could not create todo. Please try again later.") from e


@router.get("")
async def list_todos(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    filters: TodoFilter = Depends(),
    pagination: PaginationParams = Depends()
) -> Any:
    try:
        requested_columns = ["id", "title", "status", "is_bookmarked", "order", "parent_id", "created_at", "modified_at"]

        if filters.columns:
            requested_columns = [col.strip() for col in filters.columns.split(",")]

            # Ensure ID is always included for proper identification
            if "id" not in requested_columns:
                requested_columns.append("id")

            # Validate column names against schema
            valid_columns = list(TodoResponse.model_fields.keys())
            invalid_columns = [col for col in requested_columns if col not in valid_columns]
        
            if invalid_columns:
                logger.warning(f"Invalid column names requested: {invalid_columns}")
                raise ValidationException(
                    f"Invalid column(s): {', '.join(invalid_columns)}. Valid columns are: {', '.join(valid_columns)}"
                )
                
        selected_columns = [getattr(Todo, col) for col in requested_columns]

        # Build query options
        # db_query_options = [load_only(*selected_columns)]
        # if "parent_id" in requested_columns:
        #     db_query_options.insert(0, selectinload(Todo.parent).load_only(Todo.id, Todo.title))

        # Base query
        # stmt = (
        #     select(Todo)
        #     .where(Todo.parent_id.is_(None))  # only top-level todos
        #     .options(selectinload(Todo.subtasks))  # eager load subtasks
        #     .order_by(Todo.order)
        #     .offset(offset)
        #     .limit(page_size)
        # )

        parent = aliased(Todo, name="t")
        subtask = aliased(Todo, name="st")

        db_query = (
            select(parent, subtask)
            .join_from(parent, subtask, subtask.parent_id == parent.id, isouter=True)
            .where((parent.user_id == current_user.id) & (parent.parent_id.is_(None)))
            .order_by(parent.order.desc())
        )

        # Apply filters
        if filters.status:
            db_query = db_query.where(parent.status == filters.status)
        if filters.is_bookmarked is not None:
            db_query = db_query.where(parent.is_bookmarked == filters.is_bookmarked)
        if filters.parent_id is not None:
            db_query = db_query.where(parent.parent_id == filters.parent_id)
        if filters.search and filters.search.strip():
            search_term = f"%{filters.search.strip()}%"
            db_query = db_query.where(parent.title.ilike(search_term))

        # Apply ordering
        order_column = getattr(parent, pagination.order_by, parent.order)
        if pagination.order_direction == "desc":
            db_query = db_query.order_by(desc(order_column))
        else:
            db_query = db_query.order_by(asc(order_column))

        # Apply pagination
        db_query = db_query.offset((pagination.page - 1) * pagination.page_size).limit(pagination.page_size)

        # Execute query
        result = await db.execute(db_query)
        todo_pairs = result.all()

        todos = nest_subtasks(todo_pairs)
        return todos
    except ValidationException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving todos: {e}", exc_info=True)
        raise BaseAppException("Could not retrieve todos. Please try again later.") from e


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(
    *,
    db: AsyncSession = Depends(get_db),
    todo_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    try:
        todo = await db.get(Todo, todo_id)
        if not todo or todo.user_id != current_user.id:
            raise ResourceNotFoundException(
                message="Todo not found"
            )
        return TodoResponse(**todo.model_dump())
    except ResourceNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving todo: {e}", exc_info=True)
        raise BaseAppException("Could not retrieve todo. Please try again later.") from e

@router.patch("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    *,
    db: AsyncSession = Depends(get_db),
    todo_id: int,
    todo_in: TodoUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    try:
        todo = await db.get(Todo, todo_id)
        if not todo or todo.user_id != current_user.id:
            raise ResourceNotFoundException(
                message="Todo not found"
            )

        # If updating parent_id, verify the new parent exists and belongs to the user
        if todo_in.parent_id is not None:
            if todo_in.parent_id == todo_id:
                raise ValidationException(
                    message="Todo cannot be its own parent"
                )
            parent = await db.get(Todo, todo_in.parent_id)
            if not parent or parent.user_id != current_user.id:
                raise ResourceNotFoundException(
                    message="Parent todo not found"
                )
            # Verify parent doesn't have a parent (one-level nesting only)
            if parent.parent_id:
                raise ValidationException(
                    message="Cannot add subtask to a subtask"
                )

        # Update todo
        todo_data = todo_in.model_dump(exclude_unset=True)
        for field, value in todo_data.items():
            setattr(todo, field, value)

        await db.commit()
        await db.refresh(todo)

        return TodoResponse(**todo.model_dump())
    except ResourceNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error updating todo: {e}", exc_info=True)
        raise BaseAppException("Could not update todo. Please try again later.") from e

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    *,
    db: AsyncSession = Depends(get_db),
    todo_id: int,
    current_user: User = Depends(get_current_active_user)
) -> None:
    try:
        todo = await db.get(Todo, todo_id)
        if not todo or todo.user_id != current_user.id:
            raise ResourceNotFoundException(
                message="Todo not found"
            )
        
        await db.delete(todo)
        await db.commit() 
    except ResourceNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error deleting todo: {e}", exc_info=True)
        raise BaseAppException("Could not delete todo. Please try again later.") from e