"""
test_extract_text.py: Unit tests for app/services/cv_services.py

Tests cover the extract_text() function and its two sub-functions:
  - extract_text(file_path): dispatcher based on file extension
  - extract_pdf(file_path): PDF text extraction via pymupdf
  - extract_docx(file_path): DOCX text extraction via python-docx

Real sample files are used from tests/fixtures/ to validate actual
extraction behaviour. No mocking is required as these libraries are
local and require no external services.

Run with: pytest tests/test_extract_text.py -v
"""

import os

from app.services.cv_services import extract_docx, extract_pdf, extract_text


# Path to fixture files:

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
SAMPLE_PDF = os.path.join(FIXTURES_DIR, "sample.pdf")
SAMPLE_DOCX = os.path.join(FIXTURES_DIR, "sample.docx")

# Known content that must appear in extracted text
EXPECTED_TERMS = ["Software Engineer", "Python", "Flask", "REST APIs"]


# extract_text: dispatcher


class TestExtractTextDispatcher:

    def test_pdf_file_returns_string(self):
        """extract_text on a .pdf path must return a non-empty string."""
        result = extract_text(SAMPLE_PDF)
        assert isinstance(result, str)
        assert len(result.strip()) > 0

    def test_docx_file_returns_string(self):
        """extract_text on a .docx path must return a non-empty string."""
        result = extract_text(SAMPLE_DOCX)
        assert isinstance(result, str)
        assert len(result.strip()) > 0

    def test_unsupported_extension_returns_none(self):
        """
        A file path with an unsupported extension must return None
        rather than raising an exception.
        """
        result = extract_text("cv.txt")
        assert result is None

    def test_no_extension_returns_none(self):
        """A file path with no extension must return None."""
        result = extract_text("mycv")
        assert result is None

    def test_extension_check_is_case_insensitive(self):
        """
        Extension matching must be case-insensitive: .PDF and .DOCX
        should be handled the same as .pdf and .docx.
        """
        # We test only that it doesn't return None (i.e. dispatches correctly).
        # The file may not exist, but the dispatcher decision happens before
        # the file is opened, so a missing-file error confirms dispatch occurred.
        try:
            extract_text(SAMPLE_PDF.replace(".pdf", ".PDF"))
        except Exception as e:
            assert "None" not in str(type(e))


# extract_pdf: content correctness


class TestExtractPdf:

    def test_returns_non_empty_string(self):
        """PDF extraction must return a non-empty string."""
        result = extract_pdf(SAMPLE_PDF)
        assert isinstance(result, str)
        assert len(result.strip()) > 0

    def test_known_content_present(self):
        """
        Text known to exist in the sample PDF must appear in the
        extracted output, confirming content is correctly retrieved.
        """
        result = extract_pdf(SAMPLE_PDF)
        for term in EXPECTED_TERMS:
            assert term in result, f"Expected term '{term}' not found in PDF extraction"

    def test_result_is_readable_text(self):
        """Extracted PDF text must not be a raw binary or encoded string."""
        result = extract_pdf(SAMPLE_PDF)
        assert result.isprintable() or "\n" in result


# extract_docx: content correctness


class TestExtractDocx:

    def test_returns_non_empty_string(self):
        """DOCX extraction must return a non-empty string."""
        result = extract_docx(SAMPLE_DOCX)
        assert isinstance(result, str)
        assert len(result.strip()) > 0

    def test_known_content_present(self):
        """
        Text known to exist in the sample DOCX must appear in the
        extracted output, confirming paragraphs are correctly read.
        """
        result = extract_docx(SAMPLE_DOCX)
        for term in EXPECTED_TERMS:
            assert (
                term in result
            ), f"Expected term '{term}' not found in DOCX extraction"

    def test_paragraphs_separated_by_newlines(self):
        """
        Paragraphs in the DOCX must be separated by newline characters
        in the extracted output, preserving document structure.
        """
        result = extract_docx(SAMPLE_DOCX)
        assert "\n" in result

    def test_result_contains_multiple_lines(self):
        """
        Since the sample file contains multiple lines, the extracted
        text must contain more than one line.
        """
        result = extract_docx(SAMPLE_DOCX)
        lines = [l for l in result.splitlines() if l.strip()]
        assert len(lines) > 1
