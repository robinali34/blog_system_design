---
layout: post
title: "Design a Smart Glass System: Voice-Controlled Memory Video Creation"
date: 2025-11-08
categories: [System Design, Smart Glass, Video Processing, NLP, Architecture, CQRS]
excerpt: "A comprehensive system design for smart glasses that enables voice-controlled photo/video capture and automatic memory video creation using natural language queries, covering read-heavy search vs write-heavy video processing architecture."
---

## Introduction

Smart glasses represent the next frontier in wearable technology, combining augmented reality, computer vision, and voice control to create immersive experiences. One of the most compelling use cases is automatic memory creation—users can simply say "Create a memory video of my wife and me in Paris" and the system intelligently finds, trims, and merges relevant video clips.

This post designs a scalable system architecture for smart glasses that handles voice-controlled media capture and intelligent memory video generation, with a focus on managing read-heavy search queries and write-heavy video ingestion/processing workloads.

---

## Problem Statement

### Functional Requirements

1. **Voice-Controlled Media Capture**
   - Users can take pictures/videos using voice commands
   - "Take a picture"
   - "Record a video"
   - "Stop recording"

2. **Natural Language Memory Creation**
   - Users can request memory videos using natural language
   - Example: "Create a memory video of my wife and me in Paris"
   - System finds related video clips from user's albums
   - Automatically trims and merges clips into 2-minute video
   - Returns result quickly (< 2-5 seconds)

3. **Intelligent Video Search**
   - Search by location, people, objects, time
   - Semantic search using natural language
   - Face recognition and person identification
   - Object and scene detection

4. **Video Processing**
   - Automatic video trimming
   - Clip merging and transitions
   - Video enhancement and optimization
   - Thumbnail generation

### Non-Functional Requirements

- **High Read Concurrency**: Many users searching simultaneously
- **High Write Throughput**: Videos being uploaded and processed continuously
- **Scalability**: Handle millions of users and billions of video clips
- **Low Latency**: Memory video creation in 2-5 seconds
- **Durability**: Videos and metadata never lost
- **Availability**: 99.9% uptime
- **Cost Efficiency**: Optimize storage and processing costs

---

## System Requirements Analysis

### Scale Estimates

**Users:**
- 10 million active users
- 1 million concurrent users during peak hours

**Media:**
- Average user uploads 10 videos/day
- Average video size: 50MB (1080p, 30 seconds)
- Daily uploads: 100 million videos = 5TB/day
- Storage: 1.8PB/year (with 3x replication = 5.4PB)

**Queries:**
- 50 million memory video requests/day
- Peak: 100K requests/second
- Average query processes 10-20 video clips

**Processing:**
- Video processing: 2-5 seconds per memory video
- Concurrent processing: 10K videos/second

---

## Workload Analysis

### Read-Heavy Operations

| Operation | Type | Frequency | Notes |
|-----------|------|-----------|-------|
| Video metadata search | Read-heavy | 50M/day | Users querying by text tags, NLP embeddings |
| Recent memories lookup | Read-heavy | 100M/day | Frequently accessed, can cache |
| User album browsing | Read-heavy | 200M/day | Paginated queries |
| Face/person search | Read-heavy | 30M/day | Vector similarity search |

**Characteristics:**
- High read concurrency
- Need fast search (sub-second)
- Can benefit from caching
- Requires semantic/vector search

### Write-Heavy Operations

| Operation | Type | Frequency | Notes |
|-----------|------|-----------|-------|
| Video upload | Write-heavy | 100M/day | Large files to blob storage |
| Metadata ingestion | Write-heavy | 100M/day | Metadata inserted on upload |
| Video trimming jobs | Write-heavy | 50M/day | Async video processing |
| Metadata updates (tags, embeddings) | Write | 200M/day | AI processing updates |

**Characteristics:**
- High write throughput
- Large file storage
- Async processing needed
- Batch processing for efficiency

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────┐
│      Smart Glasses / Mobile App         │
│  (Voice Control, Media Capture)        │
└──────────────┬──────────────────────────┘
               │
               │ HTTPS / WebSocket
               │
┌──────────────▼──────────────────────────┐
│         API Gateway / Load Balancer     │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴───────┐
       │               │
