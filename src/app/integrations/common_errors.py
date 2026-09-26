from __future__ import annotations


class ExternalApiError(RuntimeError):
    """Provider clientで発生した外部APIエラーです。"""

    summary = "外部APIでエラーが発生した場合。"


class ExternalApiUnavailableError(ExternalApiError):
    """外部APIが利用できない場合のエラーです。"""

    summary = "外部APIが利用できない場合。"


class ExternalApiTimeoutError(ExternalApiUnavailableError):
    """外部API呼び出しがtimeoutした場合のエラーです。"""

    summary = "外部API呼び出しがtimeoutした場合。"


class ExternalApiConflictError(ExternalApiError):
    """外部API側で競合または重複が検出された場合のエラーです。"""

    summary = "外部API側で競合または重複が検出された場合。"


class ExternalApiNotFoundError(ExternalApiError):
    """外部API側で対象が存在しない場合のエラーです。"""

    summary = "外部API側で対象が存在しない場合。"


def map_provider_error(error: Exception) -> ExternalApiError:
    """Provider SDKの例外をアプリ内の外部APIエラーへ変換する。"""
    name = type(error).__name__
    if "Timeout" in name:
        return ExternalApiTimeoutError(str(error))
    if "NotFound" in name:
        return ExternalApiNotFoundError(str(error))
    return ExternalApiUnavailableError(str(error))
