---
layout: post
title: "System Design: ChatGPT-Style LLM Service (Serving, Caching, Safety)"
date: 2025-10-29 21:30:00 -0700
categories: system-design architecture ai
permalink: /2025/10/29/system-design-chatgpt/
tags: [system-design, llm, inference, caching, safety, retrieval]
---

# System Design: ChatGPT-Style LLM Service (Serving, Caching, Safety)

Goal: low‑latency, high‑availability text generation (and tools) with safety, rate limiting, and observability.

## Requirements

- Streaming tokens (<200 ms first token), batch throughput, multi‑tenant quotas, session history, tool use (functions), file/RAG.

## Architecture overview

```
Clients → API Gateway (AuthN/Z, rate limit, quotas)
  → Orchestrator (routing, context mgmt, tool calls)
    → Inference Fleet (GPU/TPU)  → KV Cache (paged attention)
    → Safety Filters (pre/post)
    → Retrieval (vector store, doc store) via RAG
  → Event Bus (telemetry)
```

## Inference serving

- Models sharded across GPUs with tensor/pipe parallel; batching/scheduling for high utilization.
- KV cache reuse across turns; paged‑attention cache in GPU/host memory tiers.
- Multi‑model routing (cost/latency/quality); fallback to smaller models under load.

## Context and tools

- Conversation store (compressed) with truncation strategies; tools/plugins invoked via JSON schemas.
- Function calling: orchestrator validates args; tool sandbox with timeouts and quotas.

## Retrieval (RAG)

- Embeddings service builds vectors for docs; chunking + metadata; ANN index (HNSW/IVF‑PQ).
- At query time: recall top‑k, re‑rank, synthesize context; guard context length with budgeters.

## Caching and dedup

- Prompt/result cache (normalized input) for deterministic prompts; stage caches (embedding, retrieval, decode prefixes).
- Safety: never cache sensitive PII; encrypt at rest.

## Safety and policy

- Pre‑filters (regex/keyword/ML) and post‑filters (classifier) for harmful content; red teaming and appeals.
- Audit logs of prompts/outputs; data retention policies per tenant.

## Observability and reliability

- Token‑level metrics (TTFT, TPS, errors); autoscaling; circuit breakers; brownout mode (shorter max tokens) under load.

## APIs

```http
POST /v1/chat/completions { model, messages[], tools?, tool_choice? }
POST /v1/embeddings { model, input }
```

## Capacity planning

- Target: 100k concurrent sessions, TTFT < 200 ms, 50 tokens/s median decode.
- GPU math: model needs 40 GB per replica; with paged‑attention, cache ~128k tokens/GPU; plan cache tiers (GPU/HBM → CPU RAM → SSD) with eviction.
- Routing: batch size 8–16 to keep utilization > 60% without harming latency; autoscale on queue depth and TTFT SLO.

## SLOs & safety

- SLOs: TTFT, tokens/sec, error rate; budget enforces brownouts (max tokens cap) when violated.
- Safety: pre/post filters with allow/deny lists; privacy guardrails per tenant; audit retention limits.

## Failure modes

- GPU node loss: retry to alternate pool; preserve cache keys when possible; degrade to smaller model if capacity constrained.
- RAG backends slow: fall back to last known context or skip retrieval with warning tag.

## Detailed APIs

```http
POST /v1/chat/completions { model, messages[], tools?, tool_choice?, stream? }
event: chunk  data: { role, delta, usage? }
```

## Orchestrator design

- Router selects model/pool; KV cache coordinator attaches cache id; streaming gateway multiplexes SSE chunks.
- Tooling: JSON schema validation and safe tool sandbox with timeouts; retries with circuit breaker per tool.

## Capacity BoE

- 100k concurrent streams @ 50 tok/s → 5M tok/s; plan GPU count for model throughput; batch size 8–16.
- KV cache: 128k tokens/GPU tier; promote hot sessions; evict with LRU per tenant.

## Testing & eval

- Load gen with mixed prompts/tools; TTFT SLO monitors; shadow deploys for new model versions with guardrails.
