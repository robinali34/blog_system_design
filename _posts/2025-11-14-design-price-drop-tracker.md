---
layout: post
title: "Design a Price Drop Tracker System - System Design Interview"
date: 2025-11-14
categories: [System Design, Interview Example, Distributed Systems, E-commerce, Web Scraping, Real-time Systems]
excerpt: "A comprehensive guide to designing a price drop tracker system like CamelCamelCamel or Honey, covering web scraping, price monitoring, notification delivery, user tracking preferences, and architectural patterns for tracking millions of products across multiple e-commerce platforms."
---

## Introduction

A price drop tracker system monitors product prices on e-commerce platforms (like Amazon) and notifies users when prices drop below their target thresholds. Systems like CamelCamelCamel and Honey track millions of products, handle billions of price checks, and send millions of notifications daily.

This post provides a detailed walkthrough of designing a scalable price drop tracker, covering web scraping, price monitoring, change detection, notification delivery, user preference management, and handling rate limits from e-commerce APIs. This is a common system design interview question that tests your understanding of distributed systems, web scraping, data pipelines, real-time processing, and notification systems.

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

**Design a price drop tracker system similar to CamelCamelCamel or Honey with the following features:**

1. Track product prices on e-commerce platforms (Amazon, eBay, etc.)
2. Allow users to add products to track
3. Set target prices or percentage drop thresholds
4. Monitor prices continuously
5. Detect price drops
6. Send notifications (email, push, SMS) when price drops
7. Display price history charts
8. Support multiple e-commerce platforms
9. Handle rate limits and anti-scraping measures
10. Provide price alerts and recommendations

**Scale Requirements:**
- 50 million+ users
- 100 million+ tracked products
- 1 billion+ price checks per day
- Peak: 50,000 price checks per second
- Average products per user: 10
- Popular products: 1 million+ trackers
- Must respect rate limits and avoid blocking
- Price check frequency: Every 1-24 hours per product

## Requirements

### Functional Requirements

**Core Features:**
1. **Product Tracking**: Add products by URL or product ID
2. **Price Monitoring**: Continuously monitor product prices
3. **Price Drop Detection**: Detect when price drops below threshold
4. **Notifications**: Send alerts via email, push, SMS
5. **Price History**: Store and display historical prices
6. **Multi-Platform**: Support Amazon, eBay, Walmart, etc.
7. **Target Price**: Set specific target prices
8. **Percentage Drop**: Set percentage drop thresholds
9. **Price Charts**: Display price history charts
10. **Product Search**: Search products to track

**Out of Scope:**
- Product reviews and ratings
- Product recommendations
- Coupon code management
- Mobile app (focus on web API)
- Payment processing
- User authentication (assume existing auth system)

### Non-Functional Requirements

1. **Availability**: 99.9% uptime
2. **Reliability**: No missed price drops, accurate price data
3. **Performance**: 
   - Price check: < 2 seconds
   - Notification delivery: < 5 minutes after price drop
   - Price history query: < 500ms
4. **Scalability**: Handle 50K+ price checks per second
5. **Accuracy**: Accurate price detection, handle price variations
6. **Rate Limiting**: Respect e-commerce platform rate limits
7. **Cost Efficiency**: Minimize API costs and scraping overhead

## Capacity Estimation

### Traffic Estimates

- **Total Users**: 50 million
- **Daily Active Users (DAU)**: 5 million
- **Tracked Products**: 100 million
- **Price Checks per Day**: 1 billion
- **Average Checks per Product**: 10 per day
- **Peak Price Check Rate**: 50,000 per second
- **Normal Price Check Rate**: 10,000 per second
- **Notifications per Day**: 10 million
- **New Products Added per Day**: 1 million

### Storage Estimates

**Product Data:**
- 100M products × 1KB = 100GB
- Product metadata, URLs, platform info

**Price History:**
- 1B price checks/day × 100 bytes = 100GB/day
- 30-day retention: ~3TB
- 1-year archive: ~36TB
- 5-year archive: ~180TB

**User Tracking Preferences:**
- 50M users × 10 products × 200 bytes = 100GB

**Notifications:**
- 10M notifications/day × 500 bytes = 5GB/day
- 7-day retention: ~35GB

**Total Storage**: ~180TB

### Bandwidth Estimates

**Normal Traffic:**
- 10,000 price checks/sec × 10KB = 100MB/s = 800Mbps
- Scraping responses, API calls

**Peak Traffic:**
- 50,000 price checks/sec × 10KB = 500MB/s = 4Gbps

