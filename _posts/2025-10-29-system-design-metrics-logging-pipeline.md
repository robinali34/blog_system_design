---
layout: post
title: "System Design: Metrics & Logging Pipeline"
date: 2025-10-29 23:18:00 -0700
categories: system-design architecture observability
permalink: /2025/10/29/system-design-metrics-logging-pipeline/
tags: [system-design, metrics, logging, kafka, prom, elastic]
---

# System Design: Metrics & Logging Pipeline

## Requirements
- Ingest 10M events/sec logs, 10M samples/sec metrics; retention, indexing, alerting.

## Architecture
Agents → Kafka (multi-tenant topics) → Stream processors (PII redaction, sampling) →
  Logs: Elastic/ClickHouse + S3 cold
  Metrics: Prometheus remote write → TSDB (Cortex/Mimir) + downsampling

## SLOs
- 99% of logs searchable < 1 min; metrics scrape latency < 10 s.

## Multi-region
- Local ingest + cross-region replication; query federation; cost-aware retention.

## Failure modes
- Backpressure to agents (buffer + sampling); hot shards → rebalancing; index throttling.
