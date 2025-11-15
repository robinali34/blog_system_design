---
layout: post
title: "Design Netflix - System Design Interview"
date: 2025-11-14
categories: [System Design, Interview Example, Distributed Systems, Video Streaming, Content Delivery]
excerpt: "A comprehensive guide to designing Netflix, covering video streaming, CDN distribution, adaptive bitrate streaming, content recommendation, user profiles, content management, and architectural patterns for handling petabytes of video content and millions of concurrent streams."
---

## Introduction

Netflix is a video streaming platform that provides on-demand access to movies and TV shows. The system handles petabytes of video content, millions of concurrent streams, and requires efficient content delivery, adaptive streaming, and personalized recommendations across multiple devices and regions.

This post provides a detailed walkthrough of designing Netflix, covering key architectural decisions, CDN distribution strategies, adaptive bitrate streaming, recommendation algorithms, and scalability challenges. This is one of the most common system design interview questions that tests your understanding of distributed systems, video streaming, content delivery networks, and handling massive scale.

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

**Design Netflix with the following features:**

1. Video streaming (on-demand movies and TV shows)
2. Adaptive bitrate streaming
3. Content search and discovery
4. Personalized recommendations
5. User profiles and watch history
6. Multiple device support (TV, mobile, web)
7. Content management (movies, TV shows, seasons, episodes)
8. Continue watching functionality
9. Content previews and trailers
10. Geographic content availability

**Scale Requirements:**
- 250 million+ subscribers worldwide
- 100 million+ daily active users
- 50,000+ titles (movies + TV shows)
- 100,000+ hours of content
- Peak: 50 million concurrent streams
- Average stream: 2 hours, 2GB per hour
- Total storage: 10+ petabytes
- Global distribution across 190+ countries

## Requirements

### Functional Requirements

**Core Features:**
1. **Video Streaming**: Stream movies and TV shows on-demand
2. **Adaptive Streaming**: Adjust quality based on bandwidth
3. **Content Discovery**: Browse and search content
4. **Recommendations**: Personalized content recommendations
5. **User Profiles**: Multiple profiles per account
6. **Watch History**: Track what users watch
7. **Continue Watching**: Resume from where user left off
8. **Content Metadata**: Titles, descriptions, ratings, genres
9. **Geographic Availability**: Content varies by region
10. **Multiple Devices**: Support TV, mobile, web, tablet

**Out of Scope:**
- Live streaming
- User-generated content
- Social features (sharing, comments)
- Advanced analytics dashboard
- Content production/upload

### Non-Functional Requirements

1. **Availability**: 99.9% uptime
2. **Reliability**: No video interruption, guaranteed playback
3. **Performance**: 
   - Video start time: < 2 seconds
   - Quality adaptation: < 5 seconds
   - Search response: < 500ms
   - Recommendation generation: < 1 second
