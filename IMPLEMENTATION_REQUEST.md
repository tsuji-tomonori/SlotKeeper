# SlotKeeper 実装指示プロンプト

作成日：2026-09-25

この文書を、SlotKeeperの対象リポジトリで作業する開発エージェントへ、そのまま渡してください。元の5案の要件定義書がなくても着手できるよう、製品要件を本文に含めています。

指定済みの技術条件はAstro、FastAPI、AWS、Python CDK、サーバーレス、Docker Composeによるローカル検証、GitHub Pagesの品質ポータルです。未指定部分の既定案として、AWSのDBにはAurora DSQL、認証にはCognito、ローカルのDBにはPostgreSQLを選んでいます。

---

## 1. あなたへの依頼

備品・会議室予約アプリ **SlotKeeper** を、以下の要件とdev-standardに基づいて実装してください。

設計案や雛形の提示で止めず、アプリ、DB定義、インフラコード、ローカル環境、実行可能なテスト、実装から生成する設計書、設計・品質ポータル、GitHub Actionsまで仕上げてください。既存コードがあれば内容を確認して再利用し、必要な修正を加えてください。

対象は現在の作業リポジトリです。新規のリポジトリ名の既定値は `slotkeeper`、製品表示名は `SlotKeeper` とします。既存リポジトリの大文字小文字や名前は変更せず、Pagesのbase pathも実際の名前から設定してください。

初回版の完成が対象です。末尾の「メンテナンス時間帯」の変更課題は、将来の変更追従性を評価するために残し、今回は実装しないでください。

## 2. 参照元と優先順位

### 2.1 固定する参照

| 対象 | URL | 参照revision |
| --- | --- | --- |
| 開発標準 | https://github.com/tsuji-tomonori/dev-standard | `5788b8671a74d08a230ade5d25c4719335cd7f71` |
| 品質ポータルの参照実装 | https://github.com/tsuji-tomonori/KotoRelay | `b0e460ea317b8c601eff6d13e871e1bdfdcf09f0` |
| ポータルの閲覧参考 | https://tsuji-tomonori.github.io/KotoRelay/ | 公開画面。固定revisionとの違いは区別する |

この指示、対象リポジトリの既存要件・運用規約、固定revisionのdev-standardの順に照合してください。意味のある矛盾は記録し、結果を変える点だけ確認してください。通常の配置・命名・実装方法は判断して進めてください。

参照revisionを無断で最新へ更新しないでください。取得できない場合も、参照できたものと未確認部分を区別し、実装可能な範囲を進めてください。

### 2.2 最初に読むもの

dev-standardでは、README、開発契約、Quint要件正本、既定4 Skillとその関連資料を読んでください。特に次を確認してください。

- `.agents/skills/generate-implementation-design/references/adoption.md`
- `.agents/skills/generate-implementation-design/references/adapter-contract.md`
- `.agents/skills/generate-implementation-design/references/api-documents.md`
- `.agents/skills/inspect-quality-gates/references/evidence-portal.md`
- manifest・API帳票profile・参照tools棚卸しの各schema

KotoRelayでは次を参照してください。

- `README.md`
- `docs/planning/DOCUMENT-STRUCTURE.md`
- `docs/planning/ER-VIEWER-UX.md`
- `frontend/portal/`
- `tools/project/design.py`、`api_documents.py`、`database_explorer.py`
- `tools/project/collector.py`、`evidence.py`、`verify.py`、`record_portal.py`
- `.github/workflows/quality.yml`

KotoRelayは、閲覧体験・生成方法・証跡の対応を参考にします。業務固有のRAG、Bedrock、文書承認、部署、ベクトル検索は移植しません。コードを流用する場合はライセンスと依存関係を確認し、採用範囲を記録してください。

## 3. 必須の技術構成

| 領域 | 指定 |
| --- | --- |
| フロントエンド | Astro＋TypeScript。静的ビルドし、必要な箇所にReact等のクライアントislandを使用する |
| バックエンド | Python＋FastAPI。Pydanticの入力・応答型を持ち、OpenAPIを生成する |
| AWS API実行 | API Gateway HTTP API＋通常のAWS Lambda。FastAPIのASGIアプリをMangum等の明示したadapterで接続する |
| アプリ配信 | 非公開S3 bucket＋CloudFront OAC。Astroの静的成果物を配信する |
| AWS DB | Aurora DSQL。単一リージョンの構成とし、アプリ用の限定権限で接続する |
| AWS認証 | Cognito User Pool。Authorization Code＋PKCEを使用する。一般利用者と管理者を判定できるようにする |
| IaC | AWS CDK v2のPythonコード。CDK CLI実行用のNode.jsもコンテナに含める |
| ローカル環境 | Docker Compose v2。PostgreSQL、ローカルOIDC provider、API、フロント、各種検証器をまとめる |
| 設計・品質ポータル | Astroを用いた静的サイト。GitHub Pagesに集約する。DB探索等にReact islandを使用してよい |
| 依存管理 | Pythonはuvとlockfile。Nodeは選択した1種類のpackage managerとlockfileに統一する |

Python、Node、Astro、FastAPI、CDK等のバージョンは、実装開始時に公式の互換性を確認して固定してください。Dockerイメージに無条件の `latest` を使わないでください。

