---
layout: post
title: "Design a Circular Buffer / Ring Buffer - System Design Interview"
date: 2025-11-24
categories: [System Design, Interview Example, Data Structures, Non-Distributed Systems, Buffer Systems]
excerpt: "A comprehensive guide to designing a circular buffer (ring buffer), covering fixed-size buffer implementation, producer-consumer synchronization, wraparound handling, and lock-free implementations."
---

## Introduction

A circular buffer (also called ring buffer) is a fixed-size buffer that uses a single, fixed-size buffer as if it were connected end-to-end. When the buffer is full, new data overwrites the oldest data. Circular buffers are used in embedded systems, audio processing, network packet buffering, and producer-consumer scenarios.

This guide covers the design of circular buffers, including implementation patterns, thread safety, and performance optimizations.

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Requirements](#requirements)
3. [Core Components](#core-components)
4. [API Design](#api-design)
5. [Detailed Design](#detailed-design)
6. [Thread-Safe Implementation](#thread-safe-implementation)
7. [Lock-Free Implementation](#lock-free-implementation)
8. [Trade-offs](#trade-offs)
9. [Summary](#summary)

## Problem Statement

**Design a circular buffer that:**

1. **Fixed-size buffer** with wraparound
2. **Producer writes** data to buffer
3. **Consumer reads** data from buffer
4. **Handles full/empty** conditions
5. **Thread-safe** for concurrent access
6. **Efficient** O(1) operations

**Scale Requirements:**
- Support 1KB to 1MB buffer sizes
- Handle 1K-1M operations per second
- Low latency: < 100ns per operation
- Memory efficient: fixed size

## Requirements

### Functional Requirements

1. **Write**: Add item to buffer (overwrite if full)
2. **Read**: Remove item from buffer
3. **Peek**: Read without removing
4. **Size**: Get current number of items
5. **Empty/Full**: Check buffer state

### Non-Functional Requirements

**Performance:**
- O(1) operations
- Low latency
- Cache-friendly

**Thread Safety:**
- Safe for single producer, single consumer
- Optional: multiple producers/consumers

## Core Components

### 1. Buffer Array
- Fixed-size array
- Stores elements
- Wraparound indexing

### 2. Read/Write Pointers
- Read pointer (head)
- Write pointer (tail)
- Track buffer state

### 3. Synchronization
- Locks (for multi-threaded)
- Atomic operations (lock-free)

## API Design

```python
class CircularBuffer:
    def __init__(self, capacity: int):
        """
        Initialize circular buffer.
        
        Args:
            capacity: Maximum number of elements
        """
        pass
    
    def write(self, item: Any) -> bool:
        """
        Write item to buffer.
        
        Returns:
            True if written, False if full (overwrite mode)
        """
        pass
    
    def read(self) -> Optional[Any]:
        """Read and remove item from buffer."""
        pass
    
    def peek(self) -> Optional[Any]:
        """Peek at next item without removing."""
        pass
    
    def size(self) -> int:
        """Get current size."""
        pass
    
    def is_empty(self) -> bool:
        """Check if empty."""
        pass
    
    def is_full(self) -> bool:
        """Check if full."""
        pass
```

## Detailed Design

### Basic Implementation

```python
from typing import Any, Optional

class CircularBuffer:
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.buffer = [None] * capacity
        self.read_ptr = 0
        self.write_ptr = 0
        self.size = 0
    
    def write(self, item: Any, overwrite: bool = False) -> bool:
        """Write item to buffer."""
        if self.is_full():
            if not overwrite:
                return False  # Buffer full
            # Overwrite: advance read pointer
            self.read_ptr = (self.read_ptr + 1) % self.capacity
            self.size -= 1
        
        self.buffer[self.write_ptr] = item
        self.write_ptr = (self.write_ptr + 1) % self.capacity
        self.size += 1
        return True
    
    def read(self) -> Optional[Any]:
        """Read and remove item."""
        if self.is_empty():
            return None
        
        item = self.buffer[self.read_ptr]
        self.buffer[self.read_ptr] = None  # Clear reference
        self.read_ptr = (self.read_ptr + 1) % self.capacity
        self.size -= 1
        return item
    
    def peek(self) -> Optional[Any]:
        """Peek at next item."""
        if self.is_empty():
            return None
        return self.buffer[self.read_ptr]
    
    def size(self) -> int:
        """Get current size."""
        return self.size
    
    def is_empty(self) -> bool:
        """Check if empty."""
        return self.size == 0
    
    def is_full(self) -> bool:
        """Check if full."""
        return self.size == self.capacity
```

### Alternative: Using Read/Write Pointers Only

```python
class CircularBufferV2:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.buffer = [None] * capacity
        self.read_ptr = 0
        self.write_ptr = 0
        # Use one empty slot to distinguish full from empty
        self.count = 0
    
    def write(self, item: Any) -> bool:
        """Write item."""
        if self.is_full():
            return False
        
        self.buffer[self.write_ptr] = item
        self.write_ptr = (self.write_ptr + 1) % self.capacity
        self.count += 1
        return True
    
    def read(self) -> Optional[Any]:
        """Read item."""
        if self.is_empty():
            return None
        
        item = self.buffer[self.read_ptr]
        self.read_ptr = (self.read_ptr + 1) % self.capacity
        self.count -= 1
        return item
    
    def is_empty(self) -> bool:
        return self.count == 0
    
    def is_full(self) -> bool:
        return self.count == self.capacity
```

## Thread-Safe Implementation

### Single Producer, Single Consumer

```python
import threading

class ThreadSafeCircularBuffer:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.buffer = [None] * capacity
        self.read_ptr = 0
        self.write_ptr = 0
        self.count = 0
        self.lock = threading.Lock()
        self.not_empty = threading.Condition(self.lock)
        self.not_full = threading.Condition(self.lock)
    
    def write(self, item: Any, block: bool = True) -> bool:
        """Write item, blocking if full."""
        with self.lock:
            if not block and self.is_full():
                return False
            
            while self.is_full():
                self.not_full.wait()
            
            self.buffer[self.write_ptr] = item
            self.write_ptr = (self.write_ptr + 1) % self.capacity
            self.count += 1
            self.not_empty.notify()
            return True
    
    def read(self, block: bool = True) -> Optional[Any]:
        """Read item, blocking if empty."""
        with self.lock:
            if not block and self.is_empty():
                return None
            
            while self.is_empty():
                self.not_empty.wait()
            
            item = self.buffer[self.read_ptr]
            self.buffer[self.read_ptr] = None
            self.read_ptr = (self.read_ptr + 1) % self.capacity
            self.count -= 1
            self.not_full.notify()
            return item
    
    def is_empty(self) -> bool:
        return self.count == 0
    
    def is_full(self) -> bool:
        return self.count == self.capacity
```

## Lock-Free Implementation

### Single Producer, Single Consumer (Lock-Free)

```python
import ctypes
from ctypes import c_int, c_void_p, POINTER

class LockFreeCircularBuffer:
    """Lock-free circular buffer for single producer, single consumer."""
    def __init__(self, capacity: int):
        # Capacity must be power of 2 for efficient modulo
        self.capacity = 1
        while self.capacity < capacity:
            self.capacity <<= 1
        self.mask = self.capacity - 1
        
        self.buffer = [None] * self.capacity
        # Use atomic operations for pointers
        self.read_ptr = ctypes.c_int(0)
        self.write_ptr = ctypes.c_int(0)
    
    def write(self, item: Any) -> bool:
        """Write item (lock-free)."""
        write_pos = self.write_ptr.value
        next_write = (write_pos + 1) & self.mask
        
        # Check if full (read_ptr would catch up)
        if next_write == (self.read_ptr.value & self.mask):
            return False  # Full
        
        self.buffer[write_pos] = item
        self.write_ptr.value = next_write
        return True
    
    def read(self) -> Optional[Any]:
        """Read item (lock-free)."""
        read_pos = self.read_ptr.value
        
        # Check if empty
        if read_pos == (self.write_ptr.value & self.mask):
            return None  # Empty
        
        item = self.buffer[read_pos]
        self.buffer[read_pos] = None
        self.read_ptr.value = (read_pos + 1) & self.mask
        return item
    
    def size(self) -> int:
        """Get size (approximate, not thread-safe)."""
        write = self.write_ptr.value & self.mask
        read = self.read_ptr.value & self.mask
        if write >= read:
            return write - read
        return self.capacity - (read - write)
```

## Trade-offs

### Size Tracking vs Pointer Comparison

**Size Tracking:**
- Simple full/empty check
- Extra variable to maintain
- Slightly more overhead

**Pointer Comparison:**
- No extra variable
- Need sentinel value or one empty slot
- Slightly more complex logic

### Lock-Based vs Lock-Free

**Lock-Based:**
- Simpler implementation
- Works for multiple producers/consumers
- May have contention

**Lock-Free:**
- Better performance
- Only works for single producer/consumer
- More complex implementation

### Power of 2 Capacity

**Power of 2:**
- Efficient modulo (bitwise AND)
- Faster operations
- May waste space

**Arbitrary Size:**
- No space waste
- Slower modulo operation
- More flexible

## What Interviewers Look For

### Data Structure Skills

1. **Circular Buffer Understanding**
   - Wraparound mechanism
   - Full/empty detection
   - Pointer management
   - **Red Flags**: Incorrect wraparound, wrong full/empty logic

2. **Efficiency Considerations**
   - O(1) operations
   - Cache-friendly design
   - Memory efficiency
   - **Red Flags**: Inefficient operations, poor memory usage

3. **Lock-Free vs Lock-Based**
   - Understanding of trade-offs
   - When to use which approach
   - **Red Flags**: Wrong choice, no understanding

### Problem-Solving Approach

1. **Full/Empty Detection**
   - Size tracking vs pointer comparison
   - Sentinel value usage
   - **Red Flags**: Incorrect detection, bugs

2. **Thread Safety**
   - Single vs multiple producers/consumers
   - Proper synchronization
   - **Red Flags**: Race conditions, incorrect synchronization

3. **Edge Cases**
   - Buffer full
   - Buffer empty
   - Wraparound scenarios
   - **Red Flags**: Ignoring edge cases, incorrect handling

### Code Quality

1. **Implementation Correctness**
   - Correct buffer logic
   - Proper pointer management
   - **Red Flags**: Bugs, incorrect logic

2. **Performance**
   - Efficient operations
   - Minimal overhead
   - **Red Flags**: Slow operations, high overhead

### Meta-Specific Focus

1. **Data Structures Mastery**
   - Understanding of efficient structures
   - Trade-off analysis
   - **Key**: Show CS fundamentals

2. **Systems Programming**
   - Low-level optimization
   - Memory efficiency
   - **Key**: Demonstrate systems skills

## Summary

### Key Takeaways

1. **Fixed Size**: Pre-allocated buffer, wraparound
2. **Pointers**: Read and write pointers track position
3. **Wraparound**: Use modulo for circular indexing
4. **Full/Empty**: Distinguish using size or sentinel
5. **Thread Safety**: Locks or lock-free for concurrent access

### Design Principles

1. **Efficiency**: O(1) operations, cache-friendly
2. **Simplicity**: Keep implementation simple
3. **Thread Safety**: Safe concurrent access
4. **Performance**: Minimize overhead

### Common Use Cases

1. **Audio Buffering**: Audio stream buffering
2. **Network Packets**: Packet buffering
3. **Log Buffering**: Recent log entries
4. **Producer-Consumer**: Decouple producers and consumers
5. **Embedded Systems**: Fixed memory constraints

Understanding circular buffers is crucial for:
- Embedded systems
- Real-time systems
- Audio/video processing
- Network programming
- System design interviews

