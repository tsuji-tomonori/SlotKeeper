import { fileURLToPath } from "node:url";
import { defineConfig } from "@playwright/test";
const root = fileURLToPath(new URL("../", import.meta.url));
export default defineConfig({
  testDir: ".",
  testMatch: "app.spec.ts",
  timeout: 60000,
  retries: 0,
  workers: 1,
  reporter: [
    ["list"],
    ["json", { outputFile: root + "artifacts/playwright.json" }],
  ],
  outputDir: root + "artifacts/e2e",
  use: {
    baseURL: "http://localhost:4321",
    trace: "off",
    screenshot: "only-on-failure",
  },
  projects: [
    { name: "desktop", use: { viewport: { width: 1280, height: 900 } } },
    { name: "mobile", use: { viewport: { width: 390, height: 844 } } },
  ],
});
