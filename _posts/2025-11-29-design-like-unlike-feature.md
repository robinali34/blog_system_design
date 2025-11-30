---
layout: post
title: "Design a Like/Unlike Feature - System Design Interview"
date: 2025-11-29
categories: [System Design, Interview Example, Distributed Systems, Social Media, High-Throughput Systems]
excerpt: "A comprehensive guide to designing a like/unlike feature system that handles high read traffic (1M QPS) and significant write traffic (100k QPS) while maintaining data consistency. Covers counter management, caching strategies, and scalability patterns."
---

## Introduction

Designing a like/unlike feature is a common system design interview question that tests your ability to handle high-throughput read and write operations while maintaining data consistency. The system must support users favoriting/unfavoriting items, checking favorite status, viewing favorite counts, and listing favorited items at massive scale.

This post provides a detailed walkthrough of designing a like/unlike feature system, covering key architectural decisions, counter management, caching strategies, and scalability challenges. This question tests your understanding of distributed systems, high-throughput systems, eventual consistency, and counter management patterns.

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Requirements](#requirements)
   - [Functional Requirements](#functional-requirements)
   - [Non-Functional Requirements](#non-functional-requirements)
3. [Capacity Estimation](#capacity-estimation)
   - [Traffic Estimates](#traffic-estimates)
   - [Storage Estimates](#storage-estimates)
4. [Core Entities](#core-entities)
5. [API](#api)
6. [Data Flow](#data-flow)
7. [Database Design](#database-design)
   - [Schema Design](#schema-design)
   - [Database Sharding Strategy](#database-sharding-strategy)
8. [High-Level Design](#high-level-design)
9. [Deep Dive](#deep-dive)
   - [Component Design](#component-design)
   - [Counter Management](#counter-management)
   - [Caching Strategy](#caching-strategy)
   - [Consistency Model](#consistency-model)
   - [Scalability Considerations](#scalability-considerations)
   - [Failure Handling](#failure-handling)
   - [Trade-offs and Optimizations](#trade-offs-and-optimizations)
10. [What Interviewers Look For](#what-interviewers-look-for)
11. [Summary](#summary)

## Problem Statement

**Design a like/unlike feature system that:**

1. Allows users to favorite/unfavorite items (posts, videos, articles, etc.)
2. Check favorite status (whether a user has favorited an item)
3. View favorite counts (total number of favorites for an item)
4. List user's favorited items (all items a user has favorited)

**Scale Requirements:**
- 1M QPS for status checks and count reads
- 100k QPS for favorite/unfavorite write operations
- Support billions of users and items
- Maintain data consistency
- Low latency (< 50ms for reads, < 100ms for writes)

## Requirements

### Functional Requirements

**Core Features:**
1. **Favorite Item**: User can favorite an item
2. **Unfavorite Item**: User can remove favorite from an item
3. **Check Status**: Check if a user has favorited a specific item
4. **Get Count**: Get total favorite count for an item
5. **List Favorites**: Get list of all items favorited by a user (with pagination)
6. **Idempotency**: Multiple favorite/unfavorite requests should be handled correctly

**Out of Scope:**
- Real-time notifications for favorites
- Favorite analytics (trending items, etc.)
- Favorite categories or tags
- Bulk operations (favorite multiple items at once)

### Non-Functional Requirements

1. **Availability**: 99.9% uptime
2. **Reliability**: No data loss, all operations must be durable
3. **Performance**: 
   - Status check: < 50ms (P95)
   - Count read: < 50ms (P95)
   - Favorite/unfavorite write: < 100ms (P95)
   - List favorites: < 200ms (P95)
4. **Scalability**: Handle 1M+ QPS reads, 100k+ QPS writes
5. **Consistency**: 
   - Strong consistency for status checks (user's own favorites)
   - Eventual consistency acceptable for counts (can be slightly stale)
6. **Durability**: All favorite/unfavorite operations must be persisted

## Capacity Estimation

### Traffic Estimates

- **Read QPS**: 1M QPS (status checks + counts)
  - Status checks: 600k QPS (60%)
  - Count reads: 400k QPS (40%)
- **Write QPS**: 100k QPS (favorite/unfavorite)
  - Favorite: 60k QPS (60%)
  - Unfavorite: 40k QPS (40%)
- **List Favorites**: 50k QPS (lower frequency)
- **Peak traffic**: 3x average = 3M QPS reads, 300k QPS writes

### Storage Estimates

**Favorite Records:**
- 100k writes/sec × 86400 sec/day = 8.64B favorites/day
- Average record size: 32 bytes (user_id, item_id, timestamp)
- Daily storage: 8.64B × 32 bytes = 276GB/day
- 5 years retention: 276GB × 365 × 5 = 504TB

**Counter Storage:**
- Assume 1B unique items
- Counter size: 8 bytes (item_id + count)
- Total counter storage: 1B × 8 bytes = 8GB

**User Favorites Index:**
- For fast listing of user's favorites
- Average 100 favorites per user
- 1B users × 100 × 8 bytes = 800GB

**Total Storage**: ~505TB over 5 years

## Core Entities

### Favorite
- **Attributes**: favorite_id, user_id, item_id, item_type, created_at
- **Relationships**: Links user to item
- **Constraints**: Unique (user_id, item_id) pair

### FavoriteCount
- **Attributes**: item_id, item_type, count, updated_at
- **Relationships**: Aggregated count per item
- **Purpose**: Fast count retrieval

### UserFavoriteIndex
- **Attributes**: user_id, item_id, item_type, created_at
- **Relationships**: Index for user's favorites
- **Purpose**: Fast listing of user's favorites

## API

### 1. Favorite Item
```
POST /api/v1/items/{item_id}/favorite
Headers:
  - Authorization: Bearer <token>
Parameters:
  - item_id: item identifier
  - item_type: type of item (post, video, article, etc.)
Response:
  - success: boolean
  - favorite_id: unique favorite identifier
  - count: updated favorite count (eventual consistency)
```

### 2. Unfavorite Item
```
DELETE /api/v1/items/{item_id}/favorite
Headers:
  - Authorization: Bearer <token>
Parameters:
  - item_id: item identifier
Response:
  - success: boolean
  - count: updated favorite count (eventual consistency)
```

### 3. Check Favorite Status
```
GET /api/v1/items/{item_id}/favorite/status
Headers:
  - Authorization: Bearer <token>
Parameters:
  - item_id: item identifier
Response:
  - is_favorited: boolean
  - favorited_at: timestamp (if favorited)
```

### 4. Get Favorite Count
```
GET /api/v1/items/{item_id}/favorite/count
Parameters:
  - item_id: item identifier
Response:
  - count: total favorite count
  - cached: boolean (indicates if count is cached)
```

### 5. List User Favorites
```
GET /api/v1/users/{user_id}/favorites
Headers:
  - Authorization: Bearer <token>
Parameters:
  - user_id: user identifier
  - cursor: pagination cursor (optional)
  - limit: number of items to return (default: 20, max: 100)
  - item_type: filter by item type (optional)
Response:
  - items: array of favorited items
  - next_cursor: cursor for next page
  - has_more: boolean
```

## Data Flow

### Favorite Operation Flow

```
1. Client → API Gateway
2. API Gateway → Auth Service (validate token)
3. API Gateway → Like Service
4. Like Service:
   a. Check cache for existing favorite (Redis)
   b. If not cached, check database
   c. If already favorited, return success (idempotent)
   d. Write favorite record to database (sharded by user_id)
   e. Update counter (async via message queue)
   f. Invalidate cache entries
   g. Return success
```

### Unfavorite Operation Flow

```
1. Client → API Gateway
2. API Gateway → Auth Service (validate token)
3. API Gateway → Like Service
4. Like Service:
   a. Check cache for favorite status
   b. If not cached, check database
   c. If not favorited, return success (idempotent)
   d. Delete favorite record from database
   e. Update counter (async via message queue)
   f. Invalidate cache entries
   g. Return success
```

### Status Check Flow

```
1. Client → API Gateway
2. API Gateway → Like Service
3. Like Service:
   a. Check Redis cache (key: user_id:item_id)
   b. If cache hit, return status
   c. If cache miss, query database
   d. Cache result (TTL: 1 hour)
   e. Return status
```

### Count Read Flow

```
1. Client → API Gateway
2. API Gateway → Like Service
3. Like Service:
   a. Check Redis cache (key: item_id:count)
   b. If cache hit, return count
   c. If cache miss, query counter table
   d. Cache result (TTL: 5 minutes)
   e. Return count
```

## Database Design

### Schema Design

#### Favorites Table
```sql
CREATE TABLE favorites (
    favorite_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    item_id BIGINT NOT NULL,
    item_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_item (user_id, item_id),
    INDEX idx_item (item_id),
    INDEX idx_user_created (user_id, created_at),
    UNIQUE KEY uk_user_item (user_id, item_id, item_type)
) ENGINE=InnoDB;

-- Sharded by user_id
-- Partition key: user_id
```

#### FavoriteCounts Table
```sql
CREATE TABLE favorite_counts (
    item_id BIGINT NOT NULL,
    item_type VARCHAR(50) NOT NULL,
    count BIGINT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (item_id, item_type),
    INDEX idx_count (count DESC)
) ENGINE=InnoDB;

-- Sharded by item_id
-- Partition key: item_id
```

#### UserFavoritesIndex Table (Optional - for fast listing)
```sql
CREATE TABLE user_favorites_index (
    user_id BIGINT NOT NULL,
    item_id BIGINT NOT NULL,
    item_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, item_id, item_type),
    INDEX idx_user_created (user_id, created_at DESC)
) ENGINE=InnoDB;

-- Sharded by user_id
-- Partition key: user_id
```

### Database Sharding Strategy

**Favorites Table:**
- **Shard Key**: `user_id`
- **Sharding Strategy**: Hash-based sharding
- **Number of Shards**: 1000 shards
- **Reasoning**: Queries are primarily user-centric (check status, list favorites)

**FavoriteCounts Table:**
- **Shard Key**: `item_id`
- **Sharding Strategy**: Hash-based sharding
- **Number of Shards**: 1000 shards
- **Reasoning**: Queries are item-centric (get count for item)

**UserFavoritesIndex Table:**
- **Shard Key**: `user_id`
- **Sharding Strategy**: Hash-based sharding (same as Favorites table)
- **Number of Shards**: 1000 shards
- **Reasoning**: Aligns with user-centric queries

## High-Level Design

```
┌─────────────────────────────────────────────────────────┐
│                    Client Applications                   │
│              (Web, Mobile, API Clients)                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTPS
                     │
┌────────────────────▼────────────────────────────────────┐
│                  API Gateway / LB                        │
│              (Rate Limiting, Auth)                       │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
┌────────▼────────┐    ┌─────────▼─────────┐
│   Read Service  │    │   Write Service    │
│  (Status/Count) │    │ (Favorite/Unfav)   │
└────────┬────────┘    └─────────┬──────────┘
         │                       │
         │                       │
┌────────▼────────┐    ┌─────────▼──────────┐
│   Redis Cache   │    │  Message Queue     │
│  (Status/Count) │    │   (Kafka/SQS)      │
└────────┬────────┘    └─────────┬──────────┘
         │                       │
         │                       │
┌────────▼───────────────────────▼──────────┐
│         Database Cluster                  │
│  (Sharded: Favorites, Counts, Index)      │
└───────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
┌────────▼────────┐    ┌─────────▼──────────┐
│ Counter Service │    │  Analytics Service │
│ (Async Updates) │    │   (Optional)       │
└─────────────────┘    └────────────────────┘
```

## Deep Dive

### Component Design

#### 1. API Gateway
- **Responsibilities**: Authentication, rate limiting, request routing
- **Technologies**: NGINX, AWS API Gateway, Kong
- **Rate Limiting**: 
  - Per-user rate limits (prevent abuse)
  - Global rate limits (protect backend)

#### 2. Read Service
- **Responsibilities**: Handle status checks and count reads
- **Optimization**: 
  - Heavy caching (Redis)
  - Read replicas for database
  - Connection pooling

#### 3. Write Service
- **Responsibilities**: Handle favorite/unfavorite operations
- **Optimization**:
  - Async counter updates
  - Batch writes where possible
  - Idempotency handling

#### 4. Cache Layer (Redis)
- **Cache Keys**:
  - Status: `favorite:status:{user_id}:{item_id}` (TTL: 1 hour)
  - Count: `favorite:count:{item_id}` (TTL: 5 minutes)
  - User favorites: `favorite:user:{user_id}:{cursor}` (TTL: 10 minutes)
- **Cache Strategy**: 
  - Write-through for status (strong consistency)
  - Write-behind for counts (eventual consistency)
  - Cache invalidation on writes

#### 5. Message Queue (Kafka/SQS)
- **Purpose**: Async counter updates
- **Topics/Queues**:
  - `favorite-events`: Favorite/unfavorite events
- **Consumers**: Counter update service

#### 6. Database Cluster
- **Primary Database**: MySQL/PostgreSQL (sharded)
- **Read Replicas**: For read-heavy operations
- **Connection Pooling**: PgBouncer, ProxySQL

### Counter Management

**Challenge**: Updating counters synchronously would create hot spots and contention.

**Solution**: Async counter updates with eventual consistency

**Approach**:
1. **Write Path**: 
   - Write favorite record immediately (strong consistency)
   - Publish event to message queue (async)
   - Return success immediately

2. **Counter Update**:
   - Consumer processes events from queue
   - Batch updates (e.g., every 100 events or 1 second)
   - Update counter table
   - Invalidate cache

3. **Read Path**:
   - Check cache first
   - If miss, read from counter table
   - Cache result

**Benefits**:
- Reduces database contention
- Improves write latency
- Handles traffic spikes better

**Trade-offs**:
- Counts may be slightly stale (acceptable for this use case)
- Need to handle counter drift (periodic reconciliation)

### Caching Strategy

#### Multi-Level Caching

**Level 1: Application Cache (In-Memory)**
- Cache frequently accessed status checks
- TTL: 5 minutes
- Size: Limited to prevent memory issues

**Level 2: Redis Cache (Distributed)**
- Cache status, counts, and user favorites
- TTL: 
  - Status: 1 hour
  - Count: 5 minutes
  - User favorites: 10 minutes
- Eviction: LRU

**Level 3: Database (Persistent)**
- Source of truth
- Read replicas for scaling reads

#### Cache Invalidation

**On Favorite/Unfavorite**:
1. Invalidate status cache: `favorite:status:{user_id}:{item_id}`
2. Invalidate count cache: `favorite:count:{item_id}`
3. Invalidate user favorites cache: `favorite:user:{user_id}:*`

**Strategy**: Cache-aside (lazy loading)

### Consistency Model

#### Strong Consistency (Status Checks)
- **Requirement**: User's own favorite status must be accurate
- **Implementation**: 
  - Write-through cache
  - Read from database if cache miss
  - Invalidate cache on write

#### Eventual Consistency (Counts)
- **Requirement**: Counts can be slightly stale (acceptable)
- **Implementation**:
  - Async counter updates
  - Cache with TTL
  - Periodic reconciliation

#### Idempotency
- **Requirement**: Multiple favorite/unfavorite requests handled correctly
- **Implementation**:
  - Database unique constraint (user_id, item_id)
  - Check before write
  - Return success if already in desired state

### Scalability Considerations

#### Read Scalability
1. **Caching**: Multi-level caching (application, Redis, database)
2. **Read Replicas**: Database read replicas for scaling reads
3. **CDN**: For static count displays (if applicable)
4. **Sharding**: Distribute load across shards

#### Write Scalability
1. **Async Processing**: Counter updates via message queue
2. **Batching**: Batch counter updates
3. **Sharding**: Distribute writes across shards
4. **Connection Pooling**: Efficient database connections

#### Hot Spot Handling
1. **Celebrity Items**: 
   - Separate caching strategy
   - Pre-warming cache
   - Dedicated shards (if needed)

2. **Viral Content**:
   - Aggressive caching
   - Rate limiting
   - Auto-scaling

### Failure Handling

#### Database Failure
- **Read Failure**: 
  - Fallback to cache
  - Return cached data (may be stale)
  - Log error for monitoring

- **Write Failure**:
  - Retry with exponential backoff
  - Dead letter queue for failed writes
  - Alert for manual intervention

#### Cache Failure
- **Redis Down**:
  - Fallback to database
  - Increased latency (acceptable)
  - Auto-recovery when Redis is back

#### Message Queue Failure
- **Kafka/SQS Down**:
  - Buffer events in local queue
  - Retry when queue is back
  - Fallback to synchronous update (degraded mode)

#### Counter Drift
- **Problem**: Counts may drift due to failures
- **Solution**: 
  - Periodic reconciliation job
  - Recalculate counts from favorites table
  - Run daily/weekly

### Trade-offs and Optimizations

#### Trade-offs

1. **Consistency vs Performance**
   - **Choice**: Eventual consistency for counts
   - **Reason**: Counts don't need to be real-time
   - **Benefit**: Better performance, lower latency

2. **Cache vs Freshness**
   - **Choice**: Aggressive caching with TTL
   - **Reason**: Most reads don't need real-time data
   - **Benefit**: Reduced database load, lower latency

3. **Sync vs Async Updates**
   - **Choice**: Async counter updates
   - **Reason**: Reduces write contention
   - **Benefit**: Better write performance, scalability

#### Optimizations

1. **Batch Counter Updates**
   - Batch multiple counter updates
   - Reduces database writes
   - Improves throughput

2. **Pre-warming Cache**
   - Pre-warm cache for popular items
   - Reduces cache misses
   - Improves latency

3. **Read Replicas**
   - Distribute read load
   - Reduces primary database load
   - Improves scalability

4. **Connection Pooling**
   - Efficient database connections
   - Reduces connection overhead
   - Improves performance

## What Interviewers Look For

### Distributed Systems Skills

1. **High-Throughput Design**
   - Handling 1M+ QPS reads
   - Handling 100k+ QPS writes
   - Caching strategies
   - **Red Flags**: No caching, synchronous counter updates, single database

2. **Counter Management**
   - Async counter updates
   - Eventual consistency understanding
   - Counter drift handling
   - **Red Flags**: Synchronous counter updates, no drift handling, no async processing

3. **Caching Strategy**
   - Multi-level caching
   - Cache invalidation
   - Cache-aside pattern
   - **Red Flags**: No caching, poor invalidation, cache stampede

### Problem-Solving Approach

1. **Scale Thinking**
   - 1M QPS reads consideration
   - 100k QPS writes consideration
   - Hot spot handling
   - **Red Flags**: Designing for small scale, ignoring hot spots, no scale thinking

2. **Trade-off Analysis**
   - Consistency vs performance
   - Cache vs freshness
   - Sync vs async
   - **Red Flags**: No trade-off discussion, dogmatic choices, wrong trade-offs

3. **Edge Cases**
   - Celebrity items (hot spots)
   - Viral content
   - Counter drift
   - Idempotency
   - **Red Flags**: Ignoring edge cases, no idempotency, no drift handling

### System Design Skills

1. **Component Design**
   - Clear service boundaries
   - Proper API design
   - Data flow understanding
   - **Red Flags**: Monolithic design, unclear boundaries, poor API design

2. **Database Design**
   - Proper sharding strategy
   - Index design
   - Query optimization
   - **Red Flags**: No sharding, poor indexes, inefficient queries

3. **Failure Handling**
   - Database failure handling
   - Cache failure handling
   - Message queue failure handling
   - **Red Flags**: No failure handling, no fallbacks, no monitoring

### Communication Skills

1. **Clear Explanation**
   - Explains design decisions
   - Discusses trade-offs
   - Justifies choices
   - **Red Flags**: Unclear explanations, no justification, confusing

2. **Architecture Diagrams**
   - Clear diagrams
   - Shows data flow
   - Component relationships
   - **Red Flags**: No diagrams, unclear diagrams, missing components

### Meta-Specific Focus

1. **High-Throughput Systems**
   - Understanding of high QPS systems
   - Caching expertise
   - Async processing
   - **Key**: Demonstrate high-throughput system design

2. **Counter Management Patterns**
   - Async counter updates
   - Eventual consistency
   - Counter reconciliation
   - **Key**: Show counter management expertise

## Summary

Designing a like/unlike feature system requires careful consideration of high-throughput reads and writes, counter management, caching strategies, and data consistency. Key design decisions include:

**Architecture Highlights:**
- Separate read and write services for independent scaling
- Multi-level caching (application, Redis, database) for read optimization
- Async counter updates via message queue for write optimization
- Sharded databases for horizontal scaling

**Key Patterns:**
- **Cache-aside**: Lazy loading with cache invalidation
- **Async Processing**: Counter updates via message queue
- **Eventual Consistency**: Acceptable for counts, strong for status
- **Idempotency**: Handle duplicate requests correctly

**Scalability Solutions:**
- Read replicas for database scaling
- Redis cluster for cache scaling
- Message queue for async processing
- Sharding for database distribution

**Trade-offs:**
- Eventual consistency for counts (better performance)
- Aggressive caching (slightly stale data acceptable)
- Async counter updates (reduced contention)

This design handles 1M QPS reads and 100k QPS writes while maintaining data consistency and low latency. The system is scalable, fault-tolerant, and optimized for high-throughput operations.

