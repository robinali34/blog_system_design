---
layout: post
title: "Design an Auction System - System Design Interview"
date: 2025-11-14
categories: [System Design, Interview Example, Distributed Systems, E-commerce, Real-time Systems]
excerpt: "A comprehensive guide to designing an auction system like eBay, covering bid management, real-time bid updates, auction lifecycle, winner determination, payment processing, and architectural patterns for handling millions of concurrent bidders and ensuring fair, accurate auctions."
---

## Introduction

An auction system enables users to create auctions, place bids, and determine winners based on highest bid at auction end time. Systems like eBay handle millions of auctions, billions of bids, and require real-time bid updates, accurate winner determination, and protection against bid manipulation.

This post provides a detailed walkthrough of designing a scalable auction system, covering key architectural decisions, bid validation, real-time updates, conflict resolution, and scalability challenges. This is a common system design interview question that tests your understanding of distributed systems, concurrency control, real-time data distribution, and handling high-frequency transactions.

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

**Design an auction system similar to eBay with the following features:**

1. Create and manage auctions
2. Place bids on auctions
3. Real-time bid updates to all bidders
4. Automatic auction ending at specified time
5. Winner determination (highest bidder)
6. Bid history and tracking
7. Proxy bidding (automatic bidding up to max)
8. Reserve price support
9. Auction search and discovery
10. Payment processing for winners

**Scale Requirements:**
- 100 million+ users
- 10 million+ active auctions
- 1 billion+ bids per day
- Peak: 100,000 concurrent bidders
- Peak bid rate: 10,000 bids per second
- Average auction: 100 bids
- Popular auctions: 10,000+ bids
- Must prevent bid manipulation and ensure fairness

## Requirements

### Functional Requirements

**Core Features:**
1. **Auction Management**: Create, update, cancel auctions
2. **Bidding**: Place bids, validate bid amounts
3. **Real-Time Updates**: Broadcast bid updates to all watchers
4. **Proxy Bidding**: Automatic bidding up to maximum
5. **Auction Ending**: Automatic ending at specified time
6. **Winner Determination**: Determine highest bidder
7. **Bid History**: Track all bids for an auction
8. **Search**: Search auctions by category, keyword, price
9. **Notifications**: Notify bidders of outbid, auction ending
10. **Payment**: Process payment from winner

**Out of Scope:**
- Seller verification
- Shipping integration
- Dispute resolution
- Advanced analytics dashboard
- Mobile app (focus on web API)

### Non-Functional Requirements

1. **Availability**: 99.9% uptime
2. **Reliability**: No bid loss, accurate winner determination
3. **Performance**: 
   - Bid placement: < 100ms
   - Bid update broadcast: < 500ms
   - Auction search: < 500ms
4. **Scalability**: Handle 10K+ bids per second
5. **Consistency**: Strong consistency for bid validation
6. **Fairness**: Prevent bid manipulation, ensure fair auctions
7. **Real-Time**: Bid updates must appear instantly

## Capacity Estimation

### Traffic Estimates

- **Total Users**: 100 million
- **Daily Active Users (DAU)**: 10 million
- **Active Auctions**: 10 million
- **Bids per Day**: 1 billion
- **Average Bids per Auction**: 100 bids
- **Peak Concurrent Bidders**: 100,000
- **Peak Bid Rate**: 10,000 bids per second
- **Normal Bid Rate**: 1,000 bids per second

### Storage Estimates

**Auction Data:**
- 10M active auctions × 2KB = 20GB
- Historical auctions: 100M auctions/year × 2KB = 200GB/year
- 5-year retention: ~1TB

**Bid Data:**
- 1B bids/day × 200 bytes = 200GB/day
- 30-day retention: ~6TB
- 5-year archive: ~365TB

**User Data:**
- 100M users × 1KB = 100GB

**Total Storage**: ~366TB

### Bandwidth Estimates

**Normal Traffic:**
- 1,000 bids/sec × 1KB = 1MB/s = 8Mbps