4. **Scalability**: Handle 50M+ concurrent streams
5. **Consistency**: Eventually consistent for watch history
6. **Durability**: 99.999999999% (11 9's) durability for content
7. **Bandwidth Efficiency**: Minimize bandwidth with adaptive streaming

## Capacity Estimation

### Traffic Estimates

- **Total Subscribers**: 250 million
- **Daily Active Users (DAU)**: 100 million
- **Average Watch Time**: 2 hours per user per day
- **Total Watch Time**: 200 million hours per day
- **Peak Concurrent Streams**: 50 million
- **Average Stream Bitrate**: 5 Mbps
- **Peak Bandwidth**: 50M streams × 5 Mbps = 250 Tbps
- **Average Bandwidth**: 200M hours/day × 5 Mbps / 24 hours = 41.7 Tbps

### Storage Estimates

**Video Content Storage:**
- 50,000 titles × 2 hours average = 100,000 hours
- Average: 2GB per hour = 200TB per title
- Total: 50K titles × 200GB = 10PB
- Multiple qualities (5 qualities): 10PB × 5 = 50PB
- With replication (3x): 50PB × 3 = 150PB

**Content Metadata:**
- 50K titles × 10KB = 500MB
- Episodes: 500K episodes × 5KB = 2.5GB
- Total metadata: ~3GB

**User Data:**
- 250M users × 2KB = 500GB
- Watch history: 250M users × 100 titles × 100 bytes = 2.5TB
- Total user data: ~3TB

**Total Storage**: ~150PB

### Bandwidth Estimates

**Peak Streaming Bandwidth:**
- 50M concurrent streams × 5 Mbps = 250 Tbps

**Average Streaming Bandwidth:**
- 200M hours/day × 2GB/hour = 400PB/day
- Average: 400PB / (24 × 3600) = 4.63TB/s = 37 Tbps

**CDN Distribution:**
- Most traffic served by CDN (90%+)
- Origin server bandwidth: 10% = 3.7 Tbps

## Core Entities

### User
- `user_id` (UUID)
- `email`
- `password_hash`
- `subscription_plan` (basic, standard, premium)
- `billing_country`
- `created_at`
- `updated_at`

### Profile
- `profile_id` (UUID)
- `user_id`
- `profile_name`
- `avatar_url`
- `maturity_rating` (G, PG, PG-13, R, etc.)
- `language_preference`
- `created_at`

### Content
- `content_id` (UUID)
- `title`
- `type` (movie, tv_show)
- `description`
- `release_year` (INT)
- `duration` (minutes, for movies)
- `genres` (JSON array)
- `rating` (G, PG, PG-13, R, etc.)
- `imdb_rating` (DECIMAL)
- `poster_url`
- `trailer_url`
- `created_at`
- `updated_at`

### TV Show
- `show_id` (UUID)
- `content_id` (references Content)
- `number_of_seasons` (INT)
- `number_of_episodes` (INT)

### Season
- `season_id` (UUID)
- `show_id`
- `season_number` (INT)
- `number_of_episodes` (INT)
- `release_date` (DATE)

### Episode
- `episode_id` (UUID)
- `season_id`
- `episode_number` (INT)
- `title`
- `description`
- `duration` (minutes)
- `release_date` (DATE)

### Content Quality
- `quality_id` (UUID)
- `content_id` (or episode_id for TV)
- `quality` (SD, HD, Full HD, 4K)
- `bitrate` (kbps)
- `file_url` (CDN URL)
- `file_size` (bytes)

### Watch History
- `watch_id` (UUID)
- `profile_id`
- `content_id` (or episode_id)
- `watch_time` (seconds)
- `total_duration` (seconds)
- `completed` (BOOLEAN)
- `last_watched_at` (TIMESTAMP)
- `created_at`

### Recommendation
- `recommendation_id` (UUID)
- `profile_id`
- `content_id`
- `score` (DECIMAL)
- `recommendation_type` (collaborative, content-based, trending)
- `created_at`

### Geographic Availability
- `availability_id` (UUID)
- `content_id`
- `country_code` (VARCHAR)
- `available` (BOOLEAN)
- `available_from` (DATE)
- `available_until` (DATE)

## API

### 1. Get Home Page (Recommendations)
```
GET /api/v1/home?profile_id=uuid
Response:
{
  "sections": [
    {
      "title": "Continue Watching",
      "content": [
        {
          "content_id": "uuid",
          "title": "Stranger Things",
          "poster_url": "https://...",
          "progress": 0.65,
          "last_watched_at": "2025-11-12T20:00:00Z"
        }
      ]
    },
    {
      "title": "Trending Now",
      "content": [...]
    },
    {
      "title": "Because you watched...",
      "content": [...]
    }
  ]
}
```

### 2. Stream Content
```
GET /api/v1/content/{content_id}/stream?profile_id=uuid&quality=HD
Response:
{
  "manifest_url": "https://cdn.netflix.com/content/{content_id}/manifest.m3u8",
  "qualities": ["SD", "HD", "Full HD", "4K"],
  "default_quality": "HD",
  "subtitles": [
    {"language": "en", "url": "..."},
    {"language": "es", "url": "..."}
  ]
}
```

### 3. Search Content
```
GET /api/v1/content/search?q=stranger+things&limit=20&offset=0
Response:
{
  "results": [
    {
      "content_id": "uuid",
      "title": "Stranger Things",
      "type": "tv_show",
      "poster_url": "https://...",
      "release_year": 2016,
      "imdb_rating": 8.7
    }
  ],
  "total": 50,
  "limit": 20,
  "offset": 0
}
```

### 4. Get Content Details
```
GET /api/v1/content/{content_id}?profile_id=uuid
Response:
{
  "content_id": "uuid",
  "title": "Stranger Things",
  "type": "tv_show",
  "description": "...",
  "genres": ["Sci-Fi", "Horror", "Drama"],
  "release_year": 2016,
  "imdb_rating": 8.7,
  "seasons": [
    {
      "season_id": "uuid",
      "season_number": 1,
      "episodes": [...]
    }
  ],
  "watch_progress": {
    "last_episode": "uuid",
    "watch_time": 3600,
    "total_duration": 3600
  }
}
```

### 5. Update Watch Progress
```
POST /api/v1/watch/progress
Request:
{
  "profile_id": "uuid",
  "content_id": "uuid",
  "watch_time": 3600,
  "total_duration": 3600
}

Response:
{
  "status": "updated",
  "progress": 1.0,
  "completed": true
}
```

### 6. Get Recommendations
```
GET /api/v1/recommendations?profile_id=uuid&limit=20
Response:
{
  "recommendations": [
    {
      "content_id": "uuid",
      "title": "The Crown",
      "score": 0.95,
      "reason": "Similar to shows you've watched"
    }
  ]
}
```

### 7. Browse by Genre
```
GET /api/v1/content/genre/sci-fi?limit=20&offset=0
Response:
{
  "genre": "Sci-Fi",
  "content": [...],
  "total": 500
}
```

## Data Flow

### Content Streaming Flow

1. **User Selects Content**:
   - User browses and selects movie/show
   - **Client** requests stream for content
   - **Streaming Service** validates subscription and geographic availability

2. **Manifest Generation**:
   - **Streaming Service**:
     - Checks user's subscription plan (determines max quality)
     - Gets available qualities for content
     - Generates HLS/DASH manifest
     - Returns manifest URL

3. **Video Delivery**:
   - **Client** requests video segments from **CDN**
   - **CDN** serves segments from nearest edge location
   - **Client** monitors bandwidth and adapts quality
   - **Client** tracks watch progress

4. **Progress Tracking**:
   - **Client** sends watch progress periodically
   - **Watch Service** updates watch history
   - Enables "Continue Watching" feature

### Recommendation Flow

1. **User Accesses Home Page**:
   - User opens Netflix home page
   - **Client** requests home page content
   - **Recommendation Service** generates personalized recommendations

2. **Recommendation Generation**:
   - **Recommendation Service**:
     - Gets user's watch history
     - Gets user's preferences and ratings
     - Applies collaborative filtering
     - Applies content-based filtering
     - Ranks content by relevance
     - Groups into sections (Continue Watching, Trending, etc.)

3. **Response**:
   - Recommendations returned to client
   - Client displays personalized home page

### Content Search Flow

1. **User Searches**:
   - User enters search query
   - **Client** sends search request
   - **Search Service** queries **Elasticsearch**

2. **Search Processing**:
   - **Search Service**:
     - Searches by title, description, cast, director
     - Filters by geographic availability
     - Ranks by relevance and popularity
     - Returns search results

3. **Response**:
   - Search results returned to client
   - Client displays results

## Database Design

### Schema Design

**Users Table:**
```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    subscription_plan ENUM('basic', 'standard', 'premium') DEFAULT 'standard',
    billing_country VARCHAR(10),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_email (email)
);
```

**Profiles Table:**
```sql
CREATE TABLE profiles (
    profile_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    profile_name VARCHAR(50) NOT NULL,
    avatar_url VARCHAR(500),
    maturity_rating VARCHAR(10),
    language_preference VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_id (user_id)
);
```

**Content Table:**
```sql
CREATE TABLE content (
    content_id UUID PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    type ENUM('movie', 'tv_show') NOT NULL,
    description TEXT,
    release_year INT,
    duration INT, -- minutes, NULL for TV shows
    genres JSON,
    rating VARCHAR(10),
    imdb_rating DECIMAL(3, 1),
    poster_url VARCHAR(500),
    trailer_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_type (type),
    INDEX idx_release_year (release_year),
    INDEX idx_imdb_rating (imdb_rating DESC),
    FULLTEXT INDEX idx_title_description (title, description)
);
```

**TV Shows Table:**
```sql
CREATE TABLE tv_shows (
    show_id UUID PRIMARY KEY,
    content_id UUID NOT NULL,
    number_of_seasons INT DEFAULT 0,
    number_of_episodes INT DEFAULT 0,
    INDEX idx_content_id (content_id)
);
```

**Seasons Table:**
```sql
CREATE TABLE seasons (
    season_id UUID PRIMARY KEY,
    show_id UUID NOT NULL,
    season_number INT NOT NULL,
    number_of_episodes INT DEFAULT 0,
    release_date DATE,
    INDEX idx_show_id (show_id),
    UNIQUE KEY uk_show_season (show_id, season_number)
);
```

**Episodes Table:**
```sql
CREATE TABLE episodes (
    episode_id UUID PRIMARY KEY,
    season_id UUID NOT NULL,
    episode_number INT NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    duration INT NOT NULL,
    release_date DATE,
    INDEX idx_season_id (season_id),
    UNIQUE KEY uk_season_episode (season_id, episode_number)
);
```

**Content Qualities Table:**
```sql
CREATE TABLE content_qualities (
    quality_id UUID PRIMARY KEY,
    content_id UUID, -- NULL for episodes
    episode_id UUID, -- NULL for movies
    quality VARCHAR(20) NOT NULL,
    bitrate INT NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    INDEX idx_content_id (content_id),
    INDEX idx_episode_id (episode_id),
    INDEX idx_quality (quality)
);
```

**Watch History Table:**
```sql
CREATE TABLE watch_history (
    watch_id UUID PRIMARY KEY,
    profile_id UUID NOT NULL,
    content_id UUID, -- NULL for episodes
    episode_id UUID, -- NULL for movies
    watch_time INT NOT NULL DEFAULT 0,
    total_duration INT NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    last_watched_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_profile_id (profile_id),
    INDEX idx_content_id (content_id),
    INDEX idx_episode_id (episode_id),
    INDEX idx_last_watched (profile_id, last_watched_at DESC),
    UNIQUE KEY uk_profile_content (profile_id, COALESCE(content_id, episode_id))
);
```

**Recommendations Table:**
```sql
CREATE TABLE recommendations (
    recommendation_id UUID PRIMARY KEY,
    profile_id UUID NOT NULL,
    content_id UUID NOT NULL,
    score DECIMAL(5, 4) NOT NULL,
    recommendation_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_profile_score (profile_id, score DESC),
    INDEX idx_content_id (content_id)
);
```

**Geographic Availability Table:**
```sql
CREATE TABLE geographic_availability (
    availability_id UUID PRIMARY KEY,
    content_id UUID NOT NULL,
    country_code VARCHAR(10) NOT NULL,
    available BOOLEAN DEFAULT TRUE,
    available_from DATE,
    available_until DATE,
    INDEX idx_content_country (content_id, country_code),
    INDEX idx_country (country_code)
);
```

### Database Sharding Strategy

**Content Table Sharding:**
- Shard by content_id using consistent hashing
- 1000 shards: `shard_id = hash(content_id) % 1000`
- Enables parallel queries and horizontal scaling

**Watch History Sharding:**
- Shard by profile_id
- All watch history for a profile in same shard
- Enables efficient recommendation queries

**Shard Key Selection:**
- `content_id` for content-centric queries
- `profile_id` for user-centric queries
- Enables efficient queries for each use case

**Replication:**
- Each shard replicated 3x for high availability
- Master-replica setup for read scaling
- Writes go to master, reads can go to replicas

## High-Level Design

```
┌─────────────┐
│   Client    │
│  (TV/Mobile/│
│    Web)     │
└──────┬──────┘
       │
       │ HTTP/HTTPS
       │
┌──────▼──────────────────────────────────────────────┐
│        API Gateway / Load Balancer                   │
│        - Rate Limiting                               │
│        - Geographic Routing                          │
│        - Subscription Validation                     │
└──────┬──────────────────────────────────────────────┘
       │
       ├──────────────┬──────────────┬──────────────┬──────────────┐
       │              │              │              │              │
┌──────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
│ Streaming    │ │Recommendation│ │  Search   │ │  Watch    │ │  Content  │
│  Service     │ │  Service     │ │  Service  │ │  Service  │ │  Service  │
└──────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
       │              │              │              │              │
       │              │              │              │              │
┌──────▼──────────────▼──────────────▼──────────────▼──────────────▼──────┐
│              Message Queue (Kafka)                                        │
│              - Watch events                                              │
│              - Recommendation updates                                   │
└──────┬───────────────────────────────────────────────────────────────────┘
       │
       │
┌──────▼───────────────────────────────────────────────────────────────────┐
│         Database Cluster (Sharded)                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                              │
│  │ Content  │  │  Watch    │  │Recommendations│                          │
│  │ DB       │  │  History  │  │  DB       │                              │
│  └──────────┘  └──────────┘  └──────────┘                              │
│                                                                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                              │
│  │ Users    │  │ Profiles │  │ Geographic│                              │
│  │ DB       │  │ DB       │  │ Availability│                            │
│  └──────────┘  └──────────┘  └──────────┘                              │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│              CDN (Global Distribution)                                     │
│  - Video segments (HLS/DASH)                                               │
│  - Content replicated to edge locations                                    │
│  - 90%+ of traffic served from CDN                                         │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│              Origin Servers (S3)                                          │
│  - Master video files                                                     │
│  - Content replicated to CDN                                               │
│  - 10% of traffic (cache misses, new content)                            │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│              Cache Layer (Redis)                                          │
│  - Content metadata                                                       │
│  - Recommendations                                                        │
│  - Popular content                                                        │
│  - Search results                                                         │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│         Search Engine (Elasticsearch)                                     │
│         - Content search by title, description, cast                       │
│         - Full-text search                                                │
└───────────────────────────────────────────────────────────────────────────┘
```

## Deep Dive

### Component Design

#### 1. Streaming Service

**Responsibilities:**
- Serve video streams
- Generate streaming manifests
- Handle adaptive bitrate streaming
- Validate subscriptions and geographic availability

**Key Design Decisions:**
- **Adaptive Streaming**: HLS or DASH for adaptive bitrate
- **CDN Integration**: Serve from CDN, fallback to origin
- **Quality Selection**: Based on subscription plan and bandwidth
- **Geographic Filtering**: Filter content by country

**Implementation:**
```python
def get_stream(content_id, profile_id, quality=None):
    # Get profile and user
    profile = get_profile(profile_id)
    user = get_user(profile.user_id)
    
    # Check geographic availability
    country = get_user_country(user.user_id)
    if not is_content_available(content_id, country):
        raise Exception("Content not available in your region")
    
    # Get available qualities
    available_qualities = get_content_qualities(content_id)
    
    # Filter by subscription plan
    max_quality = get_max_quality_for_plan(user.subscription_plan)
    filtered_qualities = [q for q in available_qualities if q['quality'] <= max_quality]
    
    # Select quality (client preference or auto)
    if quality:
        selected_quality = quality if quality in filtered_qualities else filtered_qualities[0]
    else:
        selected_quality = filtered_qualities[-1]  # Highest available
    
    # Generate manifest
    manifest = generate_hls_manifest(content_id, filtered_qualities, selected_quality)
    
    # Get CDN URL
    cdn_url = get_cdn_url(content_id, user.billing_country)
    
    return {
        'manifest_url': f"{cdn_url}/content/{content_id}/manifest.m3u8",
        'qualities': [q['quality'] for q in filtered_qualities],
        'default_quality': selected_quality,
        'subtitles': get_subtitles(content_id, profile.language_preference)
    }
```

#### 2. Recommendation Service

**Responsibilities:**
- Generate personalized recommendations
- Analyze watch history
- Rank content by relevance
- Group recommendations into sections

**Key Design Decisions:**
- **Collaborative Filtering**: Find similar users
- **Content-Based**: Find similar content
- **Hybrid Approach**: Combine multiple signals
- **Real-Time**: Update based on recent watches

**Implementation:**
```python
def get_home_page_recommendations(profile_id):
    # Get watch history
    watch_history = get_watch_history(profile_id, limit=100)
    watched_content_ids = [w.content_id for w in watch_history]
    
    sections = []
    
    # Continue Watching
    continue_watching = get_continue_watching(profile_id, limit=10)
    sections.append({
        'title': 'Continue Watching',
        'content': continue_watching
    })
    
    # Because you watched...
    if watch_history:
        last_watched = watch_history[0]
        similar_content = find_similar_content(last_watched.content_id, limit=10)
        sections.append({
            'title': f'Because you watched {last_watched.title}',
            'content': similar_content
        })
    
    # Trending Now
    trending = get_trending_content(limit=10)
    sections.append({
        'title': 'Trending Now',
        'content': trending
    })
    
    # Top Picks for You
    top_picks = get_top_recommendations(profile_id, limit=10)
    sections.append({
        'title': 'Top Picks for You',
        'content': top_picks
    })
    
    # By Genre (user's favorite genres)
    favorite_genres = get_favorite_genres(profile_id)
    for genre in favorite_genres[:3]:
        genre_content = get_content_by_genre(genre, limit=10)
        sections.append({
            'title': f'{genre} Movies & TV',
            'content': genre_content
        })
    
    return {'sections': sections}
```

#### 3. Watch Service

**Responsibilities:**
- Track watch progress
- Update watch history
- Enable "Continue Watching"
- Track completion

**Key Design Decisions:**
- **Periodic Updates**: Update progress every 10-30 seconds
- **Completion Threshold**: Mark complete at 90% watched
- **Resume Support**: Track exact position for resume
- **Multi-Device**: Sync progress across devices

**Implementation:**
```python
def update_watch_progress(profile_id, content_id, watch_time, total_duration):
    # Get or create watch history
    watch_history = get_watch_history(profile_id, content_id)
    
    if not watch_history:
        watch_history = create_watch_history(
            profile_id=profile_id,
            content_id=content_id,
            total_duration=total_duration
        )
    
    # Update progress
    watch_history.watch_time = watch_time
    watch_history.total_duration = total_duration
    watch_history.last_watched_at = now()
    
    # Check completion (90% threshold)
    progress = watch_time / total_duration
    if progress >= 0.9:
        watch_history.completed = True
    
    watch_history.save()
    
    # Publish watch event for recommendations
    publish_watch_event(profile_id, content_id, watch_time, total_duration)
    
    return {
        'status': 'updated',
        'progress': progress,
        'completed': watch_history.completed
    }
```

#### 4. Content Service

**Responsibilities:**
- Manage content metadata
- Handle content search
- Filter by geographic availability
- Provide content details

**Key Design Decisions:**
- **Metadata Storage**: Store in database
- **Search**: Use Elasticsearch for full-text search
- **Geographic Filtering**: Filter by country
- **Caching**: Cache popular content metadata

**Implementation:**
```python
def search_content(query, country_code, limit=20, offset=0):
    # Build Elasticsearch query
    es_query = {
        "bool": {
            "must": [
                {
                    "multi_match": {
                        "query": query,
                        "fields": ["title^3", "description", "cast^2", "director^2"]
                    }
                }
            ],
            "filter": [
                {
                    "term": {"available_countries": country_code}
                }
            ]
        }
    }
    
    # Execute search
    results = elasticsearch.search(
        index="content",
        body={"query": es_query, "size": limit, "from": offset}
    )
    
    # Enrich with metadata
    content_list = []
    for hit in results["hits"]["hits"]:
        content = hit["_source"]
        content_list.append({
            "content_id": content["content_id"],
            "title": content["title"],
            "type": content["type"],
            "poster_url": content["poster_url"],
            "release_year": content["release_year"],
            "imdb_rating": content.get("imdb_rating")
        })
    
    return {
        "results": content_list,
        "total": results["hits"]["total"]["value"],
        "limit": limit,
        "offset": offset
    }
```

### Detailed Design

#### Adaptive Bitrate Streaming

**Challenge:** Stream videos efficiently based on user's bandwidth and device

**Solution:**
- **HLS (HTTP Live Streaming)**: Apple's adaptive streaming protocol
- **DASH (Dynamic Adaptive Streaming over HTTP)**: MPEG-DASH standard
- **Multiple Qualities**: Encode in SD, HD, Full HD, 4K
- **Client Adaptation**: Client selects quality based on bandwidth

**Quality Levels:**
- **SD (480p)**: 1-2 Mbps (Basic plan)
- **HD (720p)**: 3-5 Mbps (Standard plan)
- **Full HD (1080p)**: 5-8 Mbps (Premium plan)
- **4K (2160p)**: 15-25 Mbps (Premium plan)

**Implementation:**
```python
def generate_hls_manifest(content_id, qualities, default_quality):
    manifest = "#EXTM3U\n"
    manifest += "#EXT-X-VERSION:3\n"
    
    # Add quality variants
    for quality in sorted(qualities, key=lambda x: x['bitrate']):
        resolution = get_resolution(quality['quality'])
        manifest += f"#EXT-X-STREAM-INF:BANDWIDTH={quality['bitrate']*1000},RESOLUTION={resolution}\n"
        manifest += f"{quality['quality']}.m3u8\n"
    
    return manifest
```

#### CDN Distribution Strategy

**Challenge:** Efficiently distribute content globally

**Solution:**
- **Regional CDNs**: Deploy CDN nodes in major regions
- **Content Replication**: Replicate popular content to edge
- **Cache Strategy**: Cache popular content aggressively
- **Origin Fallback**: Fallback to origin for cache misses

**CDN Strategy:**
- **Popular Content**: Replicate to all edge locations
- **Medium Popularity**: Replicate to regional edges
- **Low Popularity**: Serve from origin
- **New Content**: Replicate based on predicted popularity

**Implementation:**
```python
def get_cdn_url(content_id, country_code):
    # Determine CDN region
    cdn_region = get_cdn_region(country_code)
    
    # Check if content is cached at edge
    if is_content_cached(content_id, cdn_region):
        return f"https://cdn-{cdn_region}.netflix.com"
    else:
        # Pre-warm cache for popular content
        if is_popular_content(content_id):
            prewarm_cache(content_id, cdn_region)
        
        return f"https://cdn-{cdn_region}.netflix.com"
```

#### Recommendation Algorithm

**Challenge:** Provide accurate personalized recommendations

**Solution:**
- **Collaborative Filtering**: Find users with similar tastes
- **Content-Based**: Find content similar to watched content
- **Matrix Factorization**: Use matrix factorization for collaborative filtering
- **Hybrid Approach**: Combine multiple signals

**Implementation:**
```python
def get_top_recommendations(profile_id, limit=20):
    # Get watch history
    watch_history = get_watch_history(profile_id, limit=100)
    watched_content_ids = [w.content_id for w in watch_history]
    
    # Collaborative filtering: find similar users
    similar_users = find_similar_users(profile_id, watch_history)
    
    # Get content liked by similar users
    recommended_content = []
    for similar_user in similar_users:
        user_watches = get_watched_content(similar_user.profile_id)
        for content in user_watches:
            if content.content_id not in watched_content_ids:
                recommended_content.append(content)
    
    # Content-based: find similar content
    for watched_content in watch_history[:10]:
        similar = find_similar_content(watched_content.content_id)
        recommended_content.extend(similar)
    
    # Rank by relevance
    ranked = rank_content(recommended_content, profile_id)
    
    return ranked[:limit]

def rank_content(content_list, profile_id):
    scored_content = []
    
    for content in content_list:
        score = calculate_relevance_score(content, profile_id)
        scored_content.append((content, score))
    
    # Sort by score
    scored_content.sort(key=lambda x: x[1], reverse=True)
    
    return [c[0] for c in scored_content]

def calculate_relevance_score(content, profile_id):
    # Popularity score
    popularity_score = math.log(content.total_views + 1) / 20.0
    
    # Rating score
    rating_score = content.imdb_rating / 10.0 if content.imdb_rating else 0.5
    
    # Recency score
    days_since_release = (now().date() - content.release_date).days
    recency_score = 1.0 / (1.0 + days_since_release / 365.0)
    
    # Genre match score
    profile_genres = get_favorite_genres(profile_id)
    genre_match = len(set(content.genres) & set(profile_genres)) / max(len(content.genres), 1)
    
    # Combine scores
    total_score = (
        popularity_score * 0.2 +
        rating_score * 0.3 +
        recency_score * 0.2 +
        genre_match * 0.3
    )
    
    return total_score
```

#### Geographic Content Availability

**Challenge:** Manage content availability across 190+ countries

**Solution:**
- **Availability Table**: Store availability per country
- **License Management**: Track licensing agreements
- **Regional Filtering**: Filter content by user's country
- **Cache Filtering**: Filter cached recommendations

**Implementation:**
```python
def is_content_available(content_id, country_code):
    # Check cache first
    cache_key = f"availability:{content_id}:{country_code}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    
    # Query database
    availability = db.query(
        "SELECT available FROM geographic_availability WHERE content_id = ? AND country_code = ?",
        content_id, country_code
    ).first()
    
    if availability:
        result = availability.available
    else:
        # Default: available (unless explicitly restricted)
        result = True
    
    # Cache result
    cache.set(cache_key, result, ttl=3600)
    
    return result

def filter_content_by_country(content_list, country_code):
    filtered = []
    for content in content_list:
        if is_content_available(content.content_id, country_code):
            filtered.append(content)
    return filtered
```

### Scalability Considerations

#### Horizontal Scaling

**Streaming Service:**
- Stateless service, horizontally scalable
- CDN handles 90%+ of traffic
- Load balancer distributes requests
- Geographic routing to nearest CDN

**Recommendation Service:**
- Stateless service, horizontally scalable
- Pre-compute recommendations
- Cache recommendations per profile
- Batch processing for updates

#### CDN Scaling

**Global Distribution:**
- Deploy CDN nodes in major regions
- Replicate content based on popularity
- Cache popular content aggressively
- Origin servers handle cache misses

**Cache Strategy:**
- **Popular Content**: Cache at all edges
- **Medium Popularity**: Cache at regional edges
- **Low Popularity**: Serve from origin
- **TTL**: Long TTL for stable content

#### Caching Strategy

**Redis Cache:**
- **Content Metadata**: TTL 1 hour
- **Recommendations**: TTL 30 minutes
- **Geographic Availability**: TTL 1 hour
- **Search Results**: TTL 5 minutes

**CDN Cache:**
- **Video Segments**: Long TTL (content doesn't change)
- **Manifests**: Short TTL (may update)
- **Thumbnails**: Long TTL

### Security Considerations

#### Authentication & Authorization

- **JWT Tokens**: Use JWT for API authentication
- **Subscription Validation**: Verify active subscription
- **Geographic Validation**: Verify content availability
- **Rate Limiting**: Limit requests per user

#### Content Security

- **DRM**: Digital Rights Management for content protection
- **Encryption**: Encrypt video streams
- **Access Control**: Verify subscription and geographic access
- **Anti-Piracy**: Prevent unauthorized access

#### Data Security

- **Encryption at Rest**: Encrypt content in storage
- **Encryption in Transit**: TLS for all communications
- **User Data Privacy**: Protect user watch history
- **GDPR Compliance**: Comply with data privacy regulations

### Monitoring & Observability

#### Key Metrics

**System Metrics:**
- Streaming QPS
- CDN cache hit rate
- Average bitrate
- Buffering events
- Error rate

**Business Metrics:**
- Concurrent streams
- Total watch time
- Content popularity
- Recommendation click-through rate
- Subscription metrics

#### Logging

- **Structured Logging**: JSON logs for parsing
- **Streaming Events**: Log stream starts, quality changes
- **Watch Events**: Log watch progress
- **Error Logging**: Log errors with context

#### Alerting

- **High Error Rate**: Alert if error rate > 1%
- **Low CDN Hit Rate**: Alert if hit rate < 80%
- **High Buffering**: Alert if buffering rate > 5%
- **Service Degradation**: Alert on service issues

### Trade-offs and Optimizations

#### Trade-offs

**1. CDN vs Origin: Cost vs Performance**
- **CDN**: Better performance, higher cost
- **Origin**: Lower cost, worse performance
- **Decision**: CDN for popular content, origin for long-tail

**2. Quality Levels: Many vs Few**
- **Many**: Better adaptation, more storage
- **Few**: Less storage, worse adaptation
- **Decision**: 4 quality levels (SD, HD, Full HD, 4K)

**3. Recommendation: Real-Time vs Pre-computed**
- **Real-Time**: More accurate, higher latency
- **Pre-computed**: Lower latency, less accurate
- **Decision**: Pre-compute with periodic updates

**4. Caching: Aggressive vs Conservative**
- **Aggressive**: Better performance, more storage
- **Conservative**: Less storage, worse performance
- **Decision**: Aggressive for popular content

#### Optimizations

**1. CDN Pre-warming**
- Pre-warm cache for predicted popular content
- Reduce cache misses
- Improve streaming performance

**2. Adaptive Bitrate Optimization**
- Monitor user bandwidth
- Optimize quality selection
- Reduce buffering

**3. Recommendation Caching**
- Pre-compute recommendations
- Cache per profile
- Reduce computation at request time

**4. Geographic Optimization**
- Route to nearest CDN
- Reduce latency
- Improve streaming quality

## Summary

Designing Netflix at scale requires careful consideration of:

1. **CDN Distribution**: Global CDN for efficient content delivery
2. **Adaptive Streaming**: HLS/DASH for bandwidth-efficient streaming
3. **Content Management**: Efficient storage and metadata management
4. **Recommendations**: Personalized recommendations using hybrid approach
5. **Geographic Availability**: Content filtering by region
6. **Watch Tracking**: Accurate progress tracking for resume functionality
7. **Scalability**: Horizontal scaling with CDN handling most traffic
8. **Performance**: Sub-2-second streaming start time

Key architectural decisions:
- **Global CDN** for content delivery (90%+ traffic)
- **Adaptive Bitrate Streaming** (HLS/DASH) for efficient bandwidth usage
- **Hybrid Recommendations** combining collaborative and content-based filtering
- **Geographic Filtering** for content availability management
- **Multi-Quality Encoding** (SD, HD, Full HD, 4K) based on subscription
- **Watch History Tracking** for personalized experience
- **Sharded Database** for scalability
- **Elasticsearch** for content search

The system handles 50 million concurrent streams, 250 million subscribers, and provides seamless video streaming experience globally with efficient CDN distribution and adaptive streaming.

