---
layout: post
title: "System Design Technology List - Quick Reference Guide"
date: 2025-11-29
categories: [Technology, System Design, Quick Reference, Interview Preparation, Technology Comparison]
excerpt: "A quick reference guide to essential technologies used in system design interviews, organized by category with brief descriptions, use cases, and links to comprehensive guides."
---

## Introduction

This post provides a quick reference list of essential technologies used in system design interviews. Each technology is briefly described with key characteristics, common use cases, and links to comprehensive guides for deeper understanding.

Use this as a quick lookup during interview preparation or as a checklist to ensure you're familiar with the key technologies.

---

## Databases

### SQL Databases

#### PostgreSQL
- **Type**: Relational Database (SQL)
- **Characteristics**: ACID compliant, advanced features, JSON support
- **Use Cases**: Complex queries, financial systems, multi-tenant apps
- **Guide**: [PostgreSQL Comprehensive Guide](/blog_system_design/2025/11/09/postgresql-comprehensive-guide/)

#### MySQL
- **Type**: Relational Database (SQL)
- **Characteristics**: Mature, wide adoption, good read performance
- **Use Cases**: Web applications, content management, standard requirements
- **Note**: Similar to PostgreSQL, often interchangeable

### NoSQL Databases

#### Redis
- **Type**: In-Memory Key-Value Store
- **Characteristics**: Sub-millisecond latency, rich data structures, pub/sub
- **Use Cases**: Caching, sessions, real-time features, rate limiting
- **Guides**: 
  - [Redis Comprehensive Guide](/blog_system_design/2025/11/08/redis-comprehensive-guide/)
  - [Redis Practical Guide](/blog_system_design/2025/11/13/redis-guide/)

#### DynamoDB
- **Type**: Managed Key-Value Store (AWS)
- **Characteristics**: Fully managed, auto-scaling, global tables
- **Use Cases**: AWS-native apps, serverless, variable workloads
- **Guide**: [Amazon DynamoDB Comprehensive Guide](/blog_system_design/2025/11/09/amazon-dynamodb-comprehensive-guide/)

#### Cassandra
- **Type**: Column-Family Store
- **Characteristics**: High write throughput, horizontal scaling, eventual consistency
- **Use Cases**: Time-series data, high write loads, global distribution
- **Guide**: [Apache Cassandra Comprehensive Guide](/blog_system_design/2025/11/09/apache-cassandra-comprehensive-guide/)

#### MongoDB
- **Type**: Document Store
- **Characteristics**: Flexible schema, horizontal scaling, JSON-like documents
- **Use Cases**: Content management, real-time analytics, flexible schemas

#### TimescaleDB
- **Type**: Time-Series Database (PostgreSQL extension)
- **Characteristics**: Time-series optimized, SQL interface, compression
- **Use Cases**: IoT data, metrics, time-series analytics
- **Guide**: [TimescaleDB Comprehensive Guide](/blog_system_design/2025/11/09/timescaledb-comprehensive-guide/)

---

## Message Queues & Streaming

#### Apache Kafka
- **Type**: Distributed Streaming Platform
- **Characteristics**: High throughput, durability, real-time processing
- **Use Cases**: Event streaming, event-driven architecture, data pipelines
- **Guide**: [Apache Kafka Guide](/blog_system_design/2025/11/13/apache-kafka-guide/)

#### Amazon SQS
- **Type**: Managed Message Queue (AWS)
- **Characteristics**: Fully managed, auto-scaling, dead letter queues
- **Use Cases**: Decoupled services, async processing, AWS-native apps
- **Guide**: [Amazon SQS Guide](/blog_system_design/2025/11/13/amazon-sqs-guide/)

#### Dead Letter Queue (DLQ)
- **Type**: Error Handling Pattern
- **Characteristics**: Stores failed messages, retry logic, error analysis
- **Use Cases**: Error handling, message retry, failure analysis
- **Guide**: [Dead Letter Queue Guide](/blog_system_design/2025/11/13/dead-letter-queue-guide/)

