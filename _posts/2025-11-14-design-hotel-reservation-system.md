---
layout: post
title: "Design a Hotel Reservation System - System Design Interview"
date: 2025-11-14
categories: [System Design, Interview Example, Distributed Systems, E-commerce]
excerpt: "A comprehensive guide to designing a hotel reservation system like Booking.com or Expedia, covering hotel search, room availability, booking management, dynamic pricing, payment processing, and architectural patterns for handling millions of bookings per day across thousands of hotels."
---

## Introduction

A hotel reservation system enables users to search for hotels, check room availability, make bookings, and manage reservations. Systems like Booking.com and Expedia handle millions of bookings per day across thousands of hotels worldwide, requiring efficient search, real-time availability, dynamic pricing, and reliable booking processing.

This post provides a detailed walkthrough of designing a scalable hotel reservation system, covering key architectural decisions, inventory management, date range queries, pricing strategies, and scalability challenges. This is a common system design interview question that tests your understanding of distributed systems, database design for time-series data, search optimization, and handling concurrent bookings.

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

**Design a hotel reservation system similar to Booking.com or Expedia with the following features:**

1. Hotel search by location, date range, price range
2. Room availability checking for date ranges
3. Room type selection (single, double, suite, etc.)
4. Booking creation with guest information
5. Payment processing
6. Booking confirmation and management
7. Cancellation and refunds
8. Reviews and ratings
9. Price comparison across hotels
10. Multi-room bookings

**Scale Requirements:**
- 100,000+ hotels worldwide
- 10 million+ rooms total
- 50 million+ users
- 1 million+ bookings per day
- Peak traffic: 100,000 concurrent users
- Average booking: 2-3 nights
- Search queries: 10 million per day
- Must prevent overbooking (critical requirement)

## Requirements

### Functional Requirements

**Core Features:**
1. **Hotel Management**: Hotel CRUD, room types, amenities, location
2. **Search**: Search hotels by location, date range, price, amenities, ratings
3. **Availability**: Check room availability for specific date ranges
4. **Booking**: Create bookings with guest details, payment, confirmation
5. **Pricing**: Dynamic pricing based on demand, season, day of week
6. **Inventory Management**: Track available rooms per day
7. **Booking Management**: View, modify, cancel bookings
8. **Payment Processing**: Accept payments, handle refunds
9. **Reviews**: Users can leave reviews and ratings
10. **Notifications**: Email/SMS confirmations and reminders
11. **Multi-room**: Book multiple rooms in same hotel
12. **Guest Management**: Store guest information, booking history

**Out of Scope:**
- Hotel management portal (focus on booking platform)
- Loyalty programs
- Advanced analytics
- Mobile app (focus on web)
- Internationalization (single currency/language)

### Non-Functional Requirements

1. **Availability**: 99.9% uptime
2. **Reliability**: No overbooking, guaranteed booking confirmation
3. **Performance**: 
   - Search response time: < 2 seconds
   - Availability check: < 500ms
   - Booking completion: < 5 seconds
   - Payment processing: < 10 seconds
4. **Scalability**: Handle 1M+ bookings per day
5. **Consistency**: Strong consistency for availability (critical)
6. **Durability**: All bookings must be persisted reliably
7. **Accuracy**: Real-time availability must be accurate

## Capacity Estimation

### Traffic Estimates

- **Total Users**: 50 million
- **Daily Active Users (DAU)**: 5 million
- **Search Queries per Day**: 10 million
- **Bookings per Day**: 1 million
- **Average Booking Duration**: 2.5 nights
- **Peak Concurrent Users**: 100,000
- **Peak QPS**: 10,000 requests/second
- **Normal QPS**: 1,000 requests/second
- **Read:Write ratio**: 10:1 (searches vs bookings)

### Storage Estimates

**Hotel Data:**
- 100,000 hotels × 5KB = 500MB
- Room types: 1M room types × 1KB = 1GB
- Amenities: 100K hotels × 2KB = 200MB
- Total hotel data: ~1.7GB

**Availability Data:**
- 100K hotels × 365 days × 10 rooms average = 365M availability records/year
- Each record: 100 bytes = 36.5GB/year
- 5-year retention: ~180GB

