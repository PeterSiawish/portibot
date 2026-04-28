"""
test_clean_text.py: Unit tests for app/services/text_processing_service.py

Tests cover the clean_text(text) function, which normalises raw extracted
CV text for downstream NLP processing.

All tests use a blackbox approach: given a raw string input, assert the
expected cleaned string output.

Run with: pytest tests/test_clean_text.py -v
"""

from app.services.text_processing_service import clean_text


class TestCleanText:

    # Bullet point and symbol removal:

    def test_bullet_point_removed(self):
        """Standard bullet • should be replaced with a space."""
        result = clean_text("• Python")
        assert "•" not in result
        assert "Python" in result

    def test_all_bullet_variants_removed(self):
        """All bullet variants (●▪■◆▶|) must be stripped."""
        raw = "●skill1 ▪skill2 ■skill3 ◆skill4 ▶skill5 |skill6"
        result = clean_text(raw)
        for symbol in ["●", "▪", "■", "◆", "▶", "|"]:
            assert symbol not in result

    # Dash standardisation:

    def test_en_dash_standardised(self):
        """En dash (–) should be converted to a regular hyphen."""
        result = clean_text("2020–2024")
        assert "–" not in result
        assert "-" in result

    def test_em_dash_standardised(self):
        """Em dash (—) should be converted to a regular hyphen."""
        result = clean_text("Python—Expert")
        assert "—" not in result
        assert "-" in result

    def test_regular_hyphen_preserved(self):
        """An existing regular hyphen should remain untouched."""
        result = clean_text("full-stack developer")
        assert "full-stack" in result

    # Whitespace normalisation:

    def test_newlines_replaced_with_space(self):
        """Newline characters should be replaced with a single space."""
        result = clean_text("Python\nDjango")
        assert "\n" not in result
        assert "Python Django" in result

    def test_tabs_replaced_with_space(self):
        """Tab characters should be replaced with a single space."""
        result = clean_text("Python\tDjango")
        assert "\t" not in result
        assert "Python Django" in result

    def test_carriage_return_replaced_with_space(self):
        """Carriage return characters should be replaced with a single space."""
        result = clean_text("Python\rDjango")
        assert "\r" not in result

    def test_multiple_spaces_collapsed(self):
        """Multiple consecutive spaces should be collapsed into one."""
        result = clean_text("Python   Django   Flask")
        assert "  " not in result
        assert "Python Django Flask" in result

    def test_leading_whitespace_stripped(self):
        """Leading whitespace must be removed."""
        result = clean_text("   Python developer")
        assert result == result.lstrip()

    def test_trailing_whitespace_stripped(self):
        """Trailing whitespace must be removed."""
        result = clean_text("Python developer   ")
        assert result == result.rstrip()

    # Content preservation:

    def test_normal_text_preserved(self):
        """Clean text with no special characters should be returned unchanged."""
        raw = "Experienced software engineer with Python and Django skills"
        result = clean_text(raw)
        assert result == raw

    def test_technical_terms_preserved(self):
        """Technical skill names, acronyms, and version numbers must not be altered."""
        result = clean_text("Python 3.11, REST APIs, CI/CD, Node.js")
        assert "Python 3.11" in result
        assert "REST APIs" in result
        assert "CI/CD" in result
        assert "Node.js" in result

    def test_numbers_preserved(self):
        """Numeric content such as years and percentages must be retained."""
        result = clean_text("Improved performance by 40% in 2023")
        assert "40%" in result
        assert "2023" in result

    # Edge cases:

    def test_empty_string_returns_empty(self):
        """An empty input string should return an empty string."""
        result = clean_text("")
        assert result == ""

    def test_whitespace_only_returns_empty(self):
        """A string containing only whitespace should return an empty string."""
        result = clean_text("     ")
        assert result == ""

    def test_combined_noise_cleaned(self):
        """
        A realistic messy CV extract combining bullets, dashes, and excess
        whitespace should be cleaned into a single, readable line.
        """
        raw = "• Python  –  Django\n\t● REST APIs  ▪  CI/CD"
        result = clean_text(raw)

        assert "•" not in result
        assert "●" not in result
        assert "▪" not in result
        assert "–" not in result
        assert "\n" not in result
        assert "\t" not in result
        assert "  " not in result
        assert "Python" in result
        assert "Django" in result
        assert "REST APIs" in result
        assert "CI/CD" in result
