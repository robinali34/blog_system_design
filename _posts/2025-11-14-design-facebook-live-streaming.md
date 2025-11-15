---
layout: post
title: "Design Facebook Live Streaming with Comments - System Design Interview"
date: 2025-11-14
categories: [System Design, Interview Example, Distributed Systems, Real-time Systems, Video Streaming, Social Media]
excerpt: "A comprehensive guide to designing Facebook Live streaming with real-time comments, covering live video streaming, real-time comment delivery, engagement tracking, and architectural patterns for handling millions of concurrent viewers and thousands of comments per second."
---

## Introduction

Facebook Live enables users to broadcast live video streams to their friends and followers, with real-time comments appearing as the stream progresses. The system must handle live video encoding, streaming, real-time comment delivery, and high engagement rates, requiring low-latency infrastructure and efficient real-time data distribution.

This post provides a detailed walkthrough of designing Facebook Live with real-time comments, covering key architectural decisions, live streaming protocols, real-time comment delivery, engagement tracking, and scalability challenges. This is a common system design interview question that tests your understanding of distributed systems, real-time streaming, WebSocket connections, and handling massive concurrent viewers.

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

**Design Facebook Live streaming with real-time comments with the following features:**

1. Start and broadcast live video streams
2. Real-time video streaming to viewers
3. Real-time comments appearing as stream progresses
4. Live reactions (like, love, haha, etc.)
5. Viewer count updates
6. Comment moderation (filter spam, inappropriate content)
7. Stream recording and replay
8. Notification to followers when going live
9. Engagement metrics (views, comments, reactions)
10. Multi-quality streaming (adaptive bitrate)

**Scale Requirements:**
- 2 billion+ users
- 500 million+ daily active users
- Peak: 1 million concurrent live streams
- Peak: 50 million concurrent viewers per stream
- Average: 10,000 viewers per stream
- Comments: 10,000+ comments per second per popular stream
- Average comment latency: < 500ms
- Video latency: < 5 seconds end-to-end

## Requirements

### Functional Requirements

**Core Features:**
1. **Live Streaming**: Start, broadcast, and end live streams
2. **Real-Time Video**: Stream video with low latency (< 5 seconds)
3. **Real-Time Comments**: Comments appear instantly as users type
4. **Live Reactions**: Real-time reactions (like, love, haha, wow, sad, angry)
5. **Viewer Count**: Real-time viewer count updates
6. **Comment Moderation**: Filter spam and inappropriate content
7. **Stream Recording**: Record streams for replay
8. **Notifications**: Notify followers when user goes live
9. **Engagement Metrics**: Track views, comments, reactions, shares
10. **Multi-Quality**: Support multiple quality levels

**Out of Scope:**
- Video editing during stream
- Screen sharing
- Multi-user streams
- Advanced analytics dashboard
- Mobile app (focus on web API)

### Non-Functional Requirements

1. **Availability**: 99.9% uptime
2. **Reliability**: No comment loss, guaranteed delivery
3. **Performance**: 
   - Comment delivery: < 500ms latency
   - Video latency: < 5 seconds end-to-end
   - Viewer count update: < 1 second
4. **Scalability**: Handle 50M+ concurrent viewers per stream
5. **Consistency**: Eventually consistent for viewer counts
6. **Real-Time**: Comments must appear instantly
7. **Bandwidth Efficiency**: Efficient bandwidth usage with adaptive streaming

## Capacity Estimation

### Traffic Estimates

- **Total Users**: 2 billion
- **Daily Active Users (DAU)**: 500 million
- **Concurrent Live Streams**: 1 million (peak)
- **Average Viewers per Stream**: 10,000
- **Peak Viewers per Stream**: 50 million
- **Total Concurrent Viewers**: 10 billion (1M streams × 10K avg)
- **Comments per Stream**: 100 comments/second (average), 10,000/second (peak)
- **Total Comments per Second**: 100M comments/second (peak)
- **Reactions per Stream**: 1,000 reactions/second (peak)

### Storage Estimates

