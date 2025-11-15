---
layout: post
title: "Design an Embedded Local Redis Cache System - System Design Interview"
date: 2025-11-14
categories: [System Design, Interview Example, Distributed Systems, Caching, Redis, Microservices, Performance Optimization]
excerpt: "A comprehensive guide to designing an embedded local Redis cache system for microservices, covering local cache architecture, Redis integration patterns, cache synchronization, data consistency, and architectural patterns for achieving sub-millisecond cache access with high availability."
---

## Introduction

An embedded local Redis cache system uses Redis instances running locally within each microservice or application server to provide ultra-fast cache access. This pattern combines the benefits of in-process caching (low latency) with Redis's advanced data structures and persistence capabilities. It's commonly used in high-performance systems where sub-millisecond cache access is critical.

This post provides a detailed walkthrough of designing an embedded local Redis cache system, covering local Redis deployment, cache synchronization strategies, data consistency models, cache warming, eviction policies, and handling cache invalidation across distributed services. This is a common system design interview question that tests your understanding of caching strategies, Redis internals, distributed systems, and performance optimization.

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

**Design an embedded local Redis cache system for microservices with the following features:**

1. Embed Redis instance within each application server
2. Provide sub-millisecond cache access
3. Support multiple data structures (strings, hashes, sets, sorted sets)
4. Handle cache synchronization across distributed services
5. Support cache invalidation and updates
6. Implement cache warming strategies
7. Handle cache eviction policies (LRU, LFU, TTL-based)
8. Support cache persistence (RDB, AOF)
9. Provide cache monitoring and metrics
10. Handle failover and high availability

**Scale Requirements:**
- 1000+ microservice instances
- 100 million+ cache keys per instance
- 1 billion+ cache operations per day per instance
- Peak: 100,000 operations per second per instance
- Average latency: < 0.5ms (local Redis)
- Cache hit rate: > 90%
- Must support real-time cache invalidation
- Memory limit: 10GB per instance

## Requirements

### Functional Requirements

**Core Features:**
1. **Local Redis Instance**: Embed Redis on each server
2. **Fast Cache Access**: Sub-millisecond read/write operations
3. **Data Structures**: Support strings, hashes, sets, sorted sets, lists
4. **Cache Synchronization**: Sync cache updates across instances
5. **Cache Invalidation**: Invalidate cache entries on data changes
6. **Cache Warming**: Pre-load frequently accessed data
7. **Eviction Policies**: LRU, LFU, TTL-based eviction
8. **Persistence**: Optional RDB and AOF persistence
9. **Cache Monitoring**: Monitor cache performance and health
10. **High Availability**: Handle Redis failures gracefully

**Out of Scope:**
- Distributed Redis cluster (focus on local instances)
- Redis replication (focus on local caching)
- Cache-as-a-Service (focus on embedded pattern)
- Multi-region cache synchronization

### Non-Functional Requirements

1. **Availability**: 99.9% uptime per instance
2. **Reliability**: No data loss (with persistence enabled)
3. **Performance**: 
   - Cache read: < 0.5ms (p99)
   - Cache write: < 1ms (p99)
   - Cache hit rate: > 90%
4. **Scalability**: Handle 100K+ operations per second per instance
5. **Consistency**: Eventual consistency across instances
6. **Memory Efficiency**: Efficient memory usage with eviction
7. **Fault Tolerance**: Graceful degradation on Redis failure

## Capacity Estimation

### Traffic Estimates

- **Total Service Instances**: 1,000
- **Cache Keys per Instance**: 100 million
- **Cache Operations per Day per Instance**: 1 billion
- **Peak Operations per Second**: 100,000 per instance
- **Normal Operations per Second**: 10,000 per instance
- **Cache Hit Rate**: 90%
- **Cache Miss Rate**: 10%

### Storage Estimates

**Cache Data per Instance:**
- 100M keys × 1KB average = 100GB per instance
- With compression: ~50GB per instance
- Memory limit: 10GB (eviction active)

**Persistence (RDB):**
- Snapshot size: 10GB per instance
- Daily snapshots: 10GB × 1000 instances = 10TB/day
- 7-day retention: ~70TB

