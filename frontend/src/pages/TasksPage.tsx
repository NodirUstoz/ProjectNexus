/**
 * TasksPage: comprehensive task management with list view, filters, bulk actions,
 * and task detail side panel.
 */

import React, { useCallback, useEffect, useState } from 'react';
import { useTaskStore } from '../store/taskSlice';
import { useProjectStore } from '../store/projectSlice';
import { useDebounce } from '../hooks/useDebounce';
import { formatDate, isOverdue, isDueSoon } from '../utils/dateUtils';
import { getPriorityConfig, getTaskTypeConfig } from '../utils/taskUtils';
import type { Task, TaskFilters } from '../api/tasks';

const TasksPage: React.FC = () => {
  const { tasks, activeTask, isLoading, filters, fetchTasks, setFilters, setActiveTask, deleteTask } = useTaskStore();
  const { projects } = useProjectStore();
  const [searchInput, setSearchInput] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedTasks, setSelectedTasks] = useState<Set<string>>(new Set());

  const debouncedSearch = useDebounce(searchInput, 300);

  useEffect(() => {
    setFilters({ search: debouncedSearch || undefined });
  }, [debouncedSearch, setFilters]);

  useEffect(() => {
    fetchTasks();
  }, [filters, fetchTasks]);

  const handleFilterChange = useCallback(
    (key: keyof TaskFilters, value: string | undefined) => {
      setFilters({ [key]: value || undefined });
    },
    [setFilters]
  );

  const toggleTaskSelection = (taskId: string) => {
    setSelectedTasks((prev) => {
      const next = new Set(prev);
      if (next.has(taskId)) {
        next.delete(taskId);
      } else {
        next.add(taskId);
      }
      return next;
    });
  };

  const handleSelectAll = () => {
    if (selectedTasks.size === tasks.length) {
      setSelectedTasks(new Set());
    } else {
      setSelectedTasks(new Set(tasks.map((t) => t.id)));
    }
  };

  const handleBulkDelete = async () => {
    if (!confirm(`Delete ${selectedTasks.size} tasks?`)) return;
    for (const id of selectedTasks) {
      await deleteTask(id);
    }
    setSelectedTasks(new Set());
  };

  return (
    <div className="tasks-page">
      <header className="page-header">
        <h1>Tasks</h1>
        <button className="btn btn-primary" onClick={() => setShowCreateForm(true)}>
          Create Task
        </button>
      </header>

      {/* Filters */}
      <div className="filters-bar">
        <input
          type="text"
          placeholder="Search tasks..."
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          className="search-input"
        />
        <select onChange={(e) => handleFilterChange('project', e.target.value)} value={filters.project || ''}>
          <option value="">All Projects</option>
          {projects.map((p) => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>
        <select onChange={(e) => handleFilterChange('priority', e.target.value)} value={filters.priority || ''}>
          <option value="">All Priorities</option>
          <option value="highest">Highest</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
          <option value="lowest">Lowest</option>
        </select>
        <select onChange={(e) => handleFilterChange('type', e.target.value)} value={filters.type || ''}>
          <option value="">All Types</option>
          <option value="epic">Epic</option>
          <option value="story">Story</option>
          <option value="task">Task</option>
          <option value="bug">Bug</option>
        </select>
      </div>

      {/* Bulk Actions */}
      {selectedTasks.size > 0 && (
        <div className="bulk-actions-bar">
          <span>{selectedTasks.size} selected</span>
          <button className="btn btn-sm btn-danger" onClick={handleBulkDelete}>Delete Selected</button>
          <button className="btn btn-sm btn-outline" onClick={() => setSelectedTasks(new Set())}>
            Clear Selection
          </button>
        </div>
      )}

      {/* Task Table */}
      <div className="task-table">
        <div className="task-table-header">
          <input
            type="checkbox"
            checked={selectedTasks.size === tasks.length && tasks.length > 0}
            onChange={handleSelectAll}
          />
          <span className="col-key">Key</span>
          <span className="col-title">Title</span>
          <span className="col-type">Type</span>
          <span className="col-priority">Priority</span>
          <span className="col-assignee">Assignee</span>
          <span className="col-due">Due Date</span>
          <span className="col-points">Points</span>
        </div>

        {isLoading ? (
          <div className="loading-spinner">Loading tasks...</div>
        ) : (
          tasks.map((task) => {
            const priorityConfig = getPriorityConfig(task.priority);
            const typeConfig = getTaskTypeConfig(task.task_type);
            const overdue = isOverdue(task.due_date);
            const dueSoon = isDueSoon(task.due_date);

            return (
              <div
                key={task.id}
                className={`task-row ${activeTask?.id === task.id ? 'active' : ''} ${overdue ? 'overdue' : ''}`}
                onClick={() => setActiveTask(task)}
              >
                <input
                  type="checkbox"
                  checked={selectedTasks.has(task.id)}
                  onChange={() => toggleTaskSelection(task.id)}
                  onClick={(e) => e.stopPropagation()}
                />
                <span className="col-key">{task.task_key}</span>
                <span className="col-title">
                  {task.title}
                  {task.subtask_count > 0 && (
                    <span className="subtask-badge">
                      {task.subtask_completed}/{task.subtask_count}
                    </span>
                  )}
                </span>
                <span className="col-type">
                  <span className="type-badge" style={{ color: typeConfig.color, backgroundColor: typeConfig.bgColor }}>
                    {typeConfig.label}
                  </span>
                </span>
                <span className="col-priority">
                  <span className="priority-badge" style={{ color: priorityConfig.color, backgroundColor: priorityConfig.bgColor }}>
                    {priorityConfig.label}
                  </span>
                </span>
                <span className="col-assignee">
                  {task.assignee ? task.assignee.full_name : <span className="unassigned">Unassigned</span>}
                </span>
                <span className={`col-due ${overdue ? 'text-danger' : dueSoon ? 'text-warning' : ''}`}>
                  {formatDate(task.due_date)}
                </span>
                <span className="col-points">{task.story_points || '-'}</span>
              </div>
            );
          })
        )}
      </div>

      {tasks.length === 0 && !isLoading && (
        <div className="empty-state">
          <h3>No tasks found</h3>
          <p>Try adjusting your filters or create a new task.</p>
        </div>
      )}
    </div>
  );
};

export default TasksPage;
