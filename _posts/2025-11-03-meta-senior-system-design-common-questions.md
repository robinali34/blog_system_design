---
layout: post
title: "Meta Senior Software Engineer - Common System Design Interview Questions"
date: 2025-11-04
categories: [Interview Questions, Meta, System Design, Senior Engineer, Quick Reference]
excerpt: "A comprehensive list of common Meta Senior Software Engineer system design interview questions, organized by category and frequency for quick reference and practice."
---

## Introduction

This post provides a comprehensive list of common system design interview questions for Meta's Senior Software Engineer positions. These questions are based on extensive research, interview experiences, and Meta's actual products and systems.

**Note**: For detailed preparation strategies, see the [Meta System Design Interview Guide](/blog_system_design/2025/11/03/meta-system-design-interview/).

## Meta System Design Interview Overview

### Interview Format

- **Duration**: 45 minutes
- **Format**: Known as the "Pirate Interview" round
- **Focus**: Design skills demonstration - open-ended questions
- **Process**: Discussion and whiteboarding/virtual board
- **Evaluation**: Problem-solving approach, technical depth, communication

### Evaluation Criteria

Meta evaluates candidates on four key areas:

1. **Problem Navigation**: Organize problem space, identify constraints, ask clarifying questions
2. **Solution Design**: Design working solutions, consider the big picture
3. **Technical Excellence**: Dive into technical details, identify dependencies and trade-offs
4. **Technical Communication**: Articulate vision clearly, address feedback

## Common Meta System Design Questions

### Meta-Specific Product Questions (Highest Priority)

These questions are directly related to Meta's products and are asked most frequently.

#### 1. Design Facebook News Feed

**Key Features:**
- Users see news feed containing posts from friends and followed pages
- Users can post and like statuses (text, images, videos)
- Users can send friend requests and follow pages
- Real-time feed updates

**Challenges:**
- Real-time feed generation
- Ranking algorithms for feed relevance
- Handling billions of users and posts
- Efficient data retrieval and caching
- Personalization and relevance

**Key Components:**
- Feed generation service
- Ranking service
- Content delivery network (CDN)
- Caching layer
- Graph database for social connections

#### 2. Design Facebook Status Search

**Key Features:**
- Search posts, statuses, videos from friends and followed pages
- Text-based search (extendable to multimedia)
- Real-time search updates

**Challenges:**
- Indexing massive amounts of content
- Real-time search updates
- Ranking and relevance algorithms
- Scalability for millions of queries per second
- Privacy and access control

**Key Components:**
- Search index (Elasticsearch, custom)
- Indexing pipeline
- Query processing
- Ranking service
- Access control layer

#### 3. Design Facebook Messenger / WhatsApp

**Key Features:**
- 1:1 conversations between users
- Track online/offline status
- Group conversations
- Push notifications
- Message delivery confirmation

**Challenges:**
- Real-time message delivery
- Message persistence and ordering
- Presence/status management
- Handling millions of concurrent connections
- End-to-end encryption
- Message synchronization across devices

**Key Components:**
- Message delivery service
- Presence service
- Notification service
- Message storage
- WebSocket/connection management

#### 4. Design Instagram

**Key Features:**
- Upload and share photos/videos
- Follow other users
- Like photos
- Scrollable feed of photos from followed users
- Stories feature

**Challenges:**
- Media storage and CDN distribution
- Feed generation and ranking
- Image processing and optimization
- Real-time updates for likes and comments
- High-volume media uploads

**Key Components:**
- Media upload service
- Image processing pipeline
- CDN for media delivery
- Feed generation service
- Activity tracking

#### 5. Design Live Commenting

**Key Features:**
- Real-time comment feed for posts
- Users see new comments as they appear
- Handle concurrent comments from multiple users
- Comment threading

**Challenges:**
- Real-time data synchronization
- WebSocket or polling mechanisms
- Handling high concurrency
- Maintaining comment order and consistency
- Scalability for viral posts

**Key Components:**
- Real-time notification service
- Comment storage
- WebSocket connection management
- Message queue for comment processing

---

### General System Design Questions (High Priority)

These are common system design patterns that appear frequently in Meta interviews.

#### 6. Design a Distributed Cache System

**Key Features:**
- High-performance caching
- Distributed across multiple nodes
- Cache eviction strategies
- Consistency models

**Challenges:**
- Cache coherence
- Distributed caching
- Eviction policies
- Cache invalidation
- Network partitioning

#### 7. Design a URL Shortener (TinyURL)