EC2、常駐ECS/Fargate、常設アプリサーバー、NAT Gatewayを初期構成に追加しないでください。Astro SSRやサーバーislandへ依存する設計にせず、動的業務処理はFastAPIが担います。独自ドメインは必須にせず、AWSの既定ドメインで利用可能にしてください。

資源ID・予約IDの詳細画面は、静的なページ枠とクライアント側のAPI取得で実現してください。ビルド時に全予約を取得してページ化しません。クライアントルーティングを採用する場合はdeep linkの配信設定を設け、APIの404までHTMLへ置換しないでください。

DBは、本アプリの関係データ・トランザクションとサーバーレス条件を満たす既定案としてDSQLを採用します。将来、DSQLで使えないPostgreSQL機能が必須になった場合はAurora PostgreSQL Serverless等との比較をADRに記録します。今回は無断で別DBへ切り替えないでください。

### 3.1 リクエストと認証

- ブラウザから業務APIへアクセスします。API GatewayのJWT authorizerを構成し、FastAPI側でも認証済みsubjectと業務上の権限を検査してください。
- issuer、client/audience、token用途、署名、有効期限を検証します。Cognitoのaccess tokenとID tokenを混同しないでください。
- ローカルでは固定テストユーザーとJWKSを持つOIDC providerを使います。署名検証・期限・role判定を省略する認証バイパスは禁止です。
- 本番とローカルでclaimの違いを認証adapterに閉じ込め、業務層は同じ利用者モデルを使います。利用者IDやadmin指定を任意のHTTPヘッダーから信用しないでください。
- ブラウザの長期的なlocalStorageに認証トークンを保存せず、選択したライブラリのメモリ保持と再認証の動作を明記します。ログアウト時の破棄も検証してください。
- アプリ配信元、API、Cognitoのcallback/logout URL、CORSを環境ごとに接続します。認可ヘッダーを持つAPI応答を公開キャッシュへ保存しないでください。
- ローカルOIDCのissuerをブラウザとコンテナの双方から扱える設計にします。単に `localhost` をコンテナ間通信に流用しないでください。
- ローカルのテスト認証情報をAWSへ投入しません。ユーザー登録・パスワード管理画面を独自実装せず、認証基盤へ委ねます。

## 4. 製品要件

### 4.1 利用者と範囲

一般利用者は、会議室や備品の空き時間を確認し、自分の予約を作成・取消できます。管理者は、資源の登録・編集・無効化と、全利用者の開始前予約の取消ができます。

単一拠点、日本語UI、日本時間での運用とします。定期予約、参加者招待、通知、承認フロー、課金、複数資源の一括予約、多組織対応は対象外です。

### 4.2 共通要件

| ID | 要件 |
| --- | --- |
| COM-01 | 幅390pxと1280pxで主要操作ができ、ラベル、入力エラー、キーボード操作、可視フォーカスを備える。ページ全体に不要な横スクロールを出さない |
| COM-02 | 確定済みのデータは再起動後も残る。失敗操作で部分更新を残さない |
| COM-03 | 入力をサーバー側でも検証する。入力不正は422を基本とし、未認証401、権限不足403、対象なし404、業務・版競合409を区別する |
| COM-04 | サーバー側で本人と権限を判定する。UIの表示制御だけで権限を守らない |
| COM-05 | 起動・seed・リセット・全検証をCompose経由で再現できる。seedの乱数と評価用時刻を固定できる |
| COM-06 | 資源編集・予約取消等の同時更新で変更を消失させない。古い版は409とし再取得を案内する |
| COM-07 | 要求ID、操作、結果、所要時間を構造化ログに残す。認証情報・予約目的・生の例外本文を無条件に記録しない |
| COM-08 | 空、読込み中、入力不正、通信失敗、権限不足、競合、成功をUIで区別し、利用者が次の操作を判断できる |

### 4.3 機能要件

| ID | 必須機能 |
| --- | --- |
| SLOT-01 | 管理者が資源を登録・編集・無効化できる。無効資源への新規予約は禁止する |
| SLOT-02 | 資源と日付を指定して、その日の予約済み時間帯を確認できる |
| SLOT-03 | 資源、開始・終了、目的を指定して、自分名義の予約を作成できる |
| SLOT-04 | 同一資源の予約済み時間と重なる予約の確定を拒否する |
| SLOT-05 | 本人または管理者が、開始前の予約を取消できる |
| SLOT-06 | 自分の予約を日付・状態で絞り込める |
| SLOT-07 | 作成・取消の履歴を残し、権限のある利用者が詳細画面から確認できる |
| SLOT-08 | 要求の再送を識別し、予約と履歴を二重に作らない |

### 4.4 業務ルール

