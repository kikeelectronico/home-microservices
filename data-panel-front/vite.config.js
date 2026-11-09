import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [
    react({
      include: /\.(mdx|js|jsx|ts|tsx)$/,
    }),
  ],
  server: {
    host: '0.0.0.0',
  },
  preview: {
    host: '0.0.0.0',
  },
  build: {
    outDir: 'build',
    rolldownOptions: {
      moduleTypes: {
        '.js': 'jsx',
      },
    },
  },
})