**Persistence (AOF):**
- AOF file: 5GB per instance (compressed)
- Daily AOF: 5GB × 1000 instances = 5TB/day
- 7-day retention: ~35TB

**Total Storage**: ~105TB

### Bandwidth Estimates

**Local Operations:**
- 100,000 ops/sec × 1KB = 100MB/s = 800Mbps per instance
- All operations are local (no network overhead)

**Cache Synchronization:**
- 10,000 updates/day × 1KB × 1000 instances = 10GB/day = ~115KB/s = ~1Mbps

**Total Peak**: ~800Mbps per instance (local only)

## Core Entities

### Cache Entry
- `key` (STRING)
- `value` (STRING/JSON/BINARY)
- `data_type` (string, hash, set, sorted_set, list)
- `ttl` (INT, seconds)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)
- `access_count` (INT)
- `last_accessed_at` (TIMESTAMP)

### Cache Metadata
- `key` (STRING)
- `size_bytes` (INT)
- `eviction_priority` (INT)
- `tags` (SET, for invalidation)
- `source` (database, api, computed)

### Cache Invalidation Event
- `event_id` (UUID)
- `invalidation_type` (key, pattern, tag)
- `target` (key/pattern/tag)
- `timestamp` (TIMESTAMP)
- `source_instance` (instance_id)

### Cache Statistics
- `instance_id` (STRING)
- `total_keys` (INT)
- `memory_used` (INT, bytes)
- `memory_limit` (INT, bytes)
- `hits` (INT)
- `misses` (INT)
- `evictions` (INT)
- `operations_per_second` (FLOAT)
- `timestamp` (TIMESTAMP)

## API

### 1. Get Cache Value
```
GET /api/v1/cache/{key}
Response:
{
  "key": "user:123",
  "value": "{\"id\":123,\"name\":\"John\"}",
  "ttl": 3600,
  "data_type": "string",
  "hit": true
}
```

### 2. Set Cache Value
```
PUT /api/v1/cache/{key}
Request:
{
  "value": "{\"id\":123,\"name\":\"John\"}",
  "ttl": 3600,
  "data_type": "string",
  "tags": ["user", "profile"]
}

Response:
{
  "key": "user:123",
  "status": "set",
  "ttl": 3600
}
```

### 3. Delete Cache Entry
```
DELETE /api/v1/cache/{key}
Response:
{
  "key": "user:123",
  "status": "deleted"
}
```

### 4. Invalidate by Pattern
```
POST /api/v1/cache/invalidate
Request:
{
  "pattern": "user:*",
  "invalidation_type": "pattern"
}

Response:
{
  "pattern": "user:*",
  "keys_invalidated": 1000,
  "status": "success"
}
```

### 5. Invalidate by Tags
```
POST /api/v1/cache/invalidate
Request:
{
  "tags": ["user", "profile"],
  "invalidation_type": "tag"
}

Response:
{
  "tags": ["user", "profile"],
  "keys_invalidated": 500,
  "status": "success"
}
```

### 6. Get Cache Statistics
```
GET /api/v1/cache/stats
Response:
{
  "instance_id": "server-001",
  "total_keys": 1000000,
  "memory_used": 8589934592,
  "memory_limit": 10737418240,
  "memory_usage_percent": 80,
  "hits": 9000000,
  "misses": 1000000,
  "hit_rate": 0.9,
  "evictions": 50000,
  "operations_per_second": 10000,
  "uptime_seconds": 86400
}
```

### 7. Warm Cache
```
POST /api/v1/cache/warm
Request:
{
  "keys": ["user:1", "user:2", "user:3"],
  "source": "database"
}

Response:
{
  "keys_warmed": 3,
  "status": "success"
}
```

## Data Flow

### Cache Read Flow (Hit)

1. **Application Requests Data**:
   - Application needs data (e.g., user profile)
   - **Cache Client** constructs cache key
   - Sends GET request to **Local Redis**

2. **Local Redis Lookup**:
   - **Local Redis** checks memory for key
   - Cache hit: Returns value immediately
   - Updates access statistics

3. **Response**:
   - **Cache Client** returns data to application
   - Application uses cached data

### Cache Read Flow (Miss)

1. **Application Requests Data**:
   - Application needs data
   - **Cache Client** sends GET request to **Local Redis**

