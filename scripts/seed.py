import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.db import SessionLocal, init_db
from app.seed_data import seed_if_empty

if __name__ == "__main__":
    init_db()
    with SessionLocal() as db:
        seed_if_empty(db)
    print("Seed concluído.")
