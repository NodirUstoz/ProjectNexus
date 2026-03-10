/**
 * Tasks API module: CRUD, move, comments, attachments, subtasks, history.
 */

import apiClient from './client';
import type { User } from './projects';

export interface Task {
  id: string;
  task_key: string;
  task_number: number;
  title: string;
  description: string;
  task_type: 'story' | 'task' | 'bug' | 'epic' | 'subtask';
  priority: 'lowest' | 'low' | 'medium' | 'high' | 'highest';
  assignee: User | null;
  reporter: User | null;
  labels: Array<{ id: string; name: string; color: string }>;
  story_points: number | null;
  original_estimate_hours: number | null;
  time_spent_hours: number;
  due_date: string | null;
  start_date: string | null;
  completed_at: string | null;
  column: string | null;
  sprint: string | null;
  position: number;
  subtask_count: number;
  subtask_completed: number;
  comment_count: number;
  attachment_count: number;
  created_at: string;
  updated_at: string;
}

export interface TaskComment {
  id: string;
  author: User;
  content: string;
  edited: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaskFilters {
  project?: string;
  sprint?: string;
  column?: string;
  assignee?: string;
  priority?: string;
  type?: string;
  backlog?: string;
  search?: string;
}

export const tasksApi = {
  list(filters?: TaskFilters) {
    return apiClient.get<{ results: Task[] }>('/tasks/', { params: filters });
  },

  get(id: string) {
    return apiClient.get<Task>(`/tasks/${id}/`);
  },

  create(data: {
    title: string;
    project_id: string;
    description?: string;
    task_type?: string;
    priority?: string;
    assignee?: string;
    column?: string;
    sprint?: string;
    story_points?: number;
    label_ids?: string[];
  }) {
    return apiClient.post<Task>('/tasks/', data);
  },

  update(id: string, data: Partial<Task> & { label_ids?: string[] }) {
    return apiClient.patch<Task>(`/tasks/${id}/`, data);
  },

  delete(id: string) {
    return apiClient.delete(`/tasks/${id}/`);
  },

  move(id: string, columnId: string, position: number) {
    return apiClient.post<Task>(`/tasks/${id}/move/`, {
      column_id: columnId,
      position,
    });
  },

  getComments(taskId: string) {
    return apiClient.get<TaskComment[]>(`/tasks/${taskId}/comments/`);
  },

  addComment(taskId: string, content: string) {
    return apiClient.post<TaskComment>(`/tasks/${taskId}/comments/`, { content });
  },

  getAttachments(taskId: string) {
    return apiClient.get(`/tasks/${taskId}/attachments/`);
  },

  uploadAttachment(taskId: string, file: File) {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post(`/tasks/${taskId}/attachments/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  getSubtasks(taskId: string) {
    return apiClient.get(`/tasks/${taskId}/subtasks/`);
  },

  addSubtask(taskId: string, title: string) {
    return apiClient.post(`/tasks/${taskId}/subtasks/`, { title });
  },

  toggleSubtask(subtaskId: string) {
    return apiClient.post(`/subtasks/${subtaskId}/toggle/`);
  },

  getHistory(taskId: string) {
    return apiClient.get(`/tasks/${taskId}/history/`);
  },
};
