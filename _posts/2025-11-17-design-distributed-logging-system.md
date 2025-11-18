---
layout: post
title: "Design a Distributed Logging System with PII Masking and Fast Queries - System Design Interview"
date: 2025-11-17
categories: [System Design, Interview Example, Distributed Systems, Logging, Data Privacy, Observability, Search Systems, Stream Processing]
excerpt: "A comprehensive guide to designing a distributed logging system that masks PII (Personally Identifiable Information), supports top-k exception queries, and enables fast multi-field queries, covering log ingestion, storage, indexing, PII detection and masking, exception tracking, and query optimization."
---

## Introduction

A distributed logging system is a critical component of modern software infrastructure, enabling organizations to collect, store, and analyze logs from thousands of services and applications. This system must handle massive volumes of log data while ensuring data privacy through PII masking, provide real-time exception tracking with top-k queries, and support fast multi-field searches for debugging and analysis.

This post provides a detailed walkthrough of designing a distributed logging system with PII masking, top-k exception tracking, and fast query capabilities. This is a system design interview question that tests your understanding of distributed systems, data privacy, search systems, streaming data processing, and large-scale data storage.

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Requirements](#requirements)
   - [Functional Requirements](#functional-requirements)
   - [Non-Functional Requirements](#non-functional-requirements)
3. [Capacity Estimation](#capacity-estimation)
   - [Traffic Estimates](#traffic-estimates)
   - [Storage Estimates](#storage-estimates)
   - [Bandwidth Estimates](#bandwidth-estimates)
4. [Core Entities](#core-entities)
5. [API](#api)
6. [Data Flow](#data-flow)
7. [Database Design](#database-design)
   - [Schema Design](#schema-design)
   - [Database Sharding Strategy](#database-sharding-strategy)
8. [High-Level Design](#high-level-design)
9. [Deep Dive](#deep-dive)
   - [Component Design](#component-design)
   - [Detailed Design](#detailed-design)
   - [Scalability Considerations](#scability-considerations)
   - [Security Considerations](#security-considerations)
   - [Monitoring & Observability](#monitoring--observability)
   - [Trade-offs and Optimizations](#trade-offs-and-optimizations)
10. [Summary](#summary)

## Problem Statement

**Design a distributed logging system with the following features:**

1. **Log Ingestion**: Collect logs from thousands of services and applications
2. **PII Masking**: Automatically detect and mask Personally Identifiable Information (PII) in logs
3. **Top-K Exceptions**: Track and query the top K most frequent exceptions
4. **Fast Multi-Field Queries**: Support fast queries by various fields (timestamp, service, level, error type, user ID, etc.)
5. **Real-Time Processing**: Process and index logs in near real-time
6. **Retention Management**: Support configurable retention policies
7. **Search and Analytics**: Enable full-text search and aggregations
8. **Alerting**: Trigger alerts based on exception patterns or thresholds

**Scale Requirements:**
- 10 billion+ log entries per day
- 100K+ log entries per second peak ingestion rate
- 1000+ services/applications sending logs
- Support queries returning results in < 1 second
- Store logs for 30-90 days (configurable)
- Support concurrent queries from 1000+ users
- Global deployment across multiple regions

## Requirements

### Functional Requirements

**Core Features:**
1. **Log Ingestion**: Accept logs from various sources (applications, services, containers)
2. **PII Detection**: Automatically detect PII patterns (SSN, email, phone, credit card, IP addresses)
3. **PII Masking**: Mask or redact PII data before storage
4. **Log Parsing**: Parse structured and unstructured logs
5. **Field Extraction**: Extract common fields (timestamp, level, service, message, etc.)
6. **Exception Tracking**: Identify and track exceptions/errors
7. **Top-K Exceptions**: Query top K exceptions by frequency, time window, service, etc.
8. **Multi-Field Queries**: Query by timestamp range, service, log level, error type, user ID, etc.
9. **Full-Text Search**: Search within log messages
10. **Aggregations**: Support count, sum, average, percentile aggregations
11. **Retention Policies**: Automatically delete logs older than retention period
12. **Log Streaming**: Stream logs in real-time to consumers
13. **Dashboards**: Visualize logs and metrics
14. **Alerting**: Configure alerts based on exception rates or patterns

**Out of Scope:**
- Log transformation/ETL pipelines (focus on storage and query)
- User authentication/authorization (assume existing)
- Payment processing (assume existing)
- Log forwarding to external systems (focus on core system)

### Non-Functional Requirements

1. **Availability**: 99.9% uptime
2. **Reliability**: No log loss, at-least-once delivery semantics
3. **Performance**: 
   - Ingestion latency: < 100ms
   - Query latency: < 1 second for most queries
   - Top-K query latency: < 500ms
   - PII masking overhead: < 10% of ingestion time
4. **Scalability**: Handle 10B+ logs/day, 100K+ logs/second
5. **Durability**: 99.999% durability (logs written to multiple replicas)
6. **Privacy**: PII must be masked before storage, no PII in search indices
7. **Consistency**: Eventual consistency acceptable for queries
8. **Security**: Encryption at rest and in transit, access control

## Capacity Estimation

### Traffic Estimates

**Assumptions:**
- 10 billion log entries per day
- Peak traffic: 3x average = 30 billion/day = 347K/second
- Average log size: 1KB (including metadata)
- Peak log size: 2KB (with stack traces)

**Read Traffic:**
- 1000 concurrent users
- Average 10 queries per user per hour
- Peak queries: 100 queries per second
- Average query result size: 100KB
- Peak read bandwidth: 100 queries/sec × 100KB = 10MB/sec

**Write Traffic:**
- Peak ingestion: 347K logs/second
- Peak write bandwidth: 347K/sec × 2KB = 694MB/sec ≈ 700MB/sec

### Storage Estimates

**Daily Storage:**
- 10 billion logs × 1KB = 10TB/day
- With replication (3x): 30TB/day
- With compression (3x): 10TB/day after compression

**Retention:**
- 30 days retention: 10TB × 30 = 300TB
- 90 days retention: 10TB × 90 = 900TB
- With replication: 900TB × 3 = 2.7PB

**Index Storage:**
- Index overhead: ~30% of data size
- 30 days: 300TB × 0.3 = 90TB
- Total storage (30 days): 300TB + 90TB = 390TB

### Bandwidth Estimates

- **Ingestion**: 700MB/sec peak
- **Query**: 10MB/sec peak
- **Replication**: 700MB/sec × 2 = 1.4GB/sec
- **Total**: ~2GB/sec peak bandwidth

## Core Entities

1. **LogEntry**
   - log_id (UUID)
   - timestamp (datetime)
   - service_name (string)
   - log_level (enum: DEBUG, INFO, WARN, ERROR, FATAL)
   - message (text, PII-masked)
   - raw_message (text, encrypted, access-controlled)
   - fields (JSON map: user_id, request_id, trace_id, etc.)
   - exception_type (string, nullable)
   - stack_trace (text, nullable)
   - host (string)
   - environment (string: prod, staging, dev)
   - region (string)
   - created_at (datetime)

2. **ExceptionSummary**
   - exception_id (string, hash of exception_type + service)
   - exception_type (string)
   - service_name (string)
   - count (long)
   - first_seen (datetime)
   - last_seen (datetime)
   - sample_log_ids (array of UUIDs)
   - metadata (JSON: affected_users, regions, etc.)

3. **PIIPattern**
   - pattern_id (UUID)
   - pattern_type (enum: SSN, EMAIL, PHONE, CREDIT_CARD, IP_ADDRESS)
   - regex_pattern (string)
   - masking_strategy (enum: REDACT, HASH, PARTIAL_MASK)

4. **Query**
   - query_id (UUID)
   - user_id (string)
   - query_string (string)
   - filters (JSON: timestamp_range, services, levels, etc.)
   - created_at (datetime)
   - execution_time_ms (int)

## API

### Log Ingestion API

```python
POST /api/v1/logs
Headers:
  Authorization: Bearer <token>
  Content-Type: application/json
  X-Service-Name: <service_name>
  X-Environment: <environment>

Body:
{
  "timestamp": "2025-11-17T10:30:00Z",
  "level": "ERROR",
  "message": "Failed to process payment for user john.doe@example.com",
  "fields": {
    "user_id": "user_123",
    "request_id": "req_456",
    "trace_id": "trace_789"
  },
  "exception": {
    "type": "PaymentProcessingException",
    "message": "Insufficient funds",
    "stack_trace": "..."
  },
  "metadata": {
    "host": "api-server-01",
    "region": "us-east-1"
  }
}

Response:
{
  "log_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "accepted",
  "pii_detected": ["email"],
  "pii_masked": true
}
```

### Query API

```python
POST /api/v1/logs/query
Headers:
  Authorization: Bearer <token>
  Content-Type: application/json

Body:
{
  "query": "payment failed",
  "filters": {
    "timestamp_range": {
      "start": "2025-11-17T00:00:00Z",
      "end": "2025-11-17T23:59:59Z"
    },
    "services": ["payment-service", "order-service"],
    "levels": ["ERROR", "FATAL"],
    "fields": {
      "user_id": "user_123"
    }
  },
  "sort": {
    "field": "timestamp",
    "order": "desc"
  },
  "limit": 100,
  "offset": 0
}

Response:
{
  "query_id": "query_123",
  "total": 1523,
  "logs": [
    {
      "log_id": "...",
      "timestamp": "2025-11-17T10:30:00Z",
      "service_name": "payment-service",
      "level": "ERROR",
      "message": "Failed to process payment for user ***@***.***",
      "fields": {...}
    }
  ],
  "execution_time_ms": 234
}
```

### Top-K Exceptions API

```python
GET /api/v1/exceptions/top-k?k=10&window=1h&service=payment-service
Headers:
  Authorization: Bearer <token>

Response:
{
  "window": "1h",
  "service": "payment-service",
  "exceptions": [
    {
      "exception_type": "PaymentProcessingException",
      "count": 1523,
      "first_seen": "2025-11-17T09:00:00Z",
      "last_seen": "2025-11-17T10:30:00Z",
      "sample_log_ids": ["...", "..."]
    },
    {
      "exception_type": "DatabaseConnectionException",
      "count": 892,
      ...
    }
  ],
  "execution_time_ms": 45
}
```

### Exception Details API

```python
GET /api/v1/exceptions/{exception_id}?window=24h
Headers:
  Authorization: Bearer <token>

Response:
{
  "exception_id": "exc_123",
  "exception_type": "PaymentProcessingException",
  "service_name": "payment-service",
  "count": 1523,
  "trend": [
    {"timestamp": "2025-11-17T09:00:00Z", "count": 100},
    {"timestamp": "2025-11-17T10:00:00Z", "count": 500},
    {"timestamp": "2025-11-17T11:00:00Z", "count": 923}
  ],
  "sample_logs": [...]
}
```

## Data Flow

### Log Ingestion Flow

1. **Client Application** → Sends log to **Load Balancer**
2. **Load Balancer** → Routes to **Log Ingestion Service** (multiple instances)
3. **Log Ingestion Service**:
   - Validates log format
   - Detects PII using **PII Detection Service**
   - Masks PII using **PII Masking Service**
   - Extracts fields and exception information
   - Publishes to **Message Queue** (Kafka)
4. **Log Processing Workers** (consumers):
   - Consume logs from Kafka
   - Parse and normalize logs
   - Index logs in **Search Index** (Elasticsearch)
   - Update **Exception Tracking System**
   - Store logs in **Object Storage** (S3) and **Time-Series Database** (Cassandra)
5. **Exception Tracking System** (Apache Flink):
   - Consumes exception logs from Kafka
   - Performs windowed aggregations for exception counts
   - Calculates top-K exceptions in real-time
   - Updates Redis cache and PostgreSQL summaries

### Query Flow

1. **User** → Sends query to **API Gateway**
2. **API Gateway** → Routes to **Query Service**
3. **Query Service**:
   - Parses query and filters
   - Determines query strategy (time-range, fields, etc.)
   - Queries **Search Index** (Elasticsearch) for fast field-based queries
   - Queries **Time-Series Database** (Cassandra) for time-range queries
   - Aggregates results
   - Returns paginated results
4. **Top-K Exception Query**:
   - Queries **Exception Tracking System** (Redis cache, backed by Flink state store)
   - Returns top-K exceptions for time window
   - Flink continuously updates Redis with latest top-K results

### PII Masking Flow

1. **PII Detection Service**:
   - Applies regex patterns for common PII (SSN, email, phone, etc.)
   - Uses ML models for context-aware detection
   - Returns detected PII locations and types
2. **PII Masking Service**:
   - Applies masking strategy based on PII type:
     - **REDACT**: Replace with `***`
     - **HASH**: Replace with hash (for debugging)
     - **PARTIAL_MASK**: Show partial (e.g., `j***@example.com`)
   - Creates masked version of log message
   - Stores original (encrypted) separately if needed for compliance

## Database Design

### Schema Design

#### Logs Table (Cassandra - Time-Series)

```sql
CREATE TABLE logs_by_timestamp (
  date_hour TIMESTAMP,  -- Partition key: 2025-11-17 10:00:00
  log_id UUID,          -- Clustering key
  timestamp TIMESTAMP,
  service_name TEXT,
  log_level TEXT,
  message TEXT,         -- PII-masked
  fields MAP<TEXT, TEXT>,
  exception_type TEXT,
  stack_trace TEXT,
  host TEXT,
  environment TEXT,
  region TEXT,
  PRIMARY KEY (date_hour, log_id)
) WITH CLUSTERING ORDER BY (log_id DESC);

-- Secondary index for service queries
CREATE INDEX idx_service ON logs_by_timestamp(service_name);

-- Secondary index for log level
CREATE INDEX idx_level ON logs_by_timestamp(log_level);
```

#### Logs by Service (Cassandra)

```sql
CREATE TABLE logs_by_service (
  service_name TEXT,    -- Partition key
  date_hour TIMESTAMP,  -- Clustering key
  log_id UUID,          -- Clustering key
  timestamp TIMESTAMP,
  log_level TEXT,
  message TEXT,
  fields MAP<TEXT, TEXT>,
  exception_type TEXT,
  PRIMARY KEY (service_name, date_hour, log_id)
) WITH CLUSTERING ORDER BY (date_hour DESC, log_id DESC);
```

#### Exception Summaries (PostgreSQL)

```sql
CREATE TABLE exception_summaries (
  exception_id VARCHAR(255) PRIMARY KEY,
  exception_type VARCHAR(255) NOT NULL,
  service_name VARCHAR(255) NOT NULL,
  count BIGINT DEFAULT 0,
  first_seen TIMESTAMP NOT NULL,
  last_seen TIMESTAMP NOT NULL,
  sample_log_ids UUID[],
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_exception_type ON exception_summaries(exception_type);
CREATE INDEX idx_service ON exception_summaries(service_name);
CREATE INDEX idx_last_seen ON exception_summaries(last_seen DESC);
```

#### Exception Counts by Time Window (Redis)

```
Key: exception:{exception_id}:{time_window}:{timestamp}
Value: count (integer)
TTL: based on time window

Examples:
- exception:exc_123:1h:2025-11-17-10
- exception:exc_123:24h:2025-11-17
```

#### PII Patterns (PostgreSQL)

```sql
CREATE TABLE pii_patterns (
  pattern_id UUID PRIMARY KEY,
  pattern_type VARCHAR(50) NOT NULL,
  regex_pattern TEXT NOT NULL,
  masking_strategy VARCHAR(50) NOT NULL,
  description TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_pattern_type ON pii_patterns(pattern_type);
CREATE INDEX idx_active ON pii_patterns(is_active);
```

#### Query History (PostgreSQL)

```sql
CREATE TABLE query_history (
  query_id UUID PRIMARY KEY,
  user_id VARCHAR(255) NOT NULL,
  query_string TEXT,
  filters JSONB,
  result_count INTEGER,
  execution_time_ms INTEGER,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_id ON query_history(user_id);
CREATE INDEX idx_created_at ON query_history(created_at DESC);
```

### Database Sharding Strategy

**Cassandra (Logs Storage):**
- **Partitioning**: By `date_hour` (hourly partitions)
- **Replication**: 3 replicas per datacenter
- **Sharding**: Natural sharding by time (each hour is a partition)
- **Benefits**: Time-range queries are efficient, easy to delete old data

**Elasticsearch (Search Index):**
- **Sharding**: By `date_hour` and `service_name`
- **Replicas**: 1 primary + 1 replica per shard
- **Benefits**: Distributed search, parallel query execution

**PostgreSQL (Exception Summaries):**
- **Sharding**: By `service_name` (hash-based)
- **Replication**: Primary-replica setup
- **Benefits**: Service-specific queries are efficient

## High-Level Design

```
┌─────────────────┐
│  Applications   │
│  (1000+ services)│
└────────┬────────┘
         │
         │ Logs
         ▼
┌─────────────────┐
│  Load Balancer  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│      Log Ingestion Service          │
│  ┌───────────────────────────────┐ │
│  │  PII Detection Service         │ │
│  │  - Regex patterns              │ │
│  │  - ML models                   │ │
│  └───────────────────────────────┘ │
│  ┌───────────────────────────────┐ │
│  │  PII Masking Service          │ │
│  │  - Redact/Hash/Partial mask   │ │
│  └───────────────────────────────┘ │
└────────┬───────────────────────────┘
         │
         │ Masked logs
         ▼
┌─────────────────┐
│  Kafka Cluster  │
│  (Message Queue)│
└────────┬────────┘
         │
         ├─────────────────┬─────────────────┬─────────────────┐
         ▼                 ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Log Processor│  │ Log Processor│  │ Log Processor│  │ Apache Flink │
│   Workers    │  │   Workers    │  │   Workers    │  │  (Stream     │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │   Processing)│
       │                 │                 │          └──────┬───────┘
       ├─────────────────┼─────────────────┤                 │
       │                 │                 │                 │
       ▼                 ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Elasticsearch│  │   Cassandra  │  │  Exception   │  │    Redis     │
│  (Search)    │  │  (Time-Series)│  │   Tracker    │  │ (Top-K Cache)│
└──────────────┘  └──────────────┘  └──────┬───────┘  └──────┬───────┘
                                            │                 │
                                            └────────┬────────┘
                                                     │
                                            ┌────────▼────────┐
                                            │   PostgreSQL    │
                                            │ (Summaries)     │
                                            └─────────────────┘

         ┌─────────────────────────────────────┐
         │         Query Service                │
         │  ┌───────────────────────────────┐  │
         │  │  Query Parser                 │  │
         │  └───────────────────────────────┘  │
         │  ┌───────────────────────────────┐  │
         │  │  Query Optimizer              │  │
         │  └───────────────────────────────┘  │
         └────────┬────────────────────────────┘
                  │
         ┌────────┴────────┐
         ▼                 ▼
┌──────────────┐  ┌──────────────┐
│ Elasticsearch│  │   Cassandra  │
│  (Field Query)│  │ (Time Query) │
└──────────────┘  └──────────────┘

         ┌─────────────────────────────────────┐
         │    Exception Tracking Service        │
         │  ┌───────────────────────────────┐  │
         │  │  Top-K Exception Calculator   │  │
         │  │  (Queries Flink State Store)  │  │
         │  └───────────────────────────────┘  │
         └────────┬────────────────────────────┘
                  │
         ┌────────┴────────┐
         ▼                 ▼
┌──────────────┐  ┌──────────────┐
│  PostgreSQL  │  │ Apache Flink  │
│ (Summaries)  │  │ (State Store) │
└──────────────┘  └──────┬───────┘
                         │
                         ▼
                ┌──────────────┐
                │    Redis     │
                │ (Top-K Cache)│
                └──────────────┘
```

## Deep Dive

### Component Design

#### 1. Log Ingestion Service

**Responsibilities:**
- Accept logs from applications
- Validate log format
- Detect and mask PII
- Publish to Kafka

**Design:**
- Stateless service, horizontally scalable
- Uses connection pooling for Kafka
- Batches logs before publishing (reduce overhead)
- Returns acknowledgment to client

**PII Detection:**
- Pre-compiled regex patterns for common PII
- ML model for context-aware detection (optional)
- Pattern matching in parallel
- Returns PII locations and types

**PII Masking:**
- Applies masking strategy based on PII type:
  - **SSN**: `***-**-****`
  - **Email**: `***@***.***` or `j***@example.com`
  - **Phone**: `***-***-****`
  - **Credit Card**: `****-****-****-1234` (last 4 digits)
  - **IP Address**: `***.***.***.***` or hash
- Creates masked message
- Stores original encrypted separately if needed

**Scalability:**
- Auto-scaling based on queue depth
- Partition Kafka topics by service/environment
- Rate limiting per service

#### 2. Log Processing Workers

**Responsibilities:**
- Consume logs from Kafka
- Parse and normalize logs
- Extract fields and exceptions
- Index in Elasticsearch
- Store in Cassandra
- Update exception tracking

**Design:**
- Consumer groups for parallel processing
- Idempotent processing (handle duplicates)
- Batch processing for efficiency
- Error handling and dead-letter queue

**Field Extraction:**
- Parse JSON logs
- Extract common fields (timestamp, level, service, etc.)
- Extract custom fields from `fields` map
- Normalize field names

**Exception Detection:**
- Identify exception logs (level = ERROR/FATAL)
- Extract exception type from message or stack trace
- Parse stack trace for context
- Create exception signature (hash of type + service)

#### 3. Search Index (Elasticsearch)

**Responsibilities:**
- Index logs for fast field-based queries
- Support full-text search
- Enable aggregations

**Index Design:**
- **Index per day**: `logs-2025-11-17`
- **Sharding**: By `date_hour` and `service_name`
- **Mapping**: 
  - `timestamp`: date
  - `service_name`: keyword
  - `log_level`: keyword
  - `message`: text (analyzed) + keyword (exact match)
  - `fields.*`: keyword (for field queries)
  - `exception_type`: keyword

**Query Optimization:**
- Use filters (cached) instead of queries when possible
- Use date range filters for time queries
- Use keyword fields for exact matches
- Use aggregations for counts and statistics

**Retention:**
- Delete indices older than retention period
- Use index lifecycle management (ILM)

#### 4. Time-Series Database (Cassandra)

**Responsibilities:**
- Store logs for time-range queries
- Efficient time-based partitioning
- Support range scans

**Table Design:**
- Partition by `date_hour` (hourly partitions)
- Cluster by `log_id` (descending for recent-first)
- Secondary indexes for service and level

**Query Patterns:**
- Time-range queries: Query specific hour partitions
- Service queries: Use secondary index or `logs_by_service` table
- Efficient for recent data queries

**Retention:**
- TTL-based deletion (set TTL on insert)
- Compaction for old data

#### 5. Exception Tracking System (Apache Flink-Based)

**Responsibilities:**
- Track exception counts in real-time
- Calculate top-K exceptions using stream processing
- Store exception summaries
- Support multiple time windows

**Design:**
- **Apache Flink**: Stream processing engine for real-time top-K calculation
  - Consumes exception logs from Kafka
  - Maintains keyed state for exception counts
  - Calculates top-K using windowed aggregations
  - Outputs top-K results to Redis and PostgreSQL
- **Redis**: Real-time cache for top-K queries
  - Stores current top-K exceptions for each window
  - Updated by Flink sink
  - TTL based on window size
- **PostgreSQL**: Persistent exception summaries
  - Store exception metadata
  - Updated by Flink sink
  - Support complex historical queries

**Flink Top-K Calculation:**

**Stream Processing Pipeline:**
```java
// Flink Job: Top-K Exception Tracker
DataStream<LogEntry> logs = env
    .addSource(new FlinkKafkaConsumer<>("exception-logs", ...))
    .filter(log -> log.getLevel() == ERROR || log.getLevel() == FATAL);

// Extract exception signature
DataStream<ExceptionEvent> exceptions = logs
    .map(log -> new ExceptionEvent(
        hash(log.getExceptionType() + log.getServiceName()),
        log.getExceptionType(),
        log.getServiceName(),
        log.getTimestamp()
    ));

// Key by exception signature and service
KeyedStream<ExceptionEvent, String> keyed = exceptions
    .keyBy(event -> event.getExceptionId() + ":" + event.getServiceName());

// Windowed aggregation for different time windows
// 1-hour window
DataStream<ExceptionCount> hourlyCounts = keyed
    .window(TumblingEventTimeWindows.of(Time.hours(1)))
    .aggregate(new ExceptionCountAggregator())
    .windowAll(TumblingEventTimeWindows.of(Time.hours(1)))
    .process(new TopKProcessFunction(10)); // Top 10

// 24-hour window
DataStream<ExceptionCount> dailyCounts = keyed
    .window(TumblingEventTimeWindows.of(Time.hours(24)))
    .aggregate(new ExceptionCountAggregator())
    .windowAll(TumblingEventTimeWindows.of(Time.hours(24)))
    .process(new TopKProcessFunction(10));

// Sliding windows for real-time updates
DataStream<ExceptionCount> slidingCounts = keyed
    .window(SlidingEventTimeWindows.of(Time.hours(1), Time.minutes(5)))
    .aggregate(new ExceptionCountAggregator())
    .windowAll(SlidingEventTimeWindows.of(Time.hours(1), Time.minutes(5)))
    .process(new TopKProcessFunction(10));

// Sink to Redis
hourlyCounts.addSink(new RedisTopKSink("topk:1h"));
dailyCounts.addSink(new RedisTopKSink("topk:24h"));

// Sink to PostgreSQL
hourlyCounts.addSink(new PostgreSQLExceptionSink());
```

**Top-K Process Function:**
```java
public class TopKProcessFunction extends ProcessAllWindowFunction<
    ExceptionCount, TopKResult, TimeWindow> {
    
    private final int k;
    
    @Override
    public void process(Context context, 
                       Iterable<ExceptionCount> elements, 
                       Collector<TopKResult> out) {
        // Collect all exception counts
        List<ExceptionCount> counts = new ArrayList<>();
        for (ExceptionCount count : elements) {
            counts.add(count);
        }
        
        // Sort by count descending and take top K
        List<ExceptionCount> topK = counts.stream()
            .sorted((a, b) -> Long.compare(b.getCount(), a.getCount()))
            .limit(k)
            .collect(Collectors.toList());
        
        // Output top-K result
        out.collect(new TopKResult(
            context.window().getStart(),
            context.window().getEnd(),
            topK
        ));
    }
}
```

**State Management:**
- **Keyed State**: Per exception signature for counting
- **Window State**: Aggregated counts per time window
- **Checkpointing**: Periodic checkpoints for fault tolerance
- **State Backend**: RocksDB for large state storage

**Benefits of Flink Approach:**
- **Real-time Processing**: Low latency (< 100ms) for top-K updates
- **Exactly-Once Semantics**: Guaranteed processing with checkpoints
- **Scalability**: Horizontal scaling with parallelism
- **Multiple Windows**: Efficiently maintain multiple time windows
- **Fault Tolerance**: Automatic recovery from failures
- **State Management**: Built-in state management for aggregations

**Time Windows:**
- **Tumbling Windows**: 1 hour, 24 hours (non-overlapping)
- **Sliding Windows**: 1-hour window sliding every 5 minutes (for real-time updates)
- **Session Windows**: Group exceptions by service sessions
- **Custom Windows**: Support custom windowing logic

**Alternative: Redis-Only Approach (Simpler but Less Scalable)**
- Use Redis sorted sets (ZSET) for simpler deployments
- Key: `topk:{window}:{timestamp}`
- Score: count, Member: exception_id
- Use `ZREVRANGE` to get top-K
- Suitable for smaller scale (< 1M exceptions/hour)

#### 6. Query Service

**Responsibilities:**
- Parse and validate queries
- Optimize query execution
- Aggregate results from multiple sources
- Return paginated results

**Query Strategy:**
- **Field-based queries**: Use Elasticsearch
- **Time-range queries**: Use Cassandra
- **Top-K exceptions**: Use Exception Tracking System
- **Complex queries**: Combine Elasticsearch and Cassandra

**Query Optimization:**
- Cache frequent queries
- Use query hints for optimization
- Parallel queries when possible
- Limit result size

**Result Aggregation:**
- Merge results from multiple sources
- Deduplicate by log_id
- Sort and paginate
- Return metadata (total count, execution time)

### Detailed Design

#### PII Detection and Masking Pipeline

```
Log Message: "User john.doe@example.com with SSN 123-45-6789 made payment"

Step 1: PII Detection
├── Email Pattern: /[\w\.-]+@[\w\.-]+\.\w+/
│   └── Found: "john.doe@example.com" at position 5-27
├── SSN Pattern: /\d{3}-\d{2}-\d{4}/
│   └── Found: "123-45-6789" at position 33-43
└── Result: [Email(5-27), SSN(33-43)]

Step 2: PII Masking
├── Email: "john.doe@example.com" → "***@***.***"
├── SSN: "123-45-6789" → "***-**-****"
└── Masked Message: "User ***@***.*** with SSN ***-**-**** made payment"

Step 3: Store
├── Masked message → Elasticsearch, Cassandra
└── Original (encrypted) → S3 (if compliance requires)
```

#### Top-K Exception Tracking (Flink-Based)

**Real-Time Stream Processing:**
1. **Exception Log Ingestion**:
   - Exception logs published to Kafka topic `exception-logs`
   - Flink consumes from Kafka with exactly-once semantics
   - Filters for ERROR/FATAL level logs

2. **Exception Signature Extraction**:
   - Extract exception type and service name
   - Create exception signature: `hash(exception_type + service_name)`
   - Key stream by `exception_id:service_name`

3. **Windowed Aggregation**:
   - **Tumbling Windows**: 1-hour, 24-hour windows
     - Aggregate exception counts per window
     - Calculate top-K at window end
   - **Sliding Windows**: 1-hour window sliding every 5 minutes
     - Provides real-time updates
     - Recalculates top-K every 5 minutes

4. **Top-K Calculation**:
   - Use `ProcessAllWindowFunction` to collect all counts
   - Sort by count descending
   - Take top K exceptions
   - Output to Redis and PostgreSQL

5. **State Management**:
   - **Keyed State**: Per exception signature for counting
   - **Window State**: Aggregated counts per window
   - **Checkpointing**: Periodic checkpoints (every 60 seconds)
   - **State Backend**: RocksDB for large state

**Query Flow:**
1. **Top-K Query**:
   - Query Redis for cached top-K: `GET topk:{window}:{timestamp}`
   - If cache miss, query Flink state store or PostgreSQL
   - Return top-K exceptions with counts

2. **Real-Time Updates**:
   - Flink updates Redis every window completion
   - Sliding windows provide near real-time updates (5-minute latency)
   - TTL set based on window size

**Fault Tolerance:**
- Flink checkpoints every 60 seconds
- On failure, restore from last checkpoint
- Exactly-once processing guarantees
- State recovery from RocksDB

**Performance:**
- Processing latency: < 100ms per exception
- Top-K calculation: < 500ms per window
- Supports millions of exceptions per hour
- Horizontal scaling with parallelism

#### Multi-Field Query Optimization

**Query Example:**
```
Find ERROR logs from payment-service in last hour 
where user_id = "user_123" and message contains "payment failed"
```

**Query Strategy:**
1. **Time Filter**: Query Cassandra `logs_by_timestamp` for current hour
2. **Service Filter**: Use `logs_by_service` table or secondary index
3. **Level Filter**: Use secondary index or filter in application
4. **Field Filter**: Query Elasticsearch with field query
5. **Text Search**: Use Elasticsearch full-text search
6. **Combine**: Merge results, deduplicate, sort

**Optimization:**
- Use Elasticsearch for complex field queries
- Use Cassandra for simple time-range queries
- Cache query results for repeated queries
- Use materialized views for common query patterns

### Scalability Considerations

1. **Horizontal Scaling:**
   - All components are stateless and horizontally scalable
   - Kafka partitions enable parallel processing
   - Elasticsearch and Cassandra support horizontal scaling

2. **Partitioning:**
   - Kafka: Partition by service/environment
   - Cassandra: Partition by time (hourly)
   - Elasticsearch: Shard by time and service

3. **Caching:**
   - Redis for top-K exception lists (updated by Flink)
   - Query result caching for frequent queries
   - CDN for static dashboards
   - Flink state store for real-time aggregations

4. **Load Balancing:**
   - Load balancer for ingestion service
   - Multiple query service instances
   - Read replicas for databases

5. **Data Retention:**
   - Automatic deletion of old data (TTL)
   - Archive old data to cold storage (S3 Glacier)
   - Compress old indices in Elasticsearch

### Security Considerations

1. **PII Protection:**
   - PII masked before storage
   - Original logs encrypted if stored
   - Access control for unmasked logs
   - Audit logging for PII access

2. **Authentication & Authorization:**
   - API keys for service authentication
   - OAuth for user authentication
   - Role-based access control (RBAC)
   - Service-level permissions

3. **Encryption:**
   - TLS for data in transit
   - Encryption at rest (AES-256)
   - Encrypted backups

4. **Network Security:**
   - VPC for internal services
   - Firewall rules
   - DDoS protection

5. **Compliance:**
   - GDPR compliance (right to deletion)
   - SOC 2 compliance
   - Data retention policies

### Monitoring & Observability

1. **Metrics:**
   - Ingestion rate (logs/second)
   - Query latency (p50, p95, p99)
   - PII detection rate
   - Exception rate
   - Storage usage
   - Error rates

2. **Logging:**
   - Log all system events
   - Track query performance
   - Monitor PII detection accuracy

3. **Alerting:**
   - High exception rates
   - Ingestion failures
   - Query latency spikes
   - Storage capacity warnings
   - PII detection failures

4. **Dashboards:**
   - Real-time ingestion metrics
   - Query performance
   - Top exceptions
   - System health

### Trade-offs and Optimizations

1. **PII Masking:**
   - **Trade-off**: Masking overhead vs. privacy
   - **Optimization**: Pre-compile regex patterns, parallel detection
   - **Alternative**: Mask at query time (slower but more flexible)

2. **Storage:**
   - **Trade-off**: Storage cost vs. query performance
   - **Optimization**: Compress old data, use cold storage
   - **Alternative**: Store only exceptions (lose general logs)

3. **Query Performance:**
   - **Trade-off**: Index size vs. query speed
   - **Optimization**: Selective indexing, materialized views
   - **Alternative**: Pre-aggregate common queries

4. **Top-K Exceptions:**
   - **Trade-off**: Real-time accuracy vs. storage
   - **Optimization**: Use Flink for real-time stream processing with windowed aggregations
   - **Alternative**: Redis sorted sets (simpler but less scalable), batch updates (slower but more accurate)
   - **Flink Benefits**: Exactly-once semantics, fault tolerance, horizontal scaling, multiple time windows

5. **Consistency:**
   - **Trade-off**: Consistency vs. availability
   - **Optimization**: Eventual consistency for queries
   - **Alternative**: Strong consistency (slower writes)

## Summary

This distributed logging system design provides:

1. **Scalable Log Ingestion**: Handles 100K+ logs/second with horizontal scaling
2. **PII Protection**: Automatic detection and masking of PII before storage
3. **Fast Queries**: Multi-field queries in < 1 second using Elasticsearch and Cassandra
4. **Top-K Exceptions**: Real-time tracking and querying of top exceptions using Apache Flink stream processing
5. **High Availability**: 99.9% uptime with replication and redundancy
6. **Cost Efficiency**: Compression, retention policies, and cold storage

**Key Technologies:**
- **Kafka**: Message queue for log ingestion
- **Apache Flink**: Stream processing for real-time top-K exception tracking
- **Elasticsearch**: Search index for field-based queries
- **Cassandra**: Time-series storage for time-range queries
- **Redis**: Cache for top-K exception queries (updated by Flink)
- **PostgreSQL**: Persistent exception summaries
- **S3**: Long-term storage and backups

**Key Design Decisions:**
- PII masking at ingestion time (privacy-first)
- Time-based partitioning for efficient queries and retention
- Separate storage systems for different query patterns
- Real-time exception tracking with Apache Flink for low latency and fault tolerance
- Windowed aggregations for multiple time windows (1h, 24h, etc.)
- Exactly-once processing semantics with Flink checkpoints
- Eventual consistency for better availability

This system can scale to handle billions of logs per day while ensuring data privacy and providing fast query capabilities for debugging and analysis.

