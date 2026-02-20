const BASE_URL = import.meta.env.VITE_API_URL ?? '';

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

  // .json() throws on empty bodies (e.g. 204 or a Flask crash)
  const text = await res.text();
  const data = text ? JSON.parse(text) : null;

  if (res.status === 401) {
    localStorage.removeItem('user');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    // replace() so the Back button doesn't loop back to login
    window.location.replace('/login');
    throw new Error('Session expired');
  }

  if (!res.ok) {
    throw new Error(data?.error ?? `Request failed (${res.status})`);
  }

  return data as T;
}
