from __future__ import annotations

from app.apis.contract import ApiContract

CONTRACT = ApiContract(
    operation_id="cancelReservation",
    markdown_slug="reservations/cancel_reservation",
    auth_mode="bearer-jwt",
    business_summary="本人または管理者が開始前の予約を取消す。",
    sequence_assertions=("取消と取消履歴を同一transactionで確定する。",),
)
