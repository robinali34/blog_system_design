---
layout: post
title: "Design a File Storage and Sync System (Dropbox/Google Drive) - System Design Interview"
date: 2025-11-14
categories: [System Design, Interview Example, Distributed Systems, Storage Systems]
excerpt: "A comprehensive guide to designing a file storage and synchronization system like Dropbox or Google Drive, covering file upload/download, multi-device sync, conflict resolution, delta sync, versioning, sharing, and architectural patterns for handling petabytes of data and millions of concurrent users."
---

## Introduction

A file storage and synchronization system enables users to store files in the cloud and access them from multiple devices with automatic synchronization. Systems like Dropbox and Google Drive handle petabytes of data, millions of users, and billions of file operations per day, requiring efficient storage, real-time synchronization, conflict resolution, and bandwidth optimization.

This post provides a detailed walkthrough of designing a scalable file storage and sync system, covering key architectural decisions, delta synchronization, conflict resolution, versioning, and scalability challenges. This is one of the most common system design interview questions that tests your understanding of distributed systems, storage systems, real-time synchronization, and handling massive scale.

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Requirements](#requirements)
   - [Functional Requirements](#functional-requirements)
   - [Non-Functional Requirements](#non-functional-requirements)
3. [Capacity Estimation](#capacity-estimation)
   - [Traffic Estimates](#traffic-estimates)
   - [Storage Estimates](#storage-estimates)
   - [Bandwidth Estimates](#bandwidth-estimates)
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
   - [Scalability Considerations](#scalability-considerations)
   - [Security Considerations](#security-considerations)
   - [Monitoring & Observability](#monitoring--observability)
   - [Trade-offs and Optimizations](#trade-offs-and-optimizations)
10. [Summary](#summary)

## Problem Statement

**Design a file storage and synchronization system similar to Dropbox or Google Drive with the following features:**

1. File upload and download
2. File synchronization across multiple devices
3. Real-time sync (changes propagate quickly)
4. Conflict resolution when same file edited on multiple devices
5. File versioning and history
6. File sharing and collaboration
7. Folder hierarchy and organization
8. Search functionality
9. Delta sync (only sync changed parts)
10. Offline access with sync when online

**Scale Requirements:**
- 500 million+ users
- 100 million+ daily active users
- 1 billion+ files
- 10 petabytes+ total storage
- 100 million+ file operations per day
- Peak: 1 million concurrent users
- Average file size: 10MB
- Large files: Up to 10GB

## Requirements

### Functional Requirements

**Core Features:**
1. **File Management**: Upload, download, delete, rename files
2. **Folder Management**: Create, delete, organize folders
3. **Synchronization**: Sync files across devices automatically
4. **Versioning**: Keep file history and allow rollback
5. **Sharing**: Share files/folders with other users
6. **Collaboration**: Multiple users edit same file
7. **Search**: Search files by name, content, metadata
8. **Offline Access**: Access files offline, sync when online
9. **Delta Sync**: Only sync changed parts of files
10. **Conflict Resolution**: Handle conflicts when same file edited simultaneously

**Out of Scope:**
- Real-time collaborative editing (like Google Docs)
- Advanced file preview/editing
- Video streaming
- Mobile app (focus on web API)

### Non-Functional Requirements

1. **Availability**: 99.9% uptime
2. **Reliability**: No data loss, guaranteed file storage
3. **Performance**: 
   - Upload: < 5 seconds for 10MB file
   - Download: < 3 seconds for 10MB file
   - Sync latency: < 1 second for small changes
4. **Scalability**: Handle 1B+ files, 10PB+ storage
5. **Consistency**: Strong consistency for metadata, eventual for sync
6. **Durability**: 99.999999999% (11 9's) durability
7. **Bandwidth Efficiency**: Minimize data transfer with delta sync

## Capacity Estimation

### Traffic Estimates

- **Total Users**: 500 million
- **Daily Active Users (DAU)**: 100 million
- **File Operations per Day**: 100 million
- **Uploads per Day**: 50 million
- **Downloads per Day**: 200 million
- **Sync Operations per Day**: 500 million
- **Peak Concurrent Users**: 1 million
- **Peak QPS**: 10,000 operations/second
- **Normal QPS**: 1,000 operations/second

### Storage Estimates

**File Storage:**
- 1 billion files × 10MB average = 10PB
- With replication (3x): 30PB
- With versioning (5 versions average): 50PB

**Metadata Storage:**
- 1B files × 1KB metadata = 1TB
- User metadata: 500M users × 2KB = 1TB
- Sharing metadata: 100M shares × 500 bytes = 50GB
- Total metadata: ~2TB

**Total Storage**: ~50PB

### Bandwidth Estimates

**Upload Bandwidth:**
- 50M uploads/day × 10MB = 500TB/day = 5.8GB/s average
- Peak: 10K uploads/sec × 10MB = 100GB/s = 800Gbps

**Download Bandwidth:**
- 200M downloads/day × 10MB = 2PB/day = 23GB/s average
- Peak: 10K downloads/sec × 10MB = 100GB/s = 800Gbps

**Sync Bandwidth:**
- 500M sync ops/day × 1MB (delta) = 500TB/day = 5.8GB/s average
- Peak: 10K sync ops/sec × 1MB = 10GB/s = 80Gbps

**Total Peak Bandwidth**: ~1.68Tbps

## Core Entities

### User
- `user_id` (UUID)
- `email`
- `username`
- `password_hash`
- `storage_quota` (bytes)
- `storage_used` (bytes)
- `created_at`
- `updated_at`

### File
- `file_id` (UUID)
- `user_id`
- `name`
- `path` (full path including folders)
- `parent_folder_id`
- `file_type` (file, folder)
- `size` (bytes)
- `content_hash` (SHA-256)
- `mime_type`
- `version` (INT)
- `created_at`
- `updated_at`
- `deleted_at`

### File Version
- `version_id` (UUID)
- `file_id`
- `version_number` (INT)
- `content_hash`
- `size`
- `created_at`
- `created_by` (user_id)

### File Chunk
- `chunk_id` (UUID)
- `file_id`
- `version_id`
- `chunk_index` (INT)
- `chunk_hash` (SHA-256)
- `size` (bytes)
- `storage_url` (S3 URL)

### Device
- `device_id` (UUID)
- `user_id`
- `device_name`
- `device_type` (desktop, mobile, web)
- `last_sync_at`
- `sync_token` (for incremental sync)

### Sync Event
- `event_id` (UUID)
- `file_id`
- `user_id`
- `device_id`
- `event_type` (create, update, delete, move)
- `timestamp`
- `metadata` (JSON)

### Share
- `share_id` (UUID)
- `file_id`
- `owner_id`
- `shared_with_id` (user_id)
- `permission` (read, write, admin)
- `created_at`
- `expires_at`

## API

### 1. Upload File
```
POST /api/v1/files/upload
Request: multipart/form-data
  - file: file data
  - path: /folder/file.txt
  - parent_folder_id: uuid

Response:
{
  "file_id": "uuid",
  "name": "file.txt",
  "path": "/folder/file.txt",
  "size": 1048576,
  "version": 1,
  "created_at": "2025-11-13T10:00:00Z"
}
```

### 2. Download File
```
GET /api/v1/files/{file_id}/download
Response: file stream with appropriate headers
```

### 3. Get File Metadata
```
GET /api/v1/files/{file_id}
Response:
{
  "file_id": "uuid",
  "name": "file.txt",
  "path": "/folder/file.txt",
  "size": 1048576,
  "version": 5,
  "mime_type": "text/plain",
  "created_at": "2025-11-13T10:00:00Z",
  "updated_at": "2025-11-13T15:30:00Z"
}
```

### 4. Sync Files (Get Changes)
```
GET /api/v1/sync?device_id=uuid&sync_token=token&limit=100
Response:
{
  "sync_token": "new_token",
  "changes": [
    {
      "file_id": "uuid",
      "event_type": "update",
      "path": "/folder/file.txt",
      "version": 6,
      "timestamp": "2025-11-13T15:30:00Z"
    }
  ],
  "has_more": false
}
```

### 5. Update File (Delta Sync)
```
POST /api/v1/files/{file_id}/update
Request:
{
  "chunks": [
    {
      "chunk_index": 0,
      "chunk_hash": "abc123",
      "data": "base64_encoded_data"
    }
  ],
  "new_content_hash": "def456"
}

Response:
{
  "file_id": "uuid",
  "version": 6,
  "updated_at": "2025-11-13T15:30:00Z"
}
```

### 6. Share File
```
POST /api/v1/files/{file_id}/share
Request:
{
  "shared_with_id": "user_uuid",
  "permission": "read"
}

Response:
{
  "share_id": "uuid",
  "file_id": "uuid",
  "shared_with_id": "user_uuid",
  "permission": "read",
  "created_at": "2025-11-13T10:00:00Z"
}
```

### 7. Get File Versions
```
GET /api/v1/files/{file_id}/versions
Response:
{
  "versions": [
    {
      "version_id": "uuid",
      "version_number": 5,
      "size": 1048576,
      "created_at": "2025-11-13T15:30:00Z",
      "created_by": "user_uuid"
    }
  ]
}
```

### 8. Restore File Version
```
POST /api/v1/files/{file_id}/restore
Request:
{
  "version_number": 3
}

Response:
{
  "file_id": "uuid",
  "version": 6,
  "restored_from_version": 3
}
```

## Data Flow

### File Upload Flow

1. **Client Uploads File**:
   - Client sends file to **API Gateway**
   - **API Gateway** routes to **File Service**
   - **File Service** validates file and user quota

2. **File Processing**:
   - **File Service**:
     - Chunks file into blocks (e.g., 4MB chunks)
     - Computes hash for each chunk
     - Checks for duplicate chunks (deduplication)
     - Uploads unique chunks to **Object Storage** (S3)
     - Creates file metadata record

3. **Metadata Storage**:
   - **File Service** stores file metadata in **Metadata DB**
   - Creates file version record
   - Updates user storage quota
   - Publishes sync event to **Message Queue**

4. **Sync Notification**:
   - **Sync Service** consumes sync event
   - Notifies other devices of file change
   - Updates sync tokens

### File Download Flow

1. **Client Requests Download**:
   - Client requests file download
   - **File Service** retrieves file metadata
   - Gets chunk list from metadata

2. **Chunk Retrieval**:
   - **File Service** retrieves chunks from **Object Storage**
   - Assembles chunks in order
   - Streams file to client

3. **Caching**:
   - **CDN** caches popular files
   - Reduces load on object storage
   - Improves download speed

### Sync Flow

1. **Client Requests Sync**:
   - Client sends sync request with device_id and sync_token
   - **Sync Service** queries changes since last sync

2. **Change Detection**:
   - **Sync Service**:
     - Queries sync events since sync_token
     - Filters events for user's files
     - Returns list of changes

3. **Client Processes Changes**:
   - Client receives changes
   - Downloads updated files
   - Applies changes locally
   - Updates sync_token

### Delta Sync Flow

1. **File Changed Locally**:
   - Client detects file change
   - Computes file chunks and hashes
   - Compares with server version

2. **Delta Calculation**:
   - Client identifies changed chunks
   - Uploads only changed chunks
   - Sends chunk metadata to server

3. **Server Processing**:
   - **File Service** receives delta update
   - Merges chunks with existing file
   - Creates new file version
   - Publishes sync event

## Database Design

### Schema Design

**Users Table:**
```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    storage_quota BIGINT DEFAULT 10737418240, -- 10GB default
    storage_used BIGINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_email (email)
);
```

**Files Table:**
```sql
CREATE TABLE files (
    file_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    name VARCHAR(500) NOT NULL,
    path VARCHAR(2000) NOT NULL,
    parent_folder_id UUID,
    file_type ENUM('file', 'folder') NOT NULL,
    size BIGINT DEFAULT 0,
    content_hash VARCHAR(64),
    mime_type VARCHAR(100),
    version INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_path (path),
    INDEX idx_parent_folder (parent_folder_id),
    INDEX idx_user_path (user_id, path),
    INDEX idx_deleted_at (deleted_at)
);
```

**File Versions Table:**
```sql
CREATE TABLE file_versions (
    version_id UUID PRIMARY KEY,
    file_id UUID NOT NULL,
    version_number INT NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    size BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    created_by UUID,
    INDEX idx_file_id (file_id),
    INDEX idx_file_version (file_id, version_number),
    UNIQUE KEY uk_file_version (file_id, version_number)
);
```

**File Chunks Table:**
```sql
CREATE TABLE file_chunks (
    chunk_id UUID PRIMARY KEY,
    file_id UUID NOT NULL,
    version_id UUID NOT NULL,
    chunk_index INT NOT NULL,
    chunk_hash VARCHAR(64) NOT NULL,
    size BIGINT NOT NULL,
    storage_url VARCHAR(500) NOT NULL,
    INDEX idx_file_version (file_id, version_id),
    INDEX idx_chunk_hash (chunk_hash),
    INDEX idx_file_chunk (file_id, chunk_index)
);
```

**Devices Table:**
```sql
CREATE TABLE devices (
    device_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    device_name VARCHAR(200),
    device_type VARCHAR(50),
    last_sync_at TIMESTAMP,
    sync_token VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_id (user_id),
    INDEX idx_sync_token (sync_token)
);
```

**Sync Events Table:**
```sql
CREATE TABLE sync_events (
    event_id UUID PRIMARY KEY,
    file_id UUID NOT NULL,
    user_id UUID NOT NULL,
    device_id UUID,
    event_type ENUM('create', 'update', 'delete', 'move', 'rename') NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    metadata JSON,
    INDEX idx_user_timestamp (user_id, timestamp DESC),
    INDEX idx_file_id (file_id),
    INDEX idx_timestamp (timestamp DESC)
);
```

**Shares Table:**
```sql
CREATE TABLE shares (
    share_id UUID PRIMARY KEY,
    file_id UUID NOT NULL,
    owner_id UUID NOT NULL,
    shared_with_id UUID NOT NULL,
    permission ENUM('read', 'write', 'admin') DEFAULT 'read',
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NULL,
    INDEX idx_file_id (file_id),
    INDEX idx_shared_with (shared_with_id),
    INDEX idx_owner (owner_id)
);
```

### Database Sharding Strategy

**Files Table Sharding:**
- Shard by user_id using consistent hashing
- 1000 shards: `shard_id = hash(user_id) % 1000`
- All files for a user in same shard
- Enables efficient user queries

**Sync Events Sharding:**
- Shard by user_id (same as files)
- Enables efficient sync queries
- Time-based partitioning for cleanup

**Shard Key Selection:**
- `user_id` ensures all user data in same shard
- Enables efficient queries for user's files
- Prevents cross-shard queries for single user

**Replication:**
- Each shard replicated 3x for high availability
- Master-replica setup for read scaling
- Writes go to master, reads can go to replicas

## High-Level Design

```
┌─────────────┐
│   Client    │
│  (Web App)  │
└──────┬──────┘
       │
       │ HTTP/HTTPS
       │
┌──────▼──────────────────────────────────────────────┐
│        API Gateway / Load Balancer                   │
│        - Rate Limiting                               │
│        - Request Routing                             │
└──────┬──────────────────────────────────────────────┘
       │
       ├──────────────┬──────────────┬──────────────┐
       │              │              │              │
┌──────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
│   File      │ │   Sync     │ │  Share     │ │  Search   │
│   Service   │ │   Service  │ │  Service   │ │  Service  │
└──────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
       │              │              │              │
       │              │              │              │
┌──────▼──────────────▼──────────────▼──────────────▼──────┐
│              Message Queue (Kafka)                        │
│              - File events                                │
│              - Sync events                                │
│              - Share events                                │
└──────┬─────────────────────────────────────────────────────┘
       │
       │
┌──────▼─────────────────────────────────────────────────────┐
│         Database Cluster (Sharded by user_id)              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│  │ Shard 0   │  │ Shard 1   │  │ Shard N   │                │
│  │ Files     │  │ Files     │  │ Files     │                │
│  │ Metadata  │  │ Metadata  │  │ Metadata  │                │
│  └──────────┘  └──────────┘  └──────────┘                │
│                                                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│  │ Sync     │  │ Shares   │  │ Users    │                │
│  │ Events   │  │ DB       │  │ DB       │                │
│  └──────────┘  └──────────┘  └──────────┘                │
└───────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────┐
│              Object Storage (S3)                            │
│  - File chunks                                             │
│  - Deduplication                                           │
│  - Versioning                                              │
└───────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────┐
│              Cache Layer (Redis)                           │
│  - File metadata cache                                     │
│  - Sync token cache                                        │
│  - Chunk hash cache (deduplication)                        │
└───────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────┐
│              CDN                                           │
│  - Popular file caching                                    │
│  - Download acceleration                                   │
└───────────────────────────────────────────────────────────┘
```

## Deep Dive

### Component Design

#### 1. File Service

**Responsibilities:**
- Handle file upload/download
- Manage file metadata
- Chunk files for storage
- Handle deduplication
- Manage file versions

**Key Design Decisions:**
- **Chunking**: Split files into fixed-size chunks (4MB)
- **Deduplication**: Store chunks by hash, reuse across files
- **Versioning**: Create new version on each update
- **Metadata**: Store metadata separately from file content

**Scalability:**
- Stateless service, horizontally scalable
- Connection pooling for database
- Async processing for large files

#### 2. Sync Service

**Responsibilities:**
- Track file changes
- Provide sync API for clients
- Manage sync tokens
- Handle conflict detection
- Notify devices of changes

**Key Design Decisions:**
- **Sync Events**: Store all file changes as events
- **Sync Tokens**: Use tokens for incremental sync
- **Conflict Detection**: Detect simultaneous edits
- **Real-Time**: Use WebSocket for real-time notifications

**Implementation:**
```python
def get_sync_changes(user_id, device_id, sync_token):
    # Get events since last sync
    if sync_token:
        events = get_events_since_token(user_id, sync_token)
    else:
        # First sync: get all files
        events = get_all_file_events(user_id)
    
    # Filter events for this user
    changes = []
    for event in events:
        change = {
            'file_id': event.file_id,
            'event_type': event.event_type,
            'path': get_file_path(event.file_id),
            'version': get_file_version(event.file_id),
            'timestamp': event.timestamp
        }
        changes.append(change)
    
    # Generate new sync token
    new_sync_token = generate_sync_token(user_id, device_id)
    
    return {
        'sync_token': new_sync_token,
        'changes': changes,
        'has_more': len(changes) >= 100
    }
```

#### 3. Chunking and Deduplication

**Challenge:** Store files efficiently and avoid duplicate storage

**Solution:**
- **Fixed-Size Chunking**: Split files into fixed-size chunks (4MB)
- **Content-Based Hashing**: Hash each chunk (SHA-256)
- **Deduplication**: Store chunks by hash, reuse across files
- **Chunk Index**: Maintain index of chunks per file

**Implementation:**
```python
def upload_file(file_data, user_id, path):
    # Chunk file
    chunks = chunk_file(file_data, chunk_size=4*1024*1024)  # 4MB
    
    # Compute hashes and upload unique chunks
    chunk_hashes = []
    chunk_urls = []
    
    for chunk in chunks:
        chunk_hash = sha256(chunk).hexdigest()
        
        # Check if chunk already exists
        existing_chunk = get_chunk_by_hash(chunk_hash)
        
        if existing_chunk:
            # Reuse existing chunk
            chunk_url = existing_chunk.storage_url
        else:
            # Upload new chunk
            chunk_url = upload_to_s3(chunk, chunk_hash)
            store_chunk_metadata(chunk_hash, chunk_url, len(chunk))
        
        chunk_hashes.append(chunk_hash)
        chunk_urls.append(chunk_url)
    
    # Create file metadata
    file_id = create_file_metadata(
        user_id=user_id,
        path=path,
        size=len(file_data),
        content_hash=sha256(file_data).hexdigest(),
        chunks=chunk_hashes
    )
    
    return file_id
```

#### 4. Delta Sync (Incremental Sync)

**Challenge:** Sync only changed parts of files

**Solution:**
- **Chunk-Based Delta**: Compare chunks between versions
- **Rolling Hash**: Use rolling hash for efficient comparison
- **Upload Only Changes**: Upload only changed chunks
- **Merge on Server**: Merge chunks on server side

**Implementation:**
```python
def delta_sync(file_id, new_file_data, device_id):
    # Get current file version
    current_version = get_file_version(file_id)
    current_chunks = get_file_chunks(file_id, current_version)
    
    # Chunk new file
    new_chunks = chunk_file(new_file_data, chunk_size=4*1024*1024)
    new_chunk_hashes = [sha256(chunk).hexdigest() for chunk in new_chunks]
    
    # Find changed chunks
    changed_chunks = []
    for i, (new_hash, new_chunk) in enumerate(zip(new_chunk_hashes, new_chunks)):
        if i >= len(current_chunks) or new_hash != current_chunks[i].chunk_hash:
            changed_chunks.append({
                'index': i,
                'hash': new_hash,
                'data': new_chunk
            })
    
    # Upload changed chunks
    chunk_urls = []
    for chunk_info in changed_chunks:
        chunk_url = upload_to_s3(chunk_info['data'], chunk_info['hash'])
        chunk_urls.append((chunk_info['index'], chunk_url))
    
    # Create new version with merged chunks
    new_version = create_file_version(
        file_id=file_id,
        chunks=merge_chunks(current_chunks, chunk_urls),
        content_hash=sha256(new_file_data).hexdigest()
    )
    
    # Publish sync event
    publish_sync_event(file_id, 'update', device_id)
    
    return new_version
```

#### 5. Conflict Resolution

**Challenge:** Handle conflicts when same file edited on multiple devices

**Solution:**
- **Last-Write-Wins**: Default strategy (simple)
- **Version Vectors**: Track versions per device
- **Conflict Detection**: Detect simultaneous edits
- **Conflict Files**: Create conflict copies when detected

**Implementation:**
```python
def handle_file_update(file_id, new_version, device_id):
    current_file = get_file(file_id)
    
    # Check for conflicts
    if current_file.version != new_version.base_version:
        # Conflict detected: versions don't match
        conflict_file = create_conflict_file(
            file_id=file_id,
            conflicting_version=new_version,
            device_id=device_id
        )
        
        # Notify user of conflict
        notify_user_conflict(file_id, conflict_file)
        
        return {
            'status': 'conflict',
            'conflict_file_id': conflict_file.file_id
        }
    
    # No conflict: update file
    updated_file = update_file(file_id, new_version)
    
    return {
        'status': 'success',
        'file_id': file_id,
        'version': updated_file.version
    }
```

### Detailed Design

#### File Chunking Strategy

**Fixed-Size Chunking:**
- Chunk size: 4MB (balance between overhead and efficiency)
- Simple and fast
- Good for random access
- Less efficient for insertions

**Content-Defined Chunking (CDC):**
- Variable-size chunks based on content
- Better deduplication
- More complex
- Better for insertions

**Decision:** Use fixed-size chunking for simplicity and performance

#### Deduplication Strategy

**Chunk-Level Deduplication:**
- Store chunks by hash
- Multiple files can share chunks
- Significant storage savings (30-50%)
- Reduces storage costs

**File-Level Deduplication:**
- Store files by hash
- Entire file deduplication
- Simpler but less efficient
- Used for small files

**Implementation:**
```python
def get_or_upload_chunk(chunk_data):
    chunk_hash = sha256(chunk_data).hexdigest()
    
    # Check cache first
    cached_chunk = cache.get(f"chunk:{chunk_hash}")
    if cached_chunk:
        return cached_chunk['url']
    
    # Check database
    existing_chunk = db.query("SELECT storage_url FROM chunks WHERE chunk_hash = ?", chunk_hash)
    if existing_chunk:
        cache.set(f"chunk:{chunk_hash}", {'url': existing_chunk.storage_url})
        return existing_chunk.storage_url
    
    # Upload new chunk
    chunk_url = upload_to_s3(chunk_data, chunk_hash)
    
    # Store metadata
    db.execute(
        "INSERT INTO chunks (chunk_hash, storage_url, size) VALUES (?, ?, ?)",
        chunk_hash, chunk_url, len(chunk_data)
    )
    
    cache.set(f"chunk:{chunk_hash}", {'url': chunk_url})
    return chunk_url
```

#### Versioning Strategy

**Snapshot Versioning:**
- Store full file for each version
- Simple but storage-intensive
- Fast restore

**Delta Versioning:**
- Store only changes between versions
- Storage-efficient
- More complex restore

**Decision:** Use chunk-based versioning (store new chunks, reference old chunks)

#### Sync Token Management

**Challenge:** Efficiently track sync state per device

**Solution:**
- **Sync Tokens**: Opaque tokens representing sync state
- **Event-Based**: Token represents last processed event ID
- **Incremental**: Only return changes since token
- **Expiration**: Tokens expire after inactivity

**Implementation:**
```python
def generate_sync_token(user_id, device_id):
    # Get last event ID for user
    last_event = get_last_sync_event(user_id)
    
    # Create token with event ID and timestamp
    token_data = {
        'user_id': user_id,
        'device_id': device_id,
        'last_event_id': last_event.event_id if last_event else None,
        'timestamp': now()
    }
    
    # Encode token
    token = base64_encode(json.dumps(token_data))
    
    # Store token
    update_device_sync_token(device_id, token)
    
    return token

def get_events_since_token(user_id, sync_token):
    # Decode token
    token_data = json.loads(base64_decode(sync_token))
    last_event_id = token_data.get('last_event_id')
    
    if last_event_id:
        # Get events since last event
        events = db.query(
            "SELECT * FROM sync_events WHERE user_id = ? AND event_id > ? ORDER BY timestamp",
            user_id, last_event_id
        )
    else:
        # First sync: get all events
        events = db.query(
            "SELECT * FROM sync_events WHERE user_id = ? ORDER BY timestamp",
            user_id
        )
    
    return events
```

### Scalability Considerations

#### Horizontal Scaling

**File Service:**
- Stateless service, horizontally scalable
- Load balancer distributes requests
- Connection pooling for database
- Async processing for large files

**Sync Service:**
- Stateless service, horizontally scalable
- Shared database for sync events
- WebSocket connections for real-time sync
- Connection pooling

#### Storage Scaling

**Object Storage:**
- S3 for file chunks
- Automatic scaling
- CDN for popular files
- Lifecycle policies for old versions

**Database:**
- Shard by user_id
- Read replicas for read scaling
- Connection pooling
- Index optimization

#### Caching Strategy

**Redis Cache:**
- **File Metadata**: TTL 1 hour
- **Chunk Hashes**: TTL 24 hours (for deduplication)
- **Sync Tokens**: TTL 1 hour
- **User Quota**: TTL 5 minutes

**Cache Invalidation:**
- Invalidate on file updates
- Invalidate on sync events
- Use cache-aside pattern

### Security Considerations

#### Authentication & Authorization

- **JWT Tokens**: Use JWT for API authentication
- **File Access Control**: Verify user owns file or has share permission
- **Rate Limiting**: Limit requests per user/IP
- **Quota Enforcement**: Enforce storage quotas

#### Data Security

- **Encryption at Rest**: Encrypt files in object storage
- **Encryption in Transit**: TLS for all communications
- **Access Control**: Fine-grained permissions
- **Audit Logging**: Log all file operations

#### File Sharing Security

- **Share Links**: Generate secure share links
- **Permission Levels**: Read, write, admin permissions
- **Expiration**: Share links expire after time
- **Access Logging**: Track share access

### Monitoring & Observability

#### Key Metrics

**System Metrics:**
- Upload/download rate (files/second)
- Storage usage (total, per user)
- Sync latency (p50, p95, p99)
- Chunk deduplication rate
- Cache hit rate

**Business Metrics:**
- Total files stored
- Total storage used
- Active users
- Files shared
- Storage savings from deduplication

#### Logging

- **Structured Logging**: JSON logs for parsing
- **File Operations**: Log uploads, downloads, deletes
- **Sync Operations**: Log sync events
- **Error Logging**: Log errors with context

#### Alerting

- **High Storage Usage**: Alert if storage > 80% capacity
- **High Latency**: Alert if p99 latency > 5 seconds
- **High Error Rate**: Alert if error rate > 1%
- **Sync Failures**: Alert on sync failures

### Trade-offs and Optimizations

#### Trade-offs

**1. Chunk Size: Small vs Large**
- **Small (1MB)**: Better deduplication, more overhead
- **Large (8MB)**: Less overhead, worse deduplication
- **Decision**: 4MB balance

**2. Sync Frequency: Real-Time vs Batch**
- **Real-Time**: Lower latency, higher cost
- **Batch**: Higher latency, lower cost
- **Decision**: Real-time with batching optimization

**3. Versioning: Many vs Few Versions**
- **Many**: Better history, more storage
- **Few**: Less storage, less history
- **Decision**: Keep 5 versions, archive older

**4. Deduplication: Aggressive vs Conservative**
- **Aggressive**: More storage savings, more computation
- **Conservative**: Less computation, less savings
- **Decision**: Aggressive chunk-level deduplication

#### Optimizations

**1. Chunk Deduplication**
- Cache chunk hashes
- Batch chunk lookups
- Reduce storage costs by 30-50%

**2. Delta Sync**
- Only sync changed chunks
- Reduce bandwidth by 80-90%
- Faster sync for large files

**3. CDN Caching**
- Cache popular files
- Reduce load on object storage
- Improve download speed

**4. Compression**
- Compress chunks before storage
- Reduce storage by 30-50%
- Trade-off: CPU usage

## Summary

Designing a file storage and sync system at scale requires careful consideration of:

1. **Chunking and Deduplication**: Efficient storage with chunk-level deduplication
2. **Delta Sync**: Only sync changed parts for bandwidth efficiency
3. **Versioning**: Track file history with chunk-based versioning
4. **Conflict Resolution**: Handle simultaneous edits gracefully
5. **Sync Mechanism**: Event-based sync with tokens for incremental updates
6. **Scalability**: Horizontal scaling with sharding and caching
7. **Storage Efficiency**: Deduplication saves 30-50% storage
8. **Real-Time Sync**: Sub-second sync latency for small changes

Key architectural decisions:
- **Chunk-Based Storage** (4MB chunks) for efficiency
- **Chunk-Level Deduplication** for storage savings
- **Delta Sync** for bandwidth optimization
- **Event-Based Sync** with tokens for incremental updates
- **Sharded Database** by user_id for scalability
- **Object Storage** (S3) for file chunks
- **CDN** for popular file caching

The system handles 1 billion files, 10 petabytes of storage, and 100 million file operations per day with efficient deduplication and delta sync.

