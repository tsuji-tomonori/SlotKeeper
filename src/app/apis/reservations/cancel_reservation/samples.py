from datetime import UTC, datetime

from app.apis.reservations.cancel_reservation.schemas import (
    CancelReservationRequest,
    CancelReservationResponse,
    ErrorResource,
)
from app.apis.reservations.common import ReservationStatus
from app.apis.sample_cases import request_sample, status_samples

CANCEL_RESERVATION_REQUEST_SAMPLE = CancelReservationRequest(version=1)
CANCEL_RESERVATION_RESPONSE_SAMPLE = CancelReservationResponse(
    reservation_id="5d2c7f3e-0000-0000-0000-000000000001",
    resource_id="00000000-0000-0000-0000-000000000001",
    owner_principal_id="alice",
    start_at=datetime(2026, 9, 26, 1, 0, tzinfo=UTC),
    end_at=datetime(2026, 9, 26, 2, 0, tzinfo=UTC),
    purpose="定例会議",
    status=ReservationStatus.CANCELLED,
    version=2,
)
CANCEL_RESERVATION_STATUS_SAMPLES = status_samples(
    request=request_sample(
        path={"reservationId": "5d2c7f3e-0000-0000-0000-000000000001"},
        headers={"Authorization": "Bearer <access-token>"},
        body=CANCEL_RESERVATION_REQUEST_SAMPLE,
    ),
    success_status=200,
    success_response=CANCEL_RESERVATION_RESPONSE_SAMPLE,
    error_resource_model=ErrorResource,
    errors={
        401: "認証情報が未指定、期限切れ、または検証できない場合。",
        403: "呼び出し元が予約者本人でも管理者でもない場合。",
        404: "指定された予約が存在しない場合。",
        409: "予約の版が古い、取消済み、または開始済みの場合。",
        422: "pathまたはbodyがOpenAPIスキーマの型や制約に一致しない場合。",
        429: "呼び出し頻度が許可された上限を超えた場合。",
        500: "SlotKeeper内部で想定外のエラーが発生した場合。",
        503: "DBの競合や接続障害が再試行上限を超えた場合。",
    },
)