1. 予約区間は `[開始, 終了)` とします。10:00〜11:00と11:00〜12:00は重複しません。
2. 開始・終了は15分刻み、予約時間は15分以上4時間以下です。
3. 開始は現在より後、かつ現在から30日以内です。終了は開始と同じ日本時間の日付内にしてください。翌日00:00を終了とする予約も、この初期版では対象外です。
4. 保存時刻はUTCと対応付け、表示・入力はAsia/Tokyoとします。現在時刻は差替え可能なClockから取得します。公開APIで任意に現在時刻を上書きできないようにしてください。
5. 予約状態は `confirmed → cancelled` です。終了済みかどうかは時刻から判定し、状態として二重管理しません。予約日時の直接編集は提供しません。
6. 取消済み予約は重複判定から除きます。取消の確定と同時に、その枠を再予約できる状態へ戻します。
7. 既定の「将来予約」は `confirmed AND start_at > now` とします。開始済み予約の途中で資源が無効化されても、既存予約の記録は維持します。新規予約は拒否します。
8. 将来予約のある資源を無効化できません。予約作成と無効化が競合しても、無効資源に将来予約を残してはいけません。
9. 一般利用者には他人の目的・利用者識別情報・履歴を返しません。共有予約表では時間帯と「予約済み」を表示します。管理者は取消業務に必要な情報を閲覧できます。
10. 予約作成の要求キーは利用者単位で24時間有効です。同じキー・同じ正規化入力には元の成功応答を返し、異なる入力は409とします。有効期限後は新規要求として通常の重複判定を行います。
11. 成功済み要求の再送は、元の予約が開始・取消済みになっていても元の作成結果を返します。再送照合より先に現在時刻で新規予約の入力検証をしないでください。
12. 予約・履歴・要求キーの成功記録は、同一トランザクションで確定します。取消と取消履歴も一体で確定します。
13. 取消済み予約への取消は409とします。履歴を追加しません。
14. 資源名は空白除去後1〜100文字、説明は0〜1,000文字、予約目的は1〜200文字とします。一覧はページングし、順序と同順位時のID順を固定します。

### 4.5 画面

ログインのほか、資源一覧、資源別の日別予約表、予約作成、自分の予約一覧、資源管理を実装してください。予約詳細と履歴は独立ページまたは詳細パネルで閲覧可能にします。

予約表は色だけで状態を伝えず、時間と状態ラベルを表示します。入力中の目的や時間をエラーだけで消さないでください。競合時には最新の空き状況へ戻れる導線を付けます。管理者向けの操作には対象資源・予約を明示します。

## 5. バックエンドと整合性

### 5.1 実装構造

- Pythonのsrc layoutを使用し、API operation単位で所有先を分けてください。
- endpoint層が入力・認可・判定・transaction・個別処理の全体順序を所有します。endpointから直接DB I/Oは行わず、query等の個別処理を呼び出します。
- 実フローを巨大なservice関数へ丸ごと移し、endpointを単なる委譲にしないでください。具体的な責務と許可構文は固定dev-standardのprofileに合わせてください。
- 共有の認証、DB接続、Clock、トランザクション再試行等には所有先を設けます。別operationの内部実装へ直接依存しません。
- SQLをAPI別の正本ファイルで管理し、束縛引数型と結果型を生成してください。文字列補間で値をSQLへ埋め込みません。
- ドメイン例外とHTTP例外を分離し、境界で応答と運用ログへ変換してください。
- OpenAPIからフロント用の型・クライアントを生成し、手書き型との二重管理を避けてください。

### 5.2 データと競合制御

基本データはResource、Reservation、Userの業務属性、ReservationEvent、IdempotencyRecordです。排他制御に必要な補助データは根拠を記録して追加できます。

二重予約を、事前のSELECTだけで防いだつもりにしないでください。Lambda内のメモリロックや単一プロセスにも依存しません。

初期版では、**同じ資源の予約作成・取消・無効化が、同じ資源制御行をトランザクション内で競合対象にする方式**を既定とします。資源制御の内部版と、利用者が編集時に送る版は必要に応じて分離してください。

予約作成では、有効状態・時刻・重複を評価し、予約・履歴・冪等性記録を確定します。無効化では同じ競合境界に参加し、将来予約を確認してから無効化します。結果判定と更新を別transactionに分けないでください。実際に採用するSQLとcommit順序で不変条件を説明してください。

Aurora DSQLのOCC競合はcommit時にも発生します。`SELECT ... FOR UPDATE` を使う場合も、PostgreSQLと同じ待機ロックとは説明しないでください。最新の公式仕様に基づいて、transaction全体を新しいsnapshotで再実行します。

再試行対象は明示した一時的な競合等に限定し、最大試行回数・総時間上限・backoffを設定します。業務上の重複、権限不足、不正入力は再試行しません。内部競合を処理した後、予約済みなら409、再試行を使い切った基盤障害なら503等へ区別してください。

冪等性キーの同時登録競合も扱い、commit成否不明時には成功記録を再照合します。全例外を409へまとめたり、commit前に成功応答を返したりしないでください。

### 5.3 DSQLとPostgreSQLの差

- 共通の業務SQLとschemaモデルを基本にし、方言・migration・接続の差を明示したadapterへ閉じ込めます。
- ローカルのPostgreSQL結合テストでは、snapshotに関する前提を合わせるためRepeatable Readを基本にし、実際の分離レベルを証跡に残します。
- DSQLで使うDDL、索引作成、制約、transaction制限は実装時の公式仕様を確認します。ローカルだけで使える排他制約・trigger等に予約整合性を依存させません。
- DSQLのIAM認証・接続更新は公式connectorを優先します。アプリ用roleとmigration用roleを分け、アプリを常時管理者接続にしません。
- DSQL用migrationは非同期索引等の完了を確認し、再実行可能にします。大規模seedはサービス上限に収まるbatchへ分けます。
- ローカルの成功を、実DSQLの接続・SQL互換性・OCC確認済みと表現しません。実AWSの検証ケースも用意し、未実行なら明示します。

