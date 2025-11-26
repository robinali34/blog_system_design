---
layout: post
title: "Design a Social Media Feed like Twitter - System Design Interview"
date: 2025-11-20
categories: [System Design, Interview Example, Distributed Systems, Real-Time Systems, Social Media, Feed Generation]
excerpt: "A comprehensive guide to designing a social media feed like Twitter, covering feed generation strategies (push vs pull), timeline generation, real-time updates, tweet storage, follow/unfollow system, like/retweet mechanisms, search functionality, and architectural patterns for handling billions of tweets, millions of users, and real-time feed updates."
---

## Introduction

Twitter is a social media platform that allows users to post short messages (tweets), follow other users, and view a personalized feed of tweets from users they follow. The system handles billions of tweets, millions of concurrent users, and requires real-time feed generation and updates.

This post provides a detailed walkthrough of designing a social media feed like Twitter, covering key architectural decisions, feed generation strategies (push vs pull hybrid approach), timeline generation, real-time updates, tweet storage, follow/unfollow mechanisms, and scalability challenges. This is one of the most common system design interview questions that tests your understanding of distributed systems, caching strategies, feed generation algorithms, and handling massive scale.

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
   - [Feed Generation Strategy](#feed-generation-strategy)
   - [Timeline Generation Service](#timeline-generation-service)
   - [Tweet Creation Service](#tweet-creation-service)
   - [Follow/Unfollow Service](#followunfollow-service)
   - [Like/Retweet/Reply Service](#likeretweetreply-service)
   - [Search Service](#search-service)
   - [Real-Time Updates](#real-time-updates)
   - [Media Handling](#media-handling)
   - [Scalability Considerations](#scalability-considerations)
   - [Security Considerations](#security-considerations)
   - [Monitoring & Observability](#monitoring--observability)
   - [Trade-offs and Optimizations](#trade-offs-and-optimizations)
10. [Summary](#summary)

## Problem Statement

**Design a social media feed like Twitter with the following features:**

1. User registration and authentication
2. Post tweets (text, images, videos)
3. Follow/unfollow users
4. View personalized home timeline (feed)
5. View user profile timeline
6. Like tweets
7. Retweet tweets
8. Reply to tweets
9. Search tweets and users
10. Real-time feed updates
11. Trending topics
12. Notifications (mentions, likes, retweets, follows)

**Scale Requirements:**
- 500 million+ users
- 200 million+ daily active users
- 500 million+ tweets per day
- Peak: 6,000 tweets per second
- Average user follows 200 users
- Average user has 1,000 followers
- Peak: 100 million concurrent users viewing feeds
- Average feed size: 200 tweets
- Total tweets: 500+ billion tweets

## Requirements

### Functional Requirements

**Core Features:**

1. **User Management**:
   - User registration and authentication
   - User profiles (username, bio, profile picture)
   - User verification (blue checkmark)

2. **Tweet Creation**:
   - Post tweets (280 characters)
   - Include images (up to 4 per tweet)
   - Include videos (up to 2 minutes)
   - Reply to tweets
   - Quote tweet (retweet with comment)

3. **Social Graph**:
   - Follow users
   - Unfollow users
   - View followers list
   - View following list
   - Block users

4. **Feed Generation**:
   - Home timeline (tweets from followed users)
   - User timeline (tweets from specific user)
   - Real-time feed updates
   - Feed ranking/ordering

5. **Engagement**:
   - Like tweets
   - Retweet tweets
   - Reply to tweets
   - Bookmark tweets

6. **Search**:
   - Search tweets by keyword
   - Search users by username/name
   - Trending topics
   - Hashtag search

7. **Notifications**:
   - Mentions (@username)
   - Likes on your tweets
   - Retweets of your tweets
   - New followers
   - Replies to your tweets

**Out of Scope**:
- Direct messaging
- Live streaming
- Advanced analytics
- Advertising system
- Video streaming (focus on upload/storage)

### Non-Functional Requirements

1. **Availability**: 99.9% uptime
2. **Reliability**: No tweet loss, guaranteed delivery
3. **Performance**:
   - Feed load time: < 2 seconds (p95)
   - Tweet creation: < 500ms
   - Search response: < 500ms
   - Real-time updates: < 1 second latency
4. **Scalability**: Handle 6,000 tweets/second (peak)
5. **Consistency**: Eventually consistent for likes/retweets, strong consistency for tweets
6. **Durability**: All tweets must be persisted
7. **Real-Time**: Feed updates within 1 second
8. **Geographic Distribution**: Global presence with regional data centers

## Capacity Estimation

### Traffic Estimates

**Assumptions:**
- 500 million total users
- 200 million daily active users (DAU)
- 500 million tweets per day
- Peak traffic: 3x average (1.5 billion tweets/day)
- Average user views feed 10 times per day
- Average user follows 200 users
- Average user has 1,000 followers

**Read Traffic:**
- Feed views: 200M DAU × 10 views/day = 2 billion feed views/day
- Average QPS: 2B / 86400 = ~23,000 QPS
- Peak QPS: 23,000 × 3 = ~69,000 QPS
- Each feed view: ~200 tweets = 200 reads
- Total read QPS: 69,000 × 200 = ~13.8M reads/sec (from cache)

**Write Traffic:**
- Tweet creation: 500M tweets/day = ~5,800 tweets/sec
- Peak write QPS: 5,800 × 3 = ~17,400 tweets/sec
- Likes: 10x tweets = 50 billion likes/day = ~580K likes/sec
- Retweets: 5x tweets = 2.5 billion retweets/day = ~29K retweets/sec
- Follows: 1 billion follows/day = ~11.5K follows/sec
- Total writes: ~17,400 + 580K + 29K + 11.5K = ~637K writes/sec

### Storage Estimates

**Assumptions:**
- Tweet: 280 characters = ~280 bytes (text)
- Tweet metadata: 500 bytes (user_id, timestamp, etc.)
- Image: 200KB average
- Video: 5MB average
- 10% of tweets have images (1-4 images)
- 5% of tweets have videos
- Store tweets indefinitely
- Store media for 7 years

**Storage Calculations:**
- Text tweets: 500M/day × 365 days × 780 bytes = ~142TB/year
- Images: 500M/day × 0.10 × 2 images × 200KB × 365 days = ~7.3PB/year
- Videos: 500M/day × 0.05 × 5MB × 365 days = ~45.6PB/year
- Total storage: ~53PB/year
- With replication (3x): ~159PB/year

**User Data:**
- User profile: 1KB per user
- 500M users × 1KB = 500GB
- Social graph (follows): 500M users × 200 follows × 16 bytes = 1.6TB
- Total user data: ~2TB

### Bandwidth Estimates

**Assumptions:**
- Feed response: 200 tweets × 1KB = 200KB
- Tweet creation: 10KB (including media metadata)
- Image upload: 200KB
- Video upload: 5MB

**Bandwidth Calculations:**
- Feed reads: 69K QPS × 200KB = 13.8GB/sec = 110Gbps
- Tweet writes: 17.4K QPS × 10KB = 174MB/sec = 1.4Gbps
- Image uploads: 17.4K QPS × 0.10 × 200KB = 348MB/sec = 2.8Gbps
- Video uploads: 17.4K QPS × 0.05 × 5MB = 4.35GB/sec = 35Gbps
- Total bandwidth: ~150Gbps (peak)

## Core Entities

### User

```python
User {
    user_id: UUID (Primary Key)
    username: String (unique)
    email: String (unique)
    display_name: String
    bio: String (max 160 characters)
    profile_image_url: String
    banner_image_url: String
    verified: Boolean
    followers_count: Integer
    following_count: Integer
    tweets_count: Integer
    created_at: Timestamp
    updated_at: Timestamp
    status: Enum (ACTIVE, SUSPENDED, DELETED)
}
```

### Tweet

```python
Tweet {
    tweet_id: UUID (Primary Key)
    user_id: UUID (Foreign Key -> User)
    content: String (max 280 characters)
    tweet_type: Enum (TWEET, REPLY, RETWEET, QUOTE_TWEET)
    parent_tweet_id: UUID (Foreign Key -> Tweet, nullable, for replies)
    retweeted_from_tweet_id: UUID (Foreign Key -> Tweet, nullable, for retweets)
    quoted_tweet_id: UUID (Foreign Key -> Tweet, nullable, for quote tweets)
    media_urls: Array[String] (images/videos)
    hashtags: Array[String]
    mentions: Array[UUID] (user_ids)
    likes_count: Integer
    retweets_count: Integer
    replies_count: Integer
    quote_tweets_count: Integer
    created_at: Timestamp
    updated_at: Timestamp
    deleted: Boolean
}
```

### Follow

```python
Follow {
    follow_id: UUID (Primary Key)
    follower_id: UUID (Foreign Key -> User)
    followee_id: UUID (Foreign Key -> User)
    created_at: Timestamp
    # Composite unique index on (follower_id, followee_id)
}
```

### Like

```python
Like {
    like_id: UUID (Primary Key)
    user_id: UUID (Foreign Key -> User)
    tweet_id: UUID (Foreign Key -> Tweet)
    created_at: Timestamp
    # Composite unique index on (user_id, tweet_id)
}
```

### Retweet

```python
Retweet {
    retweet_id: UUID (Primary Key)
    user_id: UUID (Foreign Key -> User)
    tweet_id: UUID (Foreign Key -> Tweet)
    created_at: Timestamp
    # Composite unique index on (user_id, tweet_id)
}
```

### Timeline

```python
Timeline {
    timeline_id: UUID (Primary Key)
    user_id: UUID (Foreign Key -> User)
    tweet_id: UUID (Foreign Key -> Tweet)
    score: Float (for ranking)
    created_at: Timestamp
    # Index on (user_id, score DESC) for feed queries
}
```

## API

### Tweet APIs

```http
# Post a tweet
POST /api/v1/tweets
Request Body:
{
    "user_id": "uuid",
    "content": "Hello, Twitter!",
    "media_urls": ["https://..."],
    "reply_to_tweet_id": null
}
Response:
{
    "tweet_id": "uuid",
    "user_id": "uuid",
    "content": "Hello, Twitter!",
    "created_at": "2025-11-20T10:00:00Z",
    "likes_count": 0,
    "retweets_count": 0,
    "replies_count": 0
}

# Get tweet
GET /api/v1/tweets/{tweet_id}
Response:
{
    "tweet_id": "uuid",
    "user": {
        "user_id": "uuid",
        "username": "johndoe",
        "display_name": "John Doe",
        "verified": false
    },
    "content": "Hello, Twitter!",
    "created_at": "2025-11-20T10:00:00Z",
    "likes_count": 150,
    "retweets_count": 25,
    "replies_count": 10,
    "liked": false,
    "retweeted": false
}

# Delete tweet
DELETE /api/v1/tweets/{tweet_id}
Response:
{
    "tweet_id": "uuid",
    "status": "deleted"
}

# Like tweet
POST /api/v1/tweets/{tweet_id}/like
Request Body:
{
    "user_id": "uuid"
}
Response:
{
    "tweet_id": "uuid",
    "liked": true,
    "likes_count": 151
}

# Unlike tweet
DELETE /api/v1/tweets/{tweet_id}/like?user_id={user_id}
Response:
{
    "tweet_id": "uuid",
    "liked": false,
    "likes_count": 150
}

# Retweet
POST /api/v1/tweets/{tweet_id}/retweet
Request Body:
{
    "user_id": "uuid"
}
Response:
{
    "tweet_id": "uuid",
    "retweeted": true,
    "retweets_count": 26
}

# Reply to tweet
POST /api/v1/tweets/{tweet_id}/reply
Request Body:
{
    "user_id": "uuid",
    "content": "Great tweet!"
}
Response:
{
    "tweet_id": "uuid",
    "parent_tweet_id": "uuid",
    "content": "Great tweet!",
    "created_at": "2025-11-20T10:05:00Z"
}
```

### Feed APIs

```http
# Get home timeline (feed)
GET /api/v1/timeline/home?user_id={user_id}&limit=200&max_id={max_id}
Response:
{
    "tweets": [
        {
            "tweet_id": "uuid",
            "user": {...},
            "content": "...",
            "created_at": "...",
            "likes_count": 150,
            "retweets_count": 25,
            "liked": false,
            "retweeted": false
        },
        ...
    ],
    "next_max_id": "uuid",
    "has_more": true
}

# Get user timeline
GET /api/v1/timeline/user/{user_id}?limit=200&max_id={max_id}
Response:
{
    "tweets": [...],
    "next_max_id": "uuid",
    "has_more": true
}

# Get tweet replies
GET /api/v1/tweets/{tweet_id}/replies?limit=50&max_id={max_id}
Response:
{
    "replies": [...],
    "next_max_id": "uuid",
    "has_more": true
}
```

### Social Graph APIs

```http
# Follow user
POST /api/v1/users/{user_id}/follow
Request Body:
{
    "follower_id": "uuid"
}
Response:
{
    "follower_id": "uuid",
    "followee_id": "uuid",
    "following": true
}

# Unfollow user
DELETE /api/v1/users/{user_id}/follow?follower_id={follower_id}
Response:
{
    "follower_id": "uuid",
    "followee_id": "uuid",
    "following": false
}

# Get followers
GET /api/v1/users/{user_id}/followers?limit=100&cursor={cursor}
Response:
{
    "followers": [
        {
            "user_id": "uuid",
            "username": "johndoe",
            "display_name": "John Doe",
            "followed_at": "2025-11-20T10:00:00Z"
        },
        ...
    ],
    "next_cursor": "cursor",
    "has_more": true
}

# Get following
GET /api/v1/users/{user_id}/following?limit=100&cursor={cursor}
Response:
{
    "following": [...],
    "next_cursor": "cursor",
    "has_more": true
}
```

### Search APIs

```http
# Search tweets
GET /api/v1/search/tweets?q=hello&limit=50&max_id={max_id}
Response:
{
    "tweets": [...],
    "next_max_id": "uuid",
    "has_more": true
}

# Search users
GET /api/v1/search/users?q=johndoe&limit=20
Response:
{
    "users": [
        {
            "user_id": "uuid",
            "username": "johndoe",
            "display_name": "John Doe",
            "verified": false,
            "followers_count": 1000
        },
        ...
    ]
}

# Get trending topics
GET /api/v1/trends?woeid=1
Response:
{
    "trends": [
        {
            "name": "#HelloWorld",
            "tweet_volume": 100000,
            "url": "https://..."
        },
        ...
    ]
}
```

## Data Flow

### Tweet Creation Flow

```
1. User posts tweet
   └─> Client App
       └─> API Gateway
           └─> Tweet Service
               ├─> Validates tweet (length, content)
               ├─> Uploads media (if any)
               │   └─> Media Service
               │       └─> Object Storage (S3)
               ├─> Extracts hashtags and mentions
               ├─> Creates tweet record
               │   └─> Database (Tweets table)
               ├─> Updates user tweet count
               ├─> Publishes tweet event
               │   └─> Message Queue (Kafka)
               │       └─> Topics: tweets, user-timeline, feed-updates
               └─> Returns tweet_id

2. Feed Service processes tweet
   └─> Feed Service (consumes from Kafka)
       ├─> Gets user's followers list
       │   └─> Social Graph Service
       ├─> For each follower:
       │   ├─> Adds tweet to follower's timeline cache
       │   │   └─> Redis (Timeline Cache)
       │   └─> Sends real-time update
       │       └─> WebSocket/SSE
       └─> Updates user timeline cache
           └─> Redis

3. Search Service indexes tweet
   └─> Search Service (consumes from Kafka)
       ├─> Indexes tweet content
       └─> Elasticsearch

4. Notification Service processes mentions
   └─> Notification Service (consumes from Kafka)
       ├─> Extracts mentions (@username)
       ├─> Sends notifications to mentioned users
       └─> Push Notification Service
```

### Feed Generation Flow

```
1. User requests home timeline
   └─> Client App
       └─> API Gateway
           └─> Timeline Service
               ├─> Checks cache
               │   └─> Redis (Timeline Cache)
               │       └─> Key: user:{user_id}:timeline
               │
               ├─> If cache miss or stale:
               │   ├─> Gets user's following list
               │   │   └─> Social Graph Service
               │   ├─> Fetches recent tweets from followed users
               │   │   └─> Database (Tweets table, indexed by user_id)
               │   ├─> Merges and ranks tweets
               │   │   ├─> By timestamp (newest first)
               │   │   └─> By engagement score (likes, retweets)
               │   ├─> Caches timeline
               │   │   └─> Redis
               │   └─> Returns tweets
               │
               └─> If cache hit:
                   └─> Returns cached tweets

2. Real-time updates
   └─> WebSocket/SSE connection
       ├─> Listens for new tweets from followed users
       └─> Pushes updates to client
```

### Like/Retweet Flow

```
1. User likes tweet
   └─> Client App
       └─> API Gateway
           └─> Engagement Service
               ├─> Creates like record
               │   └─> Database (Likes table)
               ├─> Increments tweet likes_count
               │   └─> Database (Tweets table)
               │   └─> Cache (Redis counter)
               ├─> Publishes like event
               │   └─> Kafka
               └─> Returns updated likes_count

2. Notification Service processes like
   └─> Notification Service (consumes from Kafka)
       ├─> Gets tweet author
       ├─> Sends notification to author
       └─> Push Notification Service
```

## Database Design

### Schema Design

#### Users Table

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    bio VARCHAR(160),
    profile_image_url VARCHAR(500),
    banner_image_url VARCHAR(500),
    verified BOOLEAN DEFAULT FALSE,
    followers_count INT DEFAULT 0,
    following_count INT DEFAULT 0,
    tweets_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    status ENUM('ACTIVE', 'SUSPENDED', 'DELETED') DEFAULT 'ACTIVE',
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_created_at (created_at)
);
```

#### Tweets Table

```sql
CREATE TABLE tweets (
    tweet_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    content VARCHAR(280) NOT NULL,
    tweet_type ENUM('TWEET', 'REPLY', 'RETWEET', 'QUOTE_TWEET') DEFAULT 'TWEET',
    parent_tweet_id UUID,
    retweeted_from_tweet_id UUID,
    quoted_tweet_id UUID,
    media_urls JSON,
    hashtags JSON,
    mentions JSON,
    likes_count INT DEFAULT 0,
    retweets_count INT DEFAULT 0,
    replies_count INT DEFAULT 0,
    quote_tweets_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (parent_tweet_id) REFERENCES tweets(tweet_id),
    FOREIGN KEY (retweeted_from_tweet_id) REFERENCES tweets(tweet_id),
    FOREIGN KEY (quoted_tweet_id) REFERENCES tweets(tweet_id),
    INDEX idx_user_id (user_id),
    INDEX idx_user_id_created_at (user_id, created_at DESC),
    INDEX idx_parent_tweet_id (parent_tweet_id),
    INDEX idx_created_at (created_at DESC),
    FULLTEXT INDEX idx_content (content)
) PARTITION BY RANGE (YEAR(created_at), MONTH(created_at));
```

#### Follows Table

```sql
CREATE TABLE follows (
    follow_id UUID PRIMARY KEY,
    follower_id UUID NOT NULL,
    followee_id UUID NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (follower_id) REFERENCES users(user_id),
    FOREIGN KEY (followee_id) REFERENCES users(user_id),
    UNIQUE KEY unique_follow (follower_id, followee_id),
    INDEX idx_follower_id (follower_id),
    INDEX idx_followee_id (followee_id),
    INDEX idx_created_at (created_at)
);
```

#### Likes Table

```sql
CREATE TABLE likes (
    like_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    tweet_id UUID NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (tweet_id) REFERENCES tweets(tweet_id),
    UNIQUE KEY unique_like (user_id, tweet_id),
    INDEX idx_user_id (user_id),
    INDEX idx_tweet_id (tweet_id),
    INDEX idx_created_at (created_at)
);
```

#### Retweets Table

```sql
CREATE TABLE retweets (
    retweet_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    tweet_id UUID NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (tweet_id) REFERENCES tweets(tweet_id),
    UNIQUE KEY unique_retweet (user_id, tweet_id),
    INDEX idx_user_id (user_id),
    INDEX idx_tweet_id (tweet_id),
    INDEX idx_created_at (created_at)
);
```

#### Timeline Table (Fan-out Cache)

```sql
CREATE TABLE timeline_cache (
    timeline_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    tweet_id UUID NOT NULL,
    score FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (tweet_id) REFERENCES tweets(tweet_id),
    INDEX idx_user_id_score (user_id, score DESC),
    INDEX idx_user_id_created_at (user_id, created_at DESC)
) PARTITION BY HASH(user_id);
```

### Database Sharding Strategy

**Sharding by User ID**:

- **Strategy**: Hash-based sharding on `user_id`
- **Shard Key**: Hash of `user_id`
- **Benefits**:
  - Even distribution
  - User's tweets on same shard
  - User's timeline queries on same shard
- **Challenges**:
  - Cross-shard queries for feed generation
  - Follow relationships across shards

**Sharding by Tweet ID**:

- **Strategy**: Hash-based sharding on `tweet_id`
- **Shard Key**: Hash of `tweet_id`
- **Benefits**:
  - Even distribution
  - Simple routing
- **Challenges**:
  - User timeline queries require querying all shards
  - Feed generation requires querying multiple shards

**Hybrid Approach (Recommended)**:

1. **Tweets Table**: Shard by `user_id` (user's tweets on same shard)
2. **Timeline Cache**: Shard by `user_id` (user's timeline on same shard)
3. **Follows Table**: Shard by `follower_id` (user's following list on same shard)
4. **Likes/Retweets**: Shard by `tweet_id` (even distribution)
5. **Search**: Use Elasticsearch (separate search index)

**Fan-out Strategy**:

- **Push Model**: Pre-compute timelines for active users
- **Pull Model**: Compute timelines on-demand for inactive users
- **Hybrid**: Push for users with < 1M followers, pull for users with > 1M followers

## High-Level Design

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Applications                      │
│  ┌──────────────┐                    ┌──────────────┐          │
│  │  Web App     │                    │  Mobile App  │          │
│  └──────┬───────┘                    └──────┬───────┘          │
└─────────┼────────────────────────────────────┼──────────────────┘
          │                                    │
          │ HTTPS/WebSocket                    │ HTTPS/WebSocket
          │                                    │
┌─────────┴────────────────────────────────────┴──────────────────┐
│                         API Gateway                             │
│                    (Load Balancer + Routing)                     │
└─────────┬────────────────────────────────────┬──────────────────┘
          │                                    │
          ├────────────────────────────────────┤
          │                                    │
┌─────────┴────────────────────────────────────┴──────────────────┐
│                      Application Services                        │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Tweet      │  │  Timeline    │  │  Social      │        │
│  │   Service    │  │  Service     │  │  Graph       │        │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘        │
│         │                 │                 │                  │
│  ┌──────┴─────────────────┴─────────────────┴───────┐        │
│  │              Message Queue (Kafka)                │        │
│  └──────────────────────────────────────────────────┘        │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ Engagement   │  │   Search    │  │ Notification │        │
│  │   Service    │  │   Service    │  │   Service    │        │
│  └──────────────┘  └──────┬───────┘  └──────┬───────┘        │
│                           │                 │                  │
│  ┌─────────────────────────┴─────────────────┴───────┐        │
│  │              External Services                     │        │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐        │        │
│  │  │   S3     │  │Elasticsearch│ │   Push   │        │        │
│  │  │  (Media) │  │  (Search) │  │ Service │        │        │
│  │  └──────────┘  └──────────┘  └──────────┘        │        │
│  └──────────────────────────────────────────────────┘        │
└──────────────────────────────────────────────────────────────┘
          │                                    │
          ├────────────────────────────────────┤
          │                                    │
┌─────────┴────────────────────────────────────┴──────────────────┐
│                         Data Layer                                │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  PostgreSQL   │  │   Redis      │  │  Elasticsearch│        │
│  │  (Primary DB) │  │  (Cache +    │  │  (Search)    │        │
│  │               │  │   Timeline)  │  │               │        │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                   │
│  ┌──────────────┐                                              │
│  │   S3          │                                              │
│  │  (Media)       │                                              │
│  └──────────────┘                                              │
└───────────────────────────────────────────────────────────────────┘
```

## Deep Dive

### Feed Generation Strategy

#### Problem

Generate personalized home timeline for millions of users, showing tweets from users they follow, in real-time, with low latency.

#### Solution: Hybrid Push-Pull Model

**Push Model (Fan-out)**:
- When user posts tweet, push to all followers' timelines
- Pre-computed timelines stored in cache
- Fast reads, slower writes

**Pull Model (Fan-in)**:
- When user requests feed, pull tweets from followed users
- Computed on-demand
- Slower reads, faster writes

**Hybrid Approach**:
- **Push** for users with < 1M followers (most users)
- **Pull** for users with > 1M followers (celebrities/influencers)
- **Push** for active users (frequent feed views)
- **Pull** for inactive users (rare feed views)

**Implementation**:

```python
class FeedService:
    def post_tweet(self, user_id, tweet):
        """
        Post tweet and fan-out to followers
        """
        # Create tweet
        tweet_id = self.create_tweet(user_id, tweet)
        
        # Get followers
        followers = self.get_followers(user_id)
        
        # Fan-out threshold
        FAN_OUT_THRESHOLD = 1_000_000
        
        if len(followers) < FAN_OUT_THRESHOLD:
            # Push model: Fan-out to all followers
            self.fan_out_tweet(user_id, tweet_id, followers)
        else:
            # Pull model: Don't fan-out (compute on-demand)
            # Still update user's own timeline
            self.update_user_timeline(user_id, tweet_id)
        
        return tweet_id
    
    def fan_out_tweet(self, user_id, tweet_id, followers):
        """
        Push tweet to followers' timelines
        """
        # Batch process followers
        batch_size = 1000
        
        for i in range(0, len(followers), batch_size):
            batch = followers[i:i+batch_size]
            
            # Add to timeline cache for each follower
            timeline_entries = [
                {
                    "user_id": follower_id,
                    "tweet_id": tweet_id,
                    "score": self.calculate_score(tweet_id),
                    "created_at": time.now()
                }
                for follower_id in batch
            ]
            
            # Batch insert to timeline cache
            self.timeline_cache.batch_insert(timeline_entries)
            
            # Publish to Kafka for real-time updates
            self.kafka_producer.send(
                topic="timeline-updates",
                value={
                    "user_ids": batch,
                    "tweet_id": tweet_id
                }
            )
    
    def get_home_timeline(self, user_id, limit=200, max_id=None):
        """
        Get home timeline for user
        """
        # Check cache first
        cache_key = f"timeline:{user_id}"
        cached_timeline = self.redis.get(cache_key)
        
        if cached_timeline:
            return self.filter_timeline(cached_timeline, limit, max_id)
        
        # Cache miss: Check if user has push timeline
        if self.has_push_timeline(user_id):
            # Load from timeline cache
            timeline = self.timeline_cache.get_timeline(
                user_id=user_id,
                limit=limit,
                max_id=max_id
            )
        else:
            # Pull model: Compute on-demand
            timeline = self.compute_timeline_pull(user_id, limit, max_id)
        
        # Cache timeline
        self.redis.setex(
            cache_key,
            300,  # 5-minute TTL
            timeline
        )
        
        return timeline
    
    def compute_timeline_pull(self, user_id, limit, max_id):
        """
        Pull tweets from followed users on-demand
        """
        # Get following list
        following = self.get_following(user_id)
        
        # Get recent tweets from each followed user
        tweets = []
        for followee_id in following:
            user_tweets = self.get_user_tweets(
                followee_id,
                limit=10  # Recent tweets per user
            )
            tweets.extend(user_tweets)
        
        # Merge and sort by timestamp
        tweets.sort(key=lambda t: t.created_at, reverse=True)
        
        # Rank by engagement score
        tweets = self.rank_tweets(tweets)
        
        return tweets[:limit]
```

### Timeline Generation Service

#### Problem

Generate ranked timeline with tweets from followed users, considering recency and engagement.

#### Solution: Ranking Algorithm

**Ranking Factors**:
1. **Recency**: Newer tweets ranked higher
2. **Engagement**: Likes, retweets, replies
3. **User relevance**: User interaction history
4. **Media**: Tweets with media ranked higher

**Ranking Function**:

```python
def calculate_tweet_score(tweet, user_interactions):
    """
    Calculate ranking score for tweet
    """
    # Recency score (exponential decay)
    age_hours = (time.now() - tweet.created_at).total_seconds() / 3600
    recency_score = math.exp(-age_hours / 24)  # Decay over 24 hours
    
    # Engagement score
    engagement_score = (
        tweet.likes_count * 1.0 +
        tweet.retweets_count * 2.0 +
        tweet.replies_count * 1.5 +
        tweet.quote_tweets_count * 2.5
    )
    # Normalize engagement (log scale)
    engagement_score = math.log1p(engagement_score) / 10
    
    # User relevance score
    author_id = tweet.user_id
    relevance_score = 1.0
    if author_id in user_interactions:
        # User has interacted with this author before
        interaction_count = user_interactions[author_id]
        relevance_score = 1.0 + math.log1p(interaction_count) / 5
    
    # Media bonus
    media_bonus = 1.1 if tweet.media_urls else 1.0
    
    # Final score
    score = (
        recency_score * 0.4 +
        engagement_score * 0.4 +
        relevance_score * 0.2
    ) * media_bonus
    
    return score
```

**Timeline Generation**:

```python
def generate_timeline(user_id, limit=200):
    """
    Generate ranked timeline for user
    """
    # Get user's interactions (for relevance)
    user_interactions = self.get_user_interactions(user_id)
    
    # Get timeline tweets (from cache or pull)
    tweets = self.get_timeline_tweets(user_id, limit=limit * 2)
    
    # Calculate scores
    scored_tweets = [
        (tweet, self.calculate_tweet_score(tweet, user_interactions))
        for tweet in tweets
    ]
    
    # Sort by score
    scored_tweets.sort(key=lambda x: x[1], reverse=True)
    
    # Return top N
    return [tweet for tweet, score in scored_tweets[:limit]]
```

### Tweet Creation Service

#### Problem

Create tweets efficiently, handle media uploads, extract hashtags/mentions, and trigger fan-out.

#### Solution: Async Tweet Processing

**Tweet Creation Flow**:

```python
class TweetService:
    def create_tweet(self, user_id, content, media_files=None):
        """
        Create tweet with media
        """
        # Validate content
        if len(content) > 280:
            raise ValidationError("Tweet too long")
        
        # Upload media (if any)
        media_urls = []
        if media_files:
            for media_file in media_files:
                url = self.upload_media(media_file)
                media_urls.append(url)
        
        # Extract hashtags and mentions
        hashtags = self.extract_hashtags(content)
        mentions = self.extract_mentions(content)
        
        # Create tweet record
        tweet = Tweet(
            user_id=user_id,
            content=content,
            media_urls=media_urls,
            hashtags=hashtags,
            mentions=mentions
        )
        tweet.save()
        
        # Update user tweet count
        self.increment_user_tweet_count(user_id)
        
        # Publish tweet event (async)
        self.kafka_producer.send(
            topic="tweets",
            value={
                "tweet_id": tweet.tweet_id,
                "user_id": user_id,
                "content": content,
                "hashtags": hashtags,
                "mentions": mentions,
                "created_at": tweet.created_at.isoformat()
            }
        )
        
        return tweet.tweet_id
    
    def extract_hashtags(self, content):
        """
        Extract hashtags from content
        """
        import re
        hashtags = re.findall(r'#(\w+)', content)
        return hashtags
    
    def extract_mentions(self, content):
        """
        Extract mentions (@username) from content
        """
        import re
        mentions = re.findall(r'@(\w+)', content)
        # Resolve usernames to user_ids
        user_ids = []
        for username in mentions:
            user = self.get_user_by_username(username)
            if user:
                user_ids.append(user.user_id)
        return user_ids
```

### Follow/Unfollow Service

#### Problem

Handle follow/unfollow operations efficiently, update follower/following counts, and update timelines.

#### Solution: Transactional Follow Operations

**Follow Flow**:

```python
class SocialGraphService:
    def follow_user(self, follower_id, followee_id):
        """
        Follow user
        """
        # Validate
        if follower_id == followee_id:
            raise ValidationError("Cannot follow yourself")
        
        # Check if already following
        if self.is_following(follower_id, followee_id):
            return
        
        # Create follow relationship
        follow = Follow(
            follower_id=follower_id,
            followee_id=followee_id
        )
        follow.save()
        
        # Update counts (async)
        self.increment_follower_count(followee_id)
        self.increment_following_count(follower_id)
        
        # Pre-warm timeline cache (async)
        self.pre_warm_timeline(follower_id, followee_id)
        
        # Publish follow event
        self.kafka_producer.send(
            topic="follows",
            value={
                "follower_id": follower_id,
                "followee_id": followee_id,
                "action": "follow"
            }
        )
    
    def pre_warm_timeline(self, follower_id, followee_id):
        """
        Pre-warm timeline with recent tweets from followee
        """
        # Get recent tweets from followee
        recent_tweets = self.get_user_tweets(followee_id, limit=50)
        
        # Add to follower's timeline cache
        timeline_entries = [
            {
                "user_id": follower_id,
                "tweet_id": tweet.tweet_id,
                "score": self.calculate_score(tweet),
                "created_at": tweet.created_at
            }
            for tweet in recent_tweets
        ]
        
        self.timeline_cache.batch_insert(timeline_entries)
```

### Like/Retweet/Reply Service

#### Problem

Handle likes, retweets, and replies efficiently, update counts, and trigger notifications.

#### Solution: Counter-Based Engagement

**Like Flow**:

```python
class EngagementService:
    def like_tweet(self, user_id, tweet_id):
        """
        Like tweet
        """
        # Check if already liked
        if self.is_liked(user_id, tweet_id):
            return
        
        # Create like record
        like = Like(
            user_id=user_id,
            tweet_id=tweet_id
        )
        like.save()
        
        # Increment likes count (async)
        self.increment_likes_count(tweet_id)
        
        # Cache like status
        self.redis.setex(
            f"like:{user_id}:{tweet_id}",
            86400,  # 24-hour TTL
            "1"
        )
        
        # Publish like event
        self.kafka_producer.send(
            topic="engagements",
            value={
                "type": "like",
                "user_id": user_id,
                "tweet_id": tweet_id,
                "tweet_author_id": self.get_tweet_author(tweet_id)
            }
        )
    
    def increment_likes_count(self, tweet_id):
        """
        Increment likes count (with cache)
        """
        # Update cache counter
        self.redis.incr(f"tweet:{tweet_id}:likes")
        
        # Async update database
        self.kafka_producer.send(
            topic="counter-updates",
            value={
                "tweet_id": tweet_id,
                "field": "likes_count",
                "delta": 1
            }
        )
```

**Counter Aggregation**:

```python
# Batch update counters from cache to database
@periodic_task(run_every=timedelta(minutes=5))
def sync_counters():
    """
    Sync counter cache to database
    """
    # Get all counter keys
    counter_keys = redis.keys("tweet:*:likes")
    
    for key in counter_keys:
        tweet_id = extract_tweet_id(key)
        cached_count = redis.get(key)
        
        # Update database
        Tweet.objects.filter(tweet_id=tweet_id).update(
            likes_count=F('likes_count') + cached_count
        )
        
        # Reset cache counter
        redis.delete(key)
```

### Search Service

#### Problem

Enable fast search across billions of tweets and millions of users.

#### Solution: Elasticsearch-Based Search

**Search Architecture**:

```python
class SearchService:
    def __init__(self):
        self.es_client = Elasticsearch(['localhost:9200'])
        self.index_name = "tweets"
    
    def index_tweet(self, tweet):
        """
        Index tweet in Elasticsearch
        """
        doc = {
            "tweet_id": tweet.tweet_id,
            "user_id": tweet.user_id,
            "content": tweet.content,
            "hashtags": tweet.hashtags,
            "mentions": tweet.mentions,
            "created_at": tweet.created_at.isoformat(),
            "likes_count": tweet.likes_count,
            "retweets_count": tweet.retweets_count
        }
        
        self.es_client.index(
            index=self.index_name,
            id=tweet.tweet_id,
            body=doc
        )
    
    def search_tweets(self, query, limit=50, max_id=None):
        """
        Search tweets
        """
        search_body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["content", "hashtags"],
                    "type": "best_fields"
                }
            },
            "sort": [
                {"created_at": {"order": "desc"}},
                {"_score": {"order": "desc"}}
            ],
            "size": limit
        }
        
        if max_id:
            search_body["search_after"] = [max_id]
        
        response = self.es_client.search(
            index=self.index_name,
            body=search_body
        )
        
        tweets = [
            self.parse_tweet_hit(hit)
            for hit in response['hits']['hits']
        ]
        
        return tweets
```

### Real-Time Updates

#### Problem

Push new tweets to users' feeds in real-time as they are posted.

#### Solution: WebSocket/Server-Sent Events

**Real-Time Update Flow**:

```python
class RealTimeService:
    def __init__(self):
        self.connections = {}  # user_id -> [websocket_connections]
    
    def connect(self, user_id, websocket):
        """
        Connect user for real-time updates
        """
        if user_id not in self.connections:
            self.connections[user_id] = []
        
        self.connections[user_id].append(websocket)
        
        # Subscribe to Kafka for user's timeline updates
        self.kafka_consumer.subscribe(
            topics=[f"timeline-updates-{user_id}"]
        )
    
    def handle_timeline_update(self, user_id, tweet_id):
        """
        Push tweet update to user's connections
        """
        if user_id not in self.connections:
            return
        
        # Get tweet details
        tweet = self.get_tweet(tweet_id)
        
        # Push to all user's connections
        message = {
            "type": "new_tweet",
            "tweet": tweet.to_dict()
        }
        
        for websocket in self.connections[user_id]:
            try:
                websocket.send(json.dumps(message))
            except:
                # Connection closed, remove it
                self.connections[user_id].remove(websocket)
```

**Kafka Consumer for Real-Time Updates**:

```python
@kafka_consumer(topic="timeline-updates")
def handle_timeline_update(event):
    """
    Handle timeline update event
    """
    user_ids = event['user_ids']
    tweet_id = event['tweet_id']
    
    # Push to each user's real-time connections
    for user_id in user_ids:
        realtime_service.handle_timeline_update(user_id, tweet_id)
```

### Media Handling

#### Problem

Handle image and video uploads, storage, and CDN distribution.

#### Solution: Object Storage + CDN

**Media Upload Flow**:

```python
class MediaService:
    def upload_media(self, media_file, media_type):
        """
        Upload media file
        """
        # Validate file
        if media_type == "image":
            if media_file.size > 5 * 1024 * 1024:  # 5MB
                raise ValidationError("Image too large")
        elif media_type == "video":
            if media_file.size > 500 * 1024 * 1024:  # 500MB
                raise ValidationError("Video too large")
        
        # Generate unique filename
        filename = self.generate_filename(media_file.name)
        
        # Upload to S3
        s3_key = f"media/{media_type}/{filename}"
        self.s3_client.upload_fileobj(
            media_file,
            bucket="twitter-media",
            key=s3_key
        )
        
        # Generate CDN URL
        cdn_url = f"https://cdn.twitter.com/{s3_key}"
        
        # Process media (async)
        if media_type == "image":
            self.process_image(s3_key)
        elif media_type == "video":
            self.process_video(s3_key)
        
        return cdn_url
    
    def process_image(self, s3_key):
        """
        Process image (resize, optimize)
        """
        # Download from S3
        image = self.s3_client.download_file(s3_key)
        
        # Generate thumbnails
        thumbnails = self.generate_thumbnails(image)
        
        # Upload thumbnails
        for size, thumbnail in thumbnails.items():
            thumbnail_key = f"{s3_key}_thumb_{size}"
            self.s3_client.upload_file(thumbnail, thumbnail_key)
```

## Scalability Considerations

### Horizontal Scaling

**Service Scaling**:
- Stateless services: Scale horizontally easily
- Use load balancers to distribute traffic
- Auto-scaling based on CPU/memory metrics

**Database Scaling**:
- Read replicas for read-heavy workloads
- Sharding for write-heavy workloads
- Caching layer (Redis) to reduce database load

**Timeline Cache Scaling**:
- Redis Cluster for timeline cache
- Partition by user_id
- Use consistent hashing

### Caching Strategy

**Cache Layers**:
1. **Application Cache**: Cache frequently accessed data (user profiles, tweets)
2. **Redis Cache**: Cache timelines, counters, like status
3. **CDN**: Cache static assets (images, videos)

**Cache Invalidation**:
- TTL-based expiration (5 minutes for timelines)
- Event-driven invalidation (on new tweet)
- Cache-aside pattern

### Database Optimization

**Indexing**:
- Index on frequently queried fields (user_id, tweet_id, created_at)
- Composite indexes for complex queries
- Full-text indexes for search

**Query Optimization**:
- Use read replicas for analytics queries
- Batch operations where possible
- Pagination for large result sets

### Message Queue

**Kafka Topics**:
- `tweets`: New tweet events
- `timeline-updates`: Timeline update events
- `engagements`: Like/retweet events
- `follows`: Follow/unfollow events
- `notifications`: Notification events

**Benefits**:
- Decouple services
- Handle traffic spikes
- Enable event-driven architecture
- Support replay for debugging

## Security Considerations

### Authentication and Authorization

- JWT tokens for API authentication
- OAuth 2.0 for third-party integrations
- Rate limiting per user/IP
- Content moderation (spam, abuse)

### Data Protection

- Encrypt sensitive data at rest
- Use HTTPS for all communications
- PII (Personally Identifiable Information) protection
- GDPR compliance

### Content Security

- Content moderation (automated + manual)
- Spam detection
- Abuse reporting
- Account suspension

## Monitoring & Observability

### Metrics

- **Business Metrics**: Tweets per day, active users, engagement rate
- **Technical Metrics**: API latency, error rates, throughput
- **Feed Metrics**: Feed generation time, cache hit rate
- **Engagement Metrics**: Likes/retweets per second

### Logging

- Structured logging (JSON format)
- Centralized logging (ELK stack)
- Log aggregation and analysis
- Error tracking (Sentry)

### Tracing

- Distributed tracing (Jaeger, Zipkin)
- Request tracing across services
- Performance analysis
- Debugging production issues

### Alerting

- Real-time alerts for critical issues
- SLA monitoring
- Anomaly detection
- PagerDuty integration

## Trade-offs and Optimizations

### Push vs Pull Model

- **Push Model**: Fast reads, slower writes, higher storage
- **Pull Model**: Faster writes, slower reads, lower storage
- **Hybrid**: Best of both worlds, more complex

### Consistency vs Availability

- **Strong Consistency**: Tweets, user data
- **Eventual Consistency**: Likes, retweets, counters
- **Trade-off**: Accept eventual consistency for engagement metrics

### Latency vs Freshness

- **Cached Timelines**: Lower latency, may be stale
- **Real-Time Updates**: Higher latency, always fresh
- **Trade-off**: Cache with short TTL + real-time updates

### Cost vs Performance

- **Caching**: More cache = better performance but higher cost
- **Database Replicas**: More replicas = better read performance but higher cost
- **Trade-off**: Optimize for cost while meeting performance requirements

## What Interviewers Look For

### Distributed Systems Skills

1. **Feed Generation Strategy**
   - Deep understanding of push/pull/hybrid
   - Timeline caching design
   - Celebrity user handling
   - **Red Flags**: Only one approach, no caching, poor celebrity handling

2. **Real-Time Systems**
   - WebSocket/SSE architecture
   - Pub/sub patterns
   - Low-latency delivery
   - **Red Flags**: Polling, high latency, no real-time

3. **Counter Aggregation**
   - Distributed counters
   - Eventual consistency
   - Batch synchronization
   - **Red Flags**: Strong consistency everywhere, no batching

### Problem-Solving Approach

1. **Scale Thinking**
   - Billions of tweets
   - Trillions of feed views
   - Millions of QPS
   - **Red Flags**: Small-scale design, no scale thinking

2. **Trade-off Analysis**
   - Push vs pull trade-offs
   - Consistency vs latency
   - Cache freshness vs performance
   - **Red Flags**: No trade-offs, wrong choices

3. **Edge Cases**
   - Celebrity users (millions of followers)
   - Viral tweets
   - High-traffic events
   - **Red Flags**: Ignoring edge cases, one-size-fits-all

### System Design Skills

1. **Component Design**
   - Microservices architecture
   - Clear service boundaries
   - API design
   - **Red Flags**: Monolithic, unclear boundaries

2. **Caching Strategy**
   - Multi-level caching
   - Timeline pre-computation
   - Cache invalidation
   - **Red Flags**: No caching, poor strategy, cache stampede

3. **Database Design**
   - Sharding strategy
   - Read replicas
   - Proper indexing
   - **Red Flags**: No sharding, missing indexes, no read scaling

### Communication Skills

1. **Architecture Explanation**
   - Clear feed generation explanation
   - Ranking algorithm understanding
   - **Red Flags**: Unclear explanations, no algorithm knowledge

2. **Capacity Estimation**
   - Realistic estimates
   - Proper calculations
   - Resource planning
   - **Red Flags**: Unrealistic estimates, no calculations

### Meta-Specific Focus

1. **Feed Generation Mastery**
   - Deep understanding of Meta's patterns
   - Hybrid approach expertise
   - **Key**: Show Meta-specific knowledge

2. **Scale-First Thinking**
   - Design for billions
   - Global distribution
   - **Key**: Demonstrate scale awareness

## Summary

### Key Takeaways

1. **Hybrid Feed Generation**: Push model for most users, pull model for celebrities
2. **Timeline Caching**: Pre-compute timelines in Redis for fast reads
3. **Real-Time Updates**: WebSocket/SSE for real-time feed updates
4. **Ranking Algorithm**: Combine recency, engagement, and relevance
5. **Counter Aggregation**: Use Redis counters, batch sync to database
6. **Search**: Elasticsearch for fast full-text search
7. **Media Handling**: S3 for storage, CDN for distribution
8. **Scalability**: Horizontal scaling, caching, read replicas, sharding

### Architecture Highlights

- **API Gateway**: Single entry point, load balancing, routing
- **Microservices**: Tweet, Timeline, Social Graph, Engagement, Search services
- **Message Queue**: Kafka for event-driven architecture
- **Data Stores**: PostgreSQL (primary), Redis (cache), Elasticsearch (search), S3 (media)
- **Real-Time**: WebSocket/SSE for real-time updates
- **CDN**: CloudFront/Cloudflare for media distribution

### Scale Numbers

- **Users**: 500M+ users
- **Tweets**: 500M tweets/day, 6K tweets/sec (peak)
- **Feed Views**: 2B feed views/day, 69K QPS (peak)
- **Storage**: 53PB/year (with replication: 159PB)
- **Bandwidth**: 150Gbps (peak)

### Common Interview Questions

1. **How do you generate feeds?**
   - Hybrid push-pull model, timeline caching, ranking algorithm

2. **How do you handle celebrity users with millions of followers?**
   - Pull model for users with > 1M followers, don't fan-out

3. **How do you ensure real-time updates?**
   - WebSocket/SSE connections, Kafka for event distribution

4. **How do you scale to billions of tweets?**
   - Sharding, caching, read replicas, message queues

5. **How do you handle search?**
   - Elasticsearch for full-text search, separate search index

This design provides a solid foundation for a social media feed like Twitter, covering all major components and addressing scalability, reliability, and performance challenges.

