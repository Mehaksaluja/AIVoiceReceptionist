from threading import Lock

from src.models.booking import ActivityEvent, Booking, BookingStatus, Session


class SessionStore:

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}
        self._lock = Lock()

    def create(self, name: str, phone: str, reason: str) -> Session:
        booking = Booking(name=name, phone=phone, reason=reason, status=BookingStatus.IN_PROGRESS)
        session = Session(booking=booking)
        session.activity.append(
            ActivityEvent(
                step="session_created",
                message="New booking session started",
                metadata={"name": name, "phone": phone, "reason": reason},
            )
        )
        with self._lock:
            self._sessions[session.session_id] = session
        return session

    def get(self, session_id: str) -> Session | None:
        with self._lock:
            return self._sessions.get(session_id)

    def save(self, session: Session) -> None:
        with self._lock:
            self._sessions[session.session_id] = session

    def log(self, session_id: str, step: str, message: str, **metadata: object) -> None:
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return
            session.activity.append(
                ActivityEvent(step=step, message=message, metadata=dict(metadata))
            )

    def mark_confirmed(self, session_id: str, confirmed_slot: str) -> Session | None:
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return None
            session.is_booked = True
            session.booking.status = BookingStatus.CONFIRMED
            session.booking.confirmed_slot = confirmed_slot
            session.activity.append(
                ActivityEvent(
                    step="booking_confirmed",
                    message=f"Appointment booked for {confirmed_slot}",
                    metadata={"confirmed_slot": confirmed_slot},
                )
            )
            return session

    def list_sessions(self) -> list[Session]:
        with self._lock:
            return list(self._sessions.values())


store = SessionStore()