**Booking Data:**
- 1M bookings/day × 365 days = 365M bookings/year
- Average booking: 2KB = 730GB/year
- 5-year retention: ~3.6TB

**User Data:**
- 50M users × 1KB = 50GB

**Reviews:**
- 100M reviews × 500 bytes = 50GB

**Total Storage**: ~4TB (excluding images/media)

### Bandwidth Estimates

**Normal Traffic:**
- 1,000 QPS × 20KB average response = 20MB/s = 160Mbps

**Peak Traffic:**
- 10,000 QPS × 20KB = 200MB/s = 1.6Gbps
- Hotel images: 10K QPS × 500KB = 5GB/s = 40Gbps
- **Total Peak**: ~42Gbps

## Core Entities

### Hotel
- `hotel_id` (UUID)
- `name`
- `description`
- `address`
- `city`
- `state`
- `country`
- `latitude`
- `longitude`
- `star_rating`
- `amenities` (JSON array)
- `images` (JSON array of URLs)
- `check_in_time`
- `check_out_time`
- `created_at`
- `updated_at`

### Room Type
- `room_type_id` (UUID)
- `hotel_id`
- `name` (e.g., "Deluxe King Room")
- `description`
- `max_occupancy`
- `bed_type`
- `size_sqm`
- `amenities` (JSON array)
- `base_price`
- `images` (JSON array)
- `created_at`

### Room
- `room_id` (UUID)
- `hotel_id`
- `room_type_id`
- `room_number`
- `floor`
- `status` (available, occupied, maintenance)
- `created_at`

### Availability
- `availability_id` (UUID)
- `hotel_id`
- `room_type_id`
- `date` (DATE)
- `available_rooms` (INT)
- `total_rooms` (INT)
- `price` (DECIMAL)
- `updated_at`

### Booking
- `booking_id` (UUID)
- `user_id`
- `hotel_id`
- `check_in_date` (DATE)
- `check_out_date` (DATE)
- `status` (pending, confirmed, cancelled, completed)
- `total_amount` (DECIMAL)
- `currency`
- `payment_status` (pending, completed, refunded)
- `payment_method`
- `payment_transaction_id`
- `guest_count`
- `created_at`
- `confirmed_at`
- `cancelled_at`

### Booking Room
- `booking_room_id` (UUID)
- `booking_id`
- `room_id`
- `room_type_id`
- `price`
- `check_in_date`
- `check_out_date`

### User
- `user_id` (UUID)
- `email`
- `username`
- `password_hash`
- `phone_number`
- `first_name`
- `last_name`
- `created_at`
- `updated_at`

### Review
- `review_id` (UUID)
- `hotel_id`
- `user_id`
- `booking_id`
- `rating` (1-5)
- `comment` (TEXT)
- `created_at`

## API

### 1. Search Hotels
```
GET /api/v1/hotels/search?location=NYC&check_in=2025-12-01&check_out=2025-12-03&guests=2&price_min=100&price_max=500&limit=20&offset=0
Response:
{
  "hotels": [
    {
      "hotel_id": "uuid",
      "name": "Grand Hotel",
      "location": "New York, NY",
      "star_rating": 4,
      "price_per_night": 250.00,
      "available_rooms": 5,
      "images": ["url1", "url2"],
      "amenities": ["WiFi", "Pool", "Gym"],
      "rating": 4.5,
      "review_count": 1250
    }
  ],
  "total": 150,
  "limit": 20,
  "offset": 0
}
```

### 2. Get Hotel Details
```
GET /api/v1/hotels/{hotel_id}?check_in=2025-12-01&check_out=2025-12-03&guests=2
Response:
{
  "hotel_id": "uuid",
  "name": "Grand Hotel",
  "description": "...",
  "location": {...},
  "amenities": [...],
  "images": [...],
  "room_types": [
    {
      "room_type_id": "uuid",
      "name": "Deluxe King Room",
      "max_occupancy": 2,
      "price_per_night": 250.00,
      "available_rooms": 5,
      "images": [...]
    }
  ],
  "rating": 4.5,
  "review_count": 1250
}
```

