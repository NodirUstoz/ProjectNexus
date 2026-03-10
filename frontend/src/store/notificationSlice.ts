/**
 * Notification store slice: manages notifications, unread count, WebSocket connection.
 */

import { create } from 'zustand';
import { notificationsApi } from '../api/notifications';
import type { Notification } from '../api/notifications';

interface NotificationState {
  notifications: Notification[];
  unreadCount: number;
  isLoading: boolean;
  wsConnection: WebSocket | null;

  fetchNotifications: (params?: { is_read?: string }) => Promise<void>;
  fetchUnreadCount: () => Promise<void>;
  markRead: (id: string) => Promise<void>;
  markAllRead: () => Promise<void>;
  connectWebSocket: () => void;
  disconnectWebSocket: () => void;
  addNotification: (notification: Notification) => void;
}

const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

export const useNotificationStore = create<NotificationState>()((set, get) => ({
  notifications: [],
  unreadCount: 0,
  isLoading: false,
  wsConnection: null,

  fetchNotifications: async (params) => {
    set({ isLoading: true });
    try {
      const { data } = await notificationsApi.list(params);
      set({ notifications: data.results, isLoading: false });
    } catch {
      set({ isLoading: false });
    }
  },

  fetchUnreadCount: async () => {
    try {
      const { data } = await notificationsApi.getUnreadCount();
      set({ unreadCount: data.unread_count });
    } catch {
      // Silently fail - notification count is non-critical
    }
  },

  markRead: async (id) => {
    try {
      await notificationsApi.markRead(id);
      set((state) => ({
        notifications: state.notifications.map((n) =>
          n.id === id ? { ...n, is_read: true } : n
        ),
        unreadCount: Math.max(0, state.unreadCount - 1),
      }));
    } catch {
      // Silently fail
    }
  },

  markAllRead: async () => {
    try {
      await notificationsApi.markAllRead();
      set((state) => ({
        notifications: state.notifications.map((n) => ({ ...n, is_read: true })),
        unreadCount: 0,
      }));
    } catch {
      // Silently fail
    }
  },

  connectWebSocket: () => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    const ws = new WebSocket(`${WS_BASE_URL}/ws/notifications/?token=${token}`);

    ws.onopen = () => {
      console.log('Notification WebSocket connected');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'notification') {
        get().addNotification(data.data);
      } else if (data.type === 'unread_count') {
        set({ unreadCount: data.count });
      }
    };

    ws.onclose = () => {
      console.log('Notification WebSocket disconnected');
      // Attempt reconnection after 5 seconds
      setTimeout(() => {
        const state = get();
        if (!state.wsConnection || state.wsConnection.readyState === WebSocket.CLOSED) {
          state.connectWebSocket();
        }
      }, 5000);
    };

    set({ wsConnection: ws });
  },

  disconnectWebSocket: () => {
    const { wsConnection } = get();
    if (wsConnection) {
      wsConnection.close();
      set({ wsConnection: null });
    }
  },

  addNotification: (notification) => {
    set((state) => ({
      notifications: [notification, ...state.notifications],
      unreadCount: state.unreadCount + 1,
    }));
  },
}));
