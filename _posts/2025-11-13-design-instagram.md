---
layout: post
title: "Design Instagram - System Design Interview"
date: 2025-11-13
categories: [System Design, Interview Example, Distributed Systems, Social Media]
excerpt: "A comprehensive guide to designing Instagram, covering photo/video upload, feed generation, user relationships, scalability challenges, and architectural patterns for handling billions of users and petabytes of media content."
---

## Introduction

Instagram is a photo and video-sharing social networking service where users can upload, edit, and share content with followers. Designing Instagram requires handling massive scale: billions of users, millions of uploads per day, and petabytes of media storage.

This post provides a detailed walkthrough of designing Instagram, covering key features, scalability challenges, and architectural decisions. This is one of the most common system design interview questions that tests your understanding of distributed systems, media storage, feed generation, and real-time features.

## Problem Statement

**Design Instagram with the following features:**

1. Users can upload photos and videos
2. Users can follow other users
3. Users see a feed of photos/videos from users they follow
4. Users can like and comment on posts
5. Users can search for photos by tags/usernames
6. Support for stories (temporary content that expires after 24 hours)

**Scale Requirements:**
- 1 billion+ users
- 500 million+ daily active users
- 100 million+ photos/videos uploaded per day
- 23 billion+ photos viewed per day
- Average photo size: 200KB
- Average video size: 2MB

## Requirements Gathering

### Functional Requirements

**Core Features:**
1. **User Management**: Registration, authentication, profiles
2. **Media Upload**: Upload photos and videos
3. **Feed Generation**: Display posts from followed users
4. **Social Graph**: Follow/unfollow users
5. **Interactions**: Like, comment on posts
6. **Search**: Search by username, hashtags, locations
7. **Stories**: Temporary content that expires after 24 hours
8. **Notifications**: Real-time notifications for likes, comments, follows

**Out of Scope:**
- Direct messaging (DM) feature
- Video streaming (assume simple video playback)
- Advanced filters and editing
- Live streaming
- Reels/IGTV (focus on basic feed)

### Non-Functional Requirements

1. **Availability**: 99.9% uptime
2. **Reliability**: No data loss, all uploads must succeed
3. **Performance**: 
   - Feed load time: < 200ms
   - Photo upload: < 3 seconds
   - Video upload: < 30 seconds
4. **Scalability**: Handle 100M+ uploads per day
5. **Consistency**: Eventually consistent is acceptable for feed
6. **Durability**: All media must be stored reliably

## Capacity Estimation

### Traffic Estimates

- **Daily Active Users (DAU)**: 500 million
- **Daily uploads**: 100 million (photos + videos)
- **Read:Write ratio**: 100:1 (23B views / 100M uploads)
- **Average user views**: 46 photos/videos per day
- **Peak traffic**: 3x average = 300M uploads/day peak

### Storage Estimates

**Photos:**
- 100M photos/day × 200KB = 20TB/day
- 5 years retention: 20TB × 365 × 5 = 36.5PB

**Videos:**
- 20M videos/day × 2MB = 40TB/day
- 5 years retention: 40TB × 365 × 5 = 73PB

**Total Media Storage**: ~110PB over 5 years

**Metadata Storage:**
- User data: 1B users × 1KB = 1TB
- Posts metadata: 100M/day × 365 × 5 × 500 bytes = 91TB
- Social graph: 1B users × 500 followers avg × 8 bytes = 4TB
- Total metadata: ~100TB

### Bandwidth Estimates

- **Upload bandwidth**: 20TB/day (photos) + 40TB/day (videos) = 60TB/day = 694MB/s
- **Download bandwidth**: 60TB/day × 100 (read:write ratio) = 6PB/day = 69GB/s

## System APIs

### 1. Upload Photo/Video
```
POST /api/v1/media/upload
Parameters:
  - file: photo/video file
  - user_id: user ID
  - caption: optional text caption
  - location: optional location data
Response:
  - media_id: unique media identifier
  - upload_url: URL for direct upload
```

