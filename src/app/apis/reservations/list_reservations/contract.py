from __future__ import annotations

from app.apis.contract import ApiContract

CONTRACT = ApiContract(
    operation_id="listReservations",
    markdown_slug="reservations/list_reservations",
    auth_mode="bearer-jwt",
    business_summary="自分の予約を日付・状態で絞り込んで取得する。",
)
