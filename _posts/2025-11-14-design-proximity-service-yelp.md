---
layout: post
title: "Design a Proximity Service (Yelp) - System Design Interview"
date: 2025-11-14
categories: [System Design, Interview Example, Distributed Systems, Location-Based Services]
excerpt: "A comprehensive guide to designing a proximity service like Yelp, covering location-based search, business discovery, geospatial queries, reviews and ratings, recommendation algorithms, and architectural patterns for handling millions of businesses and billions of location queries."
---

## Introduction

A proximity service like Yelp helps users discover local businesses (restaurants, shops, services) based on their location. The system must handle geospatial queries efficiently, provide accurate distance calculations, support rich business information, and enable user-generated content like reviews and ratings.

This post provides a detailed walkthrough of designing a scalable proximity service, covering key architectural decisions, geospatial indexing, location-based search, recommendation algorithms, and scalability challenges. This is a common system design interview question that tests your understanding of distributed systems, geospatial databases, search optimization, and handling location-based queries at scale.

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

**Design a proximity service similar to Yelp with the following features:**

1. Business search by location (nearby businesses)
2. Business listings with details (name, address, phone, hours, etc.)
3. Search by category (restaurants, bars, shopping, etc.)
4. Reviews and ratings
5. Photos and media
6. Business hours and availability
7. Distance calculation and sorting
8. Recommendations based on user preferences
9. Check-ins and user activity
10. Business owner responses to reviews

**Scale Requirements:**
- 50 million+ businesses worldwide
- 200 million+ users
- 100 million+ reviews
- 1 billion+ search queries per day
- Peak traffic: 500,000 concurrent users
- Average search radius: 5-10 miles
- Must support sub-second response times for location queries

## Requirements

### Functional Requirements

**Core Features:**
1. **Business Management**: Business CRUD, categories, hours, contact info
2. **Location Search**: Find businesses within radius of user location
3. **Category Filtering**: Filter by business category (restaurant, bar, etc.)
4. **Search**: Full-text search by business name, category, keywords
5. **Reviews**: Users can write reviews and rate businesses
6. **Ratings**: Aggregate ratings and display average ratings
7. **Photos**: Upload and view business photos
8. **Recommendations**: Suggest businesses based on user preferences and history
9. **Check-ins**: Users can check in at businesses
10. **Business Responses**: Business owners can respond to reviews
11. **Map Integration**: Display businesses on map
12. **Sorting**: Sort by distance, rating, popularity, price

**Out of Scope:**
- Real-time reservations/bookings
- Payment processing
- Advanced analytics dashboard
- Mobile app (focus on web API)
- Internationalization (single language/currency)

### Non-Functional Requirements

1. **Availability**: 99.9% uptime
2. **Reliability**: No data loss, accurate location data
3. **Performance**: 
   - Search response time: < 500ms
   - Location query: < 200ms
   - Business details: < 100ms
4. **Scalability**: Handle 1B+ search queries per day
5. **Consistency**: Eventually consistent is acceptable for reviews/ratings
6. **Accuracy**: Geospatial queries must be accurate
7. **Real-Time**: Location queries should be real-time

## Capacity Estimation

### Traffic Estimates

- **Total Users**: 200 million
- **Daily Active Users (DAU)**: 50 million
- **Search Queries per Day**: 1 billion
- **Average Searches per User**: 20 searches/day
- **Peak Concurrent Users**: 500,000
- **Peak QPS**: 50,000 requests/second
- **Normal QPS**: 10,000 requests/second
- **Read:Write ratio**: 100:1 (searches vs reviews/business updates)

### Storage Estimates

**Business Data:**
- 50 million businesses × 2KB = 100GB
- Categories: 50M businesses × 500 bytes = 25GB
- Hours: 50M businesses × 1KB = 50GB
- Total business data: ~175GB

**Review Data:**
- 100 million reviews × 2KB = 200GB
- 5-year retention: ~1TB

**Photo Data:**
- 500 million photos × 500KB average = 250TB
- With compression: ~125TB

**User Data:**
- 200 million users × 1KB = 200GB

**Check-ins:**
- 1 billion check-ins/year × 200 bytes = 200GB/year
- 5-year retention: ~1TB

**Total Storage**: ~127TB (excluding CDN for photos)

### Bandwidth Estimates

