---
layout: post
title: "Design a File System or In-memory Storage - System Design Interview"
date: 2025-11-24
categories: [System Design, Interview Example, Storage Systems, File Systems, Operating Systems, Distributed Systems]
excerpt: "A comprehensive guide to designing a file system and in-memory storage system, covering data structures, storage organization, metadata management, caching strategies, concurrency control, durability, and scalability. Essential for system design interviews focusing on storage systems."
---

## Introduction

Designing a file system or in-memory storage system is a fundamental system design problem that tests your understanding of storage architectures, data structures, memory management, concurrency, and persistence. This problem appears frequently in system design interviews, especially for roles involving storage systems, operating systems, databases, and distributed systems.

A file system manages how data is stored and retrieved on persistent storage (disk), while in-memory storage focuses on efficient data management in RAM. Both systems share common challenges: efficient data organization, fast lookups, concurrency control, and durability guarantees.

This guide covers the design of both file systems and in-memory storage systems, including data structures, storage organization, metadata management, caching strategies, concurrency control, durability mechanisms, and scalability considerations.

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Requirements](#requirements)
   - [Functional Requirements](#functional-requirements)
   - [Non-Functional Requirements](#non-functional-requirements)
3. [Capacity Estimation](#capacity-estimation)
4. [Core Data Structures](#core-data-structures)
5. [API Design](#api-design)
6. [High-Level Architecture](#high-level-architecture)
7. [File System Design](#file-system-design)
   - [Storage Organization](#storage-organization)
   - [Metadata Management](#metadata-management)
   - [Directory Structure](#directory-structure)
   - [Allocation Strategies](#allocation-strategies)
8. [In-Memory Storage Design](#in-memory-storage-design)
   - [Memory Organization](#memory-organization)
   - [Data Structures](#data-structures)
   - [Eviction Policies](#eviction-policies)
   - [Memory Management](#memory-management)
9. [Deep Dive](#deep-dive)
   - [Concurrency Control](#concurrency-control)
   - [Durability and Persistence](#durability-and-persistence)
   - [Caching Strategies](#caching-strategies)
   - [Performance Optimization](#performance-optimization)
   - [Scalability Considerations](#scalability-considerations)
10. [Trade-offs and Design Decisions](#trade-offs-and-design-decisions)
11. [Comparison: File System vs In-Memory Storage](#comparison-file-system-vs-in-memory-storage)
12. [Summary](#summary)

## Problem Statement

**Design a file system or in-memory storage system that supports:**

### File System Requirements:
1. **File Operations**: Create, read, write, delete files
2. **Directory Operations**: Create, list, delete directories
3. **Hierarchical Structure**: Support nested directories
4. **Metadata**: Store file metadata (size, permissions, timestamps)
5. **Concurrency**: Handle concurrent file operations
6. **Durability**: Persist data to disk reliably
7. **Efficiency**: Efficient storage utilization and fast access

### In-Memory Storage Requirements:
1. **Key-Value Operations**: Store and retrieve key-value pairs
2. **Fast Access**: O(1) or O(log n) lookup time
3. **Memory Management**: Efficient memory utilization
4. **Eviction**: Support LRU, LFU, or other eviction policies
4. **Concurrency**: Thread-safe operations
5. **Persistence**: Optional persistence to disk
6. **TTL Support**: Optional time-to-live for keys

### Scale Requirements:
- **File System**:
  - Support millions of files
  - Handle files from bytes to terabytes
  - Support concurrent operations from multiple processes
  - Efficient disk space utilization
  
- **In-Memory Storage**:
  - Store millions of key-value pairs
  - Handle values from bytes to megabytes
  - Support high-throughput operations (100K+ ops/sec)
  - Efficient memory utilization

## Requirements

### Functional Requirements

**File System:**
1. **File Operations**:
   - Create file with path
   - Read file content
   - Write/append to file
   - Delete file
   - Rename/move file
   - Get file metadata (size, permissions, timestamps)

2. **Directory Operations**:
   - Create directory
   - List directory contents
   - Delete directory (recursive)
   - Navigate directory tree

3. **Path Resolution**:
   - Support absolute paths (`/home/user/file.txt`)
   - Support relative paths (`../file.txt`)
   - Handle path separators correctly

4. **Metadata Management**:
   - File size
   - Creation/modification/access times
   - Permissions (read, write, execute)
   - Owner and group information

**In-Memory Storage:**
1. **Basic Operations**:
   - `put(key, value)`: Store key-value pair
   - `get(key)`: Retrieve value by key
   - `delete(key)`: Remove key-value pair
   - `exists(key)`: Check if key exists

2. **Advanced Operations**:
   - `getAll()`: Get all key-value pairs (optional)
   - `clear()`: Clear all data
   - `size()`: Get number of entries

3. **Eviction Support**:
   - LRU (Least Recently Used)
   - LFU (Least Frequently Used)
   - TTL-based expiration

### Non-Functional Requirements

**Performance:**
- **File System**:
  - Read latency: < 10ms for small files
  - Write latency: < 50ms for small files
  - Directory listing: < 100ms for directories with 10K files
  
- **In-Memory Storage**:
  - Get/Put operations: < 1ms (O(1) or O(log n))
  - Support 100K+ operations per second

**Reliability:**
- **File System**:
  - Data durability: Guarantee writes are persisted
  - Handle crashes gracefully
  - Support journaling/logging for recovery
  
- **In-Memory Storage**:
  - Thread-safe operations
  - Optional persistence to disk
  - Handle memory pressure gracefully

**Scalability:**
- Support millions of files/keys
- Efficient memory/disk utilization
- Handle concurrent operations

**Consistency:**
- **File System**: Strong consistency for metadata and data
- **In-Memory Storage**: Eventual consistency acceptable for distributed systems

## Capacity Estimation

### File System

**Assumptions:**
- Average file size: 10KB
- Average directory contains: 100 files
- Maximum file size: 10GB
- Total files: 10 million
- Metadata per file: 1KB

**Storage Estimates:**
- Total data: 10M files × 10KB = 100GB
- Total metadata: 10M files × 1KB = 10GB
- Total storage: ~110GB (with overhead)

**Operations:**
- Read operations: 1M/sec
- Write operations: 100K/sec
- Directory operations: 10K/sec

### In-Memory Storage

**Assumptions:**
- Average key size: 50 bytes
- Average value size: 1KB
- Total entries: 10 million
- Memory overhead: 20% (data structures, pointers)

**Memory Estimates:**
- Key storage: 10M × 50 bytes = 500MB
- Value storage: 10M × 1KB = 10GB
- Overhead: 20% × 10.5GB = 2.1GB
- Total memory: ~12.6GB

**Operations:**
- Get operations: 500K/sec
- Put operations: 100K/sec
- Delete operations: 10K/sec

## Core Data Structures

### File System Data Structures

**1. Inode (Index Node)**
```
inode {
    int inode_number;          // Unique identifier
    int file_type;              // File, directory, symlink
    int permissions;            // Read, write, execute
    int owner_id;               // User ID
    int group_id;               // Group ID
    long size;                  // File size in bytes
    long blocks[];              // Block pointers
    long indirect_block;        // Indirect block pointer
    long double_indirect_block; // Double indirect block pointer
    long triple_indirect_block; // Triple indirect block pointer
    timestamp created_at;
    timestamp modified_at;
    timestamp accessed_at;
    int link_count;             // Hard link count
}
```

**2. Directory Entry**
```
directory_entry {
    int inode_number;           // Reference to inode
    string name;                // File/directory name
    int name_length;            // Length of name
}
```

**3. Superblock**
```
superblock {
    int magic_number;           // File system identifier
    int block_size;             // Size of each block
    int total_blocks;            // Total blocks in file system
    int free_blocks;             // Free blocks available
    int total_inodes;            // Total inodes
    int free_inodes;             // Free inodes
    int inode_bitmap_block;      // Block containing inode bitmap
    int block_bitmap_block;      // Block containing block bitmap
    int inode_table_block;       // Starting block of inode table
    timestamp last_mount_time;
    int mount_count;
}
```

**4. Block Allocation**
- **Bitmap**: Track free/allocated blocks
- **Block Groups**: Organize blocks into groups for efficiency

### In-Memory Storage Data Structures

**1. Hash Table (for O(1) access)**
```
hash_table {
    bucket[] buckets;           // Array of buckets
    int capacity;               // Total capacity
    int size;                   // Current size
    float load_factor;          // Load factor threshold
}
```

**2. Hash Table Entry**
```
hash_entry {
    string key;
    value data;
    hash_entry* next;           // For chaining
    timestamp last_accessed;    // For LRU
    int access_count;           // For LFU
    timestamp expires_at;       // For TTL
}
```

**3. LRU Cache (using Doubly Linked List + Hash Map)**
```
lru_cache {
    hash_map<key, node*> map;   // O(1) lookup
    doubly_linked_list list;    // Maintain order
    int capacity;
    int size;
}
```

**4. B-Tree (for range queries)**
```
b_tree_node {
    bool is_leaf;
    key[] keys;
    node*[] children;
    value[] values;             // For leaf nodes
    int key_count;
}
```

## API Design

### File System API

```python
class FileSystem:
    def create_file(path: str, content: bytes) -> bool
    def read_file(path: str, offset: int, length: int) -> bytes
    def write_file(path: str, content: bytes, offset: int) -> bool
    def append_file(path: str, content: bytes) -> bool
    def delete_file(path: str) -> bool
    def rename_file(old_path: str, new_path: str) -> bool
    def get_metadata(path: str) -> FileMetadata
    def create_directory(path: str) -> bool
    def list_directory(path: str) -> List[str]
    def delete_directory(path: str, recursive: bool) -> bool
    def exists(path: str) -> bool
    def get_size(path: str) -> int
```

**FileMetadata:**
```python
class FileMetadata:
    path: str
    size: int
    permissions: int
    owner_id: int
    group_id: int
    created_at: timestamp
    modified_at: timestamp
    accessed_at: timestamp
    is_directory: bool
```

### In-Memory Storage API

```python
class InMemoryStorage:
    def put(key: str, value: bytes) -> bool
    def get(key: str) -> Optional[bytes]
    def delete(key: str) -> bool
    def exists(key: str) -> bool
    def clear() -> bool
    def size() -> int
    def get_all() -> Dict[str, bytes]  # Optional
    def set_ttl(key: str, ttl_seconds: int) -> bool
    def get_stats() -> StorageStats
```

**With Eviction Policy:**
```python
class LRUCache(InMemoryStorage):
    def __init__(capacity: int)
    def get(key: str) -> Optional[bytes]  # Moves to front
    def put(key: str, value: bytes) -> bool  # Evicts LRU if full
```

## High-Level Architecture

### File System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Application Layer                     │
│  (File Operations: create, read, write, delete)         │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  VFS (Virtual File System)              │
│  (Path resolution, permission checks, caching)          │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              File System Implementation                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Metadata   │  │   Directory  │  │   Block      │  │
│  │   Manager    │  │   Manager    │  │   Allocator  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Inode      │  │   Journal    │  │   Cache      │  │
│  │   Manager    │  │   Manager    │  │   Manager    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Block Device Layer                     │
│  (Disk I/O, block read/write operations)                │
└─────────────────────────────────────────────────────────┘
```

### In-Memory Storage Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Application Layer                     │
│  (Key-Value Operations: put, get, delete)               │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              In-Memory Storage Engine                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Hash       │  │   Eviction   │  │   Memory     │  │
│  │   Table      │  │   Policy     │  │   Manager    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Index      │  │   TTL        │  │   Persistence│  │
│  │   Manager    │  │   Manager    │  │   Layer      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Memory (RAM)                           │
│  (Hash tables, data structures, cached data)           │
└─────────────────────────────────────────────────────────┘
                     │ (Optional)
┌────────────────────▼────────────────────────────────────┐
│                  Persistence Layer                      │
│  (Optional: Snapshot, WAL, periodic writes)            │
└─────────────────────────────────────────────────────────┘
```

## File System Design

### Storage Organization

**1. Block-Based Organization**

Files are stored in fixed-size blocks (typically 4KB):
- **Block**: Smallest unit of allocation
- **Block Group**: Collection of blocks for efficient management
- **Superblock**: Contains file system metadata

**Layout:**
```
┌──────────┬──────────┬──────────┬──────────┬──────────┐
│ Super   │ Block    │ Inode    │ Inode    │ Data     │
│ Block   │ Bitmap   │ Bitmap   │ Table    │ Blocks   │
└──────────┴──────────┴──────────┴──────────┴──────────┘
```

**2. Inode Structure**

Inodes store file metadata and block pointers:
- **Direct Blocks**: 12 direct pointers to data blocks
- **Indirect Block**: Points to a block containing 1024 block pointers
- **Double Indirect**: Points to a block of indirect blocks
- **Triple Indirect**: Points to a block of double indirect blocks

**Maximum File Size Calculation:**
- Block size: 4KB
- Pointer size: 4 bytes
- Blocks per indirect: 4KB / 4 bytes = 1024 blocks
- Direct: 12 × 4KB = 48KB
- Indirect: 1024 × 4KB = 4MB
- Double indirect: 1024 × 4MB = 4GB
- Triple indirect: 1024 × 4GB = 4TB

### Metadata Management

**1. Inode Table**

Inodes are stored in a fixed table:
- Each inode has a unique number
- Inodes are allocated from a free list
- Inode bitmap tracks allocated inodes

**2. Directory Structure**

Directories are special files containing directory entries:
```
directory_entry {
    inode_number: 123
    name: "file.txt"
    name_length: 8
}
```

**Directory Lookup:**
1. Resolve path to directory inode
2. Read directory file
3. Search for matching name
4. Return inode number

**Path Resolution:**
- Start from root inode (typically inode 2)
- Parse path components
- Traverse directory entries
- Resolve each component sequentially

### Directory Structure

**Hierarchical Tree:**
```
/ (root)
├── home/
│   ├── user1/
│   │   ├── documents/
│   │   │   └── file1.txt
│   │   └── file2.txt
│   └── user2/
│       └── file3.txt
└── etc/
    └── config.txt
```

**Implementation:**
- Each directory is a file containing directory entries
- Directory entries map names to inode numbers
- Root directory has a fixed inode number (typically 2)

### Allocation Strategies

**1. Contiguous Allocation**
- **Pros**: Fast sequential access, simple
- **Cons**: External fragmentation, difficult to grow files

**2. Linked Allocation**
- **Pros**: No external fragmentation, easy to grow
- **Cons**: Slow random access, overhead for pointers

**3. Indexed Allocation (Used in most modern file systems)**
- **Pros**: Fast random access, no external fragmentation
- **Cons**: Overhead for index blocks, limited by index size

**4. Extent-Based Allocation**
- **Pros**: Efficient for large files, reduces metadata overhead
- **Cons**: More complex management

**Block Allocation Algorithm:**
```python
def allocate_blocks(num_blocks):
    # Find free blocks using bitmap
    free_blocks = []
    bitmap = read_block_bitmap()
    
    for i in range(len(bitmap)):
        if bitmap[i] == FREE and len(free_blocks) < num_blocks:
            free_blocks.append(i)
            bitmap[i] = ALLOCATED
    
    write_block_bitmap(bitmap)
    return free_blocks
```

## In-Memory Storage Design

### Memory Organization

**1. Hash Table Implementation**

**Open Addressing (Linear Probing):**
```python
class HashTable:
    def __init__(self, capacity=16, load_factor=0.75):
        self.capacity = capacity
        self.load_factor = load_factor
        self.size = 0
        self.buckets = [None] * capacity
    
    def hash(self, key):
        return hash(key) % self.capacity
    
    def put(self, key, value):
        index = self.hash(key)
        
        # Linear probing
        while self.buckets[index] is not None:
            if self.buckets[index][0] == key:
                self.buckets[index] = (key, value)
                return
            index = (index + 1) % self.capacity
        
        self.buckets[index] = (key, value)
        self.size += 1
        
        if self.size > self.capacity * self.load_factor:
            self.resize()
    
    def get(self, key):
        index = self.hash(key)
        
        while self.buckets[index] is not None:
            if self.buckets[index][0] == key:
                return self.buckets[index][1]
            index = (index + 1) % self.capacity
        
        return None
```

**Separate Chaining:**
```python
class HashTable:
    def __init__(self, capacity=16):
        self.capacity = capacity
        self.buckets = [[] for _ in range(capacity)]
        self.size = 0
    
    def hash(self, key):
        return hash(key) % self.capacity
    
    def put(self, key, value):
        index = self.hash(key)
        bucket = self.buckets[index]
        
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        
        bucket.append((key, value))
        self.size += 1
    
    def get(self, key):
        index = self.hash(key)
        bucket = self.buckets[index]
        
        for k, v in bucket:
            if k == key:
                return v
        
        return None
```

### Data Structures

**1. LRU Cache Implementation**

```python
class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}  # key -> node
        self.head = Node(0, 0)  # Dummy head
        self.tail = Node(0, 0)  # Dummy tail
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _add_node(self, node):
        # Add after head
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
    
    def _remove_node(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev
    
    def _move_to_head(self, node):
        self._remove_node(node)
        self._add_node(node)
    
    def get(self, key):
        if key in self.cache:
            node = self.cache[key]
            self._move_to_head(node)
            return node.value
        return None
    
    def put(self, key, value):
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self._move_to_head(node)
        else:
            if len(self.cache) >= self.capacity:
                # Remove tail
                lru = self.tail.prev
                self._remove_node(lru)
                del self.cache[lru.key]
            
            node = Node(key, value)
            self._add_node(node)
            self.cache[key] = node
```

**2. B-Tree for Range Queries**

```python
class BTreeNode:
    def __init__(self, is_leaf=False):
        self.is_leaf = is_leaf
        self.keys = []
        self.values = [] if is_leaf else []
        self.children = [] if not is_leaf else []
        self.parent = None

class BTree:
    def __init__(self, min_degree=3):
        self.root = BTreeNode(is_leaf=True)
        self.min_degree = min_degree
    
    def search(self, key):
        return self._search(self.root, key)
    
    def _search(self, node, key):
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        
        if i < len(node.keys) and node.keys[i] == key:
            return node.values[i] if node.is_leaf else node
        
        if node.is_leaf:
            return None
        
        return self._search(node.children[i], key)
    
    def insert(self, key, value):
        root = self.root
        
        if len(root.keys) == 2 * self.min_degree - 1:
            new_root = BTreeNode()
            new_root.children.append(root)
            root.parent = new_root
            self._split_child(new_root, 0)
            self.root = new_root
        
        self._insert_non_full(self.root, key, value)
    
    def _insert_non_full(self, node, key, value):
        i = len(node.keys) - 1
        
        if node.is_leaf:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            node.keys.insert(i + 1, key)
            node.values.insert(i + 1, value)
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            
            if len(node.children[i].keys) == 2 * self.min_degree - 1:
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            
            self._insert_non_full(node.children[i], key, value)
```

### Eviction Policies

**1. LRU (Least Recently Used)**
- Evict least recently accessed item
- Implementation: Doubly linked list + Hash map
- Time complexity: O(1) for both get and put

**2. LFU (Least Frequently Used)**
- Evict least frequently accessed item
- Implementation: Min heap + Hash map
- Time complexity: O(log n) for eviction

**3. FIFO (First In First Out)**
- Evict oldest item
- Implementation: Queue
- Time complexity: O(1)

**4. Random Eviction**
- Evict random item
- Simple but less optimal
- Time complexity: O(1)

**5. TTL-Based Expiration**
- Evict items that have expired
- Background thread scans and removes expired items
- Time complexity: O(n) for scan

### Memory Management

**1. Memory Pool**

Pre-allocate memory pools to reduce allocation overhead:
```python
class MemoryPool:
    def __init__(self, block_size, num_blocks):
        self.block_size = block_size
        self.pool = [bytearray(block_size) for _ in range(num_blocks)]
        self.free_list = list(range(num_blocks))
    
    def allocate(self):
        if not self.free_list:
            return None
        return self.pool[self.free_list.pop()]
    
    def deallocate(self, block):
        index = self.pool.index(block)
        self.free_list.append(index)
```

**2. Memory Compression**

Compress values to reduce memory usage:
- Use compression algorithms (LZ4, Snappy)
- Compress values larger than threshold
- Decompress on access

**3. Memory Limits**

Enforce memory limits:
- Monitor memory usage
- Evict items when limit reached
- Use memory-mapped files for large values

## Deep Dive

### Concurrency Control

**File System:**

**1. File-Level Locking**
```python
class FileLock:
    def __init__(self):
        self.locks = {}  # path -> lock
        self.lock = threading.Lock()
    
    def acquire_read(self, path):
        with self.lock:
            if path not in self.locks:
                self.locks[path] = threading.RLock()
            self.locks[path].acquire()
    
    def release_read(self, path):
        with self.lock:
            if path in self.locks:
                self.locks[path].release()
    
    def acquire_write(self, path):
        # Exclusive lock
        with self.lock:
            if path not in self.locks:
                self.locks[path] = threading.RLock()
            self.locks[path].acquire()
```

**2. Directory-Level Locking**
- Lock parent directory during file creation/deletion
- Prevent concurrent modifications to directory structure

**3. Inode Locking**
- Lock inode during metadata updates
- Allow concurrent reads, exclusive writes

**In-Memory Storage:**

**1. Fine-Grained Locking**
```python
class ConcurrentHashTable:
    def __init__(self, num_buckets=16):
        self.buckets = [[] for _ in range(num_buckets)]
        self.locks = [threading.Lock() for _ in range(num_buckets)]
    
    def _get_bucket(self, key):
        return hash(key) % len(self.buckets)
    
    def get(self, key):
        bucket_idx = self._get_bucket(key)
        with self.locks[bucket_idx]:
            bucket = self.buckets[bucket_idx]
            for k, v in bucket:
                if k == key:
                    return v
            return None
    
    def put(self, key, value):
        bucket_idx = self._get_bucket(key)
        with self.locks[bucket_idx]:
            bucket = self.buckets[bucket_idx]
            for i, (k, v) in enumerate(bucket):
                if k == key:
                    bucket[i] = (key, value)
                    return
            bucket.append((key, value))
```

**2. Read-Write Locks**
- Multiple readers, single writer
- Better for read-heavy workloads

**3. Lock-Free Data Structures**
- Use atomic operations
- CAS (Compare-And-Swap) for updates
- More complex but better performance

### Durability and Persistence

**File System:**

**1. Journaling (Write-Ahead Logging)**
```
Transaction:
1. Write to journal log
2. Commit transaction
3. Write to actual file system
4. Checkpoint (mark transaction complete)
```

**Benefits:**
- Fast recovery after crash
- Atomic operations
- Consistency guarantees

**2. Copy-on-Write (COW)**
- Don't modify blocks in place
- Write new blocks, update pointers
- Atomic updates

**3. Checksums**
- Store checksums for blocks
- Detect corruption
- Enable recovery

**In-Memory Storage:**

**1. Snapshot Persistence**
```python
def save_snapshot(self, filepath):
    with open(filepath, 'wb') as f:
        pickle.dump(self.cache, f)

def load_snapshot(self, filepath):
    with open(filepath, 'rb') as f:
        self.cache = pickle.load(f)
```

**2. Write-Ahead Log (WAL)**
```python
class WAL:
    def __init__(self, log_file):
        self.log_file = open(log_file, 'ab')
    
    def append(self, operation, key, value):
        entry = {
            'op': operation,
            'key': key,
            'value': value,
            'timestamp': time.time()
        }
        self.log_file.write(pickle.dumps(entry))
        self.log_file.flush()
    
    def replay(self):
        # Replay log entries on startup
        pass
```

**3. Periodic Checkpoints**
- Periodically save full state
- Combine with WAL for recovery

### Caching Strategies

**File System:**

**1. Page Cache**
- Cache recently accessed file blocks in memory
- Reduce disk I/O
- LRU eviction policy

**2. Directory Cache**
- Cache directory entries
- Fast path resolution

**3. Metadata Cache**
- Cache inode information
- Reduce inode table lookups

**In-Memory Storage:**

**1. Multi-Level Cache**
- L1: Hot data in CPU cache
- L2: Warm data in RAM
- L3: Cold data on disk

**2. Prefetching**
- Predictively load data
- Reduce access latency

### Performance Optimization

**File System:**

**1. Block Size Optimization**
- Larger blocks: Better for large files, more waste for small files
- Smaller blocks: Better for small files, more overhead
- Typical: 4KB blocks

**2. Allocation Strategies**
- Pre-allocate blocks for growing files
- Allocate blocks near existing blocks (locality)

**3. Defragmentation**
- Reorganize files to reduce fragmentation
- Improve sequential access

**In-Memory Storage:**

**1. Hash Function Optimization**
- Fast hash functions (MurmurHash, CityHash)
- Good distribution to reduce collisions

**2. Memory Alignment**
- Align data structures to cache lines
- Reduce false sharing

**3. Batch Operations**
- Batch multiple operations
- Reduce overhead

### Scalability Considerations

**File System:**

**1. Distributed File Systems**
- Distribute files across multiple nodes
- Consistent hashing for file placement
- Replication for availability

**2. Metadata Servers**
- Separate metadata from data
- Scale metadata servers independently
- Cache metadata at clients

**3. Sharding**
- Partition file system by path or hash
- Balance load across nodes

**In-Memory Storage:**

**1. Distributed Hash Table (DHT)**
- Consistent hashing for key distribution
- Replication for availability
- Load balancing

**2. Partitioning**
- Partition by key range or hash
- Each partition on different node

**3. Replication**
- Replicate data across nodes
- Eventual consistency
- Read from replicas, write to primary

## Trade-offs and Design Decisions

### File System Trade-offs

**1. Block Size**
- **Small blocks (1KB)**: Less waste, more overhead
- **Large blocks (64KB)**: More waste, less overhead
- **Trade-off**: Balance between waste and overhead
- **Decision**: 4KB blocks (common standard)

**2. Allocation Strategy**
- **Contiguous**: Fast but fragmented
- **Indexed**: Flexible but overhead
- **Trade-off**: Performance vs flexibility
- **Decision**: Indexed allocation (extents for large files)

**3. Journaling**
- **Full journaling**: Slower but safer
- **Metadata journaling**: Faster but less safe
- **Trade-off**: Performance vs safety
- **Decision**: Metadata journaling (common in ext4)

**4. Caching**
- **Aggressive caching**: Fast but memory intensive
- **Conservative caching**: Slower but memory efficient
- **Trade-off**: Memory vs performance
- **Decision**: Adaptive caching based on memory pressure

### In-Memory Storage Trade-offs

**1. Hash Table vs B-Tree**
- **Hash Table**: O(1) access, no range queries
- **B-Tree**: O(log n) access, supports range queries
- **Trade-off**: Access speed vs query flexibility
- **Decision**: Hash table for key-value, B-tree for range queries

**2. Eviction Policy**
- **LRU**: Good for temporal locality
- **LFU**: Good for frequency-based access
- **Trade-off**: Different access patterns
- **Decision**: LRU (most common, good general purpose)

**3. Persistence**
- **No persistence**: Fast but data loss on crash
- **Full persistence**: Safe but slower
- **Trade-off**: Performance vs durability
- **Decision**: Optional persistence (configurable)

**4. Concurrency**
- **Coarse-grained locking**: Simple but less concurrent
- **Fine-grained locking**: Complex but more concurrent
- **Trade-off**: Complexity vs performance
- **Decision**: Fine-grained locking (bucket-level)

## Comparison: File System vs In-Memory Storage

| Aspect | File System | In-Memory Storage |
|--------|-------------|-------------------|
| **Storage Medium** | Disk (persistent) | RAM (volatile) |
| **Access Speed** | Slower (ms) | Faster (μs) |
| **Capacity** | Large (TB+) | Limited (GB) |
| **Durability** | Persistent | Volatile (optional persistence) |
| **Data Model** | Hierarchical (files/directories) | Flat (key-value) |
| **Use Cases** | Long-term storage, large files | Caching, temporary data, fast access |
| **Concurrency** | File/directory level | Key level |
| **Metadata** | Rich (permissions, timestamps) | Minimal (optional TTL) |
| **Operations** | Create, read, write, delete files | Put, get, delete keys |
| **Scalability** | Distributed file systems | Distributed hash tables |

## What Interviewers Look For

### Data Structures Knowledge

1. **Understanding of Storage Data Structures**
   - Inode structure and metadata management
   - Block allocation strategies
   - Hash table vs B-tree trade-offs
   - **Red Flags**: No understanding of data structures, wrong choices

2. **Algorithm Efficiency**
   - O(1) vs O(log n) operations
   - Memory efficiency considerations
   - **Red Flags**: Inefficient algorithms, high memory overhead

### System Design Skills

1. **Storage Organization**
   - Block-based vs extent-based allocation
   - Directory structure design
   - **Red Flags**: Poor organization, inefficient structures

2. **Metadata Management**
   - Inode design
   - Directory entry structure
   - **Red Flags**: Missing metadata, poor design

### Problem-Solving Approach

1. **Concurrency Control**
   - File-level vs directory-level locking
   - Thread-safe operations
   - **Red Flags**: No locking, race conditions

2. **Durability Mechanisms**
   - Journaling strategies
   - Persistence approaches
   - **Red Flags**: No durability, data loss scenarios

3. **Edge Cases**
   - Large files
   - Many small files
   - Fragmentation
   - **Red Flags**: Ignoring edge cases

### Code Quality

1. **Implementation Correctness**
   - Correct data structure implementation
   - Proper error handling
   - **Red Flags**: Bugs, no error handling

2. **Memory Management**
   - Efficient memory usage
   - Proper allocation/deallocation
   - **Red Flags**: Memory leaks, inefficient usage

### Meta-Specific Focus

1. **Storage Systems Expertise**
   - Deep understanding of file systems
   - In-memory storage knowledge
   - **Key**: Show strong systems programming skills

2. **Data Structures Mastery**
   - Understanding of complex structures
   - Trade-off analysis
   - **Key**: Demonstrate CS fundamentals

## Summary

### Key Takeaways

**File System Design:**
1. **Inode-based architecture**: Efficient metadata management
2. **Block allocation**: Indexed allocation for flexibility
3. **Journaling**: Ensure consistency and fast recovery
4. **Caching**: Page cache for performance
5. **Concurrency**: File and directory level locking

**In-Memory Storage Design:**
1. **Hash table**: O(1) access for key-value operations
2. **Eviction policies**: LRU/LFU for memory management
3. **Concurrency**: Fine-grained locking for performance
4. **Persistence**: Optional WAL and snapshots
5. **Memory management**: Efficient allocation and compression

### Design Principles

1. **Efficiency**: Optimize for common operations
2. **Scalability**: Design for growth
3. **Reliability**: Handle failures gracefully
4. **Performance**: Minimize latency and maximize throughput
5. **Simplicity**: Keep design simple and maintainable

### Common Interview Questions

1. **Design a file system**
   - Inode structure
   - Block allocation
   - Directory management
   - Concurrency control

2. **Design an LRU cache**
   - Hash map + doubly linked list
   - O(1) operations
   - Thread safety

3. **Design a key-value store**
   - Hash table implementation
   - Eviction policies
   - Persistence
   - Distributed design

4. **Design a distributed file system**
   - Metadata servers
   - Data distribution
   - Replication
   - Consistency

### Further Reading

- **File Systems**: ext4, XFS, ZFS design papers
- **In-Memory Storage**: Redis, Memcached architecture
- **Distributed Systems**: GFS, HDFS design papers
- **Data Structures**: Hash tables, B-trees, LRU caches

Understanding file system and in-memory storage design is crucial for system design interviews, especially for roles involving storage systems, databases, and operating systems. Focus on data structures, concurrency, durability, and scalability when designing these systems.

