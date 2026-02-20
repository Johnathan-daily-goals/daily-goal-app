import { apiFetch } from './client';
import type { DailyGoal } from '../types';

export function getTodaysGoal(projectId: number) {
  return apiFetch<DailyGoal>(`/projects/${projectId}/goals/today`);
}

export function upsertTodaysGoal(projectId: number, goalText: string) {
  return apiFetch<DailyGoal>(`/projects/${projectId}/goals/today`, {
    method: 'PUT',
    body: JSON.stringify({ goal_text: goalText }),
  });
}

export function getGoals(projectId: number) {
  return apiFetch<DailyGoal[]>(`/projects/${projectId}/goals`);
}
