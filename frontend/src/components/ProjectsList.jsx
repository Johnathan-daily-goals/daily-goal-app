export default function ProjectsList({
  projects,
  isLoading,
  errorMessage,
  onRefresh,
}) {
  return (
    <div style={{ marginTop: 16 }}>
      <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
        <h2 style={{ margin: 0 }}>Projects</h2>
        <button onClick={onRefresh} disabled={isLoading}>
          {isLoading ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      {errorMessage ? (
        <div style={{ color: "crimson", marginTop: 8 }}>{errorMessage}</div>
      ) : null}

      {isLoading ? <div style={{ marginTop: 8 }}>Loading…</div> : null}

      {!isLoading && projects.length === 0 ? (
        <div style={{ marginTop: 8 }}>No projects yet.</div>
      ) : null}

      {!isLoading && projects.length > 0 ? (
        <ul style={{ marginTop: 8 }}>
          {projects.map((project) => (
            <li key={project.id}>
              <strong>{project.name}</strong>
              {project.description ? ` — ${project.description}` : ""}
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  )
}