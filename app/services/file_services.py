import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename


def save_file(file):
    upload_folder = current_app.config.get("UPLOAD_FOLDER")

    # Ensure upload folder exists
    os.makedirs(upload_folder, exist_ok=True)

    # Generate short unique filename
    unique_name = f"{uuid.uuid4().hex[:8]}_{secure_filename(file.filename)}"

    file_path = os.path.join(upload_folder, unique_name)

    file.save(file_path)

    return file_path


def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
