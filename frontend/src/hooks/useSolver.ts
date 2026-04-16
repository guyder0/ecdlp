import { useState, useEffect, useCallback } from 'react';
import { socket, type TaskStartedData, type TaskCompleteData } from '@/services/socket';

export interface TaskState {
  taskId: string | null;
  status: 'idle' | 'running' | 'completed' | 'failed' | 'cancelled';
  result?: string;
  error?: string;
}

// Словарь состояний: ключ — curve_id
type SolverState = Record<string, TaskState>;

export const useSolver = () => {
  const [tasks, setTasks] = useState<SolverState>({});

  // Вспомогательная функция для обновления состояния конкретной кривой
  const updateTask = useCallback((curveId: string, patch: Partial<TaskState>) => {
    setTasks((prev) => ({
      ...prev,
      [curveId]: {
        ...(prev[curveId] || { taskId: null, status: 'idle' }),
        ...patch,
      },
    }));
  }, []);

  useEffect(() => {
    // 1. Слушаем начало задачи
    const onTaskStarted = (data: TaskStartedData) => {
      updateTask(data.curve_id, {
        taskId: data.task_id,
        status: 'running',
        error: undefined,
        result: undefined,
      });
    };

    // 2. Слушаем завершение задачи
    const onTaskComplete = (data: TaskCompleteData) => {
      // Ищем, какой кривой принадлежал этот task_id
      setTasks((prev) => {
        const curveId = Object.keys(prev).find((id) => prev[id].taskId === data.task_id);
        
        if (!curveId) return prev; // Если задача не наша или уже удалена

        return {
          ...prev,
          [curveId]: {
            ...prev[curveId],
            status: data.status === 'success' ? 'completed' : data.status,
            result: data.result,
            error: data.error,
          },
        };
      });
    };

    socket.on('task_started', onTaskStarted);
    socket.on('task_complete', onTaskComplete);

    return () => {
      socket.off('task_started', onTaskStarted);
      socket.off('task_complete', onTaskComplete);
    };
  }, [updateTask]);

  /**
   * Запустить решение
   */
  const solve = useCallback((curveId: string, x: string) => {
    // Сбрасываем состояние карточки перед стартом
    updateTask(curveId, { status: 'running', taskId: null, result: undefined, error: undefined });
    socket.emit('solve', { curve_id: curveId, x });
  }, [updateTask]);

  /**
   * Отменить решение
   */
  const cancel = useCallback((curveId: string) => {
    const task = tasks[curveId];
    if (task?.taskId) {
      socket.emit('cancel', { task_id: task.taskId });
    }
  }, [tasks]);

  return {
    tasks,
    solve,
    cancel,
  };
};