2. **Local Redis Lookup**:
   - **Local Redis** checks memory for key
   - Cache miss: Returns null

3. **Data Source Query**:
   - **Cache Client**:
     - Queries **Database** or **API**
     - Retrieves data from source

4. **Cache Update**:
   - **Cache Client**:
     - Stores data in **Local Redis**
     - Sets TTL if configured
     - Returns data to application

5. **Response**:
   - **Cache Client** returns data to application
   - Application uses data

### Cache Write Flow

1. **Application Updates Data**:
   - Application updates data (e.g., user profile)
   - **Cache Client** updates **Database**

2. **Cache Invalidation**:
   - **Cache Client**:
     - Invalidates cache entry in **Local Redis**
     - Publishes invalidation event to **Message Queue**

3. **Cache Synchronization**:
   - **Message Queue** distributes invalidation event
   - Other instances receive event
   - Each instance invalidates local cache

4. **Response**:
   - **Cache Client** confirms update
   - Application continues

### Cache Warming Flow

1. **Warm-up Trigger**:
   - Service starts or scheduled warm-up
   - **Cache Warmer** identifies keys to warm

2. **Data Loading**:
   - **Cache Warmer**:
     - Queries **Database** for data
     - Loads frequently accessed keys
     - Batch loads data

3. **Cache Population**:
   - **Cache Warmer**:
     - Stores data in **Local Redis**
     - Sets appropriate TTL
     - Updates statistics

4. **Completion**:
   - **Cache Warmer** reports warm-up completion
   - Service ready for traffic

## Database Design

### Schema Design

**Cache Metadata Table (Optional, for tracking):**
```sql
CREATE TABLE cache_metadata (
    key VARCHAR(500) PRIMARY KEY,
    instance_id VARCHAR(100) NOT NULL,
    data_type VARCHAR(50) NOT NULL,
    size_bytes INT NOT NULL,
    ttl INT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_accessed_at TIMESTAMP,
    access_count INT DEFAULT 0,
    INDEX idx_instance_id (instance_id),
    INDEX idx_last_accessed (last_accessed_at),
    INDEX idx_access_count (access_count DESC)
);
```

**Cache Invalidation Events Table:**
```sql
CREATE TABLE cache_invalidation_events (
    event_id UUID PRIMARY KEY,
    invalidation_type VARCHAR(50) NOT NULL,
    target VARCHAR(500) NOT NULL,
    instance_id VARCHAR(100),
    timestamp TIMESTAMP DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE,
    INDEX idx_timestamp (timestamp DESC),
    INDEX idx_processed (processed),
    INDEX idx_target (target)
);
```

**Cache Statistics Table:**
```sql
CREATE TABLE cache_statistics (
    stat_id UUID PRIMARY KEY,
    instance_id VARCHAR(100) NOT NULL,
    total_keys INT NOT NULL,
    memory_used BIGINT NOT NULL,
    memory_limit BIGINT NOT NULL,
    hits BIGINT NOT NULL,
    misses BIGINT NOT NULL,
    evictions INT NOT NULL,
    operations_per_second FLOAT,
    timestamp TIMESTAMP DEFAULT NOW(),
    INDEX idx_instance_id (instance_id),
    INDEX idx_timestamp (timestamp DESC)
);
```

### Database Sharding Strategy

**Note:** Since this is an embedded local Redis system, the primary storage is Redis itself. The database tables above are optional for tracking and analytics purposes.

**If using database for metadata:**
- Shard by instance_id using consistent hashing
- 10 shards: `shard_id = hash(instance_id) % 10`
- All metadata for an instance in same shard

## High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Server                        │
│                                                              │
│  ┌──────────────┐                                          │
│  │ Application  │                                          │
│  │   Code       │                                          │
│  └──────┬───────┘                                          │
│         │                                                   │
│         │                                                   │
│  ┌──────▼──────────────────────────────────────────────┐  │
│  │         Cache Client Library                          │  │
│  │  - Key construction                                   │  │
│  │  - Cache operations                                   │  │
│  │  - Invalidation handling                               │  │
│  │  - Statistics collection                              │  │
│  └──────┬──────────────────────────────────────────────┘  │
│         │                                                   │
│         │ Local Socket/Unix Socket                         │
│         │                                                   │
│  ┌──────▼──────────────────────────────────────────────┐  │
│  │         Embedded Local Redis                          │  │
│  │  - In-memory data store                               │  │
│  │  - Data structures (string, hash, set, sorted set)    │  │
│  │  - Eviction policies (LRU, LFU, TTL)                  │  │
│  │  - Persistence (RDB, AOF)                             │  │
│  │  - Memory limit: 10GB                                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
         │
         │ Invalidation Events
         │