**Notification Delivery:**
- 10M notifications/day × 1KB = 10GB/day = ~115KB/s = ~1Mbps

**Total Peak**: ~4Gbps

## Core Entities

### Product
- `product_id` (UUID)
- `platform` (amazon, ebay, walmart, etc.)
- `product_url` (VARCHAR)
- `product_asin` (VARCHAR, for Amazon)
- `product_name` (VARCHAR)
- `current_price` (DECIMAL)
- `currency` (VARCHAR)
- `availability` (in_stock, out_of_stock, unknown)
- `last_checked_at` (TIMESTAMP)
- `check_frequency_hours` (INT)
- `tracker_count` (INT)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

### Price History
- `price_id` (UUID)
- `product_id` (UUID)
- `price` (DECIMAL)
- `currency` (VARCHAR)
- `availability` (VARCHAR)
- `checked_at` (TIMESTAMP)
- `source` (scraper, api, manual)

### User Tracking
- `tracking_id` (UUID)
- `user_id` (UUID)
- `product_id` (UUID)
- `target_price` (DECIMAL, optional)
- `percentage_drop` (DECIMAL, optional)
- `notification_channels` (JSON: email, push, sms)
- `is_active` (BOOLEAN)
- `last_notified_at` (TIMESTAMP)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

### Notification
- `notification_id` (UUID)
- `user_id` (UUID)
- `product_id` (UUID)
- `old_price` (DECIMAL)
- `new_price` (DECIMAL)
- `price_drop` (DECIMAL)
- `percentage_drop` (DECIMAL)
- `channel` (email, push, sms)
- `status` (pending, sent, failed)
- `sent_at` (TIMESTAMP)
- `created_at` (TIMESTAMP)

### User
- `user_id` (UUID)
- `email` (VARCHAR)
- `phone` (VARCHAR, optional)
- `notification_preferences` (JSON)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

## API

### 1. Add Product to Track
```
POST /api/v1/products/track
Request:
{
  "product_url": "https://amazon.com/dp/B08XYZ123",
  "target_price": 99.99,
  "percentage_drop": null,
  "notification_channels": ["email", "push"]
}

Response:
{
  "tracking_id": "uuid",
  "product_id": "uuid",
  "product_name": "Example Product",
  "current_price": 149.99,
  "target_price": 99.99,
  "status": "tracking"
}
```

### 2. Get Tracked Products
```
GET /api/v1/users/{user_id}/trackings?limit=20&offset=0
Response:
{
  "trackings": [
    {
      "tracking_id": "uuid",
      "product": {
        "product_id": "uuid",
        "product_name": "Example Product",
        "current_price": 149.99,
        "price_change": -10.00,
        "percentage_change": -6.25,
        "last_checked_at": "2025-11-13T10:00:00Z"
      },
      "target_price": 99.99,
      "is_active": true
    }
  ],
  "total": 50,
  "limit": 20,
  "offset": 0
}
```

### 3. Update Tracking Preferences
```
PUT /api/v1/trackings/{tracking_id}
Request:
{
  "target_price": 89.99,
  "notification_channels": ["email", "sms"]
}

Response:
{
  "tracking_id": "uuid",
  "target_price": 89.99,
  "notification_channels": ["email", "sms"],
  "updated_at": "2025-11-13T10:05:00Z"
}
```

### 4. Remove Tracking
```
DELETE /api/v1/trackings/{tracking_id}
Response:
{
  "success": true,
  "message": "Tracking removed"
}
```

### 5. Get Price History
```
GET /api/v1/products/{product_id}/history?days=30
Response:
{
  "product_id": "uuid",
  "product_name": "Example Product",
  "price_history": [
    {
      "price": 149.99,
      "checked_at": "2025-11-13T10:00:00Z"
    },
    {
      "price": 159.99,
      "checked_at": "2025-11-12T10:00:00Z"
    }
  ],
  "current_price": 149.99,
  "lowest_price": 129.99,
  "highest_price": 179.99,
  "average_price": 149.50
}
```

### 6. Search Products
```
GET /api/v1/products/search?q=laptop&platform=amazon&limit=20
Response:
{
  "products": [
    {
      "product_id": "uuid",
      "product_name": "Laptop Example",
      "current_price": 999.99,
      "platform": "amazon",
      "product_url": "https://amazon.com/dp/B08XYZ123"
    }
  ],
  "total": 100,
  "limit": 20,
  "offset": 0
}
```

## Data Flow

### Product Addition Flow

1. **User Adds Product**:
   - User submits product URL
   - **Client** sends request to **API Gateway**
   - **API Gateway** routes to **Product Service**

