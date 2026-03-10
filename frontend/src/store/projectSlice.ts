/**
 * Project store slice: manages project list, active project, board state.
 */

import { create } from 'zustand';
import { projectsApi } from '../api/projects';
import type { Project, Board } from '../api/projects';

interface ProjectState {
  projects: Project[];
  activeProject: Project | null;
  activeBoard: Board | null;
  isLoading: boolean;
  error: string | null;

  fetchProjects: (workspaceId?: string) => Promise<void>;
  fetchProject: (id: string) => Promise<void>;
  fetchBoard: (projectId: string) => Promise<void>;
  setActiveProject: (project: Project | null) => void;
  createProject: (data: Partial<Project> & { workspace_id: string }) => Promise<Project>;
  updateProject: (id: string, data: Partial<Project>) => Promise<void>;
  archiveProject: (id: string) => Promise<void>;
  clearError: () => void;
}

export const useProjectStore = create<ProjectState>()((set, get) => ({
  projects: [],
  activeProject: null,
  activeBoard: null,
  isLoading: false,
  error: null,

  fetchProjects: async (workspaceId) => {
    set({ isLoading: true, error: null });
    try {
      const { data } = await projectsApi.list(
        workspaceId ? { workspace: workspaceId } : undefined
      );
      set({ projects: data.results, isLoading: false });
    } catch (err) {
      set({ error: 'Failed to load projects.', isLoading: false });
    }
  },

  fetchProject: async (id) => {
    set({ isLoading: true, error: null });
    try {
      const { data } = await projectsApi.get(id);
      set({ activeProject: data, isLoading: false });
    } catch (err) {
      set({ error: 'Failed to load project.', isLoading: false });
    }
  },

  fetchBoard: async (projectId) => {
    try {
      const { data } = await projectsApi.getBoard(projectId);
      set({ activeBoard: data });
    } catch (err) {
      set({ error: 'Failed to load board.' });
    }
  },

  setActiveProject: (project) => {
    set({ activeProject: project });
  },

  createProject: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const { data: newProject } = await projectsApi.create(data);
      set((state) => ({
        projects: [newProject, ...state.projects],
        isLoading: false,
      }));
      return newProject;
    } catch (err) {
      set({ error: 'Failed to create project.', isLoading: false });
      throw err;
    }
  },

  updateProject: async (id, data) => {
    try {
      const { data: updated } = await projectsApi.update(id, data);
      set((state) => ({
        projects: state.projects.map((p) => (p.id === id ? updated : p)),
        activeProject: state.activeProject?.id === id ? updated : state.activeProject,
      }));
    } catch (err) {
      set({ error: 'Failed to update project.' });
    }
  },

  archiveProject: async (id) => {
    try {
      await projectsApi.archive(id);
      set((state) => ({
        projects: state.projects.filter((p) => p.id !== id),
        activeProject: state.activeProject?.id === id ? null : state.activeProject,
      }));
    } catch (err) {
      set({ error: 'Failed to archive project.' });
    }
  },

  clearError: () => set({ error: null }),
}));