**Normal Traffic:**
- 10,000 QPS × 10KB average response = 100MB/s = 800Mbps

**Peak Traffic:**
- 50,000 QPS × 10KB = 500MB/s = 4Gbps
- Photo serving: 50K QPS × 200KB = 10GB/s = 80Gbps
- **Total Peak**: ~84Gbps

## Core Entities

### Business
- `business_id` (UUID)
- `name`
- `address`
- `city`
- `state`
- `country`
- `postal_code`
- `latitude` (DECIMAL)
- `longitude` (DECIMAL)
- `phone`
- `website`
- `email`
- `categories` (JSON array)
- `price_range` (1-4, $ to $$$$)
- `hours` (JSON: {day: {open, close}})
- `is_closed` (boolean)
- `rating` (average rating, calculated)
- `review_count` (INT)
- `check_in_count` (INT)
- `created_at`
- `updated_at`

### Category
- `category_id` (UUID)
- `name` (e.g., "Restaurants", "Bars", "Shopping")
- `parent_category_id` (for hierarchical categories)
- `slug`

### Review
- `review_id` (UUID)
- `business_id`
- `user_id`
- `rating` (1-5)
- `text` (TEXT)
- `useful_count` (INT)
- `funny_count` (INT)
- `cool_count` (INT)
- `created_at`
- `updated_at`

### Photo
- `photo_id` (UUID)
- `business_id`
- `user_id`
- `url`
- `caption`
- `created_at`

### User
- `user_id` (UUID)
- `username`
- `email`
- `password_hash`
- `first_name`
- `last_name`
- `avatar_url`
- `review_count`
- `friend_count`
- `created_at`
- `updated_at`

### Check-in
- `check_in_id` (UUID)
- `business_id`
- `user_id`
- `latitude`
- `longitude`
- `created_at`

### Business Response
- `response_id` (UUID)
- `review_id`
- `business_id`
- `text` (TEXT)
- `created_at`

## API

### 1. Search Businesses
```
GET /api/v1/businesses/search?latitude=40.7128&longitude=-74.0060&radius=5000&category=restaurants&limit=20&offset=0&sort_by=distance
Response:
{
  "businesses": [
    {
      "business_id": "uuid",
      "name": "Joe's Pizza",
      "address": "123 Main St",
      "city": "New York",
      "state": "NY",
      "distance": 0.5,  // miles
      "rating": 4.5,
      "review_count": 1250,
      "price_range": 2,
      "categories": ["Pizza", "Italian"],
      "is_closed": false,
      "image_url": "https://..."
    }
  ],
  "total": 150,
  "region": {
    "center": {"latitude": 40.7128, "longitude": -74.0060}
  }
}
```

### 2. Get Business Details
```
GET /api/v1/businesses/{business_id}
Response:
{
  "business_id": "uuid",
  "name": "Joe's Pizza",
  "address": "123 Main St",
  "city": "New York",
  "state": "NY",
  "phone": "+1234567890",
  "website": "https://joespizza.com",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "categories": ["Pizza", "Italian"],
  "price_range": 2,
  "hours": {
    "monday": {"open": "11:00", "close": "22:00"},
    "tuesday": {"open": "11:00", "close": "22:00"}
  },
  "rating": 4.5,
  "review_count": 1250,
  "check_in_count": 5000,
  "photos": ["url1", "url2"],
  "is_closed": false
}
```

### 3. Get Business Reviews
```
GET /api/v1/businesses/{business_id}/reviews?limit=20&offset=0&sort_by=recent
Response:
{
  "reviews": [
    {
      "review_id": "uuid",
      "user": {
        "user_id": "uuid",
        "username": "john_doe",
        "avatar_url": "https://..."
      },
      "rating": 5,
      "text": "Great pizza!",
      "useful_count": 10,
      "created_at": "2025-11-10T10:00:00Z"
    }
  ],
  "total": 1250
}
```

### 4. Create Review
```
POST /api/v1/businesses/{business_id}/reviews
Request:
{
  "rating": 5,
  "text": "Great pizza! Highly recommend."
}

Response:
{
  "review_id": "uuid",
  "business_id": "uuid",
  "user_id": "uuid",
  "rating": 5,
  "text": "Great pizza! Highly recommend.",
  "created_at": "2025-11-13T10:00:00Z"
}
```

