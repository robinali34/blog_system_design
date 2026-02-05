---
layout: post
title: "Design a URL Shortener (Bit.ly)"
date: 2026-02-05
categories: [System Design, Interview Example, Distributed Systems, Scaling]
excerpt: "A comprehensive guide to designing a URL shortener like Bit.ly, covering functional and non-functional requirements, short code generation, caching strategies, and scaling to billions of URLs and millions of daily users."
---

## Introduction

A URL shortener is a service that converts long URLs into short, manageable links. Users submit a long URL and receive a shortened version (e.g., `short.ly/abc123`) that redirects to the original URL when clicked. Designing a URL shortener is a common beginner-friendly system design interview question that tests your understanding of high read-to-write ratios, caching, and scalable data storage.

This post walks through the problem from requirements and API design through high-level architecture and deep dives on short code generation, fast redirects, and scaling to 1B shortened URLs and 100M daily active users.

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Requirements](#requirements)
   - [Functional Requirements](#functional-requirements)
   - [Non-Functional Requirements](#non-functional-requirements)
3. [Core Entities](#core-entities)
4. [API](#api)
5. [High-Level Design](#high-level-design)
6. [Deep Dives](#deep-dives)
   - [Short Code Uniqueness](#short-code-uniqueness)
   - [Fast Redirects](#fast-redirects)
   - [Scaling to 1B URLs and 100M DAU](#scaling-to-1b-urls-and-100m-dau)
7. [Summary](#summary)
8. [References](#references)

## Problem Statement

**Design a URL shortener that:**

1. Accepts a long URL and returns a shortened URL
2. Redirects users to the original URL when they access the short URL
3. Optionally supports custom aliases and expiration dates
4. Scales to 1B shortened URLs and 100M daily active users
5. Keeps redirect latency low (< 100 ms) and ensures high availability (99.99%)

**Out of Scope (for this design):**

- User authentication and account management
- Analytics (click counts, geographic data)
- Spam detection and malicious URL filtering

## Requirements

### Functional Requirements

**Core Requirements:**

1. **Shorten URL**: Users submit a long URL and receive a shortened version.
   - Optionally: custom alias (e.g., `short.ly/my-custom-alias`)
   - Optionally: expiration date for the shortened URL
2. **Redirect**: Users access the short URL and are redirected to the original long URL.

### Non-Functional Requirements

**Core Requirements:**

1. **Uniqueness**: Each short code maps to exactly one long URL.
2. **Low latency**: Redirection should complete with minimal delay (< 100 ms).
3. **Availability**: System should be reliable and available 99.99% of the time (availability preferred over strong consistency for reads).
4. **Scale**: Support 1B shortened URLs and 100M DAU.

**Important observation:** The read-to-write ratio is heavily skewed toward reads. Users click short links far more often than they create new ones (e.g., 1000 reads per 1 write). This asymmetry drives caching strategy, database choice, and overall architecture.

## Core Entities

1. **Original URL** – The long URL the user wants to shorten.
2. **Short URL** – The shortened URL (e.g., `short.ly/abc123`) that redirects to the original.
3. **User** – The creator of the shortened URL (optional for basic design).

## API

### Shorten a URL

```http
POST /urls
Content-Type: application/json

{
  "long_url": "https://www.example.com/some/very/long/url",
  "custom_alias": "optional_custom_alias",
  "expiration_date": "optional_expiration_date"
}

Response 200:
{
  "short_url": "https://short.ly/abc123"
}
```

- **POST** because we are creating a new resource (mapping).
- Server validates the long URL, generates or accepts a short code, stores the mapping, and returns the short URL.

### Redirect to Original URL

```http
GET /{short_code}
```

- **Response:** `302 Found` (temporary redirect) with `Location: <original_long_url>`.
- **Why 302 instead of 301:** 302 ensures the browser does not cache the redirect, so we can update or expire links later and still track clicks through our servers.

## High-Level Design

### 1) Create Short URL

1. **Client** sends `POST /urls` with long URL, optional alias, optional expiration.
2. **Server** validates the long URL (format, optionally deduplication).
3. **Short code generation**: Use a custom alias if provided (and unique), otherwise generate a unique short code (e.g., Base62 from a counter or hash with collision handling).
4. **Database**: Store mapping `(short_code, long_url, expiration_date, ...)`.
5. Return the short URL to the client.

### 2) Redirect (Resolve)

1. User’s browser sends `GET /{short_code}` to our domain (e.g., `short.ly`).
2. **Server** looks up `short_code` in cache or database.
3. If found and not expired, respond with `302` and `Location: <long_url>`.
4. Browser follows redirect to the original URL.

### High-Level Diagram

```
[Client] --> POST /urls --> [API Server] --> [DB]
                |                    |
                v                    v
           short_url            (short_code, long_url, ...)

[Client] --> GET /{short_code} --> [API Server] --> [Cache] --> [DB]
                                        |
                                        v
                              302 Location: long_url
```

## Deep Dives

### Short Code Uniqueness

**Constraints:** Short codes must be unique, as short as possible, and cheap to generate.

**Options:**

| Approach | Pros | Cons |
|----------|------|------|
| **Long URL prefix** | Simple | Not short, poor UX |
| **Hash (e.g., MD5/SHA) + truncate** | Deterministic, no central counter | Collision handling (retry or append), need collision check in DB |
| **Unique counter + Base62 encoding** | Short, no collisions, efficient | Need a single source of truth for the counter (e.g., Redis INCR or DB sequence) |

**Recommended:**  
- **Custom alias:** Use as short code after uniqueness check.  
- **Default:** Global counter in Redis (or DB) + Base62 encoding. Optionally use **counter batching**: each service instance reserves a range (e.g., 1000 IDs) to reduce round-trips to the counter store.

### Fast Redirects

Redirects must be fast (< 100 ms). Reads dominate, so optimize for read path.

1. **Database index:** Index on `short_code` (primary key) so lookups are O(1).
2. **In-memory cache (e.g., Redis):** Cache `short_code -> long_url` with TTL. Cache-aside: on miss, read from DB, then fill cache. Use negative caching for 404s (short code not found) to avoid repeated DB hits for invalid codes.
3. **CDN / edge:** Put redirect logic at the edge so most requests never hit the origin. Short codes can be cached at edge with TTL; 302 responses can be served from edge.

**Pattern:** [Scaling reads](https://www.hellointerview.com/learn/system-design/common-patterns/scaling-reads) – aggressive caching and read replicas to handle high read throughput.

### Scaling to 1B URLs and 100M DAU

**Storage:**  
- ~500 bytes per row (short_code, long_url, created_at, expires_at, metadata).  
- 1B × 500 bytes ≈ 500 GB – within a single DB or sharded across nodes.

**Database:**  
- Write volume is low (e.g., 100k new URLs/day ≈ 1–2 writes/sec). Any reasonable DB (PostgreSQL, MySQL, DynamoDB) can handle this.  
- Use **replication** for read replicas and **backups** for durability.  
- For **high availability**, use managed DB with failover and multiple replicas.

**Services:**  
- **Read path:** Redirect service – scale horizontally behind a load balancer; use cache + DB.  
- **Write path:** Shorten service – scale horizontally; short code uniqueness via centralized counter (Redis or DB sequence).  
- **Counter:** Single Redis instance (or Redis Cluster) with atomic `INCR`. Use counter batching so each app instance reserves a block of IDs to reduce Redis round-trips.

**Final architecture (conceptual):**

```
[Client] --> [LB] --> [Redirect Service x N] --> [Redis Cache] --> [DB Read Replicas]
                |
                v
           [Shorten Service x N] --> [Redis Counter] + [DB Primary]
```

## Summary

| Topic | Recommendation |
|-------|----------------|
| **Short code** | Custom alias with uniqueness check; else counter + Base62 (with optional batching). |
| **Redirect** | 302, index on `short_code`, Redis cache, optional CDN/edge. |
| **Scale** | Cache-heavy read path; separate read/write services; single counter store; DB replication and backups. |
| **SLOs** | Redirect &lt; 100 ms, 99.99% availability, 1B URLs, 100M DAU. |

A URL shortener is a classic **read-heavy** system: invest in caching and read scaling, keep writes simple, and ensure short codes are unique and short.

## References

- [ByteByteGo – Design a URL Shortener](https://bytebytego.com/courses/system-design-interview/design-a-url-shortener)
- [ByteByteGo – Scale from Zero to Millions of Users](https://bytebytego.com/courses/system-design-interview/scale-from-zero-to-millions-of-users)
- [YouTube – System Design Interview: URL Shortener](https://www.youtube.com/watch?v=HHUi8F_qAXM)
- [Hello Interview – Design a URL Shortener Like Bit.ly](https://www.hellointerview.com/learn/system-design/problem-breakdowns/bitly)
