---
layout: post
title: "Design a Top K Heavy Hitter System - System Design Interview"
date: 2025-11-14
categories: [System Design, Interview Example, Distributed Systems, Streaming Systems, Algorithms]
excerpt: "A comprehensive guide to designing a top K heavy hitter system for finding the most frequent items in a data stream, covering Count-Min Sketch, Space-Saving algorithm, distributed counting, and architectural patterns for handling billions of events per day with real-time top K computation."
---

## Introduction

A Top K Heavy Hitter system identifies the K most frequent items in a continuous data stream. This problem appears in many real-world scenarios: finding trending topics on social media, identifying most-viewed videos, tracking top search queries, or detecting popular products. The challenge lies in processing massive streams efficiently while maintaining accurate top K results with limited memory.

This post provides a detailed walkthrough of designing a scalable Top K Heavy Hitter system, covering key algorithmic approaches (Count-Min Sketch, Space-Saving), distributed counting, and scalability challenges. This is a common system design interview question that tests your understanding of streaming algorithms, probabilistic data structures, and handling high-frequency data streams at scale.

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
   - [Scalability Considerations](#scalability-considerations)
   - [Security Considerations](#security-considerations)
   - [Monitoring & Observability](#monitoring--observability)
   - [Trade-offs and Optimizations](#trade-offs-and-optimizations)
10. [Summary](#summary)

## Problem Statement

**Design a Top K Heavy Hitter system that can:**

1. Process a continuous stream of events (e.g., video views, search queries, clicks)
2. Track frequency of each item in the stream
3. Maintain top K most frequent items in real-time
4. Support multiple time windows (last hour, day, week, month)
5. Handle billions of events per day
6. Provide accurate results with bounded memory
7. Support queries for top K items at any time
8. Handle distributed streams from multiple sources

**Scale Requirements:**
- 10 billion+ events per day
- Peak rate: 1 million events per second
- 100 million+ unique items
- K = 10-100 (typically 10)
- Memory constraint: Cannot store all item counts
- Accuracy: 99%+ accuracy for top K items
- Latency: < 100ms for top K queries

## Requirements

### Functional Requirements

**Core Features:**
1. **Event Ingestion**: Accept events from multiple sources
2. **Frequency Tracking**: Track frequency of each item
3. **Top K Computation**: Maintain top K items in real-time
4. **Time Windows**: Support multiple time windows (hour, day, week, month)
5. **Query Interface**: Query top K items for any time window
6. **Item Metadata**: Store metadata for items (name, description, etc.)
7. **Trending Detection**: Detect trending items (rapidly increasing frequency)
8. **Historical Data**: Store historical top K snapshots

**Out of Scope:**
- Full event history storage
- Complex analytics and reporting
- Real-time alerting
- Item deduplication logic

### Non-Functional Requirements

1. **Availability**: 99.9% uptime
2. **Reliability**: No data loss, accurate counts
3. **Performance**: 
   - Event processing: < 1ms per event
   - Top K query: < 100ms
   - Support 1M+ events/second
4. **Scalability**: Handle 10B+ events per day
5. **Accuracy**: 99%+ accuracy for top K items
6. **Memory Efficiency**: Bounded memory usage
7. **Real-Time**: Update top K in near real-time

## Capacity Estimation

### Traffic Estimates

- **Total Events per Day**: 10 billion
- **Peak Events per Second**: 1 million
- **Average Events per Second**: 115,000
- **Unique Items**: 100 million
- **Top K Queries per Day**: 1 million
- **Average Query Rate**: 12 queries/second

### Storage Estimates

**Event Storage (Temporary):**
- Events buffered for 1 minute: 1M events/sec × 60 sec × 100 bytes = 6GB
- With replication: ~18GB

**Frequency Counts:**
- Using Count-Min Sketch: 100M items × 4 bytes = 400MB
- Using Space-Saving: K items × 100 bytes = 10KB (for K=100)
- Total: ~500MB

**Top K Results:**
- Top K snapshots per hour: 24 × 10 items × 1KB = 240KB
- Daily snapshots: 365 × 10 items × 1KB = 3.65MB
- Total: ~4MB

**Item Metadata:**
- 100M items × 500 bytes = 50GB

**Total Storage**: ~50.5GB (excluding event history)

### Bandwidth Estimates

**Event Ingestion:**
- 1M events/sec × 100 bytes = 100MB/s = 800Mbps

**Query Responses:**
- 12 queries/sec × 10KB = 120KB/s = 960Kbps

**Total Bandwidth**: ~801Mbps

## Core Entities

### Event
- `event_id` (UUID)
- `item_id` (VARCHAR)
- `timestamp` (TIMESTAMP)
- `source` (VARCHAR)
- `metadata` (JSON)

### Item
- `item_id` (VARCHAR)
- `name` (VARCHAR)
- `description` (TEXT)
- `category` (VARCHAR)
- `created_at` (TIMESTAMP)

### Frequency Count
- `item_id` (VARCHAR)
- `count` (BIGINT)
- `time_window` (VARCHAR) - 'hour', 'day', 'week', 'month'
- `window_start` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

### Top K Snapshot
- `snapshot_id` (UUID)
- `time_window` (VARCHAR)
- `window_start` (TIMESTAMP)
- `top_k_items` (JSON) - Array of {item_id, count}
- `created_at` (TIMESTAMP)

## API

### 1. Ingest Event
```
POST /api/v1/events
Request:
{
  "item_id": "video_123",
  "timestamp": "2025-11-13T10:00:00Z",
  "source": "web",
  "metadata": {
    "user_id": "user_456",
    "session_id": "session_789"
  }
}

Response:
{
  "status": "accepted",
  "event_id": "uuid"
}
```

### 2. Get Top K
```
GET /api/v1/topk?k=10&time_window=day&window_start=2025-11-13T00:00:00Z
Response:
{
  "time_window": "day",
  "window_start": "2025-11-13T00:00:00Z",
  "top_k": [
    {
      "item_id": "video_123",
      "count": 1500000,
      "rank": 1,
      "item": {
        "name": "Amazing Video",
        "category": "entertainment"
      }
    },
    {
      "item_id": "video_456",
      "count": 1200000,
      "rank": 2,
      "item": {
        "name": "Cool Video",
        "category": "music"
      }
    }
  ],
  "total_items": 1000000,
  "computed_at": "2025-11-13T10:00:00Z"
}
```

### 3. Get Item Frequency
```
GET /api/v1/items/{item_id}/frequency?time_window=day
Response:
{
  "item_id": "video_123",
  "time_window": "day",
  "count": 1500000,
  "rank": 1,
  "updated_at": "2025-11-13T10:00:00Z"
}
```

### 4. Get Trending Items
```
GET /api/v1/trending?k=10&time_window=hour
Response:
{
  "trending_items": [
    {
      "item_id": "video_789",
      "count": 50000,
      "growth_rate": 0.5,
      "rank": 1
    }
  ]
}
```

## Data Flow

### Event Ingestion Flow

1. **Event Arrives**:
   - Event arrives at **API Gateway**
   - **API Gateway** validates and routes to **Event Ingestion Service**
   - **Event Ingestion Service** accepts event

2. **Event Processing**:
   - **Event Ingestion Service**:
     - Validates event
     - Extracts item_id
     - Publishes event to **Message Queue** (Kafka)
     - Returns acknowledgment

3. **Stream Processing**:
   - **Stream Processor** consumes events from queue
   - Updates frequency counts in **Count-Min Sketch** or **Space-Saving** structure
   - Updates top K data structure
   - Publishes updates to **Top K Service**

### Top K Query Flow

1. **Query Request**:
   - User requests top K for time window
   - **API Gateway** routes to **Top K Service**
   - **Top K Service** checks cache

2. **Top K Computation**:
   - If cache miss:
     - **Top K Service** queries frequency counts
     - Computes top K items
     - Enriches with item metadata
     - Caches result
   - Returns top K items

3. **Response**:
   - **Top K Service** returns ranked list
   - **Client** displays results

### Frequency Update Flow

1. **Event Processing**:
   - **Stream Processor** processes event
   - Updates frequency count for item_id
   - Updates time-windowed counts

2. **Top K Update**:
   - **Top K Service** receives frequency update
   - Updates top K data structure
   - Maintains heap or sorted list
   - Invalidates cache for affected time windows

## Database Design

### Schema Design

**Events Table (Temporary Buffer):**
```sql
CREATE TABLE events_buffer (
    event_id UUID PRIMARY KEY,
    item_id VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    source VARCHAR(50),
    metadata JSON,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_item_timestamp (item_id, timestamp),
    INDEX idx_timestamp (timestamp)
) PARTITION BY RANGE (timestamp);
```

**Items Table:**
```sql
CREATE TABLE items (
    item_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(500),
    description TEXT,
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_category (category)
);
```

**Frequency Counts Table (Materialized):**
```sql
CREATE TABLE frequency_counts (
    item_id VARCHAR(255),
    time_window VARCHAR(20), -- 'hour', 'day', 'week', 'month'
    window_start TIMESTAMP,
    count BIGINT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (item_id, time_window, window_start),
    INDEX idx_window_count (time_window, window_start, count DESC),
    INDEX idx_item_window (item_id, time_window)
);
```

**Top K Snapshots Table:**
```sql
CREATE TABLE top_k_snapshots (
    snapshot_id UUID PRIMARY KEY,
    time_window VARCHAR(20),
    window_start TIMESTAMP,
    k INT,
    top_k_items JSON NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_window (time_window, window_start DESC),
    INDEX idx_created_at (created_at DESC)
);
```

### Database Sharding Strategy

**Events Buffer Sharding:**
- Shard by timestamp (time-based partitioning)
- Partition by hour or day
- Enables efficient cleanup of old events
- 24-365 partitions depending on retention

**Frequency Counts Sharding:**
- Shard by item_id hash
- 1000 shards: `shard_id = hash(item_id) % 1000`
- Enables parallel processing
- Prevents hot-spotting

**Replication:**
- Each shard replicated 3x for high availability
- Master-replica setup for read scaling
- Writes go to master, reads can go to replicas

## High-Level Design

```
┌─────────────┐
│Event Sources│
│(Web, Mobile)│
└──────┬──────┘
       │
       │ Events
       │
┌──────▼──────────────────────────────────────────────┐
│        API Gateway / Load Balancer                   │
└──────┬──────────────────────────────────────────────┘
       │
       │
┌──────▼──────────────────────────────────────────────┐
│         Event Ingestion Service                      │
│         - Validate events                           │
│         - Publish to queue                          │
└──────┬──────────────────────────────────────────────┘
       │
       │
┌──────▼──────────────────────────────────────────────┐
│              Message Queue (Kafka)                   │
│              - Event stream                          │
│              - Partitioned by item_id                │
└──────┬──────────────────────────────────────────────┘
       │
       │
┌──────▼──────────────────────────────────────────────┐
│         Stream Processor (Workers)                   │
│  ┌──────────────┐  ┌──────────────┐                 │
│  │ Count-Min   │  │ Space-Saving │                 │
│  │ Sketch      │  │ Algorithm    │                 │
│  └──────┬───────┘  └──────┬───────┘                 │
│         │                  │                          │
│  ┌──────▼──────────────────▼──────────────┐        │
│  │         Top K Maintainer                │        │
│  │  - Min Heap / Sorted List              │        │
│  │  - Real-time top K updates             │        │
│  └──────┬──────────────────────────────────┘        │
└─────────┼───────────────────────────────────────────┘
          │
          │
┌─────────▼───────────────────────────────────────────┐
│         Top K Service                                │
│         - Query top K                                │
│         - Cache results                              │
│         - Enrich with metadata                       │
└─────────┬────────────────────────────────────────────┘
          │
          │
┌─────────▼─────────────────────────────────────────────┐
│         Database Cluster (Sharded)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │ Events   │  │ Frequency│  │ Top K    │            │
│  │ Buffer   │  │ Counts   │  │ Snapshots│            │
│  └──────────┘  └──────────┘  └──────────┘            │
└───────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────┐
│              Cache Layer (Redis)                      │
│  - Top K results cache                                │
│  - Frequency counts cache                             │
│  - Item metadata cache                                │
└───────────────────────────────────────────────────────┘
```

## Deep Dive

### Component Design

#### 1. Count-Min Sketch

**Responsibilities:**
- Estimate frequency of items in stream
- Use probabilistic data structure
- Provide approximate counts with bounded memory

**Key Design Decisions:**
- **Width and Depth**: Balance accuracy vs memory
- **Hash Functions**: Use multiple independent hash functions
- **Memory Efficient**: O(width × depth) memory
- **Approximate**: Provides overestimate (never underestimate)

**Implementation:**
```python
import mmh3
import numpy as np

class CountMinSketch:
    def __init__(self, width=10000, depth=5):
        self.width = width
        self.depth = depth
        self.table = np.zeros((depth, width), dtype=np.int64)
        self.seeds = [i for i in range(depth)]
    
    def increment(self, item_id):
        for i in range(self.depth):
            hash_value = mmh3.hash(item_id, self.seeds[i]) % self.width
            self.table[i][hash_value] += 1
    
    def estimate(self, item_id):
        min_count = float('inf')
        for i in range(self.depth):
            hash_value = mmh3.hash(item_id, self.seeds[i]) % self.width
            min_count = min(min_count, self.table[i][hash_value])
        return min_count
    
    def get_size_bytes(self):
        return self.width * self.depth * 8  # 8 bytes per int64
```

**Memory Usage:**
- Width: 10,000, Depth: 5
- Memory: 10,000 × 5 × 8 bytes = 400KB
- Can handle millions of items with fixed memory

#### 2. Space-Saving Algorithm

**Responsibilities:**
- Maintain top K items exactly
- Track frequency of top K items
- Handle new items efficiently

**Key Design Decisions:**
- **Fixed Size**: Maintain exactly K items
- **Min Frequency**: Track minimum frequency in top K
- **Replacement**: Replace item with minimum frequency
- **Exact Counts**: Provides exact counts for top K

**Implementation:**
```python
from collections import defaultdict
import heapq

class SpaceSaving:
    def __init__(self, k=10):
        self.k = k
        self.counts = defaultdict(int)  # item_id -> count
        self.min_heap = []  # (count, item_id) min heap
        self.min_freq = 0
    
    def increment(self, item_id):
        if item_id in self.counts:
            # Item already tracked
            self.counts[item_id] += 1
            # Update heap (lazy update)
            heapq.heappush(self.min_heap, (self.counts[item_id], item_id))
        elif len(self.counts) < self.k:
            # Space available, add new item
            self.counts[item_id] = 1
            heapq.heappush(self.min_heap, (1, item_id))
            self.min_freq = 1
        else:
            # Replace minimum frequency item
            min_item = heapq.heappop(self.min_heap)
            del self.counts[min_item[1]]
            
            self.counts[item_id] = min_item[0] + 1
            heapq.heappush(self.min_heap, (self.counts[item_id], item_id))
            self.min_freq = self.min_heap[0][0]
    
    def get_top_k(self):
        return sorted(
            [(item_id, count) for item_id, count in self.counts.items()],
            key=lambda x: x[1],
            reverse=True
        )[:self.k]
```

**Memory Usage:**
- K items × (item_id + count) = K × 100 bytes
- For K=100: ~10KB
- Extremely memory efficient

#### 3. Hybrid Approach: Count-Min Sketch + Space-Saving

**Challenge:** Balance accuracy and memory

**Solution:**
- Use Count-Min Sketch for all items (approximate counts)
- Use Space-Saving for top K candidates (exact counts)
- Periodically refresh Space-Saving from Count-Min Sketch

**Implementation:**
```python
class HybridTopK:
    def __init__(self, k=10, sketch_width=10000, sketch_depth=5):
        self.k = k
        self.sketch = CountMinSketch(sketch_width, sketch_depth)
        self.space_saving = SpaceSaving(k * 2)  # Keep 2K candidates
        
    def increment(self, item_id):
        # Update both structures
        self.sketch.increment(item_id)
        self.space_saving.increment(item_id)
    
    def get_top_k(self):
        # Get top K from Space-Saving (exact counts)
        return self.space_saving.get_top_k()[:self.k]
    
    def refresh(self):
        # Periodically refresh Space-Saving with top candidates from sketch
        # This is expensive, so do it infrequently
        pass
```

#### 4. Stream Processor

**Responsibilities:**
- Process events from message queue
- Update frequency counts
- Maintain top K data structures
- Handle time windows

**Key Design Decisions:**
- **Parallel Processing**: Multiple workers process events
- **Time Windows**: Maintain separate counts per window
- **Batch Processing**: Process events in batches
- **Fault Tolerance**: Handle failures gracefully

**Implementation:**
```python
def process_events(events):
    for event in events:
        item_id = event['item_id']
        timestamp = event['timestamp']
        
        # Update all time windows
        time_windows = get_time_windows(timestamp)
        
        for window in time_windows:
            # Update Count-Min Sketch
            sketch = get_sketch(window)
            sketch.increment(item_id)
            
            # Update Space-Saving
            space_saving = get_space_saving(window)
            space_saving.increment(item_id)
            
            # Update top K
            update_top_k(window, item_id, space_saving.get_top_k())
```

#### 5. Top K Service

**Responsibilities:**
- Query top K items
- Cache results
- Enrich with metadata
- Handle time windows

**Key Design Decisions:**
- **Caching**: Cache top K results
- **Metadata Enrichment**: Join with item metadata
- **Real-Time**: Return near real-time results
- **Time Windows**: Support multiple windows

**Implementation:**
```python
def get_top_k(k=10, time_window='day', window_start=None):
    # Generate cache key
    cache_key = f"topk:{time_window}:{window_start}:{k}"
    
    # Check cache
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    # Get top K from data structure
    space_saving = get_space_saving(time_window, window_start)
    top_k = space_saving.get_top_k()[:k]
    
    # Enrich with metadata
    enriched = []
    for item_id, count in top_k:
        item_metadata = get_item_metadata(item_id)
        enriched.append({
            'item_id': item_id,
            'count': count,
            'item': item_metadata
        })
    
    # Cache result (TTL: 1 minute)
    cache.set(cache_key, enriched, ttl=60)
    
    return enriched
```

### Detailed Design

#### Time Window Management

**Challenge:** Maintain top K for multiple time windows

**Solution:**
- **Separate Data Structures**: One per time window
- **Sliding Windows**: Use circular buffers for sliding windows
- **Window Expiration**: Clean up expired windows
- **Window Aggregation**: Aggregate windows when needed

**Implementation:**
```python
class TimeWindowManager:
    def __init__(self):
        self.windows = {
            'hour': {},
            'day': {},
            'week': {},
            'month': {}
        }
    
    def get_window_start(self, timestamp, window_type):
        if window_type == 'hour':
            return timestamp.replace(minute=0, second=0, microsecond=0)
        elif window_type == 'day':
            return timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        # ... similar for week, month
    
    def get_sketch(self, window_type, window_start):
        key = f"{window_type}:{window_start}"
        if key not in self.windows[window_type]:
            self.windows[window_type][key] = CountMinSketch()
        return self.windows[window_type][key]
    
    def cleanup_expired_windows(self):
        now = datetime.now()
        for window_type in self.windows:
            expired_keys = []
            for key in self.windows[window_type]:
                window_start = parse_window_start(key)
                if is_expired(window_start, window_type, now):
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.windows[window_type][key]
```

#### Distributed Counting

**Challenge:** Aggregate counts across multiple stream processors

**Solution:**
- **Sharding**: Shard items across processors
- **Local Aggregation**: Each processor maintains local counts
- **Periodic Aggregation**: Periodically aggregate across processors
- **Consistent Hashing**: Use consistent hashing for sharding

**Implementation:**
```python
class DistributedTopK:
    def __init__(self, num_processors=10, k=10):
        self.num_processors = num_processors
        self.k = k
        self.processors = [
            HybridTopK(k=k) for _ in range(num_processors)
        ]
    
    def increment(self, item_id):
        # Route to processor based on item_id hash
        processor_id = hash(item_id) % self.num_processors
        self.processors[processor_id].increment(item_id)
    
    def get_top_k(self):
        # Aggregate top K from all processors
        all_candidates = []
        
        for processor in self.processors:
            top_k = processor.get_top_k()
            all_candidates.extend(top_k)
        
        # Merge and get global top K
        merged = {}
        for item_id, count in all_candidates:
            merged[item_id] = merged.get(item_id, 0) + count
        
        # Sort and return top K
        sorted_items = sorted(
            merged.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_items[:self.k]
```

#### Trending Detection

**Challenge:** Detect items with rapidly increasing frequency

**Solution:**
- **Growth Rate**: Calculate growth rate between time windows
- **Threshold**: Items with growth rate above threshold are trending
- **Time Comparison**: Compare current window with previous window
- **Ranking**: Rank by growth rate

**Implementation:**
```python
def get_trending_items(k=10, time_window='hour'):
    current_window = get_current_window(time_window)
    previous_window = get_previous_window(time_window)
    
    current_counts = get_counts(current_window)
    previous_counts = get_counts(previous_window)
    
    trending = []
    for item_id in current_counts:
        current_count = current_counts[item_id]
        previous_count = previous_counts.get(item_id, 0)
        
        if previous_count > 0:
            growth_rate = (current_count - previous_count) / previous_count
        else:
            growth_rate = float('inf') if current_count > 0 else 0
        
        trending.append({
            'item_id': item_id,
            'current_count': current_count,
            'growth_rate': growth_rate
        })
    
    # Sort by growth rate
    trending.sort(key=lambda x: x['growth_rate'], reverse=True)
    
    return trending[:k]
```

### Scalability Considerations

#### Horizontal Scaling

**Stream Processors:**
- Scale horizontally with Kafka consumer groups
- Each processor handles subset of items
- Consistent hashing for item distribution
- Parallel processing

**Top K Service:**
- Stateless service, horizontally scalable
- Load balancer distributes queries
- Shared cache (Redis) for results
- Database connection pooling

#### Caching Strategy

**Redis Cache:**
- **Top K Results**: TTL 1 minute
- **Frequency Counts**: TTL 5 minutes
- **Item Metadata**: TTL 1 hour
- **Trending Items**: TTL 5 minutes

**Cache Invalidation:**
- Invalidate on top K updates
- Invalidate on time window rollover
- Use cache-aside pattern

#### Memory Management

**Bounded Memory:**
- Count-Min Sketch: Fixed size
- Space-Saving: Fixed size (K items)
- Time Windows: Limit number of windows
- Cleanup: Periodic cleanup of expired windows

### Security Considerations

#### Rate Limiting

- **Per-User Rate Limiting**: Limit queries per user
- **Per-IP Rate Limiting**: Limit queries per IP
- **Event Rate Limiting**: Limit event ingestion rate
- **Sliding Window**: Use sliding window algorithm

#### Input Validation

- **Event Validation**: Validate event structure
- **Item ID Validation**: Validate item_id format
- **Timestamp Validation**: Validate timestamps
- **Size Limits**: Limit event size

### Monitoring & Observability

#### Key Metrics

**System Metrics:**
- Event processing rate (events/second)
- Top K query latency (p50, p95, p99)
- Memory usage
- Cache hit rate
- Error rate

**Business Metrics:**
- Total events processed
- Unique items tracked
- Top K accuracy
- Trending items detected

#### Logging

- **Structured Logging**: JSON logs for parsing
- **Event Logging**: Log events (sampled)
- **Query Logging**: Log top K queries
- **Performance Logging**: Log slow queries

#### Alerting

- **High Latency**: Alert if p99 latency > 100ms
- **High Error Rate**: Alert if error rate > 1%
- **Memory Usage**: Alert if memory > 80%
- **Low Accuracy**: Alert if accuracy < 95%

### Trade-offs and Optimizations

#### Trade-offs

**1. Count-Min Sketch vs Space-Saving**
- **Count-Min Sketch**: All items, approximate, fixed memory
- **Space-Saving**: Top K only, exact, very small memory
- **Decision**: Hybrid approach (both)

**2. Accuracy vs Memory**
- **High Accuracy**: More memory, larger sketch
- **Low Memory**: Less accuracy, smaller sketch
- **Decision**: Balance based on requirements

**3. Real-Time vs Batch**
- **Real-Time**: Lower latency, higher cost
- **Batch**: Higher latency, lower cost
- **Decision**: Real-time with batching optimization

**4. Exact vs Approximate**
- **Exact**: More memory, slower
- **Approximate**: Less memory, faster
- **Decision**: Approximate for all items, exact for top K

#### Optimizations

**1. Batch Processing**
- Batch event processing
- Reduce overhead
- Improve throughput

**2. Compression**
- Compress Count-Min Sketch
- Compress top K results
- Reduce memory usage

**3. Sampling**
- Sample events for very high frequency items
- Reduce processing load
- Maintain accuracy

**4. Precomputation**
- Precompute top K for common time windows
- Reduce query latency
- Improve cache hit rate

## What Interviewers Look For

### Algorithm Knowledge

1. **Probabilistic Data Structures**
   - Count-Min Sketch understanding
   - Space-Saving algorithm
   - Trade-offs between approaches
   - **Red Flags**: No understanding, wrong choice, no trade-offs

2. **Algorithm Efficiency**
   - O(1) update operations
   - Bounded memory usage
   - Accuracy vs memory trade-offs
   - **Red Flags**: Inefficient algorithms, unbounded memory

3. **Time Window Handling**
   - Multiple time windows
   - Efficient window management
   - **Red Flags**: Single window, inefficient management

### Distributed Systems Skills

1. **Distributed Counting**
   - Consistent hashing
   - Count aggregation
   - Merge strategies
   - **Red Flags**: No distribution, poor aggregation

2. **Real-Time Processing**
   - Stream processing
   - Low-latency updates
   - **Red Flags**: Batch-only, high latency

3. **Scalability Design**
   - Horizontal scaling
   - Load distribution
   - **Red Flags**: Vertical scaling, bottlenecks

### Problem-Solving Approach

1. **Memory Efficiency**
   - Bounded memory design
   - Fixed-size data structures
   - **Red Flags**: Unbounded memory, growing structures

2. **Accuracy Trade-offs**
   - Approximate vs exact
   - Error bounds understanding
   - **Red Flags**: No accuracy consideration, wrong approach

3. **Edge Cases**
   - Ties in counts
   - Very high frequency items
   - Sparse data
   - **Red Flags**: Ignoring edge cases, no handling

### System Design Skills

1. **Data Structure Choice**
   - Count-Min Sketch vs Space-Saving
   - Hybrid approach
   - **Red Flags**: Wrong structure, no hybrid

2. **Caching Strategy**
   - Top K result caching
   - Cache invalidation
   - **Red Flags**: No caching, poor invalidation

3. **Query Optimization**
   - Fast top K retrieval
   - Efficient queries
   - **Red Flags**: Slow queries, no optimization

### Communication Skills

1. **Algorithm Explanation**
   - Can explain probabilistic structures
   - Understands error bounds
   - **Red Flags**: No understanding, vague explanations

2. **Trade-off Analysis**
   - Accuracy vs memory
   - Exact vs approximate
   - **Red Flags**: No trade-offs, dogmatic choices

### Meta-Specific Focus

1. **Algorithmic Thinking**
   - Strong CS fundamentals
   - Probabilistic structures knowledge
   - **Key**: Show algorithmic expertise

2. **Stream Processing**
   - Real-time processing understanding
   - Low-latency design
   - **Key**: Demonstrate stream processing knowledge

## Summary

Designing a Top K Heavy Hitter system at scale requires careful consideration of:

1. **Probabilistic Data Structures**: Count-Min Sketch for approximate counts
2. **Space-Saving Algorithm**: Exact top K with bounded memory
3. **Hybrid Approach**: Combine both for accuracy and efficiency
4. **Time Windows**: Support multiple time windows efficiently
5. **Distributed Counting**: Aggregate counts across processors
6. **Caching**: Cache top K results for fast queries
7. **Memory Efficiency**: Bounded memory usage
8. **Real-Time Processing**: Process events in real-time

Key architectural decisions:
- **Count-Min Sketch** for approximate frequency tracking
- **Space-Saving Algorithm** for exact top K
- **Hybrid Approach** combining both
- **Time-Windowed Counts** for multiple windows
- **Distributed Processing** with consistent hashing
- **Caching** for fast top K queries
- **Bounded Memory** with fixed-size data structures

The system handles 1 million events per second, maintains top K with 99%+ accuracy, and provides sub-100ms query latency with bounded memory usage.

