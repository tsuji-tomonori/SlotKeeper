# reservations_get / Message

## API

reservations_get

## 生成・検証方針

app.pyのHTTP middlewareとDomainError境界が所有。

## メッセージ一覧

request_result: 全HTTP結果。

## ログ詳細

### request_result

#### 出力項目

request_id:string / operation:string / status:int / elapsed_ms:number。目的、token、生例外は出力しない。

## strict検証で要求する項目

401認証、403権限、404存在、409業務・版、422入力、503再試行上限。ログと応答の要求IDを照合する。
