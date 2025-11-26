---
layout: post
title: "Design a Chat System (Messenger/WhatsApp) - System Design Interview"
date: 2025-11-14
categories: [System Design, Interview Example, Distributed Systems, Real-time Systems, Social Media]
excerpt: "A comprehensive guide to designing a chat system like Messenger or WhatsApp, covering real-time messaging, message delivery guarantees, presence management, group chats, media sharing, scalability challenges, and architectural patterns for handling billions of messages per day."
---

## Introduction

A chat system enables real-time communication between users through text messages, media files, and group conversations. Systems like Facebook Messenger and WhatsApp handle billions of messages per day, requiring low-latency message delivery, high availability, and efficient resource utilization.

This post provides a detailed walkthrough of designing a scalable chat system, covering key architectural decisions, real-time communication patterns, message delivery guarantees, and scalability challenges. This is one of the most common system design interview questions that tests your understanding of distributed systems, WebSocket connections, message queues, and real-time data synchronization.

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

**Design a chat system similar to Messenger or WhatsApp with the following features:**

1. One-on-one messaging between users
2. Group messaging (up to 256 members)
3. Real-time message delivery
4. Message status indicators (sent, delivered, read)
5. Typing indicators
6. Online/offline presence
7. Media sharing (photos, videos, files)
8. Push notifications for offline users
9. Message history and search
10. End-to-end encryption (optional)

**Scale Requirements:**
- 1 billion+ users
- 500 million+ daily active users
- 100 billion+ messages per day
- Average message size: 100 bytes (text), 1MB (media)
- 50% of messages are one-on-one, 50% are group messages
- Average group size: 10 members
- Peak QPS: 1 million messages per second

## Requirements

### Functional Requirements

**Core Features:**
1. **User Management**: Registration, authentication, user profiles
2. **One-on-One Messaging**: Send and receive messages between two users
3. **Group Messaging**: Create groups, add/remove members, send group messages
4. **Real-Time Delivery**: Messages delivered instantly when recipient is online
5. **Message Status**: Show sent, delivered, and read status
6. **Presence Management**: Show online/offline status, last seen
7. **Typing Indicators**: Show when someone is typing
8. **Media Sharing**: Send photos, videos, files (up to 100MB)
9. **Push Notifications**: Notify offline users of new messages
10. **Message History**: Store and retrieve message history
11. **Search**: Search messages by content, sender, date
12. **Message Reactions**: Emoji reactions to messages

**Out of Scope:**
- Voice/video calls
- Stories/status updates
- Payment integration
- Advanced encryption (assume TLS for transport)
- Message editing/deletion after sending
- Message forwarding

### Non-Functional Requirements

1. **Availability**: 99.9% uptime
2. **Reliability**: No message loss, guaranteed delivery
3. **Performance**: 
   - Message delivery latency: < 100ms (online users)
   - Message delivery latency: < 5 seconds (offline users via push)
   - Typing indicator latency: < 50ms
4. **Scalability**: Handle 100B+ messages per day
5. **Consistency**: Eventually consistent is acceptable for presence
6. **Durability**: All messages must be persisted
7. **Real-Time**: Messages must appear instantly for online users

## Capacity Estimation

### Traffic Estimates

- **Daily Active Users (DAU)**: 500 million
- **Daily messages**: 100 billion
- **Average messages per user per day**: 200 messages
- **Peak QPS**: 1 million messages/second (assuming 10x average)
- **Read:Write ratio**: 1:1 (users read as many messages as they send)
- **Online users at peak**: 50% of DAU = 250 million
- **Concurrent connections**: 250 million WebSocket connections

### Storage Estimates

**Message Storage:**
- 100 billion messages/day
- Average text message: 100 bytes
- Average media message: 1MB
- Assume 80% text, 20% media
- Daily text storage: 100B × 0.8 × 100 bytes = 8TB
- Daily media storage: 100B × 0.2 × 1MB = 20PB
- Total daily storage: ~20PB
- 5-year retention: 20PB × 365 × 5 = ~36.5 exabytes

**Metadata Storage:**
- User metadata: 1B users × 1KB = 1TB
- Group metadata: 100M groups × 2KB = 200GB
- Presence data: 500M users × 100 bytes = 50GB
- Total metadata: ~1.25TB

### Bandwidth Estimates

