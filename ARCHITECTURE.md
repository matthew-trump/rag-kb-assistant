# Architecture

This document describes the architecture of the RAG KB Assistant and explains how the system is structured today, as well as how it is designed to evolve toward a cloud-native deployment on AWS.

The guiding principle is **explicit orchestration with observable, constrained LLM behavior**.

---

## High-Level System Overview

At a high level, the system consists of four major components:

1. **API Layer** — handles HTTP requests and user interaction
2. **Background Worker** — executes LLM workflows asynchronously
3. **Data Stores** — persist knowledge and execution traces
4. **LLM Provider** — performs inference and embedding generation

