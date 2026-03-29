import re


def clean_text(text):
    """
    Cleans extracted CV text for better NLP processing
    """

    # Remove bullet points and symbols
    text = re.sub(r"[•●▪■◆▶|]", " ", text)

    # Standardize all dashes
    text = re.sub(r"[–—−—]", "-", text)

    # Replace newlines/tabs with space
    text = re.sub(r"[\n\r\t]", " ", text)

    # Remove multiple spaces
    text = re.sub(r"\s+", " ", text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text
