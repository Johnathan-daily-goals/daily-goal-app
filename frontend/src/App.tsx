import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import TodayPage from './pages/TodayPage';
import DashboardPage from './pages/DashboardPage';
import ProjectPage from './pages/ProjectPage';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isLoggedIn } = useAuth();
  return isLoggedIn ? <>{children}</> : <Navigate to="/login" replace />;
}

export default function App() {
  const { isLoggedIn, saveSession, clearSession } = useAuth();

  return (
    <Routes>
      {/* Public routes */}
      <Route
        path="/login"
        element={isLoggedIn ? <Navigate to="/" replace /> : <LoginPage onLogin={saveSession} />}
      />
      <Route
        path="/register"
        element={isLoggedIn ? <Navigate to="/" replace /> : <RegisterPage onLogin={saveSession} />}
      />

      {/* / → Today page (main landing after login) */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <TodayPage onLogout={clearSession} />
          </ProtectedRoute>
        }
      />

      {/* /projects → project management */}
      <Route
        path="/projects"
        element={
          <ProtectedRoute>
            <DashboardPage onLogout={clearSession} />
          </ProtectedRoute>
        }
      />

      {/* /projects/:id → individual project goal editor */}
      <Route
        path="/projects/:id"
        element={
          <ProtectedRoute>
            <ProjectPage />
          </ProtectedRoute>
        }
      />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
