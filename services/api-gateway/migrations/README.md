# API Gateway Migration Path

This service still uses `Base.metadata.create_all()` for local demo startup, but schema changes must be mirrored here before Phase 10+ work.

Initial schema SQL is stored in `001_initial_schema.sql`. A future Alembic migration can use the same table definitions as its baseline.

Recommended local smoke check:

```powershell
$env:GATEWAY_DATABASE_URL="postgresql+psycopg://localbank:localbank@localhost:5432/localbank_triage"
python .\scripts\postgres_smoke.py
```

SQLite unit tests are fast feedback only; they are not considered PostgreSQL coverage.