**Peak Traffic:**
- 10,000 bids/sec × 1KB = 10MB/s = 80Mbps
- Real-time updates: 10K bids/sec × 5KB (broadcast) = 50MB/s = 400Mbps
- **Total Peak**: ~480Mbps

## Core Entities

### Auction
- `auction_id` (UUID)
- `seller_id` (user_id)
- `item_name`
- `description`
- `category`
- `starting_price` (DECIMAL)
- `reserve_price` (DECIMAL, optional)
- `current_bid` (DECIMAL)
- `current_bidder_id` (user_id)
- `bid_count` (INT)
- `status` (draft, active, ended, cancelled)
- `start_time` (TIMESTAMP)
- `end_time` (TIMESTAMP)
- `created_at`
- `updated_at`

### Bid
- `bid_id` (UUID)
- `auction_id`
- `user_id`
- `bid_amount` (DECIMAL)
- `is_proxy_bid` (BOOLEAN)
- `proxy_max_amount` (DECIMAL, for proxy bids)
- `status` (active, outbid, winning)
- `created_at` (TIMESTAMP)

### Proxy Bid
- `proxy_bid_id` (UUID)
- `auction_id`
- `user_id`
- `max_amount` (DECIMAL)
- `current_bid` (DECIMAL)
- `status` (active, exhausted, outbid)
- `created_at`
- `updated_at`

### User
- `user_id` (UUID)
- `username`
- `email`
- `password_hash`
- `rating` (seller/buyer rating)
- `created_at`
- `updated_at`

## API

### 1. Create Auction
```
POST /api/v1/auctions
Request:
{
  "item_name": "Vintage Watch",
  "description": "...",
  "category": "collectibles",
  "starting_price": 100.00,
  "reserve_price": 500.00,
  "duration_hours": 72
}

Response:
{
  "auction_id": "uuid",
  "item_name": "Vintage Watch",
  "starting_price": 100.00,
  "start_time": "2025-11-13T10:00:00Z",
  "end_time": "2025-11-16T10:00:00Z",
  "status": "active"
}
```

### 2. Place Bid
```
POST /api/v1/auctions/{auction_id}/bids
Request:
{
  "bid_amount": 150.00,
  "is_proxy_bid": false,
  "proxy_max_amount": null
}

Response:
{
  "bid_id": "uuid",
  "auction_id": "uuid",
  "bid_amount": 150.00,
  "status": "winning",
  "current_bid": 150.00,
  "created_at": "2025-11-13T10:05:00Z"
}
```

### 3. Place Proxy Bid
```
POST /api/v1/auctions/{auction_id}/bids
Request:
{
  "is_proxy_bid": true,
  "proxy_max_amount": 500.00
}

Response:
{
  "bid_id": "uuid",
  "proxy_bid_id": "uuid",
  "current_bid": 150.00,
  "proxy_max_amount": 500.00,
  "status": "active"
}
```

### 4. Get Auction Details
```
GET /api/v1/auctions/{auction_id}
Response:
{
  "auction_id": "uuid",
  "item_name": "Vintage Watch",
  "current_bid": 150.00,
  "current_bidder": {...},
  "bid_count": 5,
  "time_remaining": 259200, // seconds
  "status": "active",
  "bids": [
    {
      "bid_id": "uuid",
      "user": {...},
      "bid_amount": 150.00,
      "created_at": "2025-11-13T10:05:00Z"
    }
  ]
}
```

### 5. Get Real-Time Updates (WebSocket)
```
WS /ws/auctions/{auction_id}
Messages:
- Incoming: {"type": "subscribe"}
- Outgoing: {"type": "new_bid", "data": {...}}
- Outgoing: {"type": "auction_ended", "data": {...}}
- Outgoing: {"type": "outbid", "data": {...}}
```

### 6. Search Auctions
```
GET /api/v1/auctions/search?q=watch&category=collectibles&min_price=100&max_price=1000&limit=20
Response:
{
  "auctions": [...],
  "total": 500,
  "limit": 20,
  "offset": 0
}
```

