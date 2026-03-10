/**
 * DashboardPage: main workspace dashboard with project overview, recent activity,
 * task summary statistics, and quick-action widgets.
 */

import React, { useEffect, useState } from 'react';
import { useProjectStore } from '../store/projectSlice';
import { useTaskStore } from '../store/taskSlice';
import { useNotificationStore } from '../store/notificationSlice';
import { formatDate, timeAgo } from '../utils/dateUtils';
import { getPriorityConfig, calculateProgress } from '../utils/taskUtils';

interface DashboardStats {
  totalProjects: number;
  activeTasks: number;
  completedToday: number;
  overdueTasks: number;
}

const DashboardPage: React.FC = () => {
  const { projects, fetchProjects } = useProjectStore();
  const { tasks, fetchTasks } = useTaskStore();
  const { unreadCount, fetchUnreadCount } = useNotificationStore();
  const [stats, setStats] = useState<DashboardStats>({
    totalProjects: 0,
    activeTasks: 0,
    completedToday: 0,
    overdueTasks: 0,
  });

  useEffect(() => {
    fetchProjects();
    fetchTasks({ assignee: 'me' });
    fetchUnreadCount();
  }, [fetchProjects, fetchTasks, fetchUnreadCount]);

  useEffect(() => {
    const today = new Date().toISOString().split('T')[0];
    setStats({
      totalProjects: projects.length,
      activeTasks: tasks.filter((t) => !t.completed_at).length,
      completedToday: tasks.filter(
        (t) => t.completed_at && t.completed_at.startsWith(today)
      ).length,
      overdueTasks: tasks.filter(
        (t) => t.due_date && !t.completed_at && t.due_date < today
      ).length,
    });
  }, [projects, tasks]);

  const myUpcomingTasks = tasks
    .filter((t) => !t.completed_at && t.due_date)
    .sort((a, b) => (a.due_date! > b.due_date! ? 1 : -1))
    .slice(0, 8);

  return (
    <div className="dashboard-page">
      <header className="dashboard-header">
        <h1>Dashboard</h1>
        {unreadCount > 0 && (
          <span className="notification-badge">{unreadCount} unread notifications</span>
        )}
      </header>

      {/* Stats Cards */}
      <section className="stats-grid">
        <div className="stat-card">
          <h3>Projects</h3>
          <p className="stat-value">{stats.totalProjects}</p>
          <p className="stat-label">Active projects</p>
        </div>
        <div className="stat-card">
          <h3>My Tasks</h3>
          <p className="stat-value">{stats.activeTasks}</p>
          <p className="stat-label">In progress</p>
        </div>
        <div className="stat-card stat-success">
          <h3>Completed Today</h3>
          <p className="stat-value">{stats.completedToday}</p>
          <p className="stat-label">Tasks done</p>
        </div>
        <div className="stat-card stat-danger">
          <h3>Overdue</h3>
          <p className="stat-value">{stats.overdueTasks}</p>
          <p className="stat-label">Need attention</p>
        </div>
      </section>

      {/* Project Grid */}
      <section className="dashboard-section">
        <h2>Recent Projects</h2>
        <div className="project-grid">
          {projects.slice(0, 6).map((project) => (
            <div key={project.id} className="project-card" style={{ borderLeftColor: project.color }}>
              <div className="project-card-header">
                <span className="project-icon">{project.icon}</span>
                <div>
                  <h4>{project.name}</h4>
                  <span className="project-key">{project.key}</span>
                </div>
              </div>
              <p className="project-description">{project.description}</p>
              <div className="project-card-footer">
                <span>{project.task_count} tasks</span>
                <span>{project.member_count} members</span>
                <span>{project.project_type}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Upcoming Tasks */}
      <section className="dashboard-section">
        <h2>Upcoming Tasks</h2>
        <div className="task-list">
          {myUpcomingTasks.map((task) => {
            const priorityConfig = getPriorityConfig(task.priority);
            return (
              <div key={task.id} className="task-list-item">
                <span
                  className="priority-indicator"
                  style={{ backgroundColor: priorityConfig.color }}
                />
                <div className="task-info">
                  <span className="task-key">{task.task_key}</span>
                  <span className="task-title">{task.title}</span>
                </div>
                <div className="task-meta">
                  <span className="due-date">{formatDate(task.due_date)}</span>
                  {task.story_points && (
                    <span className="story-points">{task.story_points} pts</span>
                  )}
                </div>
              </div>
            );
          })}
          {myUpcomingTasks.length === 0 && (
            <p className="empty-state">No upcoming tasks. You are all caught up.</p>
          )}
        </div>
      </section>
    </div>
  );
};

export default DashboardPage;
