// 永続要件の一次言語。product固有の要件を追加し、JSONとMarkdownをここから生成する。
module requirements {
  type AcceptanceCriterion = { id: str, given: str, when_: str, expected: str }
  type Verification = { method: str, evidence: str }
  type Traces = {
    design: List[str],
    implementation: List[str],
    tests: List[str],
    standards: List[str],
  }
  type Requirement = {
    id: str,
    revision: int,
    status: str,
    kind: str,
    title: str,
    subject: str,
    actionName: str,
    objectName: str,
    rationale: str,
    sourceRefs: List[str],
    acceptanceCriteria: List[AcceptanceCriterion],
    verification: Verification,
    traces: Traces,
    lastChangedBy: str,
    retirementReason: str,
    supersededBy: str,
    scopeName: str,
    categoryName: str,
  }
  type Catalog = {
    schemaVersion: int,
    catalogRevision: int,
    product: str,
    updatedAt: str,
    requirements: List[Requirement],
  }
  type RequirementOperation = {
    kind: str,
    id: str,
    expectedRevision: int,
    replacement: Requirement,
  }
  type BatchFold = {
    requirements: List[Requirement],
    touchedIds: List[str],
    valid: bool,
  }
  type Lifecycle = {
    catalogRevision: int,
    itemRevision: int,
    itemPresent: bool,
    itemStatus: str,
    traceRevision: int,
    priorCatalogRevision: int,
    priorItemRevision: int,
    priorItemPresent: bool,
    priorItemStatus: str,
    priorTraceRevision: int,
    lastOperation: str,
  }

