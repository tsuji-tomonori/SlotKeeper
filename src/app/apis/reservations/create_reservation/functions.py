from __future__ import annotations

import hashlib
from datetime import timedelta
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.apis.common import JST, raise_missing_runtime_dependency
from app.apis.exceptions import ApiFunctionError
from app.apis.reservations.common import ReservationStatus
from app.apis.reservations.create_reservation.generated import queries
from app.apis.reservations.create_reservation.schemas import (
    CreateReservationRequest,
    CreateReservationResponse,
)
from app.apis.router_errors import (
    api_error_response,
    error_code_for_status,
    error_response_for_router_error,
    router_error_message_id,
    router_error_summary,
    router_log_context,
    status_code_for_router_error,
)
from app.apis.sequence_types import (
    CallerIdentity,
    Clock,
    EventRef,
    IdempotencyRecordRef,
    ResourceRef,
)
from app.apis.types import ResourceId
from app.core.logging import get_operation_logger, operational_log_context_model
from app.integrations.common_errors import ExternalApiError

ops_logger = get_operation_logger(__name__)

IDEMPOTENCY_TTL = timedelta(hours=24)
BOOKING_WINDOW = timedelta(days=30)
MIN_DURATION = timedelta(minutes=15)
MAX_DURATION = timedelta(hours=4)
SLOT_MINUTES = 15


def _request_hash(request: CreateReservationRequest) -> str:
    return hashlib.sha256(request.model_dump_json(by_alias=True).encode()).hexdigest()


def _booking_error(detail: str, summary: str) -> ApiFunctionError:
    return ApiFunctionError(status.HTTP_422_UNPROCESSABLE_CONTENT, detail, summary=summary)


async def get_idempotency_record(
    idempotency_key: str,
    caller: CallerIdentity,
    clock: Clock,
    session: AsyncSession | None = None,
) -> IdempotencyRecordRef:
    """利用者とIdempotency-Keyに対応する予約作成要求の成功記録を取得する。"""
    if session is not None:
        rows = await queries.select_idempotency_records(
            session,
            queries.SelectIdempotencyRecordsParams(
                principal_id=caller.principal_id,
                idempotency_key=idempotency_key,
            ),
        )
        if not rows:
            return IdempotencyRecordRef(idempotency_key=idempotency_key)
        row = rows[0]
        return IdempotencyRecordRef(
            idempotency_key=row.idempotency_key,
            request_hash=row.request_hash,
            response_payload=row.response_payload,
            expires_at=row.expires_at,
            is_expired=row.expires_at <= clock.now(),
        )
    return raise_missing_runtime_dependency("get_idempotency_record")


async def has_idempotency_result(record: IdempotencyRecordRef) -> bool:
    """有効期限内の成功記録がIdempotency-Keyに紐づいているかを判定する。"""
    return record.response_payload is not None and not record.is_expired


async def is_same_idempotent_request(
    record: IdempotencyRecordRef,
    request: CreateReservationRequest,
) -> bool:
    """成功記録の正規化入力と再送された要求が同じかを判定する。"""
    return record.request_hash == _request_hash(request)


async def validate_booking_request(
    request: CreateReservationRequest,
    clock: Clock,
) -> CreateReservationRequest:
    """新規要求の開始時刻・長さ・15分刻み・日本時間の日付を検証する。"""
    now = clock.now()
    start, end = request.start_at, request.end_at
    if not now < start <= now + BOOKING_WINDOW:
        raise _booking_error(
            "start_out_of_range", "開始が現在以前、または現在から30日より後の場合。"
        )
    if not MIN_DURATION <= end - start <= MAX_DURATION:
        raise _booking_error("duration_out_of_range", "予約時間が15分未満または4時間超の場合。")
    if any(
        value.minute % SLOT_MINUTES or value.second or value.microsecond for value in (start, end)
    ):
        raise _booking_error("quarter_hour_required", "開始または終了が15分刻みでない場合。")
    if start.astimezone(JST).date() != end.astimezone(JST).date():
        raise _booking_error(
            "same_japan_day_required", "終了が開始と同じ日本時間の日付内にない場合。"
        )
    return request


