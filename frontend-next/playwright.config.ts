import { defineConfig, devices } from '@playwright/test';

const desktopChrome = {
  ...devices['Desktop Chrome'],
  viewport: { width: 1440, height: 1000 },
};

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: false,
  workers: 1,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  timeout: 45_000,
  expect: { timeout: 10_000 },
  reporter: [['list'], ['html', { outputFolder: 'playwright-report', open: 'never' }]],
  use: {
    baseURL: process.env.FIELDNODE_FRONTEND_URL || 'http://localhost:3000',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'on',
    ...desktopChrome,
  },
});
