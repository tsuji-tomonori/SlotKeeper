from __future__ import annotations

from app.apis.contract import ApiContract

CONTRACT = ApiContract(
    operation_id="createResource",
    markdown_slug="resources/create_resource",
    auth_mode="bearer-jwt",
    business_summary="管理者が予約対象の資源を登録する。",
    permissions=("admin",),
)
