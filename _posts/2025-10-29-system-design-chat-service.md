---
layout: post
title: "System Design: Chat/Messaging Service"
date: 2025-10-29 23:12:00 -0700
categories: system-design architecture realtime
permalink: /2025/10/29/system-design-chat-service/
tags: [system-design, websocket, pubsub, storage, ordering, presence]
---

# System Design: Chat/Messaging

## Requirements
- One-to-one and group chats, delivery/read receipts, presence, search, attachments, E2E optional.

## Architecture
Clients → Gateway (auth) → WebSocket Fanout + Pub/Sub (Kafka) → Message Store (Cassandra) → Search (Elastic) → Attachments (S3/CDN)

## Ordering/IDs
- Per-conversation monotonic ids via time+shard (snowflake) or per-partition sequence; resolve on client.

## Data model
`conversations(id, members, type)`
`messages(conv_id, msg_id, sender, ts, body, status)`

## SLOs
- Send ACK P95 < 200 ms; delivery < 1 s; presence < 2 s convergence.

## Consistency
- At-least-once over pub/sub; idempotent message writes by (conv_id,msg_id);
- Read-your-writes with sticky reads.

## Failure modes
- Hot group → split shards, partial fanout; degraded typing indicators under load.

## Detailed APIs

```http
POST /v1/messages { conv_id, body, attachments? } -> { msg_id }
GET  /v1/conversations/{id}/history?cursor=...
POST /v1/receipts { conv_id, msg_id, type=delivered|read }
```

## Retention & search

- Retention policies per workspace; legal hold; search indexes updated async with privacy filters.

## Test plan

- WS longevity under mobile networks; presence convergence; ordered delivery under partition.

## What Interviewers Look For

### Real-Time Messaging Skills

1. **WebSocket Architecture**
   - Connection management
   - Message fanout
   - Pub/Sub integration
   - **Red Flags**: Polling, high latency, no real-time

2. **Message Ordering**
   - Per-conversation ordering
   - Monotonic IDs
   - Client-side resolution
   - **Red Flags**: No ordering, out-of-order messages, poor UX

3. **Delivery Guarantees**
   - At-least-once delivery
   - Read receipts
   - Delivery receipts
   - **Red Flags**: Message loss, no receipts, unreliable

### Distributed Systems Skills

1. **Presence System**
   - Online/offline status
   - Convergence time < 2s
   - **Red Flags**: Slow presence, inaccurate status, poor UX

2. **Message Storage**
   - Cassandra for messages
   - Search indexing
   - Retention policies
   - **Red Flags**: No storage, slow search, no retention

3. **Scalability Design**
   - Horizontal scaling
   - Sharding strategy
   - **Red Flags**: Vertical scaling, no sharding, bottlenecks

### Problem-Solving Approach

1. **Hot Group Handling**
   - Shard splitting
   - Partial fanout
   - **Red Flags**: No hot group handling, bottlenecks, poor performance

2. **Edge Cases**
   - Network partitions
   - Connection failures
   - Message duplicates
   - **Red Flags**: Ignoring edge cases, no handling

3. **Trade-off Analysis**
   - Consistency vs latency
   - Ordering vs performance
   - **Red Flags**: No trade-offs, dogmatic choices

### System Design Skills

1. **Component Design**
   - Message service
   - Presence service
   - Search service
   - **Red Flags**: Monolithic, unclear boundaries

2. **Security Design**
   - E2E encryption (optional)
   - Authentication
   - Authorization
   - **Red Flags**: No security, insecure, vulnerabilities

3. **Attachments Handling**
   - S3 storage
   - CDN delivery
   - **Red Flags**: No attachments, slow delivery, high costs

### Communication Skills

1. **Messaging Architecture Explanation**
   - Can explain WebSocket design
   - Understands ordering
   - **Red Flags**: No understanding, vague explanations

2. **Scale Explanation**
   - Can explain scaling strategies
   - Understands bottlenecks
   - **Red Flags**: No understanding, vague

### Meta-Specific Focus

1. **Real-Time Systems Expertise**
   - WebSocket knowledge
   - Low-latency design
   - **Key**: Show real-time systems expertise

2. **Reliability Focus**
   - Message delivery guarantees
   - Presence accuracy
   - **Key**: Demonstrate reliability focus
