import { useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import type { Todo, TodoStatus } from '@/types/todos';
import { todoCreateSchema, todoUpdateSchema } from '@/schemas/todos';
import type { TodoCreateFormData, TodoUpdateFormData } from '@/schemas/todos';
import { todoService } from '@/services/todoService';
import { TODO_STATUS, TODO_STATUS_COLORS, TODO_STATUS_LABELS } from '@/utils/constants';
import Badge from '../ui/Badge';
import TodoItem from './TodoItem';

interface TodoCardProps {
  todo: Todo;
  onEdit: (todo: Todo) => void;
  onDelete: (todo: Todo) => void;
}

export function TodoCard({ todo, onEdit, onDelete }: TodoCardProps) {
  const [isAddingSubtask, setIsAddingSubtask] = useState(false);
  const queryClient = useQueryClient();

  const createForm = useForm<TodoCreateFormData>({
    resolver: zodResolver(todoCreateSchema),
    defaultValues: {
      status: 'pending',
      is_bookmarked: false,
      parent_id: todo.id
    }
  });

  const updateForm = useForm<TodoUpdateFormData>({
    resolver: zodResolver(todoUpdateSchema),
    defaultValues: {
      title: todo.title,
      status: todo.status,
      is_bookmarked: todo.is_bookmarked
    }
  });

  const handleCreateSubtask = async (data: TodoCreateFormData) => {
    try {
      await todoService.createTodo(data);
      await queryClient.invalidateQueries({ queryKey: ['todos'] });
      setIsAddingSubtask(false);
      createForm.reset();
      console.log('Subtask created successfully');
    } catch (error) {
      console.log('Subtask created failed');
    }
  };

  const handleUpdateTodo = async (data: TodoUpdateFormData) => {
    try {
      await todoService.updateTodo(todo.id, data);
      await queryClient.invalidateQueries({ queryKey: ['todos'] });
      console.log('Todo updated successfully');
    } catch (error) {
      console.log('Todo updated failed');
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-4 mb-4">
      <TodoItem todo={todo} onEdit={onEdit} onDelete={onDelete} onUpdate={handleUpdateTodo} className="mb-4" />
      {/* Subtasks */}
      {todo.subtasks.length > 0 && (
        <div className="ml-6 mt-2">
          {todo.subtasks.map((subtask) => (
            <TodoItem key={subtask.id} todo={subtask} onEdit={onEdit} onDelete={onDelete} onUpdate={handleUpdateTodo} isSubtask className="py-2.5 border-t" />
          ))}
        </div>
      )}

      {/* Add Subtask Form */}
      {isAddingSubtask ? (
        <form onSubmit={createForm.handleSubmit(handleCreateSubtask)} className="mt-4">
          <div className="flex items-center space-x-2">
            <input
              {...createForm.register('title')}
              placeholder="Enter subtask title"
              className="flex-1 rounded-md border border-gray-300 px-3 py-2"
            />
            <button
              type="submit"
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
            >
              Add
            </button>
            <button
              type="button"
              onClick={() => setIsAddingSubtask(false)}
              className="text-gray-600 hover:text-gray-800"
            >
              Cancel
            </button>
          </div>
          {createForm.formState.errors.title && (
            <p className="text-red-500 text-sm mt-1">
              {createForm.formState.errors.title.message}
            </p>
          )}
        </form>
      ) : (
        <button
          onClick={() => setIsAddingSubtask(true)}
          className="mt-4 text-blue-600 hover:text-blue-800"
        >
          + Add Subtask
        </button>
      )}
    </div>
  );
}