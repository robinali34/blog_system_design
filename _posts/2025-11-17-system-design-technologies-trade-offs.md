---
layout: post
title: "System Design Interview: Technologies, Options, and Trade-offs - Complete Reference Guide"
date: 2025-11-17
categories: [System Design, Interview Preparation, Distributed Systems, Technologies, Trade-offs, Reference Guide]
excerpt: "A comprehensive reference guide covering all major technologies, options, and trade-offs for system design interviews, including databases, caching, message queues, search engines, CDNs, load balancers, storage systems, and stream processing frameworks."
---

## Introduction

System design interviews require making informed decisions about which technologies to use for different components of a system. Understanding the trade-offs, use cases, and alternatives for each technology is crucial for designing scalable, reliable, and efficient systems.

This comprehensive guide covers all major technologies used in system design interviews, their characteristics, trade-offs, and when to use them. Use this as a reference when preparing for system design interviews or making architectural decisions.

## Table of Contents

1. [Databases](#databases)
   - [SQL Databases](#sql-databases)
   - [NoSQL Databases](#nosql-databases)
   - [Time-Series Databases](#time-series-databases)
   - [Graph Databases](#graph-databases)
   - [In-Memory Databases](#in-memory-databases)
2. [Caching Solutions](#caching-solutions)
3. [Message Queues](#message-queues)
4. [Search Engines](#search-engines)
5. [Content Delivery Networks (CDNs)](#content-delivery-networks-cdns)
6. [Load Balancers](#load-balancers)
7. [Storage Systems](#storage-systems)
8. [Stream Processing](#stream-processing)
9. [API Design Patterns](#api-design-patterns)
10. [Consistency Models](#consistency-models)
11. [Replication Strategies](#replication-strategies)
12. [Sharding Strategies](#sharding-strategies)
13. [Summary](#summary)

## Databases

### SQL Databases

**Examples:** PostgreSQL, MySQL, Oracle, SQL Server

**Characteristics:**
- ACID transactions
- Relational data model
- Strong consistency
- SQL query language
- Vertical scaling (can scale horizontally with sharding)

**Use Cases:**
- Financial transactions
- User accounts and authentication
- E-commerce orders
- Systems requiring strong consistency
- Complex queries with joins
- Data integrity critical applications

**Pros:**
- ACID guarantees
- Strong consistency
- Mature ecosystem
- Rich query capabilities (joins, aggregations)
- Data integrity constraints
- Well-understood by developers

**Cons:**
- Limited horizontal scalability
- Schema changes can be expensive
- Performance issues with large datasets
- Joins can be slow at scale
- Vertical scaling is expensive

**Trade-offs:**
- **Consistency vs. Availability**: Strong consistency may reduce availability
- **Flexibility vs. Performance**: Fixed schema improves performance but reduces flexibility
- **Scalability**: Vertical scaling is limited; horizontal scaling requires complex sharding

**When to Use:**
- Need ACID transactions
- Complex relational queries
- Strong consistency requirements
- Data integrity is critical
- Moderate scale (< 100M records per table)

**Alternatives:**
- NoSQL for better scalability
- NewSQL (CockroachDB, Spanner) for distributed SQL

---

### NoSQL Databases

#### Document Databases

**Examples:** MongoDB, CouchDB, DynamoDB

**Characteristics:**
- Document-based storage (JSON/BSON)
- Schema-less or flexible schema
- Horizontal scaling
- Eventual consistency (can be configured)

**Use Cases:**
- Content management systems
- User profiles
- Product catalogs
- Real-time analytics
- Mobile applications

**Pros:**
- Flexible schema
- Easy horizontal scaling
- Good for semi-structured data
- Fast writes
- JSON-friendly

**Cons:**
- No joins (must denormalize)
- Eventual consistency
- Limited transaction support
- Query capabilities less rich than SQL

**Trade-offs:**
- **Flexibility vs. Consistency**: Flexible schema but eventual consistency
- **Performance vs. Features**: Fast but limited query capabilities

**When to Use:**
- Flexible schema requirements
- High write throughput
- Horizontal scaling needed
- Document-based data model fits well

---

#### Key-Value Stores

**Examples:** Redis, DynamoDB, Riak, Voldemort

**Characteristics:**
- Simple key-value model
- Very fast reads/writes
- Horizontal scaling
- Simple data model

**Use Cases:**
- Caching
- Session storage
- Shopping carts
- User preferences
- Real-time leaderboards

**Pros:**
- Extremely fast
- Simple data model
- Horizontal scaling
- Low latency

**Cons:**
- Limited query capabilities
- No complex data structures
- Data modeling limitations

**Trade-offs:**
- **Simplicity vs. Functionality**: Simple but limited query capabilities
- **Performance vs. Features**: Fast but basic

**When to Use:**
- Simple data model (key-value)
- High performance requirements
- Caching layer
- Session management

---

#### Column-Family Stores (Wide-Column)

**Examples:** Cassandra, HBase, ScyllaDB

**Characteristics:**
- Column-family data model
- Excellent horizontal scaling
- High write throughput
- Eventual consistency
- No single point of failure

**Use Cases:**
- Time-series data
- Logging systems
- IoT data
- High write throughput systems
- Multi-region deployments

**Pros:**
- Excellent horizontal scaling
- High write throughput
- No single point of failure
- Multi-region support
- Tunable consistency

**Cons:**
- Eventual consistency
- Limited query capabilities
- Complex data modeling
- No joins or transactions

**Trade-offs:**
- **Scalability vs. Consistency**: Excellent scalability but eventual consistency
- **Write Performance vs. Read Complexity**: Fast writes but complex reads

**When to Use:**
- High write throughput
- Time-series data
- Multi-region requirements
- Horizontal scaling critical
- Can tolerate eventual consistency

---

#### Graph Databases

**Examples:** Neo4j, Amazon Neptune, ArangoDB

**Characteristics:**
- Graph data model (nodes, edges, properties)
- Optimized for graph traversals
- Relationship queries
- ACID transactions (some)

**Use Cases:**
- Social networks
- Recommendation engines
- Fraud detection
- Knowledge graphs
- Network analysis

**Pros:**
- Excellent for relationship queries
- Fast graph traversals
- Flexible schema
- Good for complex relationships

**Cons:**
- Limited horizontal scaling
- Specialized use case
- Can be expensive
- Learning curve

**Trade-offs:**
- **Relationship Queries vs. Scalability**: Great for relationships but limited scaling
- **Specialization vs. General Use**: Optimized for graphs but not general purpose

**When to Use:**
- Complex relationships
- Graph traversals needed
- Social networks
- Recommendation systems
- Fraud detection

---

### Time-Series Databases

**Examples:** InfluxDB, TimescaleDB, Prometheus

**Characteristics:**
- Optimized for time-series data
- Efficient compression
- Time-based queries
- High write throughput

**Use Cases:**
- IoT sensor data
- Monitoring and metrics
- Financial tick data
- Log aggregation
- Real-time analytics

**Pros:**
- Optimized for time-series
- Efficient storage (compression)
- Fast time-range queries
- High write throughput

**Cons:**
- Specialized use case
- Limited general-purpose queries
- Can be expensive

**Trade-offs:**
- **Specialization vs. General Use**: Optimized for time-series but limited elsewhere

**When to Use:**
- Time-series data
- Monitoring/metrics
- IoT applications
- High-frequency time-stamped data

---

### In-Memory Databases

**Examples:** Redis, Memcached, Apache Ignite

**Characteristics:**
- Data stored in RAM
- Extremely fast
- Volatile (data lost on restart)
- Limited capacity

**Use Cases:**
- Caching
- Session storage
- Real-time analytics
- Leaderboards
- Rate limiting

**Pros:**
- Extremely fast (microsecond latency)
- Low latency
- High throughput

**Cons:**
- Volatile (data can be lost)
- Limited capacity (RAM is expensive)
- Cost per GB is high

**Trade-offs:**
- **Speed vs. Durability**: Fast but volatile
- **Performance vs. Cost**: Fast but expensive

**When to Use:**
- Caching layer
- Session storage
- Real-time data
- Temporary data
- Performance critical

---

## Caching Solutions

### Redis

**Characteristics:**
- In-memory data store
- Rich data structures (strings, lists, sets, sorted sets, hashes)
- Persistence options (RDB, AOF)
- Pub/Sub support
- Lua scripting

**Use Cases:**
- Caching
- Session storage
- Real-time leaderboards
- Rate limiting
- Pub/Sub messaging
- Distributed locks

**Pros:**
- Very fast
- Rich data structures
- Persistence options
- Pub/Sub support
- Widely used and well-documented

**Cons:**
- Single-threaded (can be bottleneck)
- Memory limited
- Cost per GB is high

**Trade-offs:**
- **Performance vs. Cost**: Fast but expensive
- **Features vs. Simplicity**: Rich features but more complex than Memcached

**When to Use:**
- Need rich data structures
- Pub/Sub required
- Complex caching needs
- Real-time features needed

---

### Memcached

**Characteristics:**
- Simple key-value cache
- Multi-threaded
- No persistence
- Simple API

**Use Cases:**
- Simple caching
- Session storage
- Database query caching

**Pros:**
- Simple
- Multi-threaded (better CPU utilization)
- Lightweight
- Fast

**Cons:**
- No persistence
- Limited data structures
- No advanced features

**Trade-offs:**
- **Simplicity vs. Features**: Simple but limited features

**When to Use:**
- Simple caching needs
- No persistence required
- High throughput needed

---

### CDN Caching

**Characteristics:**
- Edge caching
- Geographic distribution
- Static content caching
- Reduced latency

**Use Cases:**
- Static assets (images, CSS, JS)
- Video streaming
- API responses (if cacheable)
- Global content delivery

**Pros:**
- Reduced latency
- Reduced origin server load
- Global distribution
- High availability

**Cons:**
- Cache invalidation complexity
- Cost for high traffic
- Not suitable for dynamic content

**Trade-offs:**
- **Latency vs. Freshness**: Low latency but cache invalidation needed

**When to Use:**
- Static content
- Global audience
- High read traffic
- Latency sensitive

---

### Application-Level Caching

**Characteristics:**
- In-process caching
- Local to application
- Very fast
- Limited capacity

**Use Cases:**
- Frequently accessed data
- Configuration data
- Reference data

**Pros:**
- Extremely fast (no network)
- No external dependency
- Simple

**Cons:**
- Limited capacity
- Not shared across instances
- Memory overhead

**Trade-offs:**
- **Speed vs. Capacity**: Fast but limited

**When to Use:**
- Small, frequently accessed data
- Data that doesn't change often
- Performance critical paths

---

## Message Queues

### Apache Kafka

**Characteristics:**
- Distributed streaming platform
- High throughput
- Durable (disk-based)
- Pub/Sub model
- Partitioned topics
- Exactly-once semantics

**Use Cases:**
- Event streaming
- Log aggregation
- Real-time analytics
- Event sourcing
- Microservices communication

**Pros:**
- Very high throughput
- Durable (disk-based)
- Horizontal scaling
- Exactly-once semantics
- Long retention
- Replay capability

**Cons:**
- Complex setup and operations
- Higher latency than in-memory queues
- Requires Zookeeper (or KRaft)
- Learning curve

**Trade-offs:**
- **Throughput vs. Latency**: High throughput but higher latency
- **Durability vs. Performance**: Durable but slower than in-memory

**When to Use:**
- High throughput requirements
- Event streaming
- Log aggregation
- Need replay capability
- Long retention needed

---

### RabbitMQ

**Characteristics:**
- Traditional message broker
- Multiple messaging patterns (queues, topics, pub/sub)
- ACK-based delivery
- Management UI
- Plugins ecosystem

**Use Cases:**
- Task queues
- Work distribution
- Request/response patterns
- Traditional messaging

**Pros:**
- Mature and stable
- Rich features
- Good management tools
- Multiple messaging patterns
- Easy to use

**Cons:**
- Lower throughput than Kafka
- Single broker can be bottleneck
- Clustering complexity

**Trade-offs:**
- **Features vs. Performance**: Rich features but lower throughput

**When to Use:**
- Traditional messaging needs
- Task queues
- Work distribution
- Moderate throughput

---

### Amazon SQS

**Characteristics:**
- Managed message queue
- Serverless
- Auto-scaling
- At-least-once delivery
- Dead-letter queues

**Use Cases:**
- Decoupling services
- Task queues
- Event-driven architectures
- AWS-native applications

**Pros:**
- Fully managed
- Auto-scaling
- Pay-per-use
- No infrastructure management
- Integrates with AWS services

**Cons:**
- Vendor lock-in
- Limited throughput per queue
- At-least-once delivery (not exactly-once)
- Cost at scale

**Trade-offs:**
- **Management vs. Control**: Managed but less control
- **Cost vs. Scale**: Pay-per-use but can be expensive at scale

**When to Use:**
- AWS-native applications
- Want managed service
- Moderate throughput
- Decoupling services

---

### Apache Pulsar

**Characteristics:**
- Distributed pub/sub messaging
- Multi-tenancy
- Geo-replication
- Tiered storage
- Unified messaging model

**Use Cases:**
- Multi-tenant systems
- Geo-distributed systems
- Event streaming
- High throughput messaging

**Pros:**
- Multi-tenancy
- Geo-replication
- Tiered storage (cost-effective)
- Unified messaging model
- Better than Kafka for some use cases

**Cons:**
- Less mature than Kafka
- Smaller ecosystem
- Learning curve

**Trade-offs:**
- **Features vs. Maturity**: Rich features but less mature

**When to Use:**
- Multi-tenant requirements
- Geo-replication needed
- Event streaming
- Want alternatives to Kafka

---

## Search Engines

### Elasticsearch

**Characteristics:**
- Distributed search engine
- Full-text search
- Real-time indexing
- RESTful API
- Rich query DSL
- Aggregations

**Use Cases:**
- Full-text search
- Log analysis
- Real-time analytics
- Application search
- Security analytics

**Pros:**
- Powerful search capabilities
- Real-time indexing
- Rich query DSL
- Aggregations
- Horizontal scaling
- Good documentation

**Cons:**
- Complex to operate
- Resource intensive
- Can be expensive
- Requires expertise

**Trade-offs:**
- **Features vs. Complexity**: Powerful but complex
- **Performance vs. Cost**: Fast but resource-intensive

**When to Use:**
- Full-text search needed
- Complex queries
- Real-time search
- Log analysis
- Analytics

---

### Apache Solr

**Characteristics:**
- Search platform
- Full-text search
- Faceted search
- RESTful API
- Similar to Elasticsearch

**Use Cases:**
- Enterprise search
- E-commerce search
- Content search

**Pros:**
- Mature
- Good for faceted search
- Stable

**Cons:**
- Less popular than Elasticsearch
- Smaller ecosystem
- Less real-time than Elasticsearch

**Trade-offs:**
- **Maturity vs. Innovation**: Mature but less innovative

**When to Use:**
- Enterprise search
- Faceted search needed
- Prefer mature solutions

---

### Algolia

**Characteristics:**
- Managed search service
- Typo tolerance
- Instant search
- Analytics
- API-first

**Use Cases:**
- E-commerce search
- Application search
- Mobile app search

**Pros:**
- Managed service
- Typo tolerance
- Instant search
- Good UX features
- Easy to integrate

**Cons:**
- Vendor lock-in
- Cost at scale
- Less control

**Trade-offs:**
- **Ease vs. Control**: Easy but less control
- **Cost vs. Scale**: Can be expensive at scale

**When to Use:**
- Want managed service
- E-commerce search
- Need typo tolerance
- Quick integration needed

---

## Content Delivery Networks (CDNs)

### CloudFront (AWS)

**Characteristics:**
- Global CDN
- Edge locations
- Integration with AWS services
- DDoS protection
- Custom SSL certificates

**Use Cases:**
- Static content delivery
- Video streaming
- API acceleration
- Global content distribution

**Pros:**
- AWS integration
- Global network
- DDoS protection
- Pay-per-use

**Cons:**
- AWS vendor lock-in
- Cost at scale
- Less control than self-hosted

**Trade-offs:**
- **Integration vs. Flexibility**: Good AWS integration but less flexible

**When to Use:**
- AWS-native applications
- Want managed CDN
- Global distribution needed

---

### Cloudflare

**Characteristics:**
- CDN + security
- DDoS protection
- WAF (Web Application Firewall)
- Free tier available
- Global network

**Use Cases:**
- Website acceleration
- DDoS protection
- Security services
- Global content delivery

**Pros:**
- Free tier
- Security features
- DDoS protection
- Good performance

**Cons:**
- Less control than self-hosted
- Can be expensive at scale

**Trade-offs:**
- **Features vs. Cost**: Rich features but can be expensive

**When to Use:**
- Need security features
- Want free tier
- Website acceleration
- DDoS protection needed

---

### Self-Hosted CDN

**Characteristics:**
- Full control
- Custom configuration
- Can use Varnish, Nginx, etc.

**Use Cases:**
- Custom requirements
- Cost optimization
- Full control needed

**Pros:**
- Full control
- Cost optimization possible
- Custom configuration

**Cons:**
- Operational overhead
- Requires expertise
- Infrastructure management

**Trade-offs:**
- **Control vs. Management**: Full control but more management

**When to Use:**
- Custom requirements
- Want full control
- Have operational expertise
- Cost optimization critical

---

## Load Balancers

### Application Load Balancer (ALB)

**Characteristics:**
- Layer 7 (HTTP/HTTPS)
- Content-based routing
- SSL termination
- Health checks
- Auto-scaling

**Use Cases:**
- HTTP/HTTPS traffic
- Microservices routing
- Content-based routing
- SSL termination

**Pros:**
- Content-based routing
- SSL termination
- Health checks
- Auto-scaling
- Managed service

**Cons:**
- Higher latency than NLB
- Cost
- AWS vendor lock-in

**Trade-offs:**
- **Features vs. Latency**: Rich features but higher latency

**When to Use:**
- HTTP/HTTPS traffic
- Content-based routing needed
- Microservices
- SSL termination needed

---

### Network Load Balancer (NLB)

**Characteristics:**
- Layer 4 (TCP/UDP)
- Low latency
- High throughput
- Connection-based routing

**Use Cases:**
- TCP/UDP traffic
- Low latency requirements
- High throughput
- Non-HTTP protocols

**Pros:**
- Low latency
- High throughput
- Connection-based routing
- Managed service

**Cons:**
- No content-based routing
- Less features than ALB

**Trade-offs:**
- **Performance vs. Features**: Fast but fewer features

**When to Use:**
- Low latency critical
- High throughput needed
- TCP/UDP protocols
- Non-HTTP traffic

---

### HAProxy / Nginx

**Characteristics:**
- Software load balancers
- Full control
- Configurable
- Can be self-hosted

**Use Cases:**
- Custom load balancing
- Cost optimization
- Full control needed

**Pros:**
- Full control
- Cost-effective
- Highly configurable
- No vendor lock-in

**Cons:**
- Operational overhead
- Requires expertise
- Infrastructure management

**Trade-offs:**
- **Control vs. Management**: Full control but more management

**When to Use:**
- Custom requirements
- Want full control
- Cost optimization
- Have operational expertise

---

## Storage Systems

### Object Storage (S3, GCS, Azure Blob)

**Characteristics:**
- Key-value storage
- Unlimited scale
- Durable
- Cost-effective
- RESTful API

**Use Cases:**
- File storage
- Backup and archival
- Static assets
- Data lakes
- Media storage

**Pros:**
- Unlimited scale
- Durable
- Cost-effective
- RESTful API
- Versioning support

**Cons:**
- Eventual consistency
- Not for frequent updates
- Higher latency than block storage

**Trade-offs:**
- **Scale vs. Performance**: Unlimited scale but higher latency

**When to Use:**
- File storage
- Backup/archival
- Static assets
- Data lakes
- Media storage

---

### Block Storage (EBS, Persistent Disk)

**Characteristics:**
- Block-level storage
- Attached to instances
- Low latency
- Limited scale per volume

**Use Cases:**
- Database storage
- Application storage
- Boot volumes
- High IOPS requirements

**Pros:**
- Low latency
- High IOPS
- Direct attachment
- Good for databases

**Cons:**
- Limited scale per volume
- More expensive than object storage
- Tied to instances

**Trade-offs:**
- **Performance vs. Scale**: Low latency but limited scale

**When to Use:**
- Database storage
- High IOPS needed
- Low latency critical
- Application storage

---

### Distributed File Systems (HDFS, GlusterFS)

**Characteristics:**
- Distributed across nodes
- High throughput
- Fault tolerant
- Good for large files

**Use Cases:**
- Big data processing
- Data lakes
- Analytics workloads
- Large file storage

**Pros:**
- High throughput
- Fault tolerant
- Good for large files
- Cost-effective

**Cons:**
- Not for small files
- Higher latency
- Complex operations

**Trade-offs:**
- **Throughput vs. Latency**: High throughput but higher latency

**When to Use:**
- Big data processing
- Large files
- Analytics workloads
- Batch processing

---

## Stream Processing

### Apache Flink

**Characteristics:**
- Stream processing framework
- Low latency
- Exactly-once semantics
- Stateful processing
- Event time processing

**Use Cases:**
- Real-time analytics
- Event-driven applications
- Complex event processing
- Top-K calculations
- Windowed aggregations

**Pros:**
- Low latency
- Exactly-once semantics
- Stateful processing
- Event time processing
- Good fault tolerance

**Cons:**
- Complex to operate
- Learning curve
- Resource intensive

**Trade-offs:**
- **Features vs. Complexity**: Powerful but complex

**When to Use:**
- Real-time processing
- Exactly-once needed
- Stateful processing
- Low latency critical

---

### Apache Kafka Streams

**Characteristics:**
- Stream processing library
- Part of Kafka ecosystem
- Lightweight
- Exactly-once semantics

**Use Cases:**
- Kafka-native processing
- Simple stream processing
- Microservices

**Pros:**
- Kafka integration
- Lightweight
- Exactly-once semantics
- Easy to deploy

**Cons:**
- Less features than Flink
- Tied to Kafka
- Limited for complex processing

**Trade-offs:**
- **Simplicity vs. Features**: Simple but fewer features

**When to Use:**
- Kafka ecosystem
- Simple processing
- Microservices
- Lightweight needs

---

### Apache Storm

**Characteristics:**
- Stream processing framework
- Real-time processing
- At-least-once semantics
- Mature

**Use Cases:**
- Real-time processing
- Simple stream processing

**Pros:**
- Mature
- Real-time processing
- Good for simple cases

**Cons:**
- At-least-once (not exactly-once)
- Less features than Flink
- Declining popularity

**Trade-offs:**
- **Maturity vs. Features**: Mature but fewer features

**When to Use:**
- Simple stream processing
- Real-time needed
- At-least-once acceptable

---

## API Design Patterns

### REST

**Characteristics:**
- Stateless
- Resource-based
- HTTP methods
- JSON/XML
- Cacheable

**Use Cases:**
- General APIs
- CRUD operations
- Web services
- Public APIs

**Pros:**
- Simple
- Well-understood
- Cacheable
- Stateless
- Tooling support

**Cons:**
- Over-fetching/under-fetching
- Multiple round trips
- No real-time updates

**Trade-offs:**
- **Simplicity vs. Efficiency**: Simple but can be inefficient

**When to Use:**
- General APIs
- CRUD operations
- Public APIs
- Simple use cases

---

### GraphQL

**Characteristics:**
- Query language
- Single endpoint
- Client-specified queries
- Strongly typed
- Real-time subscriptions

**Use Cases:**
- Mobile applications
- Complex data requirements
- Multiple clients
- Real-time updates needed

**Pros:**
- Flexible queries
- Single endpoint
- No over-fetching
- Strongly typed
- Real-time subscriptions

**Cons:**
- Complexity
- Caching challenges
- Over-fetching prevention needed
- Learning curve

**Trade-offs:**
- **Flexibility vs. Complexity**: Flexible but complex

**When to Use:**
- Complex data requirements
- Multiple clients
- Mobile applications
- Real-time needed

---

### gRPC

**Characteristics:**
- RPC framework
- Protocol Buffers
- HTTP/2
- Strongly typed
- High performance

**Use Cases:**
- Microservices communication
- Internal APIs
- High performance needed
- Streaming

**Pros:**
- High performance
- Strongly typed
- Streaming support
- Efficient serialization
- Multi-language support

**Cons:**
- Less human-readable
- Browser support limited
- Learning curve

**Trade-offs:**
- **Performance vs. Usability**: Fast but less user-friendly

**When to Use:**
- Microservices
- Internal APIs
- High performance critical
- Streaming needed

---

## Consistency Models

### Strong Consistency

**Characteristics:**
- All reads see latest write
- ACID transactions
- Synchronous replication

**Use Cases:**
- Financial transactions
- User accounts
- Critical data
- ACID requirements

**Pros:**
- Data always correct
- Predictable behavior
- Easier to reason about

**Cons:**
- Lower availability
- Higher latency
- Limited scalability

**Trade-offs:**
- **Correctness vs. Availability**: Correct but lower availability

**When to Use:**
- Critical data
- Financial transactions
- ACID requirements
- Correctness > Availability

---

### Eventual Consistency

**Characteristics:**
- Reads may see stale data
- Asynchronous replication
- Eventually consistent

**Use Cases:**
- Social media feeds
- User profiles
- Non-critical data
- High availability needed

**Pros:**
- High availability
- Lower latency
- Better scalability
- Global distribution

**Cons:**
- Stale reads possible
- Complex conflict resolution
- Harder to reason about

**Trade-offs:**
- **Availability vs. Correctness**: High availability but may be stale

**When to Use:**
- High availability critical
- Can tolerate stale data
- Global distribution
- High scale needed

---

### Read-Your-Writes Consistency

**Characteristics:**
- User sees own writes immediately
- Others may see stale data
- Session-based

**Use Cases:**
- User profiles
- Social media
- E-commerce

**Pros:**
- Good user experience
- Better than eventual consistency for users
- Reasonable availability

**Cons:**
- Not globally consistent
- Complex to implement

**Trade-offs:**
- **UX vs. Complexity**: Good UX but complex

**When to Use:**
- User-specific data
- Good UX needed
- Can tolerate eventual consistency for others

---

## Replication Strategies

### Master-Slave (Primary-Replica)

**Characteristics:**
- One master, multiple replicas
- Master handles writes
- Replicas handle reads
- Asynchronous replication

**Use Cases:**
- Read-heavy workloads
- Scaling reads
- Backup and disaster recovery

**Pros:**
- Simple
- Scales reads
- Backup available
- Disaster recovery

**Cons:**
- Single point of failure (master)
- Replication lag
- Write bottleneck

**Trade-offs:**
- **Simplicity vs. Availability**: Simple but single point of failure

**When to Use:**
- Read-heavy workloads
- Simple setup needed
- Can tolerate replication lag

---

### Master-Master (Multi-Master)

**Characteristics:**
- Multiple masters
- Writes to any master
- Conflict resolution needed
- Synchronous or asynchronous

**Use Cases:**
- High availability
- Geographic distribution
- Write scaling

**Pros:**
- High availability
- No single point of failure
- Geographic distribution
- Write scaling

**Cons:**
- Conflict resolution complexity
- Consistency challenges
- Complex operations

**Trade-offs:**
- **Availability vs. Complexity**: High availability but complex

**When to Use:**
- High availability critical
- Geographic distribution
- Can handle conflicts
- Write scaling needed

---

### Leader-Follower (Raft, Paxos)

**Characteristics:**
- Consensus algorithm
- Leader elected
- Followers replicate
- Strong consistency

**Use Cases:**
- Distributed systems
- Configuration management
- Strong consistency needed

**Pros:**
- Strong consistency
- Fault tolerant
- No single point of failure
- Consensus guaranteed

**Cons:**
- Complex
- Higher latency
- Requires majority

**Trade-offs:**
- **Consistency vs. Latency**: Consistent but higher latency

**When to Use:**
- Strong consistency needed
- Configuration management
- Distributed coordination
- Can tolerate higher latency

---

## Sharding Strategies

### Range-Based Sharding

**Characteristics:**
- Shard by value ranges
- Sequential data
- Easy to understand

**Use Cases:**
- Time-series data
- Sequential IDs
- Range queries

**Pros:**
- Simple
- Good for range queries
- Easy to understand

**Cons:**
- Hot spots possible
- Uneven distribution
- Rebalancing needed

**Trade-offs:**
- **Simplicity vs. Distribution**: Simple but can have hot spots

**When to Use:**
- Time-series data
- Range queries
- Sequential data

---

### Hash-Based Sharding

**Characteristics:**
- Shard by hash of key
- Even distribution
- No hot spots

**Use Cases:**
- User data
- General sharding
- Even distribution needed

**Pros:**
- Even distribution
- No hot spots
- Simple hashing

**Cons:**
- Range queries difficult
- Rebalancing complex
- No locality

**Trade-offs:**
- **Distribution vs. Queries**: Even distribution but hard range queries

**When to Use:**
- Even distribution needed
- No range queries
- User data
- General sharding

---

### Directory-Based Sharding

**Characteristics:**
- Shard lookup service
- Flexible mapping
- Can change mapping

**Use Cases:**
- Flexible sharding
- Changing requirements
- Complex sharding logic

**Pros:**
- Flexible
- Can change mapping
- Complex logic possible

**Cons:**
- Single point of failure
- Lookup overhead
- Complexity

**Trade-offs:**
- **Flexibility vs. Complexity**: Flexible but complex

**When to Use:**
- Flexible sharding needed
- Complex logic
- Changing requirements

---

## What Interviewers Look For

### Technology Selection Skills

1. **Understanding Trade-offs**
   - Consistency vs. availability
   - Latency vs. throughput
   - Performance vs. cost
   - **Red Flags**: No trade-off awareness, dogmatic choices, ignoring constraints

2. **Technology Knowledge**
   - When to use SQL vs. NoSQL
   - When to use Redis vs. Memcached
   - When to use Kafka vs. RabbitMQ
   - **Red Flags**: Wrong technology choice, no justification, can't explain differences

3. **Decision-Making Framework**
   - Requirements analysis
   - Constraint identification
   - Trade-off evaluation
   - **Red Flags**: No framework, random choices, no analysis

### System Design Skills

1. **Database Selection**
   - SQL for ACID transactions
   - NoSQL for scale and flexibility
   - Time-series for metrics
   - **Red Flags**: Wrong database choice, no justification, ignoring requirements

2. **Caching Strategy**
   - Redis for rich features
   - Memcached for simplicity
   - CDN for static content
   - **Red Flags**: No caching, wrong cache choice, no strategy

3. **Message Queue Selection**
   - Kafka for high throughput
   - RabbitMQ for traditional messaging
   - SQS for managed service
   - **Red Flags**: Wrong queue choice, no justification, ignoring scale

### Problem-Solving Approach

1. **Requirements Analysis**
   - Scale requirements
   - Consistency requirements
   - Latency requirements
   - **Red Flags**: No requirements analysis, assumptions, ignoring constraints

2. **Cost Consideration**
   - Cost optimization
   - Budget constraints
   - Operational costs
   - **Red Flags**: Ignoring costs, no optimization, expensive choices

3. **Operational Complexity**
   - Team expertise
   - Maintenance overhead
   - Managed vs. self-hosted
   - **Red Flags**: Ignoring complexity, no operational consideration

### Communication Skills

1. **Technology Justification**
   - Can explain why each technology
   - Understands trade-offs
   - **Red Flags**: No justification, vague explanations, can't defend choices

2. **Alternative Discussion**
   - Considers alternatives
   - Explains why not chosen
   - **Red Flags**: No alternatives, single solution, no comparison

### Meta-Specific Focus

1. **Judgment in Technology Selection**
   - Right tool for the job
   - Understanding of trade-offs
   - **Key**: Show good judgment in technology selection

2. **Practical Knowledge**
   - Real-world experience
   - Understanding of limitations
   - **Key**: Demonstrate practical knowledge, not just theory

## Summary

### Key Decision Factors

When choosing technologies for system design, consider:

1. **Scale Requirements**
   - Read/write throughput
   - Data volume
   - Number of users
   - Geographic distribution

2. **Consistency Requirements**
   - Strong consistency vs. eventual consistency
   - ACID transactions needed?
   - Can tolerate stale data?

3. **Latency Requirements**
   - Real-time vs. batch
   - P50, P95, P99 latency targets
   - User-facing vs. background

4. **Availability Requirements**
   - Uptime SLA (99.9%, 99.99%, etc.)
   - Disaster recovery needs
   - Multi-region requirements

5. **Cost Constraints**
   - Budget limitations
   - Cost optimization needed
   - Pay-per-use vs. fixed cost

6. **Operational Complexity**
   - Team expertise
   - Operational overhead
   - Managed vs. self-hosted

7. **Data Model**
   - Relational vs. document vs. key-value
   - Query patterns
   - Relationships complexity

### Quick Reference: When to Use What

**Databases:**
- **SQL**: ACID transactions, complex queries, strong consistency
- **NoSQL Document**: Flexible schema, horizontal scaling, high writes
- **NoSQL Key-Value**: Simple model, caching, high performance
- **NoSQL Column**: Time-series, high writes, multi-region
- **Graph**: Complex relationships, social networks
- **Time-Series**: IoT, metrics, monitoring

**Caching:**
- **Redis**: Rich data structures, pub/sub, persistence
- **Memcached**: Simple caching, high throughput
- **CDN**: Static content, global distribution
- **Application Cache**: Small, frequent data, no network

**Message Queues:**
- **Kafka**: High throughput, event streaming, replay
- **RabbitMQ**: Traditional messaging, task queues
- **SQS**: Managed, AWS-native, decoupling
- **Pulsar**: Multi-tenant, geo-replication

**Search:**
- **Elasticsearch**: Full-text search, complex queries, analytics
- **Solr**: Enterprise search, faceted search
- **Algolia**: Managed, typo tolerance, instant search

**Storage:**
- **Object Storage**: Files, backups, static assets, unlimited scale
- **Block Storage**: Databases, high IOPS, low latency
- **Distributed FS**: Big data, large files, analytics

**Stream Processing:**
- **Flink**: Low latency, exactly-once, stateful processing
- **Kafka Streams**: Kafka-native, lightweight, simple
- **Storm**: Real-time, simple processing

**API Patterns:**
- **REST**: General APIs, CRUD, simple
- **GraphQL**: Complex queries, multiple clients, flexible
- **gRPC**: Microservices, high performance, streaming

**Consistency:**
- **Strong**: Financial, critical data, ACID
- **Eventual**: High availability, global, scale
- **Read-Your-Writes**: User data, good UX

**Replication:**
- **Master-Slave**: Read scaling, simple, backup
- **Master-Master**: High availability, geo-distribution
- **Leader-Follower**: Strong consistency, consensus

**Sharding:**
- **Range**: Time-series, sequential, range queries
- **Hash**: Even distribution, user data, general
- **Directory**: Flexible, complex logic, changing needs

### Common Trade-offs Summary

1. **Consistency vs. Availability**: Strong consistency reduces availability
2. **Latency vs. Throughput**: Lower latency often means lower throughput
3. **Performance vs. Cost**: Higher performance usually costs more
4. **Simplicity vs. Features**: More features increase complexity
5. **Control vs. Management**: More control requires more management
6. **Scale vs. Complexity**: Better scaling often means more complexity

Remember: There's no one-size-fits-all solution. The best technology choice depends on your specific requirements, constraints, and trade-offs you're willing to make.

