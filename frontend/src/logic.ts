import type { PublicConfig } from "./auth";
export function japanInput(value: string): string {
  if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/.test(value))
    throw new Error("日時を入力してください");
  return new Date(value + ":00+09:00").toISOString();
}
export function japanDate(value: Date): string {
  return new Intl.DateTimeFormat("sv-SE", { timeZone: "Asia/Tokyo" }).format(
    value,
  );
}
export function message(status: number, code?: string): string {
  const codes: Record<string, string> = {
    slot_taken: "この時間は予約されました。最新の予約表を確認してください。",
    stale_version:
      "ほかの操作で更新されました。再読み込みしてから操作してください。",
    future_reservations_exist: "開始前の予約があるため無効化できません。",
    already_started: "開始時刻を過ぎた予約は取り消せません。",
    already_cancelled: "すでに取り消された予約です。",
    resource_inactive: "この資源は現在予約できません。",
    idempotency_input_mismatch:
      "送信内容が変わっています。新しい予約として送信してください。",
  };
  return (
    codes[code ?? ""] ??
    {
      401: "ログインの有効期限が切れました。再度ログインしてください。",
      403: "この操作を行う権限がありません。",
      404: "対象が見つかりません。",
      409: "競合が発生しました。最新情報を確認してください。",
      422: "入力を確認してください。予約は15分刻み、4時間以内、30日以内、同じ日付内で指定します。",
      503: "一時的に利用できません。時間をおいて同じ内容で再送してください。",
    }[status] ??
    "通信に失敗しました。入力は保持されています。もう一度お試しください。"
  );
}
export function logoutLocation(config: PublicConfig, returnTo: string) {
  const url = new URL(config.logoutUrl ?? "");
  url.searchParams.set("client_id", config.clientId);
  url.searchParams.set("logout_uri", returnTo);
  return url.toString();
}
