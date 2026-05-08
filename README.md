# IS601_FinalProjectKV — CalcQuest

Advanced calculator with game-like UI built on top of Module14AssignmentKV.

## Features
- 7 calculation operations with interactive explainers
- Full calculation history per user
- Export history to CSV, Excel, and PDF
- Forgot username and reset password
- User profile with email and password update
- JWT cookie auth with bcrypt hashing
- GitHub Actions CI/CD → Docker Hub

## Run with Docker
```bash
docker compose up --build
```
App runs at http://localhost:8000

## Run locally
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

## Run tests
```bash
pytest tests/test_unit.py tests/test_integration.py -v
```

## Docker Hub
https://hub.docker.com/r/kverma19863020/is601-finalproject-kv
