COMPOSE = docker compose

.PHONY: help up down ingest test lint logs

help:
	@echo "Available targets:"
	@echo "  make up     - build and start api, worker, redis, postgres"
	@echo "  make down   - stop services"
	@echo "  make ingest - run KB ingestion"
	@echo "  make test   - run pytest (inside api container)"
	@echo "  make lint   - run ruff check (inside api container)"
	@echo "  make logs   - tail api and worker logs"

up:
	$(COMPOSE) up --build api worker redis postgres

down:
	$(COMPOSE) down

ingest:
	$(COMPOSE) run --rm api python scripts/ingest.py

test:
	$(COMPOSE) run --rm api pytest -q

lint:
	$(COMPOSE) run --rm api ruff check .

logs:
	$(COMPOSE) logs -f api worker
