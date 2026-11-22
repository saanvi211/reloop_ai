from __future__ import annotations

from backend.database import SessionLocal, init_db
from backend.services.seed import seed_database


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    print("Database initialised and demo data seeded.")


if __name__ == "__main__":
    main()
