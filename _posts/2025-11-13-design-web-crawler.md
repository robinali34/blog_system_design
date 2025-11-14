---
layout: post
title: "Design a Web Crawler System"
date: 2025-11-13
categories: [System Design, Interview Example, Distributed Systems, Web Crawling]
excerpt: "A comprehensive guide to designing a scalable web crawler system, covering architecture, politeness policies, fault tolerance, and efficient crawling strategies for indexing billions of web pages."
---

## Introduction

A web crawler is a program that automatically traverses the web by downloading web pages and following links from one page to another. It is used to index the web for search engines, collect data for research, or monitor websites for changes.

This post provides a detailed walkthrough of designing a scalable web crawler system that can efficiently crawl billions of web pages while adhering to politeness policies and handling failures gracefully. This is a common system design interview question that tests your understanding of distributed systems, queue management, rate limiting, and data storage at scale.

## Problem Statement

**Design a web crawler system that can:**

1. Crawl the web starting from a given set of seed URLs
2. Extract text data from each web page and store it for later processing
3. Follow links to discover new pages to crawl
4. Handle billions of web pages efficiently
5. Adhere to politeness policies (robots.txt, rate limiting)
6. Handle failures gracefully and resume crawling without losing progress

**Out of Scope:**
- Processing of the extracted text data (e.g., training LLMs)
- Handling non-text data (images, videos, etc.)
- Handling dynamic content (JavaScript-rendered pages)
- Handling authentication (login-required pages)

## Requirements Gathering

### Functional Requirements

**Core Requirements:**
1. **Crawl URLs**: Start from seed URLs and crawl discovered pages
2. **Extract Text Data**: Extract text content from HTML pages
3. **Follow Links**: Discover and queue new URLs from crawled pages
4. **Store Data**: Store extracted text data for later processing
5. **Track Progress**: Track which URLs have been crawled and which are pending

**Out of Scope:**
- Text data processing (LLM training, indexing, ranking)
- Non-text content handling
- Dynamic content rendering
- Authentication handling

### Non-Functional Requirements

**Scale Assumptions:**
- **10 billion pages** on the web
- **Average page size**: 2MB
- **Time constraint**: Complete crawling in 5 days
- **Total data**: ~20PB of data

**Core Requirements:**
1. **Fault Tolerance**: Handle failures gracefully and resume without losing progress
2. **Politeness**: Adhere to robots.txt and avoid overloading servers
3. **Efficiency**: Complete crawling within 5 days
4. **Scalability**: Handle 10 billion pages
5. **Deduplication**: Avoid crawling the same URL multiple times
6. **Rate Limiting**: Respect per-domain rate limits

**Out of Scope:**
- Security (protecting from malicious actors)
- Cost optimization
- Legal compliance and privacy regulations

## System Interface

**Input:**
- Seed URLs to start crawling from

**Output:**
- Text data extracted from web pages (stored in blob storage)

## Data Flow

The high-level data flow for our web crawler:

1. **Seed URLs** → Add to frontier queue
2. **Frontier Queue** → Dequeue URL for crawling
3. **DNS Resolution** → Resolve domain name to IP address
4. **Fetch HTML** → Download HTML from web server
5. **Parse HTML** → Extract text data and links
6. **Store Text** → Save extracted text to blob storage
7. **Extract Links** → Discover new URLs and add to frontier queue
8. **Repeat** → Continue until all URLs are crawled

## High-Level Design

