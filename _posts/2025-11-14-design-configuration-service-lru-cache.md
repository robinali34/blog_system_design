---
layout: post
title: "Design a Configuration Service with LRU Cache - System Design Interview"
date: 2025-11-14
categories: [System Design, Interview Example, Distributed Systems, Caching, Microservices, Configuration Management]
excerpt: "A comprehensive guide to designing a centralized configuration service with LRU cache that distributes configuration data to multiple microservices, covering configuration management, caching strategies, change propagation, versioning, and architectural patterns for handling millions of configuration reads with low latency."
---

## Introduction

A configuration service is a centralized system that manages and distributes configuration data to multiple microservices. It provides a single source of truth for application settings, feature flags, environment variables, and runtime configurations. When combined with LRU (Least Recently Used) caching, it can handle millions of configuration reads per second with sub-millisecond latency.

This post provides a detailed walkthrough of designing a configuration service with LRU cache, covering configuration storage, caching strategies, change propagation, versioning, multi-service distribution, and handling high read throughput. This is a common system design interview question that tests your understanding of distributed systems, caching algorithms, pub/sub patterns, and configuration management.

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

**Design a centralized configuration service with LRU cache that distributes configuration data to multiple microservices:**

1. Store configuration data (key-value pairs, JSON, YAML)
2. Support multiple environments (dev, staging, prod)
3. Support multiple services/applications
4. Provide fast read access with LRU cache
5. Support configuration updates and versioning
6. Propagate configuration changes to all services
7. Support configuration rollback
8. Handle high read throughput (millions of reads per second)
9. Support configuration encryption for sensitive data
10. Provide configuration validation and schema enforcement

**Scale Requirements:**
- 1000+ microservices
- 10 million+ configuration keys
- 1 billion+ configuration reads per day
- Peak: 100,000 reads per second
- Average latency: < 1ms (with cache)
- Cache hit rate: > 95%
- Configuration updates: 10,000 per day
- Must support real-time change propagation

## Requirements

### Functional Requirements

**Core Features:**
1. **Configuration Storage**: Store key-value configurations
2. **Multi-Environment**: Support dev, staging, prod environments
3. **Multi-Service**: Support multiple services/applications
4. **Fast Reads**: LRU cache for sub-millisecond reads
5. **Configuration Updates**: Update configurations with versioning
6. **Change Propagation**: Notify services of configuration changes
7. **Configuration Rollback**: Rollback to previous versions
8. **Configuration Validation**: Validate configuration schemas
9. **Encryption**: Encrypt sensitive configuration values
10. **Configuration Search**: Search configurations by key, service, environment

**Out of Scope:**
- Configuration UI/Admin panel (focus on API)
- User authentication (assume existing auth system)
- Configuration templates
- Configuration inheritance
- Mobile app (focus on service-to-service communication)

### Non-Functional Requirements

1. **Availability**: 99.99% uptime
2. **Reliability**: No configuration loss, consistent reads
3. **Performance**: 
   - Cache read: < 1ms (p99)
   - Database read: < 10ms (p99)
   - Configuration update: < 100ms
   - Change propagation: < 1 second
4. **Scalability**: Handle 100K+ reads per second
5. **Consistency**: Strong consistency for writes, eventual consistency for reads
6. **Cache Hit Rate**: > 95% cache hit rate
7. **Durability**: All configurations persisted to database

## Capacity Estimation

### Traffic Estimates

- **Total Services**: 1,000
- **Configuration Keys**: 10 million
- **Configuration Reads per Day**: 1 billion
- **Peak Read Rate**: 100,000 per second
- **Normal Read Rate**: 10,000 per second
- **Configuration Updates per Day**: 10,000
- **Average Reads per Service**: 1,000 per second
- **Cache Hit Rate**: 95%

### Storage Estimates

**Configuration Data:**
- 10M keys × 1KB average = 10GB
- Configuration metadata: 10M × 200 bytes = 2GB
- Version history: 10K updates/day × 365 days × 1KB = 3.65GB/year
- 5-year retention: ~18GB