### 7. Get Bid History
```
GET /api/v1/auctions/{auction_id}/bids?limit=50&offset=0
Response:
{
  "bids": [...],
  "total": 100,
  "limit": 50,
  "offset": 0
}
```

## Data Flow

### Bid Placement Flow

1. **User Places Bid**:
   - User submits bid on auction
   - **Client** sends bid request to **API Gateway**
   - **API Gateway** routes to **Bidding Service**

2. **Bid Validation**:
   - **Bidding Service**:
     - Validates auction is active
     - Validates bid amount > current bid
     - Validates bid increment (e.g., minimum $1 increment)
     - Checks user's bid history (prevent shill bidding)

3. **Bid Processing**:
   - **Bidding Service**:
     - Acquires distributed lock on auction
     - Double-checks current bid (prevent race conditions)
     - Creates bid record
     - Updates auction current bid and bidder
     - Handles proxy bid logic
     - Releases lock

4. **Real-Time Broadcast**:
   - **Bidding Service** publishes bid event to **Message Queue**
   - **Notification Service** broadcasts to all watchers via **WebSocket**
   - **Notification Service** notifies outbid users

### Proxy Bid Flow

1. **User Places Proxy Bid**:
   - User sets maximum bid amount
   - **Bidding Service** creates proxy bid record

2. **Automatic Bidding**:
   - When new bid comes in:
     - **Bidding Service** checks if proxy bid should outbid
     - If proxy max > new bid + increment:
       - Places automatic bid (new bid + increment)
       - Updates proxy bid current amount
     - Continues until proxy max is reached

3. **Proxy Bid Exhaustion**:
   - When proxy max is reached:
     - Mark proxy bid as exhausted
     - User must place new proxy bid or manual bid

### Auction Ending Flow

1. **Auction End Time Reached**:
   - **Auction Scheduler** detects auction end time
   - Triggers auction end process

2. **Winner Determination**:
   - **Auction Service**:
     - Gets all bids for auction
     - Determines highest bidder
     - Checks reserve price (if set)
     - Updates auction status to "ended"

3. **Notification**:
   - **Notification Service**:
     - Notifies winner
     - Notifies seller
     - Notifies other bidders

4. **Payment Processing**:
   - **Payment Service** processes payment from winner
   - Updates auction payment status

## Database Design

### Schema Design

**Auctions Table:**
```sql
CREATE TABLE auctions (
    auction_id UUID PRIMARY KEY,
    seller_id UUID NOT NULL,
    item_name VARCHAR(500) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    starting_price DECIMAL(10, 2) NOT NULL,
    reserve_price DECIMAL(10, 2) NULL,
    current_bid DECIMAL(10, 2) DEFAULT 0,
    current_bidder_id UUID NULL,
    bid_count INT DEFAULT 0,
    status ENUM('draft', 'active', 'ended', 'cancelled') DEFAULT 'draft',
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_seller_id (seller_id),
    INDEX idx_status (status),
    INDEX idx_end_time (end_time),
    INDEX idx_category (category),
    FULLTEXT INDEX idx_item_description (item_name, description)
);
```

**Bids Table (Sharded by auction_id):**
```sql
CREATE TABLE bids_0 (
    bid_id UUID PRIMARY KEY,
    auction_id UUID NOT NULL,
    user_id UUID NOT NULL,
    bid_amount DECIMAL(10, 2) NOT NULL,
    is_proxy_bid BOOLEAN DEFAULT FALSE,
    proxy_max_amount DECIMAL(10, 2) NULL,
    status ENUM('active', 'outbid', 'winning') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_auction_id (auction_id),
    INDEX idx_user_id (user_id),
    INDEX idx_bid_amount (bid_amount DESC),
    INDEX idx_created_at (created_at DESC)
);
-- Similar tables: bids_1, bids_2, ..., bids_N
```

**Proxy Bids Table:**
```sql
CREATE TABLE proxy_bids (
    proxy_bid_id UUID PRIMARY KEY,
    auction_id UUID NOT NULL,
    user_id UUID NOT NULL,
    max_amount DECIMAL(10, 2) NOT NULL,
    current_bid DECIMAL(10, 2) DEFAULT 0,
    status ENUM('active', 'exhausted', 'outbid') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_auction_id (auction_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    UNIQUE KEY uk_auction_user (auction_id, user_id)
);
```

