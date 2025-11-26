---
layout: post
title: "Design a Distributed Web Crawler Using 10,000 Nodes - System Design Interview"
date: 2025-11-14
categories: [System Design, Interview Example, Distributed Systems, Web Crawling, Edge Computing]
excerpt: "A comprehensive guide to designing a distributed web crawler system using 10,000 distributed nodes, covering command and control architecture, load distribution, fault tolerance, stealth mechanisms, and architectural patterns for large-scale distributed crawling."
---

## Introduction

A distributed web crawler leverages thousands of distributed nodes (edge devices, volunteer networks, or distributed computing resources) to crawl the web at massive scale. This architecture presents unique challenges: coordinating thousands of nodes, distributing work efficiently, handling node failures, maintaining stealth, and aggregating results reliably.

This post provides a detailed walkthrough of designing a distributed web crawler system using 10,000 nodes, covering key architectural decisions, command and control patterns, load balancing, fault tolerance, and scalability challenges. This is an advanced system design interview question that tests your understanding of distributed systems, peer-to-peer architectures, and handling massive scale with unreliable nodes.

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

**Design a distributed web crawler system using 10,000 distributed nodes with the following requirements:**

1. Distribute crawling workload across 10,000 nodes
2. Command and control (C2) infrastructure to coordinate nodes
3. Work assignment and load balancing
4. Result aggregation from distributed nodes
5. Fault tolerance (nodes can fail or go offline)
6. Stealth mechanisms (avoid detection, rate limiting per IP)
7. Health monitoring and node management
8. Data deduplication across nodes
9. Handle node churn (nodes joining/leaving)
10. Efficient bandwidth utilization

**Scale Requirements:**
- 10,000 distributed nodes
- Each node can crawl ~10 pages/second
- Total capacity: 100,000 pages/second
- Target: Crawl 10 billion pages in 5 days
- Node availability: 70% average (nodes can go offline)
- Network latency: Variable (50ms - 500ms)
- Bandwidth per node: Variable (1-100 Mbps)

## Requirements

### Functional Requirements

**Core Features:**
1. **Node Registration**: Nodes register with C2 server
2. **Work Assignment**: C2 server assigns URLs to nodes
3. **Crawling**: Nodes fetch pages and extract data
4. **Result Submission**: Nodes submit results back to C2
5. **Health Monitoring**: Track node health and availability
6. **Load Balancing**: Distribute work evenly across nodes
7. **Fault Tolerance**: Handle node failures gracefully
8. **Deduplication**: Avoid duplicate work across nodes
9. **Stealth**: Rotate IPs, respect rate limits, avoid detection
10. **Result Aggregation**: Collect and store results centrally

**Out of Scope:**
- Node compromise/exploitation mechanisms
- Malicious payload delivery
- Data exfiltration beyond crawling results
- Persistence mechanisms

### Non-Functional Requirements

1. **Availability**: System should work with 30% node failure rate
2. **Reliability**: No work loss when nodes fail
3. **Performance**: 
   - Work assignment latency: < 100ms
   - Result submission latency: < 500ms
   - C2 response time: < 200ms
4. **Scalability**: Handle 10,000+ nodes
5. **Consistency**: Eventually consistent for work assignment
6. **Stealth**: Avoid detection by target websites
7. **Resilience**: Survive C2 server failures

## Capacity Estimation

### Traffic Estimates

- **Total Nodes**: 10,000
- **Active Nodes**: 7,000 (70% availability)
- **Crawling Rate per Node**: 10 pages/second
- **Total Crawling Capacity**: 70,000 pages/second
- **Target**: 10 billion pages in 5 days
- **Required Rate**: ~23,148 pages/second
- **Utilization**: ~33% (well within capacity)

### Storage Estimates

**C2 Server Storage:**
- Node metadata: 10K nodes × 1KB = 10MB
- Work queue: 100M URLs × 200 bytes = 20GB
- Result metadata: 10B results × 100 bytes = 1TB
- Total C2 storage: ~1TB

**Per-Node Storage:**
- Temporary result storage: 1GB per node
- Total distributed storage: 10TB

**Central Result Storage:**
- Extracted text: 10B pages × 200KB = 2PB
- With compression: 1PB

### Bandwidth Estimates

**C2 to Nodes:**
- Work assignments: 70K QPS × 500 bytes = 35MB/s = 280Mbps
- Health checks: 10K nodes × 100 bytes / 30s = 33KB/s

