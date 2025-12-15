# Repository Guidelines

## Project Structure & Module Organization
- `app/` holds FastAPI entrypoints (`app/main.py`), Celery setup/tasks, ORM models, config, and LangChain RAG helpers. Keep orchestration thin; share business logic across API and worker. 
- `scripts/` contains utilities like `ingest.py` for loading KB content into Chroma. 
- `kb/` stores Markdown/text sources; mounted read-only into containers. 
- `docker/` has Dockerfiles for `api` and `worker`; `docker-compose.yml` defines services `api`, `worker`, `redis`, `postgres` and volumes `pg_data`, `chroma_data`. 
- Add tests mirroring package paths under `tests/` as they are created.

## Build, Test, and Development Commands
- `docker compose up --build api worker redis postgres` — start the stack (API on 8000; worker consumes tasks; Redis/Postgres ready; Chroma persists to `chroma_data`). 
- `docker compose run --rm api python scripts/ingest.py` — ingest/update KB chunks into Chroma after editing files in `kb/`. 
- `docker compose run --rm api pytest -q` — run tests (once added); use `-k "<pattern>"` to focus. 
- `docker compose logs -f api worker` — tail service logs during development.

## Coding Style & Naming Conventions
- Python 3.11+, 4-space indentation, type hints required for public functions and Pydantic models. 
- Route handlers: verb-noun naming (`get_run`, `create_run`); Celery tasks: action-purpose (`ingest_kb`, `run_rag_query`). 
- Keep orchestration thin: FastAPI routers delegate to services; services call adapters (LLM, vector DB, Postgres). 
- Prefer small pure functions for business logic; make LLM prompts/versioning explicit in `app/prompts/` with clear ids. 

## Testing Guidelines
- Use `pytest`; file names `test_*.py`, classes `Test<Feature>`. 
- Unit tests for orchestration and validation; integration tests can run against Docker services (mark with `@pytest.mark.integration`). 
- Target >=80% coverage on new/changed files; include fixtures for KB docs and synthetic LLM responses to avoid network calls.

## Commit & Pull Request Guidelines
- Commit messages are imperative and scoped: `feat: add worker retry policy`, `fix: guard empty kb ingestion`. Squash locally if noisy. 
- PRs include: purpose summary, key changes, testing done, and any API examples (curl or HTTPie). Link issues and add screenshots/log excerpts when behavior changes. 

## Security & Configuration Tips
- Secrets (OpenAI keys, DB URLs) live in `.env`; never commit them. Provide `.env.example` updates whenever config changes. 
- Default to least privilege DB users; rotate tokens when rotating prompts or vector-store schemas. 
- When adding new tools/LLM calls, log inputs/outputs with redaction for sensitive fields.
