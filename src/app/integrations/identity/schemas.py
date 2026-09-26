from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class VerifiedPrincipal:
    """署名・issuer・client・用途・期限を検証済みの利用者です。"""

    principal_id: str
    groups: Sequence[str]


class AccessTokenRejectedError(ValueError):
    """access token が検証できない場合の業務上の拒否です。"""

    summary = "access token の署名、issuer、client、用途、期限のいずれかが不正な場合。"