**Incoming (Write):**
- 1M QPS × 100 bytes (average) = 100MB/s = 800Mbps
- Peak with media: 1M QPS × 1MB = 1TB/s = 8Tbps

**Outgoing (Read):**
- For one-on-one: 1 message sent to 1 recipient = 1M QPS
- For group (avg 10 members): 1 message sent to 10 recipients = 10M QPS
- Assume 50% one-on-one, 50% group
- Average fan-out: 0.5 × 1 + 0.5 × 10 = 5.5
- Outgoing QPS: 1M × 5.5 = 5.5M QPS
- Bandwidth: 5.5M QPS × 100 bytes = 550MB/s = 4.4Gbps
- Peak with media: 5.5M QPS × 1MB = 5.5TB/s = 44Tbps

## Core Entities

### User
- `user_id` (UUID)
- `username`
- `email`
- `phone_number`
- `profile_picture_url`
- `status` (online, offline, away)
- `last_seen_timestamp`
- `created_at`

### Conversation
- `conversation_id` (UUID)
- `type` (one_on_one, group)
- `participants` (array of user_ids)
- `created_at`
- `updated_at`
- `last_message_id`
- `last_message_timestamp`

### Message
- `message_id` (UUID)
- `conversation_id`
- `sender_id`
- `content` (text or media URL)
- `content_type` (text, image, video, file)
- `media_url` (for media messages)
- `created_at`
- `sequence_number` (for ordering)

### Message Status
- `message_id`
- `user_id` (recipient)
- `status` (sent, delivered, read)
- `timestamp`

### Group
- `group_id` (UUID)
- `name`
- `description`
- `creator_id`
- `members` (array of user_ids)
- `created_at`
- `updated_at`

### Typing Indicator
- `conversation_id`
- `user_id`
- `is_typing` (boolean)
- `timestamp`

## API

### 1. Send Message
```
POST /api/v1/conversations/{conversation_id}/messages
Request:
{
  "content": "Hello!",
  "content_type": "text"
}

Response:
{
  "message_id": "uuid",
  "conversation_id": "uuid",
  "sender_id": "uuid",
  "content": "Hello!",
  "created_at": "2025-11-13T10:00:00Z",
  "sequence_number": 12345
}
```

### 2. Get Messages
```
GET /api/v1/conversations/{conversation_id}/messages?limit=50&before={message_id}
Response:
{
  "messages": [
    {
      "message_id": "uuid",
      "sender_id": "uuid",
      "content": "Hello!",
      "created_at": "2025-11-13T10:00:00Z",
      "sequence_number": 12345
    }
  ],
  "has_more": true
}
```

### 3. Update Message Status
```
PUT /api/v1/messages/{message_id}/status
Request:
{
  "status": "read"
}
```

### 4. Send Typing Indicator
```
POST /api/v1/conversations/{conversation_id}/typing
Request:
{
  "is_typing": true
}
```

### 5. Update Presence
```
PUT /api/v1/users/{user_id}/presence
Request:
{
  "status": "online"
}
```

### 6. Create Group
```
POST /api/v1/groups
Request:
{
  "name": "Family Group",
  "member_ids": ["user1", "user2", "user3"]
}
```

### 7. Search Messages
```
GET /api/v1/conversations/{conversation_id}/search?query=hello&limit=20
```

### 8. WebSocket Connection
```
WS /ws?user_id={user_id}&token={auth_token}
Messages:
- Incoming: {"type": "message", "data": {...}}
- Outgoing: {"type": "typing", "data": {...}}
- Presence: {"type": "presence", "data": {...}}
```

## Data Flow

### Message Send Flow

1. **Client** sends message via HTTP POST to **API Gateway**
2. **API Gateway** authenticates request and routes to **Message Service**
3. **Message Service**:
   - Validates conversation and permissions
   - Generates message_id and sequence_number
   - Stores message in **Message DB** (sharded by conversation_id)
   - Publishes message to **Message Queue** (Kafka)
4. **Message Queue** distributes message to **Delivery Service** workers
5. **Delivery Service**:
   - Checks if recipient is online (via **Presence Service**)
   - If online: Pushes message via **WebSocket Service**
   - If offline: Queues for **Push Notification Service**
6. **WebSocket Service** delivers message to recipient's connected client
7. **Push Notification Service** sends push notification to recipient's device