┌────────▼───────────────────────────────────────────────────┐
│              Message Queue (Kafka/RabbitMQ)                 │
│              - Cache invalidation events                    │
│              - Cache synchronization                        │
└────────┬───────────────────────────────────────────────────┘
         │
         │
┌────────▼───────────────────────────────────────────────────┐
│         Cache Synchronization Service                       │
│         - Process invalidation events                       │
│         - Distribute to all instances                       │
└────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│         Data Sources                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ Database │  │   API    │  │ External │                  │
│  │          │  │  Service │  │  Service │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│         Monitoring & Observability                           │
│  - Cache statistics                                          │
│  - Performance metrics                                       │
│  - Health checks                                             │
└─────────────────────────────────────────────────────────────┘
```

## Deep Dive

### Component Design

#### 1. Embedded Local Redis

**Responsibilities:**
- Provide fast in-memory cache access
- Support multiple data structures
- Handle eviction policies
- Support persistence

**Key Design Decisions:**
- **Local Instance**: One Redis per application server
- **Memory Limit**: 10GB per instance
- **Eviction Policy**: allkeys-lru (evict least recently used)
- **Persistence**: Optional RDB snapshots
- **Network**: Unix socket or localhost TCP

**Configuration:**
```conf
# redis.conf
port 6379
bind 127.0.0.1
maxmemory 10gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfsync everysec
```

**Implementation:**
```python
import redis

class EmbeddedRedisCache:
    def __init__(self, host='127.0.0.1', port=6379, db=0):
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            db=db,
            socket_connect_timeout=1,
            socket_timeout=1,
            decode_responses=True
        )
        self.ping()
    
    def get(self, key):
        """Get value from cache"""
        try:
            value = self.redis_client.get(key)
            return value
        except redis.RedisError as e:
            # Handle Redis errors
            return None
    
    def set(self, key, value, ttl=None):
        """Set value in cache"""
        try:
            if ttl:
                self.redis_client.setex(key, ttl, value)
            else:
                self.redis_client.set(key, value)
            return True
        except redis.RedisError as e:
            return False
    
    def delete(self, key):
        """Delete key from cache"""
        try:
            self.redis_client.delete(key)
            return True
        except redis.RedisError as e:
            return False
    
    def exists(self, key):
        """Check if key exists"""
        try:
            return self.redis_client.exists(key) > 0
        except redis.RedisError as e:
            return False
    
    def get_stats(self):
        """Get Redis statistics"""
        try:
            info = self.redis_client.info()
            return {
                'total_keys': info.get('db0', {}).get('keys', 0),
                'memory_used': info.get('used_memory', 0),
                'memory_limit': info.get('maxmemory', 0),
                'hits': info.get('keyspace_hits', 0),
                'misses': info.get('keyspace_misses', 0),
                'evictions': info.get('evicted_keys', 0),
                'uptime': info.get('uptime_in_seconds', 0)
            }
        except redis.RedisError as e:
            return None