**Cache Data:**
- LRU cache: 1M hot keys × 1KB = 1GB per instance
- 10 cache instances: ~10GB

**Total Storage**: ~30GB

### Bandwidth Estimates

**Normal Traffic:**
- 10,000 reads/sec × 1KB = 10MB/s = 80Mbps
- Cache hits (95%): 9,500/sec × 1KB = 9.5MB/s
- Cache misses (5%): 500/sec × 1KB = 0.5MB/s

**Peak Traffic:**
- 100,000 reads/sec × 1KB = 100MB/s = 800Mbps

**Change Propagation:**
- 10,000 updates/day × 1KB × 1,000 services = 10GB/day = ~115KB/s = ~1Mbps

**Total Peak**: ~800Mbps

## Core Entities

### Configuration
- `config_id` (UUID)
- `service_name` (VARCHAR)
- `environment` (dev, staging, prod)
- `config_key` (VARCHAR)
- `config_value` (TEXT/JSON)
- `value_type` (string, number, boolean, json, yaml)
- `is_encrypted` (BOOLEAN)
- `version` (INT)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)
- `created_by` (user_id)

### Configuration Version
- `version_id` (UUID)
- `config_id` (UUID)
- `version` (INT)
- `config_value` (TEXT/JSON)
- `change_description` (TEXT)
- `created_at` (TIMESTAMP)
- `created_by` (user_id)

### Service Subscription
- `subscription_id` (UUID)
- `service_name` (VARCHAR)
- `environment` (VARCHAR)
- `subscribed_keys` (JSON array)
- `webhook_url` (VARCHAR, optional)
- `last_notified_at` (TIMESTAMP)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

### Configuration Schema
- `schema_id` (UUID)
- `service_name` (VARCHAR)
- `config_key` (VARCHAR)
- `schema_definition` (JSON)
- `validation_rules` (JSON)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

## API

### 1. Get Configuration
```
GET /api/v1/config/{service_name}/{environment}/{config_key}
Response:
{
  "service_name": "user-service",
  "environment": "prod",
  "config_key": "database.url",
  "config_value": "postgresql://db.example.com:5432/users",
  "value_type": "string",
  "version": 5,
  "updated_at": "2025-11-13T10:00:00Z"
}
```

### 2. Get Multiple Configurations
```
POST /api/v1/config/batch
Request:
{
  "service_name": "user-service",
  "environment": "prod",
  "config_keys": ["database.url", "cache.ttl", "feature.flag"]
}

Response:
{
  "configs": [
    {
      "config_key": "database.url",
      "config_value": "postgresql://db.example.com:5432/users",
      "version": 5
    },
    {
      "config_key": "cache.ttl",
      "config_value": "3600",
      "version": 3
    },
    {
      "config_key": "feature.flag",
      "config_value": "true",
      "version": 2
    }
  ]
}
```

### 3. Set Configuration
```
PUT /api/v1/config/{service_name}/{environment}/{config_key}
Request:
{
  "config_value": "postgresql://db.example.com:5432/users",
  "value_type": "string",
  "change_description": "Updated database URL",
  "encrypt": false
}

Response:
{
  "config_id": "uuid",
  "service_name": "user-service",
  "environment": "prod",
  "config_key": "database.url",
  "config_value": "postgresql://db.example.com:5432/users",
  "version": 6,
  "updated_at": "2025-11-13T10:05:00Z"
}
```

### 4. Delete Configuration
```
DELETE /api/v1/config/{service_name}/{environment}/{config_key}
Response:
{
  "success": true,
  "message": "Configuration deleted"
}
```

### 5. Get Configuration History
```
GET /api/v1/config/{service_name}/{environment}/{config_key}/history?limit=10
Response:
{
  "config_key": "database.url",
  "versions": [
    {
      "version": 6,
      "config_value": "postgresql://db.example.com:5432/users",
      "change_description": "Updated database URL",
      "created_at": "2025-11-13T10:05:00Z",
      "created_by": "user123"
    },
    {
      "version": 5,
      "config_value": "postgresql://db.old.com:5432/users",
      "change_description": "Initial configuration",
      "created_at": "2025-11-10T08:00:00Z",
      "created_by": "user123"
    }
  ]
}
```

