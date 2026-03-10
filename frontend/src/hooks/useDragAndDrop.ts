/**
 * Custom hook for drag-and-drop functionality on the Kanban board.
 * Handles column reordering and task movement between columns.
 */

import { useCallback, useState } from 'react';

export interface DragItem {
  id: string;
  type: 'task' | 'column';
  sourceColumnId?: string;
  sourceIndex: number;
}

interface DropResult {
  targetColumnId: string;
  targetIndex: number;
}

interface UseDragAndDropOptions {
  onTaskMove?: (taskId: string, targetColumnId: string, targetIndex: number) => void;
  onColumnReorder?: (columnId: string, targetIndex: number) => void;
}

export function useDragAndDrop({ onTaskMove, onColumnReorder }: UseDragAndDropOptions) {
  const [draggedItem, setDraggedItem] = useState<DragItem | null>(null);
  const [dropTargetColumn, setDropTargetColumn] = useState<string | null>(null);
  const [dropTargetIndex, setDropTargetIndex] = useState<number | null>(null);

  const handleDragStart = useCallback(
    (item: DragItem) => {
      setDraggedItem(item);
    },
    []
  );

  const handleDragOver = useCallback(
    (columnId: string, index: number) => {
      setDropTargetColumn(columnId);
      setDropTargetIndex(index);
    },
    []
  );

  const handleDragEnd = useCallback(() => {
    if (!draggedItem || dropTargetColumn === null || dropTargetIndex === null) {
      setDraggedItem(null);
      setDropTargetColumn(null);
      setDropTargetIndex(null);
      return;
    }

    if (draggedItem.type === 'task') {
      // Skip if dropping in the same position
      const sameColumn = draggedItem.sourceColumnId === dropTargetColumn;
      const sameIndex = draggedItem.sourceIndex === dropTargetIndex;
      if (!(sameColumn && sameIndex)) {
        onTaskMove?.(draggedItem.id, dropTargetColumn, dropTargetIndex);
      }
    } else if (draggedItem.type === 'column') {
      if (draggedItem.sourceIndex !== dropTargetIndex) {
        onColumnReorder?.(draggedItem.id, dropTargetIndex);
      }
    }

    setDraggedItem(null);
    setDropTargetColumn(null);
    setDropTargetIndex(null);
  }, [draggedItem, dropTargetColumn, dropTargetIndex, onTaskMove, onColumnReorder]);

  const handleDragCancel = useCallback(() => {
    setDraggedItem(null);
    setDropTargetColumn(null);
    setDropTargetIndex(null);
  }, []);

  return {
    draggedItem,
    dropTargetColumn,
    dropTargetIndex,
    isDragging: draggedItem !== null,
    handleDragStart,
    handleDragOver,
    handleDragEnd,
    handleDragCancel,
  };
}
