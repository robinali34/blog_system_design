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

For detailed information on each technology, refer to the comprehensive guides linked above.