### 6. Rollback Configuration
```
POST /api/v1/config/{service_name}/{environment}/{config_key}/rollback
Request:
{
  "target_version": 5
}

Response:
{
  "config_id": "uuid",
  "version": 7,
  "previous_version": 6,
  "rolled_back_to": 5,
  "updated_at": "2025-11-13T10:10:00Z"
}
```

### 7. Subscribe to Configuration Changes
```
POST /api/v1/config/subscribe
Request:
{
  "service_name": "user-service",
  "environment": "prod",
  "config_keys": ["database.url", "cache.ttl"],
  "webhook_url": "https://user-service.example.com/config/webhook"
}

Response:
{
  "subscription_id": "uuid",
  "service_name": "user-service",
  "subscribed_keys": ["database.url", "cache.ttl"],
  "status": "active"
}
```

## Data Flow

### Configuration Read Flow (Cache Hit)

1. **Service Requests Config**:
   - Microservice requests configuration
   - **Client SDK** sends request to **API Gateway**
   - **API Gateway** routes to **Configuration Service**

2. **Cache Lookup**:
   - **Configuration Service**:
     - Constructs cache key: `{service_name}:{environment}:{config_key}`
     - Checks **LRU Cache**
     - Cache hit: Returns cached value immediately

3. **Response**:
   - **Configuration Service** returns configuration
   - **Client SDK** caches locally (optional)
   - **Microservice** uses configuration

### Configuration Read Flow (Cache Miss)

1. **Service Requests Config**:
   - Microservice requests configuration
   - **Client SDK** sends request to **API Gateway**
   - **API Gateway** routes to **Configuration Service**

2. **Cache Lookup**:
   - **Configuration Service** checks **LRU Cache**
   - Cache miss: Proceeds to database

3. **Database Query**:
   - **Configuration Service** queries **Database**
   - Retrieves configuration by service, environment, key

4. **Cache Update**:
   - **Configuration Service**:
     - Stores configuration in **LRU Cache**
     - Evicts least recently used entry if cache full
     - Returns configuration

5. **Response**:
   - **Configuration Service** returns configuration
   - **Client SDK** caches locally (optional)
   - **Microservice** uses configuration

### Configuration Update Flow

1. **Admin Updates Config**:
   - Admin updates configuration via API
   - **API Gateway** routes to **Configuration Service**

2. **Validation**:
   - **Configuration Service**:
     - Validates configuration schema
     - Checks permissions
     - Encrypts value if needed

3. **Database Update**:
   - **Configuration Service**:
     - Updates configuration in **Database**
     - Creates version record
     - Increments version number
     - Updates timestamp

4. **Cache Invalidation**:
   - **Configuration Service**:
     - Invalidates cache entry
     - Removes from **LRU Cache**

5. **Change Propagation**:
   - **Configuration Service**:
     - Publishes change event to **Message Queue**
     - **Notification Service** notifies subscribed services
     - Services update local cache

6. **Response**:
   - **Configuration Service** returns updated configuration

### Configuration Change Notification Flow

1. **Configuration Updated**:
   - Configuration updated in database
   - Change event published to **Message Queue**

2. **Notification Processing**:
   - **Notification Service**:
     - Gets all service subscriptions for changed key
     - Filters by service and environment
     - Creates notification jobs

3. **Notification Delivery**:
   - **Notification Workers**:
     - Send webhook notifications to services
     - Or publish to service-specific message queues
     - Handle failures with retry logic

4. **Service Update**:
   - **Microservice** receives notification
   - Invalidates local cache
   - Fetches new configuration
   - Updates application state

## Database Design

### Schema Design

