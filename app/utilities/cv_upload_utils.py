import os

ALLOWED_EXTENSIONS = {"pdf", "docx"}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def allowed_file(filename):
    """
    Check if the file has an allowed extension
    """
    if not filename:
        return False

    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_file_size(file):

    # Move cursor to end of file
    file.seek(0, os.SEEK_END)
    size = file.tell()

    # Reset cursor back to beginning
    file.seek(0)

    return size <= MAX_FILE_SIZE


def validate_file(file):
    if not file:
        return False, "No file uploaded"

    if file.filename == "":
        return False, "No file selected"

    if not allowed_file(file.filename):
        return False, "Invalid file type. Only PDF, DOCX allowed."

    if not validate_file_size(file):
        return False, "File too large. Max size is 5MB."

    return True, "File is valid"