### 3. Check Availability
```
POST /api/v1/hotels/{hotel_id}/availability
Request:
{
  "check_in": "2025-12-01",
  "check_out": "2025-12-03",
  "guests": 2,
  "room_type_id": "uuid"  // optional
}

Response:
{
  "hotel_id": "uuid",
  "check_in": "2025-12-01",
  "check_out": "2025-12-03",
  "available_room_types": [
    {
      "room_type_id": "uuid",
      "name": "Deluxe King Room",
      "available_rooms": 5,
      "price_per_night": 250.00,
      "total_price": 500.00
    }
  ]
}
```

### 4. Create Booking
```
POST /api/v1/bookings
Request:
{
  "hotel_id": "uuid",
  "room_type_id": "uuid",
  "check_in": "2025-12-01",
  "check_out": "2025-12-03",
  "guests": 2,
  "guest_info": {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "+1234567890"
  },
  "payment_method": "credit_card",
  "payment_details": {
    "card_number": "****",
    "expiry": "12/25",
    "cvv": "***"
  }
}

Response:
{
  "booking_id": "uuid",
  "status": "confirmed",
  "hotel": {...},
  "check_in": "2025-12-01",
  "check_out": "2025-12-03",
  "total_amount": 500.00,
  "confirmation_number": "ABC123XYZ",
  "created_at": "2025-11-13T10:00:00Z"
}
```

### 5. Get Booking
```
GET /api/v1/bookings/{booking_id}
Response:
{
  "booking_id": "uuid",
  "status": "confirmed",
  "hotel": {...},
  "check_in": "2025-12-01",
  "check_out": "2025-12-03",
  "rooms": [...],
  "total_amount": 500.00,
  "confirmation_number": "ABC123XYZ",
  "guest_info": {...},
  "created_at": "2025-11-13T10:00:00Z"
}
```

### 6. Cancel Booking
```
POST /api/v1/bookings/{booking_id}/cancel
Request:
{
  "reason": "Change of plans"
}

Response:
{
  "booking_id": "uuid",
  "status": "cancelled",
  "refund_amount": 500.00,
  "refund_status": "processing"
}
```

### 7. Get User Bookings
```
GET /api/v1/users/{user_id}/bookings?status=confirmed&limit=20&offset=0
Response:
{
  "bookings": [
    {
      "booking_id": "uuid",
      "hotel": {...},
      "check_in": "2025-12-01",
      "check_out": "2025-12-03",
      "status": "confirmed",
      "total_amount": 500.00
    }
  ],
  "total": 50,
  "limit": 20,
  "offset": 0
}
```

### 8. Create Review
```
POST /api/v1/hotels/{hotel_id}/reviews
Request:
{
  "booking_id": "uuid",
  "rating": 5,
  "comment": "Great hotel, excellent service!"
}

Response:
{
  "review_id": "uuid",
  "hotel_id": "uuid",
  "user_id": "uuid",
  "rating": 5,
  "comment": "Great hotel, excellent service!",
  "created_at": "2025-11-13T10:00:00Z"
}
```

## Data Flow

### Hotel Search Flow

1. **User Searches**:
   - User enters search criteria (location, dates, guests)
   - **Client** sends search request to **API Gateway**
   - **API Gateway** routes to **Search Service**

2. **Search Processing**:
   - **Search Service**:
     - Validates search parameters
     - Queries **Elasticsearch** for hotels matching location
     - For each hotel, checks availability via **Availability Service**
     - Filters by price range, amenities, ratings
     - Ranks results by relevance/rating/price
   - Returns search results with availability and pricing

3. **Availability Check**:
   - **Availability Service** queries **Availability DB** for date range
   - Checks if `available_rooms > 0` for each day in range
   - Calculates total price for stay
   - Returns availability status

### Booking Flow

1. **User Selects Hotel and Room**:
   - User views hotel details and selects room type
   - **Client** calls availability check API
   - **Availability Service** confirms availability

2. **Booking Creation**:
   - User fills guest information and payment details
   - **Client** sends booking request to **Booking Service**
   - **Booking Service**:
     - Validates availability again (double-check)
     - Acquires distributed lock on hotel/room_type/date range
     - Creates booking record with status "pending"
     - Reserves rooms in **Availability DB**
     - Releases lock