**Configurations Table:**
```sql
CREATE TABLE configurations (
    config_id UUID PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    environment VARCHAR(50) NOT NULL,
    config_key VARCHAR(500) NOT NULL,
    config_value TEXT NOT NULL,
    value_type VARCHAR(50) DEFAULT 'string',
    is_encrypted BOOLEAN DEFAULT FALSE,
    version INT NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(100),
    INDEX idx_service_env (service_name, environment),
    INDEX idx_key (config_key),
    INDEX idx_service_env_key (service_name, environment, config_key),
    UNIQUE KEY uk_service_env_key (service_name, environment, config_key)
);
```

**Configuration Versions Table:**
```sql
CREATE TABLE configuration_versions (
    version_id UUID PRIMARY KEY,
    config_id UUID NOT NULL,
    version INT NOT NULL,
    config_value TEXT NOT NULL,
    change_description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(100),
    INDEX idx_config_id (config_id),
    INDEX idx_config_version (config_id, version),
    FOREIGN KEY (config_id) REFERENCES configurations(config_id)
);
```

**Service Subscriptions Table:**
```sql
CREATE TABLE service_subscriptions (
    subscription_id UUID PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    environment VARCHAR(50) NOT NULL,
    subscribed_keys JSON NOT NULL,
    webhook_url VARCHAR(1000),
    last_notified_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_service_env (service_name, environment),
    INDEX idx_webhook (webhook_url)
);
```

**Configuration Schemas Table:**
```sql
CREATE TABLE configuration_schemas (
    schema_id UUID PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    config_key VARCHAR(500) NOT NULL,
    schema_definition JSON NOT NULL,
    validation_rules JSON,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_service_key (service_name, config_key),
    UNIQUE KEY uk_service_key (service_name, config_key)
);
```

### Database Sharding Strategy

**Configurations Table Sharding:**
- Shard by service_name using consistent hashing
- 100 shards: `shard_id = hash(service_name) % 100`
- All configurations for a service in same shard
- Enables efficient service-specific queries

**Shard Key Selection:**
- `service_name` ensures all configs for a service are in same shard
- Enables efficient queries for service configurations
- Prevents cross-shard queries for single service

**Replication:**
- Each shard replicated 3x for high availability
- Master-replica setup for read scaling
- Writes go to master, reads can go to replicas

## High-Level Design

```
┌─────────────┐
│ Microservice│
│   (Client)  │
└──────┬──────┘
       │
       │ HTTP/GRPC
       │
┌──────▼──────────────────────────────────────────────┐
│        API Gateway / Load Balancer                   │
│        - Rate Limiting                               │
│        - Request Routing                             │
└──────┬──────────────────────────────────────────────┘
       │
       │
┌──────▼──────────────────────────────────────────────┐
│         Configuration Service                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ Config   │  │ Config   │  │ Config   │          │
│  │ Reader   │  │ Writer   │  │ Validator│          │
│  └──────────┘  └──────────┘  └──────────┘          │
└──────┬──────────────────────────────────────────────┘
       │
       │
┌──────▼──────────────────────────────────────────────┐
│         LRU Cache Layer (In-Memory)                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ Cache    │  │ Cache    │  │ Cache    │          │
│  │ Instance │  │ Instance │  │ Instance │          │
│  │ 1        │  │ 2        │  │ N        │          │
│  └──────────┘  └──────────┘  └──────────┘          │
│  - Capacity: 1M keys per instance                   │
│  - Eviction: LRU algorithm                          │
│  - TTL: None (invalidate on update)                  │
└──────┬──────────────────────────────────────────────┘
       │
       │ Cache Miss
       │
┌──────▼──────────────────────────────────────────────┐
│         Database Cluster (Sharded)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ Shard 0   │  │ Shard 1   │  │ Shard N   │          │
│  │ Configs   │  │ Configs   │  │ Configs   │          │
│  └──────────┘  └──────────┘  └──────────┘          │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│              Message Queue (Kafka)                    │
│              - Configuration change events            │
│              - Notification jobs                       │
└──────┬───────────────────────────────────────────────┘
       │
       │
┌──────▼───────────────────────────────────────────────┐
│         Notification Service                          │
│         - Process change events                       │
│         - Notify subscribed services                 │
│         - Webhook delivery                           │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│         Encryption Service                            │
│         - Encrypt sensitive values                    │
│         - Decrypt on read                             │
└──────────────────────────────────────────────────────┘
```

