from datetime import UTC, date, datetime

from app.apis.reservations.common import BUSY_SLOT_LABEL, ReservationStatus
from app.apis.resources.get_resource_schedule.schemas import (
    ErrorResource,
    GetResourceScheduleResponse,
    ScheduleReservationResponse,
    ScheduleSlotResponse,
)
from app.apis.sample_cases import request_sample, status_samples

GET_RESOURCE_SCHEDULE_RESPONSE_SAMPLE = GetResourceScheduleResponse(
    items=[
        ScheduleSlotResponse(
            start_at=datetime(2026, 9, 26, 1, 0, tzinfo=UTC),
            end_at=datetime(2026, 9, 26, 2, 0, tzinfo=UTC),
            label=BUSY_SLOT_LABEL,
            reservation=ScheduleReservationResponse(
                reservation_id="5d2c7f3e-0000-0000-0000-000000000001",
                resource_id="00000000-0000-0000-0000-000000000001",
                owner_principal_id="alice",
                start_at=datetime(2026, 9, 26, 1, 0, tzinfo=UTC),
                end_at=datetime(2026, 9, 26, 2, 0, tzinfo=UTC),
                purpose="定例会議",
                status=ReservationStatus.CONFIRMED,
                version=1,
            ),
        ),
        ScheduleSlotResponse(
            start_at=datetime(2026, 9, 26, 4, 0, tzinfo=UTC),
            end_at=datetime(2026, 9, 26, 5, 0, tzinfo=UTC),
            label=BUSY_SLOT_LABEL,
        ),
    ],
    next_token=None,
)
GET_RESOURCE_SCHEDULE_STATUS_SAMPLES = status_samples(
    request=request_sample(
        path={"resourceId": "00000000-0000-0000-0000-000000000001"},
        query={"day": date(2026, 9, 26).isoformat(), "limit": 100},
        headers={"Authorization": "Bearer <access-token>"},
    ),
    success_status=200,
    success_response=GET_RESOURCE_SCHEDULE_RESPONSE_SAMPLE,
    error_resource_model=ErrorResource,
    errors={
        401: "認証情報が未指定、期限切れ、または検証できない場合。",
        404: "指定された資源が存在しない場合。",
        422: "pathまたはqueryが型や制約に一致しない、または継続tokenが不正な場合。",
        429: "呼び出し頻度が許可された上限を超えた場合。",
        500: "SlotKeeper内部で想定外のエラーが発生した場合。",
        503: "DBの競合や接続障害が再試行上限を超えた場合。",
    },
)
