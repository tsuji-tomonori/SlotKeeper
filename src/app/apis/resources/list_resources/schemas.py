from pydantic import Field

from app.apis.base import ApiBaseModel
from app.apis.resources.common import ResourceKind
from app.apis.responses import PageQuery
from app.apis.types import DescriptionText, PageToken, ResourceId, ResourceName, RowVersion


class ListResourcesQuery(PageQuery):
    """資源一覧のページング条件です。"""


class ErrorResource(ApiBaseModel):
    """資源一覧取得のエラー復帰に使用するページング条件です。"""

    next_token: PageToken | None = Field(
        default=None,
        description="一覧復帰時に同じ位置から再取得するための継続tokenです。",
    )


class ResourceItemResponse(ApiBaseModel):
    """資源一覧の1件分の資源情報です。"""

    resource_id: ResourceId = Field(description="予約対象の資源を一意に識別するIDです。")
    name: ResourceName = Field(description="利用者に表示する資源名です。")
    description: DescriptionText = Field(description="資源の設備や用途を説明する文章です。")
    kind: ResourceKind = Field(description="会議室または備品を表す資源種別です。")
    active: bool = Field(description="新規予約を受け付けるかどうかです。")
    version: RowVersion = Field(description="資源編集の楽観ロックに使う公開版です。")


class ListResourcesResponse(ApiBaseModel):
    """資源一覧のレスポンスです。"""

    items: list[ResourceItemResponse] = Field(
        description="一覧レスポンスに含まれるリソース配列です。"
    )
    next_token: PageToken | None = Field(
        default=None,
        description="次ページを取得するために前回レスポンスから受け取る継続tokenです。",
    )