### Message Receive Flow (Real-Time)

1. **Client** maintains persistent WebSocket connection to **WebSocket Service**
2. **WebSocket Service** maintains connection pool and user-to-connection mapping
3. When message arrives via **Message Queue**:
   - **Delivery Service** looks up recipient's WebSocket connection
   - Pushes message through WebSocket connection
4. **Client** receives message and displays it
5. **Client** sends acknowledgment (delivered status)
6. **Client** sends read receipt when user views message

### Typing Indicator Flow

1. **Client** detects user typing and sends typing indicator via WebSocket
2. **WebSocket Service** forwards to **Typing Service**
3. **Typing Service** broadcasts typing indicator to all other participants in conversation
4. **WebSocket Service** pushes typing indicator to other participants' clients
5. Typing indicator expires after 3 seconds of inactivity

### Presence Update Flow

1. **Client** connects/disconnects WebSocket
2. **WebSocket Service** notifies **Presence Service** of connection status
3. **Presence Service** updates user's presence in **Presence Cache** (Redis)
4. **Presence Service** broadcasts presence update to user's contacts
5. **WebSocket Service** pushes presence updates to connected clients

## Database Design

### Schema Design

**Users Table:**
```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone_number VARCHAR(20) UNIQUE,
    profile_picture_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_username (username),
    INDEX idx_email (email)
);
```

**Conversations Table:**
```sql
CREATE TABLE conversations (
    conversation_id UUID PRIMARY KEY,
    type ENUM('one_on_one', 'group') NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_message_id UUID,
    last_message_timestamp TIMESTAMP,
    INDEX idx_last_message_timestamp (last_message_timestamp DESC)
);
```

**Conversation Participants Table:**
```sql
CREATE TABLE conversation_participants (
    conversation_id UUID,
    user_id UUID,
    joined_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (conversation_id, user_id),
    INDEX idx_user_id (user_id)
);
```

**Messages Table (Sharded by conversation_id):**
```sql
CREATE TABLE messages_0 (
    message_id UUID PRIMARY KEY,
    conversation_id UUID NOT NULL,
    sender_id UUID NOT NULL,
    content TEXT,
    content_type ENUM('text', 'image', 'video', 'file') DEFAULT 'text',
    media_url VARCHAR(500),
    sequence_number BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_conversation_sequence (conversation_id, sequence_number DESC),
    INDEX idx_created_at (created_at DESC)
);
-- Similar tables: messages_1, messages_2, ..., messages_N
```

**Message Status Table:**
```sql
CREATE TABLE message_status (
    message_id UUID,
    user_id UUID,
    status ENUM('sent', 'delivered', 'read') DEFAULT 'sent',
    timestamp TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (message_id, user_id),
    INDEX idx_user_status (user_id, status, timestamp DESC)
);
```

**Groups Table:**
```sql
CREATE TABLE groups (
    group_id UUID PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    creator_id UUID NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Group Members Table:**
```sql
CREATE TABLE group_members (
    group_id UUID,
    user_id UUID,
    role ENUM('admin', 'member') DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (group_id, user_id),
    INDEX idx_user_id (user_id)
);
```

### Database Sharding Strategy

**Messages Table Sharding:**
- Shard by `conversation_id` using consistent hashing
- 1000 shards: `shard_id = hash(conversation_id) % 1000`
- Each shard handles ~100M conversations
- Enables parallel reads/writes and horizontal scaling

**Shard Key Selection:**
- `conversation_id` ensures all messages for a conversation are in the same shard
- Enables efficient querying of conversation history
- Prevents cross-shard queries for single conversation

**Replication:**
- Each shard replicated 3x for high availability
- Master-replica setup for read scaling
- Writes go to master, reads can go to replicas

**Indexing Strategy:**
- Primary index on `message_id` for direct lookups
- Composite index on `(conversation_id, sequence_number)` for conversation queries
- Index on `created_at` for time-based queries

## High-Level Design

```
┌─────────────┐
│   Client    │
│  (Mobile/   │
│   Web)      │
└──────┬──────┘
       │
       │ HTTP/WebSocket
       │
┌──────▼──────────────────────────────────────────────┐
│              API Gateway / Load Balancer            │
└──────┬──────────────────────────────────────────────┘
       │
       ├─────────────────┬──────────────────┐
       │                 │                  │