3. **Payment Processing**:
   - **Booking Service** calls **Payment Service**
   - **Payment Service**:
     - Processes payment via payment gateway
     - Updates payment status
     - Sends webhook callback
   - On success: **Booking Service** updates booking status to "confirmed"
   - On failure: **Booking Service** releases rooms, updates status to "cancelled"

4. **Confirmation**:
   - **Booking Service** generates confirmation number
   - Sends confirmation email via **Notification Service**
   - Returns booking confirmation to client

### Cancellation Flow

1. **User Cancels Booking**:
   - User requests cancellation
   - **Client** sends cancellation request
   - **Booking Service** validates cancellation policy

2. **Cancellation Processing**:
   - **Booking Service**:
     - Updates booking status to "cancelled"
     - Releases rooms in **Availability DB**
     - Calculates refund amount based on policy
     - Initiates refund via **Payment Service**

3. **Refund Processing**:
   - **Payment Service** processes refund
   - Updates payment status
   - Sends refund confirmation

## Database Design

### Schema Design

**Hotels Table:**
```sql
CREATE TABLE hotels (
    hotel_id UUID PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    address VARCHAR(500),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    star_rating INT,
    amenities JSON,
    images JSON,
    check_in_time TIME DEFAULT '15:00:00',
    check_out_time TIME DEFAULT '11:00:00',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_location (city, state, country),
    INDEX idx_coordinates (latitude, longitude),
    INDEX idx_star_rating (star_rating)
);
```

**Room Types Table:**
```sql
CREATE TABLE room_types (
    room_type_id UUID PRIMARY KEY,
    hotel_id UUID NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    max_occupancy INT NOT NULL,
    bed_type VARCHAR(50),
    size_sqm DECIMAL(5, 2),
    amenities JSON,
    base_price DECIMAL(10, 2),
    images JSON,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_hotel_id (hotel_id)
);
```

**Rooms Table:**
```sql
CREATE TABLE rooms (
    room_id UUID PRIMARY KEY,
    hotel_id UUID NOT NULL,
    room_type_id UUID NOT NULL,
    room_number VARCHAR(20),
    floor INT,
    status ENUM('available', 'occupied', 'maintenance') DEFAULT 'available',
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_hotel_room_type (hotel_id, room_type_id),
    INDEX idx_status (status)
);
```

**Availability Table (Sharded by hotel_id):**
```sql
CREATE TABLE availability_0 (
    availability_id UUID PRIMARY KEY,
    hotel_id UUID NOT NULL,
    room_type_id UUID NOT NULL,
    date DATE NOT NULL,
    available_rooms INT NOT NULL DEFAULT 0,
    total_rooms INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE KEY uk_hotel_room_date (hotel_id, room_type_id, date),
    INDEX idx_date (date),
    INDEX idx_hotel_date (hotel_id, date),
    INDEX idx_available_rooms (available_rooms)
);
-- Similar tables: availability_1, availability_2, ..., availability_N
```

**Bookings Table:**
```sql
CREATE TABLE bookings (
    booking_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    hotel_id UUID NOT NULL,
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    status ENUM('pending', 'confirmed', 'cancelled', 'completed') DEFAULT 'pending',
    total_amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payment_status ENUM('pending', 'completed', 'refunded') DEFAULT 'pending',
    payment_method VARCHAR(50),
    payment_transaction_id VARCHAR(200),
    guest_count INT NOT NULL,
    confirmation_number VARCHAR(20) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    confirmed_at TIMESTAMP NULL,
    cancelled_at TIMESTAMP NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_hotel_id (hotel_id),
    INDEX idx_check_in_date (check_in_date),
    INDEX idx_status (status),
    INDEX idx_confirmation_number (confirmation_number)
);
```

**Booking Rooms Table:**
```sql
CREATE TABLE booking_rooms (
    booking_room_id UUID PRIMARY KEY,
    booking_id UUID NOT NULL,
    room_id UUID NOT NULL,
    room_type_id UUID NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    INDEX idx_booking_id (booking_id),
    INDEX idx_room_id (room_id),
    INDEX idx_dates (check_in_date, check_out_date)
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
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_email (email)
);
```