```

#### 2. Cache Client Library

**Responsibilities:**
- Provide high-level cache API
- Handle cache operations
- Manage cache invalidation
- Collect statistics

**Key Design Decisions:**
- **Abstraction Layer**: Hide Redis complexity
- **Error Handling**: Graceful degradation on Redis failure
- **Statistics**: Collect cache performance metrics
- **Tagging**: Support tag-based invalidation

**Implementation:**
```python
class CacheClient:
    def __init__(self, redis_cache):
        self.redis = redis_cache
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
        self.message_queue = MessageQueue()
    
    def get(self, key, loader=None):
        """Get value from cache, load if miss"""
        # Try cache
        value = self.redis.get(key)
        if value:
            self.stats['hits'] += 1
            return json.loads(value) if isinstance(value, str) else value
        
        # Cache miss
        self.stats['misses'] += 1
        
        # Load from source if loader provided
        if loader:
            value = loader()
            if value:
                self.set(key, value)
            return value
        
        return None
    
    def set(self, key, value, ttl=None, tags=None):
        """Set value in cache"""
        try:
            # Serialize value
            if isinstance(value, (dict, list)):
                serialized = json.dumps(value)
            else:
                serialized = str(value)
            
            # Store in cache
            self.redis.set(key, serialized, ttl=ttl)
            
            # Store tags for invalidation
            if tags:
                self._store_tags(key, tags)
            
            self.stats['sets'] += 1
            return True
        except Exception as e:
            return False
    
    def delete(self, key):
        """Delete key from cache"""
        try:
            self.redis.delete(key)
            self._remove_tags(key)
            self.stats['deletes'] += 1
            return True
        except Exception as e:
            return False
    
    def invalidate_by_pattern(self, pattern):
        """Invalidate keys matching pattern"""
        try:
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
            
            # Publish invalidation event
            self.message_queue.publish('cache_invalidation', {
                'type': 'pattern',
                'pattern': pattern,
                'instance_id': self.get_instance_id()
            })
            
            return len(keys)
        except Exception as e:
            return 0
    
    def invalidate_by_tags(self, tags):
        """Invalidate keys with specific tags"""
        try:
            keys = []
            for tag in tags:
                tag_key = f"tag:{tag}"
                tagged_keys = self.redis.smembers(tag_key)
                keys.extend(tagged_keys)
            
            if keys:
                self.redis.delete(*keys)
            
            # Publish invalidation event
            self.message_queue.publish('cache_invalidation', {
                'type': 'tag',
                'tags': tags,
                'instance_id': self.get_instance_id()
            })
            
            return len(set(keys))
        except Exception as e:
            return 0
    
    def _store_tags(self, key, tags):
        """Store tags for a key"""
        for tag in tags:
            tag_key = f"tag:{tag}"
            self.redis.sadd(tag_key, key)
            self.redis.set(f"key:{key}:tags", json.dumps(tags))
    
    def _remove_tags(self, key):
        """Remove tags for a key"""
        tags_json = self.redis.get(f"key:{key}:tags")
        if tags_json:
            tags = json.loads(tags_json)
            for tag in tags:
                tag_key = f"tag:{tag}"
                self.redis.srem(tag_key, key)
            self.redis.delete(f"key:{key}:tags")
    
    def get_stats(self):
        """Get cache statistics"""
        redis_stats = self.redis.get_stats()
        if redis_stats:
            total_ops = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_ops * 100) if total_ops > 0 else 0
            
            return {
                **redis_stats,
                'client_hits': self.stats['hits'],
                'client_misses': self.stats['misses'],
                'client_hit_rate': hit_rate,
                'sets': self.stats['sets'],
                'deletes': self.stats['deletes']
            }
        return self.stats
```

#### 3. Cache Synchronization Service

**Responsibilities:**
- Process cache invalidation events
- Distribute invalidation to all instances
- Handle event ordering
- Retry failed invalidations

**Key Design Decisions:**
- **Event-Driven**: Process events from message queue
- **Broadcast**: Send to all instances
- **Idempotency**: Handle duplicate events
- **Retry Logic**: Retry failed invalidations

**Implementation:**
```python
class CacheSynchronizationService:
    def __init__(self, cache_client, message_queue):
        self.cache_client = cache_client
        self.message_queue = message_queue
        self.processed_events = set()  # Track processed events
        self.setup_listener()
    
    def setup_listener(self):
        """Subscribe to cache invalidation events"""
        self.message_queue.subscribe('cache_invalidation', self.handle_invalidation)
    
    def handle_invalidation(self, event):
        """Handle cache invalidation event"""
        event_id = event.get('event_id')
        
        # Skip if already processed
        if event_id in self.processed_events:
            return
        
        # Process invalidation
        invalidation_type = event.get('type')
        
        if invalidation_type == 'key':
            # Invalidate specific key
            key = event.get('key')
            self.cache_client.delete(key)
        
        elif invalidation_type == 'pattern':
            # Invalidate by pattern
            pattern = event.get('pattern')
            self.cache_client.invalidate_by_pattern(pattern)
        
        elif invalidation_type == 'tag':
            # Invalidate by tags
            tags = event.get('tags')
            self.cache_client.invalidate_by_tags(tags)
        
        # Mark as processed
        self.processed_events.add(event_id)
        
        # Cleanup old processed events (prevent memory leak)
        if len(self.processed_events) > 10000:
            self.processed_events.clear()
