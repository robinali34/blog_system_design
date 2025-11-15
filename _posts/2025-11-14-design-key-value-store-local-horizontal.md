---
layout: post
title: "Design a Key-Value Store for Local System and Horizontal Scaling - System Design Interview"
date: 2025-11-14
categories: [System Design, Interview Example, Distributed Systems, Storage Systems, Database Design, Distributed Databases]
excerpt: "A comprehensive guide to designing a key-value store optimized for a local system (2TB disk, 8 CPU, 32GB RAM) and scaling it horizontally across multiple nodes, covering storage architecture, indexing strategies, memory management, sharding, replication, and consistency models."
---

## Introduction

Designing a key-value store for a local system with specific hardware constraints (2TB disk, 8 CPU cores, 32GB RAM) requires careful consideration of memory management, disk I/O optimization, and efficient data structures. Scaling this system horizontally across multiple nodes introduces challenges in sharding, replication, consistency, and distributed coordination.

This post provides a detailed walkthrough of designing a key-value store for a single-node system and then scaling it horizontally, covering storage architecture, indexing strategies, memory management, sharding algorithms, replication strategies, consistency models, and distributed coordination. This is a common system design interview question that tests your understanding of storage systems, distributed systems, database internals, and scalability patterns.

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

**Design a key-value store for a local system with the following hardware constraints:**

**Single Node Specifications:**
- **Storage**: 2TB hard drive
- **CPU**: 8 cores
- **Memory**: 32GB RAM

**Requirements:**
1. Store key-value pairs efficiently
2. Support fast reads and writes
3. Handle more data than memory capacity
4. Support range queries
5. Handle concurrent operations
6. Provide durability guarantees
7. Support TTL (time-to-live) for keys
8. Support batch operations

**Horizontal Scaling Requirements:**
1. Scale across multiple nodes
2. Distribute data evenly
3. Handle node failures
4. Maintain consistency
5. Support replication
6. Handle rebalancing

**Scale Requirements:**
- **Single Node**: 1 billion+ key-value pairs
- **Total Data**: 1TB+ (fits in 2TB disk)
- **Average Value Size**: 1KB
- **Peak Operations**: 100,000 ops/second per node
- **Read Latency**: < 1ms (memory), < 10ms (disk)
- **Write Latency**: < 5ms (memory), < 50ms (disk)
- **Horizontal Scaling**: 10-1000 nodes

## Requirements

### Functional Requirements

**Core Features:**
1. **Basic Operations**: Get, Put, Delete key-value pairs
2. **Range Queries**: Query by key range
3. **TTL Support**: Expire keys after TTL
4. **Batch Operations**: Batch get/put/delete
5. **Durability**: Persist data to disk
6. **Concurrency**: Handle concurrent operations
7. **Compaction**: Compact old data files

**Horizontal Scaling Features:**
1. **Sharding**: Distribute data across nodes
2. **Replication**: Replicate data for availability
3. **Consistency**: Maintain consistency across replicas
4. **Rebalancing**: Rebalance data on node addition/removal
5. **Failure Handling**: Handle node failures gracefully
6. **Load Balancing**: Distribute requests across nodes

**Out of Scope:**
- Secondary indexes (focus on primary key operations)
- Transactions (focus on single-key operations)
- Complex queries (focus on key-value operations)
- Multi-region deployment (focus on single region)

### Non-Functional Requirements

**Single Node:**
1. **Performance**: 
   - Read: < 1ms (memory), < 10ms (disk)
   - Write: < 5ms (memory), < 50ms (disk)
2. **Durability**: All writes persisted to disk
3. **Memory Efficiency**: Efficient memory usage
4. **Disk Efficiency**: Efficient disk usage

**Horizontal Scaling:**
1. **Availability**: 99.9% uptime
2. **Consistency**: Eventual or strong consistency
3. **Scalability**: Linear scaling with nodes
4. **Performance**: Maintain low latency with scaling

## Capacity Estimation

### Traffic Estimates

**Single Node:**
- **Total Keys**: 1 billion
- **Average Value Size**: 1KB
- **Total Data**: 1TB
- **Peak Operations**: 100,000 ops/second
- **Read/Write Ratio**: 80/20
- **Reads**: 80,000/sec
- **Writes**: 20,000/sec

**Multi-Node (100 nodes):**
- **Total Keys**: 100 billion
- **Total Data**: 100TB
- **Peak Operations**: 10 million ops/second
- **Per Node**: 100,000 ops/second

