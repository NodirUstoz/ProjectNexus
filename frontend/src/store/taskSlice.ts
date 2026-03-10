/**
 * Task store slice: manages task list, filters, drag-and-drop state.
 */

import { create } from 'zustand';
import { tasksApi } from '../api/tasks';
import type { Task, TaskFilters } from '../api/tasks';

interface TaskState {
  tasks: Task[];
  activeTask: Task | null;
  filters: TaskFilters;
  isLoading: boolean;
  error: string | null;

  fetchTasks: (filters?: TaskFilters) => Promise<void>;
  fetchTask: (id: string) => Promise<void>;
  setActiveTask: (task: Task | null) => void;
  createTask: (data: Parameters<typeof tasksApi.create>[0]) => Promise<Task>;
  updateTask: (id: string, data: Partial<Task>) => Promise<void>;
  deleteTask: (id: string) => Promise<void>;
  moveTask: (taskId: string, columnId: string, position: number) => Promise<void>;
  setFilters: (filters: Partial<TaskFilters>) => void;
  clearFilters: () => void;
  clearError: () => void;

  // Optimistic board updates
  optimisticMove: (taskId: string, columnId: string, position: number) => void;
}

export const useTaskStore = create<TaskState>()((set, get) => ({
  tasks: [],
  activeTask: null,
  filters: {},
  isLoading: false,
  error: null,

  fetchTasks: async (filters) => {
    const appliedFilters = filters || get().filters;
    set({ isLoading: true, error: null });
    try {
      const { data } = await tasksApi.list(appliedFilters);
      set({ tasks: data.results, isLoading: false });
    } catch (err) {
      set({ error: 'Failed to load tasks.', isLoading: false });
    }
  },

  fetchTask: async (id) => {
    set({ isLoading: true, error: null });
    try {
      const { data } = await tasksApi.get(id);
      set({ activeTask: data, isLoading: false });
    } catch (err) {
      set({ error: 'Failed to load task.', isLoading: false });
    }
  },

  setActiveTask: (task) => set({ activeTask: task }),

  createTask: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const { data: newTask } = await tasksApi.create(data);
      set((state) => ({
        tasks: [newTask, ...state.tasks],
        isLoading: false,
      }));
      return newTask;
    } catch (err) {
      set({ error: 'Failed to create task.', isLoading: false });
      throw err;
    }
  },

  updateTask: async (id, data) => {
    try {
      const { data: updated } = await tasksApi.update(id, data);
      set((state) => ({
        tasks: state.tasks.map((t) => (t.id === id ? updated : t)),
        activeTask: state.activeTask?.id === id ? updated : state.activeTask,
      }));
    } catch (err) {
      set({ error: 'Failed to update task.' });
    }
  },

  deleteTask: async (id) => {
    try {
      await tasksApi.delete(id);
      set((state) => ({
        tasks: state.tasks.filter((t) => t.id !== id),
        activeTask: state.activeTask?.id === id ? null : state.activeTask,
      }));
    } catch (err) {
      set({ error: 'Failed to delete task.' });
    }
  },

  moveTask: async (taskId, columnId, position) => {
    // Optimistic update first
    get().optimisticMove(taskId, columnId, position);
    try {
      await tasksApi.move(taskId, columnId, position);
    } catch (err) {
      // Revert on failure by refetching
      get().fetchTasks();
      set({ error: 'Failed to move task.' });
    }
  },

  optimisticMove: (taskId, columnId, position) => {
    set((state) => ({
      tasks: state.tasks.map((t) =>
        t.id === taskId ? { ...t, column: columnId, position } : t
      ),
    }));
  },

  setFilters: (newFilters) => {
    set((state) => ({
      filters: { ...state.filters, ...newFilters },
    }));
  },

  clearFilters: () => set({ filters: {} }),

  clearError: () => set({ error: null }),
}));
