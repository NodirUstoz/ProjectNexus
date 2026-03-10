/**
 * Auth store slice: manages authentication state, login, logout, token refresh.
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import apiClient from '../api/client';

interface User {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  full_name: string;
  avatar: string | null;
  job_title: string;
  bio: string;
  timezone: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  login: (email: string, password: string) => Promise<void>;
  register: (data: {
    email: string;
    username: string;
    first_name: string;
    last_name: string;
    password: string;
    password_confirm: string;
  }) => Promise<void>;
  logout: () => void;
  updateProfile: (data: Partial<User>) => Promise<void>;
  fetchProfile: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (email, password) => {
        set({ isLoading: true, error: null });
        try {
          const { data } = await apiClient.post('/auth/login/', { email, password });
          localStorage.setItem('access_token', data.access);
          localStorage.setItem('refresh_token', data.refresh);
          set({
            user: data.user,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (err: any) {
          const message =
            err.response?.data?.detail ||
            err.response?.data?.message ||
            'Login failed. Please check your credentials.';
          set({ error: message, isLoading: false });
          throw err;
        }
      },

      register: async (formData) => {
        set({ isLoading: true, error: null });
        try {
          await apiClient.post('/auth/register/', formData);
          set({ isLoading: false });
        } catch (err: any) {
          const message =
            err.response?.data?.message ||
            'Registration failed. Please try again.';
          set({ error: message, isLoading: false });
          throw err;
        }
      },

      logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        set({ user: null, isAuthenticated: false, error: null });
      },

      updateProfile: async (data) => {
        set({ isLoading: true, error: null });
        try {
          const { data: updated } = await apiClient.patch('/auth/me/', data);
          set({ user: updated, isLoading: false });
        } catch (err: any) {
          set({ error: 'Failed to update profile.', isLoading: false });
          throw err;
        }
      },

      fetchProfile: async () => {
        try {
          const { data } = await apiClient.get('/auth/me/');
          set({ user: data, isAuthenticated: true });
        } catch {
          set({ user: null, isAuthenticated: false });
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
