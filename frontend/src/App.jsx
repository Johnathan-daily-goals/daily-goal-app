import { useState } from "react"
import LoginForm from "./components/LoginForm"
import LoggedInPanel from "./components/LoggedInPanel"
import ErrorBanner from "./components/ErrorBanner"
import ProjectsList from "./components/ProjectsList"
import CreateProjectForm from "./components/CreateProjectForm"

export default function App() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")

  const [accessToken, setAccessToken] = useState(null)
  const [refreshToken, setRefreshToken] = useState(null)

  const [errorMessage, setErrorMessage] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const [projects, setProjects] = useState([])
  const [projectsErrorMessage, setProjectsErrorMessage] = useState("")
  const [isProjectsLoading, setIsProjectsLoading] = useState(false)

  async function handleLogin(event) {
    event.preventDefault()
    setErrorMessage("")
    setIsLoading(true)

    try {
      const response = await fetch("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      })

      const body = await response.json().catch(() => ({}))

      if (!response.ok) {
        setErrorMessage(body?.error || "Login failed")
        return
      }

      setAccessToken(body.access_token)
      setRefreshToken(body.refresh_token)

      await fetchProjects(body.access_token)
    } finally {
      setIsLoading(false)
    }
  }

  async function handleLogout() {
    setErrorMessage("")
    setIsLoading(true)

    try {
      // logout needs refresh_token; access token is optional but we send it anyway
      const response = await fetch("/auth/logout", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      })

      const body = await response.json().catch(() => ({}))

      if (!response.ok) {
        setErrorMessage(body?.error || "Logout failed")
        return
      }

      // clear local state
      setAccessToken(null)
      setRefreshToken(null)
      setPassword("")
      setProjects([])
      setProjectsErrorMessage("")
    } finally {
      setIsLoading(false)
    }
  }

    async function fetchProjects(accessTokenValue) {
    setProjectsErrorMessage("")
    setIsProjectsLoading(true)

    try {
      const response = await fetch("/projects", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${accessTokenValue}`,
        },
      })

      const body = await response.json().catch(() => ([]))

      if (!response.ok) {
        setProjectsErrorMessage(body?.error || "Failed to load projects")
        return
      }

      setProjects(Array.isArray(body) ? body : [])
    } finally {
      setIsProjectsLoading(false)
    }
  }

  const isLoggedIn = Boolean(accessToken)

  return (
    <div style={{ padding: 24 }}>
      <h1>Daily Goals</h1>


      {!isLoggedIn ? (
        <>
        <LoginForm
          email={email}
          password={password}
          onEmailChange={setEmail}
          onPasswordChange={setPassword}
          onSubmit={handleLogin}
          isLoading={isLoading}
        />
        <ErrorBanner message={errorMessage} />
        </>

            ) : (
        <>
          <LoggedInPanel
            email={email}
            accessToken={accessToken}
            refreshToken={refreshToken}
            onLogout={handleLogout}
            isLoading={isLoading}
          />
          <CreateProjectForm
            accessToken={accessToken}
            onCreated={() => fetchProjects(accessToken)}
          />

          <ProjectsList
            projects={projects}
            isLoading={isProjectsLoading}
            errorMessage={projectsErrorMessage}
            onRefresh={() => fetchProjects(accessToken)}
          />
        </>
      )}
    </div>
  )
}