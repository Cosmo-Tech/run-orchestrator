import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: '../csm_orc_api/static',
    emptyOutDir: true,
  },
  server: {
    proxy: {
      '/project': 'http://localhost:8080',
      '/template': 'http://localhost:8080',
    },
  },
})
