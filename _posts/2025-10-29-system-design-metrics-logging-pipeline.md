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

## What Interviewers Look For

### Observability Systems Skills

1. **High-Throughput Ingestion**
   - 10M events/sec logs
   - 10M samples/sec metrics
   - Kafka for buffering
   - **Red Flags**: Low throughput, bottlenecks, poor ingestion

2. **Stream Processing**
   - PII redaction
   - Sampling strategies
   - Multi-tenant support
   - **Red Flags**: No processing, no sampling, security issues

3. **Storage & Retention**
   - Hot storage (Elasticsearch/ClickHouse)
   - Cold storage (S3)
   - Retention policies
   - **Red Flags**: No retention, high costs, poor storage

### Distributed Systems Skills

1. **Multi-Region Design**
   - Local ingest
   - Cross-region replication
   - Query federation
   - **Red Flags**: Single region, no replication, poor queries

2. **Scalability Design**
   - Horizontal scaling
   - Sharding strategy
   - Load balancing
   - **Red Flags**: Vertical scaling, no sharding, bottlenecks

3. **Cost Optimization**
   - Downsampling
   - Retention policies
   - Storage tiers
   - **Red Flags**: No optimization, high costs, inefficient

### Problem-Solving Approach

1. **Failure Handling**
   - Backpressure management
   - Hot shard rebalancing
   - Index throttling
   - **Red Flags**: Ignoring failures, no handling, poor recovery

2. **Edge Cases**
   - Traffic spikes
   - Storage capacity
   - Query performance
   - **Red Flags**: Ignoring edge cases, no handling

3. **Trade-off Analysis**
   - Cost vs retention
   - Latency vs accuracy
   - **Red Flags**: No trade-offs, dogmatic choices

### System Design Skills

1. **Component Design**
   - Ingestion service
   - Stream processors
   - Storage services
   - **Red Flags**: Monolithic, unclear boundaries

2. **Data Pipeline**
   - Kafka → Processors → Storage
   - Clear data flow
   - **Red Flags**: No pipeline, unclear flow

3. **Query Design**
   - Search optimization
   - Indexing strategy
   - **Red Flags**: Slow queries, missing indexes, poor performance

### Communication Skills

1. **Pipeline Explanation**
   - Can explain ingestion flow
   - Understands processing
   - **Red Flags**: No understanding, vague explanations

2. **Storage Explanation**
   - Can explain hot/cold storage
   - Understands retention
   - **Red Flags**: No understanding, vague

### Meta-Specific Focus

1. **Observability Expertise**
   - Metrics/logging knowledge
   - High-throughput design
   - **Key**: Show observability expertise

2. **Cost & Scale Balance**
   - Cost optimization
   - High throughput
   - **Key**: Demonstrate cost/scale balance