2. **Product Processing**:
   - **Product Service**:
     - Extracts product ID/ASIN from URL
     - Checks if product already exists
     - If new, creates product record
     - Fetches initial price from **Scraper Service**
     - Creates user tracking record

3. **Initial Price Check**:
   - **Scraper Service**:
     - Determines platform (Amazon, eBay, etc.)
     - Selects appropriate scraper
     - Fetches product page
     - Extracts price, availability, product name
     - Stores price in **Price History**

4. **Response**:
   - **Product Service** returns product and tracking info
   - **Client** displays product with current price

### Price Monitoring Flow

1. **Scheduled Price Check**:
   - **Price Monitor Scheduler** identifies products to check
   - Determines check frequency based on:
     - Number of trackers (popular products checked more frequently)
     - User preferences
     - Product volatility

2. **Price Check Execution**:
   - **Price Monitor Service**:
     - Gets product details
     - Queues price check job to **Message Queue**
     - **Scraper Worker** picks up job

3. **Price Scraping**:
   - **Scraper Worker**:
     - Selects scraper for platform
     - Respects rate limits (uses proxy rotation)
     - Fetches product page
     - Extracts price and metadata
     - Handles errors (retry, fallback)

4. **Price Storage**:
   - **Scraper Worker** stores price in **Price History**
   - Updates product current price
   - Publishes price update event

5. **Price Drop Detection**:
   - **Price Drop Detector**:
     - Compares new price with previous price
     - Checks against user target prices
     - Identifies price drops
     - Creates notification records

6. **Notification Delivery**:
   - **Notification Service**:
     - Gets pending notifications
     - Sends via email, push, SMS
     - Updates notification status

### Price Drop Detection Flow

1. **Price Update Event**:
   - New price stored in **Price History**
   - Price update event published to **Message Queue**

2. **Price Drop Detection**:
   - **Price Drop Detector**:
     - Gets all active trackings for product
     - For each tracking:
       - Compares new price with target price
       - Calculates percentage drop
       - Checks if threshold met
       - Creates notification if drop detected

3. **Notification Creation**:
   - **Notification Service**:
     - Creates notification records
     - Queues notification jobs
     - Respects user notification preferences

4. **Notification Delivery**:
   - **Notification Workers**:
     - Process notification queue
     - Send via appropriate channel
     - Update notification status
     - Handle failures (retry logic)

## Database Design

### Schema Design

**Products Table:**
```sql
CREATE TABLE products (
    product_id UUID PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    product_url VARCHAR(1000) NOT NULL,
    product_asin VARCHAR(50) NULL,
    product_name VARCHAR(500) NOT NULL,
    current_price DECIMAL(10, 2) NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    availability VARCHAR(50) DEFAULT 'unknown',
    last_checked_at TIMESTAMP NULL,
    check_frequency_hours INT DEFAULT 24,
    tracker_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_platform (platform),
    INDEX idx_asin (product_asin),
    INDEX idx_last_checked (last_checked_at),
    INDEX idx_tracker_count (tracker_count),
    UNIQUE KEY uk_platform_url (platform, product_url(500))
);
```

**Price History Table (Sharded by product_id):**
```sql
CREATE TABLE price_history_0 (
    price_id UUID PRIMARY KEY,
    product_id UUID NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    availability VARCHAR(50),
    checked_at TIMESTAMP DEFAULT NOW(),
    source VARCHAR(50) DEFAULT 'scraper',
    INDEX idx_product_id (product_id),
    INDEX idx_checked_at (checked_at DESC),
    INDEX idx_product_checked (product_id, checked_at DESC)
);
-- Similar tables: price_history_1, price_history_2, ..., price_history_N
```

**User Trackings Table:**
```sql
CREATE TABLE user_trackings (
    tracking_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    product_id UUID NOT NULL,
    target_price DECIMAL(10, 2) NULL,
    percentage_drop DECIMAL(5, 2) NULL,
    notification_channels JSON NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_notified_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_id (user_id),
    INDEX idx_product_id (product_id),
    INDEX idx_active (is_active),
    INDEX idx_user_active (user_id, is_active),
    UNIQUE KEY uk_user_product (user_id, product_id)
);
```

**Notifications Table:**
```sql
CREATE TABLE notifications (
    notification_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    product_id UUID NOT NULL,
    tracking_id UUID NOT NULL,
    old_price DECIMAL(10, 2) NOT NULL,
    new_price DECIMAL(10, 2) NOT NULL,
    price_drop DECIMAL(10, 2) NOT NULL,
    percentage_drop DECIMAL(5, 2) NOT NULL,
    channel VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    sent_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at DESC),
    INDEX idx_user_status (user_id, status)
);
```

