---
layout: post
title: "Elasticsearch: Comprehensive Guide to Distributed Search and Analytics Engine"
date: 2025-11-29
categories: [Elasticsearch, Search Engine, Database, Distributed Systems, System Design, Technology, Analytics]
excerpt: "A comprehensive guide to Elasticsearch, covering architecture, indexing, search, aggregation, scalability, and best practices for building search engines, log analytics, and real-time data exploration systems."
---

## Introduction

Elasticsearch is a distributed, RESTful search and analytics engine built on Apache Lucene. It provides near real-time search capabilities, powerful analytics, and horizontal scalability, making it ideal for search engines, log analytics, and data exploration.

This guide covers:
- **Elasticsearch Fundamentals**: Core concepts, architecture, and components
- **Indexing and Search**: How to index and search data
- **Aggregations**: Analytics and data exploration
- **Scalability**: Cluster management and horizontal scaling
- **Use Cases**: Real-world applications and patterns
- **Best Practices**: Performance, reliability, and optimization

## What is Elasticsearch?

Elasticsearch is a distributed search and analytics engine that offers:
- **Full-Text Search**: Powerful text search with relevance scoring
- **Real-Time**: Near real-time indexing and search
- **Scalability**: Horizontal scaling with automatic sharding
- **Analytics**: Aggregations for data analysis
- **RESTful API**: Simple HTTP-based interface
- **Schema-Free**: JSON document storage with dynamic mapping

### Key Concepts

**Index**: A collection of documents (similar to a database in SQL)

**Document**: A JSON object stored in an index (similar to a row in SQL)

**Type**: (Deprecated in 7.x+) A category of documents within an index

**Shard**: A subset of an index (for horizontal scaling)

**Replica**: A copy of a shard (for high availability)

**Node**: A single Elasticsearch instance

**Cluster**: A collection of nodes working together

## Core Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Elasticsearch Cluster                 │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │  Node 1  │  │  Node 2  │  │  Node 3  │              │
│  │ (Master) │  │          │  │          │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
│       │             │             │                     │
│  ┌────▼─────────────▼─────────────▼─────┐              │
│  │         Index: "products"            │              │
│  │  ┌──────────┐  ┌──────────┐         │              │
│  │  │ Shard 0  │  │ Shard 1  │         │              │
│  │  │ (Primary)│  │ (Primary)│         │              │
│  │  └────┬─────┘  └────┬─────┘         │              │
│  │       │             │                │              │
│  │  ┌────▼─────┐  ┌────▼─────┐         │              │
│  │  │ Replica  │  │ Replica  │         │              │
│  │  │  Shard 0 │  │  Shard 1 │         │              │
│  │  └──────────┘  └──────────┘         │              │
│  └─────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────┘
```

## Common Use Cases

### 1. Full-Text Search

Search through large volumes of text data with relevance scoring.

**Use Cases:**
- Product search (e-commerce)
- Content search (blogs, articles)
- Document search
- User search

**Example:**
```json
// Index a document
POST /products/_doc/1
{
  "title": "iPhone 15 Pro",
  "description": "Latest iPhone with advanced camera",
  "price": 999,
  "category": "electronics"
}

// Search
GET /products/_search
{
  "query": {
    "match": {
      "description": "camera phone"
    }
  }
}
```

### 2. Log Analytics

Store, search, and analyze log data in real-time.

**Use Cases:**
- Application logs
- System logs
- Security logs
- Error tracking

**Example:**
```json
// Index log
POST /logs/_doc
{
  "timestamp": "2025-12-29T10:00:00Z",
  "level": "ERROR",
  "message": "Database connection failed",
  "service": "payment-service",
  "user_id": "user_123"
}

// Search errors
GET /logs/_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "level": "ERROR" }},
        { "range": { "timestamp": { "gte": "now-1h" }}}
      ]
    }
  }
}
```

### 3. Real-Time Analytics

Aggregate and analyze data in real-time.

**Use Cases:**
- Metrics and monitoring
- Business intelligence
- Time-series analytics
- Dashboard data

**Example:**
```json
// Aggregation: Count errors by service
GET /logs/_search
{
  "size": 0,
  "aggs": {
    "errors_by_service": {
      "terms": {
        "field": "service.keyword",
        "size": 10
      }
    }
  }
}
```

## Indexing and Search

### Indexing Documents

**Basic Indexing:**
```json
// Index a single document
POST /products/_doc/1
{
  "title": "Laptop",
  "price": 1299,
  "category": "electronics"
}