#### Apache Flink
- **Type**: Stream Processing Framework
- **Characteristics**: Low latency, event time processing, exactly-once semantics
- **Use Cases**: Real-time analytics, event-driven apps, data pipelines
- **Guide**: [Apache Flink Guide](/blog_system_design/2025/11/29/apache-flink-guide/)

---

## Search & Analytics

#### Elasticsearch
- **Type**: Distributed Search and Analytics Engine
- **Characteristics**: Full-text search, real-time, aggregations, horizontal scaling
- **Use Cases**: Search engines, log analytics (ELK), real-time analytics
- **Guide**: [Elasticsearch Guide](/blog_system_design/2025/11/29/elasticsearch-guide/)

---

## Cloud Storage

#### Amazon S3
- **Type**: Object Storage (AWS)
- **Characteristics**: Scalable, durable, versioning, lifecycle policies
- **Use Cases**: File storage, backups, static assets, data lakes
- **Guide**: [Amazon S3 Storage Guide](/blog_system_design/2025/11/13/amazon-s3-storage-guide/)

#### CDN (Content Delivery Network)
- **Type**: Distributed Content Delivery
- **Characteristics**: Low latency, global distribution, caching
- **Use Cases**: Static assets, media delivery, global content distribution

---

## Coordination & Consensus

#### Apache Zookeeper
- **Type**: Distributed Coordination Service
- **Characteristics**: Distributed locks, leader election, configuration management
- **Use Cases**: Coordination, service discovery, distributed locks
- **Guide**: [Apache Zookeeper Guide](/blog_system_design/2025/11/29/apache-zookeeper-guide/)

---

## Theory & Concepts

#### CAP Theorem
- **Type**: Distributed Systems Theory
- **Characteristics**: Consistency, Availability, Partition Tolerance trade-offs
- **Use Cases**: Understanding distributed system trade-offs, system design decisions
- **Guide**: [CAP Theorem Guide](/blog_system_design/2025/11/29/cap-theorem-guide/)

---

## Technology Comparison

For detailed pros/cons comparisons of all technologies, see:
- [Common Technologies in System Design Interviews - Complete Comparison Guide](/blog_system_design/2025/11/09/common-technologies-system-design-interviews/)

---

## Quick Reference by Use Case

### High-Throughput Writes
- **Cassandra**: Excellent write performance, horizontal scaling
- **Kafka**: High-throughput message streaming
- **DynamoDB**: Managed high-throughput key-value store

### Low-Latency Reads
- **Redis**: Sub-millisecond in-memory access
- **CDN**: Edge caching for static content
- **Elasticsearch**: Fast full-text search

### Strong Consistency
- **PostgreSQL**: ACID transactions
- **MySQL**: ACID transactions
- **Zookeeper**: Consensus-based coordination

### Eventual Consistency
- **Cassandra**: Tunable consistency
- **DynamoDB**: Eventual consistency mode
- **MongoDB**: Replica set eventual consistency

### Real-Time Processing
- **Flink**: Stream processing with low latency
- **Kafka**: Real-time event streaming
- **Redis**: Real-time features (pub/sub, streams)

### Search & Analytics
- **Elasticsearch**: Full-text search and aggregations
- **PostgreSQL**: Full-text search capabilities
- **TimescaleDB**: Time-series analytics

### Coordination
- **Zookeeper**: Distributed coordination
- **Redis**: Distributed locks (with Lua)
- **Consensus Algorithms**: Raft, Paxos, ZAB

---

## Technology Trade-off Pair Comparisons

### Database Comparisons

#### PostgreSQL vs MySQL

| Aspect | PostgreSQL | MySQL |
|--------|------------|-------|
| **Complexity** | More features, steeper learning curve | Simpler, easier to start |
| **Performance** | Better for complex queries, analytics | Better for simple read-heavy workloads |
| **Features** | Advanced (JSON, arrays, full-text search) | Standard SQL features |
| **ACID** | Strong ACID compliance | Strong ACID compliance |
| **Use Case** | Complex applications, data warehousing | Web applications, standard requirements |
| **Max Read** | 10K-50K queries/sec | 10K-50K queries/sec |
| **Max Write** | 5K-20K writes/sec | 5K-25K writes/sec |