### 5. Check In
```
POST /api/v1/businesses/{business_id}/checkin
Request:
{
  "latitude": 40.7128,
  "longitude": -74.0060
}

Response:
{
  "check_in_id": "uuid",
  "business_id": "uuid",
  "user_id": "uuid",
  "created_at": "2025-11-13T10:00:00Z"
}
```

### 6. Upload Photo
```
POST /api/v1/businesses/{business_id}/photos
Request: multipart/form-data with image file

Response:
{
  "photo_id": "uuid",
  "business_id": "uuid",
  "url": "https://cdn.example.com/photos/uuid.jpg",
  "created_at": "2025-11-13T10:00:00Z"
}
```

### 7. Get Recommendations
```
GET /api/v1/recommendations?latitude=40.7128&longitude=-74.0060&limit=10
Response:
{
  "recommendations": [
    {
      "business_id": "uuid",
      "name": "Joe's Pizza",
      "distance": 0.5,
      "rating": 4.5,
      "reason": "Highly rated by users with similar preferences"
    }
  ]
}
```

### 8. Search by Text
```
GET /api/v1/businesses/search?query=pizza&latitude=40.7128&longitude=-74.0060&limit=20
Response:
{
  "businesses": [...],
  "total": 50
}
```

## Data Flow

### Location-Based Search Flow

1. **User Searches**:
   - User provides location (latitude, longitude) and search criteria
   - **Client** sends search request to **API Gateway**
   - **API Gateway** routes to **Search Service**

2. **Geospatial Query**:
   - **Search Service**:
     - Validates location and radius
     - Queries **Geospatial Database** (PostGIS/Elasticsearch) for businesses within radius
     - Applies filters (category, price range, rating)
     - Calculates distances
     - Sorts results (by distance, rating, popularity)

3. **Result Enrichment**:
   - **Search Service** enriches results with:
     - Current rating (from cache or database)
     - Review count
     - Business hours
     - Photos
   - Returns search results

### Review Creation Flow

1. **User Creates Review**:
   - User submits review with rating and text
   - **Client** sends review creation request
   - **Review Service** validates review

2. **Review Processing**:
   - **Review Service**:
     - Creates review record
     - Updates business review count
     - Recalculates business average rating
     - Publishes review event to **Message Queue**

3. **Rating Update**:
   - **Rating Service** consumes review event
   - Recalculates business average rating
   - Updates business record and cache
   - Invalidates search cache for business

### Check-in Flow

1. **User Checks In**:
   - User checks in at business location
   - **Client** sends check-in request with location
   - **Check-in Service** validates location proximity

2. **Check-in Processing**:
   - **Check-in Service**:
     - Validates user is near business (within 100m)
     - Creates check-in record
     - Updates business check-in count
     - Publishes check-in event

3. **Activity Feed**:
   - Check-in appears in user's activity feed
   - Friends can see check-in

## Database Design

### Schema Design

**Businesses Table:**
```sql
CREATE TABLE businesses (
    business_id UUID PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    address VARCHAR(500),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    postal_code VARCHAR(20),
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    phone VARCHAR(20),
    website VARCHAR(500),
    email VARCHAR(100),
    categories JSON,
    price_range INT CHECK (price_range >= 1 AND price_range <= 4),
    hours JSON,
    is_closed BOOLEAN DEFAULT FALSE,
    rating DECIMAL(3, 2),
    review_count INT DEFAULT 0,
    check_in_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_location (latitude, longitude),
    INDEX idx_city_state (city, state),
    INDEX idx_rating (rating DESC),
    INDEX idx_review_count (review_count DESC)
);

-- Geospatial index (PostGIS)
CREATE INDEX idx_business_location_gist ON businesses USING GIST (
    ST_Point(longitude, latitude)
);
```

**Categories Table:**
```sql
CREATE TABLE categories (
    category_id UUID PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    parent_category_id UUID,
    slug VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_parent (parent_category_id),
    INDEX idx_slug (slug)
);
```

**Business Categories Table:**
```sql
CREATE TABLE business_categories (
    business_id UUID,
    category_id UUID,
    PRIMARY KEY (business_id, category_id),
    INDEX idx_category (category_id)
);
```