// Bulk indexing
POST /products/_bulk
{"index":{"_id":"1"}}
{"title":"Laptop","price":1299}
{"index":{"_id":"2"}}
{"title":"Phone","price":699}
```

### Search Queries

**Match Query (Full-Text):**
```json
GET /products/_search
{
  "query": {
    "match": {
      "title": "laptop computer"
    }
  }
}
```

**Term Query (Exact Match):**
```json
GET /products/_search
{
  "query": {
    "term": {
      "category.keyword": "electronics"
    }
  }
}
```

**Bool Query (Combined):**
```json
GET /products/_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "title": "laptop" }}
      ],
      "filter": [
        { "range": { "price": { "gte": 1000, "lte": 2000 }}}
      ]
    }
  }
}
```

## Aggregations

### Metrics Aggregations

**Average, Sum, Min, Max:**
```json
GET /products/_search
{
  "size": 0,
  "aggs": {
    "avg_price": {
      "avg": { "field": "price" }
    },
    "max_price": {
      "max": { "field": "price" }
    }
  }
}
```

### Bucket Aggregations

**Terms Aggregation:**
```json
GET /products/_search
{
  "size": 0,
  "aggs": {
    "categories": {
      "terms": {
        "field": "category.keyword",
        "size": 10
      }
    }
  }
}
```

**Date Histogram:**
```json
GET /logs/_search
{
  "size": 0,
  "aggs": {
    "errors_over_time": {
      "date_histogram": {
        "field": "timestamp",
        "calendar_interval": "1h"
      }
    }
  }
}
```

## Scalability and Performance

### Sharding Strategy

**Shard Configuration:**
```json
// Create index with custom shard settings
PUT /products
{
  "settings": {
    "number_of_shards": 5,
    "number_of_replicas": 1
  }
}
```

**Best Practices:**
- **Shard Size**: 10-50GB per shard
- **Shard Count**: Plan for growth (hard to change later)
- **Replicas**: At least 1 replica for high availability

### Cluster Management

**Cluster Health:**
```json
GET /_cluster/health
{
  "cluster_name": "my-cluster",
  "status": "green",
  "number_of_nodes": 3,
  "number_of_data_nodes": 3
}
```

**Node Roles:**
- **Master Node**: Manages cluster state
- **Data Node**: Stores data and executes queries
- **Ingest Node**: Pre-processes documents
- **Coordinating Node**: Routes requests (default role)

## Use Cases and Patterns

### 1. E-Commerce Search

**Requirements:**
- Product search with relevance
- Faceted search (filters)
- Autocomplete
- Spell correction

**Implementation:**
```json
// Index with mapping
PUT /products
{
  "mappings": {
    "properties": {
      "title": {
        "type": "text",
        "analyzer": "standard",
        "fields": {
          "keyword": { "type": "keyword" }
        }
      },
      "price": { "type": "float" },
      "category": { "type": "keyword" }
    }
  }
}

// Faceted search
GET /products/_search
{
  "query": { "match": { "title": "laptop" }},
  "aggs": {
    "categories": {
      "terms": { "field": "category.keyword" }
    },
    "price_ranges": {
      "range": {
        "field": "price",
        "ranges": [
          { "to": 500 },
          { "from": 500, "to": 1000 },
          { "from": 1000 }
        ]
      }
    }
  }
}
```

### 2. Log Analytics (ELK Stack)

**Components:**
- **Elasticsearch**: Storage and search
- **Logstash**: Log processing
- **Kibana**: Visualization

**Pattern:**
```
Logs → Logstash → Elasticsearch → Kibana
```

**Index Template:**
```json
PUT /_template/logs-template
{
  "index_patterns": ["logs-*"],
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 1
  },
  "mappings": {
    "properties": {
      "timestamp": { "type": "date" },
      "level": { "type": "keyword" },
      "message": { "type": "text" }
    }
  }
}
```

### 3. Time-Series Data

**Use Cases:**
- Metrics and monitoring
- IoT data
- Financial data

**Index Pattern:**
```json
// Daily indices: metrics-2025-12-29
PUT /metrics-2025-12-29
{
  "settings": {
    "number_of_shards": 1
  }
}
```

## Best Practices

### Index Design

**1. Index per Time Period:**
- Daily indices: `logs-2025-12-29`
- Weekly indices: `logs-2025-w52`
- Monthly indices: `logs-2025-12`

**2. Index Templates:**
```json
PUT /_template/logs-template
{
  "index_patterns": ["logs-*"],
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 1
  }
}
```

**3. Index Lifecycle Management:**
- Hot: Recent data (SSD, fast)
- Warm: Older data (HDD, slower)
- Cold: Archive data (cheap storage)
- Delete: Very old data

### Query Optimization

**1. Use Filters for Exact Matches:**
```json
// Good: Filter (cached)
{
  "query": {
    "bool": {
      "filter": [
        { "term": { "status": "active" }}
      ]
    }
  }
}

