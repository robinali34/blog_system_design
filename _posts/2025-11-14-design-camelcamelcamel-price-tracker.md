---
layout: post
title: "Design CamelCamelCamel Price Tracker - System Design Interview"
date: 2025-11-14
categories: [System Design, Interview Example, Distributed Systems, E-commerce, Web Scraping, Real-time Systems, Analytics]
excerpt: "A comprehensive guide to designing CamelCamelCamel, a price tracking service for Amazon products, covering historical price tracking, price drop alerts, browser extensions, price charts, ASIN-based tracking, and architectural patterns for tracking millions of Amazon products with accurate historical data."
---

## Introduction

CamelCamelCamel is a price tracking service specifically designed for Amazon products. It tracks historical prices, provides price drop alerts, displays price charts, and offers browser extensions for easy product tracking. The system handles millions of Amazon products, tracks billions of price points, and serves millions of users daily.

This post provides a detailed walkthrough of designing CamelCamelCamel's architecture, covering Amazon-specific scraping, ASIN-based product tracking, historical price storage, price chart generation, browser extension integration, email alerts, and handling Amazon's rate limits and anti-scraping measures. This is a common system design interview question that tests your understanding of distributed systems, web scraping, time-series data, browser extensions, and notification systems.

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

**Design CamelCamelCamel, a price tracking service for Amazon products with the following features:**

1. Track Amazon products by ASIN (Amazon Standard Identification Number)
2. Store historical price data
3. Display price charts (1 day, 1 week, 1 month, 3 months, 1 year, all time)
4. Send price drop email alerts
5. Browser extension for easy product tracking
6. Product search and discovery
7. Price history API access
8. Support multiple Amazon marketplaces (US, UK, CA, etc.)
9. Track different product conditions (new, used, refurbished)
10. Handle Amazon's rate limits and anti-scraping measures

**Scale Requirements:**
- 20 million+ users
- 50 million+ tracked products (ASINs)
- 500 million+ price checks per day
- Peak: 30,000 price checks per second
- Average products per user: 15
- Popular products: 500,000+ trackers
- Historical data: 5+ years per product
- Must respect Amazon's rate limits
- Price check frequency: Every 1-6 hours per product

## Requirements

### Functional Requirements

**Core Features:**
1. **Product Tracking**: Add products by ASIN or Amazon URL
2. **Price Monitoring**: Continuously monitor Amazon product prices
3. **Historical Price Storage**: Store all price points with timestamps
4. **Price Charts**: Display interactive price charts (multiple time ranges)
5. **Price Drop Alerts**: Email alerts when price drops below threshold
6. **Browser Extension**: Chrome/Firefox extension for easy tracking
7. **Product Search**: Search products by name, ASIN, or URL
8. **Multi-Marketplace**: Support US, UK, CA, DE, FR, etc.
9. **Product Conditions**: Track new, used, refurbished prices separately
10. **Price History API**: Public API for price history data

**Out of Scope:**
- Product reviews and ratings
- Product recommendations
- Coupon code management
- Mobile app (focus on web and browser extension)
- Payment processing
- User authentication (assume existing auth system)

### Non-Functional Requirements

1. **Availability**: 99.9% uptime
2. **Reliability**: No missed price drops, accurate historical data
3. **Performance**: 
   - Price check: < 3 seconds
   - Price chart rendering: < 500ms
   - Alert delivery: < 10 minutes after price drop
   - Browser extension response: < 200ms
4. **Scalability**: Handle 30K+ price checks per second
5. **Accuracy**: Accurate price detection, handle Amazon's dynamic pricing
6. **Rate Limiting**: Respect Amazon's rate limits strictly
7. **Data Retention**: 5+ years of historical price data

## Capacity Estimation

### Traffic Estimates

- **Total Users**: 20 million
- **Daily Active Users (DAU)**: 2 million
- **Tracked Products (ASINs)**: 50 million
- **Price Checks per Day**: 500 million
- **Average Checks per Product**: 10 per day
- **Peak Price Check Rate**: 30,000 per second
- **Normal Price Check Rate**: 5,000 per second
- **Email Alerts per Day**: 5 million
- **Browser Extension Requests**: 10 million per day
- **New Products Added per Day**: 500,000

### Storage Estimates

**Product Data:**
- 50M products × 2KB = 100GB
- Product metadata, ASINs, URLs, marketplace info

**Price History (Time-Series):**
- 500M price checks/day × 150 bytes = 75GB/day
- 30-day retention (hot): ~2.25TB
- 1-year retention (warm): ~27TB
- 5-year archive (cold): ~135TB

**User Tracking Preferences:**
- 20M users × 15 products × 300 bytes = 90GB

