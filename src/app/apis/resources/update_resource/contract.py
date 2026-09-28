from __future__ import annotations

from app.apis.contract import ApiContract

CONTRACT = ApiContract(
    operation_id="updateResource",
    markdown_slug="resources/update_resource",
    auth_mode="bearer-jwt",
    business_summary="管理者が資源を編集または無効化する。",
    permissions=("admin",),
)