**Nodes to C2:**
- Results: 70K QPS × 10KB = 700MB/s = 5.6Gbps
- Health reports: 10K nodes × 1KB / 30s = 333KB/s

**Nodes to Web:**
- Page downloads: 70K QPS × 2MB = 140GB/s = 1.12Tbps (distributed)

## Core Entities

### Node
- `node_id` (UUID)
- `ip_address`
- `last_seen` (timestamp)
- `status` (active, inactive, failed)
- `capacity` (pages/second)
- `current_load` (active tasks)
- `total_crawled` (count)
- `registered_at`
- `metadata` (JSON: OS, location, etc.)

### Work Assignment
- `assignment_id` (UUID)
- `node_id`
- `url` (VARCHAR)
- `domain` (VARCHAR)
- `priority` (INT)
- `assigned_at` (timestamp)
- `deadline` (timestamp)
- `status` (pending, in_progress, completed, failed)
- `retry_count` (INT)

### Crawl Result
- `result_id` (UUID)
- `node_id`
- `url` (VARCHAR)
- `content_hash` (VARCHAR)
- `text_data_url` (VARCHAR)
- `links` (JSON array)
- `status_code` (INT)
- `crawl_time` (timestamp)
- `submitted_at` (timestamp)

### Domain
- `domain_id` (UUID)
- `domain_name` (VARCHAR)
- `rate_limit_per_node` (INT)
- `robots_txt` (TEXT)
- `last_crawled_by` (node_id)
- `last_crawled_at` (timestamp)

## API

### 1. Node Registration
```
POST /api/v1/nodes/register
Request:
{
  "node_id": "uuid",
  "ip_address": "192.168.1.1",
  "capacity": 10,
  "metadata": {
    "os": "Linux",
    "location": "US"
  }
}

Response:
{
  "node_id": "uuid",
  "status": "registered",
  "heartbeat_interval": 30,
  "c2_endpoint": "https://c2.example.com"
}
```

### 2. Request Work
```
POST /api/v1/nodes/{node_id}/work/request
Request:
{
  "max_tasks": 100,
  "preferred_domains": ["example.com"]
}

Response:
{
  "assignments": [
    {
      "assignment_id": "uuid",
      "url": "https://example.com/page1",
      "priority": 5,
      "deadline": "2025-11-13T10:05:00Z"
    }
  ]
}
```

### 3. Submit Results
```
POST /api/v1/nodes/{node_id}/results
Request:
{
  "results": [
    {
      "assignment_id": "uuid",
      "url": "https://example.com/page1",
      "status_code": 200,
      "content_hash": "abc123",
      "text_data_url": "s3://bucket/page1.txt",
      "links": ["url1", "url2"],
      "crawl_time": "2025-11-13T10:00:00Z"
    }
  ]
}

Response:
{
  "status": "accepted",
  "accepted_count": 1,
  "rejected_count": 0
}
```

### 4. Heartbeat
```
POST /api/v1/nodes/{node_id}/heartbeat
Request:
{
  "status": "active",
  "current_load": 5,
  "total_crawled": 1000
}

Response:
{
  "status": "ok",
  "next_heartbeat": 30
}
```

### 5. Get Node Status
```
GET /api/v1/nodes/{node_id}/status
Response:
{
  "node_id": "uuid",
  "status": "active",
  "current_load": 5,
  "total_crawled": 1000,
  "last_seen": "2025-11-13T10:00:00Z"
}
```

## Data Flow

### Node Registration Flow

1. **Node Starts**:
   - Node generates unique node_id
   - Connects to C2 server
   - Sends registration request with capabilities

2. **C2 Registration**:
   - **C2 Server** validates node
   - Creates node record in database
   - Assigns initial work capacity
   - Returns heartbeat interval and endpoints

3. **Heartbeat Setup**:
   - Node starts periodic heartbeat
   - Reports status and capacity
   - Receives work assignments

### Work Assignment Flow

1. **Node Requests Work**:
   - Node sends work request to C2
   - Specifies max tasks and preferences
   - **C2 Server** queries work queue

2. **Work Selection**:
   - **C2 Server**:
     - Checks node capacity and current load
     - Selects URLs from queue (respecting domain distribution)
     - Assigns work with deadlines
     - Updates work assignment status

3. **Work Distribution**:
   - Returns assignments to node
   - Node acknowledges receipt
   - Node begins crawling

