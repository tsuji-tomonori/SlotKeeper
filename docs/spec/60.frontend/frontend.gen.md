# 画面・状態・呼出API

静的Astroページ1枚にReact islandを載せ、画面区画はメニューとURLのreservation引数で切り替える。権限はUI表示に加え、APIの403で最終判定する。

## 画面一覧

| 画面 | 表示権限 | 見出し | 入力 | 操作関数 | 呼出API |
|---|---|---|---|---|---|
| 資源を探す（resources） | 認証済み利用者 | 使いたい資源を選ぶ / この資源を予約 | 日付, 開始, 終了, 利用目的 | book, loadSchedule | GET /resources/{resourceId}/schedule, POST /reservations |
| 自分の予約（mine） | 認証済み利用者 | 自分の予約 | 状態, 日付 | — | — |
| 資源管理（admin） | 管理者 | 資源管理 | 資源名, 種類, 説明 | saveResource | POST /resources, PUT /resources/{resourceId} |
| 予約詳細・履歴（?reservation=ID） | 本人・管理者（APIで判定） | 予約詳細・履歴 | — | cancel | POST /reservations/{reservationId}/cancel |

## 状態変化による取得

| 条件 | 関数 | 呼出API | 再実行の依存 |
|---|---|---|---|
| user | loadResources | GET /resources | user, resourcePages |
| selected && user | loadSchedule | GET /resources/{resourceId}/schedule | selected, day, user |
| user && tab === "mine" | loadMine | GET /reservations | user, tab, filter, mineDay, minePages |
| user && id | loadDetail | GET /reservations/{reservationId} | user |

## 例外表示（業務コード）

| コード | 表示 |
|---|---|
| slot_taken | この時間は予約されました。最新の予約表を確認してください。 |
| stale_version | ほかの操作で更新されました。再読み込みしてから操作してください。 |
| future_reservations_exist | 開始前の予約があるため無効化できません。 |
| already_started | 開始時刻を過ぎた予約は取り消せません。 |
| already_cancelled | すでに取り消された予約です。 |
| resource_inactive | この資源は現在予約できません。 |
| idempotency_input_mismatch | 送信内容が変わっています。新しい予約として送信してください。 |

## 例外表示（HTTP status）

| status | 表示 |
|---|---|
| 401 | ログインの有効期限が切れました。再度ログインしてください。 |
| 403 | この操作を行う権限がありません。 |
| 404 | 対象が見つかりません。 |
| 409 | 競合が発生しました。最新情報を確認してください。 |
| 422 | 入力を確認してください。予約は15分刻み、4時間以内、30日以内、同じ日付内で指定します。 |
| 503 | 一時的に利用できません。時間をおいて同じ内容で再送してください。 |
| 通信失敗 | 入力を保持して再送を案内 |

## 認証情報の保持

- tokenはInMemoryWebStorage（メモリ）
- PKCE stateはsessionStorage
- localStorage不使用

## source別の状態宣言

| source | 状態宣言 | API |
|---|---|---|
| frontend/src/App.tsx | useState, useRef } from "react", useState<PublicConfig>(), useState<UserManager>(), useState<User \| null>(null), useState("resources"), useState<Resource[]>([]), useState<Resource>(), useState(japanDate(new Date(Date.now() + 86400000))), useState<BusySlot[]>([]), useState<Reservation[]>([]), useState<Detail>(), useState(""), useState(""), useState(false), useState("future"), useState(""), useState<(string \| undefined)[]>([<br>    undefined,<br>  ]), useState<string>(), useState<(string \| undefined)[]>([<br>    undefined,<br>  ]), useState<string>(), useState<Resource>(), useState(""), useState("10:00"), useState("11:00") | /resources, /resources/{resourceId}/schedule, /reservations, /reservations/{reservationId}, /reservations, /reservations/{reservationId}/cancel, /resources/{resourceId}, /resources |
| frontend/src/auth.ts | — | — |
| frontend/src/logic.ts | — | — |
| frontend/src/pages/index.astro | — | — |
| frontend/src/style.css | — | — |