**Choose PostgreSQL when:**
- Need advanced features (JSON, arrays, custom types)
- Complex queries and analytics
- Data warehousing
- Full-text search requirements

**Choose MySQL when:**
- Simple web applications
- Standard SQL requirements
- Better ecosystem support needed
- Simpler setup and maintenance

---

#### Redis vs Memcached

| Aspect | Redis | Memcached |
|--------|-------|-----------|
| **Data Types** | Rich (strings, lists, sets, sorted sets, hashes) | Simple key-value only |
| **Persistence** | Optional (RDB, AOF) | No persistence |
| **Performance** | 100K-200K ops/sec | 200K-500K ops/sec (faster for simple ops) |
| **Features** | Pub/sub, transactions, Lua scripting | Simple caching only |
| **Memory** | More memory per item (overhead) | Less memory per item |
| **Use Case** | Caching + real-time features | Pure caching |
| **Max Read** | 100K-200K ops/sec | 200K-500K ops/sec |
| **Max Write** | 100K-200K ops/sec | 200K-500K ops/sec |

**Choose Redis when:**
- Need data structures (lists, sets, sorted sets)
- Need persistence
- Need pub/sub or real-time features
- Need transactions or Lua scripting

**Choose Memcached when:**
- Simple key-value caching only
- Maximum performance for GET/SET operations
- No persistence needed
- Minimal memory overhead

---

#### Cassandra vs MongoDB

| Aspect | Cassandra | MongoDB |
|--------|-----------|---------|
| **Data Model** | Column-family (wide rows) | Document (JSON-like) |
| **Consistency** | Tunable (eventual to strong) | Tunable (eventual to strong) |
| **Write Performance** | Optimized for writes (10K-50K/sec/node) | Good writes (5K-20K/sec/node) |
| **Read Performance** | Good reads (5K-25K/sec/node) | Good reads (10K-50K/sec/node) |
| **Query Language** | CQL (SQL-like) | MongoDB Query Language |
| **Schema** | Schema required | Schema flexible |
| **Use Case** | Time-series, high writes, global distribution | Content management, flexible schemas |
| **Scaling** | Linear horizontal scaling | Horizontal scaling with sharding |

**Choose Cassandra when:**
- High write throughput needed
- Time-series data
- Global distribution with low latency
- Predictable query patterns
- Need tunable consistency

**Choose MongoDB when:**
- Flexible schema needed
- Document-based data model
- Rich query capabilities
- Rapid development
- JSON-like data structure

---

#### DynamoDB vs Cassandra

| Aspect | DynamoDB | Cassandra |
|--------|----------|-----------|
| **Management** | Fully managed (AWS) | Self-managed |
| **Setup** | No setup, auto-scaling | Requires cluster setup |
| **Cost** | Pay per request (on-demand) | Infrastructure costs |
| **Scaling** | Automatic scaling | Manual scaling |
| **Consistency** | Eventually consistent (default) | Tunable consistency |
| **Max Read** | 40K RCU (can increase) | 5K-25K reads/sec/node |
| **Max Write** | 40K WCU (can increase) | 10K-50K writes/sec/node |
| **Use Case** | AWS-native, serverless | Self-hosted, high control |

**Choose DynamoDB when:**
- AWS ecosystem
- Serverless applications
- No infrastructure management
- Variable workloads
- Need automatic scaling

**Choose Cassandra when:**
- Self-hosted infrastructure
- Need full control
- Predictable high throughput
- Multi-cloud or on-premises
- Cost optimization at scale

---

### Message Queue Comparisons

#### Kafka vs RabbitMQ

| Aspect | Kafka | RabbitMQ |
|--------|-------|----------|
| **Throughput** | Very high (millions/sec) | High (tens of thousands/sec) |
| **Latency** | Low (milliseconds) | Very low (sub-millisecond) |
| **Durability** | High (disk-based) | Configurable (memory/disk) |
| **Message Ordering** | Per-partition ordering | Per-queue ordering |
| **Message Retention** | Configurable (days/weeks) | Until consumed |
| **Use Case** | Event streaming, data pipelines | Task queues, RPC |
| **Complexity** | More complex setup | Simpler setup |

