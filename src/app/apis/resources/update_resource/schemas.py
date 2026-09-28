from pydantic import ConfigDict, Field

from app.apis.base import ApiBaseModel
from app.apis.resources.common import ResourceKind
from app.apis.types import DescriptionText, ResourceId, ResourceName, RowVersion


class UpdateResourceRequest(ApiBaseModel):
    """資源編集のリクエストです。"""

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
    active: bool = Field(description="新規予約を受け付けるかどうかです。")
    version: RowVersion = Field(description="編集前に取得した資源の公開版です。")


class ErrorResource(ApiBaseModel):
    """資源編集のエラー復帰に使用する対象リソースです。"""

    resource_id: ResourceId | None = Field(
        default=None,
        description="編集対象資源の存在確認、再取得、問い合わせに使用する資源IDです。",
    )
    version: RowVersion | None = Field(
        default=None,
        description="編集要求で指定した資源の公開版です。",
    )


class UpdateResourceResponse(ApiBaseModel):
    """編集後の資源のレスポンスです。"""

    resource_id: ResourceId = Field(description="予約対象の資源を一意に識別するIDです。")
    name: ResourceName = Field(description="利用者に表示する資源名です。")
    description: DescriptionText = Field(description="資源の設備や用途を説明する文章です。")
    kind: ResourceKind = Field(description="会議室または備品を表す資源種別です。")
    active: bool = Field(description="新規予約を受け付けるかどうかです。")
    version: RowVersion = Field(description="資源編集の楽観ロックに使う公開版です。")
