import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',  // Bind to all interfaces (accessible via Tailscale)
    port: 5172,
    strictPort: true,
  },
})
