---
layout: post
title: "Design a URL Shortener - Meta System Design Interview"
date: 2025-11-24
categories: [System Design, Interview Example, Meta, Data Modeling, Hashing, Algorithms]
excerpt: "A comprehensive guide to designing a URL shortener focusing on data modeling, storage choice, hashing/encoding, uniqueness constraints, caching, and API design. Meta interview question emphasizing data structures and algorithms rather than network-level scalability."
---

## Introduction

Designing a URL shortener is a classic system design interview question at Meta that focuses on data modeling, storage design, hashing algorithms, and API design. Unlike distributed system design questions, Meta's version emphasizes:

- **Data structures and algorithms**: Efficient encoding/decoding
- **Data modeling**: Database schema design
- **Uniqueness constraints**: Handling collisions
- **Storage choice**: Relational vs NoSQL trade-offs
- **Caching strategies**: Fast lookups
- **API design**: Clean, efficient interfaces

This guide covers the design of a URL shortener with focus on these aspects, including collision handling, custom URLs, and efficient storage strategies.

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Requirements](#requirements)
3. [Data Modeling](#data-modeling)
4. [Hashing and Encoding](#hashing-and-encoding)
5. [API Design](#api-design)
6. [Storage Design](#storage-design)
7. [Collision Handling](#collision-handling)
8. [Custom URLs](#custom-urls)
9. [Caching Strategy](#caching-strategy)
10. [Deep Dive](#deep-dive)
11. [Summary](#summary)

## Problem Statement

**Design a URL shortener service that:**

1. **Shortens long URLs** to short, shareable links
2. **Redirects short URLs** to original long URLs
3. **Handles collisions** when generating short codes
4. **Supports custom short URLs** (optional)
5. **Tracks analytics** (click count, timestamps)
6. **Provides fast lookups** (< 10ms)

**Scale Requirements:**
- Support 100M+ URL mappings
- Handle 10K-100K requests per second
- Short code length: 6-8 characters
- Storage: Efficient space utilization
- Lookup latency: < 10ms

## Requirements

### Functional Requirements

1. **Shorten URL**: Convert long URL to short code
2. **Expand URL**: Retrieve long URL from short code
3. **Custom URLs**: Allow users to specify custom short codes
4. **Analytics**: Track click counts, timestamps
5. **Validation**: Validate URL format
6. **Expiration**: Optional TTL for URLs

### Non-Functional Requirements

**Performance:**
- Short code generation: < 1ms
- URL lookup: < 10ms
- High throughput: 10K+ ops/sec

**Reliability:**
- No data loss
- Handle collisions
- Validate URLs

**Storage:**
- Efficient space usage
- Fast lookups
- Support 100M+ mappings

## Data Modeling

### Database Schema

**Option 1: Relational Database (MySQL/PostgreSQL)**

```sql
CREATE TABLE url_mappings (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    short_code VARCHAR(8) UNIQUE NOT NULL,
    long_url TEXT NOT NULL,
    custom BOOLEAN DEFAULT FALSE,
    user_id BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL,
    click_count BIGINT DEFAULT 0,
    INDEX idx_short_code (short_code),
    INDEX idx_user_id (user_id),
    INDEX idx_expires_at (expires_at)
);

CREATE TABLE url_analytics (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    short_code VARCHAR(8) NOT NULL,
    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    referrer TEXT,
    INDEX idx_short_code (short_code),
    INDEX idx_clicked_at (clicked_at)
);
```

**Option 2: Key-Value Store (Redis)**

```python
# Redis structure
# Key: short_code -> Value: long_url
# Key: short_code:analytics -> Hash: {clicks, created_at, expires_at}
# Key: long_url:hash -> Value: short_code (for deduplication)
```

### Data Model Classes

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class URLMapping:
    id: Optional[int]
    short_code: str
    long_url: str
    custom: bool
    user_id: Optional[int]
    created_at: datetime
    expires_at: Optional[datetime]
    click_count: int
    
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

@dataclass
class URLAnalytics:
    id: Optional[int]
    short_code: str
    clicked_at: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
    referrer: Optional[str]
```

## Hashing and Encoding

### Base62 Encoding

**Character Set**: `0-9`, `a-z`, `A-Z` (62 characters)

```python
BASE62_CHARS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def encode_base62(num: int) -> str:
    """Encode number to base62 string."""
    if num == 0:
        return BASE62_CHARS[0]
    
    result = []
    while num > 0:
        result.append(BASE62_CHARS[num % 62])
        num //= 62
    
    return ''.join(reversed(result))

def decode_base62(encoded: str) -> int:
    """Decode base62 string to number."""
    num = 0
    for char in encoded:
        num = num * 62 + BASE62_CHARS.index(char)
    return num
```

### Hash-Based Approach

```python
import hashlib
import base64

def generate_short_code(long_url: str, length: int = 6) -> str:
    """Generate short code using MD5 hash."""
    # Hash the URL
    hash_bytes = hashlib.md5(long_url.encode()).digest()
    
    # Encode to base64 and take first N characters
    encoded = base64.urlsafe_b64encode(hash_bytes).decode('ascii')
    
    # Remove padding and special characters, take first N chars
    encoded = encoded.rstrip('=').replace('-', '').replace('_', '')
    
    return encoded[:length]
```

### Counter-Based Approach

```python
class URLShortener:
    def __init__(self):
        self.counter = 0  # In production, use database sequence
    
    def generate_short_code(self, long_url: str) -> str:
        """Generate short code from counter."""
        self.counter += 1
        return encode_base62(self.counter)
```

### Hybrid Approach (Recommended)

```python
def generate_short_code(long_url: str, length: int = 6) -> str:
    """Generate short code using hash + timestamp."""
    # Combine URL with timestamp for uniqueness
    timestamp = int(time.time() * 1000)  # milliseconds
    combined = f"{long_url}{timestamp}"
    
    # Hash
    hash_bytes = hashlib.md5(combined.encode()).digest()
    
    # Convert to base62
    num = int.from_bytes(hash_bytes[:4], byteorder='big')
    code = encode_base62(num)
    
    # Ensure minimum length
    while len(code) < length:
        code = '0' + code
    
    return code[:length]
```

## API Design

### REST API

```python
from flask import Flask, request, jsonify, redirect
from typing import Optional

app = Flask(__name__)

class URLShortenerService:
    def __init__(self, db, cache):
        self.db = db
        self.cache = cache
    
    def shorten_url(self, long_url: str, custom_code: Optional[str] = None,
                   user_id: Optional[int] = None, expires_in_days: Optional[int] = None) -> str:
        """Shorten URL and return short code."""
        # Validate URL
        if not self._validate_url(long_url):
            raise ValueError("Invalid URL")
        
        # Check if custom code provided
        if custom_code:
            if not self._is_valid_code(custom_code):
                raise ValueError("Invalid custom code")
            if self._code_exists(custom_code):
                raise ValueError("Custom code already exists")
            short_code = custom_code
        else:
            # Generate short code
            short_code = self._generate_unique_code(long_url)
        
        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.now() + timedelta(days=expires_in_days)
        
        # Store mapping
        mapping = URLMapping(
            id=None,
            short_code=short_code,
            long_url=long_url,
            custom=(custom_code is not None),
            user_id=user_id,
            created_at=datetime.now(),
            expires_at=expires_at,
            click_count=0
        )
        
        self.db.save_mapping(mapping)
        self.cache.set(short_code, long_url, ttl=expires_in_days * 86400 if expires_in_days else None)
        
        return short_code
    
    def expand_url(self, short_code: str) -> Optional[str]:
        """Retrieve long URL from short code."""
        # Check cache first
        long_url = self.cache.get(short_code)
        if long_url:
            return long_url
        
        # Check database
        mapping = self.db.get_mapping(short_code)
        if not mapping:
            return None
        
        if mapping.is_expired():
            return None
        
        # Update click count
        self.db.increment_click_count(short_code)
        
        # Cache result
        self.cache.set(short_code, mapping.long_url)
        
        return mapping.long_url
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL format."""
        try:
            from urllib.parse import urlparse
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _is_valid_code(self, code: str) -> bool:
        """Validate custom code format."""
        if len(code) < 4 or len(code) > 8:
            return False
        return all(c in BASE62_CHARS for c in code)
    
    def _code_exists(self, code: str) -> bool:
        """Check if code already exists."""
        return self.db.code_exists(code)
    
    def _generate_unique_code(self, long_url: str) -> str:
        """Generate unique short code."""
        max_attempts = 10
        for _ in range(max_attempts):
            code = generate_short_code(long_url)
            if not self._code_exists(code):
                return code
        raise RuntimeError("Failed to generate unique code")

@app.route('/api/shorten', methods=['POST'])
def shorten():
    data = request.json
    long_url = data.get('url')
    custom_code = data.get('custom_code')
    user_id = data.get('user_id')
    expires_in_days = data.get('expires_in_days')
    
    try:
        service = URLShortenerService(db, cache)
        short_code = service.shorten_url(long_url, custom_code, user_id, expires_in_days)
        return jsonify({
            'short_code': short_code,
            'short_url': f'https://short.ly/{short_code}'
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/<short_code>', methods=['GET'])
def redirect_to_long_url(short_code):
    service = URLShortenerService(db, cache)
    long_url = service.expand_url(short_code)
    
    if not long_url:
        return jsonify({'error': 'URL not found'}), 404
    
    # Track analytics
    service.track_click(short_code, request.remote_addr, request.headers.get('User-Agent'))
    
    return redirect(long_url, code=302)
```

## Storage Design

### Relational Database (Recommended for Meta Interview)

**Pros:**
- ACID guarantees
- Easy to query analytics
- Support for complex relationships
- Well-understood

**Cons:**
- May need sharding at very large scale
- Slightly slower than key-value stores

**Schema Design:**
```sql
-- Primary table for URL mappings
CREATE TABLE url_mappings (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    short_code VARCHAR(8) UNIQUE NOT NULL,
    long_url TEXT NOT NULL,
    -- Indexes for fast lookups
    INDEX idx_short_code (short_code)
);

-- Analytics table (separate for performance)
CREATE TABLE url_clicks (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    short_code VARCHAR(8) NOT NULL,
    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_short_code_time (short_code, clicked_at)
);
```

### Key-Value Store (Alternative)

**Pros:**
- Very fast lookups
- Simple structure
- Good for caching

**Cons:**
- Limited query capabilities
- Harder to do analytics
- May need separate database for analytics

## Collision Handling

### Strategy 1: Retry with Different Input

```python
def _generate_unique_code(self, long_url: str) -> str:
    """Generate unique code with collision handling."""
    max_attempts = 10
    salt = 0
    
    for attempt in range(max_attempts):
        # Add salt to make hash different
        salted_url = f"{long_url}{salt}{time.time()}"
        code = generate_short_code(salted_url, length=6)
        
        if not self._code_exists(code):
            return code
        
        salt += 1
    
    raise RuntimeError("Failed to generate unique code after retries")
```

### Strategy 2: Increase Code Length

```python
def _generate_unique_code(self, long_url: str, base_length: int = 6) -> str:
    """Generate code, increasing length on collision."""
    length = base_length
    max_length = 10
    
    while length <= max_length:
        code = generate_short_code(long_url, length=length)
        if not self._code_exists(code):
            return code
        length += 1
    
    raise RuntimeError("Failed to generate unique code")
```

### Strategy 3: Database Sequence

```python
def _generate_unique_code(self) -> str:
    """Generate code from database sequence (guaranteed unique)."""
    # Get next sequence number from database
    sequence_num = self.db.get_next_sequence()
    return encode_base62(sequence_num)
```

### Strategy 4: Check Before Insert

```python
def _generate_unique_code(self, long_url: str) -> str:
    """Generate code with database-level uniqueness check."""
    while True:
        code = generate_short_code(long_url)
        
        # Try to insert, handle duplicate key error
        try:
            self.db.insert_mapping(code, long_url)
            return code
        except DuplicateKeyError:
            # Collision detected, retry
            continue
```

## Custom URLs

### Implementation

```python
def shorten_url(self, long_url: str, custom_code: Optional[str] = None) -> str:
    """Shorten URL with optional custom code."""
    if custom_code:
        # Validate custom code
        if not self._is_valid_custom_code(custom_code):
            raise ValueError("Invalid custom code format")
        
        # Check availability
        if self._code_exists(custom_code):
            raise ValueError("Custom code already taken")
        
        # Use custom code
        short_code = custom_code
        is_custom = True
    else:
        # Generate random code
        short_code = self._generate_unique_code(long_url)
        is_custom = False
    
    # Store mapping
    self._store_mapping(short_code, long_url, is_custom)
    return short_code

def _is_valid_custom_code(self, code: str) -> bool:
    """Validate custom code format."""
    # Length: 4-8 characters
    if len(code) < 4 or len(code) > 8:
        return False
    
    # Only alphanumeric and hyphens
    import re
    if not re.match(r'^[a-zA-Z0-9-]+$', code):
        return False
    
    # Reserved words
    reserved = ['api', 'admin', 'www', 'mail', 'ftp']
    if code.lower() in reserved:
        return False
    
    return True
```

## Caching Strategy

### Multi-Level Caching

```python
class CacheManager:
    def __init__(self):
        self.l1_cache = {}  # In-memory LRU cache
        self.l2_cache = redis_client  # Redis cache
        self.l1_max_size = 10000
    
    def get(self, short_code: str) -> Optional[str]:
        # L1 cache (fastest)
        if short_code in self.l1_cache:
            return self.l1_cache[short_code]
        
        # L2 cache (Redis)
        long_url = self.l2_cache.get(f"url:{short_code}")
        if long_url:
            # Populate L1 cache
            self._add_to_l1(short_code, long_url)
            return long_url
        
        return None
    
    def set(self, short_code: str, long_url: str, ttl: Optional[int] = None):
        # Set in both caches
        self._add_to_l1(short_code, long_url)
        self.l2_cache.setex(f"url:{short_code}", ttl or 86400, long_url)
    
    def _add_to_l1(self, short_code: str, long_url: str):
        """Add to L1 cache with LRU eviction."""
        if len(self.l1_cache) >= self.l1_max_size:
            # Remove oldest (simple FIFO for demo)
            oldest = next(iter(self.l1_cache))
            del self.l1_cache[oldest]
        
        self.l1_cache[short_code] = long_url
```

## Deep Dive

### URL Validation

```python
def validate_url(url: str) -> bool:
    """Comprehensive URL validation."""
    try:
        from urllib.parse import urlparse
        result = urlparse(url)
        
        # Must have scheme and netloc
        if not result.scheme or not result.netloc:
            return False
        
        # Scheme must be http or https
        if result.scheme not in ['http', 'https']:
            return False
        
        # Check for valid domain
        if '.' not in result.netloc:
            return False
        
        return True
    except:
        return False
```

### Analytics Tracking

```python
def track_click(self, short_code: str, ip_address: str, user_agent: str):
    """Track URL click for analytics."""
    analytics = URLAnalytics(
        id=None,
        short_code=short_code,
        clicked_at=datetime.now(),
        ip_address=ip_address,
        user_agent=user_agent,
        referrer=None
    )
    
    # Async write to avoid blocking
    self.analytics_queue.put(analytics)
    
    # Increment click count
    self.db.increment_click_count(short_code)
```

### Expiration Handling

```python
def cleanup_expired_urls(self):
    """Background job to clean up expired URLs."""
    expired_mappings = self.db.get_expired_mappings()
    
    for mapping in expired_mappings:
        # Remove from cache
        self.cache.delete(mapping.short_code)
        
        # Optionally: Archive or delete from database
        # self.db.delete_mapping(mapping.short_code)
```

## What Interviewers Look For

### Technical Skills

1. **Data Modeling Ability**
   - Can you design a proper database schema?
   - Do you understand relationships and constraints?
   - Can you choose appropriate indexes?
   - **Red Flags**: Missing indexes, no uniqueness constraints, poor normalization

2. **Algorithm Knowledge**
   - Understanding of hashing and encoding (Base62, Base64)
   - Collision handling strategies
   - Trade-offs between different approaches
   - **Red Flags**: No collision handling, naive approaches

3. **System Design Thinking**
   - Storage choice reasoning (relational vs NoSQL)
   - Caching strategy justification
   - API design considerations
   - **Red Flags**: No reasoning for choices, over-engineering

### Problem-Solving Approach

1. **Clarifying Questions**
   - Do you ask about requirements (custom URLs, analytics, expiration)?
   - Do you clarify scale and constraints?
   - **Red Flags**: Jumping to solution without understanding

2. **Handling Edge Cases**
   - Collision scenarios
   - Invalid URLs
   - Custom URL conflicts
   - **Red Flags**: Ignoring edge cases, no error handling

3. **Trade-off Analysis**
   - Can you discuss pros/cons of different approaches?
   - Do you justify your choices?
   - **Red Flags**: No trade-off discussion, dogmatic choices

### Communication Skills

1. **Clear Explanation**
   - Can you explain your design clearly?
   - Do you use appropriate terminology?
   - **Red Flags**: Unclear explanations, jargon without context

2. **Code Quality**
   - Clean, readable code examples
   - Proper error handling
   - **Red Flags**: Sloppy code, no error handling

### Meta-Specific Focus

1. **Data Structures & Algorithms**
   - Emphasis on efficient algorithms
   - Understanding of time/space complexity
   - **Key**: Show strong CS fundamentals

2. **Practical Implementation**
   - Can you implement the solution?
   - Do you consider real-world constraints?
   - **Key**: Balance theory with practicality

## Summary

### Key Takeaways

1. **Data Modeling**: Relational schema with proper indexes
2. **Encoding**: Base62 encoding for short codes
3. **Collision Handling**: Retry with salt, increase length, or use sequence
4. **Custom URLs**: Validation and availability checking
5. **Caching**: Multi-level caching for fast lookups
6. **Storage**: Relational DB for ACID, key-value for speed

### Common Interview Questions

1. **How would you handle collisions?**
   - Retry with different input (salt)
   - Increase code length
   - Use database sequence
   - Check before insert

2. **How would you store short-long URL mapping?**
   - Relational DB: `url_mappings` table with indexes
   - Key-value: Redis with short_code as key
   - Hybrid: DB for persistence, cache for speed

3. **How would you allow for custom short URLs?**
   - Validate format (length, characters, reserved words)
   - Check availability before assignment
   - Mark as custom in database
   - Enforce uniqueness constraint

### Design Principles

1. **Efficiency**: Fast lookups with caching
2. **Uniqueness**: Handle collisions properly
3. **Flexibility**: Support custom URLs
4. **Reliability**: Validate inputs, handle errors
5. **Analytics**: Track usage for insights

Understanding URL shortener design is crucial for Meta interviews focusing on:
- Data modeling and schema design
- Hashing and encoding algorithms
- Collision handling strategies
- Storage trade-offs
- API design

