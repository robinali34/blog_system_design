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
