# 開発開始と対話の契約

## 入口

利用者は自然言語で結果を依頼する。Skill名、内部command、branch構成、CI設定を指定する必要はない。agentは対象repositoryの既存規則と利用可能なtoolを調べ、安全に不足を補う。

## 3本柱

1. 永続義務が変わる場合だけQuint要件正本を更新する。
2. 導入時・実装変更時に必要なas-built Markdownを生成する。初回はgenerate-implementation-designの`references/adoption.md`に従い、generator接続・対象網羅・欠落/drift検査まで完了する。
3. 変更に関係するcheckだけを実行する。

入口Skillは3本柱を順序付けるが、それ自体をblocking guardrailにしない。

## 既存repositoryの維持

- 既存のbranch、merge、review、CI/CD、commit、release規則を維持する。
- portable assetsは`.github/workflows/`、branch protection、rulesetを追加しない。
- CIがないことをfailureにせず、対象test等のローカル結果を使う。
- 利用者へfileのコピーやinstallation commandの実行を求めて作業を停止しない。

## 既定の公開成果

新規GitHubプロジェクトは品質portal・公開用workflowの準備を初期成果に含める。既存projectは既存CI/公開先へ接続する。agentが`inspect-quality-gates/references/evidence-portal.md`に沿って実test collector、実行結果、静的解析、coverage、設計HTMLのadapterを実装し、ローカル閲覧まで確認する。installerのworkflow非配布と、依頼されたプロジェクト初期実装でのtarget-owned設定作成は別の操作である。実公開は対象の権限に従う。

## 一時状態

再開用の一時情報が必要な場合だけgitignoreされた`.devflow/run/`を使用し、成果へ統合後に削除する。生成された品質siteはrun単位のbuild artifactであり、手書き作業記録とは区別する。通常変更で恒久的な`work/<id>/`、計画書、implementation log、test reportを作らない。

## 権限境界

外部書込み、公開、merge、削除、production、高額・不可逆操作は、対象操作が依頼または明示承認に含まれる場合だけ実行する。可逆なローカル変更や検証へ形式的な初回承認を要求しない。

## 完了

成果、適用した柱、実行したcheck、未検証範囲を簡潔に示す。PRやCIは利用者が依頼し、対象repositoryが利用する場合だけ扱う。