┌──────▼──────┐  ┌───────▼──────┐  ┌───────▼──────┐
│   Message   │  │   Presence   │  │   Group     │
│   Service   │  │   Service    │  │   Service   │
└──────┬──────┘  └───────┬──────┘  └───────┬──────┘
       │                 │                  │
       │                 │                  │
┌──────▼─────────────────▼──────────────────▼──────┐
│              Message Queue (Kafka)                 │
└──────┬─────────────────────────────────────────────┘
       │
       │
┌──────▼────────────────────────────────────────────┐
│            Delivery Service (Workers)              │
└──────┬─────────────────────────────────────────────┘
       │
       ├──────────────────┬─────────────────────┐
       │                  │                     │
┌──────▼──────┐  ┌────────▼────────┐  ┌────────▼────────┐
│  WebSocket │  │   Push          │  │   Message       │
│  Service   │  │   Notification  │  │   Storage       │
│            │  │   Service       │  │   Service       │
└──────┬──────┘  └────────────────┘  └────────┬────────┘
       │                                       │
       │                                       │
┌──────▼───────────────────────────────────────▼──────┐
│         Database Cluster (Sharded)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ Shard 0   │  │ Shard 1   │  │ Shard N   │        │
│  │ Messages  │  │ Messages  │  │ Messages  │        │
│  └──────────┘  └──────────┘  └──────────┘        │
└────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│              Cache Layer (Redis)                     │
│  - Presence Cache                                   │
│  - Typing Indicators                                 │
│  - Recent Messages                                  │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│         Object Storage (S3)                         │
│  - Media Files (Images, Videos, Files)              │
└─────────────────────────────────────────────────────┘
```

## Deep Dive

### Component Design

#### 1. Message Service

**Responsibilities:**
- Validate message requests
- Generate message IDs and sequence numbers
- Store messages in database
- Publish messages to message queue

**Key Design Decisions:**
- **Sequence Numbers**: Use distributed sequence generator (Snowflake ID or database sequences per shard)
- **Idempotency**: Use message_id as idempotency key to prevent duplicates
- **Validation**: Check conversation exists, user is participant, rate limiting

**Scalability:**
- Stateless service, horizontally scalable
- Connection pooling for database access
- Async message publishing to Kafka

#### 2. WebSocket Service

**Responsibilities:**
- Maintain persistent WebSocket connections
- Route messages to correct connections
- Handle connection lifecycle (connect, disconnect, reconnect)
- Manage connection-to-user mapping

**Key Design Decisions:**
- **Connection Mapping**: Use Redis to map user_id → [connection_ids]
- **Load Balancing**: Use sticky sessions (user_id-based routing) to ensure same server
- **Connection Pool**: Each server handles ~100K concurrent connections
- **Heartbeat**: Ping/pong every 30 seconds to detect dead connections

**Scalability:**
- Horizontal scaling with consistent hashing for user routing
- Redis pub/sub for cross-server message routing
- Connection limits per server to prevent overload

#### 3. Delivery Service

**Responsibilities:**
- Consume messages from Kafka
- Check recipient presence
- Route to WebSocket or Push Notification service
- Update message delivery status

**Key Design Decisions:**
- **Worker Pool**: Multiple workers consuming from Kafka partitions
- **Presence Check**: Query Presence Service (Redis cache)
- **Fan-out Logic**: Handle group message fan-out efficiently
- **Retry Logic**: Retry failed deliveries with exponential backoff

**Scalability:**
- Horizontal scaling with Kafka consumer groups
- Parallel processing of messages
- Batch processing for efficiency

#### 4. Presence Service

**Responsibilities:**
- Track user online/offline status
- Update last seen timestamp
- Broadcast presence changes to contacts
- Cache presence data

**Key Design Decisions:**
- **Redis Cache**: Store presence data with TTL
- **Heartbeat**: Update presence every 30 seconds when online
- **Offline Detection**: Mark offline after 2 minutes of no heartbeat
- **Contact List**: Maintain user's contact list for presence broadcasting

**Scalability:**
- Redis cluster for high availability
- Efficient caching strategy
- Batch updates for contact presence queries

#### 5. Push Notification Service

**Responsibilities:**
- Send push notifications to offline users
- Support multiple platforms (iOS, Android, Web)
- Handle notification batching and rate limiting
- Track delivery status

**Key Design Decisions:**
- **Platform Integration**: Integrate with FCM (Android), APNs (iOS)
- **Batching**: Batch notifications for same user
- **Rate Limiting**: Respect platform rate limits
- **Retry Logic**: Retry failed notifications

**Scalability:**
- Horizontal scaling with worker pools
- Queue-based processing
- Platform-specific rate limiting

### Detailed Design

#### Message Ordering

**Challenge:** Ensure messages appear in correct order despite distributed processing

**Solution:**
- **Sequence Numbers**: Assign monotonically increasing sequence numbers per conversation
- **Client-side Ordering**: Client sorts messages by sequence_number before display
- **Gap Detection**: Client detects gaps and requests missing messages
- **Database Ordering**: Messages stored with sequence_number, queries ordered by sequence_number

**Implementation:**
```python
def send_message(conversation_id, sender_id, content):
    # Get next sequence number for conversation
    sequence_number = get_next_sequence_number(conversation_id)
    
    # Create message
    message = {
        'message_id': generate_uuid(),
        'conversation_id': conversation_id,
        'sender_id': sender_id,
        'content': content,
        'sequence_number': sequence_number,
        'created_at': now()
    }
    
    # Store in database
    store_message(message)
    
    # Publish to queue
    publish_to_kafka(message)
    
    return message