**Users Table:**
```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rating DECIMAL(3, 2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_username (username),
    INDEX idx_email (email)
);
```

### Database Sharding Strategy

**Bids Table Sharding:**
- Shard by auction_id using consistent hashing
- 1000 shards: `shard_id = hash(auction_id) % 1000`
- All bids for an auction in same shard
- Enables efficient bid queries

**Shard Key Selection:**
- `auction_id` ensures all bids for an auction are in same shard
- Enables efficient queries for auction bids
- Prevents cross-shard queries for single auction

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
       │ HTTP/WebSocket
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
│  Auction    │ │  Bidding    │ │ Notification│ │  Payment   │ │  Search    │
│  Service    │ │  Service    │ │  Service    │ │  Service   │ │  Service   │
└──────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
       │              │              │              │              │
       │              │              │              │              │
┌──────▼──────────────▼──────────────▼──────────────▼──────────────▼──────┐
│              Message Queue (Kafka)                                        │
│              - Bid events                                                  │
│              - Auction events                                              │
│              - Notification events                                         │
└──────┬───────────────────────────────────────────────────────────────────┘
       │
       │
┌──────▼───────────────────────────────────────────────────────────────────┐
│         Auction Scheduler                                                 │
│         - Monitor auction end times                                        │
│         - Trigger auction ending                                          │
└──────┬───────────────────────────────────────────────────────────────────┘
       │
       │
┌──────▼───────────────────────────────────────────────────────────────────┐
│         Database Cluster (Sharded)                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                              │
│  │ Shard 0   │  │ Shard 1   │  │ Shard N   │                              │
│  │ Bids      │  │ Bids      │  │ Bids      │                              │
│  └──────────┘  └──────────┘  └──────────┘                              │
│                                                                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                              │
│  │ Auctions │  │ Proxy     │  │ Users    │                              │
│  │ DB       │  │ Bids DB   │  │ DB       │                              │
│  └──────────┘  └──────────┘  └──────────┘                              │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│              Cache Layer (Redis)                                          │
│  - Auction metadata                                                       │
│  - Current bid cache                                                      │
│  - Distributed locks                                                      │
│  - Active auctions                                                        │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│              WebSocket Service                                             │
│              - Real-time bid updates                                       │
│              - Auction status updates                                      │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│         Search Engine (Elasticsearch)                                      │
│         - Auction search by keyword, category, price                       │
└───────────────────────────────────────────────────────────────────────────┘
```

## Deep Dive

### Component Design

#### 1. Bidding Service

**Responsibilities:**
- Validate and process bids
- Handle proxy bidding logic
- Prevent race conditions
- Update auction state

**Key Design Decisions:**
- **Distributed Locks**: Use locks to prevent concurrent bid conflicts
- **Bid Validation**: Validate bid amount, increment, auction status
- **Proxy Bidding**: Automatic bidding up to maximum
- **Atomic Updates**: Ensure atomic bid and auction updates

**Critical Requirements:**
- **No Bid Loss**: All valid bids must be processed
- **Fairness**: Prevent bid manipulation
- **Accuracy**: Accurate winner determination

**Implementation:**
```python
def place_bid(auction_id, user_id, bid_amount, is_proxy_bid=False, proxy_max=None):
    # Acquire distributed lock on auction
    lock_key = f"auction:{auction_id}"
    lock = acquire_lock(lock_key, timeout=5)
    
    try:
        # Get auction
        auction = get_auction(auction_id)
        
        # Validate auction is active
        if auction.status != 'active':
            raise Exception("Auction is not active")
        
        if now() > auction.end_time:
            raise Exception("Auction has ended")
        
        # Validate bid amount
        min_bid = auction.current_bid + get_bid_increment(auction.current_bid)
        if bid_amount < min_bid:
            raise Exception(f"Bid must be at least ${min_bid}")
        
        # Handle proxy bid
        if is_proxy_bid:
            return handle_proxy_bid(auction_id, user_id, proxy_max)
        
        # Create bid
        bid = Bid(
            auction_id=auction_id,
            user_id=user_id,
            bid_amount=bid_amount,
            status='winning'
        )
        bid.save()
        
        # Update previous winning bid
        if auction.current_bidder_id:
            update_bid_status(auction_id, auction.current_bidder_id, 'outbid')
        
        # Update auction
        auction.current_bid = bid_amount
        auction.current_bidder_id = user_id
        auction.bid_count += 1
        auction.save()
        
        # Publish bid event
        publish_bid_event({
            'bid_id': bid.bid_id,
            'auction_id': auction_id,
            'user_id': user_id,
            'bid_amount': bid_amount,
            'timestamp': now()
        })
        
        return bid
    finally:
        release_lock(lock)