async def get_locked_resource(
    resource_id: ResourceId,
    session: AsyncSession | None = None,
) -> ResourceRef:
    """同一資源の予約作成・取消・無効化を競合させるため、内部制御版を進めて資源を取得する。"""
    if session is not None:
        row = await queries.update_resources_control_version(
            session,
            queries.UpdateResourcesControlVersionParams(resource_id=resource_id),
        )
        if row is None:
            raise ApiFunctionError(
                status.HTTP_404_NOT_FOUND,
                "resource_not_found",
                summary="予約対象の資源が存在しない場合。",
            )
        return ResourceRef(
            resource_id=row.resource_id,
            active=row.active,
            row_version=row.row_version,
        )
    return raise_missing_runtime_dependency("get_locked_resource")


async def is_active_resource(resource: ResourceRef) -> bool:
    """予約対象の資源が新規予約を受け付けるかを判定する。"""
    return resource.active


async def has_overlapping_reservation(
    request: CreateReservationRequest,
    session: AsyncSession | None = None,
) -> bool:
    """取消済みを除き、半開区間が重なる確定予約があるかを判定する。"""
    if session is not None:
        rows = await queries.select_reservations(
            session,
            queries.SelectReservationsParams(
                resource_id=request.resource_id,
                end_at=request.end_at,
                start_at=request.start_at,
            ),
        )
        return bool(rows and rows[0].overlapping_reservation_count)
    return raise_missing_runtime_dependency("has_overlapping_reservation")


async def delete_expired_idempotency_record(
    record: IdempotencyRecordRef,
    caller: CallerIdentity,
    session: AsyncSession | None = None,
) -> IdempotencyRecordRef:
    """有効期限を過ぎた成功記録を新規要求として扱うため削除する。"""
    if not record.is_expired:
        return record
    if session is not None:
        await queries.delete_idempotency_records(
            session,
            queries.DeleteIdempotencyRecordsParams(
                principal_id=caller.principal_id,
                idempotency_key=record.idempotency_key,
            ),
        )
        return IdempotencyRecordRef(idempotency_key=record.idempotency_key)
    return raise_missing_runtime_dependency("delete_expired_idempotency_record")


async def save_reservation_owner(
    caller: CallerIdentity,
    clock: Clock,
    session: AsyncSession | None = None,
) -> CallerIdentity:
    """初めて予約する利用者を記録する。"""
    if session is not None:
        await queries.insert_users(
            session,
            queries.InsertUsersParams(
                principal_id=caller.principal_id,
                first_seen_at=clock.now(),
            ),
        )
        return caller
    return raise_missing_runtime_dependency("save_reservation_owner")


async def save_reservation(
    request: CreateReservationRequest,
    caller: CallerIdentity,
    session: AsyncSession | None = None,
) -> CreateReservationResponse:
    """予約を確定状態の初期版で保存する。"""
    if session is not None:
        row = await queries.insert_reservations(
            session,
            queries.InsertReservationsParams(
                reservation_id=str(uuid4()),
                resource_id=request.resource_id,
                owner_principal_id=caller.principal_id,
                start_at=request.start_at,
                end_at=request.end_at,
                purpose=request.purpose,
            ),
        )
        if row is None:
            raise ApiFunctionError(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "reservation_not_saved",
                summary="予約の保存結果を取得できない場合。",
            )
        return CreateReservationResponse(
            reservation_id=row.reservation_id,
            resource_id=row.resource_id,
            owner_principal_id=row.owner_principal_id,
            start_at=row.start_at,
            end_at=row.end_at,
            purpose=row.purpose,
            status=ReservationStatus(row.status),
            version=row.row_version,
        )
    return raise_missing_runtime_dependency("save_reservation")


