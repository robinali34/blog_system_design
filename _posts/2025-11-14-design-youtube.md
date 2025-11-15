---
layout: post
title: "Design YouTube - System Design Interview"
date: 2025-11-14
categories: [System Design, Interview Example, Distributed Systems, Video Streaming, Social Media]
excerpt: "A comprehensive guide to designing YouTube, covering video upload, processing, adaptive bitrate streaming, storage, recommendations, comments, search, and architectural patterns for handling billions of videos, petabytes of storage, and millions of concurrent viewers."
---

## Introduction

YouTube is a video-sharing platform that allows users to upload, view, share, and comment on videos. The system handles billions of videos, petabytes of storage, millions of concurrent viewers, and requires efficient video processing, adaptive streaming, and intelligent recommendations.

This post provides a detailed walkthrough of designing YouTube, covering key architectural decisions, video processing pipelines, adaptive bitrate streaming, recommendation algorithms, and scalability challenges. This is one of the most common system design interview questions that tests your understanding of distributed systems, video processing, CDN distribution, and handling massive scale.

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

**Design YouTube with the following features:**

1. Video upload and processing
2. Video streaming (adaptive bitrate)
3. Video search and discovery
4. Video recommendations
5. Comments and likes/dislikes
6. Subscriptions and channels
7. Playlists
8. Video analytics (views, watch time)
9. Thumbnail generation
10. Live streaming (optional)

**Scale Requirements:**
- 2 billion+ users
- 500 million+ daily active users
- 1 billion+ videos
- 500 hours of video uploaded per minute
- 1 billion+ hours watched per day
- Peak: 10 million concurrent viewers
- Average video: 10 minutes, 100MB
- Total storage: 100+ petabytes

## Requirements

### Functional Requirements

**Core Features:**
1. **Video Upload**: Upload videos up to 15 minutes (or longer with verification)
2. **Video Processing**: Transcode videos to multiple formats/qualities
3. **Video Streaming**: Stream videos with adaptive bitrate
4. **Video Search**: Search videos by title, description, tags
5. **Recommendations**: Recommend videos based on watch history
6. **Comments**: Users can comment on videos
7. **Likes/Dislikes**: Users can like or dislike videos
8. **Subscriptions**: Users can subscribe to channels
9. **Playlists**: Users can create and manage playlists
10. **Analytics**: Track views, watch time, engagement

**Out of Scope:**
- Live streaming (focus on on-demand)
- Video editing tools
- Advanced analytics dashboard
- Mobile app (focus on web)

### Non-Functional Requirements

1. **Availability**: 99.9% uptime
2. **Reliability**: No video loss, guaranteed processing
3. **Performance**: 
   - Video upload: < 5 minutes for 100MB video
   - Video processing: < 10 minutes for 10-minute video
   - Video streaming: Start playback in < 2 seconds
   - Search response: < 500ms
