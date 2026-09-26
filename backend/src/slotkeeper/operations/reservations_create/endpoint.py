"""予約と作成履歴と要求成功記録を一体で登録する。"""

from datetime import timedelta
from hashlib import sha256
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, Header

from slotkeeper.auth import Principal
from slotkeeper.db import Connection, transaction
from slotkeeper.domain import (
    BookingInput,
    Clock,
    DomainError,
    Reservation,
    SystemClock,
    validate_booking,
)
from slotkeeper.operations.reservations_create import queries as q

router = APIRouter()


def clock() -> Clock:
    """現在時刻を依存として提供する。"""
    return SystemClock()


@router.post(
    "/reservations",
    response_model=Reservation,
    status_code=201,
    operation_id="reservations_create",
    tags=["reservations"],
)
def endpoint(
    value: BookingInput,
    user: Principal,
    timer: Annotated[Clock, Depends(clock)],
    idempotency_key: Annotated[
        str, Header(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_-]+$")
    ],
) -> Reservation:
    """再送照合を新規時刻検証より先に行い、commit後だけ成功応答を返す。"""
    digest = sha256(value.model_dump_json().encode()).hexdigest()

    def work(connection: Connection) -> Reservation:
        now = timer.now()
        records = q.replay(connection, q.ReplayParams(subject=user.subject, key=idempotency_key))
        if records and records[0].expires_at > now:
            if records[0].input_hash != digest:
                raise DomainError("idempotency_input_mismatch")
            return Reservation.model_validate_json(records[0].response)
        validate_booking(value, now)
        resources = q.control(connection, q.ControlParams(id=value.resource_id))
        if not resources:
            raise DomainError("resource_not_found", 404)
        if not resources[0].active:
            raise DomainError("resource_inactive")
        if q.overlap(
            connection,
            q.OverlapParams(resource_id=value.resource_id, start=value.start_at, end=value.end_at),
        )[0].count:
            raise DomainError("slot_taken")
        if records:
            q.expire(connection, q.ExpireParams(subject=user.subject, key=idempotency_key))
        q.user(connection, q.UserParams(subject=user.subject, now=now))
        reservation = q.create(
            connection,
            q.CreateParams(
                id=str(uuid4()),
                subject=user.subject,
                resource_id=value.resource_id,
                start_at=value.start_at,
                end_at=value.end_at,
                purpose=value.purpose,
            ),
        )[0]
        q.event(
            connection,
            q.EventParams(
                id=str(uuid4()),
                reservation_id=reservation.id,
                actor=user.subject,
                action="created",
                at=now,
            ),
        )
        q.record(
            connection,
            q.RecordParams(
                subject=user.subject,
                key=idempotency_key,
                input_hash=digest,
                response=reservation.model_dump_json(),
                expires_at=now + timedelta(hours=24),
            ),
        )
        return reservation

    return transaction(work, replay_safe=True)