```

#### 2. Proxy Bidding Service

**Responsibilities:**
- Manage proxy bids
- Automatic bidding when outbid
- Handle proxy bid exhaustion

**Key Design Decisions:**
- **Automatic Bidding**: Place bids automatically when outbid
- **Increment Logic**: Bid minimum increment above competing bid
- **Exhaustion Handling**: Mark exhausted when max reached

**Implementation:**
```python
def handle_proxy_bid(auction_id, user_id, max_amount):
    # Get or create proxy bid
    proxy_bid = get_proxy_bid(auction_id, user_id)
    
    if not proxy_bid:
        proxy_bid = ProxyBid(
            auction_id=auction_id,
            user_id=user_id,
            max_amount=max_amount,
            current_bid=0,
            status='active'
        )
        proxy_bid.save()
    
    # Get auction current bid
    auction = get_auction(auction_id)
    current_bid = auction.current_bid
    
    # Calculate bid amount (current + increment, up to max)
    bid_increment = get_bid_increment(current_bid)
    new_bid = min(current_bid + bid_increment, max_amount)
    
    if new_bid > current_bid:
        # Place automatic bid
        bid = Bid(
            auction_id=auction_id,
            user_id=user_id,
            bid_amount=new_bid,
            is_proxy_bid=True,
            status='winning'
        )
        bid.save()
        
        # Update proxy bid
        proxy_bid.current_bid = new_bid
        if new_bid >= max_amount:
            proxy_bid.status = 'exhausted'
        proxy_bid.save()
        
        # Update auction
        update_auction_bid(auction_id, new_bid, user_id)
        
        return bid
    else:
        raise Exception("Proxy bid max amount too low")

def process_proxy_bids_on_new_bid(auction_id, new_bid_amount):
    # Get all active proxy bids for this auction
    proxy_bids = get_active_proxy_bids(auction_id)
    
    for proxy_bid in proxy_bids:
        if proxy_bid.user_id == get_current_bidder(auction_id):
            continue  # Skip current bidder
        
        # Check if proxy should outbid
        if proxy_bid.max_amount > new_bid_amount:
            # Place automatic bid from proxy
            bid_increment = get_bid_increment(new_bid_amount)
            proxy_bid_amount = min(new_bid_amount + bid_increment, proxy_bid.max_amount)
            
            place_bid(auction_id, proxy_bid.user_id, proxy_bid_amount, is_proxy_bid=True)
