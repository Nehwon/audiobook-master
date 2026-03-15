import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	define: {
		// Pour éviter les erreurs de process.env côté client
		global: 'globalThis'
	},
	server: {
		port: 5173,
		host: true,
		proxy: {
			'/api': {
				target: 'http://localhost:8000',
				changeOrigin: true,
				secure: false
			},
			'/ws': {
				target: 'ws://localhost:8000',
				ws: true,
				changeOrigin: true
			}
		}
	},
	build: {
		target: 'es2020'
	},
	optimizeDeps: {
		include: ['date-fns']
	}
});
