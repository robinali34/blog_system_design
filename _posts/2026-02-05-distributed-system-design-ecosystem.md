---
layout: post
title: "Distributed System Design Ecosystem"
date: 2026-02-05 12:00:00 -0000
categories: interview-preparation system-design distributed-systems reference
tags: distributed-systems system-design ecosystem consistency replication partitioning messaging storage
excerpt: "Reference guide to common categories, components, and usage patterns in distributed system design—consistency, replication, partitioning, messaging, storage, coordination, and more."
---

# Distributed System Design Ecosystem

A reference guide to **common categories** in distributed system design, the **typical components** in each category, and their **common usage**. Use this as a mental checklist when tackling system design interviews or architecting real systems.

---

## Component Reference by Technology

Systematic breakdown by **category**, **representative technologies**, and **typical usage**. Use these tables when you need to name concrete systems (e.g. “Kafka for event streaming”) rather than abstract concepts.

### 1. Messaging & Event Streaming

| Category | Examples | Common Usage |
|----------|----------|--------------|
| **Message Queue / Broker** | RabbitMQ, ActiveMQ | Decouple services, handle asynchronous tasks, reliable delivery. |
| **Distributed Log / Event Streaming** | Kafka, Pulsar, Redpanda | High-throughput event streaming, log aggregation, real-time analytics, pub-sub communication. |
| **Pub/Sub Systems** | NATS, Google Pub/Sub | Broadcast events to multiple consumers, event-driven microservices. |

### 2. Databases

| Category | Examples | Common Usage |
|----------|----------|--------------|
| **Relational DB** | MySQL, PostgreSQL, MariaDB | Strong consistency, structured data, transactions. |
| **NoSQL Key-Value Store** | Redis, DynamoDB, Riak | Low-latency access, caching, session storage, high throughput. |
| **Document Store** | MongoDB, Couchbase | Flexible schema, JSON-style data, content storage. |
| **Wide Column Store** | Cassandra, HBase | Large-scale writes, time-series data, distributed tables. |
| **Graph DB** | Neo4j, JanusGraph | Relationships-heavy data, social networks, recommendation engines. |

### 3. Caching & In-Memory Systems

| Category | Examples | Common Usage |
|----------|----------|--------------|
| **In-Memory Cache** | Redis, Memcached | Reduce DB load, fast data access, session storage. |
| **Distributed Cache** | Hazelcast, Ignite | Shared cache across nodes in a cluster, scale horizontally. |

### 4. Storage Systems

| Category | Examples | Common Usage |
|----------|----------|--------------|
| **Object Storage** | AWS S3, MinIO | Store unstructured data like images, videos, logs. |
| **Distributed File System** | HDFS, Ceph | Large-scale batch processing, big data analytics, high durability. |
| **Block Storage** | EBS, OpenStack Cinder | Persistent storage for VMs and containers. |

### 5. Coordination & Configuration

| Category | Examples | Common Usage |
|----------|----------|--------------|
| **Distributed Coordination** | Zookeeper, Consul | Leader election, service discovery, distributed locks. |
| **Configuration Management** | etcd, Consul | Store cluster metadata, maintain consistent config across nodes. |

### 6. Search & Analytics

| Category | Examples | Common Usage |
|----------|----------|--------------|
| **Search Engine** | Elasticsearch, Solr | Full-text search, log analytics, metrics search. |
| **Analytics / OLAP** | ClickHouse, Druid | Real-time analytics, aggregate queries on big data. |

### 7. API & Gateway Layers

| Category | Examples | Common Usage |
|----------|----------|--------------|
| **API Gateway** | Kong, NGINX, Envoy | Routing, authentication, rate-limiting, service entry point. |
| **Load Balancer** | HAProxy, NGINX, AWS ELB | Distribute traffic across services, high availability. |

### 8. Stream Processing / Computation

| Category | Examples | Common Usage |
|----------|----------|--------------|
| **Stream Processing** | Apache Flink, Kafka Streams, Spark Streaming | Real-time transformations, aggregations on events. |
| **Batch Processing** | Apache Spark, Hadoop MapReduce | Large-scale offline computations. |

### 9. Monitoring & Observability

