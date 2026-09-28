import { test, expect, type Page, type TestInfo } from "@playwright/test";
async function stage(page: Page, info: TestInfo, phase: string) {
  const path = info.outputPath(phase + ".png");
  await page.screenshot({ path, fullPage: true });
  await info.attach(phase, { path, contentType: "image/png" });
}
// 公開後smoke testではPagesのURLを直接開く。ローカルは/site/をbase pathへ対応付ける。
const remote = process.env.SLOT_PORTAL_URL;
test.beforeEach(async ({ page }) => {
  if (remote) return;
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
test("階層検索から設計図とDB探索へ移動する [TECH-PORTAL-AC]", async ({
  page,
}, info) => {
  await page.goto(remote ?? "/site/");
  await expect(
    page.getByRole("heading", { name: "設計をたどる。品質を確かめる。" }),
  ).toBeVisible();
  await stage(page, info, "Given");
  await page.getByLabel("設計を検索").fill("create_reservation");
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
  await expect(page.locator("#db-detail")).toContainText("createReservation");
  await page
    .locator(".relation")
    .filter({ hasText: "reservations.resource_id" })
    .click();
  await expect(page.locator(".entity button.selected")).toHaveCount(2);
  await expect(page.locator("#db-detail")).toContainText("物理FKではなく");
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await stage(page, info, "Then");
  await page.goBack();
  await expect(page.locator(".mermaid svg")).toBeVisible();
  await page.goForward();
  await page.reload();
  await expect(
    page.getByRole("heading", { name: "データベース探索" }),
  ).toBeVisible();
});
