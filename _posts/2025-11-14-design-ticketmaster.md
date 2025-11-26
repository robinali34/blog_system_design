---
layout: post
title: "Design Ticketmaster - System Design Interview"
date: 2025-11-14
categories: [System Design, Interview Example, Distributed Systems, E-commerce]
excerpt: "A comprehensive guide to designing Ticketmaster, covering ticket booking, seat selection, concurrent booking prevention, payment processing, event management, and architectural patterns for handling millions of concurrent users competing for limited tickets."
---

## Introduction

Ticketmaster is a ticket sales and distribution company that handles ticket sales for concerts, sports events, theater shows, and other live entertainment events. The system must handle massive traffic spikes when popular events go on sale, prevent overselling tickets, ensure fair access, and process payments reliably.

This post provides a detailed walkthrough of designing Ticketmaster, covering key architectural decisions, concurrency control, seat selection algorithms, payment processing, and scalability challenges. This is one of the most common system design interview questions that tests your understanding of distributed systems, database transactions, race conditions, and handling high-traffic events.

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

**Design Ticketmaster with the following features:**

1. Event listing and search
2. Seat selection (visual seat map)
3. Ticket booking with seat reservation
4. Payment processing
5. Order confirmation and ticket delivery
6. Waitlist for sold-out events
7. Resale marketplace
8. User accounts and order history

**Scale Requirements:**
- 100 million+ users
- 1 million+ events per year
- 500 million+ tickets sold per year
- Peak traffic: 10 million concurrent users during popular event sales
- Average event: 10,000 seats
- Large events: 100,000+ seats
- Ticket sale duration: 5-15 minutes for popular events
- Must prevent overselling (critical requirement)

## Requirements

### Functional Requirements

**Core Features:**
1. **Event Management**: Create, update, delete events with venue and seat information
2. **Event Discovery**: Search and browse events by location, date, category
3. **Seat Selection**: Visual seat map showing available/occupied seats
4. **Ticket Booking**: Reserve seats, add to cart, checkout
5. **Seat Reservation**: Hold seats for limited time (5-10 minutes) during checkout
6. **Payment Processing**: Accept credit cards, process payments securely
7. **Order Management**: Create orders, send confirmations, manage cancellations
8. **Ticket Delivery**: Email tickets, mobile tickets, print-at-home
9. **Waitlist**: Add users to waitlist when event is sold out
10. **Resale**: Allow users to resell tickets (with fees)
11. **User Accounts**: Registration, authentication, order history
12. **Notifications**: Email/SMS notifications for order updates

**Out of Scope:**
- Dynamic pricing (assume fixed pricing)
- Ticket transfer between users
- Advanced analytics and reporting
- Mobile app (focus on web)
- Internationalization (single currency/language)

### Non-Functional Requirements

1. **Availability**: 99.9% uptime
2. **Reliability**: No overselling, guaranteed seat reservation
3. **Performance**: 
   - Page load time: < 2 seconds
   - Seat selection response: < 500ms
   - Booking completion: < 5 seconds
   - Payment processing: < 10 seconds
4. **Scalability**: Handle 10M+ concurrent users during peak sales
5. **Consistency**: Strong consistency for seat availability (critical)
6. **Durability**: All orders must be persisted reliably
7. **Fairness**: Prevent bots, implement rate limiting, queue system for high-demand events

## Capacity Estimation

### Traffic Estimates

- **Total Users**: 100 million
- **Daily Active Users (DAU)**: 10 million
- **Events per Year**: 1 million
- **Tickets Sold per Year**: 500 million
- **Average Tickets per Order**: 2-4 tickets
- **Orders per Year**: ~150 million
- **Average Orders per Day**: ~400,000
- **Peak Event Sale**: 10 million concurrent users
- **Peak QPS**: 100,000 requests/second during popular event sales
- **Normal QPS**: 5,000 requests/second

### Storage Estimates

**Event Data:**
- 1 million events/year × 5 years retention = 5 million events
- Average event: 2KB metadata = 10GB
- Seat maps: 5M events × 50KB average = 250GB
- Total events: ~260GB

**Order Data:**
- 150 million orders/year × 5 years = 750 million orders
- Average order: 1KB = 750GB
- Total orders: ~750GB