| Category | Examples | Common Usage |
|----------|----------|--------------|
| **Metrics & Monitoring** | Prometheus, Grafana | Track service health, alerting, system metrics. |
| **Tracing / Logging** | Jaeger, ELK stack | Debug distributed requests, trace latency, centralized logging. |

### 10. Distributed Infrastructure

| Category | Examples | Common Usage |
|----------|----------|--------------|
| **Service Mesh** | Istio, Linkerd | Traffic management, observability, secure communication between services. |
| **Container Orchestration** | Kubernetes, Nomad | Deploy, scale, and manage containers in clusters. |
| **Distributed Task Scheduler** | Airflow, Celery | Manage workflows, schedule jobs across nodes. |

**Quick takeaways:**
- **Messaging & Event Streaming** → decouple services, real-time communication  
- **Databases & Storage** → persistence, scale, reliability  
- **Coordination & Config** → consistency, leader election, cluster metadata  
- **Monitoring & Observability** → track, debug, alert  
- **Compute Layers** → process data (real-time or batch)

---

## Conceptual Categories (Consistency, Partitioning, etc.)

The sections below organize the same ecosystem by **concepts** (consistency, partitioning, fault tolerance) rather than by technology. Use them to reason about trade-offs and to answer “how” questions (e.g. how do you shard? how do you handle failures?).

---

## 1. Consistency & Replication

| Category | Common Items | Common Usage |
|----------|--------------|--------------|
| **Consistency models** | Strong (linearizable), eventual, causal, read-your-writes, session | Choose by read/write latency and correctness needs; strong for financial/leaderboard, eventual for feeds/social. |
| **Replication topologies** | Leader–follower (primary–replica), multi-leader, leaderless (Dynamo-style) | Leader–follower for simple strong consistency; multi-leader for multi-region; leaderless for availability. |
| **Reconciliation** | Quorum (R/W), vector clocks, version vectors, last-write-wins (LWW), CRDTs | Quorum for consensus; vector clocks for ordering; LWW for simple conflict resolution; CRDTs for conflict-free merges. |
| **Sync vs async** | Synchronous replication, asynchronous replication | Sync for durability/consistency; async for lower latency and higher throughput at cost of staleness. |

**When to mention:** Replication strategy, CAP trade-offs, multi-datacenter design, conflict resolution.

---

## 2. Partitioning & Sharding

| Category | Common Items | Common Usage |
|----------|--------------|--------------|
| **Partitioning strategies** | Hash-based, range-based, directory-based, hybrid | Hash for even load; range for range queries and sorting; directory for flexible rebalancing. |
| **Consistent hashing** | Virtual nodes, bounded load, rendezvous hashing | Minimize reassignment on add/remove nodes; used in caches, CDNs, distributed storage. |
| **Partition key design** | Single key, composite key, key + sort key | Avoid hot partitions; support access patterns (e.g. user_id + timestamp). |
| **Rebalancing** | Full scan, range move, double-write during migration | Minimize data movement and downtime; often combined with directory or consistent hashing. |

**When to mention:** Scaling storage or compute, hot spots, data locality, schema design.

---

## 3. Messaging & Communication

| Category | Common Items | Common Usage |
|----------|--------------|--------------|
| **Message queues** | Kafka, RabbitMQ, SQS, Azure Service Bus, Redis Streams | Decouple producers/consumers; buffer spikes; at-least-once or exactly-once delivery. |
| **Pub/sub** | Kafka topics, Google Pub/Sub, AWS SNS/SQS, Redis Pub/Sub | Fan-out to many subscribers; event-driven and real-time pipelines. |
| **Request/response** | REST, gRPC, GraphQL, Thrift | Service-to-service and client–server; gRPC for performance, REST for simplicity. |
| **Delivery guarantees** | At-most-once, at-least-once, exactly-once | Trade off simplicity vs duplicates vs implementation cost (ids, idempotency, transactions). |
| **Patterns** | Request–reply, fan-out, fan-in, priority queue, dead-letter queue (DLQ) | Model workflows, retries, and failure handling. |

**When to mention:** Async processing, event sourcing, microservices communication, backpressure.

---

## 4. Coordination & Consensus

