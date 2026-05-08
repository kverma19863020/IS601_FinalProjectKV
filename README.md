# Calculation World — IS601 Final Project

A full-stack web application built with FastAPI, SQLAlchemy, and Jinja2.
Implements complete **BREAD** operations (Browse, Read, Edit, Add, Delete)
for calculations, with a **game-style interactive UI**, history export, and secure auth.

---

## Features

### Core Calculation Features
- **7 Calculation Operations**: Add, Subtract, Multiply, Divide, Power, Modulus, Square Root
- **Game-Style Interactive Calculator UI**: Neon dark theme with animated starfield background,
  pulsing buttons, glowing operation tiles, and smooth result animations
- **Operation Explainer Tab**: Every operation tile shows a live explanation panel below
  the calculator describing what the operation does, its mathematical definition,
  and a worked example (e.g. selecting Power shows: "Raises a to the power of b — Example: 2 ^ 10 = 1024")
- **Zero Division Protection**: Divide and Modulus operations are guarded against
  division by zero — the app catches this before executing and displays a clear
  red error panel instead of crashing
- **Live Operator Symbol**: The symbol between Value A and Value B updates in real
  time when a new operation tile is selected

### BREAD Operations
- **Browse**: `/history` — view all calculations in a sortable, filterable table
- **Read**: `/calculation/{id}` — view full detail of a single calculation
- **Edit**: `/calculation/{id}/edit` — modify operands and operation, result recalculates
- **Add**: `/calculate` — run a new calculation and save to history
- **Delete**: `/calculation/{id}/delete` — remove a calculation from history

### History & Export
- Filter history by keyword or operation type
- Sort any column ascending or descending
- Export to **CSV**, **Excel** (styled with openpyxl), **PDF** (styled with ReportLab)

### User Account
- **Register** with username, email, password
- **Login / Logout** with JWT cookie session
- **Forgot Username**: recover username by entering email
- **Reset Password**: reset password by entering email and new password
- **Profile**: update email and change password (requires current password)

### Security
- Passwords hashed with **bcrypt** via passlib — never stored in plain text
- Sessions use **JWT tokens** stored in httponly cookies — not accessible by JavaScript
- All protected routes verify JWT on every request
- Profile changes require current password verification before applying
- Environment secrets loaded from `.env` file, excluded from git

### Testing
- **Unit tests**: password hashing, JWT encode/decode, all 7 calculation operations
- **Integration tests**: all BREAD routes, auth flows, export endpoints, REST API

### CI/CD
- GitHub Actions pipeline: test job → docker build → Docker Hub push
- Docker image auto-pushed on every passing push to `main`

---

## Running Locally

```bash
git clone https://github.com/kverma19863020/IS601_FinalProjectKV.git
cd IS601_FinalProjectKV
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Open: http://localhost:8000

---

## Running with Docker

```bash
docker compose up --build
```

Open: http://localhost:8000

---

## Running Tests

```bash
# Unit tests only
pytest tests/test_unit.py -v

# Integration tests only
pytest tests/test_integration.py -v

# All tests
pytest tests/ -v
```

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | SQLAlchemy DB URL | `sqlite:///./calculations.db` |
| `SECRET_KEY` | JWT signing key | changeme |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry in minutes | `30` |

---

## BREAD Operations

| Operation | Route | Method | Description |
|---|---|---|---|
| **Browse** | `/history` | GET | View all calculations |
| **Read** | `/calculation/{id}` | GET | View single calculation detail |
| **Edit** | `/calculation/{id}/edit` | GET + POST | Modify calculation, recalculates result |
| **Add** | `/calculate` | POST | Run new calculation, saves to history |
| **Delete** | `/calculation/{id}/delete` | POST | Remove calculation from history |

---

## REST API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/calculate` | POST | Run calculation via JSON payload |
| `/api/history` | GET | Get all calculations as JSON |
| `/api/calculation/{id}` | DELETE | Delete calculation by ID |

Full interactive docs at: http://localhost:8000/docs

---

## Division by Zero Handling

The application handles division by zero at two levels:

**1. HTML form route** (`/calculate`):
elif operation in ("divide", "modulus") and b == 0:
error = "Cannot divide by zero."
The result panel shows a red error box — no crash, no exception.

**2. REST API route** (`/api/calculate`):
if payload.operation in ("divide", "modulus") and payload.operand_b == 0:
raise HTTPException(status_code=400, detail="Cannot divide by zero")
Returns HTTP 400 with a clear error message.

Both divide (`a / b`) and modulus (`a mod b`) are protected.

---

## Calculator UI Highlights

The calculator page was built with a game-like interactive feel:

- **Neon dark theme** using CSS variables and Orbitron display font
- **Animated starfield** generated by JavaScript on page load
- **Operation tile grid** — click any tile to select it, highlighted with cyan glow
- **Live explainer panel** — updates instantly when a tile is selected, showing:
  - Operation name and formula
  - Plain-English description
  - Worked numeric example
- **Live operator symbol** — the symbol between inputs changes to match selected operation
- **Animated result panel** — fades in with green glow on success, red on error
- **Pulsing CALCULATE button** — CSS keyframe glow animation

---

## Docker Hub

https://hub.docker.com/r/kverma19863020/is601-finalproject-kv

---

## CI/CD Pipeline

GitHub Actions (`.github/workflows/ci.yml`) runs on every push to `main`:

1. **test job** — installs Python 3.11, installs dependencies, runs all pytest tests
2. **docker job** — runs only after test job passes, builds Docker image,
   pushes to Docker Hub with `:latest` and `:<commit-sha>` tags