### Storage Estimates

**Single Node:**
- **Data**: 1TB
- **Indexes**: 10GB (1% of data)
- **Metadata**: 1GB
- **WAL (Write-Ahead Log)**: 10GB
- **Total**: ~1TB (fits in 2TB disk)

**Multi-Node (100 nodes):**
- **Data per Node**: 1TB
- **Replication Factor 3**: 3TB per node
- **Total Storage**: 300TB across 100 nodes

### Bandwidth Estimates

**Single Node:**
- **Disk I/O**: 100,000 ops/sec × 1KB = 100MB/s
- **Memory Bandwidth**: 100,000 ops/sec × 1KB = 100MB/s

**Multi-Node:**
- **Network I/O**: 10M ops/sec × 1KB = 10GB/s
- **Replication Traffic**: 3x data = 30GB/s

## Core Entities

### Key-Value Entry
- `key` (BINARY/VARCHAR, primary key)
- `value` (BINARY/BLOB)
- `value_size` (INT, bytes)
- `timestamp` (TIMESTAMP)
- `ttl` (INT, seconds, optional)
- `version` (INT, for MVCC)

### Index Entry
- `key` (BINARY/VARCHAR)
- `file_id` (INT)
- `offset` (BIGINT, byte offset in file)
- `size` (INT, value size)

### Data File
- `file_id` (INT)
- `file_path` (VARCHAR)
- `file_size` (BIGINT)
- `key_count` (INT)
- `created_at` (TIMESTAMP)
- `compacted` (BOOLEAN)

### Node Metadata
- `node_id` (VARCHAR)
- `address` (VARCHAR, IP:port)
- `shard_range_start` (VARCHAR)
- `shard_range_end` (VARCHAR)
- `status` (active, inactive, recovering)
- `last_heartbeat` (TIMESTAMP)

### Replica Group
- `group_id` (VARCHAR)
- `shard_key_range` (VARCHAR)
- `primary_node_id` (VARCHAR)
- `replica_node_ids` (JSON array)
- `replication_factor` (INT)

## API

### 1. Put Key-Value
```
PUT /api/v1/kv/{key}
Request Body:
{
  "value": "base64_encoded_value",
  "ttl": 3600  // optional, seconds
}

Response:
{
  "key": "user:123",
  "status": "success",
  "version": 1
}
```

### 2. Get Key-Value
```
GET /api/v1/kv/{key}
Response:
{
  "key": "user:123",
  "value": "base64_encoded_value",
  "version": 1,
  "ttl": 3600,
  "expires_at": "2025-11-14T10:00:00Z"
}
```

### 3. Delete Key-Value
```
DELETE /api/v1/kv/{key}
Response:
{
  "key": "user:123",
  "status": "deleted"
}
```

### 4. Range Query
```
GET /api/v1/kv/range?start={start_key}&end={end_key}&limit=100
Response:
{
  "keys": [
    {
      "key": "user:100",
      "value": "...",
      "version": 1
    },
    {
      "key": "user:101",
      "value": "...",
      "version": 1
    }
  ],
  "total": 100,
  "limit": 100
}
```

### 5. Batch Put
```
POST /api/v1/kv/batch
Request Body:
{
  "entries": [
    {"key": "user:1", "value": "..."},
    {"key": "user:2", "value": "..."}
  ]
}

Response:
{
  "succeeded": 2,
  "failed": 0
}
```

## Data Flow

### Write Flow (Single Node)

1. **Client Writes Key-Value**:
   - Client sends PUT request
   - **API Server** receives request

2. **Memory Write**:
   - **Write Buffer**:
     - Stores key-value in memory buffer
     - Updates in-memory index
     - Returns success immediately

3. **Disk Write (Async)**:
   - **WAL Writer**:
     - Appends to Write-Ahead Log (WAL)
     - Ensures durability

4. **SSTable Flush**:
   - **Compaction Manager**:
     - Periodically flushes buffer to SSTable
     - Creates new SSTable file
     - Updates index

5. **Response**:
   - **API Server** returns success
   - Client continues

### Read Flow (Single Node)

1. **Client Reads Key-Value**:
   - Client sends GET request
   - **API Server** receives request

2. **Memory Lookup**:
   - **Read Path**:
     - Checks memory buffer first
     - Checks in-memory index
     - Returns if found