**Live Stream Metadata:**
- 1M concurrent streams × 1KB = 1GB (in-memory)
- Historical streams: 10M streams/day × 1KB × 30 days = 300GB

**Comments Storage:**
- 100M comments/second × 3600 seconds/hour = 360B comments/hour
- Average comment: 200 bytes
- Hourly storage: 360B × 200 bytes = 72TB/hour
- Daily storage: 72TB × 24 = 1.73PB/day
- 30-day retention: ~52PB

**Video Storage (Recorded):**
- 10M streams/day × 30 minutes × 2GB/hour = 10TB/day
- 30-day retention: ~300TB

**Total Storage**: ~52PB (mostly comments)

### Bandwidth Estimates

**Video Upload (Broadcaster):**
- 1M streams × 5 Mbps = 5 Tbps upload

**Video Streaming (Viewers):**
- 10B concurrent viewers × 2 Mbps average = 20 Pbps
- Peak: 50M viewers/stream × 5 Mbps = 250 Tbps per popular stream

**Comments:**
- 100M comments/sec × 500 bytes = 50GB/s = 400Gbps

**Total Peak Bandwidth**: ~20 Pbps (mostly video)

## Core Entities

### Live Stream
- `stream_id` (UUID)
- `broadcaster_id` (user_id)
- `title`
- `description`
- `status` (live, ended, scheduled)
- `started_at` (TIMESTAMP)
- `ended_at` (TIMESTAMP)
- `viewer_count` (BIGINT)
- `comment_count` (BIGINT)
- `reaction_count` (BIGINT)
- `stream_url` (RTMP/HLS URL)
- `thumbnail_url`
- `created_at`

### Comment
- `comment_id` (UUID)
- `stream_id`
- `user_id`
- `text` (TEXT)
- `parent_comment_id` (for replies)
- `reactions` (JSON: {like: 10, love: 5})
- `created_at` (TIMESTAMP)
- `status` (visible, hidden, deleted)

### Reaction
- `reaction_id` (UUID)
- `stream_id`
- `user_id`
- `reaction_type` (like, love, haha, wow, sad, angry)
- `created_at` (TIMESTAMP)

### Viewer
- `viewer_id` (UUID)
- `stream_id`
- `user_id`
- `joined_at` (TIMESTAMP)
- `last_seen_at` (TIMESTAMP)
- `watch_time` (seconds)

### Stream Recording
- `recording_id` (UUID)
- `stream_id`
- `video_url` (S3 URL)
- `duration` (seconds)
- `file_size` (bytes)
- `created_at`

## API

### 1. Start Live Stream
```
POST /api/v1/streams/start
Request:
{
  "title": "My Live Stream",
  "description": "Streaming about...",
  "privacy": "public"
}

Response:
{
  "stream_id": "uuid",
  "rtmp_url": "rtmp://live.example.com/live",
  "stream_key": "abc123",
  "status": "live",
  "started_at": "2025-11-13T10:00:00Z"
}
```

### 2. End Live Stream
```
POST /api/v1/streams/{stream_id}/end
Response:
{
  "stream_id": "uuid",
  "status": "ended",
  "ended_at": "2025-11-13T11:00:00Z",
  "total_viewers": 10000,
  "total_comments": 5000,
  "recording_url": "https://..."
}
```

### 3. Watch Live Stream
```
GET /api/v1/streams/{stream_id}/watch
Response:
{
  "stream_id": "uuid",
  "hls_url": "https://cdn.example.com/streams/{stream_id}/playlist.m3u8",
  "qualities": ["360p", "480p", "720p", "1080p"],
  "viewer_count": 10000,
  "is_live": true
}
```

### 4. Post Comment
```
POST /api/v1/streams/{stream_id}/comments
Request:
{
  "text": "Great stream!",
  "parent_comment_id": null
}

Response:
{
  "comment_id": "uuid",
  "stream_id": "uuid",
  "user_id": "uuid",
  "text": "Great stream!",
  "created_at": "2025-11-13T10:05:00Z"
}
```

