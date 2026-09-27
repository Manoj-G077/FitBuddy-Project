# FitBuddy – AI Fitness Plan Generator

A complete FastAPI + Jinja2 + SQLAlchemy + SQLite application based on the supplied FitBuddy project documentation.

## What is included

- Adult user profile form
- AI-generated 7-day workout/wellness plan
- AI-generated nutrition/recovery tip
- Feedback-based plan revision
- SQLite persistence
- Protected admin dashboard
- FastAPI Swagger docs
- Health endpoint
- Automated tests
- Responsive HTML/CSS UI

## Important update from the supplied document

The supplied documentation uses the older `google-generativeai` package and Gemini 1.5 Pro/Flash. This implementation uses Google's current `google-genai` SDK and configurable current Gemini model IDs. The model can be changed through `.env`.

## Setup

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and add your Gemini API key and a private admin token.

## Run

```bash
uvicorn app.main:app --reload
```

Open:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/health

Admin dashboard:

```text
http://127.0.0.1:8000/view-all-users?token=YOUR_ADMIN_TOKEN
```

Do not share the admin URL or token publicly.

## Test

```bash
pytest -q
```

## Project structure

```text
FitBuddy/
├── app/
│   ├── __init__.py
│   ├── ai.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── routes.py
│   └── schemas.py
├── static/css/style.css
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── result.html
│   ├── feedback.html
│   └── all_users.html
├── tests/
│   ├── test_health.py
│   └── test_schemas.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## API routes

- `GET /` – web generator
- `POST /generate-workout` – generate and save a plan
- `GET /feedback` – feedback form
- `POST /submit-feedback` – regenerate a plan from feedback
- `GET /view-all-users?token=...` – protected admin page
- `GET /health` – health check

## Safety and privacy

This app is a wellness-planning demo, not a medical service. It intentionally avoids medical diagnosis, treatment instructions, extreme dieting, starvation, dehydration, or unsafe exercise challenges.

The admin page contains personal fitness data. Use a strong admin token and do not expose SQLite or `.env` files publicly.

For production, add real authentication/authorization, HTTPS, CSRF protection for cookie-based auth, rate limiting, audit logging, secret management, encrypted backups, and a managed database.
