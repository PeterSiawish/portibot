import os
from dotenv import load_dotenv

load_dotenv()

# Security
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

# Flask Settings
DEBUG = True

# Paths for important resources
APP_DIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(APP_DIR, "..", "cv_uploads")
UPLOAD_FOLDER = os.path.abspath(UPLOAD_FOLDER)

EMBEDDING_MODEL_PATH = os.path.abspath(os.path.join(APP_DIR, "..", "embedding_model"))

JOB_DATA_DIR = os.path.abspath(os.path.join(APP_DIR, "..", "job_data"))