### 5. Get Comments (Real-Time via WebSocket)
```
WS /ws/streams/{stream_id}/comments
Messages:
- Incoming: {"type": "comment", "text": "..."}
- Outgoing: {"type": "new_comment", "data": {...}}
- Outgoing: {"type": "reaction", "data": {...}}
- Outgoing: {"type": "viewer_count", "count": 10000}
```

### 6. React to Stream
```
POST /api/v1/streams/{stream_id}/reactions
Request:
{
  "reaction_type": "like"
}

Response:
{
  "reaction_id": "uuid",
  "reaction_type": "like",
  "total_reactions": {
    "like": 1000,
    "love": 500,
    "haha": 200
  }
}
```

### 7. Get Stream Details
```
GET /api/v1/streams/{stream_id}
Response:
{
  "stream_id": "uuid",
  "broadcaster": {...},
  "title": "My Live Stream",
  "viewer_count": 10000,
  "comment_count": 5000,
  "reaction_count": 2000,
  "is_live": true,
  "started_at": "2025-11-13T10:00:00Z"
}
```

### 8. Get Stream Comments (Historical)
```
GET /api/v1/streams/{stream_id}/comments?limit=50&offset=0
Response:
{
  "comments": [
    {
      "comment_id": "uuid",
      "user": {...},
      "text": "Great stream!",
      "reactions": {"like": 10},
      "created_at": "2025-11-13T10:05:00Z"
    }
  ],
  "total": 5000,
  "limit": 50,
  "offset": 0
}
```

## Data Flow

### Start Live Stream Flow

1. **Broadcaster Starts Stream**:
   - User clicks "Go Live"
   - **Client** sends start stream request
   - **Stream Service** creates stream record

2. **Stream Setup**:
   - **Stream Service**:
     - Generates RTMP URL and stream key
     - Creates stream metadata record
     - Sets up video processing pipeline
     - Publishes "going live" event

3. **Notification**:
   - **Notification Service** notifies broadcaster's followers
   - Followers receive "X is live" notification

4. **Video Ingestion**:
   - Broadcaster's device sends video to RTMP server
   - **RTMP Server** receives video stream
   - **Video Processing Service** transcodes to multiple qualities
   - **CDN** distributes video segments

### Comment Posting Flow

1. **User Posts Comment**:
   - User types comment and submits
   - **Client** sends comment to **Comment Service**
   - **Comment Service** validates comment

2. **Comment Processing**:
   - **Comment Service**:
     - Validates stream is live
     - Applies moderation filters
     - Creates comment record
     - Publishes comment event to **Message Queue**

3. **Real-Time Distribution**:
   - **Comment Distribution Service** consumes comment event
   - Broadcasts comment to all connected viewers via **WebSocket**
   - Updates comment count
   - Stores comment in database

4. **Viewer Receives Comment**:
   - **WebSocket Service** pushes comment to viewer's client
   - **Client** displays comment in real-time

### Live Video Streaming Flow

1. **Viewer Joins Stream**:
   - Viewer clicks on live stream
   - **Client** requests stream URL
   - **Streaming Service** returns HLS manifest URL

2. **Video Delivery**:
   - **Client** requests video segments from **CDN**
   - **CDN** serves segments from nearest edge
   - **Client** plays video with low latency

3. **Real-Time Updates**:
   - **Client** maintains WebSocket connection
   - Receives real-time comments, reactions, viewer count
   - Updates UI in real-time

## Database Design

### Schema Design

**Live Streams Table:**
```sql
CREATE TABLE live_streams (
    stream_id UUID PRIMARY KEY,
    broadcaster_id UUID NOT NULL,
    title VARCHAR(500),
    description TEXT,
    status ENUM('live', 'ended', 'scheduled') DEFAULT 'live',
    started_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP NULL,
    viewer_count BIGINT DEFAULT 0,
    comment_count BIGINT DEFAULT 0,
    reaction_count BIGINT DEFAULT 0,
    stream_url VARCHAR(500),
    thumbnail_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_broadcaster_id (broadcaster_id),
    INDEX idx_status (status),
    INDEX idx_started_at (started_at DESC)
);
```

