import uuid, json
from datetime import datetime, timedelta, timezone
from app.utilities.session_db import get_db

EXPIRY_TIME = timedelta(minutes=30)


def create_session(data):
    cleanup_expired_sessions()

    session_id = str(uuid.uuid4())
    db = get_db()

    db.execute(
        "INSERT INTO sessions (session_id, data, created_at) VALUES (?, ?, ?)",
        (session_id, json.dumps(data), datetime.now(timezone.utc).isoformat()),
    )
    db.commit()

    return session_id


def get_session(session_id):
    db = get_db()

    row = db.execute(
        "SELECT data, created_at FROM sessions WHERE session_id = ?", (session_id,)
    ).fetchone()

    if not row:
        return None

    created_at = datetime.fromisoformat(row["created_at"])

    if datetime.now(timezone.utc) - created_at > EXPIRY_TIME:
        delete_session(session_id)
        return None

    return json.loads(row["data"])


def delete_session(session_id):
    db = get_db()
    db.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
    db.commit()


def cleanup_expired_sessions():
    db = get_db()

    # This deletes anything where created_at is 30 minutes ago or older
    limit = (datetime.now(timezone.utc) - EXPIRY_TIME).isoformat()
    db.execute("DELETE FROM sessions WHERE created_at < ?", (limit,))
    db.commit()