3. **Disk Lookup**:
   - **SSTable Reader**:
     - Searches SSTable files
     - Uses index to find file
     - Reads value from disk

4. **Response**:
   - **API Server** returns value
   - Client receives data

### Write Flow (Multi-Node)

1. **Client Writes Key-Value**:
   - Client sends PUT request
   - **Load Balancer** routes to appropriate node

2. **Shard Selection**:
   - **Router**:
     - Hashes key to determine shard
     - Routes to primary node for shard

3. **Primary Write**:
   - **Primary Node**:
     - Writes to local storage
     - Updates local index

4. **Replication**:
   - **Primary Node**:
     - Replicates to replica nodes
     - Waits for acknowledgments
     - Returns success

5. **Response**:
   - **Primary Node** returns success
   - Client receives confirmation

### Read Flow (Multi-Node)

1. **Client Reads Key-Value**:
   - Client sends GET request
   - **Load Balancer** routes request

2. **Shard Selection**:
   - **Router**:
     - Hashes key to determine shard
     - Routes to any node in replica group

3. **Node Read**:
   - **Node**:
     - Reads from local storage
     - Returns value

4. **Response**:
   - **Node** returns value
   - Client receives data

## Database Design

### Schema Design

**Key-Value Storage (SSTable Format):**
```
File Structure:
- Header (metadata, version, key_count)
- Data Blocks (key-value pairs, sorted by key)
- Index Block (key -> offset mapping)
- Footer (checksum, magic number)
```

**In-Memory Index:**
```python
# B-Tree or Hash Table
{
    "key": {
        "file_id": 1,
        "offset": 1024,
        "size": 1024,
        "timestamp": "2025-11-13T10:00:00Z"
    }
}
```

**WAL (Write-Ahead Log) Format:**
```
Entry Format:
- Operation Type (PUT/DELETE)
- Key Length (4 bytes)
- Key (variable)
- Value Length (4 bytes)
- Value (variable)
- Timestamp (8 bytes)
- Checksum (4 bytes)
```

### Database Sharding Strategy

**Consistent Hashing:**
- Hash key to determine shard
- Distribute keys evenly across nodes
- Handle node addition/removal gracefully

**Shard Assignment:**
- Each node responsible for key range
- Virtual nodes for better distribution
- Rebalance on node changes

## High-Level Design

### Single Node Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    API Server                                │
│                    - Request handling                        │
│                    - Concurrency control                     │
└────────────────────┬────────────────────────────────────────┘
                      │
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Memory Layer (32GB RAM)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Write Buffer │  │ Read Cache   │  │ Index        │     │
│  │ (MemTable)   │  │ (LRU)        │  │ (B-Tree)     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ Flush / Read
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Disk Layer (2TB)                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ WAL          │  │ SSTables     │  │ Index Files  │     │
│  │ (Write Log)  │  │ (Immutable)  │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└──────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│         Compaction Manager                                   │
│         - Merge SSTables                                     │
│         - Remove duplicates                                  │
│         - Optimize storage                                   │
└─────────────────────────────────────────────────────────────┘
```

### Multi-Node Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       │ HTTP
       │
┌──────▼──────────────────────────────────────────────┐
│        Load Balancer                                  │
│        - Request routing                              │
└──────┬──────────────────────────────────────────────┘
       │
       │
┌──────▼──────────────────────────────────────────────┐
│         Router / Coordinator                         │
│         - Consistent hashing                         │
│         - Shard mapping                              │
│         - Node discovery                             │
└──────┬──────────────────────────────────────────────┘
       │
       │
       ├──────────────┬──────────────┬──────────────┐
       │              │              │              │
┌──────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
│   Node 1    │ │   Node 2   │ │   Node 3   │ │   Node N   │
│             │ │             │ │             │ │             │
│ ┌─────────┐ │ │ ┌─────────┐ │ │ ┌─────────┐ │ │ ┌─────────┐ │
│ │ Memory  │ │ │ │ Memory  │ │ │ │ Memory  │ │ │ │ Memory  │ │
│ │ (32GB)  │ │ │ │ (32GB)  │ │ │ │ (32GB)  │ │ │ │ (32GB)  │ │
│ └─────────┘ │ │ └─────────┘ │ │ └─────────┘ │ │ └─────────┘ │
│ ┌─────────┐ │ │ ┌─────────┐ │ │ ┌─────────┐ │ │ ┌─────────┐ │
│ │ Disk    │ │ │ │ Disk    │ │ │ │ Disk    │ │ │ │ Disk    │ │
│ │ (2TB)   │ │ │ │ (2TB)   │ │ │ │ (2TB)   │ │ │ │ (2TB)   │ │
│ └─────────┘ │ │ └─────────┘ │ │ └─────────┘ │ │ └─────────┘ │
└──────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
       │              │              │              │
       │              │              │              │
       └──────────────┴──────────────┴──────────────┘
                      │
                      │ Replication
                      │
┌─────────────────────▼───────────────────────────────────────┐
│         Replication Layer                                   │
│         - Primary-Replica replication                        │
│         - Consistency guarantees                            │
└─────────────────────────────────────────────────────────────┘
```