**Reviews Table:**
```sql
CREATE TABLE reviews (
    review_id UUID PRIMARY KEY,
    business_id UUID NOT NULL,
    user_id UUID NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    text TEXT,
    useful_count INT DEFAULT 0,
    funny_count INT DEFAULT 0,
    cool_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_business_id (business_id),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at DESC),
    INDEX idx_rating (rating)
);
```

**Photos Table:**
```sql
CREATE TABLE photos (
    photo_id UUID PRIMARY KEY,
    business_id UUID NOT NULL,
    user_id UUID NOT NULL,
    url VARCHAR(500) NOT NULL,
    caption TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_business_id (business_id),
    INDEX idx_user_id (user_id)
);
```

**Users Table:**
```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    avatar_url VARCHAR(500),
    review_count INT DEFAULT 0,
    friend_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_username (username),
    INDEX idx_email (email)
);
```

**Check-ins Table:**
```sql
CREATE TABLE check_ins (
    check_in_id UUID PRIMARY KEY,
    business_id UUID NOT NULL,
    user_id UUID NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_business_id (business_id),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at DESC)
);
```

### Database Sharding Strategy

**Businesses Table Sharding:**
- Shard by geographic region using consistent hashing
- Shard key: `hash(city + state + country) % num_shards`
- 1000 shards: Each shard handles businesses in specific regions
- Enables parallel processing and horizontal scaling

**Shard Key Selection:**
- Geographic sharding keeps nearby businesses together
- Enables efficient geospatial queries within shard
- Reduces cross-shard queries for location-based searches

**Replication:**
- Each shard replicated 3x for high availability
- Master-replica setup for read scaling
- Writes go to master, reads can go to replicas

**Indexing Strategy:**
- Geospatial index (PostGIS GIST) for location queries
- Index on `(latitude, longitude)` for bounding box queries
- Index on `rating` and `review_count` for sorting
- Composite indexes for common query patterns

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
│         CDN (Static Content: Images, CSS, JS)        │
└──────────────────────────────────────────────────────┘
       │
       │
┌──────▼──────────────────────────────────────────────┐
│        API Gateway / Load Balancer                   │
│        - Rate Limiting                               │
│        - Request Routing                             │
│        - Authentication                              │
└──────┬──────────────────────────────────────────────┘
       │
       ├──────────────┬──────────────┬──────────────┬──────────────┐
       │              │              │              │              │
┌──────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
│   Search    │ │  Business  │ │  Review    │ │  Check-in  │ │  Photo    │
│   Service   │ │  Service  │ │  Service   │ │  Service   │ │  Service  │
└──────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
       │              │              │              │              │
       │              │              │              │              │
┌──────▼──────────────▼──────────────▼──────────────▼──────────────▼──────┐
│              Message Queue (Kafka)                                        │
│              - Review events                                              │
│              - Rating updates                                            │
│              - Check-in events                                           │
└───────────────────────────────────────────────────────────────────────────┘
       │
       │
