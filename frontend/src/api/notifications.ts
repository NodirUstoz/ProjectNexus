/**
 * Notifications API module: fetch, mark read, preferences.
 */

import apiClient from './client';
import type { User } from './projects';

export interface Notification {
  id: string;
  sender: User | null;
  notification_type: string;
  title: string;
  message: string;
  target_type: string | null;
  object_id: string | null;
  action_url: string;
  is_read: boolean;
  read_at: string | null;
  created_at: string;
}

export interface NotificationPreferences {
  task_assigned: 'in_app' | 'email' | 'both' | 'none';
  task_updated: 'in_app' | 'email' | 'both' | 'none';
  task_commented: 'in_app' | 'email' | 'both' | 'none';
  mentioned: 'in_app' | 'email' | 'both' | 'none';
  milestone_due: 'in_app' | 'email' | 'both' | 'none';
  sprint_updates: 'in_app' | 'email' | 'both' | 'none';
  document_updated: 'in_app' | 'email' | 'both' | 'none';
  team_updates: 'in_app' | 'email' | 'both' | 'none';
  daily_digest: boolean;
  weekly_summary: boolean;
}

export const notificationsApi = {
  list(params?: { is_read?: string; type?: string }) {
    return apiClient.get<{ results: Notification[] }>('/notifications/', { params });
  },

  markRead(id: string) {
    return apiClient.post(`/notifications/${id}/read/`);
  },

  markAllRead(notificationIds?: string[]) {
    return apiClient.post('/notifications/mark_all_read/', {
      notification_ids: notificationIds,
    });
  },

  getUnreadCount() {
    return apiClient.get<{ unread_count: number }>('/notifications/unread_count/');
  },

  clearRead() {
    return apiClient.delete('/notifications/clear_read/');
  },

  getPreferences() {
    return apiClient.get<NotificationPreferences>('/notification-preferences/');
  },

  updatePreferences(data: Partial<NotificationPreferences>) {
    return apiClient.post<NotificationPreferences>('/notification-preferences/', data);
  },
};
