import os
from dotenv import load_dotenv
from google.genai.types import HttpRetryOptions

load_dotenv()

# Security
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

# Gemini API Retry Configuration
GEMINI_RETRY_CONFIG = HttpRetryOptions(
    attempts=4,
    initial_delay=2.0,
    max_delay=30.0,
    exp_base=2.0,
    jitter=1.0,
    http_status_codes=[429, 503],
)

# Flask Settings
DEBUG = True

# Paths for important resources
INSTANCE_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.abspath(os.path.join(INSTANCE_DIR, ".."))

UPLOAD_FOLDER = os.path.join(INSTANCE_DIR, "cv_uploads")

EMBEDDING_MODEL_PATH = os.path.join(ROOT_DIR, "embedding_model")

JOB_DATA_DIR = os.path.join(ROOT_DIR, "job_data")
