---
layout: post
title: "Design a Rate Limiter"
date: 2026-05-26
categories: [System Design, Interview Example, Distributed Systems, Scaling]
excerpt: "A comprehensive guide to designing a distributed rate limiter that controls request volume per client, covering placement, algorithms (fixed window, sliding window, token bucket), shared state with Redis, and scaling to millions of requests per second."
---

## Introduction

A rate limiter controls how many requests a client can make within a specific timeframe. It acts like a traffic controller for your API—allowing, for example, 100 requests per minute per user, then rejecting excess requests with HTTP 429 "Too Many Requests." Rate limiters prevent abuse, protect servers from bursts of traffic, and ensure fair usage across users.

This post walks through designing a **request-level** rate limiter for an API: identifying clients, choosing algorithms, storing shared state, and scaling to 1M requests per second across 100M daily active users. It draws on patterns such as [dealing with contention](https://www.hellointerview.com/learn/system-design/patterns/dealing-with-contention), [scaling writes](https://www.hellointerview.com/learn/system-design/patterns/scaling-writes), and [scaling reads](https://www.hellointerview.com/learn/system-design/patterns/scaling-reads).

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Requirements](#requirements)
   - [Functional Requirements](#functional-requirements)
   - [Non-Functional Requirements](#non-functional-requirements)
3. [Core Entities](#core-entities)
4. [System Interface](#system-interface)
5. [High-Level Design](#high-level-design)
   - [Placement](#placement)
   - [Client Identification](#client-identification)
   - [Rate Limiting Algorithms](#rate-limiting-algorithms)
   - [Shared State: Redis + Token Bucket](#shared-state-redis--token-bucket)
   - [Response When Limit Exceeded](#response-when-limit-exceeded)
6. [Deep Dives](#deep-dives)
   - [Scaling to 1M Requests/Second](#scaling-to-1m-requestssecond)
   - [High Availability and Fault Tolerance](#high-availability-and-fault-tolerance)
   - [Minimizing Latency](#minimizing-latency)
   - [Hot Keys](#hot-keys)
   - [Dynamic Rule Configuration](#dynamic-rule-configuration)
7. [Summary](#summary)
8. [References](#references)

## Problem Statement

**Design a rate limiter that:**

1. Identifies clients by user ID, IP address, or API key
2. Limits HTTP requests based on configurable rules (e.g., 100 requests/minute per user)
3. Rejects excess requests with HTTP 429 and helpful headers (remaining, reset time)
4. Introduces minimal latency (< 10 ms per check) and is highly available
5. Scales to 1M requests/second across 100M daily active users

**Out of Scope (for this design):**

- Complex querying or analytics on rate limit data
- Long-term persistence of rate limiting data
- Strong consistency across all nodes (eventual consistency is acceptable)

## Requirements

### Functional Requirements

**Core Requirements:**

1. **Client identification:** Identify clients by user ID, IP address, or API key to apply appropriate limits.
2. **Configurable rules:** Limit requests based on rules (e.g., 100 API requests per minute per user, 10 requests/minute per IP for search).
3. **Reject with 429:** When limits are exceeded, reject requests with HTTP 429 and include headers such as `X-RateLimit-Remaining` and `X-RateLimit-Reset`.

**Out of Scope:**

- Client-side-only rate limiting (server-side is required for security)
- Queuing excess requests (fail fast is assumed)

### Non-Functional Requirements

**Core Requirements:**

1. **Low latency:** Minimal overhead per request (< 10 ms for the rate limit check).
2. **High availability:** System should be highly available; eventual consistency across nodes is acceptable.
3. **Scale:** Handle 1M requests/second across 100M daily active users.

## Core Entities

1. **Rules:** Rate limiting policies—e.g., "authenticated users: 1000 requests/hour," "search API: 10 requests/minute per IP." Each rule specifies limits, time window, and which clients/endpoints it applies to.
2. **Clients:** Entities being rate limited—users (by user ID), IP addresses, or API keys. Each client has state (e.g., token count, window counters) tracked against applicable rules.
3. **Requests:** Incoming API requests evaluated against rules; each request carries client identity, endpoint, and timestamp.

Flow: **Request** → identify **Client** → look up **Rules** → check usage → allow or deny.

## System Interface

The rate limiter is an infrastructure component that other services (e.g., API gateway) call to decide if a request is allowed:

```
isRequestAllowed(clientId, ruleId) -> { allowed: boolean, remaining: number, resetTime: timestamp }
```

- **Input:** Client identifier (user ID, IP, or API key) and rule identifier.
- **Output:** Whether the request is allowed, remaining requests in the window, and when the limit resets (for headers like `X-RateLimit-Remaining`, `X-RateLimit-Reset`).

## High-Level Design

### Placement

| Option | Pros | Cons |
|--------|------|------|
| **In-process** (inside app server) | No extra network hop | State not shared across instances; load balancer distributes requests, so each node sees only a fraction of traffic → limits are ineffective |
| **Dedicated service** | Centralized logic, reusable | Extra network call per request |
| **API Gateway / Load Balancer** | Centralized, no extra hop from client’s perspective; sees all traffic to the API | Gateway must support rate limiting or integrate with shared store |

**Recommended:** Rate limiter at **API Gateway** (or LB) so every request is checked before hitting application servers, with shared state in a store like Redis.

### Client Identification

Using only data in the HTTP request (no extra DB calls):

- **User ID:** From auth (e.g., JWT in `Authorization`). Best for authenticated APIs; each user gets their own limit.
- **IP address:** From `X-Forwarded-For` or similar. Good for anonymous or public APIs; be aware of NATs/shared IPs.
- **API key:** From `X-API-Key`. For developer APIs; each key gets its own limit.

Multiple rules can apply (e.g., per-user and per-IP). Enforce the **most restrictive** limit: if the user is under their user limit but the IP is over the IP limit, reject.

### Rate Limiting Algorithms

| Algorithm | Idea | Pros | Cons |
|-----------|------|------|------|
| **Fixed window counter** | Count requests per fixed window (e.g., 1-minute buckets); reset at window boundary | Simple, low memory | Boundary burst: 100 at 12:00:59 and 100 at 12:01:00 ⇒ 200 in 2 seconds |
| **Sliding window log** | Keep timestamps of recent requests; count only those inside the last N seconds | Accurate sliding window | High memory (many timestamps per client), more CPU to trim old entries |
| **Sliding window counter** | Use current + previous window counters; approximate sliding count with a weighted sum | Better than fixed window, only 2 counters per client | Approximate; assumes roughly uniform traffic in the window |
| **Token bucket** | Bucket of tokens; refill at constant rate; each request consumes one token; reject when empty | Handles bursts and sustained rate; simple state: (tokens, last_refill) | Need to tune capacity and refill rate |

**Recommended:** **Token bucket** for a good balance of simplicity, memory efficiency, and realistic traffic (bursts + steady rate). Used in production by many companies (e.g., Stripe).

### Shared State: Redis + Token Bucket

Rate limit state must be **shared** across all gateway instances. If each node keeps its own bucket, a user spread across nodes can exceed the global limit.

**Store state in Redis:**

- Key: e.g. `{clientId}:{ruleId}:bucket` (or similar).
- Value: Hash with `tokens` (current count) and `last_refill` (timestamp).
- Refill: On each request, compute new tokens from `min(capacity, current + (now - last_refill) * refill_rate)`, then decrement by 1 if allowed.
- **Atomicity:** The read–refill–decrement must be atomic. Use a **Lua script** in Redis so the whole check-and-update runs as one operation (avoids race conditions where two gateways both allow when only one token remains).
- **TTL:** Use `EXPIRE` on the key (e.g., 1 hour of inactivity) so inactive clients don’t fill memory.

**Pattern:** [Dealing with contention](https://www.hellointerview.com/learn/system-design/patterns/dealing-with-contention)—multiple gateways updating the same bucket; the atomic boundary must be the full read-modify-write, not just a single Redis command.

### Response When Limit Exceeded

- **Fail fast:** Reject immediately; do not queue for later.
- **HTTP 429** "Too Many Requests."
- **Headers:**
  - `X-RateLimit-Limit`: limit (e.g., 100)
  - `X-RateLimit-Remaining`: 0 when rejected
  - `X-RateLimit-Reset`: Unix timestamp when the limit resets
  - `Retry-After`: seconds until reset (optional)

Example:

```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640995200
Retry-After: 60
```

## Deep Dives

### Scaling to 1M Requests/Second

A single Redis instance can handle on the order of ~100k–200k ops/sec. At 1M requests/second, each check (e.g., Lua script) may do several ops, so one Redis is a bottleneck.

**Shard Redis by client identity:**

- Partition keys by `clientId` (user ID, IP, or API key) so that all requests for the same client hit the **same** Redis shard. Use **consistent hashing** so that gateways can route `clientId` → shard without a central lookup.
- Each shard runs the same Token Bucket logic; only the key space is partitioned. With ~10 shards of ~100k ops/sec each, you can reach ~1M checks/sec.

**In production:** Use **Redis Cluster**, which shards by key (e.g., 16k hash slots) and routes automatically. Gateways connect to the cluster; Redis routes each key to the right node.

**Pattern:** [Scaling writes](https://www.hellointerview.com/learn/system-design/patterns/scaling-writes)—high write rate to counters/buckets; sharding by client keeps each client’s updates on one node and distributes load.

### High Availability and Fault Tolerance

**Failure mode when a Redis shard is down:**

- **Fail-closed:** If Redis is unavailable, reject the request (treat as rate limited). Safer for the backend; avoids a burst when the limiter is down.
- **Fail-open:** If Redis is unavailable, allow the request. Better for availability; risk of overload during Redis outage.

**Recommendation:** For a typical API, **fail-closed** is often preferred so that during outages (e.g., traffic spikes) we don’t disable protection.

**Availability of Redis:**

- Use **master-replica** per shard; promote a replica if the master fails. **Redis Cluster** supports automatic failover. Replication adds some lag but is usually acceptable for rate limiting.

### Minimizing Latency

- **Connection pooling:** Reuse TCP connections to Redis from gateways; avoid a new connection per request. Tune pool size to request volume.
- **Geography:** Put Redis (and gateways) close to users. Cross-region latency can add milliseconds; same-region Redis keeps checks in the single-digit ms range.
- **Optional:** Lua script keeps the check to one round-trip; pipelining can help if you batch multiple checks (e.g., per-user and per-IP in one pipeline).

### Hot Keys

A single client (user/IP/API key) generating a very high request rate can overload one Redis shard (hot key).

**Pattern:** [Scaling reads](https://www.hellointerview.com/learn/system-design/patterns/scaling-reads)—hot keys cause a lot of read/write to one key.

**Mitigations:**

- **Legitimate high-volume clients:** Client-side rate limiting (e.g., SDK respecting `X-RateLimit-*`), batching, or higher limits / premium tiers.
- **Abusive traffic:** After repeated 429s, temporarily block the client (e.g., blocklist by IP or API key); use DDoS protection (e.g., Cloudflare, AWS Shield) in front of the API.

Design limits with shared IPs (NAT, offices) in mind; prefer user-based or API-key-based limits where possible.

### Dynamic Rule Configuration

Rules may change without code deploy (e.g., higher limits for a launch, different limits per tier).

- **Polling:** Gateways periodically fetch rules from a config service or DB. Simple; slight delay to propagate changes.
- **Push:** Config service pushes updates (e.g., webhooks, pub/sub) to gateways. Faster propagation; more moving parts.

Choose based on how often rules change and how quickly they must take effect.

## Summary

| Topic | Recommendation |
|-------|----------------|
| **Placement** | API Gateway (or LB) with shared state in Redis. |
| **Client ID** | User ID, IP, or API key from request; apply most restrictive rule. |
| **Algorithm** | Token bucket (capacity + refill rate); simple and burst-friendly. |
| **State** | Redis; key = client+rule, value = token bucket; atomic updates via Lua script; TTL for cleanup. |
| **Scale** | Shard Redis by client (consistent hashing or Redis Cluster) to reach ~1M req/s. |
| **Availability** | Redis master-replica + failover; fail-closed when Redis unavailable. |
| **Latency** | Connection pooling, same-region Redis, single Lua round-trip. |
| **Response** | 429 with X-RateLimit-Limit, Remaining, Reset, Retry-After. |

A rate limiter is a classic **contention** and **write-scaling** problem: shared mutable state (the bucket), atomic read-modify-write, and sharding by client to scale.

## References

- [ByteByteGo – Design a Rate Limiter](https://bytebytego.com/courses/system-design-interview/design-a-rate-limiter)
- [YouTube – System Design Interview: Rate Limiter](https://www.youtube.com/watch?v=YXkOdWBwqaA)
- [Hello Interview – Design a Distributed Rate Limiter](https://www.hellointerview.com/learn/system-design/problem-breakdowns/distributed-rate-limiter)
