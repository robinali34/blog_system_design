---
layout: post
title: "Apache Pulsar: Comprehensive Guide to Distributed Messaging and Streaming"
date: 2025-12-29
categories: [Apache Pulsar, Messaging, Streaming, Distributed Systems, System Design, Technology]
excerpt: "A comprehensive guide to Apache Pulsar, covering pub/sub messaging, multi-tenancy, geo-replication, tiered storage, and best practices for building scalable messaging and streaming systems."
---

## Introduction

Apache Pulsar is a cloud-native, distributed messaging and streaming platform designed for high performance, scalability, and multi-tenancy. It combines the best features of traditional messaging systems and streaming platforms. Understanding Pulsar is essential for system design interviews involving messaging and event streaming.

This guide covers:
- **Pulsar Fundamentals**: Topics, subscriptions, and messaging model
- **Architecture**: Brokers, BookKeeper, and ZooKeeper
- **Multi-Tenancy**: Namespaces, isolation, and resource quotas
- **Geo-Replication**: Cross-datacenter replication
- **Best Practices**: Performance, reliability, and monitoring

## What is Apache Pulsar?

Apache Pulsar is a messaging and streaming platform that:
- **Pub/Sub Messaging**: Traditional messaging patterns
- **Streaming**: Real-time data streaming
- **Multi-Tenancy**: Isolated tenants and namespaces
- **Geo-Replication**: Cross-datacenter replication
- **Tiered Storage**: Automatic data offloading

### Key Concepts

**Topic**: Channel for messages (similar to Kafka topic)

**Subscription**: Consumer group (exclusive, shared, failover, key-shared)

**Producer**: Application that publishes messages

**Consumer**: Application that consumes messages

**Namespace**: Logical grouping of topics

**Tenant**: Top-level namespace isolation

## Core Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Pulsar Cluster                              │
│                                                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │         Pulsar Brokers                           │    │
│  │  (Message Routing, Load Balancing)                │    │
│  └──────────────────────────────────────────────────┘    │
│                          │                                │
│  ┌──────────────────────────────────────────────────┐    │
│  │         Apache BookKeeper                        │    │
│  │  (Persistent Storage, Replication)                │    │
│  └──────────────────────────────────────────────────┘    │
│                          │                                │
│  ┌──────────────────────────────────────────────────┐    │
│  │         ZooKeeper                                 │    │
│  │  (Coordination, Metadata)                         │    │
│  └──────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────┘
```

## Messaging Model

### Topics

**Topic Naming:**
```
persistent://tenant/namespace/topic-name
```

**Topic Types:**
- **Persistent**: Messages persisted to disk
- **Non-Persistent**: Messages in memory only

**Example:**
```java
// Persistent topic
String topic = "persistent://public/default/my-topic";

// Non-persistent topic
String topic = "non-persistent://public/default/my-topic";
```

### Subscriptions

**Subscription Types:**

**1. Exclusive:**
- Single consumer per subscription
- Failover on consumer failure

**2. Shared:**
- Multiple consumers share messages
- Round-robin distribution

**3. Failover:**
- Primary and backup consumers
- Automatic failover

**4. Key-Shared:**
- Messages with same key to same consumer
- Ordering per key

**Example:**
```java
// Exclusive subscription
consumer.subscribe(topic, "my-subscription", 
    SubscriptionType.Exclusive);

// Shared subscription
consumer.subscribe(topic, "my-subscription", 
    SubscriptionType.Shared);
```

## Producer

### Java Producer

```java
import org.apache.pulsar.client.api.*;

PulsarClient client = PulsarClient.builder()
    .serviceUrl("pulsar://localhost:6650")
    .build();

Producer<String> producer = client.newProducer(Schema.STRING)
    .topic("persistent://public/default/my-topic")
    .create();

// Send message
producer.send("Hello Pulsar");

// Send with properties
MessageId msgId = producer.newMessage()
    .key("message-key")
    .value("Hello Pulsar")
    .property("property1", "value1")
    .send();

producer.close();
client.close();
```

### Python Producer

```python
import pulsar

client = pulsar.Client('pulsar://localhost:6650')
producer = client.create_producer('persistent://public/default/my-topic')

producer.send('Hello Pulsar'.encode('utf-8'))
producer.close()
client.close()
```

## Consumer

### Java Consumer

```java
Consumer<String> consumer = client.newConsumer(Schema.STRING)
    .topic("persistent://public/default/my-topic")
    .subscriptionName("my-subscription")
    .subscriptionType(SubscriptionType.Shared)
    .subscribe();

// Receive message
Message<String> msg = consumer.receive();
System.out.println("Received: " + msg.getValue());

// Acknowledge
consumer.acknowledge(msg);

consumer.close();
```

### Async Consumer

```java
consumer.messageListener((consumer, msg) -> {
    try {
        System.out.println("Received: " + msg.getValue());
        consumer.acknowledge(msg);
    } catch (Exception e) {
        consumer.negativeAcknowledge(msg);
    }
});
```

## Multi-Tenancy

### Namespaces

**Namespace Structure:**
```
tenant/namespace
```

**Example:**
```
public/default
production/analytics
development/testing
```

**Create Namespace:**
```bash
pulsar-admin namespaces create public/default
```

**Set Retention:**
```bash
pulsar-admin namespaces set-retention public/default \
  --size 10G --time 7d
