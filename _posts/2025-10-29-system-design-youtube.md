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
