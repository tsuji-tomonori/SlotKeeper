import { fileURLToPath } from "node:url";
import { defineConfig } from "@playwright/test";
const root = fileURLToPath(new URL("../", import.meta.url));
export default defineConfig({
  testDir: ".",
  testMatch: "portal.spec.ts",
  timeout: 60000,
  retries: 0,
  workers: 1,
  reporter: [
    ["list"],
    ["json", { outputFile: root + "artifacts/portal.json" }],
  ],
  outputDir: root + "artifacts/portal-tests",
  webServer: {
    cwd: root,
    command: "python -m http.server 4173 --directory artifacts",
    url: "http://localhost:4173/site/",
    reuseExistingServer: false,
  },
  use: { baseURL: "http://localhost:4173/site/", trace: "off" },
  projects: [
    { name: "desktop", use: { viewport: { width: 1280, height: 900 } } },
    { name: "mobile", use: { viewport: { width: 390, height: 844 } } },
  ],
});
