import { fileURLToPath } from "node:url";
import { defineConfig } from "@playwright/test";
const root = fileURLToPath(new URL("../", import.meta.url));
// GitHub Pagesへ公開した後に、実URLのbase path・図・検索・DB探索を確認する。
const url = process.env.SLOT_PORTAL_URL;
if (!url) throw new Error("SLOT_PORTAL_URLが必要です");
export default defineConfig({
  testDir: ".",
  testMatch: "portal.spec.ts",
  timeout: 60000,
  retries: 0,
  workers: 1,
  reporter: [
    ["list"],
    ["json", { outputFile: root + "artifacts/portal-smoke.json" }],
  ],
  outputDir: root + "artifacts/portal-smoke",
  use: { baseURL: url, trace: "off" },
  projects: [
    { name: "desktop", use: { viewport: { width: 1280, height: 900 } } },
    { name: "mobile", use: { viewport: { width: 390, height: 844 } } },
  ],
});