async def append_reservation_created_event(
    reservation: CreateReservationResponse,
    caller: CallerIdentity,
    clock: Clock,
    session: AsyncSession | None = None,
) -> EventRef:
    """予約作成の履歴を予約と同じtransactionで追記する。"""
    if session is not None:
        event_id = str(uuid4())
        await queries.insert_reservation_events(
            session,
            queries.InsertReservationEventsParams(
                event_id=event_id,
                reservation_id=reservation.reservation_id,
                actor_principal_id=caller.principal_id,
                occurred_at=clock.now(),
            ),
        )
        return EventRef(event_id=event_id)
    return raise_missing_runtime_dependency("append_reservation_created_event")


async def create_idempotency_record(
    idempotency_key: str,
    request: CreateReservationRequest,
    reservation: CreateReservationResponse,
    clock: Clock,
    session: AsyncSession | None = None,
) -> IdempotencyRecordRef:
    """元の成功応答を予約と同じtransactionで24時間の成功記録として保存する。"""
    if session is not None:
        request_hash = _request_hash(request)
        payload = reservation.model_dump_json(by_alias=True)
        expires_at = clock.now() + IDEMPOTENCY_TTL
        await queries.insert_idempotency_records(
            session,
            queries.InsertIdempotencyRecordsParams(
                principal_id=reservation.owner_principal_id,
                idempotency_key=idempotency_key,
                request_hash=request_hash,
                response_payload=payload,
                expires_at=expires_at,
            ),
        )
        return IdempotencyRecordRef(
            idempotency_key=idempotency_key,
            request_hash=request_hash,
            response_payload=payload,
            expires_at=expires_at,
        )
    return raise_missing_runtime_dependency("create_idempotency_record")


async def build_reservation_response(
    reservation: CreateReservationResponse,
) -> CreateReservationResponse:
    """作成した予約のレスポンスを組み立てる。"""
    return CreateReservationResponse(
        reservation_id=reservation.reservation_id,
        resource_id=reservation.resource_id,
        owner_principal_id=reservation.owner_principal_id,
        start_at=reservation.start_at,
        end_at=reservation.end_at,
        purpose=reservation.purpose,
        status=reservation.status,
        version=reservation.version,
    )


async def build_replayed_reservation_response(
    record: IdempotencyRecordRef,
) -> CreateReservationResponse:
    """成功記録に保存した元の作成応答を組み立てる。"""
    return CreateReservationResponse.model_validate_json(record.response_payload or "")


def _warning_context(
    request: CreateReservationRequest,
    idempotency_key: str,
    caller: CallerIdentity,
    detail: str,
) -> dict[str, object]:
    return router_log_context(
        status_code=status.HTTP_409_CONFLICT,
        detail=detail,
        caller=caller,
        resource={"resourceId": request.resource_id, "idempotencyKey": idempotency_key},
    )


async def build_idempotency_key_reused_response(
    request: CreateReservationRequest,
    idempotency_key: str,
    caller: CallerIdentity,
) -> JSONResponse:
    """同じIdempotency-Keyで異なる入力が送られた場合の運用ログと error response を組み立てる。"""
    ops_logger.warning(
        "createReservation.idempotency_key_reused",
        catalog_id="M001",
        summary="同じIdempotency-Keyで異なる入力が送られたため、予約作成を拒否した。",
        status_code=status.HTTP_409_CONFLICT,
        detail="idempotency_input_mismatch",
        when="有効期限内の成功記録と正規化入力のhashが一致しない場合。",
        why_production="再送の誤用による二重予約や上書きの試行を運用で追跡するため。",
        context_model=operational_log_context_model(
            trace_id=None,
            actor_principal_id=caller.principal_id,
            api_status_code=status.HTTP_409_CONFLICT,
            resource_resource_id=request.resource_id,
            error_code=error_code_for_status(status.HTTP_409_CONFLICT),
            error_message="idempotency_input_mismatch",
        ),
        operator_action="利用者へ新しいIdempotency-Keyで予約し直すよう案内する。",
        runbook="RUNBOOK-idempotency-conflict",
        context=_warning_context(request, idempotency_key, caller, "idempotency_input_mismatch"),
    )
    return api_error_response(status.HTTP_409_CONFLICT, "idempotency_input_mismatch")


