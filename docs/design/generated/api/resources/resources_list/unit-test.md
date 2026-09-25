# resources_list / Unit Test

## 0. endpoint層の暗黙処理

FastAPI入力解析と認証依存を適用。

## 1. 要因ごとの要素

### 入力・権限・状態・競合

実在ケースだけを列挙する。全組合せの網羅を意味しない。

## 2. 組合せたテストケース一覧

| ID | 受入説明 |
| --- | --- |
| backend/tests/test_auth.py::test_bad_claims | Given 不正claim When 業務API呼出し Then 401でDB未接続。 [SLOT-AC14] |
| backend/tests/test_auth.py::test_bad_signature | Given 別の秘密鍵による改ざん When 検証 Then 401。 [SLOT-AC14] |
| backend/tests/test_auth.py::test_anonymous_and_health | Given 未認証 When 業務APIとhealth Then 業務401・healthは秘密なし。 [COM-04] |
| backend/tests/test_auth.py::test_user_cannot_create_resource | Given 一般利用者 When 管理API Then 403。 [SLOT-01] |
| backend/tests/test_auth.py::test_cognito_access_and_id | Given Cognito claim When accessとIDを検証 Then accessだけ受理。 [SLOT-AC14] |
| backend/tests/test_domain.py::test_resource_input | Given 空白か長すぎる資源名 When 入力解析 Then 拒否。 [COM-03] |

## 3. テスト詳細

### backend/tests/test_auth.py::test_bad_claims

Given 不正claim When 業務API呼出し Then 401でDB未接続。 [SLOT-AC14]

### backend/tests/test_auth.py::test_bad_signature

Given 別の秘密鍵による改ざん When 検証 Then 401。 [SLOT-AC14]

### backend/tests/test_auth.py::test_anonymous_and_health

Given 未認証 When 業務APIとhealth Then 業務401・healthは秘密なし。 [COM-04]

### backend/tests/test_auth.py::test_user_cannot_create_resource

Given 一般利用者 When 管理API Then 403。 [SLOT-01]

### backend/tests/test_auth.py::test_cognito_access_and_id

Given Cognito claim When accessとIDを検証 Then accessだけ受理。 [SLOT-AC14]

### backend/tests/test_domain.py::test_resource_input

Given 空白か長すぎる資源名 When 入力解析 Then 拒否。 [COM-03]
