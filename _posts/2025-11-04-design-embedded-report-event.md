---
layout: post
title: "Design an Embedded Report Event System"
date: 2025-11-04
categories: [System Design, Interview Example, Analytics, Event Tracking, Reporting]
excerpt: "A detailed walkthrough of designing an embedded report event system for tracking, processing, and generating reports from user events in real-time and batch modes."
---

## Introduction

This post provides a comprehensive walkthrough of designing an embedded report event system. This system captures user events, processes them, and generates embedded reports (dashboards, analytics, insights) that can be displayed within applications. This is a common system design question for companies that need to provide analytics and reporting capabilities to their users.

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Requirements](#requirements)
   - [Functional Requirements](#functional-requirements)
   - [Non-Functional Requirements](#non-functional-requirements)
3. [Capacity Estimation](#capacity-estimation)
4. [Core Entities](#core-entities)
5. [API](#api)
6. [Data Flow](#data-flow)
7. [Database Design](#database-design)
   - [Schema Design](#schema-design)
   - [Database Sharding Strategy](#database-sharding-strategy)
8. [High-Level Design](#high-level-design)
9. [Deep Dive](#deep-dive)
   - [Component Design](#component-design)
   - [Detailed Design](#detailed-design)
   - [Technology Choices](#technology-choices)
   - [Scalability Design](#scalability-design)
   - [Real-Time Updates](#real-time-updates)
   - [Multi-Tenancy](#multi-tenancy)
   - [Monitoring and Observability](#monitoring-and-observability)
   - [Trade-offs and Design Decisions](#trade-offs-and-design-decisions)
   - [Failure Scenarios](#failure-scenarios)
10. [Conclusion](#conclusion)

## Problem Statement

**Design an embedded report event system that:**

1. **Event Collection**: Capture user events from various sources (web, mobile, API)
2. **Event Processing**: Process events in real-time and batch modes
3. **Report Generation**: Generate embedded reports (dashboards, charts, analytics)
4. **Real-Time Updates**: Support real-time report updates as events occur
5. **Historical Data**: Store and query historical event data
6. **Scalability**: Handle millions of events per day
7. **Multi-Tenancy**: Support multiple customers/organizations with data isolation

**Describe the system architecture, components, technology choices, and how to handle scalability, reliability, and real-time processing.**

## Requirements

### Functional Requirements

**Core Features:**

1. **Event Collection**
   - Capture events from web applications, mobile apps, APIs
   - Support multiple event types (page views, clicks, conversions, custom events)
   - Event validation and schema enforcement
   - High-volume event ingestion

2. **Event Processing**
   - Real-time event processing
   - Batch event processing
   - Event aggregation and transformation
   - Event enrichment (adding metadata, user context)

3. **Report Generation**
   - Generate embedded reports (dashboards, charts, tables)
   - Support multiple report types (time-series, cohort, funnel, retention)
   - Custom report creation
   - Report templates and widgets

4. **Real-Time Updates**
   - Real-time dashboard updates
   - Live metrics and KPIs
   - WebSocket/SSE for real-time data streaming

5. **Historical Data**
   - Store historical event data
   - Support time-range queries
   - Data retention policies
   - Efficient querying and aggregation

6. **Multi-Tenancy**
   - Data isolation per customer/organization
   - Per-tenant data access controls
   - Tenant-specific configurations

### Non-Functional Requirements

**Scale:**
- 100+ million events per day
- 10,000+ concurrent report viewers
- 1000+ customers/organizations
- Petabytes of historical data

**Performance:**
- Event ingestion latency: < 100ms
- Real-time report updates: < 1 second
- Historical report generation: < 5 seconds
- Query response time: < 2 seconds

**Reliability:**
- 99.9% uptime
- No event loss
- Data consistency
- Fault tolerance

**Availability:**
- Multi-region deployment
- Automatic failover
- Graceful degradation

### Clarifying Questions

**Scale:**
- Q: How many events per day?
- A: 100+ million events per day, with peaks up to 10 million events per hour

**Event Types:**
- Q: What types of events?
- A: Page views, clicks, conversions, custom business events, user actions

**Report Types:**
- Q: What types of reports?
- A: Time-series charts, cohort analysis, funnel analysis, retention reports, custom dashboards

**Real-Time Requirements:**
- Q: How real-time should updates be?
- A: Real-time dashboards should update within 1 second of events

**Data Retention:**
- Q: How long to retain data?
- A: 2 years for detailed events, longer for aggregated data

**Multi-Tenancy:**
- Q: How many customers?
- A: 1000+ customers, each with their own events and reports

## Capacity Estimation

### Storage Estimates

**Event Data:**
- Each event: ~500 bytes (event data + metadata)
- 100M events/day × 500 bytes = 50GB/day
- With 2-year retention: ~36.5TB
- With compression: ~10TB

**Aggregated Data:**
- Aggregated metrics: ~1KB per aggregation
- 1000 customers × 100 metrics × 365 days = 36.5M aggregations/year
- Total: ~36.5GB/year

**Report Definitions:**
- Each report: ~10KB
- 1000 customers × 100 reports = 100K reports
- Total: ~1GB

### Throughput Estimates

**Write QPS:**
- 100M events/day = ~1,157 events/second average
- Peak: 10M events/hour = ~2,778 events/second
- Total writes: ~3,000 QPS

**Read QPS:**
- Report queries: 10,000 concurrent viewers
- Average: 1 query per second per viewer
- Total reads: ~10,000 QPS

**Real-Time Updates:**
- Real-time dashboard updates: 1,000 concurrent dashboards
- Updates: 1 update per second per dashboard
- Total: ~1,000 updates/second

### Network Bandwidth

- Event ingestion: 3,000 QPS × 500 bytes = 1.5MB/s
- Report queries: 10,000 QPS × 10KB = 100MB/s
- Real-time updates: 1,000 updates/s × 5KB = 5MB/s
- Total: ~100MB/s

## Core Entities

### Event
- **Attributes**: event_id, tenant_id, event_type, user_id, properties, timestamp, created_at
- **Relationships**: Belongs to tenant, processed into reports

### Report
- **Attributes**: report_id, tenant_id, report_name, report_type, widgets, created_at, updated_at
- **Relationships**: Belongs to tenant, contains widgets, generated from events

### Widget
- **Attributes**: widget_id, report_id, widget_type, query, visualization_config, created_at
- **Relationships**: Belongs to report, queries event data

### Tenant
- **Attributes**: tenant_id, tenant_name, plan_tier, storage_quota, created_at
- **Relationships**: Has events, has reports, has users

## API

### Event Collection API
```http
POST /api/v1/events
Authorization: Bearer {token}
Content-Type: application/json

{
  "event_type": "page_view",
  "user_id": "user-123",
  "properties": {
    "page_url": "/products"
  }
}

Response: 202 Accepted
{
  "event_id": "uuid",
  "status": "accepted"
}
```

### Report Generation API
```http
GET /api/v1/reports/{report_id}?start_time=2025-11-01&end_time=2025-11-04

Response: 200 OK
{
  "report_id": "uuid",
  "report_name": "Traffic Overview",
  "widgets": [
    {
      "widget_id": "uuid",
      "type": "time_series",
      "data": {
        "series": [
          {"time": "2025-11-01T00:00:00Z", "value": 1000},
          {"time": "2025-11-02T00:00:00Z", "value": 1200}
        ]
      }
    }
  ]
}
```

### Embedding API
```http
GET /api/v1/reports/{report_id}/embed?width=800&height=600

Response: 200 OK
{
  "embed_code": "<iframe src='...'></iframe>",
  "embed_url": "https://embed.example.com/report?token=...",
  "javascript_sdk": "<script src='...'></script>"
}
```

## Data Flow

### Event Ingestion Flow
1. Client sends event → API Gateway
2. API Gateway → Event Collection Service
3. Event Collection Service validates event
4. Event Collection Service → Message Queue (Kafka)
5. Message Queue → Event Processing Service (real-time)
6. Event Processing Service → Time-Series Database (store event)
7. Event Processing Service → Cache (update real-time metrics)
8. Response returned to client

### Report Generation Flow
1. Client requests report → API Gateway
2. API Gateway → Report Service
3. Report Service checks cache for pre-computed report
4. If cache miss:
   - Report Service → Query Service (query event data)
   - Query Service → Time-Series Database (aggregate events)
   - Query Service → Report Service (return aggregated data)
   - Report Service → Cache (cache report)
5. Report Service → API Gateway (return report)
6. API Gateway → Client (return report)

### Real-Time Update Flow
1. New event processed → Event Processing Service
2. Event Processing Service → Cache (update metrics)
3. Event Processing Service → Message Queue (report update event)
4. Message Queue → Real-Time Service
5. Real-Time Service → WebSocket/SSE (push update to clients)
6. Clients receive updated report data

## Database Design

### Schema Design

**Events Table:**
```sql
CREATE TABLE events (
    event_id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    user_id VARCHAR(36),
    properties JSON,
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP,
    INDEX idx_tenant_timestamp (tenant_id, timestamp),
    INDEX idx_event_type (event_type),
    INDEX idx_user_id (user_id)
);
```

**Reports Table:**
```sql
CREATE TABLE reports (
    report_id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    report_name VARCHAR(255) NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    widgets JSON,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    INDEX idx_tenant_id (tenant_id),
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
);
```

**Widgets Table:**
```sql
CREATE TABLE widgets (
    widget_id VARCHAR(36) PRIMARY KEY,
    report_id VARCHAR(36) NOT NULL,
    widget_type VARCHAR(50) NOT NULL,
    query JSON,
    visualization_config JSON,
    created_at TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES reports(report_id),
    INDEX idx_report_id (report_id)
);
```

**Tenants Table:**
```sql
CREATE TABLE tenants (
    tenant_id VARCHAR(36) PRIMARY KEY,
    tenant_name VARCHAR(255) NOT NULL,
    plan_tier VARCHAR(50),
    storage_quota BIGINT,
    created_at TIMESTAMP
);
```

### Database Sharding Strategy

**Shard by Tenant ID:**
- Tenant data, events, and reports on same shard
- Enables efficient tenant queries
- Use consistent hashing for distribution

**Time-Series Database:**
- Use specialized time-series DB (InfluxDB, TimescaleDB)
- Partition by time for efficient time-range queries
- Optimize for time-series aggregations

## High-Level Design

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                       │
│  (Web Apps, Mobile Apps, APIs - Event Sources)              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Event Collection Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Event       │  │  Event       │  │  Event       │      │
│  │  Gateway     │  │  Validator   │  │  Enricher    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Event Processing Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Real-Time   │  │  Batch       │  │  Aggregation │      │
│  │  Processor   │  │  Processor   │  │  Service     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Message    │ │   Time-Series│ │  Aggregated  │
│   Queue      │ │   Database   │ │   Data Store │
│   (Kafka)    │ │  (InfluxDB)  │ │  (PostgreSQL)│
└──────────────┘ └──────────────┘ └──────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Report Generation Layer                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Report      │  │  Query       │  │  Cache       │      │
│  │  Generator   │  │  Engine      │  │  Service     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Embedding & Delivery Layer                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Embedding   │  │  Real-Time   │  │  API         │      │
│  │  Service     │  │  Streamer    │  │  Gateway     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                       │
│  (Customer Applications - Embedded Reports)                   │
└─────────────────────────────────────────────────────────────┘
```

### Core Services

1. **Event Gateway**: Receives events from clients, validates, routes
2. **Event Validator**: Validates event schema and data
3. **Event Enricher**: Adds metadata, user context, timestamps
4. **Real-Time Processor**: Processes events in real-time for live dashboards
5. **Batch Processor**: Processes events in batches for historical reports
6. **Aggregation Service**: Aggregates events into metrics
7. **Report Generator**: Generates reports from processed data
8. **Query Engine**: Executes queries on historical data
9. **Embedding Service**: Generates embeddable report widgets
10. **Real-Time Streamer**: Streams real-time updates via WebSocket/SSE

### Data Stores

1. **Message Queue (Kafka)**: Event streaming and processing
2. **Time-Series Database (InfluxDB/TimescaleDB)**: Raw event storage
3. **Aggregated Data Store (PostgreSQL)**: Aggregated metrics and reports
4. **Cache (Redis)**: Report cache and real-time data
5. **Object Storage (S3)**: Report exports and archives

## Deep Dive

### Component Design

#### Detailed Design

### Event Schema

**Event Structure:**
```json
{
  "event_id": "uuid",
  "tenant_id": "customer-123",
  "event_type": "page_view",
  "timestamp": "2025-11-04T10:00:00Z",
  "user_id": "user-456",
  "session_id": "session-789",
  "properties": {
    "page_url": "/products",
    "page_title": "Products",
    "referrer": "https://google.com",
    "device_type": "desktop",
    "browser": "Chrome",
    "location": {
      "country": "US",
      "city": "San Francisco"
    }
  },
  "metadata": {
    "ip_address": "192.168.1.1",
    "user_agent": "...",
    "sdk_version": "1.2.3"
  }
}
```

### Database Schema

**Events Table (Time-Series):**
```sql
CREATE TABLE events (
    event_id UUID PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    user_id VARCHAR(255),
    session_id VARCHAR(255),
    properties JSONB,
    metadata JSONB,
    
    -- Partitioning
    PARTITION BY RANGE (timestamp),
    
    -- Indexes
    INDEX idx_tenant_timestamp (tenant_id, timestamp),
    INDEX idx_event_type (event_type),
    INDEX idx_user_id (user_id),
    INDEX idx_session_id (session_id)
);

-- Partition by month
CREATE TABLE events_2025_11 PARTITION OF events
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');
```

**Aggregated Metrics Table:**
```sql
CREATE TABLE aggregated_metrics (
    metric_id UUID PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_type VARCHAR(50), -- 'counter', 'gauge', 'histogram'
    time_bucket TIMESTAMP NOT NULL, -- hourly, daily
    bucket_type VARCHAR(20), -- 'hour', 'day', 'week', 'month'
    value DECIMAL(20, 4),
    dimensions JSONB, -- filters/dimensions
    
    UNIQUE(tenant_id, metric_name, time_bucket, bucket_type, dimensions),
    INDEX idx_tenant_metric_time (tenant_id, metric_name, time_bucket)
);
```

**Reports Table:**
```sql
CREATE TABLE reports (
    report_id UUID PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    report_name VARCHAR(255) NOT NULL,
    report_type VARCHAR(50), -- 'time_series', 'cohort', 'funnel', 'retention'
    config JSONB, -- report configuration
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    
    INDEX idx_tenant_id (tenant_id)
);
```

**Report Widgets Table:**
```sql
CREATE TABLE report_widgets (
    widget_id UUID PRIMARY KEY,
    report_id UUID REFERENCES reports(report_id),
    widget_type VARCHAR(50), -- 'chart', 'table', 'metric'
    config JSONB, -- widget configuration
    position INTEGER, -- position in dashboard
    created_at TIMESTAMP NOT NULL
);
```

### Event Collection Service

**API Design:**
```http
POST /api/v1/events
Content-Type: application/json
X-Tenant-ID: customer-123

{
  "event_type": "page_view",
  "user_id": "user-456",
  "session_id": "session-789",
  "properties": {
    "page_url": "/products",
    "page_title": "Products"
  }
}

Response: 202 Accepted
{
  "event_id": "uuid",
  "status": "accepted",
  "timestamp": "2025-11-04T10:00:00Z"
}
```

**Implementation:**
```python
class EventCollectionService:
    def collect_event(self, event_data, tenant_id):
        # Validate event
        validated_event = self.validator.validate(event_data, tenant_id)
        
        # Enrich event
        enriched_event = self.enricher.enrich(validated_event, tenant_id)
        
        # Add tenant isolation
        enriched_event['tenant_id'] = tenant_id
        enriched_event['event_id'] = str(uuid.uuid4())
        enriched_event['timestamp'] = datetime.utcnow().isoformat()
        
        # Publish to Kafka
        self.kafka.produce('events', {
            'key': tenant_id,  # Partition by tenant
            'value': enriched_event
        })
        
        # Return event ID
        return enriched_event['event_id']
```

### Real-Time Processing Service

**Implementation:**
```python
class RealTimeProcessor:
    def process_event(self, event):
        tenant_id = event['tenant_id']
        event_type = event['event_type']
        
        # Update real-time metrics
        self.update_realtime_metrics(tenant_id, event_type, event)
        
        # Update cache for dashboards
        self.update_dashboard_cache(tenant_id, event)
        
        # Trigger real-time updates
        self.trigger_realtime_updates(tenant_id, event)
    
    def update_realtime_metrics(self, tenant_id, event_type, event):
        # Update counters
        key = f"metrics:{tenant_id}:{event_type}:realtime"
        self.redis.incr(key)
        
        # Update time-windowed metrics
        time_window = self.get_current_time_window()  # e.g., last hour
        window_key = f"metrics:{tenant_id}:{event_type}:{time_window}"
        self.redis.incr(window_key)
        self.redis.expire(window_key, 3600)  # 1 hour TTL
    
    def update_dashboard_cache(self, tenant_id, event):
        # Update cached dashboard data
        dashboard_key = f"dashboard:{tenant_id}:realtime"
        self.redis.hincrby(dashboard_key, event['event_type'], 1)
        self.redis.expire(dashboard_key, 300)  # 5 minute TTL
    
    def trigger_realtime_updates(self, tenant_id, event):
        # Publish to WebSocket channel
        self.websocket.publish(f"tenant:{tenant_id}:updates", {
            'event_type': event['event_type'],
            'timestamp': event['timestamp'],
            'metrics': self.get_realtime_metrics(tenant_id)
        })
```

### Batch Processing Service

**Implementation:**
```python
class BatchProcessor:
    def process_batch(self, events):
        # Group events by tenant and time bucket
        grouped = self.group_events(events)
        
        for (tenant_id, time_bucket), event_group in grouped.items():
            # Aggregate events
            aggregations = self.aggregate_events(event_group)
            
            # Store aggregated metrics
            self.store_aggregated_metrics(tenant_id, time_bucket, aggregations)
            
            # Update report cache
            self.update_report_cache(tenant_id, aggregations)
    
    def aggregate_events(self, events):
        aggregations = {}
        
        # Count by event type
        for event in events:
            event_type = event['event_type']
            aggregations[f"{event_type}_count"] = aggregations.get(f"{event_type}_count", 0) + 1
        
        # Calculate other metrics (unique users, sessions, etc.)
        unique_users = len(set(e['user_id'] for e in events if e.get('user_id')))
        aggregations['unique_users'] = unique_users
        
        return aggregations
    
    def store_aggregated_metrics(self, tenant_id, time_bucket, aggregations):
        for metric_name, value in aggregations.items():
            self.db.insert_aggregated_metric(
                tenant_id=tenant_id,
                metric_name=metric_name,
                time_bucket=time_bucket,
                value=value,
                bucket_type='hour'
            )
```

### Report Generation Service

**Implementation:**
```python
class ReportGenerator:
    def generate_report(self, report_id, tenant_id, time_range):
        # Get report configuration
        report = self.db.get_report(report_id, tenant_id)
        
        # Generate report data
        report_data = {}
        
        for widget in report['widgets']:
            widget_data = self.generate_widget_data(
                widget, tenant_id, time_range
            )
            report_data[widget['widget_id']] = widget_data
        
        return report_data
    
    def generate_widget_data(self, widget, tenant_id, time_range):
        widget_type = widget['widget_type']
        config = widget['config']
        
        if widget_type == 'time_series':
            return self.generate_timeseries_data(
                config, tenant_id, time_range
            )
        elif widget_type == 'cohort':
            return self.generate_cohort_data(
                config, tenant_id, time_range
            )
        elif widget_type == 'funnel':
            return self.generate_funnel_data(
                config, tenant_id, time_range
            )
        elif widget_type == 'metric':
            return self.generate_metric_data(
                config, tenant_id, time_range
            )
    
    def generate_timeseries_data(self, config, tenant_id, time_range):
        # Query aggregated metrics
        metrics = self.db.query_aggregated_metrics(
            tenant_id=tenant_id,
            metric_name=config['metric'],
            start_time=time_range['start'],
            end_time=time_range['end'],
            bucket_type=config.get('bucket_type', 'hour')
        )
        
        # Format for chart
        return {
            'data': [
                {'time': m['time_bucket'], 'value': m['value']}
                for m in metrics
            ],
            'type': 'line'
        }
```

### Embedding Service

**Implementation:**
```python
class EmbeddingService:
    def generate_embed_code(self, report_id, tenant_id, options):
        # Generate embed URL
        embed_url = self.generate_embed_url(report_id, tenant_id, options)
        
        # Generate iframe embed code
        embed_code = f"""
        <iframe
            src="{embed_url}"
            width="{options.get('width', 800)}"
            height="{options.get('height', 600)}"
            frameborder="0"
            allowfullscreen>
        </iframe>
        """
        
        return {
            'embed_code': embed_code,
            'embed_url': embed_url,
            'javascript_sdk': self.generate_sdk_code(report_id, tenant_id)
        }
    
    def generate_embed_url(self, report_id, tenant_id, options):
        base_url = self.config.embed_base_url
        params = {
            'report_id': report_id,
            'tenant_id': tenant_id,
            'token': self.generate_embed_token(report_id, tenant_id),
            **options
        }
        
        return f"{base_url}/embed?{urlencode(params)}"
```

### Real-Time Streaming Service

**WebSocket Implementation:**
```python
class WebSocketService:
    def handle_connection(self, websocket, tenant_id, report_id):
        # Authenticate connection
        if not self.authenticate(websocket, tenant_id):
            websocket.close()
            return
        
        # Subscribe to updates
        channel = f"tenant:{tenant_id}:report:{report_id}"
        self.subscribe(websocket, channel)
        
        # Send initial data
        initial_data = self.get_report_data(report_id, tenant_id)
        websocket.send_json(initial_data)
        
        # Keep connection alive
        while True:
            try:
                # Wait for updates
                message = self.wait_for_update(channel)
                if message:
                    websocket.send_json(message)
            except WebSocketDisconnect:
                break
        
        self.unsubscribe(websocket, channel)
```

### Technology Choices

### Message Queue: Apache Kafka

**Why Kafka:**
- **High Throughput**: Handle millions of events per second
- **Durability**: Events persisted to disk
- **Partitioning**: Partition by tenant for isolation
- **Consumer Groups**: Multiple consumers for processing
- **Replay Capability**: Replay events for reprocessing

**Topic Design:**
- `events`: Raw events (partitioned by tenant_id)
- `events-processed`: Processed events
- `metrics-updates`: Metric updates
- `report-updates`: Report update events

### Time-Series Database: InfluxDB or TimescaleDB

**Why Time-Series DB:**
- **Optimized for Time-Series**: Efficient time-range queries
- **Data Compression**: Automatic compression
- **High Write Throughput**: Handle high event volumes
- **Retention Policies**: Automatic data retention

**Why InfluxDB:**
- Built specifically for time-series
- Excellent compression
- Good query performance

**Why TimescaleDB:**
- PostgreSQL-based (familiar SQL)
- Better for complex queries
- Good for hybrid workloads

### Aggregated Data Store: PostgreSQL

**Why PostgreSQL:**
- **ACID Compliance**: Strong consistency for reports
- **Complex Queries**: Support for complex aggregations
- **JSONB Support**: Flexible schema for report configs
- **Mature Ecosystem**: Proven reliability

### Cache: Redis

**Why Redis:**
- **Low Latency**: Sub-millisecond access
- **Data Structures**: Rich data structures (hashes, sorted sets)
- **Pub/Sub**: Real-time updates
- **Persistence**: Optional persistence

**Caching Strategy:**
- **Report Cache**: Cache generated reports (TTL: 5 minutes)
- **Real-Time Metrics**: Cache real-time metrics (TTL: 1 minute)
- **Dashboard Cache**: Cache dashboard data (TTL: 1 minute)

### Scalability Design

### Horizontal Scaling

**Event Collection:**
- Multiple event gateway instances
- Load balancer (round-robin, least connections)
- Auto-scaling based on event rate

**Event Processing:**
- Multiple real-time processors
- Kafka consumer groups for parallel processing
- Multiple batch processors

**Report Generation:**
- Multiple report generator instances
- Query engine scaling
- Cache layer scaling

### Data Partitioning

**Events Partitioning:**
- Partition by tenant_id (Kafka partitioning)
- Time-based partitioning (monthly partitions)
- Partition pruning for queries

**Aggregated Metrics Partitioning:**
- Partition by tenant_id and time_bucket
- Monthly partitions for historical data
- Hot/cold data separation

### Caching Strategy

**Multi-Level Caching:**
1. **L1 Cache**: In-memory cache in application
2. **L2 Cache**: Redis (distributed cache)
3. **CDN**: Static report assets

**Cache Invalidation:**
- Time-based expiration (TTL)
- Event-driven invalidation
- Manual cache invalidation API

### Real-Time Updates

### WebSocket Architecture

```
Client ←→ WebSocket Server ←→ Redis Pub/Sub ←→ Event Processors
```

**Implementation:**
- WebSocket server for client connections
- Redis Pub/Sub for event distribution
- Event processors publish to Redis channels
- WebSocket server subscribes and broadcasts to clients

### Server-Sent Events (SSE) Alternative

For simpler use cases:
- HTTP-based (easier than WebSocket)
- One-way communication (server to client)
- Automatic reconnection
- Lower overhead

### Multi-Tenancy

### Data Isolation

**Tenant Isolation Strategies:**

1. **Database-Level Isolation**
   - Separate database per tenant (strongest isolation)
   - Tenant ID in all tables (shared database)

2. **Application-Level Isolation**
   - All queries filtered by tenant_id
   - Tenant context in all operations

3. **Hybrid Approach**
   - Tenant ID in all tables
   - Row-level security policies
   - Application-level filtering

**Implementation:**
```python
class TenantContext:
    def __init__(self, tenant_id):
        self.tenant_id = tenant_id
    
    def query_events(self, filters):
        # Always filter by tenant_id
        filters['tenant_id'] = self.tenant_id
        return self.db.query('events', filters)
```

### Security

**Authentication:**
- API keys per tenant
- OAuth tokens
- JWT tokens with tenant claim

**Authorization:**
- Tenant-based access control
- Role-based access within tenant
- Report-level permissions

### Monitoring and Observability

### Key Metrics

**Event Metrics:**
- Events ingested per second
- Events processed per second
- Event processing latency
- Event loss rate

**Report Metrics:**
- Report generation latency
- Report cache hit rate
- Report query performance
- Concurrent report viewers

**System Metrics:**
- API latency (p50, p95, p99)
- Database query latency
- Cache hit rate
- Error rates

### Alerting

**Critical Alerts:**
- Event ingestion failure
- Event processing lag
- Report generation failures
- Database connection issues

**Warning Alerts:**
- High event processing latency
- Low cache hit rate
- High error rates
- Resource utilization

### Trade-offs and Design Decisions

### Real-Time vs. Batch Processing

**Decision**: Both
- **Real-Time**: For live dashboards and alerts
- **Batch**: For historical reports and complex aggregations

**Trade-off**: Complexity vs. flexibility

### Time-Series DB vs. Relational DB

**Decision**: Both
- **Time-Series DB**: For raw event storage
- **Relational DB**: For aggregated metrics and reports

**Trade-off**: Specialized storage vs. query flexibility

### WebSocket vs. Polling

**Decision**: WebSocket for real-time, polling fallback
- **WebSocket**: Real-time updates, lower latency
- **Polling**: Fallback for WebSocket-unavailable scenarios

**Trade-off**: Complexity vs. real-time capabilities

### Failure Scenarios

### Event Collection Failure

**Scenario**: Event gateway fails

**Handling:**
1. Multiple gateway instances (redundancy)
2. Load balancer health checks
3. Client retry with exponential backoff
4. Dead letter queue for failed events

### Event Processing Lag

**Scenario**: Event processing falls behind

**Handling:**
1. Scale processors horizontally
2. Increase Kafka consumer instances
3. Alert on lag threshold
4. Prioritize critical events

### Database Failure

**Scenario**: Database unavailable

**Handling:**
1. Database replication (primary + replicas)
2. Automatic failover
3. Cache serving stale data temporarily
4. Graceful degradation

## Conclusion

Designing an embedded report event system requires:

1. **Event Collection**: Scalable event ingestion with validation
2. **Event Processing**: Real-time and batch processing pipelines
3. **Report Generation**: Efficient report generation with caching
4. **Real-Time Updates**: WebSocket/SSE for live dashboards
5. **Historical Data**: Time-series database for efficient queries
6. **Multi-Tenancy**: Data isolation and security
7. **Scalability**: Horizontal scaling of all components
8. **Reliability**: Fault tolerance and graceful degradation

**Key Design Principles:**
- **Separation of Concerns**: Separate collection, processing, and reporting
- **Caching Strategy**: Multi-level caching for performance
- **Data Partitioning**: Partition by tenant and time
- **Real-Time First**: Design for real-time with batch fallback
- **Tenant Isolation**: Strong data isolation and security

This system design demonstrates understanding of event-driven architectures, real-time processing, time-series data, and multi-tenant systems—all critical for building production-grade analytics and reporting systems.

