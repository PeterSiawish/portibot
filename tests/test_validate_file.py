"""
test_validate_file.py: Unit tests for app/utilities/cv_upload_utils.py

Tests cover three functions:
  - allowed_file(filename)
  - validate_file_size(file)
  - validate_file(file)

All tests use a blackbox approach: given an input, assert the expected output
without knowledge of internal implementation details.

Run with: pytest tests/test_validate_file.py -v
"""

import io


from app.utilities.cv_upload_utils import (
    allowed_file,
    validate_file_size,
    validate_file,
)


# allowed_file(filename)
# Tests that only .pdf and .docx extensions are permitted.


class TestAllowedFile:

    # Accepted cases:

    def test_pdf_extension_accepted(self):
        """Standard .pdf filename should be allowed."""
        assert allowed_file("cv.pdf") is True

    def test_docx_extension_accepted(self):
        """Standard .docx filename should be allowed."""
        assert allowed_file("cv.docx") is True

    def test_uppercase_pdf_accepted(self):
        """Extension check should be case-insensitive (.PDF)."""
        assert allowed_file("cv.PDF") is True

    def test_uppercase_docx_accepted(self):
        """Extension check should be case-insensitive (.DOCX)."""
        assert allowed_file("cv.DOCX") is True

    def test_mixed_case_extension_accepted(self):
        """Mixed case extension (.Pdf) should also be accepted."""
        assert allowed_file("cv.Pdf") is True

    def test_filename_with_spaces_accepted(self):
        """Filenames containing spaces are still valid if extension is correct."""
        assert allowed_file("my curriculum vitae.pdf") is True

    def test_filename_with_dots_in_name_accepted(self):
        """Filenames with multiple dots should resolve to correct extension."""
        assert allowed_file("peter.siawish.cv.pdf") is True

    # Rejected cases:

    def test_txt_extension_rejected(self):
        """Plain text files must not be accepted."""
        assert allowed_file("cv.txt") is False

    def test_png_extension_rejected(self):
        """Image files must not be accepted."""
        assert allowed_file("photo.png") is False

    def test_exe_extension_rejected(self):
        """Executable files must be rejected."""
        assert allowed_file("malware.exe") is False

    def test_no_extension_rejected(self):
        """A filename with no extension at all must be rejected."""
        assert allowed_file("mycv") is False

    def test_empty_string_rejected(self):
        """An empty filename string must be rejected."""
        assert allowed_file("") is False

    def test_none_rejected(self):
        """None as a filename must be rejected without raising an exception."""
        assert allowed_file(None) is False

    def test_dot_only_filename_rejected(self):
        """A filename that is just a dot should be rejected."""
        assert allowed_file(".") is False

    def test_pdf_as_name_not_extension_rejected(self):
        """'pdf' as the filename stem with no extension should be rejected."""
        assert allowed_file("pdf") is False


# validate_file_size(file)
# Tests that files over 5 MB are rejected and those at/under are accepted.


class TestValidateFileSize:

    def _make_file(self, size_bytes: int) -> io.BytesIO:
        """Helper: create an in-memory file of a given byte size."""
        f = io.BytesIO(b"A" * size_bytes)
        f.filename = "cv.pdf"
        return f

    # Accepted cases:

    def test_small_file_accepted(self):
        """A typical 100 KB CV should be well within the limit."""
        assert validate_file_size(self._make_file(100 * 1024)) is True

    def test_exact_limit_accepted(self):
        """A file at exactly 5 MB should be accepted (boundary value)."""
        assert validate_file_size(self._make_file(5 * 1024 * 1024)) is True

    def test_one_byte_file_accepted(self):
        """A 1-byte file is trivially within the limit."""
        assert validate_file_size(self._make_file(1)) is True

    # Rejected cases:

    def test_oversized_by_one_byte_rejected(self):
        """A file that is 1 byte over the 5 MB limit must be rejected (boundary value)."""
        assert validate_file_size(self._make_file(5 * 1024 * 1024 + 1)) is False

    def test_large_file_rejected(self):
        """A 10 MB file must be rejected."""
        assert validate_file_size(self._make_file(10 * 1024 * 1024)) is False

    def test_cursor_is_reset_after_check(self):
        """
        After validate_file_size runs, the file cursor must be back at position 0
        so subsequent reads (e.g. extraction) are not broken.
        """
        f = self._make_file(1024)
        validate_file_size(f)
        assert f.tell() == 0


# validate_file(file)
# Integration of the above, tests the full validation function as used
# in the pipeline. Uses fixtures from conftest.py.


class TestValidateFile:

    # Accepted cases:

    def test_valid_pdf_returns_true(self, valid_pdf):
        """A well-formed PDF upload should pass validation."""
        is_valid, message = validate_file(valid_pdf)
        assert is_valid is True
        assert message == "File is valid"

    def test_valid_docx_returns_true(self, valid_docx):
        """A well-formed DOCX upload should pass validation."""
        is_valid, message = validate_file(valid_docx)
        assert is_valid is True
        assert message == "File is valid"

    # No file cases:

    def test_none_file_rejected(self):
        """Passing None (no file in request) must be caught."""
        is_valid, message = validate_file(None)
        assert is_valid is False
        assert "No file uploaded" in message

    def test_empty_filename_rejected(self, empty_filename):
        """A file object with an empty filename string must be rejected."""
        is_valid, message = validate_file(empty_filename)
        assert is_valid is False
        assert "No file selected" in message

    # Wrong format cases:

    def test_txt_file_rejected(self, invalid_txt):
        """A .txt file must be rejected with an appropriate message."""
        is_valid, message = validate_file(invalid_txt)
        assert is_valid is False
        assert "Invalid file type" in message

    def test_png_file_rejected(self, invalid_png):
        """A .png file must be rejected with an appropriate message."""
        is_valid, message = validate_file(invalid_png)
        assert is_valid is False
        assert "Invalid file type" in message

    def test_no_extension_rejected(self, no_extension):
        """A file with no extension must be rejected."""
        is_valid, message = validate_file(no_extension)
        assert is_valid is False
        assert "Invalid file type" in message

    # File size cases:

    def test_oversized_file_rejected(self, oversized_file):
        """A file over 5 MB must be rejected with an appropriate message."""
        is_valid, message = validate_file(oversized_file)
        assert is_valid is False
        assert "File too large" in message

    def test_exact_max_size_accepted(self, max_size_file):
        """A file at exactly 5 MB must be accepted (boundary value)."""
        is_valid, message = validate_file(max_size_file)
        assert is_valid is True
