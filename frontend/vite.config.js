import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// GitHub Pages 部署时用 /novel-site/ 子路径
// 本地开发用 /
export default defineConfig({
  plugins: [vue()],
  base: process.env.NODE_ENV === 'production' ? '/novel-site/' : '/',
})