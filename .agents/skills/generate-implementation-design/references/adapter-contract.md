# 言語非依存adapter契約

契約の検査器は導入先言語のsourceを解析しない。実装担当は参照toolsを全件比較し、導入先のparser・型検査・公開契約export・test collectorで次の能力を実装する。既存adapterがある場合も同じ受入条件で不足を補う。

## 能力と受入条件

| 能力 | 導入先adapterが検査・生成すること |
|---|---|
| 所有と責務 | 1 operation 1所有単位、入力/応答型・応答組立・契約・sample・queryの実接続。空・未参照・旧集約処理への単純委譲を拒否。共有責務に所有者を付け、API間の別名/相対参照も含む直接依存を拒否 |
| endpointの全体フロー | 処理順・分岐・例外・transactionをendpoint層が所有する。個別処理への全体フローの逆流とendpointからの直接DB/provider I/Oを拒否。worker共有flowも所有者・実呼出しを検証 |
| endpoint専用profile | 許可symbol集合と全sourceの走査を定義。同期/非同期の補助処理、class/method、入れ子、lambda、未登録endpointを負例に含める。登録済み入口だけ走査して完了しない |
| 戻り値（REQ-DESIGN-018/019） | 同期/非同期の意味ある戻り値の単独破棄と、同じ定数真偽値だけを返す判定処理を拒否。別名呼出しも実体照合し、検証専用の値なし処理と結果を使う処理を正例にする |
| 例外境界（REQ-DESIGN-020/021） | 全例外・基底例外・別名/集合に隠れた包括的捕捉と、業務層からの通信層固有例外の送出を拒否。宣言済みの具体的例外と境界層の応答変換を同期/非同期で検証 |
| 処理説明（REQ-DESIGN-022） | 選択profileの処理単位に自然言語の責務説明を要求し、docstringや文書コメントの欠落・空白を拒否。説明言語は既存要件に従う |
| 逆依存（REQ-DESIGN-023） | 個別処理からendpoint/共有workflowへの逆依存を別名/相対参照も含め拒否。正当なworker共有workflowの所有者・実呼出しを設計へ追跡 |
| query型 | SQL採用時は所有先を含む一意IDと束縛引数だけの厳格型、SELECT投影とNULLに一致した結果型を生成。余剰引数・投影削減・型/NULL不一致・欠落/手編集/SQL変更の負例を検査。SQL非採用へSQL層を要求しない |
| 制御フロー設計 | 実call graphの順序・条件・反復・例外・transactionをsequenceへ投影。呼出し順/条件の変更が図を変えることを検査。定型図で未解析箇所を補完しない |
| 例外とログ | 例外型→catch/rethrow→HTTP status/body→ログID/level/message/運用対応を対応させる。内部catchによる正常statusの失敗結果も区別。型不整合、機密を含む依存例外、応答未解決の負例を検査。生例外・本文・tokenをログへ漏らさない |
| test設計 | 自然言語GWTを実collectorの検証単位へ対応。fixture名/式の転載は説明の代わりにしない。説明欠落/重複・未実在test・要因欠落を拒否。実行結果とassert妥当性を生成driftから区別 |
| その他のsurface | dataの属性/制約/関係/CRUD、infraの構築artifact・権限/参照/flow、frontendの画面/状態/依存を実装から生成する。未接続を省略理由にしない |

参照追従時は`REQ-DESIGN-024`に従い、固定SHAと実装・生成器・規則・関連testを比較し、責務の粒度と適用範囲・理由付き適用外を導入先の要件とprofileへ記録する。例外/logger/query型/帳票の意味まで比較対象にし、参照固有のframeworkや閾値を無条件移植しない。責務移行では`REQ-DESIGN-025`に従い、HTTP契約・commit/rollback・外部呼出し前後の認可などの既存挙動を同一revisionの関係する実行テストで検証する。

正本の詳細は`spec/requirements/requirements.qnt`（`REQ-ASBUILT-*`、`REQ-DESIGN-*`、`REQ-DOCS-*`、`REQ-EVIDENCE-*`）。言語・frameworkの具体的な実装は導入先が所有する。

## Manifest v2

配置は既存の`.dev-standard/design.json`を使用する。[schema](../assets/adapter-manifest.schema.json)が構造の正本である。`check_design.py --contract <相対path>`で別配置も指定できる。

- `requirements`: active IDを読むQuint派生JSON。未知・inactive IDを拒否する。
- `applicable_requirement_ids`: 適用要件の明示集合。capabilityの`requirement_ids`の和集合と完全一致させる。適用外catalog要件を無条件要求しない。
- `reference_inventories`: 導入先の`target-adoption`棚卸しJSONのpath配列。適用要件全件がtoolまたは明示gapに対応する。配布blueprintだけでは導入完了しない。
- `surfaces`: api/data/infra/frontendを必ず分類し、固有領域も追加する。`status: required`なら`capabilities`に接続IDを列挙。`not-applicable`なら実装がない理由を記す。
- `capabilities`: IDをkeyとするobject。各能力は`requirement_ids`と`status`を持つ。非該当には`reason`、requiredには`sources`、`generate`、`check`、`output_root`、`outputs`、`report`を必須とする。
- `generate` / `check`: shell文字列ではなくargv配列。checkには`--check`を含め、同じ生成logicで書換えずに比較する。commandは信頼済みローカル処理で、公開/production操作を含めない。
- `output_root`: そのcapabilityが完全所有する相対directory。他capabilityと重複/包含させない。`outputs`はその下の全fileを個別列挙する。空・欠落・旧生成物・余剰directory・symlink・directoryのfile置換・管理外pathを拒否。少なくとも1つの非空Markdown設計を含める。
- `report`: 所有出力内のJSON。以下の4項目だけを持ち、未検証のテストは`not-run`とする。

