---
name: chat-first-development
description: Complete development requests through a lightweight three-pillar flow covering durable requirements, implementation-derived design, and only the checks relevant to the change.
---

# Chat-first Development

形式契約: `spec/skills/skills.qnt`の`name: "chat-first-development"`（保守・監査時に参照）。

開発を依頼されたとき、依頼の成果と対象repositoryの規則に従って完了まで進める。相談・評価だけの依頼は回答を成果とし、変更へ拡張しない。

## 3本柱

1. 利用者向け挙動、受入条件、恒久制約が変わる場合だけ`$maintain-canonical-requirements`でQuint要件正本を更新する。可逆な実装選択は要件へ固定しない。
2. Dev標準の導入・実装変更時は`$generate-implementation-design`で必要なMarkdown設計を生成し、欠落とdriftを検査する。初回や未接続ならgenerator/adapterの接続まで行う。未生成の必要領域を残して導入・実装完了としない。
3. `$inspect-quality-gates`で変更と受入条件に関係する検査を選ぶ。失敗、新しい依存、公開契約への影響が分かった場合だけ検査範囲を広げる。

## 既定の品質portal

新規開発・Dev標準導入時は、`inspect-quality-gates/references/evidence-portal.md`に従い、実testの一覧・実行結果、静的解析、coverage、生成設計書の閲覧とGitHub Pages公開用設定まで通常の初期構築に含める。利用者は製品要件だけを指定すればよく、agentがframeworkに応じたadapterと既存commandを接続する。空templateや未接続を完了としない。既存repositoryのCI・公開規則は維持し、公開操作には対象の権限を適用する。

## 実行と権限

- 依頼、既存の`AGENTS.md`等、変更対象、受入条件を確認し、必要な実装と検証を行う。可逆な詳細は既存規約と合理的な仮定で進め、結果・権限を左右する不足だけを質問する。
- 現在も有効な明示依頼・承認を再利用し、同じ作業の許可を取り直さない。途中の質問や訂正は、取消しがない限り元の目的へ取り込む。
- SQLの配置・型生成と説明コメントの言語も導入・実装の受入条件として確認する。別言語の明示指示がなければ説明コメント/docstring/生成ヘッダーは日本語にする。保存先がある場合は設計Skillの`references/adapter-contract.md`へ進み、所有単位ごとのquery・型・呼出境界を導入先adapterで検査する。再開時は過去の完了報告だけでなく現在のsource・生成元を確認する。
- PRの作成・更新・comment・review・merge、公開、外部書込み、production、削除、高額操作は、それぞれが明示依頼・承認の対象であり、必要な権限がある場合だけ行う。code変更の依頼だけからPR操作やmergeを推測しない。
- 承認が不足する操作へ到達したら、先に独立して進められる準備を完了し、対象・効果・未充足の権限を示す。既存の承認gateや実行環境の制限を回避しない。
- 独立した読み取り・検査は一括実行できる。subagentは利用可能で、独立した仕事があり並列化が有効な場合だけ使う。人数・モデル・推論強度を固定せず、対象環境の制限に従う。

## 完了

依頼された成果、実際の検証結果、未検証範囲・残存riskを簡潔に伝える。実装を伴う場合は生成Markdownのpathと生成・drift検査結果を含め、Skill配置やCIの成功だけで設計生成完了としない。長い作業では実行結果に基づく進捗を伝え、再開情報が必要な場合だけ`.devflow/run/`に目的・承認境界・完了・残件を残す。成功後は無目的な追加検査や文書を増やさない。

Skill配布だけを理由にbranch構成、merge rule、CI workflow、required check、commit形式、PR template、review YAMLを新たに要求しない。CIがないrepositoryではローカル検証を証拠とする。secret、PII、生ログを保存せず、検査を通すためにtest・型・lint・security controlを弱めない。

導入時だけ[bootstrap-and-conversation.md](references/bootstrap-and-conversation.md)を参照する。

<!-- BEGIN GENERATED QUINT CONTRACT -->
## Quint contract（自動生成）

このblockは`spec/skills/skills.qnt`から自動生成し、直接編集しません。
詳細・要件trace・digestは`spec/skills/skills.json`の同名契約を、契約の保守・監査時だけ参照します。
repository policyは導入先が所有します。非該当ならartifactやblocking判定を作りません。

- Skill: `chat-first-development`
- 柱: auxiliary
- repository blocking: no
- 既定portable: yes
- 適用条件: when-development-is-requested
- 起動context: `development-request`
- 外部作用capability: yes
- Authority: user-and-target-repository
- 副作用: repository-and-authorized-external-write
- 失敗状態: report-bounded
<!-- END GENERATED QUINT CONTRACT -->
