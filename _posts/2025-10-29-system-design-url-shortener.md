---
layout: post
title: "System Design: URL Shortener (bit.ly)"
date: 2025-10-29 23:05:00 -0700
categories: system-design architecture
permalink: /2025/10/29/system-design-url-shortener/
tags: [system-design, cache, database, consistency, idempotency]
---

# System Design: URL Shortener

## Requirements
- Shorten and resolve URLs; custom aliases; TTL; analytics optional.

## APIs
```http
POST /v1/shorten { long_url, custom? } -> { short_code }
GET  /{short_code} -> 302 Location: long_url
```

## High-level
Clients → API → Cache (Redis) → DB (MySQL/Cassandra) → Analytics (Kafka)

## Data model
`urls(code PK, long_url, created_at, expires_at, owner)`

## Code generation
- Base62 from numeric id; or hash(long_url) + collision check; reserve words blacklist.

## Consistency
- Strong on create (unique code constraint); eventual for analytics counts.

## Capacity
- 1B reads/day (~11.6k rps avg, 100k rps peak); 100M writes/day (~1.1k rps).
- Cache hit > 95% for resolves; Redis with TTL and negative caching.

## SLOs
- Resolve P95 < 50 ms; Shorten P95 < 200 ms; 99.9% availability.

## Failures
- Cache miss storm → single-flight; warmup popular codes; rate limit.

## Evolution
- Shard by code prefix; add geo DNS; move analytics to stream processing.

## DDL sketch

```sql
CREATE TABLE urls (
  code varchar(10) PRIMARY KEY,
  long_url text NOT NULL,
  created_at timestamptz NOT NULL,
  expires_at timestamptz,
  owner bigint
);
```

## Cache strategy

- Cache‑aside with negative caching for 404s; TTL skew to avoid stampedes; single‑flight locks per code.

## Failure drills

- DB hot partition → rehash codes; add read replicas; protect with rate limit per IP.
