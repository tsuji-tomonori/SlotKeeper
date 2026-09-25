<!-- dev-standard:begin -->
# dev-standard lightweight guardrails

portableなblocking guardrailは次の3本だけです。

1. durableな要件を`spec/requirements/requirements.qnt`へ原子的に保つ。
2. 導入・実装変更時に現在状態のMarkdown設計を実装artifactから決定的に生成する。初回はgenerator/adapterを接続し、必要な生成物の欠落・drift検査まで行う。未接続や未対応を完了扱いにしない。
3. 変更と受入条件に関係する検査だけを実行する。

通常の入口は`$chat-first-development`です。Quint正本からJSONを生成し、そのJSONから人向けMarkdownを生成します。生成viewは直接編集しません。

静的解析と設計生成の実装は、このrepositoryのadapterが担います。設計Skillの`references/adoption.md`と`references/adapter-contract.md`に従い、固定revisionの参照tools全件を比較し、用途・要件対応・採用判断・実接続先を記録します。schema version 2の`.dev-standard/design.json`へ生成・検査command、所有する出力root、要件ID、帳票構成profileを接続し、2回生成のbyte一致、drift、未対応surfaceを確認します。

dev-standardは、このrepositoryのbranch、merge方式、CI/CD workflow、required check、PR template、commit形式を追加も変更もしません。既存のrepository指示と権限境界を優先してください。

新規開発・導入時は`inspect-quality-gates`の`references/evidence-portal.md`に従い、test一覧・実行結果・静的解析・coverage・生成設計HTMLの品質portalを初期構築します。agentが対象frameworkの実commandへadapterを接続します。新規GitHub projectはPages公開用設定を準備し、既存projectのCI・公開規則は維持します。実公開は既存の権限に従い、未接続を完成としません。
<!-- dev-standard:end -->