## Deep Dive

### Component Design

#### 1. Memory Management (Single Node)

**Responsibilities:**
- Manage 32GB RAM efficiently
- Store hot data in memory
- Evict cold data to disk
- Maintain indexes in memory

**Key Design Decisions:**
- **Write Buffer**: 1-2GB for writes
- **Read Cache**: 10-20GB LRU cache
- **Index**: 5-10GB for indexes
- **Eviction**: LRU for cache, flush for buffer

**Implementation:**
```python
class MemoryManager:
    def __init__(self, total_memory_gb=32):
        self.total_memory = total_memory_gb * 1024 * 1024 * 1024  # bytes
        self.write_buffer_size = 2 * 1024 * 1024 * 1024  # 2GB
        self.read_cache_size = 20 * 1024 * 1024 * 1024  # 20GB
        self.index_size = 10 * 1024 * 1024 * 1024  # 10GB
        
        self.write_buffer = {}  # MemTable
        self.read_cache = LRUCache(capacity=self.read_cache_size)
        self.index = BTree()  # In-memory index
    
    def put(self, key, value):
        """Put key-value in write buffer"""
        # Check if buffer is full
        if self.get_buffer_size() >= self.write_buffer_size:
            self.flush_buffer()
        
        # Add to buffer
        self.write_buffer[key] = {
            'value': value,
            'timestamp': time.time()
        }
        
        # Update index
        self.index.put(key, {
            'in_memory': True,
            'buffer': True
        })
    
    def get(self, key):
        """Get key-value from memory"""
        # Check write buffer first
        if key in self.write_buffer:
            value = self.write_buffer[key]['value']
            self.read_cache.put(key, value)
            return value
        
        # Check read cache
        cached = self.read_cache.get(key)
        if cached:
            return cached
        
        # Not in memory, return None (will read from disk)
        return None
    
    def flush_buffer(self):
        """Flush write buffer to disk"""
        # Create SSTable from buffer
        sstable = self.create_sstable(self.write_buffer)
        
        # Write to disk
        self.disk_manager.write_sstable(sstable)
        
        # Clear buffer
        self.write_buffer.clear()
        
        # Update index
        self.update_index_after_flush(sstable)
```

#### 2. Disk Storage (Single Node)

**Responsibilities:**
- Store data efficiently on 2TB disk
- Organize data in SSTables
- Maintain WAL for durability
- Support efficient reads

**Key Design Decisions:**
- **SSTable Format**: Immutable sorted files
- **WAL**: Write-Ahead Log for durability
- **Compaction**: Merge SSTables periodically
- **Index Files**: Separate index files for fast lookup