**Comments Table (Sharded by stream_id):**
```sql
CREATE TABLE comments_0 (
    comment_id UUID PRIMARY KEY,
    stream_id UUID NOT NULL,
    user_id UUID NOT NULL,
    text TEXT NOT NULL,
    parent_comment_id UUID NULL,
    reactions JSON DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    status ENUM('visible', 'hidden', 'deleted') DEFAULT 'visible',
    INDEX idx_stream_id (stream_id),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at DESC),
    INDEX idx_parent_comment (parent_comment_id)
);
-- Similar tables: comments_1, comments_2, ..., comments_N
```

**Reactions Table:**
```sql
CREATE TABLE reactions (
    reaction_id UUID PRIMARY KEY,
    stream_id UUID NOT NULL,
    user_id UUID NOT NULL,
    reaction_type ENUM('like', 'love', 'haha', 'wow', 'sad', 'angry') NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_stream_id (stream_id),
    INDEX idx_user_id (user_id),
    UNIQUE KEY uk_stream_user (stream_id, user_id)
);
```

**Viewers Table:**
```sql
CREATE TABLE viewers (
    viewer_id UUID PRIMARY KEY,
    stream_id UUID NOT NULL,
    user_id UUID NOT NULL,
    joined_at TIMESTAMP DEFAULT NOW(),
    last_seen_at TIMESTAMP DEFAULT NOW(),
    watch_time INT DEFAULT 0,
    INDEX idx_stream_id (stream_id),
    INDEX idx_user_id (user_id),
    INDEX idx_last_seen (last_seen_at),
    UNIQUE KEY uk_stream_user (stream_id, user_id)
);
```

**Stream Recordings Table:**
```sql
CREATE TABLE stream_recordings (
    recording_id UUID PRIMARY KEY,
    stream_id UUID NOT NULL,
    video_url VARCHAR(500) NOT NULL,
    duration INT NOT NULL,
    file_size BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_stream_id (stream_id)
);
```

### Database Sharding Strategy

**Comments Table Sharding:**
- Shard by stream_id using consistent hashing
- 1000 shards: `shard_id = hash(stream_id) % 1000`
- All comments for a stream in same shard
- Enables efficient comment queries

**Shard Key Selection:**
- `stream_id` ensures all comments for a stream are in same shard
- Enables efficient queries for stream comments
- Prevents cross-shard queries for single stream

**Replication:**
- Each shard replicated 3x for high availability
- Master-replica setup for read scaling
- Writes go to master, reads can go to replicas

## High-Level Design

```
┌─────────────┐
│ Broadcaster │
│  (Mobile/   │
│   Desktop)  │
└──────┬──────┘
       │
       │ RTMP
       │
┌──────▼──────────────────────────────────────────────┐
│         RTMP Ingest Server                           │
│         - Receives live video                        │
│         - Validates stream key                       │
└──────┬──────────────────────────────────────────────┘
       │
       │
┌──────▼──────────────────────────────────────────────┐
│         Video Processing Service                     │
│  ┌──────────────┐  ┌──────────────┐                │
│  │ Transcoding  │  │ HLS Segment  │                │
│  │ Workers      │  │ Generation    │                │
│  └──────┬───────┘  └──────┬───────┘                │
└─────────┼──────────────────┼───────────────────────────┘
          │                  │
          │                  │
┌─────────▼──────────────────▼───────────────────────────┐
│         CDN (Global Distribution)                      │
│         - Video segments                                │
│         - Low latency delivery                         │
└────────────────────────────────────────────────────────┘
          │
          │
┌─────────▼───────────────────────────────────────────────┐
│         API Gateway / Load Balancer                    │
└─────────┬──────────────────────────────────────────────┘
          │
          ├──────────────┬──────────────┬──────────────┐
          │              │              │              │
┌─────────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
│   Stream       │ │  Comment   │ │  Reaction  │ │  Viewer    │
│   Service      │ │  Service   │ │  Service  │ │  Service   │
└─────────┬──────┘ └─────┬───────┘ └─────┬──────┘ └─────┬──────┘
          │              │              │              │
          │              │              │              │
┌─────────▼──────────────▼──────────────▼──────────────▼──────┐
│              Message Queue (Kafka)                          │
│              - Comment events                               │
│              - Reaction events                              │
│              - Viewer events                                │
└─────────┬───────────────────────────────────────────────────┘
          │
          │
┌─────────▼───────────────────────────────────────────────────┐
│         Comment Distribution Service                        │
│         - Consumes comment events                           │
│         - Broadcasts to WebSocket connections               │
└─────────┬───────────────────────────────────────────────────┘
          │
          │
┌─────────▼───────────────────────────────────────────────────┐
│         WebSocket Service                                    │
│         - Maintains connections per stream                   │
│         - Broadcasts comments/reactions to viewers           │
└─────────┬───────────────────────────────────────────────────┘
          │
          │ WebSocket
          │
┌─────────▼───────────────────────────────────────────────────┐
│         Viewers (Millions)                                   │
│         - Receive video from CDN                            │
│         - Receive comments via WebSocket                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│         Database Cluster (Sharded)                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ Comments │  │ Reactions│  │ Viewers  │                  │
│  │ DB       │  │ DB       │  │ DB       │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
│                                                             │
│  ┌──────────┐  ┌──────────┐                               │
│  │ Streams  │  │Recordings│                               │
│  │ DB       │  │ DB       │                               │
│  └──────────┘  └──────────┘                               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Cache Layer (Redis)                             │
│  - Stream metadata                                           │
│  - Viewer counts                                             │
│  - Comment counts                                            │
│  - Reaction counts                                           │
└─────────────────────────────────────────────────────────────┘
```

