"""自分の予約一覧APIを実PostgreSQLで検査する。"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from tests.helpers import Signer, create_reservation

pytestmark = pytest.mark.db


def test_list_filters_only_own(client: TestClient, signed: Signer, booking: dict[str, str]) -> None:
    """Given 自分と他人の2日分の予約と取消 When 日付・状態で絞込み Then 自分の対象だけ固定順で返す。 [SLOT-AC08] [RULE-07-AC]"""
    later = {**booking, "startAt": "2026-09-27T01:00:00Z", "endAt": "2026-09-27T02:00:00Z"}
    first = create_reservation(client, signed, booking).json()
    second = create_reservation(client, signed, later).json()
    other = create_reservation(
        client,
        signed,
        {**booking, "startAt": "2026-09-26T03:00:00Z", "endAt": "2026-09-26T04:00:00Z"},
        subject="bob",
    ).json()
    client.post(
        "/reservations/" + second["reservationId"] + "/cancel",
        headers=signed(),
        json={"version": 1},
    )

    def ids(query: str) -> list[str]:
        rows = client.get("/reservations?limit=100&" + query, headers=signed()).json()["items"]
        return [r["reservationId"] for r in rows if r["resourceId"] == booking["resourceId"]]

    assert first["reservationId"] in ids("day=2026-09-26&future=false")
    assert other["reservationId"] not in ids("day=2026-09-26&future=false")
    assert second["reservationId"] not in ids("day=2026-09-26&future=false")
    assert ids("day=2026-09-27&status=cancelled&future=false") == [second["reservationId"]]
    assert second["reservationId"] not in ids("future=true")
    assert (
        client.get("/reservations/" + other["reservationId"], headers=signed()).status_code == 403
    )
    assert client.get("/reservations?limit=0", headers=signed()).status_code == 422


def test_reservation_paging_order(
    client: TestClient, signed: Signer, booking: dict[str, str]
) -> None:
    """Given 同じ日の3件の予約 When 継続tokenでページ単位に取得 Then 開始日時とIDの固定順で欠落・重複がない。 [RULE-14-AC]"""
    starts = ["01", "03", "05"]
    created = [
        create_reservation(
            client,
            signed,
            {
                **booking,
                "startAt": f"2026-09-26T{hour}:00:00Z",
                "endAt": f"2026-09-26T{hour}:30:00Z",
            },
            subject="pager",
        ).json()["reservationId"]
        for hour in starts
    ]
    seen: list[str] = []
    token = ""
    while True:
        query = "/reservations?day=2026-09-26&limit=2" + ("&nextToken=" + token if token else "")
        page = client.get(query, headers=signed("pager")).json()
        seen += [
            r["reservationId"] for r in page["items"] if r["resourceId"] == booking["resourceId"]
        ]
        if not page.get("nextToken"):
            break
        token = page["nextToken"]
    assert seen == created
    broken = client.get("/reservations?nextToken=%%%", headers=signed("pager"))
    assert broken.status_code == 422
