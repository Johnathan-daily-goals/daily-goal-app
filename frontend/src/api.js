const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

async function apiFetch(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    ...options
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "Request failed");
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export const api = {
  listProjects: () => apiFetch("/api/projects"),
  createProject: (payload) =>
    apiFetch("/api/projects", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  getProject: (id) => apiFetch(`/api/projects/${id}`),
  updateProject: (id, payload) =>
    apiFetch(`/api/projects/${id}`, {
      method: "PATCH",
      body: JSON.stringify(payload)
    }),
  listGoals: (id) => apiFetch(`/api/projects/${id}/goals`),
  createGoal: (id, payload) =>
    apiFetch(`/api/projects/${id}/goals`, {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  listRetros: (id) => apiFetch(`/api/projects/${id}/retros`),
  createRetro: (id, payload) =>
    apiFetch(`/api/projects/${id}/retros`, {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  dashboard: () => apiFetch("/api/dashboard")
};
