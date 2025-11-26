---
layout: post
title: "Design a News Feed System - System Design Interview"
date: 2025-11-13
categories: [System Design, Interview Example, Distributed Systems, Social Media]
excerpt: "A comprehensive guide to designing a news feed system, covering feed generation strategies (push/pull/hybrid), ranking algorithms, real-time updates, scalability challenges, and architectural patterns for handling billions of users and millions of posts per day."
---

## Introduction

A news feed is a core feature of social media platforms that displays a personalized stream of content from users, pages, and groups that a user follows. Designing a news feed system requires handling massive scale, real-time updates, personalized ranking, and efficient content delivery.

This post provides a detailed walkthrough of designing a news feed system, covering key architectural decisions, feed generation strategies, ranking algorithms, and scalability challenges. This is one of the most common system design interview questions that tests your understanding of distributed systems, caching, real-time processing, and algorithmic ranking.

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
9. [Feed Generation Strategies](#feed-generation-strategies)
10. [Deep Dive](#deep-dive)
    - [Component Design](#component-design)
    - [Detailed Design](#detailed-design)
    - [Scalability Considerations](#scalability-considerations)
    - [Security Considerations](#security-considerations)
    - [Monitoring & Observability](#monitoring--observability)
    - [Trade-offs and Optimizations](#trade-offs-and-optimizations)
11. [Summary](#summary)

## Problem Statement

**Design a news feed system with the following features:**

1. Users can post text, images, videos, and links
2. Users can follow other users, pages, and groups
3. Users see a personalized feed of posts from entities they follow
4. Feed is ranked by relevance (not just chronological)
5. Feed updates in real-time as new posts are created
6. Users can like, comment, and share posts
7. Feed supports pagination (infinite scroll)

**Scale Requirements:**
- 1 billion+ users
- 500 million+ daily active users
- 500 million+ posts per day
- 100 billion+ feed views per day
- Average user follows: 200 users/pages/groups
- Average posts per user per day: 5 posts
- Read:Write ratio: 200:1 (100B views / 500M posts)

## Requirements

### Functional Requirements

**Core Features:**
1. **Feed Generation**: Generate personalized feed for each user
2. **Ranking**: Rank posts by relevance, not just timestamp
3. **Real-time Updates**: Show new posts as they're created
4. **Social Graph**: Manage follow/unfollow relationships
5. **Interactions**: Support likes, comments, shares
6. **Pagination**: Infinite scroll with cursor-based pagination
7. **Filtering**: Filter by post type, date range, etc.

**Out of Scope:**
- Content creation (assume posts are created elsewhere)
- Direct messaging
- Advanced analytics
- Ad insertion (focus on organic content)
- Video streaming (assume simple video playback)

### Non-Functional Requirements

1. **Availability**: 99.9% uptime
2. **Performance**: 
   - Feed generation: < 200ms (p95)
   - Feed refresh: < 100ms
   - Real-time update latency: < 1 second
3. **Scalability**: Handle 100B+ feed views per day
4. **Consistency**: Eventually consistent is acceptable
5. **Freshness**: Feed should reflect new posts within 1 minute
6. **Personalization**: Feed should be highly personalized per user

## Capacity Estimation

### Traffic Estimates

- **Daily Active Users (DAU)**: 500 million
- **Daily posts**: 500 million
- **Daily feed views**: 100 billion
- **Read:Write ratio**: 200:1
- **Average feed requests per user**: 200 per day
- **Peak traffic**: 3x average = 300B feed views/day peak

### Storage Estimates

**Posts Metadata:**
- 500M posts/day × 1KB = 500GB/day
- 5 years retention: 500GB × 365 × 5 = 912TB

**Feed Data (if pre-computed):**
- 500M users × 200KB (cached feed) = 100TB
- With replication (3x): 300TB

**Social Graph:**
- 1B users × 200 follows avg × 8 bytes = 1.6TB
- With indexes: ~5TB

**Total Storage**: ~1.2PB over 5 years

### Bandwidth Estimates

- **Read bandwidth**: 100B feed views/day × 50KB avg = 5PB/day = 58GB/s
- **Write bandwidth**: 500M posts/day × 1KB = 500GB/day = 5.8MB/s
- **Peak bandwidth**: 3x average = 174GB/s

## Core Entities

### User
- **Attributes**: user_id, username, email, created_at
- **Relationships**: Follows users/pages/groups, creates posts, interacts with posts

### Post
- **Attributes**: post_id, user_id, content_type, content, media_url, like_count, comment_count, share_count, created_at
- **Relationships**: Belongs to user/page/group, has likes, comments, shares

### Follow
- **Attributes**: follower_id, followee_id, followee_type, created_at
- **Relationships**: Links user to user/page/group

### Interaction
- **Attributes**: interaction_id, user_id, post_id, interaction_type, created_at
- **Relationships**: Links user to post (like, comment, share, view)

## API

### 1. Get Feed
```
GET /api/v1/feed
Parameters:
  - user_id: user ID
  - cursor: pagination cursor (optional)
  - limit: number of posts to return (default: 20)
  - filter: optional filter (e.g., "photos_only")
Response:
  - posts: array of post objects
  - next_cursor: cursor for next page
  - has_more: boolean indicating more posts available
```

### 2. Refresh Feed
```
GET /api/v1/feed/refresh
Parameters:
  - user_id: user ID
Response:
  - new_posts_count: number of new posts since last view
  - posts: array of new post objects
```

### 3. Get Post Details
```
GET /api/v1/posts/{post_id}
Parameters:
  - post_id: post ID
Response:
  - post: post object with full details
```

### 4. Like Post
```
POST /api/v1/posts/{post_id}/like
Parameters:
  - user_id: user ID
  - post_id: post ID
Response:
  - like_count: updated like count
  - is_liked: boolean
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

## Data Flow

### Feed Generation Flow
1. Client requests feed → Load Balancer
2. Load Balancer → API Gateway
3. API Gateway → Feed Service
4. Feed Service checks Redis cache for pre-computed feed
5. If cache miss:
   - Fetch followed entities from Social Graph Service
   - Fetch cached posts (push model) from Redis
   - Fetch recent posts from celebrities (pull model) from Database
   - Merge and rank posts using Ranking Service
   - Cache result in Redis
6. Return feed to client

### Post Creation Flow
1. User creates post → API Gateway
2. API Gateway → Post Service
3. Post Service → Database (store post)
4. Post Service → Message Queue (for async processing)
5. Message Queue → Ranking Service (calculate relevance score)
6. Message Queue → Feed Service (fan-out to followers)
7. Feed Service updates followers' feed caches
8. Response returned to client

### Ranking Update Flow
1. User likes/comments on post → API Gateway
2. API Gateway → Interaction Service
3. Interaction Service → Database (store interaction)
4. Interaction Service → Message Queue
5. Message Queue → Ranking Service (recalculate score)
6. Ranking Service → Feed Service (update feed rankings)
7. Response returned to client

## Database Design

### Schema Design

**Users Table:**
```sql
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    INDEX idx_username (username)
);
```

**Posts Table:**
```sql
CREATE TABLE posts (
    post_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    content_type ENUM('text', 'photo', 'video', 'link') NOT NULL,
    content TEXT,
    media_url VARCHAR(512),
    like_count INT DEFAULT 0,
    comment_count INT DEFAULT 0,
    share_count INT DEFAULT 0,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    INDEX idx_user_created (user_id, created_at),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

**Follows Table:**
```sql
CREATE TABLE follows (
    follower_id BIGINT NOT NULL,
    followee_id BIGINT NOT NULL,
    followee_type ENUM('user', 'page', 'group') NOT NULL,
    created_at TIMESTAMP,
    PRIMARY KEY (follower_id, followee_id, followee_type),
    INDEX idx_follower (follower_id),
    INDEX idx_followee (followee_id, followee_type),
    FOREIGN KEY (follower_id) REFERENCES users(user_id)
);
```

**Feed Cache Table (for pre-computed feeds):**
```sql
CREATE TABLE feed_cache (
    user_id BIGINT NOT NULL,
    post_id BIGINT NOT NULL,
    score DECIMAL(10, 6) NOT NULL,
    created_at TIMESTAMP,
    PRIMARY KEY (user_id, post_id),
    INDEX idx_user_score (user_id, score DESC),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (post_id) REFERENCES posts(post_id)
);
```

**User Interactions Table:**
```sql
CREATE TABLE user_interactions (
    interaction_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    post_id BIGINT NOT NULL,
    interaction_type ENUM('like', 'comment', 'share', 'view') NOT NULL,
    created_at TIMESTAMP,
    INDEX idx_user_post (user_id, post_id),
    INDEX idx_post (post_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (post_id) REFERENCES posts(post_id)
);
```

### Database Sharding Strategy

**Shard by User ID:**
- User data, follows, and feed cache on same shard
- Enables efficient feed generation

**Shard by Post ID:**
- Posts distributed across shards
- Enables parallel processing

## High-Level Design

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
│ Feed        │  │ Ranking     │  │ Social Graph │
│ Service     │  │ Service     │  │ Service      │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Cache        │  │ Message      │  │ Database     │
│ (Redis)      │  │ Queue        │  │ (Sharded)    │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Feed Generation Strategies

### Approach 1: Pull Model (Fan-out on Read)

**How it works:**
- When user requests feed, fetch posts from all followed entities
- Rank and return top N posts

**Flow:**
1. Get list of followed users/pages/groups
2. Fetch recent posts from each entity
3. Merge and rank posts
4. Return top N posts

**Pros:**
- Simple implementation
- Always shows latest content
- No storage overhead for feed cache
- Easy to handle unfollows

**Cons:**
- Slow for users with many follows (O(n) queries)
- High database load
- Doesn't scale well

**Use Case:** Small-scale systems or users with few follows

### Approach 2: Push Model (Fan-out on Write)

**How it works:**
- When user posts, push to all followers' feed caches
- Feed retrieval is just reading from cache

**Flow:**
1. User creates post
2. Get list of followers
3. Add post to each follower's feed cache
4. When user requests feed, read from cache

**Pros:**
- Fast feed retrieval (O(1))
- Low latency
- Scales well for reads

**Cons:**
- High write load (fan-out to millions of followers)
- Storage overhead (duplicate posts in many caches)
- Slow for users with many followers (celebrities)
- Complex to handle unfollows (need to remove from cache)

**Use Case:** Users with few followers (< 1000)

### Approach 3: Hybrid Approach (Recommended)

**How it works:**
- Push model for normal users (< 1000 followers)
- Pull model for celebrities (> 1000 followers)
- Use Redis sorted sets for feed storage

**Flow:**
1. User creates post
2. If follower count < 1000:
   - Fan-out to all followers' feed caches
3. If follower count >= 1000:
   - Store post, don't fan-out
   - Followers pull posts on feed request
4. Feed retrieval:
   - Merge cached posts (push) + recent posts from celebrities (pull)
   - Rank and return

**Pros:**
- Balances read and write performance
- Handles both normal users and celebrities
- Scalable

**Cons:**
- More complex implementation
- Need to track follower counts

**Use Case:** Production systems at scale

## Deep Dive

### Component Design

#### 1. Feed Service

**Responsibilities:**
- Generate user feeds
- Handle pagination
- Merge push and pull feeds

**Feed Generation Flow:**
1. Check Redis cache for pre-computed feed
2. If cache miss:
   - Get followed entities from social graph
   - Fetch cached posts (push model) from Redis
   - Fetch recent posts from celebrities (pull model)
   - Merge and rank posts
   - Cache result
3. Return feed

**Redis Data Structure:**
```
Key: feed:{user_id}
Type: Sorted Set
Score: relevance_score (timestamp + engagement)
Value: post_id
TTL: 7 days
```

#### 2. Ranking Service

**Ranking Factors:**
1. **Recency**: Newer posts ranked higher
2. **Engagement**: Likes, comments, shares boost ranking
3. **User Affinity**: Posts from frequently interacted users ranked higher
4. **Content Type**: Videos/images ranked higher than text
5. **Post Quality**: Spam detection, content quality score

**Ranking Algorithm:**
```
score = (
    recency_score * 0.3 +
    engagement_score * 0.4 +
    affinity_score * 0.2 +
    content_score * 0.1
) * quality_multiplier
```

**Recency Score:**
```
recency_score = 1 / (1 + hours_since_post)
```

**Engagement Score:**
```
engagement_score = (
    like_count * 1.0 +
    comment_count * 2.0 +
    share_count * 3.0
) / max_engagement
```

**User Affinity Score:**
```
affinity_score = (
    interaction_count_with_user / total_interactions
) * interaction_recency_factor
```

**Implementation:**
- Pre-compute scores for posts
- Store scores in Redis sorted sets
- Update scores as engagement changes

#### 3. Social Graph Service

**Responsibilities:**
- Manage follow/unfollow relationships
- Cache social graph data
- Provide efficient lookups

**Data Structures:**
```
Key: followers:{user_id}
Type: Set
Value: follower user_ids
TTL: 1 hour

Key: following:{user_id}
Type: Set
Value: followee user_ids
TTL: 1 hour

Key: follower_count:{user_id}
Type: String (counter)
Value: follower count
TTL: 1 hour
```

**Operations:**
- Follow: Add to sets, increment counter
- Unfollow: Remove from sets, decrement counter
- Get followers: Read from cache or DB

#### 4. Real-time Update Service

**Requirements:**
- Update feed when new posts are created
- Push updates to active users

**Implementation Options:**

**Option 1: Polling**
- Client polls for updates every few seconds
- Simple but inefficient

**Option 2: WebSockets**
- Maintain persistent connection
- Push updates immediately
- Better for real-time but higher server load

**Option 3: Server-Sent Events (SSE)**
- One-way push from server
- Simpler than WebSockets
- Good for feed updates

**Recommended: Hybrid**
- WebSockets for active users (last 5 minutes)
- Polling for inactive users
- Use message queue (Kafka) to distribute updates

**Flow:**
1. User creates post
2. Publish to Kafka topic
3. Feed service consumes and updates feed caches
4. Push notification service sends to active users via WebSocket
5. Inactive users get updates on next feed request

#### 5. Feed Pre-computation Service

**Purpose:**
- Pre-compute feeds for better performance
- Update feeds asynchronously

**Flow:**
1. Background worker processes new posts
2. For each post:
   - Get followers
   - Calculate relevance score
   - Add to followers' feed caches
3. Periodically refresh feed rankings

**Optimizations:**
- Batch processing for efficiency
- Prioritize active users' feeds
- Use message queue for async processing

### Detailed Design

### Caching Strategy

**Multi-level Caching:**

**L1: Application Cache (In-memory)**
- Recent feed requests
- TTL: 1 minute

**L2: Redis Cache**
- Pre-computed feeds
- Social graph data
- Post metadata
- TTL: 1 hour for feeds, 24 hours for profiles

**L3: CDN Cache**
- Static content (images, videos)
- TTL: 7 days

**Cache Invalidation:**
- On new post: Invalidate followers' feed caches
- On like/comment: Update post cache
- On follow/unfollow: Invalidate feed cache

### Message Queue Architecture

**Use Cases:**
1. **Feed Updates**: Fan-out posts to followers
2. **Ranking Updates**: Recalculate scores as engagement changes
3. **Real-time Notifications**: Push updates to users
4. **Analytics**: Track feed views, interactions

**Technology**: Apache Kafka

**Topics:**
- `posts.created`: New posts
- `posts.updated`: Post updates (likes, comments)
- `follows.created`: New follow relationships
- `feed.updates`: Feed update events

### Database Optimization

**Indexes:**
- `posts(user_id, created_at)`: Fast user post queries
- `follows(follower_id)`: Fast follower lookups
- `feed_cache(user_id, score)`: Fast feed retrieval

**Partitioning:**
- Shard by user_id for user-related data
- Shard by post_id for posts
- Use consistent hashing

**Replication:**
- Master-slave replication
- Read replicas for read-heavy workloads
- Geographic distribution for low latency

### Handling Edge Cases

**Hot Users (Celebrities):**
- Use pull model instead of push
- Dedicated infrastructure
- Aggressive caching
- Rate limiting

**Users with Many Follows:**
- Limit feed size (top 1000 posts)
- Use sampling for ranking
- Lazy loading

**Feed Freshness:**
- Background refresh for active users
- Real-time updates via WebSocket
- TTL-based cache invalidation

### Scalability Considerations

### Horizontal Scaling

**Stateless Services:**
- Feed Service, Ranking Service, API Gateway
- Scale based on CPU/memory metrics
- Use load balancer for distribution

**Stateful Services:**
- Redis cluster for caching
- Database sharding for storage
- Message queue partitioning

### Performance Optimizations

1. **Feed Pre-computation**
   - Pre-compute feeds for active users
   - Update asynchronously

2. **Batch Processing**
   - Batch feed updates
   - Batch database queries

3. **Lazy Loading**
   - Load feed incrementally
   - Load images/videos on demand

4. **CDN Integration**
   - Serve static content from CDN
   - Reduce origin server load

### Security Considerations

1. **Authentication**: JWT tokens, OAuth 2.0
2. **Authorization**: Verify user can access feed
3. **Rate Limiting**: Prevent abuse
4. **Input Validation**: Sanitize user inputs
5. **Privacy**: Respect user privacy settings
6. **Content Filtering**: Filter inappropriate content

### Monitoring & Observability

**Key Metrics:**
- Feed generation latency (p50, p95, p99)
- Cache hit rates
- Feed freshness (time to show new posts)
- API response times
- Error rates
- Database query performance

**Tools:**
- Prometheus + Grafana for metrics
- ELK stack for logging
- Distributed tracing (Jaeger/Zipkin)

### Trade-offs and Optimizations

### Trade-offs

1. **Consistency vs Availability**
   - Choose eventual consistency for feeds
   - Acceptable delay for feed updates

2. **Storage vs Compute**
   - Pre-compute feeds (more storage, faster reads)
   - Compute on-demand (less storage, slower reads)
   - Hybrid balances both

3. **Latency vs Freshness**
   - Cache feeds (lower latency, stale data)
   - Real-time updates (higher latency, fresh data)
   - Use cache with short TTL + real-time updates

### Optimizations

1. **Feed Ranking**
   - Pre-compute scores
   - Update scores incrementally
   - Use machine learning for personalization

2. **Caching**
   - Cache warm-up for active users
   - Predictive caching
   - Cache aside pattern

3. **Database**
   - Read replicas for scaling reads
   - Connection pooling
   - Query optimization

## What Interviewers Look For

### Distributed Systems Skills

1. **Feed Generation Strategy**
   - Deep understanding of push/pull/hybrid
   - When to use each approach
   - Trade-offs and optimizations
   - **Red Flags**: Only one approach, no understanding of trade-offs

2. **Ranking Algorithm Design**
   - Relevance scoring
   - Personalization
   - Real-time ranking
   - **Red Flags**: Simple chronological only, no ranking, poor algorithm

3. **Real-Time Updates**
   - WebSocket/SSE usage
   - Pub/sub architecture
   - Low-latency delivery
   - **Red Flags**: Polling, high latency, no real-time

### Problem-Solving Approach

1. **Scale Thinking**
   - Billions of users
   - Trillions of feed views
   - High read:write ratio (200:1)
   - **Red Flags**: Designing for small scale, ignoring read-heavy nature

2. **Trade-off Analysis**
   - Push vs pull trade-offs
   - Consistency vs freshness
   - Latency vs accuracy
   - **Red Flags**: No trade-off discussion, wrong choices

3. **Edge Cases**
   - Celebrity users
   - Viral posts
   - Inactive users
   - **Red Flags**: Ignoring edge cases, one-size-fits-all

### System Design Skills

1. **Caching Strategy**
   - Multi-level caching
   - Feed pre-computation
   - Cache invalidation
   - **Red Flags**: No caching, poor strategy, cache stampede

2. **Database Design**
   - Efficient querying
   - Read replicas
   - Proper indexing
   - **Red Flags**: No read scaling, missing indexes

3. **Message Queue Usage**
   - Async processing
   - Event-driven updates
   - **Red Flags**: Synchronous processing, blocking operations

### Communication Skills

1. **Algorithm Explanation**
   - Can explain ranking algorithm
   - Discusses personalization
   - **Red Flags**: No algorithm understanding, vague explanations

2. **Architecture Justification**
   - Explains design decisions
   - Discusses alternatives
   - **Red Flags**: No justification, no alternatives considered

### Meta-Specific Focus

1. **Feed Generation Mastery**
   - Deep understanding of Meta's patterns
   - Hybrid approach knowledge
   - **Key**: Show Meta-specific knowledge

2. **Ranking Expertise**
   - Understanding of relevance ranking
   - Personalization concepts
   - **Key**: Demonstrate algorithmic thinking

## Summary

Designing a news feed system requires handling:

1. **Massive Scale**: Billions of users, trillions of feed views
2. **High Read:Write Ratio**: 200:1 read to write ratio
3. **Real-time Updates**: Show new posts quickly
4. **Personalization**: Rank posts by relevance
5. **Social Graph**: Efficient follow/unfollow operations

**Key Architectural Decisions:**
- Hybrid feed generation (push for normal users, pull for celebrities)
- Redis sorted sets for feed storage
- Pre-computed feeds with async updates
- Multi-level caching strategy
- Message queue for async processing
- Ranking algorithm balancing recency, engagement, and affinity

**Feed Generation Strategy:**
- **Push Model**: For users with < 1000 followers
- **Pull Model**: For users with >= 1000 followers
- **Hybrid**: Combine both approaches

This design can handle the scale of major social media platforms while maintaining low latency and high availability.