```
┌─────────────────────────────────────────────────────────┐
│                    System Boundary                       │
│                                                           │
│  ┌──────────────┐                                         │
│  │   Frontier   │  ──── Queue of URLs to crawl            │
│  │    Queue     │                                         │
│  └──────┬───────┘                                         │
│         │                                                  │
│         ▼                                                  │
│  ┌──────────────┐                                         │
│  │   Crawler    │  ──── Fetches pages, extracts data     │
│  │   Workers    │                                         │
│  └──────┬───────┘                                         │
│         │                                                  │
│         ▼                                                  │
│  ┌──────────────┐                                         │
│  │     DNS      │  ──── Resolves domain names            │
│  └──────┬───────┘                                         │
│         │                                                  │
│         ▼                                                  │
│  ┌──────────────┐                                         │
│  │   Parser     │  ──── Extracts text and links           │
│  │   Workers    │                                         │
│  └──────┬───────┘                                         │
│         │                                                  │
│         ▼                                                  │
│  ┌──────────────┐                                         │
│  │  Blob Store  │  ──── Stores extracted text data       │
│  │     (S3)     │                                         │
│  └──────────────┘                                         │
│                                                           │
│  ┌──────────────┐                                         │
│  │  Metadata DB │  ──── Tracks crawled URLs, status      │
│  └──────────────┘                                         │
│                                                           │
└───────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│   Web Servers   │  ──── External web pages
└─────────────────┘
```

### Core Components

1. **Frontier Queue**: Queue of URLs to crawl (Kafka, Redis, or SQS)
2. **Crawler Workers**: Fetch web pages from external servers
3. **DNS Service**: Resolve domain names to IP addresses
4. **Parser Workers**: Extract text data and links from HTML
5. **Blob Storage (S3)**: Store extracted text data
6. **Metadata Database**: Track crawled URLs, status, and metadata

## Detailed Design

### 1. Frontier Queue

The frontier queue stores URLs that need to be crawled. It should support:
- **High throughput**: Millions of URLs per second
- **Deduplication**: Avoid duplicate URLs
- **Prioritization**: Crawl important URLs first
- **Persistence**: Survive system failures

**Technology Options:**

**Kafka:**
- ✅ High throughput (millions of messages/second)
- ✅ Persistence and durability
- ✅ Multiple consumer groups
- ✅ Built-in partitioning
- ❌ More complex setup
- ❌ Overkill for simple use cases

**Redis:**
- ✅ Simple and fast
- ✅ Built-in data structures (sets, sorted sets)
- ✅ Good for deduplication
- ❌ Limited persistence options
- ❌ Memory constraints

**SQS:**
- ✅ Fully managed
- ✅ Simple to use
- ✅ Built-in retry logic
- ❌ Lower throughput than Kafka
- ❌ Less control over prioritization

**Recommendation**: Use **Kafka** for high-scale crawling (10B pages) due to its high throughput and persistence capabilities.

**Queue Structure:**
- Partition by domain to ensure politeness (one partition per domain)
- Use priority queues for important URLs
- Implement deduplication using Bloom filters or hash sets

### 2. Crawler Workers

Crawler workers fetch HTML pages from web servers. They need to:
- **Respect robots.txt**: Check robots.txt before crawling
- **Rate Limiting**: Limit requests per domain
- **Handle Failures**: Retry failed requests
- **Timeout Handling**: Set appropriate timeouts

**Architecture:**
```
Crawler Worker Pool
├── Worker 1 → Domain A (rate limited)
├── Worker 2 → Domain B (rate limited)
├── Worker 3 → Domain C (rate limited)
└── ...
```

**Rate Limiting Strategy:**
- Maintain per-domain rate limiters
- Use token bucket or sliding window algorithms
- Default: 1 request per second per domain
- Respect robots.txt crawl-delay directives

**Robots.txt Handling:**
- Fetch and parse robots.txt for each domain
- Cache robots.txt rules (TTL: 24 hours)
- Check rules before crawling each URL
- Respect User-Agent requirements

**Failure Handling:**
- Retry transient failures (5xx errors) with exponential backoff
- Skip permanent failures (4xx errors)
- Track failure rates per domain
- Blacklist domains with high failure rates

### 3. DNS Resolution

DNS resolution is a critical bottleneck. We need to:
- **Cache DNS lookups**: Avoid repeated DNS queries
- **Handle DNS failures**: Retry with backoff
- **Avoid overloading DNS servers**: Rate limit DNS queries