**Choose Kafka when:**
- High throughput event streaming
- Event sourcing
- Data pipelines
- Long message retention
- Multiple consumers per topic

**Choose RabbitMQ when:**
- Task queues
- RPC patterns
- Complex routing (exchanges, bindings)
- Lower latency requirements
- Simpler setup needed

---

#### Kafka vs Amazon SQS

| Aspect | Kafka | Amazon SQS |
|--------|-------|------------|
| **Management** | Self-managed | Fully managed (AWS) |
| **Throughput** | Very high (millions/sec) | High (unlimited standard, 3K/sec FIFO) |
| **Ordering** | Per-partition | FIFO queues only |
| **Retention** | Configurable (days) | 14 days max |
| **Features** | Event streaming, replay | Simple message queue |
| **Use Case** | Event streaming, data pipelines | Decoupled services, AWS-native |

**Choose Kafka when:**
- Event streaming architecture
- Need message replay
- High throughput requirements
- Multiple consumer groups
- Self-managed infrastructure

**Choose SQS when:**
- AWS ecosystem
- Simple message queuing
- Serverless applications
- No infrastructure management
- Standard queue patterns

---

### Search & Analytics Comparisons

#### Elasticsearch vs PostgreSQL Full-Text Search

| Aspect | Elasticsearch | PostgreSQL Full-Text |
|--------|---------------|---------------------|
| **Search Features** | Advanced (fuzzy, aggregations) | Basic full-text search |
| **Performance** | Optimized for search | Good for simple searches |
| **Scalability** | Horizontal scaling | Vertical scaling |
| **Complexity** | More complex setup | Built-in, simpler |
| **Use Case** | Search engines, log analytics | Simple search in SQL apps |

**Choose Elasticsearch when:**
- Advanced search features needed
- Log analytics (ELK stack)
- Large-scale search
- Real-time search
- Complex aggregations

**Choose PostgreSQL Full-Text when:**
- Simple search requirements
- Already using PostgreSQL
- Don't want additional infrastructure
- Basic full-text search sufficient

---

### Storage Comparisons

#### Amazon S3 vs HDFS

| Aspect | Amazon S3 | HDFS |
|--------|-----------|------|
| **Management** | Fully managed | Self-managed |
| **Access** | REST API, object storage | File system interface |
| **Durability** | 99.999999999% (11 nines) | High (with replication) |
| **Cost** | Pay per storage/request | Infrastructure costs |
| **Use Case** | Cloud-native, backups | Hadoop ecosystem, on-premises |

**Choose S3 when:**
- AWS ecosystem
- Cloud-native applications
- Backup and archival
- No infrastructure management
- REST API access

**Choose HDFS when:**
- Hadoop ecosystem
- On-premises infrastructure
- File system interface needed
- Cost optimization at scale
- Full control required

---

### Coordination Comparisons

#### Zookeeper vs etcd vs Consul

| Aspect | Zookeeper | etcd | Consul |
|--------|-----------|------|--------|
| **Consensus** | ZAB protocol | Raft | Raft |
| **API** | Custom protocol | REST/gRPC | REST/gRPC |
| **Service Discovery** | Manual | Manual | Built-in |
| **Health Checks** | Manual | Manual | Built-in |
| **Use Case** | Kafka, Hadoop | Kubernetes, distributed systems | Service mesh, microservices |

**Choose Zookeeper when:**
- Kafka or Hadoop ecosystem
- Established coordination needs
- Custom protocol acceptable

**Choose etcd when:**
- Kubernetes ecosystem
- Need REST/gRPC API
- Simple key-value store
- Distributed systems coordination

**Choose Consul when:**
- Service discovery needed
- Health checks required
- Service mesh integration
- Microservices architecture

---

### Time-Series Database Comparisons

#### InfluxDB vs TimescaleDB

| Aspect | InfluxDB | TimescaleDB |
|--------|----------|-------------|
| **Base** | Standalone time-series DB | PostgreSQL extension |
| **Query Language** | InfluxQL, Flux | SQL (PostgreSQL) |
| **Write Performance** | 100K-500K points/sec | 10K-50K inserts/sec |
| **Read Performance** | 10K-50K queries/sec | 5K-25K queries/sec |
| **SQL Support** | Limited (InfluxQL) | Full SQL support |
| **Ecosystem** | Time-series focused | PostgreSQL ecosystem |
| **Use Case** | Pure time-series, IoT | Time-series with SQL needs |

