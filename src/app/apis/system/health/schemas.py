from typing import Literal

from pydantic import Field

from app.apis.base import ApiBaseModel


class ErrorResource(ApiBaseModel):
    """稼働確認のエラー復帰に使用する項目はありません。"""


class HealthResponse(ApiBaseModel):
    """稼働確認の結果です。"""

    status: Literal["ok"] = Field(
        description="APIプロセスが要求を処理できることを表す稼働状態です。"
    )
