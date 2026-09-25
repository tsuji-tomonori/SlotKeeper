import { test, expect, type Page, type TestInfo } from "@playwright/test";
async function stage(page: Page, info: TestInfo, phase: string) {
  const path = info.outputPath(phase + ".png");
  await page.screenshot({ path, fullPage: true });
  await info.attach(phase, { path, contentType: "image/png" });
}
test.beforeEach(async ({ page }) => {
  await page.route("**/SlotKeeper/**", async (route) => {
    const url = new URL(route.request().url());
    const response = await route.fetch({
      url:
        url.origin +
        url.pathname.replace("/SlotKeeper/", "/site/") +
        url.search,
    });
    await route.fulfill({ response });
  });
});
test("階層検索から設計図とDB探索へ移動する", async ({ page }, info) => {
  await page.goto("/site/");
  await expect(
    page.getByRole("heading", { name: "設計をたどる。品質を確かめる。" }),
  ).toBeVisible();
  await stage(page, info, "Given");
  await page.getByLabel("設計を検索").fill("reservations_create");
  await page
    .locator("#results a")
    .filter({ hasText: "sequence" })
    .first()
    .click();
  await expect(page.locator(".mermaid svg")).toBeVisible();
  await stage(page, info, "When");
  await page.getByRole("button", { name: "図を拡大" }).click();
  await expect(page.locator("dialog")).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.locator("dialog")).not.toBeVisible();
  await page.getByRole("link", { name: "DB探索", exact: true }).click();
  await page.getByLabel("テーブル・列を検索").fill("予約");
  await page.locator('[data-column="reservations.purpose"]').click();
  await expect(page.locator("#db-detail")).toContainText("目的");
  await expect(page.locator("#db-detail")).toContainText("reservations_create");
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await stage(page, info, "Then");
  await page.reload();
  await expect(
    page.getByRole("heading", { name: "データベース探索" }),
  ).toBeVisible();
});
