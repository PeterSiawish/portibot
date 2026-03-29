import pymupdf
from docx import Document


def extract_text(file_path):
    """
    Detect file type and extract text accordingly
    """

    if file_path.endswith(".pdf"):
        return extract_pdf(file_path)

    elif file_path.endswith(".docx"):
        return extract_docx(file_path)

    else:
        return "Something Went Wrong"


def extract_pdf(file_path):
    """
    Extract text from PDF using PyMuPDF
    """
    text = ""

    with pymupdf.open(file_path) as doc:
        for page in doc:
            text += page.get_text()

    return text


def extract_docx(file_path):
    """
    Extract text from DOCX using python-docx
    """
    text = ""

    doc = Document(file_path)

    for para in doc.paragraphs:
        text += para.text + "\n"

    return text
