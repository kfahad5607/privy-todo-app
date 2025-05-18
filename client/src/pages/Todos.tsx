import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';
import type { Todo, TodoStatus } from '@/types/todos';
import type { TodoCreateFormData, TodoUpdateFormData } from '@/schemas/todos';
import { todoService } from '@/services/todoService';
import { TodoCard } from '@/components/todos/TodoCard';
import { TodoForm } from '@/components/todos/TodoForm';
import { TODO_STATUS_OPTIONS } from '@/utils/constants';
import SpinnerLoader from '@/components/ui/SpinnerLoader';

export function Todos() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedTodo, setSelectedTodo] = useState<Todo | undefined>();
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [todoToDelete, setTodoToDelete] = useState<Todo | undefined>();
  const queryClient = useQueryClient();

  // Get query parameters with defaults
  const page = Number(searchParams.get('page')) || 1;
  const pageSize = Number(searchParams.get('page_size')) || 10;
  const status = searchParams.get('status') as TodoStatus | undefined;
  const isBookmarked = searchParams.get('is_bookmarked') as 'true' | 'false' | undefined;
  const search = searchParams.get('search') || '';

  // Fetch todos
  const { data, isLoading } = useQuery({
    queryKey: ['todos', { page, pageSize, status, isBookmarked, search }],
    queryFn: () => todoService.listTodos(
      { status, is_bookmarked: isBookmarked, search },
      { page, page_size: pageSize }
    )
  });

  const handleCreateTodo = async (data: TodoCreateFormData) => {
    try {
      await todoService.createTodo(data);
      await queryClient.invalidateQueries({ queryKey: ['todos'] });
      setIsModalOpen(false);
      console.log('Todo created successfully', {
        title: 'Success',
        description: 'Todo created successfully'
      });
    } catch (error) {
      console.log('Todo created failed', {
        title: 'Error',
        description: 'Failed to create todo',
      });
    }
  };

  const handleUpdateTodo = async (data: TodoUpdateFormData) => {
    if (!selectedTodo) return;
    try {
      await todoService.updateTodo(selectedTodo.id, data);
      await queryClient.invalidateQueries({ queryKey: ['todos'] });
      setIsModalOpen(false);
      setSelectedTodo(undefined);
      console.log('Todo updated successfully', {
        title: 'Success',
        description: 'Todo updated successfully'
      });
    } catch (error) {
      console.log('Todo updated failed', {
        title: 'Error',
        description: 'Failed to update todo',
      });
    }
  };

  const handleDeleteTodo = async () => {
    if (!todoToDelete) return;
    try {
      await todoService.deleteTodo(todoToDelete.id);
      await queryClient.invalidateQueries({ queryKey: ['todos'] });
      setIsDeleteModalOpen(false);
      setTodoToDelete(undefined);
      console.log('Todo deleted successfully', {
        title: 'Success',
        description: 'Todo deleted successfully'
      });
    } catch (error) {
      console.log('Todo deleted failed', {
        title: 'Error',
        description: 'Failed to delete todo',
      });
    }
  };

  const handleFilterChange = (key: string, value: string | null) => {
    const newParams = new URLSearchParams(searchParams);
    if (value === null) {
      newParams.delete(key);
    } else {
      newParams.set(key, value);
    }
    // newParams.set('page', '1'); // Reset to first page on filter change
    setSearchParams(newParams);
  };

  return (
    <div>
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold">Todos</h1>
        <button
          onClick={() => {
            setSelectedTodo(undefined);
            setIsModalOpen(true);
          }}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
        >
          Add Todo
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-md p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label htmlFor="search" className="block text-sm font-medium text-gray-700">
              Search
            </label>
            <input
              type="text"
              id="search"
              value={search}
              onChange={(e) => handleFilterChange('search', e.target.value || null)}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2"
              placeholder="Search todos..."
            />
          </div>
          <div>
            <label htmlFor="status" className="block text-sm font-medium text-gray-700">
              Status
            </label>
            <select
              id="status"
              value={status || ''}
              onChange={(e) => handleFilterChange('status', e.target.value || null)}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2"
            >
              <option value="">All</option>
              {TODO_STATUS_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="is_bookmarked_filter" className="block text-sm font-medium text-gray-700">
              Bookmarked
            </label>
            <select
              id="is_bookmarked_filter"
              value={isBookmarked ? 'true' : ''}
              onChange={(e) => handleFilterChange('is_bookmarked', e.target.value || null)}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2"
            >
              <option value="">All</option>
              <option value="true">Bookmarked</option>
              <option value="false">Not Bookmarked</option>
            </select>
          </div>
          <div>
            <label htmlFor="page_size" className="block text-sm font-medium text-gray-700">
              Items per page
            </label>
            <select
              id="page_size"
              value={pageSize}
              onChange={(e) => handleFilterChange('page_size', e.target.value)}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2"
            >
              <option value="5">5</option>
              <option value="10">10</option>
              <option value="20">20</option>
              <option value="50">50</option>
            </select>
          </div>
        </div>
      </div>

      {/* Todo List */}
      {isLoading ? (
        <div className="text-center py-8">
          <SpinnerLoader size="lg" />
        </div>
      ) : (
        <div className="space-y-4">
          {data?.items.map((todo) => (
            <TodoCard
              key={todo.id}
              todo={todo}
              onEdit={(todo) => {
                setSelectedTodo(todo);
                setIsModalOpen(true);
              }}
              onDelete={(todo) => {
                setTodoToDelete(todo);
                setIsDeleteModalOpen(true);
              }}
            />
          ))}
        </div>
      )}

      {/* Pagination */}
      {data && data.total_count > 0 ? (
        <div className="mt-6 mb-10 flex justify-between items-center">
          <div className="text-sm text-gray-700">
            Showing {((page - 1) * pageSize) + 1} to {Math.min(page * pageSize, data.total_count)} of {data.total_count} items
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => handleFilterChange('page', String(page - 1))}
              disabled={page === 1}
              className="px-3 py-1 rounded-md border border-gray-300 disabled:opacity-50"
            >
              Previous
            </button>
            <button
              onClick={() => handleFilterChange('page', String(page + 1))}
              disabled={page * pageSize >= data.total_count}
              className="px-3 py-1 rounded-md border border-gray-300 disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      ) : (
        <div className="mt-6 mb-10 flex justify-center items-center">
          <div className="text-lg text-gray-700">
            No todos found.
          </div>
        </div>
      )}

      {/* Create/Edit Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">
              {selectedTodo ? 'Edit Todo' : 'Create Todo'}
            </h2>
            <TodoForm
              todo={selectedTodo}
              onSubmit={(data) => {
                console.log('onSubmit', data);
                if (selectedTodo) {
                  handleUpdateTodo(data as TodoUpdateFormData);
                } else {
                  handleCreateTodo(data as TodoCreateFormData);
                }
              }}
              onCancel={() => {
                setIsModalOpen(false);
                setSelectedTodo(undefined);
              }}
            />
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {isDeleteModalOpen && todoToDelete && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Delete Todo</h2>
            <p className="mb-4">
              Are you sure you want to delete "{todoToDelete.title}"? This action cannot be undone.
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => {
                  setIsDeleteModalOpen(false);
                  setTodoToDelete(undefined);
                }}
                className="px-4 py-2 rounded-md border border-gray-300"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteTodo}
                className="px-4 py-2 rounded-md bg-red-600 text-white hover:bg-red-700"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 