**Email Alerts:**
- 5M alerts/day × 1KB = 5GB/day
- 30-day retention: ~150GB

**Browser Extension Cache:**
- 10M requests/day × 500 bytes = 5GB/day
- 7-day retention: ~35GB

**Total Storage**: ~135TB

### Bandwidth Estimates

**Normal Traffic:**
- 5,000 price checks/sec × 15KB = 75MB/s = 600Mbps
- Amazon scraping responses

**Peak Traffic:**
- 30,000 price checks/sec × 15KB = 450MB/s = 3.6Gbps

**Browser Extension:**
- 10M requests/day × 2KB = 20GB/day = ~230KB/s = ~2Mbps

**Email Delivery:**
- 5M emails/day × 5KB = 25GB/day = ~290KB/s = ~2Mbps

**Total Peak**: ~3.6Gbps

## Core Entities

### Product
- `product_id` (UUID)
- `asin` (VARCHAR, unique)
- `marketplace` (us, uk, ca, de, fr, etc.)
- `product_url` (VARCHAR)
- `product_name` (VARCHAR)
- `brand` (VARCHAR)
- `category` (VARCHAR)
- `current_price_new` (DECIMAL)
- `current_price_used` (DECIMAL)
- `current_price_refurbished` (DECIMAL)
- `currency` (VARCHAR)
- `availability` (in_stock, out_of_stock, unknown)
- `last_checked_at` (TIMESTAMP)
- `check_frequency_hours` (INT)
- `tracker_count` (INT)
- `first_tracked_at` (TIMESTAMP)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

### Price Point
- `price_id` (UUID)
- `product_id` (UUID)
- `asin` (VARCHAR)
- `marketplace` (VARCHAR)
- `condition` (new, used, refurbished)
- `price` (DECIMAL)
- `currency` (VARCHAR)
- `availability` (VARCHAR)
- `seller_type` (amazon, third_party)
- `checked_at` (TIMESTAMP)
- `source` (scraper, api)

### User Tracking
- `tracking_id` (UUID)
- `user_id` (UUID)
- `product_id` (UUID)
- `asin` (VARCHAR)
- `marketplace` (VARCHAR)
- `condition` (new, used, refurbished)
- `target_price` (DECIMAL, optional)
- `percentage_drop` (DECIMAL, optional)
- `alert_enabled` (BOOLEAN)
- `last_notified_at` (TIMESTAMP)
- `last_notified_price` (DECIMAL)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

### Price Alert
- `alert_id` (UUID)
- `user_id` (UUID)
- `product_id` (UUID)
- `tracking_id` (UUID)
- `old_price` (DECIMAL)
- `new_price` (DECIMAL)
- `price_drop` (DECIMAL)
- `percentage_drop` (DECIMAL)
- `condition` (VARCHAR)
- `status` (pending, sent, failed)
- `sent_at` (TIMESTAMP)
- `created_at` (TIMESTAMP)

### User
- `user_id` (UUID)
- `email` (VARCHAR)
- `email_verified` (BOOLEAN)
- `notification_preferences` (JSON)
- `browser_extension_installed` (BOOLEAN)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

## API

### 1. Add Product to Track
```
POST /api/v1/products/track
Request:
{
  "asin": "B08XYZ123",
  "marketplace": "us",
  "condition": "new",
  "target_price": 99.99,
  "alert_enabled": true
}

Response:
{
  "tracking_id": "uuid",
  "product_id": "uuid",
  "asin": "B08XYZ123",
  "product_name": "Example Product",
  "current_price": 149.99,
  "target_price": 99.99,
  "price_chart_url": "/charts/B08XYZ123",
  "status": "tracking"
}
```

### 2. Get Product Price History
```
GET /api/v1/products/{asin}/history?marketplace=us&condition=new&range=1year
Response:
{
  "asin": "B08XYZ123",
  "product_name": "Example Product",
  "marketplace": "us",
  "condition": "new",
  "price_history": [
    {
      "price": 149.99,
      "checked_at": "2025-11-13T10:00:00Z",
      "availability": "in_stock"
    },
    {
      "price": 159.99,
      "checked_at": "2025-11-12T10:00:00Z",
      "availability": "in_stock"
    }
  ],
  "statistics": {
    "current_price": 149.99,
    "lowest_price": 129.99,
    "highest_price": 179.99,
    "average_price": 149.50,
    "price_drops": 5,
    "price_increases": 3
  },
  "chart_data_url": "/api/v1/products/B08XYZ123/chart?range=1year"
}
```

