.PHONY: up down logs shell seed test fmt

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f app

shell:
	docker compose exec app bash

seed:
	docker compose exec app python scripts/seed.py

test:
	docker compose exec app pytest -q
