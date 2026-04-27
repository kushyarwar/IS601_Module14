# IS601 Module 14 - Calculation BREAD Functionality

FastAPI application with JWT authentication, user-scoped calculation BREAD endpoints, static front-end pages, pytest integration tests, Playwright E2E tests, Docker, and GitHub Actions CI/CD.

## Repository and Docker Hub

GitHub repository: https://github.com/kushyarwar/IS601_Module14.git

Docker Hub image: `kushyarwar/is601-module14:latest`

```bash
docker pull kushyarwar/is601-module14:latest
docker run -p 8000:8000 \
  -e DATABASE_URL=<your-postgres-url> \
  -e JWT_SECRET=<your-secret> \
  kushyarwar/is601-module14:latest
```

## Running the Application Locally

```bash
docker-compose up --build
```

Open these pages:

| Page | URL |
|------|-----|
| Register | http://localhost:8000/static/register.html |
| Login | http://localhost:8000/static/login.html |
| Calculations | http://localhost:8000/static/calculations.html |
| API Docs | http://localhost:8000/docs |
| pgAdmin | http://localhost:5050 |

The calculation page uses the JWT saved in `localStorage` after login or registration. It supports browse, read, edit, add, and delete actions for the logged-in user's own calculations.

## Running Tests Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run integration tests:

```bash
pytest tests/ --ignore=tests/e2e -v --cov=app --cov-report=term-missing
```

Run Playwright tests:

```bash
playwright install chromium
pytest tests/e2e/ -v
```

The E2E suite starts a local SQLite-backed server on port 8001 and shuts it down after the tests finish.

## API Endpoints

### Auth

| Method | Path | Description |
|--------|------|-------------|
| POST | `/register` | Register and return JWT |
| POST | `/login` | Login and return JWT |
| POST | `/users/register` | Same register endpoint |
| POST | `/users/login` | Same login endpoint |

### Calculations

All calculation routes require:

```text
Authorization: Bearer <jwt>
```

| Method | Path | Description |
|--------|------|-------------|
| GET | `/calculations` | Browse logged-in user's calculations |
| GET | `/calculations/{id}` | Read one calculation owned by the user |
| POST | `/calculations` | Add a calculation |
| PUT | `/calculations/{id}` | Edit a calculation |
| PATCH | `/calculations/{id}` | Partially edit a calculation |
| DELETE | `/calculations/{id}` | Delete a calculation |

Supported operations: `Add`, `Sub`, `Multiply`, `Divide`.

Create calculation body:

```json
{ "a": 10, "b": 5, "type": "Add" }
```

Example response:

```json
{ "id": 1, "a": 10.0, "b": 5.0, "type": "Add", "result": 15.0, "user_id": 1 }
```

## CI/CD Pipeline

GitHub Actions workflow: `.github/workflows/ci.yml`

The workflow:

1. Starts PostgreSQL 15 for integration tests.
2. Installs Python dependencies and Playwright Chromium.
3. Runs pytest integration tests with coverage.
4. Runs Playwright E2E tests.
5. Builds and pushes `kushyarwar/is601-module14:latest` to Docker Hub on pushes to `main`.
6. Runs a Trivy vulnerability scan on the pushed image.

Required GitHub secrets:

```text
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
```

## Screenshots

Add these screenshots before final submission:

| Requirement | File |
|-------------|------|
| GitHub Actions successful workflow | `Screenshots/1.png` |
| Docker Hub pushed image | `Screenshots/2.png` |
| Calculation add/browse in front-end | `Screenshots/3.png` |
| Calculation read/edit/delete in front-end | `Screenshots/4.png` |

The repository currently includes the `Screenshots` folder so the files can be replaced with final Module 14 captures.
