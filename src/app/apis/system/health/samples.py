from app.apis.sample_cases import request_sample, status_samples
from app.apis.system.health.schemas import ErrorResource, HealthResponse

HEALTH_RESPONSE_SAMPLE = HealthResponse(status="ok")
HEALTH_STATUS_SAMPLES = status_samples(
    request=request_sample(),
    success_status=200,
    success_response=HEALTH_RESPONSE_SAMPLE,
    error_resource_model=ErrorResource,
    errors={
        429: "呼び出し頻度が許可された上限を超えた場合。",
        500: "SlotKeeper内部で想定外のエラーが発生した場合。",
    },
)
