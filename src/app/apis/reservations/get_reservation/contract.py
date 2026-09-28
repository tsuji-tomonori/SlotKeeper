from __future__ import annotations

from app.apis.contract import ApiContract

CONTRACT = ApiContract(
    operation_id="getReservation",
    markdown_slug="reservations/get_reservation",
    auth_mode="bearer-jwt",
    business_summary="本人または管理者が予約の詳細と操作履歴を取得する。",
)
