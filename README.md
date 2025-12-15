# RAG KB Assistant  
*A practical, production-minded agentic application*

## Overview

This project is an intentionally **simple but realistic “agentic” application** built to explore how modern LLM-based systems are actually engineered in practice.

The goal is **not** to build a fully autonomous AI, but to build a **useful, debuggable, and scalable application** that combines:

- FastAPI for a clean HTTP API
- LangChain for LLM plumbing (RAG, structured outputs)
- A vector database for retrieval-augmented generation (RAG)
- A background worker for asynchronous execution
- Clear boundaries between orchestration, LLM calls, and business logic

Initially, this project runs **locally** and is optimized for clarity and learning.  
Over time, it is designed to be deployable to **AWS** in a scalable, production-ready way.

---

## Project Intent

This repository exists to answer a practical question:

> *What does “building an agentic LLM application” actually mean, beyond the buzzwords?*

Concretely, this project aims to:

- Build a **retrieval-augmented knowledgebase assistant**
- Treat the LLM as an **unreliable component**, not an oracle
- Use **explicit workflows and guardrails**, not unconstrained autonomy
- Favor **structured outputs, validation, and traceability**
- Separate:
  - API layer
  - Background execution
  - LLM interactions
  - Data persistence

This reflects how serious LLM applications are built in real systems.

---

## What “Agentic” Means Here

In this project, *agentic* does **not** mean:

- Fully autonomous systems
- Infinite tool-calling loops
- “The model figures everything out”

Instead, it means:

- The system performs **multi-step reasoning**
- It **retrieves information**, evaluates it, and produces a response
- Decisions are made in **constrained, observable steps**
- Control flow is explicit and testable

Today, this looks like a **RAG workflow**.  
Later, it can evolve into more complex workflows (branching, tool usage, human-in-the-loop).

---

## Current Functionality

At its current stage, the system provides:

- A **REST API** for submitting questions
- A **background worker** that:
  - Retrieves relevant documents from a vector store
  - Calls an LLM with retrieved context
  - Produces a **structured response** (answer, citations, confidence)
- Persistent storage of:
  - Each “run”
  - Inputs, outputs, and status
- A simple **local knowledgebase** ingested from Markdown/text files

The application is deliberately minimal, but complete end-to-end.

---

## Tech Stack

### Core
- **FastAPI** — API layer
- **Celery + Redis** — background task execution
- **LangChain** — RAG and structured LLM interactions
- **Chroma** — local persistent vector store
- **PostgreSQL** — run and trace storage

### LLM
- OpenAI APIs (easily swappable for Bedrock, Anthropic, etc.)

### Infrastructure (initial)
- Docker & Docker Compose
- Local-first development

---

## Architecture (High Level)

Client
|
| POST /ask
v
FastAPI API
|
| enqueue background task
v
Celery Worker
|
| retrieve context (RAG)
| call LLM
| validate structured output
v
PostgreSQL (runs) + Vector Store (knowledge)

Key characteristics:
- API remains responsive
- LLM execution is isolated
- Results are persisted and inspectable
- Failures are explicit and recoverable

---

## Design Decisions (and Why)

### 1. Asynchronous execution from day one
LLM calls are slow, expensive, and failure-prone.  
Using a background worker avoids blocking APIs and mirrors real production deployments.

### 2. Explicit workflows over autonomous agents
Rather than a free-running agent loop, this project uses **explicit, inspectable steps**.
This dramatically improves reliability and debuggability.

### 3. Structured outputs instead of free-text parsing
All LLM responses are validated against schemas.  
If the model fails to comply, the system fails safely.

### 4. Local-first, cloud-ready
Local development reduces friction, but the architecture cleanly maps to:
- AWS ECS or Lambda
- AWS Step Functions
- Managed vector stores

### 5. Replaceable components
The system is designed so that:
- Celery → Step Functions
- Chroma → OpenSearch / pgvector
- OpenAI → Bedrock / Anthropic

…without rewriting core logic.

---

## What This Project Is *Not*

- A toy demo
- A prompt-engineering experiment
- A claim of autonomous AI
- A fine-tuned model or ML research project

It is a **software engineering project** that treats LLMs as one component in a larger system.

---

## Roadmap

### Near-term
- Improved tracing (latency, token usage, retrieved chunks)
- Streaming responses (SSE / WebSockets)
- Authentication and API keys
- Better retry and failure semantics

### Medium-term
- Richer agentic workflows (branching, tool usage)
- Human-in-the-loop approval steps
- Migration from Celery to AWS Step Functions
- Replace Chroma with a managed vector store

### Long-term
- Full AWS deployment (ECS or Lambda)
- OpenTelemetry instrumentation
- Cost controls and quotas
- Multi-tenant support

---

## Running Locally

See the setup instructions for:
- Environment configuration
- Document ingestion
- API usage

Quick start:
- Copy `.env.example` to `.env` and set `OPENAI_API_KEY` (and any other secrets).
- Run `docker compose up --build api worker redis postgres` in one terminal.
- In another terminal, ingest docs with `docker compose run --rm api python scripts/ingest.py`.
- Run tests: `docker compose run --rm api pytest -q` (once tests are added); lint with `docker compose run --rm api ruff check .`.
- Make targets: `make up`, `make ingest`, `make test`, `make lint`, `make logs`, `make down`.

Local development is the default and encouraged.

---

## Who This Is For

This repository is intended for:

- Engineers interested in **real-world LLM system design**
- Teams evaluating how to move from demos to production
- Hiring managers reviewing **production-quality backend work**
- Anyone curious what “agentic AI” actually looks like when implemented responsibly

---

## License

MIT


## Why Not LangChain Agents?

This project intentionally does **not** use LangChain’s autonomous agent executors.

While agent loops (ReAct-style “think → act → observe”) are useful for exploration and prototyping, they introduce significant challenges in production systems:

- Hidden control flow
- Difficult debugging
- Unbounded execution paths
- Hard-to-predict cost and latency
- Complex failure modes

In contrast, this project favors:

- Explicit workflows
- Deterministic orchestration
- Constrained decision points
- Schema-validated outputs

LangChain is still used where it excels:
- retrieval (RAG)
- prompt composition
- structured output parsing

But orchestration remains in application code, where it can be observed, tested, and evolved safely.

This mirrors the direction many production LLM teams take after early experimentation with fully autonomous agents.
