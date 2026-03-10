/**
 * GanttChart: interactive Gantt chart component that visualizes task timelines,
 * dependencies, and milestones across a project schedule.
 */

import React, { useMemo, useRef, useState } from 'react';
import { daysBetween, formatDate } from '../../utils/dateUtils';
import { getPriorityConfig } from '../../utils/taskUtils';
import type { Task } from '../../api/tasks';
import type { Milestone } from '../../api/milestones';

interface GanttChartProps {
  tasks: Task[];
  milestones?: Milestone[];
  startDate: string;
  endDate: string;
  onTaskClick?: (task: Task) => void;
}

interface GanttRow {
  id: string;
  label: string;
  type: 'task' | 'milestone';
  startDate: string | null;
  endDate: string | null;
  progress: number;
  color: string;
  priority: string;
  assignee: string;
  data: Task | Milestone;
}

const DAY_WIDTH = 32; // pixels per day
const ROW_HEIGHT = 40;
const HEADER_HEIGHT = 60;

const GanttChart: React.FC<GanttChartProps> = ({
  tasks,
  milestones = [],
  startDate,
  endDate,
  onTaskClick,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [hoveredRow, setHoveredRow] = useState<string | null>(null);
  const [zoom, setZoom] = useState(1);

  const totalDays = daysBetween(startDate, endDate);
  const dayWidth = DAY_WIDTH * zoom;
  const chartWidth = totalDays * dayWidth;

  // Build row data from tasks and milestones
  const rows = useMemo<GanttRow[]>(() => {
    const taskRows: GanttRow[] = tasks
      .filter((t) => t.start_date || t.due_date)
      .map((task) => ({
        id: task.id,
        label: `${task.task_key}: ${task.title}`,
        type: 'task' as const,
        startDate: task.start_date || task.due_date,
        endDate: task.due_date || task.start_date,
        progress: task.completed_at ? 100 : 0,
        color: getPriorityConfig(task.priority).color,
        priority: task.priority,
        assignee: task.assignee?.full_name || 'Unassigned',
        data: task,
      }));

    const milestoneRows: GanttRow[] = milestones.map((ms) => ({
      id: ms.id,
      label: ms.title,
      type: 'milestone' as const,
      startDate: ms.start_date || ms.due_date,
      endDate: ms.due_date,
      progress: ms.progress_percentage,
      color: ms.color,
      priority: ms.priority,
      assignee: ms.owner?.full_name || '',
      data: ms,
    }));

    return [...milestoneRows, ...taskRows];
  }, [tasks, milestones]);

  // Generate date headers
  const dateHeaders = useMemo(() => {
    const headers: Array<{ date: string; label: string; isWeekend: boolean; isToday: boolean }> = [];
    const start = new Date(startDate);
    const today = new Date().toISOString().split('T')[0];

    for (let i = 0; i < totalDays; i++) {
      const current = new Date(start);
      current.setDate(current.getDate() + i);
      const dateStr = current.toISOString().split('T')[0];
      const dayOfWeek = current.getDay();

      headers.push({
        date: dateStr,
        label: current.getDate().toString(),
        isWeekend: dayOfWeek === 0 || dayOfWeek === 6,
        isToday: dateStr === today,
      });
    }
    return headers;
  }, [startDate, totalDays]);

  // Calculate bar position and width for a row
  const getBarStyle = (row: GanttRow) => {
    if (!row.startDate) return null;
    const start = daysBetween(startDate, row.startDate);
    const duration = row.endDate ? daysBetween(row.startDate, row.endDate) : 1;
    const left = Math.max(0, start) * dayWidth;
    const width = Math.max(1, duration) * dayWidth;

    return { left, width };
  };

  const totalHeight = HEADER_HEIGHT + rows.length * ROW_HEIGHT;

  return (
    <div className="gantt-chart">
      <div className="gantt-controls">
        <button className="btn btn-sm" onClick={() => setZoom(Math.max(0.5, zoom - 0.25))}>
          Zoom Out
        </button>
        <span>{Math.round(zoom * 100)}%</span>
        <button className="btn btn-sm" onClick={() => setZoom(Math.min(3, zoom + 0.25))}>
          Zoom In
        </button>
      </div>

      <div className="gantt-container" ref={containerRef} style={{ height: totalHeight }}>
        {/* Left panel: task labels */}
        <div className="gantt-labels">
          <div className="gantt-label-header" style={{ height: HEADER_HEIGHT }}>
            Task
          </div>
          {rows.map((row) => (
            <div
              key={row.id}
              className={`gantt-label-row ${hoveredRow === row.id ? 'hovered' : ''}`}
              style={{ height: ROW_HEIGHT }}
              onMouseEnter={() => setHoveredRow(row.id)}
              onMouseLeave={() => setHoveredRow(null)}
              title={`${row.label} | ${row.assignee}`}
            >
              <span className={`row-type-indicator ${row.type}`} style={{ backgroundColor: row.color }} />
              <span className="row-label">{row.label}</span>
            </div>
          ))}
        </div>

        {/* Right panel: chart area */}
        <div className="gantt-chart-area" style={{ width: chartWidth }}>
          {/* Date headers */}
          <div className="gantt-date-headers" style={{ height: HEADER_HEIGHT }}>
            {dateHeaders.map((header) => (
              <div
                key={header.date}
                className={`gantt-date-cell ${header.isWeekend ? 'weekend' : ''} ${header.isToday ? 'today' : ''}`}
                style={{ width: dayWidth }}
              >
                {header.label}
              </div>
            ))}
          </div>

          {/* Grid lines and bars */}
          <div className="gantt-grid">
            {/* Vertical grid lines */}
            {dateHeaders.map((header) => (
              <div
                key={header.date}
                className={`gantt-grid-line ${header.isWeekend ? 'weekend' : ''} ${header.isToday ? 'today-line' : ''}`}
                style={{ left: dateHeaders.indexOf(header) * dayWidth, width: dayWidth, height: rows.length * ROW_HEIGHT }}
              />
            ))}

            {/* Task bars */}
            {rows.map((row, rowIndex) => {
              const barStyle = getBarStyle(row);
              if (!barStyle) return null;

              return (
                <div
                  key={row.id}
                  className={`gantt-bar ${row.type} ${hoveredRow === row.id ? 'hovered' : ''}`}
                  style={{
                    top: rowIndex * ROW_HEIGHT + 8,
                    left: barStyle.left,
                    width: barStyle.width,
                    height: ROW_HEIGHT - 16,
                    backgroundColor: row.type === 'milestone' ? 'transparent' : row.color,
                    borderColor: row.color,
                  }}
                  onMouseEnter={() => setHoveredRow(row.id)}
                  onMouseLeave={() => setHoveredRow(null)}
                  onClick={() => {
                    if (row.type === 'task' && onTaskClick) {
                      onTaskClick(row.data as Task);
                    }
                  }}
                >
                  {row.type === 'task' && row.progress > 0 && (
                    <div
                      className="gantt-bar-progress"
                      style={{ width: `${row.progress}%` }}
                    />
                  )}
                  {row.type === 'milestone' && (
                    <div className="milestone-diamond" style={{ backgroundColor: row.color }} />
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default GanttChart;
