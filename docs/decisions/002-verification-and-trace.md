# 検証経路と要件traceの判断

## 背景

初回CI（`feat/initial-release`）で、OpenAPI型のdrift、アプリE2Eのログイン後遷移、ポータルE2Eの図の拡大が失敗した。Quint要件の受入条件は定型文で、テストへのtraceが空だった。

## 判断

- **E2Eの到達経路**：Playwrightの`page.route`でlocalhostを各サービスへ書き換える方式は、Keycloakの302応答を`route.fulfill`した後の遷移がrouteを通らず失敗した。verifyコンテナ内でlocalhostの4321/8000/8080を`web`/`api`/`oidc`へTCP転送する（`e2e/forward.ts`）。ブラウザは利用者と同じissuer・callback URLを使い、認証検証を省略しない。
- **ログアウト**：token破棄後もOIDC sessionを終了する。Keycloakは`id_token_hint`付きend session、CognitoはOIDCのend_session_endpointを公開しないためHosted UIの`/logout`（`config.json`の`logoutUrl`）を使う。
- **ポータルの図**：Layoutのscriptでtop-level awaitを使うと、Mermaidが遅延読込する図チャンクがLayoutチャンクの評価完了を待ち、`mermaid.run`と循環待ちになる。描画処理を関数へ移し、module評価を先に終える。
- **DB探索のデータ**：`define:vars`はJSON用scriptをJSのIIFEへ変換するため使わない。`is:inline`で埋め込み、`<`を`<`へエスケープする。
- **OpenAPI型**：`artifacts/`は`.gitignore`対象でprettier CLIが整形を省くため、生成・検査とも`tools/frontend.mjs`がprettier APIで整形する。
- **要件trace**：受入条件IDをテスト説明に`[ID]`で付け、設計生成器（`trace()`）が「全受入条件に実在テストまたはverify検査名がある」「未知IDがない」「参照元fileが要件の`traces.tests`にある」を検査する。結果は`TRACE.md`/`trace.json`とポータルの要件ページに出す。これはテスト存在の照合であり、テスト内容の十分性や予約不変条件の証明ではない。
- **CDK環境**：`-c env=dev|prod`で`infra/environments/*.json`を読み、未定義の環境は拒否する。accountは実行時の認証情報に委ね、synthはlookupしない。
- **性能run**：`perf`は`verify --performance-only`としてポータルまで同一runで更新する。scopeは`performance-only`と表示し、テスト結果を含む全件合格には見せない。
- **実AWS検証**：`cloud-tests`はhealth・JWT境界・cold/warm応答と、合成資源を指定した場合のDSQL上の20同時予約を検査し、同じrevision・runでのみポータルへ取り込む。未実行は`not-run`のまま表示する。

## ローカル検証環境の注記

この判断を検証した作業環境では、ghcr.io・quay.io・Debian aptへの到達がproxyで拒否された。Dockerfileとcompose.yamlは変更せず、作業環境専用の上書き（Docker HubのKeycloak、PyPIのuv wheel、MCRのPlaywright image）で同じCompose入口を実行した。CIは本来の定義で実行する。
