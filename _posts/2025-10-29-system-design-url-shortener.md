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

## What Interviewers Look For

### URL Shortener Skills

1. **Code Generation**
   - Base62 encoding
   - Collision handling
   - Custom aliases
   - **Red Flags**: Collisions, no custom aliases, inefficient encoding

2. **Caching Strategy**
   - Cache-aside pattern
   - Negative caching
   - TTL management
   - **Red Flags**: No caching, cache stampedes, poor hit rate

3. **High Read/Write Ratio**
   - Read-heavy optimization
   - Cache hit rate > 95%
   - **Red Flags**: Poor read performance, low cache hit rate, slow resolves

### Distributed Systems Skills

1. **Scalability Design**
   - Sharding by code prefix
   - Horizontal scaling
   - **Red Flags**: No sharding, vertical scaling, bottlenecks

2. **Consistency Models**
   - Strong consistency for creates
   - Eventual for analytics
   - **Red Flags**: Wrong consistency, no understanding

3. **Idempotency**
   - Unique code constraint
   - Safe retries
   - **Red Flags**: No idempotency, duplicate codes, race conditions

### Problem-Solving Approach

1. **Cache Stampede Prevention**
   - Single-flight locks
   - Warmup strategies
   - **Red Flags**: Cache stampedes, no protection, poor performance

2. **Edge Cases**
   - Hot partitions
   - Cache misses
   - Expired URLs
   - **Red Flags**: Ignoring edge cases, no handling

3. **Trade-off Analysis**
   - Consistency vs performance
   - Storage vs cost
   - **Red Flags**: No trade-offs, dogmatic choices

### System Design Skills

1. **Component Design**
   - Shorten service
   - Resolve service
   - Analytics service
   - **Red Flags**: Monolithic, unclear boundaries

2. **Database Design**
   - Proper indexing
   - Sharding strategy
   - **Red Flags**: Missing indexes, no sharding, poor queries

3. **Analytics Design**
   - Click tracking
   - Stream processing
   - **Red Flags**: No analytics, synchronous processing, bottlenecks

### Communication Skills

1. **Architecture Explanation**
   - Can explain code generation
   - Understands caching strategy
   - **Red Flags**: No understanding, vague explanations

2. **Scale Explanation**
   - Can explain scaling strategies
   - Understands bottlenecks
   - **Red Flags**: No understanding, vague

### Meta-Specific Focus

1. **High-Throughput Systems Expertise**
   - Read-heavy optimization
   - Caching expertise
   - **Key**: Show high-throughput systems expertise

2. **Simple but Scalable Design**
   - Clean architecture
   - Efficient operations
   - **Key**: Demonstrate simple but scalable design