**Users Table:**
```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) NULL,
    notification_preferences JSON,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_email (email)
);
```

### Database Sharding Strategy

**Price History Table Sharding:**
- Shard by product_id using consistent hashing
- 1000 shards: `shard_id = hash(product_id) % 1000`
- All price history for a product in same shard
- Enables efficient price history queries

**Shard Key Selection:**
- `product_id` ensures all prices for a product are in same shard
- Enables efficient queries for product price history
- Prevents cross-shard queries for single product

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
       │ HTTP
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
│  Product    │ │  Price     │ │ Notification│ │  Search    │ │  User      │
│  Service    │ │  Monitor   │ │  Service    │ │  Service   │ │  Service   │
└──────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
       │              │              │              │              │
       │              │              │              │              │
┌──────▼──────────────▼──────────────▼──────────────▼──────────────▼──────┐
│              Message Queue (Kafka)                                        │
│              - Price check jobs                                            │
│              - Price update events                                         │
│              - Notification jobs                                           │
└──────┬───────────────────────────────────────────────────────────────────┘
       │
       │
┌──────▼───────────────────────────────────────────────────────────────────┐
│         Scraper Service                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                              │
│  │ Amazon    │  │ eBay      │  │ Walmart   │                              │
│  │ Scraper   │  │ Scraper   │  │ Scraper   │                              │
│  └──────────┘  └──────────┘  └──────────┘                              │
│                                                                           │
│  ┌──────────────────────────────────────────────────────┐                │
│  │ Proxy Pool Manager                                    │                │
│  │ - IP Rotation                                          │                │
│  │ - Rate Limit Management                               │                │
│  └──────────────────────────────────────────────────────┘                │
└──────┬───────────────────────────────────────────────────────────────────┘
       │
       │
┌──────▼───────────────────────────────────────────────────────────────────┐
│         Price Drop Detector                                               │
│         - Compare prices                                                  │
│         - Check thresholds                                                │
│         - Create notifications                                            │
└──────┬───────────────────────────────────────────────────────────────────┘
       │
       │
┌──────▼───────────────────────────────────────────────────────────────────┐
│         Database Cluster (Sharded)                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                              │
│  │ Products │  │ Price     │  │ User      │                              │
│  │ DB       │  │ History   │  │ Trackings │                              │
│  │          │  │ (Sharded) │  │ DB        │                              │
│  └──────────┘  └──────────┘  └──────────┘                              │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│              Cache Layer (Redis)                                          │
│  - Product metadata                                                       │
│  - Current prices                                                         │
│  - Rate limit counters                                                    │
│  - Popular products                                                       │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│         Notification Workers                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                              │
│  │ Email     │  │ Push      │  │ SMS       │                              │
│  │ Worker    │  │ Worker    │  │ Worker    │                              │
│  └──────────┘  └──────────┘  └──────────┘                              │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│         Price Monitor Scheduler                                            │
│         - Schedule price checks                                            │
│         - Determine check frequency                                        │
└───────────────────────────────────────────────────────────────────────────┘
```

## Deep Dive

### Component Design

#### 1. Scraper Service

**Responsibilities:**
- Scrape product pages from e-commerce platforms
- Extract price, availability, product name
- Handle rate limits and anti-scraping measures
- Rotate proxies and user agents
- Retry failed requests

**Key Design Decisions:**
- **Platform-Specific Scrapers**: Different scrapers for each platform
- **Proxy Rotation**: Rotate IPs to avoid blocking
- **Rate Limiting**: Respect platform rate limits
- **Error Handling**: Retry logic, fallback mechanisms
- **HTML Parsing**: Use CSS selectors or XPath

**Critical Requirements:**
- **Accuracy**: Extract correct price
- **Reliability**: Handle page structure changes
- **Rate Limiting**: Avoid getting blocked
- **Performance**: Fast scraping (< 2 seconds)

**Implementation:**
```python
class ScraperService:
    def __init__(self):
        self.scrapers = {
            'amazon': AmazonScraper(),
            'ebay': EbayScraper(),
            'walmart': WalmartScraper()
        }
        self.proxy_pool = ProxyPool()
        self.rate_limiter = RateLimiter()
    
    def scrape_product(self, product_id, platform):
        scraper = self.scrapers.get(platform)
        if not scraper:
            raise Exception(f"Unsupported platform: {platform}")
        
        # Get proxy
        proxy = self.proxy_pool.get_proxy(platform)
        
        # Check rate limit
        if not self.rate_limiter.can_scrape(platform, proxy):
            raise RateLimitError("Rate limit exceeded")
        
        try:
            # Scrape product page
            product_data = scraper.scrape(product_id, proxy)
            
            # Update rate limit
            self.rate_limiter.record_scrape(platform, proxy)
            
            return product_data
        except ScrapingError as e:
            # Mark proxy as bad
            self.proxy_pool.mark_bad(proxy)
            raise
        finally:
            # Return proxy to pool
            self.proxy_pool.return_proxy(proxy)