**User Data:**
- 100 million users × 1KB = 100GB

**Seat Availability:**
- 5M events × 10K seats average = 50 billion seat records
- Each record: 50 bytes = 2.5TB
- With indexes: ~5TB

**Total Storage**: ~6TB (excluding media/images)

### Bandwidth Estimates

**Normal Traffic:**
- 5,000 QPS × 10KB average response = 50MB/s = 400Mbps

**Peak Traffic:**
- 100,000 QPS × 10KB = 1GB/s = 8Gbps
- Seat map images: 100K QPS × 200KB = 20GB/s = 160Gbps
- **Total Peak**: ~168Gbps

## Core Entities

### Event
- `event_id` (UUID)
- `name`
- `description`
- `venue_id`
- `start_time`
- `end_time`
- `category` (concert, sports, theater, etc.)
- `status` (upcoming, on_sale, sold_out, cancelled)
- `on_sale_time`
- `total_seats`
- `available_seats`
- `price_tiers` (JSON: {section: price})
- `created_at`
- `updated_at`

### Venue
- `venue_id` (UUID)
- `name`
- `address`
- `city`
- `state`
- `country`
- `capacity`
- `seat_map_url`
- `layout_type` (stadium, theater, arena, etc.)

### Seat
- `seat_id` (UUID)
- `event_id`
- `section`
- `row`
- `number`
- `status` (available, reserved, sold, blocked)
- `price_tier`
- `price`
- `reserved_until` (timestamp, null if not reserved)
- `reserved_by` (user_id, null if not reserved)

### Order
- `order_id` (UUID)
- `user_id`
- `event_id`
- `status` (pending, confirmed, cancelled, refunded)
- `total_amount`
- `currency`
- `payment_method`
- `payment_status` (pending, completed, failed)
- `created_at`
- `confirmed_at`
- `expires_at` (for pending orders)

### Order Item
- `order_item_id` (UUID)
- `order_id`
- `seat_id`
- `price`
- `status` (reserved, confirmed, cancelled)

### User
- `user_id` (UUID)
- `email`
- `username`
- `password_hash`
- `phone_number`
- `created_at`
- `updated_at`

### Reservation
- `reservation_id` (UUID)
- `user_id`
- `event_id`
- `seat_ids` (array)
- `expires_at`
- `status` (active, expired, converted_to_order)

## API

### 1. Search Events
```
GET /api/v1/events?location=NYC&date=2025-12-01&category=concert&limit=20&offset=0
Response:
{
  "events": [
    {
      "event_id": "uuid",
      "name": "Taylor Swift Concert",
      "venue": "Madison Square Garden",
      "start_time": "2025-12-15T20:00:00Z",
      "available_seats": 5000,
      "min_price": 100.00
    }
  ],
  "total": 150,
  "limit": 20,
  "offset": 0
}
```

### 2. Get Event Details
```
GET /api/v1/events/{event_id}
Response:
{
  "event_id": "uuid",
  "name": "Taylor Swift Concert",
  "description": "...",
  "venue": {...},
  "start_time": "2025-12-15T20:00:00Z",
  "available_seats": 5000,
  "price_tiers": {
    "VIP": 500.00,
    "Floor": 300.00,
    "Lower Bowl": 150.00,
    "Upper Bowl": 100.00
  }
}
```

### 3. Get Seat Map
```
GET /api/v1/events/{event_id}/seats?section=Floor
Response:
{
  "sections": [
    {
      "section": "Floor",
      "rows": [
        {
          "row": "A",
          "seats": [
            {"seat_id": "uuid", "number": 1, "status": "available", "price": 300.00},
            {"seat_id": "uuid", "number": 2, "status": "reserved", "price": 300.00}
          ]
        }
      ]
    }
  ]
}
```

### 4. Reserve Seats
```
POST /api/v1/events/{event_id}/reserve
Request:
{
  "seat_ids": ["uuid1", "uuid2"],
  "hold_duration": 600  // seconds
}

Response:
{
  "reservation_id": "uuid",
  "seat_ids": ["uuid1", "uuid2"],
  "expires_at": "2025-11-13T10:10:00Z",
  "total_amount": 600.00
}
```

