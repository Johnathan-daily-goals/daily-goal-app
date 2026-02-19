// This is the "base" HTTP client. Every API call goes through here.
// It handles:
//   1. Prefixing all URLs with the backend base URL
//   2. Attaching the Authorization header automatically
//   3. Parsing JSON responses
//   4. Throwing a consistent error shape when the server returns an error

// Empty string = relative URL. In dev, Vite proxies these to Flask.
// In production, set VITE_API_URL env var to point at your deployed backend.
const BASE_URL = import.meta.env.VITE_API_URL ?? '';

// A thin wrapper around fetch that:
// - always sends JSON
// - attaches the bearer token if one is stored
// - throws an Error with the backend's error message if status >= 400
export async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem('access_token');

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
  });

  // Read as text first — calling .json() on an empty body throws.
  // This can happen on 204 responses or if Flask crashes before sending JSON.
  const text = await res.text();
  const data = text ? JSON.parse(text) : null;

  if (res.status === 401) {
    // Token is invalid or expired — clear the session and send to login.
    // We use window.location.replace (not navigate) because:
    //   1. This code lives outside React, so we can't use useNavigate()
    //   2. replace() doesn't add to browser history, so Back won't loop them here
    localStorage.removeItem('user');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.replace('/login');
    // Throw so any in-flight .catch() handlers don't try to update state
    // on an unmounting component
    throw new Error('Session expired');
  }

  if (!res.ok) {
    // data?.error is the backend's error message (e.g. "Invalid credentials")
    throw new Error(data?.error ?? `Request failed (${res.status})`);
  }

  return data as T;
}
