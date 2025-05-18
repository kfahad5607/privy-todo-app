import type { TodoUpdateFormData } from '@/schemas/todos';
import type { Todo } from '@/types/todos';
import { TODO_STATUS, TODO_STATUS_COLORS, TODO_STATUS_LABELS } from '@/utils/constants';
import Badge from '../ui/Badge';

interface Props {
  todo: Todo;
  onEdit: (todo: Todo) => void;
  onDelete: (todo: Todo) => void;
  onUpdate: (todo: TodoUpdateFormData) => Promise<void>;
  className?: string;
  isSubtask?: boolean;
}

const TodoItem = ({ todo, onEdit, onDelete, onUpdate, className = '', isSubtask = false }: Props) => {
  return (
    <div className={`flex items-center justify-between space-x-5 ${className}`}>
    <div className="flex items-center space-x-2 min-w-0">
      <input
        type="checkbox"
        checked={todo.status === TODO_STATUS.COMPLETED.value}
        onChange={(e) =>
          onUpdate({
            status: e.target.checked
              ? TODO_STATUS.COMPLETED.value
              : TODO_STATUS.PENDING.value,
          })
        }
        className="h-4 w-4 rounded border-gray-300 flex-shrink-0"
      />
      <div className="flex items-center space-x-6">
        <p
          className={`${isSubtask ? '' : 'text-lg font-medium'} ${todo.status === TODO_STATUS.COMPLETED.value ? 'line-through text-gray-500' : ''}`}
          style={{ maxWidth: '100%' }}
        >
          {todo.title}
        </p>
        <span className="text-sm text-gray-500 flex-shrink-0">
          <Badge text={TODO_STATUS_LABELS[todo.status]} className={TODO_STATUS_COLORS[todo.status]} />
        </span>
      </div>
    </div>
    <div className="flex items-center justify-end space-x-2 flex-shrink-0 w-[100px]">
      <button
        onClick={() => onEdit(todo)}
        className="text-blue-600 hover:text-blue-800"
      >
        Edit
      </button>
      <button
        onClick={() => onDelete(todo)}
        className="text-red-600 hover:text-red-800"
      >
        Delete
      </button>
    </div>
  </div>
  );
};

export default TodoItem;