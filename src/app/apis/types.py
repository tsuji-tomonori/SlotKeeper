from datetime import date, datetime
from typing import Annotated

from pydantic import AwareDatetime, Field

ResourceId = Annotated[str, Field(min_length=1, max_length=36)]
Timestamp = datetime
CalendarDate = date

BookingTimestamp = AwareDatetime
DescriptionText = Annotated[str, Field(max_length=1000)]
IdempotencyKey = Annotated[str, Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_-]+$")]
PageToken = Annotated[str, Field(min_length=1, max_length=512)]
PrincipalId = Annotated[str, Field(min_length=1, max_length=200)]
PurposeText = Annotated[str, Field(min_length=1, max_length=200)]
ResourceName = Annotated[str, Field(min_length=1, max_length=100)]
RowVersion = Annotated[int, Field(ge=1)]
