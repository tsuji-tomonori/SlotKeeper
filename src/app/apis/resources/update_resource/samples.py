from app.apis.resources.common import ResourceKind
from app.apis.resources.update_resource.schemas import (
    ErrorResource,
    UpdateResourceRequest,
    UpdateResourceResponse,
)
from app.apis.sample_cases import request_sample, status_samples

UPDATE_RESOURCE_REQUEST_SAMPLE = UpdateResourceRequest(
    name="会議室 青葉",
    description="6名 · モニター · ホワイトボード",
    kind=ResourceKind.ROOM,
    active=True,
    version=1,
)
UPDATE_RESOURCE_RESPONSE_SAMPLE = UpdateResourceResponse(
    resource_id="00000000-0000-0000-0000-000000000001",
    name="会議室 青葉",
    description="6名 · モニター · ホワイトボード",
    kind=ResourceKind.ROOM,
    active=True,
    version=2,
)
UPDATE_RESOURCE_STATUS_SAMPLES = status_samples(
    request=request_sample(
        path={"resourceId": "00000000-0000-0000-0000-000000000001"},
        headers={"Authorization": "Bearer <access-token>"},
        body=UPDATE_RESOURCE_REQUEST_SAMPLE,
    ),
    success_status=200,
    success_response=UPDATE_RESOURCE_RESPONSE_SAMPLE,
    error_resource_model=ErrorResource,
    errors={
        401: "認証情報が未指定、期限切れ、または検証できない場合。",
        403: "呼び出し元が資源を管理できる管理者でない場合。",
        404: "指定された資源が存在しない場合。",
        409: "資源の公開版が古い、または無効化する資源に将来予約がある場合。",
        422: "pathまたはbodyがOpenAPIスキーマの型や制約に一致しない場合。",
        429: "呼び出し頻度が許可された上限を超えた場合。",
        500: "SlotKeeper内部で想定外のエラーが発生した場合。",
        503: "DBの競合や接続障害が再試行上限を超えた場合。",
    },
)