## Deep Dive

### Component Design

#### 1. LRU Cache Implementation

**Responsibilities:**
- Store frequently accessed configurations
- Evict least recently used entries
- Provide sub-millisecond read access
- Handle cache invalidation

**Key Design Decisions:**
- **In-Memory Cache**: Fast access, limited capacity
- **LRU Eviction**: Evict least recently used when full
- **No TTL**: Invalidate on update instead
- **Distributed Cache**: Multiple cache instances
- **Cache Key Format**: `{service_name}:{environment}:{config_key}`

**Implementation:**
```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity=1000000):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.lock = threading.Lock()
    
    def get(self, key):
        with self.lock:
            if key not in self.cache:
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]
    
    def put(self, key, value):
        with self.lock:
            if key in self.cache:
                # Update existing
                self.cache[key] = value
                self.cache.move_to_end(key)
            else:
                # Add new
                if len(self.cache) >= self.capacity:
                    # Evict least recently used (first item)
                    self.cache.popitem(last=False)
                
                self.cache[key] = value
    
    def delete(self, key):
        with self.lock:
            if key in self.cache:
                del self.cache[key]
    
    def clear(self):
        with self.lock:
            self.cache.clear()
    
    def size(self):
        return len(self.cache)

class ConfigurationCache:
    def __init__(self):
        self.lru_cache = LRUCache(capacity=1000000)
        self.cache_stats = {
            'hits': 0,
            'misses': 0
        }
    
    def get_config(self, service_name, environment, config_key):
        cache_key = f"{service_name}:{environment}:{config_key}"
        
        # Try cache
        value = self.lru_cache.get(cache_key)
        if value:
            self.cache_stats['hits'] += 1
            return value
        
        # Cache miss
        self.cache_stats['misses'] += 1
        return None
    
    def set_config(self, service_name, environment, config_key, config_value):
        cache_key = f"{service_name}:{environment}:{config_key}"
        self.lru_cache.put(cache_key, config_value)
    
    def invalidate_config(self, service_name, environment, config_key):
        cache_key = f"{service_name}:{environment}:{config_key}"
        self.lru_cache.delete(cache_key)
    
    def get_cache_stats(self):
        total = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total * 100) if total > 0 else 0
        return {
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses'],
            'hit_rate': hit_rate,
            'cache_size': self.lru_cache.size()
        }
```

#### 2. Configuration Service

**Responsibilities:**
- Handle configuration reads and writes
- Manage cache
- Validate configurations
- Handle encryption

**Key Design Decisions:**
- **Cache-Aside Pattern**: Check cache first, then database
- **Write-Through**: Update cache on write
- **Cache Invalidation**: Invalidate on update
- **Batch Reads**: Support batch configuration reads

