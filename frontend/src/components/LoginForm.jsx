export default function LoginForm({
  email,
  password,
  onEmailChange,
  onPasswordChange,
  onSubmit,
  isLoading = false,
}) {
  return (
    <form onSubmit={onSubmit}>
      <div style={{ display: "flex", flexDirection: "column", gap: 8, maxWidth: 320 }}>
        <input
          placeholder="email"
          value={email}
          onChange={(event) => onEmailChange(event.target.value)}
        />

        <input
          placeholder="password"
          type="password"
          value={password}
          onChange={(event) => onPasswordChange(event.target.value)}
        />

        <button type="submit" disabled={isLoading}>
          {isLoading ? "Logging in..." : "Login"}
        </button>
      </div>
    </form>
  )
}