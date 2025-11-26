---
layout: post
title: "Design a Memory Allocator - System Design Interview"
date: 2025-11-24
categories: [System Design, Interview Example, Memory Management, Non-Distributed Systems, Operating Systems]
excerpt: "A comprehensive guide to designing a memory allocator, covering allocation strategies, free list management, fragmentation handling, alignment, and memory pool design. Essential for system design interviews focusing on memory management and low-level systems."
---

## Introduction

A memory allocator is a system component responsible for managing dynamic memory allocation and deallocation. It provides functions like `malloc()` and `free()` that allow programs to request and release memory blocks. Designing an efficient memory allocator requires understanding allocation strategies, fragmentation management, alignment requirements, and performance optimization.

This is a common system design interview question that tests your understanding of memory management, data structures, algorithms, and low-level system programming. This guide covers the design of a memory allocator, including allocation algorithms, free list management, fragmentation handling, and implementation patterns.

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Requirements](#requirements)
3. [Core Components](#core-components)
4. [Allocation Strategies](#allocation-strategies)
5. [Detailed Design](#detailed-design)
6. [Memory Pool Allocator](#memory-pool-allocator)
7. [Trade-offs and Design Decisions](#trade-offs-and-design-decisions)
8. [Summary](#summary)

## Problem Statement

**Design a memory allocator that:**

1. **Allocates memory blocks** of requested sizes
2. **Deallocates memory blocks** and reuses them
3. **Manages free memory** efficiently
4. **Minimizes fragmentation** (internal and external)
5. **Handles alignment** requirements
6. **Provides thread safety** (optional)
7. **Tracks memory usage** and statistics

**Scale Requirements:**
- Support allocations from bytes to megabytes
- Handle millions of allocations/deallocations
- Low overhead: < 5% memory overhead
- Fast allocation: < 100ns for small blocks
- Efficient memory utilization: > 90%

## Requirements

### Functional Requirements

1. **Allocate**: `void* malloc(size_t size)` - Allocate memory block
2. **Deallocate**: `void free(void* ptr)` - Free memory block
3. **Reallocate**: `void* realloc(void* ptr, size_t size)` - Resize block
4. **Alignment**: Support alignment requirements (8, 16, 32 bytes)
5. **Thread Safety**: Optional thread-safe operations

### Non-Functional Requirements

**Performance:**
- Allocation: < 100ns for small blocks
- Deallocation: < 50ns
- Low fragmentation: < 10% wasted space

**Reliability:**
- No memory leaks
- Detect double-free
- Detect buffer overflows (optional)

**Efficiency:**
- High memory utilization: > 90%
- Low metadata overhead: < 5%

## Core Components

### 1. Memory Block Header
```c
typedef struct BlockHeader {
    size_t size;           // Block size (including header)
    bool is_free;          // Free flag
    struct BlockHeader* next;  // Next free block (if free)
    struct BlockHeader* prev;  // Previous free block (if free)
} BlockHeader;
```

### 2. Free List
- Linked list of free blocks
- Sorted by size or address
- Fast allocation and coalescing

### 3. Heap Manager
- Manages memory region
- Tracks allocated/free blocks
- Handles expansion

## Allocation Strategies

### 1. First Fit
- **Algorithm**: Allocate first block that fits
- **Pros**: Simple, fast
- **Cons**: May create fragmentation
- **Time**: O(n) where n = number of free blocks

### 2. Best Fit
- **Algorithm**: Allocate smallest block that fits
- **Pros**: Better memory utilization
- **Cons**: Slower, may create small fragments
- **Time**: O(n)

### 3. Worst Fit
- **Algorithm**: Allocate largest block
- **Pros**: Leaves large free blocks
- **Cons**: Poor utilization, slower
- **Time**: O(n)

### 4. Next Fit
- **Algorithm**: Start from last allocation position
- **Pros**: Faster than first fit
- **Cons**: Similar fragmentation to first fit
- **Time**: O(n) average

## Detailed Design

### Basic Allocator Implementation

```c
#include <stddef.h>
#include <stdbool.h>

#define ALIGNMENT 8
#define MIN_BLOCK_SIZE (sizeof(BlockHeader) + ALIGNMENT)

typedef struct BlockHeader {
    size_t size;
    bool is_free;
    struct BlockHeader* next;
    struct BlockHeader* prev;
} BlockHeader;

static BlockHeader* free_list = NULL;
static void* heap_start = NULL;
static size_t heap_size = 0;

// Align size to ALIGNMENT boundary
static size_t align_size(size_t size) {
    return (size + ALIGNMENT - 1) & ~(ALIGNMENT - 1);
}

// Get block header from pointer
static BlockHeader* get_header(void* ptr) {
    return (BlockHeader*)((char*)ptr - sizeof(BlockHeader));
}

// Initialize heap
void init_heap(void* start, size_t size) {
    heap_start = start;
    heap_size = size;
    
    BlockHeader* header = (BlockHeader*)start;
    header->size = size;
    header->is_free = true;
    header->next = NULL;
    header->prev = NULL;
    
    free_list = header;
}

// First fit allocation
void* malloc(size_t size) {
    if (size == 0) return NULL;
    
    size = align_size(size + sizeof(BlockHeader));
    
    // Search free list
    BlockHeader* current = free_list;
    while (current) {
        if (current->is_free && current->size >= size) {
            // Found block
            if (current->size >= size + MIN_BLOCK_SIZE) {
                // Split block
                BlockHeader* new_block = (BlockHeader*)((char*)current + size);
                new_block->size = current->size - size;
                new_block->is_free = true;
                new_block->next = current->next;
                new_block->prev = current->prev;
                
                // Update free list
                if (new_block->next) new_block->next->prev = new_block;
                if (new_block->prev) new_block->prev->next = new_block;
                else free_list = new_block;
                
                current->size = size;
            } else {
                // Remove from free list
                if (current->next) current->next->prev = current->prev;
                if (current->prev) current->prev->next = current->next;
                else free_list = current->next;
            }
            
            current->is_free = false;
            current->next = NULL;
            current->prev = NULL;
            
            return (char*)current + sizeof(BlockHeader);
        }
        current = current->next;
    }
    
    return NULL; // No free block found
}

// Free block
void free(void* ptr) {
    if (!ptr) return;
    
    BlockHeader* header = get_header(ptr);
    if (header->is_free) {
        // Double free detection
        return;
    }
    
    header->is_free = true;
    
    // Coalesce with adjacent free blocks
    BlockHeader* next = (BlockHeader*)((char*)header + header->size);
    if ((char*)next < (char*)heap_start + heap_size && next->is_free) {
        // Merge with next
        header->size += next->size;
        if (next->next) next->next->prev = header;
        if (next->prev) next->prev->next = header;
        if (free_list == next) free_list = header;
    }
    
    // Add to free list
    header->next = free_list;
    header->prev = NULL;
    if (free_list) free_list->prev = header;
    free_list = header;
}
```

### Best Fit Implementation

```c
void* malloc_best_fit(size_t size) {
    if (size == 0) return NULL;
    
    size = align_size(size + sizeof(BlockHeader));
    
    BlockHeader* best = NULL;
    BlockHeader* current = free_list;
    
    // Find smallest block that fits
    while (current) {
        if (current->is_free && current->size >= size) {
            if (!best || current->size < best->size) {
                best = current;
            }
        }
        current = current->next;
    }
    
    if (!best) return NULL;
    
    // Allocate from best block (similar splitting logic)
    // ... (same as first fit)
    
    return (char*)best + sizeof(BlockHeader);
}
```

## Memory Pool Allocator

**Concept**: Pre-allocate fixed-size blocks for faster allocation.

```c
typedef struct Pool {
    void* memory;
    size_t block_size;
    size_t num_blocks;
    void* free_list;
} Pool;

Pool* create_pool(size_t block_size, size_t num_blocks) {
    Pool* pool = malloc(sizeof(Pool));
    pool->block_size = block_size;
    pool->num_blocks = num_blocks;
    pool->memory = malloc(block_size * num_blocks);
    
    // Initialize free list
    pool->free_list = pool->memory;
    void* current = pool->memory;
    for (size_t i = 0; i < num_blocks - 1; i++) {
        void* next = (char*)current + block_size;
        *(void**)current = next;
        current = next;
    }
    *(void**)current = NULL;
    
    return pool;
}

void* pool_alloc(Pool* pool) {
    if (!pool->free_list) return NULL;
    
    void* block = pool->free_list;
    pool->free_list = *(void**)block;
    return block;
}

void pool_free(Pool* pool, void* ptr) {
    *(void**)ptr = pool->free_list;
    pool->free_list = ptr;
}
```

## Trade-offs and Design Decisions

### First Fit vs Best Fit

**First Fit:**
- Faster allocation
- May create fragmentation
- Simpler implementation

**Best Fit:**
- Better utilization
- Slower allocation
- May create small fragments

### Free List Organization

**Unsorted:**
- Simple
- O(n) search

**Sorted by Size:**
- Faster best fit
- O(n) insertion

**Sorted by Address:**
- Faster coalescing
- O(n) insertion

### Coalescing Strategy

**Immediate Coalescing:**
- Merge on free
- Better utilization
- Slightly slower free

**Deferred Coalescing:**
- Merge on allocation
- Faster free
- May fragment more

## What Interviewers Look For

### Memory Management Skills

1. **Allocation Algorithm Knowledge**
   - Understanding of first-fit, best-fit, worst-fit
   - Trade-offs between algorithms
   - When to use which strategy
   - **Red Flags**: No algorithm knowledge, wrong choice

2. **Fragmentation Understanding**
   - Internal vs external fragmentation
   - Fragmentation reduction strategies
   - Coalescing mechanisms
   - **Red Flags**: No fragmentation awareness, poor strategies

3. **Free List Management**
   - Efficient free list organization
   - Coalescing adjacent blocks
   - **Red Flags**: Inefficient free list, no coalescing

### Problem-Solving Approach

1. **Memory Efficiency**
   - Minimize overhead
   - Reduce fragmentation
   - Efficient space utilization
   - **Red Flags**: High overhead, excessive fragmentation

2. **Edge Cases**
   - Alignment requirements
   - Large vs small allocations
   - Memory exhaustion
   - **Red Flags**: Ignoring edge cases, no handling

3. **Error Detection**
   - Double-free detection
   - Buffer overflow detection
   - Memory leak detection
   - **Red Flags**: No error detection, unsafe operations

### Code Quality

1. **Implementation Correctness**
   - Correct allocation logic
   - Proper free list management
   - **Red Flags**: Bugs, incorrect logic

2. **Memory Safety**
   - No memory leaks
   - Proper bounds checking
   - **Red Flags**: Memory leaks, buffer overflows

### Meta-Specific Focus

1. **Systems Programming Expertise**
   - Deep understanding of memory management
   - Low-level programming skills
   - **Key**: Show systems-level knowledge

2. **Algorithm Efficiency**
   - Understanding of time/space complexity
   - Optimization strategies
   - **Key**: Demonstrate CS fundamentals

## Summary

### Key Takeaways

1. **Allocation Strategies**: First fit, best fit, worst fit, next fit
2. **Free List Management**: Linked list of free blocks
3. **Fragmentation**: Internal (waste in block) and external (waste between blocks)
4. **Coalescing**: Merge adjacent free blocks
5. **Memory Pools**: Fixed-size blocks for performance

### Design Principles

1. **Efficiency**: Fast allocation/deallocation
2. **Utilization**: Minimize fragmentation
3. **Simplicity**: Keep design simple
4. **Reliability**: Detect errors, prevent leaks

Understanding memory allocator design is crucial for interviews focusing on:
- Operating systems
- Memory management
- Low-level systems
- Performance optimization
- System programming