class AmazonScraper:
    def scrape(self, product_asin, proxy):
        url = f"https://www.amazon.com/dp/{product_asin}"
        
        # Make request with proxy
        response = requests.get(
            url,
            proxies={'http': proxy, 'https': proxy},
            headers={'User-Agent': self.get_random_user_agent()},
            timeout=10
        )
        
        if response.status_code != 200:
            raise ScrapingError(f"HTTP {response.status_code}")
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract price
        price_element = soup.select_one('#priceblock_ourprice, #priceblock_dealprice')
        if not price_element:
            raise ScrapingError("Price not found")
        
        price_text = price_element.get_text()
        price = self.parse_price(price_text)
        
        # Extract availability
        availability = self.extract_availability(soup)
        
        # Extract product name
        product_name = soup.select_one('#productTitle')
        if product_name:
            product_name = product_name.get_text().strip()
        
        return {
            'price': price,
            'currency': 'USD',
            'availability': availability,
            'product_name': product_name,
            'checked_at': datetime.now()
        }
```

#### 2. Price Monitor Service

**Responsibilities:**
- Schedule price checks for products
- Determine check frequency
- Queue price check jobs
- Handle check failures

**Key Design Decisions:**
- **Dynamic Frequency**: More frequent checks for popular products
- **Priority Queue**: Prioritize products with more trackers
- **Batch Processing**: Batch checks for efficiency
- **Failure Handling**: Retry failed checks

**Implementation:**
```python
class PriceMonitorService:
    def __init__(self):
        self.scheduler = Scheduler()
        self.message_queue = MessageQueue()
    
    def schedule_price_checks(self):
        # Get products that need checking
        products = self.get_products_to_check()
        
        for product in products:
            # Determine check frequency
            frequency = self.calculate_check_frequency(product)
            
            # Queue price check job
            self.message_queue.publish('price_check', {
                'product_id': product.product_id,
                'platform': product.platform,
                'priority': product.tracker_count
            })
    
    def calculate_check_frequency(self, product):
        # Base frequency: 24 hours
        base_frequency = 24
        
        # More trackers = more frequent checks
        if product.tracker_count > 1000:
            return 1  # Check every hour
        elif product.tracker_count > 100:
            return 6  # Check every 6 hours
        elif product.tracker_count > 10:
            return 12  # Check every 12 hours
        else:
            return base_frequency
    
    def get_products_to_check(self):
        # Get products that haven't been checked recently
        now = datetime.now()
        check_threshold = now - timedelta(hours=24)
        
        return db.query(Product).filter(
            Product.last_checked_at < check_threshold,
            Product.tracker_count > 0
        ).order_by(
            Product.tracker_count.desc()
        ).limit(10000).all()
```

#### 3. Price Drop Detector

**Responsibilities:**
- Compare new prices with previous prices
- Check against user target prices
- Detect price drops
- Create notifications

**Key Design Decisions:**
- **Threshold Detection**: Check target price and percentage drop
- **Notification Deduplication**: Avoid duplicate notifications
- **Price Change Calculation**: Calculate absolute and percentage drops
- **Batch Processing**: Process multiple trackings efficiently

**Implementation:**
```python
class PriceDropDetector:
    def detect_price_drops(self, product_id, new_price):
        # Get product
        product = get_product(product_id)
        
        # Get previous price
        previous_price = self.get_previous_price(product_id)
        
        if not previous_price:
            return []  # No previous price
        
        # Calculate price change
        price_drop = previous_price - new_price
        percentage_drop = (price_drop / previous_price) * 100
        
        # Get all active trackings for this product
        trackings = get_active_trackings(product_id)
        
        notifications = []
        
        for tracking in trackings:
            # Check if price drop meets threshold
            should_notify = False
            
            # Check target price
            if tracking.target_price and new_price <= tracking.target_price:
                should_notify = True
            
            # Check percentage drop
            if tracking.percentage_drop and percentage_drop >= tracking.percentage_drop:
                should_notify = True
            
            # Check if already notified recently (avoid spam)
            if tracking.last_notified_at:
                time_since_notification = datetime.now() - tracking.last_notified_at
                if time_since_notification < timedelta(hours=1):
                    should_notify = False  # Don't notify too frequently
            
            if should_notify:
                # Create notification
                notification = Notification(
                    user_id=tracking.user_id,
                    product_id=product_id,
                    tracking_id=tracking.tracking_id,
                    old_price=previous_price,
                    new_price=new_price,
                    price_drop=price_drop,
                    percentage_drop=percentage_drop,
                    channel=tracking.notification_channels[0],  # Primary channel
                    status='pending'
                )
                notification.save()
                notifications.append(notification)
                
                # Update tracking
                tracking.last_notified_at = datetime.now()
                tracking.save()
        
        return notifications
