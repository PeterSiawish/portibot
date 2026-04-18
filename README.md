# Graduate Employability Support App

Final-year project: a web application that helps computing graduates understand how their CV lines up with common tech roles, using structured skill extraction, semantic similarity, and AI-generated feedback. Users upload a PDF or DOCX CV, choose a target role (or auto-detect), receive an evaluation, and get a simple portfolio page generated from their CV text.

## What it does

- **CV upload** — Accepts PDF and DOCX; text is extracted and normalised.
- **Skill profiling** — Uses the Google Gemini API to pull structured skills and profile data from the CV.
- **Role comparison** — Compares the CV against curated job profiles in `job_data/` using [Sentence Transformers](https://www.sbert.net/) embeddings (`all-MiniLM-L6-v2` in `embedding_model/`). Similarity is used to highlight gaps and strengths.
- **Target roles** — Backend, frontend, full stack, game development, data science, AI/ML, DevOps, mobile, or **auto-detect** (recommendations across roles).
- **AI evaluation** — Gemini turns comparison results into readable feedback (role-specific or auto-match views).
- **Portfolio preview** — Generates HTML for a personal portfolio from the CV; preview in the browser and download as a file.
- **Sessions** — Results are stored in a local SQLite database for **30 minutes** (see `app/utilities/session_handling.py`); there is no user database.

## Tech stack

| Layer         | Choice                                                                    |
| ------------- | ------------------------------------------------------------------------- |
| Web framework | Flask 3 (application factory, blueprints)                                 |
| LLM           | Google Gen AI (`google-genai`) for extraction, evaluation, portfolio HTML |
| Embeddings    | `sentence-transformers` + PyTorch; local model under `embedding_model/`   |
| Documents     | PyMuPDF (PDF), python-docx (DOCX)                                         |
| Config        | `instance/config.py` loads environment via `python-dotenv`                |

## Project layout

```
├── app/
│   ├── __init__.py          # create_app(), Gemini client, embedding model, blueprints
│   ├── routes/              # home, upload, results, preview
│   ├── services/            # CV pipeline, skills, comparison, evaluation, portfolio
│   ├── templates/ & static/
│   └── utilities/           # upload validation, in-memory sessions
├── instance/config.py       # Paths, DEBUG, env-backed secrets
├── job_data/                # One JSON file per role (skills, responsibilities)
├── embedding_model/         # Local SentenceTransformer weights (all-MiniLM-L6-v2)
├── cv_uploads/              # Created at runtime for temporary uploads
├── run.py                   # Entry point: create_app() then app.run()
└── requirements.txt
```

## Prerequisites

- **Python 3.13+**
- A **Google Gemini API key** ([Google AI Studio](https://aistudio.google.com/)).
- Enough disk/RAM for the sentence-transformers model (first load can take a short while).

PyTorch is pinned in `requirements.txt`; a CUDA build is optional if you want GPU acceleration for encoding.

## Setup

1. **Clone** the repository and create a virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Environment variables** — Create a `.env` file in the project root (same directory as `run.py`). `instance/config.py` loads it automatically:

   | Variable         | Purpose                                                   |
   | ---------------- | --------------------------------------------------------- |
   | `GEMINI_API_KEY` | Required for Gemini calls                                 |
   | `SECRET_KEY`     | Flask secret key (sessions/signing if you extend the app) |

4. **Embedding model** — `EMBEDDING_MODEL_PATH` in config points at `embedding_model/`, which should contain the local `all-MiniLM-L6-v2` model files. If the folder is empty, download the model from [Hugging Face](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) into that directory or change the path in `instance/config.py`.

5. **Job data** — Ensure `job_data/*.json` files exist for each role you expose in the upload form. Each file defines `technical_skills`, `soft_skills`, and `responsibilities` used for embedding and comparison.

6. **Run the app:**

   ```bash
   python run.py
   ```

   With default Flask development settings, open the URL shown in the terminal (typically `http://127.0.0.1:5000/`).

## HTTP routes (overview)

| Route                           | Description                                             |
| ------------------------------- | ------------------------------------------------------- |
| `/`                             | Landing page                                            |
| `/upload`                       | GET: form; POST: full CV pipeline → redirect to results |
| `/results/<session_id>`         | Evaluation UI (role vs auto templates)                  |
| `/preview/<session_id>`         | Portfolio preview shell                                 |
| `/preview/content/<session_id>` | Raw generated HTML for the iframe                       |
| `/download/<session_id>`        | Download portfolio as HTML attachment                   |

## Application factory and `app.app_context()`

The app is created in `create_app()` in `app/__init__.py`. After configuring the Flask app and attaching `gemini_client` and `embedding_model`, startup runs:

```python
with app.app_context():
    preload_jobs(app, app.embedding_model)
```

**What this is:** Flask’s [application context](https://flask.palletsprojects.com/en/stable/appcontext/) is a stack-bound context that makes the `current_app` proxy and the `g` object available for the duration of the `with` block.

**Why it’s used here:** `preload_jobs()` loads every JSON in `JOB_DATA_DIR` and fills module-level caches (`JOB_DATA`, `JOB_EMBEDDINGS` in `job_embedding_cache.py`). That runs once at import/factory time, not during an HTTP request—so there is no request context. Wrapping this work in `app.app_context()` is the standard Flask pattern for “application-level” setup so that:

- Any code in the preload path (now or later) can safely use `current_app` or `g` without surprises.
- Behaviour stays consistent with other Flask extensions or helpers that expect an active app context.

The preload function already receives `app` explicitly and reads `app.config`, which works on the instance without a context; the context is still useful as lifecycle hygiene and for future changes.

## Limitations (for markers and future work)

- Sessions are stored in a local SQLite database and expire after 30 minutes.
- Uploaded files are deleted after processing; there is no long-term CV storage.
- Job profiles are static JSON, not live job listings.
- Rate limits and costs apply to the Gemini API in production use.

## License and academic use

This repository is submitted as part of a final-year project. Reuse of third-party models and libraries is subject to their respective licenses (e.g. Apache-2.0 for `all-MiniLM-L6-v2` per the model card in `embedding_model/README.md`).
