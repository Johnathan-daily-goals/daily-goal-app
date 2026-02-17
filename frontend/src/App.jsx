import { useState } from "react"

export default function App() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [accessToken, setAccessToken] = useState(null)
  const [refreshToken, setRefreshToken] = useState(null)
  const [errorMessage, setErrorMessage] = useState("")

  async function handleLogin(event) {
    event.preventDefault()
    setErrorMessage("")

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
  }

  return (
    <div style={{ maxWidth: 420, margin: "48px auto", fontFamily: "system-ui" }}>
      <h1>Daily Goals</h1>

      {!accessToken ? (
        <form onSubmit={handleLogin}>
          <div style={{ display: "grid", gap: 12 }}>
            <input
              placeholder="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <input
              placeholder="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <button type="submit">Login</button>
            {errorMessage ? <div style={{ color: "crimson" }}>{errorMessage}</div> : null}
          </div>
        </form>
      ) : (
        <div style={{ display: "grid", gap: 8 }}>
          <div>✅ Logged in</div>
          <div style={{ wordBreak: "break-all" }}>
            <strong>Access token:</strong> {accessToken}
          </div>
          <div style={{ wordBreak: "break-all" }}>
            <strong>Refresh token:</strong> {refreshToken}
          </div>
        </div>
      )}
    </div>
  )
}