### Crawling Flow

1. **Node Crawls**:
   - Node fetches URL
   - Respects rate limits per domain
   - Extracts text and links
   - Stores text data temporarily

2. **Result Submission**:
   - Node submits results to C2
   - Includes content hash, links, metadata
   - **C2 Server** validates results

3. **Result Processing**:
   - **C2 Server**:
     - Checks for duplicates (content hash)
     - Stores results
     - Extracts new URLs and adds to queue
     - Updates node statistics

### Fault Tolerance Flow

1. **Node Failure Detection**:
   - **C2 Server** detects missing heartbeat
   - Marks node as inactive
   - Reassigns pending work to other nodes

2. **Work Reassignment**:
   - **C2 Server** finds assignments for failed node
   - Marks assignments as failed
   - Re-queues URLs for other nodes
   - Updates work queue

## Database Design

### Schema Design

**Nodes Table:**
```sql
CREATE TABLE nodes (
    node_id UUID PRIMARY KEY,
    ip_address VARCHAR(45),
    last_seen TIMESTAMP NOT NULL,
    status ENUM('active', 'inactive', 'failed') DEFAULT 'active',
    capacity INT DEFAULT 10,
    current_load INT DEFAULT 0,
    total_crawled BIGINT DEFAULT 0,
    registered_at TIMESTAMP DEFAULT NOW(),
    metadata JSON,
    INDEX idx_status (status),
    INDEX idx_last_seen (last_seen),
    INDEX idx_capacity (capacity)
);
```

**Work Assignments Table:**
```sql
CREATE TABLE work_assignments (
    assignment_id UUID PRIMARY KEY,
    node_id UUID NOT NULL,
    url VARCHAR(2048) NOT NULL,
    domain VARCHAR(255) NOT NULL,
    priority INT DEFAULT 0,
    assigned_at TIMESTAMP DEFAULT NOW(),
    deadline TIMESTAMP NOT NULL,
    status ENUM('pending', 'in_progress', 'completed', 'failed') DEFAULT 'pending',
    retry_count INT DEFAULT 0,
    INDEX idx_node_status (node_id, status),
    INDEX idx_domain (domain),
    INDEX idx_deadline (deadline),
    INDEX idx_status_priority (status, priority DESC)
);
```

**Work Queue Table:**
```sql
CREATE TABLE work_queue (
    url_id UUID PRIMARY KEY,
    url VARCHAR(2048) UNIQUE NOT NULL,
    domain VARCHAR(255) NOT NULL,
    priority INT DEFAULT 0,
    discovered_at TIMESTAMP DEFAULT NOW(),
    assigned_count INT DEFAULT 0,
    status ENUM('pending', 'assigned', 'completed', 'failed') DEFAULT 'pending',
    INDEX idx_domain_status (domain, status),
    INDEX idx_priority (priority DESC),
    INDEX idx_status (status)
);
```

**Crawl Results Table:**
```sql
CREATE TABLE crawl_results (
    result_id UUID PRIMARY KEY,
    node_id UUID NOT NULL,
    assignment_id UUID,
    url VARCHAR(2048) NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    text_data_url VARCHAR(512),
    links JSON,
    status_code INT,
    crawl_time TIMESTAMP,
    submitted_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_node_id (node_id),
    INDEX idx_content_hash (content_hash),
    INDEX idx_submitted_at (submitted_at DESC)
);
```

**Domains Table:**
```sql
CREATE TABLE domains (
    domain_id UUID PRIMARY KEY,
    domain_name VARCHAR(255) UNIQUE NOT NULL,
    rate_limit_per_node INT DEFAULT 1,
    robots_txt TEXT,
    last_crawled_by UUID,
    last_crawled_at TIMESTAMP,
    INDEX idx_domain_name (domain_name)
);
```

### Database Sharding Strategy

**Work Queue Sharding:**
- Shard by domain using consistent hashing
- 100 shards: `shard_id = hash(domain) % 100`
- Enables efficient domain-based work distribution
- Prevents hot-spotting on popular domains

**Results Sharding:**
- Shard by content_hash for deduplication
- 1000 shards: `shard_id = hash(content_hash) % 1000`
- Enables efficient duplicate detection
- Parallel result processing

**Replication:**
- Each shard replicated 3x for high availability
- Master-replica setup for read scaling
- Writes go to master, reads can go to replicas

## High-Level Design

