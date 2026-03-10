/**
 * NotificationBell: header component showing unread notification count
 * with a dropdown panel for recent notifications.
 */

import React, { useEffect, useRef, useState } from 'react';
import { useNotificationStore } from '../../store/notificationSlice';
import { timeAgo } from '../../utils/dateUtils';

const NOTIFICATION_TYPE_LABELS: Record<string, string> = {
  task_assigned: 'Task Assigned',
  task_updated: 'Task Updated',
  task_completed: 'Task Completed',
  task_commented: 'New Comment',
  mentioned: 'Mentioned',
  milestone_due: 'Milestone Due',
  milestone_completed: 'Milestone Completed',
  sprint_started: 'Sprint Started',
  sprint_completed: 'Sprint Completed',
  document_updated: 'Document Updated',
  team_joined: 'Team Joined',
  project_invited: 'Project Invitation',
  workspace_invited: 'Workspace Invitation',
};

const NotificationBell: React.FC = () => {
  const {
    notifications,
    unreadCount,
    fetchNotifications,
    fetchUnreadCount,
    markRead,
    markAllRead,
    connectWebSocket,
    disconnectWebSocket,
  } = useNotificationStore();

  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchUnreadCount();
    connectWebSocket();

    return () => {
      disconnectWebSocket();
    };
  }, []);

  useEffect(() => {
    if (isOpen) {
      fetchNotifications();
    }
  }, [isOpen]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const handleNotificationClick = async (notificationId: string, actionUrl?: string) => {
    await markRead(notificationId);
    if (actionUrl) {
      window.location.href = actionUrl;
    }
  };

  return (
    <div className="notification-bell" ref={dropdownRef}>
      <button
        className="bell-button"
        onClick={() => setIsOpen(!isOpen)}
        aria-label={`Notifications (${unreadCount} unread)`}
      >
        <svg
          width="20"
          height="20"
          viewBox="0 0 20 20"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M10 2C7.79 2 6 3.79 6 6V9.59C6 10.19 5.78 10.78 5.38 11.22L4.29 12.42C3.59 13.19 4.13 14.5 5.17 14.5H14.83C15.87 14.5 16.41 13.19 15.71 12.42L14.62 11.22C14.22 10.78 14 10.19 14 9.59V6C14 3.79 12.21 2 10 2Z"
            stroke="currentColor"
            strokeWidth="1.5"
          />
          <path d="M8 15C8 16.1 8.9 17 10 17C11.1 17 12 16.1 12 15" stroke="currentColor" strokeWidth="1.5" />
        </svg>
        {unreadCount > 0 && (
          <span className="bell-badge">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="notification-dropdown">
          <div className="dropdown-header">
            <h3>Notifications</h3>
            {unreadCount > 0 && (
              <button className="mark-all-btn" onClick={markAllRead}>
                Mark all read
              </button>
            )}
          </div>

          <div className="notification-list">
            {notifications.length === 0 ? (
              <div className="empty-notifications">
                <p>No notifications yet.</p>
              </div>
            ) : (
              notifications.slice(0, 20).map((notification) => (
                <div
                  key={notification.id}
                  className={`notification-item ${notification.is_read ? '' : 'unread'}`}
                  onClick={() => handleNotificationClick(notification.id, notification.action_url)}
                >
                  <div className="notification-content">
                    <span className="notification-type">
                      {NOTIFICATION_TYPE_LABELS[notification.notification_type] || notification.notification_type}
                    </span>
                    <p className="notification-title">{notification.title}</p>
                    {notification.message && (
                      <p className="notification-message">{notification.message}</p>
                    )}
                    <span className="notification-time">{timeAgo(notification.created_at)}</span>
                  </div>
                  {!notification.is_read && <span className="unread-dot" />}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationBell;