### 2. Get User Feed
```
GET /api/v1/feed
Parameters:
  - user_id: user ID
  - max_id: pagination cursor (optional)
  - count: number of posts to return (default: 20)
Response:
  - posts: array of post objects
  - next_max_id: cursor for next page
```

### 3. Follow User
```
POST /api/v1/follow
Parameters:
  - user_id: current user ID
  - follow_user_id: user to follow
Response:
  - success: boolean
```

### 4. Like Post
```
POST /api/v1/posts/{post_id}/like
Parameters:
  - user_id: user ID
  - post_id: post ID
Response:
  - like_count: updated like count
```

### 5. Comment on Post
```
POST /api/v1/posts/{post_id}/comments
Parameters:
  - user_id: user ID
  - post_id: post ID
  - text: comment text
Response:
  - comment_id: unique comment identifier
```

### 6. Get User Stories
```
GET /api/v1/stories/{user_id}
Parameters:
  - user_id: user ID
Response:
  - stories: array of story objects
```

## Database Design

### Schema Design

**Users Table:**
```sql
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    bio TEXT,
    profile_picture_url VARCHAR(512),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
);
```

**Posts Table:**
```sql
CREATE TABLE posts (
    post_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    media_type ENUM('photo', 'video') NOT NULL,
    media_url VARCHAR(512) NOT NULL,
    thumbnail_url VARCHAR(512),
    caption TEXT,
    location VARCHAR(255),
    like_count INT DEFAULT 0,
    comment_count INT DEFAULT 0,
    created_at TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

**Follows Table:**
```sql
CREATE TABLE follows (
    follower_id BIGINT NOT NULL,
    followee_id BIGINT NOT NULL,
    created_at TIMESTAMP,
    PRIMARY KEY (follower_id, followee_id),
    INDEX idx_follower (follower_id),
    INDEX idx_followee (followee_id),
    FOREIGN KEY (follower_id) REFERENCES users(user_id),
    FOREIGN KEY (followee_id) REFERENCES users(user_id)
);
```

**Likes Table:**
```sql
CREATE TABLE likes (
    like_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    post_id BIGINT NOT NULL,
    created_at TIMESTAMP,
    UNIQUE KEY unique_like (user_id, post_id),
    INDEX idx_post_id (post_id),
    INDEX idx_user_id (user_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (post_id) REFERENCES posts(post_id)
);
```

**Comments Table:**
```sql
CREATE TABLE comments (
    comment_id BIGINT PRIMARY KEY,
    post_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMP,
    INDEX idx_post_id (post_id),
    FOREIGN KEY (post_id) REFERENCES posts(post_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

**Stories Table:**
```sql
CREATE TABLE stories (
    story_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    media_url VARCHAR(512) NOT NULL,
    media_type ENUM('photo', 'video') NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_expires_at (expires_at),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

### Database Sharding Strategy

**Shard by User ID:**
- Use consistent hashing to distribute users across shards
- User data, posts, and follows stored on same shard for locality
- Enables efficient feed generation for a user's own posts

**Challenges:**
- Cross-shard queries for feed generation (posts from multiple users)
- Need to aggregate data from multiple shards

## High-Level System Design

```
┌─────────────┐
│   Client    │
│  (Mobile/   │
│    Web)     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│         Load Balancer                   │
└──────┬──────────────────┬───────────────┘
       │                  │
       ▼                  ▼
┌──────────────┐   ┌──────────────┐
│  API Gateway │   │  API Gateway │
└──────┬───────┘   └──────┬───────┘
       │                  │
       ├──────────────────┼──────────────────┐
       │                  │                  │
       ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Upload       │  │ Feed        │  │ Social Graph │
│ Service      │  │ Service     │  │ Service      │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Object       │  │ Cache        │  │ Database     │
│ Storage      │  │ (Redis)      │  │ (Sharded)    │
│ (S3/CDN)     │  └──────────────┘  └──────────────┘
└──────────────┘
```

## Component Design

### 1. Upload Service

**Flow:**
1. Client uploads media file to Upload Service
2. Upload Service validates file (size, format)
3. Generate unique media ID
4. Upload to Object Storage (S3)
5. Generate thumbnail for videos
6. Store metadata in database
7. Invalidate cache for user's feed
8. Return success response

**Optimizations:**
- **Resumable uploads**: For large videos, support chunked uploads
- **Async processing**: Thumbnail generation and metadata extraction done asynchronously
- **CDN integration**: Upload directly to CDN edge locations

### 2. Feed Service

**Feed Generation Approaches:**

**Approach 1: Pull Model (Fan-out on Read)**
- When user requests feed, fetch posts from all followed users
- Aggregate and sort posts
- **Pros**: Simple, real-time data
- **Cons**: Slow for users with many followees, high database load

**Approach 2: Push Model (Fan-out on Write)**
- When user posts, push to all followers' feed caches
- **Pros**: Fast feed retrieval
- **Cons**: High write load, storage overhead

**Approach 3: Hybrid Approach (Recommended)**
- Push model for users with < 1000 followers
- Pull model for users with > 1000 followers (celebrities)
- Use Redis sorted sets for feed storage

**Feed Generation Flow:**
1. Check Redis cache for user feed
2. If cache miss:
   - Fetch recent posts from followed users
   - Merge and sort by timestamp
   - Cache result in Redis
3. Return feed to user

**Redis Data Structure:**
```
Key: feed:{user_id}
Type: Sorted Set
Score: timestamp
Value: post_id
TTL: 7 days
```

### 3. Social Graph Service

**Stores follow relationships:**
- Use graph database (Neo4j) or relational DB with optimized indexes
- Cache frequently accessed relationships in Redis

**Redis Cache:**
```
Key: followers:{user_id}
Type: Set
Value: follower user_ids
TTL: 1 hour

Key: following:{user_id}
Type: Set
Value: followee user_ids
TTL: 1 hour
```

### 4. Search Service

**Features:**
- Search by username
- Search by hashtags
- Search by location

**Implementation:**
- Use Elasticsearch for full-text search
- Index usernames, hashtags, captions, locations
- Real-time indexing via message queue

### 5. Stories Service

**Features:**
- Stories expire after 24 hours
- Background job removes expired stories
- Stories appear at top of feed

**Implementation:**
- Store stories in database with `expires_at` timestamp
- Background cron job deletes expired stories
- Cache active stories in Redis with TTL

## Detailed Design

### Media Storage Architecture

**Object Storage (S3):**
- Store original photos and videos
- Use multiple availability zones for redundancy
- Lifecycle policies for old content

**CDN (CloudFront):**
- Cache frequently accessed media
- Serve media from edge locations
- Reduce origin server load

**Storage Tiers:**
1. **Hot storage**: Recent posts (last 30 days) - SSD
2. **Warm storage**: Older posts (30 days - 1 year) - Standard
3. **Cold storage**: Archive (1+ years) - Glacier

### Caching Strategy

**Multi-level Caching:**

**L1: Application Cache (In-memory)**
- Cache user profiles, recent posts
- TTL: 5 minutes

**L2: Redis Cache**
- Feed data, social graph, trending posts
- TTL: 1 hour for feeds, 24 hours for profiles

**L3: CDN Cache**
- Media files, static content
- TTL: 7 days

**Cache Invalidation:**
- On post upload: Invalidate user's feed cache
- On like/comment: Invalidate post cache
- On follow/unfollow: Invalidate feed cache

### Load Balancing

**Strategy:**
- **Layer 4 (NLB)**: For media uploads (high bandwidth)
- **Layer 7 (ALB)**: For API requests (routing based on path)

**Load Balancer Features:**
- Health checks
- SSL termination
- Request routing
- Rate limiting

### Database Replication

**Master-Slave Replication:**
- Master handles writes
- Slaves handle reads
- Automatic failover

**Read Replicas:**
- Distribute read load across multiple replicas
- Geographic distribution for low latency

### Message Queue

**Use Cases:**
1. **Async processing**: Thumbnail generation, metadata extraction
2. **Feed updates**: Fan-out to followers
3. **Notifications**: Like, comment, follow notifications
4. **Search indexing**: Update search index

**Technology**: Apache Kafka or AWS SQS

## Scalability Considerations

### Horizontal Scaling

**Stateless Services:**
- Upload Service, Feed Service, API Gateway
- Scale based on CPU/memory metrics

**Database Scaling:**
- Shard by user_id
- Use consistent hashing
- Replicate shards for availability

### Data Partitioning

**Sharding Strategy:**
- **By User ID**: User data, posts, follows on same shard
- **By Post ID**: For global post lookups
- **By Location**: For location-based queries

### Handling Hot Users

**Problem**: Celebrities with millions of followers

**Solutions:**
1. **Separate feed generation**: Use pull model for hot users
2. **Dedicated infrastructure**: Separate servers for hot users
3. **Rate limiting**: Prevent abuse
4. **Caching**: Aggressive caching for hot content

## Security Considerations

1. **Authentication**: JWT tokens, OAuth 2.0
2. **Authorization**: Role-based access control
3. **Media validation**: File type, size, content scanning
4. **Rate limiting**: Prevent abuse
5. **DDoS protection**: CloudFlare, AWS Shield
6. **Data encryption**: Encrypt data at rest and in transit
7. **Privacy**: User privacy settings, content visibility controls

## Monitoring & Observability

**Key Metrics:**
- Upload success rate
- Feed generation latency
- API response times
- Cache hit rates
- Database query performance
- CDN bandwidth usage

**Tools:**
- Prometheus + Grafana for metrics
- ELK stack for logging
- Distributed tracing (Jaeger/Zipkin)

## Trade-offs and Optimizations

### Trade-offs

1. **Consistency vs Availability**
   - Choose eventual consistency for feeds (better availability)
   - Strong consistency for critical operations (likes, follows)

2. **Storage vs Compute**
   - Pre-compute feeds (more storage, faster reads)
   - Compute on-demand (less storage, slower reads)
   - Hybrid approach balances both

3. **Latency vs Freshness**
   - Cache feeds (lower latency, stale data)
   - Real-time updates (higher latency, fresh data)
   - Use cache with short TTL

### Optimizations

1. **Image Optimization**
   - Multiple resolutions (thumbnail, medium, full)
   - WebP format for better compression
   - Lazy loading

2. **Video Optimization**
   - Multiple bitrates for adaptive streaming
   - H.264/H.265 encoding
   - Progressive download

3. **Database Optimization**
   - Indexes on frequently queried fields
   - Connection pooling
   - Query optimization

4. **Caching Optimization**
   - Cache warming for popular content
   - Cache aside pattern
   - Write-through for critical data

## Summary

Designing Instagram requires handling:

1. **Massive Scale**: Billions of users, petabytes of media
2. **High Read:Write Ratio**: 100:1 read to write ratio
3. **Real-time Features**: Feed updates, notifications
4. **Media Storage**: Efficient storage and delivery of photos/videos
5. **Social Graph**: Efficient follow/unfollow operations
6. **Feed Generation**: Fast feed retrieval with hybrid push/pull model

**Key Architectural Decisions:**
- Object storage (S3) + CDN for media
- Sharded databases for scalability
- Redis for caching and feed storage
- Hybrid feed generation (push for normal users, pull for celebrities)
- Message queues for async processing
- Multi-level caching strategy

This design can handle Instagram's scale while maintaining low latency and high availability.

