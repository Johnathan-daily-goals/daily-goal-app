import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getProjects } from '../api/projects';
import { getTodaysGoal, upsertTodaysGoal } from '../api/goals';
import { logout } from '../api/auth';
import { useToast } from '../components/ToastProvider';
import type { Project, DailyGoal } from '../types';

interface Props {
  onLogout: () => void;
}

type ProjectWithGoal = Project & { todayGoal: DailyGoal | null };

export default function TodayPage({ onLogout }: Props) {
  const [items, setItems] = useState<ProjectWithGoal[]>([]);
  const [loading, setLoading] = useState(true);
  const { showToast } = useToast();

  const [editingId, setEditingId] = useState<number | null>(null);
  const [editText, setEditText] = useState('');
  const [savingId, setSavingId] = useState<number | null>(null);
  const [savedId, setSavedId] = useState<number | null>(null);

  const navigate = useNavigate();

  const today = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  });

  useEffect(() => {
    loadAll();
  }, []);

  async function loadAll() {
    try {
      const projects = await getProjects();

      // allSettled so a 404 (no goal yet) doesn't abort the rest
      const goalResults = await Promise.allSettled(
        projects.map((p) => getTodaysGoal(p.id))
      );

      const combined: ProjectWithGoal[] = projects.map((project, i) => ({
        ...project,
        todayGoal: goalResults[i].status === 'fulfilled' ? goalResults[i].value : null,
      }));

      setItems(combined);
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Failed to load');
    } finally {
      setLoading(false);
    }
  }

  function startEditing(project: ProjectWithGoal) {
    setEditingId(project.id);
    setEditText(project.todayGoal?.goal_text ?? '');
  }

  async function handleSave(projectId: number) {
    if (!editText.trim()) return;
    setSavingId(projectId);

    try {
      const updated = await upsertTodaysGoal(projectId, editText.trim());

      setItems((prev) =>
        prev.map((item) =>
          item.id === projectId ? { ...item, todayGoal: updated } : item
        )
      );

      setEditingId(null);
      setSavedId(projectId);
      setTimeout(() => setSavedId(null), 2000);
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Failed to save');
    } finally {
      setSavingId(null);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent, projectId: number) {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      handleSave(projectId);
    }
    if (e.key === 'Escape') {
      setEditingId(null);
    }
  }

  async function handleLogout() {
    const refreshToken = localStorage.getItem('refresh_token') ?? '';
    try { await logout(refreshToken); } catch { /* ignore */ }
    onLogout();
    navigate('/login');
  }

  const goalsSetCount = items.filter((i) => i.todayGoal).length;

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-2xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 bg-indigo-600 rounded-lg flex items-center justify-center">
              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <span className="font-semibold text-gray-900 text-sm">Daily Goals</span>
          </div>
          <div className="flex items-center gap-5">
            <button
              onClick={() => navigate('/projects')}
              className="text-xs text-gray-500 hover:text-gray-900 transition-colors font-medium"
            >
              Projects
            </button>
            <button
              onClick={handleLogout}
              className="text-xs text-gray-500 hover:text-gray-900 transition-colors font-medium"
            >
              Sign out
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-6 py-10">

        {/* Date heading */}
        <div className="mb-8">
          <p className="text-xs font-medium text-indigo-500 uppercase tracking-widest mb-1">{today}</p>
          <h1 className="text-2xl font-semibold text-gray-900">Today's Goals</h1>
          {!loading && items.length > 0 && (
            <p className="text-sm text-gray-400 mt-1">
              {goalsSetCount} of {items.length} set
            </p>
          )}
        </div>

        {/* Loading skeleton */}
        {loading && (
          <div className="space-y-3">
            {[1, 2].map((n) => (
              <div key={n} className="bg-white border border-gray-100 rounded-2xl p-5 animate-pulse">
                <div className="h-4 bg-gray-100 rounded w-1/4 mb-3" />
                <div className="h-10 bg-gray-100 rounded-lg w-full" />
              </div>
            ))}
          </div>
        )}

        {/* No projects at all */}
        {!loading && items.length === 0 && (
          <div className="text-center py-20">
            <div className="w-14 h-14 bg-indigo-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <svg className="w-7 h-7 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v6m3-3H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p className="text-gray-900 font-medium">No projects yet</p>
            <p className="text-sm text-gray-400 mt-1">Create a project first to set daily goals.</p>
            <button
              onClick={() => navigate('/projects')}
              className="mt-5 text-sm text-indigo-600 font-medium hover:text-indigo-700"
            >
              Go to Projects →
            </button>
          </div>
        )}

        {/* Project + goal cards */}
        {!loading && (
          <ul className="space-y-3">
            {items.map((item) => {
              const isEditing = editingId === item.id;
              const isSaving = savingId === item.id;
              const justSaved = savedId === item.id;

              return (
                <li key={item.id} className="bg-white border border-gray-200 rounded-2xl p-5 transition-all hover:border-gray-300">

                  {/* Project name row */}
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full bg-indigo-400 shrink-0" />
                      <span className="text-sm font-semibold text-gray-900">{item.name}</span>
                    </div>

                    <div className="flex items-center gap-3">
                      {/* "Saved" flash */}
                      {justSaved && (
                        <span className="flex items-center gap-1 text-xs text-emerald-600 font-medium">
                          <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clipRule="evenodd" />
                          </svg>
                          Saved
                        </span>
                      )}

                      {/* Goal set indicator */}
                      {item.todayGoal && !isEditing && !justSaved && (
                        <span className="text-xs text-emerald-500 font-medium">✓ Set</span>
                      )}

                      {/* Edit / Cancel toggle */}
                      {!isEditing ? (
                        <button
                          onClick={() => startEditing(item)}
                          className="text-xs text-indigo-500 hover:text-indigo-700 font-medium transition-colors"
                        >
                          {item.todayGoal ? 'Edit' : 'Set goal'}
                        </button>
                      ) : (
                        <button
                          onClick={() => setEditingId(null)}
                          className="text-xs text-gray-400 hover:text-gray-600 transition-colors"
                        >
                          Cancel
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Goal content */}
                  {isEditing ? (
                    <div className="space-y-2">
                      <textarea
                        autoFocus
                        value={editText}
                        onChange={(e) => setEditText(e.target.value)}
                        onKeyDown={(e) => handleKeyDown(e, item.id)}
                        rows={3}
                        placeholder="What's your goal for today?"
                        className="w-full border border-indigo-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none bg-indigo-50/30 transition-all"
                      />
                      <div className="flex items-center justify-between">
                        <p className="text-xs text-gray-300">⌘ Enter to save</p>
                        <button
                          onClick={() => handleSave(item.id)}
                          disabled={isSaving || !editText.trim()}
                          className="bg-indigo-600 text-white text-xs font-medium px-3.5 py-1.5 rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors flex items-center gap-1.5"
                        >
                          {isSaving && (
                            <svg className="animate-spin h-3 w-3" viewBox="0 0 24 24" fill="none">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                            </svg>
                          )}
                          {isSaving ? 'Saving…' : 'Save'}
                        </button>
                      </div>
                    </div>
                  ) : item.todayGoal ? (
                    <p
                      onClick={() => startEditing(item)}
                      className="text-sm text-gray-700 leading-relaxed cursor-pointer hover:text-gray-900 transition-colors"
                    >
                      {item.todayGoal.goal_text}
                    </p>
                  ) : (
                    <button
                      onClick={() => startEditing(item)}
                      className="text-sm text-gray-300 hover:text-gray-500 transition-colors text-left w-full"
                    >
                      No goal set yet — click to write one…
                    </button>
                  )}
                </li>
              );
            })}
          </ul>
        )}
      </main>
    </div>
  );
}
