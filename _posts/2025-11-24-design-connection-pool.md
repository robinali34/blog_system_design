---
layout: post
title: "Design a Connection Pool - System Design Interview"
date: 2025-11-24
categories: [System Design, Interview Example, Resource Management, Non-Distributed Systems, Database Systems]
excerpt: "A comprehensive guide to designing a connection pool for managing database, HTTP, or socket connections, covering pool initialization, connection lifecycle, health checking, timeout handling, and resource management."
---

## Introduction

A connection pool is a cache of connections maintained so that connections can be reused when needed, rather than creating new connections for each request. Connection pools are essential for database systems, HTTP clients, and network applications to reduce connection overhead and improve performance.

This guide covers the design of a connection pool system, including pool management, connection lifecycle, health checking, timeout handling, and resource limits.

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Requirements](#requirements)
3. [Core Components](#core-components)
4. [API Design](#api-design)
5. [Detailed Design](#detailed-design)
6. [Connection Lifecycle](#connection-lifecycle)
7. [Health Checking](#health-checking)
8. [Trade-offs](#trade-offs)
9. [Summary](#summary)

## Problem Statement

**Design a connection pool that:**

1. **Manages a pool of connections** (database, HTTP, socket)
2. **Reuses connections** instead of creating new ones
3. **Handles connection lifecycle** (create, validate, destroy)
4. **Monitors connection health** and removes dead connections
5. **Enforces resource limits** (max connections, timeouts)
6. **Provides thread-safe** connection acquisition/release

**Scale Requirements:**
- Support 10-1000 connections
- Handle 1K-100K requests per second
- Connection creation: 10-100ms
- Connection acquisition: < 1ms
- Low overhead: < 1% CPU

## Requirements

### Functional Requirements

1. **Get Connection**: Acquire connection from pool
2. **Return Connection**: Return connection to pool
3. **Create Connection**: Create new connection when needed
4. **Validate Connection**: Check if connection is valid
5. **Close Connection**: Remove connection from pool
6. **Health Check**: Monitor connection health

### Non-Functional Requirements

**Performance:**
- Fast acquisition: < 1ms
- Connection reuse: > 90% reuse rate
- Low overhead

**Reliability:**
- Handle dead connections
- Automatic recovery
- No connection leaks

**Resource Management:**
- Enforce max connections
- Handle timeouts
- Efficient memory usage

## Core Components

### 1. Connection Pool
- Manages connection collection
- Enforces limits
- Handles acquisition/release

### 2. Connection Factory
- Creates new connections
- Validates connections
- Closes connections

### 3. Connection Wrapper
- Wraps actual connection
- Tracks state
- Handles lifecycle

## API Design

```python
class ConnectionPool:
    def __init__(self,
                 factory: ConnectionFactory,
                 min_size: int = 5,
                 max_size: int = 20,
                 timeout: float = 30.0,
                 max_idle_time: float = 300.0):
        """
        Initialize connection pool.
        
        Args:
            factory: Factory for creating connections
            min_size: Minimum pool size
            max_size: Maximum pool size
            timeout: Connection acquisition timeout
            max_idle_time: Max idle time before closing
        """
        pass
    
    def get_connection(self, timeout: float = None) -> Connection:
        """Get connection from pool."""
        pass
    
    def return_connection(self, connection: Connection):
        """Return connection to pool."""
        pass
    
    def close_all(self):
        """Close all connections."""
        pass
    
    def get_stats(self) -> PoolStats:
        """Get pool statistics."""
        pass
```

## Detailed Design

```python
import threading
import queue
import time
from typing import Optional, Callable
from dataclasses import dataclass

@dataclass
class Connection:
    id: str
    connection: Any  # Actual connection object
    created_at: float
    last_used_at: float
    is_in_use: bool

class ConnectionFactory:
    def create(self) -> Any:
        """Create new connection."""
        raise NotImplementedError
    
    def validate(self, connection: Any) -> bool:
        """Validate connection is alive."""
        raise NotImplementedError
    
    def close(self, connection: Any):
        """Close connection."""
        raise NotImplementedError

class ConnectionPool:
    def __init__(self,
                 factory: ConnectionFactory,
                 min_size: int = 5,
                 max_size: int = 20,
                 timeout: float = 30.0,
                 max_idle_time: float = 300.0,
                 health_check_interval: float = 60.0):
        self.factory = factory
        self.min_size = min_size
        self.max_size = max_size
        self.timeout = timeout
        self.max_idle_time = max_idle_time
        self.health_check_interval = health_check_interval
        
        # Connection storage
        self.available = queue.Queue()  # Available connections
        self.in_use = {}  # connection_id -> Connection
        self.all_connections = {}  # connection_id -> Connection
        
        # Statistics
        self.stats = {
            'total_created': 0,
            'total_closed': 0,
            'current_size': 0,
            'in_use_count': 0,
            'available_count': 0
        }
        self.stats_lock = threading.Lock()
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Background threads
        self.health_check_thread = threading.Thread(target=self._health_check_loop, daemon=True)
        self.health_check_thread.start()
        
        # Initialize pool
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize pool with minimum connections."""
        for _ in range(self.min_size):
            conn = self._create_connection()
            if conn:
                self.available.put(conn)
    
    def _create_connection(self) -> Optional[Connection]:
        """Create new connection."""
        with self.lock:
            if len(self.all_connections) >= self.max_size:
                return None
        
        try:
            actual_conn = self.factory.create()
            conn = Connection(
                id=f"conn_{time.time()}_{id(actual_conn)}",
                connection=actual_conn,
                created_at=time.time(),
                last_used_at=time.time(),
                is_in_use=False
            )
            
            with self.lock:
                self.all_connections[conn.id] = conn
                with self.stats_lock:
                    self.stats['total_created'] += 1
                    self.stats['current_size'] += 1
            
            return conn
        except Exception as e:
            print(f"Failed to create connection: {e}")
            return None
    
    def get_connection(self, timeout: float = None) -> Optional[Connection]:
        """Get connection from pool."""
        timeout = timeout or self.timeout
        deadline = time.time() + timeout
        
        while time.time() < deadline:
            try:
                # Try to get from available queue
                conn = self.available.get(timeout=0.1)
                
                # Validate connection
                if not self.factory.validate(conn.connection):
                    # Connection is dead, remove it
                    self._remove_connection(conn)
                    continue
                
                # Mark as in use
                with self.lock:
                    conn.is_in_use = True
                    conn.last_used_at = time.time()
                    self.in_use[conn.id] = conn
                    with self.stats_lock:
                        self.stats['in_use_count'] += 1
                        self.stats['available_count'] = max(0, self.stats['available_count'] - 1)
                
                return conn
                
            except queue.Empty:
                # No available connections, try to create new one
                with self.lock:
                    if len(self.all_connections) < self.max_size:
                        conn = self._create_connection()
                        if conn:
                            conn.is_in_use = True
                            conn.last_used_at = time.time()
                            self.in_use[conn.id] = conn
                            with self.stats_lock:
                                self.stats['in_use_count'] += 1
                            return conn
        
        # Timeout
        raise TimeoutError("Could not acquire connection within timeout")
    
    def return_connection(self, connection: Connection):
        """Return connection to pool."""
        if connection.id not in self.all_connections:
            return  # Already removed
        
        with self.lock:
            if connection.id in self.in_use:
                del self.in_use[connection.id]
                connection.is_in_use = False
                connection.last_used_at = time.time()
                
                with self.stats_lock:
                    self.stats['in_use_count'] = max(0, self.stats['in_use_count'] - 1)
                    self.stats['available_count'] += 1
                
                # Return to available queue
                self.available.put(connection)
    
    def _remove_connection(self, connection: Connection):
        """Remove connection from pool."""
        with self.lock:
            if connection.id in self.all_connections:
                del self.all_connections[connection.id]
            if connection.id in self.in_use:
                del self.in_use[connection.id]
            
            try:
                self.factory.close(connection.connection)
            except:
                pass
            
            with self.stats_lock:
                self.stats['total_closed'] += 1
                self.stats['current_size'] = max(0, self.stats['current_size'] - 1)
    
    def _health_check_loop(self):
        """Background thread for health checking."""
        while True:
            time.sleep(self.health_check_interval)
            self._health_check()
    
    def _health_check(self):
        """Check and remove dead/idle connections."""
        current_time = time.time()
        to_remove = []
        
        with self.lock:
            for conn_id, conn in list(self.all_connections.items()):
                if conn.is_in_use:
                    continue
                
                # Check if idle too long
                if current_time - conn.last_used_at > self.max_idle_time:
                    to_remove.append(conn)
                    continue
                
                # Validate connection
                if not self.factory.validate(conn.connection):
                    to_remove.append(conn)
        
        # Remove dead/idle connections
        for conn in to_remove:
            self._remove_connection(conn)
        
        # Ensure minimum pool size
        with self.lock:
            current_available = self.stats['available_count']
            if current_available < self.min_size:
                for _ in range(self.min_size - current_available):
                    if len(self.all_connections) < self.max_size:
                        conn = self._create_connection()
                        if conn:
                            self.available.put(conn)
    
    def close_all(self):
        """Close all connections."""
        with self.lock:
            for conn in list(self.all_connections.values()):
                self._remove_connection(conn)
    
    def get_stats(self) -> dict:
        """Get pool statistics."""
        with self.stats_lock:
            return self.stats.copy()
```

## Connection Lifecycle

1. **Creation**: Create when pool below min_size or on demand
2. **Validation**: Check health before use
3. **Acquisition**: Get from pool, mark in-use
4. **Usage**: Use connection for operations
5. **Return**: Return to pool, mark available
6. **Health Check**: Periodic validation
7. **Removal**: Remove if dead or idle too long

## Health Checking

**Strategies:**
1. **On Acquisition**: Validate before use
2. **Periodic**: Background thread checks
3. **On Return**: Validate when returned
4. **Ping/Query**: Send test query

**Implementation:**
- Validate connection state
- Remove dead connections
- Recreate if below minimum

## Trade-offs

### Pool Size

**Small Pool:**
- Less memory
- May wait for connections
- Lower overhead

**Large Pool:**
- More memory
- Faster acquisition
- Higher overhead

### Health Check Frequency

**Frequent:**
- Detect issues faster
- Higher overhead

**Infrequent:**
- Lower overhead
- May use dead connections

## What Interviewers Look For

### Resource Management Skills

1. **Pool Management**
   - Min/max size configuration
   - Connection lifecycle management
   - Health checking strategies
   - **Red Flags**: No size limits, no health checks

2. **Connection Reuse**
   - Efficient connection reuse
   - Overhead reduction
   - **Red Flags**: Creating new connections each time, high overhead

3. **Thread Safety**
   - Safe concurrent access
   - Proper synchronization
   - **Red Flags**: Race conditions, no synchronization

### Problem-Solving Approach

1. **Health Monitoring**
   - Dead connection detection
   - Automatic recovery
   - Idle connection cleanup
   - **Red Flags**: No health checks, dead connections in pool

2. **Resource Limits**
   - Max connection enforcement
   - Timeout handling
   - **Red Flags**: No limits, resource exhaustion

3. **Edge Cases**
   - Connection failures
   - Pool exhaustion
   - Timeout scenarios
   - **Red Flags**: Ignoring edge cases, no handling

### Code Quality

1. **Error Handling**
   - Connection failure handling
   - Graceful degradation
   - **Red Flags**: No error handling, crashes

2. **Resource Cleanup**
   - Proper connection closing
   - No resource leaks
   - **Red Flags**: Connection leaks, no cleanup

### Meta-Specific Focus

1. **Resource Management**
   - Efficient resource utilization
   - Proper lifecycle management
   - **Key**: Show resource management skills

2. **Concurrency Skills**
   - Thread-safe operations
   - Proper synchronization
   - **Key**: Demonstrate concurrency understanding

## Summary

### Key Takeaways

1. **Connection Reuse**: Reduce creation overhead
2. **Pool Management**: Min/max size, health checks
3. **Thread Safety**: Safe concurrent access
4. **Resource Limits**: Enforce max connections
5. **Health Monitoring**: Detect and remove dead connections

### Design Principles

1. **Efficiency**: Reuse connections, fast acquisition
2. **Reliability**: Handle dead connections, automatic recovery
3. **Resource Management**: Enforce limits, prevent leaks
4. **Simplicity**: Keep design simple and maintainable

Understanding connection pool design is crucial for:
- Database systems
- HTTP clients
- Network applications
- Resource management
- Performance optimization

