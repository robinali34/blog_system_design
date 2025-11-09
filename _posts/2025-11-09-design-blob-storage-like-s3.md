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

---

## Problem Statement

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

---

## Scale Estimates

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

---

## Architecture Overview

### High-Level Architecture

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

---

## Component Design

### 1. API Gateway / Load Balancer

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

### 2. Metadata Service

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

### 3. Metadata Database

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

### 4. Storage Service

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

### 5. Storage Nodes

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

### 6. Data Durability & Replication

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

### 7. Consistency Model

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

---

## Data Flow Examples

### Example 1: PUT Object (Upload)

```
1. Client → API Gateway
   PUT /my-bucket/my-object
   Headers: Content-Type, Content-Length, Authorization
   Body: Object data
   
2. API Gateway → Authentication Service
   Validate credentials, check permissions
   
3. API Gateway → Metadata Service
   Check bucket exists, validate key
   
4. Metadata Service → Storage Service
   Request storage allocation
   
5. Storage Service:
   a. Split object into chunks (if needed)
   b. Select storage nodes (3 nodes for replication)
   c. Write chunks to primary node
   d. Trigger replication to secondary nodes
   e. Wait for quorum (2 of 3 written)
   
6. Storage Service → Metadata Service
   Update metadata with:
   - Object key, size, etag
   - Storage node locations
   - Timestamps
   
7. Metadata Service → Metadata DB
   Insert/update object metadata
   
8. Metadata Service → API Gateway
   Return success (201 Created)
   
9. API Gateway → Client
   Return ETag, location
```

**Optimization:**
- Parallel writes to storage nodes
- Asynchronous replication (for non-critical)
- Chunked uploads for large objects
- Direct upload to storage nodes (signed URLs)

---

### Example 2: GET Object (Download)

```
1. Client → API Gateway
   GET /my-bucket/my-object
   Headers: Authorization, Range (optional)
   
2. API Gateway → Authentication Service
   Validate credentials, check permissions
   
3. API Gateway → Metadata Service
   Get object metadata
   
4. Metadata Service → Metadata DB
   Query object metadata by bucket+key
   
5. Metadata DB → Metadata Service
   Return metadata including storage locations
   
6. Metadata Service → Storage Service
   Request object retrieval
   
7. Storage Service:
   a. Select nearest/available storage node
   b. Read object chunks from node
   c. Verify checksum
   d. If node unavailable, read from replica
   
8. Storage Service → API Gateway
   Stream object data
   
9. API Gateway → Client
   Return object with headers (Content-Type, ETag)
```

**Optimization:**
- CDN caching for popular objects
- Range requests for partial downloads
- Parallel reads from multiple replicas
- Compression for transfer

---

### Example 3: LIST Objects

```
1. Client → API Gateway
   GET /my-bucket?prefix=photos/
   
2. API Gateway → Metadata Service
   List objects with prefix
   
3. Metadata Service → Metadata DB
   Query objects by bucket+prefix
   
4. Metadata DB → Metadata Service
   Return paginated results
   
5. Metadata Service → API Gateway
   Return object list (keys, sizes, timestamps)
   
6. API Gateway → Client
   Return XML/JSON response
```

**Optimization:**
- Pagination (limit results per page)
- Caching common prefixes
- Index optimization for prefix queries
- Parallel queries for large buckets

---

## Scalability Design

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

## Performance Optimization

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

## Data Integrity

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

## Cost Optimization

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

