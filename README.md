# Module 14 — BREAD Calculations

A full-stack FastAPI web application implementing BREAD operations for a calculations resource with JWT authentication and Docker deployment.

## How to Run Locally

```bash
# Clone the repo
git clone https://github.com/kverma19863020/Module14AssignmentKV.git
cd Module14AssignmentKV

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy env file and configure
cp .env.example .env

# Run the app
uvicorn app.main:app --reload
```

Visit http://localhost:8000

## How to Run Tests Locally

```bash
pytest tests/ -v --ignore=tests/test_e2e.py
```

## How to Run with Docker

```bash
docker compose up --build
```

## Docker Hub

Image: https://hub.docker.com/r/kverma1986/module14assignmentkv

## API Endpoints

- `GET /calculations` — Browse all calculations
- `GET /calculations/{id}` — Read a specific calculation
- `GET /calculations/new` — Add form
- `POST /calculations/new` — Create calculation
- `GET /calculations/{id}/edit` — Edit form
- `POST /calculations/{id}/edit` — Update calculation
- `POST /calculations/{id}/delete` — Delete calculation