```

#### Message Delivery Guarantees

**Requirements:**
- At-least-once delivery (messages may be delivered multiple times)
- Exactly-once processing (duplicate messages handled idempotently)

**Implementation:**
- **Idempotency Key**: Use message_id as idempotency key
- **Deduplication**: Check if message already processed before storing
- **Acknowledgments**: Client acknowledges message receipt
- **Retry Logic**: Retry unacknowledged messages

#### Typing Indicators

**Challenge:** Show typing status in real-time without overwhelming system

**Solution:**
- **Redis Cache**: Store typing indicators with 3-second TTL
- **Throttling**: Update typing indicator max once per second
- **Broadcast**: Broadcast to conversation participants via WebSocket
- **Cleanup**: Auto-expire after 3 seconds of inactivity

**Implementation:**
```python
def update_typing_indicator(conversation_id, user_id, is_typing):
    key = f"typing:{conversation_id}:{user_id}"
    
    if is_typing:
        # Set typing indicator with 3-second TTL
        redis.setex(key, 3, "typing")
        
        # Get conversation participants
        participants = get_conversation_participants(conversation_id)
        
        # Broadcast to other participants
        for participant_id in participants:
            if participant_id != user_id:
                send_websocket_message(participant_id, {
                    'type': 'typing',
                    'conversation_id': conversation_id,
                    'user_id': user_id,
                    'is_typing': True
                })
    else:
        # Remove typing indicator
        redis.delete(key)
```

#### Media Handling

**Challenge:** Handle large media files efficiently

**Solution:**
- **Upload Flow**: Client uploads media to Object Storage (S3) via presigned URL
- **Processing**: Async processing for video thumbnails, image resizing
- **CDN**: Serve media via CDN for fast delivery
- **Message Reference**: Store media URL in message, not actual file

**Implementation:**
```python
def send_media_message(conversation_id, sender_id, media_file):
    # Upload to S3
    media_url = upload_to_s3(media_file)
    
    # Generate thumbnail (async)
    thumbnail_url = generate_thumbnail_async(media_url)
    
    # Create message with media URL
    message = {
        'message_id': generate_uuid(),
        'conversation_id': conversation_id,
        'sender_id': sender_id,
        'content_type': 'image',
        'media_url': media_url,
        'thumbnail_url': thumbnail_url,
        'sequence_number': get_next_sequence_number(conversation_id)
    }
    
    # Store and publish
    store_message(message)
    publish_to_kafka(message)
    
    return message
```

#### Group Message Fan-out

**Challenge:** Efficiently deliver group messages to all members

**Solution:**
- **Fan-out at Delivery**: Fan-out happens at delivery service, not message service
- **Parallel Delivery**: Deliver to all members in parallel
- **Member Caching**: Cache group members in Redis
- **Batch Processing**: Process multiple group messages in batch

**Implementation:**
```python
def deliver_group_message(message):
    conversation_id = message['conversation_id']
    
    # Get group members from cache or database
    members = get_group_members(conversation_id)
    
    # Deliver to all members in parallel
    delivery_tasks = []
    for member_id in members:
        if member_id != message['sender_id']:
            task = deliver_to_user(member_id, message)
            delivery_tasks.append(task)
    
    # Wait for all deliveries
    asyncio.gather(*delivery_tasks)
