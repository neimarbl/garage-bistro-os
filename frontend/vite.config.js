import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev
export default defineConfig({
  plugins: [react()],
  server: {
    watch: {
      usePolling: true, // Força o HMR (Hot Module Replacement) a funcionar perfeitamente dentro de volumes Docker no WSL2
    },
  },
})