```
┌─────────────────────────────────────────────────────────────────┐
│                    Command & Control (C2) Server                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  Work Queue  │  │ Node Manager │  │ Result       │        │
│  │  Service     │  │ Service      │  │ Aggregator   │        │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘        │
│         │                  │                  │                 │
│  ┌──────▼──────────────────▼──────────────────▼──────────────┐│
│  │              Message Queue (Kafka)                          ││
│  │              - Work assignments                             ││
│  │              - Results                                      ││
│  │              - Node events                                  ││
│  └──────┬──────────────────────────────────────────────────────┘│
│         │                                                         │
│  ┌──────▼──────────────────────────────────────────────────────┐│
│  │         Database Cluster (Sharded)                           ││
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐                  ││
│  │  │ Work     │  │ Results  │  │ Nodes    │                  ││
│  │  │ Queue DB │  │ DB       │  │ DB       │                  ││
│  │  └──────────┘  └──────────┘  └──────────┘                  ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
         │
         │ HTTPS / Encrypted Channel
         │
         ├──────────────────┬──────────────────┬──────────────────┐
         │                  │                  │                  │
┌────────▼──────┐  ┌────────▼──────┐  ┌────────▼──────┐  ┌────────▼──────┐
│   Node 1      │  │   Node 2      │  │   Node 3      │  │   Node N      │
│  (IP: A.B.C.1)│  │  (IP: A.B.C.2)│  │  (IP: A.B.C.3)│  │  (IP: X.Y.Z.N)│
│               │  │               │  │               │  │               │
│  - Crawler    │  │  - Crawler    │  │  - Crawler    │  │  - Crawler    │
│  - Parser     │  │  - Parser     │  │  - Parser     │  │  - Parser     │
│  - Local      │  │  - Local      │  │  - Local      │  │  - Local      │
│    Storage    │  │    Storage    │  │    Storage    │  │    Storage    │
└────────┬──────┘  └────────┬──────┘  └────────┬──────┘  └────────┬──────┘
         │                  │                  │                  │
         └──────────────────┴──────────────────┴──────────────────┘
                              │
                              │ HTTP/HTTPS
                              │
                    ┌─────────▼──────────┐
                    │   Web Servers      │
                    │  (Target Sites)    │
                    └────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              Result Storage (S3)                                 │
│              - Extracted text data                                │
│              - Aggregated results                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Deep Dive

### Component Design

#### 1. Command & Control (C2) Server

**Responsibilities:**
- Coordinate all nodes
- Assign work to nodes
- Aggregate results
- Monitor node health
- Manage work queue

**Key Design Decisions:**
- **Stateless Design**: C2 server is stateless for horizontal scaling
- **Load Balancing**: Distribute work based on node capacity
- **Fault Tolerance**: Handle node failures gracefully
- **Rate Limiting**: Enforce per-domain rate limits

**Scalability:**
- Horizontal scaling with load balancer
- Stateless design enables multiple C2 instances
- Database connection pooling
- Caching for frequently accessed data

#### 2. Work Queue Service

**Responsibilities:**
- Manage queue of URLs to crawl
- Assign work to nodes
- Track work status
- Handle work reassignment

**Key Design Decisions:**
- **Priority Queue**: Prioritize important URLs
- **Domain Distribution**: Distribute domains across nodes
- **Deadline Management**: Reassign expired work
- **Deduplication**: Prevent duplicate assignments

**Implementation:**
```python
def assign_work(node_id, max_tasks):
    node = get_node(node_id)
    
    # Check node capacity
    available_capacity = node.capacity - node.current_load
    tasks_to_assign = min(max_tasks, available_capacity)
    
    # Select work from queue
    assignments = []
    domains_assigned = set()
    
    # Try to distribute across domains
    for priority_level in [5, 4, 3, 2, 1, 0]:
        urls = get_pending_urls(
            limit=tasks_to_assign - len(assignments),
            priority=priority_level,
            exclude_domains=domains_assigned
        )
        
        for url in urls:
            # Check domain rate limit
            domain = extract_domain(url)
            if can_assign_domain(domain, node_id):
                assignment = create_assignment(node_id, url, priority_level)
                assignments.append(assignment)
                domains_assigned.add(domain)
                
                if len(assignments) >= tasks_to_assign:
                    break
        
        if len(assignments) >= tasks_to_assign:
            break
    
    return assignments
