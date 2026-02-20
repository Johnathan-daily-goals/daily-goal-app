import { useState } from 'react';
import type { User } from '../types';

function getStoredUser(): User | null {
  const raw = localStorage.getItem('user');
  return raw ? (JSON.parse(raw) as User) : null;
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(getStoredUser);

  const isLoggedIn = user !== null;

  function saveSession(user: User, accessToken: string, refreshToken: string) {
    localStorage.setItem('user', JSON.stringify(user));
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
    setUser(user);
  }

  function clearSession() {
    localStorage.removeItem('user');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  }

  return { user, isLoggedIn, saveSession, clearSession };
}