| Category | Common Items | Common Usage |
|----------|--------------|--------------|
| **Consensus algorithms** | Paxos, Raft, Zab (ZooKeeper), Viewstamped Replication | Replicated logs, cluster metadata, configuration. |
| **Coordination services** | ZooKeeper, etcd, Consul | Leader election, distributed locks, service discovery, config storage. |
| **Distributed locks** | Redis SET NX, ZooKeeper sequences, database advisory locks | Mutual exclusion across processes; use with TTL or heartbeats. |
| **Leader election** | Bully, ring, Raft leader | Single writer or coordinator per partition/shard. |
| **Discovery** | etcd, Consul, Eureka, DNS, K8s Services | Find healthy instances; support load balancing and failover. |

**When to mention:** Multi-node coordination, strong consistency, avoiding split-brain, deployment and config.

---

## 5. Storage

| Category | Common Items | Common Usage |
|----------|--------------|--------------|
| **Relational DB** | PostgreSQL, MySQL, Aurora, Spanner | Transactions, joins, strong consistency; vertical + read replicas + sharding for scale. |
| **Key–value** | Redis, DynamoDB, Riak, etcd | Caching, session store, simple CRUD by key; low latency. |
| **Document** | MongoDB, Couchbase, Firestore | Flexible schema, nested documents, query by fields. |
| **Wide-column** | Cassandra, HBase, Bigtable | High write throughput, time-series, log data; tunable consistency. |
| **Search** | Elasticsearch, OpenSearch, Solr | Full-text search, aggregations, log analytics. |
| **Object/blob** | S3, GCS, Azure Blob, MinIO | Large binaries, backups, data lakes; eventual consistency. |
| **Caching** | Redis, Memcached, Varnish, CDN | Reduce DB load and latency; cache-aside, write-through, write-behind. |
| **CDN** | CloudFront, Cloudflare, Akamai | Static assets, API caching at edge; lower latency and origin load. |

**When to mention:** Data model, access patterns, durability, latency, cost.

---

## 6. Load Balancing & Routing

| Category | Common Items | Common Usage |
|----------|--------------|--------------|
| **LB algorithms** | Round-robin, least connections, weighted, IP hash, consistent hash | Spread traffic; avoid overloaded or unhealthy nodes. |
| **Layers** | DNS, L4 (TCP/UDP), L7 (HTTP/gRPC) | DNS for geo/failover; L4 for raw throughput; L7 for routing by path/header. |
| **Components** | Nginx, HAProxy, Envoy, AWS ALB/NLB, cloud LB | Ingress, internal routing, health checks, TLS termination. |
| **Service mesh** | Istio, Linkerd, Consul Connect | mTLS, retries, timeouts, observability across services. |

**When to mention:** High availability, scaling stateless services, canary/blue-green.

---

## 7. Fault Tolerance & Resilience

| Category | Common Items | Common Usage |
|----------|--------------|--------------|
| **Retry** | Exponential backoff, jitter, max attempts | Transient failures; avoid thundering herd. |
| **Timeout** | Connection, read, total request | Prevent hanging calls; propagate and set at each layer. |
| **Circuit breaker** | Open / half-open / closed | Stop calling failing dependencies; fail fast and recover. |
| **Bulkhead** | Thread pools, connection limits per dependency | Isolate failures; one bad dependency doesn’t starve others. |
| **Idempotency** | Idempotency keys, dedupe by request ID | Safe retries; exactly-once semantics where needed. |
| **Graceful degradation** | Fallbacks, cached/stale data, feature flags | Maintain partial service when dependencies fail. |
| **Health checks** | Liveness, readiness, dependency checks | LB and orchestrator use these to route traffic and restart. |

**When to mention:** Reliability, cascading failures, SLA, client experience under failure.

---

## 8. Security & Access Control

| Category | Common Items | Common Usage |
|----------|--------------|--------------|
| **Authentication** | JWT, OAuth2, OIDC, API keys, mTLS | Identify users and services; SSO and delegated access. |
| **Authorization** | RBAC, ABAC, ACLs, policy engines | Who can do what on which resource. |
| **Rate limiting** | Token bucket, leaky bucket, sliding window, per-user/per-IP | Protect APIs and backends; fairness and cost control. |
| **Encryption** | TLS in transit, encryption at rest (KMS), field-level | Confidentiality and compliance. |
| **Secrets** | Vault, K8s Secrets, managed secret managers | Store and rotate DB credentials, API keys. |

**When to mention:** Multi-tenant systems, public APIs, compliance, zero-trust.

---

## 9. Observability & Operations

