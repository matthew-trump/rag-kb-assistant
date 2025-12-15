# Design Decisions

This document explains the major design decisions behind the RAG KB Assistant, with an emphasis on trade-offs and production considerations.

---

## 1. FastAPI + Background Workers

**Decision:** Use FastAPI for the API layer and a background worker for execution.

**Why:**
- LLM calls are slow and unpredictable
- Blocking HTTP requests leads to poor reliability
- Async execution enables retries and timeouts

**Alternative considered:** synchronous API calls  
**Rejected because:** it couples user experience to LLM latency and failures.

---

## 2. Explicit Workflows Over Autonomous Agents

**Decision:** Implement agentic behavior as explicit workflows rather than autonomous agent loops.

**Why:**
- Predictable execution paths
- Easier debugging
- Easier testing
- Easier cost control

**Alternative considered:** LangChain Agent executors  
**Rejected because:** they obscure control flow and complicate observability.

---

## 3. Structured Outputs Everywhere

**Decision:** Enforce schema-validated outputs from LLMs.

**Why:**
- Free-text parsing is fragile
- Schema validation provides fail-fast behavior
- Enables reliable downstream processing

This turns LLM output into a typed interface, not a suggestion.

---

## 4. RAG Over Fine-Tuning

**Decision:** Use retrieval-augmented generation instead of model fine-tuning.

**Why:**
- Lower cost
- Faster iteration
- Easier updates to knowledge
- Clearer grounding and citations

Fine-tuning may be appropriate later, but RAG provides the best baseline.

---

## 5. Local-First Development

**Decision:** Optimize for local development first.

**Why:**
- Faster iteration
- Lower cognitive overhead
- Easier debugging

The architecture maps cleanly to AWS without early cloud lock-in.

---

## 6. Celery First, Step Functions Later

**Decision:** Start with Celery for orchestration.

**Why:**
- Simple to reason about
- Easy to run locally
- Mirrors real orchestration needs

The workflow is designed so it can be migrated to AWS Step Functions with minimal changes.

---

## 7. Replaceable Infrastructure Components

**Decision:** Avoid hard dependencies on specific vendors.

**Why:**
- OpenAI → Bedrock / Anthropic
- Chroma → OpenSearch / pgvector
- Celery → Step Functions

This protects the design from premature lock-in.

---

## 8. Treat LLMs as Unreliable Dependencies

**Decision:** Assume LLMs will:
- hallucinate
- fail schema validation
- timeout
- change behavior over time

**Mitigation:**
- validation
- retries
- explicit failure states
- persisted traces

---

## Summary

Every design decision favors:
- clarity over cleverness
- explicit control over autonomy
- debuggability over novelty

This reflects how production systems are actually built.