**Choose InfluxDB when:**
- Pure time-series workloads
- High write throughput needed
- Time-series specific features
- Don't need SQL

**Choose TimescaleDB when:**
- Need SQL interface
- Already using PostgreSQL
- Want PostgreSQL ecosystem
- Need relational queries with time-series

---

### Stream Processing Comparisons

#### Apache Flink vs Apache Spark

| Aspect | Apache Flink | Apache Spark |
|--------|--------------|--------------|
| **Processing Model** | True stream processing | Micro-batch processing |
| **Latency** | Low (milliseconds) | Higher (seconds) |
| **Throughput** | High | Very high |
| **State Management** | Built-in stateful processing | External state stores |
| **Use Case** | Real-time stream processing | Batch + stream processing |
| **Complexity** | More complex | Moderate |

**Choose Flink when:**
- True real-time processing needed
- Low latency requirements
- Event time processing
- Stateful stream processing

**Choose Spark when:**
- Batch + stream processing
- Higher throughput needed
- Existing Spark ecosystem
- Micro-batch acceptable

---

#### Apache Kafka vs Apache Pulsar

| Aspect | Kafka | Pulsar |
|--------|-------|--------|
| **Architecture** | Partition-based | Topic-based with segments |
| **Multi-tenancy** | Limited | Built-in |
| **Geo-replication** | Manual setup | Built-in |
| **Message Model** | Consumer groups | Subscriptions (exclusive, shared, failover) |
| **Storage** | Local disk | BookKeeper (separate storage) |
| **Use Case** | Event streaming, data pipelines | Multi-tenant, geo-distributed |

**Choose Kafka when:**
- Event streaming
- Established ecosystem
- Simple deployment
- Standard use cases

**Choose Pulsar when:**
- Multi-tenant architecture
- Geo-replication needed
- Need multiple subscription types
- Separate compute and storage

---

### API/Communication Comparisons

#### REST vs GraphQL vs gRPC

| Aspect | REST | GraphQL | gRPC |
|--------|------|---------|------|
| **Protocol** | HTTP/HTTPS | HTTP/HTTPS | HTTP/2 |
| **Data Format** | JSON, XML | JSON | Protocol Buffers |
| **Query Flexibility** | Fixed endpoints | Flexible queries | Fixed methods |
| **Performance** | Good | Good | Excellent (binary) |
| **Caching** | Easy (HTTP caching) | Limited | Limited |
| **Use Case** | Standard APIs | Flexible data fetching | Microservices, high performance |

**Choose REST when:**
- Standard web APIs
- Need HTTP caching
- Simple integration
- Browser clients

**Choose GraphQL when:**
- Flexible data fetching
- Mobile apps with limited bandwidth
- Multiple data sources
- Over-fetching is a problem

**Choose gRPC when:**
- Microservices communication
- High performance needed
- Strong typing required
- Internal services

---

#### WebSocket vs Server-Sent Events (SSE) vs Long Polling

| Aspect | WebSocket | SSE | Long Polling |
|--------|-----------|-----|--------------|
| **Direction** | Bidirectional | Server → Client | Bidirectional (via requests) |
| **Protocol** | WebSocket | HTTP | HTTP |
| **Overhead** | Low (persistent) | Low | High (repeated connections) |
| **Browser Support** | Good | Good | Universal |
| **Use Case** | Real-time chat, gaming | Live updates, notifications | Simple real-time needs |

**Choose WebSocket when:**
- Bidirectional communication needed
- Real-time chat, gaming
- Low latency required
- Frequent message exchange

**Choose SSE when:**
- Server-to-client only
- Live updates, notifications
- Simpler than WebSocket
- One-way data flow

**Choose Long Polling when:**
- Simple real-time needs
- Limited browser support acceptable
- Infrequent updates
- Fallback option

---

### Load Balancer Comparisons

#### NGINX vs HAProxy vs AWS ELB