┌──────▼───────────────────────────────────────────────────────────────────┐
│         Database Cluster (Sharded by Geography)                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                              │
│  │ Shard 0   │  │ Shard 1   │  │ Shard N   │                              │
│  │ Businesses│ │ Businesses│ │ Businesses│                              │
│  │ (Region 1)│ │ (Region 2)│ │ (Region N)│                              │
│  └──────────┘  └──────────┘  └──────────┘                              │
│                                                                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Reviews  │  │  Users    │  │ Check-ins│  │  Photos  │              │
│  │ DB       │  │ DB       │  │ DB       │  │ DB       │              │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘              │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│              Cache Layer (Redis)                                          │
│  - Business details                                                        │
│  - Search results cache                                                    │
│  - Rating cache                                                            │
│  - Popular businesses                                                      │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│         Search Engine (Elasticsearch)                                       │
│         - Full-text search                                                 │
│         - Geospatial search                                                │
│         - Category filtering                                               │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│         Geospatial Database (PostGIS)                                      │
│         - Location-based queries                                           │
│         - Distance calculations                                            │
│         - Bounding box queries                                             │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│         Object Storage (S3)                                                 │
│         - Photo storage                                                    │
│         - CDN integration                                                  │
└───────────────────────────────────────────────────────────────────────────┘
```

## Deep Dive

### Component Design

#### 1. Search Service

**Responsibilities:**
- Process location-based search queries
- Integrate with geospatial database and Elasticsearch
- Filter by category, price, rating
- Sort and rank results

**Key Design Decisions:**
- **Geospatial Database**: Use PostGIS for location queries
- **Elasticsearch**: Use for full-text search and filtering
- **Caching**: Cache popular search results
- **Hybrid Approach**: Combine geospatial DB and Elasticsearch

**Scalability:**
- Stateless service, horizontally scalable
- Geospatial database cluster
- Elasticsearch cluster for search
- Cache frequently searched locations

#### 2. Business Service

**Responsibilities:**
- Manage business CRUD operations
- Provide business details
- Update business information
- Calculate and cache ratings

**Key Design Decisions:**
- **Caching**: Cache business details with 1-hour TTL
- **Rating Calculation**: Pre-calculate and cache average ratings
- **Cache Invalidation**: Invalidate on updates

**Scalability:**
- Stateless service, horizontally scalable
- Read replicas for read-heavy workloads
- Connection pooling

#### 3. Review Service

**Responsibilities:**
- Create and manage reviews
- Update business ratings
- Handle review moderation
- Calculate review helpfulness

**Key Design Decisions:**
- **Async Processing**: Process rating updates asynchronously
- **Idempotency**: Prevent duplicate reviews
- **Moderation**: Basic spam detection

**Implementation:**
```python
def create_review(business_id, user_id, rating, text):
    # Check if user already reviewed this business
    existing_review = Review.objects.filter(
        business_id=business_id,
        user_id=user_id
    ).first()
    
    if existing_review:
        raise Exception("User already reviewed this business")
    
    # Create review
    review = Review(
        business_id=business_id,
        user_id=user_id,
        rating=rating,
        text=text
    )
    review.save()
    
    # Publish review event for async rating update
    publish_review_event({
        'review_id': review.id,
        'business_id': business_id,
        'rating': rating,
        'action': 'created'
    })
    
    return review
```

#### 4. Check-in Service

**Responsibilities:**
- Validate check-in location
- Create check-in records
- Update business check-in counts
- Track user activity

**Key Design Decisions:**
- **Location Validation**: Verify user is near business (within 100m)
- **Rate Limiting**: Limit check-ins per user per business
- **Activity Feed**: Publish check-in events

**Implementation:**
```python
def check_in(business_id, user_id, latitude, longitude):
    # Get business location
    business = Business.objects.get(business_id=business_id)
    
    # Calculate distance
    distance = calculate_distance(
        (latitude, longitude),
        (business.latitude, business.longitude)
    )
    
    # Validate proximity (within 100 meters)
    if distance > 0.1:  # 100 meters
        raise Exception("User is not near business")
    
    # Check rate limiting (max 1 check-in per hour)
    recent_checkin = CheckIn.objects.filter(
        business_id=business_id,
        user_id=user_id,
        created_at__gte=now() - timedelta(hours=1)
    ).first()
    
    if recent_checkin:
        raise Exception("Already checked in recently")
    
    # Create check-in
    checkin = CheckIn(
        business_id=business_id,
        user_id=user_id,
        latitude=latitude,
        longitude=longitude
    )
    checkin.save()
    
    # Update business check-in count
    Business.objects.filter(business_id=business_id).update(
        check_in_count=F('check_in_count') + 1
    )
    
    # Publish check-in event
    publish_checkin_event(checkin)
    
    return checkin
```

### Detailed Design

#### Geospatial Query Optimization

**Challenge:** Efficiently find businesses within radius

**Solution:**
- **PostGIS**: Use PostGIS for geospatial queries
- **Spatial Index**: Use GIST index on location
- **Bounding Box**: First filter by bounding box, then calculate exact distance
- **Caching**: Cache results for popular locations

**Implementation:**
```sql
-- Find businesses within 5km radius
SELECT 
    business_id,
    name,
    latitude,
    longitude,
    ST_Distance(
        ST_Point(longitude, latitude),
        ST_Point(-74.0060, 40.7128)
    ) * 111.32 AS distance_km  -- Convert to km