### 3. Get Price Chart Data
```
GET /api/v1/products/{asin}/chart?marketplace=us&condition=new&range=1year
Response:
{
  "asin": "B08XYZ123",
  "range": "1year",
  "data_points": [
    {"date": "2025-11-13", "price": 149.99},
    {"date": "2025-11-12", "price": 159.99}
  ],
  "statistics": {
    "min": 129.99,
    "max": 179.99,
    "avg": 149.50
  }
}
```

### 4. Browser Extension API
```
GET /api/v1/browser/product?url=https://amazon.com/dp/B08XYZ123
Response:
{
  "asin": "B08XYZ123",
  "product_name": "Example Product",
  "current_price": 149.99,
  "lowest_price": 129.99,
  "highest_price": 179.99,
  "price_trend": "decreasing",
  "is_tracked": true,
  "tracking_id": "uuid",
  "chart_url": "/charts/B08XYZ123"
}
```

### 5. Search Products
```
GET /api/v1/products/search?q=laptop&marketplace=us&limit=20
Response:
{
  "products": [
    {
      "asin": "B08XYZ123",
      "product_name": "Laptop Example",
      "current_price": 999.99,
      "lowest_price": 899.99,
      "price_trend": "stable",
      "product_url": "https://amazon.com/dp/B08XYZ123"
    }
  ],
  "total": 100,
  "limit": 20,
  "offset": 0
}
```

### 6. Get User Trackings
```
GET /api/v1/users/{user_id}/trackings?limit=20&offset=0
Response:
{
  "trackings": [
    {
      "tracking_id": "uuid",
      "product": {
        "asin": "B08XYZ123",
        "product_name": "Example Product",
        "current_price": 149.99,
        "price_change": -10.00,
        "percentage_change": -6.25,
        "lowest_price": 129.99
      },
      "target_price": 99.99,
      "alert_enabled": true,
      "is_active": true
    }
  ],
  "total": 50,
  "limit": 20,
  "offset": 0
}
```

## Data Flow

### Product Addition Flow (Browser Extension)

1. **User Clicks Extension**:
   - User visits Amazon product page
   - Clicks browser extension icon
   - **Extension** extracts ASIN from URL

2. **Product Lookup**:
   - **Extension** sends ASIN to **API Gateway**
   - **API Gateway** routes to **Product Service**
   - **Product Service**:
     - Checks if product exists
     - If new, creates product record
     - Fetches initial price from **Amazon Scraper**
     - Returns product info to extension

3. **Display Product Info**:
   - **Extension** displays:
     - Current price
     - Price history chart
     - Lowest/highest prices
     - Track button

4. **User Tracks Product**:
   - User clicks "Track" button
   - **Extension** sends tracking request
   - **Product Service** creates user tracking record
   - Returns confirmation

### Price Monitoring Flow

1. **Scheduled Price Check**:
   - **Price Monitor Scheduler** identifies products to check
   - Determines check frequency:
     - Popular products (many trackers): Every 1 hour
     - Medium popularity: Every 3 hours
     - Low popularity: Every 6 hours

2. **Price Check Execution**:
   - **Price Monitor Service**:
     - Gets product details (ASIN, marketplace)
     - Queues price check job to **Message Queue**
     - **Amazon Scraper Worker** picks up job

3. **Amazon Scraping**:
   - **Scraper Worker**:
     - Constructs Amazon URL from ASIN and marketplace
     - Uses proxy rotation and user agent rotation
     - Respects rate limits (tracks requests per IP)
     - Fetches product page
     - Extracts prices for all conditions (new, used, refurbished)
     - Handles errors (retry, fallback, CAPTCHA)

4. **Price Storage**:
   - **Scraper Worker**:
     - Stores price points in **Time-Series Database**
     - Updates product current prices
     - Publishes price update event

5. **Price Drop Detection**:
   - **Price Drop Detector**:
     - Compares new price with previous price
     - Checks against user target prices
     - Identifies price drops
     - Creates alert records

6. **Alert Delivery**:
   - **Alert Service**:
     - Gets pending alerts
     - Sends email alerts
     - Updates alert status

### Price Chart Generation Flow

1. **User Requests Chart**:
   - User visits product page
   - Selects time range (1 day, 1 week, 1 month, etc.)
   - **Client** requests chart data

2. **Chart Data Retrieval**:
   - **Chart Service**:
     - Queries **Time-Series Database** for price history
     - Filters by time range and condition
     - Aggregates data points (if needed for long ranges)
     - Calculates statistics (min, max, avg)

3. **Chart Rendering**:
   - **Chart Service** returns data points
   - **Client** renders interactive chart
   - Displays price trends and statistics

## Database Design

### Schema Design