```

#### 3. Auction Scheduler

**Responsibilities:**
- Monitor auction end times
- Trigger auction ending
- Determine winners
- Handle auction cleanup

**Key Design Decisions:**
- **Scheduled Jobs**: Use cron jobs or scheduled tasks
- **Winner Determination**: Find highest bidder
- **Reserve Price**: Check reserve price before declaring winner
- **Notifications**: Notify winner and seller

**Implementation:**
```python
def end_auction(auction_id):
    # Acquire lock
    lock_key = f"auction_end:{auction_id}"
    lock = acquire_lock(lock_key, timeout=10)
    
    try:
        auction = get_auction(auction_id)
        
        # Check if already ended
        if auction.status == 'ended':
            return
        
        # Get highest bid
        highest_bid = get_highest_bid(auction_id)
        
        if not highest_bid:
            # No bids, end auction
            auction.status = 'ended'
            auction.save()
            return
        
        # Check reserve price
        if auction.reserve_price and highest_bid.bid_amount < auction.reserve_price:
            # Reserve not met, end without winner
            auction.status = 'ended'
            auction.save()
            notify_seller_reserve_not_met(auction_id)
            return
        
        # Determine winner
        auction.winner_id = highest_bid.user_id
        auction.winning_bid = highest_bid.bid_amount
        auction.status = 'ended'
        auction.ended_at = now()
        auction.save()
        
        # Notify winner and seller
        notify_winner(auction_id, highest_bid.user_id)
        notify_seller(auction_id, auction.seller_id)
        
        # Notify other bidders
        notify_outbid_bidders(auction_id, highest_bid.user_id)
        
    finally:
        release_lock(lock)

def schedule_auction_ending():
    # Find auctions ending in next minute
    ending_auctions = get_auctions_ending_soon(minutes=1)
    
    for auction in ending_auctions:
        # Schedule end job
        schedule_job(end_auction, auction.auction_id, delay=auction.end_time - now())
```

#### 4. Notification Service

**Responsibilities:**
- Broadcast bid updates in real-time
- Notify users of auction events
- Manage WebSocket connections

**Key Design Decisions:**
- **WebSocket**: Use WebSocket for real-time updates
- **Redis Pub/Sub**: Use Redis for cross-server broadcasting
- **Event Types**: Bid updates, auction ending, outbid notifications

**Implementation:**
```python
def broadcast_bid_update(auction_id, bid_data):
    # Publish to Redis channel
    redis.publish(f"auction:{auction_id}:updates", json.dumps({
        'type': 'new_bid',
        'data': bid_data
    }))
    
    # All WebSocket servers subscribed to this channel will broadcast

def notify_outbid_user(auction_id, user_id, new_bid_amount):
    # Send notification
    notification = {
        'type': 'outbid',
        'auction_id': auction_id,
        'new_bid': new_bid_amount,
        'message': 'You have been outbid'
    }
    
    # Send via WebSocket if connected
    send_websocket_message(user_id, notification)
    
    # Send via push notification
    send_push_notification(user_id, notification)
```

### Detailed Design

#### Preventing Race Conditions

**Challenge:** Multiple users bidding simultaneously on same auction

**Solution:**
- **Distributed Locks**: Acquire lock before processing bid
- **Optimistic Locking**: Use version numbers on auction
- **Database Transactions**: Use transactions for atomic updates
- **Retry Logic**: Retry on lock failure

**Implementation:**
```python
def place_bid_with_lock(auction_id, user_id, bid_amount):
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Acquire lock
            lock = acquire_lock(f"auction:{auction_id}", timeout=5)
            
            try:
                # Get auction with lock
                auction = get_auction_for_update(auction_id)
                
                # Validate and process bid
                return process_bid(auction, user_id, bid_amount)
                
            finally:
                release_lock(lock)
                
        except LockAcquisitionError:
            retry_count += 1
            if retry_count >= max_retries:
                raise Exception("Could not acquire lock, please try again")
            time.sleep(0.1 * retry_count)  # Exponential backoff
