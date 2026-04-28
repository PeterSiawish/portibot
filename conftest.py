"""
conftest.py: Shared pytest fixtures for the system.

Fixtures defined here are automatically available to all test files
in the tests/ directory without needing to import them.

Run all tests with: pytest -v or pytest tests/ -v
"""

import io
import pytest


# File fixtures:


def make_file_object(filename: str, content: bytes = b"dummy content") -> io.BytesIO:
    """
    Helper that creates an in-memory file object mimicking a Flask/Werkzeug
    FileStorage upload, with a .filename attribute and seek/tell support.
    """
    file = io.BytesIO(content)
    file.filename = filename
    return file


@pytest.fixture
def valid_pdf():
    """A small, valid-looking PDF upload."""
    return make_file_object("cv.pdf", b"%PDF-1.4 dummy pdf content")


@pytest.fixture
def valid_docx():
    """A small, valid-looking DOCX upload."""
    return make_file_object("cv.docx", b"PK dummy docx content")


@pytest.fixture
def invalid_txt():
    """A .txt file (not an allowed format)."""
    return make_file_object("cv.txt", b"plain text content")


@pytest.fixture
def invalid_png():
    """A .png file (not an allowed format)."""
    return make_file_object("photo.png", b"\x89PNG fake image bytes")


@pytest.fixture
def empty_filename():
    """Simulates a submission where the user did not select a file."""
    return make_file_object("", b"some content")


@pytest.fixture
def no_extension():
    """A file with no extension at all."""
    return make_file_object("mycv", b"some content")


@pytest.fixture
def oversized_file():
    """A file that exceeds the 5 MB limit."""
    big_content = b"A" * (5 * 1024 * 1024 + 1)  # 5 MB + 1 byte
    return make_file_object("cv.pdf", big_content)


@pytest.fixture
def max_size_file():
    """A file that is exactly at the 5 MB limit (should be accepted)."""
    exact_content = b"A" * (5 * 1024 * 1024)
    return make_file_object("cv.pdf", exact_content)
