/**
 * ProjectBoard: Kanban board component with drag-and-drop columns,
 * task cards, real-time updates, and collaborative cursors.
 */

import React, { useCallback, useEffect, useMemo } from 'react';
import { useProjectStore } from '../../store/projectSlice';
import { useTaskStore } from '../../store/taskSlice';
import { useDragAndDrop } from '../../hooks/useDragAndDrop';
import { useWebSocket } from '../../hooks/useWebSocket';
import { groupTasksByColumn } from '../../utils/taskUtils';
import type { Task } from '../../api/tasks';
import type { BoardColumn } from '../../api/projects';

interface ProjectBoardProps {
  projectId: string;
}

const WS_BASE = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

const ProjectBoard: React.FC<ProjectBoardProps> = ({ projectId }) => {
  const { activeBoard, fetchBoard } = useProjectStore();
  const { tasks, fetchTasks, moveTask, setActiveTask } = useTaskStore();

  const { isConnected, sendMessage } = useWebSocket({
    url: `${WS_BASE}/ws/tasks/${projectId}/`,
    onMessage: (data) => {
      if (data.type === 'task.created' || data.type === 'task.updated' || data.type === 'task.moved') {
        fetchTasks({ project: projectId });
      }
    },
  });

  useEffect(() => {
    fetchBoard(projectId);
    fetchTasks({ project: projectId });
  }, [projectId, fetchBoard, fetchTasks]);

  const handleTaskMove = useCallback(
    async (taskId: string, targetColumnId: string, targetIndex: number) => {
      await moveTask(taskId, targetColumnId, targetIndex);
      sendMessage({
        type: 'task.move',
        data: { task_id: taskId, column_id: targetColumnId, position: targetIndex },
      });
    },
    [moveTask, sendMessage]
  );

  const { draggedItem, dropTargetColumn, isDragging, handleDragStart, handleDragOver, handleDragEnd } =
    useDragAndDrop({ onTaskMove: handleTaskMove });

  const tasksByColumn = useMemo(() => groupTasksByColumn(tasks), [tasks]);

  if (!activeBoard) {
    return <div className="loading-spinner">Loading board...</div>;
  }

  return (
    <div className="project-board">
      <div className="board-header">
        <h2>{activeBoard.name}</h2>
        <div className="board-indicators">
          <span className={`ws-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? 'Live' : 'Offline'}
          </span>
        </div>
      </div>

      <div className="board-columns">
        {activeBoard.columns
          .sort((a, b) => a.position - b.position)
          .map((column) => {
            const columnTasks = (tasksByColumn[column.id] || []).sort(
              (a, b) => a.position - b.position
            );
            const isOverWipLimit = column.wip_limit && columnTasks.length > column.wip_limit;

            return (
              <div
                key={column.id}
                className={`board-column ${dropTargetColumn === column.id ? 'drop-target' : ''} ${isOverWipLimit ? 'wip-exceeded' : ''}`}
                onDragOver={(e) => {
                  e.preventDefault();
                  handleDragOver(column.id, columnTasks.length);
                }}
                onDrop={handleDragEnd}
              >
                <div className="column-header" style={{ borderBottomColor: column.color }}>
                  <h3>{column.name}</h3>
                  <span className="column-count">
                    {columnTasks.length}
                    {column.wip_limit && ` / ${column.wip_limit}`}
                  </span>
                </div>

                <div className="column-tasks">
                  {columnTasks.map((task, index) => (
                    <TaskCard
                      key={task.id}
                      task={task}
                      index={index}
                      columnId={column.id}
                      onDragStart={handleDragStart}
                      onClick={() => setActiveTask(task)}
                      isDragging={draggedItem?.id === task.id}
                    />
                  ))}
                </div>
              </div>
            );
          })}
      </div>
    </div>
  );
};

interface TaskCardProps {
  task: Task;
  index: number;
  columnId: string;
  onDragStart: (item: any) => void;
  onClick: () => void;
  isDragging: boolean;
}

const TaskCard: React.FC<TaskCardProps> = ({
  task,
  index,
  columnId,
  onDragStart,
  onClick,
  isDragging,
}) => {
  const priorityColors: Record<string, string> = {
    highest: '#DC2626',
    high: '#F97316',
    medium: '#EAB308',
    low: '#3B82F6',
    lowest: '#6B7280',
  };

  return (
    <div
      className={`task-card ${isDragging ? 'dragging' : ''}`}
      draggable
      onDragStart={() =>
        onDragStart({
          id: task.id,
          type: 'task',
          sourceColumnId: columnId,
          sourceIndex: index,
        })
      }
      onClick={onClick}
    >
      <div className="task-card-header">
        <span className="task-key">{task.task_key}</span>
        <span
          className="priority-dot"
          style={{ backgroundColor: priorityColors[task.priority] }}
          title={task.priority}
        />
      </div>
      <p className="task-title">{task.title}</p>
      <div className="task-card-footer">
        {task.labels.map((label) => (
          <span key={label.id} className="label-chip" style={{ backgroundColor: label.color }}>
            {label.name}
          </span>
        ))}
      </div>
      <div className="task-card-meta">
        {task.assignee && (
          <span className="assignee-avatar" title={task.assignee.full_name}>
            {task.assignee.first_name.charAt(0)}{task.assignee.last_name.charAt(0)}
          </span>
        )}
        {task.story_points && <span className="story-points">{task.story_points}</span>}
        {task.subtask_count > 0 && (
          <span className="subtask-count">{task.subtask_completed}/{task.subtask_count}</span>
        )}
        {task.comment_count > 0 && <span className="comment-count">{task.comment_count}</span>}
      </div>
    </div>
  );
};

export default ProjectBoard;