┌──────▼──────┐  ┌─────▼──────┐
│  Read Path  │  │ Write Path │
│  (Search)   │  │ (Ingestion)│
└─────────────┘  └────────────┘
       │               │
       │               │
┌──────▼──────┐  ┌─────▼──────┐
│   Cache     │  │   Queue    │
│  (Redis)    │  │  (Kafka)   │
└─────────────┘  └────────────┘
       │               │
┌──────▼──────┐  ┌─────▼──────┐
│  Read DB    │  │  Write DB  │
│(Elasticsearch│  │ (Cassandra)│
│  Vector DB) │  │            │
└─────────────┘  └────────────┘
       │               │
       └───────┬───────┘
               │
       ┌───────▼───────┐
       │ Blob Storage  │
       │ (S3/Azure Blob)│
       └───────────────┘
```

### Architecture Principles

1. **CQRS Pattern**: Separate read and write paths
2. **Event-Driven**: Async processing for video operations
3. **Microservices**: Independent scaling of components
4. **Caching**: Multiple cache layers for performance
5. **Horizontal Scaling**: All components scale independently

---

## Component Design

### 1. Smart Glasses / Mobile App

**Responsibilities:**
- Voice command capture and processing
- Media capture (photos/videos)
- Upload to cloud
- Display memory videos
- Offline mode support

**Key Features:**
- Voice recognition (on-device or cloud)
- Real-time video preview
- Background upload
- Local caching for offline access

**Technology:**
- Native mobile apps (iOS/Android)
- WebRTC for real-time video
- Local SQLite for metadata cache

---

### 2. API Gateway

**Responsibilities:**
- Request routing
- Authentication and authorization
- Rate limiting
- Request/response transformation
- Load balancing

**Features:**
- JWT token validation
- User quota management
- Request throttling
- API versioning

**Technology:**
- AWS API Gateway
- Azure API Management
- Kong / Envoy

---

### 3. Write Path (Write-Heavy)

#### 3.1 Video Upload Service

**Flow:**
```
Smart Glass → Upload Service → Blob Storage → Metadata Extraction → Write DB
```

**Process:**
1. Receive video upload (chunked upload for large files)
2. Store video in blob storage (S3/Azure Blob)
3. Trigger metadata extraction
4. Insert metadata into write-optimized DB
5. Queue video for processing

**Optimizations:**
- Chunked uploads (resumable)
- Compression before upload
- Direct upload to blob storage (signed URLs)
- Async metadata extraction

#### 3.2 Metadata Extraction Service

**Extracted Metadata:**
- **Temporal**: Timestamp, duration
- **Spatial**: GPS coordinates, location name
- **People**: Face detection, person identification
- **Objects**: Scene detection, object recognition
- **Embeddings**: Vector embeddings for semantic search
- **Audio**: Speech-to-text, audio features
- **Video**: Resolution, fps, codec

**AI/ML Models:**
- Face recognition (AWS Rekognition, Azure Face API)
- Object detection (YOLO, TensorFlow)
- Scene classification (CNN models)
- NLP embeddings (BERT, OpenAI embeddings)
- Speech-to-text (Whisper, Google Speech)

**Technology:**
- Microservice architecture
- GPU clusters for ML inference
- Batch processing for cost efficiency
- Real-time processing for recent videos

#### 3.3 Write Database

**Requirements:**
- High write throughput (100M writes/day)
- Scalable and distributed
- Flexible schema for metadata
- Fast ingestion

**Database Choice: Cassandra / DynamoDB**

**Why:**
- Excellent write performance
- Horizontal scaling
- NoSQL flexibility for metadata
- High availability

**Schema Design (Cassandra):**
```sql
CREATE TABLE video_metadata (
    video_id UUID PRIMARY KEY,
    user_id UUID,
    upload_timestamp TIMESTAMP,
    blob_url TEXT,
    duration_seconds INT,
    location_name TEXT,
    gps_lat DOUBLE,
    gps_lon DOUBLE,
    detected_faces LIST<UUID>,  -- Person IDs
    detected_objects LIST<TEXT>,
    scene_tags LIST<TEXT>,
    embedding_vector BLOB,  -- Vector embedding
    processing_status TEXT,
    created_at TIMESTAMP
);

