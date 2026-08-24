import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'jsdom',
    setupFiles: [],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov'],
      include: ['src/**/*.js'],
      // Barrel re-exports (index.js) and the frozen enum (messageCodes.js)
      // contain no logic of their own, so they are excluded from coverage.
      exclude: ['src/i18n/index.js', 'src/i18n/messageCodes.js'],
      thresholds: {
        lines: 99,
        functions: 100,
        statements: 99,
        branches: 95,
      },
    },
  },
});
