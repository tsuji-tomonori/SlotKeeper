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

  pure val requirementsSource: Catalog = { schemaVersion: 1, catalogRevision: 1, product: "SlotKeeper", updatedAt: "2026-09-25", requirements: [{ id: "COM-01", revision: 1, status: "active", kind: "functional", title: "幅390pxと1280pxで主要操作ができ、ラベル、入力エラー、キーボード操作、可視フォーカスを備える。ページ全体に不要な横スクロールを出さない", subject: "SlotKeeper", actionName: "provide", objectName: "幅390pxと1280pxで主要操作ができ、ラベル、入力エラー、キーボード操作、可視フォーカスを備える。ページ全体に不要な横スクロールを出さない", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "COM-01-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "幅390pxと1280pxで主要操作ができ、ラベル、入力エラー、キーボード操作、可視フォーカスを備える。ページ全体に不要な横スクロールを出さない" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: ["backend/src/slotkeeper/app.py"], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "functional" }, { id: "COM-02", revision: 1, status: "active", kind: "functional", title: "確定済みのデータは再起動後も残る。失敗操作で部分更新を残さない", subject: "SlotKeeper", actionName: "provide", objectName: "確定済みのデータは再起動後も残る。失敗操作で部分更新を残さない", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "COM-02-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "確定済みのデータは再起動後も残る。失敗操作で部分更新を残さない" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: ["backend/src/slotkeeper/app.py"], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "functional" }, { id: "COM-03", revision: 1, status: "active", kind: "functional", title: "入力をサーバー側でも検証する。入力不正は422を基本とし、未認証401、権限不足403、対象なし404、業務・版競合409を区別する", subject: "SlotKeeper", actionName: "provide", objectName: "入力をサーバー側でも検証する。入力不正は422を基本とし、未認証401、権限不足403、対象なし404、業務・版競合409を区別する", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "COM-03-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "入力をサーバー側でも検証する。入力不正は422を基本とし、未認証401、権限不足403、対象なし404、業務・版競合409を区別する" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: ["backend/src/slotkeeper/app.py"], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "functional" }, { id: "COM-04", revision: 1, status: "active", kind: "functional", title: "サーバー側で本人と権限を判定する。UIの表示制御だけで権限を守らない", subject: "SlotKeeper", actionName: "provide", objectName: "サーバー側で本人と権限を判定する。UIの表示制御だけで権限を守らない", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "COM-04-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "サーバー側で本人と権限を判定する。UIの表示制御だけで権限を守らない" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: ["backend/src/slotkeeper/app.py"], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "functional" }, { id: "COM-05", revision: 1, status: "active", kind: "functional", title: "起動・seed・リセット・全検証をCompose経由で再現できる。seedの乱数と評価用時刻を固定できる", subject: "SlotKeeper", actionName: "provide", objectName: "起動・seed・リセット・全検証をCompose経由で再現できる。seedの乱数と評価用時刻を固定できる", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "COM-05-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "起動・seed・リセット・全検証をCompose経由で再現できる。seedの乱数と評価用時刻を固定できる" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: ["backend/src/slotkeeper/app.py"], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "functional" }, { id: "COM-06", revision: 1, status: "active", kind: "functional", title: "資源編集・予約取消等の同時更新で変更を消失させない。古い版は409とし再取得を案内する", subject: "SlotKeeper", actionName: "provide", objectName: "資源編集・予約取消等の同時更新で変更を消失させない。古い版は409とし再取得を案内する", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "COM-06-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "資源編集・予約取消等の同時更新で変更を消失させない。古い版は409とし再取得を案内する" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: ["backend/src/slotkeeper/app.py"], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "functional" }, { id: "COM-07", revision: 1, status: "active", kind: "functional", title: "要求ID、操作、結果、所要時間を構造化ログに残す。認証情報・予約目的・生の例外本文を無条件に記録しない", subject: "SlotKeeper", actionName: "provide", objectName: "要求ID、操作、結果、所要時間を構造化ログに残す。認証情報・予約目的・生の例外本文を無条件に記録しない", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "COM-07-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "要求ID、操作、結果、所要時間を構造化ログに残す。認証情報・予約目的・生の例外本文を無条件に記録しない" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: ["backend/src/slotkeeper/app.py"], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "functional" }, { id: "COM-08", revision: 1, status: "active", kind: "functional", title: "空、読込み中、入力不正、通信失敗、権限不足、競合、成功をUIで区別し、利用者が次の操作を判断できる", subject: "SlotKeeper", actionName: "provide", objectName: "空、読込み中、入力不正、通信失敗、権限不足、競合、成功をUIで区別し、利用者が次の操作を判断できる", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "COM-08-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "空、読込み中、入力不正、通信失敗、権限不足、競合、成功をUIで区別し、利用者が次の操作を判断できる" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: ["backend/src/slotkeeper/app.py"], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "functional" }, { id: "SLOT-01", revision: 1, status: "active", kind: "functional", title: "管理者が資源を登録・編集・無効化できる。無効資源への新規予約は禁止する", subject: "SlotKeeper", actionName: "provide", objectName: "管理者が資源を登録・編集・無効化できる。無効資源への新規予約は禁止する", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "SLOT-01-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "管理者が資源を登録・編集・無効化できる。無効資源への新規予約は禁止する" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: ["backend/src/slotkeeper/app.py"], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "functional" }, { id: "SLOT-02", revision: 1, status: "active", kind: "functional", title: "資源と日付を指定して、その日の予約済み時間帯を確認できる", subject: "SlotKeeper", actionName: "provide", objectName: "資源と日付を指定して、その日の予約済み時間帯を確認できる", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "SLOT-02-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "資源と日付を指定して、その日の予約済み時間帯を確認できる" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: ["backend/src/slotkeeper/app.py"], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "functional" }, { id: "SLOT-03", revision: 1, status: "active", kind: "functional", title: "資源、開始・終了、目的を指定して、自分名義の予約を作成できる", subject: "SlotKeeper", actionName: "provide", objectName: "資源、開始・終了、目的を指定して、自分名義の予約を作成できる", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "SLOT-03-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "資源、開始・終了、目的を指定して、自分名義の予約を作成できる" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: ["backend/src/slotkeeper/app.py"], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "functional" }, { id: "SLOT-04", revision: 1, status: "active", kind: "functional", title: "同一資源の予約済み時間と重なる予約の確定を拒否する", subject: "SlotKeeper", actionName: "provide", objectName: "同一資源の予約済み時間と重なる予約の確定を拒否する", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "SLOT-04-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "同一資源の予約済み時間と重なる予約の確定を拒否する" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: ["backend/src/slotkeeper/app.py"], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "functional" }, { id: "SLOT-05", revision: 1, status: "active", kind: "functional", title: "本人または管理者が、開始前の予約を取消できる", subject: "SlotKeeper", actionName: "provide", objectName: "本人または管理者が、開始前の予約を取消できる", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "SLOT-05-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "本人または管理者が、開始前の予約を取消できる" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: ["backend/src/slotkeeper/app.py"], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "functional" }, { id: "SLOT-06", revision: 1, status: "active", kind: "functional", title: "自分の予約を日付・状態で絞り込める", subject: "SlotKeeper", actionName: "provide", objectName: "自分の予約を日付・状態で絞り込める", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "SLOT-06-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "自分の予約を日付・状態で絞り込める" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: ["backend/src/slotkeeper/app.py"], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "functional" }, { id: "SLOT-07", revision: 1, status: "active", kind: "functional", title: "作成・取消の履歴を残し、権限のある利用者が詳細画面から確認できる", subject: "SlotKeeper", actionName: "provide", objectName: "作成・取消の履歴を残し、権限のある利用者が詳細画面から確認できる", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "SLOT-07-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "作成・取消の履歴を残し、権限のある利用者が詳細画面から確認できる" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: ["backend/src/slotkeeper/app.py"], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "functional" }, { id: "SLOT-08", revision: 1, status: "active", kind: "functional", title: "要求の再送を識別し、予約と履歴を二重に作らない", subject: "SlotKeeper", actionName: "provide", objectName: "要求の再送を識別し、予約と履歴を二重に作らない", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "SLOT-08-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "要求の再送を識別し、予約と履歴を二重に作らない" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: ["backend/src/slotkeeper/app.py"], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "functional" }, { id: "TECH-STACK", revision: 1, status: "active", kind: "constraint", title: "Astro静的フロントとFastAPIを使用する", subject: "SlotKeeper", actionName: "provide", objectName: "Astro静的フロントとFastAPIを使用する", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "TECH-STACK-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "Astro静的フロントとFastAPIを使用する" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: [], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "project", categoryName: "nonfunctional" }, { id: "TECH-DB", revision: 1, status: "active", kind: "constraint", title: "DSQLとPostgreSQLで共通の予約不変条件を守る", subject: "SlotKeeper", actionName: "provide", objectName: "DSQLとPostgreSQLで共通の予約不変条件を守る", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "TECH-DB-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "DSQLとPostgreSQLで共通の予約不変条件を守る" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: [], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "project", categoryName: "nonfunctional" }, { id: "TECH-AUTH", revision: 1, status: "active", kind: "constraint", title: "署名、issuer、client、用途、期限を検査する", subject: "SlotKeeper", actionName: "provide", objectName: "署名、issuer、client、用途、期限を検査する", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "TECH-AUTH-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "署名、issuer、client、用途、期限を検査する" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: [], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "project", categoryName: "nonfunctional" }, { id: "TECH-LAMBDA", revision: 1, status: "active", kind: "constraint", title: "依存を含むLinux用Lambda ZIPを作成する", subject: "SlotKeeper", actionName: "provide", objectName: "依存を含むLinux用Lambda ZIPを作成する", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "TECH-LAMBDA-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "依存を含むLinux用Lambda ZIPを作成する" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: [], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "project", categoryName: "nonfunctional" }, { id: "TECH-INFRA", revision: 1, status: "active", kind: "constraint", title: "Python CDKで常設サーバーを持たない構成を合成する", subject: "SlotKeeper", actionName: "provide", objectName: "Python CDKで常設サーバーを持たない構成を合成する", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "TECH-INFRA-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "Python CDKで常設サーバーを持たない構成を合成する" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: [], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "project", categoryName: "nonfunctional" }, { id: "TECH-COMPOSE", revision: 1, status: "active", kind: "constraint", title: "GitとDocker Composeだけで起動と全検証を行える", subject: "SlotKeeper", actionName: "provide", objectName: "GitとDocker Composeだけで起動と全検証を行える", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "TECH-COMPOSE-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "GitとDocker Composeだけで起動と全検証を行える" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: [], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "project", categoryName: "nonfunctional" }, { id: "TECH-DESIGN", revision: 1, status: "active", kind: "constraint", title: "実装から6帳票、DB、CRUD、画面、infraを決定的に生成する", subject: "SlotKeeper", actionName: "provide", objectName: "実装から6帳票、DB、CRUD、画面、infraを決定的に生成する", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "TECH-DESIGN-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "実装から6帳票、DB、CRUD、画面、infraを決定的に生成する" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: [], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "project", categoryName: "nonfunctional" }, { id: "TECH-PORTAL", revision: 1, status: "active", kind: "constraint", title: "同一revisionとrunの実測結果と設計をPagesへ集約する", subject: "SlotKeeper", actionName: "provide", objectName: "同一revisionとrunの実測結果と設計をPagesへ集約する", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "TECH-PORTAL-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "同一revisionとrunの実測結果と設計をPagesへ集約する" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: [], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "project", categoryName: "nonfunctional" }, { id: "TECH-PERF", revision: 1, status: "active", kind: "constraint", title: "指定負荷とデータ量でAPI別の性能を測定する", subject: "SlotKeeper", actionName: "provide", objectName: "指定負荷とデータ量でAPI別の性能を測定する", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "TECH-PERF-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "指定負荷とデータ量でAPI別の性能を測定する" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: [], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "project", categoryName: "nonfunctional" }, { id: "TECH-QUALITY", revision: 1, status: "active", kind: "constraint", title: "型、lint、実DB、ブラウザ、負例検査の失敗を隠さない", subject: "SlotKeeper", actionName: "provide", objectName: "型、lint、実DB、ブラウザ、負例検査の失敗を隠さない", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "TECH-QUALITY-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "型、lint、実DB、ブラウザ、負例検査の失敗を隠さない" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: [], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "project", categoryName: "nonfunctional" }, { id: "TECH-PRIVACY", revision: 1, status: "active", kind: "constraint", title: "公開allowlistに秘密や生ログを含めない", subject: "SlotKeeper", actionName: "provide", objectName: "公開allowlistに秘密や生ログを含めない", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "TECH-PRIVACY-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "公開allowlistに秘密や生ログを含めない" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: [], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "project", categoryName: "nonfunctional" }, { id: "RULE-01", revision: 1, status: "active", kind: "constraint", title: "予約区間は `[開始, 終了)` とします。10:00〜11:00と11:00〜12:00は重複しません。", subject: "SlotKeeper", actionName: "provide", objectName: "予約区間は `[開始, 終了)` とします。10:00〜11:00と11:00〜12:00は重複しません。", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "RULE-01-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "予約区間は `[開始, 終了)` とします。10:00〜11:00と11:00〜12:00は重複しません。" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: ["backend/src/slotkeeper/app.py"], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "nonfunctional" }, { id: "RULE-02", revision: 1, status: "active", kind: "constraint", title: "開始・終了は15分刻み、予約時間は15分以上4時間以下です。", subject: "SlotKeeper", actionName: "provide", objectName: "開始・終了は15分刻み、予約時間は15分以上4時間以下です。", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "RULE-02-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "開始・終了は15分刻み、予約時間は15分以上4時間以下です。" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: ["backend/src/slotkeeper/app.py"], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "nonfunctional" }, { id: "RULE-03", revision: 1, status: "active", kind: "constraint", title: "開始は現在より後、かつ現在から30日以内です。終了は開始と同じ日本時間の日付内にしてください。翌日00:00を終了とする予約も、この初期版では対象外です。", subject: "SlotKeeper", actionName: "provide", objectName: "開始は現在より後、かつ現在から30日以内です。終了は開始と同じ日本時間の日付内にしてください。翌日00:00を終了とする予約も、この初期版では対象外です。", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "RULE-03-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "開始は現在より後、かつ現在から30日以内です。終了は開始と同じ日本時間の日付内にしてください。翌日00:00を終了とする予約も、この初期版では対象外です。" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: ["backend/src/slotkeeper/app.py"], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "nonfunctional" }, { id: "RULE-04", revision: 1, status: "active", kind: "constraint", title: "保存時刻はUTCと対応付け、表示・入力はAsia/Tokyoとします。現在時刻は差替え可能なClockから取得します。公開APIで任意に現在時刻を上書きできないようにしてください。", subject: "SlotKeeper", actionName: "provide", objectName: "保存時刻はUTCと対応付け、表示・入力はAsia/Tokyoとします。現在時刻は差替え可能なClockから取得します。公開APIで任意に現在時刻を上書きできないようにしてください。", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "RULE-04-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "保存時刻はUTCと対応付け、表示・入力はAsia/Tokyoとします。現在時刻は差替え可能なClockから取得します。公開APIで任意に現在時刻を上書きできないようにしてください。" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: ["backend/src/slotkeeper/app.py"], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "nonfunctional" }, { id: "RULE-05", revision: 1, status: "active", kind: "constraint", title: "予約状態は `confirmed → cancelled` です。終了済みかどうかは時刻から判定し、状態として二重管理しません。予約日時の直接編集は提供しません。", subject: "SlotKeeper", actionName: "provide", objectName: "予約状態は `confirmed → cancelled` です。終了済みかどうかは時刻から判定し、状態として二重管理しません。予約日時の直接編集は提供しません。", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "RULE-05-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "予約状態は `confirmed → cancelled` です。終了済みかどうかは時刻から判定し、状態として二重管理しません。予約日時の直接編集は提供しません。" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: ["backend/src/slotkeeper/app.py"], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "nonfunctional" }, { id: "RULE-06", revision: 1, status: "active", kind: "constraint", title: "取消済み予約は重複判定から除きます。取消の確定と同時に、その枠を再予約できる状態へ戻します。", subject: "SlotKeeper", actionName: "provide", objectName: "取消済み予約は重複判定から除きます。取消の確定と同時に、その枠を再予約できる状態へ戻します。", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "RULE-06-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "取消済み予約は重複判定から除きます。取消の確定と同時に、その枠を再予約できる状態へ戻します。" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: ["backend/src/slotkeeper/app.py"], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "nonfunctional" }, { id: "RULE-07", revision: 1, status: "active", kind: "constraint", title: "既定の「将来予約」は `confirmed AND start_at > now` とします。開始済み予約の途中で資源が無効化されても、既存予約の記録は維持します。新規予約は拒否します。", subject: "SlotKeeper", actionName: "provide", objectName: "既定の「将来予約」は `confirmed AND start_at > now` とします。開始済み予約の途中で資源が無効化されても、既存予約の記録は維持します。新規予約は拒否します。", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "RULE-07-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "既定の「将来予約」は `confirmed AND start_at > now` とします。開始済み予約の途中で資源が無効化されても、既存予約の記録は維持します。新規予約は拒否します。" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: ["backend/src/slotkeeper/app.py"], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "nonfunctional" }, { id: "RULE-08", revision: 1, status: "active", kind: "constraint", title: "将来予約のある資源を無効化できません。予約作成と無効化が競合しても、無効資源に将来予約を残してはいけません。", subject: "SlotKeeper", actionName: "provide", objectName: "将来予約のある資源を無効化できません。予約作成と無効化が競合しても、無効資源に将来予約を残してはいけません。", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "RULE-08-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "将来予約のある資源を無効化できません。予約作成と無効化が競合しても、無効資源に将来予約を残してはいけません。" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: ["backend/src/slotkeeper/app.py"], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "nonfunctional" }, { id: "RULE-09", revision: 1, status: "active", kind: "constraint", title: "一般利用者には他人の目的・利用者識別情報・履歴を返しません。共有予約表では時間帯と「予約済み」を表示します。管理者は取消業務に必要な情報を閲覧できます。", subject: "SlotKeeper", actionName: "provide", objectName: "一般利用者には他人の目的・利用者識別情報・履歴を返しません。共有予約表では時間帯と「予約済み」を表示します。管理者は取消業務に必要な情報を閲覧できます。", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "RULE-09-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "一般利用者には他人の目的・利用者識別情報・履歴を返しません。共有予約表では時間帯と「予約済み」を表示します。管理者は取消業務に必要な情報を閲覧できます。" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: ["backend/src/slotkeeper/app.py"], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "nonfunctional" }, { id: "RULE-10", revision: 1, status: "active", kind: "constraint", title: "予約作成の要求キーは利用者単位で24時間有効です。同じキー・同じ正規化入力には元の成功応答を返し、異なる入力は409とします。有効期限後は新規要求として通常の重複判定を行います。", subject: "SlotKeeper", actionName: "provide", objectName: "予約作成の要求キーは利用者単位で24時間有効です。同じキー・同じ正規化入力には元の成功応答を返し、異なる入力は409とします。有効期限後は新規要求として通常の重複判定を行います。", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "RULE-10-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "予約作成の要求キーは利用者単位で24時間有効です。同じキー・同じ正規化入力には元の成功応答を返し、異なる入力は409とします。有効期限後は新規要求として通常の重複判定を行います。" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: ["backend/src/slotkeeper/app.py"], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "nonfunctional" }, { id: "RULE-11", revision: 1, status: "active", kind: "constraint", title: "成功済み要求の再送は、元の予約が開始・取消済みになっていても元の作成結果を返します。再送照合より先に現在時刻で新規予約の入力検証をしないでください。", subject: "SlotKeeper", actionName: "provide", objectName: "成功済み要求の再送は、元の予約が開始・取消済みになっていても元の作成結果を返します。再送照合より先に現在時刻で新規予約の入力検証をしないでください。", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "RULE-11-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "成功済み要求の再送は、元の予約が開始・取消済みになっていても元の作成結果を返します。再送照合より先に現在時刻で新規予約の入力検証をしないでください。" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: ["backend/src/slotkeeper/app.py"], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "nonfunctional" }, { id: "RULE-12", revision: 1, status: "active", kind: "constraint", title: "予約・履歴・要求キーの成功記録は、同一トランザクションで確定します。取消と取消履歴も一体で確定します。", subject: "SlotKeeper", actionName: "provide", objectName: "予約・履歴・要求キーの成功記録は、同一トランザクションで確定します。取消と取消履歴も一体で確定します。", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "RULE-12-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "予約・履歴・要求キーの成功記録は、同一トランザクションで確定します。取消と取消履歴も一体で確定します。" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: ["backend/src/slotkeeper/app.py"], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "nonfunctional" }, { id: "RULE-13", revision: 1, status: "active", kind: "constraint", title: "取消済み予約への取消は409とします。履歴を追加しません。", subject: "SlotKeeper", actionName: "provide", objectName: "取消済み予約への取消は409とします。履歴を追加しません。", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "RULE-13-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "取消済み予約への取消は409とします。履歴を追加しません。" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: ["backend/src/slotkeeper/app.py"], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "nonfunctional" }, { id: "RULE-14", revision: 1, status: "active", kind: "constraint", title: "資源名は空白除去後1〜100文字、説明は0〜1,000文字、予約目的は1〜200文字とします。一覧はページングし、順序と同順位時のID順を固定します。", subject: "SlotKeeper", actionName: "provide", objectName: "資源名は空白除去後1〜100文字、説明は0〜1,000文字、予約目的は1〜200文字とします。一覧はページングし、順序と同順位時のID順を固定します。", rationale: "利用者が指定した初回受入の永続義務", sourceRefs: ["IMPLEMENTATION_REQUEST.md"], acceptanceCriteria: [{ id: "RULE-14-AC", given: "対応する入力、権限、状態がある", when_: "仕様に対応する操作または検証を実行する", expected: "資源名は空白除去後1〜100文字、説明は0〜1,000文字、予約目的は1〜200文字とします。一覧はページングし、順序と同順位時のID順を固定します。" }], verification: { method: "実装と受入テストの照合", evidence: "同一runのcollectorと結果を品質ポータルに掲載" }, traces: { design: [], implementation: ["backend/src/slotkeeper/app.py"], tests: [], standards: ["dev-standard@5788b8671a74d08a230ade5d25c4719335cd7f71"] }, lastChangedBy: "initial-implementation", retirementReason: "", supersededBy: "", scopeName: "product", categoryName: "nonfunctional" }] }

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
