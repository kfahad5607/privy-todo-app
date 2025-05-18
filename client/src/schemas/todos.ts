import { z } from 'zod';

export const todoStatusSchema = z.enum(['pending', 'in_progress', 'completed']);

export const todoCreateSchema = z.object({
  title: z.string().min(1, 'Title is required').max(255, 'Title must be less than 255 characters'),
  status: todoStatusSchema,
  is_bookmarked: z.boolean().optional().default(false),
  parent_id: z.number().nullable().optional()
});

export const todoUpdateSchema = todoCreateSchema.partial();

export const todoFilterSchema = z.object({
  status: todoStatusSchema.optional(),
  is_bookmarked: z.boolean().optional(),
  parent_id: z.number().nullable().optional(),
  search: z.string().optional()
});

export const paginationSchema = z.object({
  page: z.number().int().min(1).default(1),
  page_size: z.number().int().min(1).max(100).default(10),
  order_by: z.string().optional(),
  order_direction: z.enum(['asc', 'desc']).optional()
});

export type TodoCreateFormData = z.infer<typeof todoCreateSchema>;
export type TodoUpdateFormData = z.infer<typeof todoUpdateSchema>;
export type TodoFilterFormData = z.infer<typeof todoFilterSchema>;
export type PaginationFormData = z.infer<typeof paginationSchema>; 