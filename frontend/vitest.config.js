import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

// Vitest runs the component tests in a jsdom environment - a headless DOM, no
// real browser needed. Fast and deterministic, which is what CI wants. The
// end-to-end browser checks (Playwright) stay a local/manual tool.
export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.js'],
    css: false,
  },
});