## Deep Dive

### Component Design

#### 1. RTMP Ingest Server

**Responsibilities:**
- Receive live video from broadcasters
- Validate stream keys
- Forward video to processing pipeline
- Handle connection management

**Key Design Decisions:**
- **RTMP Protocol**: Use RTMP for video ingestion
- **Stream Key Validation**: Validate broadcaster permissions
- **Connection Pooling**: Handle multiple concurrent streams
- **Fault Tolerance**: Handle connection failures gracefully

**Scalability:**
- Multiple RTMP servers for horizontal scaling
- Load balancer distributes streams
- Connection pooling

#### 2. Video Processing Service

**Responsibilities:**
- Transcode live video to multiple qualities
- Generate HLS segments
- Create streaming manifests
- Handle real-time transcoding

**Key Design Decisions:**
- **Real-Time Transcoding**: Transcode on-the-fly
- **Multiple Qualities**: 360p, 480p, 720p, 1080p
- **Low Latency**: Minimize processing delay
- **HLS Format**: Use HLS for streaming

**Implementation:**
```python
def process_live_stream(stream_id, rtmp_url):
    # Start transcoding pipeline
    qualities = ['360p', '480p', '720p', '1080p']
    
    transcoded_streams = []
    for quality in qualities:
        # Transcode to quality
        output_url = transcode_stream(rtmp_url, quality)
        
        # Generate HLS segments
        hls_segments = generate_hls_segments(output_url, segment_duration=2)
        
        transcoded_streams.append({
            'quality': quality,
            'segments': hls_segments
        })
    
    # Create HLS manifest
    manifest = create_hls_manifest(stream_id, transcoded_streams)
    
    # Upload to CDN
    cdn_url = upload_to_cdn(stream_id, manifest, transcoded_streams)
    
    return cdn_url
```

#### 3. Comment Service

**Responsibilities:**
- Handle comment creation
- Apply moderation filters
- Store comments
- Publish comment events

**Key Design Decisions:**
- **Moderation**: Filter spam and inappropriate content
- **Event Publishing**: Publish to message queue for distribution
- **Rate Limiting**: Limit comments per user per stream
- **Validation**: Validate comment text and length