| Category | Common Items | Common Usage |
|----------|--------------|--------------|
| **Logging** | Structured logs (JSON), log levels, correlation IDs | Debugging, audit, tracing requests across services. |
| **Metrics** | Counters, gauges, histograms, percentiles (p50/p99) | Latency, throughput, error rate; SLOs and alerting. |
| **Tracing** | OpenTelemetry, Jaeger, Zipkin, X-Ray | Distributed trace IDs; find bottlenecks and failure paths. |
| **Alerting** | PagerDuty, Opsgenie, Slack, on-call runbooks | React to SLO breaches and incidents. |
| **Dashboards** | Grafana, Datadog, CloudWatch | Visualize metrics and logs; capacity and trend analysis. |

**When to mention:** Debugging at scale, SLO/SLA, incident response, capacity planning.

---

## 10. Compute & Scheduling

| Category | Common Items | Common Usage |
|----------|--------------|--------------|
| **Job queues** | Celery, Sidekiq, K8s Jobs, Lambda, Step Functions | Async and batch jobs; retries and backoff. |
| **Orchestration** | Kubernetes, Mesos, Nomad, ECS | Deploy and scale containers; placement and resource limits. |
| **Workflow** | Temporal, Cadence, Airflow, Prefect | Durable workflows, human-in-the-loop, data pipelines. |
| **Serverless** | Lambda, Cloud Functions, Knative | Event-driven, scale-to-zero; short, stateless tasks. |

**When to mention:** Background processing, batch vs real-time, resource and cost optimization.

---

## How to Use This in an Interview

1. **Clarify requirements** — Then map them to categories above (e.g. “strong consistency” → Consistency & Replication; “10M QPS” → Partitioning, Load Balancing, Storage).
2. **Name categories first** — e.g. “We need replication, partitioning, and a message queue,” then drill into specific items.
3. **Justify choices** — For each item, briefly say why (e.g. “Eventual consistency because reads can be stale and we need low latency”).
4. **Trade-offs** — Refer back to categories when discussing trade-offs (e.g. consistency vs availability, sync vs async replication).

---

## Quick Reference: Category → Typical Questions

| Category | Interview angles |
|----------|------------------|
| Consistency & Replication | How do you replicate across regions? How do you resolve conflicts? |
| Partitioning | How do you shard? How do you avoid hot partitions? |
| Messaging | How do you decouple services? How do you guarantee delivery? |
| Coordination | How do you elect a leader? How do you implement a distributed lock? |
| Storage | Why this DB? How do you scale reads/writes? |
| Load Balancing | How do you scale out? How do you do canary releases? |
| Fault Tolerance | How do you handle failures? How do you make retries safe? |
| Security | How do you authenticate/authorize? How do you rate limit? |
| Observability | How do you debug in production? How do you define SLOs? |
| Compute | How do you run background jobs? How do you orchestrate workflows? |

---

## System Scale Analysis

Concrete **throughput**, **capacity**, and **scale** numbers help you sanity-check designs and answer “how big can this get?” in interviews. Numbers below are indicative (hardware, config, and workload vary); use them as order-of-magnitude references.

### Messaging & Event Streaming

| System | Typical scale (setup) | Notes |
|--------|------------------------|--------|
| **Kafka** | **~100K–600K+ msg/s** per broker; **~100–600+ MB/s** write throughput on a 3-broker cluster (e.g. 8 vCPU, NVMe, tuned producer) | Single broker: ~25–95+ MB/s with batching/compression. Cluster scales linearly with brokers. p99 latency ~5 ms at ~200 MB/s. Tuning: `batch.size`, `linger.ms`, `compression.type=lz4`, `acks=1` for throughput. |
| **RabbitMQ** | **~10K–50K msg/s** per node (small messages); lower for large payloads | Throughput depends on message size, persistence (disk vs RAM), and cluster size. Use for moderate throughput and flexible routing. |
| **Google Pub/Sub** | **~1M msg/s** per topic (managed; scales with partitions and subscribers) | Fully managed; throughput and retention are service limits, not single-machine limits. |

### Databases

