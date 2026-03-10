/**
 * Milestones API module: CRUD, task linking, progress tracking.
 */

import apiClient from './client';
import type { User, Task } from './tasks';

export interface Milestone {
  id: string;
  title: string;
  description: string;
  status: 'not_started' | 'in_progress' | 'completed' | 'overdue' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'critical';
  owner: User | null;
  start_date: string | null;
  due_date: string;
  completed_at: string | null;
  color: string;
  position: number;
  progress_percentage: number;
  total_tasks: number;
  completed_tasks: number;
  is_overdue: boolean;
  created_at: string;
  updated_at: string;
}

export interface MilestoneDetail extends Milestone {
  tasks: Array<{
    id: string;
    task: Task;
    added_at: string;
  }>;
}

export const milestonesApi = {
  list(params?: { project?: string; status?: string; priority?: string }) {
    return apiClient.get<{ results: Milestone[] }>('/milestones/', { params });
  },

  get(id: string) {
    return apiClient.get<MilestoneDetail>(`/milestones/${id}/`);
  },

  create(data: {
    title: string;
    project_id: string;
    description?: string;
    priority?: string;
    owner?: string;
    start_date?: string;
    due_date: string;
    color?: string;
  }) {
    return apiClient.post<Milestone>('/milestones/', data);
  },

  update(id: string, data: Partial<Milestone>) {
    return apiClient.patch<Milestone>(`/milestones/${id}/`, data);
  },

  delete(id: string) {
    return apiClient.delete(`/milestones/${id}/`);
  },

  complete(id: string) {
    return apiClient.post<Milestone>(`/milestones/${id}/complete/`);
  },

  reopen(id: string) {
    return apiClient.post<Milestone>(`/milestones/${id}/reopen/`);
  },

  addTasks(milestoneId: string, taskIds: string[]) {
    return apiClient.post(`/milestones/${milestoneId}/add_tasks/`, {
      task_ids: taskIds,
    });
  },

  removeTasks(milestoneId: string, taskIds: string[]) {
    return apiClient.post(`/milestones/${milestoneId}/remove_tasks/`, {
      task_ids: taskIds,
    });
  },

  getTasks(milestoneId: string) {
    return apiClient.get(`/milestones/${milestoneId}/tasks/`);
  },
};