```

#### 4. Cache Warmer

**Responsibilities:**
- Pre-load frequently accessed data
- Warm cache on service startup
- Maintain cache freshness
- Handle warm-up failures

**Key Design Decisions:**
- **Startup Warm-up**: Load data on service start
- **Scheduled Warm-up**: Periodic cache refresh
- **Batch Loading**: Load multiple keys efficiently
- **Failure Handling**: Continue on individual failures

**Implementation:**
```python
class CacheWarmer:
    def __init__(self, cache_client, data_loader):
        self.cache_client = cache_client
        self.data_loader = data_loader
        self.warmup_keys = []
    
    def register_keys(self, keys):
        """Register keys to warm"""
        self.warmup_keys.extend(keys)
    
    def warm_cache(self):
        """Warm cache with registered keys"""
        warmed = 0
        failed = 0
        
        for key in self.warmup_keys:
            try:
                # Load data
                value = self.data_loader.load(key)
                if value:
                    # Store in cache
                    self.cache_client.set(key, value, ttl=3600)
                    warmed += 1
            except Exception as e:
                failed += 1
                continue
        
        return {
            'warmed': warmed,
            'failed': failed,
            'total': len(self.warmup_keys)
        }
    
    def warm_by_pattern(self, pattern, loader):
        """Warm cache for keys matching pattern"""
        # Get all keys matching pattern from data source
        keys = loader.get_keys(pattern)
        
        warmed = 0
        for key in keys:
            try:
                value = loader.load(key)
                if value:
                    self.cache_client.set(key, value, ttl=3600)
                    warmed += 1
            except Exception as e:
                continue
        
        return warmed
```

### Detailed Design

#### LRU Eviction Policy

**Challenge:** Evict least recently used keys when memory limit reached

**Solution:**
- **Redis LRU**: Use Redis's built-in LRU eviction
- **Approximate LRU**: Redis uses approximate LRU (faster)
- **Sampling**: Sample keys for eviction

**Configuration:**
```conf
maxmemory 10gb
maxmemory-policy allkeys-lru
```

#### Cache Invalidation Strategies

**Challenge:** Invalidate cache across distributed instances

**Solution:**
- **Event-Driven**: Publish invalidation events
- **Pattern Matching**: Invalidate by key patterns
- **Tag-Based**: Invalidate by tags
- **TTL-Based**: Automatic expiration

**Implementation:**
```python
def invalidate_cache(self, invalidation_strategy, target):
    """Invalidate cache using different strategies"""
    
    if invalidation_strategy == 'key':
        # Invalidate specific key
        self.cache_client.delete(target)
        self.publish_invalidation('key', target)
    
    elif invalidation_strategy == 'pattern':
        # Invalidate by pattern
        keys_invalidated = self.cache_client.invalidate_by_pattern(target)
        self.publish_invalidation('pattern', target)
    
    elif invalidation_strategy == 'tag':
        # Invalidate by tags
        keys_invalidated = self.cache_client.invalidate_by_tags(target)
        self.publish_invalidation('tag', target)
    
    elif invalidation_strategy == 'ttl':
        # Set TTL to expire soon
        self.cache_client.expire(target, 1)
```

#### Cache Persistence

**Challenge:** Persist cache data for recovery

**Solution:**
- **RDB Snapshots**: Periodic snapshots
- **AOF Logging**: Append-only file logging
- **Hybrid**: Both RDB and AOF

**Configuration:**
```conf
# RDB snapshots
save 900 1      # Save if at least 1 key changed in 900 seconds
save 300 10     # Save if at least 10 keys changed in 300 seconds
save 60 10000   # Save if at least 10000 keys changed in 60 seconds