| Aspect | NGINX | HAProxy | AWS ELB |
|--------|-------|---------|---------|
| **Type** | Web server + reverse proxy | Load balancer | Managed load balancer |
| **Management** | Self-managed | Self-managed | Fully managed (AWS) |
| **Features** | Web server, caching, SSL | Advanced load balancing | Auto-scaling, health checks |
| **Performance** | Very high | Very high | High (managed) |
| **Use Case** | Web server + load balancing | Advanced load balancing | AWS-native, managed service |

**Choose NGINX when:**
- Need web server + load balancer
- Static file serving
- Reverse proxy with caching
- Self-managed infrastructure

**Choose HAProxy when:**
- Advanced load balancing features
- TCP/HTTP load balancing
- High performance requirements
- Complex routing rules

**Choose AWS ELB when:**
- AWS ecosystem
- Managed service needed
- Auto-scaling required
- No infrastructure management

---

### Container & Orchestration Comparisons

#### Docker vs Containerd vs Podman

| Aspect | Docker | Containerd | Podman |
|--------|--------|------------|--------|
| **Daemon** | Docker daemon | Containerd daemon | No daemon (rootless) |
| **Orchestration** | Docker Swarm | Kubernetes runtime | Kubernetes compatible |
| **Rootless** | Limited | Yes | Yes (default) |
| **Ecosystem** | Largest | Growing | Growing |
| **Use Case** | Development, simple deployments | Kubernetes runtime | Rootless containers |

**Choose Docker when:**
- Development environment
- Simple containerization
- Largest ecosystem
- Standard tooling

**Choose Containerd when:**
- Kubernetes runtime
- Lightweight runtime
- Production Kubernetes

**Choose Podman when:**
- Rootless containers needed
- No daemon required
- Security-focused

---

#### Kubernetes vs Docker Swarm

| Aspect | Kubernetes | Docker Swarm |
|--------|------------|-------------|
| **Complexity** | High | Low |
| **Features** | Extensive | Basic |
| **Scalability** | Very high | High |
| **Ecosystem** | Largest | Limited |
| **Learning Curve** | Steep | Gentle |
| **Use Case** | Production, complex apps | Simple orchestration |

**Choose Kubernetes when:**
- Production workloads
- Complex applications
- Need extensive features
- Large scale deployments

**Choose Docker Swarm when:**
- Simple orchestration
- Docker-native
- Quick setup
- Small to medium scale

---

### Monitoring & Observability Comparisons

#### Prometheus vs Grafana vs Datadog

| Aspect | Prometheus | Grafana | Datadog |
|--------|------------|---------|---------|
| **Type** | Metrics collection | Visualization | Full observability platform |
| **Cost** | Open source | Open source | Commercial (SaaS) |
| **Setup** | Self-managed | Self-managed | Managed service |
| **Features** | Metrics, alerting | Dashboards, visualization | Metrics, logs, traces, APM |
| **Use Case** | Metrics collection | Visualization | Full observability |

**Choose Prometheus when:**
- Metrics collection
- Self-managed solution
- Open source needed
- Time-series metrics

**Choose Grafana when:**
- Visualization needed
- Multiple data sources
- Dashboard creation
- Works with Prometheus

**Choose Datadog when:**
- Full observability platform
- Managed service needed
- Metrics + logs + traces
- Commercial support

---

### Search Engine Comparisons

#### Elasticsearch vs Apache Solr

| Aspect | Elasticsearch | Apache Solr |
|--------|---------------|-------------|
| **Architecture** | Distributed by default | Can be standalone or distributed |
| **Setup** | Simpler | More configuration |
| **JSON API** | Native | REST API |
| **Real-time** | Near real-time | Near real-time |
| **Ecosystem** | ELK stack | SolrCloud |
| **Use Case** | Log analytics, search | Enterprise search |

**Choose Elasticsearch when:**
- ELK stack (Elasticsearch, Logstash, Kibana)
- Log analytics
- Real-time search
- Simpler setup

**Choose Solr when:**
- Enterprise search
- More configuration control
- Existing Solr infrastructure
- Advanced search features

---

### Database Sharding Comparisons

