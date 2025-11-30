---
layout: post
title: "Consul: Comprehensive Guide to Service Discovery and Configuration Management"
date: 2025-12-29
categories: [Consul, Service Discovery, Configuration Management, Distributed Systems, System Design, Technology]
excerpt: "A comprehensive guide to HashiCorp Consul, covering service discovery, health checking, key-value storage, multi-datacenter deployment, and best practices for building distributed systems."
---

## Introduction

Consul is a distributed service mesh solution that provides service discovery, health checking, and key-value storage. It enables services to discover and communicate with each other in a distributed system. Understanding Consul is essential for system design interviews involving microservices and service discovery.

This guide covers:
- **Consul Fundamentals**: Service discovery, health checking, and KV store
- **Architecture**: Agents, servers, and datacenter design
- **Service Registration**: Automatic and manual service registration
- **Health Checks**: HTTP, TCP, and script-based checks
- **Multi-Datacenter**: WAN federation and replication

## What is Consul?

Consul is a service mesh solution that:
- **Service Discovery**: Automatically discovers services
- **Health Checking**: Monitors service health
- **Key-Value Store**: Distributed configuration storage
- **Multi-Datacenter**: Supports multiple datacenters
- **Service Mesh**: Secure service-to-service communication

### Key Concepts

**Agent**: Consul process (client or server)

**Server**: Agent that participates in consensus

**Client**: Agent that forwards requests to servers

**Service**: Application or process to discover

**Health Check**: Mechanism to verify service health

**Datacenter**: Logical grouping of Consul agents

## Core Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Consul Cluster                             │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │         Consul Servers (3-5)                     │   │
│  │  (Consensus, Service Catalog, KV Store)          │   │
│  └──────────────────────────────────────────────────┘   │
│                          │                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │         Consul Clients                          │   │
│  │  (Service Registration, Health Checks)           │   │
│  └──────────────────────────────────────────────────┘   │
│                          │                               │
│        ┌─────────────────┴─────────────────┐            │
│        │                                     │            │
│  ┌─────▼──────┐                    ┌───────▼──────┐     │
│  │  Service 1 │                    │  Service 2   │     │
│  │            │                    │              │     │
│  └────────────┘                    └──────────────┘     │
└───────────────────────────────────────────────────────────┘
```

## Service Discovery

### Service Registration

**Automatic Registration (Service Definition):**
```json
{
  "service": {
    "name": "web",
    "tags": ["production", "v1"],
    "port": 8080,
    "check": {
      "http": "http://localhost:8080/health",
      "interval": "10s"
    }
  }
}
```

**Manual Registration (API):**
```bash
curl -X PUT http://localhost:8500/v1/agent/service/register \
  -d '{
    "ID": "web-1",
    "Name": "web",
    "Tags": ["production"],
    "Port": 8080,
    "Check": {
      "HTTP": "http://localhost:8080/health",
      "Interval": "10s"
    }
  }'
```

### Service Discovery

**DNS-Based Discovery:**
```bash
# Query service
dig @127.0.0.1 -p 8600 web.service.consul

# Query with tag
dig @127.0.0.1 -p 8600 web.production.service.consul
```

**HTTP API Discovery:**
```bash
# Get healthy services
curl http://localhost:8500/v1/health/service/web?passing

# Get service by ID
curl http://localhost:8500/v1/catalog/service/web
```

**Code Example (Go):**
```go
package main

import (
    "fmt"
    "github.com/hashicorp/consul/api"
)

func main() {
    client, _ := api.NewClient(api.DefaultConfig())
    
    // Get healthy services
    services, _, _ := client.Health().Service("web", "", true, nil)
    
    for _, service := range services {
        fmt.Printf("Service: %s:%d\n", 
            service.Service.Address, 
            service.Service.Port)
    }
}
```

## Health Checking

### HTTP Health Check

```json
{
  "check": {
    "id": "web-health",
    "name": "Web Health Check",
    "http": "http://localhost:8080/health",
    "interval": "10s",
    "timeout": "5s"
  }
}
```

### TCP Health Check

```json
{
  "check": {
    "id": "db-health",
    "name": "Database Health Check",
    "tcp": "localhost:5432",
    "interval": "10s",
    "timeout": "3s"
  }
}
```

### Script Health Check

```json
{
  "check": {
    "id": "script-health",
    "name": "Script Health Check",
    "script": "/usr/local/bin/check-service.sh",
    "interval": "30s"
  }
}
```

### TTL Health Check

```json
{
  "check": {
    "id": "ttl-health",
    "name": "TTL Health Check",
    "ttl": "30s"
  }
}
```

**Update TTL:**
```bash
curl -X PUT http://localhost:8500/v1/agent/check/pass/ttl-health
curl -X PUT http://localhost:8500/v1/agent/check/fail/ttl-health
curl -X PUT http://localhost:8500/v1/agent/check/warn/ttl-health
```

## Key-Value Store

### Basic Operations

**Set Value:**
```bash
curl -X PUT http://localhost:8500/v1/kv/config/database/url \
  -d 'postgresql://localhost:5432/mydb'
