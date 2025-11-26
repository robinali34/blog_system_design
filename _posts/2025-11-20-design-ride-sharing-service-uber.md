---
layout: post
title: "Design a Ride-Sharing Service like Uber - System Design Interview"
date: 2025-11-20
categories: [System Design, Interview Example, Distributed Systems, Real-Time Systems, Geospatial Systems, Microservices]
excerpt: "A comprehensive guide to designing a ride-sharing service like Uber, covering real-time matching, location tracking, dynamic pricing, payment processing, driver-rider coordination, and architectural patterns for handling millions of rides, real-time location updates, and complex matching algorithms."
---

## Introduction

Uber is a ride-sharing platform that connects riders with nearby drivers in real-time. The system handles millions of rides daily, processes real-time location updates, matches riders with drivers efficiently, implements dynamic pricing, and processes payments seamlessly.

This post provides a detailed walkthrough of designing a ride-sharing service like Uber, covering key architectural decisions, real-time matching algorithms, geospatial data structures, dynamic pricing models, payment processing, and scalability challenges. This is one of the most common system design interview questions that tests your understanding of real-time systems, geospatial queries, microservices architecture, and handling complex business logic at scale.

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
   - [Driver-Rider Matching Service](#driver-rider-matching-service)
   - [Location Tracking Service](#location-tracking-service)
   - [Dynamic Pricing Service](#dynamic-pricing-service)
   - [Payment Service](#payment-service)
   - [Notification Service](#notification-service)
   - [Trip Management Service](#trip-management-service)
   - [Rating and Review Service](#rating-and-review-service)
   - [Scalability Considerations](#scalability-considerations)
   - [Security Considerations](#security-considerations)
   - [Monitoring & Observability](#monitoring--observability)
   - [Trade-offs and Optimizations](#trade-offs-and-optimizations)
10. [Summary](#summary)

## Problem Statement

**Design a ride-sharing service like Uber with the following features:**

1. Rider registration and authentication
2. Driver registration, verification, and onboarding
3. Real-time driver-rider matching
4. Real-time location tracking (drivers and riders)
5. Dynamic pricing (surge pricing)
6. Ride booking and cancellation
7. Trip tracking and navigation
8. Payment processing
9. Rating and review system
10. Driver earnings and payouts
11. Ride history
12. Multi-city support

**Scale Requirements:**
- 100 million+ users (riders and drivers)
- 20 million+ daily active users
- 15 million+ rides per day
- Peak: 1 million concurrent rides
- 500K+ active drivers
- Real-time location updates every 4 seconds
- Average ride: 20 minutes, 5 miles
- Global presence: 10,000+ cities

## Requirements

### Functional Requirements

**Core Features:**

1. **User Management**:
   - Rider registration and authentication
   - Driver registration, background checks, vehicle verification
   - Profile management

2. **Ride Booking**:
   - Request a ride with pickup and dropoff locations
   - Select ride type (UberX, UberXL, UberBlack, etc.)
   - See estimated fare and wait time
   - Cancel ride (with cancellation fees if applicable)

3. **Driver-Rider Matching**:
   - Match rider with nearest available driver
   - Consider driver availability, location, rating, vehicle type
   - Handle multiple concurrent ride requests
   - Reassign driver if needed

4. **Real-Time Location Tracking**:
   - Track driver location in real-time
   - Track rider location (for pickup)
   - Show ETA (Estimated Time of Arrival)
   - Update location every 4 seconds

5. **Dynamic Pricing**:
   - Base fare calculation
   - Surge pricing based on demand/supply ratio
   - Time and distance-based pricing
   - Show price estimate before booking

6. **Trip Management**:
   - Start trip when driver arrives
   - Track trip progress
   - End trip at destination
   - Handle trip cancellation

7. **Payment Processing**:
   - Multiple payment methods (credit card, PayPal, etc.)
   - Automatic payment after trip completion
   - Split fare (multiple riders)
   - Refund processing

8. **Rating and Reviews**:
   - Rate driver after trip
   - Rate rider (driver perspective)
   - Review and feedback

9. **Notifications**:
   - Push notifications for ride status
   - SMS notifications
   - Email receipts

10. **Driver Features**:
    - Driver earnings dashboard
    - Payout processing
    - Driver availability toggle
    - Accept/reject ride requests

**Out of Scope:**
- Food delivery (UberEats)
- Freight (Uber Freight)
- Advanced route optimization
- Multi-stop trips
- Scheduled rides
- Carpool/ridesharing between riders

### Non-Functional Requirements

1. **Availability**: 99.9% uptime
2. **Reliability**: No ride loss, guaranteed matching
3. **Performance**:
   - Ride matching: < 5 seconds
   - Location update latency: < 1 second
   - Payment processing: < 2 seconds
   - API response time: < 200ms (p95)
4. **Scalability**: Handle 1 million concurrent rides
5. **Consistency**: Strong consistency for payments, eventual consistency for ratings
6. **Durability**: All ride data must be persisted
7. **Real-Time**: Location updates every 4 seconds
8. **Geographic Distribution**: Global presence with regional data centers
9. **Security**: Secure payment processing, user data protection, driver verification

## Capacity Estimation

### Traffic Estimates

**Assumptions:**
- 100 million total users
- 20 million daily active users (DAU)
- 15 million rides per day
- Peak traffic: 3x average (45 million rides/day)
- Average ride duration: 20 minutes

**Read Traffic:**
- Location updates: 4 seconds per update
  - Active drivers: 500K
  - Active riders (during trip): 1M (peak)
  - Location updates per second: (500K + 1M) / 4 = 375K updates/sec
- API calls per ride: ~50 calls (booking, matching, tracking, payment)
- Total API calls per day: 15M rides × 50 = 750M calls/day
- Average QPS: 750M / 86400 = ~8,700 QPS
- Peak QPS: 8,700 × 3 = ~26,000 QPS

**Write Traffic:**
- Ride creation: 15M rides/day = ~174 rides/sec
- Location updates: 375K updates/sec
- Payment transactions: 15M/day = ~174 transactions/sec
- Total writes: ~375K writes/sec (dominated by location updates)

### Storage Estimates

**Assumptions:**
- User data: 1KB per user
- Ride data: 5KB per ride
- Location data: 100 bytes per update
- Location updates per ride: 20 min × 60 sec / 4 sec = 300 updates
- Store location history for 30 days
- Store ride history indefinitely

**Storage Calculations:**
- User data: 100M users × 1KB = 100GB
- Ride data: 15M rides/day × 365 days × 5KB = ~27TB/year
- Location data: 15M rides/day × 300 updates × 100 bytes × 30 days = ~1.35TB
- Total storage: ~100GB + 27TB + 1.35TB = ~28.5TB (first year)
- With replication (3x): ~85TB

### Bandwidth Estimates

**Assumptions:**
- Location update: 200 bytes (including headers)
- API request/response: 2KB average
- Real-time updates: WebSocket or long polling

**Bandwidth Calculations:**
- Location updates: 375K updates/sec × 200 bytes = 75MB/sec = 600Mbps
- API traffic: 26K QPS × 2KB = 52MB/sec = 416Mbps
- Total bandwidth: ~1Gbps (peak)
- Per region: ~100-200Mbps average

## Core Entities

### User (Rider/Driver)

```python
User {
    user_id: UUID (Primary Key)
    email: String
    phone: String
    name: String
    user_type: Enum (RIDER, DRIVER)
    created_at: Timestamp
    updated_at: Timestamp
    status: Enum (ACTIVE, INACTIVE, SUSPENDED)
}
```

### Driver

```python
Driver {
    driver_id: UUID (Primary Key, Foreign Key -> User)
    license_number: String
    vehicle_make: String
    vehicle_model: String
    vehicle_year: Integer
    vehicle_license_plate: String
    vehicle_type: Enum (UBERX, UBERXL, UBERBLACK, etc.)
    rating: Float (average rating)
    total_rides: Integer
    is_available: Boolean
    current_location: Point (latitude, longitude)
    status: Enum (ONLINE, OFFLINE, ON_TRIP)
    verified: Boolean
    created_at: Timestamp
}
```

### Ride

```python
Ride {
    ride_id: UUID (Primary Key)
    rider_id: UUID (Foreign Key -> User)
    driver_id: UUID (Foreign Key -> Driver, nullable)
    pickup_location: Point
    dropoff_location: Point
    pickup_address: String
    dropoff_address: String
    ride_type: Enum (UBERX, UBERXL, etc.)
    status: Enum (REQUESTED, MATCHED, DRIVER_ARRIVED, IN_PROGRESS, COMPLETED, CANCELLED)
    fare: Decimal
    base_fare: Decimal
    distance_fare: Decimal
    time_fare: Decimal
    surge_multiplier: Float
    estimated_fare: Decimal
    actual_fare: Decimal
    distance: Float (miles)
    duration: Integer (seconds)
    requested_at: Timestamp
    matched_at: Timestamp
    started_at: Timestamp
    completed_at: Timestamp
    cancelled_at: Timestamp
    cancellation_reason: String
    payment_status: Enum (PENDING, PROCESSING, COMPLETED, FAILED)
    payment_method_id: UUID
}
```

### Location Update

```python
LocationUpdate {
    update_id: UUID (Primary Key)
    user_id: UUID (Foreign Key -> User)
    user_type: Enum (RIDER, DRIVER)
    ride_id: UUID (Foreign Key -> Ride, nullable)
    latitude: Float
    longitude: Float
    heading: Float (direction in degrees)
    speed: Float (mph)
    accuracy: Float (meters)
    timestamp: Timestamp
    created_at: Timestamp
}
```

### Payment

```python
Payment {
    payment_id: UUID (Primary Key)
    ride_id: UUID (Foreign Key -> Ride)
    rider_id: UUID (Foreign Key -> User)
    amount: Decimal
    currency: String (USD, EUR, etc.)
    payment_method: Enum (CREDIT_CARD, PAYPAL, etc.)
    payment_method_id: UUID
    status: Enum (PENDING, PROCESSING, COMPLETED, FAILED, REFUNDED)
    transaction_id: String
    processed_at: Timestamp
    created_at: Timestamp
}
```

### Rating

```python
Rating {
    rating_id: UUID (Primary Key)
    ride_id: UUID (Foreign Key -> Ride)
    rated_user_id: UUID (Foreign Key -> User)  # Driver or Rider
    rating_user_id: UUID (Foreign Key -> User)  # Who gave the rating
    rating: Integer (1-5)
    review: String (optional)
    created_at: Timestamp
}
```

## API

### Rider APIs

```http
# Request a ride
POST /api/v1/rides/request
Request Body:
{
    "rider_id": "uuid",
    "pickup_location": {
        "latitude": 37.7749,
        "longitude": -122.4194
    },
    "dropoff_location": {
        "latitude": 37.7849,
        "longitude": -122.4094
    },
    "pickup_address": "123 Main St, San Francisco, CA",
    "dropoff_address": "456 Market St, San Francisco, CA",
    "ride_type": "UBERX"
}
Response:
{
    "ride_id": "uuid",
    "estimated_fare": 15.50,
    "estimated_wait_time": 5,  // minutes
    "surge_multiplier": 1.2,
    "status": "REQUESTED"
}

# Get ride status
GET /api/v1/rides/{ride_id}
Response:
{
    "ride_id": "uuid",
    "status": "MATCHED",
    "driver": {
        "driver_id": "uuid",
        "name": "John Doe",
        "rating": 4.8,
        "vehicle": {
            "make": "Toyota",
            "model": "Camry",
            "license_plate": "ABC123"
        },
        "current_location": {
            "latitude": 37.7750,
            "longitude": -122.4195
        },
        "eta": 3  // minutes
    },
    "pickup_location": {...},
    "dropoff_location": {...}
}

# Cancel ride
POST /api/v1/rides/{ride_id}/cancel
Request Body:
{
    "reason": "Changed my mind"
}
Response:
{
    "ride_id": "uuid",
    "status": "CANCELLED",
    "cancellation_fee": 5.00
}

# Rate driver
POST /api/v1/rides/{ride_id}/rate
Request Body:
{
    "rating": 5,
    "review": "Great driver!"
}
Response:
{
    "rating_id": "uuid",
    "status": "success"
}

# Get ride history
GET /api/v1/rides/history?rider_id={rider_id}&page=1&limit=20
Response:
{
    "rides": [...],
    "total": 150,
    "page": 1,
    "limit": 20
}
```

### Driver APIs

```http
# Update driver availability
PUT /api/v1/drivers/{driver_id}/availability
Request Body:
{
    "is_available": true
}
Response:
{
    "driver_id": "uuid",
    "is_available": true,
    "status": "ONLINE"
}

# Update driver location
POST /api/v1/drivers/{driver_id}/location
Request Body:
{
    "latitude": 37.7749,
    "longitude": -122.4194,
    "heading": 45.0,
    "speed": 25.5
}
Response:
{
    "status": "success",
    "timestamp": "2025-11-20T10:30:00Z"
}

# Accept ride request
POST /api/v1/rides/{ride_id}/accept
Request Body:
{
    "driver_id": "uuid"
}
Response:
{
    "ride_id": "uuid",
    "status": "MATCHED",
    "rider": {
        "rider_id": "uuid",
        "name": "Jane Smith",
        "rating": 4.9,
        "pickup_location": {...}
    }
}

# Reject ride request
POST /api/v1/rides/{ride_id}/reject
Request Body:
{
    "driver_id": "uuid",
    "reason": "Too far"
}
Response:
{
    "status": "success"
}

# Start trip
POST /api/v1/rides/{ride_id}/start
Request Body:
{
    "driver_id": "uuid"
}
Response:
{
    "ride_id": "uuid",
    "status": "IN_PROGRESS",
    "started_at": "2025-11-20T10:35:00Z"
}

# Complete trip
POST /api/v1/rides/{ride_id}/complete
Request Body:
{
    "driver_id": "uuid",
    "dropoff_location": {
        "latitude": 37.7849,
        "longitude": -122.4094
    }
}
Response:
{
    "ride_id": "uuid",
    "status": "COMPLETED",
    "fare": 18.50,
    "distance": 5.2,
    "duration": 1200
}

# Get driver earnings
GET /api/v1/drivers/{driver_id}/earnings?start_date=2025-11-01&end_date=2025-11-20
Response:
{
    "driver_id": "uuid",
    "total_earnings": 1250.50,
    "total_rides": 85,
    "period": {
        "start": "2025-11-01",
        "end": "2025-11-20"
    },
    "daily_earnings": [...]
}
```

### Common APIs

```http
# Get fare estimate
GET /api/v1/fare/estimate?pickup_lat=37.7749&pickup_lng=-122.4194&dropoff_lat=37.7849&dropoff_lng=-122.4094&ride_type=UBERX
Response:
{
    "estimated_fare": 15.50,
    "estimated_distance": 5.2,  // miles
    "estimated_duration": 20,  // minutes
    "surge_multiplier": 1.2,
    "base_fare": 2.50,
    "distance_fare": 1.50,
    "time_fare": 0.25
}

# Get nearby drivers
GET /api/v1/drivers/nearby?latitude=37.7749&longitude=-122.4194&radius=5&limit=10
Response:
{
    "drivers": [
        {
            "driver_id": "uuid",
            "distance": 0.5,  // miles
            "eta": 2,  // minutes
            "rating": 4.8
        },
        ...
    ]
}
```

## Data Flow

### Ride Request Flow

```
1. Rider opens app and requests ride
   └─> Rider App
       └─> API Gateway
           └─> Ride Service
               ├─> Validates request
               ├─> Calculates fare estimate
               │   └─> Pricing Service
               ├─> Creates ride record
               │   └─> Database (Ride table)
               ├─> Publishes ride request event
               │   └─> Message Queue (Kafka)
               └─> Returns ride_id and estimate

2. Matching Service processes ride request
   └─> Matching Service (consumes from Kafka)
       ├─> Queries nearby available drivers
       │   └─> Location Service (Geospatial Index)
       ├─> Applies matching algorithm
       │   ├─> Distance
       │   ├─> Driver rating
       │   ├─> Driver availability
       │   └─> Vehicle type match
       ├─> Selects best driver
       ├─> Sends ride request to driver
       │   └─> Notification Service
       │       └─> Push Notification
       └─> Waits for driver acceptance (30 seconds timeout)

3. Driver accepts ride
   └─> Driver App
       └─> API Gateway
           └─> Ride Service
               ├─> Updates ride status to MATCHED
               ├─> Updates driver_id in ride record
               ├─> Updates driver status to ON_TRIP
               ├─> Sends notifications
               │   ├─> Rider: "Driver matched"
               │   └─> Driver: "Ride details"
               └─> Starts real-time location tracking

4. Real-time tracking
   └─> Location Service
       ├─> Receives location updates (every 4 seconds)
       │   ├─> From Driver App
       │   └─> From Rider App (during pickup)
       ├─> Stores location updates
       │   └─> Time-Series Database
       ├─> Calculates ETA
       └─> Pushes updates to clients
           └─> WebSocket/Server-Sent Events

5. Driver arrives at pickup
   └─> Driver App
       └─> API Gateway
           └─> Ride Service
               ├─> Updates ride status to DRIVER_ARRIVED
               └─> Sends notification to rider

6. Trip starts
   └─> Driver App (starts trip)
       └─> API Gateway
           └─> Ride Service
               ├─> Updates ride status to IN_PROGRESS
               ├─> Records start time and location
               └─> Continues location tracking

7. Trip completes
   └─> Driver App (completes trip)
       └─> API Gateway
           └─> Ride Service
               ├─> Updates ride status to COMPLETED
               ├─> Calculates final fare
               │   └─> Pricing Service
               ├─> Records end time, location, distance, duration
               ├─> Triggers payment processing
               │   └─> Payment Service
               │       ├─> Charges rider
               │       └─> Updates driver earnings
               └─> Sends notifications
                   ├─> Rider: "Trip completed, receipt"
                   └─> Driver: "Earnings updated"

8. Rating flow
   └─> Rider App (rates driver)
       └─> API Gateway
           └─> Rating Service
               ├─> Creates rating record
               ├─> Updates driver average rating
               └─> Stores review
```

## Database Design

### Schema Design

#### Users Table

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    user_type ENUM('RIDER', 'DRIVER') NOT NULL,
    status ENUM('ACTIVE', 'INACTIVE', 'SUSPENDED') DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_phone (phone),
    INDEX idx_user_type (user_type)
);
```

#### Drivers Table

```sql
CREATE TABLE drivers (
    driver_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    license_number VARCHAR(50) UNIQUE NOT NULL,
    vehicle_make VARCHAR(100) NOT NULL,
    vehicle_model VARCHAR(100) NOT NULL,
    vehicle_year INT NOT NULL,
    vehicle_license_plate VARCHAR(20) UNIQUE NOT NULL,
    vehicle_type ENUM('UBERX', 'UBERXL', 'UBERBLACK', 'UBERLUX') NOT NULL,
    rating DECIMAL(3,2) DEFAULT 0.00,
    total_rides INT DEFAULT 0,
    is_available BOOLEAN DEFAULT FALSE,
    current_latitude DECIMAL(10,8),
    current_longitude DECIMAL(11,8),
    status ENUM('ONLINE', 'OFFLINE', 'ON_TRIP') DEFAULT 'OFFLINE',
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    INDEX idx_status (status),
    INDEX idx_is_available (is_available),
    INDEX idx_vehicle_type (vehicle_type),
    SPATIAL INDEX idx_location (current_latitude, current_longitude)
);
```

#### Rides Table

```sql
CREATE TABLE rides (
    ride_id UUID PRIMARY KEY,
    rider_id UUID NOT NULL,
    driver_id UUID,
    pickup_latitude DECIMAL(10,8) NOT NULL,
    pickup_longitude DECIMAL(11,8) NOT NULL,
    dropoff_latitude DECIMAL(10,8) NOT NULL,
    dropoff_longitude DECIMAL(11,8) NOT NULL,
    pickup_address TEXT NOT NULL,
    dropoff_address TEXT NOT NULL,
    ride_type ENUM('UBERX', 'UBERXL', 'UBERBLACK', 'UBERLUX') NOT NULL,
    status ENUM('REQUESTED', 'MATCHED', 'DRIVER_ARRIVED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED') NOT NULL,
    fare DECIMAL(10,2),
    base_fare DECIMAL(10,2),
    distance_fare DECIMAL(10,2),
    time_fare DECIMAL(10,2),
    surge_multiplier DECIMAL(4,2) DEFAULT 1.00,
    estimated_fare DECIMAL(10,2),
    actual_fare DECIMAL(10,2),
    distance DECIMAL(10,2),  -- miles
    duration INT,  -- seconds
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    matched_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    cancellation_reason TEXT,
    payment_status ENUM('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED') DEFAULT 'PENDING',
    payment_method_id UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (rider_id) REFERENCES users(user_id),
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id),
    INDEX idx_rider_id (rider_id),
    INDEX idx_driver_id (driver_id),
    INDEX idx_status (status),
    INDEX idx_requested_at (requested_at),
    INDEX idx_completed_at (completed_at)
);
```

#### Location Updates Table

```sql
CREATE TABLE location_updates (
    update_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    user_type ENUM('RIDER', 'DRIVER') NOT NULL,
    ride_id UUID,
    latitude DECIMAL(10,8) NOT NULL,
    longitude DECIMAL(11,8) NOT NULL,
    heading DECIMAL(5,2),
    speed DECIMAL(5,2),
    accuracy DECIMAL(5,2),
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (ride_id) REFERENCES rides(ride_id),
    INDEX idx_user_id (user_id),
    INDEX idx_ride_id (ride_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_created_at (created_at)
) PARTITION BY RANGE (YEAR(created_at), MONTH(created_at));
```

#### Payments Table

```sql
CREATE TABLE payments (
    payment_id UUID PRIMARY KEY,
    ride_id UUID NOT NULL,
    rider_id UUID NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payment_method ENUM('CREDIT_CARD', 'PAYPAL', 'DEBIT_CARD', 'WALLET') NOT NULL,
    payment_method_id UUID NOT NULL,
    status ENUM('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'REFUNDED') DEFAULT 'PENDING',
    transaction_id VARCHAR(255),
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (ride_id) REFERENCES rides(ride_id),
    FOREIGN KEY (rider_id) REFERENCES users(user_id),
    INDEX idx_ride_id (ride_id),
    INDEX idx_rider_id (rider_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

#### Ratings Table

```sql
CREATE TABLE ratings (
    rating_id UUID PRIMARY KEY,
    ride_id UUID NOT NULL,
    rated_user_id UUID NOT NULL,  -- Driver or Rider being rated
    rating_user_id UUID NOT NULL,  -- User giving the rating
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ride_id) REFERENCES rides(ride_id),
    FOREIGN KEY (rated_user_id) REFERENCES users(user_id),
    FOREIGN KEY (rating_user_id) REFERENCES users(user_id),
    INDEX idx_ride_id (ride_id),
    INDEX idx_rated_user_id (rated_user_id),
    INDEX idx_rating (rating)
);
```

### Database Sharding Strategy

**Sharding by Geography (City/Region)**:

- **Strategy**: Shard by city or geographic region
- **Shard Key**: `city_id` or `region_id`
- **Benefits**:
  - Locality: Most queries are city-specific
  - Reduced cross-shard queries
  - Easier data management per region
- **Challenges**:
  - Cross-city rides (rare but possible)
  - Driver movement between cities

**Sharding by User ID**:

- **Strategy**: Hash-based sharding on `user_id`
- **Shard Key**: Hash of `user_id`
- **Benefits**:
  - Even distribution
  - Simple routing
- **Challenges**:
  - Cross-shard queries for matching
  - Location queries require querying all shards

**Hybrid Approach**:

- **Primary Sharding**: By geography (city/region)
- **Secondary Indexing**: User-based indexes for cross-shard queries
- **Location Service**: Separate service with geospatial indexes (Redis Geo, Elasticsearch)

**Recommended Approach**:

1. **Rides Table**: Shard by `city_id` (geographic sharding)
2. **Users Table**: Shard by `user_id` hash (even distribution)
3. **Location Updates**: Use time-series database (InfluxDB, TimescaleDB) with city-based partitioning
4. **Location Service**: Use Redis Geo or Elasticsearch for real-time location queries

## High-Level Design

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Applications                      │
│  ┌──────────────┐                    ┌──────────────┐          │
│  │  Rider App   │                    │  Driver App  │          │
│  │  (Mobile)    │                    │  (Mobile)    │          │
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
│  │   Ride       │  │  Matching    │  │  Location    │        │
│  │   Service    │  │  Service     │  │  Service     │        │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘        │
│         │                 │                 │                  │
│  ┌──────┴─────────────────┴─────────────────┴───────┐        │
│  │              Message Queue (Kafka)                │        │
│  └──────────────────────────────────────────────────┘        │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Pricing    │  │   Payment    │  │ Notification │        │
│  │   Service    │  │   Service    │  │   Service    │        │
│  └──────────────┘  └──────┬───────┘  └──────┬───────┘        │
│                           │                 │                  │
│  ┌─────────────────────────┴─────────────────┴───────┐        │
│  │              External Services                     │        │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐        │        │
│  │  │ Payment  │  │   SMS    │  │   Push   │        │        │
│  │  │ Gateway  │  │ Gateway  │  │ Service │        │        │
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
│  │  PostgreSQL  │  │   Redis      │  │  Elasticsearch│        │
│  │  (Primary DB)│  │  (Cache +    │  │  (Location    │        │
│  │              │  │   Geo Index) │  │   Search)    │        │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │  TimescaleDB │  │   S3         │                            │
│  │  (Location   │  │  (Archived   │                            │
│  │   History)   │  │   Data)      │                            │
│  └──────────────┘  └──────────────┘                            │
└───────────────────────────────────────────────────────────────────┘
```

## Deep Dive

### Driver-Rider Matching Service

#### Problem

Match a rider with the best available driver in real-time, considering:
- Proximity (distance)
- Driver availability
- Driver rating
- Vehicle type match
- Driver preferences (if any)

#### Solution: Geospatial Matching Algorithm

**Approach 1: Radius-Based Search**

```python
def find_nearby_drivers(pickup_location, radius_miles=5, ride_type='UBERX'):
    """
    Find drivers within radius using geospatial index
    """
    # Query Redis Geo or Elasticsearch for nearby drivers
    nearby_drivers = location_service.find_within_radius(
        latitude=pickup_location.latitude,
        longitude=pickup_location.longitude,
        radius_miles=radius_miles,
        filters={
            'status': 'ONLINE',
            'is_available': True,
            'vehicle_type': ride_type
        }
    )
    
    # Score and rank drivers
    scored_drivers = []
    for driver in nearby_drivers:
        score = calculate_match_score(driver, pickup_location)
        scored_drivers.append((driver, score))
    
    # Sort by score (higher is better)
    scored_drivers.sort(key=lambda x: x[1], reverse=True)
    
    return [driver for driver, score in scored_drivers[:10]]
```

**Scoring Function**:

```python
def calculate_match_score(driver, pickup_location):
    """
    Calculate match score based on multiple factors
    """
    # Distance score (closer is better)
    distance = calculate_distance(
        driver.current_location,
        pickup_location
    )
    distance_score = max(0, 100 - (distance * 10))  # Max 100 points
    
    # Rating score (higher rating is better)
    rating_score = driver.rating * 20  # Max 100 points (5.0 * 20)
    
    # Availability score (recently available is better)
    availability_score = calculate_availability_score(driver)
    
    # Total rides score (more experience is better, but diminishing returns)
    experience_score = min(50, driver.total_rides / 100)
    
    # Weighted combination
    total_score = (
        distance_score * 0.4 +      # 40% weight on distance
        rating_score * 0.3 +         # 30% weight on rating
        availability_score * 0.2 +   # 20% weight on availability
        experience_score * 0.1       # 10% weight on experience
    )
    
    return total_score
```

**Approach 2: Grid-Based Matching**

For very high scale, use grid-based approach:

```python
class GridBasedMatching:
    def __init__(self, grid_size_miles=1):
        self.grid_size = grid_size_miles
        self.grid_cache = {}  # grid_id -> [driver_ids]
    
    def get_grid_id(self, latitude, longitude):
        """Convert lat/lng to grid ID"""
        lat_grid = int(latitude / self.grid_size)
        lng_grid = int(longitude / self.grid_size)
        return f"{lat_grid}_{lng_grid}"
    
    def find_drivers_in_grid(self, pickup_location):
        """Find drivers in same and adjacent grids"""
        grid_id = self.get_grid_id(
            pickup_location.latitude,
            pickup_location.longitude
        )
        
        # Check current grid and 8 adjacent grids
        drivers = []
        for lat_offset in [-1, 0, 1]:
            for lng_offset in [-1, 0, 1]:
                check_grid_id = self.get_grid_id(
                    pickup_location.latitude + lat_offset * self.grid_size,
                    pickup_location.longitude + lng_offset * self.grid_size
                )
                drivers.extend(self.grid_cache.get(check_grid_id, []))
        
        return drivers
```

**Matching Flow**:

```
1. Ride request received
   └─> Matching Service

2. Query nearby drivers
   └─> Location Service (Redis Geo/Elasticsearch)
       └─> Returns drivers within 5 miles radius

3. Filter drivers
   ├─> Available (is_available = true)
   ├─> Online (status = ONLINE)
   ├─> Vehicle type match
   └─> Not on trip

4. Score drivers
   ├─> Distance (closer = better)
   ├─> Rating (higher = better)
   ├─> Availability (recently available = better)
   └─> Experience (more rides = better)

5. Select top driver
   └─> Send ride request notification

6. Wait for acceptance (30 seconds timeout)
   ├─> If accepted: Match confirmed
   ├─> If rejected: Select next driver
   └─> If timeout: Select next driver or expand radius
```

**Optimization**:

- **Caching**: Cache available drivers per grid/city
- **Pre-computation**: Pre-score drivers when they come online
- **Batch Processing**: Process multiple ride requests in batch
- **Load Balancing**: Distribute matching across multiple instances

### Location Tracking Service

#### Problem

Track real-time location of drivers and riders, update every 4 seconds, support millions of concurrent users.

#### Solution: Real-Time Location Tracking

**Architecture**:

```
Client App (Mobile)
    │
    │ Location Update (every 4 seconds)
    │
    ▼
API Gateway
    │
    │
    ▼
Location Service
    ├─> Validates location
    ├─> Stores in cache (Redis)
    │   └─> Key: user_id, Value: {lat, lng, timestamp}
    ├─> Updates geospatial index (Redis Geo)
    ├─> Stores in time-series DB (TimescaleDB)
    └─> Publishes location update event
        └─> Kafka (for other services)
```

**Redis Geo Index**:

```python
# Add driver location to Redis Geo
redis.geoadd(
    "drivers:geo",
    longitude,
    latitude,
    driver_id
)

# Find nearby drivers
nearby_drivers = redis.georadius(
    "drivers:geo",
    longitude,
    latitude,
    radius=5,  # miles
    unit="mi",
    withdist=True,  # Include distance
    withcoord=True  # Include coordinates
)
```

**Time-Series Storage**:

```sql
-- TimescaleDB hypertable for location history
CREATE TABLE location_updates (
    time TIMESTAMPTZ NOT NULL,
    user_id UUID NOT NULL,
    ride_id UUID,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    heading DOUBLE PRECISION,
    speed DOUBLE PRECISION
);

SELECT create_hypertable('location_updates', 'time');

-- Query location history for a ride
SELECT time, latitude, longitude
FROM location_updates
WHERE ride_id = 'uuid'
  AND time >= '2025-11-20 10:00:00'
ORDER BY time;
```

**Real-Time Updates to Clients**:

```python
# WebSocket connection for real-time updates
class LocationWebSocket:
    def on_connect(self, client):
        # Subscribe to location updates for active ride
        ride_id = client.get_ride_id()
        client.subscribe(f"ride:{ride_id}:location")
    
    def on_location_update(self, user_id, location):
        # Publish to subscribed clients
        redis.publish(
            f"ride:{ride_id}:location",
            json.dumps({
                "user_id": user_id,
                "latitude": location.latitude,
                "longitude": location.longitude,
                "timestamp": location.timestamp
            })
        )
```

**Optimization**:

- **Batching**: Batch location updates (reduce write load)
- **Compression**: Compress location data
- **Throttling**: Throttle updates if client is slow
- **Caching**: Cache recent locations in Redis
- **Partitioning**: Partition by time (daily/monthly partitions)

### Dynamic Pricing Service

#### Problem

Calculate ride fare dynamically based on:
- Base fare
- Distance
- Time
- Surge pricing (demand/supply ratio)
- Ride type

#### Solution: Multi-Factor Pricing Model

**Base Fare Calculation**:

```python
def calculate_fare(ride):
    """
    Calculate ride fare
    """
    # Base fare (varies by ride type)
    base_fare = get_base_fare(ride.ride_type)  # e.g., $2.50 for UberX
    
    # Distance fare
    distance_fare = ride.distance * get_per_mile_rate(ride.ride_type)  # e.g., $1.50/mile
    
    # Time fare
    time_fare = (ride.duration / 60) * get_per_minute_rate(ride.ride_type)  # e.g., $0.25/minute
    
    # Surge multiplier
    surge_multiplier = calculate_surge_multiplier(
        ride.pickup_location,
        ride.requested_at
    )
    
    # Total fare
    total_fare = (base_fare + distance_fare + time_fare) * surge_multiplier
    
    # Minimum fare
    min_fare = get_minimum_fare(ride.ride_type)
    
    return max(total_fare, min_fare)
```

**Surge Pricing Algorithm**:

```python
def calculate_surge_multiplier(location, timestamp):
    """
    Calculate surge multiplier based on demand/supply ratio
    """
    # Get demand (active ride requests in area)
    demand = get_active_requests_count(location, radius_miles=2)
    
    # Get supply (available drivers in area)
    supply = get_available_drivers_count(location, radius_miles=2)
    
    # Calculate demand/supply ratio
    if supply == 0:
        return 3.0  # Maximum surge if no drivers
    
    ratio = demand / supply
    
    # Map ratio to surge multiplier
    if ratio < 0.5:
        return 1.0  # No surge
    elif ratio < 1.0:
        return 1.0 + (ratio - 0.5) * 0.4  # 1.0 to 1.2
    elif ratio < 1.5:
        return 1.2 + (ratio - 1.0) * 0.6  # 1.2 to 1.5
    elif ratio < 2.0:
        return 1.5 + (ratio - 1.5) * 0.5  # 1.5 to 1.75
    else:
        return min(3.0, 1.75 + (ratio - 2.0) * 0.25)  # 1.75 to 3.0
```

**Demand/Supply Calculation**:

```python
def get_active_requests_count(location, radius_miles):
    """
    Count active ride requests in area
    """
    # Query Redis for active requests in geospatial index
    active_requests = redis.georadius(
        "requests:geo",
        location.longitude,
        location.latitude,
        radius=radius_miles,
        unit="mi"
    )
    
    # Filter by time (requests in last 5 minutes)
    recent_requests = [
        req for req in active_requests
        if (time.now() - req.timestamp).seconds < 300
    ]
    
    return len(recent_requests)

def get_available_drivers_count(location, radius_miles):
    """
    Count available drivers in area
    """
    # Query Redis Geo for available drivers
    available_drivers = redis.georadius(
        "drivers:geo:available",
        location.longitude,
        location.latitude,
        radius=radius_miles,
        unit="mi"
    )
    
    return len(available_drivers)
```

**Caching Surge Multipliers**:

```python
# Cache surge multipliers per grid
def get_surge_multiplier(location):
    grid_id = get_grid_id(location)
    cache_key = f"surge:{grid_id}"
    
    # Check cache (5-minute TTL)
    cached = redis.get(cache_key)
    if cached:
        return float(cached)
    
    # Calculate and cache
    multiplier = calculate_surge_multiplier(location, time.now())
    redis.setex(cache_key, 300, multiplier)  # 5-minute TTL
    
    return multiplier
```

### Payment Service

#### Problem

Process payments securely, handle failures, support multiple payment methods, process refunds.

#### Solution: Payment Processing Pipeline

**Payment Flow**:

```
1. Trip completes
   └─> Ride Service triggers payment

2. Payment Service
   ├─> Validates payment method
   ├─> Calculates final fare
   ├─> Creates payment record (status: PENDING)
   └─> Sends to Payment Gateway

3. Payment Gateway (Stripe, PayPal, etc.)
   ├─> Processes payment
   ├─> Returns transaction_id
   └─> Webhook callback

4. Payment Service (webhook handler)
   ├─> Updates payment status
   ├─> Updates ride payment_status
   ├─> Updates driver earnings
   └─> Sends receipt notification
```

**Payment Processing**:

```python
class PaymentService:
    def process_payment(self, ride_id):
        """
        Process payment for completed ride
        """
        ride = self.get_ride(ride_id)
        
        # Create payment record
        payment = Payment(
            ride_id=ride_id,
            rider_id=ride.rider_id,
            amount=ride.actual_fare,
            payment_method_id=ride.payment_method_id,
            status='PENDING'
        )
        payment.save()
        
        # Process payment
        try:
            result = self.payment_gateway.charge(
                amount=ride.actual_fare,
                payment_method_id=ride.payment_method_id,
                description=f"Ride {ride_id}"
            )
            
            # Update payment
            payment.transaction_id = result.transaction_id
            payment.status = 'COMPLETED'
            payment.processed_at = time.now()
            payment.save()
            
            # Update ride
            ride.payment_status = 'COMPLETED'
            ride.save()
            
            # Update driver earnings
            self.update_driver_earnings(ride.driver_id, ride.actual_fare)
            
            # Send receipt
            self.send_receipt(ride.rider_id, payment)
            
        except PaymentException as e:
            # Handle payment failure
            payment.status = 'FAILED'
            payment.save()
            
            # Retry logic or notify user
            self.handle_payment_failure(ride, payment, e)
```

**Idempotency**:

```python
def process_payment(ride_id, idempotency_key):
    """
    Process payment with idempotency
    """
    # Check if already processed
    existing_payment = Payment.objects.filter(
        ride_id=ride_id,
        idempotency_key=idempotency_key
    ).first()
    
    if existing_payment:
        return existing_payment  # Return existing result
    
    # Process payment with idempotency key
    payment = create_and_process_payment(
        ride_id=ride_id,
        idempotency_key=idempotency_key
    )
    
    return payment
```

**Retry Logic**:

```python
def process_payment_with_retry(ride_id, max_retries=3):
    """
    Process payment with exponential backoff retry
    """
    for attempt in range(max_retries):
        try:
            return process_payment(ride_id)
        except PaymentException as e:
            if attempt == max_retries - 1:
                # Final attempt failed
                handle_payment_failure(ride_id, e)
                raise
            
            # Exponential backoff
            wait_time = 2 ** attempt  # 1s, 2s, 4s
            time.sleep(wait_time)
```

### Notification Service

#### Problem

Send real-time notifications to riders and drivers for ride status updates, payment confirmations, etc.

#### Solution: Multi-Channel Notification System

**Notification Types**:

- Push notifications (mobile app)
- SMS notifications
- Email notifications
- In-app notifications

**Notification Service**:

```python
class NotificationService:
    def send_ride_matched(self, rider_id, driver_info):
        """
        Notify rider that driver is matched
        """
        notification = {
            "type": "RIDE_MATCHED",
            "rider_id": rider_id,
            "message": f"Driver {driver_info.name} is on the way",
            "data": {
                "driver": driver_info,
                "eta": driver_info.eta
            }
        }
        
        # Send push notification
        self.push_service.send(
            user_id=rider_id,
            notification=notification
        )
        
        # Send SMS
        self.sms_service.send(
            phone=rider_info.phone,
            message=f"Your driver {driver_info.name} is on the way. ETA: {driver_info.eta} minutes"
        )
    
    def send_trip_completed(self, rider_id, ride_info):
        """
        Notify rider that trip is completed
        """
        notification = {
            "type": "TRIP_COMPLETED",
            "rider_id": rider_id,
            "message": "Your trip has been completed",
            "data": {
                "fare": ride_info.fare,
                "receipt_url": ride_info.receipt_url
            }
        }
        
        # Send push notification
        self.push_service.send(
            user_id=rider_id,
            notification=notification
        )
        
        # Send email receipt
        self.email_service.send_receipt(
            email=rider_info.email,
            ride=ride_info
        )
```

**Message Queue Integration**:

```python
# Publish notification events to Kafka
kafka_producer.send(
    topic="notifications",
    value={
        "user_id": rider_id,
        "type": "RIDE_MATCHED",
        "message": "...",
        "channels": ["push", "sms"]
    }
)

# Notification Service consumes from Kafka
@kafka_consumer(topic="notifications")
def handle_notification(event):
    notification_service.send(event)
```

### Trip Management Service

#### Problem

Manage trip lifecycle: request → match → pickup → in-progress → complete.

#### Solution: State Machine-Based Trip Management

**Trip State Machine**:

```
REQUESTED → MATCHED → DRIVER_ARRIVED → IN_PROGRESS → COMPLETED
     │         │            │              │
     └─────────┴────────────┴──────────────┴──→ CANCELLED
```

**State Transitions**:

```python
class TripStateMachine:
    TRANSITIONS = {
        'REQUESTED': ['MATCHED', 'CANCELLED'],
        'MATCHED': ['DRIVER_ARRIVED', 'CANCELLED'],
        'DRIVER_ARRIVED': ['IN_PROGRESS', 'CANCELLED'],
        'IN_PROGRESS': ['COMPLETED', 'CANCELLED'],
        'COMPLETED': [],
        'CANCELLED': []
    }
    
    def transition(self, ride, new_status):
        """
        Transition ride to new status
        """
        current_status = ride.status
        
        if new_status not in self.TRANSITIONS.get(current_status, []):
            raise InvalidTransitionError(
                f"Cannot transition from {current_status} to {new_status}"
            )
        
        # Update status
        ride.status = new_status
        
        # Update timestamps
        if new_status == 'MATCHED':
            ride.matched_at = time.now()
        elif new_status == 'IN_PROGRESS':
            ride.started_at = time.now()
        elif new_status == 'COMPLETED':
            ride.completed_at = time.now()
        elif new_status == 'CANCELLED':
            ride.cancelled_at = time.now()
        
        ride.save()
        
        # Trigger side effects
        self.handle_status_change(ride, new_status)
```

### Rating and Review Service

#### Problem

Allow riders and drivers to rate each other after trip completion.

#### Solution: Two-Way Rating System

**Rating Flow**:

```python
class RatingService:
    def rate_driver(self, ride_id, rider_id, rating, review=None):
        """
        Rate driver after trip
        """
        ride = self.get_ride(ride_id)
        
        # Validate ride is completed
        if ride.status != 'COMPLETED':
            raise InvalidRideStatusError("Ride must be completed")
        
        # Validate rider
        if ride.rider_id != rider_id:
            raise UnauthorizedError("Not your ride")
        
        # Create rating
        rating_record = Rating(
            ride_id=ride_id,
            rated_user_id=ride.driver_id,
            rating_user_id=rider_id,
            rating=rating,
            review=review
        )
        rating_record.save()
        
        # Update driver average rating
        self.update_driver_rating(ride.driver_id)
        
        return rating_record
    
    def update_driver_rating(self, driver_id):
        """
        Recalculate driver average rating
        """
        ratings = Rating.objects.filter(rated_user_id=driver_id)
        avg_rating = ratings.aggregate(Avg('rating'))['rating__avg']
        
        driver = Driver.objects.get(driver_id=driver_id)
        driver.rating = avg_rating
        driver.save()
```

**Batch Rating Update**:

```python
# Update ratings in batch (for performance)
@periodic_task(run_every=timedelta(minutes=5))
def update_driver_ratings():
    """
    Batch update driver ratings
    """
    drivers = Driver.objects.all()
    
    for driver in drivers:
        ratings = Rating.objects.filter(rated_user_id=driver.driver_id)
        avg_rating = ratings.aggregate(Avg('rating'))['rating__avg']
        
        driver.rating = avg_rating
        driver.save()
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

**Location Service Scaling**:
- Redis Cluster for geospatial queries
- Partition by geography (city/region)
- Use Elasticsearch for complex location queries

### Caching Strategy

**Cache Layers**:
1. **Application Cache**: Cache frequently accessed data (driver info, ride details)
2. **Redis Cache**: Cache location data, surge multipliers
3. **CDN**: Cache static assets (maps, images)

**Cache Invalidation**:
- TTL-based expiration
- Event-driven invalidation (on ride status change)
- Cache-aside pattern

### Database Optimization

**Indexing**:
- Index on frequently queried fields (user_id, ride_id, status)
- Geospatial indexes for location queries
- Composite indexes for complex queries

**Query Optimization**:
- Use read replicas for analytics queries
- Batch operations where possible
- Pagination for large result sets

### Message Queue

**Kafka Topics**:
- `ride-requests`: Ride request events
- `ride-updates`: Ride status updates
- `location-updates`: Location update events
- `payments`: Payment events
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
- Role-based access control (RBAC)
- API rate limiting

### Payment Security

- PCI DSS compliance
- Tokenization for payment methods
- Encryption for sensitive data
- Secure payment gateway integration

### Data Protection

- Encrypt sensitive data at rest
- Use HTTPS for all communications
- PII (Personally Identifiable Information) protection
- GDPR compliance

### Driver Verification

- Background checks
- License verification
- Vehicle inspection
- Insurance verification

## Monitoring & Observability

### Metrics

- **Business Metrics**: Rides per day, revenue, driver earnings
- **Technical Metrics**: API latency, error rates, throughput
- **Location Metrics**: Location update latency, geospatial query performance
- **Payment Metrics**: Payment success rate, processing time

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

### Consistency vs Availability

- **Strong Consistency**: Payments, ride status
- **Eventual Consistency**: Ratings, driver locations
- **Trade-off**: Accept eventual consistency for location updates to improve availability

### Latency vs Accuracy

- **Location Updates**: 4-second updates (balance between accuracy and load)
- **Matching**: Real-time matching (low latency) vs optimal matching (higher latency)
- **Trade-off**: Prefer low latency for better user experience

### Cost vs Performance

- **Caching**: More cache = better performance but higher cost
- **Database Replicas**: More replicas = better read performance but higher cost
- **Trade-off**: Optimize for cost while meeting performance requirements

### Complexity vs Features

- **Matching Algorithm**: Simple distance-based vs complex ML-based
- **Pricing**: Fixed pricing vs dynamic surge pricing
- **Trade-off**: Start simple, add complexity as needed

## What Interviewers Look For

### Geospatial Systems Skills

1. **Real-Time Matching**
   - Geospatial index usage (Redis Geo, Elasticsearch)
   - Efficient driver-rider matching
   - Distance calculations
   - **Red Flags**: No geospatial index, inefficient matching, slow queries

2. **Location Tracking**
   - Real-time location updates
   - Time-series data storage
   - Efficient location queries
   - **Red Flags**: No real-time tracking, inefficient storage, slow queries

3. **Dynamic Pricing**
   - Surge pricing algorithm
   - Demand/supply calculation
   - Grid-based pricing
   - **Red Flags**: Fixed pricing, no surge, poor algorithm

### Distributed Systems Skills

1. **State Management**
   - Trip state machine
   - State transitions
   - Consistency guarantees
   - **Red Flags**: No state machine, inconsistent states

2. **Microservices Architecture**
   - Service decomposition
   - Clear boundaries
   - Service communication
   - **Red Flags**: Monolithic, unclear boundaries, tight coupling

3. **Scalability Design**
   - Geographic sharding
   - Horizontal scaling
   - Load balancing
   - **Red Flags**: No sharding, vertical scaling, bottlenecks

### Problem-Solving Approach

1. **Scale Thinking**
   - Millions of concurrent rides
   - Real-time location updates
   - Global distribution
   - **Red Flags**: Small-scale design, no real-time, single region

2. **Trade-off Analysis**
   - Latency vs accuracy
   - Consistency vs availability
   - **Red Flags**: No trade-offs, dogmatic choices

3. **Edge Cases**
   - No available drivers
   - Driver cancellation
   - Payment failures
   - **Red Flags**: Ignoring edge cases, no handling

### System Design Skills

1. **Component Design**
   - Matching service
   - Location service
   - Pricing service
   - **Red Flags**: Monolithic, unclear boundaries

2. **Payment Processing**
   - Idempotency
   - Retry logic
   - Failure handling
   - **Red Flags**: No idempotency, no retry, payment loss

3. **Real-Time Updates**
   - WebSocket/SSE
   - Pub/sub architecture
   - **Red Flags**: Polling, high latency, no real-time

### Communication Skills

1. **Architecture Explanation**
   - Clear service design
   - Data flow understanding
   - **Red Flags**: Unclear design, no flow

2. **Algorithm Explanation**
   - Can explain matching algorithm
   - Understands pricing
   - **Red Flags**: No understanding, vague

### Meta-Specific Focus

1. **Real-Time Systems Expertise**
   - Geospatial systems knowledge
   - Low-latency design
   - **Key**: Show real-time systems knowledge

2. **Product System Design**
   - End-to-end thinking
   - User experience consideration
   - **Key**: Demonstrate product thinking

## Summary

### Key Takeaways

1. **Real-Time Matching**: Use geospatial indexes (Redis Geo, Elasticsearch) for efficient driver-rider matching
2. **Location Tracking**: Real-time location updates every 4 seconds, use time-series database for history
3. **Dynamic Pricing**: Surge pricing based on demand/supply ratio, cache multipliers for performance
4. **Payment Processing**: Secure payment processing with idempotency and retry logic
5. **Microservices Architecture**: Separate services for matching, location, pricing, payment, notifications
6. **Scalability**: Horizontal scaling, caching, read replicas, message queues
7. **Geographic Sharding**: Shard by city/region for locality
8. **State Machine**: Use state machine for trip lifecycle management

### Architecture Highlights

- **API Gateway**: Single entry point, load balancing, routing
- **Microservices**: Ride, Matching, Location, Pricing, Payment, Notification services
- **Message Queue**: Kafka for event-driven architecture
- **Data Stores**: PostgreSQL (primary), Redis (cache + geo), TimescaleDB (location history)
- **Real-Time**: WebSocket/SSE for location updates
- **External Services**: Payment gateway, SMS gateway, push notification service

### Scale Numbers

- **Users**: 100M+ users
- **Rides**: 15M rides/day, 1M concurrent rides (peak)
- **Location Updates**: 375K updates/second
- **API Traffic**: 26K QPS (peak)
- **Storage**: 28.5TB/year (with replication: 85TB)

### Common Interview Questions

1. **How do you match riders with drivers?**
   - Geospatial queries, scoring algorithm, real-time matching

2. **How do you handle surge pricing?**
   - Demand/supply ratio, grid-based calculation, caching

3. **How do you track locations in real-time?**
   - Redis Geo index, time-series database, WebSocket updates

4. **How do you ensure payment reliability?**
   - Idempotency, retry logic, webhook callbacks, failure handling

5. **How do you scale to millions of users?**
   - Horizontal scaling, caching, database sharding, message queues

This design provides a solid foundation for a ride-sharing service like Uber, covering all major components and addressing scalability, reliability, and performance challenges.

