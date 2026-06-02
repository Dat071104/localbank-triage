# LocalBank API Gateway

Workflow and RBAC orchestration service backed by PostgreSQL for local product data.

## Run locally

```powershell
cd "D:\Project cua Dat\Localbank-triage\services\api-gateway"
python -m pip install -r requirements.txt
$env:GATEWAY_DATABASE_URL="postgresql+psycopg://localbank:localbank@localhost:5432/localbank_triage"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8005
```

## Endpoints

- `GET /health`
- `POST /tickets`
- `GET /tickets`
- `GET /tickets/{ticket_id}`
- `POST /tickets/{ticket_id}/analyze`
- `GET /tickets/{ticket_id}/analysis`
- `POST /tickets/{ticket_id}/draft`
- `GET /tickets/{ticket_id}/draft`
- `POST /tickets/{ticket_id}/review`
- `GET /tickets/{ticket_id}/audit`

The gateway calls `auth-service /auth/me` for bearer-token verification. Tests override this dependency and use SQLite, so they do not require a live full stack.

