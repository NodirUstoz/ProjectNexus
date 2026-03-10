/**
 * TaskDetailPanel: slide-out panel for viewing and editing a task's details,
 * comments, subtasks, attachments, and history.
 */

import React, { useEffect, useState } from 'react';
import { useTaskStore } from '../../store/taskSlice';
import { tasksApi } from '../../api/tasks';
import type { TaskComment, Task } from '../../api/tasks';
import { formatDate, timeAgo, formatDuration } from '../../utils/dateUtils';
import { getPriorityConfig, getTaskTypeConfig } from '../../utils/taskUtils';

interface TaskDetailPanelProps {
  taskId: string;
  onClose: () => void;
}

interface Subtask {
  id: string;
  title: string;
  is_completed: boolean;
  position: number;
}

const TaskDetailPanel: React.FC<TaskDetailPanelProps> = ({ taskId, onClose }) => {
  const { activeTask, fetchTask, updateTask } = useTaskStore();
  const [comments, setComments] = useState<TaskComment[]>([]);
  const [subtasks, setSubtasks] = useState<Subtask[]>([]);
  const [newComment, setNewComment] = useState('');
  const [newSubtask, setNewSubtask] = useState('');
  const [activeTab, setActiveTab] = useState<'details' | 'comments' | 'subtasks' | 'history'>('details');
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState<Partial<Task>>({});

  useEffect(() => {
    fetchTask(taskId);
    loadComments();
    loadSubtasks();
  }, [taskId]);

  useEffect(() => {
    if (activeTask) {
      setEditForm({
        title: activeTask.title,
        description: activeTask.description,
        priority: activeTask.priority,
        task_type: activeTask.task_type,
        story_points: activeTask.story_points,
        due_date: activeTask.due_date,
        start_date: activeTask.start_date,
      });
    }
  }, [activeTask]);

  const loadComments = async () => {
    try {
      const { data } = await tasksApi.getComments(taskId);
      setComments(data);
    } catch (err) {
      console.error('Failed to load comments:', err);
    }
  };

  const loadSubtasks = async () => {
    try {
      const { data } = await tasksApi.getSubtasks(taskId);
      setSubtasks(data);
    } catch (err) {
      console.error('Failed to load subtasks:', err);
    }
  };

  const handleAddComment = async () => {
    if (!newComment.trim()) return;
    try {
      await tasksApi.addComment(taskId, newComment);
      setNewComment('');
      loadComments();
    } catch (err) {
      console.error('Failed to add comment:', err);
    }
  };

  const handleAddSubtask = async () => {
    if (!newSubtask.trim()) return;
    try {
      await tasksApi.addSubtask(taskId, newSubtask);
      setNewSubtask('');
      loadSubtasks();
    } catch (err) {
      console.error('Failed to add subtask:', err);
    }
  };

  const handleToggleSubtask = async (subtaskId: string) => {
    try {
      await tasksApi.toggleSubtask(subtaskId);
      loadSubtasks();
    } catch (err) {
      console.error('Failed to toggle subtask:', err);
    }
  };

  const handleSave = async () => {
    await updateTask(taskId, editForm);
    setIsEditing(false);
  };

  if (!activeTask) {
    return <div className="task-detail-panel loading">Loading...</div>;
  }

  const priorityConfig = getPriorityConfig(activeTask.priority);
  const typeConfig = getTaskTypeConfig(activeTask.task_type);
  const completedSubtasks = subtasks.filter((s) => s.is_completed).length;

  return (
    <div className="task-detail-panel">
      <div className="panel-header">
        <div className="panel-title-row">
          <span className="task-key">{activeTask.task_key}</span>
          <div className="panel-actions">
            <button className="btn btn-sm" onClick={() => setIsEditing(!isEditing)}>
              {isEditing ? 'Cancel' : 'Edit'}
            </button>
            <button className="btn btn-sm btn-outline" onClick={onClose}>Close</button>
          </div>
        </div>
        {isEditing ? (
          <input
            type="text"
            className="title-input"
            value={editForm.title || ''}
            onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
          />
        ) : (
          <h2>{activeTask.title}</h2>
        )}
      </div>

      {/* Metadata */}
      <div className="panel-metadata">
        <div className="meta-row">
          <span className="meta-label">Type</span>
          <span className="type-badge" style={{ color: typeConfig.color, backgroundColor: typeConfig.bgColor }}>
            {typeConfig.label}
          </span>
        </div>
        <div className="meta-row">
          <span className="meta-label">Priority</span>
          <span className="priority-badge" style={{ color: priorityConfig.color, backgroundColor: priorityConfig.bgColor }}>
            {priorityConfig.label}
          </span>
        </div>
        <div className="meta-row">
          <span className="meta-label">Assignee</span>
          <span>{activeTask.assignee?.full_name || 'Unassigned'}</span>
        </div>
        <div className="meta-row">
          <span className="meta-label">Reporter</span>
          <span>{activeTask.reporter?.full_name || 'Unknown'}</span>
        </div>
        <div className="meta-row">
          <span className="meta-label">Story Points</span>
          <span>{activeTask.story_points || '-'}</span>
        </div>
        <div className="meta-row">
          <span className="meta-label">Due Date</span>
          <span>{formatDate(activeTask.due_date)}</span>
        </div>
        <div className="meta-row">
          <span className="meta-label">Time Tracked</span>
          <span>
            {formatDuration(activeTask.time_spent_hours)}
            {activeTask.original_estimate_hours && (
              <span className="estimate"> / {formatDuration(activeTask.original_estimate_hours)}</span>
            )}
          </span>
        </div>
        <div className="meta-row">
          <span className="meta-label">Created</span>
          <span>{timeAgo(activeTask.created_at)}</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="panel-tabs">
        {(['details', 'comments', 'subtasks', 'history'] as const).map((tab) => (
          <button
            key={tab}
            className={`tab ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
            {tab === 'comments' && comments.length > 0 && (
              <span className="tab-count">{comments.length}</span>
            )}
            {tab === 'subtasks' && subtasks.length > 0 && (
              <span className="tab-count">{completedSubtasks}/{subtasks.length}</span>
            )}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="panel-content">
        {activeTab === 'details' && (
          <div className="task-description">
            <h4>Description</h4>
            {isEditing ? (
              <>
                <textarea
                  value={editForm.description || ''}
                  onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                  rows={8}
                  placeholder="Add a description..."
                />
                <button className="btn btn-primary btn-sm" onClick={handleSave}>Save</button>
              </>
            ) : (
              <p>{activeTask.description || 'No description provided.'}</p>
            )}
            <div className="task-labels">
              <h4>Labels</h4>
              <div className="label-list">
                {activeTask.labels.map((label) => (
                  <span key={label.id} className="label-chip" style={{ backgroundColor: label.color }}>
                    {label.name}
                  </span>
                ))}
                {activeTask.labels.length === 0 && <span className="text-muted">No labels</span>}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'comments' && (
          <div className="task-comments">
            <div className="comment-input">
              <textarea
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                placeholder="Write a comment..."
                rows={3}
              />
              <button className="btn btn-primary btn-sm" onClick={handleAddComment}>
                Comment
              </button>
            </div>
            <div className="comment-list">
              {comments.map((comment) => (
                <div key={comment.id} className="comment-item">
                  <div className="comment-header">
                    <span className="comment-author">{comment.author.full_name}</span>
                    <span className="comment-time">{timeAgo(comment.created_at)}</span>
                    {comment.edited && <span className="edited-badge">edited</span>}
                  </div>
                  <p className="comment-body">{comment.content}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'subtasks' && (
          <div className="task-subtasks">
            <div className="subtask-input">
              <input
                type="text"
                value={newSubtask}
                onChange={(e) => setNewSubtask(e.target.value)}
                placeholder="Add a subtask..."
                onKeyDown={(e) => e.key === 'Enter' && handleAddSubtask()}
              />
              <button className="btn btn-sm" onClick={handleAddSubtask}>Add</button>
            </div>
            {subtasks.length > 0 && (
              <div className="subtask-progress">
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{ width: `${(completedSubtasks / subtasks.length) * 100}%` }}
                  />
                </div>
                <span>{completedSubtasks}/{subtasks.length} completed</span>
              </div>
            )}
            <div className="subtask-list">
              {subtasks.map((subtask) => (
                <div key={subtask.id} className="subtask-item">
                  <input
                    type="checkbox"
                    checked={subtask.is_completed}
                    onChange={() => handleToggleSubtask(subtask.id)}
                  />
                  <span className={subtask.is_completed ? 'completed' : ''}>
                    {subtask.title}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TaskDetailPanel;