```

**Get Value:**
```bash
curl http://localhost:8500/v1/kv/config/database/url?raw
```

**List Keys:**
```bash
curl http://localhost:8500/v1/kv/config/?recurse
```

**Delete Key:**
```bash
curl -X DELETE http://localhost:8500/v1/kv/config/database/url
```

### Code Example

```go
package main

import (
    "fmt"
    "github.com/hashicorp/consul/api"
)

func main() {
    client, _ := api.NewClient(api.DefaultConfig())
    kv := client.KV()
    
    // Set value
    pair := &api.KVPair{
        Key:   "config/database/url",
        Value: []byte("postgresql://localhost:5432/mydb"),
    }
    _, err := kv.Put(pair, nil)
    
    // Get value
    pair, _, err := kv.Get("config/database/url", nil)
    if err == nil {
        fmt.Printf("Value: %s\n", string(pair.Value))
    }
}
```

## Multi-Datacenter

### WAN Federation

**Configuration:**
```hcl
# datacenter1
datacenter = "dc1"
primary_datacenter = "dc1"

# datacenter2
datacenter = "dc2"
primary_datacenter = "dc1"
retry_join_wan = ["consul-server-dc1:8302"]
```

**Benefits:**
- Cross-datacenter service discovery
- Centralized configuration
- Disaster recovery

### Service Replication

**Replicate Services:**
```json
{
  "service": {
    "name": "web",
    "port": 8080,
    "connect": {
      "sidecar_service": {}
    }
  }
}
```

## Service Mesh (Connect)

### Service-to-Service Security

**Enable Connect:**
```json
{
  "service": {
    "name": "web",
    "port": 8080,
    "connect": {
      "sidecar_service": {
        "proxy": {
          "upstreams": [
            {
              "destination_name": "api",
              "local_bind_port": 9090
            }
          ]
        }
      }
    }
  }
}
```

**Benefits:**
- Automatic TLS encryption
- Service identity
- Access control
- Observability

## Best Practices

### 1. Service Registration

- Use automatic registration when possible
- Register services with appropriate tags
- Set up health checks
- Use unique service IDs

### 2. Health Checks

- Use appropriate check types
- Set reasonable intervals
- Handle check failures gracefully
- Monitor check status

### 3. Key-Value Store

- Organize keys hierarchically
- Use consistent naming
- Version configuration
- Secure sensitive data

### 4. Multi-Datacenter

- Plan datacenter topology
- Configure WAN federation
- Test failover scenarios
- Monitor cross-datacenter latency

## What Interviewers Look For

### Service Discovery Understanding

1. **Consul Concepts**
   - Understanding of service discovery
   - Health checking mechanisms
   - Key-value storage
   - **Red Flags**: No Consul understanding, wrong concepts, poor health checks

2. **Microservices Architecture**
   - Service registration
   - Service discovery patterns
   - Health monitoring
   - **Red Flags**: No service discovery, poor registration, no health checks

3. **Distributed Systems**
   - Multi-datacenter support
   - Consensus and consistency
   - Service mesh
   - **Red Flags**: No multi-datacenter, poor consistency, no mesh

### Problem-Solving Approach

1. **Service Discovery Design**
   - Registration strategies
   - Health check design
   - Service catalog management
   - **Red Flags**: Poor registration, no health checks, no catalog

2. **Configuration Management**
   - Key-value organization
   - Configuration versioning
   - Dynamic configuration
   - **Red Flags**: Poor organization, no versioning, static config

### System Design Skills

1. **Microservices Architecture**
   - Service discovery design
   - Health monitoring
   - Service mesh integration
   - **Red Flags**: No discovery, poor monitoring, no mesh

2. **Scalability**
   - Multi-datacenter design
   - Service replication
   - Performance optimization
   - **Red Flags**: Single datacenter, no replication, poor performance

### Communication Skills

1. **Clear Explanation**
   - Explains Consul concepts
   - Discusses trade-offs
   - Justifies design decisions
   - **Red Flags**: Unclear explanations, no justification, confusing

### Meta-Specific Focus

1. **Microservices Expertise**
   - Understanding of service discovery
   - Consul mastery
   - Service mesh patterns
   - **Key**: Demonstrate microservices expertise

2. **System Design Skills**
   - Can design service discovery
   - Understands microservices challenges
   - Makes informed trade-offs
   - **Key**: Show practical microservices design skills

## Summary

**Consul Key Points:**
- **Service Discovery**: Automatic service registration and discovery
- **Health Checking**: HTTP, TCP, script, and TTL checks
- **Key-Value Store**: Distributed configuration storage
- **Multi-Datacenter**: WAN federation and replication
- **Service Mesh**: Secure service-to-service communication

**Common Use Cases:**
- Microservices service discovery
- Configuration management
- Health monitoring
- Service mesh
- Multi-datacenter deployments

**Best Practices:**
- Use automatic service registration
- Set up appropriate health checks
- Organize KV store hierarchically
- Plan multi-datacenter topology
- Enable service mesh for security
- Monitor service health
- Version configuration changes

Consul is a powerful tool for building distributed systems with automatic service discovery and configuration management.