```

#### 4. Notification Service

**Responsibilities:**
- Send notifications via multiple channels
- Handle notification failures
- Retry failed notifications
- Manage notification preferences

**Key Design Decisions:**
- **Multi-Channel**: Email, push, SMS
- **Retry Logic**: Retry failed notifications
- **Rate Limiting**: Respect notification rate limits
- **Template System**: Use templates for notifications

**Implementation:**
```python
class NotificationService:
    def __init__(self):
        self.email_service = EmailService()
        self.push_service = PushService()
        self.sms_service = SMSService()
        self.message_queue = MessageQueue()
    
    def send_notification(self, notification):
        # Get user preferences
        user = get_user(notification.user_id)
        channels = notification.channel.split(',')
        
        for channel in channels:
            if channel == 'email':
                self.send_email_notification(notification, user)
            elif channel == 'push':
                self.send_push_notification(notification, user)
            elif channel == 'sms':
                self.send_sms_notification(notification, user)
    
    def send_email_notification(self, notification, user):
        product = get_product(notification.product_id)
        
        subject = f"Price Drop Alert: {product.product_name}"
        body = self.render_email_template('price_drop', {
            'product_name': product.product_name,
            'old_price': notification.old_price,
            'new_price': notification.new_price,
            'price_drop': notification.price_drop,
            'percentage_drop': notification.percentage_drop,
            'product_url': product.product_url
        })
        
        try:
            self.email_service.send(user.email, subject, body)
            notification.status = 'sent'
            notification.sent_at = datetime.now()
            notification.save()
        except Exception as e:
            notification.status = 'failed'
            notification.save()
            # Queue for retry
            self.message_queue.publish('notification_retry', {
                'notification_id': notification.notification_id
            })
```

### Detailed Design

#### Handling Rate Limits

**Challenge:** E-commerce platforms have rate limits and anti-scraping measures

**Solution:**
- **Proxy Rotation**: Rotate IP addresses
- **Rate Limiting**: Track and respect rate limits per proxy
- **User Agent Rotation**: Rotate user agents
- **Request Spacing**: Add delays between requests
- **Distributed Scraping**: Distribute across multiple servers

**Implementation:**
```python
class RateLimiter:
    def __init__(self):
        self.redis = Redis()
        self.rate_limits = {
            'amazon': {'requests': 100, 'window': 3600},  # 100 per hour
            'ebay': {'requests': 200, 'window': 3600},
            'walmart': {'requests': 150, 'window': 3600}
        }
    
    def can_scrape(self, platform, proxy):
        key = f"rate_limit:{platform}:{proxy}"
        limit = self.rate_limits[platform]
        
        # Get current count
        count = self.redis.get(key) or 0
        
        if count >= limit['requests']:
            return False
        
        return True
    
    def record_scrape(self, platform, proxy):
        key = f"rate_limit:{platform}:{proxy}"
        limit = self.rate_limits[platform]
        
        # Increment count
        count = self.redis.incr(key)
        
        # Set expiration
        if count == 1:
            self.redis.expire(key, limit['window'])

class ProxyPool:
    def __init__(self):
        self.proxies = {}
        self.bad_proxies = set()
        self.redis = Redis()
    
    def get_proxy(self, platform):
        # Get available proxies for platform
        proxies = self.get_platform_proxies(platform)
        
        # Filter out bad proxies
        available = [p for p in proxies if p not in self.bad_proxies]
        
        if not available:
            # Reset bad proxies if all are bad
            self.bad_proxies.clear()
            available = proxies
        
        # Select random proxy
        return random.choice(available)
    
    def mark_bad(self, proxy):
        self.bad_proxies.add(proxy)
        # Remove from Redis pool
        self.redis.srem(f"proxies:{platform}", proxy)
    
    def return_proxy(self, proxy):
        # Proxy returned to pool (already available)
        pass
