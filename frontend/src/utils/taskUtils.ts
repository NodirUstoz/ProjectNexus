/**
 * Task-related utility functions: priority colors, type icons, status helpers.
 */

export type Priority = 'lowest' | 'low' | 'medium' | 'high' | 'highest';
export type TaskType = 'story' | 'task' | 'bug' | 'epic' | 'subtask';

/**
 * Priority configuration with colors and display labels.
 */
export const PRIORITY_CONFIG: Record<Priority, {
  label: string;
  color: string;
  bgColor: string;
  icon: string;
}> = {
  highest: { label: 'Highest', color: '#DC2626', bgColor: '#FEE2E2', icon: 'arrow-double-up' },
  high: { label: 'High', color: '#F97316', bgColor: '#FFEDD5', icon: 'arrow-up' },
  medium: { label: 'Medium', color: '#EAB308', bgColor: '#FEF9C3', icon: 'minus' },
  low: { label: 'Low', color: '#3B82F6', bgColor: '#DBEAFE', icon: 'arrow-down' },
  lowest: { label: 'Lowest', color: '#6B7280', bgColor: '#F3F4F6', icon: 'arrow-double-down' },
};

/**
 * Task type configuration with colors and display labels.
 */
export const TASK_TYPE_CONFIG: Record<TaskType, {
  label: string;
  color: string;
  bgColor: string;
  icon: string;
}> = {
  epic: { label: 'Epic', color: '#7C3AED', bgColor: '#EDE9FE', icon: 'lightning-bolt' },
  story: { label: 'Story', color: '#10B981', bgColor: '#D1FAE5', icon: 'bookmark' },
  task: { label: 'Task', color: '#3B82F6', bgColor: '#DBEAFE', icon: 'check-square' },
  bug: { label: 'Bug', color: '#EF4444', bgColor: '#FEE2E2', icon: 'bug' },
  subtask: { label: 'Subtask', color: '#6B7280', bgColor: '#F3F4F6', icon: 'subdirectory' },
};

/**
 * Get the display configuration for a priority level.
 */
export function getPriorityConfig(priority: string) {
  return PRIORITY_CONFIG[priority as Priority] || PRIORITY_CONFIG.medium;
}

/**
 * Get the display configuration for a task type.
 */
export function getTaskTypeConfig(type: string) {
  return TASK_TYPE_CONFIG[type as TaskType] || TASK_TYPE_CONFIG.task;
}

/**
 * Sort tasks by priority (highest first) then by position.
 */
export function sortTasksByPriority<T extends { priority: string; position: number }>(
  tasks: T[]
): T[] {
  const priorityOrder: Record<string, number> = {
    highest: 0,
    high: 1,
    medium: 2,
    low: 3,
    lowest: 4,
  };

  return [...tasks].sort((a, b) => {
    const priorityDiff =
      (priorityOrder[a.priority] ?? 5) - (priorityOrder[b.priority] ?? 5);
    if (priorityDiff !== 0) return priorityDiff;
    return a.position - b.position;
  });
}

/**
 * Group tasks by their column ID for board view rendering.
 */
export function groupTasksByColumn<T extends { column: string | null }>(
  tasks: T[]
): Record<string, T[]> {
  const grouped: Record<string, T[]> = {};
  for (const task of tasks) {
    const key = task.column || 'unassigned';
    if (!grouped[key]) {
      grouped[key] = [];
    }
    grouped[key].push(task);
  }
  return grouped;
}

/**
 * Calculate progress percentage from completed and total counts.
 */
export function calculateProgress(completed: number, total: number): number {
  if (total === 0) return 0;
  return Math.round((completed / total) * 100);
}

/**
 * Generate a user-friendly task filter description.
 */
export function describeFilters(filters: Record<string, string | undefined>): string {
  const parts: string[] = [];
  if (filters.priority) parts.push(`Priority: ${filters.priority}`);
  if (filters.type) parts.push(`Type: ${filters.type}`);
  if (filters.assignee) parts.push('Assigned');
  if (filters.search) parts.push(`Search: "${filters.search}"`);
  return parts.length > 0 ? parts.join(' | ') : 'All tasks';
}