**Implementation:**
```python
class ConfigurationService:
    def __init__(self):
        self.cache = ConfigurationCache()
        self.db = Database()
        self.encryption_service = EncryptionService()
        self.validator = ConfigurationValidator()
    
    def get_config(self, service_name, environment, config_key):
        # Try cache first
        cached = self.cache.get_config(service_name, environment, config_key)
        if cached:
            return cached
        
        # Cache miss - query database
        config = self.db.get_configuration(
            service_name=service_name,
            environment=environment,
            config_key=config_key
        )
        
        if not config:
            return None
        
        # Decrypt if needed
        if config.is_encrypted:
            config.config_value = self.encryption_service.decrypt(config.config_value)
        
        # Store in cache
        self.cache.set_config(
            service_name, environment, config_key, config
        )
        
        return config
    
    def set_config(self, service_name, environment, config_key, config_value, 
                   encrypt=False, change_description=None):
        # Validate configuration
        if not self.validator.validate(service_name, config_key, config_value):
            raise ValidationError("Invalid configuration value")
        
        # Encrypt if needed
        if encrypt:
            config_value = self.encryption_service.encrypt(config_value)
        
        # Get current version
        current = self.get_config(service_name, environment, config_key)
        new_version = (current.version + 1) if current else 1
        
        # Update database
        config = self.db.update_configuration(
            service_name=service_name,
            environment=environment,
            config_key=config_key,
            config_value=config_value,
            version=new_version,
            is_encrypted=encrypt,
            change_description=change_description
        )
        
        # Create version record
        self.db.create_version(
            config_id=config.config_id,
            version=new_version,
            config_value=config_value,
            change_description=change_description
        )
        
        # Invalidate cache
        self.cache.invalidate_config(service_name, environment, config_key)
        
        # Publish change event
        self.publish_change_event(config)
        
        return config
    
    def batch_get_config(self, service_name, environment, config_keys):
        results = {}
        cache_misses = []
        
        # Try cache for all keys
        for key in config_keys:
            cached = self.cache.get_config(service_name, environment, key)
            if cached:
                results[key] = cached
            else:
                cache_misses.append(key)
        
        # Query database for cache misses
        if cache_misses:
            db_configs = self.db.batch_get_configurations(
                service_name=service_name,
                environment=environment,
                config_keys=cache_misses
            )
            
            for config in db_configs:
                # Decrypt if needed
                if config.is_encrypted:
                    config.config_value = self.encryption_service.decrypt(
                        config.config_value
                    )
                
                # Store in cache
                self.cache.set_config(
                    service_name, environment, config.config_key, config
                )
                
                results[config.config_key] = config
        
        return results
    
    def publish_change_event(self, config):
        event = {
            'service_name': config.service_name,
            'environment': config.environment,
            'config_key': config.config_key,
            'version': config.version,
            'updated_at': config.updated_at.isoformat()
        }
        
        # Publish to message queue
        message_queue.publish('config_changes', event)
```

#### 3. Change Propagation Service

**Responsibilities:**
- Process configuration change events
- Notify subscribed services
- Handle webhook delivery
- Retry failed notifications

**Key Design Decisions:**
- **Event-Driven**: Process change events from message queue
- **Webhook Delivery**: Send HTTP webhooks to services
- **Retry Logic**: Retry failed notifications
- **Batching**: Batch notifications for efficiency

**Implementation:**
```python
class ChangePropagationService:
    def __init__(self):
        self.message_queue = MessageQueue()
        self.db = Database()
        self.webhook_client = WebhookClient()
    
    def process_change_event(self, event):
        service_name = event['service_name']
        environment = event['environment']
        config_key = event['config_key']
        
        # Get all subscriptions for this key
        subscriptions = self.db.get_subscriptions(
            service_name=service_name,
            environment=environment,
            config_key=config_key
        )
        
        # Notify each subscriber
        for subscription in subscriptions:
            self.notify_subscriber(subscription, event)
    
    def notify_subscriber(self, subscription, event):
        if subscription.webhook_url:
            # Send webhook
            try:
                self.webhook_client.post(
                    subscription.webhook_url,
                    json={
                        'event_type': 'config_change',
                        'service_name': event['service_name'],
                        'environment': event['environment'],
                        'config_key': event['config_key'],
                        'version': event['version'],
                        'timestamp': event['updated_at']
                    },
                    timeout=5
                )
                
                # Update last notified
                self.db.update_subscription_notified(
                    subscription.subscription_id
                )
            except Exception as e:
                # Queue for retry
                self.queue_retry(subscription, event, e)
        else:
            # Publish to service-specific queue
            queue_name = f"config_changes:{subscription.service_name}"
            self.message_queue.publish(queue_name, event)
    
    def queue_retry(self, subscription, event, error):
        retry_job = {
            'subscription_id': subscription.subscription_id,
            'event': event,
            'error': str(error),
            'retry_count': 0,
            'max_retries': 3
        }
        
        # Queue with delay
        self.message_queue.publish_delayed(
            'config_notification_retry',
            retry_job,
            delay_seconds=60
        )
```

### Detailed Design

#### LRU Cache Eviction Strategy

**Challenge:** Evict least recently used entries when cache is full