## 6. AWS CDKと配布成果物

Python CDKで、少なくともS3・CloudFront・API Gateway・Lambda・Cognito・DSQL・必要なIAM・CloudWatch Logsを定義してください。runtime、memory、timeout、ログ保持期間、環境名、リージョン、CORS等を明示します。日本向けリージョンを既定候補にし、対象サービスの利用可能性を公式情報で確認してください。

CDKのsynthとassertionはAWS認証情報なしで実行可能にします。通常のsynthでlive lookupや実AWSへの接続が必要にならないようにしてください。contextによる環境指定と、公開可能な設定例を用意します。

Lambdaは、Composeのパッケージ作成工程で依存を含めたZIPを作り、それをCDKが参照する方式を既定とします。LinuxとLambdaのarchitectureに合う依存を組み込み、エントリポイント、依存読込み、API Gatewayイベント変換をローカルテストしてください。

CDK実行コンテナからDocker daemonへ無制限に接続する構成を既定にしません。依存をビルドするコンテナとCDK synthを分離し、パッケージ成果物を共有してください。別方式を採用する場合も、ホストにPython・Node・CDKを要求しないことを守ります。

次をCDK assertionとcdk-nag等で確認してください。

- S3はpublic access blockを有効化し、CloudFrontだけに必要な読取りを許可する。
- APIの対象routeが認証で保護され、一般利用者が管理APIへ到達できない。
- IAMは対象resourceに絞る。抑制が必要な診断は理由と範囲を記録する。
- ログの保持、暗号化、データ削除保護を設定する。通常の更新で永続データを失わない。
- Cognitoの許可URL、DSQLの接続権限、Lambdaの設定、APIのCORSが環境設定と一致する。
- 認証不要のhealthは秘密・DB情報を返さない。readinessを用意する場合は用途と公開範囲を分ける。

CDKでのresource構築に加え、フロント成果物のS3配置、CloudFrontの必要な更新、DB初期化、Cognito初期管理者の作成手順まで接続してください。CDK出力値を使い、コピー＆ペーストでしか動かない手順にしません。環境固有の公開設定に秘密を混ぜず、アセット作成時に全利用者の情報を埋め込みません。

AWSの実デプロイ先account・region・roleが未確定なら、推測で作成せず、synth・検査・配布物・手順まで仕上げてください。実AWSへの展開と実測は、その実行環境で与えられた権限・依頼範囲に従います。

## 7. ローカル開発・テストをDocker Composeに統一する

### 7.1 ホストの前提

ホスト側に必要なのはGitとDocker Engine／Docker Desktop、Compose v2だけにしてください。Windows 11＋WSL2＋Docker Desktopでも使える構成とし、シェルの特殊機能やホストのPython・Node・Java・AWS CLIに依存させません。

依存取得はimage build時に行ってよいものとします。ローカルの通常検証に実AWS認証・AWS料金・外部の有料エミュレーターを要求しないでください。

### 7.2 Composeにまとめるサービス

| サービス例 | 役割 |
| --- | --- |
| `db` | 永続volumeを持つローカルPostgreSQL |
| `oidc` | 固定テストユーザーを持つローカル認証provider |
| `api` | Uvicornで動く同じFastAPI業務実装 |
| `web` | Astroの開発サーバー。検証profileでは静的build成果物を配信する |
| `migrate` / `seed` | ローカルDB初期化と固定データ投入。対象環境を検査する |
| `verify` | 全検証の順序、結果収集、終了コード、ポータル生成を管理するコンテナ |
| `docs` | 生成済み品質ポータルのローカル静的配信 |
| `perf` | API負荷試験。通常のverifyと別profileに分ける |
| `cloud-tests` | 明示実行時だけ実AWSを対象にする検証器。通常のverifyには含めない |

名前は実装上調整できますが、READMEと実際のコマンドを一致させてください。`verify`のimageには必要なPython・Node・Playwrightブラウザ・Quint runtime等を含め、ホストの実行環境へ処理を逃がさないでください。

依存serviceのhealthcheck、migration完了待ち、テストごとのデータ隔離、明示的な終了待ちを実装します。固定秒のsleepだけで起動順序を制御しません。複数の試験で同じDBを使う場合は衝突しないスキーマまたはデータ識別子を使い、開発データを消さないでください。

### 7.3 提供するコマンドの契約

以下の操作をこの形で提供してください。必要なprofile・service名を調整する場合は、完成時の実コマンドをREADMEへ反映してください。

```bash
# 初回起動。DB準備と開発用seedも依存関係として処理する
docker compose up --build --wait

# 全ローカル検証。異常系・生成設計・ポータル検証を含める
docker compose --profile test run --build --rm verify

# 検査対象を絞った日常実行
docker compose --profile test run --rm verify --suite backend
docker compose --profile test run --rm verify --suite frontend
docker compose --profile test run --rm verify --suite infra
docker compose --profile test run --rm verify --suite e2e
docker compose --profile test run --rm verify --suite design
docker compose --profile test run --rm verify --suite portal

# 実装由来設計を明示的に更新する。通常checkとは分ける
docker compose --profile test run --rm verify --generate-design

# 性能測定と、同一run内の結果を使ったポータル更新
docker compose --profile perf run --build --rm perf

# 保存した品質ポータルを閲覧する
docker compose --profile docs up --build --wait docs

# データを残して停止する
docker compose down
```

