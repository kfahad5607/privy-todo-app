import { api } from '@/services/api';
import type {
  Todo,
  TodoCreate,
  TodoUpdate,
  TodoFilter,
  PaginationParams,
  PaginatedResponse,
  TodoReorderRequest
} from '@/types/todos';

export const todoService = {
  async listTodos(filters: TodoFilter, pagination: PaginationParams): Promise<PaginatedResponse<Todo>> {
    const params = new URLSearchParams();
    
    // Add filters
    if (filters.status) params.append('status', filters.status);
    if (filters.is_bookmarked) params.append('is_bookmarked', String(filters.is_bookmarked));
    if (filters.parent_id !== undefined) params.append('parent_id', String(filters.parent_id));
    if (filters.search) params.append('search', filters.search);
    
    // Add pagination
    params.append('page', String(pagination.page));
    params.append('page_size', String(pagination.page_size));
    if (pagination.order_by) params.append('order_by', pagination.order_by);
    if (pagination.order_direction) params.append('order_direction', pagination.order_direction);

    const response = await api.get(`/todos?${params.toString()}`);
    return response.data;
  },

  async getTodo(id: number): Promise<Todo> {
    const response = await api.get(`/todos/${id}`);
    return response.data;
  },

  async createTodo(todo: TodoCreate): Promise<Todo> {
    const response = await api.post('/todos', todo);
    return response.data;
  },

  async updateTodo(id: number, todo: TodoUpdate): Promise<Todo> {
    const response = await api.patch(`/todos/${id}`, todo);
    return response.data;
  },

  async deleteTodo(id: number): Promise<void> {
    await api.delete(`/todos/${id}`);
  },

  async reorderTodos(request: TodoReorderRequest): Promise<Todo[]> {
    const response = await api.post('/todos/reorder', request);
    return response.data;
  }
}; 