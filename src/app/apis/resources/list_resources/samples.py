from app.apis.resources.common import ResourceKind
from app.apis.resources.list_resources.schemas import (
    ErrorResource,
    ListResourcesResponse,
    ResourceItemResponse,
)
from app.apis.sample_cases import request_sample, status_samples

LIST_RESOURCES_RESPONSE_SAMPLE = ListResourcesResponse(
    items=[
        ResourceItemResponse(
            resource_id="00000000-0000-0000-0000-000000000001",
            name="会議室 青葉",
            description="4名 · モニター · ホワイトボード",
            kind=ResourceKind.ROOM,
            active=True,
            version=1,
        )
    ],
    next_token=None,
)
LIST_RESOURCES_STATUS_SAMPLES = status_samples(
    request=request_sample(
        query={"limit": 50},
        headers={"Authorization": "Bearer <access-token>"},
    ),
    success_status=200,
    success_response=LIST_RESOURCES_RESPONSE_SAMPLE,
    error_resource_model=ErrorResource,
    errors={
        401: "認証情報が未指定、期限切れ、または検証できない場合。",
        422: "queryがOpenAPIスキーマの型や制約に一致しない、または継続tokenが不正な場合。",
        429: "呼び出し頻度が許可された上限を超えた場合。",
        500: "SlotKeeper内部で想定外のエラーが発生した場合。",
        503: "DBの競合や接続障害が再試行上限を超えた場合。",
    },
)
