import { describe, it, expect } from "vitest";
import { japanDate, japanInput, logoutLocation, message } from "../src/logic";
describe("日本時間の入力と次の操作案内 [COM-08-AC] [RULE-04-AC]", () => {
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
describe("Cognitoのログアウト先 [COM-01-AC]", () => {
  it("logout URLがない設定では推測で遷移しない", () =>
    expect(() =>
      logoutLocation(
        {
          api: "https://api.example.test",
          authority: "https://issuer.example.test",
          clientId: "client",
          authMode: "oidc",
        },
        "https://app.example.test/",
      ),
    ).toThrow());
  it("client_idと戻り先を付けてHosted UIへ送る", () =>
    expect(
      logoutLocation(
        {
          api: "https://api.example.test",
          authority: "https://issuer.example.test",
          clientId: "client",
          authMode: "cognito",
          logoutUrl: "https://login.example.test/logout",
        },
        "https://app.example.test/",
      ),
    ).toBe(
      "https://login.example.test/logout?client_id=client&logout_uri=https%3A%2F%2Fapp.example.test%2F",
    ));
});