**Implementation:**
```python
class DiskStorage:
    def __init__(self, disk_path, max_disk_size=2 * 1024 * 1024 * 1024 * 1024):
        self.disk_path = disk_path
        self.max_disk_size = max_disk_size
        self.sstables = []  # List of SSTable files
        self.wal = WriteAheadLog(os.path.join(disk_path, 'wal'))
    
    def write_sstable(self, data):
        """Write data to new SSTable"""
        # Sort data by key
        sorted_data = sorted(data.items(), key=lambda x: x[0])
        
        # Create SSTable file
        sstable_id = len(self.sstables)
        sstable_path = os.path.join(self.disk_path, f'sstable_{sstable_id}.sst')
        
        # Write SSTable
        with open(sstable_path, 'wb') as f:
            # Write header
            header = {
                'version': 1,
                'key_count': len(sorted_data),
                'data_start': 1024  # Header size
            }
            f.write(struct.pack('I I Q', header['version'], 
                              header['key_count'], header['data_start']))
            
            # Write data blocks
            offset = header['data_start']
            index = {}
            
            for key, value in sorted_data:
                # Write key-value pair
                key_bytes = key.encode() if isinstance(key, str) else key
                value_bytes = value.encode() if isinstance(value, str) else value
                
                # Entry format: key_len (4) + key + value_len (4) + value
                entry = struct.pack('I', len(key_bytes)) + key_bytes + \
                       struct.pack('I', len(value_bytes)) + value_bytes
                
                f.write(entry)
                
                # Update index
                index[key] = offset
                offset += len(entry)
            
            # Write index at end
            index_offset = offset
            index_data = json.dumps(index).encode()
            f.write(index_data)
            
            # Write footer with index offset
            footer = struct.pack('Q', index_offset)
            f.write(footer)
        
        # Add to SSTable list
        self.sstables.append({
            'id': sstable_id,
            'path': sstable_path,
            'key_count': len(sorted_data),
            'size': os.path.getsize(sstable_path)
        })
    
    def read(self, key):
        """Read key from SSTables"""
        # Search SSTables in reverse order (newest first)
        for sstable in reversed(self.sstables):
            value = self.read_from_sstable(sstable, key)
            if value is not None:
                return value
        
        return None
    
    def read_from_sstable(self, sstable, key):
        """Read key from specific SSTable"""
        with open(sstable['path'], 'rb') as f:
            # Read header
            header_data = f.read(1024)
            version, key_count, data_start = struct.unpack('I I Q', header_data[:16])
            
            # Read footer to get index offset
            f.seek(-8, 2)  # Seek to last 8 bytes
            index_offset = struct.unpack('Q', f.read(8))[0]
            
            # Read index
            f.seek(index_offset)
            index_data = f.read()
            index = json.loads(index_data.decode())
            
            # Check if key exists
            if key not in index:
                return None
            
            # Read value
            offset = index[key]
            f.seek(offset)
            
            # Read key
            key_len = struct.unpack('I', f.read(4))[0]
            key_bytes = f.read(key_len)
            
            # Read value
            value_len = struct.unpack('I', f.read(4))[0]
            value_bytes = f.read(value_len)
            
            return value_bytes
```

#### 3. Sharding (Multi-Node)

**Responsibilities:**
- Distribute keys across nodes
- Handle node addition/removal
- Rebalance data when needed
- Route requests to correct node

**Key Design Decisions:**
- **Consistent Hashing**: Use consistent hashing for sharding
- **Virtual Nodes**: Use virtual nodes for better distribution
- **Replication**: Replicate each shard to multiple nodes
- **Rebalancing**: Rebalance on node changes

**Implementation:**
```python
class ShardingManager:
    def __init__(self, nodes, replication_factor=3):
        self.nodes = nodes
        self.replication_factor = replication_factor
        self.virtual_nodes_per_node = 100
        self.ring = ConsistentHashRing()
        
        # Add nodes to ring
        for node in nodes:
            for i in range(self.virtual_nodes_per_node):
                virtual_node_id = f"{node['id']}:{i}"
                self.ring.add_node(virtual_node_id, node)
    
    def get_shard_nodes(self, key):
        """Get nodes responsible for key"""
        # Hash key
        key_hash = self.hash_key(key)
        
        # Find primary node
        primary_virtual = self.ring.get_node(key_hash)
        primary_node = primary_virtual['node']
        
        # Find replica nodes
        replica_nodes = []
        current_virtual = primary_virtual
        for _ in range(self.replication_factor - 1):
            current_virtual = self.ring.get_next_node(current_virtual)
            replica_nodes.append(current_virtual['node'])
        
        return {
            'primary': primary_node,
            'replicas': replica_nodes
        }
    
    def hash_key(self, key):
        """Hash key to determine shard"""
        return hashlib.md5(str(key).encode()).hexdigest()
    
    def add_node(self, node):
        """Add new node to cluster"""
        # Add virtual nodes
        for i in range(self.virtual_nodes_per_node):
            virtual_node_id = f"{node['id']}:{i}"
            self.ring.add_node(virtual_node_id, node)
        
        # Trigger rebalancing
        self.rebalance()
    
    def remove_node(self, node_id):
        """Remove node from cluster"""
        # Remove virtual nodes
        for i in range(self.virtual_nodes_per_node):
            virtual_node_id = f"{node_id}:{i}"
            self.ring.remove_node(virtual_node_id)
        
        # Trigger rebalancing
        self.rebalance()
    
    def rebalance(self):
        """Rebalance data across nodes"""
        # Identify keys that need to move
        keys_to_move = self.identify_keys_to_move()
        
        # Move keys to new nodes
        for key, old_node, new_node in keys_to_move:
            self.move_key(key, old_node, new_node)
```

