export default function LoggedInPanel({
  email,
  accessToken,
  refreshToken,
  onLogout,
  isLoading = false,
}) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      <div>✅ Logged in as <strong>{email}</strong></div>

      <div>
        <strong>Access token:</strong>{" "}
        <code style={{ wordBreak: "break-all" }}>{accessToken}</code>
      </div>

      <div>
        <strong>Refresh token:</strong>{" "}
        <code style={{ wordBreak: "break-all" }}>{refreshToken}</code>
      </div>

      <button onClick={onLogout} disabled={isLoading}>
        {isLoading ? "Logging out..." : "Logout"}
      </button>
    </div>
  )
}