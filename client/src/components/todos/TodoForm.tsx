import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import type { Todo } from '@/types/todos';
import { todoCreateSchema, todoUpdateSchema } from '@/schemas/todos';
import type { TodoCreateFormData, TodoUpdateFormData } from '@/schemas/todos';
import { TODO_STATUS_OPTIONS } from '@/utils/constants';

interface TodoFormProps {
  todo?: Todo;
  onSubmit: (data: TodoCreateFormData | TodoUpdateFormData) => void;
  onCancel: () => void;
}

export function TodoForm({ todo, onSubmit, onCancel }: TodoFormProps) {
  const isEditing = !!todo;
  const form = useForm<TodoCreateFormData | TodoUpdateFormData>({
    resolver: zodResolver(isEditing ? todoUpdateSchema : todoCreateSchema),
    defaultValues: todo ? {
      title: todo.title,
      status: todo.status,
      is_bookmarked: todo.is_bookmarked,
      parent_id: todo.parent_id
    } : {
      status: 'pending',
      is_bookmarked: false
    }
  });

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700">
          Title
        </label>
        <input
          {...form.register('title')}
          type="text"
          id="title"
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
        {form.formState.errors.title && (
          <p className="mt-1 text-sm text-red-600">
            {form.formState.errors.title.message}
          </p>
        )}
      </div>

      <div>
        <label htmlFor="status" className="block text-sm font-medium text-gray-700">
          Status
        </label>
        <select
          {...form.register('status')}
          id="status"
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          {TODO_STATUS_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>{option.label}</option>
          ))}
        </select>
      </div>

      <div className="flex items-center">
        <input
          {...form.register('is_bookmarked')}
          type="checkbox"
          id="is_bookmarked"
          className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
        />
        <label htmlFor="is_bookmarked" className="ml-2 block text-sm text-gray-700">
          Bookmark
        </label>
      </div>

      <div className="flex justify-end space-x-3">
        <button
          type="button"
          onClick={onCancel}
          className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          Cancel
        </button>
        <button
          type="submit"
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          {isEditing ? 'Update' : 'Create'}
        </button>
      </div>
    </form>
  );
} 