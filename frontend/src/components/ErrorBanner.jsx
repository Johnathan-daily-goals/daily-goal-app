export default function ErrorBanner({ message }) {
  if (!message) return null

  return (
    <div style={{ color: "crimson", marginTop: 8 }}>
      {message}
    </div>
  )
}