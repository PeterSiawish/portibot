"""
test_session.py: Unit tests for app/utilities/session_handling.py

Tests cover four functions:
  - create_session(data): stores session data, returns UUID
  - get_session(session_id): retrieves data if session exists and is valid
  - delete_session(session_id): removes a session from the database
  - cleanup_expired_sessions(): bulk-removes sessions older than 30 minutes

Because these functions depend on Flask's app context (via get_db() and
current_app), a minimal Flask test application is created as a session-scoped
fixture. A temporary SQLite database is used so tests are fully isolated
from the production database and leave no state behind.

Run with: pytest tests/test_session.py -v
"""

import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone

import pytest
from flask import Flask

from app.utilities.session_handling import (
    create_session,
    get_session,
    delete_session,
    cleanup_expired_sessions,
)


# Fixtures: minimal Flask app with isolated temporary database


@pytest.fixture(scope="module")
def app():
    """
    Creates a minimal Flask application with a temporary SQLite database.
    The database is initialised with the sessions table schema and torn
    down after all tests in this module complete.
    """
    db_path = os.path.join(os.path.dirname(__file__), "fixtures", "test_sessions.db")

    flask_app = Flask(__name__)
    flask_app.config["DATABASE"] = db_path
    flask_app.config["TESTING"] = True

    # Initialise the sessions table
    con = sqlite3.connect(db_path)
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """
    )
    con.commit()
    con.close()

    yield flask_app

    # Teardown: close file descriptor and remove temp database
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except PermissionError:
            pass  # Windows may still hold a lock; file will be cleaned on next run


@pytest.fixture(scope="module")
def app_context(app):
    """Pushes a Flask application context for the duration of the module."""
    with app.app_context():
        yield


@pytest.fixture(autouse=True)
def clean_db(app):
    """
    Clears all rows from the sessions table before each test to ensure
    tests are fully isolated and do not share state.
    """
    con = sqlite3.connect(app.config["DATABASE"])
    con.execute("DELETE FROM sessions")
    con.commit()
    con.close()


# Helpers:

SAMPLE_DATA = {"evaluation": {"score": 0.85}, "role": "backend"}


def insert_session_with_age(app, session_id: str, age: timedelta):
    """
    Directly inserts a session row with a created_at timestamp offset
    by the given age, bypassing create_session() to control timing precisely.
    """
    created_at = (datetime.now(timezone.utc) - age).isoformat()
    con = sqlite3.connect(app.config["DATABASE"])
    con.execute(
        "INSERT INTO sessions (session_id, data, created_at) VALUES (?, ?, ?)",
        (session_id, json.dumps(SAMPLE_DATA), created_at),
    )
    con.commit()
    con.close()


# create_session:


class TestCreateSession:

    def test_returns_a_string(self, app_context):
        """create_session must return a string session ID."""
        session_id = create_session(SAMPLE_DATA)
        assert isinstance(session_id, str)

    def test_returns_valid_uuid(self, app_context):
        """The returned session ID must be a valid UUID4 string."""
        import uuid

        session_id = create_session(SAMPLE_DATA)
        try:
            uuid.UUID(session_id, version=4)
        except ValueError:
            pytest.fail(f"session_id '{session_id}' is not a valid UUID4")

    def test_each_session_id_is_unique(self, app_context):
        """Two consecutive calls must produce different session IDs."""
        id1 = create_session(SAMPLE_DATA)
        id2 = create_session(SAMPLE_DATA)
        assert id1 != id2

    def test_data_is_persisted(self, app, app_context):
        """
        Data passed to create_session must be retrievable directly
        from the database, confirming it was written correctly.
        """
        session_id = create_session(SAMPLE_DATA)
        con = sqlite3.connect(app.config["DATABASE"])
        row = con.execute(
            "SELECT data FROM sessions WHERE session_id = ?", (session_id,)
        ).fetchone()
        con.close()
        assert row is not None
        assert json.loads(row[0]) == SAMPLE_DATA


# get_session:


class TestGetSession:

    def test_returns_correct_data_for_valid_session(self, app, app_context):
        """A recently created session must return the original data."""
        session_id = create_session(SAMPLE_DATA)
        result = get_session(session_id)
        assert result == SAMPLE_DATA

    def test_returns_none_for_nonexistent_session(self, app_context):
        """A session ID that was never created must return None."""
        result = get_session("00000000-0000-0000-0000-000000000000")
        assert result is None

    def test_returns_none_for_expired_session(self, app, app_context):
        """
        A session older than 30 minutes must return None, confirming
        that the expiry mechanism works as required by NFR-4.1 and the
        GDPR data minimisation principle stated in the requirements chapter.
        """
        session_id = "expired-session-test-id"
        insert_session_with_age(app, session_id, age=timedelta(minutes=31))
        result = get_session(session_id)
        assert result is None

    def test_expired_session_is_deleted_on_access(self, app, app_context):
        """
        Accessing an expired session must trigger its deletion from the
        database, ensuring stale data is not retained beyond its useful life.
        """
        session_id = "expired-delete-test-id"
        insert_session_with_age(app, session_id, age=timedelta(minutes=31))
        get_session(session_id)  # triggers deletion

        con = sqlite3.connect(app.config["DATABASE"])
        row = con.execute(
            "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
        ).fetchone()
        con.close()
        assert row is None

    def test_session_at_exactly_30_minutes_is_expired(self, app, app_context):
        """
        A session created exactly 30 minutes ago must be treated as expired.
        This is a boundary value test for the expiry threshold.
        """
        session_id = "boundary-expired-id"
        insert_session_with_age(app, session_id, age=timedelta(minutes=30, seconds=1))
        result = get_session(session_id)
        assert result is None

    def test_session_just_under_30_minutes_is_valid(self, app, app_context):
        """
        A session created just under 30 minutes ago must still be accessible.
        Boundary value test for the lower side of the expiry threshold.
        """
        session_id = "boundary-valid-id"
        insert_session_with_age(app, session_id, age=timedelta(minutes=29))
        result = get_session(session_id)
        assert result == SAMPLE_DATA


# delete_session:


class TestDeleteSession:

    def test_session_no_longer_retrievable_after_delete(self, app_context):
        """A deleted session must not be returned by get_session."""
        session_id = create_session(SAMPLE_DATA)
        delete_session(session_id)
        assert get_session(session_id) is None

    def test_delete_nonexistent_session_does_not_raise(self, app_context):
        """
        Deleting a session ID that does not exist must not raise
        an exception — the operation should be idempotent.
        """
        try:
            delete_session("nonexistent-id")
        except Exception as e:
            pytest.fail(f"delete_session raised an unexpected exception: {e}")

    def test_session_removed_from_database(self, app, app_context):
        """After deletion, the row must not exist in the database."""
        session_id = create_session(SAMPLE_DATA)
        delete_session(session_id)

        con = sqlite3.connect(app.config["DATABASE"])
        row = con.execute(
            "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
        ).fetchone()
        con.close()
        assert row is None


# cleanup_expired_sessions:


class TestCleanupExpiredSessions:

    def test_expired_sessions_are_removed(self, app, app_context):
        """
        cleanup_expired_sessions must remove all sessions older than
        30 minutes, supporting automated data minimisation in line
        with GDPR requirements.
        """
        insert_session_with_age(app, "old-1", age=timedelta(minutes=45))
        insert_session_with_age(app, "old-2", age=timedelta(minutes=60))
        cleanup_expired_sessions()

        con = sqlite3.connect(app.config["DATABASE"])
        rows = con.execute(
            "SELECT * FROM sessions WHERE session_id IN ('old-1', 'old-2')"
        ).fetchall()
        con.close()
        assert len(rows) == 0

    def test_valid_sessions_are_not_removed(self, app, app_context):
        """
        cleanup_expired_sessions must not remove sessions that are
        still within the 30-minute validity window.
        """
        session_id = create_session(SAMPLE_DATA)
        cleanup_expired_sessions()
        result = get_session(session_id)
        assert result == SAMPLE_DATA

    def test_mixed_sessions_only_removes_expired(self, app, app_context):
        """
        When both valid and expired sessions exist, only expired ones
        must be removed. Valid sessions must remain accessible.
        """
        insert_session_with_age(app, "old-mixed", age=timedelta(minutes=45))
        valid_id = create_session(SAMPLE_DATA)

        cleanup_expired_sessions()

        con = sqlite3.connect(app.config["DATABASE"])
        old_row = con.execute(
            "SELECT * FROM sessions WHERE session_id = 'old-mixed'"
        ).fetchone()
        con.close()

        assert old_row is None
        assert get_session(valid_id) == SAMPLE_DATA
