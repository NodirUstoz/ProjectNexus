/**
 * MilestoneTracker: visual timeline component showing milestone progress,
 * due dates, and task completion status within each milestone.
 */

import React from 'react';
import { formatDate, isOverdue, daysBetween } from '../../utils/dateUtils';
import { calculateProgress } from '../../utils/taskUtils';
import type { Milestone } from '../../api/milestones';

interface MilestoneTrackerProps {
  milestones: Milestone[];
  onMilestoneClick: (milestone: Milestone) => void;
  onComplete: (id: string) => void;
}

const STATUS_ICONS: Record<string, string> = {
  not_started: 'O',
  in_progress: '...',
  completed: 'V',
  overdue: '!',
  cancelled: 'X',
};

const STATUS_COLORS: Record<string, string> = {
  not_started: '#94A3B8',
  in_progress: '#3B82F6',
  completed: '#10B981',
  overdue: '#EF4444',
  cancelled: '#6B7280',
};

const MilestoneTracker: React.FC<MilestoneTrackerProps> = ({
  milestones,
  onMilestoneClick,
  onComplete,
}) => {
  const sortedMilestones = [...milestones].sort(
    (a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime()
  );

  const today = new Date().toISOString().split('T')[0];

  return (
    <div className="milestone-tracker">
      {/* Timeline line */}
      <div className="timeline-line" />

      {sortedMilestones.map((milestone, index) => {
        const progress = calculateProgress(milestone.completed_tasks, milestone.total_tasks);
        const overdue = isOverdue(milestone.due_date) && milestone.status !== 'completed';
        const statusColor = STATUS_COLORS[overdue ? 'overdue' : milestone.status];
        const daysUntilDue = daysBetween(today, milestone.due_date);

        return (
          <div
            key={milestone.id}
            className={`timeline-item ${overdue ? 'overdue' : ''} ${milestone.status === 'completed' ? 'completed' : ''}`}
            onClick={() => onMilestoneClick(milestone)}
          >
            {/* Timeline node */}
            <div className="timeline-node" style={{ backgroundColor: statusColor }}>
              <span className="node-icon">{STATUS_ICONS[overdue ? 'overdue' : milestone.status]}</span>
            </div>

            {/* Milestone card */}
            <div className="timeline-card" style={{ borderLeftColor: milestone.color }}>
              <div className="timeline-card-header">
                <h4>{milestone.title}</h4>
                <span className={`priority-tag priority-${milestone.priority}`}>
                  {milestone.priority}
                </span>
              </div>

              {milestone.description && (
                <p className="timeline-card-description">{milestone.description}</p>
              )}

              {/* Progress bar */}
              <div className="milestone-progress-bar">
                <div className="progress-track">
                  <div
                    className="progress-fill"
                    style={{
                      width: `${progress}%`,
                      backgroundColor: milestone.color,
                    }}
                  />
                </div>
                <span className="progress-label">{progress}%</span>
              </div>

              <div className="timeline-card-footer">
                <div className="footer-info">
                  <span className="due-info">
                    {milestone.status === 'completed'
                      ? `Completed ${formatDate(milestone.completed_at)}`
                      : overdue
                      ? `Overdue by ${Math.abs(daysUntilDue)} days`
                      : `Due ${formatDate(milestone.due_date)} (${daysUntilDue} days)`}
                  </span>
                  <span className="task-info">
                    {milestone.completed_tasks}/{milestone.total_tasks} tasks
                  </span>
                  {milestone.owner && (
                    <span className="owner-info">{milestone.owner.full_name}</span>
                  )}
                </div>

                {milestone.status !== 'completed' && milestone.status !== 'cancelled' && (
                  <button
                    className="btn btn-sm btn-success"
                    onClick={(e) => {
                      e.stopPropagation();
                      onComplete(milestone.id);
                    }}
                  >
                    Mark Complete
                  </button>
                )}
              </div>
            </div>
          </div>
        );
      })}

      {sortedMilestones.length === 0 && (
        <div className="empty-timeline">
          <p>No milestones to display. Create one to track your project goals.</p>
        </div>
      )}
    </div>
  );
};

export default MilestoneTracker;