```

#### Proxy Bid Processing

**Challenge:** Process proxy bids automatically when outbid

**Solution:**
- **Event-Driven**: Process proxy bids when new bid arrives
- **Increment Logic**: Bid minimum increment above competing bid
- **Max Amount**: Respect proxy maximum amount
- **Exhaustion**: Mark exhausted when max reached

**Implementation:**
```python
def process_proxy_bids_after_bid(auction_id, new_bid_amount, new_bidder_id):
    # Get all active proxy bids except new bidder
    proxy_bids = get_active_proxy_bids(auction_id, exclude_user=new_bidder_id)
    
    # Sort by max amount descending
    proxy_bids.sort(key=lambda x: x.max_amount, reverse=True)
    
    # Process proxy bids
    current_bid = new_bid_amount
    current_bidder = new_bidder_id
    
    for proxy_bid in proxy_bids:
        if proxy_bid.max_amount <= current_bid:
            continue  # Proxy max too low
        
        # Calculate proxy bid amount
        bid_increment = get_bid_increment(current_bid)
        proxy_bid_amount = min(current_bid + bid_increment, proxy_bid.max_amount)
        
        # Place proxy bid
        bid = create_bid(
            auction_id=auction_id,
            user_id=proxy_bid.user_id,
            bid_amount=proxy_bid_amount,
            is_proxy_bid=True
        )
        
        # Update proxy bid
        proxy_bid.current_bid = proxy_bid_amount
        if proxy_bid_amount >= proxy_bid.max_amount:
            proxy_bid.status = 'exhausted'
        proxy_bid.save()
        
        # Update current bid
        current_bid = proxy_bid_amount
        current_bidder = proxy_bid.user_id
        
        # Broadcast update
        broadcast_bid_update(auction_id, bid)
        
        # Check if proxy exhausted
        if proxy_bid.status == 'exhausted':
            notify_proxy_exhausted(proxy_bid.user_id, auction_id)
```

#### Real-Time Bid Updates

**Challenge:** Broadcast bid updates to all watchers in real-time

**Solution:**
- **WebSocket Connections**: Maintain persistent connections
- **Redis Pub/Sub**: Use Redis for cross-server broadcasting
- **Connection Mapping**: Map auction_id → [connections]
- **Message Batching**: Batch multiple updates

**Implementation:**
```python
class AuctionWebSocketService:
    def __init__(self):
        self.connections = {}  # auction_id -> [connections]
        self.redis_pubsub = redis.pubsub()
    
    def handle_connection(self, websocket, auction_id, user_id):
        # Add connection
        if auction_id not in self.connections:
            self.connections[auction_id] = []
            # Subscribe to Redis channel
            self.redis_pubsub.subscribe(f"auction:{auction_id}:updates")
        
        self.connections[auction_id].append({
            'websocket': websocket,
            'user_id': user_id
        })
        
        # Send initial auction state
        auction = get_auction(auction_id)
        websocket.send(json.dumps({
            'type': 'auction_state',
            'data': {
                'current_bid': auction.current_bid,
                'bid_count': auction.bid_count,
                'time_remaining': auction.end_time - now()
            }
        }))
        
        # Listen for updates
        try:
            while True:
                # Redis messages
                message = self.redis_pubsub.get_message()
                if message:
                    self.broadcast_to_auction(auction_id, message['data'])
                
                # WebSocket messages
                data = websocket.receive()
                if data:
                    self.handle_message(websocket, auction_id, user_id, data)
        except WebSocketDisconnect:
            self.remove_connection(auction_id, websocket)
    
    def broadcast_to_auction(self, auction_id, message):
        if auction_id in self.connections:
            for conn in self.connections[auction_id]:
                try:
                    conn['websocket'].send(message)
                except:
                    self.remove_connection(auction_id, conn['websocket'])
```

#### Bid Increment Calculation

**Challenge:** Determine minimum bid increment

**Solution:**
- **Tiered Increments**: Different increments based on current bid
- **Standard Rules**: Common auction increment rules
- **Configurable**: Allow custom increments per auction

**Implementation:**
```python
def get_bid_increment(current_bid):
    if current_bid < 1:
        return 0.25
    elif current_bid < 5:
        return 0.50
    elif current_bid < 25:
        return 1.00
    elif current_bid < 100:
        return 2.50
    elif current_bid < 500:
        return 5.00
    elif current_bid < 1000:
        return 10.00
    elif current_bid < 5000:
        return 25.00
    elif current_bid < 25000:
        return 50.00
    else:
        return 100.00
