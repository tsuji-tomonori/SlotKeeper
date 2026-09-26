from __future__ import annotations

from app.apis.contract import ApiContract

CONTRACT = ApiContract(
    operation_id="getResourceSchedule",
    markdown_slug="resources/get_resource_schedule",
    auth_mode="bearer-jwt",
    business_summary="資源と日付を指定して予約済み時間帯を取得する。",
)
