import { describe, it, expect } from "vitest";
import { japanDate, japanInput, message } from "../src/logic";
describe("日本時間の入力と次の操作案内", () => {
  it("JSTの10時をUTCの1時として送る", () =>
    expect(japanInput("2026-09-26T10:00")).toBe("2026-09-26T01:00:00.000Z"));
  it("日本時間の日付境界を表示する", () =>
    expect(japanDate(new Date("2026-09-25T16:00:00Z"))).toBe("2026-09-26"));
  it("不正な入力を拒否する", () => expect(() => japanInput("bad")).toThrow());
  for (const status of [0, 401, 403, 404, 409, 422, 503])
    it("応答" + status + "で次の操作を案内する", () =>
      expect(message(status).length).toBeGreaterThan(10),
    );
  for (const code of [
    "slot_taken",
    "stale_version",
    "future_reservations_exist",
    "already_started",
    "already_cancelled",
    "resource_inactive",
    "idempotency_input_mismatch",
  ])
    it(code + "の理由を示す", () =>
      expect(message(409, code)).not.toBe(message(409)),
    );
});