#### 4. Replication (Multi-Node)

**Responsibilities:**
- Replicate data across nodes
- Maintain consistency
- Handle replica failures
- Elect new primary on failure

**Key Design Decisions:**
- **Primary-Replica**: One primary, multiple replicas
- **Synchronous Replication**: Wait for majority acknowledgment
- **Quorum**: Require majority for writes
- **Leader Election**: Elect new primary on failure

**Implementation:**
```python
class ReplicationManager:
    def __init__(self, sharding_manager):
        self.sharding_manager = sharding_manager
        self.replication_factor = 3
        self.quorum = (self.replication_factor // 2) + 1
    
    def replicate_write(self, key, value, shard_nodes):
        """Replicate write to all replicas"""
        primary = shard_nodes['primary']
        replicas = shard_nodes['replicas']
        
        # Write to primary
        primary_result = self.write_to_node(primary, key, value)
        if not primary_result:
            raise ReplicationError("Primary write failed")
        
        # Replicate to replicas
        replica_results = []
        for replica in replicas:
            try:
                result = self.write_to_node(replica, key, value)
                replica_results.append(result)
            except Exception as e:
                # Log error but continue
                pass
        
        # Check quorum
        successful_writes = 1 + len([r for r in replica_results if r])
        if successful_writes < self.quorum:
            raise ReplicationError("Quorum not reached")
        
        return True
    
    def write_to_node(self, node, key, value):
        """Write to specific node"""
        # Make HTTP request to node
        response = requests.put(
            f"http://{node['address']}/api/v1/kv/{key}",
            json={'value': base64.b64encode(value).decode()},
            timeout=5
        )
        return response.status_code == 200
    
    def read_with_consistency(self, key, shard_nodes, consistency_level='strong'):
        """Read with consistency level"""
        if consistency_level == 'strong':
            # Read from primary
            primary = shard_nodes['primary']
            return self.read_from_node(primary, key)
        else:  # eventual
            # Read from any node
            nodes = [shard_nodes['primary']] + shard_nodes['replicas']
            for node in nodes:
                try:
                    return self.read_from_node(node, key)
                except:
                    continue
            raise ReadError("All nodes failed")
    
    def read_from_node(self, node, key):
        """Read from specific node"""
        response = requests.get(
            f"http://{node['address']}/api/v1/kv/{key}",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return base64.b64decode(data['value'])
        else:
            raise ReadError(f"Read failed: {response.status_code}")
```

### Detailed Design

#### Consistent Hashing Implementation

**Challenge:** Distribute keys evenly across nodes

**Solution:**
- **Consistent Hashing Ring**: Hash nodes and keys to ring
- **Virtual Nodes**: Multiple virtual nodes per physical node
- **Even Distribution**: Better key distribution

**Implementation:**
```python
class ConsistentHashRing:
    def __init__(self):
        self.ring = {}  # hash -> node mapping
        self.sorted_keys = []  # Sorted hash keys
    
    def add_node(self, node_id, node_data):
        """Add node to ring"""
        for i in range(100):  # Virtual nodes
            hash_key = self.hash(f"{node_id}:{i}")
            self.ring[hash_key] = node_data
            self.sorted_keys.append(hash_key)
        
        self.sorted_keys.sort()
    
    def get_node(self, key_hash):
        """Get node for key hash"""
        if not self.sorted_keys:
            return None
        
        # Find first node with hash >= key_hash
        for hash_key in self.sorted_keys:
            if hash_key >= key_hash:
                return self.ring[hash_key]
        
        # Wrap around to first node
        return self.ring[self.sorted_keys[0]]
    
    def hash(self, value):
        """Hash value"""
        return int(hashlib.md5(value.encode()).hexdigest(), 16)
```

#### Compaction Strategy

**Challenge:** Manage disk space efficiently

**Solution:**
- **Leveled Compaction**: Organize SSTables in levels
- **Merge Strategy**: Merge SSTables at same level
- **Size Limits**: Limit SSTable size per level

