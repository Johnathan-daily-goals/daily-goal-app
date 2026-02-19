import { useState } from 'react';
import type { User } from '../types';

// We store tokens in localStorage so the user stays logged in on page refresh.
// In a more security-sensitive app you'd use httpOnly cookies instead —
// but localStorage is fine for a portfolio project and is much simpler to implement.

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
