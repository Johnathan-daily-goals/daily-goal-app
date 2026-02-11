import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api.js";

const statusOptions = [
  { value: "open", label: "Open" },
  { value: "done", label: "Done" },
  { value: "blocked", label: "Blocked" }
];

export default function ProjectView() {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [goals, setGoals] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const [title, setTitle] = useState("");
  const [goalDate, setGoalDate] = useState(new Date().toISOString().slice(0, 10));
  const [status, setStatus] = useState("open");
  const [note, setNote] = useState("");

  const loadData = async () => {
    try {
      setLoading(true);
      const [proj, goalsList] = await Promise.all([
        api.getProject(projectId),
        api.listGoals(projectId)
      ]);
      setProject(proj);
      setGoals(goalsList);
      setError("");
    } catch (err) {
      setError(err.message || "Failed to load project");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [projectId]);

  const handleAddGoal = async (event) => {
    event.preventDefault();
    if (!title.trim()) return;

    try {
      await api.createGoal(projectId, {
        title: title.trim(),
        goal_date: goalDate,
        status,
        note: note.trim() || null
      });
      setTitle("");
      setNote("");
      setStatus("open");
      loadData();
    } catch (err) {
      setError(err.message || "Failed to add goal");
    }
  };

  const handleToggleActive = async () => {
    if (!project) return;
    try {
      await api.updateProject(projectId, { active: !project.active });
      loadData();
    } catch (err) {
      setError(err.message || "Failed to update project");
    }
  };

  return (
    <section className="page">
      {loading && <div className="loading">Loading project...</div>}
      {error && <div className="alert">{error}</div>}

      {project && (
        <>
          <div className="page-header">
            <div>
              <h1>{project.name}</h1>
              <p>Capture goals and keep the timeline visible.</p>
            </div>
            <button className="ghost" onClick={handleToggleActive}>
              {project.active ? "Mark Inactive" : "Mark Active"}
            </button>
          </div>

          <div className="grid">
            <div className="card">
              <div className="card-header">
                <h2>Add Goal</h2>
                <span className="muted">Make it specific.</span>
              </div>
              <form className="form" onSubmit={handleAddGoal}>
                <label>
                  Goal title
                  <input
                    type="text"
                    value={title}
                    onChange={(event) => setTitle(event.target.value)}
                    placeholder="Ship onboarding flow"
                  />
                </label>
                <label>
                  Date
                  <input
                    type="date"
                    value={goalDate}
                    onChange={(event) => setGoalDate(event.target.value)}
                  />
                </label>
                <label>
                  Status
                  <select value={status} onChange={(event) => setStatus(event.target.value)}>
                    {statusOptions.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Note
                  <textarea
                    rows="3"
                    value={note}
                    onChange={(event) => setNote(event.target.value)}
                    placeholder="Constraints, dependencies, or details"
                  />
                </label>
                <button type="submit">Add Goal</button>
              </form>
            </div>

            <div className="card">
              <div className="card-header">
                <h2>Goal History</h2>
                <span className="muted">{goals.length} total</span>
              </div>
              <div className="card-list">
                {goals.length === 0 && (
                  <div className="empty">No goals yet. Add one to start tracking progress.</div>
                )}
                {goals.map((goal) => (
                  <div key={goal.id} className="goal-item">
                    <div>
                      <div className="goal-title">{goal.title}</div>
                      <div className="muted">{goal.goal_date} • {goal.status}</div>
                      {goal.note && <div className="note">{goal.note}</div>}
                    </div>
                    <span className={`pill pill-${goal.status}`}>{goal.status}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </section>
  );
}