**Implementation:**
```python
class CompactionManager:
    def __init__(self, disk_storage):
        self.disk_storage = disk_storage
        self.level_sizes = [10, 100, 1000, 10000]  # Max SSTables per level
    
    def compact(self):
        """Compact SSTables"""
        # Group SSTables by level
        levels = self.group_by_level()
        
        # Compact each level
        for level, sstables in enumerate(levels):
            if len(sstables) > self.level_sizes[level]:
                self.compact_level(level, sstables)
    
    def compact_level(self, level, sstables):
        """Compact SSTables at level"""
        # Merge SSTables
        merged_data = {}
        for sstable in sstables:
            data = self.read_sstable(sstable)
            merged_data.update(data)
        
        # Remove old SSTables
        for sstable in sstables:
            os.remove(sstable['path'])
        
        # Write merged SSTable to next level
        self.disk_storage.write_sstable(merged_data)
```

### Scalability Considerations

#### Horizontal Scaling

**Adding Nodes:**
1. Add node to consistent hash ring
2. Identify keys to move
3. Move keys to new node
4. Update routing table

**Removing Nodes:**
1. Identify keys on node
2. Move keys to other nodes
3. Remove node from ring
4. Update routing table

#### Performance Optimization

**Single Node:**
- **Memory**: Use memory efficiently
- **Disk I/O**: Minimize disk seeks
- **Compression**: Compress values
- **Batch Operations**: Batch writes

**Multi-Node:**
- **Load Balancing**: Distribute load evenly
- **Caching**: Cache frequently accessed data
- **Network Optimization**: Minimize network hops
- **Parallel Processing**: Process requests in parallel

### Security Considerations

#### Data Security

- **Encryption**: Encrypt data at rest
- **Access Control**: Control access to nodes
- **Network Security**: Secure node communication
- **Audit Logging**: Log all operations

### Monitoring & Observability

#### Key Metrics

**Single Node:**
- Memory usage
- Disk usage
- Read/write latency
- Cache hit rate
- SSTable count

**Multi-Node:**
- Node health
- Replication lag
- Shard distribution
- Request routing
- Rebalancing status

### Trade-offs and Optimizations

#### Trade-offs

**1. Consistency: Strong vs Eventual**
- **Strong**: Higher latency, better consistency
- **Eventual**: Lower latency, eventual consistency
- **Decision**: Configurable per operation

**2. Replication: Synchronous vs Asynchronous**
- **Synchronous**: Better consistency, higher latency
- **Asynchronous**: Lower latency, eventual consistency
- **Decision**: Synchronous for critical data

**3. Compaction: Aggressive vs Lazy**
- **Aggressive**: Less disk space, higher CPU
- **Lazy**: More disk space, lower CPU
- **Decision**: Balanced approach

#### Optimizations

**1. Compression**
- Compress values before storage
- Reduce disk usage
- Trade CPU for storage

**2. Bloom Filters**
- Use bloom filters for SSTables
- Reduce unnecessary disk reads
- Improve read performance

**3. Read-Ahead**
- Prefetch data for range queries
- Improve sequential read performance

## Summary

Designing a key-value store for a local system and scaling it horizontally requires careful consideration of:

**Single Node:**
1. **Memory Management**: Efficient use of 32GB RAM
2. **Disk Storage**: Efficient storage on 2TB disk
3. **Write Buffer**: Fast in-memory writes
4. **SSTable Format**: Immutable sorted files
5. **Compaction**: Merge SSTables periodically
6. **Indexing**: Fast key lookup

**Horizontal Scaling:**
1. **Sharding**: Consistent hashing for distribution
2. **Replication**: Primary-replica replication
3. **Consistency**: Configurable consistency levels
4. **Rebalancing**: Handle node addition/removal
5. **Failure Handling**: Graceful node failure handling
6. **Load Balancing**: Distribute requests evenly

Key architectural decisions:
- **SSTable Format** for efficient disk storage
- **Write Buffer** for fast writes
- **Consistent Hashing** for sharding
- **Primary-Replica Replication** for availability
- **Quorum-Based Writes** for consistency
- **Leveled Compaction** for disk management
- **Virtual Nodes** for even distribution
- **Horizontal Scaling** by adding nodes

The system handles 100,000 operations per second per node, stores 1TB+ data per node, scales linearly with nodes, maintains 99.9% availability, and provides sub-millisecond read latency for cached data.

