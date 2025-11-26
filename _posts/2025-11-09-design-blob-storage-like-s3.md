---
layout: post
title: "Design a Blob Storage System Like S3: Distributed Object Storage"
date: 2025-11-09
categories: [System Design, Distributed Systems, Storage, Object Storage, S3, Architecture]
excerpt: "A comprehensive system design for building a blob storage system like Amazon S3, covering architecture, data durability, replication, scalability, API design, and key design decisions for petabyte-scale object storage."
---

## Introduction

Object storage (blob storage) is a fundamental building block of modern cloud infrastructure. Systems like Amazon S3, Azure Blob Storage, and Google Cloud Storage handle exabytes of data, billions of objects, and millions of requests per second while maintaining 99.999999999% (11 9's) durability.

This post designs a scalable blob storage system that can handle massive scale, ensure data durability, and provide high availability while maintaining low latency and cost efficiency.

## Table of Contents

1. [Requirements](#requirements)
   - [Functional Requirements](#functional-requirements)
   - [Non-Functional Requirements](#non-functional-requirements)
2. [Capacity Estimation](#capacity-estimation)
   - [Storage Scale](#storage-scale)
   - [Request Scale](#request-scale)
   - [User Scale](#user-scale)
3. [Core Entities](#core-entities)
4. [API](#api)
5. [Data Flow](#data-flow)
6. [Database Design](#database-design)
   - [Schema Design](#schema-design)
   - [Database Sharding Strategy](#database-sharding-strategy)
7. [High-Level Design](#high-level-design)
8. [Deep Dive](#deep-dive)
   - [Component Design](#component-design)
   - [Scalability Design](#scalability-design)
   - [Performance Optimization](#performance-optimization)
   - [Data Integrity](#data-integrity)
   - [Cost Optimization](#cost-optimization)
   - [Security](#security)
   - [Monitoring & Observability](#monitoring--observability)
   - [Disaster Recovery](#disaster-recovery)
   - [Technology Stack](#technology-stack)
   - [Comparison with Real Systems](#comparison-with-real-systems)

---

## Requirements

### Functional Requirements

1. **Object Operations**
   - PUT: Upload objects (files) with metadata
   - GET: Download objects
   - DELETE: Delete objects
   - LIST: List objects in a bucket/prefix
   - HEAD: Get object metadata without downloading

2. **Bucket Management**
   - Create/delete buckets (containers)
   - List buckets
   - Set bucket policies and ACLs

3. **Metadata Management**
   - Store object metadata (size, content-type, etag, timestamps)
   - Custom metadata (key-value pairs)
   - Versioning support

4. **Access Control**
   - Authentication (API keys, IAM)
   - Authorization (ACLs, bucket policies)
   - Signed URLs for temporary access

### Non-Functional Requirements

- **Durability**: 99.999999999% (11 9's) - lose 1 object per 10,000 years
- **Availability**: 99.99% uptime (4 9's)
- **Scalability**: Handle exabytes of data, billions of objects
- **Throughput**: Millions of requests per second
- **Latency**: < 100ms for metadata operations, < 1s for object retrieval
- **Cost Efficiency**: Optimize storage and bandwidth costs
- **Consistency**: Eventually consistent (or strong consistency option)

## Capacity Estimation

### Storage Scale

- **Total Storage**: 100+ exabytes
- **Objects**: 100+ billion objects
- **Average Object Size**: 1MB (ranges from bytes to 5TB)
- **Daily Uploads**: 1 billion objects = 1PB/day
- **Daily Downloads**: 10 billion objects = 10PB/day

### Request Scale

- **Read Requests**: 100M requests/second (peak)
- **Write Requests**: 10M requests/second (peak)
- **Metadata Operations**: 200M operations/second (peak)

### User Scale

- **Active Users**: 10 million
- **Concurrent Users**: 1 million
- **Buckets**: 100 million buckets

## Core Entities

### Bucket
- **Attributes**: bucket_id, bucket_name, owner_id, region, created_at, policy, acl
- **Relationships**: Contains objects, belongs to user

### Object
- **Attributes**: object_id, bucket_id, key, size, content_type, etag, version_id, created_at, updated_at
- **Relationships**: Belongs to bucket, has metadata, has versions

### Object Metadata
- **Attributes**: metadata_id, object_id, key, value, created_at
- **Relationships**: Belongs to object

### Object Version
- **Attributes**: version_id, object_id, version_number, is_latest, created_at
- **Relationships**: Belongs to object

## API

### PUT Object (Upload)
```
PUT /{bucket}/{key}
Headers:
  - Content-Type: application/json
  - Content-Length: 1024
  - x-amz-meta-custom-key: custom-value
Body: [object data]

Response: 200 OK
Headers:
  - ETag: "d41d8cd98f00b204e9800998ecf8427e"
  - x-amz-version-id: version-id
```

### GET Object (Download)
```
GET /{bucket}/{key}
Headers:
  - Range: bytes=0-1023 (optional)

Response: 200 OK
Headers:
  - Content-Type: application/json
  - Content-Length: 1024
  - ETag: "d41d8cd98f00b204e9800998ecf8427e"
  - Last-Modified: Wed, 01 Jan 2025 12:00:00 GMT
Body: [object data]
```

### DELETE Object
```
DELETE /{bucket}/{key}

Response: 204 No Content
```

### LIST Objects
```
GET /{bucket}?prefix=photos/&max-keys=1000&marker=photos/photo-100.jpg

Response: 200 OK
{
  "Contents": [
    {
      "Key": "photos/photo-1.jpg",
      "Size": 1024,
      "LastModified": "2025-01-01T12:00:00Z",
      "ETag": "etag-1"
    }
  ],
  "IsTruncated": false,
  "NextMarker": null
}
```

### HEAD Object (Get Metadata)
```
HEAD /{bucket}/{key}

Response: 200 OK
Headers:
  - Content-Type: application/json
  - Content-Length: 1024
  - ETag: "d41d8cd98f00b204e9800998ecf8427e"
  - Last-Modified: Wed, 01 Jan 2025 12:00:00 GMT
  - x-amz-meta-custom-key: custom-value
```

## Data Flow

### PUT Object (Upload) Flow
1. Client uploads object → API Gateway
2. API Gateway → Metadata Service (validate bucket, permissions)
3. Metadata Service → Storage Service (get storage node locations)
4. Storage Service → Storage Nodes (write object data)
5. Storage Nodes → Replication Service (replicate to other nodes)
6. Storage Service → Metadata Service (confirm write success)
7. Metadata Service → Metadata Database (store object metadata)
8. Metadata Service → API Gateway (return success with ETag)
9. API Gateway → Client (return response)

### GET Object (Download) Flow
1. Client requests object → API Gateway
2. API Gateway → Metadata Service (get object metadata)
3. Metadata Service → Metadata Database (query metadata)
4. Metadata Service → Storage Service (get object location)
5. Storage Service → Storage Nodes (read object data)
6. Storage Nodes → Storage Service (return object data)
7. Storage Service → API Gateway (stream object data)
8. API Gateway → Client (return object)

### LIST Objects Flow
1. Client requests list → API Gateway
2. API Gateway → Metadata Service
3. Metadata Service → Metadata Database (query objects by prefix)
4. Metadata Database → Metadata Service (return object list)
5. Metadata Service → API Gateway (return paginated results)
6. API Gateway → Client (return object list)

## Database Design

### Schema Design

**Buckets Table:**
```sql
CREATE TABLE buckets (
    bucket_id VARCHAR(36) PRIMARY KEY,
    bucket_name VARCHAR(255) UNIQUE NOT NULL,
    owner_id VARCHAR(36) NOT NULL,
    region VARCHAR(50) NOT NULL,
    created_at TIMESTAMP,
    policy JSON,
    acl JSON,
    INDEX idx_owner_id (owner_id),
    INDEX idx_bucket_name (bucket_name)
);
```

**Objects Table:**
```sql
CREATE TABLE objects (
    object_id VARCHAR(36) PRIMARY KEY,
    bucket_id VARCHAR(36) NOT NULL,
    key VARCHAR(1024) NOT NULL,
    size BIGINT NOT NULL,
    content_type VARCHAR(255),
    etag VARCHAR(64) NOT NULL,
    version_id VARCHAR(36),
    is_latest BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE KEY unique_bucket_key_version (bucket_id, key, version_id),
    INDEX idx_bucket_key (bucket_id, key),
    INDEX idx_bucket_prefix (bucket_id, key(255)),
    FOREIGN KEY (bucket_id) REFERENCES buckets(bucket_id)
);
```

**Object Metadata Table:**
```sql
CREATE TABLE object_metadata (
    metadata_id VARCHAR(36) PRIMARY KEY,
    object_id VARCHAR(36) NOT NULL,
    meta_key VARCHAR(255) NOT NULL,
    meta_value TEXT,
    created_at TIMESTAMP,
    INDEX idx_object_id (object_id),
    FOREIGN KEY (object_id) REFERENCES objects(object_id)
);
```

### Database Sharding Strategy

**Shard by Bucket ID:**
- Buckets and their objects on same shard
- Enables efficient bucket operations
- Use consistent hashing for distribution

**Partition Objects Table:**
- Partition by bucket_id for large buckets
- Enables parallel queries within bucket

## High-Level Design

```
┌─────────────────────────────────────────┐
│         Client Applications             │
│    (REST API, SDK, CLI Tools)          │
└──────────────┬──────────────────────────┘
               │
               │ HTTPS
               │
┌──────────────▼──────────────────────────┐
│         Load Balancer / API Gateway     │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴───────┐
       │               │
┌──────▼──────┐  ┌─────▼──────┐
│  Metadata   │  │  Storage   │
│   Service   │  │   Service  │
│  (Metadata  │  │  (Object   │
│   DB)       │  │   Storage)  │
└─────────────┘  └────────────┘
       │               │
       │               │
┌──────▼──────┐  ┌─────▼──────┐
│  Metadata   │  │  Storage    │
│  Database   │  │   Nodes     │
│ (Cassandra) │  │ (Distributed│
│             │  │   Disks)    │
└─────────────┘  └────────────┘
```

### Core Components

1. **API Gateway / Load Balancer**: Routes requests, handles authentication
2. **Metadata Service**: Manages object metadata, bucket information
3. **Storage Service**: Handles actual object storage and retrieval
4. **Metadata Database**: Stores metadata (Cassandra, DynamoDB)
5. **Storage Nodes**: Physical storage servers with disks
6. **Replication Service**: Ensures data durability through replication
7. **Monitoring & Analytics**: System health and usage metrics

## Deep Dive

### Component Design

#### 1. API Gateway / Load Balancer

**Responsibilities:**
- Request routing to appropriate services
- Authentication and authorization
- Rate limiting and throttling
- Request/response transformation
- SSL/TLS termination

**Features:**
- RESTful API (S3-compatible)
- Request signing (HMAC-SHA256)
- CORS support
- Request logging

**Technology:**
- AWS API Gateway / Azure API Management
- Envoy Proxy / NGINX
- Custom API service

**API Endpoints:**
```
PUT /{bucket}/{key}          # Upload object
GET /{bucket}/{key}          # Download object
DELETE /{bucket}/{key}       # Delete object
HEAD /{bucket}/{key}         # Get metadata
GET /{bucket}?prefix={prefix} # List objects
```

---

#### 2. Metadata Service

**Responsibilities:**
- Object metadata management
- Bucket management
- Access control (ACLs, policies)
- Versioning
- Lifecycle management

**Metadata Stored:**
- Object key (path)
- Bucket name
- Size (bytes)
- Content-Type
- ETag (MD5 hash)
- Creation timestamp
- Last modified timestamp
- Storage location (node IDs)
- Replication status
- Custom metadata (key-value pairs)
- Access control lists (ACLs)

**API Operations:**
- Create/update/delete object metadata
- List objects by prefix
- Get bucket information
- Manage ACLs and policies

**Technology:**
- Microservice architecture
- Stateless design
- Horizontal scaling
- Caching layer (Redis)

---

#### 3. Metadata Database

**Database Choice: Cassandra / DynamoDB**

**Why:**
- High write throughput
- Horizontal scaling
- Low latency reads
- No single point of failure
- Tunable consistency

**Schema Design (Cassandra):**

**Objects Table:**
```sql
CREATE TABLE objects (
    bucket_name TEXT,
    object_key TEXT,
    version_id UUID,
    size_bytes BIGINT,
    content_type TEXT,
    etag TEXT,
    created_at TIMESTAMP,
    modified_at TIMESTAMP,
    storage_nodes LIST<TEXT>,  -- Node IDs storing replicas
    replication_status TEXT,
    custom_metadata MAP<TEXT, TEXT>,
    acl_permissions MAP<TEXT, TEXT>,
    PRIMARY KEY ((bucket_name, object_key), version_id)
) WITH CLUSTERING ORDER BY (version_id DESC);
```

**Buckets Table:**
```sql
CREATE TABLE buckets (
    bucket_name TEXT PRIMARY KEY,
    owner_id TEXT,
    created_at TIMESTAMP,
    region TEXT,
    versioning_enabled BOOLEAN,
    lifecycle_policy TEXT,
    acl_permissions MAP<TEXT, TEXT>,
    custom_metadata MAP<TEXT, TEXT>
);
```

**Indexes:**
- Secondary index on `prefix` for listing
- Materialized view for common queries
- Partition by bucket_name for locality

**Consistency:**
- Write: QUORUM (2 of 3 replicas)
- Read: QUORUM for strong consistency
- Read: ONE for eventual consistency (faster)

#### Why Cassandra? Can We Use SQL Instead?

This is a critical design decision. Let's analyze both options:

**Why Cassandra is Preferred for Blob Storage Metadata:**

1. **Write-Intensive Workload**
   - **Scale**: 10M writes/second (peak)
   - **Cassandra**: Optimized for high write throughput
     - Append-only writes (no updates in place)
     - No locking overhead
     - Sequential disk writes
   - **SQL**: Struggles with high write throughput
     - Row-level locking creates contention
     - Index maintenance overhead
     - Transaction log writes add latency

2. **Horizontal Scaling**
   - **Cassandra**: Built-in horizontal scaling
     - Add nodes, automatic data distribution
     - No manual sharding required
     - Linear scalability
   - **SQL**: Vertical scaling + complex sharding
     - Sharding requires application logic
     - Cross-shard queries are complex
     - Rebalancing is difficult

3. **No Complex Joins**
   - **Blob Storage Queries**: Simple lookups
     - Get object by bucket+key
     - List objects by prefix
     - No joins needed
   - **Cassandra**: Perfect for simple queries
     - Fast key-based lookups
     - Efficient prefix queries
   - **SQL**: Joins are powerful but unnecessary overhead
     - Join overhead not needed
     - Simpler queries = better performance

4. **Flexible Schema**
   - **Metadata**: Varies by object type
     - Custom metadata (key-value pairs)
     - Different fields for different objects
   - **Cassandra**: Schema flexibility
     - MAP, LIST, SET types
     - Easy to add new fields
   - **SQL**: Rigid schema
     - Schema changes expensive
     - EAV pattern needed for flexible metadata

5. **Multi-Region Support**
   - **Cassandra**: Multi-region replication
     - Built-in multi-datacenter support
     - Tunable consistency per region
   - **SQL**: Complex multi-region setup
     - Requires replication solutions
     - Cross-region transactions are slow

**When SQL Databases Can Work:**

SQL databases (PostgreSQL, MySQL) can be used for blob storage metadata in certain scenarios:

**✅ Suitable When:**
- **Smaller Scale**: < 1M writes/second
- **Strong Consistency Required**: Need ACID transactions
- **Complex Queries**: Need joins, aggregations, analytics
- **Team Familiarity**: Team more comfortable with SQL
- **Existing Infrastructure**: Already using SQL databases

**SQL Schema Design (PostgreSQL):**

```sql
-- Objects table
CREATE TABLE objects (
    bucket_name VARCHAR(255) NOT NULL,
    object_key VARCHAR(1024) NOT NULL,
    version_id UUID NOT NULL,
    size_bytes BIGINT NOT NULL,
    content_type VARCHAR(255),
    etag VARCHAR(64),
    created_at TIMESTAMP NOT NULL,
    modified_at TIMESTAMP NOT NULL,
    storage_nodes TEXT[],  -- Array of node IDs
    replication_status VARCHAR(50),
    custom_metadata JSONB,  -- Flexible metadata
    acl_permissions JSONB,
    PRIMARY KEY (bucket_name, object_key, version_id)
);

-- Indexes for common queries
CREATE INDEX idx_objects_bucket_key ON objects(bucket_name, object_key);
CREATE INDEX idx_objects_prefix ON objects(bucket_name, object_key text_pattern_ops);
CREATE INDEX idx_objects_created ON objects(created_at);

-- Buckets table
CREATE TABLE buckets (
    bucket_name VARCHAR(255) PRIMARY KEY,
    owner_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    region VARCHAR(50),
    versioning_enabled BOOLEAN DEFAULT FALSE,
    lifecycle_policy JSONB,
    acl_permissions JSONB,
    custom_metadata JSONB
);
```

**SQL Optimization Strategies:**

1. **Partitioning**
   ```sql
   -- Partition by bucket_name for better performance
   CREATE TABLE objects (
       ...
   ) PARTITION BY HASH (bucket_name);
   
   CREATE TABLE objects_bucket_0 PARTITION OF objects
       FOR VALUES WITH (MODULUS 4, REMAINDER 0);
   ```

2. **Read Replicas**
   - Use read replicas for LIST operations
   - Primary handles writes
   - Replicas handle reads

3. **Connection Pooling**
   - Use connection pools (PgBouncer)
   - Reduce connection overhead

4. **Caching**
   - Cache frequently accessed metadata in Redis
   - Reduce database load

**Trade-offs: SQL vs Cassandra**

| Aspect | Cassandra | SQL (PostgreSQL) |
|--------|-----------|------------------|
| **Write Throughput** | Very High (10M+/sec) | High (1M/sec) |
| **Read Latency** | Low (< 10ms) | Low (< 10ms) |
| **Horizontal Scaling** | Easy (add nodes) | Complex (sharding) |
| **Consistency** | Tunable (eventual/strong) | Strong (ACID) |
| **Complex Queries** | Limited | Excellent (joins, SQL) |
| **Schema Flexibility** | High | Low (rigid) |
| **Multi-Region** | Built-in | Complex setup |
| **Operational Complexity** | Medium | Low (familiar) |
| **Cost** | Lower (commodity hardware) | Higher (vertical scaling) |

**Hybrid Approach:**

Some systems use both:

1. **Cassandra for Metadata**
   - High write throughput
   - Simple lookups
   - Horizontal scaling

2. **SQL for Analytics/Reporting**
   - Complex queries
   - Aggregations
   - Business intelligence

3. **Sync Between Systems**
   - ETL pipeline syncs data
   - Cassandra → SQL for analytics
   - Use appropriate tool for each use case

**Recommendation:**

- **For Large-Scale Blob Storage (S3-like)**: Use **Cassandra**
  - High write throughput requirement
  - Simple query patterns
  - Need horizontal scaling
  - Multi-region support

- **For Smaller Scale or Strong Consistency**: Use **SQL (PostgreSQL)**
  - < 1M writes/second
  - Need ACID transactions
  - Complex queries needed
  - Team familiarity with SQL

- **For Best of Both Worlds**: Use **Hybrid**
  - Cassandra for metadata operations
  - SQL for analytics/reporting
  - Sync between systems

**Real-World Examples:**

- **Amazon S3**: Uses DynamoDB (NoSQL) for metadata
- **Azure Blob Storage**: Uses SQL Server for metadata (but with heavy optimization)
- **Google Cloud Storage**: Uses Bigtable (NoSQL) for metadata

Most large-scale blob storage systems use NoSQL databases for metadata due to write throughput and scalability requirements.

---

#### 4. Storage Service

**Responsibilities:**
- Object storage and retrieval
- Replication coordination
- Data integrity verification
- Storage node management

**Architecture:**
- Stateless service layer
- Routes requests to storage nodes
- Handles replication logic
- Manages erasure coding

**Operations:**
- PUT: Store object, trigger replication
- GET: Retrieve object from storage nodes
- DELETE: Mark for deletion, garbage collection
- Replication: Copy objects to multiple nodes

---

#### 5. Storage Nodes

**Physical Architecture:**
- Servers with multiple disks (HDD/SSD)
- Network attached storage
- Distributed across data centers

**Node Responsibilities:**
- Store object chunks/blocks
- Serve read requests
- Report health status
- Participate in replication

**Storage Organization:**
```
/storage/
  ├── node-001/
  │   ├── bucket1/
  │   │   ├── object1/chunk1
  │   │   ├── object1/chunk2
  │   │   └── object2/chunk1
  │   └── bucket2/
  └── node-002/
      └── ...
```

**Object Storage Format:**
- Objects split into chunks (e.g., 64MB chunks)
- Chunks stored on different nodes
- Erasure coding for durability
- Checksums for integrity

---

#### 6. Data Durability & Replication

#### Replication Strategies

**1. Multi-Copy Replication**
- Store N copies of each object (typically 3)
- Copies stored on different nodes/data centers
- Simple to implement and understand
- Storage overhead: Nx (3x for 3 copies)

**Example:**
```
Object → Replicate to 3 nodes
  ├─ Node A (Data Center 1)
  ├─ Node B (Data Center 2)
  └─ Node C (Data Center 3)
```

**2. Erasure Coding (EC)**
- Split object into K data chunks
- Generate M parity chunks
- Store K+M chunks across nodes
- Can recover from M failures
- Storage overhead: (K+M)/K (e.g., 1.5x for 6+3)

**Example (6+3 Erasure Coding):**
```
Object (60MB) → Split into:
  - 6 data chunks (10MB each)
  - 3 parity chunks (10MB each)
  - Store 9 chunks across 9 nodes
  - Can lose any 3 chunks and still recover
  - Storage overhead: 1.5x (vs 3x for replication)
```

**3. Hybrid Approach**
- Hot data: 3x replication (fast access)
- Warm data: Erasure coding (cost efficient)
- Cold data: Erasure coding + compression

#### Replication Process

**Write Path:**
```
1. Client uploads object
2. Storage service receives object
3. Split into chunks (if using EC)
4. Write chunks to primary nodes
5. Trigger replication to secondary nodes
6. Wait for quorum (e.g., 2 of 3 replicas)
7. Update metadata with storage locations
8. Return success to client
```

**Read Path:**
```
1. Client requests object
2. Metadata service returns storage locations
3. Storage service reads from nearest node
4. If node unavailable, read from replica
5. Verify checksum
6. Return object to client
```

**Failure Handling:**
- Detect failed nodes (health checks)
- Trigger re-replication from healthy replicas
- Maintain replication factor
- Background repair process

---

#### 7. Consistency Model

#### Eventual Consistency (Default)

**Behavior:**
- Writes may take time to propagate
- Reads may see stale data temporarily
- Eventually all replicas converge
- Best for high availability and performance

**Use Cases:**
- Most object storage operations
- Non-critical data
- High-throughput scenarios

**Example:**
```
Write to Node A → Replicate to B, C
Read from Node B (may see old data)
Eventually all nodes have latest data
```

#### Strong Consistency (Optional)

**Behavior:**
- Read-after-write consistency
- All reads see latest write
- Higher latency
- Lower throughput

**Implementation:**
- Read from quorum (2 of 3 replicas)
- Compare versions/timestamps
- Return latest version

**Use Cases:**
- Critical data
- When consistency is required
- Lower throughput acceptable

### Scalability Design

### Horizontal Scaling

**Metadata Service:**
- Stateless design
- Load balancer distributes requests
- Scale by adding instances
- No shared state

**Storage Nodes:**
- Add nodes to increase capacity
- Automatic data rebalancing
- Consistent hashing for object placement
- No single bottleneck

**Metadata Database:**
- Cassandra: Add nodes, automatic sharding
- Partition by bucket_name
- Replication across data centers

### Partitioning Strategy

**Object Placement:**
- Consistent hashing based on object key
- Ensures even distribution
- Minimal rebalancing on node addition/removal

**Example:**
```
Hash(object_key) % num_nodes → Storage node
Object "photos/img1.jpg" → Hash → Node 5
Object "photos/img2.jpg" → Hash → Node 2
```

**Metadata Partitioning:**
- Partition by (bucket_name, object_key)
- Ensures metadata locality
- Efficient prefix queries

### Load Balancing

**Strategies:**
1. **Round Robin**: Distribute evenly
2. **Least Connections**: Route to least busy
3. **Geographic**: Route to nearest data center
4. **Consistent Hashing**: Same object → same node

**Multi-Level:**
- Global load balancer (DNS)
- Regional load balancers
- Service-level load balancers

---

### Performance Optimization

### Caching Strategy

**1. Metadata Cache (Redis)**
- Cache frequently accessed metadata
- TTL: 5-15 minutes
- Invalidate on updates

**2. CDN (Content Delivery Network)**
- Cache popular objects at edge
- Reduce latency for global users
- Cache-Control headers

**3. Object Cache**
- Cache hot objects in memory
- LRU eviction policy
- Reduce disk I/O

### Compression

**Storage Compression:**
- Compress objects before storage
- Gzip, Snappy, LZ4
- Trade-off: CPU vs storage cost

**Transfer Compression:**
- Compress during transfer
- Reduce bandwidth costs
- Client can request compression

### Parallel Operations

**Multi-Part Upload:**
- Split large objects into parts
- Upload parts in parallel
- Merge parts on server
- Resume interrupted uploads

**Parallel Reads:**
- Read from multiple replicas
- Combine chunks in parallel
- Faster retrieval

### Network Optimization

**Bandwidth Management:**
- Throttling per user/bucket
- Quality of Service (QoS)
- Prioritize critical operations

**Connection Pooling:**
- Reuse connections
- Reduce connection overhead
- Keep-alive connections

---

### Data Integrity

### Checksums

**ETag (Entity Tag):**
- MD5 hash of object content
- Verify integrity on upload/download
- Detect corruption

**Process:**
```
Upload: Client calculates MD5 → Server verifies
Download: Server sends ETag → Client verifies
```

**Storage-Level Checksums:**
- Checksum per chunk
- Verify on read
- Background verification

### Corruption Detection

**Background Scans:**
- Periodically verify all objects
- Compare checksums
- Trigger repair if corruption detected

**Repair Process:**
- Detect corrupted chunk
- Recover from other replicas
- Re-replicate to maintain durability

---

### Cost Optimization

### Storage Tiers

**1. Hot Storage**
- Frequently accessed data
- Low latency (SSD)
- Higher cost
- Use case: Active data

**2. Warm Storage**
- Occasionally accessed data
- Medium latency (HDD)
- Medium cost
- Use case: Archives

**3. Cold Storage**
- Rarely accessed data
- High latency (tape/glacier)
- Low cost
- Use case: Long-term backup

**Lifecycle Policies:**
```
Hot → Warm (after 30 days)
Warm → Cold (after 90 days)
Delete (after 1 year)
```

### Erasure Coding

**Cost Savings:**
- 3x replication: 3x storage cost
- 6+3 erasure coding: 1.5x storage cost
- 50% cost reduction

**Trade-off:**
- Higher CPU for encoding/decoding
- Slower recovery (need to reconstruct)
- Good for warm/cold data

### Compression

**Storage Savings:**
- Compress objects before storage
- 30-70% reduction typical
- Trade-off: CPU cost

**Deduplication:**
- Detect duplicate objects
- Store once, reference multiple times
- Significant savings for backups

---

## Security

### Authentication

**Methods:**
1. **API Keys**: Access key + secret key
2. **IAM**: Identity and Access Management
3. **OAuth 2.0**: Token-based
4. **Federated Identity**: SAML, OpenID Connect

**Request Signing:**
- HMAC-SHA256 signature
- Include timestamp (prevent replay)
- Include request parameters

### Authorization

**Access Control Lists (ACLs):**
- Per-object permissions
- Read, write, delete permissions
- User/group-based

**Bucket Policies:**
- JSON policy documents
- Fine-grained permissions
- IP-based restrictions

**Signed URLs:**
- Temporary access URLs
- Expiration time
- No authentication needed
- Use case: Public sharing

### Encryption

**Encryption at Rest:**
- AES-256 encryption
- Per-object encryption keys
- Key management service (KMS)

**Encryption in Transit:**
- TLS 1.3 for HTTPS
- End-to-end encryption option
- Certificate management

**Key Management:**
- Centralized key service
- Key rotation
- Audit logging

---

## Monitoring & Observability

### Key Metrics

**Performance:**
- Request latency (p50, p95, p99)
- Throughput (requests/second)
- Error rates
- Cache hit ratio

**Storage:**
- Total storage used
- Storage by tier
- Replication status
- Node capacity

**Durability:**
- Replication factor
- Failed replications
- Corruption events
- Repair progress

**Cost:**
- Storage costs by tier
- Bandwidth costs
- Request costs
- Cost per GB stored

### Logging

**Structured Logging:**
- All API requests logged
- Include: user, bucket, key, timestamp, latency
- Centralized logging (ELK stack)

**Audit Logging:**
- All data access logged
- Compliance requirements
- Security monitoring

### Alerting

**Critical Alerts:**
- Service downtime
- High error rates
- Storage capacity thresholds
- Replication failures
- Security breaches

---

## Disaster Recovery

### Backup Strategy

**Metadata Backups:**
- Daily snapshots
- Point-in-time recovery
- Cross-region backups

**Object Backups:**
- Replication across regions
- Versioning enabled
- Immutable backups

### Recovery Procedures

**RTO (Recovery Time Objective):**
- Target: < 1 hour
- Automated failover
- Health checks

**RPO (Recovery Point Objective):**
- Target: < 15 minutes
- Continuous replication
- Transaction logs

### Multi-Region Deployment

**Active-Active:**
- Multiple regions serving traffic
- Data replicated across regions
- Automatic failover

**Active-Passive:**
- Primary region active
- Secondary region standby
- Failover on primary failure

---

## Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **API Gateway** | Envoy / NGINX | High performance, routing |
| **Metadata DB** | Cassandra / DynamoDB | High write throughput, scalability |
| **Cache** | Redis Cluster | Fast metadata caching |
| **Storage Nodes** | Custom / Ceph | Distributed storage |
| **Load Balancer** | HAProxy / AWS ELB | Request distribution |
| **CDN** | CloudFront / Cloudflare | Global content delivery |
| **Monitoring** | Prometheus + Grafana | Metrics and visualization |
| **Logging** | ELK Stack | Centralized logging |

---

## Comparison with Real Systems

### Amazon S3

**Similarities:**
- Object storage model
- RESTful API
- High durability (11 9's)
- Eventual consistency
- Lifecycle policies

**Differences:**
- S3 uses proprietary storage layer
- More advanced features (Lambda triggers, etc.)
- Global infrastructure

### Azure Blob Storage

**Similarities:**
- Blob storage model
- Tiered storage
- Access tiers (Hot, Cool, Archive)

**Differences:**
- Integrated with Azure ecosystem
- Different API design

### Google Cloud Storage

**Similarities:**
- Object storage
- Multi-region support
- Strong consistency option

**Differences:**
- Different API design
- Integrated with GCP

---

## Future Enhancements

1. **Advanced Features**
   - Object versioning
   - Object locking (WORM)
   - Cross-region replication
   - Event notifications

2. **Performance**
   - Multi-part upload optimization
   - Transfer acceleration
   - Intelligent tiering

3. **Integration**
   - Database backups
   - Data lake integration
   - Analytics integration

4. **AI/ML**
   - Content analysis
   - Automatic tagging
   - Anomaly detection

---

## What Interviewers Look For

### Storage Systems Skills

1. **Object Storage Architecture**
   - Metadata vs. data separation
   - Consistent hashing
   - Multi-copy replication
   - **Red Flags**: No separation, poor distribution, single copy

2. **Durability Design**
   - 11 9's durability target
   - Erasure coding
   - Multi-region replication
   - **Red Flags**: No durability strategy, single region, no redundancy

3. **Scalability Design**
   - Horizontal scaling
   - Partitioning strategy
   - Load distribution
   - **Red Flags**: Vertical scaling, bottlenecks, poor distribution

### Distributed Systems Skills

1. **Consistency Models**
   - Eventual consistency (default)
   - Strong consistency (optional)
   - **Red Flags**: Wrong consistency model, no understanding

2. **Replication Strategy**
   - Multi-copy for hot data
   - Erasure coding for cold data
   - **Red Flags**: Single strategy, no optimization, high costs

3. **Metadata Management**
   - High write throughput
   - Efficient queries
   - **Red Flags**: Wrong database, slow queries, bottlenecks

### Problem-Solving Approach

1. **Cost Optimization**
   - Storage tiers
   - Erasure coding
   - Compression
   - **Red Flags**: No optimization, high costs, single tier

2. **Edge Cases**
   - Node failures
   - Network partitions
   - Data corruption
   - **Red Flags**: Ignoring failures, no recovery, data loss

3. **Trade-off Analysis**
   - Durability vs. cost
   - Consistency vs. performance
   - **Red Flags**: No trade-offs, dogmatic choices

### System Design Skills

1. **Component Design**
   - Metadata service
   - Storage service
   - API gateway
   - **Red Flags**: Monolithic, unclear boundaries

2. **Performance Optimization**
   - Multi-layer caching
   - CDN integration
   - Parallel operations
   - **Red Flags**: No caching, slow operations, no optimization

3. **Security Design**
   - Encryption at rest
   - Encryption in transit
   - Access control
   - **Red Flags**: No encryption, insecure, no access control

### Communication Skills

1. **Architecture Explanation**
   - Can explain metadata/data separation
   - Understands durability strategies
   - **Red Flags**: No understanding, vague explanations

2. **Trade-off Justification**
   - Explains design decisions
   - Discusses alternatives
   - **Red Flags**: No justification, no alternatives

### Meta-Specific Focus

1. **Storage Systems Expertise**
   - Deep understanding of object storage
   - Durability and consistency
   - **Key**: Show storage systems expertise

2. **Scale Thinking**
   - Exabytes of data
   - Billions of objects
   - **Key**: Demonstrate scale expertise

## Conclusion

Designing a blob storage system like S3 requires careful consideration of:

1. **Architecture**: Separate metadata and storage layers
2. **Durability**: Multi-copy replication or erasure coding
3. **Scalability**: Horizontal scaling, consistent hashing
4. **Performance**: Caching, CDN, parallel operations
5. **Cost**: Storage tiers, erasure coding, compression
6. **Security**: Encryption, authentication, authorization

**Key Design Decisions:**
- **Metadata DB**: Cassandra for high write throughput
- **Replication**: 3x replication for hot data, erasure coding for warm/cold
- **Consistency**: Eventual consistency (default), strong consistency (optional)
- **Caching**: Multi-layer caching (Redis, CDN)
- **Storage**: Distributed nodes with consistent hashing

The system is designed to scale to exabytes of data while maintaining high durability, availability, and performance at reasonable cost.

