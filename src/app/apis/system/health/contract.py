from __future__ import annotations

from app.apis.contract import ApiContract

CONTRACT = ApiContract(
    operation_id="health",
    markdown_slug="system/health",
    auth_mode="none",
    business_summary="秘密やDB情報を含まない稼働状態を返す。",
)
