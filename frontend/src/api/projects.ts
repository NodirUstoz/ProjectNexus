/**
 * Projects API module: CRUD operations, board management, member management.
 */

import apiClient from './client';

export interface Project {
  id: string;
  name: string;
  key: string;
  description: string;
  project_type: 'kanban' | 'scrum';
  lead: User | null;
  icon: string;
  color: string;
  is_archived: boolean;
  member_count: number;
  task_count: number;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  full_name: string;
  avatar: string | null;
  job_title: string;
}

export interface Board {
  id: string;
  name: string;
  description: string;
  is_default: boolean;
  columns: BoardColumn[];
  created_at: string;
}

export interface BoardColumn {
  id: string;
  name: string;
  position: number;
  color: string;
  wip_limit: number | null;
  is_done_column: boolean;
  task_count: number;
}

export interface ProjectMember {
  id: string;
  user: User;
  role: 'admin' | 'member' | 'viewer';
  joined_at: string;
}

export const projectsApi = {
  list(params?: { workspace?: string }) {
    return apiClient.get<{ results: Project[] }>('/projects/', { params });
  },

  get(id: string) {
    return apiClient.get<Project>(`/projects/${id}/`);
  },

  create(data: Partial<Project> & { workspace_id: string }) {
    return apiClient.post<Project>('/projects/', data);
  },

  update(id: string, data: Partial<Project>) {
    return apiClient.patch<Project>(`/projects/${id}/`, data);
  },

  delete(id: string) {
    return apiClient.delete(`/projects/${id}/`);
  },

  archive(id: string) {
    return apiClient.post(`/projects/${id}/archive/`);
  },

  unarchive(id: string) {
    return apiClient.post(`/projects/${id}/unarchive/`);
  },

  getBoard(id: string) {
    return apiClient.get<Board>(`/projects/${id}/board/`);
  },

  addMember(projectId: string, userId: string, role: string = 'member') {
    return apiClient.post<ProjectMember>(`/projects/${projectId}/add_member/`, {
      user_id: userId,
      role,
    });
  },

  getLabels(projectId: string) {
    return apiClient.get('/labels/', { params: { project: projectId } });
  },

  createLabel(projectId: string, name: string, color: string) {
    return apiClient.post('/labels/', { project_id: projectId, name, color });
  },

  reorderColumns(boardId: string, columnIds: string[]) {
    return apiClient.post(`/boards/${boardId}/reorder_columns/`, {
      column_ids: columnIds,
    });
  },
};