**Implementation:**
```python
def create_comment(stream_id, user_id, text, parent_comment_id=None):
    # Validate stream is live
    stream = get_stream(stream_id)
    if stream.status != 'live':
        raise Exception("Stream is not live")
    
    # Apply moderation
    if is_spam(text) or is_inappropriate(text):
        return {'status': 'rejected', 'reason': 'moderation'}
    
    # Rate limiting
    if exceeds_rate_limit(user_id, stream_id):
        raise Exception("Rate limit exceeded")
    
    # Create comment
    comment = Comment(
        stream_id=stream_id,
        user_id=user_id,
        text=text,
        parent_comment_id=parent_comment_id
    )
    comment.save()
    
    # Publish comment event
    publish_comment_event({
        'comment_id': comment.comment_id,
        'stream_id': stream_id,
        'user_id': user_id,
        'text': text,
        'created_at': comment.created_at
    })
    
    # Update comment count
    increment_comment_count(stream_id)
    
    return comment
```

#### 4. Comment Distribution Service

**Responsibilities:**
- Consume comment events from queue
- Broadcast comments to viewers
- Manage WebSocket connections
- Handle high-frequency comment delivery

**Key Design Decisions:**
- **WebSocket Broadcasting**: Broadcast via WebSocket for real-time delivery
- **Connection Management**: Manage connections per stream
- **Batching**: Batch comments for efficiency
- **Prioritization**: Prioritize recent comments

**Implementation:**
```python
def distribute_comment(comment_event):
    stream_id = comment_event['stream_id']
    
    # Get all WebSocket connections for this stream
    connections = get_stream_connections(stream_id)
    
    # Prepare comment message
    message = {
        'type': 'new_comment',
        'data': {
            'comment_id': comment_event['comment_id'],
            'user_id': comment_event['user_id'],
            'text': comment_event['text'],
            'created_at': comment_event['created_at']
        }
    }
    
    # Broadcast to all connections
    broadcast_to_connections(connections, message)
    
    # Update metrics
    update_comment_metrics(stream_id)
```

#### 5. WebSocket Service

**Responsibilities:**
- Maintain WebSocket connections
- Map connections to streams
- Broadcast messages to connections
- Handle connection lifecycle

**Key Design Decisions:**
- **Connection Mapping**: Map user_id → [connections] per stream
- **Load Balancing**: Use sticky sessions for WebSocket
- **Heartbeat**: Ping/pong to detect dead connections
- **Scaling**: Horizontal scaling with Redis pub/sub

**Implementation:**
```python
class WebSocketService:
    def __init__(self):
        self.connections = {}  # stream_id -> [connections]
        self.redis_pubsub = redis.pubsub()
    
    def handle_connection(self, websocket, stream_id, user_id):
        # Add connection
        if stream_id not in self.connections:
            self.connections[stream_id] = []
        self.connections[stream_id].append({
            'websocket': websocket,
            'user_id': user_id,
            'connected_at': now()
        })
        
        # Subscribe to Redis channel for this stream
        self.redis_pubsub.subscribe(f"stream:{stream_id}:comments")
        
        # Send initial data
        self.send_initial_data(websocket, stream_id)
        
        # Handle messages
        try:
            while True:
                # Listen for Redis messages
                message = self.redis_pubsub.get_message()
                if message:
                    self.broadcast_to_stream(stream_id, message['data'])
                
                # Handle WebSocket messages
                data = websocket.receive()
                if data:
                    self.handle_message(websocket, stream_id, user_id, data)
        except WebSocketDisconnect:
            self.remove_connection(stream_id, websocket)
    
    def broadcast_to_stream(self, stream_id, message):
        if stream_id in self.connections:
            for conn in self.connections[stream_id]:
                try:
                    conn['websocket'].send(message)
                except:
                    # Remove dead connection
                    self.remove_connection(stream_id, conn['websocket'])
```

### Detailed Design

#### Real-Time Comment Delivery

**Challenge:** Deliver comments to millions of viewers in real-time

**Solution:**
- **WebSocket Connections**: Maintain persistent WebSocket connections
- **Redis Pub/Sub**: Use Redis for cross-server message distribution
- **Connection Pooling**: Group connections by stream
- **Batching**: Batch comments for efficiency

**Architecture:**
```
Comment Event → Kafka → Comment Distributor → Redis Pub/Sub → WebSocket Servers → Viewers
```

