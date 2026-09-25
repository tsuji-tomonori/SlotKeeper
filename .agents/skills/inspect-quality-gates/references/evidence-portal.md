# 既定の品質エビデンス公開

## 適用と初期構築

開発開始時は利用者が製品要件だけを指定すればよい。agentは既存manifestとcommandを調べ、この仕組みを設計生成・選択検査の通常成果として接続する。追加Skillの選択や利用者によるfileコピーを待たない。新しいblocking柱は追加しない。

新規GitHubプロジェクトでは、初期実装に品質portalとGitHub Pages公開用のtarget-owned workflowを含める。既存プロジェクトでは既存CIと公開先へ接続し、branch、required check、merge、release設定を上書きしない。installer自身はworkflowをコピーしない。公開操作は既存の依頼・権限に従う。公開権限がない場合も生成・ローカル閲覧・workflowの準備までは完了する。非GitHub環境では同じ静的siteを既存artifact置場に接続する。

1. アプリの実装言語・framework・テストrunner・設計generator・既存CI・Pages設定を調べる。
2. 受入条件→要因→要素→ケースID→実装test→実行結果を対応させる。テスト一覧は実際のcollectorから作り、未実行ケースも残す。
3. 対象repositoryにadapterを実装し、実際のtest、lint、型検査、coverage、設計生成commandから以下のJSONを生成する。空template、サンプル結果、未接続adapterを完成としない。
4. `scripts/evidence.py build`でsiteを生成し、`check`で同じsourceからbyte一致を検査する。生成先はgitignoreしたrun固有directoryにする。
5. ブラウザで入口、階層一覧、検索、Given/When/Then、画像拡大とEscape/focus復帰、mobile横overflow、coverage分母分子、設計の検索・章一覧・目次・Mermaid表示を確認する。
6. 既存の実行結果を隠さない公開jobを接続し、結果を簡潔に報告する。通常の小さな変更へ全suite再実行や手書き恒久reportを一律追加しない。

## framework非依存adapter

共通rendererはPython標準libraryだけで動作し、アプリのframeworkを固定しない。adapterは対象側が所有し、原本と共通形式の対応をfixtureで検証する。標準出力をそのままHTMLへ貼らない。

| 原本例 | 共通形式への対応 |
| --- | --- |
| pytest / JVM / .NET等のJUnit XML | collectorの安定case ID、suite/file階層、parameterを保持し、failure/error/skippedと未実行を区別 |
| Vitest / Jest JSON | assertion単位でID、file、状態、期待値・実測値を取り込む |
| Playwright JSON | project/suite/spec/test階層、retry結果とflaky、GWT説明と選別PNGを保持 |
| Ruff / mypy / Pyright / ESLint等 | command、exit code由来の状態、公開可能な診断だけを取り込む |
| coverage.py JSON | linesとbranchesのcovered/totalを実測値から取得 |
| Istanbul / LCOV等 | statements/lines/branchesを区別して実測値を取得 |
| その他の言語・runner | 同じ共通契約へadapterを実装し、実データで検証する。未対応を対象外にしない |

同梱`test_evidence.py junit|vitest --input RESULT --inventory INVENTORY`で共通tests区分をJSONとして出力できる。inventoryは公開用metadata（id/name/group、任意のrequirement/factor/expected等）の配列。JUnitのIDは`classname::name`（classnameなしはfile、さらに省略ならsuite）、Vitestは`file name::fullName`。collector側も同じ規約へ変換し、他runnerは対象側adapterで補う。

collectorと結果のidentity集合を照合する。parametrized testを潰さず、未実行をnot-run、証拠不足をmissingとする。retry成功を無条件passedにしない。集計は失敗・skip・flaky・missingを残す。coverageのlineをC0命令と呼び替えず、statements（C0相当）、branches（C1相当）、linesを別表示する。分母0は成功率100%にせず、理由付き対象外または計測不足として扱う。

## 共通JSON v1

`evidence.py init --manifest <run>/evidence.json`は上書きせず未接続templateを作る。agentはその後adapterを接続する。共通JSONは公開用に選別した値だけを持つ。

```json
{
  "schemaVersion": 1,
  "revision": "actual-full-commit-sha",
  "runId": "run-123",
  "generatedAt": "2026-09-06T00:00:00Z",
  "tests": {
    "applicable": true,
    "inventory": ["unit/accounts::empty"],
    "items": [{"id": "unit/accounts::empty", "name": "空のIDを拒否する", "group": "unit/accounts", "status": "passed", "requirement": "REQ-1", "factor": "ID/空文字", "expected": "入力エラー", "actual": "入力エラー"}]
  },
  "e2e": {"applicable": false, "reason": "画面も外部APIもないlibrary", "items": []},
  "static": {"applicable": true, "items": [{"id": "typecheck", "name": "型検査", "command": "project-owned typecheck", "status": "passed"}]},
  "coverage": {"applicable": true, "items": [{"id": "unit-lines", "name": "単体テスト行網羅", "status": "passed", "metric": "lines", "tool": "coverage.py", "covered": 9, "total": 10}]},
  "design": {"applicable": true, "items": [{"id": "design", "name": "設計書", "status": "passed", "path": "design/index.html"}], "files": ["design/index.html"]}
}
```