```

#### 3. Node Manager Service

**Responsibilities:**
- Register and manage nodes
- Track node health
- Handle node failures
- Reassign work from failed nodes

**Key Design Decisions:**
- **Heartbeat Mechanism**: Periodic health checks
- **Failure Detection**: Detect nodes that stop responding
- **Work Reassignment**: Reassign work from failed nodes
- **Capacity Management**: Track node capacity and load

**Implementation:**
```python
def process_heartbeat(node_id, status, current_load, total_crawled):
    node = get_node(node_id)
    
    # Update node status
    node.last_seen = now()
    node.status = 'active'
    node.current_load = current_load
    node.total_crawled = total_crawled
    node.save()
    
    # Check for expired assignments
    expired_assignments = get_expired_assignments(node_id)
    for assignment in expired_assignments:
        # Reassign to other nodes
        reassign_work(assignment)
        assignment.status = 'failed'
        assignment.save()
    
    return {'status': 'ok', 'next_heartbeat': 30}
```

#### 4. Result Aggregator Service

**Responsibilities:**
- Receive results from nodes
- Validate results
- Deduplicate content
- Store results
- Extract new URLs

**Key Design Decisions:**
- **Deduplication**: Use content hash for duplicate detection
- **Validation**: Validate results before storing
- **Async Processing**: Process results asynchronously
- **URL Extraction**: Extract and queue new URLs

**Implementation:**
```python
def submit_results(node_id, results):
    accepted = []
    rejected = []
    
    for result in results:
        # Check for duplicates
        if is_duplicate(result['content_hash']):
            rejected.append(result['assignment_id'])
            continue
        
        # Validate result
        if not validate_result(result):
            rejected.append(result['assignment_id'])
            continue
        
        # Store result
        store_result(result)
        accepted.append(result['assignment_id'])
        
        # Extract new URLs
        new_urls = extract_urls(result['links'])
        add_urls_to_queue(new_urls)
        
        # Update assignment status
        update_assignment_status(result['assignment_id'], 'completed')
    
    return {
        'status': 'accepted',
        'accepted_count': len(accepted),
        'rejected_count': len(rejected)
    }
```

### Detailed Design

#### Load Balancing Strategy

**Challenge:** Distribute work evenly across 10,000 nodes

**Solution:**
- **Capacity-Based**: Assign work based on node capacity
- **Domain Distribution**: Distribute domains across nodes to avoid IP-based blocking
- **Load Balancing**: Track current load per node
- **Priority Queue**: Prioritize important URLs

**Implementation:**
```python
def select_node_for_work(url, priority):
    domain = extract_domain(url)
    
    # Get nodes that haven't crawled this domain recently
    available_nodes = get_available_nodes(
        exclude_domains=[domain],
        min_capacity=1
    )
    
    if not available_nodes:
        # Fallback: use any available node
        available_nodes = get_available_nodes(min_capacity=1)
    
    # Select node with lowest load
    node = min(available_nodes, key=lambda n: n.current_load / n.capacity)
    
    return node
```

#### Stealth Mechanisms

**Challenge:** Avoid detection and blocking by target websites

**Solution:**
- **IP Rotation**: Distribute requests across many IPs (10K nodes)
- **Rate Limiting**: Respect per-domain rate limits
- **User-Agent Rotation**: Rotate user agents
- **Request Spacing**: Add delays between requests
- **Domain Distribution**: Avoid concentrating requests from single IP

**Implementation:**
```python
def crawl_with_stealth(node_id, url):
    domain = extract_domain(url)
    
    # Check rate limit for domain
    if not can_crawl_domain(domain, node_id):
        wait_for_rate_limit(domain, node_id)
    
    # Rotate user agent
    user_agent = get_random_user_agent()
    
    # Add random delay
    delay = random.uniform(0.5, 2.0)
    time.sleep(delay)
    
    # Fetch page
    response = fetch_url(url, user_agent=user_agent)
    
    return response