**Reviews Table:**
```sql
CREATE TABLE reviews (
    review_id UUID PRIMARY KEY,
    hotel_id UUID NOT NULL,
    user_id UUID NOT NULL,
    booking_id UUID NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_hotel_id (hotel_id),
    INDEX idx_user_id (user_id),
    INDEX idx_rating (rating),
    INDEX idx_created_at (created_at DESC)
);
```

### Database Sharding Strategy

**Availability Table Sharding:**
- Shard by `hotel_id` using consistent hashing
- 1000 shards: `shard_id = hash(hotel_id) % 1000`
- Each shard handles availability for multiple hotels
- Enables parallel processing and horizontal scaling

**Shard Key Selection:**
- `hotel_id` ensures all availability records for a hotel are in the same shard
- Enables efficient queries for hotel availability
- Prevents cross-shard queries for single hotel

**Replication:**
- Each shard replicated 3x for high availability
- Master-replica setup for read scaling
- Writes go to master, reads can go to replicas

**Indexing Strategy:**
- Unique index on `(hotel_id, room_type_id, date)` prevents duplicates
- Index on `date` for date range queries
- Index on `available_rooms` for filtering available rooms
- Composite index on `(hotel_id, date)` for hotel-specific queries

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
│   Search    │ │Availability│ │  Booking   │ │  Payment   │ │  Review   │
│   Service   │ │  Service   │ │  Service   │ │  Service   │ │  Service  │
└──────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
       │              │              │              │              │
       │              │              │              │              │
┌──────▼──────────────▼──────────────▼──────────────▼──────────────▼──────┐
│              Message Queue (Kafka)                                        │
│              - Booking events                                            │
│              - Availability updates                                       │
│              - Notification events                                        │
└───────────────────────────────────────────────────────────────────────────┘
       │
       │
