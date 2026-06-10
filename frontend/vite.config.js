import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// lyriq.space 根域名部署，base 设为 /
export default defineConfig({
  plugins: [vue()],
  base: '/',
})