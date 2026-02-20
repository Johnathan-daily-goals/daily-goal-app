import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getProject } from '../api/projects';
import { getTodaysGoal, upsertTodaysGoal } from '../api/goals';
import { useToast } from '../components/ToastProvider';
import type { Project, DailyGoal } from '../types';

export default function ProjectPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { showToast } = useToast();

  const [project, setProject] = useState<Project | null>(null);
  const [goal, setGoal] = useState<DailyGoal | null>(null);
  const [goalText, setGoalText] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (!id) return;
    loadData(Number(id));
  }, [id]);

  async function loadData(projectId: number) {
    try {
      const [projectResult, goalResult] = await Promise.allSettled([
        getProject(projectId),
        getTodaysGoal(projectId),
      ]);

      if (projectResult.status === 'fulfilled') {
        setProject(projectResult.value);
      } else {
        showToast('Project not found');
        return;
      }

      if (goalResult.status === 'fulfilled') {
        setGoal(goalResult.value);
        setGoalText(goalResult.value.goal_text);
      }
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Failed to load project');
    } finally {
      setLoading(false);
    }
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    if (!id) return;
    setSaving(true);
    try {
      const updated = await upsertTodaysGoal(Number(id), goalText);
      setGoal(updated);
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Failed to save goal');
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <svg className="animate-spin h-6 w-6 text-indigo-400" viewBox="0 0 24 24" fill="none">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-500 font-medium">Project not found</p>
          <button onClick={() => navigate('/')} className="text-sm text-indigo-600 mt-2 hover:underline">
            Go back home
          </button>
        </div>
      </div>
    );
  }

  const today = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  });

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-2xl mx-auto px-6 h-14 flex items-center gap-3">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-1.5 text-sm text-gray-400 hover:text-gray-700 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
            </svg>
            Projects
          </button>
          <span className="text-gray-200">/</span>
          <span className="text-sm font-medium text-gray-900 truncate">{project.name}</span>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-6 py-12">

        {/* Date + heading */}
        <div className="mb-8">
          <p className="text-xs font-medium text-indigo-500 uppercase tracking-widest mb-2">{today}</p>
          <h1 className="text-2xl font-semibold text-gray-900">What's your goal today?</h1>
          {project.description && (
            <p className="text-sm text-gray-400 mt-1">{project.description}</p>
          )}
        </div>

        {/* Goal already set banner */}
        {goal && !saving && (
          <div className="flex items-center gap-2 text-sm text-emerald-700 bg-emerald-50 border border-emerald-100 rounded-xl px-4 py-2.5 mb-5">
            <svg className="w-4 h-4 shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clipRule="evenodd" />
            </svg>
            Goal set for today — you can update it below.
          </div>
        )}

        {/* Goal form */}
        <form onSubmit={handleSave} className="space-y-4">
          <textarea
            value={goalText}
            onChange={(e) => setGoalText(e.target.value)}
            rows={5}
            required
            autoFocus
            placeholder="Write your goal for today…"
            className="w-full border border-gray-200 rounded-2xl px-5 py-4 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none shadow-sm transition-all placeholder-gray-300"
          />

          <div className="flex items-center gap-3">
            <button
              type="submit"
              disabled={saving}
              className="bg-indigo-600 text-white text-sm font-medium px-5 py-2.5 rounded-xl hover:bg-indigo-700 disabled:opacity-60 transition-colors flex items-center gap-2"
            >
              {saving && (
                <svg className="animate-spin h-3.5 w-3.5" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
              )}
              {saving ? 'Saving…' : goal ? 'Update goal' : 'Set goal'}
            </button>

            {/* Success flash */}
            {saved && (
              <span className="flex items-center gap-1.5 text-sm text-emerald-600 font-medium">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clipRule="evenodd" />
                </svg>
                Saved
              </span>
            )}
          </div>
        </form>
      </main>
    </div>
  );
}
