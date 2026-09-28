from __future__ import annotations

from app.apis.contract import ApiContract

CONTRACT = ApiContract(
    operation_id="listResources",
    markdown_slug="resources/list_resources",
    auth_mode="bearer-jwt",
    business_summary="予約できる資源の一覧を取得する。",
)