#### Horizontal Sharding vs Vertical Sharding

| Aspect | Horizontal Sharding | Vertical Sharding |
|--------|---------------------|-------------------|
| **Method** | Split by rows (partition key) | Split by columns (tables) |
| **Scalability** | Linear scaling | Limited by single table size |
| **Complexity** | High (cross-shard queries) | Lower (same database) |
| **Use Case** | Large tables, high throughput | Different access patterns |
| **Joins** | Difficult across shards | Easier (same database) |

**Choose Horizontal Sharding when:**
- Large tables
- High write throughput
- Can partition by key
- Linear scaling needed

**Choose Vertical Sharding when:**
- Different access patterns
- Different tables for different features
- Easier joins needed
- Simpler architecture

---

### Caching Strategy Comparisons

#### Cache-Aside vs Write-Through vs Write-Back

| Aspect | Cache-Aside | Write-Through | Write-Back |
|--------|-------------|---------------|------------|
| **Write Path** | Write to DB, invalidate cache | Write to cache + DB | Write to cache, async to DB |
| **Read Path** | Check cache, fallback to DB | Read from cache | Read from cache |
| **Consistency** | Eventual (until invalidation) | Strong (always consistent) | Eventual (async writes) |
| **Performance** | Good | Slower writes | Fastest writes |
| **Data Loss Risk** | Low | Low | Higher (cache failure) |
| **Use Case** | General purpose | Critical data | High write throughput |

**Choose Cache-Aside when:**
- General purpose caching
- Read-heavy workloads
- Simple implementation
- Can tolerate eventual consistency

**Choose Write-Through when:**
- Strong consistency needed
- Critical data
- Write performance acceptable
- Cache must match database

**Choose Write-Back when:**
- High write throughput needed
- Can tolerate data loss risk
- Async writes acceptable
- Performance critical

---

### Database Replication Comparisons

#### Master-Slave vs Master-Master vs Multi-Master

| Aspect | Master-Slave | Master-Master | Multi-Master |
|--------|--------------|---------------|--------------|
| **Write Nodes** | 1 (master) | 2 (both masters) | Multiple |
| **Read Scaling** | Linear (with slaves) | Linear (both masters) | Linear (all nodes) |
| **Write Scaling** | Limited (single master) | Limited (2 masters) | Linear (all nodes) |
| **Conflict Resolution** | None needed | Manual | Automatic/manual |
| **Complexity** | Low | Medium | High |
| **Use Case** | Read scaling | Geographic distribution | High availability |

**Choose Master-Slave when:**
- Read scaling needed
- Simple setup
- Single write location
- Standard replication

**Choose Master-Master when:**
- Geographic distribution
- Two write locations
- Manual conflict resolution
- Active-active setup

**Choose Multi-Master when:**
- High availability critical
- Multiple write locations
- Automatic conflict resolution
- Complex distributed system

---

### Consistency Model Comparisons

#### Strong Consistency vs Eventual Consistency vs Causal Consistency

| Aspect | Strong Consistency | Eventual Consistency | Causal Consistency |
|--------|-------------------|---------------------|-------------------|
| **Read Guarantee** | Always latest | May be stale | Causally related reads consistent |
| **Latency** | Higher (wait for replication) | Lower | Medium |
| **Availability** | Lower (may reject writes) | Higher | Higher |
| **Use Case** | Financial systems, critical data | Social media, CDNs | Distributed systems, chat |
| **Complexity** | Lower | Lower | Higher |

**Choose Strong Consistency when:**
- Financial transactions
- Critical data integrity
- ACID requirements
- Can tolerate higher latency

**Choose Eventual Consistency when:**
- High availability needed
- Can tolerate stale reads
- Global distribution
- High throughput

**Choose Causal Consistency when:**
- Need causal ordering
- Distributed systems
- Chat applications
- More than eventual, less than strong

---

### Data Partitioning Comparisons

#### Range Partitioning vs Hash Partitioning vs Directory Partitioning

