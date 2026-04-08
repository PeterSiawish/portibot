import uuid
from datetime import datetime, timedelta
import threading

TEMP_STORAGE = {}
EXPIRY_TIME = timedelta(minutes=30)
storage_lock = threading.Lock()


def create_session(data):
    cleanup_expired_sessions()
    session_id = str(uuid.uuid4())

    with storage_lock:
        TEMP_STORAGE[session_id] = {"data": data, "created_at": datetime.now()}

    return session_id


def get_session(session_id):
    with storage_lock:
        session = TEMP_STORAGE.get(session_id)

        if not session:
            return None

        if datetime.now() - session["created_at"] > EXPIRY_TIME:
            TEMP_STORAGE.pop(session_id, None)
            return None

    return session["data"]


def delete_session(session_id):
    with storage_lock:
        TEMP_STORAGE.pop(session_id, None)


def cleanup_expired_sessions():
    with storage_lock:
        now = datetime.now()
        expired = [
            sid
            for sid, s in TEMP_STORAGE.items()
            if now - s["created_at"] > EXPIRY_TIME
        ]

        for sid in expired:
            TEMP_STORAGE.pop(sid, None)