ここに示した`verify`のオプションは、これから実装する公開インターフェースです。現時点で存在するdev-standard標準コマンドとみなさないでください。

全検証は1つの`verify`コマンドで依存serviceの準備から完了します。先に手でnpm install、uv sync、migration、Playwright installを実行させないでください。ローカルのデータ削除を伴うリセットは別コマンドとして明示し、全検証に混ぜません。

`verify`は必要な検査を最後まで収集し、失敗を表示するポータルを作成してから、失敗があれば非0で終了します。途中の`|| true`や結果の上書きで失敗を隠しません。タイムアウト・クラッシュ時も、collector上の残りのケースを未実行・証拠不足として残してください。

## 8. dev-standardの導入と設計生成

### 8.1 導入と要件の正本

固定revisionのinstallerをdry-runし、差分を自分で確認してから適用してください。既存のAGENTS.md／CLAUDE.mdは管理領域の外を維持します。branch保護、merge方式、required checksは本依頼だけを理由に変更しません。

本書のCOM・SLOT要件と、技術・検証・公開の永続義務を、原子的な要件として `spec/requirements/requirements.qnt` へ登録してください。元のCOM・SLOT IDは保持します。受入条件、実装、設計、テストへのtraceを接続し、JSONと人向けMarkdownを生成します。

単なる文字列一覧を形式検証しただけで、予約整合性を証明したと言わないでください。業務状態をモデル化する場合は、モデルが表す範囲、境界、実装との対応、未証明の部分を記録します。

### 8.2 adapterの完成条件

- api/data/frontend/infraを棚卸しし、`.dev-standard/design.json` のschema version 2へ実際のgenerate/checkを接続する。
- 参照toolsの全件を比較し、採用・適応・拡張・非採用と理由、対象要件、実接続先を記録する。
- 少なくとも1つのMarkdown設計を各該当能力から生成し、出力rootと出力集合の所有を明示する。
- 2回のクリーン生成がバイト一致する。時刻、乱数、絶対path、環境差を決定的設計出力へ混ぜない。
- `--check`は既存生成物を書き換えず、欠落・変更・余剰・旧生成物・リンク切れを非0で報告する。
- verifyの冒頭で設計を上書きしてdriftを隠さない。検査と更新は別操作にする。
- Python、SQL、Astro、CDKの実際のsource・登録情報・schemaを解析する。抽出不能な領域を空の成功にせず、pathと理由を示す。
- manifestに並べた固定説明だけを、実装由来設計と呼ばない。

実行結果やrun時刻はrunごとの証跡として別に持たせます。決定的な設計出力と、実測結果を混ぜないでください。

### 8.3 必須の設計書

| 分類 | 内容 |
| --- | --- |
| 全体 | システム構成、ローカルとAWSの対応、責務、依存関係 |
| API | API一覧、認証・権限、operationごとの6帳票 |
| データ | テーブル・列の和名と物理名、型、制約、索引、関係、冪等性、transaction境界 |
| CRUD | APIと保存先のC/R/U/D、根拠source、表・図・CSV |
| フロント | 画面一覧、状態、入力、遷移、呼出API、権限、例外表示 |
| インフラ | CDK synth由来のresource・権限・接続・環境設定・デプロイ成果物 |
| テスト設計 | 要件→受入条件→要因・要素→ケース→実collector IDの対応 |
| 運用 | 起動、seed、検証、配布、DB更新、復旧、ログ確認、設定・秘密の扱い |

現在の構造は実装から生成します。採用理由や運用上の判断は手書きADR・運用書に分け、同じ現在状態を別の正本として重複管理しません。

APIの6帳票はDetail Design、Interface、Message、Query、Sequence、Unit Testです。`APIグループ → operation → 帳票` の階層と、固定dev-standardの版付きprofileに従ってください。KotoRelayの旧命名を理由に、現行profileを緩めないでください。

Sequenceは実際の呼出し順、認可、条件分岐、例外、transaction、retryから生成します。QueryはSQL種別、対象、束縛変数、戻り値、条件、原文を表示します。Unit Testには実在するテストだけを載せ、未達の網羅を完成扱いにしません。

## 9. テストの必須範囲

### 9.1 実行する検査

| 分類 | 検査内容 |
| --- | --- |
| Python | Ruff、mypy strict、Pyright strict、pytest。アプリ・infra・adapterを対象にする |
| フロント | Astro check、TypeScript strict、ESLint、format check、Vitest、静的build |
| API契約 | OpenAPI、入力・応答、認証・権限、フロント生成型、sampleとの一致 |
| 実DB結合 | PostgreSQLでtransaction、再起動、版競合、取消、冪等性、失敗時rollback |
| 並行実行 | 同じ枠の20同時予約、作成と無効化、取消と再予約、同一キー同時再送 |
| Lambda | 配布ZIPのimport、API GatewayイベントからASGIへの変換、JWT claimの境界 |
| インフラ | CDK synth、assertion、cdk-nag、設定別の差分・削除保護 |
| 設計 | Quint派生物、生成設計、型付きSQL、source集合、リンク、2回生成、未対応診断 |
| UI E2E | Chromiumで製品の主要操作と権限制御。390px／1280pxを検証する |
| ポータルE2E | 階層・検索・図・DB探索・画像拡大・深いリンク・狭い画面を検証する |
| 性能 | 指定データ量でAPI別p50/p95/p99、throughput、エラー、CPU・メモリを計測する |