**Solution:**
- **OrderedDict**: Use OrderedDict to track access order
- **Move to End**: Move accessed items to end
- **Pop from Front**: Evict from front (least recently used)

**Implementation:**
```python
class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()
    
    def get(self, key):
        if key not in self.cache:
            return None
        
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def put(self, key, value):
        if key in self.cache:
            # Update and move to end
            self.cache[key] = value
            self.cache.move_to_end(key)
        else:
            # Add new
            if len(self.cache) >= self.capacity:
                # Evict least recently used (first item)
                self.cache.popitem(last=False)
            
            self.cache[key] = value
```

#### Distributed Cache Consistency

**Challenge:** Keep multiple cache instances consistent

**Solution:**
- **Cache Invalidation**: Invalidate on update
- **Event-Driven**: Use message queue for invalidation
- **Eventual Consistency**: Accept eventual consistency

**Implementation:**
```python
class DistributedCacheManager:
    def __init__(self):
        self.cache_instances = [
            LRUCache(capacity=1000000) for _ in range(10)
        ]
        self.message_queue = MessageQueue()
        self.setup_invalidation_listener()
    
    def get_cache_instance(self, key):
        # Consistent hashing to select instance
        hash_value = hash(key)
        instance_index = hash_value % len(self.cache_instances)
        return self.cache_instances[instance_index]
    
    def get(self, service_name, environment, config_key):
        cache_key = f"{service_name}:{environment}:{config_key}"
        instance = self.get_cache_instance(cache_key)
        return instance.get(cache_key)
    
    def put(self, service_name, environment, config_key, value):
        cache_key = f"{service_name}:{environment}:{config_key}"
        instance = self.get_cache_instance(cache_key)
        instance.put(cache_key, value)
    
    def invalidate(self, service_name, environment, config_key):
        cache_key = f"{service_name}:{environment}:{config_key}"
        
        # Invalidate in all instances (broadcast)
        for instance in self.cache_instances:
            instance.delete(cache_key)
        
        # Publish invalidation event
        self.message_queue.publish('cache_invalidation', {
            'cache_key': cache_key
        })
    
    def setup_invalidation_listener(self):
        # Listen for invalidation events from other instances
        self.message_queue.subscribe('cache_invalidation', self.handle_invalidation)
    
    def handle_invalidation(self, event):
        cache_key = event['cache_key']
        # Invalidate in this instance
        for instance in self.cache_instances:
            instance.delete(cache_key)
```

#### Configuration Encryption

**Challenge:** Encrypt sensitive configuration values

**Solution:**
- **AES Encryption**: Use AES-256 for encryption
- **Key Management**: Use key management service
- **Transparent Decryption**: Decrypt on read automatically

**Implementation:**
```python
class EncryptionService:
    def __init__(self):
        self.key_manager = KeyManager()
        self.algorithm = 'AES-256-GCM'
    
    def encrypt(self, plaintext):
        # Get encryption key
        key = self.key_manager.get_encryption_key()
        
        # Generate IV
        iv = os.urandom(12)
        
        # Encrypt
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
        
        # Combine IV + ciphertext + tag
        encrypted = iv + ciphertext + encryptor.tag
        
        # Base64 encode
        return base64.b64encode(encrypted).decode()
    
    def decrypt(self, ciphertext):
        # Base64 decode
        encrypted = base64.b64decode(ciphertext)
        
        # Extract components
        iv = encrypted[:12]
        tag = encrypted[-16:]
        ciphertext_data = encrypted[12:-16]
        
        # Get decryption key
        key = self.key_manager.get_encryption_key()
        
        # Decrypt
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag))
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext_data) + decryptor.finalize()
        
        return plaintext.decode()
```

### Scalability Considerations

#### Horizontal Scaling

**Configuration Service:**
- Stateless service, horizontally scalable
- Multiple instances behind load balancer
- Shared cache instances or distributed cache
- Database connection pooling

**Cache Layer:**
- Multiple cache instances
- Consistent hashing for key distribution
- Cache invalidation via message queue

#### Caching Strategy