FROM businesses
WHERE ST_DWithin(
    ST_Point(longitude, latitude)::geography,
    ST_Point(-74.0060, 40.7128)::geography,
    5000  -- 5km in meters
)
ORDER BY distance_km
LIMIT 20;
```

**Python Implementation:**
```python
def search_nearby(latitude, longitude, radius_km, filters):
    # Convert radius to meters
    radius_meters = radius_km * 1000
    
    # Build query
    query = """
        SELECT 
            business_id,
            name,
            latitude,
            longitude,
            rating,
            review_count,
            ST_Distance(
                ST_Point(longitude, latitude)::geography,
                ST_Point(%s, %s)::geography
            ) * 0.001 AS distance_km
        FROM businesses
        WHERE ST_DWithin(
            ST_Point(longitude, latitude)::geography,
            ST_Point(%s, %s)::geography,
            %s
        )
    """
    
    # Add filters
    if filters.get('category'):
        query += " AND categories @> %s"
    
    if filters.get('min_rating'):
        query += " AND rating >= %s"
    
    query += " ORDER BY distance_km LIMIT %s"
    
    # Execute query
    results = database.execute(query, [
        longitude, latitude,
        longitude, latitude,
        radius_meters,
        filters.get('category'),
        filters.get('min_rating'),
        20
    ])
    
    return results
```

#### Rating Calculation

**Challenge:** Efficiently calculate and update business ratings

**Solution:**
- **Pre-calculation**: Calculate average rating and store in business table
- **Async Updates**: Update rating asynchronously when reviews are created/updated
- **Caching**: Cache ratings in Redis
- **Batch Updates**: Batch rating recalculations

**Implementation:**
```python
def update_business_rating(business_id):
    # Calculate average rating
    reviews = Review.objects.filter(business_id=business_id)
    
    if reviews.count() == 0:
        average_rating = None
        review_count = 0
    else:
        average_rating = reviews.aggregate(
            avg_rating=Avg('rating')
        )['avg_rating']
        review_count = reviews.count()
    
    # Update business
    Business.objects.filter(business_id=business_id).update(
        rating=round(average_rating, 2) if average_rating else None,
        review_count=review_count
    )
    
    # Update cache
    cache.set(f"business:{business_id}:rating", average_rating, 3600)
    
    # Invalidate search cache
    invalidate_search_cache(business_id)
```

#### Recommendation Algorithm

**Challenge:** Recommend businesses based on user preferences

**Solution:**
- **Collaborative Filtering**: Find users with similar preferences
- **Content-Based**: Recommend based on user's past reviews/check-ins
- **Hybrid Approach**: Combine multiple signals
- **Real-Time**: Calculate recommendations on-demand or pre-compute

**Implementation:**
```python
def get_recommendations(user_id, latitude, longitude, limit=10):
    # Get user's past preferences
    user_reviews = Review.objects.filter(user_id=user_id).values_list(
        'business_id', 'rating'
    )
    
    # Find similar users (users who rated same businesses similarly)
    similar_users = find_similar_users(user_id, user_reviews)
    
    # Get businesses liked by similar users
    recommended_businesses = get_businesses_from_users(
        similar_users,
        exclude_businesses=[r[0] for r in user_reviews]
    )
    
    # Filter by location (within 10km)
    nearby_businesses = filter_by_location(
        recommended_businesses,
        latitude,
        longitude,
        radius_km=10
    )
    
    # Rank by rating and review count
    ranked = sorted(
        nearby_businesses,
        key=lambda b: (b.rating or 0) * b.review_count,
        reverse=True
    )
    
    return ranked[:limit]