**Products Table:**
```sql
CREATE TABLE products (
    product_id UUID PRIMARY KEY,
    asin VARCHAR(20) NOT NULL,
    marketplace VARCHAR(10) NOT NULL,
    product_url VARCHAR(1000) NOT NULL,
    product_name VARCHAR(500) NOT NULL,
    brand VARCHAR(200),
    category VARCHAR(200),
    current_price_new DECIMAL(10, 2) NULL,
    current_price_used DECIMAL(10, 2) NULL,
    current_price_refurbished DECIMAL(10, 2) NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    availability VARCHAR(50) DEFAULT 'unknown',
    last_checked_at TIMESTAMP NULL,
    check_frequency_hours INT DEFAULT 6,
    tracker_count INT DEFAULT 0,
    first_tracked_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_asin (asin),
    INDEX idx_marketplace (marketplace),
    INDEX idx_asin_marketplace (asin, marketplace),
    INDEX idx_last_checked (last_checked_at),
    INDEX idx_tracker_count (tracker_count),
    UNIQUE KEY uk_asin_marketplace (asin, marketplace)
);
```

**Price Points Table (Time-Series, Sharded by ASIN):**
```sql
CREATE TABLE price_points_0 (
    price_id UUID PRIMARY KEY,
    product_id UUID NOT NULL,
    asin VARCHAR(20) NOT NULL,
    marketplace VARCHAR(10) NOT NULL,
    condition VARCHAR(20) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    availability VARCHAR(50),
    seller_type VARCHAR(50),
    checked_at TIMESTAMP NOT NULL,
    source VARCHAR(50) DEFAULT 'scraper',
    INDEX idx_asin_marketplace (asin, marketplace),
    INDEX idx_checked_at (checked_at DESC),
    INDEX idx_product_condition (product_id, condition),
    INDEX idx_asin_condition_checked (asin, marketplace, condition, checked_at DESC)
);
-- Similar tables: price_points_1, price_points_2, ..., price_points_N
```

**User Trackings Table:**
```sql
CREATE TABLE user_trackings (
    tracking_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    product_id UUID NOT NULL,
    asin VARCHAR(20) NOT NULL,
    marketplace VARCHAR(10) NOT NULL,
    condition VARCHAR(20) NOT NULL,
    target_price DECIMAL(10, 2) NULL,
    percentage_drop DECIMAL(5, 2) NULL,
    alert_enabled BOOLEAN DEFAULT TRUE,
    last_notified_at TIMESTAMP NULL,
    last_notified_price DECIMAL(10, 2) NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_id (user_id),
    INDEX idx_product_id (product_id),
    INDEX idx_asin (asin),
    INDEX idx_alert_enabled (alert_enabled),
    INDEX idx_user_alert (user_id, alert_enabled),
    UNIQUE KEY uk_user_product_condition (user_id, product_id, condition)
);
```

**Price Alerts Table:**
```sql
CREATE TABLE price_alerts (
    alert_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    product_id UUID NOT NULL,
    tracking_id UUID NOT NULL,
    asin VARCHAR(20) NOT NULL,
    old_price DECIMAL(10, 2) NOT NULL,
    new_price DECIMAL(10, 2) NOT NULL,
    price_drop DECIMAL(10, 2) NOT NULL,
    percentage_drop DECIMAL(5, 2) NOT NULL,
    condition VARCHAR(20) NOT NULL,
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
    email_verified BOOLEAN DEFAULT FALSE,
    notification_preferences JSON,
    browser_extension_installed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_email (email)
);
```

### Database Sharding Strategy

**Price Points Table Sharding:**
- Shard by ASIN using consistent hashing
- 1000 shards: `shard_id = hash(asin + marketplace) % 1000`
- All price points for a product in same shard
- Enables efficient price history queries

**Time-Series Optimization:**
- Use time-series database (TimescaleDB, InfluxDB) for price points
- Partition by time (monthly partitions)
- Efficient range queries for charts
- Automatic data retention policies

**Shard Key Selection:**
- `asin + marketplace` ensures all prices for a product are in same shard
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
│  Product    │ │  Price     │ │  Chart     │ │  Alert     │ │  Browser   │
│  Service    │ │  Monitor   │ │  Service   │ │  Service   │ │  Extension │
│             │ │  Service   │ │            │ │            │ │  API       │
└──────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
       │              │              │              │              │
       │              │              │              │              │
┌──────▼──────────────▼──────────────▼──────────────▼──────────────▼──────┐
│              Message Queue (Kafka)                                        │
│              - Price check jobs                                            │
│              - Price update events                                         │
│              - Alert jobs                                                  │
└──────┬───────────────────────────────────────────────────────────────────┘
       │
       │