| System | Typical scale (setup) | Notes |
|--------|------------------------|--------|
| **PostgreSQL** | **No hard DB size limit**; single table up to **~32 TB** (default 8 KB block size); single field up to **1 GB** | Practical limit is disk and performance. Single instance: often **hundreds of GB–few TB** before sharding/read replicas. Extensions (e.g. Citus) add sharding for larger scale. |
| **MySQL** | Single table **~64 TB** (InnoDB); practical single-instance **~1–10 TB** depending on workload | Scale via read replicas, then sharding or Vitess/ProxySQL for very large datasets. |
| **Redis (single node)** | **~100K–1.2M ops/s** per node (simple GET/SET); **~1M+ RPS** on larger instances (e.g. r7g.4xlarge) | Cluster: linear scaling (e.g. **~10M ops/s** on 6 nodes, **~200M ops/s** on 40 nodes with Redis Enterprise). Sub-ms latency typical. |
| **DynamoDB** | **~3K–10K WCU** per partition (write); **~3K–10K RCU** per partition (read); auto-scaling and partition splitting | Throughput and storage scale with partitions; no fixed “max DB size”—pay per request and storage. |
| **Cassandra** | **Linear write scaling** with nodes; **~10K–30K+ writes/s per node** depending on schema and hardware | No single “max size”; cluster size and replication factor determine capacity. Proper data modeling and vnodes (e.g. 4–16 tokens per node) matter. |
| **MongoDB** | Single replica set **~TB** range; sharded clusters **100+ TB** with many shards | Throughput scales with shards and read preference (primary vs secondaries). |

### Caching & In-Memory

| System | Typical scale (setup) | Notes |
|--------|------------------------|--------|
| **Redis** | See Databases above; **~100K–1M+ ops/s** per node, sub-ms latency | Same product used as cache and as KV store; cluster mode for horizontal scale. |
| **Memcached** | **~100K–500K+ ops/s** per node (GET-heavy) | Simpler than Redis; multi-threaded; no persistence. Scale by adding nodes. |

### Storage Systems

| System | Typical scale (setup) | Notes |
|--------|------------------------|--------|
| **AWS S3** | **Unlimited** objects and total size; **3,500 PUT / 5,500 GET per second per prefix** (request rate best practices) | Scale by prefix design (shard prefixes for higher aggregate throughput). No single “max bucket size.” |
| **HDFS** | **PB-scale** with hundreds/thousands of nodes; single NameNode metadata in millions of files | Throughput scales with DataNodes and replication; block size (e.g. 128 MB) affects large-file throughput. |

### Search & Analytics

| System | Typical scale (setup) | Notes |
|--------|------------------------|--------|
| **Elasticsearch** | **~10–50 GB per shard** recommended; **&lt;200M documents per shard**; **~1000 shards per (non-frozen) data node** default | Total cluster size = nodes × shard capacity. Oversharding hurts performance; scale by adding nodes and reindexing/shrinking if needed. |
| **ClickHouse** | **TB–PB** per cluster; **billions of rows** per table; high compression | Optimized for analytical queries; throughput depends on schema, compression, and hardware. |

### Coordination & Configuration

| System | Typical scale (setup) | Notes |
|--------|------------------------|--------|
| **ZooKeeper** | **~10K–100K+ ops/s** for reads; writes lower (consensus); **KB–MB** for znodes | Suited for metadata and coordination, not bulk data. Scale by ensemble size (3, 5, 7 nodes typical). |
| **etcd** | **~10K+ writes/s** (small values); **~100K+ reads/s**; **multi-GB** storage per cluster | Used by Kubernetes; scale by cluster size and resource limits. |

### Why Scale Numbers Matter in Interviews

- **Sizing**: “We need 1M events/s → Kafka with N brokers” or “We have 50 TB → PostgreSQL + Citus or Cassandra.”
- **Bottlenecks**: “Single Redis node caps at ~1M ops/s; we’ll need a cluster for 10M.”
- **Trade-offs**: “PostgreSQL single table is 32 TB; beyond that we shard or move to a distributed store.”
- **Realism**: Avoid “Kafka can do infinite throughput” or “PostgreSQL can’t hold more than 1 GB”—use order-of-magnitude numbers instead.

---

This ecosystem view helps you **structure** your answer (by category), **recall** standard building blocks (items), and **explain** their use in a given design. The **component reference** gives you concrete technology names; the **conceptual categories** help you reason about trade-offs; the **scale analysis** grounds designs in realistic numbers. Keep this as a mental map when practicing system design problems.
