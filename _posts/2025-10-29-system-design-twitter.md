---
layout: post
title: "System Design: Twitter (Timeline, Fanout, Search, Trends)"
date: 2025-10-29 21:00:00 -0700
categories: system-design architecture social
permalink: /2025/10/29/system-design-twitter/
tags: [system-design, timeline, feed, fanout, search, trends, caching]
---

# System Design: Twitter (Timeline, Fanout, Search, Trends)

Goal: newsfeed of short posts with follows, likes/retweets, media, search, and trends, at massive read/write scale with low latency.

## Requirements

- Functional: post tweet (text/media), follow/unfollow, home timeline, user timeline, likes/retweets/replies, search, trends, notifications.
- Non‑functional: P95 read < 200 ms, write < 500 ms; HC read skew; hot‑key protection; multi‑region DR.

## High‑level architecture

```
Clients → API Gateway → (Auth, Rate‑Limit)
  ├─ Tweet Write Service → Tweets Store (Cassandra/S3) → Media Store (S3/CDN)
  ├─ Fanout Service (to caches/queues)
  ├─ Timeline Read Service → Redis/Timeline Cache → Tweets Store
  ├─ Graph Service (Follows) → Graph DB/Cache
  ├─ Engagements (Likes/RT) → Counters Store (Redis/CRDT + Cassandra)
  └─ Search Indexer → Kafka → Elastic/OpenSearch
```

## Data model

- Tweets: `tweet_id (KS), user_id, ts, text, media, counters` in wide‑column store; payload persisted to S3 for cold.
- Follows graph: adjacency lists in KV (sorted sets) + caching.
- Timelines: precomputed home timelines in Redis lists (fanout‑to‑cache), fallback to on‑read merge.

## Write path

1) Validate/auth, create tweet row (idempotency key), enqueue to Kafka.
2) Fanout: for users with small follower counts, push `tweet_id` into each follower’s home list (Redis). For super‑users, mark as pull‑on‑read.
3) Index into search; media to CDN.

## Read path (Home timeline)

1) Read `tweet_id`s from home list (Redis). On cache miss or pull‑user, merge K sorted lists (followees) from Timeline Store.
2) Hydrate tweets from Tweets Store; batch get; enrich counters from Redis; return.

## Hot key and super‑user strategy

- Hybrid fanout: push for normal, pull for super‑users; also use sharded queues and backpressure.
- Token buckets per user; coalesce duplicate writes; cache stampede protection with single‑flight.

## Counters (likes/retweets)

- Redis sharded counters with periodic flush to Cassandra; CRDT (G‑Counter) across regions.

## Search and trends

- Ingest to Kafka → consumers update inverted index (Elastic/OpenSearch) with fields (text, hashtags, user).
- Trends: streaming aggregations on hashtag counts per geo/window (Flink/Beam) with anomaly detection.

## Moderation and abuse

- ML classifiers for spam/toxicity; shadow bans; rate‑limits; IP/device reputation; human review queue.

## Multi‑region

- Active‑active reads; active‑passive writes for tweets; CRDT counters; asynchronous index replication.

## APIs

```http
POST /v1/tweets { text, media_ids[] }
GET  /v1/timeline/home?cursor=...
GET  /v1/timeline/{user}
POST /v1/tweets/{id}/like
```

## Testing/observability

- Canary releases; tail latency alarms; cardinality‑aware dashboards; chaos on fanout queues.

## Capacity & back‑of‑the‑envelope

- Assumptions: 200M MAU, 20M DAU, 2M peak QPS reads, 50k peak TPS writes.
- Average tweet 280 bytes + metadata → ~0.5–1 KB/tweet in KV (excl. media). Daily 50M tweets → ~50 GB/day (hot store), archive to S3.
- Home timeline: 100 tweets/page; Redis list node ~60 bytes → per user cache ~6 KB for head; for 20M DAU cached head ~120 GB across shards.
- Fanout workers: if avg fanout 200 followers/tweet, 50k TPS → 10M inserts/s naive; hybrid push/pull to keep inserts <2M/s, remainder pulled on read.

## SLOs & error budgets

- Home timeline P95 < 200 ms; Tweet publish ACK P95 < 500 ms; Availability 99.9%.
- Budget resets per 30 days; protect with circuit breakers on fanout and single‑flight cache.

## Consistency & trade‑offs

- Eventual consistency for timelines and counters; strong consistency on tweet write path (idempotency key, single writer per tweet id).
- Read repairs during hydration; monotonic timeline per user using per‑followee cursors.

## Bottlenecks & mitigations

- Super‑user hot keys: switch to pull, sample followers for push; cache pinning + request coalescing.
- Search indexing lag: prioritize fresh content pipeline; separate cold backfills.

## Evolution plan

- Phase 1: push‑only for small scale; Phase 2: hybrid fanout with on‑read merge; Phase 3: multi‑region with CRDT counters and geo‑proximal reads.

## Detailed APIs (sample)

```http
POST /v1/tweets { text, media_ids[], reply_to?, audience? } -> { id }
GET  /v1/timeline/home?cursor=... -> { items:[{tweet_id, user, text, media, counters}], next_cursor }
POST /v1/tweets/{id}/like -> 204
```

## Data model (DDL sketch)

```sql
CREATE TABLE tweets (
  tweet_id bigint PRIMARY KEY,
  user_id bigint NOT NULL,
  ts timestamp NOT NULL,
  text text,
  media jsonb,
  visibility smallint,
  attrs jsonb
);
CREATE TABLE timeline_items (
  user_id bigint,
  tweet_id bigint,
  ts timestamp,
  PRIMARY KEY (user_id, tweet_id)
);
```

## Capacity math (BoE)

- Home timeline read 2M QPS p95 200 ms → Redis cluster of N shards each ~150k QPS; cache size ~120 GB for heads.
- Storage: 50M tweets/day @1 KB → 50 GB/day; 2‑year hot tier ~36 TB (before compression).

## Consistency matrix

- Tweet create: strong (single writer, idempotency key)
- Timeline insert: eventual; reconcile on read with per‑followee cursors
- Counters: eventual with periodic flush to base store

## Failure drill runbook

- Fanout backlog > threshold → switch heavy authors to pull, throttle enrichment, shed "who to follow".
- Redis shard hot → enable request coalescing, migrate keys, temporarily reduce page size.

## Testing plan

- Load tests with mixed read/write and super‑user spikes; chaos on fanout queue; cache stampede simulations.