```

### Scalability Considerations

#### Horizontal Scaling

**Bidding Service:**
- Stateless service, horizontally scalable
- Distributed locks for concurrency control
- Load balancer distributes requests
- Connection pooling for database

**WebSocket Service:**
- Scale horizontally with Redis pub/sub
- Each server handles subset of auctions
- Sticky sessions for WebSocket connections
- Connection limits per server

#### Caching Strategy

**Redis Cache:**
- **Auction Metadata**: TTL 1 minute
- **Current Bid**: TTL 10 seconds
- **Active Auctions**: TTL 5 minutes
- **Distributed Locks**: TTL 5 seconds

**Cache Invalidation:**
- Invalidate on bid placement
- Invalidate on auction status change
- Use cache-aside pattern

### Security Considerations

#### Bid Validation

- **Amount Validation**: Validate bid amount and increment
- **Auction Status**: Verify auction is active
- **User Validation**: Verify user can bid
- **Shill Bidding Prevention**: Detect and prevent shill bidding

#### Anti-Fraud Measures

- **Rate Limiting**: Limit bids per user per auction
- **Bid History Analysis**: Analyze bid patterns
- **Account Verification**: Verify user accounts
- **IP Tracking**: Track bid sources

### Monitoring & Observability

#### Key Metrics

**System Metrics:**
- Bid rate (bids/second)
- Bid processing latency (p50, p95, p99)
- Lock acquisition time
- WebSocket connection count
- Auction ending accuracy

**Business Metrics:**
- Total auctions
- Total bids
- Average bids per auction
- Proxy bid usage rate
- Winner determination accuracy

#### Logging

- **Structured Logging**: JSON logs for parsing
- **Bid Events**: Log all bids
- **Auction Events**: Log auction lifecycle
- **Error Logging**: Log errors with context

#### Alerting

- **High Latency**: Alert if p95 latency > 200ms
- **High Error Rate**: Alert if error rate > 1%
- **Lock Contention**: Alert on high lock wait times
- **Auction Ending Failures**: Alert on ending failures

### Trade-offs and Optimizations

#### Trade-offs

**1. Lock Duration: Short vs Long**
- **Short**: Better concurrency, more retries
- **Long**: Fewer retries, worse concurrency
- **Decision**: Short locks with retry logic

**2. Proxy Bid Processing: Immediate vs Batch**
- **Immediate**: Lower latency, higher load
- **Batch**: Higher latency, lower load
- **Decision**: Immediate for fairness

**3. Real-Time Updates: WebSocket vs Polling**
- **WebSocket**: Lower latency, more complex
- **Polling**: Simpler, higher latency
- **Decision**: WebSocket for real-time

**4. Winner Determination: Exact vs Approximate**
- **Exact**: More accurate, slower
- **Approximate**: Faster, less accurate
- **Decision**: Exact for fairness

#### Optimizations

**1. Bid Batching**
- Batch multiple proxy bids
- Reduce processing overhead
- Improve throughput

**2. Connection Pooling**
- Reuse database connections
- Reuse Redis connections
- Reduce connection overhead

**3. Caching**
- Cache auction metadata
- Cache current bids
- Reduce database load

**4. Pre-computation**
- Pre-compute bid increments
- Pre-compute proxy bid outcomes
- Reduce computation at bid time

## Summary

Designing an auction system at scale requires careful consideration of:

1. **Concurrency Control**: Distributed locks prevent race conditions
2. **Proxy Bidding**: Automatic bidding up to maximum amount
3. **Real-Time Updates**: WebSocket + Redis Pub/Sub for instant updates
4. **Winner Determination**: Accurate determination at auction end
5. **Bid Validation**: Ensure fair and valid bids
6. **Scalability**: Handle 10K+ bids per second
7. **Fairness**: Prevent bid manipulation and ensure fair auctions
8. **Performance**: Sub-100ms bid processing latency

Key architectural decisions:
- **Distributed Locks** for concurrency control
- **Proxy Bidding** for automatic bidding
- **WebSocket + Redis Pub/Sub** for real-time updates
- **Sharded Database** for bid storage
- **Auction Scheduler** for automatic ending
- **Event-Driven Architecture** for bid processing
- **Horizontal Scaling** for all services

The system handles 10,000 bids per second, ensures fair auctions with accurate winner determination, and provides real-time updates to all bidders with sub-500ms latency.