### 5. Create Order
```
POST /api/v1/orders
Request:
{
  "reservation_id": "uuid",
  "payment_method": "credit_card",
  "payment_details": {
    "card_number": "****",
    "expiry": "12/25",
    "cvv": "***"
  }
}

Response:
{
  "order_id": "uuid",
  "status": "confirmed",
  "total_amount": 600.00,
  "tickets": [
    {
      "ticket_id": "uuid",
      "seat": "Floor A-1",
      "qr_code": "base64_encoded_qr"
    }
  ],
  "confirmation_email_sent": true
}
```

### 6. Get Order Status
```
GET /api/v1/orders/{order_id}
Response:
{
  "order_id": "uuid",
  "status": "confirmed",
  "event": {...},
  "seats": [...],
  "total_amount": 600.00,
  "created_at": "2025-11-13T10:05:00Z"
}
```

### 7. Cancel Reservation
```
DELETE /api/v1/reservations/{reservation_id}
Response:
{
  "status": "cancelled",
  "seats_released": 2
}
```

### 8. Get User Orders
```
GET /api/v1/users/{user_id}/orders
Response:
{
  "orders": [
    {
      "order_id": "uuid",
      "event": {...},
      "status": "confirmed",
      "total_amount": 600.00,
      "created_at": "2025-11-13T10:05:00Z"
    }
  ]
}
```

## Data Flow

### Event Sale Flow (High-Demand Event)

1. **Pre-Sale Preparation**:
   - Event goes on sale at specific time
   - Load balancer ready for traffic spike
   - Database connections pooled
   - Cache warmed with event data

2. **User Arrives**:
   - User navigates to event page
   - **CDN** serves static content (seat maps, images)
   - **API Gateway** routes to **Event Service**
   - **Event Service** returns event details from cache

3. **Seat Selection**:
   - User selects seats on seat map
   - **Client** sends seat availability check to **Seat Service**
   - **Seat Service** checks seat status in **Database** (with locking)
   - Returns available/reserved status

4. **Seat Reservation**:
   - User confirms seat selection
   - **Client** calls **Reservation Service**
   - **Reservation Service**:
     - Acquires distributed lock on seats
     - Checks seat availability
     - Creates reservation record with expiration
     - Updates seat status to "reserved"
     - Releases lock
   - Returns reservation_id and expiration time

5. **Checkout**:
   - User proceeds to checkout
   - **Client** sends order creation request with reservation_id
   - **Order Service**:
     - Validates reservation still active
     - Creates order record
     - Processes payment via **Payment Service**
     - On success: Updates seat status to "sold", creates tickets
     - On failure: Releases reservation, updates seat status to "available"

6. **Order Confirmation**:
   - **Order Service** sends confirmation email via **Notification Service**
   - Returns order confirmation with tickets

### Seat Availability Check Flow

1. **User Views Seat Map**:
   - **Client** requests seat map for event
   - **Seat Service** queries database for seat availability
   - Returns seat map with status (available/reserved/sold)

2. **Real-Time Updates**:
   - **Seat Service** subscribes to seat status changes via **Message Queue**
   - When seat status changes, updates are pushed to connected clients
   - **Client** updates seat map in real-time

### Payment Processing Flow

1. **Payment Request**:
   - **Order Service** receives payment request
   - Validates order and amount
   - Calls **Payment Service**

2. **Payment Processing**:
   - **Payment Service**:
     - Validates payment details
     - Calls external payment gateway (Stripe, PayPal)
     - Waits for payment confirmation
     - Updates payment status

3. **Payment Callback**:
   - Payment gateway sends webhook callback
   - **Payment Service** updates order status
   - **Order Service** finalizes order and creates tickets

## Database Design

### Schema Design

**Events Table:**
```sql
CREATE TABLE events (
    event_id UUID PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    venue_id UUID NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    category VARCHAR(50),
    status ENUM('upcoming', 'on_sale', 'sold_out', 'cancelled') DEFAULT 'upcoming',
    on_sale_time TIMESTAMP NOT NULL,
    total_seats INT NOT NULL,
    available_seats INT NOT NULL,
    price_tiers JSON,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_venue_id (venue_id),
    INDEX idx_start_time (start_time),
    INDEX idx_status (status),
    INDEX idx_on_sale_time (on_sale_time),
    INDEX idx_category (category)
);
```