```

#### Price Change Detection

**Challenge:** Detect price drops accurately, handle price variations

**Solution:**
- **Price Comparison**: Compare with previous price
- **Threshold Detection**: Check target price and percentage
- **Noise Filtering**: Ignore small fluctuations
- **Historical Analysis**: Use price history for context

**Implementation:**
```python
def detect_price_change(product_id, new_price):
    # Get price history
    price_history = get_price_history(product_id, days=7)
    
    if not price_history:
        return None
    
    # Get previous price
    previous_price = price_history[0].price
    
    # Calculate change
    price_change = new_price - previous_price
    percentage_change = (price_change / previous_price) * 100
    
    # Filter noise (ignore changes < 1%)
    if abs(percentage_change) < 1:
        return None
    
    # Determine change type
    if price_change < 0:
        change_type = 'drop'
    elif price_change > 0:
        change_type = 'increase'
    else:
        change_type = 'stable'
    
    return {
        'change_type': change_type,
        'price_change': abs(price_change),
        'percentage_change': abs(percentage_change),
        'old_price': previous_price,
        'new_price': new_price
    }
```

#### Notification Deduplication

**Challenge:** Avoid sending duplicate notifications

**Solution:**
- **Time-Based Deduplication**: Don't notify too frequently
- **Price-Based Deduplication**: Don't notify for same price
- **Threshold-Based**: Only notify for significant drops
- **User Preferences**: Respect user notification preferences

**Implementation:**
```python
def should_send_notification(tracking, new_price, previous_price):
    # Check if already notified recently
    if tracking.last_notified_at:
        time_since = datetime.now() - tracking.last_notified_at
        if time_since < timedelta(hours=1):
            return False
    
    # Check if price actually dropped
    if new_price >= previous_price:
        return False
    
    # Check target price
    if tracking.target_price:
        if new_price <= tracking.target_price:
            return True
    
    # Check percentage drop
    if tracking.percentage_drop:
        price_drop = previous_price - new_price
        percentage_drop = (price_drop / previous_price) * 100
        if percentage_drop >= tracking.percentage_drop:
            return True
    
    return False
