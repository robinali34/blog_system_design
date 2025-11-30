---
layout: post
title: "Design a Pub/Sub System - System Design Interview"
date: 2025-11-29
categories: [System Design, Interview Example, Distributed Systems, Real-time Systems, Messaging]
excerpt: "A comprehensive guide to designing a publish-subscribe messaging system with ephemeral delivery, low-latency fan-out, topic routing, connection management, and horizontal scaling. Messages are intentionally lost if no subscribers are listening."
---

## Introduction

Designing a publish-subscribe (pub/sub) messaging system is a complex distributed systems problem that tests your ability to build low-latency, real-time messaging infrastructure. The system must support publishers sending messages to topics and subscribers receiving those messages in near real-time, with the key characteristic that messages are ephemeral—they are lost if no subscribers are currently listening.

This post provides a detailed walkthrough of designing a pub/sub system, covering key architectural decisions, topic routing, connection management, ephemeral delivery guarantees, hot-topic handling, backpressure, and horizontal scaling. This is a common system design interview question that tests your understanding of distributed systems, WebSocket connections, message fan-out, and real-time communication patterns.

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
7. [High-Level Design](#high-level-design)
8. [Deep Dive](#deep-dive)
   - [Component Design](#component-design)
   - [Topic Routing](#topic-routing)
   - [Connection Management](#connection-management)
   - [Message Fan-Out](#message-fan-out)
   - [Ephemeral Delivery](#ephemeral-delivery)
   - [Hot-Topic Handling](#hot-topic-handling)
   - [Backpressure](#backpressure)
   - [Protocols](#protocols)
   - [Failure Handling](#failure-handling)
   - [Trade-offs and Optimizations](#trade-offs-and-optimizations)
9. [What Interviewers Look For](#what-interviewers-look-for)
10. [Summary](#summary)

## Problem Statement

**Design a publish-subscribe messaging system where:**

1. Publishers can send messages to topics
2. Subscribers can listen to topics and receive messages in real-time
3. Messages are ephemeral—lost if no subscribers are currently listening
4. Low-latency delivery to connected subscribers
5. Support for topic management and permissions
6. Handle hot topics with many subscribers
7. Support horizontal scaling

**Scale Requirements:**
- 1M+ concurrent subscribers
- 100K+ topics
- 1M+ messages per second
- < 50ms message delivery latency (P95)
- Support topics with 100K+ subscribers
- Handle connection churn (frequent connect/disconnect)

**Key Characteristics:**
- **Ephemeral Delivery**: Messages only delivered to currently connected subscribers
- **At-Most-Once**: Messages may be lost (no durability)
- **Real-Time**: Low-latency delivery (< 50ms)
- **No Retention**: Messages not stored or replayed
- **Topic-Based**: Messages routed by topic

## Requirements

### Functional Requirements

**Core Features:**
1. **Topic Management**: Create topics, manage permissions (who can publish/subscribe)
2. **Publish Messages**: Publishers send messages to topics
3. **Subscribe to Topics**: Subscribers connect and listen to topics
4. **Unsubscribe**: Subscribers can unsubscribe from topics
5. **Real-Time Delivery**: Messages delivered immediately to connected subscribers
6. **Presence**: See who's subscribed to a topic
7. **Ephemeral Delivery**: Messages dropped if no subscribers connected

**Topic Permissions:**
- **Public**: Anyone can publish/subscribe
- **Private**: Only authorized users can publish/subscribe
- **Publish-Only**: Anyone can publish, only authorized can subscribe
- **Subscribe-Only**: Only authorized can publish, anyone can subscribe

**Out of Scope:**
- Message persistence/durability
- Message replay/history
- Message ordering guarantees (best-effort)
- Message acknowledgments
- Dead letter queues

### Non-Functional Requirements

1. **Availability**: 99.9% uptime
2. **Performance**: 
   - Message delivery latency: < 50ms (P95)
   - Topic creation: < 100ms
   - Subscribe/unsubscribe: < 100ms
3. **Scalability**: Handle 1M+ concurrent subscribers, 1M+ messages/second
4. **Consistency**: Eventually consistent for presence (who's subscribed)
5. **Ephemeral**: No message storage, messages lost if no subscribers
6. **Real-Time**: Messages delivered immediately to connected subscribers

## Capacity Estimation

### Traffic Estimates

- **Concurrent Subscribers**: 1M+
- **Topics**: 100K+
- **Messages per Second**: 1M+ (peak)
- **Average Subscribers per Topic**: 10
- **Hot Topics**: 100K+ subscribers per topic
- **Connection Churn**: 10% per minute (100K connects/disconnects per minute)

### Storage Estimates

**Topic Metadata:**
- 100K topics × 1KB = 100MB
- Topic permissions, settings

**Connection State:**
- 1M connections × 256 bytes = 256MB (in-memory)
- Connection-to-topic mappings

**Presence Data:**
- 1M subscribers × 128 bytes = 128MB (in-memory)
- Who's subscribed to which topics

**Total Storage**: ~500MB (mostly in-memory, no message storage)

## Core Entities

### Topic
- **Attributes**: topic_id, name, owner_id, permissions, created_at, subscriber_count
- **Permissions**: PUBLIC, PRIVATE, PUBLISH_ONLY, SUBSCRIBE_ONLY
- **Relationships**: Has many subscribers, receives many messages

### Subscription
- **Attributes**: subscription_id, topic_id, user_id, subscribed_at, connection_id
- **Relationships**: Links user to topic via connection
- **Purpose**: Track active subscriptions

### Message
- **Attributes**: message_id, topic_id, publisher_id, payload, timestamp
- **Relationships**: Belongs to topic, sent by publisher
- **Purpose**: Ephemeral message (not stored)

### Connection
- **Attributes**: connection_id, user_id, connected_at, last_heartbeat, topics
- **Relationships**: Has many subscriptions
- **Purpose**: WebSocket/SSE connection

## API

### 1. Create Topic
```
POST /api/v1/topics
Headers:
  - Authorization: Bearer <token>
Body:
  - name: string
  - permissions: string (PUBLIC, PRIVATE, PUBLISH_ONLY, SUBSCRIBE_ONLY)
Response:
  - topic_id: string
  - name: string
  - permissions: string
```

### 2. Publish Message
```
POST /api/v1/topics/{topic_id}/publish
Headers:
  - Authorization: Bearer <token>
Body:
  - payload: object (JSON)
Response:
  - message_id: string
  - delivered_to: integer (number of subscribers)
```

### 3. Subscribe to Topic (WebSocket)
```
WS /ws/subscribe?topic_id={topic_id}&token={auth_token}
Messages:
  - Incoming: {"type": "message", "topic_id": "...", "payload": {...}}
  - Incoming: {"type": "presence", "topic_id": "...", "subscribers": [...]}
  - Outgoing: {"type": "subscribe", "topic_id": "..."}
  - Outgoing: {"type": "unsubscribe", "topic_id": "..."}
```

### 4. Subscribe to Topic (SSE)
```
GET /api/v1/topics/{topic_id}/subscribe
Headers:
  - Authorization: Bearer <token>
  - Accept: text/event-stream
Response:
  - Stream of Server-Sent Events
  - data: {"type": "message", "payload": {...}}
```

### 5. Unsubscribe from Topic
```
DELETE /api/v1/topics/{topic_id}/subscribe
Headers:
  - Authorization: Bearer <token>
Response:
  - success: boolean
```

### 6. Get Topic Info
```
GET /api/v1/topics/{topic_id}
Headers:
  - Authorization: Bearer <token>
Response:
  - topic_id: string
  - name: string
  - subscriber_count: integer
  - permissions: string
```

### 7. List Subscriptions
```
GET /api/v1/topics/{topic_id}/subscribers
Headers:
  - Authorization: Bearer <token>
Response:
  - subscribers: array of user objects
  - count: integer
```

## Data Flow

### Publish Message Flow

```
1. Publisher → API Gateway
2. API Gateway → Auth Service (validate token)
3. API Gateway → Pub/Sub Service
4. Pub/Sub Service:
   a. Validate topic exists
   b. Check publish permission
   c. Get list of active subscribers for topic
   d. If no subscribers: Drop message (ephemeral)
   e. If subscribers exist:
      - Create message object
      - Fan-out to all subscriber connections
      - Return delivery count
```

### Subscribe Flow

```
1. Client → WebSocket/SSE Connection
2. Connection Manager:
   a. Authenticate connection
   b. Create connection record
   c. Add subscription to topic
   d. Update topic subscriber count
   e. Send initial presence info
   f. Start delivering messages
```

### Message Delivery Flow

```
1. Publisher publishes message to topic
2. Pub/Sub Service:
   a. Get all active subscriptions for topic
   b. For each subscription:
      - Get connection
      - Check connection is alive (heartbeat)
      - Send message via WebSocket/SSE
   c. If connection dead: Remove subscription
   d. Return delivery count
```

### Unsubscribe Flow

```
1. Client → Unsubscribe request
2. Connection Manager:
   a. Remove subscription from topic
   b. Update topic subscriber count
   c. Stop delivering messages
   d. Return success
```

## High-Level Design

```
┌─────────────────────────────────────────────────────────┐
│                    Publishers                            │
│              (Send Messages to Topics)                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTP POST
                     │
┌────────────────────▼────────────────────────────────────┐
│                  API Gateway / LB                        │
│              (Rate Limiting, Auth)                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     │
┌────────────────────▼────────────────────────────────────┐
│              Pub/Sub Service                            │
│  (Topic Management, Message Routing, Fan-Out)           │
└──────┬───────────────────────────────────┬──────────────┘
       │                                   │
       │                                   │
┌──────▼──────────┐              ┌─────────▼───────────┐
│  Topic Router   │              │  Connection Manager │
│  (Route by Topic)│              │  (WebSocket/SSE)    │
└──────┬──────────┘              └─────────┬───────────┘
       │                                   │
       │                                   │
┌──────▼───────────────────────────────────▼───────────┐
│         Redis Cluster                                  │
│  (Topic Metadata, Subscriptions, Presence)            │
└──────┬─────────────────────────────────────────────────┘
       │
       │
┌──────▼─────────────────────────────────────────────────┐
│         Message Queue (Optional)                      │
│  (For Cross-Server Fan-Out, Hot Topics)                │
└───────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                    Subscribers                          │
│              (WebSocket/SSE Connections)                │
└─────────────────────────────────────────────────────────┘
```

## Deep Dive

### Component Design

#### 1. Pub/Sub Service
- **Responsibilities**: Topic management, message routing, fan-out
- **Optimization**: 
  - Fast topic lookups
  - Efficient subscriber enumeration
  - Message batching for hot topics

#### 2. Topic Router
- **Responsibilities**: Route messages to correct topic handlers
- **Optimization**:
  - Hash-based routing
  - Topic sharding
  - Load balancing

#### 3. Connection Manager
- **Responsibilities**: Manage WebSocket/SSE connections, subscriptions
- **Optimization**:
  - Connection pooling
  - Efficient connection-to-topic mapping
  - Heartbeat management

#### 4. Redis Cluster
- **Topic Metadata**: Topic info, permissions
- **Subscriptions**: Topic → [connection_ids]
- **Presence**: Who's subscribed to which topics
- **Connection State**: Connection info, heartbeat

### Topic Routing

#### Topic Sharding

**Challenge**: Distribute topics across multiple servers.

**Solution**: Hash-based sharding by topic_id

```python
class TopicRouter:
    def __init__(self, num_shards=100):
        self.num_shards = num_shards
        self.shards = [TopicShard(i) for i in range(num_shards)]
    
    def get_shard(self, topic_id):
        """Route topic to shard"""
        shard_index = hash(topic_id) % self.num_shards
        return self.shards[shard_index]
    
    def publish(self, topic_id, message):
        """Route publish to correct shard"""
        shard = self.get_shard(topic_id)
        return shard.publish(topic_id, message)
```

**Benefits:**
- Even distribution of topics
- Independent scaling per shard
- Isolated failures

#### Topic Metadata Storage

**Redis Hash:**
```python
# Topic metadata
topic:{topic_id} = {
    "name": "chat-room-1",
    "owner_id": "user_123",
    "permissions": "PUBLIC",
    "subscriber_count": 1000,
    "created_at": "2025-11-25T10:00:00Z"
}
```

### Connection Management

#### WebSocket Connection

**Connection Lifecycle:**
1. **Connect**: Client opens WebSocket connection
2. **Authenticate**: Validate token, create connection record
3. **Subscribe**: Client subscribes to topics
4. **Heartbeat**: Ping/pong every 30 seconds
5. **Disconnect**: Clean up subscriptions

**Connection Mapping:**
```python
class ConnectionManager:
    def __init__(self):
        self.connections = {}  # connection_id -> Connection
        self.topic_subscriptions = {}  # topic_id -> [connection_ids]
        self.user_connections = {}  # user_id -> [connection_ids]
    
    def add_connection(self, connection_id, user_id, websocket):
        """Add new connection"""
        connection = Connection(
            connection_id=connection_id,
            user_id=user_id,
            websocket=websocket,
            connected_at=now()
        )
        self.connections[connection_id] = connection
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(connection_id)
    
    def subscribe(self, connection_id, topic_id):
        """Subscribe connection to topic"""
        if topic_id not in self.topic_subscriptions:
            self.topic_subscriptions[topic_id] = []
        
        if connection_id not in self.topic_subscriptions[topic_id]:
            self.topic_subscriptions[topic_id].append(connection_id)
        
        # Update Redis
        redis.sadd(f"topic:{topic_id}:subscribers", connection_id)
    
    def unsubscribe(self, connection_id, topic_id):
        """Unsubscribe connection from topic"""
        if topic_id in self.topic_subscriptions:
            self.topic_subscriptions[topic_id].remove(connection_id)
        
        # Update Redis
        redis.srem(f"topic:{topic_id}:subscribers", connection_id)
```

#### Heartbeat Management

**Purpose**: Detect dead connections

**Implementation:**
```python
class ConnectionManager:
    def heartbeat(self, connection_id):
        """Update connection heartbeat"""
        if connection_id in self.connections:
            self.connections[connection_id].last_heartbeat = now()
            redis.setex(
                f"connection:{connection_id}:heartbeat",
                60,  # 60 second TTL
                str(now())
            )
    
    def check_connections(self):
        """Check for dead connections"""
        for connection_id, connection in self.connections.items():
            if now() - connection.last_heartbeat > 60:
                # Connection dead, cleanup
                self.remove_connection(connection_id)
    
    def remove_connection(self, connection_id):
        """Remove dead connection"""
        connection = self.connections[connection_id]
        
        # Unsubscribe from all topics
        for topic_id in connection.subscribed_topics:
            self.unsubscribe(connection_id, topic_id)
        
        # Remove connection
        del self.connections[connection_id]
        self.user_connections[connection.user_id].remove(connection_id)
```

### Message Fan-Out

#### Direct Fan-Out

**For Small Topics (< 1000 subscribers):**
```python
def publish_message(topic_id, message):
    """Publish message to topic"""
    # Get all subscribers
    subscribers = get_topic_subscribers(topic_id)
    
    if not subscribers:
        # No subscribers, drop message (ephemeral)
        return {"delivered_to": 0}
    
    # Fan-out to all subscribers
    delivered = 0
    for connection_id in subscribers:
        connection = get_connection(connection_id)
        if connection and connection.is_alive():
            try:
                connection.send(message)
                delivered += 1
            except:
                # Connection dead, remove subscription
                unsubscribe(connection_id, topic_id)
    
    return {"delivered_to": delivered}
```

#### Distributed Fan-Out (Hot Topics)

**For Large Topics (> 1000 subscribers):**
```python
def publish_message_hot_topic(topic_id, message):
    """Publish to hot topic using message queue"""
    # Publish to Redis pub/sub or Kafka
    redis.publish(f"topic:{topic_id}", json.dumps(message))
    
    # Or use Kafka for better scalability
    kafka.produce(f"topic-{topic_id}", message)
```

**Redis Pub/Sub:**
```python
# Publisher
redis.publish(f"topic:{topic_id}", json.dumps(message))

# Subscriber (each server)
redis_subscriber = redis.pubsub()
redis_subscriber.subscribe(f"topic:{topic_id}")

for message in redis_subscriber.listen():
    # Fan-out to local connections
    fan_out_to_local_connections(topic_id, message)
```

### Ephemeral Delivery

#### No Message Storage

**Key Design**: Messages are never stored, only delivered to active subscribers.

**Implementation:**
```python
def publish_message(topic_id, message):
    """Publish message (ephemeral)"""
    # Get active subscribers
    subscribers = get_active_subscribers(topic_id)
    
    if not subscribers:
        # No subscribers, message is dropped
        return {"delivered_to": 0, "dropped": True}
    
    # Deliver to active subscribers only
    delivered = fan_out_to_subscribers(subscribers, message)
    
    # Message is not stored anywhere
    return {"delivered_to": delivered, "dropped": False}
```

**Benefits:**
- No storage overhead
- Simple implementation
- Low latency (no disk I/O)

**Trade-offs:**
- Messages lost if no subscribers
- No message replay
- No durability guarantees

### Hot-Topic Handling

#### Challenge
Topics with 100K+ subscribers create fan-out bottlenecks.

#### Solution: Multi-Level Fan-Out

**Approach 1: Redis Pub/Sub**
```python
# Publisher publishes to Redis channel
redis.publish(f"topic:{topic_id}", message)

# Each server subscribes to Redis channel
# Then fans out to local connections
redis_subscriber.subscribe(f"topic:{topic_id}")
for message in redis_subscriber.listen():
    local_subscribers = get_local_subscribers(topic_id)
    fan_out_to_connections(local_subscribers, message)
```

**Approach 2: Kafka Topics**
```python
# Publisher publishes to Kafka topic
kafka.produce(f"pubsub-topic-{topic_id}", message)

# Each server consumes from Kafka
# Then fans out to local connections
for message in kafka.consume(f"pubsub-topic-{topic_id}"):
    local_subscribers = get_local_subscribers(topic_id)
    fan_out_to_connections(local_subscribers, message)
```

**Approach 3: Topic Partitioning**
```python
# Partition hot topic across multiple servers
def get_subscriber_shard(topic_id, connection_id):
    """Route subscriber to shard"""
    return hash(f"{topic_id}:{connection_id}") % num_shards

# Each shard handles subset of subscribers
# Publisher sends to all shards
for shard in range(num_shards):
    shard_connections = get_shard_subscribers(topic_id, shard)
    fan_out_to_connections(shard_connections, message)
```

### Backpressure

#### Challenge
Subscribers can't keep up with message rate.

#### Solution: Connection-Level Backpressure

**WebSocket Backpressure:**
```python
class Connection:
    def __init__(self):
        self.send_queue = queue.Queue(maxsize=1000)
        self.is_ready = True
    
    def send(self, message):
        """Send message with backpressure"""
        try:
            self.send_queue.put_nowait(message)
            if self.is_ready:
                self.flush_queue()
        except queue.Full:
            # Queue full, drop message or disconnect
            self.handle_backpressure()
    
    def flush_queue(self):
        """Flush queued messages"""
        self.is_ready = False
        while not self.send_queue.empty():
            message = self.send_queue.get()
            try:
                self.websocket.send(message)
            except:
                # Connection dead, stop flushing
                return
        self.is_ready = True
```

**Server-Level Backpressure:**
```python
def publish_message(topic_id, message):
    """Publish with server-level backpressure"""
    subscribers = get_topic_subscribers(topic_id)
    
    # Check server load
    if server_load > 0.8:
        # High load, drop low-priority messages
        if message.priority == "LOW":
            return {"delivered_to": 0, "dropped": "backpressure"}
    
    # Fan-out with rate limiting
    delivered = 0
    for connection_id in subscribers:
        connection = get_connection(connection_id)
        if connection and connection.can_send():
            connection.send(message)
            delivered += 1
    
    return {"delivered_to": delivered}
```

### Protocols

#### WebSocket

**Advantages:**
- Full-duplex communication
- Low overhead
- Binary support

**Implementation:**
```python
# Server
import websockets

async def handle_websocket(websocket, path):
    connection_id = generate_id()
    user_id = authenticate(websocket)
    
    connection_manager.add_connection(connection_id, user_id, websocket)
    
    try:
        async for message in websocket:
            data = json.loads(message)
            if data['type'] == 'subscribe':
                connection_manager.subscribe(connection_id, data['topic_id'])
            elif data['type'] == 'unsubscribe':
                connection_manager.unsubscribe(connection_id, data['topic_id'])
    except websockets.exceptions.ConnectionClosed:
        connection_manager.remove_connection(connection_id)
```

#### Server-Sent Events (SSE)

**Advantages:**
- Simpler than WebSocket
- Automatic reconnection
- HTTP-based

**Implementation:**
```python
# Server
from flask import Response, stream_with_context

@app.route('/api/v1/topics/<topic_id>/subscribe')
def subscribe_sse(topic_id):
    user_id = authenticate(request)
    
    def event_stream():
        connection_id = generate_id()
        connection_manager.add_connection(connection_id, user_id, None)
        connection_manager.subscribe(connection_id, topic_id)
        
        try:
            while True:
                # Get messages for this topic
                message = message_queue.get(topic_id, connection_id)
                yield f"data: {json.dumps(message)}\n\n"
        except GeneratorExit:
            connection_manager.remove_connection(connection_id)
    
    return Response(stream_with_context(event_stream()), 
                   mimetype='text/event-stream')
```

### Failure Handling

#### Connection Failures

**Scenario**: Connection drops during message delivery.

**Solution:**
- Detect dead connections via heartbeat
- Remove subscription on disconnect
- Continue delivering to other subscribers

#### Server Failures

**Scenario**: Server crashes, connections lost.

**Solution:**
- Clients reconnect automatically
- Re-subscribe to topics on reconnect
- Load balancer routes to healthy servers

#### Topic Shard Failures

**Scenario**: Shard handling topic fails.

**Solution:**
- Failover to replica shard
- Re-route topic to different shard
- Clients reconnect and re-subscribe

### Trade-offs and Optimizations

#### Trade-offs

1. **Durability vs Latency**
   - **Choice**: Ephemeral (no durability)
   - **Reason**: Low latency, simplicity
   - **Benefit**: Fast delivery, no storage overhead

2. **At-Most-Once vs At-Least-Once**
   - **Choice**: At-most-once (may lose messages)
   - **Reason**: Simpler, no deduplication needed
   - **Benefit**: Lower latency, simpler implementation

3. **Ordering vs Performance**
   - **Choice**: Best-effort ordering
   - **Reason**: Performance over strict ordering
   - **Benefit**: Better throughput, lower latency

#### Optimizations

1. **Message Batching**
   - Batch multiple messages for same topic
   - Reduce WebSocket overhead
   - Better throughput

2. **Connection Pooling**
   - Reuse WebSocket connections
   - Reduce connection overhead
   - Better resource utilization

3. **Topic Sharding**
   - Distribute topics across servers
   - Better load distribution
   - Isolated failures

4. **Caching**
   - Cache topic metadata
   - Cache subscription lists
   - Reduce database queries

## What Interviewers Look For

### Distributed Systems Skills

1. **Low-Latency Fan-Out**
   - Efficient message distribution
   - Direct fan-out for small topics
   - Distributed fan-out for hot topics
   - **Red Flags**: Inefficient fan-out, no hot-topic handling, high latency

2. **Connection Management**
   - WebSocket/SSE connection handling
   - Heartbeat management
   - Connection lifecycle
   - **Red Flags**: No heartbeat, dead connections, poor lifecycle management

3. **Ephemeral Delivery**
   - No message storage
   - Drop messages if no subscribers
   - Clear delivery guarantees
   - **Red Flags**: Storing messages, durability, over-engineering

### Problem-Solving Approach

1. **Trade-off Awareness**
   - At-most-once vs at-least-once
   - Durability vs latency
   - Ordering vs performance
   - **Red Flags**: No trade-offs, wrong trade-offs, over-engineering

2. **Hot-Topic Handling**
   - Recognize hot topics
   - Multi-level fan-out
   - Topic partitioning
   - **Red Flags**: No hot-topic handling, single-level fan-out, bottlenecks

3. **Backpressure**
   - Connection-level backpressure
   - Server-level backpressure
   - Message dropping strategies
   - **Red Flags**: No backpressure, resource exhaustion, no dropping

### System Design Skills

1. **Component Design**
   - Clear service boundaries
   - Proper abstractions
   - Efficient interfaces
   - **Red Flags**: Monolithic design, poor abstractions, inefficient APIs

2. **Scalability**
   - Horizontal scaling
   - Topic sharding
   - Load balancing
   - **Red Flags**: Vertical scaling only, no sharding, no load balancing

3. **Protocols**
   - WebSocket vs SSE trade-offs
   - Protocol selection
   - Implementation details
   - **Red Flags**: Wrong protocol, no protocol choice, poor implementation

### Communication Skills

1. **Clear Explanation**
   - Explains ephemeral delivery
   - Discusses trade-offs
   - Justifies design decisions
   - **Red Flags**: Unclear explanations, no justification, confusing

2. **Architecture Diagrams**
   - Clear component diagram
   - Shows message flow
   - Fan-out architecture
   - **Red Flags**: No diagrams, unclear diagrams, missing components

### Meta-Specific Focus

1. **Real-Time Systems**
   - Understanding of low-latency requirements
   - WebSocket expertise
   - Connection management
   - **Key**: Demonstrate real-time systems expertise

2. **Pub/Sub Patterns**
   - Topic-based routing
   - Message fan-out
   - Ephemeral delivery
   - **Key**: Show pub/sub pattern mastery

3. **Production-Grade Robustness**
   - Failure handling
   - Backpressure
   - Hot-topic handling
   - **Key**: Demonstrate production thinking

## Summary

Designing a pub/sub system requires careful consideration of ephemeral delivery, low-latency fan-out, connection management, and horizontal scaling. Key design decisions include:

**Architecture Highlights:**
- Topic-based routing with hash-based sharding
- WebSocket/SSE for real-time delivery
- Ephemeral message delivery (no storage)
- Multi-level fan-out for hot topics
- Connection management with heartbeat

**Key Patterns:**
- **Ephemeral Delivery**: Messages dropped if no subscribers
- **At-Most-Once**: No durability, messages may be lost
- **Topic Routing**: Hash-based sharding for scalability
- **Connection Management**: WebSocket/SSE with heartbeat
- **Hot-Topic Handling**: Multi-level fan-out (Redis/Kafka)

**Scalability Solutions:**
- Horizontal scaling (multiple servers)
- Topic sharding (distribute topics)
- Connection pooling (efficient connections)
- Message queue for cross-server fan-out

**Trade-offs:**
- Durability vs latency (ephemeral for low latency)
- At-most-once vs at-least-once (at-most-once for simplicity)
- Ordering vs performance (best-effort ordering)

This design handles 1M+ concurrent subscribers, 1M+ messages/second, and maintains < 50ms message delivery latency while ensuring messages are ephemeral and dropped if no subscribers are listening. The system is scalable, fault-tolerant, and optimized for real-time pub/sub messaging.