```

### Resource Quotas

**Set Quota:**
```bash
pulsar-admin namespaces set-quota public/default \
  --msgRateIn 1000 \
  --msgRateOut 2000 \
  --storage 10G
```

## Geo-Replication

### Configure Replication

**Cluster Setup:**
```bash
# Cluster 1
pulsar-admin clusters create cluster1 \
  --url http://cluster1-broker:8080

# Cluster 2
pulsar-admin clusters create cluster2 \
  --url http://cluster2-broker:8080
```

**Enable Replication:**
```bash
pulsar-admin namespaces set-clusters public/default \
  --clusters cluster1,cluster2
```

**Benefits:**
- Cross-datacenter replication
- Disaster recovery
- Low-latency access

## Tiered Storage

### Offload to S3

**Configure Offload:**
```bash
pulsar-admin namespaces set-offload-threshold public/default \
  --size 10G
```

**Benefits:**
- Reduce storage costs
- Automatic data offloading
- Transparent access

## Performance Optimization

### Batching

**Enable Batching:**
```java
producer.batchingMaxMessages(1000)
    .batchingMaxPublishDelay(10, TimeUnit.MILLISECONDS);
```

### Compression

**Enable Compression:**
```java
producer.compressionType(CompressionType.LZ4);
```

### Message Key

**Set Message Key:**
```java
producer.newMessage()
    .key("user-123")
    .value("message")
    .send();
```

## Best Practices

### 1. Subscription Design

- Choose appropriate subscription type
- Use key-shared for ordering
- Handle acknowledgments properly
- Monitor consumer lag

### 2. Topic Design

- Use persistent topics for reliability
- Organize topics in namespaces
- Set appropriate retention
- Plan for growth

### 3. Performance

- Enable batching
- Use compression
- Set message keys
- Monitor throughput

### 4. Multi-Tenancy

- Isolate tenants properly
- Set resource quotas
- Monitor usage
- Plan capacity

## What Interviewers Look For

### Messaging Understanding

1. **Pulsar Concepts**
   - Understanding of topics, subscriptions
   - Multi-tenancy
   - Geo-replication
   - **Red Flags**: No Pulsar understanding, wrong concepts, no multi-tenancy

2. **Messaging Patterns**
   - Pub/sub patterns
   - Subscription types
   - Message ordering
   - **Red Flags**: Wrong patterns, poor subscriptions, no ordering

3. **Scalability**
   - Multi-tenancy design
   - Geo-replication
   - Performance optimization
   - **Red Flags**: No multi-tenancy, no replication, poor performance

### Problem-Solving Approach

1. **Subscription Design**
   - Choose appropriate type
   - Handle ordering
   - Manage consumer groups
   - **Red Flags**: Wrong type, no ordering, poor management

2. **Multi-Tenancy Design**
   - Namespace organization
   - Resource quotas
   - Isolation strategies
   - **Red Flags**: Poor organization, no quotas, no isolation

### System Design Skills

1. **Messaging Architecture**
   - Pulsar cluster design
   - Topic organization
   - Subscription management
   - **Red Flags**: No architecture, poor organization, no management

2. **Scalability**
   - Multi-tenant design
   - Geo-replication
   - Performance tuning
   - **Red Flags**: No scaling, no replication, no tuning

### Communication Skills

1. **Clear Explanation**
   - Explains Pulsar concepts
   - Discusses trade-offs
   - Justifies design decisions
   - **Red Flags**: Unclear explanations, no justification, confusing

### Meta-Specific Focus

1. **Messaging Expertise**
   - Understanding of messaging systems
   - Pulsar mastery
   - Multi-tenancy patterns
   - **Key**: Demonstrate messaging expertise

2. **System Design Skills**
   - Can design messaging systems
   - Understands multi-tenancy challenges
   - Makes informed trade-offs
   - **Key**: Show practical messaging design skills

## Summary

**Apache Pulsar Key Points:**
- **Pub/Sub Messaging**: Traditional messaging patterns
- **Streaming**: Real-time data streaming
- **Multi-Tenancy**: Isolated tenants and namespaces
- **Geo-Replication**: Cross-datacenter replication
- **Tiered Storage**: Automatic data offloading
- **Multiple Subscription Types**: Exclusive, shared, failover, key-shared

**Common Use Cases:**
- Event-driven architecture
- Real-time analytics
- Multi-tenant applications
- Cross-datacenter messaging
- Stream processing

**Best Practices:**
- Use appropriate subscription types
- Organize topics in namespaces
- Set resource quotas
- Enable geo-replication for DR
- Use tiered storage for cost savings
- Monitor consumer lag
- Optimize batching and compression

Apache Pulsar is a powerful messaging and streaming platform that combines the best features of traditional messaging and modern streaming systems.

