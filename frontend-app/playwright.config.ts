import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  timeout: 30_000,
  expect: { timeout: 8_000 },
  use: {
    baseURL: "http://127.0.0.1:5173",
    trace: "retain-on-failure"
  },
  webServer: {
    command: "npm run dev -- --port 5173",
    url: "http://127.0.0.1:5173",
    reuseExistingServer: process.env.E2E_REAL_STACK === "1" ? false : !process.env.CI,
    env: {
      VITE_API_MODE: process.env.VITE_API_MODE ?? "mock",
      VITE_GATEWAY_BASE_URL: process.env.VITE_GATEWAY_BASE_URL ?? "http://localhost:8005",
      VITE_AUTH_SERVICE_URL: process.env.VITE_AUTH_SERVICE_URL ?? "http://localhost:8000"
    }
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] }
    }
  ]
});