  pure val requirementsSource: Catalog = { schemaVersion: 1, catalogRevision: 2, product: "SlotKeeper", updatedAt: "2026-09-26", requirements: [{ id: "COM-01", revision: 2, status: "active", kind: "functional", title: "幅390pxと1280pxで主要操作ができ、ラベル、入力エラー、キーボード操作、可視フォーカスを備える。ページ全体に不要な横スクロールを出さない", subject: "SlotKeeper", actionName: "provide", objectName: "幅390pxと1280pxで主要操作ができ、ラベル、入力エラー、キーボード操作、可視フォーカスを備える。ページ全体に不要な横スクロールを出さない", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "COM-01-AC", given: "一般利用者が390pxと1280pxの画面でログインしている", when_: "資源選択・予約作成・詳細・取消・ログアウトをキーボード操作可能な部品で行う", expected: "各操作が完了し、ページ全体の横スクロール幅が表示幅以下で、localStorageにtokenを残さない" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/FRONTEND.md"], implementation: ["frontend/src/App.tsx", "frontend/src/style.css", "frontend/src/logic.ts"], tests: ["e2e/app.spec.ts", "frontend/tests/logic.test.ts"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "functional" }, { id: "COM-02", revision: 2, status: "active", kind: "functional", title: "確定済みのデータは再起動後も残る。失敗操作で部分更新を残さない", subject: "SlotKeeper", actionName: "provide", objectName: "確定済みのデータは再起動後も残る。失敗操作で部分更新を残さない", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "COM-02-AC", given: "確定済み予約と途中で失敗する作成要求がある", when_: "migration・seedの再実行と履歴保存中の障害を起こす", expected: "確定データは保持され、失敗した要求は予約・履歴・要求キーを残さない" }, { id: "SLOT-AC16", given: "確定データと開発用seedがある", when_: "起動・seed・アプリ再起動を繰り返す", expected: "確定データを保持し、seedの無条件重複や開発データ消去を起こさない" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/DATA.md"], implementation: ["backend/src/slotkeeper/db.py", "tools/project/migrate.py"], tests: ["backend/tests/test_reservations.py"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "functional" }, { id: "COM-03", revision: 2, status: "active", kind: "functional", title: "入力をサーバー側でも検証する。入力不正は422を基本とし、未認証401、権限不足403、対象なし404、業務・版競合409を区別する", subject: "SlotKeeper", actionName: "provide", objectName: "入力をサーバー側でも検証する。入力不正は422を基本とし、未認証401、権限不足403、対象なし404、業務・版競合409を区別する", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "COM-03-AC", given: "不正入力・未認証・権限不足・存在しない対象・業務競合の要求がある", when_: "各APIを呼び出す", expected: "それぞれ422・401・403・404・409を返し、入力値を応答へ反射しない" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/api/index.md"], implementation: ["backend/src/slotkeeper/app.py", "backend/src/slotkeeper/domain.py"], tests: ["backend/tests/test_domain.py", "backend/tests/test_auth.py", "backend/tests/test_reservations.py", "backend/tests/test_operations.py"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "functional" }, { id: "COM-04", revision: 2, status: "active", kind: "functional", title: "サーバー側で本人と権限を判定する。UIの表示制御だけで権限を守らない", subject: "SlotKeeper", actionName: "provide", objectName: "サーバー側で本人と権限を判定する。UIの表示制御だけで権限を守らない", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "COM-04-AC", given: "一般利用者のtokenと任意の権限ヘッダーがある", when_: "管理API・他人の予約の詳細と取消を呼び出す", expected: "サーバー側で403とし、UI表示に依存せず拒否する" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/api/index.md"], implementation: ["backend/src/slotkeeper/auth.py", "backend/src/slotkeeper/domain.py"], tests: ["backend/tests/test_auth.py", "backend/tests/test_reservations.py", "e2e/app.spec.ts"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "functional" }, { id: "COM-05", revision: 2, status: "active", kind: "functional", title: "起動・seed・リセット・全検証をCompose経由で再現できる。seedの乱数と評価用時刻を固定できる", subject: "SlotKeeper", actionName: "provide", objectName: "起動・seed・リセット・全検証をCompose経由で再現できる。seedの乱数と評価用時刻を固定できる", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "COM-05-AC", given: "Git checkoutとDocker Composeだけがある", when_: "起動・seed・全検証のCompose commandを繰り返す", expected: "依存の準備から検証まで完了し、seedは固定IDで重複しない" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/OPERATIONS.md"], implementation: ["compose.yaml", "tools/project/migrate.py", "tools/project/verify.py"], tests: ["backend/tests/test_reservations.py"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "functional" }, { id: "COM-06", revision: 2, status: "active", kind: "functional", title: "資源編集・予約取消等の同時更新で変更を消失させない。古い版は409とし再取得を案内する", subject: "SlotKeeper", actionName: "provide", objectName: "資源編集・予約取消等の同時更新で変更を消失させない。古い版は409とし再取得を案内する", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "SLOT-AC11", given: "資源または予約が他の操作で先に更新されている", when_: "古い版で資源編集・予約取消を送る", expected: "409を返し、先に確定した値と履歴を失わない" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/api/resources/resources_update/index.md", "docs/design/generated/api/reservations/reservations_cancel/index.md"], implementation: ["backend/src/slotkeeper/operations/resources_update/endpoint.py", "backend/src/slotkeeper/operations/reservations_cancel/endpoint.py"], tests: ["backend/tests/test_reservations.py"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "functional" }, { id: "COM-07", revision: 2, status: "active", kind: "functional", title: "要求ID、操作、結果、所要時間を構造化ログに残す。認証情報・予約目的・生の例外本文を無条件に記録しない", subject: "SlotKeeper", actionName: "provide", objectName: "要求ID、操作、結果、所要時間を構造化ログに残す。認証情報・予約目的・生の例外本文を無条件に記録しない", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "COM-07-AC", given: "予約目的とBearer tokenを含む要求がある", when_: "APIを呼び出す", expected: "要求ID・operation・status・所要時間を構造化ログに残し、目的とtokenを記録しない" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/api/reservations/reservations_create/messages.md"], implementation: ["backend/src/slotkeeper/app.py"], tests: ["backend/tests/test_operations.py"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "functional" }, { id: "COM-08", revision: 2, status: "active", kind: "functional", title: "空、読込み中、入力不正、通信失敗、権限不足、競合、成功をUIで区別し、利用者が次の操作を判断できる", subject: "SlotKeeper", actionName: "provide", objectName: "空、読込み中、入力不正、通信失敗、権限不足、競合、成功をUIで区別し、利用者が次の操作を判断できる", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "COM-08-AC", given: "通信失敗・401・403・404・409・422・503と業務コードがある", when_: "画面の案内文を求める", expected: "状態ごとに異なり次の操作を判断できる日本語の案内を返す" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/FRONTEND.md"], implementation: ["frontend/src/logic.ts", "frontend/src/App.tsx"], tests: ["frontend/tests/logic.test.ts"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "functional" }, { id: "SLOT-01", revision: 2, status: "active", kind: "functional", title: "管理者が資源を登録・編集・無効化できる。無効資源への新規予約は禁止する", subject: "SlotKeeper", actionName: "provide", objectName: "管理者が資源を登録・編集・無効化できる。無効資源への新規予約は禁止する", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "SLOT-01-AC", given: "管理者と一般利用者がいる", when_: "資源の登録・編集・無効化と一覧取得を行う", expected: "管理者だけが変更でき、一覧は名前とIDの固定順でページングされる" }, { id: "SLOT-AC05", given: "無効資源と将来予約のある有効資源がある", when_: "無効資源への予約と、将来予約のある資源の無効化を行う", expected: "両方409で拒否し、データは変化しない" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/api/resources/index.md"], implementation: ["backend/src/slotkeeper/operations/resources_create/endpoint.py", "backend/src/slotkeeper/operations/resources_update/endpoint.py", "backend/src/slotkeeper/operations/resources_list/endpoint.py"], tests: ["backend/tests/test_auth.py", "backend/tests/test_reservations.py"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "functional" }, { id: "SLOT-02", revision: 2, status: "active", kind: "functional", title: "資源と日付を指定して、その日の予約済み時間帯を確認できる", subject: "SlotKeeper", actionName: "provide", objectName: "資源と日付を指定して、その日の予約済み時間帯を確認できる", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "SLOT-02-AC", given: "資源に確定予約と取消済み予約がある", when_: "一般利用者が資源と日付で予約表を取得する", expected: "確定済みの時間帯と「予約済み」だけを返し、他人の目的と識別情報を返さない" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/api/resources/schedule/index.md"], implementation: ["backend/src/slotkeeper/operations/schedule/endpoint.py"], tests: ["backend/tests/test_reservations.py", "e2e/app.spec.ts"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "functional" }, { id: "SLOT-03", revision: 2, status: "active", kind: "functional", title: "資源、開始・終了、目的を指定して、自分名義の予約を作成できる", subject: "SlotKeeper", actionName: "provide", objectName: "資源、開始・終了、目的を指定して、自分名義の予約を作成できる", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "SLOT-AC01", given: "空き資源がある", when_: "翌日10:00〜11:00を予約する", expected: "1件確定し、予約表と自分の一覧へ反映する" }, { id: "SLOT-AC06", given: "過去・現在と同時刻・0分・4時間超・30日超・15分未満の刻み・日跨ぎの入力がある", when_: "予約時刻を検証する", expected: "入力エラーとし、15分・4時間・30日以内の境界は受け付ける" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/api/reservations/reservations_create/index.md"], implementation: ["backend/src/slotkeeper/operations/reservations_create/endpoint.py", "backend/src/slotkeeper/domain.py"], tests: ["backend/tests/test_reservations.py", "backend/tests/test_domain.py", "e2e/app.spec.ts"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "functional" }, { id: "SLOT-04", revision: 2, status: "active", kind: "functional", title: "同一資源の予約済み時間と重なる予約の確定を拒否する", subject: "SlotKeeper", actionName: "provide", objectName: "同一資源の予約済み時間と重なる予約の確定を拒否する", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "SLOT-AC02", given: "既存の10:00〜11:00予約がある", when_: "10:30〜11:30と11:00〜12:00を予約する", expected: "前者409、後者成功" }, { id: "SLOT-AC03", given: "空き枠に20人がいる", when_: "直列化せず同時に予約する", expected: "1件成功・19件409で重複0件" }, { id: "SLOT-AC10", given: "有効資源がある", when_: "予約作成と資源無効化を同時実行する", expected: "無効化と将来予約が両方確定する結果は0件" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/api/reservations/reservations_create/sequence.md", "docs/design/generated/DATA.md"], implementation: ["backend/src/slotkeeper/operations/reservations_create/endpoint.py", "backend/src/slotkeeper/operations/reservations_create/sql/control.sql", "backend/src/slotkeeper/db.py"], tests: ["backend/tests/test_reservations.py", "backend/tests/test_operations.py"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "functional" }, { id: "SLOT-05", revision: 2, status: "active", kind: "functional", title: "本人または管理者が、開始前の予約を取消できる", subject: "SlotKeeper", actionName: "provide", objectName: "本人または管理者が、開始前の予約を取消できる", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "SLOT-AC04", given: "利用者Aの開始前予約がある", when_: "B・A・管理者が取消を試みる", expected: "Bは403、本人と管理者は取消でき、取消履歴が追加される" }, { id: "SLOT-AC13", given: "開始時刻ちょうどの予約と取消済み予約がある", when_: "取消する", expected: "409で拒否し、履歴を増やさない" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/api/reservations/reservations_cancel/index.md"], implementation: ["backend/src/slotkeeper/operations/reservations_cancel/endpoint.py"], tests: ["backend/tests/test_reservations.py", "e2e/app.spec.ts"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "functional" }, { id: "SLOT-06", revision: 2, status: "active", kind: "functional", title: "自分の予約を日付・状態で絞り込める", subject: "SlotKeeper", actionName: "provide", objectName: "自分の予約を日付・状態で絞り込める", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "SLOT-AC08", given: "自分と他人の予約が複数日・複数状態にある", when_: "日付・状態で絞込み、他人の詳細を取得する", expected: "自分の対象だけを返し、他人の目的・履歴は403で漏れない" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/api/reservations/reservations_list/index.md"], implementation: ["backend/src/slotkeeper/operations/reservations_list/endpoint.py"], tests: ["backend/tests/test_reservations.py"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "functional" }, { id: "SLOT-07", revision: 2, status: "active", kind: "functional", title: "作成・取消の履歴を残し、権限のある利用者が詳細画面から確認できる", subject: "SlotKeeper", actionName: "provide", objectName: "作成・取消の履歴を残し、権限のある利用者が詳細画面から確認できる", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "SLOT-07-AC", given: "作成後に取消した予約がある", when_: "本人・管理者・他人が詳細画面で履歴を取得する", expected: "本人と管理者は作成・取消の順の履歴を閲覧でき、他人は403" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/api/reservations/reservations_get/index.md"], implementation: ["backend/src/slotkeeper/operations/reservations_get/endpoint.py"], tests: ["backend/tests/test_reservations.py", "e2e/app.spec.ts"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "functional" }, { id: "SLOT-08", revision: 2, status: "active", kind: "functional", title: "要求の再送を識別し、予約と履歴を二重に作らない", subject: "SlotKeeper", actionName: "provide", objectName: "要求の再送を識別し、予約と履歴を二重に作らない", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "SLOT-AC07", given: "成功応答を失った作成要求がある", when_: "同じキーで再送（同時再送を含む）する", expected: "元の予約IDと応答を返し、予約・作成履歴は各1件" }, { id: "SLOT-AC09", given: "同じ要求キーの成功記録がある", when_: "異なる入力を送る", expected: "409で元の予約を変更しない" }, { id: "SLOT-AC12", given: "予約保存後の履歴保存で障害が起きる", when_: "作成し、その後同じキーで再送する", expected: "部分保存を残さず、再送で1件だけ作成する" }, { id: "SLOT-AC15", given: "作成済みキーの経過が24時間前後で、予約は取消・開始済みである", when_: "同じキーで再送する", expected: "有効期間内は元の作成結果、期限後は新規要求の規則に従う" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/api/reservations/reservations_create/sequence.md"], implementation: ["backend/src/slotkeeper/operations/reservations_create/endpoint.py", "backend/src/slotkeeper/operations/reservations_create/sql/replay.sql", "backend/src/slotkeeper/operations/reservations_create/sql/record.sql"], tests: ["backend/tests/test_reservations.py", "backend/tests/test_domain.py", "backend/tests/test_operations.py"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "functional" }, { id: "TECH-STACK", revision: 2, status: "active", kind: "constraint", title: "Astro静的フロントとFastAPIを使用する", subject: "SlotKeeper", actionName: "provide", objectName: "Astro静的フロントとFastAPIを使用する", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "TECH-STACK-AC", given: "Astro画面・FastAPI・PostgreSQLを起動している", when_: "静的buildとOpenAPI型生成を検査する", expected: "静的成果物がbuildでき、フロント型がOpenAPIとdriftしない" }], verification: { method: "check", evidence: "verify:astro, verify:frontend-build, verify:openapi-types" }, traces: { design: ["docs/design/generated/OVERVIEW.md"], implementation: ["frontend/astro.config.mjs", "backend/src/slotkeeper/app.py", "tools/frontend.mjs"], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "project", categoryName: "nonfunctional" }, { id: "TECH-DB", revision: 2, status: "active", kind: "constraint", title: "DSQLとPostgreSQLで共通の予約不変条件を守る", subject: "SlotKeeper", actionName: "provide", objectName: "DSQLとPostgreSQLで共通の予約不変条件を守る", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "TECH-DB-AC", given: "ローカルPostgreSQLの検証DBがある", when_: "接続の分離レベルと共通SQLの型を検査する", expected: "Repeatable Readで接続し、SQL正本の束縛引数と結果型が一致する" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/DATA.md"], implementation: ["backend/src/slotkeeper/db.py", "tools/project/queries.py", "tools/project/migrate.py"], tests: ["backend/tests/test_reservations.py", "backend/tests/test_operations.py"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "project", categoryName: "nonfunctional" }, { id: "TECH-AUTH", revision: 2, status: "active", kind: "constraint", title: "署名、issuer、client、用途、期限を検査する", subject: "SlotKeeper", actionName: "provide", objectName: "署名、issuer、client、用途、期限を検査する", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "SLOT-AC14", given: "不正署名・期限切れ・異なるissuer/client・role改ざん・ID tokenがある", when_: "業務APIを呼び出す", expected: "401/403で拒否し、DBは変化しない" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/api/index.md"], implementation: ["backend/src/slotkeeper/auth.py", "frontend/src/auth.ts"], tests: ["backend/tests/test_auth.py", "backend/tests/test_reservations.py", "backend/tests/test_operations.py"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "project", categoryName: "nonfunctional" }, { id: "TECH-LAMBDA", revision: 2, status: "active", kind: "constraint", title: "依存を含むLinux用Lambda ZIPを作成する", subject: "SlotKeeper", actionName: "provide", objectName: "依存を含むLinux用Lambda ZIPを作成する", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "TECH-LAMBDA-AC", given: "Compose内でLinux向けに作った配布ZIPがある", when_: "隔離pathからimportし、API Gatewayイベントを変換する", expected: "handlerを読み込み、healthは200・未認証の業務APIは401" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/INFRA.md"], implementation: ["tools/project/package_lambda.py", "backend/src/slotkeeper/app.py"], tests: ["backend/tests/test_lambda.py"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "project", categoryName: "nonfunctional" }, { id: "TECH-INFRA", revision: 2, status: "active", kind: "constraint", title: "Python CDKで常設サーバーを持たない構成を合成する", subject: "SlotKeeper", actionName: "provide", objectName: "Python CDKで常設サーバーを持たない構成を合成する", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "TECH-INFRA-AC", given: "AWS認証情報のない環境で環境contextを指定する", when_: "CDKをsynthしassertionとcdk-nagで検査する", expected: "非公開S3+OAC、JWT保護route、限定IAM、ログ保持、削除保護、環境別のCORSとcallbackを満たし、常設サーバーを持たない" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/INFRA.md"], implementation: ["infra/stack.py", "infra/app.py"], tests: ["infra/tests/test_stack.py"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "project", categoryName: "nonfunctional" }, { id: "TECH-COMPOSE", revision: 2, status: "active", kind: "constraint", title: "GitとDocker Composeだけで起動と全検証を行える", subject: "SlotKeeper", actionName: "provide", objectName: "GitとDocker Composeだけで起動と全検証を行える", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "TECH-COMPOSE-AC", given: "ホストにGitとDocker Composeだけがある", when_: "verifyを1コマンドで実行する", expected: "依存serviceの準備から結果収集とポータル生成まで行い、失敗時は非0で終了する" }], verification: { method: "check", evidence: "verify:package, verify:backend, verify:e2e, verify:portal-build" }, traces: { design: ["docs/OPERATIONS.md"], implementation: ["compose.yaml", "Dockerfile", "tools/project/verify.py"], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "project", categoryName: "nonfunctional" }, { id: "TECH-DESIGN", revision: 2, status: "active", kind: "constraint", title: "実装から6帳票、DB、CRUD、画面、infraを決定的に生成する", subject: "SlotKeeper", actionName: "provide", objectName: "実装から6帳票、DB、CRUD、画面、infraを決定的に生成する", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "TECH-DESIGN-AC", given: "実装source・SQL・CDKがある", when_: "設計を2回クリーン生成し、既存生成物と比較する", expected: "byte一致し、欠落・変更・余剰・未対応構文・要件traceの欠落を非0で報告する" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/report.json"], implementation: ["tools/project/design.py", ".dev-standard/design.json"], tests: ["tools/tests/test_guards.py"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "project", categoryName: "nonfunctional" }, { id: "TECH-PORTAL", revision: 2, status: "active", kind: "constraint", title: "同一revisionとrunの実測結果と設計をPagesへ集約する", subject: "SlotKeeper", actionName: "provide", objectName: "同一revisionとrunの実測結果と設計をPagesへ集約する", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "TECH-PORTAL-AC", given: "同一revision・runの検査結果と生成設計がある", when_: "ポータルをbuildしブラウザで検証する", expected: "階層・検索・図の拡大・DB探索・深いリンク・390px表示が動作する" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/OVERVIEW.md"], implementation: ["tools/project/evidence.py", "portal/src/layouts/Layout.astro"], tests: ["e2e/portal.spec.ts"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "project", categoryName: "nonfunctional" }, { id: "TECH-PERF", revision: 2, status: "active", kind: "constraint", title: "指定負荷とデータ量でAPI別の性能を測定する", subject: "SlotKeeper", actionName: "provide", objectName: "指定負荷とデータ量でAPI別の性能を測定する", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "TECH-PERF-AC", given: "資源100・利用者200・予約10万件のデータがある", when_: "20並列で参照80%・作成取消20%の負荷を測定する", expected: "API別のp50/p95/p99・throughput・エラー率・整合性違反を同一runの証跡に残す" }], verification: { method: "check", evidence: "verify:performance" }, traces: { design: ["docs/design/generated/OVERVIEW.md"], implementation: ["tools/project/perf.py"], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "project", categoryName: "nonfunctional" }, { id: "TECH-QUALITY", revision: 2, status: "active", kind: "constraint", title: "型、lint、実DB、ブラウザ、負例検査の失敗を隠さない", subject: "SlotKeeper", actionName: "provide", objectName: "型、lint、実DB、ブラウザ、負例検査の失敗を隠さない", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "TECH-QUALITY-AC", given: "失敗・skip・未実行・flakyを含む結果がある", when_: "結果を共通形式へ変換する", expected: "非成功状態を成功へ変えず、collector外の結果と別runの混入を拒否する" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/TESTS.md"], implementation: ["tools/project/evidence.py", "tools/project/collector.py", "tools/project/verify.py"], tests: ["tools/tests/test_guards.py"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "project", categoryName: "nonfunctional" }, { id: "TECH-PRIVACY", revision: 2, status: "active", kind: "constraint", title: "公開allowlistに秘密や生ログを含めない", subject: "SlotKeeper", actionName: "provide", objectName: "公開allowlistに秘密や生ログを含めない", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "TECH-PRIVACY-AC", given: "公開サイトにallowlist外のfileやsymlinkがある", when_: "公開集合を検査する", expected: "公開を拒否し、生ログ・token・DB dumpを含めない" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/OVERVIEW.md"], implementation: ["tools/project/evidence.py"], tests: ["tools/tests/test_guards.py"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "project", categoryName: "nonfunctional" }, { id: "RULE-01", revision: 2, status: "active", kind: "constraint", title: "予約区間は `[開始, 終了)` とします。10:00〜11:00と11:00〜12:00は重複しません。", subject: "SlotKeeper", actionName: "provide", objectName: "予約区間は `[開始, 終了)` とします。10:00〜11:00と11:00〜12:00は重複しません。", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "RULE-01-AC", given: "10:00〜11:00の予約がある", when_: "11:00〜12:00を予約する", expected: "半開区間として重複せず成功する" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/api/index.md"], implementation: ["backend/src/slotkeeper/domain.py", "backend/src/slotkeeper/operations/reservations_create/endpoint.py"], tests: ["backend/tests/test_reservations.py"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "nonfunctional" }, { id: "RULE-02", revision: 2, status: "active", kind: "constraint", title: "開始・終了は15分刻み、予約時間は15分以上4時間以下です。", subject: "SlotKeeper", actionName: "provide", objectName: "開始・終了は15分刻み、予約時間は15分以上4時間以下です。", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "RULE-02-AC", given: "15分刻みでない、15分未満、4時間超の入力がある", when_: "時刻を検証する", expected: "422とし、15分と4時間ちょうどは受け付ける" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/api/index.md"], implementation: ["backend/src/slotkeeper/domain.py", "backend/src/slotkeeper/operations/reservations_create/endpoint.py"], tests: ["backend/tests/test_domain.py"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "nonfunctional" }, { id: "RULE-03", revision: 2, status: "active", kind: "constraint", title: "開始は現在より後、かつ現在から30日以内です。終了は開始と同じ日本時間の日付内にしてください。翌日00:00を終了とする予約も、この初期版では対象外です。", subject: "SlotKeeper", actionName: "provide", objectName: "開始は現在より後、かつ現在から30日以内です。終了は開始と同じ日本時間の日付内にしてください。翌日00:00を終了とする予約も、この初期版では対象外です。", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "RULE-03-AC", given: "過去・30日超・日本時間の日跨ぎの入力がある", when_: "時刻を検証する", expected: "422とし、翌日00:00終了も拒否する" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/api/index.md"], implementation: ["backend/src/slotkeeper/domain.py", "backend/src/slotkeeper/operations/reservations_create/endpoint.py"], tests: ["backend/tests/test_domain.py"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "nonfunctional" }, { id: "RULE-04", revision: 2, status: "active", kind: "constraint", title: "保存時刻はUTCと対応付け、表示・入力はAsia/Tokyoとします。現在時刻は差替え可能なClockから取得します。公開APIで任意に現在時刻を上書きできないようにしてください。", subject: "SlotKeeper", actionName: "provide", objectName: "保存時刻はUTCと対応付け、表示・入力はAsia/Tokyoとします。現在時刻は差替え可能なClockから取得します。公開APIで任意に現在時刻を上書きできないようにしてください。", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "RULE-04-AC", given: "公開APIとClock依存がある", when_: "OpenAPIと日本時間の変換を検査する", expected: "現在時刻を上書きする入力はなく、日本時間の日付境界で変換する" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/api/index.md"], implementation: ["backend/src/slotkeeper/domain.py", "frontend/src/logic.ts"], tests: ["backend/tests/test_operations.py", "frontend/tests/logic.test.ts"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "nonfunctional" }, { id: "RULE-05", revision: 2, status: "active", kind: "constraint", title: "予約状態は `confirmed → cancelled` です。終了済みかどうかは時刻から判定し、状態として二重管理しません。予約日時の直接編集は提供しません。", subject: "SlotKeeper", actionName: "provide", objectName: "予約状態は `confirmed → cancelled` です。終了済みかどうかは時刻から判定し、状態として二重管理しません。予約日時の直接編集は提供しません。", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "RULE-05-AC", given: "確定予約がある", when_: "公開APIを検査して取消する", expected: "予約日時の直接編集APIはなく、状態はconfirmedからcancelledへだけ遷移する" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/api/index.md"], implementation: ["backend/src/slotkeeper/domain.py", "backend/src/slotkeeper/operations/reservations_create/endpoint.py"], tests: ["backend/tests/test_operations.py", "backend/tests/test_reservations.py"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "nonfunctional" }, { id: "RULE-06", revision: 2, status: "active", kind: "constraint", title: "取消済み予約は重複判定から除きます。取消の確定と同時に、その枠を再予約できる状態へ戻します。", subject: "SlotKeeper", actionName: "provide", objectName: "取消済み予約は重複判定から除きます。取消の確定と同時に、その枠を再予約できる状態へ戻します。", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "RULE-06-AC", given: "確定予約がある", when_: "取消と同じ枠の再予約を行う", expected: "取消済みは重複判定から除かれ、確定予約は最大1件" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/api/index.md"], implementation: ["backend/src/slotkeeper/domain.py", "backend/src/slotkeeper/operations/reservations_create/endpoint.py"], tests: ["backend/tests/test_reservations.py"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "nonfunctional" }, { id: "RULE-07", revision: 2, status: "active", kind: "constraint", title: "既定の「将来予約」は `confirmed AND start_at > now` とします。開始済み予約の途中で資源が無効化されても、既存予約の記録は維持します。新規予約は拒否します。", subject: "SlotKeeper", actionName: "provide", objectName: "既定の「将来予約」は `confirmed AND start_at > now` とします。開始済み予約の途中で資源が無効化されても、既存予約の記録は維持します。新規予約は拒否します。", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "RULE-07-AC", given: "開始済みの予約がある資源", when_: "資源を無効化し将来予約を一覧する", expected: "無効化でき既存記録を保持し、将来予約はconfirmedかつ開始前だけ" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/api/index.md"], implementation: ["backend/src/slotkeeper/operations/resources_update/endpoint.py", "backend/src/slotkeeper/operations/reservations_list/sql/select_page.sql"], tests: ["backend/tests/test_reservations.py"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "nonfunctional" }, { id: "RULE-08", revision: 2, status: "active", kind: "constraint", title: "将来予約のある資源を無効化できません。予約作成と無効化が競合しても、無効資源に将来予約を残してはいけません。", subject: "SlotKeeper", actionName: "provide", objectName: "将来予約のある資源を無効化できません。予約作成と無効化が競合しても、無効資源に将来予約を残してはいけません。", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "RULE-08-AC", given: "将来予約がある資源、または予約作成と無効化の同時実行", when_: "無効化する", expected: "無効資源に将来予約を残さない" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/api/index.md"], implementation: ["backend/src/slotkeeper/domain.py", "backend/src/slotkeeper/operations/reservations_create/endpoint.py"], tests: ["backend/tests/test_reservations.py"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "nonfunctional" }, { id: "RULE-09", revision: 2, status: "active", kind: "constraint", title: "一般利用者には他人の目的・利用者識別情報・履歴を返しません。共有予約表では時間帯と「予約済み」を表示します。管理者は取消業務に必要な情報を閲覧できます。", subject: "SlotKeeper", actionName: "provide", objectName: "一般利用者には他人の目的・利用者識別情報・履歴を返しません。共有予約表では時間帯と「予約済み」を表示します。管理者は取消業務に必要な情報を閲覧できます。", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "RULE-09-AC", given: "他人の予約がある", when_: "一般利用者が予約表と詳細を取得し、管理者が詳細を取得する", expected: "一般利用者へ目的・識別情報・履歴を返さず、管理者は閲覧できる" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/api/index.md"], implementation: ["backend/src/slotkeeper/operations/schedule/endpoint.py", "backend/src/slotkeeper/domain.py"], tests: ["backend/tests/test_reservations.py"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "nonfunctional" }, { id: "RULE-10", revision: 2, status: "active", kind: "constraint", title: "予約作成の要求キーは利用者単位で24時間有効です。同じキー・同じ正規化入力には元の成功応答を返し、異なる入力は409とします。有効期限後は新規要求として通常の重複判定を行います。", subject: "SlotKeeper", actionName: "provide", objectName: "予約作成の要求キーは利用者単位で24時間有効です。同じキー・同じ正規化入力には元の成功応答を返し、異なる入力は409とします。有効期限後は新規要求として通常の重複判定を行います。", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "RULE-10-AC", given: "同じ利用者の要求キーがある", when_: "同じ入力・異なる入力・24時間後に再送する", expected: "元の成功応答・409・新規要求として扱う" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/api/index.md"], implementation: ["backend/src/slotkeeper/domain.py", "backend/src/slotkeeper/operations/reservations_create/endpoint.py"], tests: ["backend/tests/test_reservations.py"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "nonfunctional" }, { id: "RULE-11", revision: 2, status: "active", kind: "constraint", title: "成功済み要求の再送は、元の予約が開始・取消済みになっていても元の作成結果を返します。再送照合より先に現在時刻で新規予約の入力検証をしないでください。", subject: "SlotKeeper", actionName: "provide", objectName: "成功済み要求の再送は、元の予約が開始・取消済みになっていても元の作成結果を返します。再送照合より先に現在時刻で新規予約の入力検証をしないでください。", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "RULE-11-AC", given: "作成済み予約が取消または開始済みである", when_: "24時間以内に同じキーで再送する", expected: "時刻検証より先に照合し元の作成結果を返す" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/api/index.md"], implementation: ["backend/src/slotkeeper/domain.py", "backend/src/slotkeeper/operations/reservations_create/endpoint.py"], tests: ["backend/tests/test_reservations.py"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "nonfunctional" }, { id: "RULE-12", revision: 2, status: "active", kind: "constraint", title: "予約・履歴・要求キーの成功記録は、同一トランザクションで確定します。取消と取消履歴も一体で確定します。", subject: "SlotKeeper", actionName: "provide", objectName: "予約・履歴・要求キーの成功記録は、同一トランザクションで確定します。取消と取消履歴も一体で確定します。", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "RULE-12-AC", given: "作成または取消の途中で障害が起きる", when_: "操作を確定する", expected: "予約・履歴・要求キーを同一transactionで確定またはrollbackする" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/api/index.md"], implementation: ["backend/src/slotkeeper/domain.py", "backend/src/slotkeeper/operations/reservations_create/endpoint.py"], tests: ["backend/tests/test_reservations.py"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "nonfunctional" }, { id: "RULE-13", revision: 2, status: "active", kind: "constraint", title: "取消済み予約への取消は409とします。履歴を追加しません。", subject: "SlotKeeper", actionName: "provide", objectName: "取消済み予約への取消は409とします。履歴を追加しません。", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "RULE-13-AC", given: "取消済み予約がある", when_: "取消する", expected: "409で履歴を追加しない" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/api/index.md"], implementation: ["backend/src/slotkeeper/domain.py", "backend/src/slotkeeper/operations/reservations_create/endpoint.py"], tests: ["backend/tests/test_reservations.py"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "nonfunctional" }, { id: "RULE-14", revision: 2, status: "active", kind: "constraint", title: "資源名は空白除去後1〜100文字、説明は0〜1,000文字、予約目的は1〜200文字とします。一覧はページングし、順序と同順位時のID順を固定します。", subject: "SlotKeeper", actionName: "provide", objectName: "資源名は空白除去後1〜100文字、説明は0〜1,000文字、予約目的は1〜200文字とします。一覧はページングし、順序と同順位時のID順を固定します。", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "RULE-14-AC", given: "境界長の名前・説明・目的と複数ページの一覧がある", when_: "入力と一覧を検査する", expected: "長さ制約を守り、固定順とID順でページングする" }], verification: { method: "test", evidence: "品質ポータルのテスト結果。テスト説明の[受入条件ID]と実collector IDを設計生成器が照合する" }, traces: { design: ["docs/design/generated/api/index.md"], implementation: ["backend/src/slotkeeper/domain.py", "backend/src/slotkeeper/operations/reservations_create/endpoint.py"], tests: ["backend/tests/test_domain.py", "backend/tests/test_reservations.py"], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "trace-completion", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "nonfunctional" }] }

  pure val lifecycleRequirement: Requirement = {
    id: "REQ-LIFECYCLE-MODEL-001",
    revision: 1,
    status: "active",
    kind: "functional",
    title: "lifecycle fixture",
    subject: "requirements lifecycle model",
    actionName: "maintain",
    objectName: "a typed catalog requirement",
    rationale: "A concrete item makes lifecycle refinement non-vacuous.",
    sourceRefs: ["model:requirements-lifecycle"],
    acceptanceCriteria: [
      { id: "AC-LIFECYCLE-MODEL-001-1", given: "a current catalog", when_: "a CAS transition is accepted", expected: "catalog and item revisions advance together" }
    ],
    verification: { method: "Quint model", evidence: "catalog lifecycle transition tests" },
    traces: {
      design: [],
      implementation: [],
      tests: [],
      standards: ["QUINT-0.32"],
    },
    lastChangedBy: "model:add",
    retirementReason: "",
    supersededBy: "",
    scopeName: "project",
    categoryName: "nonfunctional",
  }

  pure val successionR1: Requirement = lifecycleRequirement
    .with("id", "REQ-SUCCESSION-R1")
    .with("acceptanceCriteria", [
      { id: "AC-SUCCESSION-R1", given: "R1 exists", when_: "R1 is superseded", expected: "the chain advances" }
    ])
    .with("status", "retired")
    .with("retirementReason", "superseded by R2")
    .with("supersededBy", "REQ-SUCCESSION-R2")
  pure val successionR2: Requirement = lifecycleRequirement
    .with("id", "REQ-SUCCESSION-R2")
    .with("acceptanceCriteria", [
      { id: "AC-SUCCESSION-R2", given: "R2 exists", when_: "R2 is superseded", expected: "the chain advances" }
    ])
    .with("status", "retired")
    .with("retirementReason", "superseded by R3")
    .with("supersededBy", "REQ-SUCCESSION-R3")
  pure val successionR3: Requirement = lifecycleRequirement
    .with("id", "REQ-SUCCESSION-R3")
    .with("acceptanceCriteria", [
      { id: "AC-SUCCESSION-R3", given: "R3 exists", when_: "the chain terminates", expected: "R3 is active" }
    ])
  pure val successionCycleR2: Requirement = successionR2
    .with("supersededBy", "REQ-SUCCESSION-R1")
  pure val successionRetiredTerminalR2: Requirement = successionR2
    .with("supersededBy", "")
  pure val successionCatalog: Catalog = {
    schemaVersion: 1,
    catalogRevision: 1,
    product: "succession-contract",
    updatedAt: "succession:fixture",
    requirements: [successionR1, successionR2, successionR3],
  }

  pure val batchRequirement1: Requirement = lifecycleRequirement
    .with("id", "REQ-BATCH-1")
    .with("acceptanceCriteria", [
      { id: "AC-BATCH-1", given: "batch source", when_: "item one changes", expected: "revision advances once" }
    ])
  pure val batchRequirement2: Requirement = lifecycleRequirement
    .with("id", "REQ-BATCH-2")
    .with("acceptanceCriteria", [
      { id: "AC-BATCH-2", given: "batch source", when_: "item two changes", expected: "revision advances once" }
    ])
  pure val batchRequirement3: Requirement = lifecycleRequirement
    .with("id", "REQ-BATCH-3")
    .with("acceptanceCriteria", [
      { id: "AC-BATCH-3", given: "batch source", when_: "item three changes", expected: "revision advances once" }
    ])
  pure val batchBefore: Catalog = {
    schemaVersion: 1,
    catalogRevision: 5,
    product: "batch-contract",
    updatedAt: "batch:before",
    requirements: [batchRequirement1, batchRequirement2, batchRequirement3],
  }
  pure val batchAfterTwo: Catalog = batchBefore
    .with("catalogRevision", 6)
    .with("updatedAt", "batch:two")
    .with("requirements", [
      batchRequirement1
        .with("revision", 2)
        .with("title", "batch item one updated")
        .with("lastChangedBy", "batch:change"),
      batchRequirement2
        .with("revision", 2)
        .with("traces", batchRequirement2.traces.with("tests", ["tests/batch-two.py"]))
        .with("lastChangedBy", "batch:change"),
      batchRequirement3,
    ])
  pure val batchAfterThree: Catalog = batchBefore
    .with("catalogRevision", 6)
    .with("updatedAt", "batch:three")
    .with("requirements", [
      batchAfterTwo.requirements.nth(0),
      batchAfterTwo.requirements.nth(1),
      batchRequirement3
        .with("revision", 2)
        .with("status", "retired")
        .with("retirementReason", "batch retirement")
        .with("lastChangedBy", "batch:change"),
    ])
  pure val batchStaleAfter: Catalog = batchAfterTwo.with("requirements", [
    batchRequirement1,
    batchAfterTwo.requirements.nth(1),
    batchRequirement3,
  ])
  pure val batchPartialAfterStale: Catalog = batchBefore
    .with("catalogRevision", 6)
    .with("updatedAt", "batch:stale-after-valid")
    .with("requirements", [
      batchAfterTwo.requirements.nth(0),
      batchRequirement2,
      batchRequirement3,
    ])
  pure val batchInvalidAfter: Catalog = batchAfterTwo.with("requirements", [
    batchAfterTwo.requirements.nth(0).with("title", ""),
    batchAfterTwo.requirements.nth(1),
    batchRequirement3,
  ])
  pure val batchUpdateOperation: RequirementOperation = {
    kind: "update",
    id: "REQ-BATCH-1",
    expectedRevision: 1,
    replacement: batchAfterTwo.requirements.nth(0),
  }
  pure val batchTraceOperation: RequirementOperation = {
    kind: "trace",
    id: "REQ-BATCH-2",
    expectedRevision: 1,
    replacement: batchAfterTwo.requirements.nth(1),
  }
  pure val batchRetireOperation: RequirementOperation = {
    kind: "retire",
    id: "REQ-BATCH-3",
    expectedRevision: 1,
    replacement: batchAfterThree.requirements.nth(2),
  }
  pure val batchStaleOperation: RequirementOperation = batchUpdateOperation
    .with("expectedRevision", 0)
  pure val batchStaleTraceOperation: RequirementOperation = batchTraceOperation
    .with("expectedRevision", 0)
  pure val batchInvalidOperation: RequirementOperation = batchUpdateOperation
    .with("replacement", batchInvalidAfter.requirements.nth(0))
  pure val batchResurrectionOperation: RequirementOperation = {
    kind: "update",
    id: "REQ-BATCH-3",
    expectedRevision: 2,
    replacement: batchAfterThree.requirements.nth(2)
      .with("revision", 3)
      .with("status", "active")
      .with("retirementReason", "")
      .with("lastChangedBy", "batch:change"),
  }
  pure val batchResurrectedAfter: Catalog = batchAfterThree
    .with("catalogRevision", 7)
    .with("updatedAt", "batch:resurrection")
    .with("requirements", batchAfterThree.requirements.replaceAt(
      2,
      batchResurrectionOperation.replacement
    ))

  var catalog: Catalog
  var lifecycle: Lifecycle

  action init = all {
    catalog' = requirementsSource,
    lifecycle' = {
      catalogRevision: requirementsSource.catalogRevision,
      itemRevision: 0,
      itemPresent: false,
      itemStatus: "missing",
      traceRevision: 0,
      priorCatalogRevision: requirementsSource.catalogRevision,
      priorItemRevision: 0,
      priorItemPresent: false,
      priorItemStatus: "missing",
      priorTraceRevision: 0,
      lastOperation: "init",
    },
  }

  action addRequirementAt(expectedCatalogRevision: int): bool = all {
    expectedCatalogRevision == catalog.catalogRevision,
    lifecycle.catalogRevision == expectedCatalogRevision,
    not(lifecycle.itemPresent),
    catalog.requirements.indices().forall(i =>
      catalog.requirements.nth(i).id != lifecycleRequirement.id
    ),
    catalog' = catalog
      .with("catalogRevision", catalog.catalogRevision + 1)
      .with("requirements", catalog.requirements.append(lifecycleRequirement)),
    lifecycle' = {
      catalogRevision: lifecycle.catalogRevision + 1,
      itemRevision: 1,
      itemPresent: true,
      itemStatus: "active",
      traceRevision: 0,
      priorCatalogRevision: lifecycle.catalogRevision,
      priorItemRevision: lifecycle.itemRevision,
      priorItemPresent: lifecycle.itemPresent,
      priorItemStatus: lifecycle.itemStatus,
      priorTraceRevision: lifecycle.traceRevision,
      lastOperation: "add",
    },
  }

  action addRequirement = addRequirementAt(lifecycle.catalogRevision)

  def updateRequirementIsAllowed(expectedCatalogRevision: int, expectedItemRevision: int): bool =
    all {
      lifecycle.itemPresent,
      lifecycle.itemStatus == "active",
      expectedCatalogRevision == catalog.catalogRevision,
      expectedCatalogRevision == lifecycle.catalogRevision,
      expectedItemRevision == lifecycle.itemRevision,
      catalog.requirements.nth(catalog.requirements.length() - 1).id == lifecycleRequirement.id,
      catalog.requirements.nth(catalog.requirements.length() - 1).revision == expectedItemRevision,
      catalog.requirements.nth(catalog.requirements.length() - 1).status == "active",
      catalog.requirements.nth(catalog.requirements.length() - 1).title != "lifecycle fixture updated",
    }

  action updateRequirementAt(expectedCatalogRevision: int, expectedItemRevision: int): bool = all {
    updateRequirementIsAllowed(expectedCatalogRevision, expectedItemRevision),
    catalog' = catalog
      .with("catalogRevision", catalog.catalogRevision + 1)
      .with(
        "requirements",
        catalog.requirements.replaceAt(
          catalog.requirements.length() - 1,
          catalog.requirements.nth(catalog.requirements.length() - 1)
            .with("revision", expectedItemRevision + 1)
            .with("title", "lifecycle fixture updated")
            .with("lastChangedBy", "model:update")
        )
      ),
    lifecycle' = {
      catalogRevision: lifecycle.catalogRevision + 1,
      itemRevision: lifecycle.itemRevision + 1,
      itemPresent: true,
      itemStatus: "active",
      traceRevision: lifecycle.traceRevision,
      priorCatalogRevision: lifecycle.catalogRevision,
      priorItemRevision: lifecycle.itemRevision,
      priorItemPresent: lifecycle.itemPresent,
      priorItemStatus: lifecycle.itemStatus,
      priorTraceRevision: lifecycle.traceRevision,
      lastOperation: "update",
    },
  }

  action updateRequirement = updateRequirementAt(lifecycle.catalogRevision, lifecycle.itemRevision)

  def traceUpdateIsAllowed(expectedCatalogRevision: int, expectedItemRevision: int): bool =
    all {
      lifecycle.itemPresent,
      lifecycle.itemStatus == "active",
      lifecycle.traceRevision == 0,
      expectedCatalogRevision == catalog.catalogRevision,
      expectedCatalogRevision == lifecycle.catalogRevision,
      expectedItemRevision == lifecycle.itemRevision,
      catalog.requirements.nth(catalog.requirements.length() - 1).id == lifecycleRequirement.id,
      catalog.requirements.nth(catalog.requirements.length() - 1).revision == expectedItemRevision,
      catalog.requirements.nth(catalog.requirements.length() - 1).status == "active",
    }

  action updateRequirementTraceAt(expectedCatalogRevision: int, expectedItemRevision: int): bool = all {
    traceUpdateIsAllowed(expectedCatalogRevision, expectedItemRevision),
    catalog' = catalog
      .with("catalogRevision", catalog.catalogRevision + 1)
      .with(
        "requirements",
        catalog.requirements.replaceAt(
          catalog.requirements.length() - 1,
          catalog.requirements.nth(catalog.requirements.length() - 1)
            .with("revision", expectedItemRevision + 1)
            .with(
              "traces",
              catalog.requirements.nth(catalog.requirements.length() - 1).traces.with(
                "tests",
                catalog.requirements.nth(catalog.requirements.length() - 1).traces.tests
                  .append("tests/model-trace-update.py")
              )
            )
            .with("lastChangedBy", "model:trace-update")
        )
      ),
    lifecycle' = {
      catalogRevision: lifecycle.catalogRevision + 1,
      itemRevision: lifecycle.itemRevision + 1,
      itemPresent: true,
      itemStatus: "active",
      traceRevision: lifecycle.traceRevision + 1,
      priorCatalogRevision: lifecycle.catalogRevision,
      priorItemRevision: lifecycle.itemRevision,
      priorItemPresent: lifecycle.itemPresent,
      priorItemStatus: lifecycle.itemStatus,
      priorTraceRevision: lifecycle.traceRevision,
      lastOperation: "trace-update",
    },
  }

  action updateRequirementTrace =
    updateRequirementTraceAt(lifecycle.catalogRevision, lifecycle.itemRevision)

  def retirementIsAllowed(expectedCatalogRevision: int, expectedItemRevision: int): bool =
    all {
      lifecycle.itemPresent,
      lifecycle.itemStatus == "active",
      expectedCatalogRevision == catalog.catalogRevision,
      expectedCatalogRevision == lifecycle.catalogRevision,
      expectedItemRevision == lifecycle.itemRevision,
      catalog.requirements.nth(catalog.requirements.length() - 1).id == lifecycleRequirement.id,
      catalog.requirements.nth(catalog.requirements.length() - 1).revision == expectedItemRevision,
      catalog.requirements.nth(catalog.requirements.length() - 1).status == "active",
    }

  action retireRequirementAt(expectedCatalogRevision: int, expectedItemRevision: int): bool = all {
    retirementIsAllowed(expectedCatalogRevision, expectedItemRevision),
    catalog' = catalog
      .with("catalogRevision", catalog.catalogRevision + 1)
      .with(
        "requirements",
        catalog.requirements.replaceAt(
          catalog.requirements.length() - 1,
          catalog.requirements.nth(catalog.requirements.length() - 1)
            .with("revision", expectedItemRevision + 1)
            .with("status", "retired")
            .with("retirementReason", "model retirement")
            .with("lastChangedBy", "model:retire")
        )
      ),
    lifecycle' = {
      catalogRevision: lifecycle.catalogRevision + 1,
      itemRevision: lifecycle.itemRevision + 1,
      itemPresent: true,
      itemStatus: "retired",
      traceRevision: lifecycle.traceRevision,
      priorCatalogRevision: lifecycle.catalogRevision,
      priorItemRevision: lifecycle.itemRevision,
      priorItemPresent: lifecycle.itemPresent,
      priorItemStatus: lifecycle.itemStatus,
      priorTraceRevision: lifecycle.traceRevision,
      lastOperation: "retire",
    },
  }

  action retireRequirement = retireRequirementAt(lifecycle.catalogRevision, lifecycle.itemRevision)

  action lifecycleStutter = all {
    catalog' = catalog,
    lifecycle' = {
      catalogRevision: lifecycle.catalogRevision,
      itemRevision: lifecycle.itemRevision,
      itemPresent: lifecycle.itemPresent,
      itemStatus: lifecycle.itemStatus,
      traceRevision: lifecycle.traceRevision,
      priorCatalogRevision: lifecycle.catalogRevision,
      priorItemRevision: lifecycle.itemRevision,
      priorItemPresent: lifecycle.itemPresent,
      priorItemStatus: lifecycle.itemStatus,
      priorTraceRevision: lifecycle.traceRevision,
      lastOperation: "none",
    },
  }

  action counterOnlyMutation = all {
    catalog' = catalog,
    lifecycle' = lifecycle.with("catalogRevision", lifecycle.catalogRevision + 1),
  }

  action step = any {
    addRequirement,
    updateRequirement,
    updateRequirementTrace,
    retireRequirement,
    lifecycleStutter,
  }

  pure val allowedStatuses = Set("active", "retired")
  pure val allowedKinds = Set("functional", "quality", "constraint", "interface", "data", "operational")
  pure val allowedScopes = Set("product", "project")
  pure val allowedCategories = Set("functional", "nonfunctional")
  pure val allowedActions = Set(
    "constrain", "derive", "detect", "discover", "enable", "enforce", "estimate",
    "expand", "formalize", "generate", "maintain", "measure", "parse", "preserve",
    "provide", "route", "select", "separate", "stage", "stop", "structure", "validate", "verify"
  )

  pure def stringsAreUnique(values: List[str]): bool = values.indices().forall(i =>
    values.indices().forall(j => i == j or values.nth(i) != values.nth(j))
  )

  pure def stringsAreNonempty(values: List[str]): bool =
    values.indices().forall(i => values.nth(i) != "")

  pure def requirementIdsAreUniqueIn(requirements: List[Requirement]): bool =
    requirements.indices().forall(i =>
      requirements.indices().forall(j =>
        i == j or requirements.nth(i).id != requirements.nth(j).id
      )
    )

  val requirementIdsAreUnique = requirementIdsAreUniqueIn(catalog.requirements)

  // 構造的完全性は機械検査する。1 IDが意味的に1義務だけを表すかは、
  // 自然言語を解釈できる権限あるhuman semantic reviewの責務である。
  pure def requirementsAreStructurallyCompleteIn(requirements: List[Requirement]): bool =
    requirements.indices().forall(i => all {
      requirements.nth(i).id != "",
      requirements.nth(i).revision >= 1,
      requirements.nth(i).title != "",
      requirements.nth(i).subject != "",
      requirements.nth(i).actionName != "",
      requirements.nth(i).objectName != "",
      requirements.nth(i).rationale != "",
      requirements.nth(i).lastChangedBy != "",
      requirements.nth(i).sourceRefs.length() > 0,
      stringsAreNonempty(requirements.nth(i).sourceRefs),
      stringsAreUnique(requirements.nth(i).sourceRefs),
      requirements.nth(i).acceptanceCriteria.length() > 0,
      requirements.nth(i).verification.method != "",
      requirements.nth(i).verification.evidence != "",
    })

  val requirementsAreStructurallyComplete =
    requirementsAreStructurallyCompleteIn(catalog.requirements)

  pure def requirementsAreTypedIn(requirements: List[Requirement]): bool =
    requirements.indices().forall(i => all {
      allowedStatuses.contains(requirements.nth(i).status),
      allowedKinds.contains(requirements.nth(i).kind),
      allowedActions.contains(requirements.nth(i).actionName),
      (requirements.nth(i).scopeName == "").or(allowedScopes.contains(requirements.nth(i).scopeName)),
      (requirements.nth(i).categoryName == "").or(allowedCategories.contains(requirements.nth(i).categoryName)),
    })

  val requirementsAreTyped = requirementsAreTypedIn(catalog.requirements)

  pure def acceptanceCriteriaAreCompleteIn(requirements: List[Requirement]): bool =
    requirements.indices().forall(i =>
      requirements.nth(i).acceptanceCriteria.indices().forall(j => all {
        requirements.nth(i).acceptanceCriteria.nth(j).id != "",
        requirements.nth(i).acceptanceCriteria.nth(j).given != "",
        requirements.nth(i).acceptanceCriteria.nth(j).when_ != "",
        requirements.nth(i).acceptanceCriteria.nth(j).expected != "",
      })
    )

  val acceptanceCriteriaAreComplete =
    acceptanceCriteriaAreCompleteIn(catalog.requirements)

  pure def acceptanceCriterionIdsAreUniqueIn(requirements: List[Requirement]): bool =
    requirements.indices().forall(i =>
      requirements.indices().forall(j =>
        requirements.nth(i).acceptanceCriteria.indices().forall(x =>
          requirements.nth(j).acceptanceCriteria.indices().forall(y =>
          (i == j and x == y) or
            requirements.nth(i).acceptanceCriteria.nth(x).id !=
              requirements.nth(j).acceptanceCriteria.nth(y).id
          )
        )
      )
    )

  val acceptanceCriterionIdsAreUnique =
    acceptanceCriterionIdsAreUniqueIn(catalog.requirements)

  pure def traceLinksAreUniqueIn(requirements: List[Requirement]): bool =
    requirements.indices().forall(i => all {
      stringsAreNonempty(requirements.nth(i).traces.design),
      stringsAreNonempty(requirements.nth(i).traces.implementation),
      stringsAreNonempty(requirements.nth(i).traces.tests),
      stringsAreNonempty(requirements.nth(i).traces.standards),
      stringsAreUnique(requirements.nth(i).traces.design),
      stringsAreUnique(requirements.nth(i).traces.implementation),
      stringsAreUnique(requirements.nth(i).traces.tests),
      stringsAreUnique(requirements.nth(i).traces.standards),
    })

  val traceLinksAreUnique = traceLinksAreUniqueIn(catalog.requirements)

  pure def classificationIsPairedIn(requirements: List[Requirement]): bool =
    requirements.indices().forall(i =>
      (requirements.nth(i).scopeName == "") iff
      (requirements.nth(i).categoryName == "")
    )

  val classificationIsPaired = classificationIsPairedIn(catalog.requirements)

  pure def retirementFieldsAreConsistentIn(requirements: List[Requirement]): bool =
    requirements.indices().forall(i => all {
    (requirements.nth(i).status == "active").implies(all {
      requirements.nth(i).retirementReason == "",
      requirements.nth(i).supersededBy == "",
    }),
    (requirements.nth(i).status == "retired").implies(
      requirements.nth(i).retirementReason != ""
    ),
    (requirements.nth(i).supersededBy != "").implies(all {
      requirements.nth(i).status == "retired",
      requirements.nth(i).supersededBy != requirements.nth(i).id,
    }),
  })

  val retirementFieldsAreConsistent =
    retirementFieldsAreConsistentIn(catalog.requirements)

  pure def supersessionChainsAreValid(requirements: List[Requirement]): bool =
    requirements.indices().forall(i =>
      (requirements.nth(i).supersededBy != "").implies(
        requirements.indices().exists(j => all {
          j > i,
          requirements.nth(j).id == requirements.nth(i).supersededBy,
          requirements.nth(j).id != requirements.nth(i).id,
          (requirements.nth(j).status == "active").or(all {
            requirements.nth(j).status == "retired",
            requirements.nth(j).supersededBy != "",
          }),
        })
      )
    )

  pure def catalogHeaderIsValid(source: Catalog): bool = all {
    source.schemaVersion == 1,
    source.catalogRevision >= 1,
    source.product != "",
    source.updatedAt != "",
    source.requirements.length() > 0,
  }

  // Pure catalog component of catalogWellFormed. Lifecycle witness refinement
  // remains a state invariant below and is intentionally not fabricated for a
  // caller-supplied batch result.
  pure def catalogDataWellFormed(source: Catalog): bool = all {
    catalogHeaderIsValid(source),
    requirementIdsAreUniqueIn(source.requirements),
    requirementsAreStructurallyCompleteIn(source.requirements),
    requirementsAreTypedIn(source.requirements),
    acceptanceCriteriaAreCompleteIn(source.requirements),
    acceptanceCriterionIdsAreUniqueIn(source.requirements),
    traceLinksAreUniqueIn(source.requirements),
    classificationIsPairedIn(source.requirements),
    retirementFieldsAreConsistentIn(source.requirements),
    supersessionChainsAreValid(source.requirements),
  }

  pure def stringsContain(values: List[str], value: str): bool =
    values.indices().exists(i => values.nth(i) == value)

  pure def requirementExists(requirements: List[Requirement], id: str): bool =
    requirements.indices().exists(i => requirements.nth(i).id == id)

  pure def requirementById(requirements: List[Requirement], id: str): Requirement =
    requirements.select(requirement => requirement.id == id).head()

  pure def replaceRequirement(
    requirements: List[Requirement],
    id: str,
    replacement: Requirement,
  ): List[Requirement] =
    range(0, requirements.length()).foldl(requirements, (result, index) =>
      if (result.nth(index).id == id)
        result.replaceAt(index, replacement)
      else
        result
    )

  pure def updateReplacementIsValid(
    current: Requirement,
    replacement: Requirement,
    changeId: str,
  ): bool = all {
    current.status == "active",
    replacement == current
      .with("revision", current.revision + 1)
      .with("kind", replacement.kind)
      .with("title", replacement.title)
      .with("subject", replacement.subject)
      .with("actionName", replacement.actionName)
      .with("objectName", replacement.objectName)
      .with("rationale", replacement.rationale)
      .with("sourceRefs", replacement.sourceRefs)
      .with("acceptanceCriteria", replacement.acceptanceCriteria)
      .with("verification", replacement.verification)
      .with("scopeName", replacement.scopeName)
      .with("categoryName", replacement.categoryName)
      .with("lastChangedBy", changeId),
    replacement
      .with("revision", current.revision)
      .with("lastChangedBy", current.lastChangedBy) != current,
  }

  pure def traceReplacementIsValid(
    current: Requirement,
    replacement: Requirement,
    changeId: str,
  ): bool = all {
    current.status == "active",
    replacement.traces != current.traces,
    replacement == current
      .with("revision", current.revision + 1)
      .with("traces", replacement.traces)
      .with("lastChangedBy", changeId),
  }

  pure def retirementReplacementIsValid(
    current: Requirement,
    replacement: Requirement,
    changeId: str,
  ): bool = all {
    current.status == "active",
    replacement.retirementReason != "",
    replacement == current
      .with("revision", current.revision + 1)
      .with("status", "retired")
      .with("retirementReason", replacement.retirementReason)
      .with("supersededBy", replacement.supersededBy)
      .with("lastChangedBy", changeId),
  }

  pure def batchOperationIsAllowed(
    accumulator: BatchFold,
    operation: RequirementOperation,
    changeId: str,
  ): bool =
    if (not(accumulator.valid)) false
    else if (stringsContain(accumulator.touchedIds, operation.id)) false
    else if (operation.kind == "add") all {
      not(requirementExists(accumulator.requirements, operation.id)),
      operation.expectedRevision == 0,
      operation.id == operation.replacement.id,
      operation.replacement.revision == 1,
      operation.replacement.status == "active",
      operation.replacement.retirementReason == "",
      operation.replacement.supersededBy == "",
      operation.replacement.lastChangedBy == changeId,
    }
    else if (not(requirementExists(accumulator.requirements, operation.id))) false
    else if (
      operation.expectedRevision !=
        requirementById(accumulator.requirements, operation.id).revision
    ) false
    else if (operation.kind == "update") updateReplacementIsValid(
      requirementById(accumulator.requirements, operation.id),
      operation.replacement,
      changeId
    )
    else if (operation.kind == "trace") traceReplacementIsValid(
      requirementById(accumulator.requirements, operation.id),
      operation.replacement,
      changeId
    )
    else if (operation.kind == "retire") retirementReplacementIsValid(
      requirementById(accumulator.requirements, operation.id),
      operation.replacement,
      changeId
    )
    else false

  pure def applyBatchOperation(
    accumulator: BatchFold,
    operation: RequirementOperation,
    changeId: str,
  ): BatchFold =
    if (batchOperationIsAllowed(accumulator, operation, changeId)) {
      requirements:
        if (operation.kind == "add")
          accumulator.requirements.append(operation.replacement)
        else
          replaceRequirement(accumulator.requirements, operation.id, operation.replacement),
      touchedIds: accumulator.touchedIds.append(operation.id),
      valid: true,
    } else accumulator.with("valid", false)

  pure def initialBatchFold(before: Catalog): BatchFold = {
    requirements: before.requirements,
    touchedIds: [],
    valid: true,
  }

  pure def foldBatchOperations(
    before: Catalog,
    operations: List[RequirementOperation],
    changeId: str,
  ): BatchFold = operations.foldl(
    initialBatchFold(before),
    (accumulator, operation) => applyBatchOperation(accumulator, operation, changeId)
  )

  pure def batchCandidate(
    before: Catalog,
    operations: List[RequirementOperation],
    changedAt: str,
    changeId: str,
  ): Catalog = before
    .with("catalogRevision", before.catalogRevision + 1)
    .with("updatedAt", changedAt)
    .with("requirements", foldBatchOperations(before, operations, changeId).requirements)

  pure def batchWouldBeAccepted(
    before: Catalog,
    expectedCatalogRevision: int,
    operations: List[RequirementOperation],
    changedAt: str,
    changeId: str,
  ): bool = all {
    expectedCatalogRevision == before.catalogRevision,
    operations.length() > 0,
    changedAt != "",
    changeId != "",
    foldBatchOperations(before, operations, changeId).valid,
    catalogDataWellFormed(batchCandidate(before, operations, changedAt, changeId)),
  }

  // This relation models the same arbitrary-length operation fold and CAS
  // boundary as specflow.apply_change. No operation may resurrect a retired
  // item, and any stale or invalid member makes the entire batch stutter.
  pure def atomicBatchTransitionIsValid(
    before: Catalog,
    after: Catalog,
    expectedCatalogRevision: int,
    operations: List[RequirementOperation],
    changedAt: str,
    changeId: str,
    outcome: str,
  ): bool = all {
    Set("accepted", "rejected").contains(outcome),
    catalogDataWellFormed(before),
    (outcome == "accepted") iff batchWouldBeAccepted(
      before, expectedCatalogRevision, operations, changedAt, changeId
    ),
    (outcome == "accepted").implies(
      after == batchCandidate(before, operations, changedAt, changeId)
    ),
    (outcome == "rejected").implies(after == before),
  }

  val lifecycleRevisionTransitionIsSound = all {
    Set("init", "add", "update", "trace-update", "retire", "none").contains(lifecycle.lastOperation),
    (lifecycle.lastOperation == "init").implies(all {
      lifecycle.catalogRevision == requirementsSource.catalogRevision,
      lifecycle.itemRevision == 0,
      not(lifecycle.itemPresent),
    }),
    (lifecycle.lastOperation == "add").implies(all {
      not(lifecycle.priorItemPresent),
      lifecycle.itemPresent,
      lifecycle.itemStatus == "active",
      lifecycle.catalogRevision == lifecycle.priorCatalogRevision + 1,
      lifecycle.itemRevision == 1,
    }),
    (lifecycle.lastOperation == "update").implies(all {
      lifecycle.priorItemPresent,
      lifecycle.priorItemStatus == "active",
      lifecycle.itemStatus == "active",
      lifecycle.catalogRevision == lifecycle.priorCatalogRevision + 1,
      lifecycle.itemRevision == lifecycle.priorItemRevision + 1,
      lifecycle.traceRevision == lifecycle.priorTraceRevision,
    }),
    (lifecycle.lastOperation == "trace-update").implies(all {
      lifecycle.priorItemPresent,
      lifecycle.priorItemStatus == "active",
      lifecycle.itemStatus == "active",
      lifecycle.catalogRevision == lifecycle.priorCatalogRevision + 1,
      lifecycle.itemRevision == lifecycle.priorItemRevision + 1,
      lifecycle.traceRevision == lifecycle.priorTraceRevision + 1,
    }),
    (lifecycle.lastOperation == "retire").implies(all {
      lifecycle.priorItemPresent,
      lifecycle.priorItemStatus == "active",
      lifecycle.itemPresent,
      lifecycle.itemStatus == "retired",
      lifecycle.catalogRevision == lifecycle.priorCatalogRevision + 1,
      lifecycle.itemRevision == lifecycle.priorItemRevision + 1,
      lifecycle.traceRevision == lifecycle.priorTraceRevision,
    }),
    (lifecycle.lastOperation == "none").implies(all {
      lifecycle.catalogRevision == lifecycle.priorCatalogRevision,
      lifecycle.itemRevision == lifecycle.priorItemRevision,
      lifecycle.itemPresent == lifecycle.priorItemPresent,
      lifecycle.itemStatus == lifecycle.priorItemStatus,
      lifecycle.traceRevision == lifecycle.priorTraceRevision,
    }),
  }

  val lifecycleRefinesCatalog = all {
    lifecycle.catalogRevision == catalog.catalogRevision,
    lifecycle.itemPresent iff
      catalog.requirements.indices().exists(i =>
        catalog.requirements.nth(i).id == lifecycleRequirement.id
      ),
    lifecycle.itemPresent.implies(all {
      catalog.requirements.nth(catalog.requirements.length() - 1).id == lifecycleRequirement.id,
      catalog.requirements.nth(catalog.requirements.length() - 1).revision == lifecycle.itemRevision,
      catalog.requirements.nth(catalog.requirements.length() - 1).status == lifecycle.itemStatus,
      (lifecycle.traceRevision == 0).implies(
        catalog.requirements.nth(catalog.requirements.length() - 1).traces.tests ==
          lifecycleRequirement.traces.tests
      ),
      (lifecycle.traceRevision == 1).implies(
        catalog.requirements.nth(catalog.requirements.length() - 1).traces.tests ==
          lifecycleRequirement.traces.tests.append("tests/model-trace-update.py")
      ),
    }),
  }

  val catalogWellFormed = all {
    catalogDataWellFormed(catalog),
    lifecycleRevisionTransitionIsSound,
    lifecycleRefinesCatalog,
  }

  run catalogContractTest = {
    init.then(all {
      assert(catalogWellFormed),
      catalog' = catalog,
      lifecycle' = lifecycle,
    })
  }

  run catalogAndSupersessionMutationRejectionTest = {
    init.then(all {
      assert(not(catalogHeaderIsValid(catalog.with("requirements", [])))),
      assert(catalogDataWellFormed(successionCatalog)),
      assert(supersessionChainsAreValid([successionR1, successionR2, successionR3])),
      assert(not(catalogDataWellFormed(successionCatalog.with("requirements", [successionR1])))),
      assert(not(catalogDataWellFormed(successionCatalog.with("requirements", [successionR1, successionRetiredTerminalR2])))),
      assert(not(catalogDataWellFormed(successionCatalog.with("requirements", [successionR1, successionCycleR2])))),
      assert(not(supersessionChainsAreValid([successionR1]))),
      assert(not(supersessionChainsAreValid([successionR1, successionRetiredTerminalR2]))),
      assert(not(supersessionChainsAreValid([successionR1, successionCycleR2]))),
      catalog' = catalog,
      lifecycle' = lifecycle,
    })
  }

  run atomicBatchTransitionContractTest = {
    init.then(all {
      assert(atomicBatchTransitionIsValid(batchBefore, batchAfterTwo, 5, [batchUpdateOperation, batchTraceOperation], "batch:two", "batch:change", "accepted")),
      assert(atomicBatchTransitionIsValid(batchBefore, batchAfterThree, 5, [batchUpdateOperation, batchTraceOperation, batchRetireOperation], "batch:three", "batch:change", "accepted")),
      assert(atomicBatchTransitionIsValid(batchBefore, batchBefore, 4, [batchUpdateOperation], "batch:stale-catalog", "batch:change", "rejected")),
      assert(atomicBatchTransitionIsValid(batchBefore, batchBefore, 5, [batchStaleOperation], "batch:stale-item", "batch:change", "rejected")),
      assert(atomicBatchTransitionIsValid(batchBefore, batchBefore, 5, [batchUpdateOperation, batchStaleTraceOperation], "batch:stale-after-valid", "batch:change", "rejected")),
      assert(not(atomicBatchTransitionIsValid(batchBefore, batchPartialAfterStale, 5, [batchUpdateOperation, batchStaleTraceOperation], "batch:stale-after-valid", "batch:change", "accepted"))),
      assert(atomicBatchTransitionIsValid(batchBefore, batchBefore, 5, [batchUpdateOperation, batchUpdateOperation], "batch:duplicate", "batch:change", "rejected")),
      assert(atomicBatchTransitionIsValid(batchBefore, batchBefore, 5, [batchInvalidOperation], "batch:invalid", "batch:change", "rejected")),
      assert(not(atomicBatchTransitionIsValid(batchBefore, batchInvalidAfter, 5, [batchInvalidOperation], "batch:invalid", "batch:change", "accepted"))),
      assert(catalogDataWellFormed(batchResurrectedAfter)),
      assert(atomicBatchTransitionIsValid(batchAfterThree, batchAfterThree, 6, [batchResurrectionOperation], "batch:resurrection", "batch:change", "rejected")),
      assert(not(atomicBatchTransitionIsValid(batchAfterThree, batchResurrectedAfter, 6, [batchResurrectionOperation], "batch:resurrection", "batch:change", "accepted"))),
      catalog' = catalog,
      lifecycle' = lifecycle,
    })
  }

  run lifecycleContractTest = {
    init
      .then(addRequirement)
      .then(updateRequirement)
      .then(updateRequirementTrace)
      .then(retireRequirement)
      .then(all {
        assert(catalogWellFormed),
        assert(lifecycleRefinesCatalog),
        assert(not(updateRequirementIsAllowed(catalog.catalogRevision, lifecycle.itemRevision))),
        assert(not(traceUpdateIsAllowed(catalog.catalogRevision, lifecycle.itemRevision))),
        catalog' = catalog,
        lifecycle' = lifecycle,
      })
  }

  run lifecycleCasRejectionTest = {
    init
      .then(addRequirement)
      .then(all {
        assert(not(updateRequirementIsAllowed(catalog.catalogRevision - 1, lifecycle.itemRevision))),
        assert(not(updateRequirementIsAllowed(catalog.catalogRevision, lifecycle.itemRevision - 1))),
        catalog' = catalog,
        lifecycle' = lifecycle,
      })
  }


  run refinementRejectsCounterOnlyMutationTest = {
    init
      .then(counterOnlyMutation)
      .then(all {
        assert(not(lifecycleRefinesCatalog)),
        catalog' = catalog,
        lifecycle' = lifecycle,
      })
  }
}
