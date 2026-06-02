# auth-service

Local FastAPI authentication service for the LocalBank-Triage staff access gate.

## Demo Credentials

`employees_seed.json` contains local demo-only credentials for development and testing. The seed file contains plaintext access codes, but the SQLite database stores only PBKDF2 hashes.

## Environment

Create `.env` from `.env.example` only for local use.

```powershell
$env:AUTH_DATABASE_URL="sqlite:///data/auth/auth.db"
$env:AUTH_SESSION_EXPIRE_MINUTES="60"
```

## Install

```powershell
python -m pip install -r .\services\auth-service\requirements.txt
```

## Seed Demo Employees

```powershell
python .\services\auth-service\seed_employees.py
```

## Run

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir .\services\auth-service
```

## Endpoints

- `GET /health`
- `POST /auth/login`
- `GET /auth/me`
- `POST /auth/logout`
