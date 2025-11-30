---
layout: post
title: "etcd: Comprehensive Guide to Distributed Key-Value Store and Coordination"
date: 2025-11-29
categories: [etcd, Distributed Systems, Key-Value Store, Coordination, System Design, Technology]
excerpt: "A comprehensive guide to etcd, covering distributed key-value storage, consensus algorithm (Raft), watch mechanism, leases, and best practices for building distributed coordination systems."
---

## Introduction

etcd is a distributed, reliable key-value store for the most critical data of a distributed system. It's used for service discovery, configuration management, and coordination. Understanding etcd is essential for system design interviews involving distributed systems and coordination.

This guide covers:
- **etcd Fundamentals**: Key-value storage, Raft consensus, and watch mechanism
- **Operations**: Get, put, delete, and watch operations
- **Leases**: TTL-based key expiration
- **Transactions**: Atomic operations
- **Best Practices**: Performance, security, and monitoring

## What is etcd?

etcd is a distributed key-value store that:
- **Distributed**: Runs across multiple nodes
- **Consistent**: Raft consensus algorithm
- **Reliable**: Data replication and persistence
- **Watch**: Real-time change notifications
- **Fast**: Low latency operations

### Key Concepts

**Key**: String identifier for stored value

**Value**: Data stored in etcd

**Revision**: Monotonically increasing version number

**Lease**: TTL-based expiration mechanism

**Watch**: Real-time change notification

**Transaction**: Atomic multi-operation

## Core Architecture

```
┌─────────────────────────────────────────────────────────┐
│              etcd Cluster                               │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │         etcd Node 1 (Leader)                     │   │
│  │  (Raft Consensus, Key-Value Store)               │   │
│  └──────────────────────────────────────────────────┘   │
│                          │                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │         etcd Node 2 (Follower)                   │   │
│  │  (Replication, Consensus)                        │   │
│  └──────────────────────────────────────────────────┘   │
│                          │                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │         etcd Node 3 (Follower)                   │   │
│  │  (Replication, Consensus)                        │   │
│  └──────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────┘
```

## Basic Operations

### Put (Write)

**CLI:**
```bash
etcdctl put /config/database/url "postgresql://localhost:5432/mydb"
```

**Go Client:**
```go
package main

import (
    "context"
    "fmt"
    "go.etcd.io/etcd/clientv3"
    "time"
)

func main() {
    cli, err := clientv3.New(clientv3.Config{
        Endpoints:   []string{"localhost:2379"},
        DialTimeout: 5 * time.Second,
    })
    if err != nil {
        panic(err)
    }
    defer cli.Close()
    
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    _, err = cli.Put(ctx, "/config/database/url", 
        "postgresql://localhost:5432/mydb")
    cancel()
    
    if err != nil {
        panic(err)
    }
}
```

**Python Client:**
```python
import etcd3

client = etcd3.client(host='localhost', port=2379)
client.put('/config/database/url', 'postgresql://localhost:5432/mydb')
```

### Get (Read)

**CLI:**
```bash
etcdctl get /config/database/url
```

**Go Client:**
```go
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
resp, err := cli.Get(ctx, "/config/database/url")
cancel()

if err != nil {
    panic(err)
}

for _, ev := range resp.Kvs {
    fmt.Printf("%s: %s\n", ev.Key, ev.Value)
}
```

**With Revision:**
```go
resp, err := cli.Get(ctx, "/config/database/url", 
    clientv3.WithRev(100))
```

### Delete

**CLI:**
```bash
etcdctl del /config/database/url
```

**Go Client:**
```go
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
_, err := cli.Delete(ctx, "/config/database/url")
cancel()
```

**Delete with Prefix:**
```go
_, err := cli.Delete(ctx, "/config/", clientv3.WithPrefix())
```

## Watch Mechanism

### Watch Key

**Go Client:**
```go
watchChan := cli.Watch(context.Background(), "/config/database/url")

for watchResp := range watchChan {
    for _, ev := range watchResp.Events {
        switch ev.Type {
        case clientv3.EventTypePut:
            fmt.Printf("PUT: %s = %s\n", ev.Kv.Key, ev.Kv.Value)
        case clientv3.EventTypeDelete:
            fmt.Printf("DELETE: %s\n", ev.Kv.Key)
        }
    }
}
```

**Watch with Revision:**
```go
watchChan := cli.Watch(context.Background(), "/config/database/url",
    clientv3.WithRev(100))
```

**Watch with Prefix:**
```go
watchChan := cli.Watch(context.Background(), "/config/",
    clientv3.WithPrefix())
```

### Python Client

```python
import etcd3

client = etcd3.client(host='localhost', port=2379)

def watch_callback(event):
    if isinstance(event, etcd3.events.PutEvent):
        print(f"PUT: {event.key} = {event.value}")
    elif isinstance(event, etcd3.events.DeleteEvent):
        print(f"DELETE: {event.key}")

client.add_watch_callback('/config/database/url', watch_callback)
```

## Leases

### Create Lease

**Go Client:**
```go
// Grant lease with 60 second TTL
lease, err := cli.Grant(context.TODO(), 60)
if err != nil {
    panic(err)
}

// Put with lease
_, err = cli.Put(context.TODO(), "/session/lock", "locked",
    clientv3.WithLease(lease.ID))

// Keep lease alive
keepAliveChan, err := cli.KeepAlive(context.TODO(), lease.ID)
if err != nil {
    panic(err)
}

go func() {
    for ka := range keepAliveChan {
        fmt.Printf("Lease kept alive: %d\n", ka.ID)
    }
}()
```

**Revoke Lease:**
```go
_, err := cli.Revoke(context.TODO(), lease.ID)
```

### Use Cases

