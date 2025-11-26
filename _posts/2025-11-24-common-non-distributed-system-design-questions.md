---
layout: post
title: "Common Non-Distributed System Design Interview Questions - Complete List"
date: 2025-11-24
categories: [System Design, Interview Questions, Non-Distributed Systems, Local Systems, Single-Machine Systems, Operating Systems]
excerpt: "A comprehensive list of common non-distributed system design interview questions that focus on single-machine systems, local storage, concurrency, memory management, and operating system components. Essential for interviews focusing on low-level system design."
---

## Introduction

Non-distributed system design questions focus on designing systems that run on a single machine or within a single process. These questions test your understanding of data structures, algorithms, memory management, concurrency, operating system concepts, and efficient resource utilization.

Unlike distributed system design questions, non-distributed questions emphasize:
- **Single-machine constraints**: Limited memory, CPU, disk
- **Local operations**: No network communication
- **Efficiency**: Optimal algorithms and data structures
- **Concurrency**: Thread safety and synchronization
- **Resource management**: Memory, CPU, I/O management

This post provides a comprehensive list of common non-distributed system design interview questions organized by category.

## Table of Contents

1. [Storage and Data Structures](#storage-and-data-structures)
2. [Concurrency and Threading](#concurrency-and-threading)
3. [Memory Management](#memory-management)
4. [Task and Process Management](#task-and-process-management)
5. [Resource Pools](#resource-pools)
6. [Queues and Buffers](#queues-and-buffers)
7. [Caching Systems](#caching-systems)
8. [Event and Messaging Systems](#event-and-messaging-systems)
9. [Operating System Components](#operating-system-components)
10. [I/O and File Systems](#io-and-file-systems)
11. [Search and Indexing](#search-and-indexing)
12. [Summary](#summary)

## Storage and Data Structures

### 1. Design a File System or In-Memory Storage
**Status**: ✅ [Covered](/blog_system_design/2025/11/24/design-file-system-in-memory-storage/)

**Key Focus Areas:**
- Inode structure and metadata management
- Block allocation strategies
- Directory hierarchy
- Concurrency control
- Durability and journaling

**Common Variations:**
- Design a file system with specific block size
- Design an in-memory key-value store
- Design a local database (SQLite-like)

### 2. Design a Key-Value Store (Local)
**Status**: ✅ [Covered](/blog_system_design/2025/11/14/design-key-value-store-local-horizontal/)

**Key Focus Areas:**
- Hash table implementation
- B-tree for range queries
- Memory management
- Persistence strategies
- Concurrency control

### 3. Design a Local Database
**Key Focus Areas:**
- Storage engine design
- Index structures (B-tree, hash index)
- Query execution
- Transaction management (ACID)
- WAL (Write-Ahead Logging)
- Buffer pool management

**Common Variations:**
- Design SQLite
- Design a document database
- Design a time-series database

### 4. Design a Search Index (Local)
**Key Focus Areas:**
- Inverted index structure
- Tokenization and indexing
- Query processing
- Ranking algorithms
- Memory-efficient storage

**Common Variations:**
- Design a full-text search engine
- Design a local search index for files

## Concurrency and Threading

### 5. Design a Thread Pool
**Status**: ✅ [Covered](/blog_system_design/2025/11/24/design-thread-pool/)

**Key Focus Areas:**
- Thread pool architecture
- Task queue management
- Thread lifecycle management
- Load balancing
- Shutdown and graceful termination
- Exception handling

**Common Variations:**
- Design a fixed-size thread pool
- Design a dynamic thread pool
- Design a work-stealing thread pool

### 6. Design a Producer-Consumer Queue
**Status**: ✅ [Covered](/blog_system_design/2025/11/24/design-producer-consumer-queue/)

**Key Focus Areas:**
- Bounded/unbounded queue
- Blocking vs non-blocking operations
- Multiple producers/consumers
- Backpressure handling
- Priority queues

**Common Variations:**
- Design a blocking queue
- Design a lock-free queue
- Design a priority queue

### 7. Design a Concurrent Data Structure
**Key Focus Areas:**
- Lock-free algorithms
- Lock-based synchronization
- CAS (Compare-And-Swap) operations
- Memory ordering
- Performance optimization

**Common Variations:**
- Design a concurrent hash map
- Design a concurrent linked list
- Design a concurrent stack

### 8. Design a Synchronization Primitive
**Key Focus Areas:**
- Mutex implementation
- Semaphore implementation
- Condition variable
- Read-write locks
- Barrier implementation

**Common Variations:**
- Design a mutex
- Design a semaphore
- Design a read-write lock

## Memory Management

### 9. Design a Memory Allocator
**Status**: ✅ [Covered](/blog_system_design/2025/11/24/design-memory-allocator/)

**Key Focus Areas:**
- Memory pool design
- Allocation strategies (first-fit, best-fit, worst-fit)
- Fragmentation management
- Free list management
- Alignment handling
- Thread-local allocation

**Common Variations:**
- Design a malloc/free implementation
- Design a memory pool allocator
- Design a garbage collector

### 10. Design a Garbage Collector
**Status**: ⚠️ Needs detailed post

**Key Focus Areas:**
- Mark-and-sweep algorithm
- Generational garbage collection
- Reference counting
- Stop-the-world vs concurrent
- Memory compaction

**Common Variations:**
- Design a mark-and-sweep GC
- Design a generational GC
- Design a reference counting GC

### 11. Design a Memory Cache with Eviction
**Key Focus Areas:**
- LRU/LFU/FIFO eviction
- Memory limits
- TTL support
- Thread safety

**Common Variations:**
- Design an LRU cache
- Design an LFU cache
- Design a cache with TTL

## Task and Process Management

### 12. Design a Task Scheduler (Single Machine)
**Status**: ✅ [Covered](/blog_system_design/2025/11/24/design-task-scheduler-single-machine/)

**Key Focus Areas:**
- Task queue management
- Priority scheduling
- Scheduling algorithms (FIFO, priority, round-robin)
- Task dependencies
- Retry mechanisms
- Task persistence

**Common Variations:**
- Design a priority task scheduler
- Design a cron-like scheduler
- Design a task queue with dependencies

### 13. Design a Process Manager
**Key Focus Areas:**
- Process lifecycle management
- Process scheduling
- Resource allocation
- Inter-process communication
- Process isolation

**Common Variations:**
- Design a process scheduler
- Design a process manager for containers

### 14. Design a Job Queue
**Key Focus Areas:**
- Job storage
- Job execution
- Priority handling
- Retry logic
- Job status tracking

**Common Variations:**
- Design a background job queue
- Design a priority job queue

## Resource Pools

### 15. Design a Connection Pool
**Status**: ✅ [Covered](/blog_system_design/2025/11/24/design-connection-pool/)

**Key Focus Areas:**
- Pool initialization
- Connection acquisition/release
- Connection lifecycle
- Health checking
- Pool sizing
- Timeout handling

**Common Variations:**
- Design a database connection pool
- Design a HTTP connection pool
- Design a socket connection pool

### 16. Design a Resource Pool
**Key Focus Areas:**
- Resource allocation
- Resource reuse
- Pool management
- Resource limits
- Fairness and priority

**Common Variations:**
- Design a thread pool (see #5)
- Design a memory pool
- Design a file handle pool

## Queues and Buffers

### 17. Design a Circular Buffer / Ring Buffer
**Status**: ✅ [Covered](/blog_system_design/2025/11/24/design-circular-buffer/)

**Key Focus Areas:**
- Fixed-size buffer
- Producer/consumer synchronization
- Wraparound handling
- Full/empty detection
- Lock-free implementation

**Common Variations:**
- Design a ring buffer
- Design a circular queue
- Design a lock-free ring buffer

### 18. Design a Message Queue (Local)
**Key Focus Areas:**
- Queue storage
- Message ordering
- Priority queues
- Message persistence
- Acknowledgment handling

**Common Variations:**
- Design a local message queue
- Design a priority message queue

### 19. Design a Buffer Manager
**Key Focus Areas:**
- Buffer allocation
- Buffer replacement policies
- Dirty page tracking
- Flush strategies
- Memory limits

**Common Variations:**
- Design a database buffer pool
- Design a file system buffer cache

## Caching Systems

### 20. Design an LRU Cache
**Status**: ✅ Mentioned in multiple posts

**Key Focus Areas:**
- Hash map + doubly linked list
- O(1) operations
- Thread safety
- Memory limits

**Common Variations:**
- Design an LRU cache
- Design an LFU cache
- Design a cache with TTL

### 21. Design a Multi-Level Cache
**Key Focus Areas:**
- Cache hierarchy
- Cache coherence
- Eviction policies
- Cache warming

**Common Variations:**
- Design L1/L2/L3 cache
- Design CPU cache hierarchy

## Event and Messaging Systems

### 22. Design an Event System
**Status**: ⚠️ Needs detailed post

**Key Focus Areas:**
- Event registration
- Event dispatch
- Event filtering
- Asynchronous handling
- Event ordering

**Common Variations:**
- Design a local event bus
- Design an observer pattern
- Design a pub/sub system (local)

### 23. Design a Local Logger
**Status**: ✅ [Covered](/blog_system_design/2025/11/24/design-local-logger/)

**Key Focus Areas:**
- Log levels
- Log formatting
- Log rotation
- Async logging
- Performance optimization

**Common Variations:**
- Design a logging framework
- Design a structured logger
- Design a high-performance logger

## Operating System Components

### 24. Design a Virtual Memory Manager
**Key Focus Areas:**
- Page table management
- Page replacement algorithms (LRU, FIFO, Clock)
- Memory mapping
- Swap space management
- TLB (Translation Lookaside Buffer)

**Common Variations:**
- Design a paging system
- Design a virtual memory manager

### 25. Design a Process Scheduler
**Key Focus Areas:**
- Scheduling algorithms
- Priority management
- Context switching
- Preemption
- Multi-core scheduling

**Common Variations:**
- Design a CPU scheduler
- Design a real-time scheduler

### 26. Design a File Watcher
**Key Focus Areas:**
- File system monitoring
- Event notification
- Efficient polling
- Event filtering
- Performance optimization

**Common Variations:**
- Design a file system watcher
- Design inotify-like system

### 27. Design a Device Driver Interface
**Key Focus Areas:**
- Hardware abstraction
- Interrupt handling
- DMA management
- Device registration
- Resource management

**Common Variations:**
- Design a device driver framework
- Design a HAL (Hardware Abstraction Layer)

## I/O and File Systems

### 28. Design a File System (see #1)
**Status**: ✅ [Covered](/blog_system_design/2025/11/24/design-file-system-in-memory-storage/)

### 29. Design a File Watcher (see #26)

### 30. Design an I/O Scheduler
**Key Focus Areas:**
- I/O request queuing
- Request merging
- Priority handling
- Deadline scheduling
- Fairness

**Common Variations:**
- Design a disk I/O scheduler
- Design a network I/O scheduler

## Search and Indexing

### 31. Design a Local Search Index (see #4)

### 32. Design a Trie / Prefix Tree
**Key Focus Areas:**
- Trie structure
- Insert/search operations
- Memory optimization
- Prefix matching
- Autocomplete support

**Common Variations:**
- Design a trie
- Design a compressed trie
- Design a radix tree

## What Interviewers Look For

### Non-Distributed System Design Skills

1. **Data Structure Selection**
   - Appropriate data structures for the problem
   - Time/space complexity understanding
   - **Red Flags**: Wrong data structure, poor complexity, no justification

2. **Algorithm Design**
   - Efficient algorithms
   - Optimization for common cases
   - **Red Flags**: Inefficient algorithms, no optimization, poor performance

3. **Memory Management**
   - Allocation/deallocation strategies
   - Fragmentation handling
   - **Red Flags**: Memory leaks, fragmentation issues, no management

### Concurrency Skills

1. **Thread Safety**
   - Proper synchronization
   - Lock-free programming where appropriate
   - **Red Flags**: Race conditions, deadlocks, no synchronization

2. **Concurrent Data Structures**
   - Thread-safe implementations
   - Lock-free algorithms
   - **Red Flags**: Not thread-safe, poor concurrency, bottlenecks

3. **Resource Management**
   - Proper resource allocation
   - Deadlock prevention
   - **Red Flags**: Resource leaks, deadlocks, poor management

### Problem-Solving Approach

1. **Requirements Clarification**
   - Functional requirements
   - Non-functional requirements
   - **Red Flags**: No clarification, assumptions, wrong requirements

2. **Edge Case Handling**
   - Full/empty conditions
   - Resource exhaustion
   - **Red Flags**: Ignoring edge cases, no handling, incomplete

3. **Trade-off Analysis**
   - Memory vs speed
   - Simplicity vs performance
   - **Red Flags**: No trade-offs, dogmatic choices, no justification

### System Design Skills

1. **Component Design**
   - Clear component boundaries
   - Appropriate abstractions
   - **Red Flags**: Monolithic, unclear boundaries, poor abstractions

2. **API Design**
   - Clean interfaces
   - Appropriate operations
   - **Red Flags**: Poor API, missing operations, unclear interfaces

3. **Code Implementation**
   - Can implement key operations
   - Clean, efficient code
   - **Red Flags**: Can't implement, poor code, inefficient

### Communication Skills

1. **Design Explanation**
   - Clear explanations
   - Justifies decisions
   - **Red Flags**: Unclear, no justification, can't explain

2. **Code Walkthrough**
   - Can explain code
   - Understands complexity
   - **Red Flags**: Can't explain, no understanding, vague

### Meta-Specific Focus

1. **Local System Expertise**
   - Deep understanding of local systems
   - Efficient algorithms
   - **Key**: Show local system expertise

2. **Concurrency Mastery**
   - Thread safety knowledge
   - Lock-free programming
   - **Key**: Demonstrate concurrency expertise

## Summary

### Most Common Non-Distributed System Design Questions

**High Priority (Frequently Asked):**
1. ✅ Design a File System or In-Memory Storage
2. ✅ Design a Key-Value Store (Local)
3. ⚠️ Design a Thread Pool
4. ⚠️ Design a Task Scheduler (Single Machine)
5. ⚠️ Design a Memory Allocator
6. ⚠️ Design a Connection Pool
7. ⚠️ Design a Producer-Consumer Queue
8. ⚠️ Design an LRU Cache
9. ⚠️ Design a Circular Buffer
10. ⚠️ Design a Local Logger

**Medium Priority:**
11. Design a Garbage Collector
12. Design a Concurrent Data Structure
13. Design a Local Database
14. Design an Event System
15. Design a Buffer Manager

**Lower Priority (Domain-Specific):**
16. Design a Virtual Memory Manager
17. Design a Process Scheduler
18. Design a Device Driver Interface
19. Design a File Watcher
20. Design a Trie / Prefix Tree

### Key Skills Tested

1. **Data Structures**: Hash tables, trees, linked lists, queues
2. **Algorithms**: Scheduling, allocation, eviction, search
3. **Concurrency**: Thread safety, synchronization, lock-free programming
4. **Memory Management**: Allocation, deallocation, fragmentation
5. **System Programming**: OS concepts, I/O, resource management
6. **Performance**: Optimization, caching, efficient algorithms

### Interview Tips

1. **Start with Requirements**: Clarify functional and non-functional requirements
2. **Design Data Structures**: Choose appropriate data structures
3. **Consider Concurrency**: Thread safety is critical
4. **Optimize for Common Cases**: Focus on typical usage patterns
5. **Handle Edge Cases**: Full queues, empty queues, resource exhaustion
6. **Discuss Trade-offs**: Memory vs speed, simplicity vs performance
7. **Write Code**: Be prepared to implement key operations

### Next Steps

For detailed design guides on these questions, see:
- ✅ [File System / In-Memory Storage](/blog_system_design/2025/11/24/design-file-system-in-memory-storage/)
- ✅ [Key-Value Store (Local)](/blog_system_design/2025/11/14/design-key-value-store-local-horizontal/)
- ✅ [Thread Pool](/blog_system_design/2025/11/24/design-thread-pool/)
- ✅ [Task Scheduler (Single Machine)](/blog_system_design/2025/11/24/design-task-scheduler-single-machine/)
- ✅ [Memory Allocator](/blog_system_design/2025/11/24/design-memory-allocator/)
- ✅ [Connection Pool](/blog_system_design/2025/11/24/design-connection-pool/)
- ✅ [Producer-Consumer Queue](/blog_system_design/2025/11/24/design-producer-consumer-queue/)
- ✅ [Circular Buffer](/blog_system_design/2025/11/24/design-circular-buffer/)
- ✅ [Local Logger](/blog_system_design/2025/11/24/design-local-logger/)

Understanding non-distributed system design is crucial for interviews focusing on:
- Operating systems
- Embedded systems
- System programming
- Low-level optimization
- Performance-critical applications