**Venues Table:**
```sql
CREATE TABLE venues (
    venue_id UUID PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    address VARCHAR(500),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    capacity INT NOT NULL,
    seat_map_url VARCHAR(500),
    layout_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Seats Table (Sharded by event_id):**
```sql
CREATE TABLE seats_0 (
    seat_id UUID PRIMARY KEY,
    event_id UUID NOT NULL,
    section VARCHAR(50) NOT NULL,
    row VARCHAR(10) NOT NULL,
    number VARCHAR(10) NOT NULL,
    status ENUM('available', 'reserved', 'sold', 'blocked') DEFAULT 'available',
    price_tier VARCHAR(50),
    price DECIMAL(10, 2) NOT NULL,
    reserved_until TIMESTAMP NULL,
    reserved_by UUID NULL,
    order_id UUID NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_event_seat (event_id, section, row, number),
    INDEX idx_status (status),
    INDEX idx_reserved_until (reserved_until),
    INDEX idx_order_id (order_id)
);
-- Similar tables: seats_1, seats_2, ..., seats_N
```

**Orders Table:**
```sql
CREATE TABLE orders (
    order_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    event_id UUID NOT NULL,
    status ENUM('pending', 'confirmed', 'cancelled', 'refunded') DEFAULT 'pending',
    total_amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payment_method VARCHAR(50),
    payment_status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
    payment_transaction_id VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW(),
    confirmed_at TIMESTAMP NULL,
    expires_at TIMESTAMP NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_event_id (event_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at DESC)
);
```

**Order Items Table:**
```sql
CREATE TABLE order_items (
    order_item_id UUID PRIMARY KEY,
    order_id UUID NOT NULL,
    seat_id UUID NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    status ENUM('reserved', 'confirmed', 'cancelled') DEFAULT 'reserved',
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_order_id (order_id),
    INDEX idx_seat_id (seat_id)
);
```

**Reservations Table:**
```sql
CREATE TABLE reservations (
    reservation_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    event_id UUID NOT NULL,
    seat_ids JSON NOT NULL,  -- Array of seat_ids
    expires_at TIMESTAMP NOT NULL,
    status ENUM('active', 'expired', 'converted_to_order') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_id (user_id),
    INDEX idx_event_id (event_id),
    INDEX idx_expires_at (expires_at),
    INDEX idx_status (status)
);
```

**Users Table:**
```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_email (email)
);
```

### Database Sharding Strategy

**Seats Table Sharding:**
- Shard by `event_id` using consistent hashing
- 1000 shards: `shard_id = hash(event_id) % 1000`
- Each shard handles seats for multiple events
- Enables parallel processing and horizontal scaling

**Shard Key Selection:**
- `event_id` ensures all seats for an event are in the same shard
- Enables efficient queries for event seat availability
- Prevents cross-shard queries for single event

**Replication:**
- Each shard replicated 3x for high availability
- Master-replica setup for read scaling
- Writes go to master, reads can go to replicas

**Indexing Strategy:**
- Composite index on `(event_id, section, row, number)` for seat lookups
- Index on `status` for filtering available seats
- Index on `reserved_until` for cleanup of expired reservations
- Index on `order_id` for order queries

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
│         CDN (Static Content: Images, Seat Maps)     │
└──────────────────────────────────────────────────────┘
       │
       │
┌──────▼──────────────────────────────────────────────┐
│        API Gateway / Load Balancer                   │
│        - Rate Limiting                               │
│        - Request Routing                             │
│        - Queue Management (for high-demand events)   │
└──────┬──────────────────────────────────────────────┘
       │
       ├──────────────┬──────────────┬──────────────┐
       │              │              │              │
┌──────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
│   Event     │ │   Seat     │ │  Order     │ │ Payment   │
│   Service   │ │   Service  │ │  Service  │ │  Service  │
└──────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
       │              │              │              │
       │              │              │              │
┌──────▼──────────────▼──────────────▼──────────────▼──────┐
│              Message Queue (Kafka)                        │
│              - Seat status updates                         │
│              - Order events                                │
└───────────────────────────────────────────────────────────┘
       │
       │
┌──────▼─────────────────────────────────────────────────────┐
│         Database Cluster (Sharded)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Shard 0   │  │ Shard 1   │  │ Shard N   │              │
│  │ Seats     │  │ Seats     │  │ Seats     │              │
│  └──────────┘  └──────────┘  └──────────┘              │
│                                                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Events   │  │ Orders   │  │ Users    │              │
│  │ DB       │  │ DB       │  │ DB       │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└───────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Cache Layer (Redis)                             │
│  - Event details                                            │
│  - Seat availability (with TTL)                             │
│  - Reservation locks                                        │
│  - Rate limiting counters                                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│         Distributed Lock Service (Redis/Zookeeper)          │
│         - Seat reservation locks                            │
│         - Prevent concurrent seat booking                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│         External Services                                    │
│  - Payment Gateway (Stripe, PayPal)                         │
│  - Email Service (SendGrid, SES)                             │
│  - SMS Service (Twilio)                                      │
└─────────────────────────────────────────────────────────────┘
```