**Session Management:**
```go
// Create session with lease
lease, _ := cli.Grant(context.TODO(), 30)
cli.Put(context.TODO(), "/sessions/user123", "active",
    clientv3.WithLease(lease.ID))

// Keep session alive
cli.KeepAlive(context.TODO(), lease.ID)
```

**Distributed Locks:**
```go
// Acquire lock with lease
lease, _ := cli.Grant(context.TODO(), 10)
cli.Put(context.TODO(), "/locks/resource1", "locked",
    clientv3.WithLease(lease.ID))

// Keep lock alive
cli.KeepAlive(context.TODO(), lease.ID)
```

## Transactions

### Compare-and-Swap

**Go Client:**
```go
txn := cli.Txn(context.TODO())

txn.If(clientv3.Compare(clientv3.Value("/config/version"), "=", "1")).
    Then(clientv3.OpPut("/config/version", "2")).
    Else(clientv3.OpGet("/config/version"))

resp, err := txn.Commit()
if err != nil {
    panic(err)
}

if resp.Succeeded {
    fmt.Println("Transaction succeeded")
} else {
    fmt.Println("Transaction failed")
}
```

### Atomic Operations

**Increment Counter:**
```go
txn := cli.Txn(context.TODO())

txn.If(clientv3.Compare(clientv3.Value("/counter"), "=", "10")).
    Then(clientv3.OpPut("/counter", "11")).
    Else(clientv3.OpGet("/counter"))

resp, err := txn.Commit()
```

## Raft Consensus

### Leader Election

**How it Works:**
1. Nodes start as candidates
2. Candidate requests votes
3. Node with majority becomes leader
4. Leader handles all writes
5. Followers replicate from leader

### Consistency Guarantees

- **Linearizability**: Strong consistency
- **Sequential Consistency**: Ordered operations
- **Eventual Consistency**: All nodes eventually consistent

## Performance Optimization

### Connection Pooling

**Reuse Connections:**
```go
cli, err := clientv3.New(clientv3.Config{
    Endpoints:   []string{"localhost:2379"},
    DialTimeout: 5 * time.Second,
    MaxCallSendMsgSize: 10 * 1024 * 1024, // 10MB
    MaxCallRecvMsgSize: 10 * 1024 * 1024, // 10MB
})
```

### Batch Operations

**Batch Put:**
```go
ops := []clientv3.Op{
    clientv3.OpPut("/key1", "value1"),
    clientv3.OpPut("/key2", "value2"),
    clientv3.OpPut("/key3", "value3"),
}

_, err := cli.Txn(context.TODO()).Then(ops...).Commit()
```

## Best Practices

### 1. Key Design

- Use hierarchical keys
- Keep keys short
- Use consistent naming
- Avoid too many keys

**Good:**
```
/config/database/url
/config/database/port
/sessions/user123
```

**Bad:**
```
key1
data
info
```

### 2. Value Size

- Keep values small (< 1.5MB)
- Use compression for large values
- Store references instead of data

### 3. Leases

- Use leases for temporary data
- Keep leases alive
- Handle lease expiration
- Use appropriate TTL

### 4. Watch

- Watch specific keys when possible
- Use revision for recovery
- Handle watch errors
- Limit watch scope

## What Interviewers Look For

### Distributed Systems Understanding

1. **etcd Concepts**
   - Understanding of key-value store
   - Raft consensus
   - Watch mechanism
   - **Red Flags**: No etcd understanding, wrong consensus, no watch

2. **Coordination Patterns**
   - Distributed locks
   - Leader election
   - Configuration management
   - **Red Flags**: No coordination, poor locks, no election

3. **Consistency**
   - Raft consensus
   - Linearizability
   - Eventual consistency
   - **Red Flags**: No consensus, wrong consistency, poor understanding

### Problem-Solving Approach

1. **Key-Value Design**
   - Key organization
   - Value size management
   - Lease usage
   - **Red Flags**: Poor keys, large values, no leases

2. **Coordination Design**
   - Lock implementation
   - Leader election
   - Configuration management
   - **Red Flags**: Poor locks, no election, no config

### System Design Skills

1. **Distributed Architecture**
   - etcd cluster design
   - Raft configuration
   - Performance optimization
   - **Red Flags**: No cluster, poor config, no optimization

2. **Scalability**
   - Cluster sizing
   - Performance tuning
   - Load distribution
   - **Red Flags**: Poor sizing, no tuning, no distribution

### Communication Skills

1. **Clear Explanation**
   - Explains etcd concepts
   - Discusses trade-offs
   - Justifies design decisions
   - **Red Flags**: Unclear explanations, no justification, confusing

### Meta-Specific Focus

1. **Distributed Systems Expertise**
   - Understanding of distributed coordination
   - etcd mastery
   - Consensus algorithms
   - **Key**: Demonstrate distributed systems expertise

2. **System Design Skills**
   - Can design coordination systems
   - Understands consensus challenges
   - Makes informed trade-offs
   - **Key**: Show practical distributed systems design skills

## Summary

**etcd Key Points:**
- **Distributed Key-Value Store**: Reliable key-value storage
- **Raft Consensus**: Strong consistency guarantees
- **Watch Mechanism**: Real-time change notifications
- **Leases**: TTL-based expiration
- **Transactions**: Atomic operations

**Common Use Cases:**
- Service discovery
- Configuration management
- Distributed locks
- Leader election
- Coordination
- Metadata storage

**Best Practices:**
- Design hierarchical keys
- Keep values small
- Use leases for temporary data
- Watch specific keys
- Optimize connection usage
- Monitor cluster health
- Handle failures gracefully

etcd is a powerful distributed key-value store that provides reliable coordination for distributed systems.