| Aspect | Range Partitioning | Hash Partitioning | Directory Partitioning |
|--------|-------------------|-------------------|------------------------|
| **Method** | Partition by value ranges | Hash function on key | Lookup table |
| **Hotspots** | Possible (uneven distribution) | Even distribution | Configurable |
| **Query Performance** | Good for range queries | Poor for range queries | Good for all queries |
| **Rebalancing** | Complex | Automatic | Manual |
| **Use Case** | Time-series, ordered data | Even distribution | Custom partitioning |

**Choose Range Partitioning when:**
- Time-series data
- Range queries common
- Ordered data
- Can manage hotspots

**Choose Hash Partitioning when:**
- Even distribution needed
- No range queries
- Automatic rebalancing
- Simple implementation

**Choose Directory Partitioning when:**
- Custom partitioning logic
- Need flexibility
- Can manage lookup table
- Complex requirements

---

### Index Strategy Comparisons

#### B-Tree Index vs Hash Index vs Bitmap Index

| Aspect | B-Tree Index | Hash Index | Bitmap Index |
|--------|--------------|------------|--------------|
| **Query Types** | Range, equality | Equality only | Equality, low cardinality |
| **Performance** | Good (O(log n)) | Excellent (O(1)) | Excellent (bitwise ops) |
| **Storage** | Moderate | Low | High (for high cardinality) |
| **Use Case** | General purpose | Exact match queries | Low cardinality columns |
| **Updates** | Efficient | Efficient | Less efficient |

**Choose B-Tree Index when:**
- Range queries needed
- General purpose
- Ordered data
- Standard use case

**Choose Hash Index when:**
- Exact match queries only
- No range queries
- Maximum performance needed
- Memory-based

**Choose Bitmap Index when:**
- Low cardinality columns
- Boolean queries
- Data warehousing
- Aggregations

---

### Message Delivery Comparisons

#### At-Least-Once vs At-Most-Once vs Exactly-Once

| Aspect | At-Least-Once | At-Most-Once | Exactly-Once |
|--------|---------------|--------------|--------------|
| **Guarantee** | No message loss (may duplicate) | No duplicates (may lose) | No loss, no duplicates |
| **Performance** | Highest | High | Lower (overhead) |
| **Complexity** | Low | Low | High (idempotency) |
| **Use Case** | Logging, analytics | Non-critical data | Financial transactions |
| **Implementation** | Simple | Simple | Complex (deduplication) |

**Choose At-Least-Once when:**
- Duplicates acceptable
- Message loss unacceptable
- Logging, analytics
- Simple implementation

**Choose At-Most-Once when:**
- Duplicates unacceptable
- Message loss acceptable
- Non-critical data
- Simple implementation

**Choose Exactly-Once when:**
- Financial transactions
- Critical operations
- Need idempotency
- Can handle complexity

---

## Technology Selection Guide

### Choose Based on Requirements

**Need ACID Transactions?**
→ PostgreSQL, MySQL

**Need High Write Throughput?**
→ Cassandra, Kafka

**Need Low-Latency Reads?**
→ Redis, CDN

**Need Full-Text Search?**
→ Elasticsearch

**Need Stream Processing?**
→ Flink, Kafka

**Need Distributed Coordination?**
→ Zookeeper

**Need Managed Service?**
→ DynamoDB, SQS, S3 (AWS)

**Need Time-Series Data?**
→ TimescaleDB, Cassandra

---

## Summary

This quick reference provides an overview of essential technologies for system design interviews. Each technology has specific strengths and use cases:

**Key Takeaways:**
- **Databases**: Choose based on consistency, scalability, and query patterns
- **Message Queues**: Choose based on throughput, durability, and features
- **Search**: Elasticsearch for full-text search and analytics
- **Streaming**: Flink for real-time stream processing
- **Coordination**: Zookeeper for distributed coordination
- **Theory**: CAP Theorem for understanding trade-offs
- **Trade-offs**: Every technology has strengths and weaknesses - choose based on your specific requirements
- **Patterns**: Caching strategies, replication models, partitioning methods, and consistency models all have trade-offs
- **Architecture**: Consider scalability, consistency, availability, and complexity when choosing technologies
- **Comparisons**: Use pair comparisons to understand when to choose one technology over another

For detailed information on each technology, refer to the comprehensive guides linked above.

