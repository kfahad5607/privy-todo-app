export const TODO_STATUS = {
  PENDING: {
    label: 'Pending',
    value: 'pending',
    color: 'bg-yellow-100 text-yellow-800',
  },
  IN_PROGRESS: {
    label: 'In Progress',
    value: 'in_progress',
    color: 'bg-blue-100 text-blue-800',
  },
  COMPLETED: {
    label: 'Completed',
    value: 'completed',
    color: 'bg-green-100 text-green-800',
  },
} as const;

export const TODO_STATUS_VALUES = Object.values(TODO_STATUS).map((status) => status.value);
export const TODO_STATUS_LABELS = Object.fromEntries(Object.values(TODO_STATUS).map((status) => [status.value, status.label]));
export const TODO_STATUS_COLORS = Object.fromEntries(Object.values(TODO_STATUS).map((status) => [status.value, status.color]));

export const TODO_STATUS_OPTIONS = Object.values(TODO_STATUS).map((status) => ({
  value: status.value,
  label: status.label,
}));