/**
 * Teams API module: CRUD, member management, project assignment, workload.
 */

import apiClient from './client';
import type { User } from './projects';

export interface Team {
  id: string;
  name: string;
  description: string;
  lead: User | null;
  avatar: string | null;
  color: string;
  is_active: boolean;
  member_count: number;
  active_tasks_count: number;
  created_at: string;
  updated_at: string;
}

export interface TeamMember {
  id: string;
  user: User;
  role: 'lead' | 'senior' | 'member';
  joined_at: string;
}

export interface WorkloadEntry {
  user: { id: string; email: string; full_name: string };
  role: string;
  active_tasks: number;
  total_story_points: number;
  tasks_by_priority: Record<string, number>;
}

export const teamsApi = {
  list(params?: { workspace?: string; active?: string }) {
    return apiClient.get<{ results: Team[] }>('/teams/', { params });
  },

  get(id: string) {
    return apiClient.get<Team>(`/teams/${id}/`);
  },

  create(data: {
    name: string;
    workspace_id: string;
    description?: string;
    lead?: string;
    color?: string;
  }) {
    return apiClient.post<Team>('/teams/', data);
  },

  update(id: string, data: Partial<Team>) {
    return apiClient.patch<Team>(`/teams/${id}/`, data);
  },

  delete(id: string) {
    return apiClient.delete(`/teams/${id}/`);
  },

  getMembers(teamId: string) {
    return apiClient.get<TeamMember[]>(`/teams/${teamId}/members/`);
  },

  addMember(teamId: string, userId: string, role: string = 'member') {
    return apiClient.post<TeamMember>(`/teams/${teamId}/add_member/`, {
      user_id: userId,
      role,
    });
  },

  removeMember(teamId: string, memberId: string) {
    return apiClient.delete(`/teams/${teamId}/members/${memberId}/`);
  },

  assignProject(teamId: string, projectId: string) {
    return apiClient.post(`/teams/${teamId}/assign_project/`, {
      project_id: projectId,
    });
  },

  unassignProject(teamId: string, projectId: string) {
    return apiClient.delete(`/teams/${teamId}/projects/${projectId}/`);
  },

  getWorkload(teamId: string) {
    return apiClient.get<WorkloadEntry[]>(`/teams/${teamId}/workload/`);
  },
};
