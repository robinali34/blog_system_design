---
layout: post
title: "Design a Producer-Consumer Queue - System Design Interview"
date: 2025-11-24
categories: [System Design, Interview Example, Concurrency, Non-Distributed Systems, Queue Systems]
excerpt: "A comprehensive guide to designing a producer-consumer queue, covering bounded/unbounded queues, blocking/non-blocking operations, multiple producers and consumers, backpressure handling, and thread synchronization."
---

## Introduction

A producer-consumer queue is a concurrent data structure that allows multiple threads to produce items (producers) and consume items (consumers) safely. It's a fundamental pattern in concurrent programming for decoupling producers and consumers, managing backpressure, and coordinating work distribution.

This guide covers the design of producer-consumer queues, including bounded/unbounded implementations, blocking/non-blocking operations, and synchronization mechanisms.

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Requirements](#requirements)
3. [Core Components](#core-components)
4. [API Design](#api-design)
5. [Detailed Design](#detailed-design)
6. [Variations](#variations)
7. [Trade-offs](#trade-offs)
8. [Summary](#summary)

## Problem Statement

**Design a producer-consumer queue that:**

1. **Supports multiple producers** adding items concurrently
2. **Supports multiple consumers** removing items concurrently
3. **Provides thread-safe** operations
4. **Handles backpressure** (bounded queue)
5. **Supports blocking/non-blocking** operations
6. **Maintains ordering** (FIFO)

**Scale Requirements:**
- Support 1-1000 producers/consumers
- Handle 1K-1M items per second
- Low latency: < 1μs per operation
- Memory efficient

## Requirements

### Functional Requirements

1. **Put**: Add item to queue (blocking/non-blocking)
2. **Get**: Remove item from queue (blocking/non-blocking)
3. **Size**: Get current queue size
4. **Empty/Full**: Check if queue is empty/full
5. **Close**: Signal no more items

### Non-Functional Requirements

**Performance:**
- Fast operations: < 1μs
- High throughput
- Low contention

**Thread Safety:**
- Safe concurrent access
- No race conditions
- Deadlock prevention

## Core Components

### 1. Queue Storage
- Array or linked list
- Thread-safe access
- Bounded or unbounded

### 2. Synchronization
- Locks (mutex, condition variables)
- Atomic operations (lock-free)
- Semaphores

### 3. Producer/Consumer Coordination
- Blocking when full/empty
- Wake up on space/items available

## API Design

```python
class ProducerConsumerQueue:
    def __init__(self, maxsize: int = 0):
        """
        Initialize queue.
        
        Args:
            maxsize: Maximum size (0 for unbounded)
        """
        pass
    
    def put(self, item: Any, block: bool = True, timeout: float = None):
        """Put item in queue."""
        pass
    
    def get(self, block: bool = True, timeout: float = None) -> Any:
        """Get item from queue."""
        pass
    
    def qsize(self) -> int:
        """Get queue size."""
        pass
    
    def empty(self) -> bool:
        """Check if empty."""
        pass
    
    def full(self) -> bool:
        """Check if full."""
        pass
```

## Detailed Design

### Bounded Blocking Queue

```python
import threading
import queue
from typing import Any, Optional

class BoundedBlockingQueue:
    def __init__(self, maxsize: int):
        if maxsize <= 0:
            raise ValueError("maxsize must be positive")
        
        self.maxsize = maxsize
        self.queue = []
        self.lock = threading.Lock()
        self.not_empty = threading.Condition(self.lock)
        self.not_full = threading.Condition(self.lock)
        self.closed = False
    
    def put(self, item: Any, block: bool = True, timeout: Optional[float] = None):
        """Put item, blocking if full."""
        with self.lock:
            if self.closed:
                raise ValueError("Queue is closed")
            
            if not block:
                if len(self.queue) >= self.maxsize:
                    raise queue.Full
            else:
                deadline = None
                if timeout is not None:
                    deadline = time.time() + timeout
                
                while len(self.queue) >= self.maxsize:
                    if timeout is not None:
                        remaining = deadline - time.time()
                        if remaining <= 0:
                            raise queue.Full
                        self.not_full.wait(remaining)
                    else:
                        self.not_full.wait()
            
            self.queue.append(item)
            self.not_empty.notify()
    
    def get(self, block: bool = True, timeout: Optional[float] = None) -> Any:
        """Get item, blocking if empty."""
        with self.lock:
            if not block:
                if not self.queue:
                    raise queue.Empty
            else:
                deadline = None
                if timeout is not None:
                    deadline = time.time() + timeout
                
                while not self.queue:
                    if self.closed:
                        raise queue.Empty("Queue is closed")
                    if timeout is not None:
                        remaining = deadline - time.time()
                        if remaining <= 0:
                            raise queue.Empty
                        self.not_empty.wait(remaining)
                    else:
                        self.not_empty.wait()
            
            item = self.queue.pop(0)
            self.not_full.notify()
            return item
    
    def qsize(self) -> int:
        """Get queue size."""
        with self.lock:
            return len(self.queue)
    
    def empty(self) -> bool:
        """Check if empty."""
        with self.lock:
            return len(self.queue) == 0
    
    def full(self) -> bool:
        """Check if full."""
        with self.lock:
            return len(self.queue) >= self.maxsize
    
    def close(self):
        """Close queue (no more items)."""
        with self.lock:
            self.closed = True
            self.not_empty.notify_all()
```

### Unbounded Queue

```python
class UnboundedQueue:
    def __init__(self):
        self.queue = []
        self.lock = threading.Lock()
        self.not_empty = threading.Condition(self.lock)
        self.closed = False
    
    def put(self, item: Any):
        """Put item (never blocks)."""
        with self.lock:
            if self.closed:
                raise ValueError("Queue is closed")
            self.queue.append(item)
            self.not_empty.notify()
    
    def get(self, block: bool = True, timeout: Optional[float] = None) -> Any:
        """Get item, blocking if empty."""
        with self.lock:
            if not block:
                if not self.queue:
                    raise queue.Empty
            else:
                deadline = None
                if timeout is not None:
                    deadline = time.time() + timeout
                
                while not self.queue:
                    if self.closed:
                        raise queue.Empty
                    if timeout is not None:
                        remaining = deadline - time.time()
                        if remaining <= 0:
                            raise queue.Empty
                        self.not_empty.wait(remaining)
                    else:
                        self.not_empty.wait()
            
            return self.queue.pop(0)
```

### Lock-Free Queue (Simplified)

```python
import queue
from collections import deque
from threading import Lock

class LockFreeQueue:
    """Simplified lock-free queue using atomic operations."""
    def __init__(self, maxsize: int = 0):
        self.maxsize = maxsize
        self.queue = deque()
        self.lock = Lock()  # Simplified: use lock for thread safety
    
    def put(self, item: Any, block: bool = True, timeout: Optional[float] = None):
        """Put item."""
        if self.maxsize > 0:
            # Bounded queue
            with self.lock:
                if len(self.queue) >= self.maxsize:
                    if not block:
                        raise queue.Full
                    # Wait for space (simplified)
                self.queue.append(item)
        else:
            # Unbounded queue
            with self.lock:
                self.queue.append(item)
    
    def get(self, block: bool = True, timeout: Optional[float] = None) -> Any:
        """Get item."""
        with self.lock:
            if not self.queue:
                if not block:
                    raise queue.Empty
                # Wait for item (simplified)
            return self.queue.popleft()
```

## Variations

### Priority Queue

```python
import heapq

class PriorityProducerConsumerQueue:
    def __init__(self, maxsize: int = 0):
        self.maxsize = maxsize
        self.queue = []
        self.counter = 0
        self.lock = threading.Lock()
        self.not_empty = threading.Condition(self.lock)
        self.not_full = threading.Condition(self.lock)
    
    def put(self, item: Any, priority: int = 0):
        """Put item with priority."""
        with self.lock:
            if self.maxsize > 0 and len(self.queue) >= self.maxsize:
                self.not_full.wait()
            
            heapq.heappush(self.queue, (priority, self.counter, item))
            self.counter += 1
            self.not_empty.notify()
    
    def get(self) -> Any:
        """Get highest priority item."""
        with self.lock:
            while not self.queue:
                self.not_empty.wait()
            
            _, _, item = heapq.heappop(self.queue)
            if self.maxsize > 0:
                self.not_full.notify()
            return item
```

### Multiple Queues (Work Stealing)

```python
class WorkStealingQueue:
    def __init__(self, num_queues: int):
        self.queues = [queue.Queue() for _ in range(num_queues)]
        self.lock = threading.Lock()
    
    def put(self, item: Any, queue_id: int = None):
        """Put item to specific or random queue."""
        if queue_id is None:
            import random
            queue_id = random.randint(0, len(self.queues) - 1)
        self.queues[queue_id].put(item)
    
    def get(self, queue_id: int, steal: bool = True) -> Any:
        """Get from own queue, optionally steal from others."""
        # Try own queue first
        try:
            return self.queues[queue_id].get_nowait()
        except queue.Empty:
            pass
        
        # Steal from other queues
        if steal:
            for i in range(len(self.queues)):
                if i != queue_id:
                    try:
                        return self.queues[i].get_nowait()
                    except queue.Empty:
                        continue
        
        raise queue.Empty
```

## Trade-offs

### Bounded vs Unbounded

**Bounded:**
- Prevents memory issues
- Provides backpressure
- May block producers

**Unbounded:**
- No backpressure
- Memory growth risk
- Never blocks producers

### Blocking vs Non-Blocking

**Blocking:**
- Simpler code
- May block threads
- Better for coordination

**Non-Blocking:**
- Never blocks
- Requires polling/retry
- More complex

## What Interviewers Look For

### Concurrency Skills

1. **Thread Synchronization**
   - Proper use of locks and condition variables
   - Deadlock prevention
   - Race condition handling
   - **Red Flags**: Deadlocks, race conditions, no synchronization

2. **Blocking Mechanisms**
   - Condition variable usage
   - Timeout handling
   - **Red Flags**: Busy waiting, no proper blocking

3. **Thread Safety**
   - Safe concurrent operations
   - Proper state management
   - **Red Flags**: Unsafe operations, incorrect state

### Problem-Solving Approach

1. **Backpressure Handling**
   - Bounded queue design
   - Queue full scenarios
   - **Red Flags**: No backpressure, memory issues

2. **Multiple Producers/Consumers**
   - Safe concurrent access
   - Fairness considerations
   - **Red Flags**: Starvation, unfair access

3. **Edge Cases**
   - Empty queue
   - Full queue
   - Queue closure
   - **Red Flags**: Ignoring edge cases, crashes

### Code Quality

1. **Implementation Correctness**
   - Correct queue logic
   - Proper synchronization
   - **Red Flags**: Bugs, incorrect logic

2. **Error Handling**
   - Timeout handling
   - Queue full/empty handling
   - **Red Flags**: No error handling, unclear errors

### Meta-Specific Focus

1. **Concurrency Mastery**
   - Deep understanding of synchronization
   - Proper use of primitives
   - **Key**: Show strong concurrency skills

2. **Data Structure Design**
   - Efficient queue implementation
   - Proper abstraction
   - **Key**: Demonstrate design skills

## Summary

### Key Takeaways

1. **Thread Safety**: Use locks and condition variables
2. **Backpressure**: Bounded queues prevent memory issues
3. **Coordination**: Condition variables for blocking
4. **Ordering**: FIFO or priority-based
5. **Multiple Producers/Consumers**: Safe concurrent access

### Design Principles

1. **Thread Safety**: Safe concurrent operations
2. **Efficiency**: Fast operations, low contention
3. **Flexibility**: Support various use cases
4. **Simplicity**: Keep design simple

Understanding producer-consumer queues is crucial for:
- Concurrent programming
- Thread coordination
- Work distribution
- Backpressure management
- System design interviews