CREATE INDEX ON video_metadata (user_id);
CREATE INDEX ON video_metadata (location_name);
```

**Partitioning:**
- Partition by `user_id` for user queries
- Replication factor: 3
- Consistency level: QUORUM for writes

#### 3.4 Video Processing Queue

**Purpose:**
- Async video processing (trimming, merging)
- Decouple upload from processing
- Handle burst traffic
- Retry failed processing

**Queue Choice: Kafka**

**Why:**
- High throughput (millions of messages/second)
- Message replayability
- Multiple consumer groups
- Long retention for reprocessing

**Topics:**
- `video-uploads`: New video uploads
- `video-processing`: Video trimming/merging jobs
- `metadata-updates`: Metadata enrichment
- `memory-video-creation`: Memory video generation requests

**Message Format:**
```json
{
  "video_id": "uuid",
  "user_id": "uuid",
  "operation": "trim|merge|create_memory",
  "parameters": {
    "start_time": 10,
    "end_time": 30,
    "clip_ids": ["uuid1", "uuid2"]
  },
  "priority": "high|normal|low",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### 3.5 Video Processing Workers

**Responsibilities:**
- Video trimming
- Clip merging
- Video encoding/transcoding
- Thumbnail generation
- Quality optimization

**Technology:**
- FFmpeg for video processing
- GPU acceleration (NVENC)
- Containerized workers (Docker/Kubernetes)
- Auto-scaling based on queue depth

**Processing Pipeline:**
```
Video Clip → Decode → Trim/Merge → Encode → Upload → Update Metadata
```

**Optimization:**
- Parallel processing
- GPU acceleration
- Adaptive bitrate encoding
- Caching intermediate results

---

### 4. Read Path (Read-Heavy)

#### 4.1 Query Processing Service

**Flow:**
```
User Query → NLP Processing → Cache Check → Search DB → Fetch Videos → Process → Return
```

**Natural Language Processing:**
1. **Intent Recognition**: Extract intent (create memory video)
2. **Entity Extraction**: Extract entities (wife, Paris, date range)
3. **Query Expansion**: Expand to related terms
4. **Vector Embedding**: Convert to embedding vector

**Example Query Processing:**
```
Input: "Create a memory video of my wife and me in Paris"

Processing:
- Intent: CREATE_MEMORY_VIDEO
- Entities:
  - People: ["wife", "me"]
  - Location: "Paris"
  - Relationship: "wife" → person_id mapping
- Time: (optional, default: all time)
- Embedding: [0.123, 0.456, ...] (768-dim vector)
```

#### 4.2 Cache Layer (Redis)

**Purpose:**
- Cache hot query results
- Cache frequently accessed metadata
- Cache user-specific data
- Reduce database load

**Cache Strategy:**

1. **Query Result Cache**
   ```
   Key: user:{user_id}:query:{query_hash}
   Value: {video_ids: [...], metadata: {...}}
   TTL: 10 minutes
   ```

2. **Recent Memories Cache**
   ```
   Key: user:{user_id}:recent:memories
   Value: List of recent memory video IDs
   TTL: 1 hour
   ```

3. **Metadata Cache**
   ```
   Key: video:{video_id}:metadata
   Value: Video metadata JSON
   TTL: 1 hour
   ```

4. **User Profile Cache**
   ```
   Key: user:{user_id}:profile
   Value: User profile, person mappings
   TTL: 24 hours
   ```

**Cache Invalidation:**
- Invalidate on video upload
- Invalidate on metadata update
- TTL-based expiration
- Manual invalidation API

#### 4.3 Read Database - Search Engine

**Database Choice: Elasticsearch**

**Why:**
- Full-text search capabilities
- Vector search support (kNN)
- Fast search performance
- Horizontal scaling
- Rich query DSL

**Index Design:**
```json
{
  "mappings": {
    "properties": {
      "video_id": {"type": "keyword"},
      "user_id": {"type": "keyword"},
      "upload_timestamp": {"type": "date"},
      "location_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
      "gps": {"type": "geo_point"},
      "detected_faces": {"type": "keyword"},
      "detected_objects": {"type": "text"},
      "scene_tags": {"type": "text"},
      "embedding_vector": {
        "type": "dense_vector",
        "dims": 768,
        "index": true,
        "similarity": "cosine"
      },
      "duration_seconds": {"type": "integer"},
      "processing_status": {"type": "keyword"}
    }
  }
}
```

**Search Queries:**

1. **Text Search** (location, tags):
```json
{
  "query": {
    "bool": {
      "must": [
        {"match": {"location_name": "Paris"}},
        {"terms": {"detected_faces": ["person_123", "person_456"]}}
      ],
      "filter": [
        {"term": {"user_id": "user_789"}},
        {"range": {"upload_timestamp": {"gte": "2024-01-01"}}}
      ]
    }
  }
}
```

2. **Vector Search** (semantic similarity):
```json
{
  "query": {
    "script_score": {
      "query": {"match_all": {}},
      "script": {
        "source": "cosineSimilarity(params.query_vector, 'embedding_vector') + 1.0",
        "params": {"query_vector": [0.123, 0.456, ...]}
      }
    }
  }
}
```

3. **Hybrid Search** (text + vector):
```json
{
  "query": {
    "bool": {
      "should": [
        {"match": {"location_name": "Paris"}},
        {"script_score": {
          "script": {
            "source": "cosineSimilarity(params.query_vector, 'embedding_vector') + 1.0",
            "params": {"query_vector": [...]}
          }
        }}
      ],
      "minimum_should_match": 1
    }
  }
}
```

#### 4.4 Vector Database (Alternative/Complementary)

**Database Choice: Milvus / Pinecone / Weaviate**

**Why:**
- Optimized for vector search
- Better performance for large-scale vector search
- Advanced vector indexing (IVF, HNSW)
- Can complement Elasticsearch

**Use Cases:**
- Primary vector search for semantic queries
- Person similarity search
- Scene similarity search
- Cross-modal search (text-to-video)

**Integration:**
- Use for pure vector search queries
- Elasticsearch for hybrid (text + vector) queries
- Sync embeddings between systems

---

### 5. Memory Video Creation Service

**Workflow:**

```
User Query → Query Processing → Search Videos → Select Clips → 
Trim & Merge → Generate Video → Store → Return URL
```

**Step-by-Step:**

1. **Query Processing**
   - Parse natural language query
   - Extract entities (people, location, time)
   - Generate search criteria

2. **Video Search**
   - Search Elasticsearch/Vector DB
   - Filter by user, location, people, time
   - Rank by relevance
   - Select top N clips (10-20 clips)

3. **Clip Selection Algorithm**
   ```python
   def select_clips(videos, target_duration=120):
       # Sort by relevance score
       sorted_videos = sort_by_relevance(videos)
       
       # Select clips covering time range
       selected = []
       total_duration = 0
       
       for video in sorted_videos:
           # Extract best segment (e.g., 10-15 seconds)
           segment = extract_best_segment(video)
           
           if total_duration + segment.duration <= target_duration:
               selected.append(segment)
               total_duration += segment.duration
           else:
               break
       
       return selected
   ```

4. **Video Processing**
   - Trim selected clips
   - Add transitions
   - Merge into single video
   - Add music/effects (optional)
   - Generate thumbnail

5. **Optimization**
   - Cache common queries
   - Pre-generate popular memories
   - Use GPU acceleration
   - Parallel processing

**Performance Optimization:**
- **Caching**: Cache common memory videos
- **Pre-computation**: Pre-generate popular memories
- **Lazy Generation**: Generate on-demand, cache result
- **Progressive Loading**: Return partial results quickly

---

### 6. Blob Storage

**Storage Choice: S3 / Azure Blob Storage**

**Organization:**
```
s3://smart-glass-videos/
  ├── raw/
  │   └── {user_id}/
  │       └── {year}/{month}/{day}/
  │           └── {video_id}.mp4
  ├── processed/
  │   └── {user_id}/
  │       └── {video_id}/
  │           ├── 1080p.mp4
  │           ├── 720p.mp4
  │           └── thumbnail.jpg
  └── memories/
      └── {user_id}/
          └── {memory_id}.mp4
```

**Features:**
- Lifecycle policies (move to cheaper storage)
- CDN integration (CloudFront, Azure CDN)
- Versioning for recovery
- Encryption at rest
- Cross-region replication

**Optimization:**
- Use different storage tiers
- Hot: Recent videos (S3 Standard)
- Warm: Older videos (S3 Standard-IA)
- Cold: Archived videos (S3 Glacier)

---

## Data Flow Examples

### Example 1: Video Upload Flow

```
1. Smart Glass captures video
   ↓
2. Upload Service receives chunked upload
   ↓
3. Store in S3 (direct upload with signed URL)
   ↓
4. Publish to Kafka topic: video-uploads
   ↓
5. Metadata Extraction Service processes:
   - Extract faces → Identify people
   - Detect objects/scenes
   - Generate embeddings
   - Extract GPS, timestamp
   ↓
6. Insert metadata into Cassandra (write DB)
   ↓
7. Index metadata in Elasticsearch (read DB)
   ↓
8. Cache metadata in Redis
   ↓
9. Trigger video processing (trimming, encoding)
```

### Example 2: Memory Video Creation Flow

```
1. User: "Create a memory video of my wife and me in Paris"
   ↓
2. API Gateway receives request
   ↓
3. Query Processing Service:
   - NLP: Extract "wife", "me", "Paris"
   - Map "wife" → person_id (from user profile)
   - Generate query embedding
   ↓
4. Check Redis cache:
   - Key: user:{user_id}:query:{hash}
   - If hit → return cached result
   ↓
5. If cache miss → Search Elasticsearch:
   - Filter: user_id, location="Paris", faces=[wife_id, user_id]
   - Vector search: semantic similarity
   - Return top 20 clips
   ↓
6. Fetch video metadata from Cassandra
   ↓
7. Select best clips (algorithm):
   - Rank by relevance
   - Select segments totaling ~2 minutes
   ↓
8. Video Processing:
   - Trim clips
   - Merge with transitions
   - Generate video
   ↓
9. Store in S3 (memories bucket)
   ↓
10. Update metadata, cache result
    ↓
11. Return video URL to user
```

---

## Scalability & Performance

### Read Scaling

**Strategies:**
1. **Read Replicas**: Multiple Elasticsearch replicas
2. **Caching**: Multi-layer caching (Redis, CDN)
3. **Sharding**: Partition data by user_id
4. **CDN**: Cache popular memory videos
5. **Query Optimization**: Index optimization, query tuning

**Metrics:**
- Elasticsearch: 10+ nodes, 3 replicas per shard
- Redis: Cluster mode, 6+ nodes
- CDN: Global edge locations

### Write Scaling

**Strategies:**
1. **Horizontal Partitioning**: Cassandra sharding by user_id
2. **Async Processing**: Queue-based processing
3. **Batch Processing**: Batch metadata updates
4. **Direct Upload**: Signed URLs for direct S3 upload
5. **Worker Scaling**: Auto-scale processing workers

**Metrics:**
- Cassandra: 10+ nodes, replication factor 3
- Kafka: 6+ brokers, 3 partitions per topic
- Processing Workers: Auto-scale 10-1000 instances

### Performance Targets

| Operation | Target Latency | Throughput |
|-----------|---------------|-------------|
| Video Upload | < 5s | 100K uploads/sec |
| Metadata Search | < 500ms | 100K queries/sec |
| Memory Video Creation | < 5s | 10K creations/sec |
| Video Processing | < 30s | 10K videos/sec |

---

## Reliability & Durability

### Data Durability

1. **Video Storage**
   - S3: 99.999999999% (11 9's) durability
   - Cross-region replication
   - Versioning enabled

2. **Metadata**
   - Cassandra: Replication factor 3
   - Elasticsearch: Replica count 2
   - Regular backups

3. **Queue**
   - Kafka: Replication factor 3
   - Message retention: 7 days
   - Idempotent producers

### High Availability

1. **Multi-Region Deployment**
   - Active-active regions
   - Data replication across regions
   - Failover mechanisms

2. **Health Checks**
   - Service health endpoints
   - Database connectivity checks
   - Queue depth monitoring

3. **Circuit Breakers**
   - Prevent cascade failures
   - Fallback mechanisms
   - Graceful degradation

### Disaster Recovery

1. **Backup Strategy**
   - Daily backups of metadata
   - S3 versioning for videos
   - Point-in-time recovery

2. **Recovery Procedures**
   - RTO: 1 hour
   - RPO: 15 minutes
   - Automated failover

---

## Security & Privacy

### Authentication & Authorization

1. **User Authentication**
   - OAuth 2.0 / JWT tokens
   - Multi-factor authentication
   - Device registration

2. **Authorization**
   - User can only access own videos
   - Role-based access control
   - API key management

### Data Privacy

1. **Encryption**
   - Encryption at rest (AES-256)
   - Encryption in transit (TLS 1.3)
   - End-to-end encryption (optional)

2. **Face Recognition**
   - On-device processing option
   - User consent for face recognition
   - GDPR compliance

3. **Data Retention**
   - User-controlled retention
   - Automatic deletion policies
   - Right to deletion

---

## Cost Optimization

### Storage Costs

1. **Storage Tiers**
   - Hot: Recent videos (S3 Standard)
   - Warm: 30-90 days (S3 Standard-IA)
   - Cold: Archive (S3 Glacier)

2. **Compression**
   - Video compression (H.265)
   - Metadata compression
   - Efficient encoding

### Compute Costs

1. **Processing Optimization**
   - GPU acceleration (cheaper than CPU)
   - Batch processing
   - Spot instances for non-critical jobs

2. **Caching**
   - Reduce database queries
   - CDN for video delivery
   - Cache hit ratio > 80%

### Database Costs

1. **Right-Sizing**
   - Appropriate instance types
   - Reserved instances for steady load
   - Auto-scaling

---

## Monitoring & Observability

### Key Metrics

1. **Performance Metrics**
   - API latency (p50, p95, p99)
   - Video processing time
   - Search query latency
   - Cache hit ratio

2. **System Metrics**
   - CPU, memory, disk usage
   - Queue depth
   - Database connection pool
   - Error rates

3. **Business Metrics**
   - Videos uploaded per day
   - Memory videos created
   - Active users
   - Storage usage

### Logging

1. **Structured Logging**
   - JSON format
   - Correlation IDs
   - Centralized logging (ELK stack)

2. **Distributed Tracing**
   - Request tracing across services
   - Performance profiling
   - Error tracking

### Alerting

1. **Critical Alerts**
   - Service downtime
   - High error rates
   - Storage capacity
   - Queue backlog

---

## Technology Stack Summary

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **API Gateway** | AWS API Gateway / Kong | Request routing, auth, rate limiting |
| **Write DB** | Cassandra / DynamoDB | High write throughput, scalability |
| **Read DB** | Elasticsearch | Full-text + vector search |
| **Vector DB** | Milvus / Pinecone | Optimized vector search |
| **Cache** | Redis Cluster | Fast in-memory caching |
| **Queue** | Kafka | High throughput, replayability |
| **Blob Storage** | S3 / Azure Blob | Scalable object storage |
| **Video Processing** | FFmpeg + GPU | Video encoding/transcoding |
| **ML/AI** | AWS Rekognition / Custom | Face recognition, object detection |
| **NLP** | BERT / OpenAI Embeddings | Natural language understanding |
| **CDN** | CloudFront / Azure CDN | Global content delivery |

---

## Future Enhancements

1. **Real-Time Collaboration**
   - Shared memory videos
   - Collaborative editing
   - Real-time notifications

2. **Advanced AI Features**
   - Automatic video editing
   - Music selection
   - Story generation
   - Emotion detection

3. **AR Integration**
   - Overlay memories in AR view
   - Location-based memory triggers
   - Augmented reality previews

4. **Social Features**
   - Share memory videos
   - Comments and reactions
   - Memory collections

---

## Conclusion

This smart glass system design addresses the unique challenges of handling both read-heavy search queries and write-heavy video processing workloads through:

1. **CQRS Architecture**: Separating read and write paths
2. **Appropriate Database Choices**: Cassandra for writes, Elasticsearch for reads
3. **Multi-Layer Caching**: Redis for hot data, CDN for videos
4. **Async Processing**: Kafka queue for video operations
5. **Horizontal Scaling**: All components scale independently

**Key Design Decisions:**
- **Write Path**: Cassandra + Kafka for high throughput
- **Read Path**: Elasticsearch + Redis for fast search
- **Storage**: S3 with lifecycle policies for cost optimization
- **Processing**: Async workers with GPU acceleration

The system is designed to scale to millions of users while maintaining low latency for memory video creation and high reliability for video storage and processing.

