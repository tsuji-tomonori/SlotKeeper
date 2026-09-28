from __future__ import annotations

from app.apis.contract import ApiContract

CONTRACT = ApiContract(
    operation_id="createReservation",
    markdown_slug="reservations/create_reservation",
    auth_mode="bearer-jwt",
    business_summary="資源・開始・終了・目的を指定して自分名義の予約を作成する。",
    sequence_assertions=(
        "再送照合を新規予約の時刻検証より先に行う。",
        "予約・作成履歴・要求成功記録を同一transactionで確定する。",
    ),
)