**Key Features:**
- Shorten long URLs
- Redirect to original URLs
- Analytics and tracking
- Custom short URLs

**Challenges:**
- Generating unique short codes
- High read/write ratio
- Scalability
- Redirect performance
- Analytics at scale

#### 8. Design a Distributed Lock Service

**Key Features:**
- Distributed locking mechanism
- Lease-based locking
- Automatic lock expiration
- High availability

**Challenges:**
- Consensus algorithms
- Lock expiration and renewal
- Deadlock prevention
- Network partitions
- Performance at scale

#### 9. Design a Rate Limiter

**Key Features:**
- Limit requests per user/IP
- Multiple rate limiting strategies
- Distributed rate limiting
- High-throughput support

**Challenges:**
- Sliding window algorithms
- Distributed coordination
- Token bucket implementation
- Performance optimization
- Accurate rate limiting

#### 10. Design a Distributed Counter

**Key Features:**
- Count events across distributed systems
- Real-time counting
- High write throughput
- Eventual consistency

**Challenges:**
- Distributed counting
- Consistency vs. performance
- Handling high write rates
- Aggregation strategies
- Sharding and partitioning

---

### Real-Time and Event-Driven Systems (High Priority)

#### 11. Design a Real-Time Analytics System

**Key Features:**
- Real-time event processing
- Aggregations and metrics
- Dashboard updates
- High-throughput event ingestion

**Challenges:**
- Stream processing
- Low-latency aggregations
- Handling high event rates
- Data retention
- Query performance

#### 12. Design a Notification System

**Key Features:**
- Multi-channel notifications (push, email, SMS)
- Notification preferences
- Delivery tracking
- High-throughput delivery

**Challenges:**
- Multi-channel delivery
- Notification batching
- Delivery reliability
- User preferences
- Rate limiting per channel

#### 13. Design a Real-Time Collaboration System

**Key Features:**
- Real-time document editing
- Conflict resolution
- Presence awareness
- Change synchronization

**Challenges:**
- Operational transforms
- Conflict resolution
- Real-time synchronization
- Consistency models
- Scalability

---

### Data-Intensive Systems (Medium Priority)

#### 14. Design Proximity Server

**Key Features:**
- Add, update, and delete places
- Query nearby places within distance
- Query events near a place at specific time
- Geospatial queries

**Challenges:**
- Geospatial indexing (GeoHash, R-trees)
- Efficient proximity queries
- Handling time-based queries
- Scalability for location services
- Real-time updates

**Key Components:**
- Geospatial database
- Location indexing service
- Query processing
- Caching layer

#### 15. Design Typeahead Suggestions (Autocomplete)

**Key Features:**
- Suggest top 10 search queries based on typed characters
- Popularity determined by search frequency
- Real-time suggestions
- Low-latency responses

**Challenges:**
- Real-time suggestions
- Efficient prefix matching (Trie)
- Ranking and relevance
- Handling millions of queries
- Response time optimization

**Key Components:**
- Trie data structure
- Ranking service
- Caching layer
- Query processing

#### 16. Design Top N Songs / Trending Topics

**Key Features:**
- Get top N songs based on listen frequency
- Time-based windowing (past X days)
- Ranking by popularity
- Real-time updates

**Challenges:**
- Real-time aggregation
- Efficient top-K algorithms
- Sliding window calculations
- Handling high-volume data streams
- Ranking accuracy

#### 17. Design a Web Crawler

**Key Features:**
- Download web pages from seed URLs
- Index pages for future retrieval
- Handle duplicate URLs
- Crawl all connected pages

**Challenges:**
- URL deduplication
- Respecting robots.txt
- Rate limiting
- Distributed crawling
- Handling different content types
- Politeness and fairness

#### 18. Design a Distributed File System

**Key Features:**
- File storage and retrieval
- Replication and fault tolerance
- High availability
- Scalability

**Challenges:**
- Distributed storage
- Consistency models
- Replication strategies
- Fault tolerance
- Performance optimization

---

### Specialized Systems (Medium Priority)

#### 19. Design Privacy Settings

**Key Features:**
- Specify privacy levels for posts (Public, Friends, etc.)
- Control post visibility to specific user sets
- Friends of friends, custom groups
- Efficient privacy checks

**Challenges:**
- Efficient privacy checks
- Access control enforcement
- Querying posts with privacy constraints
- Scalability for billions of posts
- Complex privacy rules

#### 20. Design a Distributed Task Scheduler

**Key Features:**
- Schedule and execute tasks
- Task priorities and dependencies
- Fault tolerance
- Scalability

