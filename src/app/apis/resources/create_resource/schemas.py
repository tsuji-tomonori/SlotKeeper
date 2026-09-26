from pydantic import ConfigDict, Field

from app.apis.base import ApiBaseModel
from app.apis.resources.common import ResourceKind
from app.apis.types import DescriptionText, ResourceId, ResourceName, RowVersion


class CreateResourceRequest(ApiBaseModel):
    """資源登録のリクエストです。"""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: ResourceName = Field(description="利用者に表示する資源名です。空白除去後1〜100文字です。")
    description: DescriptionText = Field(
        default="",
        description="資源の設備や用途を説明する文章です。0〜1,000文字です。",
    )
    kind: ResourceKind = Field(
        default=ResourceKind.ROOM,
        description="会議室または備品を表す資源種別です。",
    )


class ErrorResource(ApiBaseModel):
    """資源登録のエラー復帰に使用する対象リソースです。"""

    name: ResourceName | None = Field(
        default=None,
        description="登録しようとした資源名です。",
    )


class CreateResourceResponse(ApiBaseModel):
    """登録した資源のレスポンスです。"""

    resource_id: ResourceId = Field(description="予約対象の資源を一意に識別するIDです。")
    name: ResourceName = Field(description="利用者に表示する資源名です。")
    description: DescriptionText = Field(description="資源の設備や用途を説明する文章です。")
    kind: ResourceKind = Field(description="会議室または備品を表す資源種別です。")
    active: bool = Field(description="新規予約を受け付けるかどうかです。")
    version: RowVersion = Field(description="資源編集の楽観ロックに使う公開版です。")