┌──────▼───────────────────────────────────────────────────────────────────┐
│         Amazon Scraper Service                                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                              │
│  │ US        │  │ UK        │  │ CA        │                              │
│  │ Scraper   │  │ Scraper   │  │ Scraper   │                              │
│  └──────────┘  └──────────┘  └──────────┘                              │
│                                                                           │
│  ┌──────────────────────────────────────────────────────┐                │
│  │ Proxy Pool Manager                                    │                │
│  │ - IP Rotation                                          │                │
│  │ - Rate Limit Management                               │                │
│  │ - CAPTCHA Handling                                    │                │
│  └──────────────────────────────────────────────────────┘                │
└──────┬───────────────────────────────────────────────────────────────────┘
       │
       │
┌──────▼───────────────────────────────────────────────────────────────────┐
│         Price Drop Detector                                               │
│         - Compare prices                                                  │
│         - Check thresholds                                                │
│         - Create alerts                                                   │
└──────┬───────────────────────────────────────────────────────────────────┘
       │
       │
┌──────▼───────────────────────────────────────────────────────────────────┐
│         Database Cluster                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                              │
│  │ Products │  │ User      │  │ Price     │                              │
│  │ DB       │  │ Trackings │  │ Alerts    │                              │
│  │          │  │ DB        │  │ DB        │                              │
│  └──────────┘  └──────────┘  └──────────┘                              │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│         Time-Series Database (TimescaleDB/InfluxDB)                        │
│         - Price points (sharded by ASIN)                                   │
│         - Time-based partitioning                                          │
│         - Efficient range queries                                         │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│              Cache Layer (Redis)                                          │
│  - Product metadata                                                       │
│  - Current prices                                                         │
│  - Rate limit counters                                                    │
│  - Popular products                                                       │
│  - Chart data (cached)                                                    │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│         Email Service                                                     │
│         - Send price drop alerts                                          │
│         - Email templates                                                 │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│         Browser Extension Backend                                         │
│         - Product lookup                                                  │
│         - Quick price display                                              │
│         - Tracking management                                              │
└───────────────────────────────────────────────────────────────────────────┘
```

## Deep Dive

### Component Design

#### 1. Amazon Scraper Service

**Responsibilities:**
- Scrape Amazon product pages by ASIN
- Extract prices for all conditions (new, used, refurbished)
- Handle multiple marketplaces
- Respect rate limits and avoid blocking
- Rotate proxies and user agents

**Key Design Decisions:**
- **ASIN-Based**: Use ASIN for product identification
- **Multi-Condition**: Track new, used, refurbished separately
- **Multi-Marketplace**: Support US, UK, CA, DE, FR, etc.
- **Proxy Rotation**: Rotate IPs to avoid blocking
- **Rate Limiting**: Strict rate limit enforcement

**Implementation:**
```python
class AmazonScraperService:
    def __init__(self):
        self.proxy_pool = ProxyPool()
        self.rate_limiter = RateLimiter()
        self.user_agent_rotator = UserAgentRotator()
    
    def scrape_product(self, asin, marketplace='us'):
        # Get proxy for marketplace
        proxy = self.proxy_pool.get_proxy(marketplace)
        
        # Check rate limit
        if not self.rate_limiter.can_scrape(marketplace, proxy):
            raise RateLimitError("Rate limit exceeded")
        
        try:
            # Construct Amazon URL
            url = self.build_amazon_url(asin, marketplace)
            
            # Make request
            response = requests.get(
                url,
                proxies={'http': proxy, 'https': proxy},
                headers={
                    'User-Agent': self.user_agent_rotator.get_random(),
                    'Accept': 'text/html,application/xhtml+xml',
                    'Accept-Language': 'en-US,en;q=0.9'
                },
                timeout=10,
                cookies=self.get_amazon_cookies(marketplace)
            )
            
            if response.status_code == 503:
                # CAPTCHA or blocking
                raise CAPTCHAError("CAPTCHA detected")
            
            if response.status_code != 200:
                raise ScrapingError(f"HTTP {response.status_code}")
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract product name
            product_name = self.extract_product_name(soup)
            
            # Extract prices for all conditions
            prices = {
                'new': self.extract_price(soup, 'new'),
                'used': self.extract_price(soup, 'used'),
                'refurbished': self.extract_price(soup, 'refurbished')
            }
            
            # Extract availability
            availability = self.extract_availability(soup)
            
            # Update rate limit
            self.rate_limiter.record_scrape(marketplace, proxy)
            
            return {
                'asin': asin,
                'marketplace': marketplace,
                'product_name': product_name,
                'prices': prices,
                'availability': availability,
                'checked_at': datetime.now()
            }
        except CAPTCHAError:
            # Mark proxy as bad
            self.proxy_pool.mark_bad(proxy)
            raise
        except ScrapingError as e:
            # Retry with different proxy
            self.proxy_pool.mark_bad(proxy)
            raise
        finally:
            self.proxy_pool.return_proxy(proxy)
    
    def extract_price(self, soup, condition):
        # Different selectors for different conditions
        selectors = {
            'new': ['#priceblock_ourprice', '#priceblock_dealprice', '.a-price-whole'],
            'used': ['#usedBuySection .a-price-whole'],
            'refurbished': ['#renewedBuySection .a-price-whole']
        }
        
        for selector in selectors.get(condition, []):
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text()
                price = self.parse_price(price_text)
                if price:
                    return price
        
        return None