**Challenges:**
- Task scheduling algorithms
- Dependency management
- Fault tolerance
- Resource allocation
- Load balancing

#### 21. Design a Distributed Logging System

**Key Features:**
- Collect logs from distributed services
- Log aggregation and storage
- Log search and querying
- Real-time log streaming

**Challenges:**
- High-volume log ingestion
- Log storage and retention
- Search performance
- Real-time streaming
- Cost optimization

#### 22. Design a Distributed Configuration System

**Key Features:**
- System-wide configuration
- Dynamic configuration updates
- Configuration versioning
- Rollback mechanisms

**Challenges:**
- Configuration distribution
- Consistency across services
- Version management
- Rollback strategies
- Performance impact

---

### Infrastructure and Scalability Questions (Lower Priority)

#### 23. Design a Load Balancer

**Key Features:**
- Distribute requests across servers
- Health checking
- Multiple routing algorithms
- High availability

**Challenges:**
- Load balancing algorithms
- Health checking
- Session affinity
- High availability
- Performance optimization

#### 24. Design a Distributed Database

**Key Features:**
- Distributed data storage
- Replication and consistency
- Query processing
- Transaction support

**Challenges:**
- CAP theorem trade-offs
- Replication strategies
- Consistency models
- Partitioning and sharding
- Query routing

#### 25. Design a Content Delivery Network (CDN)

**Key Features:**
- Global content distribution
- Edge caching
- Origin server management
- Cache invalidation

**Challenges:**
- Edge server placement
- Cache strategies
- Invalidation mechanisms
- Latency optimization
- Cost optimization

---

## Question Categories by Frequency

### Tier 1: Most Common Questions (Must Practice)

These questions appear in 70%+ of Meta interviews:

