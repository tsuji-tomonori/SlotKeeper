"""資源一覧APIを実PostgreSQLで検査する。"""

from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from tests.helpers import Signer

pytestmark = pytest.mark.db


def test_resource_paging_order(client: TestClient, signed: Signer, database: None) -> None:
    """Given 同名の資源 When ページ単位で取得 Then 名前とIDの固定順で欠落・重複がない。 [SLOT-01-AC] [RULE-14-AC]"""
    admin = signed("admin", True)
    name = "順序確認 " + str(uuid4())
    created = sorted(
        client.post(
            "/resources", headers=admin, json={"name": name, "description": "", "kind": "room"}
        ).json()["resourceId"]
        for _ in range(3)
    )
    seen: list[str] = []
    token = ""
    while True:
        query = "/resources?limit=2" + ("&nextToken=" + token if token else "")
        page = client.get(query, headers=signed("bob")).json()
        seen += [r["resourceId"] for r in page["items"] if r["name"] == name]
        if not page.get("nextToken"):
            break
        token = page["nextToken"]
    assert seen == created