## Deep Dive

### Component Design

#### 1. Event Service

**Responsibilities:**
- Manage event CRUD operations
- Event search and filtering
- Event status management
- Cache event data

**Key Design Decisions:**
- **Caching**: Cache event details in Redis with 5-minute TTL
- **Search**: Use Elasticsearch for event search
- **Status Updates**: Publish status changes to message queue

**Scalability:**
- Stateless service, horizontally scalable
- Read replicas for read-heavy workloads
- Connection pooling for database access

#### 2. Seat Service

**Responsibilities:**
- Manage seat availability
- Handle seat reservations
- Provide seat map data
- Prevent overselling

**Key Design Decisions:**
- **Distributed Locks**: Use Redis/Zookeeper for seat reservation locks
- **Optimistic Locking**: Use database version numbers for concurrent updates
- **Reservation Expiry**: Background job to release expired reservations
- **Availability Cache**: Cache seat availability with short TTL (5 seconds)

**Critical Requirements:**
- **No Overselling**: Must guarantee seats are not double-booked
- **Strong Consistency**: Seat status must be consistent across all requests
- **Fast Response**: Seat availability checks must be fast (< 500ms)

**Scalability:**
- Sharded database by event_id
- Connection pooling
- Caching for frequently accessed events

#### 3. Reservation Service

**Responsibilities:**
- Create seat reservations
- Manage reservation expiration
- Release expired reservations
- Convert reservations to orders

**Key Design Decisions:**
- **Reservation Duration**: 5-10 minutes hold time
- **Expiration Cleanup**: Background job runs every minute
- **Lock Management**: Acquire locks before creating reservations
- **Idempotency**: Prevent duplicate reservations

**Implementation:**
```python
def create_reservation(event_id, user_id, seat_ids, hold_duration=600):
    # Acquire distributed locks on all seats
    locks = []
    try:
        for seat_id in seat_ids:
            lock = acquire_lock(f"seat:{seat_id}", timeout=5)
            if not lock:
                raise Exception(f"Could not acquire lock for seat {seat_id}")
            locks.append(lock)
        
        # Check all seats are available
        seats = get_seats(seat_ids)
        for seat in seats:
            if seat.status != 'available':
                raise Exception(f"Seat {seat.seat_id} is not available")
        
        # Create reservation
        reservation = Reservation(
            user_id=user_id,
            event_id=event_id,
            seat_ids=seat_ids,
            expires_at=now() + timedelta(seconds=hold_duration)
        )
        reservation.save()
        
        # Update seat status to reserved
        update_seats_status(seat_ids, 'reserved', reservation.id)
        
        return reservation
    finally:
        # Release all locks
        for lock in locks:
            release_lock(lock)
```

#### 4. Order Service

**Responsibilities:**
- Create orders from reservations
- Process payments
- Generate tickets
- Manage order lifecycle

**Key Design Decisions:**
- **Transaction Management**: Use database transactions for order creation
- **Payment Integration**: Async payment processing with retries
- **Ticket Generation**: Generate QR codes for tickets
- **Order Confirmation**: Send confirmation emails

**Scalability:**
- Stateless service, horizontally scalable
- Async processing for non-critical operations
- Message queue for order events

#### 5. Payment Service

**Responsibilities:**
- Process payments via payment gateway
- Handle payment callbacks
- Manage refunds
- Payment status tracking