```

#### 2. Price Chart Service

**Responsibilities:**
- Generate price chart data for different time ranges
- Aggregate data points for long ranges
- Calculate statistics (min, max, avg)
- Cache chart data

**Key Design Decisions:**
- **Time-Series Database**: Use TimescaleDB for efficient queries
- **Data Aggregation**: Aggregate data for long ranges
- **Caching**: Cache chart data for popular products
- **Multiple Ranges**: Support 1 day, 1 week, 1 month, 3 months, 1 year, all time

**Implementation:**
```python
class PriceChartService:
    def __init__(self):
        self.timeseries_db = TimescaleDB()
        self.redis = Redis()
    
    def get_chart_data(self, asin, marketplace, condition, time_range):
        # Check cache
        cache_key = f"chart:{asin}:{marketplace}:{condition}:{time_range}"
        cached = self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Calculate time window
        end_time = datetime.now()
        start_time = self.calculate_start_time(end_time, time_range)
        
        # Query time-series database
        query = """
            SELECT 
                time_bucket('1 hour', checked_at) AS bucket,
                AVG(price) AS avg_price,
                MIN(price) AS min_price,
                MAX(price) AS max_price
            FROM price_points
            WHERE asin = %s 
                AND marketplace = %s 
                AND condition = %s
                AND checked_at >= %s
                AND checked_at <= %s
            GROUP BY bucket
            ORDER BY bucket ASC
        """
        
        data_points = self.timeseries_db.query(
            query,
            (asin, marketplace, condition, start_time, end_time)
        )
        
        # Calculate statistics
        all_prices = [dp['avg_price'] for dp in data_points]
        statistics = {
            'min': min(all_prices) if all_prices else None,
            'max': max(all_prices) if all_prices else None,
            'avg': sum(all_prices) / len(all_prices) if all_prices else None
        }
        
        result = {
            'asin': asin,
            'marketplace': marketplace,
            'condition': condition,
            'time_range': time_range,
            'data_points': data_points,
            'statistics': statistics
        }
        
        # Cache result
        self.redis.setex(cache_key, 3600, json.dumps(result))  # 1 hour cache
        
        return result
    
    def calculate_start_time(self, end_time, time_range):
        ranges = {
            '1day': timedelta(days=1),
            '1week': timedelta(weeks=1),
            '1month': timedelta(days=30),
            '3months': timedelta(days=90),
            '1year': timedelta(days=365),
            'all': timedelta(days=3650)  # 10 years
        }
        
        delta = ranges.get(time_range, timedelta(days=30))
        return end_time - delta
