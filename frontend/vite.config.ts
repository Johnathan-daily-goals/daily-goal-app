import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    // Proxy: any request to /auth/*, /projects/*, /health goes to Flask.
    // The browser thinks it's talking to localhost:5173 (same origin),
    // so no CORS preflight is triggered. Vite forwards it to Flask server-side.
    proxy: {
      '/auth': 'http://localhost:5001',
      '/projects': 'http://localhost:5001',
      '/health': 'http://localhost:5001',
    },
  },
})
