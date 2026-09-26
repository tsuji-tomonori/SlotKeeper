import { test, expect, type Page, type TestInfo } from "@playwright/test";
async function stage(page: Page, info: TestInfo, phase: string) {
  const path = info.outputPath(phase + ".png");
  await page.screenshot({ path, fullPage: true });
  await info.attach(phase, { path, contentType: "image/png" });
}
test("ログインから予約・履歴・取消・ログアウトまで [COM-01-AC] [SLOT-AC01] [SLOT-02-AC] [SLOT-07-AC] [SLOT-AC04]", async ({
  page,
}, info) => {
  await page.goto("/");
  await page.getByRole("button", { name: "ログインして予約する" }).click();
  await page.locator("#username").fill("alice");
  await page.locator("#password").fill("Local-test-2026!");
  await page.locator("#kc-login").click();
  await expect(page.getByRole("button", { name: "自分の予約" })).toBeVisible();
  await stage(page, info, "Given");
  await page.getByRole("button").filter({ hasText: "会議室 青葉" }).click();
  const day = new Date(
    Date.now() + 86400000 * (info.project.name === "desktop" ? 2 : 3),
  )
    .toISOString()
    .slice(0, 10);
  await page.getByLabel("日付", { exact: true }).fill(day);
  await page.getByLabel("利用目的").fill("画面受入 " + info.project.name);
  await page.getByRole("button", { name: "予約を確定する" }).click();
  await expect(
    page.getByRole("heading", { name: "予約詳細・履歴" }),
  ).toBeVisible();
  await stage(page, info, "When");
  await page.getByRole("button", { name: "この予約を取り消す" }).click();
  await expect(page.getByText("予約を取り消しました。")).toBeVisible();
  await expect(page.getByText(/状態：取消済み/)).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await stage(page, info, "Then");
  expect(await page.evaluate(() => Object.keys(localStorage))).toEqual([]);
  await page.getByRole("button", { name: "ログアウト" }).click();
  await expect(
    page.getByRole("button", { name: "ログインして予約する" }),
  ).toBeVisible();
});
test("一般利用者に資源管理を表示しない [COM-01-AC] [COM-04-AC]", async ({
  page,
}, info) => {
  await page.goto("/");
  await page.getByRole("button", { name: "ログインして予約する" }).click();
  await page.locator("#username").fill("bob");
  await page.locator("#password").fill("Local-test-2026!");
  await page.locator("#kc-login").click();
  await expect(page.getByRole("button", { name: "自分の予約" })).toBeVisible();
  await stage(page, info, "Given");
  await page.getByRole("button", { name: "自分の予約" }).click();
  await stage(page, info, "When");
  await expect(
    page.getByRole("button", { name: "資源管理", exact: true }),
  ).toHaveCount(0);
  await stage(page, info, "Then");
});