これはschema例であり実績ではない。状態はpassed/failed/skipped/not-run/flaky/missing。coverage未計測や設計build失敗も`status: "missing"`と`detail`に理由を入れて表示できる。未計測coverageはcovered/totalを省略し、設計HTML未生成はpathを省略する。成功へ偽装したり架空の数値を埋めない。E2Eのpassedケースは`steps: [{"phase":"Given","text":"前提","image":"screenshots/given.png"}, ...]`にGiven/When/Then各段階の説明とPNGが必要。設計書の`files`はHTML、CSS、JS、検索index、図を含む公開済みbuildの明示allowlist。pathはmanifest配下相対、symlinkと`..`は禁止。rendererは任意directoryや生ログを再帰公開しない。

```sh
python .agents/skills/inspect-quality-gates/scripts/evidence.py build --manifest .devflow/reports/RUN/evidence.json --revision COMMIT_SHA --output .devflow/reports/RUN/site
python .agents/skills/inspect-quality-gates/scripts/evidence.py check --manifest .devflow/reports/RUN/evidence.json --revision COMMIT_SHA --output .devflow/reports/RUN/site
```

repository Pagesのroot相対linkを使う場合は`siteBase: "/repository/"`を設定する。内部HTML参照の欠落は生成時に拒否する。

revisionは実行checkout SHAから渡し、adapterは同一runの原本だけを入力にする。共通JSONと原本の対応・収集command・source hashは非公開artifactへ保持し、公開siteのprovenanceにはrevision/run IDと公開file hashを載せる。rendererは結果の真偽や原本の実行時刻を推測できないため、adapterで異なるrunの混入を拒否する。

## 設計書の公開adapter

実装由来MarkdownはStarlight等、対象側のdoc builderでHTML化する。アプリがReact/Vue/Python等のどれでも、doc builderは独立に選択可能。相対base path（`/<repository>/design/`等）、内部link、全文検索、日本語検索、左側章一覧、右側目次、Mermaidの実際の描画を確認する。MarkdownやMermaid code fenceをそのまま見せて完了としない。

APIがある場合、Detail Design（処理ごとの入出力・DB/table操作）、Interface（Swagger/OpenAPI）、Message（ログ）、Query（対象table・SQL種別・概要・引数・戻り値・条件）、Sequence（Mermaid）、Unit Test（要因・要素・ケース詳細・実装対応）の6領域すべてへ到達できるようにする。該当範囲の欠落・drift検査は設計生成側で行う。

## GitHub Pages接続

agentは対象の言語setupと既存commandに合わせ、次のjob構造をtarget-owned workflowへ実装する。placeholderを残したworkflowを完成としない。

- 検査job: checkoutの実SHAを取得し、各commandの終了状態を収集する。後続が走れるようにしても、最後に元の失敗状態を非zeroへ戻す。
- 常時実行するreport段階: `always()`相当でadapter・設計build・site生成・UI検証を行う。検査失敗時も失敗を表示したsiteを作り、原本と公開siteを別artifactへ分ける。renderer自体の失敗は古い成功siteで代替しない。
- 公開job: trusted branchへのpushまたは許可された手動実行だけ。PRやfork由来artifactは公開しない。branch名は現行設定から解決し`main`/`dev`を固定しない。
- 検査失敗時にもreport artifactが有効なら公開できるよう、needsの暗黙success条件を避ける。report失敗時はdeployしない。
- GitHubのconfigure-pages、upload-pages-artifact、deploy-pagesを利用し、利用時点の公式action SHAを固定する。公開jobのみ`pages: write`と`id-token: write`、environmentは既存Pages設定を使用する。不要なcontents writeは付けない。
- 同じ公開先へのconcurrencyを設定し、古い実行で新しいsiteを上書きしない。初回はPagesのsource設定と公開範囲を確認する。
- 公開allowlistを検査し、secret、PII、production dump、生ログ、認証画像を除外する。HTML/JSの設計buildは信頼された同一checkoutからのみ採用する。

公開先の可視性をrepositoryのprivate/publicから推測しない。公開権限・環境設定待ちは検査やsite生成成功と分けて報告する。

## 受入確認と出典

新規導入fixtureと既存CIありfixtureの両方で、利用者の追加設定なしでagentが実commandへ接続できることを確認する。少なくとも異なる2系統のrunnerでschema変換を検証し、失敗、未実行、欠落、対象外、古いrevision、漏れたcollector IDを試す。

移植元: [CornellNoteWebv2 dev](https://github.com/tsuji-tomonori/CornellNoteWebv2/tree/dev)のREQ-REPORT、tools/report.py、tools/test_results.py、tools/docs_site.py、frontend/report-tests/report.spec.ts、.github/workflows/verify.yml。製品固有のAWS・認証・branch運用は移植しない。
公開jobの仕様: [GitHub Pages custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)。


## API設計の階層

各design itemの`hierarchy`へ`["group", "API"]`の親ラベルを設定する。item名を葉の帳票名とし、`path`は公開allowlist内のHTMLとする。従来の`group`だけのreportも読める。検索は階層名も対象とし、該当帳票の祖先を展開して残す。葉の移動で現在位置とaria-currentを更新する。

CRUD itemは`diagram`へ生成SVG、`download`へCSVの相対pathを指定し、両方をdesign.filesのallowlistへ含める。モデルから生成した表・図・CSVを結合し、エビデンスrenderer側でCRUDを再推測しない。通常の生成HTMLの帳票間linkを維持する。

参照repositoryのブラウザ回帰は`npm run test:evidence-hierarchy`。Chromiumを`npx playwright install chromium`で準備するか、既存browserを`PLAYWRIGHT_CHROMIUM_EXECUTABLE`で指定する。GWT画像・ブラウザ結果は一時実行領域へ出力し、任意の公開・CI変更は行わない。