**Key Design Decisions:**
- **Idempotency**: Use idempotency keys for payment requests
- **Retry Logic**: Retry failed payments with exponential backoff
- **Webhook Handling**: Process payment gateway webhooks
- **Security**: Never store full credit card numbers

**Scalability:**
- Stateless service, horizontally scalable
- Async processing for payment callbacks
- Rate limiting for payment gateway

### Detailed Design

#### Preventing Overselling

**Challenge:** Multiple users trying to book the same seat simultaneously

**Solution 1: Distributed Locks**
- Acquire distributed lock before checking/updating seat status
- Use Redis or Zookeeper for distributed locking
- Lock timeout prevents deadlocks
- Ensures only one user can reserve a seat at a time

**Solution 2: Database Transactions with Row Locking**
- Use `SELECT FOR UPDATE` to lock rows during transaction
- Check availability within transaction
- Update seat status atomically
- Rollback if seat not available

**Solution 3: Optimistic Locking**
- Use version numbers on seat records
- Check version before update
- Retry if version changed (another user booked)

**Implementation:**
```python
def reserve_seat(event_id, seat_id, user_id):
    with database.transaction():
        # Lock seat row
        seat = Seat.objects.select_for_update().get(
            event_id=event_id,
            seat_id=seat_id,
            status='available'
        )
        
        # Update seat status
        seat.status = 'reserved'
        seat.reserved_by = user_id
        seat.reserved_until = now() + timedelta(minutes=10)
        seat.save()
        
        # Create reservation
        reservation = Reservation(
            event_id=event_id,
            seat_id=seat_id,
            user_id=user_id,
            expires_at=seat.reserved_until
        )
        reservation.save()
        
        return reservation
```

#### Queue System for High-Demand Events

**Challenge:** Handle 10M concurrent users for popular events

**Solution:**
- **Virtual Queue**: Users enter virtual queue when event goes on sale
- **Fair Access**: Randomize queue position to prevent bot advantage
- **Progressive Admission**: Admit users in batches (e.g., 10K at a time)
- **Status Updates**: Show queue position and estimated wait time

**Implementation:**
```python
def join_event_queue(event_id, user_id):
    # Add user to queue
    queue_position = redis.zadd(
        f"event_queue:{event_id}",
        {user_id: time.time()}
    )
    
    # Get total queue size
    queue_size = redis.zcard(f"event_queue:{event_id}")
    
    # Calculate estimated wait time
    admission_rate = 10000  # users per minute
    wait_time_minutes = queue_position / admission_rate
    
    return {
        "queue_position": queue_position,
        "queue_size": queue_size,
        "estimated_wait_time": wait_time_minutes
    }

def process_queue(event_id, batch_size=10000):
    # Get next batch of users
    user_ids = redis.zrange(
        f"event_queue:{event_id}",
        0,
        batch_size - 1
    )
    
    # Remove from queue
    redis.zrem(f"event_queue:{event_id}", *user_ids)
    
    # Notify users they can proceed
    for user_id in user_ids:
        send_notification(user_id, "You can now access the event!")
```

#### Seat Map Caching

**Challenge:** Serve seat maps efficiently to millions of users

**Solution:**
- **CDN**: Serve static seat map images via CDN
- **Availability Cache**: Cache seat availability in Redis with short TTL
- **Incremental Updates**: Push only changed seat statuses via WebSocket
- **Compression**: Compress seat map data

**Implementation:**
```python
def get_seat_map(event_id):
    # Try cache first
    cache_key = f"seat_map:{event_id}"
    cached_map = redis.get(cache_key)
    
    if cached_map:
        return json.loads(cached_map)
    
    # Load from database
    seats = Seat.objects.filter(event_id=event_id).values(
        'seat_id', 'section', 'row', 'number', 'status', 'price'
    )
    
    # Build seat map structure
    seat_map = build_seat_map_structure(seats)
    
    # Cache for 5 seconds
    redis.setex(cache_key, 5, json.dumps(seat_map))
    
    return seat_map
```

#### Reservation Expiration Cleanup

**Challenge:** Release expired reservations automatically

**Solution:**
- **Background Job**: Run cleanup job every minute
- **Database Query**: Find reservations expiring in next minute
- **Batch Processing**: Process in batches to avoid overload
- **Seat Release**: Update seat status back to available

