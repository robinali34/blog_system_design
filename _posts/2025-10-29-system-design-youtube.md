---
layout: post
title: "System Design: YouTube (Upload, Transcode, CDN, Recommendations)"
date: 2025-10-29 21:10:00 -0700
categories: system-design architecture media
permalink: /2025/10/29/system-design-youtube/
tags: [system-design, video, cdn, transcoding, recommendation, search]
---

# System Design: YouTube (Upload, Transcode, CDN, Recommendations)

Requirements: upload videos, process into multiple bitrates/codecs, global CDN delivery, metadata/search, live streams, comments/likes, recommendations.

## High‑level flow

```
Upload → Ingest → Virus Scan → Transcode Farm → Packaging (HLS/DASH) → Origin → CDN
                                ↘ Thumbnails  ↘ Audio tracks / captions
Metadata API → Postgres/Spanner; Search → Kafka → Indexer (Elastic)
Watch Service → Player API → CDN edge
```

## Storage

- Object storage for masters and segments (S3/GCS) with lifecycle (IA/Glacier).
- Metadata DB for videos, channels, playlists; counters in Redis (views/likes).

## Transcoding

- Async jobs (Kafka/SQS) to a fleet with GPU/CPU pools; ladder: 144p..4K, VP9/H.265/AV1; audio AAC/Opus.
- Packaging: HLS (TS/fMP4) and DASH with segment durations ~2–6s; CMAF for reuse.

## CDN delivery

- Multi‑CDN with origin shield; signed URLs; range requests; QUIC/HTTP3; prefetch next segments.

## Recommendations

- Candidate generation: collaborative filtering (co‑view), content‑based (tags/topic), trending.
- Ranking: deep models with watch time, CTR, satisfaction signals; online features in Redis/Feast; A/B testing.

## Live

- RTMP ingest → transcoding pipeline with low‑latency HLS/DASH; chat via websockets; DVR window.

## Moderation

- Content ID/fingerprint; ML for NSFW; geo‑blocking; age gates; strikes policy.

## APIs

```http
POST /v1/videos { title, file_id }
GET  /v1/videos/{id}
GET  /v1/watch/{id}/manifest.m3u8
GET  /v1/search?q=...
```

## Observability

- QoE KPIs: startup time, rebuffer ratio, bitrate switches; edge POP dashboards; error budgets per region.

## Capacity & sizing

- Assumptions: 10M DAU, 1M uploads/day avg 200 MB → 200 TB/day raw; store masters in S3 IA after 30 days; segments hot on CDN.
- Transcode fleet: 1 hour content ~ 2–4x real‑time CPU/GPU; with parallelism target 1x wall‑clock; size workers accordingly with queue depth alarms.
- CDN egress: P95 5 Mbps per active viewer; 1M concurrent → ~5 Tbps; multi‑CDN and regional load‑shedding.

## SLOs

- Upload ACK < 1 s; processing ETA within 5 min for 95% of short videos; TTFF < 2 s; rebuffer ratio < 0.5%.

## Failure scenarios

- Transcoder zone loss → drain queues to healthy zones, degrade ladder (drop 4K) temporarily.
- CDN provider outage → failover to alternate CDN via DNS; protect origin with shield.

## Data consistency

- Metadata strongly consistent; edge caches eventual; search index eventually consistent with tombstone handling.

## Detailed APIs

```http
POST /v1/videos { title, file_id, privacy } -> { id }
GET  /v1/videos/{id}
GET  /v1/watch/{id}/manifest.m3u8
POST /v1/live/start { stream_key }
```

## Storage layout

- Masters: `s3://videos/master/{id}`; Segments: `s3://videos/segments/{id}/{bitrate}/{seq}.m4s`;
- Manifests cached at CDN; signed cookies for private content.

## Capacity table (BoE)

| Component | Rate | Notes |
|---|---:|---|
| Upload ingest | 2 Gbps/region | spikes on events |
| Transcode jobs | 1M/day | GPU pool autoscaled |
| CDN egress | 5 Tbps peak | multi‑CDN |

## Failure drills

- Region transcoder loss → drain queues to others; degrade ladder; user messaging for quality.
- CDN cache miss surge → pre‑warm top manifests; tighten CDN TTL for manifests only.

## What Interviewers Look For

### Video Streaming Skills

1. **Video Processing Pipeline**
   - Transcoding ladder
   - Multiple codecs/formats
   - Async processing
   - **Red Flags**: Single format, synchronous processing, slow

2. **CDN Delivery**
   - Multi-CDN strategy
   - Origin shield
   - Signed URLs
   - **Red Flags**: Single CDN, no origin shield, insecure

3. **Adaptive Streaming**
   - HLS/DASH packaging
   - Bitrate switching
   - Quality optimization
   - **Red Flags**: No adaptive streaming, poor quality, buffering

### Distributed Systems Skills

1. **Storage Design**
   - Object storage for masters
   - Lifecycle policies
   - Cost optimization
   - **Red Flags**: No lifecycle, high costs, inefficient storage

2. **Recommendation System**
   - Candidate generation
   - Ranking models
   - A/B testing
   - **Red Flags**: No recommendations, poor ranking, no testing

3. **Live Streaming**
   - Low-latency pipeline
   - RTMP ingest
   - DVR support
   - **Red Flags**: High latency, no live support, poor UX

### Problem-Solving Approach

1. **Cost Optimization**
   - Storage tiers
   - Transcoding efficiency
   - CDN costs
   - **Red Flags**: No optimization, high costs, inefficient

2. **Edge Cases**
   - Transcoder failures
   - CDN outages
   - Quality degradation
   - **Red Flags**: Ignoring edge cases, no handling

3. **Trade-off Analysis**
   - Quality vs cost
   - Latency vs quality
   - **Red Flags**: No trade-offs, dogmatic choices

### System Design Skills

1. **Component Design**
   - Upload service
   - Transcoding service
   - CDN service
   - **Red Flags**: Monolithic, unclear boundaries

2. **Moderation System**
   - Content ID
   - ML classifiers
   - Geo-blocking
   - **Red Flags**: No moderation, security issues, compliance problems

3. **Search & Metadata**
   - Search indexing
   - Metadata management
   - **Red Flags**: Slow search, poor metadata, no indexing

### Communication Skills

1. **Video Pipeline Explanation**
   - Can explain transcoding
   - Understands CDN delivery
   - **Red Flags**: No understanding, vague explanations

2. **Scale Explanation**
   - Can explain scaling strategies
   - Understands bottlenecks
   - **Red Flags**: No understanding, vague

### Meta-Specific Focus

1. **Media Systems Expertise**
   - Video processing knowledge
   - CDN expertise
   - **Key**: Show media systems expertise

2. **Cost & Quality Balance**
   - Cost optimization
   - Quality maintenance
   - **Key**: Demonstrate cost/quality balance
