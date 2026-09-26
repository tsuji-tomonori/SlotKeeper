from datetime import UTC, datetime

from app.apis.reservations.common import ReservationStatus
from app.apis.reservations.create_reservation.schemas import (
    CreateReservationRequest,
    CreateReservationResponse,
    ErrorResource,
)
from app.apis.sample_cases import request_sample, status_samples

CREATE_RESERVATION_REQUEST_SAMPLE = CreateReservationRequest(
    resource_id="00000000-0000-0000-0000-000000000001",
    start_at=datetime(2026, 9, 26, 1, 0, tzinfo=UTC),
    end_at=datetime(2026, 9, 26, 2, 0, tzinfo=UTC),
    purpose="定例会議",
)
CREATE_RESERVATION_RESPONSE_SAMPLE = CreateReservationResponse(
    reservation_id="5d2c7f3e-0000-0000-0000-000000000001",
    resource_id="00000000-0000-0000-0000-000000000001",
    owner_principal_id="alice",
    start_at=datetime(2026, 9, 26, 1, 0, tzinfo=UTC),
    end_at=datetime(2026, 9, 26, 2, 0, tzinfo=UTC),
    purpose="定例会議",
    status=ReservationStatus.CONFIRMED,
    version=1,
)
CREATE_RESERVATION_STATUS_SAMPLES = status_samples(
    request=request_sample(
        headers={
            "Authorization": "Bearer <access-token>",
            "Idempotency-Key": "reservation-20260926-0001",
        },
        body=CREATE_RESERVATION_REQUEST_SAMPLE,
    ),
    success_status=201,
    success_response=CREATE_RESERVATION_RESPONSE_SAMPLE,
    error_resource_model=ErrorResource,
    errors={
        401: "認証情報が未指定、期限切れ、または検証できない場合。",
        404: "予約対象の資源が存在しない場合。",
        409: "予約枠が重なる、資源が無効、または同じIdempotency-Keyで異なる入力を送った場合。",
        422: "bodyまたはheaderが型や制約に一致しない、または予約時刻の規則に反する場合。",
        429: "呼び出し頻度が許可された上限を超えた場合。",
        500: "SlotKeeper内部で想定外のエラーが発生した場合。",
        503: "DBの競合や接続障害が再試行上限を超えた場合。",
    },
)