```

### Scalability Considerations

#### Horizontal Scaling

**API Services:**
- Stateless services, scale horizontally
- Load balancer distributes requests
- Auto-scaling based on CPU/memory metrics

**Database:**
- Shard businesses table by geographic region
- Read replicas for read scaling
- Connection pooling

**Cache:**
- Redis cluster for high availability
- Shard cache by business_id
- Cache warming for popular businesses

#### Caching Strategy

**Redis Cache:**
- **Business Details**: TTL 1 hour
- **Search Results**: TTL 5 minutes
- **Ratings**: TTL 1 hour
- **Popular Businesses**: TTL 30 minutes
- **User Sessions**: TTL 30 minutes

**Cache Invalidation:**
- Invalidate on business updates
- Invalidate on review creation
- Invalidate on rating updates
- Use cache-aside pattern

#### Load Balancing

**Traffic Distribution:**
- Round-robin or least-connections
- Health checks for backend services
- Circuit breakers for failing services

**Geographic Distribution:**
- CDN for static content and photos
- Regional database replicas
- Edge caching for popular locations

#### Database Optimization

**Indexing:**
- Geospatial index (PostGIS GIST) for location queries
- Index on `(latitude, longitude)` for bounding box queries
- Index on `rating` and `review_count` for sorting
- Composite indexes for common query patterns

**Query Optimization:**
- Use pagination for large result sets
- Limit query result sizes
- Use covering indexes where possible
- Batch operations for efficiency

### Security Considerations

#### Authentication & Authorization

- **JWT Tokens**: Use JWT for API authentication
- **Rate Limiting**: Limit requests per user/IP
- **Permission Checks**: Verify user owns review before modifications
- **Input Validation**: Validate all inputs

#### Data Protection

- **Input Validation**: Validate all inputs
- **SQL Injection Prevention**: Use parameterized queries
- **XSS Prevention**: Sanitize user inputs
- **CSRF Protection**: Use CSRF tokens

#### Location Privacy

- **Anonymization**: Don't store exact user locations long-term
- **Aggregation**: Aggregate location data for analytics
- **Consent**: Get user consent for location tracking

### Monitoring & Observability

#### Key Metrics

**System Metrics:**
- Request rate (requests/second)
- Response latency (p50, p95, p99)
- Error rate
- Database query latency
- Cache hit rate
- Geospatial query performance

**Business Metrics:**
- Search queries per day
- Businesses searched
- Reviews created per day
- Check-ins per day
- Average rating
- Popular categories

#### Logging

- **Structured Logging**: JSON logs for easy parsing
- **Request Tracing**: Trace requests across services
- **Error Logging**: Log errors with context
- **Geospatial Logging**: Log location queries for optimization

#### Alerting

- **High Error Rate**: Alert if error rate > 1%
- **High Latency**: Alert if p95 latency > 500ms
- **Database Issues**: Alert on database errors
- **Geospatial Query Performance**: Alert if queries > 1 second

### Trade-offs and Optimizations

#### Trade-offs

**1. Geospatial Database: PostGIS vs Elasticsearch**
- **PostGIS**: Better for complex geospatial queries, but requires PostgreSQL
- **Elasticsearch**: Good for search and simple geospatial, but less accurate
- **Decision**: Use PostGIS for primary geospatial queries, Elasticsearch for search

**2. Rating Calculation: Real-Time vs Batch**
- **Real-Time**: More accurate, but higher database load
- **Batch**: Lower load, but slight delay in updates
- **Decision**: Async updates with eventual consistency

**3. Search: Database vs Elasticsearch**
- **Database**: Simpler, but slower for complex queries
- **Elasticsearch**: Faster for full-text search, but additional infrastructure
- **Decision**: Elasticsearch for search, database for geospatial

**4. Caching: Aggressive vs Conservative**
- **Aggressive**: Better performance, but may show stale data
- **Conservative**: More accurate, but higher database load
- **Decision**: Moderate caching with smart invalidation

#### Optimizations

**1. Geospatial Index Optimization**
- Use PostGIS GIST index for fast location queries
- Pre-calculate distances for common locations
- Use bounding box queries before exact distance

**2. Batch Operations**
- Batch rating updates
- Batch cache updates
- Reduce database round trips

**3. Read Replicas**
- Use read replicas for read-heavy queries
- Reduce load on primary database
- Improve read performance

**4. CDN for Static Content**
- Serve photos via CDN
- Reduce server load
- Improve delivery speed

**5. Compression**
- Compress API responses
- Reduce bandwidth usage
- Improve performance

## Summary

Designing a proximity service like Yelp at scale requires careful consideration of:

1. **Geospatial Queries**: PostGIS for efficient location-based queries
2. **Search Optimization**: Elasticsearch for full-text search
3. **Rating Management**: Pre-calculated ratings with async updates
4. **Scalability**: Horizontal scaling with geographic sharding
5. **Caching**: Strategic caching for performance
6. **Recommendations**: Hybrid recommendation algorithm
7. **Performance**: Sub-second response times for location queries
8. **Accuracy**: Accurate distance calculations and location data

Key architectural decisions:
- **PostGIS** for geospatial queries
- **Elasticsearch** for full-text search
- **Geographic Sharding** for businesses
- **Redis Cache** for business details and search results
- **Async Processing** for rating updates
- **CDN** for photo delivery
- **Horizontal Scaling** for all services

The system handles 1 billion search queries per day with sub-second response times and accurate location-based results.