┌──────▼───────────────────────────────────────────────────────────────────┐
│         Database Cluster (Sharded)                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                              │
│  │ Shard 0   │  │ Shard 1   │  │ Shard N   │                              │
│  │Availability│ │Availability│ │Availability│                              │
│  └──────────┘  └──────────┘  └──────────┘                              │
│                                                                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Hotels   │  │ Bookings │  │  Users    │  │  Reviews  │              │
│  │ DB       │  │ DB       │  │ DB       │  │ DB       │              │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘              │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│              Cache Layer (Redis)                                          │
│  - Hotel details                                                          │
│  - Availability cache (with TTL)                                          │
│  - Search results cache                                                   │
│  - Distributed locks                                                      │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│         Search Engine (Elasticsearch)                                       │
│         - Hotel search by location, amenities, ratings                    │
│         - Full-text search                                                 │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│         External Services                                                  │
│  - Payment Gateway (Stripe, PayPal)                                       │
│  - Email Service (SendGrid, SES)                                          │
│  - SMS Service (Twilio)                                                   │
└───────────────────────────────────────────────────────────────────────────┘
```

## Deep Dive

### Component Design

#### 1. Search Service

**Responsibilities:**
- Process hotel search queries
- Integrate with Elasticsearch for location-based search
- Filter by availability, price, amenities
- Rank and sort results

**Key Design Decisions:**
- **Elasticsearch**: Use for location and full-text search
- **Caching**: Cache popular search results
- **Filtering**: Apply filters after Elasticsearch results
- **Ranking**: Rank by relevance, rating, price

**Scalability:**
- Stateless service, horizontally scalable
- Elasticsearch cluster for search
- Cache frequently searched locations

#### 2. Availability Service

**Responsibilities:**
- Check room availability for date ranges
- Update availability when bookings are made/cancelled
- Calculate pricing for date ranges
- Prevent overbooking

**Key Design Decisions:**
- **Date Range Queries**: Efficient queries for date ranges
- **Atomic Updates**: Use transactions for availability updates
- **Caching**: Cache availability with short TTL (30 seconds)
- **Locking**: Distributed locks for concurrent bookings

**Critical Requirements:**
- **No Overbooking**: Must guarantee rooms are not double-booked
- **Strong Consistency**: Availability must be accurate
- **Fast Response**: Availability checks must be fast (< 500ms)

**Scalability:**
- Sharded database by hotel_id
- Connection pooling
- Caching for frequently accessed hotels

#### 3. Booking Service

**Responsibilities:**
- Create bookings
- Manage booking lifecycle
- Process cancellations
- Generate confirmations

**Key Design Decisions:**
- **Transaction Management**: Use database transactions for booking creation
- **Idempotency**: Use idempotency keys for booking requests
- **Reservation**: Reserve rooms before payment
- **Confirmation**: Generate unique confirmation numbers

**Implementation:**
```python
def create_booking(hotel_id, room_type_id, check_in, check_out, guest_info, payment_details):
    # Acquire distributed lock
    lock_key = f"booking:{hotel_id}:{room_type_id}:{check_in}:{check_out}"
    lock = acquire_lock(lock_key, timeout=10)
    
    try:
        with database.transaction():
            # Check availability for date range
            availability = check_availability(hotel_id, room_type_id, check_in, check_out)
            if not availability['available']:
                raise Exception("Rooms not available")
            
            # Calculate total price
            total_price = calculate_price(hotel_id, room_type_id, check_in, check_out)
            
            # Create booking
            booking = Booking(
                hotel_id=hotel_id,
                check_in_date=check_in,
                check_out_date=check_out,
                status='pending',
                total_amount=total_price,
                guest_info=guest_info
            )
            booking.save()
            
            # Reserve rooms (update availability)
            reserve_rooms(hotel_id, room_type_id, check_in, check_out, booking.id)
            
            # Process payment
            payment_result = process_payment(total_price, payment_details)
            
            if payment_result['success']:
                booking.status = 'confirmed'
                booking.confirmation_number = generate_confirmation_number()
                booking.save()
                
                # Send confirmation email
                send_confirmation_email(booking)
            else:
                # Release rooms
                release_rooms(hotel_id, room_type_id, check_in, check_out)
                booking.status = 'cancelled'
                booking.save()
                raise Exception("Payment failed")
            
            return booking
    finally:
        release_lock(lock)
```

#### 4. Payment Service

**Responsibilities:**
- Process payments via payment gateway
- Handle payment callbacks
- Process refunds
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

#### Preventing Overbooking

**Challenge:** Multiple users trying to book the same room for the same dates

**Solution 1: Database Transactions with Row Locking**
- Use `SELECT FOR UPDATE` to lock availability rows
- Check availability within transaction
- Update availability atomically
- Rollback if not available

**Solution 2: Distributed Locks**
- Acquire distributed lock before checking/updating availability
- Use Redis or Zookeeper for distributed locking
- Lock timeout prevents deadlocks
- Ensures only one booking can reserve rooms at a time

**Solution 3: Optimistic Locking**
- Use version numbers on availability records
- Check version before update
- Retry if version changed (another booking made)

**Implementation:**
```python
def reserve_rooms(hotel_id, room_type_id, check_in, check_out, booking_id):
    # Get all dates in range
    dates = get_dates_in_range(check_in, check_out)
    
    with database.transaction():
        for date in dates:
            # Lock availability row
            availability = Availability.objects.select_for_update().get(
                hotel_id=hotel_id,
                room_type_id=room_type_id,
                date=date,
                available_rooms__gt=0
            )
            
            # Decrement available rooms
            availability.available_rooms -= 1
            availability.save()
            
            # Create booking room record
            BookingRoom.objects.create(
                booking_id=booking_id,
                room_type_id=room_type_id,
                check_in_date=date,
                check_out_date=date
            )
