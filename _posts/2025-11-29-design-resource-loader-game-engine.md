---
layout: post
title: "Design a Resource Loader in a Game Engine - System Design Interview"
date: 2025-11-29
categories: [System Design, Interview Example, Game Engine, Client Systems, Low-Level Design, Performance]
excerpt: "A comprehensive guide to designing a resource loading system for a game engine that handles asset discovery, fetching from local packages and remote CDNs, processing operations (decryption, decompression), and efficient caching with support for prioritization, concurrency control, and memory budgeting."
---

## Introduction

Designing a resource loader for a game engine is a complex client-side systems problem that tests your ability to build efficient, low-latency asset pipelines. The system must discover, fetch, and prepare game assets (textures, meshes, audio, shaders) from both local application packages and remote CDNs, then transform them into formats ready for CPU/GPU consumption.

This post provides a detailed walkthrough of designing a resource loader system, covering key architectural decisions, multi-stage pipelines, cache hierarchies, security, prioritization, concurrency control, and memory/IO budgeting. This is a common system design interview question that tests your understanding of client-side systems, game engine architecture, performance optimization, and production-grade robustness.

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Requirements](#requirements)
   - [Functional Requirements](#functional-requirements)
   - [Non-Functional Requirements](#non-functional-requirements)
3. [Capacity Estimation](#capacity-estimation)
   - [Resource Estimates](#resource-estimates)
   - [Storage Estimates](#storage-estimates)
4. [Core Entities](#core-entities)
5. [API](#api)
6. [Data Flow](#data-flow)
7. [High-Level Design](#high-level-design)
8. [Deep Dive](#deep-dive)
   - [Component Design](#component-design)
   - [Multi-Stage Pipeline](#multi-stage-pipeline)
   - [Cache Hierarchy](#cache-hierarchy)
   - [Prioritization System](#prioritization-system)
   - [Concurrency Control](#concurrency-control)
   - [Memory and IO Budgeting](#memory-and-io-budgeting)
   - [Security and Integrity](#security-and-integrity)
   - [Failure Handling](#failure-handling)
   - [Offline and Online Support](#offline-and-online-support)
   - [Trade-offs and Optimizations](#trade-offs-and-optimizations)
9. [What Interviewers Look For](#what-interviewers-look-for)
10. [Summary](#summary)

## Problem Statement

**Design a resource loading system for a game engine that:**

1. Discovers and fetches assets from local application packages and remote CDNs
2. Processes assets through multi-stage pipelines (decryption, decompression, transcoding)
3. Transforms assets into formats ready for CPU/GPU consumption
4. Manages cache hierarchies (memory, disk, CDN)
5. Handles prioritization, concurrency control, and memory/IO budgeting
6. Ensures security (encryption, integrity checks)
7. Supports both offline and online sources
8. Avoids duplicated work and prevents jank

**Scale Requirements:**
- 10,000+ unique assets per game
- 100+ concurrent asset loads
- 1GB+ total asset size per level
- < 100ms latency for cached assets
- < 2 seconds for uncached assets (local)
- < 5 seconds for uncached assets (CDN)
- Support for assets from 1KB to 100MB

**Key Challenges:**
- Multi-stage pipelines with dependencies
- Low-latency IO on constrained devices (mobile, console)
- Cache hierarchies with different access patterns
- Security (encryption, integrity verification)
- Failure handling and retry logic
- Prioritization (critical vs. background assets)
- Concurrency control (avoid duplicate loads)
- Memory/IO budgeting (prevent resource exhaustion)
- Avoiding jank (smooth frame rates)

## Requirements

### Functional Requirements

**Core Features:**
1. **Asset Discovery**: Discover assets from local packages and remote CDNs
2. **Asset Fetching**: Fetch assets from multiple sources (local, CDN)
3. **Asset Processing**: Decrypt, decompress, transcode assets
4. **Asset Loading**: Load processed assets into memory (CPU/GPU ready)
5. **Caching**: Multi-level caching (memory, disk, CDN)
6. **Prioritization**: Load critical assets first
7. **Concurrency**: Handle multiple concurrent asset loads
8. **Offline Support**: Work with local assets when offline

**Asset Types:**
- Textures (PNG, JPG, DDS, KTX)
- Meshes (OBJ, FBX, GLTF)
- Audio (WAV, MP3, OGG)
- Shaders (GLSL, HLSL)
- Animations (JSON, Binary)
- Scripts (Lua, JavaScript)

**Processing Operations:**
- Decryption (encrypted assets)
- Decompression (compressed formats)
- Transcoding (format conversion)
- Validation (integrity checks)
- Optimization (platform-specific)

**Out of Scope:**
- Asset authoring tools
- Asset versioning system
- Asset streaming (focus on loading)
- Asset hot-reloading (focus on initial load)

### Non-Functional Requirements

1. **Performance**: 
   - Cached asset load: < 100ms (P95)
   - Local asset load: < 2 seconds (P95)
   - CDN asset load: < 5 seconds (P95)
   - No frame drops during loading
2. **Memory Efficiency**: 
   - Memory budget per level: 500MB
   - Efficient memory usage
   - Memory cleanup (unload unused assets)
3. **IO Efficiency**: 
   - IO budget: 50MB/s read
   - Efficient disk access
   - Minimize disk seeks
4. **Reliability**: 
   - No asset corruption
   - Graceful failure handling
   - Retry logic for failed loads
5. **Security**: 
   - Encryption for sensitive assets
   - Integrity verification (checksums)
   - Secure CDN communication (HTTPS)
6. **Scalability**: 
   - Handle 100+ concurrent loads
   - Support large asset catalogs (10K+ assets)
   - Efficient resource utilization

## Capacity Estimation

### Resource Estimates

**Assets Per Game:**
- Unique assets: 10,000+
- Average asset size: 1MB
- Total asset size: 10GB+
- Per-level assets: 1GB (1000 assets)

**Concurrent Loads:**
- Peak concurrent loads: 100+
- Average load time: 2 seconds
- Throughput: 50 assets/second

**Memory Usage:**
- Memory budget: 500MB per level
- Average asset in memory: 5MB
- Max assets in memory: 100 assets

**IO Bandwidth:**
- Disk read: 50MB/s
- Network (CDN): 10MB/s (mobile)
- Network (CDN): 100MB/s (desktop)

### Storage Estimates

**Local Package Storage:**
- Base game assets: 5GB
- Per-level assets: 1GB each
- Total local storage: 10GB+

**Disk Cache:**
- Cached processed assets: 2GB
- Cache eviction: LRU policy
- Cache TTL: 7 days

**Memory Cache:**
- Hot assets in memory: 500MB
- LRU eviction
- Immediate cleanup on level unload

## Core Entities

### Asset
- **Attributes**: asset_id, asset_type, source (local/cdn), path, size, checksum, encryption_key, compression_type
- **Relationships**: Has processing pipeline, has cache entries
- **Purpose**: Represents a game asset

### AssetRequest
- **Attributes**: request_id, asset_id, priority, callback, timeout, retry_count
- **Relationships**: Links to asset, has loading state
- **Purpose**: Represents an asset load request

### ProcessingStage
- **Attributes**: stage_id, stage_type (fetch, decrypt, decompress, transcode, validate), dependencies, timeout
- **Relationships**: Part of processing pipeline
- **Purpose**: Represents a processing stage

### CacheEntry
- **Attributes**: cache_key, asset_id, location (memory/disk/cdn), size, access_time, hit_count
- **Relationships**: Links to asset
- **Purpose**: Represents a cached asset

### LoadQueue
- **Attributes**: queue_id, priority, max_concurrent, current_loads
- **Relationships**: Contains asset requests
- **Purpose**: Manages prioritized asset loading

## API

### 1. Load Asset
```
ResourceLoader::LoadAsset(
    asset_id: string,
    priority: Priority,
    callback: function,
    timeout: int = 5000
) -> request_id

// Priority: CRITICAL, HIGH, NORMAL, LOW, BACKGROUND
```

### 2. Unload Asset
```
ResourceLoader::UnloadAsset(asset_id: string) -> bool
```

### 3. Preload Assets
```
ResourceLoader::PreloadAssets(
    asset_ids: array<string>,
    priority: Priority = NORMAL
) -> array<request_id>
```

### 4. Get Asset Status
```
ResourceLoader::GetAssetStatus(asset_id: string) -> AssetStatus
// Status: NOT_LOADED, LOADING, LOADED, FAILED
```

### 5. Get Cache Info
```
ResourceLoader::GetCacheInfo(asset_id: string) -> CacheInfo
// Returns: location, size, access_time
```

### 6. Clear Cache
```
ResourceLoader::ClearCache(
    cache_type: CacheType,  // MEMORY, DISK, ALL
    older_than: timestamp = null
) -> int  // Returns number of assets cleared
```

## Data Flow

### Asset Loading Flow

```
1. Game requests asset:
   a. ResourceLoader::LoadAsset(asset_id, priority, callback)
   b. Check cache hierarchy:
      - Memory cache (fastest)
      - Disk cache (medium)
      - CDN cache (slowest)
   
2. If not cached:
   a. Create AssetRequest
   b. Add to LoadQueue (prioritized)
   c. Processing pipeline:
      - Stage 1: Fetch (local or CDN)
      - Stage 2: Decrypt (if encrypted)
      - Stage 3: Decompress (if compressed)
      - Stage 4: Transcode (if needed)
      - Stage 5: Validate (checksum)
      - Stage 6: Load into memory
   d. Store in cache hierarchy
   e. Invoke callback with asset data

3. If cached:
   a. Load from cache
   b. Update access time
   c. Invoke callback immediately
```

### Processing Pipeline Flow

```
1. Fetch Stage:
   a. Check source (local or CDN)
   b. If local: Read from package
   c. If CDN: Download via HTTP/HTTPS
   d. Stream to next stage

2. Decrypt Stage:
   a. Get encryption key
   b. Decrypt asset data
   c. Stream to next stage

3. Decompress Stage:
   a. Detect compression type
   b. Decompress asset data
   c. Stream to next stage

4. Transcode Stage:
   a. Detect target format
   b. Transcode asset (if needed)
   c. Stream to next stage

5. Validate Stage:
   a. Calculate checksum
   b. Verify against expected checksum
   c. Stream to next stage

6. Load Stage:
   a. Allocate memory
   b. Copy asset data to memory
   c. Create asset handle
   d. Return to caller
```

## High-Level Design

```
┌─────────────────────────────────────────────────────────┐
│                    Game Engine                          │
│              (Requests Assets)                          │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ LoadAsset(asset_id, priority)
                     │
┌────────────────────▼────────────────────────────────────┐
│              Resource Loader                            │
│  (Orchestrates Loading, Prioritization, Caching)        │
└──────┬───────────────────────────────────┬───────────┘
       │                                       │
       │                                       │
┌──────▼──────────┐                  ┌────────▼───────────┐
│  Load Queue     │                  │  Cache Manager     │
│  (Prioritized)  │                  │  (Multi-Level)      │
└──────┬──────────┘                  └────────┬───────────┘
       │                                       │
       │                                       │
┌──────▼───────────────────────────────────────▼───────────┐
│         Processing Pipeline                             │
│  Fetch → Decrypt → Decompress → Transcode → Validate   │
└──────┬─────────────────────────────────────────────────┘
       │
       │
┌──────▼──────────┐              ┌──────────────┐
│  Local Source   │              │  CDN Source  │
│  (App Package)  │              │  (Remote)    │
└─────────────────┘              └──────────────┘

┌─────────────────────────────────────────────────────────┐
│              Cache Hierarchy                            │
│  L1: Memory Cache (Hot Assets)                         │
│  L2: Disk Cache (Processed Assets)                      │
│  L3: CDN Cache (Remote Assets)                          │
└─────────────────────────────────────────────────────────┘
```

## Deep Dive

### Component Design

#### 1. Resource Loader (Main Orchestrator)
- **Responsibilities**: Coordinate asset loading, manage queues, handle callbacks
- **Optimization**: 
  - Efficient request routing
  - Priority-based scheduling
  - Duplicate request detection

#### 2. Load Queue (Prioritization)
- **Responsibilities**: Manage prioritized asset requests
- **Optimization**:
  - Priority queues (critical first)
  - Concurrency limits per priority
  - Fair scheduling

#### 3. Processing Pipeline
- **Responsibilities**: Execute multi-stage asset processing
- **Optimization**:
  - Streaming between stages
  - Parallel processing where possible
  - Error handling per stage

#### 4. Cache Manager
- **Responsibilities**: Manage multi-level cache hierarchy
- **Optimization**:
  - LRU eviction
  - Cache warming
  - Efficient lookups

#### 5. Source Manager
- **Responsibilities**: Handle local and CDN sources
- **Optimization**:
  - Connection pooling
  - Retry logic
  - Bandwidth management

### Multi-Stage Pipeline

#### Pipeline Architecture

**Stages:**
1. **Fetch**: Get raw asset data
2. **Decrypt**: Decrypt encrypted assets
3. **Decompress**: Decompress compressed assets
4. **Transcode**: Convert to target format
5. **Validate**: Verify integrity
6. **Load**: Load into memory

**Streaming Between Stages:**
```cpp
class ProcessingPipeline {
    void ProcessAsset(AssetRequest& request) {
        // Stage 1: Fetch
        auto fetched_data = FetchStage::Execute(request.asset_id);
        
        // Stage 2: Decrypt (if needed)
        auto decrypted_data = request.asset.encrypted 
            ? DecryptStage::Execute(fetched_data, request.asset.encryption_key)
            : fetched_data;
        
        // Stage 3: Decompress (if needed)
        auto decompressed_data = request.asset.compressed
            ? DecompressStage::Execute(decrypted_data, request.asset.compression_type)
            : decrypted_data;
        
        // Stage 4: Transcode (if needed)
        auto transcoded_data = TranscodeStage::Execute(
            decompressed_data, 
            request.asset.asset_type,
            GetTargetFormat(request.asset.asset_type)
        );
        
        // Stage 5: Validate
        if (!ValidateStage::Execute(transcoded_data, request.asset.checksum)) {
            throw IntegrityError("Checksum mismatch");
        }
        
        // Stage 6: Load into memory
        auto loaded_asset = LoadStage::Execute(transcoded_data);
        
        // Store in cache
        CacheManager::Store(request.asset_id, loaded_asset);
        
        // Invoke callback
        request.callback(loaded_asset);
    }
};
```

**Parallel Processing:**
- Independent stages can run in parallel
- Use thread pool for CPU-intensive stages
- Pipeline parallelism (multiple assets in different stages)

### Cache Hierarchy

#### Three-Level Cache

**L1: Memory Cache (Hot Assets)**
- **Location**: RAM
- **Size**: 500MB
- **Access Time**: < 1ms
- **Eviction**: LRU
- **Use Case**: Frequently accessed assets, current level assets

**L2: Disk Cache (Processed Assets)**
- **Location**: Local disk
- **Size**: 2GB
- **Access Time**: 10-50ms
- **Eviction**: LRU, TTL (7 days)
- **Use Case**: Processed assets (decrypted, decompressed, transcoded)

**L3: CDN Cache (Remote Assets)**
- **Location**: CDN edge servers
- **Size**: Unlimited
- **Access Time**: 100-500ms (network dependent)
- **Eviction**: CDN policy
- **Use Case**: Original assets, fallback when local not available

**Cache Lookup Strategy:**
```cpp
AssetHandle CacheManager::GetAsset(AssetId asset_id) {
    // L1: Memory cache
    if (auto asset = memory_cache.Get(asset_id)) {
        return asset;
    }
    
    // L2: Disk cache
    if (auto asset = disk_cache.Get(asset_id)) {
        // Promote to memory cache
        memory_cache.Store(asset_id, asset);
        return asset;
    }
    
    // L3: CDN cache (fallback)
    if (auto asset = cdn_cache.Get(asset_id)) {
        // Store in disk cache
        disk_cache.Store(asset_id, asset);
        return asset;
    }
    
    return nullptr;  // Not cached, need to load
}
```

### Prioritization System

#### Priority Levels

**CRITICAL**: 
- Assets needed for current frame
- Blocking gameplay
- Load immediately, highest priority

**HIGH**: 
- Assets needed soon (next few seconds)
- Important for gameplay
- Load after critical

**NORMAL**: 
- Standard priority
- Load in order

**LOW**: 
- Background assets
- Load when resources available

**BACKGROUND**: 
- Prefetch assets
- Load when idle

**Priority Queue Implementation:**
```cpp
class LoadQueue {
    std::priority_queue<AssetRequest> critical_queue;
    std::priority_queue<AssetRequest> high_queue;
    std::queue<AssetRequest> normal_queue;
    std::queue<AssetRequest> low_queue;
    std::queue<AssetRequest> background_queue;
    
    void ProcessQueue() {
        // Process critical first
        while (!critical_queue.empty() && HasCapacity()) {
            ProcessRequest(critical_queue.top());
            critical_queue.pop();
        }
        
        // Then high priority
        while (!high_queue.empty() && HasCapacity()) {
            ProcessRequest(high_queue.top());
            high_queue.pop();
        }
        
        // Then normal, low, background
        // ...
    }
};
```

### Concurrency Control

#### Duplicate Request Prevention

**Challenge**: Multiple requests for same asset.

**Solution**: Request deduplication + reference counting

```cpp
class ResourceLoader {
    std::unordered_map<AssetId, std::shared_ptr<AssetRequest>> active_requests;
    std::mutex requests_mutex;
    
    RequestId LoadAsset(AssetId asset_id, Priority priority, Callback callback) {
        std::lock_guard<std::mutex> lock(requests_mutex);
        
        // Check if already loading
        if (auto existing = active_requests.find(asset_id); existing != active_requests.end()) {
            // Add callback to existing request
            existing->second->AddCallback(callback);
            return existing->second->request_id;
        }
        
        // Check if already loaded
        if (auto cached = CacheManager::GetAsset(asset_id)) {
            callback(cached);
            return GenerateRequestId();
        }
        
        // Create new request
        auto request = std::make_shared<AssetRequest>(asset_id, priority, callback);
        active_requests[asset_id] = request;
        
        // Add to queue
        LoadQueue::Add(request);
        
        return request->request_id;
    }
};
```

#### Concurrency Limits

**Per Priority Limits:**
- CRITICAL: 10 concurrent
- HIGH: 20 concurrent
- NORMAL: 30 concurrent
- LOW: 20 concurrent
- BACKGROUND: 10 concurrent

**Total Limit**: 100 concurrent loads

### Memory and IO Budgeting

#### Memory Budget

**Budget Per Level**: 500MB

**Memory Management:**
```cpp
class MemoryBudget {
    size_t budget_mb = 500;
    size_t used_mb = 0;
    std::mutex budget_mutex;
    
    bool Allocate(size_t size_mb) {
        std::lock_guard<std::mutex> lock(budget_mutex);
        
        if (used_mb + size_mb > budget_mb) {
            // Evict least recently used assets
            EvictLRU(size_mb);
        }
        
        used_mb += size_mb;
        return true;
    }
    
    void Deallocate(size_t size_mb) {
        std::lock_guard<std::mutex> lock(budget_mutex);
        used_mb -= size_mb;
    }
};
```

#### IO Budget

**Disk Read Budget**: 50MB/s
**Network Budget**: 10MB/s (mobile), 100MB/s (desktop)

**IO Throttling:**
```cpp
class IOBudget {
    size_t disk_budget_mbps = 50;
    size_t network_budget_mbps = 10;
    size_t disk_used_mb = 0;
    size_t network_used_mb = 0;
    std::chrono::steady_clock::time_point last_reset;
    
    bool CanReadDisk(size_t size_mb) {
        ResetIfNeeded();
        return (disk_used_mb + size_mb) <= disk_budget_mbps;
    }
    
    bool CanDownloadNetwork(size_t size_mb) {
        ResetIfNeeded();
        return (network_used_mb + size_mb) <= network_budget_mbps;
    }
    
    void ResetIfNeeded() {
        auto now = std::chrono::steady_clock::now();
        if (now - last_reset > std::chrono::seconds(1)) {
            disk_used_mb = 0;
            network_used_mb = 0;
            last_reset = now;
        }
    }
};
```

### Security and Integrity

#### Encryption

**Encrypted Assets:**
- Sensitive assets encrypted at rest
- Decryption key stored securely (keychain, secure storage)
- Decrypt during processing pipeline

**Implementation:**
```cpp
class DecryptStage {
    static ByteArray Execute(const ByteArray& encrypted_data, const EncryptionKey& key) {
        // Decrypt using AES-256
        return AES::Decrypt(encrypted_data, key);
    }
};
```

#### Integrity Verification

**Checksums:**
- SHA-256 checksum for each asset
- Verify checksum after processing
- Reject corrupted assets

**Implementation:**
```cpp
class ValidateStage {
    static bool Execute(const ByteArray& data, const std::string& expected_checksum) {
        auto calculated_checksum = SHA256::Hash(data);
        return calculated_checksum == expected_checksum;
    }
};
```

#### Secure CDN Communication

**HTTPS:**
- All CDN requests over HTTPS
- Certificate pinning (optional)
- Secure token authentication

### Failure Handling

#### Retry Logic

**Retry Strategy:**
- Max retries: 3
- Exponential backoff: 1s, 2s, 4s
- Retry on network errors, not on corruption

**Implementation:**
```cpp
class AssetRequest {
    int retry_count = 0;
    static const int MAX_RETRIES = 3;
    
    void Retry() {
        if (retry_count < MAX_RETRIES) {
            retry_count++;
            auto delay = std::chrono::seconds(1 << (retry_count - 1));  // Exponential backoff
            ScheduleRetry(delay);
        } else {
            // Max retries reached, fail
            Fail("Max retries exceeded");
        }
    }
};
```

#### Graceful Degradation

**Fallback Strategies:**
1. **CDN Failure**: Fallback to local package
2. **Local Failure**: Fallback to CDN
3. **Processing Failure**: Use cached version (if available)
4. **Memory Full**: Evict least recently used assets

### Offline and Online Support

#### Source Selection

**Priority:**
1. Local package (fastest, always available)
2. Disk cache (fast, available offline)
3. CDN (slower, requires online)

**Implementation:**
```cpp
class SourceManager {
    AssetHandle FetchAsset(AssetId asset_id) {
        // Try local first
        if (auto asset = LocalSource::Fetch(asset_id)) {
            return asset;
        }
        
        // Try disk cache
        if (auto asset = DiskCache::Get(asset_id)) {
            return asset;
        }
        
        // Try CDN (if online)
        if (IsOnline() && (asset = CDNSource::Fetch(asset_id))) {
            return asset;
        }
        
        return nullptr;  // Not available
    }
};
```

#### Offline Mode

**Behavior:**
- Use only local package and disk cache
- Skip CDN requests
- Show appropriate error messages
- Queue CDN requests for when online

### Trade-offs and Optimizations

#### Trade-offs

1. **Memory vs Speed**
   - **Choice**: Multi-level cache (memory + disk)
   - **Reason**: Balance speed and memory usage
   - **Benefit**: Fast access with reasonable memory

2. **Latency vs Throughput**
   - **Choice**: Prioritize critical assets, batch others
   - **Reason**: Ensure smooth gameplay, load others in background
   - **Benefit**: No jank, efficient loading

3. **Security vs Performance**
   - **Choice**: Encrypt sensitive assets only
   - **Reason**: Balance security and performance
   - **Benefit**: Security where needed, performance elsewhere

#### Optimizations

1. **Prefetching**
   - Preload next level assets
   - Predict asset needs
   - Load in background

2. **Batch Loading**
   - Load multiple assets together
   - Reduce overhead
   - Better IO efficiency

3. **Compression**
   - Compress assets on disk
   - Decompress on load
   - Save disk space

4. **Streaming**
   - Stream large assets
   - Start using before fully loaded
   - Reduce perceived latency

## What Interviewers Look For

### Client Systems Skills

1. **Multi-Stage Pipelines**
   - Understanding of pipeline architecture
   - Stage dependencies
   - Streaming between stages
   - **Red Flags**: No pipeline, synchronous stages, no streaming

2. **Cache Hierarchies**
   - Multi-level caching
   - Cache eviction strategies
   - Cache warming
   - **Red Flags**: Single-level cache, no eviction, no warming

3. **Performance Optimization**
   - Low-latency IO
   - Memory efficiency
   - Frame rate considerations
   - **Red Flags**: High latency, memory leaks, frame drops

### Problem-Solving Approach

1. **Prioritization**
   - Priority system design
   - Critical vs background assets
   - Fair scheduling
   - **Red Flags**: No prioritization, FIFO only, starvation

2. **Concurrency Control**
   - Duplicate request prevention
   - Concurrency limits
   - Resource budgeting
   - **Red Flags**: Duplicate loads, no limits, resource exhaustion

3. **Failure Handling**
   - Retry logic
   - Graceful degradation
   - Error recovery
   - **Red Flags**: No retries, no fallbacks, crashes on error

### System Design Skills

1. **Component Design**
   - Clear component boundaries
   - Proper abstractions
   - Efficient interfaces
   - **Red Flags**: Monolithic design, poor abstractions, inefficient APIs

2. **Resource Management**
   - Memory budgeting
   - IO budgeting
   - Resource cleanup
   - **Red Flags**: No budgeting, memory leaks, no cleanup

3. **Security**
   - Encryption
   - Integrity verification
   - Secure communication
   - **Red Flags**: No encryption, no integrity, insecure communication

### Communication Skills

1. **Clear Explanation**
   - Explains pipeline stages
   - Discusses cache hierarchy
   - Justifies design decisions
   - **Red Flags**: Unclear explanations, no justification, confusing

2. **Performance Thinking**
   - Latency considerations
   - Memory constraints
   - Frame rate impact
   - **Red Flags**: Ignores performance, no constraints, jank

### Meta-Specific Focus

1. **Game Engine Systems**
   - Understanding of game engine architecture
   - Asset pipeline expertise
   - Performance optimization
   - **Key**: Demonstrate game engine systems expertise

2. **Client-Side Systems**
   - Resource-constrained environments
   - Memory/IO management
   - Offline support
   - **Key**: Show client-side systems mastery

3. **Production-Grade Robustness**
   - Failure handling
   - Security
   - Observability
   - **Key**: Demonstrate production thinking

## Summary

Designing a resource loader for a game engine requires careful consideration of multi-stage pipelines, cache hierarchies, prioritization, concurrency control, and memory/IO budgeting. Key design decisions include:

**Architecture Highlights:**
- Multi-stage processing pipeline (fetch → decrypt → decompress → transcode → validate → load)
- Three-level cache hierarchy (memory, disk, CDN)
- Priority-based loading queues
- Duplicate request prevention with reference counting
- Memory and IO budgeting to prevent resource exhaustion

**Key Patterns:**
- **Pipeline Architecture**: Streaming between stages, parallel processing
- **Cache Hierarchy**: Multi-level caching with LRU eviction
- **Prioritization**: Priority queues for critical assets
- **Concurrency Control**: Request deduplication, concurrency limits
- **Resource Budgeting**: Memory and IO budgets per level

**Scalability Solutions:**
- Horizontal scaling (multiple processing threads)
- Efficient caching (reduce redundant loads)
- Batch loading (reduce overhead)
- Prefetching (reduce perceived latency)

**Trade-offs:**
- Memory vs speed (multi-level cache)
- Latency vs throughput (prioritization)
- Security vs performance (selective encryption)

This design handles 100+ concurrent asset loads, supports 10K+ unique assets, and maintains < 100ms latency for cached assets while ensuring no frame drops and proper resource management. The system is scalable, fault-tolerant, and optimized for game engine performance requirements.