1. **Design Facebook News Feed** (#1)
2. **Design Facebook Messenger / WhatsApp** (#3)
3. **Design Instagram** (#4)
4. **Design Facebook Status Search** (#2)
5. **Design Live Commenting** (#5)

### Tier 2: Very Common Questions (High Priority)

These questions appear in 40-70% of interviews:

6. **Design a Distributed Cache System** (#6)
7. **Design a URL Shortener** (#7)
8. **Design a Rate Limiter** (#9)
9. **Design a Real-Time Analytics System** (#11)
10. **Design Proximity Server** (#14)
11. **Design Typeahead Suggestions** (#15)

### Tier 3: Common Questions (Medium Priority)

These questions appear in 20-40% of interviews:

12. **Design a Distributed Lock Service** (#8)
13. **Design a Notification System** (#12)
14. **Design Top N Songs / Trending Topics** (#16)
15. **Design a Web Crawler** (#17)
16. **Design Privacy Settings** (#19)
17. **Design a Distributed Task Scheduler** (#20)

### Tier 4: Less Common Questions (Lower Priority)

These questions appear in 10-20% of interviews:

18. **Design a Distributed Counter** (#10)
19. **Design a Real-Time Collaboration System** (#13)
20. **Design a Distributed File System** (#18)
21. **Design a Distributed Logging System** (#21)
22. **Design a Distributed Configuration System** (#22)
23. **Design a Load Balancer** (#23)
24. **Design a Distributed Database** (#24)
25. **Design a Content Delivery Network** (#25)

---

## Meta-Specific Question Patterns

### Pattern 1: Social Graph Problems

- News Feed
- Friend Suggestions
- Social Search
- Privacy Settings

**Key Concepts:**
- Graph databases
- Social graph algorithms
- Privacy and access control
- Feed ranking

### Pattern 2: Real-Time Systems

- Live Commenting
- Messenger/Chat
- Real-Time Analytics
- Notification Systems

**Key Concepts:**
- WebSockets
- Pub/Sub systems
- Message queues
- Event streaming

### Pattern 3: Content Systems

- Instagram
- Media Storage
- CDN Design
- Content Delivery

**Key Concepts:**
- Media processing
- CDN architecture
- Storage systems
- Image/video optimization

### Pattern 4: Search and Discovery

- Status Search
- Typeahead/Autocomplete
- Proximity Server
- Trending Topics

**Key Concepts:**
- Search indexing
- Trie data structures
- Geospatial indexing
- Ranking algorithms

---

## How to Use This List

### Preparation Strategy

1. **Start with Tier 1 Questions**
   - Master the most common Meta-specific questions
   - Understand Meta's products deeply
   - Practice with detailed solutions

2. **Practice Tier 2 Questions**
   - Cover common system design patterns
   - Understand distributed systems concepts
   - Practice problem exploration

3. **Review Tier 3 & 4 Questions**
   - Familiarize with concepts
   - Understand basic approaches
   - Know when to apply them

### Practice Approach

For each question, practice:

1. **Problem Navigation**
   - Ask clarifying questions
   - Gather requirements
   - Understand constraints and scale

2. **Solution Design**
   - High-level architecture
   - Component design
   - Data flow and interactions

3. **Technical Excellence**
   - Detailed component design
   - Technology choices
   - Scalability considerations
   - Trade-offs analysis

4. **Technical Communication**
   - Clear explanations
   - Diagrams and visualizations
   - Address feedback
   - Discuss alternatives

### Interview Tips

1. **Ask Questions First**
   - Clarify requirements
   - Understand scale
   - Identify constraints
   - Understand use cases

2. **Think at Scale**
   - Meta operates at massive scale
   - Think billions of users
   - Consider global distribution
   - Plan for high throughput

3. **Discuss Trade-offs**
   - Performance vs. consistency
   - Latency vs. throughput
   - Cost vs. reliability
   - Simplicity vs. flexibility

4. **Show Depth**
   - Dive into technical details
   - Discuss implementation challenges
   - Consider edge cases
   - Address failure scenarios

5. **Communicate Clearly**
   - Explain your thought process
   - Use diagrams effectively
   - Listen to feedback
   - Adjust approach when needed

---

## Key Concepts to Master

### Distributed Systems

- **Consistency Models**: Strong, eventual, causal
- **CAP Theorem**: Consistency, Availability, Partition tolerance
- **Replication**: Master-slave, multi-master, quorum
- **Sharding**: Horizontal partitioning strategies
- **Load Balancing**: Algorithms and strategies

### Scalability Patterns

- **Caching**: Multi-level caching, cache strategies
- **CDN**: Content delivery, edge caching
- **Database Scaling**: Read replicas, sharding, partitioning
- **Message Queues**: Async processing, event streaming
- **Microservices**: Service decomposition, communication

### Real-Time Systems

- **WebSockets**: Persistent connections, real-time updates
- **Pub/Sub**: Event-driven architectures
- **Stream Processing**: Real-time data processing
- **WebRTC**: Peer-to-peer communication

### Data Systems

- **Storage**: SQL, NoSQL, object storage
- **Indexing**: Search indexes, geospatial indexes
- **Aggregation**: Real-time aggregations, batch processing
- **Analytics**: OLAP, OLTP, data warehousing

---

## Meta-Specific Considerations

### Scale Expectations

- **Users**: Billions of users
- **Requests**: Millions of QPS
- **Data**: Petabytes of data
- **Global**: Worldwide distribution
- **Real-time**: Low-latency requirements

### Technology Stack Awareness

Meta commonly uses:
- **Languages**: Python, C++, Java, Hack (PHP)
- **Databases**: MySQL, RocksDB, TAO
- **Messaging**: Thrift, Protocol Buffers
- **Caching**: Memcached, Redis
- **Storage**: Haystack (photo storage), HDFS

### Product Awareness

- Understand Facebook, Instagram, WhatsApp, Messenger
- Know Meta's infrastructure (TAO, RocksDB, etc.)
- Understand Meta's engineering culture
- Be aware of Meta's open-source projects

---

## Related Resources

- **[Meta System Design Interview Guide](/blog_system_design/2025/11/03/meta-system-design-interview/)**: Comprehensive interview guide
- **[Meta SpecSWE System Design Guide](/blog_system_design/2025/11/03/meta-specswe-system-design/)**: Specialized roles guide
- **[Meta In-Domain Design Guide](/blog_system_design/2025/11/03/meta-in-domain-design-interview/)**: Domain-specific design

---

## Conclusion

This list provides a comprehensive overview of common Meta Senior Software Engineer system design interview questions. Remember:

- **Focus on Meta-specific questions first** (News Feed, Messenger, Instagram)
- **Master distributed systems fundamentals** (scalability, consistency, reliability)
- **Practice problem-solving approach**, not memorizing solutions
- **Think at Meta scale** (billions of users, global distribution)
- **Show your thought process**, communicate clearly
- **Discuss trade-offs**, make informed decisions

**Key Success Factors:**
1. Deep understanding of Meta's products
2. Strong distributed systems knowledge
3. Clear problem-solving approach
4. Excellent communication skills
5. Ability to think at massive scale

Good luck with your Meta Senior Software Engineer interview preparation!

