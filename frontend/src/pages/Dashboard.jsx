import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api.js";

function StatusPill({ status }) {
  const label = status === "done" ? "Done" : status === "blocked" ? "Blocked" : "Open";
  return <span className={`pill pill-${status}`}>{label}</span>;
}

export default function Dashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [projects, setProjects] = useState([]);
  const [error, setError] = useState("");
  const [projectName, setProjectName] = useState("");
  const [loading, setLoading] = useState(true);

  const projectMap = useMemo(() => {
    const map = new Map();
    projects.forEach((project) => map.set(project.id, project));
    return map;
  }, [projects]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [dash, proj] = await Promise.all([
        api.dashboard(),
        api.listProjects()
      ]);
      setDashboard(dash);
      setProjects(proj);
      setError("");
    } catch (err) {
      setError(err.message || "Failed to load dashboard");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateProject = async (event) => {
    event.preventDefault();
    if (!projectName.trim()) return;

    try {
      await api.createProject({ name: projectName.trim(), active: true });
      setProjectName("");
      loadData();
    } catch (err) {
      setError(err.message || "Failed to create project");
    }
  };

  return (
    <section className="page">
      <div className="page-header">
        <div>
          <h1>Dashboard</h1>
          <p>Track today, steer tomorrow, keep the streak alive.</p>
        </div>
        <form className="inline-form" onSubmit={handleCreateProject}>
          <input
            type="text"
            placeholder="New project name"
            value={projectName}
            onChange={(event) => setProjectName(event.target.value)}
          />
          <button type="submit">Add Project</button>
        </form>
      </div>

      {error && <div className="alert">{error}</div>}
      {loading && <div className="loading">Loading dashboard...</div>}

      {dashboard && (
        <div className="grid">
          <div className="card">
            <div className="card-header">
              <h2>Active Projects</h2>
              <span className="muted">{dashboard.active_projects.length} active</span>
            </div>
            <div className="card-list">
              {dashboard.active_projects.length === 0 && (
                <div className="empty">Create your first project to begin.</div>
              )}
              {dashboard.active_projects.map((project) => (
                <Link key={project.id} to={`/projects/${project.id}`} className="project-item">
                  <div>
                    <div className="project-name">{project.name}</div>
                    <div className="muted">Started {new Date(project.created_at).toLocaleDateString()}</div>
                  </div>
                  <span className="chip">View</span>
                </Link>
              ))}
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h2>Today’s Goals</h2>
              <span className="muted">{dashboard.today}</span>
            </div>
            <div className="card-list">
              {dashboard.todays_goals.length === 0 && (
                <div className="empty">No goals set for today yet.</div>
              )}
              {dashboard.todays_goals.map((goal) => {
                const project = projectMap.get(goal.project_id);
                return (
                  <div key={goal.id} className="goal-item">
                    <div>
                      <div className="goal-title">{goal.title}</div>
                      <div className="muted">
                        {project ? project.name : "Project"} • {goal.goal_date}
                      </div>
                    </div>
                    <StatusPill status={goal.status} />
                  </div>
                );
              })}
            </div>
          </div>

          <div className="card highlight">
            <h2>Today’s Focus</h2>
            <p>
              Pick one project and commit to the smallest meaningful step. Consistency beats intensity.
            </p>
            <ul className="list">
              <li>Clarify the next deliverable.</li>
              <li>Protect a 45-minute deep work block.</li>
              <li>Write a quick retrospective before you stop.</li>
            </ul>
          </div>
        </div>
      )}
    </section>
  );
}