```json
{
  "configuration": "pass",
  "design_drift": "pass",
  "execution_tests": "not-run",
  "unsupported_surfaces": []
}
```

未対応診断は`unsupported_surfaces`へpath・処理単位・行・構文種別・理由・support statusを記載する。1件でも残れば合格しない。意味解析と実行testを共通検査器が実施したと誤表示しない。配置検査のpassはHTTP互換性やDB transactionの回帰成功を意味しない。

## APIとCRUDの追加項目

`surfaces.api.status: required`なら`api`と`crud`が必要である。

`api`は次を持つ。

- `profile`: [profile schema](../assets/api-document-profile.schema.json)に適合するversion付き構成profileのpath。固定節と繰返し節、level、最小件数、理由を含む非該当表現を検証する。配布済みID・版の章構成は変更できず、独自構成は別IDまたは版を明示する。
- `operation_inventory`: adapterが実登録集合から生成した重複のないoperation IDのJSON配列のpath。
- `root`、`index`: 所有するAPI帳票rootと`<root>/index.md`。
- `group_indexes`: group名→`<root>/<group>/index.md`。
- `api_indexes`: operation ID→`<root>/<group>/<api>/index.md`。
- `operations`: `id/group/api/documents/sections`を持つ配列。`documents`は6帳票kind→path、`sections`はprofileのrepeat key→実装から列挙した見出し配列。空節には`non_applicable[key]`を付ける。

`crud`は`model/csv/table/diagram/evidence`の5pathを持つ。すべて所有出力に含める。モデルの最小例:

```json
{
  "schema_version": 1,
  "operations": ["getItem", "health"],
  "rows": [{
    "operation": "getItem", "resource": "inventory.items", "access": ["R"],
    "evidence": [{"path": "src/item.query", "line": 1, "role": "read"}]
  }],
  "no_access": {"health": "依存先へアクセスせず稼働状態を返す"},
  "unresolved": []
}
```

1つのoperation/resourceにつき1rowとし、accessはC/R/U/Dの集合。読み書き両方ならread/writeの根拠を別々に持つ。`crud_renderings`の出力形式によりCSV・表・図・根拠を照合する。これは関係モデルの射影でありSQL parserではない。

## Markdownリンクの検査

[CommonMarkのリンク構文](https://spec.commonmark.org/0.31.2/#links)に基づき、inline/image、山括弧付き宛先、平衡括弧・escape、単一/二重引用符・括弧title、明示/省略参照と定義を解析する。参照labelは大文字小文字と空白を正規化し、宛先の文字参照とURL encodingを解決する。コードfenceとinline codeの例はリンクにしない。外部URLは取得しない。

完全なMarkdown rendererではない。HTMLリンク、container内の参照定義など未対応の明示リンクや解析不能な宛先はsourceと行を示して失敗する。未定義の明示参照も拒否する。通常の角括弧だけの文章を未定義リンクとはみなさない。

## 参照tools棚卸し

[reference-inventory.schema.json](../assets/reference-inventory.schema.json)は参照実装に依存しない。repository URL、固定40桁Git revision、source_root、全件数、パス/blob一覧のSHA-256、対象要件ID、全fileとgapを記録する。fileごとに用途、分類、要件ID、採用区分、理由、固有前提、実接続先を持つ。

`adopt`は挙動を保持して採用、`adapt`は言語/型/配置を適応、`extend`は参照に不足する契約を追加、`not-adopted`は理由を付けて非採用。配布表は`reference-blueprint`、実導入は`target-adoption`で区別する。実導入では採用fileの全`connections`が導入先の実fileを指す。gapは参照との差分であり、未実装を許可する免除ではない。

```sh
python <host-skill-path>/scripts/reference_inventory.py <inventory.json> --requirements spec/requirements/requirements.json --target-root . --out <一覧.md>
python <host-skill-path>/scripts/reference_inventory.py <inventory.json> --requirements spec/requirements/requirements.json --target-root . --out <一覧.md> --check
python <host-skill-path>/scripts/reference_inventory.py <inventory.json> --requirements spec/requirements/requirements.json --target-root . --reference-root <ローカル参照clone>
```

最後の照合は固定commitのGit tree/blobを読む。参照cloneを変更せず、ネットワークも使わない。オフラインの回帰では構造・件数・一意性・要件coverageと固定tree digestを検査する。

## 実行境界と検査順

検査器はmanifest・出力の現在状態を先に検査する。その後repositoryの作業用コピーで非破壊の`--check`を実行する。所有出力rootを毎回空にしてクリーン生成を2回行い、それぞれ既存出力とのbyte一致・生成集合・管理外tree不変性を確認する。元repositoryへ生成し直して古い設計を隠さない。commandはコピーのcwdを基準に相対入出力を使い、cacheも含むすべての書込みを所有出力へ限定する。

作業用コピーはOS sandboxではなく、信頼済みcommandの絶対path・network等の外部作用は隔離しない。依存runtimeと実行環境は導入先が管理する。未宣言source・動的な実行時意味の完全性は共通検査だけでは証明できず、導入先のsource集合照合と負例試験を併用する。既存branch/CI/merge/PR templateは変更しない。
