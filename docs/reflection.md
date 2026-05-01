# Module 14 Reflection — BREAD Calculations

## What I Built
A full-stack web application implementing BREAD (Browse, Read, Edit, Add, Delete)
operations for a calculations resource. Users register, log in, and manage their
own calculation history (add, subtract, multiply, divide).

## Key Experiences

### FastAPI + SQLAlchemy
Working with FastAPI's dependency injection made it clean to protect routes with
`get_current_user`. SQLAlchemy's ORM handled database queries without raw SQL.

### Authentication
Implemented JWT-based session cookies with `python-jose` and `passlib`. The
cookie-based approach (rather than Authorization headers) integrates well with
HTML forms.

### BREAD vs CRUD
BREAD adds "Browse" (list all) as distinct from "Read" (single record), which
maps naturally to the `/calculations` vs `/calculations/{id}` pattern.

### Testing
Used FastAPI's `TestClient` with an in-memory SQLite test database. Fixtures
create a fresh DB per test to ensure isolation.

### Playwright E2E
E2E tests simulate real browser interactions — register, login, BREAD operations,
and negative cases like divide-by-zero and unauthenticated access.

### CI/CD with GitHub Actions
The pipeline runs unit tests on every push, then builds and pushes the Docker
image to Docker Hub only on main branch, ensuring the image always reflects
passing code.

## Challenges
- Handling form validation errors gracefully and re-rendering the form with
  the error message required careful routing logic.
- SQLite's lack of certain features (like `server_default` with timezones)
  required minor adjustments compared to PostgreSQL.

## What I Would Improve
- Add pagination to the Browse view.
- Add search/filter by operation type.
- Use PostgreSQL via Docker Compose for closer production parity.