```

### Scalability Considerations

#### Horizontal Scaling

**WebSocket Service:**
- Scale horizontally with consistent hashing
- Each server handles subset of users based on user_id hash
- Redis pub/sub for cross-server communication

**Message Service:**
- Stateless service, scale horizontally
- Load balancer distributes requests
- Database connection pooling

**Database:**
- Shard messages table by conversation_id
- Read replicas for read scaling
- Connection pooling and query optimization

#### Caching Strategy

**Redis Cache:**
- **Presence Data**: TTL 2 minutes
- **Typing Indicators**: TTL 3 seconds
- **Recent Messages**: Cache last 50 messages per conversation
- **Group Members**: Cache group membership with 5-minute TTL
- **User Metadata**: Cache user profiles with 1-hour TTL

**Cache Invalidation:**
- Invalidate on updates
- Use cache-aside pattern
- Handle cache misses gracefully

#### Load Balancing

**WebSocket Connections:**
- Sticky sessions based on user_id
- Consistent hashing for user routing
- Health checks for connection servers

**HTTP Requests:**
- Round-robin or least-connections
- Health checks
- Circuit breakers for failing services

#### Database Optimization

**Indexing:**
- Index on (conversation_id, sequence_number) for message queries
- Index on created_at for time-based queries
- Index on user_id for user-related queries

**Query Optimization:**
- Pagination for large result sets
- Limit query result sizes
- Use covering indexes where possible

**Connection Management:**
- Connection pooling
- Read replicas for read-heavy workloads
- Query timeouts and retries

### Security Considerations

#### Authentication & Authorization

- **JWT Tokens**: Use JWT for API authentication
- **WebSocket Auth**: Authenticate WebSocket connections with token
- **Rate Limiting**: Limit requests per user/IP
- **Permission Checks**: Verify user is conversation participant before sending messages

#### Data Privacy

- **Encryption in Transit**: TLS for all communications
- **Encryption at Rest**: Encrypt sensitive data in database
- **Access Control**: Users can only access their own conversations
- **Data Retention**: Implement data retention policies

#### Input Validation

- **Content Validation**: Validate message content, prevent XSS
- **File Validation**: Validate file types and sizes
- **Rate Limiting**: Prevent spam and abuse
- **Content Moderation**: Optional content filtering

### Monitoring & Observability

#### Key Metrics

**System Metrics:**
- Message throughput (messages/second)
- Message delivery latency (p50, p95, p99)
- WebSocket connection count
- Database query latency
- Cache hit rate

**Business Metrics:**
- Daily active users
- Messages sent per user
- Group message participation
- Media sharing rate

#### Logging

- **Structured Logging**: JSON logs for easy parsing
- **Request Tracing**: Trace requests across services
- **Error Logging**: Log errors with context
- **Audit Logging**: Log important actions (message sends, group creation)

#### Alerting

- **High Latency**: Alert if p95 latency > 500ms
- **High Error Rate**: Alert if error rate > 1%
- **Connection Failures**: Alert if connection failure rate > 5%
- **Database Issues**: Alert on database errors or high latency

### Trade-offs and Optimizations

#### Trade-offs

**1. WebSocket vs HTTP Long Polling**
- **WebSocket**: Lower latency, persistent connection, better for real-time
- **Long Polling**: Simpler, works through firewalls, but higher latency
- **Decision**: Use WebSocket for online users, HTTP for initial connection

**2. Message Ordering: Sequence Numbers vs Timestamps**
- **Sequence Numbers**: Guaranteed ordering, but requires coordination
- **Timestamps**: Simpler, but clock skew can cause issues
- **Decision**: Use sequence numbers for guaranteed ordering

**3. Push Notifications: Immediate vs Batched**
- **Immediate**: Lower latency, but higher battery usage
- **Batched**: Better battery life, but higher latency
- **Decision**: Immediate for important messages, batched for less critical

**4. Message Storage: Hot vs Cold**
- **Hot Storage**: Fast access, but expensive
- **Cold Storage**: Cheap, but slower access
- **Decision**: Hot storage for recent messages, cold storage for old messages

#### Optimizations

**1. Message Batching**
- Batch multiple messages in single WebSocket frame
- Reduce network overhead
- Improve throughput

**2. Connection Pooling**
- Reuse database connections
- Reduce connection overhead
- Improve performance

**3. Read Replicas**
- Use read replicas for read-heavy queries
- Reduce load on primary database
- Improve read performance

**4. CDN for Media**
- Serve media files via CDN
- Reduce server load
- Improve delivery speed

**5. Compression**
- Compress WebSocket messages
- Reduce bandwidth usage
- Improve performance

## What Interviewers Look For

### Real-Time Systems Skills

1. **WebSocket Architecture**
   - Connection management
   - Message routing
   - Connection pooling
   - **Red Flags**: HTTP polling, poor connection management, no routing

2. **Message Ordering**
   - Sequence number design
   - Ordering guarantees
   - Handling out-of-order messages
   - **Red Flags**: No ordering, race conditions, incorrect ordering

3. **Presence Management**
   - Online/offline tracking
   - Typing indicators
   - Efficient broadcasting
   - **Red Flags**: No presence, inefficient updates, high overhead

### Distributed Systems Skills

1. **Message Queue Design**
   - Kafka/Message queue usage
   - Topic partitioning
   - Consumer groups
   - **Red Flags**: No message queue, poor partitioning, no consumer groups

2. **Database Sharding**
   - Sharding strategy
   - Message distribution
   - Cross-shard queries
   - **Red Flags**: No sharding, poor strategy, inefficient queries

3. **Scalability Design**
   - Horizontal scaling
   - Load balancing
   - Service decomposition
   - **Red Flags**: Vertical scaling only, bottlenecks, monolithic design

### Problem-Solving Approach

1. **Message Delivery Guarantees**
   - At-least-once vs exactly-once
   - Delivery confirmation
   - Retry mechanisms
   - **Red Flags**: No guarantees, message loss, no retry

2. **Edge Cases**
   - Offline users
   - Group messaging
   - Message failures
   - **Red Flags**: Ignoring edge cases, no offline handling

3. **Trade-off Analysis**
   - Consistency vs latency
   - Storage vs performance
   - **Red Flags**: No trade-off discussion

### System Design Skills

1. **Component Design**
   - Message service
   - Presence service
   - Notification service
   - **Red Flags**: Monolithic, unclear boundaries

2. **Caching Strategy**
   - Recent messages cache
   - Presence cache
   - **Red Flags**: No caching, poor strategy

3. **Media Handling**
   - Object storage
   - CDN integration
   - **Red Flags**: Database storage, no CDN

### Communication Skills

1. **Architecture Explanation**
   - Clear component design
   - Data flow understanding
   - **Red Flags**: Unclear design, no data flow

2. **Scale Considerations**
   - Billions of messages
   - Millions of concurrent connections
   - **Red Flags**: No scale thinking, small-scale design

### Meta-Specific Focus

1. **Real-Time Systems Expertise**
   - WebSocket mastery
   - Low-latency design
   - **Key**: Show real-time systems knowledge

2. **Message Systems**
   - Message queue understanding
   - Delivery guarantees
   - **Key**: Demonstrate messaging expertise

## Summary

Designing a chat system at scale requires careful consideration of:

1. **Real-Time Communication**: WebSocket connections for instant message delivery
2. **Message Ordering**: Sequence numbers ensure correct message ordering
3. **Scalability**: Horizontal scaling with sharding and caching
4. **Reliability**: Message queues and retry logic ensure message delivery
5. **Presence Management**: Efficient caching and broadcasting of presence updates
6. **Media Handling**: Object storage and CDN for efficient media delivery
7. **Group Messaging**: Efficient fan-out to group members
8. **Push Notifications**: Reliable delivery to offline users

Key architectural decisions:
- **WebSocket** for real-time communication
- **Kafka** for message queuing and distribution
- **Sharded Database** for message storage
- **Redis** for caching and presence management
- **Object Storage** for media files
- **Horizontal Scaling** for all services

The system handles 100 billion messages per day with low latency, high availability, and efficient resource utilization.

