/**
 * MilestonesPage: milestone tracker with timeline view, progress indicators,
 * and milestone detail panel.
 */

import React, { useEffect, useState } from 'react';
import { milestonesApi } from '../api/milestones';
import type { Milestone } from '../api/milestones';
import { formatDate, isOverdue, daysBetween } from '../utils/dateUtils';
import { calculateProgress } from '../utils/taskUtils';

const STATUS_COLORS: Record<string, string> = {
  not_started: '#94A3B8',
  in_progress: '#3B82F6',
  completed: '#10B981',
  overdue: '#EF4444',
  cancelled: '#6B7280',
};

const MilestonesPage: React.FC = () => {
  const [milestones, setMilestones] = useState<Milestone[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedMilestone, setSelectedMilestone] = useState<Milestone | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newMilestone, setNewMilestone] = useState({
    title: '',
    description: '',
    due_date: '',
    priority: 'medium',
    color: '#6366F1',
  });

  useEffect(() => {
    loadMilestones();
  }, [filterStatus]);

  const loadMilestones = async () => {
    setIsLoading(true);
    try {
      const params: Record<string, string> = {};
      if (filterStatus) params.status = filterStatus;
      const { data } = await milestonesApi.list(params);
      setMilestones(data.results);
    } catch (err) {
      console.error('Failed to load milestones:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleComplete = async (id: string) => {
    await milestonesApi.complete(id);
    loadMilestones();
  };

  const handleReopen = async (id: string) => {
    await milestonesApi.reopen(id);
    loadMilestones();
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    await milestonesApi.create({
      ...newMilestone,
      project_id: '', // Set from context
    });
    setShowCreateModal(false);
    setNewMilestone({ title: '', description: '', due_date: '', priority: 'medium', color: '#6366F1' });
    loadMilestones();
  };

  return (
    <div className="milestones-page">
      <header className="page-header">
        <h1>Milestones</h1>
        <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
          New Milestone
        </button>
      </header>

      {/* Filters */}
      <div className="filters-bar">
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
        >
          <option value="">All Statuses</option>
          <option value="not_started">Not Started</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
          <option value="overdue">Overdue</option>
        </select>
      </div>

      {/* Milestones Timeline */}
      {isLoading ? (
        <div className="loading-spinner">Loading milestones...</div>
      ) : (
        <div className="milestones-timeline">
          {milestones.map((milestone) => {
            const progress = calculateProgress(milestone.completed_tasks, milestone.total_tasks);
            const statusColor = STATUS_COLORS[milestone.status] || '#94A3B8';

            return (
              <div
                key={milestone.id}
                className={`milestone-card ${selectedMilestone?.id === milestone.id ? 'selected' : ''}`}
                style={{ borderLeftColor: milestone.color }}
                onClick={() => setSelectedMilestone(milestone)}
              >
                <div className="milestone-header">
                  <div className="milestone-title-group">
                    <h3>{milestone.title}</h3>
                    <span
                      className="status-badge"
                      style={{ backgroundColor: statusColor }}
                    >
                      {milestone.status.replace('_', ' ')}
                    </span>
                  </div>
                  <span className="milestone-priority">{milestone.priority}</span>
                </div>

                {milestone.description && (
                  <p className="milestone-description">{milestone.description}</p>
                )}

                <div className="milestone-progress">
                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{ width: `${progress}%`, backgroundColor: milestone.color }}
                    />
                  </div>
                  <span className="progress-text">
                    {milestone.completed_tasks}/{milestone.total_tasks} tasks ({progress}%)
                  </span>
                </div>

                <div className="milestone-footer">
                  <span>Due: {formatDate(milestone.due_date)}</span>
                  {milestone.owner && <span>Owner: {milestone.owner.full_name}</span>}
                  {milestone.start_date && (
                    <span>Duration: {daysBetween(milestone.start_date, milestone.due_date)} days</span>
                  )}
                </div>

                <div className="milestone-actions">
                  {milestone.status !== 'completed' ? (
                    <button className="btn btn-sm btn-success" onClick={(e) => { e.stopPropagation(); handleComplete(milestone.id); }}>
                      Complete
                    </button>
                  ) : (
                    <button className="btn btn-sm btn-outline" onClick={(e) => { e.stopPropagation(); handleReopen(milestone.id); }}>
                      Reopen
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {milestones.length === 0 && !isLoading && (
        <div className="empty-state">
          <h3>No milestones yet</h3>
          <p>Create milestones to track key deliverables and checkpoints.</p>
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Create Milestone</h2>
            <form onSubmit={handleCreate}>
              <div className="form-group">
                <label>Title</label>
                <input
                  type="text"
                  value={newMilestone.title}
                  onChange={(e) => setNewMilestone({ ...newMilestone, title: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={newMilestone.description}
                  onChange={(e) => setNewMilestone({ ...newMilestone, description: e.target.value })}
                  rows={3}
                />
              </div>
              <div className="form-group">
                <label>Due Date</label>
                <input
                  type="date"
                  value={newMilestone.due_date}
                  onChange={(e) => setNewMilestone({ ...newMilestone, due_date: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Priority</label>
                <select
                  value={newMilestone.priority}
                  onChange={(e) => setNewMilestone({ ...newMilestone, priority: e.target.value })}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-outline" onClick={() => setShowCreateModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">Create</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default MilestonesPage;
