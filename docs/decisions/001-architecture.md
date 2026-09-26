# 初回構成の判断

- ユーザー指定：Astro静的生成、FastAPI、通常Lambda、Python CDK、DSQL、Cognito PKCE、Compose、Pages。
- 参照固定：dev-standard `5788b8671a74d08a230ade5d25c4719335cd7f71`、KotoRelay `b0e460ea317b8c601eff6d13e871e1bdfdcf09f0`。
- KotoRelayの閲覧構造とgenerator/collectorの責務を参照。LICENSEファイルを確認できなかったため、そのコードはコピーしない。業務固有のRAG、部署、文書承認は移植しない。
- 資源の内部 `control_version` を作成・取消・編集の共通書込み境界にする。公開 `version` は利用者の編集競合に使用する。内部競合で無関係な画面の版を変えない。
- PostgreSQLではRepeatable Read、DSQLではOCC。成功commit時に同資源の並行書込みを両方通さない。競合失敗時はsnapshotを新しくして有効状態と重複を再評価する。プロセス内ロック、排他制約、triggerに依存しない。
- アプリ側の参照整合性を明示する。DSQLに存在しない物理FKを図に描かない。
- 本人または管理者にだけ目的と履歴を返す。共有予約表は開始・終了と予約済みラベルだけ。
- tokenはメモリ、PKCE stateはsessionStorage。再読み込み時は再認証。再送キーは入力が同じ間はメモリで維持し、成功後に破棄。
- FastAPI 0.141のinclude_routerは遅延登録形式のため、実登録を再帰的に抽出し、OpenAPIとの全件一致を検査する。
- CDKのnag抑制はコード中にIDと理由を個別記録。公開health以外をJWTで保護する。

## 公式資料（実装時確認）

- https://docs.aws.amazon.com/aurora-dsql/latest/userguide/working-with-concurrency-control.html
- https://docs.aws.amazon.com/aurora-dsql/latest/userguide/working-with-create-index-async.html
- https://docs.aws.amazon.com/aurora-dsql/latest/userguide/SECTION_program-with-dsql-connector-for-python.html
- https://docs.aws.amazon.com/aurora-dsql/latest/userguide/using-database-and-iam-roles.html
- https://docs.astro.build/en/install-and-setup/
- https://fastapi.tiangolo.com/release-notes/

## 検証の限界

Quintは要件catalogの構造と更新契約を検査する。予約不変条件の形式証明ではない。
ASTの図は対応構文の呼出し・分岐を生成する。自然言語と実装の完全同値を証明するものではない。
ローカル値を実AWSのSLOとして表示しない。
