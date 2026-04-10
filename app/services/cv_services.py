import pymupdf
from docx import Document


def extract_text(file_path):
    path_lower = file_path.lower()
    if path_lower.endswith(".pdf"):
        return extract_pdf(file_path)

    if path_lower.endswith(".docx"):
        return extract_docx(file_path)

    return None


def extract_pdf(file_path):
    text = ""

    with pymupdf.open(file_path) as doc:
        for page in doc:
            text += page.get_text()

    return text


def extract_docx(file_path):
    text = ""

    doc = Document(file_path)

    for para in doc.paragraphs:
        text += para.text + "\n"

    return text