**Implementation:**
```python
def cleanup_expired_reservations():
    # Find reservations expiring in next minute
    now = datetime.now()
    next_minute = now + timedelta(minutes=1)
    
    expired_reservations = Reservation.objects.filter(
        status='active',
        expires_at__lte=next_minute
    )[:1000]  # Process in batches
    
    for reservation in expired_reservations:
        # Release seats
        Seat.objects.filter(
            seat_id__in=reservation.seat_ids
        ).update(
            status='available',
            reserved_by=None,
            reserved_until=None
        )
        
        # Mark reservation as expired
        reservation.status = 'expired'
        reservation.save()
        
        # Publish event for real-time updates
        publish_seat_status_update(reservation.event_id, reservation.seat_ids)
```

### Scalability Considerations

#### Horizontal Scaling

**API Services:**
- Stateless services, scale horizontally
- Load balancer distributes requests
- Auto-scaling based on CPU/memory metrics

**Database:**
- Shard seats table by event_id
- Read replicas for read scaling
- Connection pooling

**Cache:**
- Redis cluster for high availability
- Shard cache by event_id
- Cache warming before high-demand events

#### Caching Strategy

**Redis Cache:**
- **Event Details**: TTL 5 minutes
- **Seat Availability**: TTL 5 seconds (short for accuracy)
- **Seat Maps**: TTL 1 minute
- **User Sessions**: TTL 30 minutes
- **Rate Limiting**: Per-user counters with TTL

**Cache Invalidation:**
- Invalidate on seat status changes
- Invalidate on event updates
- Use cache-aside pattern

#### Load Balancing

**Traffic Distribution:**
- Round-robin or least-connections
- Health checks for backend services
- Circuit breakers for failing services

**High-Demand Events:**
- Dedicated server pool for popular events
- Queue system to throttle traffic
- Progressive admission

#### Database Optimization

**Indexing:**
- Index on (event_id, status) for seat queries
- Index on expires_at for reservation cleanup
- Index on user_id for order queries
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
- **Bot Prevention**: CAPTCHA for high-risk operations
- **Permission Checks**: Verify user owns reservation before checkout

#### Payment Security

- **PCI Compliance**: Never store full credit card numbers
- **Tokenization**: Use payment gateway tokens
- **Encryption**: Encrypt sensitive data in transit and at rest
- **Fraud Detection**: Monitor for suspicious patterns

#### Data Protection

- **Input Validation**: Validate all inputs
- **SQL Injection Prevention**: Use parameterized queries
- **XSS Prevention**: Sanitize user inputs
- **CSRF Protection**: Use CSRF tokens

### Monitoring & Observability

#### Key Metrics

**System Metrics:**
- Request rate (requests/second)
- Response latency (p50, p95, p99)
- Error rate
- Database query latency
- Cache hit rate
- Queue length

**Business Metrics:**
- Events on sale
- Tickets sold per event
- Revenue per event
- Conversion rate (reservations to orders)
- Average order value
- Failed payments

#### Logging

- **Structured Logging**: JSON logs for easy parsing
- **Request Tracing**: Trace requests across services
- **Error Logging**: Log errors with context
- **Audit Logging**: Log important actions (orders, payments)

#### Alerting

- **High Error Rate**: Alert if error rate > 1%
- **High Latency**: Alert if p95 latency > 2 seconds
- **Database Issues**: Alert on database errors
- **Payment Failures**: Alert on payment gateway errors
- **Overselling Risk**: Alert if available seats < 0

### Trade-offs and Optimizations

#### Trade-offs

**1. Strong Consistency vs Availability**
- **Strong Consistency**: Required for seat availability (no overselling)
- **Availability**: Can sacrifice for critical operations
- **Decision**: Use strong consistency for seat booking, eventual consistency for other features

**2. Reservation Duration: Short vs Long**
- **Short (5 min)**: More seats available, but users may not complete checkout
- **Long (15 min)**: Better user experience, but seats locked longer
- **Decision**: 10 minutes balance, with option to extend

**3. Real-Time Updates: WebSocket vs Polling**
- **WebSocket**: Lower latency, but more complex
- **Polling**: Simpler, but higher latency and server load
- **Decision**: WebSocket for seat status, polling fallback

