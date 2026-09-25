# SlotKeeper

会議室と備品の空き時間を確認し、予約と取消ができる日本語アプリです。Astroの静的画面、FastAPI、PostgreSQL（AWSはAurora DSQL）、Cognito/ローカルKeycloakで構成します。

開発標準は `5788b8671a74d08a230ade5d25c4719335cd7f71` に固定しています。初回版の受入範囲は [実装指示](IMPLEMENTATION_REQUEST.md)、永続要件の正本は [Quint](spec/requirements/requirements.qnt) です。

## ローカルで使う

必要なものはGitとDocker Compose v2だけです。Windows 11ではWSL2とDocker Desktopを使用できます。

```bash
git clone https://github.com/tsuji-tomonori/SlotKeeper.git
cd SlotKeeper
docker compose up --build --wait
```

[アプリ](http://localhost:4321)を開いてログインします。ローカル専用の合成ユーザーは `alice`、`bob`、`admin`、パスワードは全員 `Local-test-2026!` です。AWSには投入しません。

## 検証と設計

```bash
docker compose --profile test run --build --rm verify
docker compose --profile test run --rm verify --suite backend
docker compose --profile test run --rm verify --suite frontend
docker compose --profile test run --rm verify --suite infra
docker compose --profile test run --rm verify --suite e2e
docker compose --profile test run --rm verify --suite design
docker compose --profile test run --rm verify --suite portal
docker compose --profile test run --rm verify --generate-design
docker compose --profile docs up --build --wait docs
```

品質ポータルは [http://localhost:4173/SlotKeeper/](http://localhost:4173/SlotKeeper/) です。原本は `artifacts/`、公開allowlistは `artifacts/site/`。検証DBは開発DBと別サービスで、開発データを削除しません。失敗を含むポータルを作成してから失敗の終了コードを返します。

`--generate-design` は専用のbind mountを通して生成物をホストへ書き戻します。通常検査は生成物を上書きせずdriftを報告します。

## 停止とリセット

```bash
# データを保持する
docker compose down
# ローカル開発データを明示的に全削除する（復元できません）
docker compose down --volumes
# 再起動時にschemaとseedを準備する
docker compose up --build --wait
```

## AWSと公開

アプリ本体は非公開S3＋CloudFront OAC、HTTP API＋通常Lambda、Cognito、Aurora DSQL。Python CDKで定義します。実AWS account・roleが未指定のため、本作業ではデプロイしません。合成・ZIP検査と実AWS検証は別です。

設計・品質の公開予定URL：<https://tsuji-tomonori.github.io/SlotKeeper/>。GitHub Actionsは同じCompose入口を実行し、信頼された既定branchだけからPages artifactを公開します。PagesのsourceをGitHub Actionsに設定する必要があります。

## 整合性

予約区間は `[開始,終了)`。同一資源の作成・取消・無効化は内部制御版を更新し、DSQLのOCC/ローカルのRepeatable Readで競合させます。成功時の予約・履歴・要求キーは同一commit。一般利用者へ他人の目的・識別情報・履歴を返しません。開始前だけ取消できます。

認証tokenはブラウザのメモリのみ。ページ再読み込み時は再認証します。PKCEの一時stateだけをsessionStorageへ置き、ログアウトでメモリを破棄します。
