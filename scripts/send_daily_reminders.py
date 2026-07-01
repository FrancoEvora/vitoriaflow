import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.db import init_db
from app.services.reminders import send_daily_reminders_sync

if __name__ == "__main__":
    init_db()
    send_daily_reminders_sync()
    print("Rotina de lembretes executada.")
