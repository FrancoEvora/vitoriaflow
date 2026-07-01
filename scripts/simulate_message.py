import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import argparse
from app.db import SessionLocal, init_db
from app.seed_data import seed_if_empty
from app.services.vitoria import VitoriaAgent


def main() -> None:
    parser = argparse.ArgumentParser(description="Simula mensagem recebida pela Vitória sem WhatsApp.")
    parser.add_argument("text", help="Texto da mensagem")
    parser.add_argument("--phone", default="5516999999999", help="Telefone do corretor")
    parser.add_argument("--name", default="Carlos", help="Nome de perfil do corretor")
    args = parser.parse_args()

    init_db()
    with SessionLocal() as db:
        seed_if_empty(db)
        reply = VitoriaAgent().handle_incoming(db, args.phone, args.text, args.name)
        print(reply)


if __name__ == "__main__":
    main()
