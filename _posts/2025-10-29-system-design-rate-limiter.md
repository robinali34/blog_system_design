---
layout: post
title: "System Design: Distributed Rate Limiter"
date: 2025-10-29 23:08:00 -0700
categories: system-design architecture reliability
permalink: /2025/10/29/system-design-rate-limiter/
tags: [system-design, redis, token-bucket, leaky-bucket, lua, consistency]
---

# System Design: Distributed Rate Limiter

<div class="post-reading-tip" markdown="1">

**How to read this post:** Skim the **architecture diagram** under High-Level Design first, then walk through requirements → API → deep dives. Diagrams render as interactive visuals in the browser.

</div>

## Requirements
- Enforce per-user and per-IP limits (e.g., 100 req/min), burst handling, low latency, global distribution.

## Approaches
- Token bucket in Redis with Lua scripts (atomic); or sliding window counters.

## Architecture
### Architecture at a glance

<figure class="diagram-figure">
  <img src="{{ '/assets/diagrams/c58096000293a5d5.png' | relative_url }}" alt="System architecture diagram" class="diagram-img" loading="lazy" />
</figure>


<p class="diagram-caption">High-level system diagram — read top to bottom or left to right.</p>



### Key flows

<figure class="diagram-figure">
  <img src="{{ '/assets/diagrams/58009e50002fbbe3.png' | relative_url }}" alt="Request flow sequence diagram" class="diagram-img" loading="lazy" />
</figure>


<p class="diagram-caption">Typical request/data flow — use in interviews to explain the happy path.</p>
### Design patterns

<figure class="diagram-figure">
  <img src="{{ '/assets/diagrams/0a3203c37cabde1c.png' | relative_url }}" alt="System architecture diagram" class="diagram-img" loading="lazy" />
</figure>


<p class="diagram-caption">Typical request/data flow — use in interviews to explain the happy path.</p>
Clients → Gateway → Limiter SDK → Redis/Memcache cluster (sharded) → Fallback local estimators.

## Data model
`key = tenant:user:minute` → counters; or `key = tenant:user` → (tokens, last_ts).

## Consistency
- Prefer strong atomic ops (Lua) per key; eventual across regions with locality; shadow write to secondary.

## SLOs
- Check P95 < 5 ms; availability 99.99% (graceful degrade to stricter local limits on Redis outage).

## Capacity
- 1M rps checks: shard across 10 Redis primaries (100k rps each); pipeline ops.

## Failure modes
- Hot keys → add jitter to keys (bucketize), hierarchical keys.
- Region outage → fail open/closed per product policy.

## Lua pseudo (token bucket)

```lua
-- KEYS[1]=key, ARGV[1]=now_ms, ARGV[2]=rate_per_s, ARGV[3]=burst
local now=tonumber(ARGV[1])
local rate=tonumber(ARGV[2])
local burst=tonumber(ARGV[3])
local tokens=tonumber(redis.call('HGET', KEYS[1], 't') or burst)
local ts=tonumber(redis.call('HGET', KEYS[1], 'ts') or now)
tokens=math.min(burst, tokens + (now-ts)*rate/1000)
local allowed=tokens>=1 and 1 or 0
if allowed==1 then tokens=tokens-1 end
redis.call('HMSET', KEYS[1], 't', tokens, 'ts', now)
redis.call('PEXPIRE', KEYS[1], 60000)
return allowed
```

## Failover policy

- Redis down: enforce stricter local in‑process leaky bucket; log to audit; restore to central when healthy.
