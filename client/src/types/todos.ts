export type TodoStatus = 'pending' | 'in_progress' | 'completed';

export interface Todo {
  id: number;
  title: string;
  status: TodoStatus;
  is_bookmarked: boolean;
  order: number;
  parent_id: number | null;
  user_id: number;
  created_at: string;
  updated_at: string;
  subtasks: Todo[];
}

export interface TodoCreate {
  title: string;
  status: TodoStatus;
  is_bookmarked?: boolean;
  parent_id?: number | null;
}

export interface TodoUpdate {
  title?: string;
  status?: TodoStatus;
  is_bookmarked?: boolean;
  parent_id?: number | null;
}

export interface TodoFilter {
  status?: TodoStatus;
  is_bookmarked?: 'true' | 'false';
  parent_id?: number | null;
  search?: string;
}

export interface PaginationParams {
  page: number;
  page_size: number;
  order_by?: string;
  order_direction?: 'asc' | 'desc';
}

export interface TodoReorder {
  todo_id: number;
  new_order: number;
}

export interface TodoReorderRequest {
  reorders: TodoReorder[];
  parent_id?: number | null;
}

export interface PaginatedResponse<T> {
  items: T[];
  total_count: number;
  page: number;
  page_size: number;
} 