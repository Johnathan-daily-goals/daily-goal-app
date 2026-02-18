import { useState } from "react"

export default function CreateProjectForm({ accessToken, onCreated }) {
  const [projectName, setProjectName] = useState("")
  const [projectDescription, setProjectDescription] = useState("")
  const [errorMessage, setErrorMessage] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setErrorMessage("")

    const trimmedName = projectName.trim()
    if (!trimmedName) {
      setErrorMessage("Project name is required")
      return
    }

    setIsSubmitting(true)
    try {
      const response = await fetch("/projects", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({
          name: trimmedName,
          description: projectDescription.trim() || null,
        }),
      })

      const body = await response.json().catch(() => ({}))

      if (!response.ok) {
        setErrorMessage(body?.error || "Failed to create project")
        return
      }

      setProjectName("")
      setProjectDescription("")
      onCreated()
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div style={{ marginTop: 16 }}>
      <h2 style={{ margin: 0 }}>Create project</h2>

      <form onSubmit={handleSubmit} style={{ marginTop: 8 }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 8, maxWidth: 420 }}>
          <label>
            Name *
            <input
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="e.g. Gym"
              style={{ width: "100%" }}
            />
          </label>

          <label>
            Description
            <input
              value={projectDescription}
              onChange={(e) => setProjectDescription(e.target.value)}
              placeholder="Optional"
              style={{ width: "100%" }}
            />
          </label>

          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Creating..." : "Create"}
          </button>

          {errorMessage ? <div style={{ color: "crimson" }}>{errorMessage}</div> : null}
        </div>
      </form>
    </div>
  )
}