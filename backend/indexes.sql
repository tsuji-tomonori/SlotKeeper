CREATE INDEX IF NOT EXISTS reservation_resource_time ON slotkeeper.reservations(resource_id, start_at);
CREATE INDEX IF NOT EXISTS reservation_subject_time ON slotkeeper.reservations(subject, start_at);
CREATE INDEX IF NOT EXISTS event_reservation ON slotkeeper.reservation_events(reservation_id, at);