実装がないテストファイル、空assert、結果の固定JSONだけで合格にしないでください。抑制・除外は理由と対象を記録し、後から分母を減らして合格にしません。

### 9.2 最低限の受入ケース

| ID | 操作・条件 | 期待結果 |
| --- | --- | --- |
| SLOT-AC01 | 空き資源へ翌日10:00〜11:00を予約 | 1件確定し、予約表・自分の一覧へ反映する |
| SLOT-AC02 | 既存10:00〜11:00に対して10:30〜11:30と11:00〜12:00 | 前者409、後者成功 |
| SLOT-AC03 | 空き枠へ20人が同時に予約 | 1件成功、19件409、重複0件。検査のために要求を直列化しない |
| SLOT-AC04 | Aの開始前予約をB・A・管理者が操作 | Bは403。本人・管理者は許可範囲で取消できる |
| SLOT-AC05 | 無効資源の予約、将来予約のある資源の無効化 | 両方拒否し、データは変化しない |
| SLOT-AC06 | 過去、現在と同時刻、0分、4時間超、30日超、15分未満の刻み、日跨ぎ | 入力エラー。境界値の15分・4時間・30日以内は正しく受け付ける |
| SLOT-AC07 | 成功応答を失った作成要求を同じキーで再送 | 元の予約IDと応答を返し、予約・作成履歴は各1件 |
| SLOT-AC08 | 日付・状態の絞込み、他人の詳細取得 | 自分の対象だけを返し、他人の目的・履歴は漏れない |
| SLOT-AC09 | 同じ要求キーに違う入力を送る | 409。元の予約を変更しない |
| SLOT-AC10 | 予約作成と資源無効化を同時実行 | 無効化と将来予約が両方確定する結果は0件 |
| SLOT-AC11 | 古い版で資源編集・予約取消 | 409。先に確定した値や履歴を失わない |
| SLOT-AC12 | 予約保存中・履歴保存中の障害、commit後の応答断 | 部分保存を残さず、応答断後の再送で二重作成しない |
| SLOT-AC13 | 開始時刻ちょうどの取消、取消済みへの取消 | 拒否し、履歴を増やさない |
| SLOT-AC14 | 不正署名、期限切れ、異なるissuer/client、role改ざん | 認証・認可を拒否し、DBは変化しない |
| SLOT-AC15 | 24時間経過前後のキー再使用、既存予約の取消後の再送 | 有効期間内は元の作成結果、期限後は新規要求の規則に従う |
| SLOT-AC16 | 起動・seed・アプリ再起動を繰り返す | 確定データを保持し、seedの無条件重複や開発データ消去を起こさない |

入力境界、権限、状態、競合の要因を分け、必要なケースを追加してください。代表的なUI E2Eには自然言語のGiven/When/Then、各段階のPNG、公開可能な期待値・実測値を持たせます。

### 9.3 検査器を試す負例

作業用コピーで1件ずつ変更し、次を検出するテストを実装してください。

1. API追加後に設計未更新。
2. SQLの参照先・更新先の変更後にCRUD未更新。
3. 生成Markdownの手編集・旧帳票の残存。
4. 要件に必要なテストの削除・collector IDの欠落。
5. 失敗・skip・未実行・flakyを含む実行結果。
6. 別revisionまたは別runの結果の混入。
7. adapter未対応の構文・実装surface。
8. sourceと和名辞書・列型・SQL結果型の不一致。

### 9.4 カバレッジと性能

手書きの業務コード・フロントの業務ロジックは、statement相当95%以上、branch90%以上を目標とします。Pythonでline coverageとして計測された値を、無条件にC0命令網羅と呼び替えないでください。生成コード、外部依存、テストコードは別区分にし、除外一覧を示します。adapter・infraのcoverageも別表示してください。

性能データは資源100件、利用者200人、予約10万件です。ローカルのアプリ＋DBに合計CPU 2コア相当・メモリ4GiBの制約を設け、負荷生成器は別枠とします。制約を適用できない環境は、その条件での参考値として表示します。

20並列、参照80%・作成取消20%、ウォームアップ2分後に5分測定を3回行います。予約表・自分の一覧はp95 500ms以下、作成・取消はp95 800ms以下を目標とします。予期しない5xx・timeoutは0.1%未満、整合性違反は0件です。

速度試験には十分な空き枠を用意し、競合試験と分けます。APIごとの件数、p50/p95/p99、成功・想定4xx・想定外エラー、資源条件、seed、revisionを保存してください。ローカル値をAWSのSLO達成として表示しません。AWSではcold/warm条件とDSQL接続条件を別途記録します。

## 10. GitHub Pagesの設計・品質ポータル

### 10.1 公開内容

アプリ本体はAWS、設計書と品質結果はGitHub Pagesへ配置します。KotoRelayのように、1つの入口から次を閲覧できる静的ポータルを作成してください。