4. **Scalability**: Handle 500 hours uploaded per minute
5. **Consistency**: Eventually consistent for views/likes
6. **Durability**: 99.999999999% (11 9's) durability for videos
7. **Bandwidth**: Efficient bandwidth usage with adaptive streaming

## Capacity Estimation

### Traffic Estimates

- **Total Users**: 2 billion
- **Daily Active Users (DAU)**: 500 million
- **Video Uploads per Day**: 500 hours/min × 60 min × 24 hours = 720,000 hours/day
- **Videos Watched per Day**: 1 billion hours/day
- **Average Video Length**: 10 minutes
- **Videos Watched**: 1B hours / 10 min = 6 billion videos/day
- **Peak Concurrent Viewers**: 10 million
- **Peak QPS**: 100,000 requests/second
- **Normal QPS**: 10,000 requests/second

### Storage Estimates

**Video Storage:**
- 720K hours uploaded/day × 365 days = 262.8M hours/year
- Average: 100MB per 10-minute video = 600MB per hour
- Annual storage: 262.8M hours × 600MB = 157.7PB/year
- With multiple qualities (5 qualities): 157.7PB × 5 = 788.5PB/year
- With replication (3x): 788.5PB × 3 = 2.37 exabytes/year
- 5-year retention: ~11.8 exabytes

**Thumbnail Storage:**
- 1B videos × 3 thumbnails × 200KB = 600TB

**Metadata Storage:**
- 1B videos × 2KB = 2TB
- User data: 2B users × 1KB = 2TB
- Comments: 100B comments × 500 bytes = 50TB
- Total metadata: ~54TB

**Total Storage**: ~11.8 exabytes (excluding CDN cache)

### Bandwidth Estimates

**Upload Bandwidth:**
- 500 hours/min × 600MB/hour = 300GB/min = 5GB/s = 40Gbps
- Peak: 10x average = 400Gbps

**Streaming Bandwidth:**
- 1B hours/day × 600MB/hour = 600PB/day = 6.94TB/s = 55.5Tbps average
- Peak: 10M concurrent × 5Mbps average = 50Tbps
- **Total Peak**: ~50Tbps

## Core Entities

### User
- `user_id` (UUID)
- `username`
- `email`
- `password_hash`
- `channel_name`
- `subscriber_count`
- `created_at`
- `updated_at`

### Video
- `video_id` (UUID)
- `user_id` (channel owner)
- `title`
- `description`
- `tags` (JSON array)
- `category`
- `duration` (seconds)
- `status` (processing, published, private, deleted)
- `views` (BIGINT)
- `likes` (BIGINT)
- `dislikes` (BIGINT)
- `thumbnail_url`
- `created_at`
- `published_at`
- `updated_at`

### Video Quality
- `quality_id` (UUID)
- `video_id`
- `quality` (144p, 240p, 360p, 480p, 720p, 1080p, 4K)
- `bitrate` (kbps)
- `file_url` (S3 URL)
- `file_size` (bytes)
- `created_at`

### Comment
- `comment_id` (UUID)
- `video_id`
- `user_id`
- `parent_comment_id` (for replies)
- `text` (TEXT)
- `likes` (BIGINT)
- `created_at`
- `updated_at`

### Subscription
- `subscription_id` (UUID)
- `user_id` (subscriber)
- `channel_id` (user_id of channel owner)
- `created_at`

### Playlist
- `playlist_id` (UUID)
- `user_id`
- `name`
- `description`
- `is_public` (BOOLEAN)
- `video_count` (INT)
- `created_at`
- `updated_at`

### Playlist Video
- `playlist_video_id` (UUID)
- `playlist_id`
- `video_id`
- `position` (INT)
- `added_at`

### Watch History
- `watch_id` (UUID)
- `user_id`
- `video_id`
- `watch_time` (seconds)
- `completed` (BOOLEAN)
- `watched_at` (TIMESTAMP)

## API

### 1. Upload Video
```
POST /api/v1/videos/upload
Request: multipart/form-data
  - video: file data
  - title: "My Video"
  - description: "Video description"
  - tags: ["tag1", "tag2"]
  - category: "entertainment"
  - privacy: "public"

Response:
{
  "video_id": "uuid",
  "status": "processing",
  "upload_url": "https://s3.../upload",
  "estimated_processing_time": 600
}
```

### 2. Get Video
```
GET /api/v1/videos/{video_id}
Response:
{
  "video_id": "uuid",
  "title": "My Video",
  "description": "...",
  "channel": {
    "channel_id": "uuid",
    "name": "My Channel",
    "subscriber_count": 1000
  },
  "views": 50000,
  "likes": 1000,
  "dislikes": 50,
  "duration": 600,
  "published_at": "2025-11-13T10:00:00Z",
  "qualities": ["144p", "240p", "360p", "480p", "720p", "1080p"]
}
```

### 3. Stream Video
```
GET /api/v1/videos/{video_id}/stream?quality=720p&start=0
Response: Video stream (HLS or DASH manifest + segments)
```

### 4. Search Videos
```
GET /api/v1/videos/search?q=python+tutorial&limit=20&offset=0
Response:
{
  "videos": [
    {
      "video_id": "uuid",
      "title": "Python Tutorial",
      "thumbnail_url": "https://...",
      "channel": {...},
      "views": 100000,
      "duration": 600,
      "published_at": "2025-11-10T10:00:00Z"
    }
  ],
  "total": 1000,
  "limit": 20,
  "offset": 0
}
```

### 5. Get Recommendations
```
GET /api/v1/videos/recommendations?limit=20
Response:
{
  "videos": [...],
  "recommendation_type": "based_on_watch_history"
}
```

### 6. Like Video
```
POST /api/v1/videos/{video_id}/like
Response:
{
  "video_id": "uuid",
  "likes": 1001,
  "user_liked": true
}
```

### 7. Comment on Video
```
POST /api/v1/videos/{video_id}/comments
Request:
{
  "text": "Great video!",
  "parent_comment_id": null
}

Response:
{
  "comment_id": "uuid",
  "text": "Great video!",
  "user": {...},
  "likes": 0,
  "created_at": "2025-11-13T10:00:00Z"
}
```

### 8. Subscribe to Channel
```
POST /api/v1/channels/{channel_id}/subscribe
Response:
{
  "subscription_id": "uuid",
  "channel_id": "uuid",
  "subscriber_count": 1001
}
```

## Data Flow

### Video Upload Flow

1. **User Uploads Video**:
   - User uploads video file
   - **Client** sends upload request to **API Gateway**
   - **API Gateway** routes to **Upload Service**

2. **Upload Processing**:
   - **Upload Service**:
     - Validates video file
     - Generates video_id
     - Creates video metadata record (status: "processing")
     - Uploads video to **Object Storage** (S3)
     - Publishes upload event to **Message Queue**

3. **Video Processing**:
   - **Video Processing Service** consumes upload event
   - Downloads video from S3
   - **Transcoding Pipeline**:
     - Extracts metadata (duration, resolution)
     - Generates thumbnails
     - Transcodes to multiple qualities (144p, 240p, 360p, 480p, 720p, 1080p)
     - Creates HLS/DASH manifests
   - Uploads processed videos to **Object Storage**
   - Updates video status to "published"

4. **CDN Distribution**:
   - Videos replicated to **CDN** edge locations
   - Ready for streaming

### Video Streaming Flow

1. **User Requests Video**:
   - User clicks on video
   - **Client** requests video stream
   - **Streaming Service** retrieves video metadata

2. **Adaptive Streaming**:
   - **Streaming Service**:
     - Determines available qualities
     - Returns HLS/DASH manifest
     - **Client** selects initial quality based on bandwidth

3. **Video Delivery**:
   - **Client** requests video segments from **CDN**
   - **CDN** serves segments from nearest edge
   - **Client** monitors bandwidth and adjusts quality
   - **Client** tracks watch time

4. **Analytics**:
   - **Client** sends watch events
   - **Analytics Service** updates view count and watch time

### Recommendation Flow

1. **User Watches Video**:
   - User watches video
   - **Client** sends watch event
   - **Recommendation Service** records watch history

2. **Recommendation Generation**:
   - **Recommendation Service**:
     - Analyzes user's watch history
     - Finds similar users (collaborative filtering)
     - Finds similar videos (content-based)
     - Ranks videos by relevance
     - Returns top recommendations

3. **Response**:
   - Recommendations returned to client
   - Client displays recommended videos

## Database Design

### Schema Design

**Users Table:**
```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    channel_name VARCHAR(100),
    subscriber_count BIGINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_username (username),
    INDEX idx_email (email)
);
```

**Videos Table:**
```sql
CREATE TABLE videos (
    video_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    tags JSON,
    category VARCHAR(100),
    duration INT NOT NULL,
    status ENUM('processing', 'published', 'private', 'deleted') DEFAULT 'processing',
    views BIGINT DEFAULT 0,
    likes BIGINT DEFAULT 0,
    dislikes BIGINT DEFAULT 0,
    thumbnail_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    published_at TIMESTAMP NULL,
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_published_at (published_at DESC),
    INDEX idx_views (views DESC),
    FULLTEXT INDEX idx_title_description (title, description)
);
```

**Video Qualities Table:**
```sql
CREATE TABLE video_qualities (
    quality_id UUID PRIMARY KEY,
    video_id UUID NOT NULL,
    quality VARCHAR(20) NOT NULL,
    bitrate INT NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_video_id (video_id),
    INDEX idx_quality (quality),
    UNIQUE KEY uk_video_quality (video_id, quality)
);
```

**Comments Table:**
```sql
CREATE TABLE comments (
    comment_id UUID PRIMARY KEY,
    video_id UUID NOT NULL,
    user_id UUID NOT NULL,
    parent_comment_id UUID NULL,
    text TEXT NOT NULL,
    likes BIGINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_video_id (video_id),
    INDEX idx_user_id (user_id),
    INDEX idx_parent_comment (parent_comment_id),
    INDEX idx_created_at (created_at DESC)
);
```

**Subscriptions Table:**
```sql
CREATE TABLE subscriptions (
    subscription_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    channel_id UUID NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_id (user_id),
    INDEX idx_channel_id (channel_id),
    UNIQUE KEY uk_user_channel (user_id, channel_id)
);
```

**Playlists Table:**
```sql
CREATE TABLE playlists (
    playlist_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT TRUE,
    video_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_id (user_id),
    INDEX idx_is_public (is_public)
);
```

**Playlist Videos Table:**
```sql
CREATE TABLE playlist_videos (
    playlist_video_id UUID PRIMARY KEY,
    playlist_id UUID NOT NULL,
    video_id UUID NOT NULL,
    position INT NOT NULL,
    added_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_playlist_id (playlist_id),
    INDEX idx_video_id (video_id),
    UNIQUE KEY uk_playlist_video_position (playlist_id, video_id, position)
);
```

**Watch History Table:**
```sql
CREATE TABLE watch_history (
    watch_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    video_id UUID NOT NULL,
    watch_time INT NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    watched_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_id (user_id),
    INDEX idx_video_id (video_id),
    INDEX idx_watched_at (watched_at DESC),
    INDEX idx_user_watched (user_id, watched_at DESC)
);
```

### Database Sharding Strategy

**Videos Table Sharding:**
- Shard by video_id using consistent hashing
- 1000 shards: `shard_id = hash(video_id) % 1000`
- Enables parallel queries and horizontal scaling

**Comments Table Sharding:**
- Shard by video_id (same as videos)
- All comments for a video in same shard
- Enables efficient comment queries

**Watch History Sharding:**
- Shard by user_id
- All watch history for a user in same shard
- Enables efficient recommendation queries

**Shard Key Selection:**
- `video_id` for videos and comments (video-centric)
- `user_id` for watch history (user-centric)
- Enables efficient queries for each use case

**Replication:**
- Each shard replicated 3x for high availability
- Master-replica setup for read scaling
- Writes go to master, reads can go to replicas

## High-Level Design

```
┌─────────────┐
│   Client    │
│  (Web App)  │
└──────┬──────┘
       │
       │ HTTP/HTTPS
       │
┌──────▼──────────────────────────────────────────────┐
│        API Gateway / Load Balancer                   │
│        - Rate Limiting                               │
│        - Request Routing                             │
└──────┬──────────────────────────────────────────────┘
       │
       ├──────────────┬──────────────┬──────────────┬──────────────┐
       │              │              │              │              │
┌──────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
│   Upload    │ │ Streaming  │ │  Search   │ │Recommendation│ │  Social   │
│   Service   │ │  Service   │ │  Service  │ │  Service    │ │  Service  │
└──────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
       │              │              │              │              │
       │              │              │              │              │
┌──────▼──────────────▼──────────────▼──────────────▼──────────────▼──────┐
│              Message Queue (Kafka)                                        │
│              - Video upload events                                       │
│              - Processing events                                         │
│              - Watch events                                              │
└──────┬───────────────────────────────────────────────────────────────────┘
       │
       │
┌──────▼───────────────────────────────────────────────────────────────────┐
│         Video Processing Service (Workers)                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │ Transcoding  │  │ Thumbnail    │  │ Manifest     │                  │
│  │ Workers      │  │ Generation   │  │ Generation   │                  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                  │
└─────────┼──────────────────┼──────────────────┼───────────────────────────┘
          │                  │                  │
          │                  │                  │
┌─────────▼──────────────────▼──────────────────▼───────────────────────────┐
│         Database Cluster (Sharded)                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                              │
│  │ Videos   │  │ Comments │  │ Watch    │                              │
│  │ DB       │  │ DB       │  │ History  │                              │
│  └──────────┘  └──────────┘  └──────────┘                              │
│                                                                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                              │
│  │ Users    │  │ Playlists│  │Subscriptions│                            │
│  │ DB       │  │ DB       │  │ DB       │                              │
│  └──────────┘  └──────────┘  └──────────┘                              │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│              Object Storage (S3)                                          │
│  - Raw video files                                                        │
│  - Processed video files (multiple qualities)                             │
│  - Thumbnails                                                              │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│              CDN (Global Distribution)                                     │
│  - Video segments (HLS/DASH)                                              │
│  - Thumbnails                                                              │
│  - Popular videos cached at edge                                          │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│              Cache Layer (Redis)                                           │
│  - Video metadata                                                          │
│  - Recommendations                                                         │
│  - Popular videos                                                          │
│  - Search results                                                          │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│         Search Engine (Elasticsearch)                                      │
│         - Video search by title, description, tags                         │
│         - Full-text search                                                 │
└───────────────────────────────────────────────────────────────────────────┘
```

## Deep Dive

### Component Design

#### 1. Upload Service

**Responsibilities:**
- Handle video uploads
- Validate video files
- Initiate processing pipeline
- Manage upload progress

**Key Design Decisions:**
- **Resumable Uploads**: Support resumable uploads for large files
- **Direct S3 Upload**: Use presigned URLs for direct S3 upload
- **Validation**: Validate file type, size before processing
- **Async Processing**: Process videos asynchronously

**Scalability:**
- Stateless service, horizontally scalable
- Direct S3 upload reduces server load
- Connection pooling for database

#### 2. Video Processing Service

**Responsibilities:**
- Transcode videos to multiple qualities
- Generate thumbnails
- Create streaming manifests
- Extract metadata

**Key Design Decisions:**
- **Transcoding Pipeline**: Multiple workers for parallel processing
- **Quality Levels**: 144p, 240p, 360p, 480p, 720p, 1080p, 4K
- **Format**: HLS (HTTP Live Streaming) or DASH
- **Thumbnails**: Generate 3 thumbnails per video

**Processing Pipeline:**
```python
def process_video(video_id, raw_video_url):
    # Download raw video
    raw_video = download_from_s3(raw_video_url)
    
    # Extract metadata
    metadata = extract_metadata(raw_video)
    duration = metadata['duration']
    resolution = metadata['resolution']
    
    # Generate thumbnails
    thumbnails = generate_thumbnails(raw_video, count=3)
    upload_thumbnails(video_id, thumbnails)
    
    # Transcode to multiple qualities
    qualities = ['144p', '240p', '360p', '480p', '720p', '1080p']
    if resolution >= 2160:
        qualities.append('4K')
    
    transcoded_videos = []
    for quality in qualities:
        transcoded = transcode_video(raw_video, quality)
        transcoded_url = upload_to_s3(transcoded, video_id, quality)
        transcoded_videos.append({
            'quality': quality,
            'url': transcoded_url,
            'bitrate': get_bitrate(quality),
            'file_size': get_file_size(transcoded)
        })
    
    # Create HLS manifest
    manifest = create_hls_manifest(video_id, transcoded_videos)
    upload_manifest(video_id, manifest)
    
    # Update video status
    update_video_status(video_id, 'published', {
        'duration': duration,
        'qualities': [q['quality'] for q in transcoded_videos]
    })
    
    # Replicate to CDN
    replicate_to_cdn(video_id, transcoded_videos)
```

#### 3. Streaming Service

**Responsibilities:**
- Serve video streams
- Handle adaptive bitrate streaming
- Manage CDN distribution
- Track watch analytics

**Key Design Decisions:**
- **Adaptive Streaming**: HLS or DASH for adaptive bitrate
- **CDN**: Use CDN for video delivery
- **Manifest**: Return manifest, client requests segments
- **Quality Selection**: Client selects quality based on bandwidth

**Implementation:**
```python
def get_video_stream(video_id, quality=None):
    # Get video metadata
    video = get_video(video_id)
    
    # Get available qualities
    qualities = get_video_qualities(video_id)
    
    # Generate HLS manifest
    manifest = generate_hls_manifest(video_id, qualities, quality)
    
    return {
        'manifest_url': f"https://cdn.example.com/videos/{video_id}/manifest.m3u8",
        'qualities': [q['quality'] for q in qualities],
        'default_quality': quality or '720p'
    }
```

#### 4. Recommendation Service

**Responsibilities:**
- Generate video recommendations
- Analyze watch history
- Rank videos by relevance
- Personalize recommendations

**Key Design Decisions:**
- **Collaborative Filtering**: Find similar users
- **Content-Based**: Find similar videos
- **Hybrid Approach**: Combine multiple signals
- **Real-Time**: Update recommendations based on recent watches

**Implementation:**
```python
def get_recommendations(user_id, limit=20):
    # Get user's watch history
    watch_history = get_watch_history(user_id, limit=100)
    watched_video_ids = [w.video_id for w in watch_history]
    
    # Collaborative filtering: find similar users
    similar_users = find_similar_users(user_id, watch_history)
    
    # Get videos liked by similar users
    recommended_videos = []
    for similar_user in similar_users:
        user_videos = get_watched_videos(similar_user.user_id)
        for video in user_videos:
            if video.video_id not in watched_video_ids:
                recommended_videos.append(video)
    
    # Content-based: find similar videos
    for watched_video in watch_history[:10]:
        similar_videos = find_similar_videos(watched_video.video_id)
        recommended_videos.extend(similar_videos)
    
    # Rank by relevance
    ranked = rank_videos(recommended_videos, user_id)
    
    return ranked[:limit]

def rank_videos(videos, user_id):
    scored_videos = []
    
    for video in videos:
        score = calculate_relevance_score(video, user_id)
        scored_videos.append((video, score))
    
    # Sort by score
    scored_videos.sort(key=lambda x: x[1], reverse=True)
    
    return [v[0] for v in scored_videos]

def calculate_relevance_score(video, user_id):
    # Views score
    views_score = math.log(video.views + 1) / 20.0
    
    # Recency score
    days_since_published = (now() - video.published_at).days
    recency_score = 1.0 / (1.0 + days_since_published / 30.0)
    
    # Engagement score (likes/views ratio)
    engagement_score = video.likes / max(video.views, 1)
    
    # Channel score (subscriber count)
    channel_score = math.log(video.channel.subscriber_count + 1) / 15.0
    
    # Combine scores
    total_score = (
        views_score * 0.3 +
        recency_score * 0.2 +
        engagement_score * 0.3 +
        channel_score * 0.2
    )
    
    return total_score
```

#### 5. Search Service

**Responsibilities:**
- Search videos by title, description, tags
- Rank search results
- Handle filters (duration, upload date, etc.)
- Cache popular searches

**Key Design Decisions:**
- **Elasticsearch**: Use Elasticsearch for full-text search
- **Ranking**: Rank by relevance, views, recency
- **Caching**: Cache popular search results
- **Filters**: Support multiple filters

**Implementation:**
```python
def search_videos(query, filters=None, limit=20, offset=0):
    # Build Elasticsearch query
    es_query = {
        "bool": {
            "must": [
                {
                    "multi_match": {
                        "query": query,
                        "fields": ["title^3", "description", "tags^2"]
                    }
                }
            ],
            "filter": []
        }
    }
    
    # Add filters
    if filters:
        if filters.get("duration"):
            es_query["bool"]["filter"].append({
                "range": {"duration": filters["duration"]}
            })
        if filters.get("upload_date"):
            es_query["bool"]["filter"].append({
                "range": {"published_at": {"gte": filters["upload_date"]}}
            })
    
    # Execute search
    results = elasticsearch.search(
        index="videos",
        body={"query": es_query, "size": limit, "from": offset}
    )
    
    # Enrich with metadata
    videos = []
    for hit in results["hits"]["hits"]:
        video = hit["_source"]
        videos.append({
            "video_id": video["video_id"],
            "title": video["title"],
            "thumbnail_url": video["thumbnail_url"],
            "channel": get_channel(video["user_id"]),
            "views": video["views"],
            "duration": video["duration"],
            "published_at": video["published_at"]
        })
    
    return {
        "videos": videos,
        "total": results["hits"]["total"]["value"],
        "limit": limit,
        "offset": offset
    }
```

### Detailed Design

#### Adaptive Bitrate Streaming

**Challenge:** Stream videos efficiently based on user's bandwidth

**Solution:**
- **HLS (HTTP Live Streaming)**: Apple's adaptive streaming protocol
- **DASH (Dynamic Adaptive Streaming over HTTP)**: MPEG-DASH standard
- **Multiple Qualities**: Encode video in multiple bitrates
- **Client Selection**: Client selects quality based on bandwidth

**HLS Structure:**
```
manifest.m3u8
├── #EXT-X-STREAM-INF:BANDWIDTH=500000,RESOLUTION=640x360
│   └── 360p.m3u8
├── #EXT-X-STREAM-INF:BANDWIDTH=1000000,RESOLUTION=854x480
│   └── 480p.m3u8
└── #EXT-X-STREAM-INF:BANDWIDTH=2500000,RESOLUTION=1280x720
    └── 720p.m3u8
```

**Implementation:**
```python
def create_hls_manifest(video_id, qualities):
    manifest = "#EXTM3U\n"
    manifest += "#EXT-X-VERSION:3\n"
    
    for quality in sorted(qualities, key=lambda x: x['bitrate']):
        manifest += f"#EXT-X-STREAM-INF:BANDWIDTH={quality['bitrate']*1000},RESOLUTION={get_resolution(quality['quality'])}\n"
        manifest += f"{quality['quality']}.m3u8\n"
    
    return manifest
```

#### Thumbnail Generation

**Challenge:** Generate representative thumbnails efficiently

**Solution:**
- **Multiple Thumbnails**: Generate 3 thumbnails per video
- **Time-Based**: Extract frames at 25%, 50%, 75% of video
- **Quality Selection**: Use ML to select best thumbnail
- **Caching**: Cache thumbnails in CDN

**Implementation:**
```python
def generate_thumbnails(video_file, count=3):
    # Get video duration
    duration = get_video_duration(video_file)
    
    # Calculate thumbnail positions
    positions = [duration * (i + 1) / (count + 1) for i in range(count)]
    
    thumbnails = []
    for position in positions:
        # Extract frame at position
        thumbnail = extract_frame(video_file, position)
        
        # Optimize thumbnail
        thumbnail = optimize_thumbnail(thumbnail, size=(320, 180))
        
        thumbnails.append(thumbnail)
    
    return thumbnails
```

#### View Count Aggregation

**Challenge:** Track view counts accurately at scale

**Solution:**
- **Event-Based**: Track views as events
- **Batch Aggregation**: Aggregate views in batches
- **Approximate Counts**: Use approximate counting for very popular videos
- **Deduplication**: Deduplicate views (same user, same video)

**Implementation:**
```python
def track_view(video_id, user_id):
    # Create view event
    view_event = {
        'video_id': video_id,
        'user_id': user_id,
        'timestamp': now()
    }
    
    # Publish to message queue
    publish_view_event(view_event)
    
    # Update approximate count (Redis)
    redis.incr(f"video:{video_id}:views")

def aggregate_views():
    # Process view events in batch
    events = consume_view_events(batch_size=1000)
    
    # Group by video_id
    video_views = {}
    for event in events:
        video_id = event['video_id']
        video_views[video_id] = video_views.get(video_id, 0) + 1
    
    # Update database
    for video_id, count in video_views.items():
        db.execute(
            "UPDATE videos SET views = views + ? WHERE video_id = ?",
            count, video_id
        )
```

### Scalability Considerations

#### Horizontal Scaling

**Upload Service:**
- Stateless service, horizontally scalable
- Direct S3 upload reduces server load
- Load balancer distributes requests

**Processing Service:**
- Worker pool for transcoding
- Scale workers based on queue depth
- Parallel processing of multiple videos

**Streaming Service:**
- Stateless service, horizontally scalable
- CDN handles most traffic
- Cache popular videos at edge

#### Storage Scaling

**Object Storage:**
- S3 for video files
- Automatic scaling
- Lifecycle policies for old videos
- Compression for storage efficiency

**CDN:**
- Global CDN for video delivery
- Cache popular videos at edge
- Reduce load on origin servers
- Improve streaming performance

#### Caching Strategy

**Redis Cache:**
- **Video Metadata**: TTL 1 hour
- **Recommendations**: TTL 30 minutes
- **Search Results**: TTL 5 minutes
- **Popular Videos**: TTL 1 hour

**CDN Cache:**
- **Video Segments**: Cache at edge
- **Thumbnails**: Cache at edge
- **Manifests**: Cache with short TTL

### Security Considerations

#### Authentication & Authorization

- **JWT Tokens**: Use JWT for API authentication
- **Video Access Control**: Verify user has access to video
- **Rate Limiting**: Limit uploads and requests per user
- **Content Moderation**: Moderate uploaded content

#### Content Security

- **Virus Scanning**: Scan uploaded videos
- **Content Filtering**: Filter inappropriate content
- **DMCA Compliance**: Handle copyright claims
- **Access Control**: Private/public video settings

### Monitoring & Observability

#### Key Metrics

**System Metrics:**
- Upload rate (videos/minute)
- Processing time (p50, p95, p99)
- Streaming QPS
- CDN cache hit rate
- Storage usage

**Business Metrics:**
- Videos uploaded per day
- Hours watched per day
- Average watch time
- Engagement rate (likes/views)
- Subscriber growth

#### Logging

- **Structured Logging**: JSON logs for parsing
- **Video Operations**: Log uploads, processing, streaming
- **Error Logging**: Log errors with context
- **Performance Logging**: Log slow operations

#### Alerting

- **High Processing Time**: Alert if p95 > 10 minutes
- **High Error Rate**: Alert if error rate > 1%
- **Storage Capacity**: Alert if storage > 80%
- **CDN Issues**: Alert on CDN errors

### Trade-offs and Optimizations

#### Trade-offs

**1. Video Quality: Many vs Few Qualities**
- **Many**: Better user experience, more storage
- **Few**: Less storage, worse experience
- **Decision**: 5-7 qualities (144p to 1080p/4K)

**2. Processing: Fast vs High Quality**
- **Fast**: Lower quality, faster processing
- **High Quality**: Better quality, slower processing
- **Decision**: Balance based on video popularity

**3. Storage: Replication vs Erasure Coding**
- **Replication**: Simpler, more storage
- **Erasure Coding**: Less storage, more complex
- **Decision**: Replication for hot videos, erasure coding for cold

**4. CDN: Aggressive vs Conservative Caching**
- **Aggressive**: Better performance, more storage
- **Conservative**: Less storage, worse performance
- **Decision**: Aggressive caching for popular videos

#### Optimizations

**1. Chunked Upload**
- Upload large videos in chunks
- Resume interrupted uploads
- Reduce memory usage

**2. Parallel Transcoding**
- Transcode multiple qualities in parallel
- Reduce processing time
- Utilize multiple CPU cores

**3. CDN Optimization**
- Cache popular videos at edge
- Reduce latency
- Reduce origin server load

**4. Compression**
- Compress video files
- Reduce storage by 30-50%
- Trade-off: Processing time

## Summary

Designing YouTube at scale requires careful consideration of:

1. **Video Processing**: Efficient transcoding pipeline for multiple qualities
2. **Adaptive Streaming**: HLS/DASH for bandwidth-efficient streaming
3. **Storage**: Petabyte-scale storage with deduplication
4. **CDN Distribution**: Global CDN for video delivery
5. **Recommendations**: Intelligent recommendation algorithm
6. **Search**: Fast full-text search with Elasticsearch
7. **Scalability**: Horizontal scaling for all services
8. **Performance**: Sub-second streaming start time

Key architectural decisions:
- **Multi-Quality Transcoding** for adaptive streaming
- **HLS/DASH** for adaptive bitrate streaming
- **CDN** for global video delivery
- **Elasticsearch** for video search
- **Hybrid Recommendations** combining collaborative and content-based filtering
- **Event-Based Analytics** for view tracking
- **Sharded Database** for scalability

The system handles 500 hours of video uploaded per minute, 1 billion hours watched per day, and provides seamless video streaming experience to millions of concurrent users.