```

### Scalability Considerations

#### Horizontal Scaling

**Scraper Service:**
- Stateless workers, horizontally scalable
- Distribute scraping across multiple servers
- Use message queue for job distribution
- Proxy pool shared across workers

**Price Monitor Service:**
- Stateless scheduler, horizontally scalable
- Multiple schedulers with distributed locking
- Use leader election for single scheduler

#### Caching Strategy

**Redis Cache:**
- **Product Metadata**: TTL 1 hour
- **Current Prices**: TTL 10 minutes
- **Price History**: Cache recent prices
- **Rate Limit Counters**: TTL 1 hour

**Cache Invalidation:**
- Invalidate on price update
- Invalidate on product update
- Use cache-aside pattern

### Security Considerations

#### Anti-Scraping Measures

- **Proxy Rotation**: Rotate IPs frequently
- **User Agent Rotation**: Rotate user agents
- **Request Spacing**: Add delays between requests
- **CAPTCHA Handling**: Handle CAPTCHAs (manual or service)

#### Data Privacy

- **User Data**: Encrypt sensitive user data
- **Product URLs**: Sanitize URLs
- **Notification Data**: Secure notification delivery

### Monitoring & Observability

#### Key Metrics

**System Metrics:**
- Price check rate (checks/second)
- Scraping success rate
- Scraping latency (p50, p95, p99)
- Proxy failure rate
- Rate limit hits

**Business Metrics:**
- Total tracked products
- Total price checks
- Price drops detected
- Notifications sent
- User engagement

#### Logging

- **Structured Logging**: JSON logs for parsing
- **Price Events**: Log all price changes
- **Scraping Events**: Log scraping attempts and results
- **Error Logging**: Log errors with context

#### Alerting

- **High Failure Rate**: Alert if scraping failure rate > 5%
- **Rate Limit Hits**: Alert on frequent rate limit hits
- **Proxy Exhaustion**: Alert if proxy pool depleted
- **Notification Failures**: Alert on high notification failure rate

### Trade-offs and Optimizations

#### Trade-offs

**1. Check Frequency: Frequent vs Infrequent**
- **Frequent**: More accurate, higher cost
- **Infrequent**: Lower cost, less accurate
- **Decision**: Dynamic frequency based on popularity

**2. Scraping: Direct vs API**
- **Direct**: More control, risk of blocking
- **API**: More reliable, may have costs
- **Decision**: Direct scraping with proxy rotation

**3. Notification: Immediate vs Batch**
- **Immediate**: Lower latency, higher load
- **Batch**: Lower load, higher latency
- **Decision**: Immediate for price drops

**4. Price History: Full vs Sampled**
- **Full**: More accurate, higher storage
- **Sampled**: Lower storage, less accurate
- **Decision**: Full history with archival

#### Optimizations

**1. Batch Price Checks**
- Batch multiple products per request
- Reduce overhead
- Improve throughput

**2. Intelligent Scheduling**
- Prioritize popular products
- Adjust frequency based on volatility
- Reduce unnecessary checks

**3. Caching**
- Cache product metadata
- Cache current prices
- Reduce database load

**4. Proxy Pool Management**
- Monitor proxy health
- Rotate proxies proactively
- Use multiple proxy providers

## What Interviewers Look For

### Web Scraping Skills

1. **Scraping Architecture**
   - Platform-specific scrapers
   - Proxy rotation
   - Rate limiting respect
   - **Red Flags**: No proxy rotation, rate limit violations, blocking

2. **Stealth Mechanisms**
   - User-agent rotation
   - Request patterns
   - Avoid detection
   - **Red Flags**: No stealth, easy detection, frequent blocking

3. **Error Handling**
   - Retry logic
   - Failure recovery
   - **Red Flags**: No retry, no recovery, data loss

### Distributed Systems Skills

1. **Price Monitoring Pipeline**
   - Continuous monitoring
   - Dynamic frequency
   - Efficient scheduling
   - **Red Flags**: Fixed frequency, inefficient, poor scheduling

2. **Price Drop Detection**
   - Accurate detection
   - Threshold checking
   - Change tracking
   - **Red Flags**: Inaccurate detection, no threshold, missed drops

3. **Scalability Design**
   - Horizontal scaling
   - Message queue
   - Database sharding
   - **Red Flags**: Vertical scaling, no queue, no sharding

### Problem-Solving Approach

1. **Rate Limiting Handling**
   - Respect platform limits
   - Proxy rotation
   - Intelligent scheduling
   - **Red Flags**: No rate limiting, violations, blocking

2. **Edge Cases**
   - Product unavailable
   - Price format changes
   - Platform changes
   - **Red Flags**: Ignoring edge cases, no handling

3. **Trade-off Analysis**
   - Frequency vs accuracy
   - Cost vs coverage
   - **Red Flags**: No trade-offs, dogmatic choices

### System Design Skills

1. **Component Design**
   - Scraper service
   - Monitoring service
   - Notification service
   - **Red Flags**: Monolithic, unclear boundaries

2. **Notification System**
   - Multi-channel delivery
   - Reliable delivery
   - **Red Flags**: Single channel, unreliable, no retry

3. **Data Storage**
   - Price history
   - User preferences
   - Proper indexing
   - **Red Flags**: No history, missing indexes, poor queries

### Communication Skills

1. **Scraping Strategy Explanation**
   - Can explain proxy rotation
   - Understands rate limiting
   - **Red Flags**: No understanding, vague

2. **Architecture Justification**
   - Explains design decisions
   - Discusses alternatives
   - **Red Flags**: No justification, no alternatives

### Meta-Specific Focus

1. **Data Pipeline Expertise**
   - Web scraping knowledge
   - Pipeline design
   - **Key**: Show pipeline expertise

2. **Reliability Focus**
   - Accurate price tracking
   - Reliable notifications
   - **Key**: Demonstrate reliability focus

## Summary

Designing a price drop tracker system at scale requires careful consideration of:

1. **Web Scraping**: Efficient scraping with proxy rotation and rate limiting
2. **Price Monitoring**: Continuous monitoring with dynamic frequency
3. **Price Drop Detection**: Accurate detection with threshold checking
4. **Notification Delivery**: Reliable multi-channel notification delivery
5. **Rate Limiting**: Respect platform rate limits and avoid blocking
6. **Scalability**: Handle 50K+ price checks per second
7. **Accuracy**: Accurate price detection and change tracking
8. **Performance**: Sub-2-second price checks, sub-5-minute notifications

Key architectural decisions:
- **Platform-Specific Scrapers** for different e-commerce sites
- **Proxy Rotation** to avoid blocking
- **Dynamic Check Frequency** based on product popularity
- **Sharded Database** for price history storage
- **Message Queue** for asynchronous processing
- **Multi-Channel Notifications** for user alerts
- **Horizontal Scaling** for all services

The system handles 50,000 price checks per second, tracks 100 million products, and sends millions of notifications daily while respecting rate limits and ensuring accurate price tracking.

