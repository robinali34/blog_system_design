---
layout: post
title: "Design a Real-Time Game Leaderboard System - System Design Interview"
date: 2025-11-13
categories: [System Design, Interview Example, Distributed Systems, Gaming]
excerpt: "A comprehensive guide to designing a real-time game leaderboard system, covering score updates, ranking algorithms, multiple leaderboard types, high write throughput, low latency reads, and scalability challenges for handling millions of concurrent players."
---

## Introduction

A real-time game leaderboard is a critical component of gaming systems that displays player rankings based on scores, achievements, or other metrics. Designing a leaderboard system requires handling high write throughput (score updates), low latency reads, real-time updates, and multiple leaderboard types (global, friends, weekly, etc.).

This post provides a detailed walkthrough of designing a real-time game leaderboard system, covering key architectural decisions, ranking algorithms, data structures, and scalability challenges. This is a common system design interview question that tests your understanding of distributed systems, caching, real-time processing, and efficient data structures for ranking.

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

**Design a real-time game leaderboard system with the following features:**

1. Players can submit scores after completing a game
2. System maintains multiple leaderboards:
   - Global leaderboard (all players)
   - Friends leaderboard (player's friends only)
   - Weekly leaderboard (resets weekly)
   - Country/Region leaderboard
3. Players can view their rank and nearby players
4. Leaderboard updates in real-time as scores are submitted
5. Support for multiple game modes/types
6. Historical leaderboard data (past weeks/months)

**Scale Requirements:**
- 100 million+ registered players
- 10 million+ daily active players
- 50 million+ score submissions per day
- 500 million+ leaderboard views per day
- Peak: 100,000 score submissions per second
- Read:Write ratio: 10:1 (500M views / 50M submissions)
- Average latency: < 50ms for reads, < 100ms for writes

## Requirements

### Functional Requirements

**Core Features:**
1. **Score Submission**: Players submit scores after game completion
2. **Ranking**: Calculate and maintain player ranks
3. **Multiple Leaderboards**: Support different leaderboard types
4. **Real-time Updates**: Leaderboard updates within seconds
5. **Rank Queries**: Get player rank, top N players, players around rank
6. **Historical Data**: Store and query past leaderboards

**Out of Scope:**
- Game logic and gameplay mechanics
- Player authentication (assume handled elsewhere)
- Payment processing
- Anti-cheat mechanisms (focus on system design)

### Non-Functional Requirements

1. **Availability**: 99.9% uptime
2. **Performance**: 
   - Score submission: < 100ms (p95)
   - Leaderboard read: < 50ms (p95)
   - Real-time update latency: < 1 second
3. **Scalability**: Handle 100K+ writes/second peak
4. **Consistency**: Eventually consistent is acceptable
5. **Durability**: All scores must be persisted
6. **Accuracy**: Rankings must be accurate (no data loss)

## Capacity Estimation

### Traffic Estimates

- **Daily Active Players (DAU)**: 10 million
- **Daily score submissions**: 50 million
- **Daily leaderboard views**: 500 million
- **Read:Write ratio**: 10:1
- **Peak writes**: 100,000 per second
- **Peak reads**: 1,000,000 per second

### Storage Estimates

**Score Records:**
- 50M submissions/day × 200 bytes = 10GB/day
- 1 year retention: 10GB × 365 = 3.65TB

**Leaderboard Data:**
- 100M players × 100 bytes (rank metadata) = 10GB
- Multiple leaderboards (4x): 40GB
- With replication (3x): 120GB

**Historical Data:**
- Weekly snapshots: 52 weeks × 40GB = 2TB
- Monthly snapshots: 12 months × 40GB = 480GB
- Total historical: ~2.5TB

**Total Storage**: ~6TB

### Bandwidth Estimates

- **Write bandwidth**: 50M submissions/day × 200 bytes = 10GB/day = 116KB/s
- **Read bandwidth**: 500M views/day × 5KB avg = 2.5TB/day = 29GB/s
- **Peak bandwidth**: 3x average = 87GB/s

## Core Entities

### Player
- **Attributes**: user_id, username, country_code, created_at, updated_at
- **Relationships**: Submits scores, has friends, participates in leaderboards

### Score
- **Attributes**: score_id, user_id, game_id, leaderboard_type, score, metadata, created_at
- **Relationships**: Belongs to player and game, contributes to leaderboard ranking

### Leaderboard
- **Attributes**: leaderboard_type, game_id, snapshot_date (for historical)
- **Relationships**: Contains scores, ranked by score value

### Friend
- **Attributes**: user_id, friend_id, created_at
- **Relationships**: Links players for friends leaderboard

## API

### 1. Submit Score
```
POST /api/v1/scores
Parameters:
  - user_id: player ID
  - game_id: game/mode ID
  - score: score value
  - leaderboard_type: "global", "weekly", "country", etc.
  - metadata: optional (level, time, etc.)
Response:
  - success: boolean
  - rank: new rank
  - previous_rank: previous rank (if applicable)
```

### 2. Get Leaderboard
```
GET /api/v1/leaderboard/{type}
Parameters:
  - type: "global", "friends", "weekly", "country"
  - limit: number of players to return (default: 100)
  - offset: pagination offset (optional)
Response:
  - players: array of player objects (rank, user_id, score)
  - total_players: total number of players
```

### 3. Get Player Rank
```
GET /api/v1/leaderboard/{type}/rank/{user_id}
Parameters:
  - type: leaderboard type
  - user_id: player ID
Response:
  - rank: player rank
  - score: player score
  - total_players: total players in leaderboard
```

### 4. Get Players Around Rank
```
GET /api/v1/leaderboard/{type}/around/{user_id}
Parameters:
  - type: leaderboard type
  - user_id: player ID
  - range: number of players above/below (default: 5)
Response:
  - players: array of players around the specified player
  - player_rank: rank of the specified player
```

### 5. Get Historical Leaderboard
```
GET /api/v1/leaderboard/{type}/historical/{date}
Parameters:
  - type: leaderboard type
  - date: date in YYYY-MM-DD format
Response:
  - players: array of players from historical leaderboard
  - date: leaderboard date
```

## Data Flow

### Score Submission Flow
1. Player submits score → Load Balancer
2. Load Balancer → API Gateway
3. API Gateway → Score Service
4. Score Service validates score
5. Score Service → Database (store score)
6. Score Service → Message Queue (for async ranking)
7. Message Queue → Ranking Engine (calculate rank)
8. Ranking Engine → Redis (update leaderboard)
9. Ranking Engine → Cache invalidation
10. Response returned to client (with new rank)

### Leaderboard Query Flow
1. Client requests leaderboard → Load Balancer
2. Load Balancer → API Gateway
3. API Gateway → Leaderboard Service
4. Leaderboard Service checks Redis cache
5. If cache miss:
   - Query Redis Sorted Set for leaderboard
   - If not in Redis, query Database
   - Cache result in Redis
6. Return leaderboard to client

### Rank Update Flow
1. Score update triggers ranking recalculation
2. Ranking Engine calculates new rank
3. Ranking Engine updates Redis Sorted Set
4. Ranking Engine → Message Queue (for real-time updates)
5. Message Queue → Real-time Service
6. Real-time Service pushes update to active clients via WebSocket

## Database Design

### Schema Design

**Players Table:**
```sql
CREATE TABLE players (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    country_code VARCHAR(2),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    INDEX idx_country (country_code)
);
```

**Scores Table:**
```sql
CREATE TABLE scores (
    score_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    game_id INT NOT NULL,
    leaderboard_type VARCHAR(50) NOT NULL,
    score INT NOT NULL,
    metadata JSON,
    created_at TIMESTAMP,
    INDEX idx_user_game (user_id, game_id),
    INDEX idx_type_score (leaderboard_type, score DESC),
    INDEX idx_created (created_at),
    FOREIGN KEY (user_id) REFERENCES players(user_id)
);
```

**Leaderboard Snapshots Table:**
```sql
CREATE TABLE leaderboard_snapshots (
    snapshot_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    leaderboard_type VARCHAR(50) NOT NULL,
    snapshot_date DATE NOT NULL,
    snapshot_data JSON NOT NULL,
    created_at TIMESTAMP,
    UNIQUE KEY unique_snapshot (leaderboard_type, snapshot_date),
    INDEX idx_type_date (leaderboard_type, snapshot_date)
);
```

**Friends Table:**
```sql
CREATE TABLE friends (
    user_id BIGINT NOT NULL,
    friend_id BIGINT NOT NULL,
    created_at TIMESTAMP,
    PRIMARY KEY (user_id, friend_id),
    INDEX idx_user (user_id),
    INDEX idx_friend (friend_id),
    FOREIGN KEY (user_id) REFERENCES players(user_id),
    FOREIGN KEY (friend_id) REFERENCES players(user_id)
);
```

### Database Sharding Strategy

**Shard by User ID:**
- Player data, scores, friends on same shard
- Enables efficient player queries

**Challenges:**
- Global leaderboard requires aggregation across shards
- Need efficient cross-shard queries

## High-Level Design

```
┌─────────────┐
│   Client    │
│  (Game)     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│         Load Balancer                   │
└──────┬──────────────────┬───────────────┘
       │                  │
       ▼                  ▼
┌──────────────┐   ┌──────────────┐
│ Score        │   │ Leaderboard │
│ Service      │   │ Service     │
└──────┬───────┘   └──────┬───────┘
       │                  │
       ├──────────────────┼──────────────────┐
       │                  │                  │
       ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Ranking      │  │ Cache        │  │ Database     │
│ Engine       │  │ (Redis)       │  │ (Sharded)    │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Deep Dive

### Component Design

#### 1. Score Service

**Responsibilities:**
- Receive score submissions
- Validate scores
- Store scores in database
- Trigger ranking updates

**Flow:**
1. Receive score submission
2. Validate score (anti-cheat checks, etc.)
3. Store score in database
4. Publish to message queue for ranking
5. Return acknowledgment

**Optimizations:**
- Batch writes for high throughput
- Async processing for ranking
- Rate limiting per user

#### 2. Ranking Engine

**Responsibilities:**
- Calculate and maintain rankings
- Update leaderboard caches
- Handle tie-breaking logic

**Data Structures:**

**Option 1: Redis Sorted Sets (Recommended)**
```
Key: leaderboard:{type}:{game_id}
Type: Sorted Set
Score: score value
Value: user_id
```

**Advantages:**
- O(log N) insertion and update
- O(log N + M) range queries (top N)
- Built-in ranking operations
- Atomic operations

**Operations:**
- `ZADD`: Add/update score
- `ZREVRANGE`: Get top N players
- `ZREVRANK`: Get player rank
- `ZREVRANGEBYSCORE`: Get players around rank

**Option 2: Database with Materialized View**
- Pre-computed rankings
- Slower updates but faster reads
- Good for less frequent updates

**Ranking Algorithm:**

**Tie-breaking Logic:**
1. Higher score wins
2. If scores equal, earlier submission wins (timestamp)
3. If still equal, lower user_id wins (deterministic)

**Score Calculation:**
```
final_score = base_score + bonus_points - penalty_points
```

#### 3. Leaderboard Service

**Responsibilities:**
- Serve leaderboard queries
- Handle pagination
- Cache frequently accessed data

**Query Patterns:**

**Get Top N Players:**
```
ZREVRANGE leaderboard:global:1 0 99 WITHSCORES
```

**Get Player Rank:**
```
ZREVRANK leaderboard:global:1 {user_id}
ZSCORE leaderboard:global:1 {user_id}
```

**Get Players Around Rank:**
```
rank = ZREVRANK leaderboard:global:1 {user_id}
ZREVRANGE leaderboard:global:1 rank-5 rank+5 WITHSCORES
```

**Caching Strategy:**
- Cache top 1000 players for each leaderboard
- TTL: 1 second (very short for real-time)
- Invalidate on score updates

#### 4. Real-time Update Service

**Requirements:**
- Push leaderboard updates to clients
- Notify players of rank changes

**Implementation:**

**Option 1: WebSockets**
- Maintain persistent connections
- Push updates immediately
- Higher server load

**Option 2: Server-Sent Events (SSE)**
- One-way push from server
- Simpler than WebSockets
- Good for leaderboard updates

**Option 3: Polling**
- Client polls every few seconds
- Simple but less efficient

**Recommended: Hybrid**
- WebSockets for active players (top 1000)
- Polling for others
- Use message queue (Kafka) to distribute updates

**Flow:**
1. Score update triggers ranking recalculation
2. Publish update event to Kafka
3. Real-time service consumes and pushes to clients
4. Clients receive updated leaderboard

#### 5. Historical Leaderboard Service

**Responsibilities:**
- Store leaderboard snapshots
- Serve historical queries

**Snapshot Strategy:**
- Daily snapshots at midnight UTC
- Weekly snapshots for weekly leaderboards
- Monthly snapshots for long-term storage

**Storage:**
- Store top 10,000 players per snapshot
- Compress old snapshots
- Archive to cold storage after 1 year

### Detailed Design

### Data Structure: Redis Sorted Sets

**Why Redis Sorted Sets?**
- Efficient ranking operations
- O(log N) complexity for inserts/updates
- Built-in range queries
- Atomic operations
- High performance

**Key Operations:**

**Add/Update Score:**
```redis
ZADD leaderboard:global:1 {score} {user_id}
```

**Get Top N:**
```redis
ZREVRANGE leaderboard:global:1 0 99 WITHSCORES
```

**Get Rank:**
```redis
ZREVRANK leaderboard:global:1 {user_id}
ZSCORE leaderboard:global:1 {user_id}
```

**Get Range Around Rank:**
```redis
ZREVRANGE leaderboard:global:1 {start} {end} WITHSCORES
```

**Remove Player:**
```redis
ZREM leaderboard:global:1 {user_id}
```

### Leaderboard Types

**1. Global Leaderboard**
- All players across all games
- Key: `leaderboard:global:{game_id}`
- Most frequently accessed

**2. Friends Leaderboard**
- Filtered by player's friends
- Key: `leaderboard:friends:{user_id}:{game_id}`
- Requires friend list lookup

**3. Weekly Leaderboard**
- Resets every week
- Key: `leaderboard:weekly:{week_number}:{game_id}`
- Archive at end of week

**4. Country Leaderboard**
- Filtered by country
- Key: `leaderboard:country:{country_code}:{game_id}`
- Pre-filtered by country

**5. Custom Leaderboards**
- Time-based (daily, monthly)
- Event-based (tournaments)
- Group-based (clans, teams)

### Handling High Write Throughput

**Challenge:** 100K writes/second

**Solutions:**

**1. Write Batching**
- Batch score submissions
- Process in batches of 100-1000
- Reduce Redis operations

**2. Write Buffer**
- Buffer writes in memory
- Flush periodically
- Handle backpressure

**3. Sharding Leaderboards**
- Shard by game_id or user_id hash
- Distribute load across Redis instances
- Use consistent hashing

**4. Async Processing**
- Accept writes immediately
- Process ranking asynchronously
- Eventual consistency acceptable

**5. Redis Cluster**
- Horizontal scaling
- Shard data across nodes
- High availability

### Handling Tie-breaking

**Problem:** Multiple players with same score

**Solution:**
- Use composite score: `{score}.{timestamp}.{user_id}`
- Convert to decimal: `score + (1 / (timestamp + 1)) + (1 / (user_id + 1))`
- Ensures deterministic ordering

**Example:**
```
Player A: score=1000, timestamp=1234567890, user_id=123
Player B: score=1000, timestamp=1234567891, user_id=456

Composite A: 1000.0000000008103715 (earlier timestamp wins)
Composite B: 1000.0000000008103714
```

### Caching Strategy

**Multi-level Caching:**

**L1: Application Cache (In-memory)**
- Top 100 players per leaderboard
- TTL: 100ms
- Very fast access

**L2: Redis Cache**
- Full leaderboard data
- TTL: 1 second
- Fast updates

**L3: Database**
- Persistent storage
- Historical data
- Backup for cache

**Cache Invalidation:**
- Invalidate on score updates
- Use pub/sub for cache invalidation
- Lazy invalidation for non-critical updates

### Message Queue Architecture

**Use Cases:**
1. **Score Processing**: Async score processing
2. **Ranking Updates**: Trigger ranking recalculation
3. **Real-time Updates**: Push updates to clients
4. **Historical Snapshots**: Schedule snapshot creation

**Technology**: Apache Kafka

**Topics:**
- `scores.submitted`: New score submissions
- `leaderboard.updated`: Leaderboard update events
- `rank.changed`: Player rank change events
- `snapshot.created`: Historical snapshot events

## Scalability Considerations

### Horizontal Scaling

**Stateless Services:**
- Score Service, Leaderboard Service
- Scale based on load
- Use load balancer

**Stateful Services:**
- Redis cluster for caching
- Database sharding
- Message queue partitioning

### Redis Scaling

**Redis Cluster:**
- Shard data across nodes
- Automatic failover
- High availability

**Redis Sentinel:**
- Master-slave replication
- Automatic failover
- Read scaling

**Sharding Strategy:**
- Shard by leaderboard type
- Shard by game_id
- Use consistent hashing

### Database Scaling

**Sharding:**
- Shard by user_id
- Shard by game_id
- Cross-shard queries for global leaderboard

**Read Replicas:**
- Scale reads
- Geographic distribution
- Eventual consistency

### Handling Hot Leaderboards

**Problem:** Popular games have very high traffic

**Solutions:**
1. **Dedicated Infrastructure**: Separate Redis instances
2. **Aggressive Caching**: Cache top players longer
3. **Rate Limiting**: Limit queries per user
4. **CDN**: Cache static leaderboard pages

### Security Considerations

1. **Score Validation**: Prevent cheating
   - Server-side validation
   - Rate limiting
   - Anomaly detection

2. **Authentication**: Verify player identity
   - JWT tokens
   - API keys

3. **Rate Limiting**: Prevent abuse
   - Limit score submissions per user
   - Limit leaderboard queries

4. **Data Privacy**: Protect player data
   - Encrypt sensitive data
   - GDPR compliance

5. **Anti-cheat**: Detect and prevent cheating
   - Score validation
   - Pattern detection
   - Manual review

### Monitoring & Observability

**Key Metrics:**
- Score submission rate
- Leaderboard query latency (p50, p95, p99)
- Cache hit rates
- Redis operations per second
- Error rates
- Rank update latency

**Alerts:**
- High latency (> 100ms)
- High error rate (> 1%)
- Redis memory usage
- Database connection pool exhaustion

**Tools:**
- Prometheus + Grafana for metrics
- ELK stack for logging
- Distributed tracing (Jaeger/Zipkin)

### Trade-offs and Optimizations

### Trade-offs

1. **Consistency vs Availability**
   - Choose eventual consistency
   - Acceptable delay for rank updates

2. **Latency vs Accuracy**
   - Cache for low latency
   - Periodic recalculation for accuracy
   - Balance both

3. **Storage vs Compute**
   - Pre-compute rankings (more storage)
   - Compute on-demand (less storage)
   - Hybrid approach

### Optimizations

1. **Score Batching**
   - Batch multiple scores
   - Reduce Redis operations
   - Improve throughput

2. **Lazy Ranking**
   - Update rankings asynchronously
   - Accept slight delay
   - Better write performance

3. **Selective Updates**
   - Only update affected ranks
   - Skip updates for players far from top
   - Reduce computation

4. **Compression**
   - Compress historical data
   - Reduce storage costs
   - Faster retrieval

## What Interviewers Look For

### Data Structure Skills

1. **Sorted Set Usage**
   - Redis Sorted Sets
   - O(log N) operations
   - Efficient ranking
   - **Red Flags**: Inefficient data structure, O(N) operations, poor performance

2. **Ranking Algorithm**
   - Accurate ranking
   - Tie-breaking logic
   - Composite scores
   - **Red Flags**: Incorrect ranking, no tie-breaking, simple scores only

3. **Score Updates**
   - Atomic updates
   - Efficient operations
   - **Red Flags**: Non-atomic, inefficient, race conditions

### Real-Time Systems Skills

1. **Low Latency Reads**
   - < 50ms query latency
   - Multi-level caching
   - **Red Flags**: High latency, no caching, slow queries

2. **High Write Throughput**
   - 100K+ writes/second
   - Async processing
   - **Red Flags**: Synchronous processing, low throughput, bottlenecks

3. **Real-Time Updates**
   - Updates within seconds
   - Efficient propagation
   - **Red Flags**: Delayed updates, no real-time, polling

### Problem-Solving Approach

1. **Multiple Leaderboard Types**
   - Global, friends, weekly
   - Efficient filtering
   - **Red Flags**: Single type, inefficient filtering, no variety

2. **Edge Cases**
   - Concurrent score updates
   - Large player base
   - Tie situations
   - **Red Flags**: Ignoring edge cases, no handling

3. **Trade-off Analysis**
   - Latency vs accuracy
   - Consistency vs performance
   - **Red Flags**: No trade-offs, dogmatic choices

### System Design Skills

1. **Component Design**
   - Ranking service
   - Query service
   - Update service
   - **Red Flags**: Monolithic, unclear boundaries

2. **Sharding Strategy**
   - Horizontal scaling
   - Efficient distribution
   - **Red Flags**: No sharding, vertical scaling, bottlenecks

3. **Caching Strategy**
   - Multi-level caching
   - Cache invalidation
   - **Red Flags**: No caching, poor strategy, stale data

### Communication Skills

1. **Data Structure Explanation**
   - Can explain sorted sets
   - Understands complexity
   - **Red Flags**: No understanding, vague

2. **Algorithm Explanation**
   - Can explain ranking algorithm
   - Understands tie-breaking
   - **Red Flags**: No understanding, vague

### Meta-Specific Focus

1. **Data Structures Expertise**
   - Deep understanding of sorted sets
   - Algorithm knowledge
   - **Key**: Show data structures expertise

2. **Performance Optimization**
   - Low latency design
   - High throughput
   - **Key**: Demonstrate performance focus

## Summary

Designing a real-time game leaderboard system requires handling:

1. **High Write Throughput**: 100K+ writes/second
2. **Low Latency Reads**: < 50ms for queries
3. **Real-time Updates**: Updates within seconds
4. **Multiple Leaderboard Types**: Global, friends, weekly, etc.
5. **Ranking Accuracy**: Accurate and consistent rankings

**Key Architectural Decisions:**
- **Redis Sorted Sets**: Efficient ranking data structure
- **Async Processing**: Handle high write throughput
- **Multi-level Caching**: Low latency reads
- **Message Queue**: Decouple components
- **Sharding**: Scale horizontally
- **Composite Scores**: Handle tie-breaking

**Data Structure Choice:**
- **Redis Sorted Sets**: O(log N) operations, built-in ranking
- Perfect for leaderboard use case
- High performance and scalability

**Leaderboard Types:**
- Global: All players
- Friends: Filtered by friend list
- Weekly: Time-based with reset
- Country: Geographic filtering
- Custom: Event-based, group-based

This design can handle the scale of major gaming platforms while maintaining low latency and high availability for real-time leaderboard updates.