| メニュー | 内容 |
| --- | --- |
| 概要 | revision、run ID、実行日時、環境、成功・失敗・未実行・欠落の件数 |
| 要件 | Quintから生成した要件と受入条件、実装・設計・テストへの対応 |
| 設計書 | 全体、API階層、画面、DB、CRUD、インフラ、運用 |
| DB探索 | テーブル・列・関係・DDL・API・SQLを相互にたどる画面 |
| 静的解析 | 検査名、コマンド、終了状態、公開可能な診断 |
| カバレッジ | 種別別の分母・分子・率、対象・除外、未計測の理由 |
| 単体・結合テスト | 階層、ケース、GWT、期待値、実測値、結果 |
| E2E | Given/When/Then各段階の説明・PNG、失敗段階、再試行の有無 |
| 性能 | データ量、測定条件、API別分位値、throughput、エラー、グラフ |
| AWS検証 | 実AWSでの対象ケースと結果。未実行ならその状態と理由 |

JUnit・Vitest・Playwright・coverage・静的解析の実出力をadapterで共通形式へ変換し、実collectorとの集合一致を確認します。`passed / failed / skipped / not-run / flaky / missing`を区別してください。分母0を成功率100%にしません。

### 10.2 閲覧機能

- APIグループ→operation→6帳票の階層を保持し、検索結果でも親階層と現在位置を示す。
- 日本語・物理名で検索し、左の章一覧・本文の目次から移動できる。
- Mermaidを実際の図として描画し、表示エラーを隠さない。
- 図・画像は拡大でき、Escapeで閉じ、元の操作位置へフォーカスを戻す。
- 深いリンク、更新、戻る・進む、Pagesのrepository base pathが動作する。
- 390pxでも本文や図がページ全体を横へ押し広げない。
- 色だけに頼らず状態名と数値を表示する。
- 原本のダウンロードは公開許可済みファイルだけに限定する。

### 10.3 KotoRelay相当のDB探索

左に一覧、中央に図、右に詳細を置き、小画面では切り替えて閲覧できるようにします。和名・物理名・併記、検索、拡大縮小、全体表示、選択位置への移動を実装してください。

列を選ぶと型、NULL、キー、説明、DDLを表示します。関係を選ぶと対応する列を示します。API・CRUD・SQL・同一revisionのソースへ移動できるようにします。

和名辞書は構造の正本にせず、DDLから得たtable/column集合と一致を検査します。実DDLにないFKをDB制約として描きません。アプリが保証する論理参照を表示する場合は、物理FKと区別し、宣言元を示します。

### 10.4 証跡の作成順と再現性

設計生成・実装検証→結果変換→ポータルbuild→ローカル静的配信→ポータルE2E→ポータル検証結果の追記、の順に処理します。

ポータル自身のテスト結果を載せるために、テストとbuildを無限反復しないでください。検証対象のbuild hashを記録し、結果追記後はリンク・schema等の最小確認を行います。追記で検証対象UIを変更した場合は、その影響範囲を再検証します。

過去runの成功画像・coverageで当該runの欠落を埋めません。異なるrunを比較表示するときも、それぞれのrevision・run ID・測定条件を保持します。フル検証、部分検証、性能だけの実行を明示し、部分検証を全件合格に見せないでください。

## 11. GitHub Actionsと公開

PRで検証と成果物生成を行い、信頼された公開対象branchのpushまたは許可された手動実行でPagesへ公開してください。既存の公開運用があればそれに接続します。

CIの検証処理も、ローカルと同じComposeの入口を使います。Actionsホストで別のpytest/npm/CDK手順を再実装しません。checkout、cache、artifact、Pages deploy等のCI固有操作はActions側で行って構いません。

次を満たしてください。

1. 検査失敗時も、結果変換・ポータル生成・原本artifact保存を可能な限り実行する。
2. テスト失敗をCIの非0に反映しつつ、有効な「失敗を示すポータル」は公開できる構造にする。
3. ポータルbuild・整合検査が失敗した場合は、古い成功サイトを新しい結果として再公開しない。
4. fork/未信頼PRのartifactを公開せず、PRコードへ公開権限・AWS認証情報を渡さない。
5. Pages公開jobだけに `pages: write` と `id-token: write` を付ける。その他は必要最小限にする。
6. 利用するActionsは実装時に公式のrevisionを確認し、SHAで固定する。
7. 同一公開先のconcurrencyを制御し、古い実行で新しい結果を上書きしない。
8. 生ログ、認証token、cookie、ブラウザstorage state、実ユーザー情報、DB dumpは公開allowlistへ入れない。画像は合成ユーザー・合成データを使う。
9. collector、変換後JSON、公開file hash、元結果の対応を保持し、同一run・revisionであることを検査する。
10. 公開先のbase path、図、検索、深いリンク、PNG、DB探索を、公開URLに対するsmoke testでも確認する。

GitHub Pagesへの集約・公開はこの実装依頼の成果範囲です。対象リポジトリの権限と既存運用で可能なら、公開と公開後確認まで進めてください。設定・権限が不足する場合も、アプリと検証、Pages artifact、workflowの実装を先に完成させ、残る操作を具体的に示してください。

PRの作成・更新は作業環境の権限と依頼範囲で行い、branch保護の解除や管理者例外によるmergeを、このプロンプトだけを根拠に実施しないでください。

## 12. 進め方と完了条件

### 12.1 実装順序

