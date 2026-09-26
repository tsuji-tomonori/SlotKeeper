# lazunex構成への準拠

## 背景

[lazunex](https://github.com/tsuji-tomonori/lazunex)（固定revision `096e1e580ab1c0670c57e4febad2bd9fdd4698ee`）を正とし、文書内容、CRUD表の書き方、実装構成の差異をすべて解消する方針とした。差異と処置の一覧は [lazunex-alignment.manual.md](../lazunex-alignment.manual.md) を参照する。

## 判断

- backendを`src/app`へ移し、API operationを`src/app/apis/<group>/<operation>/`の`router.py`/`functions.py`/`schemas.py`/`samples.py`/`contract.py`/`sql/`/`generated/queries.py`へ分解する。
- lazunexの生成器・検査器を`src/tools`、実行入口を`src/app_tool`（`app-docs`/`app-codegen`/`app-archlint`）へ移植し、設計文書をlazunex形式の`docs/spec/<NN>.<name>/`で生成する。
- SlotKeeperの要件に必要なPostgreSQL/Aurora DSQL、Cognito JWT、Lambda、Astroは維持する。lazunexのMySQL、`X-Principal-Id`、AWS管理APIのprovider群は採用しない。
- dev-standardの設計adapter契約は、lazunex生成物を能力ごとの所有rootとして接続して満たす（`src/tools/project/design.py`）。契約の固定kind名`interface`に合わせ、IF帳票のfile名だけ`interface_gen.md`とする。
- lazunex生成器の不具合（入れ子分岐のsequence・単体テスト要因）とSlotKeeper固有構成への非対応は、生成器側を修正して取り込む。修正点は差異一覧に記録する。
