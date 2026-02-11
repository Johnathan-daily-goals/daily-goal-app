import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Retrospective() {
  const [projects, setProjects] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [retros, setRetros] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const [retroDate, setRetroDate] = useState(new Date().toISOString().slice(0, 10));
  const [wentWell, setWentWell] = useState("");
  const [challenges, setChallenges] = useState("");
  const [nextSteps, setNextSteps] = useState("");

  const loadProjects = async () => {
    try {
      setLoading(true);
      const proj = await api.listProjects();
      setProjects(proj);
      if (!selectedId && proj.length > 0) {
        setSelectedId(String(proj[0].id));
      }
      setError("");
    } catch (err) {
      setError(err.message || "Failed to load projects");
    } finally {
      setLoading(false);
    }
  };

  const loadRetros = async (projectId) => {
    if (!projectId) {
      setRetros([]);
      return;
    }
    try {
      const data = await api.listRetros(projectId);
      setRetros(data);
    } catch (err) {
      setError(err.message || "Failed to load retrospectives");
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

  useEffect(() => {
    loadRetros(selectedId);
  }, [selectedId]);

  const handleCreateRetro = async (event) => {
    event.preventDefault();
    if (!selectedId) return;

    try {
      await api.createRetro(selectedId, {
        retro_date: retroDate,
        went_well: wentWell.trim() || null,
        challenges: challenges.trim() || null,
        next_steps: nextSteps.trim() || null
      });
      setWentWell("");
      setChallenges("");
      setNextSteps("");
      loadRetros(selectedId);
    } catch (err) {
      setError(err.message || "Failed to create retrospective");
    }
  };

  return (
    <section className="page">
      <div className="page-header">
        <div>
          <h1>Retrospective</h1>
          <p>Capture lessons while they are fresh.</p>
        </div>
        <div className="inline-form">
          <label className="inline-label">
            Project
            <select
              value={selectedId}
              onChange={(event) => setSelectedId(event.target.value)}
            >
              <option value="">Select a project</option>
              {projects.map((project) => (
                <option key={project.id} value={project.id}>
                  {project.name}
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>

      {loading && <div className="loading">Loading retrospectives...</div>}
      {error && <div className="alert">{error}</div>}

      <div className="grid">
        <div className="card">
          <div className="card-header">
            <h2>New Retrospective</h2>
            <span className="muted">Short and honest.</span>
          </div>
          <form className="form" onSubmit={handleCreateRetro}>
            <label>
              Date
              <input
                type="date"
                value={retroDate}
                onChange={(event) => setRetroDate(event.target.value)}
              />
            </label>
            <label>
              What went well
              <textarea
                rows="3"
                value={wentWell}
                onChange={(event) => setWentWell(event.target.value)}
                placeholder="Momentum, wins, surprises"
              />
            </label>
            <label>
              Challenges
              <textarea
                rows="3"
                value={challenges}
                onChange={(event) => setChallenges(event.target.value)}
                placeholder="Blockers, friction, missing info"
              />
            </label>
            <label>
              Next steps
              <textarea
                rows="3"
                value={nextSteps}
                onChange={(event) => setNextSteps(event.target.value)}
                placeholder="Adjustments for tomorrow"
              />
            </label>
            <button type="submit" disabled={!selectedId}>Save Retro</button>
          </form>
        </div>

        <div className="card">
          <div className="card-header">
            <h2>History</h2>
            <span className="muted">{retros.length} entries</span>
          </div>
          <div className="card-list">
            {retros.length === 0 && (
              <div className="empty">No retrospectives yet.</div>
            )}
            {retros.map((retro) => (
              <div key={retro.id} className="retro-item">
                <div className="retro-date">{retro.retro_date}</div>
                {retro.went_well && (
                  <div>
                    <div className="retro-label">Went well</div>
                    <div className="retro-body">{retro.went_well}</div>
                  </div>
                )}
                {retro.challenges && (
                  <div>
                    <div className="retro-label">Challenges</div>
                    <div className="retro-body">{retro.challenges}</div>
                  </div>
                )}
                {retro.next_steps && (
                  <div>
                    <div className="retro-label">Next steps</div>
                    <div className="retro-body">{retro.next_steps}</div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