**4. Seat Map: Pre-rendered vs Dynamic**
- **Pre-rendered**: Faster, but less flexible
- **Dynamic**: More flexible, but slower
- **Decision**: Pre-rendered images with dynamic status overlay

#### Optimizations

**1. Database Connection Pooling**
- Reuse database connections
- Reduce connection overhead
- Improve performance

**2. Batch Operations**
- Batch seat status updates
- Batch reservation cleanup
- Reduce database round trips

**3. Read Replicas**
- Use read replicas for read-heavy queries
- Reduce load on primary database
- Improve read performance

**4. CDN for Static Content**
- Serve seat maps via CDN
- Reduce server load
- Improve delivery speed

**5. Compression**
- Compress API responses
- Reduce bandwidth usage
- Improve performance

## What Interviewers Look For

### Concurrency Control Skills

1. **Double-Booking Prevention**
   - Distributed locks for seat reservation
   - Database transactions with row locking
   - Atomic seat reservation operations
   - **Red Flags**: No locking, race conditions, overselling possible

2. **Seat Reservation Logic**
   - Time-limited reservations
   - Automatic cleanup of expired reservations
   - **Red Flags**: No expiration, permanent reservations, no cleanup

3. **Transaction Design**
   - ACID properties for bookings
   - Rollback on failures
   - **Red Flags**: Non-atomic operations, partial updates

### Distributed Systems Skills

1. **Queue System Design**
   - Virtual queue for high-demand events
   - Fair access mechanism
   - **Red Flags**: No queue, first-come-first-served only, unfair access

2. **Real-Time Updates**
   - WebSocket for seat status
   - Efficient broadcasting
   - **Red Flags**: Polling, high latency, no real-time

3. **Scalability Design**
   - Horizontal scaling
   - Database sharding
   - Caching strategy
   - **Red Flags**: Vertical scaling, no sharding, no caching

### Problem-Solving Approach

1. **High-Demand Events**
   - Queue system design
   - Load distribution
   - **Red Flags**: No special handling, system overload

2. **Edge Cases**
   - Concurrent bookings
   - Payment failures
   - Reservation expiration
   - **Red Flags**: Ignoring edge cases, no handling

3. **Trade-off Analysis**
   - Consistency vs availability
   - Performance vs accuracy
   - **Red Flags**: No trade-offs, dogmatic choices

### System Design Skills

1. **Component Design**
   - Seat reservation service
   - Payment service
   - Queue service
   - **Red Flags**: Monolithic, unclear boundaries

2. **Payment Processing**
   - Idempotency
   - Retry logic
   - Failure handling
   - **Red Flags**: No idempotency, no retry, payment loss

3. **Database Design**
   - Proper indexing
   - Sharding strategy
   - **Red Flags**: Missing indexes, no sharding

### Communication Skills

1. **Concurrency Explanation**
   - Can explain locking mechanisms
   - Understands transactions
   - **Red Flags**: No understanding, vague explanations

2. **Architecture Justification**
   - Explains design decisions
   - Discusses alternatives
   - **Red Flags**: No justification, no alternatives

### Meta-Specific Focus

1. **Concurrency Mastery**
   - Deep understanding of locking
   - Transaction design
   - **Key**: Show concurrency expertise

2. **Correctness Over Scale**
   - Emphasis on correctness
   - No overselling guarantee
   - **Key**: Demonstrate reliability focus

## Summary

Designing Ticketmaster at scale requires careful consideration of:

1. **Concurrency Control**: Distributed locks and database transactions prevent overselling
2. **Seat Reservation**: Time-limited reservations with automatic cleanup
3. **Scalability**: Horizontal scaling with sharding and caching
4. **Queue System**: Virtual queue for high-demand events ensures fair access
5. **Payment Processing**: Reliable payment processing with retry logic
6. **Real-Time Updates**: WebSocket for seat status updates
7. **Strong Consistency**: Critical for seat availability to prevent overselling
8. **Performance**: Fast response times even under high load

Key architectural decisions:
- **Distributed Locks** for seat reservation
- **Database Transactions** with row locking
- **Sharded Database** for seat storage
- **Redis Cache** for availability and reservations
- **Message Queue** for event distribution
- **Queue System** for high-demand events
- **Horizontal Scaling** for all services

The system handles 10 million concurrent users during peak sales with guaranteed seat availability and no overselling.

