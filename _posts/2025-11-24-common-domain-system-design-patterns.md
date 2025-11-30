---
layout: post
title: "Common Domain System Design Patterns - Interview Preparation Guide"
date: 2025-11-24
categories: [System Design, Interview Preparation, Domain Design, System Architecture, Design Patterns]
excerpt: "A comprehensive guide to common domain system design patterns, covering engineering culture, technology stack, design principles, common patterns, scale considerations, and interview approaches. Essential reading for system design interviews."
---

## Introduction

Large-scale technology companies have developed unique patterns and approaches to system design over the years, driven by the need to scale to billions of users, handle petabytes of data, and maintain high availability across global infrastructure. Understanding common patterns and design philosophies is crucial for success in system design interviews.

This guide covers engineering culture, technology stack, common design patterns, scale considerations, and how these patterns manifest in domain-specific system design interviews.

## Table of Contents

1. [Meta Engineering Culture](#meta-engineering-culture)
2. [Meta Technology Stack](#meta-technology-stack)
3. [Core Design Principles](#core-design-principles)
4. [Common System Design Patterns](#common-system-design-patterns)
5. [Scale Considerations](#scale-considerations)
6. [Domain-Specific Patterns](#domain-specific-patterns)
7. [Common Interview Patterns](#common-interview-patterns)
8. [Meta-Specific Technologies](#meta-specific-technologies)
9. [Interview Approach](#interview-approach)
10. [Summary](#summary)

## Engineering Culture

### Move Fast and Build Things

Engineering culture at large-scale companies emphasizes:
- **Rapid iteration**: Ship quickly, iterate based on data
- **Data-driven decisions**: A/B testing, metrics-driven development
- **Code ownership**: Engineers own their code end-to-end
- **Impact-focused**: Focus on user impact and business value
- **Collaboration**: Cross-functional teams, code reviews

### Scale-First Thinking

Engineers at scale think about scale from day one:
- **Billions of users**: Every design must handle billions
- **Petabytes of data**: Storage and processing at massive scale
- **Global distribution**: Multi-region, low-latency requirements
- **Real-time systems**: Low-latency requirements for user-facing features

### Infrastructure as Product

Large-scale companies treat infrastructure as a product:
- **TAO**: Distributed graph database
- **RocksDB**: Embedded key-value store
- **Haystack**: Photo storage system
- **Thrift**: Cross-language RPC framework
- **HHVM**: High-performance PHP runtime

## Meta Technology Stack

### Languages

- **Hack (PHP)**: Primary language for web services
- **C++**: Performance-critical systems, infrastructure
- **Python**: Data processing, tooling, ML
- **Java**: Some backend services
- **JavaScript/TypeScript**: Frontend, React

### Databases and Storage

- **MySQL**: Primary relational database (heavily customized)
- **RocksDB**: Embedded key-value store (used in TAO)
- **TAO**: Distributed graph database (social graph)
- **Haystack**: Photo storage (object storage)
- **HDFS**: Distributed file system for analytics
- **Memcached**: Distributed caching layer

### Messaging and RPC

- **Thrift**: Cross-language RPC framework
- **Protocol Buffers**: Some services use protobuf
- **Kafka**: Event streaming (in some newer systems)
- **Scribe**: Log aggregation (older system)

### Infrastructure

- **HHVM**: High-performance PHP runtime
- **XHP**: React-like component system for PHP
- **React**: Frontend framework
- **GraphQL**: API query language (developed at Facebook)

### Monitoring and Observability

- **Scuba**: Real-time analytics and monitoring
- **Oculus**: Performance monitoring
- **FBAR**: Facebook Analytics and Reporting

## Core Design Principles

### 1. Fan-out Pattern

**Concept**: When a user creates content, push it to all followers' timelines.

**Use Cases**:
- News Feed: Push posts to followers' feeds
- Notifications: Push notifications to users
- Activity feeds: Push activities to followers

**Trade-offs**:
- **Pros**: Fast reads (pre-computed), good for users with few followers
- **Cons**: Slow writes, expensive for users with many followers

**Example**:
```
User posts → Fan-out service → Push to all followers' timeline caches
```

### 2. Pull Pattern

**Concept**: When a user requests content, pull it from sources on-demand.

**Use Cases**:
- News Feed for celebrities (millions of followers)
- Search results
- On-demand content aggregation

**Trade-offs**:
- **Pros**: Fast writes, efficient for users with many followers
- **Cons**: Slower reads, requires real-time computation

**Example**:
```
User requests feed → Pull service → Query recent posts from followed users → Merge and rank
```

### 3. Hybrid Push-Pull Pattern

**Concept**: Combine push and pull based on user characteristics.

**Meta's Approach**:
- **Push** for users with < 1M followers (most users)
- **Pull** for users with > 1M followers (celebrities)
- **Push** for active users (frequent feed views)
- **Pull** for inactive users (rare feed views)

**Benefits**:
- Optimize for common case (push)
- Handle edge cases efficiently (pull)
- Balance read/write performance

### 4. Timeline Caching

**Concept**: Pre-compute and cache user timelines.

**Implementation**:
- Store timeline in cache (Redis/Memcached)
- Update cache on new posts (fan-out)
- Serve from cache for reads
- Fallback to pull on cache miss

**Benefits**:
- Fast reads (< 100ms)
- Reduced database load
- Better user experience

### 5. Social Graph Storage

**Concept**: Efficiently store and query social relationships.

**Meta's Solution**: TAO (The Associations and Objects)
- Distributed graph database
- Optimized for social graph queries
- Handles billions of relationships
- Low-latency queries

**Use Cases**:
- Friend relationships
- Follow relationships
- Group memberships
- Privacy checks

### 6. Counter Aggregation

**Concept**: Aggregate counters (likes, shares, comments) efficiently.

**Meta's Approach**:
- Use distributed counters (Memcached)
- Batch updates to database
- Accept eventual consistency
- Handle counter overflow

**Benefits**:
- Fast updates
- Reduced database writes
- Scalable to billions of interactions

### 7. Media Storage and CDN

**Concept**: Efficiently store and serve media at scale.

**Meta's Solution**: Haystack
- Object storage for photos
- CDN for global distribution
- Multiple storage tiers (hot, warm, cold)
- Deduplication and compression

**Benefits**:
- Low storage costs
- Fast global access
- Efficient storage utilization

### 8. Privacy and Access Control

**Concept**: Efficiently enforce privacy settings at scale.

**Meta's Approach**:
- Pre-compute privacy checks
- Cache privacy decisions
- Batch privacy checks
- Use social graph for efficient queries

**Challenges**:
- Complex privacy rules
- Performance at scale
- Consistency across systems

## Common System Design Patterns

### 1. Three-Tier Architecture

**Pattern**: Client → Application Server → Database

**Meta's Implementation**:
```
Web/Mobile → PHP/Hack Services → MySQL/TAO
         ↓
    Memcached (Cache Layer)
```

**Benefits**:
- Clear separation of concerns
- Scalable horizontally
- Caching layer reduces database load

### 2. Read Replicas

**Pattern**: Master database for writes, replicas for reads

**Meta's Implementation**:
- MySQL master-slave replication
- Read from replicas, write to master
- Multiple replicas per region
- Automatic failover

**Benefits**:
- Scale reads independently
- Reduce master load
- Geographic distribution

### 3. Sharding

**Pattern**: Partition data across multiple databases

**Meta's Approach**:
- Shard by user_id (hash-based)
- Each shard independent
- Cross-shard queries minimized
- Rebalancing as needed

**Benefits**:
- Horizontal scalability
- Independent scaling
- Fault isolation

### 4. Caching Layers

**Pattern**: Multiple levels of caching

**Meta's Implementation**:
- **L1**: Application-level cache (in-process)
- **L2**: Memcached (distributed cache)
- **L3**: CDN (edge cache)
- **L4**: Database query cache

**Benefits**:
- Reduced latency
- Reduced database load
- Better user experience

### 5. Event-Driven Architecture

**Pattern**: Services communicate via events

**Meta's Implementation**:
- Thrift RPC for synchronous calls
- Scribe/Kafka for asynchronous events
- Event sourcing for some systems
- Pub/sub for notifications

**Benefits**:
- Loose coupling
- Scalability
- Resilience

### 6. Microservices

**Pattern**: Decompose system into independent services

**Meta's Approach**:
- Service-oriented architecture
- Thrift for service communication
- Independent deployment
- Service discovery

**Benefits**:
- Independent scaling
- Technology diversity
- Team autonomy

## Scale Considerations

### User Scale

**Numbers**:
- **Users**: 3+ billion monthly active users
- **Daily Active Users**: 2+ billion
- **Peak Concurrent**: 100+ million

**Implications**:
- Every design must handle billions
- Geographic distribution critical
- Multi-region architecture required
- Low-latency requirements

### Data Scale

**Numbers**:
- **Posts**: Billions per day
- **Photos**: Billions stored
- **Social Graph**: Trillions of relationships
- **Storage**: Petabytes of data

**Implications**:
- Efficient storage critical
- Compression and deduplication
- Tiered storage (hot/warm/cold)
- Data lifecycle management

### Traffic Scale

**Numbers**:
- **Requests**: Millions of QPS
- **Peak Traffic**: 10x average
- **Global Distribution**: Multi-region

**Implications**:
- Horizontal scaling required
- Load balancing critical
- Caching essential
- Rate limiting necessary

### Latency Requirements

**Targets**:
- **Feed Load**: < 200ms (p95)
- **Post Creation**: < 500ms
- **Search**: < 500ms
- **Real-time Updates**: < 1s

**Implications**:
- Caching critical
- CDN for static content
- Database optimization
- Minimize network hops

## Domain-Specific Patterns

### News Feed Pattern

**Components**:
1. **Content Creation**: User posts content
2. **Fan-out Service**: Push to followers' timelines
3. **Timeline Cache**: Pre-computed timelines
4. **Ranking Service**: Rank posts by relevance
5. **Real-time Updates**: Push new posts to active users

**Key Design Decisions**:
- Hybrid push-pull for feed generation
- Timeline caching for fast reads
- Ranking algorithm (relevance, recency, engagement)
- Real-time updates via WebSocket/SSE

### Social Graph Pattern

**Components**:
1. **TAO**: Distributed graph database
2. **Graph Cache**: Cached graph queries
3. **Privacy Service**: Privacy checks
4. **Graph Algorithms**: Friend suggestions, mutual friends

**Key Design Decisions**:
- TAO for graph storage
- Caching for frequent queries
- Batch privacy checks
- Efficient graph traversal algorithms

### Media Storage Pattern

**Components**:
1. **Haystack**: Object storage
2. **CDN**: Global distribution
3. **Upload Service**: Handle uploads
4. **Processing Service**: Resize, optimize media

**Key Design Decisions**:
- Haystack for efficient storage
- CDN for global access
- Multiple storage tiers
- Deduplication and compression

### Search Pattern

**Components**:
1. **Indexer**: Index content
2. **Search Service**: Handle search queries
3. **Ranking Service**: Rank results
4. **Real-time Updates**: Update index on new content

**Key Design Decisions**:
- Distributed search index
- Real-time indexing
- Ranking algorithm
- Query optimization

### Messaging Pattern

**Components**:
1. **Message Service**: Handle messages
2. **Presence Service**: Track online/offline
3. **Delivery Service**: Ensure delivery
4. **Encryption**: End-to-end encryption

**Key Design Decisions**:
- Real-time delivery
- Message persistence
- Ordering guarantees
- Encryption at rest and in transit

## Common Interview Patterns

### Pattern 1: Feed Generation

**Question**: Design Facebook News Feed

**Key Points**:
- Fan-out vs pull trade-offs
- Timeline caching strategy
- Ranking algorithm
- Real-time updates
- Scale to billions

**Meta's Approach**:
- Hybrid push-pull
- Timeline cache (Memcached)
- Ranking by relevance
- WebSocket for real-time

### Pattern 2: Social Graph

**Question**: Design friend suggestions / mutual friends

**Key Points**:
- Graph storage (TAO)
- Graph algorithms (BFS, DFS)
- Privacy considerations
- Performance at scale

**Meta's Approach**:
- TAO for graph storage
- Cached graph queries
- Batch processing
- Efficient algorithms

### Pattern 3: Media Storage

**Question**: Design photo storage system

**Key Points**:
- Storage efficiency (Haystack)
- CDN distribution
- Upload handling
- Processing pipeline

**Meta's Approach**:
- Haystack for storage
- CDN for distribution
- Multiple tiers
- Deduplication

### Pattern 4: Real-time Systems

**Question**: Design live commenting / real-time updates

**Key Points**:
- WebSocket/SSE
- Pub/sub architecture
- Scale to millions
- Low latency

**Meta's Approach**:
- WebSocket connections
- Pub/sub for distribution
- Connection pooling
- Efficient message routing

### Pattern 5: Search

**Question**: Design search for posts / users

**Key Points**:
- Distributed indexing
- Real-time updates
- Ranking algorithm
- Query optimization

**Meta's Approach**:
- Distributed search index
- Real-time indexing
- Relevance ranking
- Query caching

## Meta-Specific Technologies

### TAO (The Associations and Objects)

**Purpose**: Distributed graph database for social graph

**Key Features**:
- Optimized for social graph queries
- Handles billions of relationships
- Low-latency queries (< 10ms)
- Eventually consistent

**Use Cases**:
- Friend relationships
- Follow relationships
- Group memberships
- Privacy checks

**Design Considerations**:
- Graph traversal optimization
- Caching strategies
- Consistency models
- Sharding strategies

### RocksDB

**Purpose**: Embedded key-value store

**Key Features**:
- High performance
- Used in TAO
- LSM-tree structure
- Configurable consistency

**Use Cases**:
- TAO storage engine
- Caching layer
- Log storage

**Design Considerations**:
- Write amplification
- Read amplification
- Compaction strategies
- Memory management

### Haystack

**Purpose**: Photo storage system

**Key Features**:
- Efficient storage (deduplication)
- Multiple storage tiers
- CDN integration
- High availability

**Use Cases**:
- Photo storage
- Video storage (in some cases)
- Media distribution

**Design Considerations**:
- Storage efficiency
- Access patterns
- CDN integration
- Lifecycle management

### Thrift

**Purpose**: Cross-language RPC framework

**Key Features**:
- Language-agnostic
- Efficient serialization
- Service definition (IDL)
- Code generation

**Use Cases**:
- Service-to-service communication
- API definition
- Cross-language integration

**Design Considerations**:
- Service contracts
- Versioning
- Performance
- Error handling

### HHVM

**Purpose**: High-performance PHP runtime

**Key Features**:
- JIT compilation
- Better performance than PHP
- Backward compatible
- Production-ready

**Use Cases**:
- Web services
- API servers
- High-traffic applications

**Design Considerations**:
- Performance optimization
- Memory management
- Deployment strategies

## Interview Approach

### Understanding the Problem

1. **Clarify Requirements**:
   - Functional requirements
   - Non-functional requirements
   - Scale requirements
   - Constraints

2. **Ask Meta-Specific Questions**:
   - Is this for Facebook, Instagram, WhatsApp, or Messenger?
   - What's the expected scale?
   - Are there existing Meta systems to consider?
   - What are the latency requirements?

### Designing the Solution

1. **Start with High-Level Architecture**:
   - Identify main components
   - Show data flow
   - Highlight key services

2. **Apply Meta Patterns**:
   - Fan-out for feed generation
   - TAO for social graph
   - Haystack for media storage
   - Memcached for caching

3. **Consider Scale**:
   - Billions of users
   - Petabytes of data
   - Millions of QPS
   - Global distribution

4. **Discuss Trade-offs**:
   - Push vs pull
   - Consistency vs availability
   - Latency vs freshness
   - Cost vs performance

### Communicating Your Design

1. **Explain Meta Context**:
   - Reference Meta's scale
   - Mention Meta technologies where relevant
   - Show understanding of Meta's challenges

2. **Justify Decisions**:
   - Explain why you chose specific patterns
   - Discuss trade-offs
   - Show consideration of alternatives

3. **Handle Questions**:
   - Be ready to dive deep
   - Discuss edge cases
   - Consider failure scenarios
   - Optimize based on feedback

### Common Pitfalls to Avoid

1. **Underestimating Scale**:
   - Don't design for thousands when Meta needs billions
   - Consider global distribution
   - Think about peak traffic

2. **Ignoring Meta Patterns**:
   - Use Meta's proven patterns
   - Reference Meta technologies
   - Show awareness of Meta's approach

3. **Over-Engineering**:
   - Start simple, add complexity as needed
   - Don't over-optimize prematurely
   - Focus on the problem at hand

4. **Not Discussing Trade-offs**:
   - Always discuss alternatives
   - Explain why you chose your approach
   - Show understanding of trade-offs

## What Interviewers Look For

### Meta-Specific Knowledge

1. **Meta Patterns Understanding**
   - Fan-out pattern
   - Timeline caching
   - Social graph (TAO)
   - **Red Flags**: Generic patterns only, no Meta-specific knowledge, can't reference Meta tech

2. **Meta Technologies**
   - TAO (social graph)
   - Haystack (photo storage)
   - RocksDB
   - Thrift
   - **Red Flags**: No Meta tech knowledge, generic solutions only, can't explain Meta choices

3. **Meta Scale Understanding**
   - Billions of users
   - Petabytes of data
   - Millions of requests/second
   - **Red Flags**: Small-scale thinking, no scale awareness, unrealistic assumptions

### System Design Skills

1. **Pattern Application**
   - Can apply Meta patterns
   - Understands when to use each
   - **Red Flags**: Wrong patterns, no pattern knowledge, generic solutions

2. **Scale Thinking**
   - Designs for Meta scale
   - Appropriate optimizations
   - **Red Flags**: Small-scale design, no optimization, bottlenecks

3. **Trade-off Analysis**
   - Understands Meta trade-offs
   - Justifies decisions
   - **Red Flags**: No trade-offs, no justification, dogmatic choices

### Problem-Solving Approach

1. **Meta Context**
   - Understands Meta's challenges
   - Applies Meta solutions
   - **Red Flags**: Generic solutions, no Meta context, ignoring Meta scale

2. **Pattern Recognition**
   - Recognizes when to use patterns
   - Applies appropriately
   - **Red Flags**: Wrong pattern, no recognition, over-engineering

3. **Reference Meta Work**
   - Can reference Meta papers
   - Understands Meta architecture
   - **Red Flags**: No Meta knowledge, generic references, can't explain Meta choices

### Communication Skills

1. **Meta Terminology**
   - Uses Meta terminology correctly
   - References Meta technologies
   - **Red Flags**: Wrong terminology, no Meta references, generic language

2. **Pattern Explanation**
   - Can explain Meta patterns
   - Understands trade-offs
   - **Red Flags**: No understanding, vague explanations, can't explain

### Meta-Specific Focus

1. **Meta-Specific Expertise**
   - Deep Meta knowledge
   - Pattern understanding
   - **Key**: Show Meta-specific expertise

2. **Scale Expertise**
   - Meta-scale thinking
   - Appropriate solutions
   - **Key**: Demonstrate Meta-scale expertise

## Summary

### Key Takeaways

1. **Meta's Scale**:
   - Billions of users
   - Petabytes of data
   - Millions of QPS
   - Global distribution

2. **Common Patterns**:
   - Fan-out for feed generation
   - Hybrid push-pull
   - Timeline caching
   - Social graph storage (TAO)
   - Counter aggregation
   - Media storage (Haystack)

3. **Technology Stack**:
   - Hack/PHP for services
   - MySQL for relational data
   - TAO for social graph
   - RocksDB for key-value
   - Haystack for media
   - Memcached for caching
   - Thrift for RPC

4. **Design Principles**:
   - Scale-first thinking
   - Data-driven decisions
   - Infrastructure as product
   - Move fast and build things

5. **Interview Approach**:
   - Understand Meta's scale
   - Apply Meta patterns
   - Discuss trade-offs
   - Reference Meta technologies

### Common Interview Questions

1. **Design Facebook News Feed**
   - Fan-out pattern
   - Timeline caching
   - Ranking algorithm
   - Real-time updates

2. **Design Friend Suggestions**
   - Social graph (TAO)
   - Graph algorithms
   - Privacy considerations
   - Performance optimization

3. **Design Photo Storage**
   - Haystack storage
   - CDN distribution
   - Upload handling
   - Processing pipeline

4. **Design Live Commenting**
   - Real-time updates
   - WebSocket/SSE
   - Pub/sub architecture
   - Scale considerations

5. **Design Search**
   - Distributed indexing
   - Real-time updates
   - Ranking algorithm
   - Query optimization

### Resources for Further Learning

- **Meta Engineering Blog**: Engineering.fb.com
- **TAO Paper**: "TAO: Facebook's Distributed Data Store for the Social Graph"
- **Haystack Paper**: "Finding a Needle in Haystack: Facebook's Photo Storage"
- **RocksDB Documentation**: Rocksdb.org
- **Thrift Documentation**: Thrift.apache.org

Understanding Meta's common patterns and design approaches will significantly improve your performance in Meta system design interviews. Focus on scale, apply proven patterns, and demonstrate understanding of Meta's unique challenges and solutions.

