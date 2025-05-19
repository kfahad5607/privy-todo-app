from collections import defaultdict
from typing import Any, List, Tuple, Optional, Dict
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import and_, select, desc, asc

from app.models.todos import Todo
from app.models.users import User
from app.schemas.todos import (
    TodoCreate,
    TodoReorderRequest,
    TodoUpdate,
    TodoResponse,
    TodoFilter,
    PaginationParams
)
from app.core.exceptions import (
    PG_FOREIGN_KEY_VIOLATION,
    BaseAppException,
    ResourceNotFoundException,
    ValidationException,
    extract_constraint_name
)
from app.core.logging import get_logger

logger = get_logger(__name__)

class TodoService:
    """Service class for handling Todo-related operations."""

    def __init__(self, db: AsyncSession):
        """Initialize TodoService with database session.

        Args:
            db (AsyncSession): SQLAlchemy async session
        """
        self.db = db

    async def _get_todo_by_id(self, todo_id: int, user_id: int) -> Optional[Todo]:
        """Get a todo by ID and verify user ownership.

        Args:
            todo_id (int): ID of the todo to retrieve
            user_id (int): ID of the user who owns the todo

        Returns:
            Optional[Todo]: The todo if found and owned by user, None otherwise
        """
        todo = await self.db.get(Todo, todo_id)
        if not todo or todo.user_id != user_id:
            return None
        return todo

    async def _validate_parent_todo(self, parent_id: int, user_id: int) -> None:
        """Validate parent todo exists and belongs to user.

        Args:
            parent_id (int): ID of the parent todo
            user_id (int): ID of the user who owns the parent todo

        Raises:
            ValidationException: If parent todo doesn't exist or doesn't belong to user
        """
        parent = await self._get_todo_by_id(parent_id, user_id)
        if not parent:
            raise ValidationException(message="Parent todo not found")
        if parent.parent_id:
            raise ValidationException(message="Cannot add subtask to a subtask")

    def _handle_foreign_key_violation(self, error: IntegrityError, entity_id: int) -> None:
        """Handle foreign key violation errors.

        Args:
            error (IntegrityError): The integrity error to handle
            entity_id (int): ID of the entity that caused the violation

        Raises:
            ValidationException: With appropriate error message
        """
        orig = getattr(error, 'orig', None)
        pgcode = getattr(orig, 'sqlstate', None)

        if not pgcode and hasattr(orig, 'pgcode'):
            pgcode = orig.pgcode

        if pgcode == PG_FOREIGN_KEY_VIOLATION:
            constraint_name = extract_constraint_name(str(orig))
            entity_constraint_map = {
                'todos_parent_id_fkey': {
                    'label': 'Parent Todo',
                    'id': entity_id,
                },
            }
            entity_info = entity_constraint_map.get(constraint_name, {})
            entity_name = entity_info.get('label', 'Unknown entity')
            entity_id = entity_info.get('id', 'unknown')

            logger.warning(f"Foreign key violation: {entity_name} with ID '{entity_id}' does not exist")
            raise ValidationException(f"{entity_name} with ID '{entity_id}' does not exist.")

    def _nest_subtasks(self, todo_pairs: List[Tuple[Todo, Todo]]) -> List[TodoResponse]:
        """Convert flat todo pairs into nested structure.

        Args:
            todo_pairs (List[Tuple[Todo, Todo]]): List of (parent, subtask) pairs

        Returns:
            List[TodoResponse]: List of todos with nested subtasks
        """
        todos_dict: Dict[int, TodoResponse] = {}
        subtasks_map: Dict[int, List[Todo]] = defaultdict(list)

        for parent, sub in todo_pairs:
            parent_response = TodoResponse(**parent.model_dump())
            if parent.id not in todos_dict:
                todos_dict[parent.id] = parent_response
            if sub:
                subtasks_map[parent.id].append(sub)
        
        for parent_id, subtasks in subtasks_map.items():
            todos_dict[parent_id].subtasks.extend(subtasks)

        return list(todos_dict.values())

    async def create_todo(self, todo_in: TodoCreate, current_user: User) -> TodoResponse:
        """Create a new todo.

        Args:
            todo_in (TodoCreate): Todo creation data
            current_user (User): Current authenticated user

        Returns:
            TodoResponse: Created todo

        Raises:
            ValidationException: If parent todo validation fails
            BaseAppException: If creation fails
        """
        try:
            if todo_in.parent_id:
                await self._validate_parent_todo(todo_in.parent_id, current_user.id)

            todo = Todo(
                **todo_in.model_dump(),
                user_id=current_user.id
            )
            self.db.add(todo)
            await self.db.commit()
            await self.db.refresh(todo)

            return TodoResponse(**todo.model_dump())
        
        except IntegrityError as e:
            self._handle_foreign_key_violation(e, todo_in.parent_id)
            raise
        except ValidationException:
            raise
        except Exception as e:
            logger.error(f"Error creating todo: {e}", exc_info=True)
            raise BaseAppException("Could not create todo. Please try again later.") from e

    async def list_todos(
        self,
        current_user: User,
        filters: TodoFilter,
        pagination: PaginationParams
    ) -> Dict[str, Any]:
        """List todos with filtering and pagination.

        Args:
            current_user (User): Current authenticated user
            filters (TodoFilter): Filter criteria
            pagination (PaginationParams): Pagination parameters

        Returns:
            Dict[str, Any]: Paginated list of todos with metadata

        Raises:
            BaseAppException: If retrieval fails
        """
        try:
            parent = aliased(Todo, name="t")
            subtask = aliased(Todo, name="st")

            db_query = (
                select(parent, subtask)
                .join_from(parent, subtask, subtask.parent_id == parent.id, isouter=True)
                .where((parent.user_id == current_user.id) & (parent.parent_id.is_(None)))
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

            # Get total count for pagination
            count_query = select(func.count()).select_from(db_query.subquery())
            total_records = await self.db.execute(count_query)
            total_records = total_records.scalar_one()

            # Apply pagination
            db_query = db_query.offset((pagination.page - 1) * pagination.page_size).limit(pagination.page_size)

            # Execute query
            result = await self.db.execute(db_query)
            todo_pairs = result.all()

            todos = self._nest_subtasks(todo_pairs)
            return {
                "items": todos,
                "total_count": total_records,
                "page": pagination.page,
                "page_size": pagination.page_size
            }
        except Exception as e:
            logger.error(f"Error retrieving todos: {e}", exc_info=True)
            raise BaseAppException("Could not retrieve todos. Please try again later.") from e

    async def get_todo(self, todo_id: int, current_user: User) -> TodoResponse:
        """Get a single todo by ID.

        Args:
            todo_id (int): ID of the todo to retrieve
            current_user (User): Current authenticated user

        Returns:
            TodoResponse: The requested todo

        Raises:
            ResourceNotFoundException: If todo not found
            BaseAppException: If retrieval fails
        """
        try:
            todo = await self._get_todo_by_id(todo_id, current_user.id)
            if not todo:
                raise ResourceNotFoundException(message="Todo not found")
            return TodoResponse(**todo.model_dump())
        except ResourceNotFoundException:
            raise
        except Exception as e:
            logger.error(f"Error retrieving todo: {e}", exc_info=True)
            raise BaseAppException("Could not retrieve todo. Please try again later.") from e

    async def update_todo(self, todo_id: int, todo_in: TodoUpdate, current_user: User) -> TodoResponse:
        """Update an existing todo.

        Args:
            todo_id (int): ID of the todo to update
            todo_in (TodoUpdate): Updated todo data
            current_user (User): Current authenticated user

        Returns:
            TodoResponse: Updated todo

        Raises:
            ResourceNotFoundException: If todo not found
            ValidationException: If parent todo validation fails
            BaseAppException: If update fails
        """
        try:
            todo = await self._get_todo_by_id(todo_id, current_user.id)
            if not todo:
                raise ResourceNotFoundException(message="Todo not found")

            # If updating parent_id, verify the new parent exists and belongs to the user
            if todo_in.parent_id is not None:
                if todo_in.parent_id == todo_id:
                    raise ValidationException(message="Todo cannot be its own parent")
                await self._validate_parent_todo(todo_in.parent_id, current_user.id)

            # Update todo
            todo_data = todo_in.model_dump(exclude_unset=True)
            for field, value in todo_data.items():
                setattr(todo, field, value)

            await self.db.commit()
            await self.db.refresh(todo)

            return TodoResponse(**todo.model_dump())
        except IntegrityError as e:
            self._handle_foreign_key_violation(e, todo_in.parent_id)
            raise
        except (ResourceNotFoundException, ValidationException):
            raise
        except Exception as e:
            logger.error(f"Error updating todo: {e}", exc_info=True)
            raise BaseAppException("Could not update todo. Please try again later.") from e

    async def delete_todo(self, todo_id: int, current_user: User) -> None:
        """Delete a todo.

        Args:
            todo_id (int): ID of the todo to delete
            current_user (User): Current authenticated user

        Raises:
            ResourceNotFoundException: If todo not found
            BaseAppException: If deletion fails
        """
        try:
            todo = await self._get_todo_by_id(todo_id, current_user.id)
            if not todo:
                raise ResourceNotFoundException(message="Todo not found")
            
            await self.db.delete(todo)
            await self.db.commit()
        except ResourceNotFoundException:
            raise
        except Exception as e:
            logger.error(f"Error deleting todo: {e}", exc_info=True)
            raise BaseAppException("Could not delete todo. Please try again later.") from e

    async def reorder_todos(self, reorder_request: TodoReorderRequest, current_user: User) -> List[Todo]:
        """Reorder a list of todos.

        Args:
            reorder_request (TodoReorderRequest): Reordering request data
            current_user (User): Current authenticated user

        Returns:
            List[Todo]: Reordered todos

        Raises:
            ValidationException: If validation fails
            ResourceNotFoundException: If parent todo not found
            BaseAppException: If reordering fails
        """
        try:
            # Get all todos that need to be reordered
            todo_ids = [reorder.todo_id for reorder in reorder_request.reorders]
            query = select(Todo).where(
                and_(
                    Todo.id.in_(todo_ids),
                    Todo.user_id == current_user.id
                )
            )
            result = await self.db.execute(query)
            todos = result.scalars().all()

            # Verify all todos exist and belong to the user
            if len(todos) != len(todo_ids):
                raise ValidationException(message="One or more todos not found")

            # If parent_id is provided, verify it exists and belongs to the user
            if reorder_request.parent_id is not None:
                parent = await self._get_todo_by_id(reorder_request.parent_id, current_user.id)
                if not parent:
                    raise ResourceNotFoundException(message="Parent todo not found")
                # Verify all todos are subtasks of the specified parent
                for todo in todos:
                    if todo.parent_id != reorder_request.parent_id:
                        raise ValidationException(
                            message="All todos must be subtasks of the specified parent"
                        )
            else:
                # Verify all todos are root-level todos (no parent)
                for todo in todos:
                    if todo.parent_id is not None:
                        raise ValidationException(
                            message="All todos must be root-level todos when no parent is specified"
                        )

            # Create a mapping of todo_id to new order
            order_mapping = {reorder.todo_id: reorder.new_order for reorder in reorder_request.reorders}

            # Update todos with new orders
            for todo in todos:
                todo.order = order_mapping[todo.id]

            await self.db.commit()
            
            return todos
        except (ValidationException, ResourceNotFoundException):
            raise
        except Exception as e:
            logger.error(f"Error reordering todos: {e}", exc_info=True)
            raise BaseAppException("Could not reorder todos. Please try again later.") from e 