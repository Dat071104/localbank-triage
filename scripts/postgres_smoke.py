from __future__ import annotations

import os
import sys
from pathlib import Path


def main() -> int:
    database_url = os.getenv("GATEWAY_DATABASE_URL")
    if not database_url or "postgresql" not in database_url:
        print("SKIPPED: set GATEWAY_DATABASE_URL to a PostgreSQL URL to run this smoke check.")
        return 0
    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root / "services" / "api-gateway"))
    from app.db import build_engine
    from app.models import Base

    engine = build_engine(database_url)
    with engine.begin() as connection:
        Base.metadata.create_all(bind=connection)
        table_names = set(Base.metadata.tables)
    print(f"PostgreSQL smoke initialized tables: {', '.join(sorted(table_names))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
