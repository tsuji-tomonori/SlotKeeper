# APIの6帳票と構成profile

全operationを実公開契約から列挙し、グループ→API→帳票の階層とroot/group/API索引を生成する。実operation抽出は導入先adapterの責務であり、共通検査器はoperation ID JSON配列との集合一致を確認する。

[api-document-profile-v1.json](../assets/api-document-profile-v1.json)はlazunex固定版の実帳票を比較した版付き構成profileである。章名・順序・見出しlevel・繰返し節・非該当表現・配置を持つ。Routerという表現はendpoint層へ、直積という表現は実際に生成した組合せへ適応した。SQL非採用ではquery帳票へ理由を残す。別の構成を選ぶ場合は導入先profileのversionと差異・理由を記録する。

| 帳票 | 必要な意味内容（導入先adapterが検査する） |
|---|---|
| detail-design | 正常入力、前提、資源変更と入出力・条件、応答の取得元。実装の式を転載しただけでは完了しない |
| interface | Headers、Path/Query Parameters、Data、Responses、Samples。実公開契約と参照型・認証・制約・例を保持 |
| messages | 例外型→捕捉/再送出→HTTP status/body→ログID/level/message/項目型・マスク/運用対応。実loggerとの接続を追跡 |
| query | queryごとの種別、概要、保存先、束縛引数型、投影結果型・NULL、条件。所有先を含む識別子で衝突を拒否 |
| sequence | 実call graphの順序・条件・反復・例外・transactionからMermaidを生成。内部で捕捉し正常statusの失敗結果へ変換する経路も表示 |
| unit-test | 暗黙処理、要因/要素、到達する組合せ、自然言語Given/When/Then、期待ログ/状態、実collectorの検証単位。説明欠落・重複を拒否 |

## 章の検査

profileの`headings[kind]`は順序付きgrammar。`level/title`は固定節、`repeat/level/children/min`は繰返し節である。各operationの`sections`がquery/message/要因/caseの見出しを実装から列挙する。空を許す節では`non_applicable[key]`に理由を宣言し、profileの`empty`文を帳票に出す。必須章の削除・重複・順序入替・SQL節全体の欠落を検出する。コードfenceの中の見出しは数えない。

profile適合は内容の正しさを証明しない。adapterの構成検査には、実source集合、全operation、責務の実呼出し、型、例外、テスト対応の負例も含める。参照用帳票に載るサービスや定型認可を対象実装の事実として補完しない。

## CRUD

API×保存先のCRUDはquery一覧やER図と別のモデルである。参照先Rと変更先C/U/Dを区別し、DB以外の保存先にも同じ関係を使う。未解決動的呼出しは`unresolved`へ残して失敗させる。アクセスしないAPIは理由付き`no_access`へ明示する。

`check_design.crud_renderings(model)`は抽出を行わず、言語非依存JSONモデルからCSV・Markdown表・Mermaid・根拠JSONを決定的に射影する。導入先は同じ形式を使って4出力を生成する。全operation集合とCRUD集合、各rowのread/write根拠、4出力のbyte一致を共通検査器が検査する。根拠の意味と実到達性は導入先adapterが検証する。