```

#### Date Range Availability Query

**Challenge:** Efficiently check availability for date ranges

**Solution:**
- Query availability table for all dates in range
- Check if `available_rooms > 0` for each date
- Use indexed queries on `(hotel_id, room_type_id, date)`
- Cache results with short TTL

**Implementation:**
```python
def check_availability(hotel_id, room_type_id, check_in, check_out):
    dates = get_dates_in_range(check_in, check_out)
    
    # Query availability for all dates
    availability_records = Availability.objects.filter(
        hotel_id=hotel_id,
        room_type_id=room_type_id,
        date__in=dates
    ).values('date', 'available_rooms', 'price')
    
    # Check if all dates have availability
    available = all(record['available_rooms'] > 0 for record in availability_records)
    
    # Calculate total price
    total_price = sum(record['price'] for record in availability_records)
    
    return {
        'available': available,
        'dates': availability_records,
        'total_price': total_price
    }
```

#### Dynamic Pricing

**Challenge:** Adjust prices based on demand, season, day of week

**Solution:**
- Store base price in room_type
- Calculate dynamic price based on:
  - Demand (available_rooms / total_rooms)
  - Day of week (weekend premium)
  - Season (holiday premium)
  - Advance booking (early bird discount)
- Update prices in availability table
- Background job to recalculate prices

**Implementation:**
```python
def calculate_dynamic_price(hotel_id, room_type_id, date):
    room_type = RoomType.objects.get(room_type_id=room_type_id)
    availability = Availability.objects.get(
        hotel_id=hotel_id,
        room_type_id=room_type_id,
        date=date
    )
    
    base_price = room_type.base_price
    
    # Demand-based pricing
    occupancy_rate = 1 - (availability.available_rooms / availability.total_rooms)
    if occupancy_rate > 0.8:
        demand_multiplier = 1.5  # High demand
    elif occupancy_rate > 0.5:
        demand_multiplier = 1.2  # Medium demand
    else:
        demand_multiplier = 1.0  # Low demand
    
    # Day of week pricing
    day_of_week = date.weekday()
    if day_of_week >= 5:  # Weekend
        day_multiplier = 1.3
    else:
        day_multiplier = 1.0
    
    # Season pricing (simplified)
    month = date.month
    if month in [6, 7, 8, 12]:  # Summer and December
        season_multiplier = 1.2
    else:
        season_multiplier = 1.0
    
    dynamic_price = base_price * demand_multiplier * day_multiplier * season_multiplier
    
    return round(dynamic_price, 2)
```

#### Search Optimization

**Challenge:** Fast search across 100K+ hotels

**Solution:**
- **Elasticsearch** for location and full-text search
- **Geospatial Queries**: Use geo_distance queries for location
- **Filtering**: Apply filters (price, amenities) in Elasticsearch
- **Caching**: Cache popular search results
- **Pagination**: Use cursor-based pagination for large result sets

**Implementation:**
```python
def search_hotels(location, check_in, check_out, guests, filters):
    # Build Elasticsearch query
    query = {
        "bool": {
            "must": [
                {
                    "geo_distance": {
                        "distance": "50km",
                        "location": {
                            "lat": location["latitude"],
                            "lon": location["longitude"]
                        }
                    }
                }
            ],
            "filter": []
        }
    }
    
    # Add filters
    if filters.get("price_min"):
        query["bool"]["filter"].append({
            "range": {"price_per_night": {"gte": filters["price_min"]}}
        })
    
    if filters.get("amenities"):
        query["bool"]["filter"].append({
            "terms": {"amenities": filters["amenities"]}
        })
    
    # Execute search
    results = elasticsearch.search(
        index="hotels",
        body={"query": query, "size": 20}
    )
    
    # Check availability for each hotel
    hotels_with_availability = []
    for hit in results["hits"]["hits"]:
        hotel = hit["_source"]
        availability = check_availability(
            hotel["hotel_id"],
            check_in,
            check_out,
            guests
        )
        if availability["available"]:
            hotel["price_per_night"] = availability["price_per_night"]
            hotels_with_availability.append(hotel)
    
    return hotels_with_availability