```

#### Fault Tolerance

**Challenge:** Handle node failures without losing work

**Solution:**
- **Work Tracking**: Track all work assignments
- **Deadline Management**: Set deadlines for work assignments
- **Heartbeat Monitoring**: Detect failed nodes via heartbeat
- **Work Reassignment**: Reassign work from failed nodes

**Implementation:**
```python
def handle_node_failure(node_id):
    # Mark node as failed
    node = get_node(node_id)
    node.status = 'failed'
    node.save()
    
    # Find pending assignments for this node
    pending_assignments = get_assignments(node_id, status='in_progress')
    
    # Reassign to other nodes
    for assignment in pending_assignments:
        # Check if deadline passed
        if assignment.deadline < now():
            # Requeue URL
            requeue_url(assignment.url)
        else:
            # Reassign to another node
            new_node = select_node_for_work(assignment.url, assignment.priority)
            assignment.node_id = new_node.node_id
            assignment.assigned_at = now()
            assignment.deadline = now() + timedelta(minutes=5)
            assignment.save()
```

#### Deduplication Across Nodes

**Challenge:** Avoid duplicate work when multiple nodes crawl same URL

**Solution:**
- **Content Hash**: Use content hash for deduplication
- **URL Tracking**: Track crawled URLs in database
- **Assignment Locking**: Lock URL when assigned
- **Distributed Lock**: Use distributed lock for URL assignment

**Implementation:**
```python
def assign_url_with_lock(url):
    # Acquire distributed lock
    lock_key = f"url_lock:{hash_url(url)}"
    lock = acquire_lock(lock_key, timeout=5)
    
    try:
        # Check if already crawled
        if is_crawled(url):
            return None
        
        # Check if already assigned
        if is_assigned(url):
            return None
        
        # Mark as assigned
        mark_as_assigned(url)
        
        return url
    finally:
        release_lock(lock)
