from datetime import UTC, datetime

from app.apis.reservations.common import ReservationStatus
from app.apis.reservations.list_reservations.schemas import (
    ErrorResource,
    ListReservationsResponse,
    ReservationItemResponse,
)
from app.apis.sample_cases import request_sample, status_samples

LIST_RESERVATIONS_RESPONSE_SAMPLE = ListReservationsResponse(
    items=[
        ReservationItemResponse(
            reservation_id="5d2c7f3e-0000-0000-0000-000000000001",
            resource_id="00000000-0000-0000-0000-000000000001",
            owner_principal_id="alice",
            start_at=datetime(2026, 9, 26, 1, 0, tzinfo=UTC),
            end_at=datetime(2026, 9, 26, 2, 0, tzinfo=UTC),
            purpose="定例会議",
            status=ReservationStatus.CONFIRMED,
            version=1,
        )
    ],
    next_token=None,
)
LIST_RESERVATIONS_STATUS_SAMPLES = status_samples(
    request=request_sample(
        query={
            "day": "2026-09-26",
            "status": ReservationStatus.CONFIRMED,
            "future": True,
            "limit": 50,
        },
        headers={"Authorization": "Bearer <access-token>"},
    ),
    success_status=200,
    success_response=LIST_RESERVATIONS_RESPONSE_SAMPLE,
    error_resource_model=ErrorResource,
    errors={
        401: "認証情報が未指定、期限切れ、または検証できない場合。",
        422: "queryがOpenAPIスキーマの型や制約に一致しない、または継続tokenが不正な場合。",
        429: "呼び出し頻度が許可された上限を超えた場合。",
        500: "SlotKeeper内部で想定外のエラーが発生した場合。",
        503: "DBの競合や接続障害が再試行上限を超えた場合。",
    },
)