1. 対象リポジトリと参照元を確認し、dev-standardを導入する。
2. 要件正本、技術判断、Composeでの最小起動と実測結果の収集経路を作る。
3. 認証→資源一覧→予約作成→一覧・履歴の縦の流れを完成させる。
4. 取消、権限、版、冪等性、競合制御、失敗復旧を実装する。
5. CDK、Lambda配布物、DB migration、フロント配布を接続する。
6. 実装surfaceに対応する設計generatorを完成させ、初回生成・負例検証を行う。
7. KotoRelay相当のポータルへ実測結果を接続し、Composeで全検証する。
8. CIとPagesへ接続し、権限のある範囲で公開後確認まで行う。

各段階で必要な検査を選び、最後に全体の初回受入を行います。小さな修正のたびに無関係な全suiteを何度も回さず、変更理由と残存リスクで範囲を決めてください。

### 12.2 完了チェック

- [ ] Astroの実画面からFastAPIを通して、永続DB上で予約・取消ができる。
- [ ] COM-01〜08、SLOT-01〜08、本文の業務ルールと受入条件を検証している。
- [ ] 20同時予約、作成対無効化、同一キー再送で不変条件を守る。
- [ ] 全ローカル検証がDocker Composeだけで再現できる。
- [ ] Lambda配布物、Python CDK、認証・DB・静的配信が接続されている。
- [ ] Quintが永続要件の正本になり、派生文書が生成されている。
- [ ] manifest v2、参照棚卸し、実adapter、API6帳票、DB・CRUD・画面・infra設計がそろう。
- [ ] generatorの2回一致・drift・欠落・余剰・未対応の検出を確認している。
- [ ] ポータルが実collectorと実結果を表示し、GWT画像、coverage、性能結果へ到達できる。
- [ ] GitHub Pagesの公開workflowが動作し、公開できた範囲は実URLで確認している。
- [ ] 実AWSの未実行を、ローカル合格やsynth成功と混同していない。
- [ ] READMEに起動・検証・設計更新・データ初期化・公開・復旧の実コマンドがある。
- [ ] 空adapter、架空結果、未接続の雛形、黙ってskipした必須ケースを残していない。

### 12.3 最後の報告

以下を簡潔に報告してください。

1. 実装できた機能と、未完了の要件ID。
2. ローカル起動・全検証・ポータル閲覧のコマンドとURL。
3. 実行した検査の結果、対象revision、run ID、成果物path。
4. 構成適合、設計drift、実行テスト、未対応surfaceを分けた結果。
5. ローカルPostgreSQL検証、Lambdaイベント検証、CDK synth、実AWS検証の各実施状況。
6. GitHub Pagesの公開URLと公開後確認結果。未公開なら具体的な残作業。
7. 性能の測定条件と実測値、人の介入、標準導入・adapter・製品実装・検証に要した時間。取得できない指標は不明とする。

「ローカル実装完了」「Pages公開完了」「AWS実環境確認完了」を別々に示してください。未検証が残る場合、全面的な完了と表現しないでください。

## 13. 今回は実装しない変更課題

`SLOT-CHG01`：管理者がメンテナンス時間帯を登録できるようにする。将来の確定予約との重複を拒否し、新規予約との同時実行でも重複を許さない。

この課題は初回完成後に別途指示します。先回りで画面・API・テーブルを増やさず、現在の責務分離と変更後の要件・設計・テストの追跡で対応してください。

---

## 作成時に確認した資料

以下はプロンプト作成時の根拠です。参照実装のソースと構成を確認したものであり、この文書作成時にSlotKeeperの実装・AWSデプロイ・テスト・Pages公開を実施したという意味ではありません。KotoRelay公開画面のブラウザ動作も、この文書作成時には確認していません。

- [dev-standard README](https://github.com/tsuji-tomonori/dev-standard/blob/5788b8671a74d08a230ade5d25c4719335cd7f71/README.md)
- [dev-standard adapter契約](https://github.com/tsuji-tomonori/dev-standard/blob/5788b8671a74d08a230ade5d25c4719335cd7f71/.agents/skills/generate-implementation-design/references/adapter-contract.md)
- [dev-standard 品質portal契約](https://github.com/tsuji-tomonori/dev-standard/blob/5788b8671a74d08a230ade5d25c4719335cd7f71/.agents/skills/inspect-quality-gates/references/evidence-portal.md)
- [KotoRelay README](https://github.com/tsuji-tomonori/KotoRelay/blob/b0e460ea317b8c601eff6d13e871e1bdfdcf09f0/README.md)
- [KotoRelay 帳票構成](https://github.com/tsuji-tomonori/KotoRelay/blob/b0e460ea317b8c601eff6d13e871e1bdfdcf09f0/docs/planning/DOCUMENT-STRUCTURE.md)
- [KotoRelay DB探索](https://github.com/tsuji-tomonori/KotoRelay/blob/b0e460ea317b8c601eff6d13e871e1bdfdcf09f0/docs/planning/ER-VIEWER-UX.md)
- [KotoRelay 公開workflow](https://github.com/tsuji-tomonori/KotoRelay/blob/b0e460ea317b8c601eff6d13e871e1bdfdcf09f0/.github/workflows/quality.yml)
- [Aurora DSQLの並行制御](https://docs.aws.amazon.com/aurora-dsql/latest/userguide/working-with-concurrency-control.html)
- [Aurora DSQLとPostgreSQL](https://docs.aws.amazon.com/aurora-dsql/latest/userguide/working-with.html)
- [Astroのisland構成](https://docs.astro.build/en/concepts/islands/)
- [GitHub Pagesのcustom workflow](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
