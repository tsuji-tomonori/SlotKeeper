from app.apis.resources.common import ResourceKind
from app.apis.resources.create_resource.schemas import (
    CreateResourceRequest,
    CreateResourceResponse,
    ErrorResource,
)
from app.apis.sample_cases import request_sample, status_samples

CREATE_RESOURCE_REQUEST_SAMPLE = CreateResourceRequest(
    name="会議室 青葉",
    description="4名 · モニター · ホワイトボード",
    kind=ResourceKind.ROOM,
)
CREATE_RESOURCE_RESPONSE_SAMPLE = CreateResourceResponse(
    resource_id="00000000-0000-0000-0000-000000000001",
    name="会議室 青葉",
    description="4名 · モニター · ホワイトボード",
    kind=ResourceKind.ROOM,
    active=True,
    version=1,
)
CREATE_RESOURCE_STATUS_SAMPLES = status_samples(
    request=request_sample(
        headers={"Authorization": "Bearer <access-token>"},
        body=CREATE_RESOURCE_REQUEST_SAMPLE,
    ),
    success_status=201,
    success_response=CREATE_RESOURCE_RESPONSE_SAMPLE,
    error_resource_model=ErrorResource,
    errors={
        401: "認証情報が未指定、期限切れ、または検証できない場合。",
        403: "呼び出し元が資源を管理できる管理者でない場合。",
        422: "bodyがOpenAPIスキーマの型や制約に一致しない場合。",
        429: "呼び出し頻度が許可された上限を超えた場合。",
        500: "SlotKeeper内部で想定外のエラーが発生した場合。",
        503: "DBの競合や接続障害が再試行上限を超えた場合。",
    },
)