**LRU Cache:**
- **Capacity**: 1M keys per instance
- **Eviction**: LRU algorithm
- **No TTL**: Invalidate on update
- **Distributed**: Multiple instances with consistent hashing

**Cache Hit Rate Optimization:**
- **Warm-up**: Pre-load popular configurations
- **Batch Reads**: Reduce cache misses
- **Cache Size**: Large enough for hot data

### Security Considerations

#### Configuration Encryption

- **Sensitive Data**: Encrypt passwords, API keys, tokens
- **Key Management**: Use key management service
- **Access Control**: Restrict who can read encrypted configs

#### Access Control

- **Authentication**: Authenticate all requests
- **Authorization**: Role-based access control
- **Audit Logging**: Log all configuration changes

### Monitoring & Observability

#### Key Metrics

**System Metrics:**
- Cache hit rate
- Cache size
- Read latency (p50, p95, p99)
- Write latency (p50, p95, p99)
- Configuration update rate
- Change propagation latency

**Business Metrics:**
- Total configurations
- Total services
- Configuration reads per second
- Configuration updates per day
- Cache efficiency

#### Logging

- **Structured Logging**: JSON logs for parsing
- **Configuration Events**: Log all reads and writes
- **Cache Events**: Log cache hits and misses
- **Error Logging**: Log errors with context

#### Alerting

- **Low Cache Hit Rate**: Alert if hit rate < 90%
- **High Latency**: Alert if p95 latency > 10ms
- **High Error Rate**: Alert if error rate > 1%
- **Cache Full**: Alert if cache utilization > 95%

### Trade-offs and Optimizations

#### Trade-offs

**1. Cache Size: Large vs Small**
- **Large**: Higher hit rate, more memory
- **Small**: Lower memory, lower hit rate
- **Decision**: 1M keys per instance (balance)

**2. Cache Consistency: Strong vs Eventual**
- **Strong**: More complex, higher latency
- **Eventual**: Simpler, lower latency
- **Decision**: Eventual consistency with invalidation

**3. Change Propagation: Immediate vs Batch**
- **Immediate**: Lower latency, higher load
- **Batch**: Lower load, higher latency
- **Decision**: Immediate for critical configs, batch for others

**4. Encryption: Always vs On-Demand**
- **Always**: More secure, higher overhead
- **On-Demand**: Lower overhead, less secure
- **Decision**: On-demand encryption for sensitive data

#### Optimizations

**1. Cache Warming**
- Pre-load popular configurations
- Reduce initial cache misses
- Improve hit rate

**2. Batch Reads**
- Read multiple configs in one query
- Reduce database load
- Improve throughput

**3. Connection Pooling**
- Reuse database connections
- Reduce connection overhead
- Improve performance

**4. Compression**
- Compress large configuration values
- Reduce storage and bandwidth
- Improve cache efficiency

## Summary

Designing a configuration service with LRU cache requires careful consideration of:

1. **LRU Cache**: Efficient in-memory cache with LRU eviction
2. **Cache-Aside Pattern**: Check cache first, then database
3. **Change Propagation**: Real-time notification of configuration changes
4. **Configuration Versioning**: Track all configuration changes
5. **Multi-Service Support**: Serve multiple microservices
6. **Encryption**: Encrypt sensitive configuration values
7. **Scalability**: Handle 100K+ reads per second
8. **High Cache Hit Rate**: > 95% cache hit rate
9. **Low Latency**: Sub-millisecond cache reads
10. **Configuration Validation**: Validate configuration schemas

Key architectural decisions:
- **LRU Cache** for fast configuration reads
- **Cache-Aside Pattern** for cache management
- **Event-Driven Change Propagation** for real-time updates
- **Sharded Database** for configuration storage
- **Distributed Cache** for horizontal scaling
- **Encryption Service** for sensitive data
- **Message Queue** for change notifications
- **Horizontal Scaling** for all services

The system handles 100,000 configuration reads per second with sub-millisecond latency, maintains > 95% cache hit rate, and provides real-time configuration change propagation to all subscribed services.

