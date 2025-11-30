---
layout: post
title: "Design a Matchmaking Service for Multiplayer Games - System Design Interview"
date: 2025-11-29
categories: [System Design, Interview Example, Distributed Systems, Gaming, Real-time Systems, High-Throughput Systems]
excerpt: "A comprehensive guide to designing a matchmaking service for multiplayer games that handles skill-based matching, team formation, server allocation, and real-time coordination at scale. Covers queue partitioning, atomic reservations, multi-step workflows, and fairness vs wait time trade-offs."
---

## Introduction

Designing a matchmaking service for multiplayer games is a complex distributed systems problem that tests your ability to build high-throughput, low-latency coordination systems under contention. The service orchestrates player queues, skill-based team formation, atomic player reservations, and game server allocation to create fair, balanced matches.

This post provides a detailed walkthrough of designing a matchmaking service, covering key architectural decisions, queue partitioning, skill-based matching algorithms, atomic reservation patterns, server allocation strategies, and real-time coordination. This is a common system design interview question that tests your understanding of distributed systems, real-time systems, queue management, and coordination patterns.

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
   - [Queue Management](#queue-management)
   - [Skill-Based Matching](#skill-based-matching)
   - [Atomic Reservation](#atomic-reservation)
   - [Server Allocation](#server-allocation)
   - [Real-Time Updates](#real-time-updates)
   - [Fairness vs Wait Time](#fairness-vs-wait-time)
   - [Failure Handling](#failure-handling)
   - [Backpressure and Capacity](#backpressure-and-capacity)
   - [Trade-offs and Optimizations](#trade-offs-and-optimizations)
10. [What Interviewers Look For](#what-interviewers-look-for)
11. [Summary](#summary)

## Problem Statement

**Design a matchmaking service for multiplayer games that:**

1. Allows players to join waiting queues by game mode, region, and skill level
2. Groups players by skill level into teams of 16
3. Allocates new game servers for each match
4. Ensures all 16 players load into the server simultaneously
5. Handles high-throughput, low-latency operations
6. Maintains fairness while minimizing wait times

**Scale Requirements:**
- 1M+ concurrent players in queues
- 100k+ matchmaking operations per minute
- < 100ms latency for queue operations
- < 5 seconds for match formation
- Support multiple games, regions, and skill brackets
- Handle server capacity constraints

**Key Challenges:**
- Partition hot queues to avoid global locks
- Atomic multi-step workflows (queue → reserve → allocate)
- Balance fairness vs wait time
- Real-time updates at scale
- Handle failures gracefully
- Manage capacity and backpressure

## Requirements

### Functional Requirements

**Core Features:**
1. **Join Queue**: Player joins queue for specific game/region/skill bracket
2. **Leave Queue**: Player can leave queue before match is found
3. **Skill-Based Matching**: Match players with similar skill levels
4. **Team Formation**: Form teams of 16 players
5. **Server Allocation**: Allocate fresh game server for each match
6. **Atomic Reservation**: Reserve all 16 players atomically
7. **Real-Time Updates**: Notify players of queue status and match found
8. **Match Confirmation**: Confirm all players loaded into server

**Matchmaking Rules:**
- Team size: 16 players per match
- Skill matching: ±100 MMR (Matchmaking Rating) initially, expands over time
- Wait time limits: Max 5 minutes, then expand skill range
- Region matching: Match players in same region (low latency)
- Game mode: Separate queues for different game modes

**Out of Scope:**
- In-game features (gameplay, scoring, etc.)
- Player progression/ranking updates
- Spectator mode
- Replay system
- Anti-cheat systems

### Non-Functional Requirements

1. **Availability**: 99.9% uptime
2. **Reliability**: No player loss, all matches must be created successfully
3. **Performance**: 
   - Join queue: < 100ms (P95)
   - Leave queue: < 100ms (P95)
   - Match formation: < 5 seconds (P95)
   - Server allocation: < 2 seconds (P95)
4. **Scalability**: Handle 1M+ concurrent players, 100k+ matches/minute
5. **Consistency**: 
   - Strong consistency for player reservations (atomic)
   - Eventual consistency acceptable for queue statistics
6. **Latency**: Low latency for real-time updates (< 50ms)
7. **Fairness**: Balanced skill-based matching
8. **Wait Time**: Minimize average wait time while maintaining fairness

## Capacity Estimation

### Traffic Estimates

- **Concurrent Players in Queue**: 1M players
- **Join Queue Rate**: 200k QPS (players joining)
- **Leave Queue Rate**: 50k QPS (players leaving)
- **Match Formation Rate**: 10k matches/minute = 167 matches/second
- **Players Matched**: 167 matches/sec × 16 players = 2,672 players/second
- **Server Allocation**: 167 allocations/second
- **Real-Time Updates**: 500k QPS (queue status, match notifications)

### Storage Estimates

**Queue State:**
- 1M players in queue
- Average record size: 128 bytes (player_id, skill, region, timestamp)
- Queue storage: 1M × 128 bytes = 128MB (in-memory)

**Match Records:**
- 10k matches/minute × 60 × 24 = 14.4M matches/day
- Average record size: 256 bytes (match_id, players, server, timestamp)
- Daily storage: 14.4M × 256 bytes = 3.7GB/day
- 1 year retention: 3.7GB × 365 = 1.35TB

**Server Capacity:**
- Track available servers per region
- 1000 servers × 8 bytes = 8KB (in-memory)

**Total Storage**: ~1.35TB per year (mostly match history)

## Core Entities

### Player
- **Attributes**: player_id, skill_rating (MMR), region, game_mode, status, queue_join_time
- **Status**: IDLE, IN_QUEUE, RESERVED, IN_GAME
- **Relationships**: Can be in one queue, can be reserved for one match

### Queue
- **Attributes**: queue_id, game_mode, region, skill_bracket_min, skill_bracket_max, players
- **Relationships**: Contains multiple players, partitioned by game/region/skill
- **Purpose**: Organize players waiting for matches

### Match
- **Attributes**: match_id, game_mode, region, players (16), server_id, status, created_at
- **Status**: FORMING, RESERVED, ALLOCATING, READY, ACTIVE, COMPLETED
- **Relationships**: Links 16 players, assigned to one server

### GameServer
- **Attributes**: server_id, region, capacity, current_players, status, allocated_at
- **Status**: AVAILABLE, ALLOCATING, ACTIVE, FULL, MAINTENANCE
- **Relationships**: Can host one match at a time

### Reservation
- **Attributes**: reservation_id, match_id, player_id, status, expires_at
- **Status**: PENDING, CONFIRMED, EXPIRED, CANCELLED
- **Purpose**: Atomic reservation of players for match

## API

### 1. Join Queue
```
POST /api/v1/matchmaking/queue/join
Headers:
  - Authorization: Bearer <token>
Body:
  - game_mode: string (e.g., "battle_royale", "team_deathmatch")
  - region: string (e.g., "us-east", "eu-west")
  - skill_rating: integer (optional, from player profile)
Response:
  - queue_id: string
  - estimated_wait_time: integer (seconds)
  - position_in_queue: integer
  - websocket_url: string (for real-time updates)
```

### 2. Leave Queue
```
DELETE /api/v1/matchmaking/queue/{queue_id}/leave
Headers:
  - Authorization: Bearer <token>
Response:
  - success: boolean
```

### 3. Get Queue Status
```
GET /api/v1/matchmaking/queue/{queue_id}/status
Headers:
  - Authorization: Bearer <token>
Response:
  - players_in_queue: integer
  - estimated_wait_time: integer (seconds)
  - skill_bracket: object (min, max)
```

### 4. Match Found (WebSocket/SSE)
```
WebSocket: wss://matchmaking.example.com/queue/{queue_id}
Events:
  - queue_update: { players_in_queue, estimated_wait_time }
  - match_found: { match_id, server_info, players, load_time }
  - reservation_expired: { reason }
```

### 5. Confirm Match (Internal/Player)
```
POST /api/v1/matchmaking/match/{match_id}/confirm
Headers:
  - Authorization: Bearer <token>
Body:
  - player_id: string
Response:
  - server_connection_info: object
  - load_deadline: timestamp
```

### 6. Server Allocation (Internal)
```
POST /api/v1/matchmaking/servers/allocate
Body:
  - match_id: string
  - region: string
  - game_mode: string
Response:
  - server_id: string
  - server_endpoint: string
  - connection_token: string
```

## Data Flow

### Join Queue Flow

```
1. Player → API Gateway
2. API Gateway → Auth Service (validate token)
3. API Gateway → Matchmaking Service
4. Matchmaking Service:
   a. Get player skill rating (from cache/DB)
   b. Determine skill bracket
   c. Select queue partition (game/region/skill)
   d. Add player to queue (Redis sorted set)
   e. Update queue statistics
   f. Establish WebSocket connection for updates
   g. Return queue info
```

### Matchmaking Flow (Background Process)

```
1. Matchmaking Service (Background Worker):
   a. Scan queues for ready matches
   b. For each queue partition:
      - Find players in skill bracket
      - Group 16 players (skill-based algorithm)
      - Create match record
      - Atomically reserve all 16 players
      - If reservation succeeds:
         - Allocate game server
         - Notify all players via WebSocket
         - Set reservation expiry (30 seconds)
      - If reservation fails:
         - Release reserved players
         - Retry with next group
```

### Atomic Reservation Flow

```
1. Matchmaking Service:
   a. Start transaction/distributed lock
   b. Check all 16 players still in queue
   c. Update all players to RESERVED status
   d. Create reservation records
   e. Create match record
   f. Commit transaction
   g. If any step fails, rollback and retry
```

### Server Allocation Flow

```
1. Matchmaking Service → Server Manager:
   a. Request server for region/game_mode
   b. Server Manager:
      - Find available server in region
      - Mark server as ALLOCATING
      - Return server info
   c. Matchmaking Service:
      - Update match with server_id
      - Notify players with server connection info
```

### Player Confirmation Flow

```
1. Player → Matchmaking Service:
   a. Confirm match acceptance
   b. Matchmaking Service:
      - Mark player as confirmed
      - Track confirmation count
      - When all 16 confirmed:
         - Mark match as READY
         - Notify game server to start
         - Set match start time
      - If timeout (30s) and not all confirmed:
         - Cancel match
         - Release server
         - Return players to queue
```

## Database Design

### Schema Design

#### Players Table
```sql
CREATE TABLE players (
    player_id BIGINT PRIMARY KEY,
    skill_rating INT NOT NULL,
    region VARCHAR(50) NOT NULL,
    current_status ENUM('IDLE', 'IN_QUEUE', 'RESERVED', 'IN_GAME') DEFAULT 'IDLE',
    current_queue_id VARCHAR(100),
    current_match_id VARCHAR(100),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status_queue (current_status, current_queue_id),
    INDEX idx_skill_region (skill_rating, region)
) ENGINE=InnoDB;

-- Sharded by player_id
```

#### Queues Table (Metadata)
```sql
CREATE TABLE queue_metadata (
    queue_id VARCHAR(100) PRIMARY KEY,
    game_mode VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,
    skill_bracket_min INT NOT NULL,
    skill_bracket_max INT NOT NULL,
    player_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_game_region (game_mode, region)
) ENGINE=InnoDB;

-- Not sharded (small table)
```

#### Matches Table
```sql
CREATE TABLE matches (
    match_id VARCHAR(100) PRIMARY KEY,
    game_mode VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,
    server_id VARCHAR(100),
    status ENUM('FORMING', 'RESERVED', 'ALLOCATING', 'READY', 'ACTIVE', 'COMPLETED', 'CANCELLED') DEFAULT 'FORMING',
    players JSON NOT NULL, -- Array of 16 player IDs
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reserved_at TIMESTAMP,
    ready_at TIMESTAMP,
    started_at TIMESTAMP,
    INDEX idx_status_created (status, created_at),
    INDEX idx_server (server_id)
) ENGINE=InnoDB;

-- Sharded by match_id
```

#### Reservations Table
```sql
CREATE TABLE reservations (
    reservation_id VARCHAR(100) PRIMARY KEY,
    match_id VARCHAR(100) NOT NULL,
    player_id BIGINT NOT NULL,
    status ENUM('PENDING', 'CONFIRMED', 'EXPIRED', 'CANCELLED') DEFAULT 'PENDING',
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_match (match_id),
    INDEX idx_player (player_id),
    INDEX idx_expires (expires_at)
) ENGINE=InnoDB;

-- Sharded by match_id
```

#### GameServers Table
```sql
CREATE TABLE game_servers (
    server_id VARCHAR(100) PRIMARY KEY,
    region VARCHAR(50) NOT NULL,
    game_mode VARCHAR(50) NOT NULL,
    status ENUM('AVAILABLE', 'ALLOCATING', 'ACTIVE', 'FULL', 'MAINTENANCE') DEFAULT 'AVAILABLE',
    current_match_id VARCHAR(100),
    capacity INT DEFAULT 16,
    current_players INT DEFAULT 0,
    allocated_at TIMESTAMP,
    INDEX idx_region_status (region, status),
    INDEX idx_match (current_match_id)
) ENGINE=InnoDB;

-- Not sharded (relatively small)
```

### Database Sharding Strategy

**Players Table:**
- **Shard Key**: `player_id`
- **Sharding Strategy**: Hash-based sharding
- **Number of Shards**: 100 shards
- **Reasoning**: Player lookups are by player_id

**Matches Table:**
- **Shard Key**: `match_id`
- **Sharding Strategy**: Hash-based sharding
- **Number of Shards**: 100 shards
- **Reasoning**: Match operations are by match_id

**Reservations Table:**
- **Shard Key**: `match_id` (same as matches)
- **Sharding Strategy**: Hash-based sharding (aligned with matches)
- **Number of Shards**: 100 shards
- **Reasoning**: Reservations are always accessed with match_id

## High-Level Design

```
┌─────────────────────────────────────────────────────────┐
│                    Game Clients                          │
│              (Players on various platforms)              │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTPS / WebSocket
                     │
┌────────────────────▼────────────────────────────────────┐
│                  API Gateway / LB                        │
│              (Rate Limiting, Auth)                       │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
┌────────▼────────┐    ┌─────────▼─────────┐
│  Queue Service  │    │ Matchmaking Service│
│  (Join/Leave)   │    │  (Match Formation) │
└────────┬────────┘    └─────────┬──────────┘
         │                       │
         │                       │
┌────────▼───────────────────────▼──────────┐
│         Redis Cluster                     │
│  (Queue State, Player Status, Locks)      │
└────────┬──────────────────────────────────┘
         │
         │
┌────────▼──────────────────────────────────┐
│         Database Cluster                  │
│  (Players, Matches, Reservations, Servers)│
└────────┬──────────────────────────────────┘
         │
         │
┌────────▼──────────────────────────────────┐
│      Server Manager Service                │
│  (Game Server Allocation & Management)      │
└────────┬──────────────────────────────────┘
         │
         │
┌────────▼──────────────────────────────────┐
│      Game Server Pool                     │
│  (Available Game Servers by Region)       │
└───────────────────────────────────────────┘

┌───────────────────────────────────────────┐
│      WebSocket Service                    │
│  (Real-Time Updates to Players)           │
└───────────────────────────────────────────┘
```

## Deep Dive

### Component Design

#### 1. Queue Service
- **Responsibilities**: Handle join/leave queue operations
- **Optimization**: 
  - Redis sorted sets for O(log N) operations
  - Partition queues by game/region/skill to avoid global locks
  - In-memory queue state for fast access

#### 2. Matchmaking Service
- **Responsibilities**: Form matches, skill-based grouping, atomic reservations
- **Optimization**:
  - Background workers scanning queues
  - Skill-based matching algorithm
  - Atomic reservation using distributed locks

#### 3. Server Manager Service
- **Responsibilities**: Allocate and manage game servers
- **Optimization**:
  - Server pool per region
  - Fast server allocation
  - Server health monitoring

#### 4. WebSocket Service
- **Responsibilities**: Real-time updates to players
- **Optimization**:
  - Connection pooling
  - Message batching
  - Efficient routing

#### 5. Redis Cluster
- **Queue State**: Sorted sets for each queue partition
- **Player Status**: Hash maps for fast lookups
- **Distributed Locks**: For atomic operations
- **Cache**: Player skill ratings, queue statistics

### Queue Management

#### Queue Partitioning

**Challenge**: Global queue creates contention and locks.

**Solution**: Partition queues by game/region/skill bracket.

**Partitioning Strategy:**
```
Queue Key: queue:{game_mode}:{region}:{skill_bracket}
Example: queue:battle_royale:us-east:1500-1600

Skill Brackets:
- 0-500, 500-1000, 1000-1500, 1500-2000, 2000-2500, 2500+
- Each bracket is 500 MMR wide
- Can expand brackets over time (wait time > 2 minutes)
```

**Benefits:**
- No global locks (each partition independent)
- Parallel processing (multiple workers per partition)
- Better skill matching (narrower brackets)
- Scalability (add partitions as needed)

#### Queue Data Structure (Redis)

**Sorted Set for Queue:**
```python
# Redis Sorted Set
# Key: queue:{game_mode}:{region}:{skill_bracket}
# Score: join_timestamp (for FIFO within skill bracket)
# Member: player_id

# Add player to queue
ZADD queue:battle_royale:us-east:1500-1600 <timestamp> <player_id>

# Get players in skill range, ordered by join time
ZRANGEBYSCORE queue:battle_royale:us-east:1500-1600 <min_time> <max_time> WITHSCORES

# Remove player from queue
ZREM queue:battle_royale:us-east:1500-1600 <player_id>

# Get queue size
ZCARD queue:battle_royale:us-east:1500-1600
```

**Player Status Hash:**
```python
# Redis Hash
# Key: player:{player_id}
# Fields: status, queue_id, match_id, skill_rating

HSET player:12345 status IN_QUEUE queue_id queue:battle_royale:us-east:1500-1600
```

### Skill-Based Matching

#### Matching Algorithm

**Goal**: Match 16 players with similar skill levels while minimizing wait time.

**Algorithm:**
1. **Initial Match**: ±100 MMR range
2. **Expansion**: Expand range by 50 MMR every 30 seconds
3. **Maximum Range**: ±500 MMR (after 5 minutes)
4. **Priority**: FIFO within skill bracket (fairness)

**Implementation:**
```python
def find_match(queue_key, min_players=16):
    # Get players in current skill bracket
    players = redis.zrange(queue_key, 0, min_players - 1, withscores=True)
    
    if len(players) < min_players:
        # Expand skill bracket
        expanded_players = expand_skill_bracket(queue_key, min_players)
        if len(expanded_players) >= min_players:
            players = expanded_players[:min_players]
        else:
            return None
    
    # Calculate average skill
    avg_skill = sum(p.skill for p in players) / len(players)
    
    # Check skill variance (max ±200 from average)
    if all(abs(p.skill - avg_skill) <= 200 for p in players):
        return players
    
    return None

def expand_skill_bracket(queue_key, min_players):
    # Get adjacent skill brackets
    # Query multiple brackets and combine
    # Sort by join time (FIFO)
    pass
```

**Fairness Considerations:**
- FIFO within skill bracket (first come, first served)
- Skill expansion over time (prevents indefinite waiting)
- Maximum wait time (5 minutes, then any match)

### Atomic Reservation

#### Challenge
Reserving 16 players atomically without race conditions.

#### Solution: Distributed Lock + Transaction

**Approach 1: Redis Distributed Lock**
```python
def reserve_players_for_match(player_ids, match_id):
    # Acquire distributed lock
    lock_key = f"match_lock:{match_id}"
    lock = acquire_lock(lock_key, timeout=5)
    
    try:
        # Check all players still available
        available = check_players_available(player_ids)
        if not available:
            return False
        
        # Update all players to RESERVED
        pipeline = redis.pipeline()
        for player_id in player_ids:
            pipeline.hset(f"player:{player_id}", "status", "RESERVED")
            pipeline.hset(f"player:{player_id}", "match_id", match_id)
        pipeline.execute()
        
        # Create reservation records
        create_reservations(match_id, player_ids)
        
        return True
    finally:
        release_lock(lock_key)
```

**Approach 2: Database Transaction**
```python
def reserve_players_for_match(player_ids, match_id):
    with db.transaction():
        # Check all players available
        players = db.query("SELECT * FROM players WHERE player_id IN (?) AND status = 'IN_QUEUE'", player_ids)
        if len(players) != 16:
            raise Exception("Not all players available")
        
        # Update all players
        db.execute("UPDATE players SET status = 'RESERVED', match_id = ? WHERE player_id IN (?)", 
                   match_id, player_ids)
        
        # Create reservations
        for player_id in player_ids:
            db.execute("INSERT INTO reservations (match_id, player_id, status, expires_at) VALUES (?, ?, 'PENDING', ?)",
                      match_id, player_id, datetime.now() + timedelta(seconds=30))
        
        # Create match record
        db.execute("INSERT INTO matches (match_id, players, status) VALUES (?, ?, 'RESERVED')",
                  match_id, json.dumps(player_ids))
```

**Idempotency:**
- Check player status before reservation
- Use unique constraints (player can only be in one match)
- Handle duplicate reservation requests

### Server Allocation

#### Server Pool Management

**Server Selection:**
1. **Region Matching**: Allocate server in same region as players
2. **Availability**: Find server with AVAILABLE status
3. **Load Balancing**: Distribute load across servers
4. **Health Check**: Only allocate healthy servers

**Allocation Flow:**
```python
def allocate_server(region, game_mode):
    # Find available server in region
    servers = db.query("""
        SELECT * FROM game_servers 
        WHERE region = ? AND game_mode = ? AND status = 'AVAILABLE'
        ORDER BY current_players ASC
        LIMIT 1
    """, region, game_mode)
    
    if not servers:
        # No available servers - wait or scale up
        return None
    
    server = servers[0]
    
    # Mark server as ALLOCATING
    db.execute("""
        UPDATE game_servers 
        SET status = 'ALLOCATING', allocated_at = NOW()
        WHERE server_id = ?
    """, server.server_id)
    
    return server
```

#### Server Scaling

**Auto-Scaling:**
- Monitor queue depth (players waiting)
- Provision new servers when queue depth > threshold
- De-provision servers when idle > threshold

**Server Health:**
- Health check endpoint on game servers
- Mark unhealthy servers as MAINTENANCE
- Remove from allocation pool

### Real-Time Updates

#### WebSocket Connection

**Connection Management:**
- One WebSocket per player in queue
- Connection key: `ws:{player_id}:{queue_id}`
- Heartbeat to keep connection alive

**Message Types:**
```json
// Queue update
{
  "type": "queue_update",
  "players_in_queue": 45,
  "estimated_wait_time": 30,
  "position": 12
}

// Match found
{
  "type": "match_found",
  "match_id": "match_123",
  "server_info": {
    "endpoint": "game.example.com:7777",
    "connection_token": "token_abc"
  },
  "players": [16 player IDs],
  "load_deadline": "2025-11-25T10:30:00Z"
}

// Reservation expired
{
  "type": "reservation_expired",
  "reason": "player_timeout"
}
```

**Optimization:**
- Batch updates (send every 1 second, not every change)
- Connection pooling
- Efficient routing (route by queue_id)

### Fairness vs Wait Time

#### Trade-off Analysis

**Fairness (Strict Skill Matching):**
- **Pros**: Balanced matches, better player experience
- **Cons**: Longer wait times, especially for high/low skill players

**Wait Time (Looser Matching):**
- **Pros**: Faster matches, better throughput
- **Cons**: Unbalanced matches, worse player experience

#### Balanced Approach

**Dynamic Skill Expansion:**
1. Start with strict matching (±100 MMR)
2. Expand range over time:
   - 0-30s: ±100 MMR
   - 30-60s: ±150 MMR
   - 60-120s: ±200 MMR
   - 120-300s: ±300 MMR
   - 300s+: ±500 MMR (any match)

**Wait Time Limits:**
- Maximum wait: 5 minutes
- After 5 minutes: Match with any available players
- Priority queue: VIP players (optional)

### Failure Handling

#### Player Leaves During Reservation

**Scenario**: Player leaves queue after being reserved.

**Solution:**
1. Detect player left (status check)
2. Cancel match if < 16 players
3. Return remaining players to queue
4. Release server allocation
5. Retry matchmaking for remaining players

#### Server Allocation Failure

**Scenario**: No servers available.

**Solution:**
1. Hold reservation (extend expiry)
2. Trigger auto-scaling
3. Wait for server (max 30 seconds)
4. If still no server: Cancel match, return players to queue

#### Reservation Timeout

**Scenario**: Player doesn't confirm within 30 seconds.

**Solution:**
1. Expire reservation
2. If < 16 confirmed: Cancel match
3. Return unconfirmed players to queue
4. Release server

#### Database Failure

**Scenario**: Database unavailable during reservation.

**Solution:**
1. Retry with exponential backoff
2. Fallback to Redis-only (degraded mode)
3. Reconcile when database recovers
4. Alert for manual intervention

### Backpressure and Capacity

#### Queue Depth Monitoring

**Metrics:**
- Players in queue per partition
- Average wait time
- Match formation rate
- Server availability

**Backpressure Actions:**
1. **High Queue Depth**: 
   - Expand skill brackets faster
   - Provision more servers
   - Alert operations team

2. **Server Capacity Exceeded**:
   - Slow down match formation
   - Queue server allocation requests
   - Trigger auto-scaling

3. **System Overload**:
   - Rate limit join queue requests
   - Reject new joins (degraded mode)
   - Scale horizontally

#### Capacity Planning

**Server Capacity:**
- Average match duration: 20 minutes
- Servers needed: (matches/minute × 20) / 60
- Example: 167 matches/sec × 60 × 20 / 60 = 3,340 servers

**Queue Processing:**
- Matchmaking workers: Based on queue partitions
- Each worker handles: 10-20 partitions
- Workers needed: (total partitions) / 15

### Trade-offs and Optimizations

#### Trade-offs

1. **Consistency vs Performance**
   - **Choice**: Strong consistency for reservations, eventual for stats
   - **Reason**: Reservations must be atomic, stats can be slightly stale
   - **Benefit**: Better performance, lower latency

2. **Fairness vs Wait Time**
   - **Choice**: Dynamic skill expansion
   - **Reason**: Balance both concerns
   - **Benefit**: Good matches with reasonable wait times

3. **Partitioning vs Global Matching**
   - **Choice**: Partition by game/region/skill
   - **Reason**: Avoid global locks, better scalability
   - **Benefit**: Parallel processing, no contention

#### Optimizations

1. **Pre-warming Servers**
   - Keep pool of warm servers ready
   - Faster allocation
   - Better latency

2. **Batch Operations**
   - Batch player status updates
   - Batch reservation creation
   - Reduces database load

3. **Caching**
   - Cache player skill ratings
   - Cache queue statistics
   - Cache server availability
   - Reduces database queries

4. **Connection Pooling**
   - Pool database connections
   - Pool Redis connections
   - Pool WebSocket connections
   - Better resource utilization

## What Interviewers Look For

### Distributed Systems Skills

1. **High-Throughput Coordination**
   - Handling 1M+ concurrent players
   - Low-latency operations (< 100ms)
   - Queue partitioning strategies
   - **Red Flags**: Global locks, synchronous operations, no partitioning

2. **Atomic Multi-Step Workflows**
   - Queue → Reserve → Allocate workflow
   - Atomic reservation of 16 players
   - Idempotency handling
   - **Red Flags**: No atomicity, race conditions, no idempotency

3. **Real-Time Systems**
   - WebSocket/SSE for updates
   - Low-latency notifications
   - Connection management
   - **Red Flags**: Polling, high latency, poor connection handling

### Problem-Solving Approach

1. **Partitioning Strategy**
   - Queue partitioning (game/region/skill)
   - Avoiding global locks
   - Parallel processing
   - **Red Flags**: Global queue, global locks, no partitioning

2. **Fairness vs Wait Time**
   - Skill-based matching algorithm
   - Dynamic skill expansion
   - Trade-off analysis
   - **Red Flags**: No fairness, no wait time consideration, no trade-offs

3. **Failure Handling**
   - Player leaves during reservation
   - Server allocation failure
   - Reservation timeout
   - **Red Flags**: No failure handling, no timeouts, no recovery

### System Design Skills

1. **Component Design**
   - Clear service boundaries
   - Queue service, matchmaking service, server manager
   - Proper API design
   - **Red Flags**: Monolithic design, unclear boundaries, poor APIs

2. **Data Structures**
   - Redis sorted sets for queues
   - Efficient player lookups
   - Queue statistics
   - **Red Flags**: Wrong data structures, inefficient lookups, no optimization

3. **Scalability**
   - Horizontal scaling
   - Queue partitioning
   - Server auto-scaling
   - **Red Flags**: Vertical scaling only, no partitioning, no auto-scaling

### Communication Skills

1. **Clear Explanation**
   - Explains matching algorithm
   - Discusses trade-offs
   - Justifies design decisions
   - **Red Flags**: Unclear explanations, no justification, confusing

2. **Architecture Diagrams**
   - Clear component diagram
   - Shows data flow
   - Queue partitioning visualization
   - **Red Flags**: No diagrams, unclear diagrams, missing components

### Meta-Specific Focus

1. **High-Throughput Systems**
   - Understanding of high QPS systems
   - Low-latency requirements
   - Real-time coordination
   - **Key**: Demonstrate high-throughput system design

2. **Coordination Patterns**
   - Atomic reservations
   - Distributed locks
   - Multi-step workflows
   - **Key**: Show coordination pattern expertise

3. **Capacity and Backpressure**
   - Queue depth monitoring
   - Server capacity planning
   - Auto-scaling strategies
   - **Key**: Demonstrate capacity thinking

## Summary

Designing a matchmaking service for multiplayer games requires careful consideration of high-throughput coordination, atomic multi-step workflows, skill-based matching, and real-time updates. Key design decisions include:

**Architecture Highlights:**
- Queue partitioning by game/region/skill to avoid global locks
- Redis sorted sets for efficient queue operations
- Atomic reservation using distributed locks
- Async server allocation with capacity management
- WebSocket for real-time player updates

**Key Patterns:**
- **Queue Partitioning**: Avoid global locks, enable parallel processing
- **Atomic Reservation**: Distributed locks + transactions for 16-player reservation
- **Skill-Based Matching**: Dynamic skill expansion balancing fairness and wait time
- **Real-Time Updates**: WebSocket for low-latency notifications
- **Capacity Management**: Auto-scaling, backpressure, queue depth monitoring

**Scalability Solutions:**
- Horizontal scaling (multiple matchmaking workers)
- Queue partitioning (independent processing)
- Server auto-scaling (dynamic capacity)
- Redis cluster (distributed queue state)

**Trade-offs:**
- Fairness vs wait time (dynamic skill expansion)
- Consistency vs performance (strong for reservations, eventual for stats)
- Partitioning vs global matching (partitioning for scalability)

This design handles 1M+ concurrent players, 100k+ matches/minute, and maintains < 100ms latency for queue operations while ensuring fair, skill-based matches. The system is scalable, fault-tolerant, and optimized for high-throughput coordination.

