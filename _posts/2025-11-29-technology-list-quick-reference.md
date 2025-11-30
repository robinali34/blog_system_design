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
- **Guide**: [Apache Flink Guide](/blog_system_design/2025/12/29/apache-flink-guide/)

---

## Search & Analytics

#### Elasticsearch
- **Type**: Distributed Search and Analytics Engine
- **Characteristics**: Full-text search, real-time, aggregations, horizontal scaling
- **Use Cases**: Search engines, log analytics (ELK), real-time analytics
- **Guide**: [Elasticsearch Guide](/blog_system_design/2025/12/29/elasticsearch-guide/)

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
- **Guide**: [Apache Zookeeper Guide](/blog_system_design/2025/12/29/apache-zookeeper-guide/)

---

## Theory & Concepts

#### CAP Theorem
- **Type**: Distributed Systems Theory
- **Characteristics**: Consistency, Availability, Partition Tolerance trade-offs
- **Use Cases**: Understanding distributed system trade-offs, system design decisions
- **Guide**: [CAP Theorem Guide](/blog_system_design/2025/12/29/cap-theorem-guide/)

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

For detailed information on each technology, refer to the comprehensive guides linked above.