# AOF logging
appendonly yes
appendfsync everysec  # fsync every second
```

### Scalability Considerations

#### Horizontal Scaling

**Application Servers:**
- Each server has its own embedded Redis
- No shared state between instances
- Scale by adding more servers
- Cache synchronization via message queue

#### Memory Management

**Eviction Policies:**
- **allkeys-lru**: Evict least recently used
- **allkeys-lfu**: Evict least frequently used
- **volatile-lru**: Evict LRU with TTL
- **noeviction**: Don't evict (return errors)

**Memory Optimization:**
- **Compression**: Compress large values
- **Data Structure Selection**: Use appropriate structures
- **TTL Management**: Set appropriate TTLs

### Security Considerations

#### Access Control

- **Local Only**: Bind to localhost/Unix socket
- **No Network Access**: Don't expose Redis to network
- **Authentication**: Use Redis AUTH if needed

#### Data Encryption

- **At-Rest**: Encrypt sensitive values before caching
- **In-Transit**: Not needed (local only)
- **Key Management**: Use secure key management

### Monitoring & Observability

#### Key Metrics

**Cache Performance:**
- Cache hit rate
- Cache miss rate
- Average latency (p50, p95, p99)
- Operations per second
- Memory usage
- Eviction rate

**Cache Health:**
- Redis uptime
- Connection status
- Error rate
- Persistence status

#### Logging

- **Structured Logging**: JSON logs for parsing
- **Cache Events**: Log cache hits, misses, evictions
- **Error Logging**: Log Redis errors
- **Performance Logging**: Log slow operations

#### Alerting

- **Low Hit Rate**: Alert if hit rate < 85%
- **High Memory**: Alert if memory usage > 90%
- **High Error Rate**: Alert if error rate > 1%
- **Redis Down**: Alert if Redis unavailable

### Trade-offs and Optimizations

#### Trade-offs

**1. Persistence: RDB vs AOF vs None**
- **RDB**: Faster recovery, data loss risk
- **AOF**: No data loss, slower recovery
- **None**: Fastest, no persistence
- **Decision**: RDB for most cases, AOF for critical data

**2. Eviction Policy: LRU vs LFU vs TTL**
- **LRU**: Good for temporal locality
- **LFU**: Good for frequency-based access
- **TTL**: Good for time-sensitive data
- **Decision**: LRU for general caching

**3. Memory Limit: High vs Low**
- **High**: More cache, less eviction
- **Low**: Less cache, more eviction
- **Decision**: Balance based on workload

**4. Synchronization: Real-Time vs Batch**
- **Real-Time**: Lower latency, higher load
- **Batch**: Lower load, higher latency
- **Decision**: Real-time for critical invalidations

#### Optimizations

**1. Compression**
- Compress large values
- Reduce memory usage
- Trade CPU for memory

**2. Batch Operations**
- Batch multiple operations
- Reduce overhead
- Improve throughput

**3. Connection Pooling**
- Reuse Redis connections
- Reduce connection overhead
- Improve performance

**4. Lazy Loading**
- Load data on demand
- Reduce initial load time
- Improve startup performance

## Summary

Designing an embedded local Redis cache system requires careful consideration of:

1. **Local Redis Instance**: One Redis per application server for ultra-low latency
2. **Sub-Millisecond Access**: Local socket communication for fast access
3. **Eviction Policies**: LRU/LFU/TTL-based eviction for memory management
4. **Cache Synchronization**: Event-driven invalidation across instances
5. **Cache Warming**: Pre-load frequently accessed data
6. **Persistence**: Optional RDB/AOF for data recovery
7. **High Hit Rate**: > 90% cache hit rate with proper eviction
8. **Memory Management**: Efficient memory usage with eviction
9. **Fault Tolerance**: Graceful degradation on Redis failure
10. **Monitoring**: Comprehensive metrics and alerting

Key architectural decisions:
- **Embedded Redis** for local cache access
- **Event-Driven Synchronization** for cache invalidation
- **LRU Eviction** for memory management
- **Tag-Based Invalidation** for flexible cache management
- **Cache Warming** for improved hit rates
- **Optional Persistence** for data recovery
- **Local Socket Communication** for minimal latency
- **Horizontal Scaling** by adding more servers

The system provides sub-millisecond cache access, handles 100,000+ operations per second per instance, maintains > 90% cache hit rate, and supports real-time cache invalidation across distributed services.