// Bad: Query (not cached)
{
  "query": {
    "term": { "status": "active" }
  }
}
```

**2. Limit Result Size:**
```json
GET /products/_search
{
  "size": 20,  // Limit results
  "from": 0    // Pagination
}
```

**3. Use Source Filtering:**
```json
GET /products/_search
{
  "_source": ["title", "price"],  // Only return needed fields
  "query": { "match_all": {} }
}
```

### Performance Tuning

**1. Refresh Interval:**
```json
PUT /products/_settings
{
  "index": {
    "refresh_interval": "30s"  // Reduce refresh frequency
  }
}
```

**2. Bulk Operations:**
```json
// Bulk index (faster than individual requests)
POST /products/_bulk
{"index":{}}
{"title":"Product 1"}
{"index":{}}
{"title":"Product 2"}
```

**3. Mapping Optimization:**
- Use `keyword` for exact matches
- Use `text` for full-text search
- Disable `_source` if not needed (saves storage)

## Common Patterns

### Autocomplete

**Completion Suggester:**
```json
PUT /products
{
  "mappings": {
    "properties": {
      "title": {
        "type": "completion"
      }
    }
  }
}

// Search
GET /products/_search
{
  "suggest": {
    "title_suggest": {
      "prefix": "iph",
      "completion": {
        "field": "title"
      }
    }
  }
}
```

### Fuzzy Search

**Fuzzy Query:**
```json
GET /products/_search
{
  "query": {
    "fuzzy": {
      "title": {
        "value": "lapto",
        "fuzziness": "AUTO"
      }
    }
  }
}
```

### Highlighting

**Highlight Matches:**
```json
GET /products/_search
{
  "query": { "match": { "title": "laptop" }},
  "highlight": {
    "fields": {
      "title": {}
    }
  }
}
```

## What Interviewers Look For

### Search Engine Skills

1. **Full-Text Search Understanding**
   - Understanding of indexing and search
   - Relevance scoring
   - Query types and optimization
   - **Red Flags**: No search understanding, poor queries, no optimization

2. **Distributed Search Architecture**
   - Sharding and replication
   - Cluster management
   - Horizontal scaling
   - **Red Flags**: No sharding strategy, single node, no scaling

3. **Analytics Capabilities**
   - Aggregations
   - Real-time analytics
   - Time-series handling
   - **Red Flags**: No aggregations, no analytics, poor time-series

### Problem-Solving Approach

1. **Index Design**
   - Proper index structure
   - Mapping optimization
   - Lifecycle management
   - **Red Flags**: Poor index design, no lifecycle, inefficient mappings

2. **Query Optimization**
   - Efficient queries
   - Filter vs query
   - Performance tuning
   - **Red Flags**: Inefficient queries, no optimization, poor performance

### System Design Skills

1. **Scalability**
   - Horizontal scaling
   - Shard management
   - Cluster design
   - **Red Flags**: Vertical scaling only, no sharding, poor cluster design

2. **Use Case Application**
   - Search engines
   - Log analytics
   - Real-time analytics
   - **Red Flags**: Wrong use cases, no application, poor understanding

### Communication Skills

1. **Clear Explanation**
   - Explains search concepts
   - Discusses trade-offs
   - Justifies design decisions
   - **Red Flags**: Unclear explanations, no justification, confusing

### Meta-Specific Focus

1. **Search Engine Expertise**
   - Understanding of search engines
   - Elasticsearch mastery
   - Real-world application
   - **Key**: Demonstrate search engine expertise

## Summary

**Elasticsearch Key Points:**
- **Distributed Search**: Horizontal scaling with sharding
- **Real-Time**: Near real-time indexing and search
- **Full-Text Search**: Powerful text search with relevance
- **Analytics**: Aggregations for data analysis
- **RESTful API**: Simple HTTP-based interface

**Common Use Cases:**
- Full-text search (e-commerce, content)
- Log analytics (ELK stack)
- Real-time analytics (metrics, dashboards)
- Time-series data (monitoring, IoT)

**Best Practices:**
- Index per time period
- Use filters for exact matches
- Optimize mappings
- Bulk operations for performance
- Index lifecycle management

Elasticsearch is a powerful tool for building search engines, log analytics, and real-time data exploration systems with horizontal scalability and near real-time performance.

