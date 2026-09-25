import fs from "node:fs";
import { spawnSync } from "node:child_process";
const temp = "artifacts/api-types.ts";
fs.mkdirSync("artifacts", { recursive: true });
const result = spawnSync(
  "npx",
  ["openapi-typescript", "docs/design/generated/openapi.json", "-o", temp],
  { stdio: "inherit" },
);
if (result.status !== 0) process.exit(1);
const format = spawnSync("npx", ["prettier", "--write", temp], {
  stdio: "inherit",
});
if (format.status !== 0) process.exit(1);
if (
  fs.readFileSync(temp, "utf8") !==
  fs.readFileSync("frontend/src/generated/api.ts", "utf8")
)
  throw Error("OpenAPI型にdriftがあります");