**DNS Caching Strategy:**
- Cache DNS responses (TTL from DNS record)
- Use in-memory cache (Redis) for frequently accessed domains
- Fallback to DNS server if cache miss
- Handle DNS failures gracefully

**Implementation:**
- Use DNS caching library (e.g., dns-cache)
- Cache in Redis with TTL from DNS response
- Maintain DNS resolver pool for parallel lookups

### 4. Parser Workers

Parser workers extract text data and links from HTML:
- **HTML Parsing**: Parse HTML and extract text content
- **Link Extraction**: Find all links (href attributes)
- **Normalization**: Normalize URLs (remove fragments, resolve relative URLs)
- **Filtering**: Filter out unwanted URLs (mailto:, javascript:, etc.)

**Text Extraction:**
- Remove HTML tags
- Extract text content
- Clean and normalize text
- Handle encoding (UTF-8, etc.)

**Link Extraction:**
- Parse `<a href="">` tags
- Extract absolute and relative URLs
- Normalize URLs (resolve relative URLs)
- Filter URLs (remove duplicates, invalid URLs)

**URL Normalization:**
- Convert to absolute URLs
- Remove fragments (#)
- Remove default ports (80, 443)
- Convert to lowercase
- Remove trailing slashes (optional)

### 5. Blob Storage (S3)

Store extracted text data in blob storage:
- **Scalability**: Handle petabytes of data
- **Durability**: 99.999999999% (11 9's) durability
- **Cost**: Low-cost storage for large files
- **Access**: Easy retrieval for downstream processing

**Storage Structure:**
```
s3://crawler-data/
├── domain1.com/
│   ├── page1.html.txt
│   ├── page2.html.txt
│   └── ...
├── domain2.com/
│   └── ...
```

**Metadata:**
- Store metadata in separate database (not in S3)
- Include: URL, crawl timestamp, file path, size, etc.

### 6. Metadata Database

Track crawled URLs and their status:
- **URL Status**: Pending, Crawling, Completed, Failed
- **Crawl History**: Timestamp, status, error messages
- **Deduplication**: Track seen URLs
- **Statistics**: Crawl progress, success rates

**Database Schema:**

```sql
CREATE TABLE urls (
    url_hash VARCHAR(64) PRIMARY KEY,
    url TEXT NOT NULL,
    domain VARCHAR(255) NOT NULL,
    status ENUM('pending', 'crawling', 'completed', 'failed') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    crawled_at TIMESTAMP,
    retry_count INT DEFAULT 0,
    error_message TEXT,
    file_path VARCHAR(512),
    file_size BIGINT,
    INDEX idx_domain (domain),
    INDEX idx_status (status),
    INDEX idx_crawled_at (crawled_at)
);

CREATE TABLE crawl_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    url_hash VARCHAR(64) NOT NULL,
    status ENUM('crawling', 'completed', 'failed') NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT,
    FOREIGN KEY (url_hash) REFERENCES urls(url_hash),
    INDEX idx_url_hash (url_hash),
    INDEX idx_timestamp (timestamp)
);
```

**Technology Choice:**
- **PostgreSQL**: For structured metadata and queries
- **Cassandra**: For high-scale write-heavy workloads
- **DynamoDB**: For fully managed solution

**Recommendation**: Use **PostgreSQL** for structured queries and **Cassandra** for high-scale scenarios.

## Scalability and Performance

### Throughput Calculation

**Target**: Crawl 10 billion pages in 5 days

**Calculation:**
- Total pages: 10B
- Time: 5 days = 432,000 seconds
- Required throughput: 10B / 432,000 ≈ **23,148 pages/second**

**With overhead and failures:**
- Assume 50% overhead (DNS, retries, etc.)
- Target: **~35,000 pages/second**

### Scaling Strategy

**Horizontal Scaling:**
- Scale crawler workers: 1,000+ workers
- Scale parser workers: 500+ workers
- Scale Kafka partitions: 100+ partitions
- Scale database: Shard by domain or URL hash

**Bottlenecks:**
1. **DNS Resolution**: Cache aggressively, use DNS pools
2. **Network Bandwidth**: Distribute across regions
3. **Database Writes**: Batch writes, use write-optimized DB
4. **Queue Throughput**: Partition Kafka topics by domain

### Deduplication

**Bloom Filter:**
- Use Bloom filter for fast duplicate detection
- False positives acceptable (will skip some URLs)
- Memory efficient: ~10 bits per URL
- For 10B URLs: ~12.5GB memory

**Hash Set:**
- Use distributed hash set (Redis) for exact deduplication
- More memory intensive but accurate
- Use for critical URLs

**Hybrid Approach:**
- Use Bloom filter for first-pass filtering
- Use hash set for confirmed unique URLs
- Balance between memory and accuracy

### Politeness and Rate Limiting

**Per-Domain Rate Limiting:**
- Default: 1 request per second per domain
- Respect robots.txt crawl-delay
- Use token bucket algorithm
- Track rate limiters per domain

**Robots.txt Caching:**
- Cache robots.txt rules (TTL: 24 hours)
- Store in Redis or database
- Parse and apply rules before crawling

**Implementation:**
```python
class RateLimiter:
    def __init__(self, domain, requests_per_second=1):
        self.domain = domain
        self.requests_per_second = requests_per_second
        self.tokens = requests_per_second
        self.last_update = time.time()
    
    def acquire(self):
        now = time.time()
        elapsed = now - self.last_update
        self.tokens = min(
            self.requests_per_second,
            self.tokens + elapsed * self.requests_per_second
        )
        self.last_update = now
        
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False
```

## Fault Tolerance

### Failure Scenarios

1. **Crawler Worker Failure**: Worker crashes mid-crawl
2. **Network Failure**: Connection timeout or DNS failure
3. **Web Server Failure**: 5xx errors from web servers
4. **Database Failure**: Metadata DB unavailable
5. **Queue Failure**: Kafka partition unavailable

### Handling Strategies

**Crawler Worker Failures:**
- Use idempotent operations
- Track progress in database
- Re-queue URLs on worker failure
- Implement heartbeat mechanism

**Network Failures:**
- Retry with exponential backoff
- Skip after max retries
- Track failure rates per domain
- Blacklist problematic domains

**Database Failures:**
- Use database replication
- Implement retry logic
- Use eventual consistency where possible
- Batch writes to reduce load

**Queue Failures:**
- Use Kafka replication (3 replicas)
- Implement consumer group rebalancing
- Handle partition leader changes

### Idempotency

**URL Processing:**
- Check if URL already crawled before processing
- Use database transaction to mark URL as crawling
- Store results atomically
- Handle duplicate processing gracefully

**Implementation:**
```python
def crawl_url(url):
    url_hash = hash_url(url)
    
    # Check if already crawled
    if is_crawled(url_hash):
        return
    
    # Mark as crawling (atomic operation)
    if not mark_as_crawling(url_hash):
        return  # Another worker is processing
    
    try:
        # Fetch and parse
        html = fetch_html(url)
        text = extract_text(html)
        links = extract_links(html)
        
        # Store results
        store_text(url, text)
        add_links_to_queue(links)
        mark_as_completed(url_hash)
    except Exception as e:
        mark_as_failed(url_hash, str(e))
        raise
```

## Advanced Considerations

### 1. URL Prioritization

**Priority Queue:**
- Prioritize important URLs (high PageRank, popular domains)
- Use multiple priority levels
- Implement priority queue in Kafka or Redis

**Strategies:**
- **PageRank**: Prioritize URLs with high PageRank
- **Domain Popularity**: Prioritize popular domains
- **Recency**: Prioritize recently updated pages
- **User Signals**: Prioritize based on user clicks/views

### 2. Crawler Traps

**Detection:**
- Track URL depth (number of hops from seed)
- Detect URL patterns (session IDs, timestamps)
- Limit depth per domain
- Detect cycles in URL graph

**Prevention:**
- Set maximum depth limit (e.g., 10 hops)
- Filter URLs with suspicious patterns
- Use canonical URLs
- Track URL patterns per domain

### 3. Distributed Crawling

**Domain-Based Partitioning:**
- Partition URLs by domain
- Each worker handles specific domains
- Ensures politeness (one worker per domain)
- Simplifies rate limiting

**Geographic Distribution:**
- Deploy crawlers in multiple regions
- Crawl from region closest to web server
- Reduce latency and bandwidth costs
- Handle regional restrictions

### 4. Monitoring and Observability

**Key Metrics:**
- Crawl rate (pages/second)
- Success rate (% of successful crawls)
- Failure rate by domain
- Queue depth (pending URLs)
- Storage usage
- Worker utilization

**Alerting:**
- Low crawl rate
- High failure rate
- Queue backup
- Worker failures
- Storage capacity

**Tools:**
- Prometheus for metrics
- Grafana for dashboards
- ELK stack for logs
- PagerDuty for alerts

## Technology Stack Summary

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Frontier Queue | Kafka | High throughput, persistence, partitioning |
| Crawler Workers | Python/Go | HTTP clients, async processing |
| DNS Resolution | DNS Cache (Redis) | Fast lookups, caching |
| Parser Workers | Python (BeautifulSoup) | HTML parsing, text extraction |
| Blob Storage | S3 | Scalable, durable, cost-effective |
| Metadata DB | PostgreSQL/Cassandra | Structured queries, high-scale writes |
| Rate Limiting | Redis | Token bucket, per-domain limits |
| Monitoring | Prometheus + Grafana | Metrics and dashboards |

## Interview Tips

### For Mid-Level Engineers

**Focus Areas:**
- High-level architecture
- Basic components (queue, workers, storage)
- Simple scaling strategies
- Basic fault tolerance

**Expected Depth:**
- Understand data flow
- Know basic technologies (Kafka, S3, PostgreSQL)
- Discuss simple rate limiting
- Handle basic failures

### For Senior Engineers

**Focus Areas:**
- Detailed component design
- Advanced scaling strategies
- Politeness and rate limiting details
- Fault tolerance and idempotency
- Performance optimization

**Expected Depth:**
- Deep dive into queue technology choices
- Detailed rate limiting implementation
- DNS caching strategies
- Database sharding strategies
- Throughput calculations

### For Staff+ Engineers

**Focus Areas:**
- System-wide optimizations
- Advanced distributed systems concepts
- Cost optimization
- Operational excellence
- Trade-off analysis

**Expected Depth:**
- Multiple deep dives (3+ areas)
- Innovative solutions
- Real-world experience
- Complex problem-solving
- Strategic thinking

## Conclusion

Designing a web crawler requires careful consideration of:

1. **Scalability**: Handle billions of pages efficiently
2. **Politeness**: Respect robots.txt and rate limits
3. **Fault Tolerance**: Handle failures gracefully
4. **Deduplication**: Avoid crawling duplicates
5. **Performance**: Meet time constraints

Key design decisions:
- **Kafka** for high-throughput queue management
- **Domain-based partitioning** for politeness
- **Aggressive DNS caching** for performance
- **Bloom filters + hash sets** for deduplication
- **S3** for scalable blob storage
- **PostgreSQL/Cassandra** for metadata tracking

The system should be designed to scale horizontally, handle failures gracefully, and respect web server resources while efficiently crawling the web.

## References

- [Hello Interview - Design Web Crawler](https://www.hellointerview.com/learn/system-design/problem-breakdowns/web-crawler)
- [Web Crawler Video Walkthrough](https://www.youtube.com/watch?v=krsuaUp__pM)

