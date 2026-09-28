# API×保存先 CRUD

| operation | resource | access |
|---|---|---|
| cancelReservation | identity.jwks_signing_key | R |
| cancelReservation | slotkeeper.reservation_events | C |
| cancelReservation | slotkeeper.reservations | RU |
| cancelReservation | slotkeeper.resources | U |
| createReservation | identity.jwks_signing_key | R |
| createReservation | slotkeeper.idempotency_records | CRD |
| createReservation | slotkeeper.reservation_events | C |
| createReservation | slotkeeper.reservations | CR |
| createReservation | slotkeeper.resources | U |
| createReservation | slotkeeper.users | C |
| createResource | identity.jwks_signing_key | R |
| createResource | slotkeeper.resources | C |
| getReservation | identity.jwks_signing_key | R |
| getReservation | slotkeeper.reservation_events | R |
| getReservation | slotkeeper.reservations | R |
| getResourceSchedule | identity.jwks_signing_key | R |
| getResourceSchedule | slotkeeper.reservations | R |
| getResourceSchedule | slotkeeper.resources | R |
| listReservations | identity.jwks_signing_key | R |
| listReservations | slotkeeper.reservations | R |
| listResources | identity.jwks_signing_key | R |
| listResources | slotkeeper.resources | R |
| updateResource | identity.jwks_signing_key | R |
| updateResource | slotkeeper.reservations | R |
| updateResource | slotkeeper.resources | U |