**Implementation:**
```python
def broadcast_comment(stream_id, comment):
    # Publish to Redis channel
    redis.publish(f"stream:{stream_id}:comments", json.dumps({
        'type': 'comment',
        'data': comment
    }))
    
    # All WebSocket servers subscribed to this channel will receive
    # and broadcast to their connected clients
```

#### Viewer Count Tracking

**Challenge:** Track viewer count accurately in real-time

**Solution:**
- **Connection-Based**: Count active WebSocket connections
- **Heartbeat**: Track last seen timestamp
- **Aggregation**: Aggregate counts across servers
- **Approximation**: Use approximate counting for very popular streams

**Implementation:**
```python
def update_viewer_count(stream_id):
    # Count active connections
    connections = get_stream_connections(stream_id)
    active_count = len([c for c in connections if is_active(c)])
    
    # Update in Redis (for fast reads)
    redis.set(f"stream:{stream_id}:viewer_count", active_count, ex=60)
    
    # Update in database (periodically)
    db.execute(
        "UPDATE live_streams SET viewer_count = ? WHERE stream_id = ?",
        active_count, stream_id
    )
    
    # Broadcast viewer count update
    broadcast_viewer_count(stream_id, active_count)

def broadcast_viewer_count(stream_id, count):
    message = {
        'type': 'viewer_count',
        'count': count
    }
    redis.publish(f"stream:{stream_id}:updates", json.dumps(message))
```

#### Comment Moderation

**Challenge:** Filter spam and inappropriate content in real-time

**Solution:**
- **Keyword Filtering**: Filter known spam keywords
- **ML-Based**: Use ML models for content classification
- **Rate Limiting**: Limit comments per user
- **Async Moderation**: Moderate asynchronously, hide if needed

**Implementation:**
```python
def moderate_comment(text, user_id, stream_id):
    # Keyword filtering
    if contains_spam_keywords(text):
        return {'status': 'rejected', 'reason': 'spam'}
    
    # Rate limiting
    if get_comment_count(user_id, stream_id, window=60) > 10:
        return {'status': 'rejected', 'reason': 'rate_limit'}
    
    # ML-based moderation (async)
    moderation_result = moderate_with_ml(text)
    if moderation_result['inappropriate']:
        # Hide comment but don't reject (for review)
        return {'status': 'hidden', 'reason': moderation_result['reason']}
    
    return {'status': 'approved'}
```

#### Low-Latency Video Streaming

**Challenge:** Minimize video latency for live streaming

**Solution:**
- **Short Segments**: Use 2-second HLS segments (vs 10 seconds)
- **Low-Latency HLS**: Use LL-HLS extensions
- **CDN Optimization**: Deploy CDN nodes close to viewers
- **Reduced Buffering**: Minimize client-side buffering

**Implementation:**
```python
def generate_low_latency_hls(stream_id, video_segments):
    manifest = "#EXTM3U\n"
    manifest += "#EXT-X-VERSION:6\n"
    manifest += "#EXT-X-INDEPENDENT-SEGMENTS\n"
    manifest += "#EXT-X-SERVER-CONTROL:CAN-BLOCK-RELOAD=YES,PART-HOLD-BACK=1.0\n"
    
    for segment in video_segments:
        manifest += f"#EXTINF:2.0,\n"
        manifest += f"{segment.url}\n"
    
    return manifest
```

### Scalability Considerations

#### Horizontal Scaling

**WebSocket Servers:**
- Scale horizontally with Redis pub/sub
- Each server handles subset of streams
- Sticky sessions for WebSocket connections
- Connection limits per server

**Comment Service:**
- Stateless service, horizontally scalable
- Load balancer distributes requests
- Kafka for event distribution
- Parallel processing

#### Connection Management

**WebSocket Connections:**
- 50M viewers = 50M WebSocket connections
- Distribute across servers (100K per server = 500 servers)
- Use Redis for connection mapping
- Heartbeat to detect dead connections

**Redis Pub/Sub:**
- Subscribe to stream channels
- Cross-server message distribution
- Handle high message rates
- Scale Redis cluster

#### Caching Strategy