```

### Scalability Considerations

#### Horizontal Scaling

**API Services:**
- Stateless services, scale horizontally
- Load balancer distributes requests
- Auto-scaling based on CPU/memory metrics

**Database:**
- Shard availability table by hotel_id
- Read replicas for read scaling
- Connection pooling

**Cache:**
- Redis cluster for high availability
- Shard cache by hotel_id
- Cache warming for popular hotels

#### Caching Strategy

**Redis Cache:**
- **Hotel Details**: TTL 1 hour
- **Availability**: TTL 30 seconds (short for accuracy)
- **Search Results**: TTL 5 minutes
- **Room Types**: TTL 1 hour
- **User Sessions**: TTL 30 minutes

**Cache Invalidation:**
- Invalidate on availability changes
- Invalidate on hotel updates
- Use cache-aside pattern

#### Load Balancing

**Traffic Distribution:**
- Round-robin or least-connections
- Health checks for backend services
- Circuit breakers for failing services

**Geographic Distribution:**
- CDN for static content
- Regional database replicas
- Edge caching for popular locations

#### Database Optimization

**Indexing:**
- Index on `(hotel_id, room_type_id, date)` for availability queries
- Index on `check_in_date` for booking queries
- Index on `user_id` for user bookings
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
- **Permission Checks**: Verify user owns booking before modifications
- **Input Validation**: Validate all inputs

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
- Availability accuracy

**Business Metrics:**
- Bookings per day
- Revenue per day
- Conversion rate (searches to bookings)
- Average booking value
- Cancellation rate
- Overbooking incidents (should be 0)

#### Logging

- **Structured Logging**: JSON logs for easy parsing
- **Request Tracing**: Trace requests across services
- **Error Logging**: Log errors with context
- **Audit Logging**: Log important actions (bookings, cancellations)

#### Alerting

- **High Error Rate**: Alert if error rate > 1%
- **High Latency**: Alert if p95 latency > 2 seconds
- **Database Issues**: Alert on database errors
- **Payment Failures**: Alert on payment gateway errors
- **Overbooking Risk**: Alert if available_rooms < 0

### Trade-offs and Optimizations

#### Trade-offs

**1. Strong Consistency vs Availability**
- **Strong Consistency**: Required for availability (no overbooking)
- **Availability**: Can sacrifice for critical operations
- **Decision**: Use strong consistency for booking, eventual consistency for search

**2. Availability Cache TTL: Short vs Long**
- **Short (30 sec)**: More accurate, but higher database load
- **Long (5 min)**: Lower load, but may show stale data
- **Decision**: 30 seconds balance, with cache invalidation on updates

**3. Search: Elasticsearch vs Database**
- **Elasticsearch**: Better for complex search, but additional infrastructure
- **Database**: Simpler, but slower for complex queries
- **Decision**: Elasticsearch for search, database for availability

**4. Pricing: Static vs Dynamic**
- **Static**: Simpler, but less revenue optimization
- **Dynamic**: More revenue, but more complex
- **Decision**: Dynamic pricing with background job updates

#### Optimizations

**1. Database Connection Pooling**
- Reuse database connections
- Reduce connection overhead
- Improve performance

**2. Batch Operations**
- Batch availability updates
- Batch price calculations
- Reduce database round trips

**3. Read Replicas**
- Use read replicas for read-heavy queries
- Reduce load on primary database
- Improve read performance

**4. CDN for Static Content**
- Serve hotel images via CDN
- Reduce server load
- Improve delivery speed

**5. Compression**
- Compress API responses
- Reduce bandwidth usage
- Improve performance

## Summary

Designing a hotel reservation system at scale requires careful consideration of:

1. **Overbooking Prevention**: Database transactions and distributed locks prevent double-booking
2. **Date Range Queries**: Efficient queries for checking availability across date ranges
3. **Search Optimization**: Elasticsearch for fast location-based search
4. **Dynamic Pricing**: Price adjustment based on demand and season
5. **Scalability**: Horizontal scaling with sharding and caching
6. **Strong Consistency**: Critical for availability to prevent overbooking
7. **Performance**: Fast search and availability checks even under high load
8. **Reliability**: Guaranteed booking confirmation and payment processing

Key architectural decisions:
- **Sharded Database** for availability storage
- **Elasticsearch** for hotel search
- **Redis Cache** for availability and search results
- **Database Transactions** with row locking
- **Distributed Locks** for concurrent bookings
- **Message Queue** for event distribution
- **Horizontal Scaling** for all services

The system handles 1 million bookings per day with guaranteed availability accuracy and no overbooking.

