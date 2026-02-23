import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getProjects, createProject, archiveProject, getArchivedProjects, restoreProject } from '../api/projects';
import { logout } from '../api/auth';
import { useToast } from '../components/ToastProvider';
import type { Project } from '../types';

interface Props {
  onLogout: () => void;
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

export default function DashboardPage({ onLogout }: Props) {
  const [tab, setTab] = useState<'active' | 'archived'>('active');
  const [projects, setProjects] = useState<Project[]>([]);
  const [archivedProjects, setArchivedProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [archivedLoading, setArchivedLoading] = useState(false);
  const [archivedLoaded, setArchivedLoaded] = useState(false);
  const { showToast } = useToast();
  const [showForm, setShowForm] = useState(false);
  const [newName, setNewName] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [creating, setCreating] = useState(false);
  const [archiveTarget, setArchiveTarget] = useState<Project | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadProjects();
  }, []);

  async function loadProjects() {
    try {
      const data = await getProjects();
      setProjects(data);
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Failed to load projects');
    } finally {
      setLoading(false);
    }
  }

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setCreating(true);
    try {
      const project = await createProject(newName, newDesc || undefined);
      setProjects((prev) => [project, ...prev]);
      setNewName('');
      setNewDesc('');
      setShowForm(false);
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Failed to create project');
    } finally {
      setCreating(false);
    }
  }

  function handleArchive(e: React.MouseEvent, project: Project) {
    e.stopPropagation();
    setArchiveTarget(project);
  }

  async function confirmArchive() {
    if (!archiveTarget) return;
    try {
      await archiveProject(archiveTarget.id);
      setProjects((prev) => prev.filter((p) => p.id !== archiveTarget.id));
      setArchivedLoaded(false);
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Failed to archive project');
    } finally {
      setArchiveTarget(null);
    }
  }

  async function handleRestore(e: React.MouseEvent, id: number) {
    e.stopPropagation();
    try {
      await restoreProject(id);
      setArchivedProjects((prev) => prev.filter((p) => p.id !== id));
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Failed to restore project');
    }
  }

  async function handleTabSwitch(next: 'active' | 'archived') {
    setTab(next);
    if (next === 'archived' && !archivedLoaded) {
      setArchivedLoading(true);
      try {
        const data = await getArchivedProjects();
        setArchivedProjects(data);
        setArchivedLoaded(true);
      } catch (err) {
        showToast(err instanceof Error ? err.message : 'Failed to load archived projects');
      } finally {
        setArchivedLoading(false);
      }
    }
  }

  async function handleLogout() {
    const refreshToken = localStorage.getItem('refresh_token') ?? '';
    try {
      await logout(refreshToken);
    } catch {
      // ignore — clear session regardless
    }
    onLogout();
    navigate('/login');
  }

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
              onClick={() => navigate('/')}
              className="text-xs text-gray-500 hover:text-gray-900 transition-colors font-medium"
            >
              Today
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

      <main className="max-w-2xl mx-auto px-6 py-8">

        {/* Page title row */}
        <div className="flex items-center justify-between mb-5">
          <h1 className="text-xl font-semibold text-gray-900">Projects</h1>
          {tab === 'active' && (
            <button
              onClick={() => setShowForm((v) => !v)}
              className={`text-sm font-medium px-4 py-2 rounded-lg transition-colors ${
                showForm
                  ? 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  : 'bg-indigo-600 text-white hover:bg-indigo-700'
              }`}
            >
              {showForm ? 'Cancel' : '+ New project'}
            </button>
          )}
        </div>

        {/* Tabs */}
        <div className="flex gap-1 bg-gray-100 rounded-lg p-1 mb-6 w-fit">
          {(['active', 'archived'] as const).map((t) => (
            <button
              key={t}
              onClick={() => handleTabSwitch(t)}
              className={`text-xs font-medium px-4 py-1.5 rounded-md transition-colors capitalize ${
                tab === t
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {t}
            </button>
          ))}
        </div>

        {/* New project form */}
        {showForm && (
          <form
            onSubmit={handleCreate}
            className="bg-white border border-indigo-100 ring-1 ring-indigo-50 rounded-2xl p-5 mb-5 space-y-4"
          >
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1.5 uppercase tracking-wide">
                Project name
              </label>
              <input
                type="text"
                required
                autoFocus
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                className="w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                placeholder="e.g. Learn TypeScript"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1.5 uppercase tracking-wide">
                Description <span className="normal-case text-gray-400 font-normal">(optional)</span>
              </label>
              <input
                type="text"
                value={newDesc}
                onChange={(e) => setNewDesc(e.target.value)}
                className="w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                placeholder="A short description…"
              />
            </div>
            <div className="flex items-center gap-3 pt-1">
              <button
                type="submit"
                disabled={creating}
                className="bg-indigo-600 text-white text-sm font-medium px-4 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-60 transition-colors flex items-center gap-2"
              >
                {creating && (
                  <svg className="animate-spin h-3.5 w-3.5" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                )}
                {creating ? 'Creating…' : 'Create project'}
              </button>
            </div>
          </form>
        )}

        {/* Active tab */}
        {tab === 'active' && (
          <>
            {/* Loading skeleton */}
            {loading && (
              <div className="space-y-3">
                {[1, 2, 3].map((n) => (
                  <div key={n} className="bg-white border border-gray-100 rounded-2xl p-5 animate-pulse">
                    <div className="h-4 bg-gray-100 rounded w-1/3 mb-2" />
                    <div className="h-3 bg-gray-100 rounded w-1/2" />
                  </div>
                ))}
              </div>
            )}

            {/* Empty state */}
            {!loading && projects.length === 0 && (
              <div className="text-center py-20">
                <div className="w-14 h-14 bg-indigo-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <svg className="w-7 h-7 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v6m3-3H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <p className="text-gray-900 font-medium">No projects yet</p>
                <p className="text-sm text-gray-400 mt-1">Create a project to start setting daily goals.</p>
                <button
                  onClick={() => setShowForm(true)}
                  className="mt-5 text-sm text-indigo-600 font-medium hover:text-indigo-700"
                >
                  Create your first project →
                </button>
              </div>
            )}

            {/* Project list */}
            {!loading && projects.length > 0 && (
              <ul className="space-y-2.5">
                {projects.map((project) => (
                  <li key={project.id}>
                    <div
                      onClick={() => navigate(`/projects/${project.id}`)}
                      className="group bg-white border border-gray-200 rounded-2xl p-5 flex items-center gap-4 cursor-pointer hover:border-indigo-200 hover:shadow-sm transition-all"
                    >
                      <div className="w-2 h-2 rounded-full bg-indigo-400 shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-gray-900 truncate">{project.name}</p>
                        {project.description && (
                          <p className="text-sm text-gray-400 truncate mt-0.5">{project.description}</p>
                        )}
                        {project.created_at && (
                          <p className="text-xs text-gray-300 mt-1">Created {formatDate(project.created_at)}</p>
                        )}
                      </div>
                      <div className="flex items-center gap-3 shrink-0">
                        <button
                          onClick={(e) => handleArchive(e, project)}
                          className="text-xs text-gray-300 hover:text-red-400 transition-colors opacity-0 group-hover:opacity-100"
                        >
                          Archive
                        </button>
                        <svg className="w-4 h-4 text-gray-300 group-hover:text-indigo-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
                        </svg>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </>
        )}

        {/* Archived tab */}
        {tab === 'archived' && (
          <>
            {/* Loading skeleton */}
            {archivedLoading && (
              <div className="space-y-3">
                {[1, 2].map((n) => (
                  <div key={n} className="bg-white border border-gray-100 rounded-2xl p-5 animate-pulse">
                    <div className="h-4 bg-gray-100 rounded w-1/3 mb-2" />
                    <div className="h-3 bg-gray-100 rounded w-1/2" />
                  </div>
                ))}
              </div>
            )}

            {/* Empty state */}
            {!archivedLoading && archivedProjects.length === 0 && (
              <div className="text-center py-20">
                <div className="w-14 h-14 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <svg className="w-7 h-7 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z" />
                  </svg>
                </div>
                <p className="text-gray-900 font-medium">No archived projects</p>
                <p className="text-sm text-gray-400 mt-1">Archived projects will appear here.</p>
              </div>
            )}

            {/* Archived project list */}
            {!archivedLoading && archivedProjects.length > 0 && (
              <ul className="space-y-2.5">
                {archivedProjects.map((project) => (
                  <li key={project.id}>
                    <div className="group bg-white border border-gray-200 rounded-2xl p-5 flex items-center gap-4">
                      <div className="w-2 h-2 rounded-full bg-gray-300 shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-gray-500 truncate">{project.name}</p>
                        {project.description && (
                          <p className="text-sm text-gray-400 truncate mt-0.5">{project.description}</p>
                        )}
                        {project.archived_at && (
                          <p className="text-xs text-gray-300 mt-1">Archived {formatDate(project.archived_at)}</p>
                        )}
                      </div>
                      <button
                        onClick={(e) => handleRestore(e, project.id)}
                        className="text-xs text-gray-400 hover:text-indigo-600 font-medium transition-colors shrink-0 opacity-0 group-hover:opacity-100"
                      >
                        Restore
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </>
        )}
      </main>

      {/* Archive confirmation modal */}
      {archiveTarget && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 px-4">
          <div className="bg-white rounded-2xl shadow-xl p-6 w-full max-w-sm">
            <h2 className="text-base font-semibold text-gray-900 mb-1">Archive project?</h2>
            <p className="text-sm text-gray-500 mb-6">
              <span className="font-medium text-gray-700">"{archiveTarget.name}"</span> will be moved to your archived projects.
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setArchiveTarget(null)}
                className="text-sm font-medium px-4 py-2 rounded-lg bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={confirmArchive}
                className="text-sm font-medium px-4 py-2 rounded-lg bg-red-500 text-white hover:bg-red-600 transition-colors"
              >
                Archive
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
