/**
 * ReportsPage: analytics dashboards with project metrics, sprint velocity,
 * burndown charts, and time tracking reports.
 */

import React, { useEffect, useState } from 'react';
import apiClient from '../api/client';
import { useProjectStore } from '../store/projectSlice';
import { formatDate, formatDuration, getDateRange } from '../utils/dateUtils';

interface ProjectDashboard {
  project: { id: string; name: string; key: string };
  tasks: {
    total: number;
    completed: number;
    in_progress: number;
    overdue: number;
    unassigned: number;
    completion_rate: number;
  };
  story_points: { total: number; completed: number };
  time_tracking: { estimated_hours: number; logged_hours: number };
  distribution: {
    by_type: Record<string, number>;
    by_priority: Record<string, number>;
    by_assignee: Array<{
      assignee__email: string;
      assignee__first_name: string;
      total: number;
      completed: number;
    }>;
  };
  recent_activity: { created_this_week: number; completed_this_week: number };
}

interface VelocityData {
  velocity_data: Array<{
    sprint_number: number;
    name: string;
    planned_points: number;
    completed_points: number;
    velocity: number;
    task_count: number;
  }>;
  average_velocity: number;
  trend: string;
}

type ReportTab = 'overview' | 'velocity' | 'time';

const ReportsPage: React.FC = () => {
  const { projects } = useProjectStore();
  const [selectedProjectId, setSelectedProjectId] = useState<string>('');
  const [activeTab, setActiveTab] = useState<ReportTab>('overview');
  const [dashboard, setDashboard] = useState<ProjectDashboard | null>(null);
  const [velocityData, setVelocityData] = useState<VelocityData | null>(null);
  const [timeReport, setTimeReport] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [dateRange, setDateRange] = useState<'week' | 'month' | 'quarter'>('month');

  useEffect(() => {
    if (selectedProjectId) {
      loadReport();
    }
  }, [selectedProjectId, activeTab, dateRange]);

  const loadReport = async () => {
    setIsLoading(true);
    try {
      if (activeTab === 'overview') {
        const { data } = await apiClient.get(
          `/analytics/projects/${selectedProjectId}/dashboard/`
        );
        setDashboard(data);
      } else if (activeTab === 'velocity') {
        const { data } = await apiClient.get(
          `/analytics/projects/${selectedProjectId}/velocity/`
        );
        setVelocityData(data);
      } else if (activeTab === 'time') {
        const range = getDateRange(dateRange);
        const { data } = await apiClient.get('/analytics/activity/', {
          params: { ...range },
        });
        setTimeReport(data);
      }
    } catch (err) {
      console.error('Failed to load report:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="reports-page">
      <header className="page-header">
        <h1>Reports & Analytics</h1>
      </header>

      {/* Project Selector */}
      <div className="report-controls">
        <select
          value={selectedProjectId}
          onChange={(e) => setSelectedProjectId(e.target.value)}
          className="project-selector"
        >
          <option value="">Select a project</option>
          {projects.map((p) => (
            <option key={p.id} value={p.id}>{p.name} ({p.key})</option>
          ))}
        </select>

        <div className="tabs">
          {(['overview', 'velocity', 'time'] as ReportTab[]).map((tab) => (
            <button
              key={tab}
              className={`tab ${activeTab === tab ? 'active' : ''}`}
              onClick={() => setActiveTab(tab)}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {!selectedProjectId ? (
        <div className="empty-state">
          <h3>Select a project to view reports</h3>
        </div>
      ) : isLoading ? (
        <div className="loading-spinner">Loading report...</div>
      ) : (
        <>
          {/* Overview Tab */}
          {activeTab === 'overview' && dashboard && (
            <div className="report-overview">
              <div className="stats-grid">
                <div className="stat-card">
                  <h3>Completion Rate</h3>
                  <p className="stat-value">{dashboard.tasks.completion_rate}%</p>
                  <p className="stat-detail">
                    {dashboard.tasks.completed}/{dashboard.tasks.total} tasks
                  </p>
                </div>
                <div className="stat-card">
                  <h3>In Progress</h3>
                  <p className="stat-value">{dashboard.tasks.in_progress}</p>
                </div>
                <div className="stat-card stat-danger">
                  <h3>Overdue</h3>
                  <p className="stat-value">{dashboard.tasks.overdue}</p>
                </div>
                <div className="stat-card">
                  <h3>Story Points</h3>
                  <p className="stat-value">
                    {dashboard.story_points.completed}/{dashboard.story_points.total}
                  </p>
                </div>
              </div>

              <div className="report-row">
                <div className="report-section">
                  <h3>Task Distribution by Priority</h3>
                  <div className="distribution-bars">
                    {Object.entries(dashboard.distribution.by_priority).map(
                      ([priority, count]) => (
                        <div key={priority} className="dist-bar-row">
                          <span className="dist-label">{priority}</span>
                          <div className="dist-bar">
                            <div
                              className="dist-bar-fill"
                              style={{
                                width: `${(count / dashboard.tasks.total) * 100}%`,
                              }}
                            />
                          </div>
                          <span className="dist-count">{count}</span>
                        </div>
                      )
                    )}
                  </div>
                </div>

                <div className="report-section">
                  <h3>Time Tracking</h3>
                  <div className="time-comparison">
                    <div>
                      <span className="time-label">Estimated</span>
                      <span className="time-value">
                        {formatDuration(dashboard.time_tracking.estimated_hours)}
                      </span>
                    </div>
                    <div>
                      <span className="time-label">Logged</span>
                      <span className="time-value">
                        {formatDuration(dashboard.time_tracking.logged_hours)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="report-section">
                <h3>Top Contributors</h3>
                <div className="contributor-list">
                  {dashboard.distribution.by_assignee.map((member, idx) => (
                    <div key={idx} className="contributor-row">
                      <span className="contributor-name">
                        {member.assignee__first_name} ({member.assignee__email})
                      </span>
                      <span>{member.completed}/{member.total} completed</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Velocity Tab */}
          {activeTab === 'velocity' && velocityData && (
            <div className="report-velocity">
              <div className="velocity-summary">
                <div className="stat-card">
                  <h3>Average Velocity</h3>
                  <p className="stat-value">{velocityData.average_velocity} pts</p>
                </div>
                <div className="stat-card">
                  <h3>Trend</h3>
                  <p className="stat-value">{velocityData.trend}</p>
                </div>
                <div className="stat-card">
                  <h3>Sprints Tracked</h3>
                  <p className="stat-value">{velocityData.velocity_data.length}</p>
                </div>
              </div>

              <div className="velocity-chart">
                <h3>Sprint Velocity</h3>
                <div className="chart-bars">
                  {velocityData.velocity_data.map((sprint) => (
                    <div key={sprint.sprint_number} className="chart-bar-group">
                      <div className="chart-bar-container">
                        <div
                          className="chart-bar planned"
                          style={{
                            height: `${(sprint.planned_points / Math.max(...velocityData.velocity_data.map((s) => s.planned_points), 1)) * 200}px`,
                          }}
                          title={`Planned: ${sprint.planned_points} pts`}
                        />
                        <div
                          className="chart-bar completed"
                          style={{
                            height: `${(sprint.completed_points / Math.max(...velocityData.velocity_data.map((s) => s.planned_points), 1)) * 200}px`,
                          }}
                          title={`Completed: ${sprint.completed_points} pts`}
                        />
                      </div>
                      <span className="chart-label">Sprint {sprint.sprint_number}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default ReportsPage;