```

#### 3. Browser Extension Backend

**Responsibilities:**
- Handle extension requests
- Extract ASIN from Amazon URLs
- Return product info quickly
- Support quick tracking

**Key Design Decisions:**
- **Fast Response**: Sub-200ms response time
- **ASIN Extraction**: Parse Amazon URLs
- **Cached Data**: Return cached product data
- **Quick Tracking**: One-click tracking

**Implementation:**
```python
class BrowserExtensionAPI:
    def get_product_info(self, amazon_url):
        # Extract ASIN from URL
        asin = self.extract_asin(amazon_url)
        marketplace = self.extract_marketplace(amazon_url)
        
        if not asin:
            raise ValueError("Invalid Amazon URL")
        
        # Get product from cache or database
        product = self.get_product(asin, marketplace)
        
        if not product:
            # Product not tracked yet
            return {
                'asin': asin,
                'marketplace': marketplace,
                'is_tracked': False,
                'message': 'Product not tracked yet'
            }
        
        # Get price history statistics
        stats = self.get_price_statistics(asin, marketplace)
        
        # Determine price trend
        trend = self.calculate_trend(stats)
        
        return {
            'asin': asin,
            'product_name': product.product_name,
            'current_price': product.current_price_new,
            'lowest_price': stats['lowest'],
            'highest_price': stats['highest'],
            'average_price': stats['average'],
            'price_trend': trend,
            'is_tracked': True,
            'chart_url': f"/charts/{asin}?marketplace={marketplace}"
        }
    
    def extract_asin(self, url):
        # Extract ASIN from various Amazon URL formats
        patterns = [
            r'/dp/([A-Z0-9]{10})',
            r'/gp/product/([A-Z0-9]{10})',
            r'/product/([A-Z0-9]{10})',
            r'asin=([A-Z0-9]{10})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
```

### Detailed Design

#### Handling Amazon Rate Limits

**Challenge:** Amazon has strict rate limits and anti-scraping measures

**Solution:**
- **Proxy Rotation**: Large proxy pool with rotation
- **Rate Limiting**: Track requests per IP per hour
- **Request Spacing**: Add delays between requests
- **User Agent Rotation**: Rotate user agents
- **Cookie Management**: Use session cookies
- **CAPTCHA Handling**: Detect and handle CAPTCHAs

**Implementation:**
```python
class AmazonRateLimiter:
    def __init__(self):
        self.redis = Redis()
        self.rate_limits = {
            'us': {'requests': 50, 'window': 3600},  # 50 per hour per IP
            'uk': {'requests': 50, 'window': 3600},
            'ca': {'requests': 50, 'window': 3600}
        }
    
    def can_scrape(self, marketplace, proxy_ip):
        key = f"amazon_rate:{marketplace}:{proxy_ip}"
        limit = self.rate_limits[marketplace]
        
        count = self.redis.get(key)
        if count and int(count) >= limit['requests']:
            return False
        
        return True
    
    def record_scrape(self, marketplace, proxy_ip):
        key = f"amazon_rate:{marketplace}:{proxy_ip}"
        limit = self.rate_limits[marketplace]
        
        count = self.redis.incr(key)
        if count == 1:
            self.redis.expire(key, limit['window'])
```

#### Price Drop Detection with Conditions

**Challenge:** Detect price drops for different product conditions

**Solution:**
- **Condition-Specific Tracking**: Track each condition separately
- **Condition-Specific Alerts**: Alert based on tracked condition
- **Price Comparison**: Compare with condition-specific previous price

**Implementation:**
```python
def detect_price_drops(product_id, asin, marketplace, new_prices):
    # Get all active trackings for this product
    trackings = get_active_trackings(product_id)
    
    alerts = []
    
    for tracking in trackings:
        condition = tracking.condition
        new_price = new_prices.get(condition)
        
        if not new_price:
            continue  # Price not available for this condition
        
        # Get previous price for this condition
        previous_price = get_previous_price(asin, marketplace, condition)
        
        if not previous_price:
            continue  # No previous price
        
        # Calculate price change
        price_drop = previous_price - new_price
        percentage_drop = (price_drop / previous_price) * 100
        
        # Check if should alert
        should_alert = False
        
        # Check target price
        if tracking.target_price and new_price <= tracking.target_price:
            should_alert = True
        
        # Check percentage drop
        if tracking.percentage_drop and percentage_drop >= tracking.percentage_drop:
            should_alert = True
        
        # Check if already notified recently
        if tracking.last_notified_at:
            time_since = datetime.now() - tracking.last_notified_at
            if time_since < timedelta(hours=6):
                should_alert = False  # Don't notify too frequently
        
        if should_alert and tracking.alert_enabled:
            # Create alert
            alert = PriceAlert(
                user_id=tracking.user_id,
                product_id=product_id,
                tracking_id=tracking.tracking_id,
                asin=asin,
                old_price=previous_price,
                new_price=new_price,
                price_drop=price_drop,
                percentage_drop=percentage_drop,
                condition=condition,
                status='pending'
            )
            alert.save()
            alerts.append(alert)
            
            # Update tracking
            tracking.last_notified_at = datetime.now()
            tracking.last_notified_price = new_price
            tracking.save()
    
    return alerts
```

#### Historical Data Retention

**Challenge:** Store 5+ years of price data efficiently

**Solution:**
- **Time-Series Database**: Use TimescaleDB for efficient storage
- **Time Partitioning**: Partition by month
- **Data Archival**: Archive old data to cold storage
- **Data Compression**: Compress old partitions

**Implementation:**
```python
class PriceHistoryManager:
    def __init__(self):
        self.timeseries_db = TimescaleDB()
        self.s3 = S3Client()
    
    def store_price_point(self, price_point):
        # Insert into time-series database
        self.timeseries_db.insert('price_points', price_point)
    
    def archive_old_data(self):
        # Archive data older than 1 year to S3
        cutoff_date = datetime.now() - timedelta(days=365)
        
        # Query old data
        old_data = self.timeseries_db.query(
            "SELECT * FROM price_points WHERE checked_at < %s",
            (cutoff_date,)
        )
        
        # Upload to S3
        for batch in chunks(old_data, 10000):
            key = f"price_history/{cutoff_date.year}/{cutoff_date.month}/batch_{uuid4()}.json"
            self.s3.upload(key, json.dumps(batch))
        
        # Delete from database
        self.timeseries_db.delete(
            "DELETE FROM price_points WHERE checked_at < %s",
            (cutoff_date,)
        )
```

### Scalability Considerations

#### Horizontal Scaling

**Scraper Service:**
- Stateless workers, horizontally scalable
- Distribute scraping across multiple servers
- Use message queue for job distribution
- Shared proxy pool across workers

**Chart Service:**
- Stateless service, horizontally scalable
- Cache chart data in Redis
- Use read replicas for time-series database

#### Caching Strategy

**Redis Cache:**
- **Product Metadata**: TTL 1 hour
- **Current Prices**: TTL 10 minutes
- **Chart Data**: TTL 1 hour
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
- **CAPTCHA Handling**: Detect and handle CAPTCHAs
- **Cookie Management**: Use session cookies

#### Data Privacy

- **User Data**: Encrypt sensitive user data
- **Email Addresses**: Secure email storage
- **Tracking Data**: Anonymize tracking data for analytics

### Monitoring & Observability

#### Key Metrics

**System Metrics:**
- Price check rate (checks/second)
- Scraping success rate
- Scraping latency (p50, p95, p99)
- Proxy failure rate
- Rate limit hits
- CAPTCHA rate

**Business Metrics:**
- Total tracked products
- Total price checks
- Price drops detected
- Email alerts sent
- Browser extension usage
- User engagement

#### Logging

- **Structured Logging**: JSON logs for parsing
- **Price Events**: Log all price changes
- **Scraping Events**: Log scraping attempts and results
- **Alert Events**: Log alert creation and delivery
- **Error Logging**: Log errors with context

#### Alerting

- **High Failure Rate**: Alert if scraping failure rate > 5%
- **Rate Limit Hits**: Alert on frequent rate limit hits
- **Proxy Exhaustion**: Alert if proxy pool depleted
- **CAPTCHA Rate**: Alert if CAPTCHA rate > 10%
- **Alert Delivery Failures**: Alert on high alert failure rate

### Trade-offs and Optimizations

#### Trade-offs

**1. Check Frequency: Frequent vs Infrequent**
- **Frequent**: More accurate, higher cost
- **Infrequent**: Lower cost, less accurate
- **Decision**: Dynamic frequency based on popularity

**2. Scraping: Direct vs API**
- **Direct**: More control, risk of blocking
- **API**: More reliable, may have costs
- **Decision**: Direct scraping with extensive proxy rotation

**3. Historical Data: Full vs Sampled**
- **Full**: More accurate, higher storage
- **Sampled**: Lower storage, less accurate
- **Decision**: Full data with archival to S3

**4. Chart Data: Real-Time vs Cached**
- **Real-Time**: Always accurate, higher load
- **Cached**: Lower load, may be stale
- **Decision**: Cached with 1-hour TTL

#### Optimizations

**1. Intelligent Scheduling**
- Prioritize popular products
- Adjust frequency based on price volatility
- Reduce unnecessary checks

**2. Batch Price Checks**
- Batch multiple products per proxy session
- Reduce overhead
- Improve throughput

**3. Data Compression**
- Compress old price data
- Use columnar storage for time-series
- Reduce storage costs

**4. Chart Data Aggregation**
- Pre-aggregate chart data for common ranges
- Store aggregated data
- Reduce query time

## Summary

Designing CamelCamelCamel requires careful consideration of:

1. **Amazon Scraping**: Efficient scraping with proxy rotation and rate limiting
2. **ASIN-Based Tracking**: Use ASIN for product identification
3. **Multi-Condition Tracking**: Track new, used, refurbished separately
4. **Historical Price Storage**: Time-series database for 5+ years of data
5. **Price Charts**: Efficient chart generation with data aggregation
6. **Browser Extension**: Fast product lookup and tracking
7. **Email Alerts**: Reliable price drop notification delivery
8. **Rate Limiting**: Strict enforcement of Amazon's rate limits
9. **Scalability**: Handle 30K+ price checks per second
10. **Data Retention**: Efficient storage and archival of historical data

Key architectural decisions:
- **ASIN-Based Product Identification** for Amazon products
- **Time-Series Database** for efficient price history storage
- **Multi-Condition Price Tracking** for new, used, refurbished
- **Proxy Rotation** to avoid blocking
- **Dynamic Check Frequency** based on product popularity
- **Browser Extension Integration** for easy product tracking
- **Email Alert System** for price drop notifications
- **Horizontal Scaling** for all services

The system handles 30,000 price checks per second, tracks 50 million Amazon products, stores 5+ years of historical data, and sends millions of email alerts daily while respecting Amazon's rate limits and ensuring accurate price tracking.

