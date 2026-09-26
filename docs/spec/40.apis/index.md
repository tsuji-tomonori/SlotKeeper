# API設計

lazunex形式のAPI帳票。各APIの6帳票はgroup/API単位のindexから辿る。OpenAPIは`openapi.json`、operation一覧は`operations.json`に出力する。

- [API一覧](apis_list_gen.md)
- [運用ログmessage一覧](messages_index_gen.md)

## Group

- [reservations](reservations/index.md)
- [resources](resources/index.md)

## Platform route

`src/app/main.py`が所有する業務外routeは、lazunexと同じくIF帳票だけを持つ。

- [health](system/health/interface_gen.md)