async def build_resource_inactive_response(
    request: CreateReservationRequest,
    idempotency_key: str,
    caller: CallerIdentity,
) -> JSONResponse:
    """無効な資源への予約を拒否する場合の運用ログと error response を組み立てる。"""
    ops_logger.warning(
        "createReservation.resource_inactive",
        catalog_id="M002",
        summary="予約対象の資源が無効化されているため、予約作成を拒否した。",
        status_code=status.HTTP_409_CONFLICT,
        detail="resource_inactive",
        when="予約対象の資源のactiveがfalseの場合。",
        why_production="無効資源への予約試行を運用で把握するため。",
        context_model=operational_log_context_model(
            trace_id=None,
            actor_principal_id=caller.principal_id,
            api_status_code=status.HTTP_409_CONFLICT,
            resource_resource_id=request.resource_id,
            error_code=error_code_for_status(status.HTTP_409_CONFLICT),
            error_message="resource_inactive",
        ),
        operator_action="資源の有効状態と利用者への案内を確認する。",
        runbook="RUNBOOK-resource-deactivation",
        context=_warning_context(request, idempotency_key, caller, "resource_inactive"),
    )
    return api_error_response(
        status.HTTP_409_CONFLICT,
        "resource_inactive",
        resource={"resourceId": request.resource_id},
    )


async def build_slot_taken_response(
    request: CreateReservationRequest,
    idempotency_key: str,
    caller: CallerIdentity,
) -> JSONResponse:
    """予約枠が重なる場合の運用ログと error response を組み立てる。"""
    ops_logger.warning(
        "createReservation.slot_taken",
        catalog_id="M003",
        summary="同じ資源の確定予約と時間帯が重なるため、予約作成を拒否した。",
        status_code=status.HTTP_409_CONFLICT,
        detail="slot_taken",
        when="半開区間[開始,終了)が重なる確定予約が同じ資源にある場合。",
        why_production="予約競合の発生頻度を運用で把握するため。",
        context_model=operational_log_context_model(
            trace_id=None,
            actor_principal_id=caller.principal_id,
            api_status_code=status.HTTP_409_CONFLICT,
            resource_resource_id=request.resource_id,
            error_code=error_code_for_status(status.HTTP_409_CONFLICT),
            error_message="slot_taken",
        ),
        operator_action="利用者へ予約表を再取得して別の時間帯を選ぶよう案内する。",
        runbook="RUNBOOK-reservation-conflict",
        context=_warning_context(request, idempotency_key, caller, "slot_taken"),
    )
    return api_error_response(
        status.HTTP_409_CONFLICT,
        "slot_taken",
        resource={"resourceId": request.resource_id},
    )


async def build_router_error_response(
    request: CreateReservationRequest,
    idempotency_key: str,
    caller: CallerIdentity,
    error: ApiFunctionError | ExternalApiError | HTTPException,
) -> JSONResponse:
    """Router で捕捉した例外を運用ログと HTTP error response に変換する。"""
    ops_logger.error(
        router_error_message_id("createReservation", error),
        catalog_id="M004",
        summary=router_error_summary(
            "Routerで捕捉した例外により予約作成が失敗した。",
            error,
        ),
        when="ROUTER_HANDLED_EXCEPTIONSを捕捉した場合。",
        check_procedure="traceIdでログを検索し、routerで捕捉された例外種別とresourceIdを確認する。",
        remediation_procedure="入力規則と資源の状態を確認し、同じIdempotency-Keyで再送する。",
        context_model=operational_log_context_model(
            trace_id=None,
            actor_principal_id=caller.principal_id,
            api_status_code=status_code_for_router_error(error),
            resource_resource_id=request.resource_id,
            error_code=error_code_for_status(status_code_for_router_error(error)),
            error_message=str(error),
            error_exception_type=type(error).__name__,
        ),
        operator_action="同一routeの4xx/5xx率、直近deploy、DB状態を確認する。",
        runbook="RUNBOOK-unexpected-api-failure",
        context=router_log_context(
            status_code=status_code_for_router_error(error),
            detail=str(error),
            caller=caller,
            resource={"resourceId": request.resource_id, "idempotencyKey": idempotency_key},
            error=error,
        ),
    )
    return error_response_for_router_error(error)
