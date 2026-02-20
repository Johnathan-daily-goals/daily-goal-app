import { apiFetch } from './client';
import type { Project } from '../types';

export function getProjects() {
  return apiFetch<Project[]>('/projects');
}

export function getProject(id: number) {
  return apiFetch<Project>(`/projects/${id}`);
}

export function createProject(name: string, description?: string) {
  return apiFetch<Project>('/projects', {
    method: 'POST',
    body: JSON.stringify({ name, description }),
  });
}

export function archiveProject(id: number) {
  return apiFetch<Project>(`/projects/${id}/archive`, { method: 'POST' });
}

export function restoreProject(id: number) {
  return apiFetch<Project>(`/projects/${id}/restore`, { method: 'POST' });
}

export function getArchivedProjects() {
  return apiFetch<Project[]>('/projects/archived');
}
