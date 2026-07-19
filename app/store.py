import threading
from .models import Session

SESSIONS: dict[str, Session] = {}
_lock = threading.Lock()


def get_session(session_id: str) -> Session | None:
    with _lock:
        return SESSIONS.get(session_id)


def create_session(session: Session) -> None:
    with _lock:
        SESSIONS[session.id] = session


def update_session(session: Session) -> None:
    with _lock:
        SESSIONS[session.id] = session
