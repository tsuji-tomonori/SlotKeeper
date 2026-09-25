# 初回導入と旧generatorからの移行

1. 導入先の全sourceとbuild設定からAPI・data・infra・frontendおよび固有領域を棚卸しする。実装がない領域だけを理由付きで非該当とする。
2. [参照tools全件表](../assets/reference-tools/lazunex-096e1e5.md)と固定SHAの全ファイル、関連規約、生成例を比較する。用途、言語固有の前提、adopt / adapt / extend / not-adoptedと理由を検討する。表に載ることだけを実装済みと扱わない。
3. 参照toolsを基に、導入先の言語・framework・DB・test collectorを使うadapterを導入先repositoryで実装する。共通IO・規則評価・構造解析を再利用し、実装固有の業務定数や命名辞書を取り込まない。別の参照実装を選ぶ場合も固定commitと全件一覧を同じschemaに記録する。
4. `reference-blueprint`を導入先所有の`target-adoption`棚卸しへ変換する。採用toolには実在するadapter/check/testへの接続pathを記録する。非採用理由と、参照だけでは満たせない要件のgapに対する実装・検査を明示する。未実装のpathを記入して済ませない。
5. [adapter契約](adapter-contract.md)のschema v2で`.dev-standard/design.json`を作成する。全適用要件をcapabilityへ集合として完全対応させ、全必要surfaceをrequired capabilityへ接続する。APIは[6帳票profile](api-documents.md)と実operation inventoryを接続する。
6. sourceから初回生成し、構成適合・実source集合の完全照合・意味解析・drift・実テストを実行する。未知構文/動的呼出しはpath・処理単位・行・構文種別・理由を持つ診断として失敗させる。解析不能をアクセスなしや定型図に置換しない。
7. `python <host-skill-path>/scripts/check_design.py --root .`を実行し、正例と実装変更・生成物削除・所有逸脱などの負例を確認する。導入先の既存検証入口に接続し、CI・公開規則と権限を維持する。
8. 生成Markdownのpath、対象revision、実行command、4種の結果と残存範囲を報告する。会話やinstall receiptは生成証拠の代わりにしない。

## 移行

旧`designflow.py`、`qualityflow.py`、`portable_python.py`は配布しない。既存のschema v1契約はv2へ移す。旧generatorを使用中なら導入先で所有する実装へ移し、解析意味と既存公開契約を回帰検査してからmanifestへ接続する。旧生成物を新しい所有rootに残すと検査は失敗する。過去の配置を維持する場合は導入先profileのlayoutを明示する。

installerは導入先の旧fileやvenvを自動削除しない。呼出元と依存がなくなったことを確認し、対象repositoryの権限に従って除去する。新検査器自体はPython標準ライブラリだけで動作し、導入先のPython package環境を変更しない。
