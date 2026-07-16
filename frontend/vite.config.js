import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // The frontend calls /api/* and Vite forwards to the FastAPI backend.
      // This means no CORS config and no hardcoded localhost:8000 in the app -
      // the same code works in dev and behind a reverse proxy in production.
      '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true },
    },
  },
})
