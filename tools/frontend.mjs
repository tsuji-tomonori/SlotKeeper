// OpenAPIからフロント型を生成する。--writeで正本を更新し、既定は差分検査だけを行う。
import fs from "node:fs";
import { spawnSync } from "node:child_process";
import * as prettier from "prettier";
const target = "frontend/src/generated/api.ts";
const result = spawnSync(
  "npx",
  ["openapi-typescript", "docs/design/generated/openapi.json"],
  { encoding: "utf8", stdio: ["ignore", "pipe", "inherit"] },
);
if (result.status !== 0) process.exit(1);
// artifacts/は.gitignore対象でprettierのCLIが整形を省くため、APIで整形する。
const options = (await prettier.resolveConfig(target)) ?? {};
const generated = await prettier.format(result.stdout, {
  ...options,
  filepath: target,
});
if (process.argv.includes("--write")) {
  fs.writeFileSync(target, generated);
} else if (generated !== fs.readFileSync(target, "utf8")) {
  fs.mkdirSync("artifacts", { recursive: true });
  fs.writeFileSync("artifacts/api-types.ts", generated);
  console.error(
    "OpenAPI型にdriftがあります。artifacts/api-types.tsと比較してください。",
  );
  process.exit(1);
}
