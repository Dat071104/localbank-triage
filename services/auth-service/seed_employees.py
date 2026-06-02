from __future__ import annotations

from pathlib import Path

from app.db import get_database_url, load_seed_employees, seed_employees


def main() -> None:
    seed_path = Path(__file__).with_name("employees_seed.json")
    seed_records = load_seed_employees(seed_path)
    seeded = seed_employees(seed_records)
    print(f"Seeded {seeded} demo employees into {get_database_url()}")


if __name__ == "__main__":
    main()