**Redis Cache:**
- **Stream Metadata**: TTL 1 minute
- **Viewer Counts**: TTL 10 seconds
- **Comment Counts**: TTL 1 minute
- **Recent Comments**: TTL 5 minutes

**Cache Invalidation:**
- Invalidate on stream updates
- Invalidate on comment creation
- Use cache-aside pattern

### Security Considerations

#### Authentication & Authorization

- **JWT Tokens**: Use JWT for API and WebSocket authentication
- **Stream Access Control**: Verify user can view stream
- **Rate Limiting**: Limit comments and reactions per user
- **Moderation**: Filter inappropriate content

#### Content Security

- **Stream Key Validation**: Validate RTMP stream keys
- **Access Control**: Verify broadcaster permissions
- **DRM**: Optional DRM for premium content
- **Anti-Abuse**: Detect and prevent abuse

### Monitoring & Observability

#### Key Metrics

**System Metrics:**
- Active streams count
- Concurrent viewers
- Comments per second
- WebSocket connection count
- Video latency
- Comment delivery latency

**Business Metrics:**
- Total streams per day
- Average viewers per stream
- Engagement rate (comments/views)
- Reaction rate
- Stream duration

#### Logging

- **Structured Logging**: JSON logs for parsing
- **Comment Events**: Log all comments
- **Stream Events**: Log stream start/end
- **Error Logging**: Log errors with context

#### Alerting

- **High Latency**: Alert if video latency > 10 seconds
- **High Error Rate**: Alert if error rate > 1%
- **Connection Failures**: Alert on WebSocket failures
- **Comment Delivery Issues**: Alert if comment latency > 1 second

### Trade-offs and Optimizations

#### Trade-offs

**1. Comment Delivery: WebSocket vs Server-Sent Events**
- **WebSocket**: Bidirectional, lower latency
- **SSE**: Simpler, unidirectional
- **Decision**: WebSocket for real-time bidirectional communication

**2. Viewer Count: Exact vs Approximate**
- **Exact**: More accurate, higher cost
- **Approximate**: Less accurate, lower cost
- **Decision**: Exact for small streams, approximate for very large

**3. Comment Storage: Real-Time vs Batch**
- **Real-Time**: Lower latency, higher cost
- **Batch**: Higher latency, lower cost
- **Decision**: Real-time for delivery, batch for storage

**4. Video Latency: Low vs Very Low**
- **Low (5-10s)**: Standard HLS, simpler
- **Very Low (1-3s)**: LL-HLS, more complex
- **Decision**: Low latency HLS with 2-second segments

#### Optimizations

**1. Comment Batching**
- Batch multiple comments in single message
- Reduce WebSocket message overhead
- Improve throughput

**2. Connection Pooling**
- Reuse WebSocket connections
- Reduce connection overhead
- Improve performance

**3. CDN Optimization**
- Deploy CDN nodes close to viewers
- Cache video segments
- Reduce latency

**4. Compression**
- Compress WebSocket messages
- Reduce bandwidth usage
- Improve performance

## Summary

Designing Facebook Live streaming with real-time comments requires careful consideration of:

1. **Live Video Streaming**: Low-latency video delivery with HLS
2. **Real-Time Comments**: WebSocket-based comment delivery
3. **Scalability**: Handle millions of concurrent viewers per stream
4. **Comment Distribution**: Efficient broadcasting to millions of connections
5. **Viewer Tracking**: Accurate viewer count in real-time
6. **Moderation**: Real-time content moderation
7. **Connection Management**: Manage millions of WebSocket connections
8. **Performance**: Sub-500ms comment delivery latency

Key architectural decisions:
- **RTMP** for video ingestion from broadcasters
- **HLS** for low-latency video streaming to viewers
- **WebSocket** for real-time comment delivery
- **Redis Pub/Sub** for cross-server message distribution
- **Kafka** for comment event processing
- **CDN** for video segment delivery
- **Sharded Database** for comment storage
- **Horizontal Scaling** for all services

The system handles 1 million concurrent streams, 50 million viewers per popular stream, and 10,000+ comments per second with sub-500ms comment delivery latency.

