import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173, // specify default port
    host: true, // listen on all addresses
    strictPort: true, // fail if port is already in use
    allowedHosts: [
      'directed-codeanalyzer.onrender.com',
      'localhost',
      '127.0.0.1'
    ]
  }
})
