---
layout: post
title: "Design a Local Logger - System Design Interview"
date: 2025-11-24
categories: [System Design, Interview Example, Logging, Non-Distributed Systems, I/O Systems]
excerpt: "A comprehensive guide to designing a local logging system, covering log levels, formatting, rotation, async logging, buffering, and performance optimization for high-throughput logging scenarios."
---

## Introduction

A local logger is a system component that records application events, errors, and debug information to local storage (files, console, or memory). Designing an efficient logger requires handling high write throughput, log rotation, formatting, filtering, and asynchronous operations.

This guide covers the design of a local logging system, including log levels, formatting, rotation strategies, async logging, and performance optimizations.

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Requirements](#requirements)
3. [Core Components](#core-components)
4. [API Design](#api-design)
5. [Detailed Design](#detailed-design)
6. [Log Rotation](#log-rotation)
7. [Async Logging](#async-logging)
8. [Performance Optimization](#performance-optimization)
9. [Trade-offs](#trade-offs)
10. [Summary](#summary)

## Problem Statement

**Design a local logger that:**

1. **Records log messages** with different levels
2. **Formats messages** consistently
3. **Writes to files** or console
4. **Rotates logs** to prevent disk full
5. **Handles high throughput** (async logging)
6. **Filters by level** and other criteria
7. **Provides thread-safe** operations

**Scale Requirements:**
- Handle 1K-1M log messages per second
- Support log files from KB to GB
- Low overhead: < 1% CPU
- Fast writes: < 10μs per message

## Requirements

### Functional Requirements

1. **Log Levels**: DEBUG, INFO, WARN, ERROR, FATAL
2. **Formatting**: Timestamp, level, message, context
3. **Multiple Handlers**: File, console, memory
4. **Log Rotation**: Size-based, time-based
5. **Filtering**: By level, module, pattern
6. **Structured Logging**: JSON, key-value pairs

### Non-Functional Requirements

**Performance:**
- Fast writes: < 10μs
- High throughput: 1M+ messages/sec
- Low memory overhead

**Reliability:**
- No log loss
- Handle disk full
- Graceful degradation

**Usability:**
- Easy configuration
- Readable format
- Searchable logs

## Core Components

### 1. Logger
- Main interface
- Log level management
- Message formatting

### 2. Handler
- Writes to destination
- File, console, etc.
- Handles rotation

### 3. Formatter
- Formats messages
- Timestamp, level, etc.
- Structured formats

### 4. Filter
- Filters messages
- By level, pattern, etc.

## API Design

```python
class Logger:
    def __init__(self, name: str, level: LogLevel = LogLevel.INFO):
        """Initialize logger."""
        pass
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        pass
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        pass
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        pass
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        pass
    
    def fatal(self, message: str, **kwargs):
        """Log fatal message."""
        pass
```

## Detailed Design

### Basic Logger

```python
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any
import threading

class LogLevel(Enum):
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    FATAL = 50

class Logger:
    def __init__(self, name: str, level: LogLevel = LogLevel.INFO):
        self.name = name
        self.level = level
        self.handlers = []
        self.filters = []
        self.lock = threading.Lock()
    
    def add_handler(self, handler):
        """Add log handler."""
        with self.lock:
            self.handlers.append(handler)
    
    def log(self, level: LogLevel, message: str, **kwargs):
        """Log message at specified level."""
        if level.value < self.level.value:
            return  # Below threshold
        
        record = LogRecord(
            name=self.name,
            level=level,
            message=message,
            timestamp=datetime.now(),
            **kwargs
        )
        
        # Apply filters
        for filter in self.filters:
            if not filter.filter(record):
                return
        
        # Write to handlers
        with self.lock:
            for handler in self.handlers:
                handler.handle(record)
    
    def debug(self, message: str, **kwargs):
        self.log(LogLevel.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        self.log(LogLevel.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self.log(LogLevel.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self.log(LogLevel.ERROR, message, **kwargs)
    
    def fatal(self, message: str, **kwargs):
        self.log(LogLevel.FATAL, message, **kwargs)

class LogRecord:
    def __init__(self, name: str, level: LogLevel, message: str, 
                 timestamp: datetime, **kwargs):
        self.name = name
        self.level = level
        self.message = message
        self.timestamp = timestamp
        self.extra = kwargs
```

### Handler

```python
class Handler:
    def __init__(self, formatter=None, level: LogLevel = LogLevel.DEBUG):
        self.formatter = formatter or DefaultFormatter()
        self.level = level
    
    def handle(self, record: LogRecord):
        """Handle log record."""
        if record.level.value < self.level.value:
            return
        
        formatted = self.formatter.format(record)
        self.emit(formatted)
    
    def emit(self, message: str):
        """Emit formatted message."""
        raise NotImplementedError

class FileHandler(Handler):
    def __init__(self, filename: str, **kwargs):
        super().__init__(**kwargs)
        self.filename = filename
        self.file = open(filename, 'a')
        self.lock = threading.Lock()
    
    def emit(self, message: str):
        """Write to file."""
        with self.lock:
            self.file.write(message + '\n')
            self.file.flush()
    
    def close(self):
        """Close file."""
        if self.file:
            self.file.close()

class ConsoleHandler(Handler):
    def emit(self, message: str):
        """Write to console."""
        print(message)
```

### Formatter

```python
class Formatter:
    def format(self, record: LogRecord) -> str:
        """Format log record."""
        raise NotImplementedError

class DefaultFormatter(Formatter):
    def format(self, record: LogRecord) -> str:
        """Default format: timestamp level name message"""
        timestamp = record.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')
        level_name = record.level.name
        return f"{timestamp} [{level_name}] {record.name}: {record.message}"

class JSONFormatter(Formatter):
    def format(self, record: LogRecord) -> str:
        """JSON format."""
        import json
        data = {
            'timestamp': record.timestamp.isoformat(),
            'level': record.level.name,
            'name': record.name,
            'message': record.message,
            **record.extra
        }
        return json.dumps(data)
```

## Log Rotation

### Size-Based Rotation

```python
class RotatingFileHandler(FileHandler):
    def __init__(self, filename: str, max_bytes: int = 10*1024*1024,
                 backup_count: int = 5, **kwargs):
        super().__init__(filename, **kwargs)
        self.max_bytes = max_bytes
        self.backup_count = backup_count
    
    def emit(self, message: str):
        """Emit with rotation check."""
        with self.lock:
            # Check if rotation needed
            if self.file.tell() + len(message) > self.max_bytes:
                self.rotate()
            
            self.file.write(message + '\n')
            self.file.flush()
    
    def rotate(self):
        """Rotate log file."""
        self.file.close()
        
        # Rotate existing files
        for i in range(self.backup_count - 1, 0, -1):
            old_name = f"{self.filename}.{i}"
            new_name = f"{self.filename}.{i+1}"
            if os.path.exists(old_name):
                os.rename(old_name, new_name)
        
        # Move current to .1
        if os.path.exists(self.filename):
            os.rename(self.filename, f"{self.filename}.1")
        
        # Open new file
        self.file = open(self.filename, 'a')
```

### Time-Based Rotation

```python
class TimedRotatingFileHandler(FileHandler):
    def __init__(self, filename: str, when: str = 'midnight',
                 interval: int = 1, **kwargs):
        super().__init__(filename, **kwargs)
        self.when = when
        self.interval = interval
        self.next_rollover = self._calculate_next_rollover()
    
    def emit(self, message: str):
        """Emit with time-based rotation."""
        with self.lock:
            if datetime.now() >= self.next_rollover:
                self.rotate()
            
            self.file.write(message + '\n')
            self.file.flush()
    
    def _calculate_next_rollover(self) -> datetime:
        """Calculate next rotation time."""
        now = datetime.now()
        if self.when == 'midnight':
            return (now + timedelta(days=1)).replace(hour=0, minute=0, second=0)
        # Add other when options...
        return now + timedelta(seconds=self.interval)
```

## Async Logging

```python
import queue
import threading

class AsyncHandler(Handler):
    def __init__(self, target_handler: Handler, queue_size: int = 1000):
        super().__init__(target_handler.formatter, target_handler.level)
        self.target_handler = target_handler
        self.queue = queue.Queue(maxsize=queue_size)
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.running = True
        self.worker_thread.start()
    
    def emit(self, message: str):
        """Queue message for async writing."""
        try:
            self.queue.put_nowait(message)
        except queue.Full:
            # Queue full, write synchronously or drop
            self.target_handler.emit(message)
    
    def _worker(self):
        """Worker thread for async writing."""
        while self.running:
            try:
                message = self.queue.get(timeout=1.0)
                self.target_handler.emit(message)
                self.queue.task_done()
            except queue.Empty:
                continue
    
    def close(self):
        """Close handler."""
        self.running = False
        self.worker_thread.join()
        self.target_handler.close()
```

## Performance Optimization

### Buffering

```python
class BufferedFileHandler(FileHandler):
    def __init__(self, filename: str, buffer_size: int = 8192, **kwargs):
        super().__init__(filename, **kwargs)
        self.buffer_size = buffer_size
        self.buffer = []
        self.buffer_bytes = 0
    
    def emit(self, message: str):
        """Emit with buffering."""
        message_bytes = len(message.encode())
        
        with self.lock:
            if self.buffer_bytes + message_bytes > self.buffer_size:
                self.flush()
            
            self.buffer.append(message)
            self.buffer_bytes += message_bytes
    
    def flush(self):
        """Flush buffer to file."""
        if self.buffer:
            self.file.write('\n'.join(self.buffer) + '\n')
            self.file.flush()
            self.buffer.clear()
            self.buffer_bytes = 0
```

## Trade-offs

### Sync vs Async Logging

**Sync:**
- Simple, reliable
- May block caller
- Lower throughput

**Async:**
- Non-blocking
- Higher throughput
- May lose logs on crash

### Buffering

**Buffered:**
- Better performance
- May lose on crash
- More memory

**Unbuffered:**
- Immediate writes
- Slower
- More reliable

## What Interviewers Look For

### System Design Skills

1. **Architecture Design**
   - Logger, Handler, Formatter separation
   - Clean component design
   - Extensibility
   - **Red Flags**: Monolithic design, poor separation

2. **Performance Optimization**
   - Async logging
   - Buffering strategies
   - High throughput design
   - **Red Flags**: Blocking operations, poor performance

3. **Log Rotation**
   - Size-based rotation
   - Time-based rotation
   - File management
   - **Red Flags**: No rotation, disk full issues

### Problem-Solving Approach

1. **Reliability**
   - No log loss
   - Handle disk full
   - Graceful degradation
   - **Red Flags**: Log loss, crashes on disk full

2. **Flexibility**
   - Multiple handlers
   - Custom formatters
   - Configurable levels
   - **Red Flags**: Hard-coded, not flexible

3. **Edge Cases**
   - High log volume
   - Disk full
   - Concurrent logging
   - **Red Flags**: Ignoring edge cases, no handling

### Code Quality

1. **Thread Safety**
   - Safe concurrent logging
   - Proper synchronization
   - **Red Flags**: Race conditions, data corruption

2. **Error Handling**
   - File write failures
   - Queue full handling
   - **Red Flags**: No error handling, crashes

### Meta-Specific Focus

1. **I/O Systems Understanding**
   - Efficient file operations
   - Performance optimization
   - **Key**: Show I/O systems knowledge

2. **Practical Design**
   - Real-world constraints
   - Performance vs reliability trade-offs
   - **Key**: Balance theory with practice

## Summary

### Key Takeaways

1. **Log Levels**: DEBUG, INFO, WARN, ERROR, FATAL
2. **Handlers**: File, console, async
3. **Formatters**: Default, JSON, custom
4. **Rotation**: Size-based, time-based
5. **Performance**: Buffering, async, batching

### Design Principles

1. **Performance**: Fast writes, high throughput
2. **Reliability**: No log loss, handle failures
3. **Flexibility**: Multiple handlers, formatters
4. **Usability**: Easy configuration, readable format

Understanding logger design is crucial for:
- Application development
- Debugging and monitoring
- System observability
- Performance optimization
- System design interviews

