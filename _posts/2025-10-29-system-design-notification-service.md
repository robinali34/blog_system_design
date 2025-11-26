---
layout: post
title: "System Design: Notification/Push Service"
date: 2025-10-29 23:15:00 -0700
categories: system-design architecture
permalink: /2025/10/29/system-design-notification-service/
tags: [system-design, push, apns, fcm, email, retry]
---

# System Design: Notification/Push Service

## Requirements
- Multi-channel: mobile push (APNs/FCM), email, SMS; templates, preferences, retries, dedupe.

## Architecture
Producers → Topic (Kafka) → Router → Channel Workers (APNs/FCM/SMTP/SMS) → Providers
           ↘ Store (Postgres) for receipts, logs, preferences

## SLOs
- Enqueue→provider ACK P95 < 300 ms; Exactly-once user experience via dedupe keys.

## Capacity
- 100k notifications/sec fanout bursts; workers horizontally scaled; provider quotas respected.

## Failure modes
- Provider outage → circuit break and requeue with exponential backoff; channel fallback.

## What Interviewers Look For

### Notification Systems Skills

1. **Multi-Channel Support**
   - APNs/FCM for mobile push
   - Email/SMS channels
   - Template management
   - **Red Flags**: Single channel, no templates, poor management

2. **Reliability & Delivery**
   - Exactly-once semantics
   - Retry mechanisms
   - Deduplication
   - **Red Flags**: Duplicate notifications, no retry, unreliable delivery

3. **Provider Integration**
   - Provider quotas
   - Circuit breakers
   - Fallback strategies
   - **Red Flags**: No quota management, no circuit breakers, provider failures

### Distributed Systems Skills

1. **Message Queue Design**
   - Kafka for high throughput
   - Topic partitioning
   - Consumer groups
   - **Red Flags**: Wrong queue choice, no partitioning, bottlenecks

2. **Scalability Design**
   - Horizontal scaling
   - Worker pools
   - Load distribution
   - **Red Flags**: Vertical scaling, bottlenecks, poor distribution

3. **SLO Management**
   - Latency targets (< 300ms)
   - Throughput targets (100k/sec)
   - **Red Flags**: No SLOs, high latency, low throughput

### Problem-Solving Approach

1. **Failure Handling**
   - Provider outages
   - Network failures
   - Rate limiting
   - **Red Flags**: Ignoring failures, no handling, poor recovery

2. **Edge Cases**
   - Duplicate notifications
   - Provider quotas
   - Channel failures
   - **Red Flags**: Ignoring edge cases, no handling

3. **Trade-off Analysis**
   - Latency vs reliability
   - Cost vs features
   - **Red Flags**: No trade-offs, dogmatic choices

### System Design Skills

1. **Component Design**
   - Router service
   - Channel workers
   - Preference store
   - **Red Flags**: Monolithic, unclear boundaries

2. **Storage Design**
   - Receipt tracking
   - Preference management
   - Logging
   - **Red Flags**: No tracking, no preferences, no logs

3. **Monitoring**
   - Delivery rates
   - Provider health
   - Latency metrics
   - **Red Flags**: No monitoring, no metrics, no visibility

### Communication Skills

1. **Architecture Explanation**
   - Can explain notification flow
   - Understands multi-channel
   - **Red Flags**: No understanding, vague explanations

2. **Reliability Explanation**
   - Can explain retry logic
   - Understands deduplication
   - **Red Flags**: No understanding, vague

### Meta-Specific Focus

1. **Notification Systems Expertise**
   - Multi-channel knowledge
   - Reliability focus
   - **Key**: Show notification systems expertise

2. **Scale & Performance**
   - High throughput design
   - Low latency
   - **Key**: Demonstrate scale expertise