```

### Scalability Considerations

#### Horizontal Scaling

**C2 Server:**
- Stateless design enables horizontal scaling
- Load balancer distributes requests
- Multiple C2 instances share database
- Auto-scaling based on load

**Database:**
- Shard work queue by domain
- Shard results by content hash
- Read replicas for read scaling
- Connection pooling

**Message Queue:**
- Kafka partitions for work distribution
- Multiple consumer groups
- Parallel processing

#### Caching Strategy

**Redis Cache:**
- **Node Status**: TTL 30 seconds
- **Domain Rate Limits**: TTL 1 hour
- **URL Assignment Locks**: TTL 5 minutes
- **Content Hash Lookup**: TTL 1 hour

**Cache Invalidation:**
- Invalidate on node status changes
- Invalidate on work assignment
- Use cache-aside pattern

#### Load Balancing

**Work Distribution:**
- Capacity-based assignment
- Domain-based distribution
- Priority-based queue
- Load-aware node selection

**Result Aggregation:**
- Batch result processing
- Async result storage
- Parallel URL extraction
- Distributed deduplication

### Security Considerations

#### Communication Security

- **Encryption**: Use TLS for all C2 communication
- **Authentication**: Authenticate nodes with tokens
- **Authorization**: Verify node permissions
- **Message Integrity**: Sign messages to prevent tampering

#### Node Security

- **Isolation**: Isolate nodes from each other
- **Sandboxing**: Run crawler in sandbox
- **Resource Limits**: Limit node resources
- **Monitoring**: Monitor node behavior

#### Data Security

- **Encryption**: Encrypt stored results
- **Access Control**: Control access to results
- **Audit Logging**: Log all operations
- **Data Retention**: Implement retention policies

### Monitoring & Observability

#### Key Metrics

**System Metrics:**
- Active nodes count
- Work assignment rate
- Result submission rate
- Node failure rate
- Average node load
- Queue depth

**Business Metrics:**
- Pages crawled per second
- Total pages crawled
- Success rate
- Duplicate rate
- Average crawl time

#### Logging

- **Structured Logging**: JSON logs for parsing
- **Request Tracing**: Trace requests across services
- **Node Events**: Log node registration, failures
- **Work Events**: Log work assignments, completions

#### Alerting

- **Low Node Count**: Alert if active nodes < 5,000
- **High Failure Rate**: Alert if failure rate > 10%
- **Queue Backup**: Alert if queue depth > 1M
- **C2 Server Issues**: Alert on C2 errors

### Trade-offs and Optimizations

#### Trade-offs

**1. Centralized vs Decentralized C2**
- **Centralized**: Simpler, single point of failure
- **Decentralized**: More resilient, but complex
- **Decision**: Centralized with redundancy

**2. Work Assignment: Push vs Pull**
- **Push**: C2 assigns work proactively
- **Pull**: Nodes request work when ready
- **Decision**: Pull model (nodes request work)

**3. Result Storage: Immediate vs Batch**
- **Immediate**: Lower latency, higher overhead
- **Batch**: Higher throughput, higher latency
- **Decision**: Batch results for efficiency

**4. Deduplication: Centralized vs Distributed**
- **Centralized**: Single source of truth, bottleneck
- **Distributed**: Faster, but consistency challenges
- **Decision**: Centralized with caching

#### Optimizations

**1. Batch Operations**
- Batch work assignments
- Batch result submissions
- Reduce network overhead
- Improve throughput

**2. Connection Pooling**
- Reuse database connections
- Reuse HTTP connections
- Reduce connection overhead

**3. Compression**
- Compress results before transmission
- Reduce bandwidth usage
- Improve performance

**4. Caching**
- Cache node status
- Cache domain rate limits
- Cache content hashes
- Reduce database load

## What Interviewers Look For

### Distributed Systems Skills

1. **Command & Control Architecture**
   - Centralized C2 server
   - Efficient coordination
   - Work distribution
   - **Red Flags**: No C2, inefficient coordination, poor distribution

2. **Fault Tolerance**
   - Node failure handling
   - Work reassignment
   - Heartbeat monitoring
   - **Red Flags**: No fault tolerance, work loss, no monitoring

3. **Work Distribution**
   - Load balancing
   - Domain distribution
   - Pull model
   - **Red Flags**: Push model, poor balancing, bottlenecks

### Web Crawling Skills

1. **Deduplication**
   - Content hash deduplication
   - Prevent duplicate work
   - **Red Flags**: No deduplication, duplicate work, wasted resources

2. **Stealth Mechanisms**
   - Avoid detection
   - User-agent rotation
   - Rate limiting
   - **Red Flags**: No stealth, easy detection, blocking

3. **Politeness**
   - Respect robots.txt
   - Rate limiting
   - **Red Flags**: No politeness, violations, blocking

### Problem-Solving Approach

1. **Scale Thinking**
   - 10,000 nodes
   - Billions of pages
   - Efficient coordination
   - **Red Flags**: Small-scale design, no scale consideration

2. **Edge Cases**
   - Node failures
   - Network issues
   - C2 failures
   - **Red Flags**: Ignoring edge cases, no handling

3. **Trade-off Analysis**
   - Pull vs push model
   - Centralized vs decentralized
   - **Red Flags**: No trade-offs, dogmatic choices

### System Design Skills

1. **Component Design**
   - C2 server
   - Crawler nodes
   - Result aggregator
   - **Red Flags**: Monolithic, unclear boundaries

2. **Result Aggregation**
   - Efficient collection
   - Batch processing
   - **Red Flags**: Inefficient, no batching, high overhead

3. **Monitoring**
   - Node health
   - Work progress
   - **Red Flags**: No monitoring, no visibility

### Communication Skills

1. **Distributed Architecture Explanation**
   - Can explain C2 design
   - Understands work distribution
   - **Red Flags**: No understanding, vague

2. **Fault Tolerance Explanation**
   - Can explain failure handling
   - Understands recovery
   - **Red Flags**: No understanding, vague

### Meta-Specific Focus

1. **Distributed Systems Expertise**
   - C2 architecture knowledge
   - Fault tolerance
   - **Key**: Show distributed systems expertise

2. **Scale Thinking**
   - 10,000 nodes
   - Billions of pages
   - **Key**: Demonstrate scale expertise

## Summary

Designing a distributed web crawler using 10,000 nodes requires careful consideration of:

1. **Command & Control**: Centralized C2 server for coordination
2. **Work Distribution**: Efficient load balancing across nodes
3. **Fault Tolerance**: Handle node failures gracefully
4. **Stealth Mechanisms**: Avoid detection and blocking
5. **Deduplication**: Prevent duplicate work across nodes
6. **Result Aggregation**: Collect results from distributed nodes
7. **Scalability**: Handle 10,000+ nodes efficiently
8. **Resilience**: Survive node and C2 failures

Key architectural decisions:
- **Pull Model**: Nodes request work when ready
- **Domain Distribution**: Distribute domains across nodes
- **Content Hash Deduplication**: Use hash for duplicate detection
- **Heartbeat Monitoring**: Detect node failures
- **Work Reassignment**: Reassign work from failed nodes
- **Batch Processing**: Batch results for efficiency
- **Horizontal Scaling**: Scale C2 server horizontally

The system handles 10,000 distributed nodes, crawls 10 billion pages in 5 days, and maintains high availability despite 30% node failure rate.

