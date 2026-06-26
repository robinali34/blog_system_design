---
layout: page
title: "Learning Path"
permalink: /system-design-list.html
date: 2026-05-26
categories: [System Design, Learning Path, Reference]
---

# System Design Interview — Learning Path & Blog Index

<div class="lp-hero">
  <p class="lp-hero-lead">Your guided map through <strong>{{ site.posts.size }} posts</strong> — start at Level 0, follow the graphs, or jump to any section from the sidebar.</p>
  <div class="lp-stat-grid">
    <div class="lp-stat"><span class="lp-stat-num">58</span><span class="lp-stat-label">Design problems</span></div>
    <div class="lp-stat"><span class="lp-stat-num">50</span><span class="lp-stat-label">Tech guides</span></div>
    <div class="lp-stat"><span class="lp-stat-num">22</span><span class="lp-stat-label">Foundations</span></div>
    <div class="lp-stat"><span class="lp-stat-num">31</span><span class="lp-stat-label">OS / embedded</span></div>
    <div class="lp-stat"><span class="lp-stat-num">6</span><span class="lp-stat-label">Study levels</span></div>
  </div>
  <nav class="lp-jump-nav" aria-label="Jump to study level">
    <a href="#level-0-orientation-references" class="lp-pill lp-pill-0">Level 0 · Prep</a>
    <a href="#level-1-fundamentals-beginner" class="lp-pill lp-pill-1">Level 1 · Basics</a>
    <a href="#level-2-intermediate-distributed-systems" class="lp-pill lp-pill-2">Level 2 · Distributed</a>
    <a href="#level-3-advanced-large-scale-systems" class="lp-pill lp-pill-3">Level 3 · Advanced</a>
    <a href="#level-4-technology-depth-reference-library" class="lp-pill lp-pill-4">Level 4 · Tech</a>
    <a href="#level-5-specialized-tracks-optional" class="lp-pill lp-pill-5">Level 5 · Specialized</a>
  </nav>
</div>

<div class="lp-quick-links">
  <strong>Quick links:</strong>
  <a href="#1-system-design-study-path">Study path</a>
  <a href="{{ site.baseurl }}/2025/11/29/system-design-learning-path-index/">Path index</a>
  <a href="{{ site.baseurl }}/2025/11/29/technology-list-quick-reference/">Tech reference</a>
  <a href="{{ site.baseurl }}/2025/11/03/system-design-references/">References</a>
  <a href="{{ site.baseurl }}/posts/">All posts</a>
</div>

---

## Blog at a glance

This blog is a **structured library** for system design interview prep and related engineering depth—not a chronological diary. Content spans **distributed systems** (feeds, chat, storage, streaming), **50+ technology guides** (Redis, Kafka, databases, K8s, …), **local/embedded/OS** interviews, and **hardware test & DFT** (ATE, scan, BIST).

### Content mix (visual)

<div class="lp-bar-chart" aria-label="Approximate post counts by category">
  <div class="lp-bar-row"><span class="lp-bar-label">Design problems</span><div class="lp-bar-track"><div class="lp-bar-fill" style="width:34%"></div></div><span class="lp-bar-count">58</span></div>
  <div class="lp-bar-row"><span class="lp-bar-label">Technology guides</span><div class="lp-bar-track"><div class="lp-bar-fill" style="width:29%"></div></div><span class="lp-bar-count">50</span></div>
  <div class="lp-bar-row"><span class="lp-bar-label">OS / embedded</span><div class="lp-bar-track"><div class="lp-bar-fill" style="width:18%"></div></div><span class="lp-bar-count">31</span></div>
  <div class="lp-bar-row"><span class="lp-bar-label">Foundations & prep</span><div class="lp-bar-track"><div class="lp-bar-fill" style="width:13%"></div></div><span class="lp-bar-count">22</span></div>
  <div class="lp-bar-row"><span class="lp-bar-label">Product-scale notes</span><div class="lp-bar-track"><div class="lp-bar-fill" style="width:6%"></div></div><span class="lp-bar-count">11</span></div>
</div>

<figure class="diagram-figure">
  <img src="{{ '/assets/diagrams/88d177a65e8ee5d5.png' | relative_url }}" alt="Distribution chart" class="diagram-img" loading="lazy" />
</figure>

<p class="diagram-caption">Bar chart + pie chart — same data, pick whichever reads easier for you.</p>

| Category | ~Posts | What it covers |
|----------|-------:|----------------|
| **System design problems** | 58 | Step-by-step “Design a …” walkthroughs (URL shortener → Uber, crawlers, schedulers) |
| **Technology guides** | 50 | Deep dives on tools you plug into designs (reference, not read cover-to-cover) |
| **OS, embedded & domain prep** | 31 | OS frameworks, JNI, glass/IoT, Android native, **hardware test & DFT** |
| **Foundations & interview prep** | 22 | Framework, CAP, patterns, references, question lists, ecosystem map |
| **Product-scale designs** | 11 | Concise “System Design: Twitter/YouTube/…” product notes |
| **Total** | **{{ site.posts.size }}** | Full lists in [Section 3](#3-all-posts-by-category) (expandable) |

### High-level content map

How the major tracks relate—start at the top, branch only when your role or a design requires it.

<figure class="diagram-figure">
  <img src="{{ '/assets/diagrams/c2e6caca6c0f8bc2.png' | relative_url }}" alt="System architecture diagram" class="diagram-img" loading="lazy" />
</figure>

<p class="diagram-caption">Main path flows left to right inside each box; dashed lines mean “open when needed,” not required reading order.</p>

### Three ways to use this blog

<div class="lp-card-grid">
  <div class="lp-audience-card">
    <h4>New to system design interviews</h4>
    <p>Start with the <a href="{{ site.baseurl }}/2025/10/04/system-design-interview-framework/">interview framework</a>, then <a href="#1-system-design-study-path">Level 0–1</a> and your first design: <a href="{{ site.baseurl }}/2026/05/26/design-url-shortener/">URL shortener</a>.</p>
  </div>
  <div class="lp-audience-card">
    <h4>Backend / platform practice</h4>
    <p>Follow <a href="#level-2-intermediate-distributed-systems">Levels 2–3</a> in order. Open the <a href="{{ site.baseurl }}/2025/11/29/technology-list-quick-reference/">tech reference</a> only when a post names a tool you do not know.</p>
  </div>
  <div class="lp-audience-card">
    <h4>OS, embedded, or hardware test</h4>
    <p>Jump to <a href="#level-5-specialized-tracks-optional">Level 5</a>, or start with <a href="{{ site.baseurl }}/2025/11/03/os-frameworks-system-design/">OS frameworks</a> / <a href="{{ site.baseurl }}/2026/05/26/hardware-design-for-testing/">hardware test & DFT</a>.</p>
  </div>
</div>

**New posts worth noting (2026):** [URL shortener]({{ site.baseurl }}/2026/05/26/design-url-shortener/) · [Rate limiter]({{ site.baseurl }}/2026/05/26/design-rate-limiter/) · [Distributed ecosystem map]({{ site.baseurl }}/2026/05/26/distributed-system-design-ecosystem/) · [Hardware design for testing & DFT]({{ site.baseurl }}/2026/05/26/hardware-design-for-testing/)

---

## 1. System Design Study Path

Follow **Level 0 → 3** in order for a typical backend/platform interview. Use **Level 4** for technology depth on demand. **Level 5** is optional for OS, embedded, or hardware roles.

| Level | Focus | Time hint | Outcome |
|:-----:|-------|-----------|---------|
| **0** | Orientation & references | Week 0 | Know where to study and how interviews run |
| **1** | Fundamentals & small designs | Weeks 1–2 | Explain requirements, API, data model on simple problems |
| **2** | Distributed building blocks | Weeks 3–5 | Design cache, queues, feeds, crawlers with scale hooks |
| **3** | Large-scale products | Weeks 6+ | Twitter, Uber, schedulers, LLM-style systems |
| **4** | Technology guides (on demand) | As needed | Redis, Kafka, DBs, K8s when a design requires them |
| **5** | Specialized tracks (optional) | Role-specific | OS/middleware, embedded, hardware test & DFT |
{: .lp-level-table}

<figure class="diagram-figure">
  <img src="{{ '/assets/diagrams/b4778b2226a424a2.png' | relative_url }}" alt="System architecture diagram" class="diagram-img" loading="lazy" />
</figure>


<figure class="diagram-figure">
  <img src="{{ '/assets/diagrams/1471e7b8093d42ca.png' | relative_url }}" alt="Timeline diagram" class="diagram-img" loading="lazy" />
</figure>

<p class="diagram-caption">Top: level dependencies. Bottom: a sample 10-week backend timeline — adjust pace to your schedule.</p>

---

### Level 0 — Orientation & references

**Goal:** Set up your study map before deep designs.

| # | Read |
|---|------|
| 1 | [System Design Interview Framework]({{ site.baseurl }}/2025/10/04/system-design-interview-framework/) |
| 2 | [System Design Interview Guide]({{ site.baseurl }}/2025/11/03/system-design-interview/) |
| 3 | [System Design References]({{ site.baseurl }}/2025/11/03/system-design-references/) |
| 4 | [Distributed System Design Ecosystem]({{ site.baseurl }}/2026/05/26/distributed-system-design-ecosystem/) |
| 5 | External: [Hello Interview](https://www.hellointerview.com/learn/system-design) · [ByteByteGo](https://bytebytego.com/courses/system-design-interview) |

---

### Level 1 — Fundamentals (beginner)

**Goal:** Learn interview structure and practice **single-machine / small** designs.

#### Core concepts (read first)

1. [Client to API Gateway Connection Options]({{ site.baseurl }}/2025/10/04/system-design-client-api-gateway-connection-options/)
2. [System Design Overview: Cloud-Native]({{ site.baseurl }}/2025/10/29/system-design-overview-cloud/)
3. [System Design Overview: Embedded]({{ site.baseurl }}/2025/10/29/system-design-overview-embedded/)
4. [CAP Theorem Guide]({{ site.baseurl }}/2025/11/29/cap-theorem-guide/)
5. [Common Domain System Design Patterns]({{ site.baseurl }}/2025/11/24/common-domain-system-design-patterns/)
6. [System Design Technologies Trade-offs]({{ site.baseurl }}/2025/11/17/system-design-technologies-trade-offs/)
7. [Common Non-Distributed System Design Questions]({{ site.baseurl }}/2025/11/24/common-non-distributed-system-design-questions/)

#### Classic starter designs (in recommended order)

1. [Design a URL Shortener (full)]({{ site.baseurl }}/2026/05/26/design-url-shortener/) — review: [short notes]({{ site.baseurl }}/2025/10/29/system-design-url-shortener/)
2. [Design a Rate Limiter (full)]({{ site.baseurl }}/2026/05/26/design-rate-limiter/) — review: [short notes]({{ site.baseurl }}/2025/10/29/system-design-rate-limiter/)
3. [Design a Parking Lot System]({{ site.baseurl }}/2025/11/24/design-parking-lot-system/)
4. [Design a Library Management System]({{ site.baseurl }}/2025/11/24/design-library-management-system/)
5. [Design a Ticket Booking System]({{ site.baseurl }}/2025/11/24/design-ticket-booking-system/)
6. [Design an ATM / Banking System]({{ site.baseurl }}/2025/11/24/design-atm-banking-system/)
7. [Design a Basic Online Shopping Cart]({{ site.baseurl }}/2025/11/24/design-online-shopping-cart/)
8. [Design a File System or In-Memory Storage]({{ site.baseurl }}/2025/11/24/design-file-system-in-memory-storage/)
9. [Design a Text Editor]({{ site.baseurl }}/2025/11/24/design-text-editor/)
10. [Design a Social Media Feed (Local)]({{ site.baseurl }}/2025/11/24/design-social-media-feed-local/)
11. [Design a Simple Chat Application]({{ site.baseurl }}/2025/11/24/design-simple-chat-application/)

#### Local system components (LLD-style)

- [Thread Pool]({{ site.baseurl }}/2025/11/24/design-thread-pool/)
- [Task Scheduler (Single Machine)]({{ site.baseurl }}/2025/11/24/design-task-scheduler-single-machine/)
- [Connection Pool]({{ site.baseurl }}/2025/11/24/design-connection-pool/)
- [Producer-Consumer Queue]({{ site.baseurl }}/2025/11/24/design-producer-consumer-queue/)
- [Circular Buffer]({{ site.baseurl }}/2025/11/24/design-circular-buffer/)
- [Memory Allocator]({{ site.baseurl }}/2025/11/24/design-memory-allocator/)
- [Local Logger]({{ site.baseurl }}/2025/11/24/design-local-logger/)

---

### Level 2 — Intermediate (distributed systems)

**Goal:** Add **caching, storage, messaging, search, and feeds** with scalability and reliability.

#### Distributed storage & databases

- [Design a Key-Value Store (Local & Horizontal)]({{ site.baseurl }}/2025/11/14/design-key-value-store-local-horizontal/)
- [Design Blob Storage Like S3]({{ site.baseurl }}/2025/11/09/design-blob-storage-like-s3/)
- [Design a File Storage Sync System (Dropbox)]({{ site.baseurl }}/2025/11/14/design-file-storage-sync-system/)
- [Design a Configuration Service with LRU Cache]({{ site.baseurl }}/2025/11/14/design-configuration-service-lru-cache/)

#### Messaging & real-time

- [Design a Chat System]({{ site.baseurl }}/2025/11/14/design-chat-system/)
- [Design a Pub/Sub System]({{ site.baseurl }}/2025/11/29/design-pub-sub-system/)
- [System Design: Notification/Push Service]({{ site.baseurl }}/2025/10/29/system-design-notification-service/)
- [System Design: Chat/Messaging Service]({{ site.baseurl }}/2025/10/29/system-design-chat-service/)
- [Design a Real-Time Game Leaderboard]({{ site.baseurl }}/2025/11/13/design-real-time-game-leaderboard/)

#### Search, crawl & analytics

- [Design a Web Crawler]({{ site.baseurl }}/2025/11/13/design-web-crawler/) → then [Distributed Web Crawler]({{ site.baseurl }}/2025/11/14/design-distributed-web-crawler/)
- [Design a Search Autocomplete System]({{ site.baseurl }}/2025/11/14/design-search-autocomplete-system/)
- [Design a Top-K Heavy Hitter]({{ site.baseurl }}/2025/11/14/design-top-k-heavy-hitter/)

#### Social & media

- [Design a News Feed]({{ site.baseurl }}/2025/11/13/design-news-feed/)
- [Design Instagram]({{ site.baseurl }}/2025/11/13/design-instagram/)
- [Design a Like/Unlike Feature]({{ site.baseurl }}/2025/11/29/design-like-unlike-feature/)

#### Level 2 — essential technology reads

Open when the design above mentions the tool:

- [Redis Comprehensive Guide]({{ site.baseurl }}/2025/11/08/redis-comprehensive-guide/)
- [Apache Kafka Guide]({{ site.baseurl }}/2025/11/13/apache-kafka-guide/)
- [PostgreSQL Comprehensive Guide]({{ site.baseurl }}/2025/11/09/postgresql-comprehensive-guide/)
- [Amazon S3 Storage Guide]({{ site.baseurl }}/2025/11/13/amazon-s3-storage-guide/)
- [Technology List Quick Reference]({{ site.baseurl }}/2025/11/29/technology-list-quick-reference/)

---

### Level 3 — Advanced (large-scale systems)

**Goal:** Design **complex, high-traffic** products and infrastructure.

#### Large-scale platforms

- [System Design: Twitter]({{ site.baseurl }}/2025/10/29/system-design-twitter/)
- [Design a Social Media Feed (Twitter)]({{ site.baseurl }}/2025/11/20/design-social-media-feed-twitter/)
- [Design YouTube (full)]({{ site.baseurl }}/2025/11/14/design-youtube/) · [YouTube (short)]({{ site.baseurl }}/2025/10/29/system-design-youtube/)
- [Design Netflix]({{ site.baseurl }}/2025/11/14/design-netflix/)
- [Design Facebook Live Streaming]({{ site.baseurl }}/2025/11/14/design-facebook-live-streaming/)

#### E-commerce & marketplace

- [Design a Hotel Reservation System]({{ site.baseurl }}/2025/11/14/design-hotel-reservation-system/)
- [Design an Auction System]({{ site.baseurl }}/2025/11/14/design-auction-system/)
- [Design Ticketmaster]({{ site.baseurl }}/2025/11/14/design-ticketmaster/)
- [Design a Proximity Service (Yelp)]({{ site.baseurl }}/2025/11/14/design-proximity-service-yelp/)
- [Design a Price Drop Tracker]({{ site.baseurl }}/2025/11/14/design-price-drop-tracker/)
- [Design CamelCamelCamel Price Tracker]({{ site.baseurl }}/2025/11/14/design-camelcamelcamel-price-tracker/)

#### Ride-sharing, finance & payments

- [Design a Ride-Sharing Service (Uber)]({{ site.baseurl }}/2025/11/20/design-ride-sharing-service-uber/)
- [System Design: Robinhood Trading Platform]({{ site.baseurl }}/2025/10/29/system-design-robinhood-trading-platform/)
- [Design a Delayed Payment Scheduler]({{ site.baseurl }}/2025/11/29/design-delayed-payment-scheduler-service/)

#### Gaming & entertainment

- [Design Roblox]({{ site.baseurl }}/2025/11/16/design-roblox/)
- [Design Roblox Studio]({{ site.baseurl }}/2025/11/16/design-roblox-studio/)
- [Design In-Memory Gaming Platform (Matchmaking)]({{ site.baseurl }}/2025/11/24/design-in-memory-gaming-platform-matchmaking/)
- [Design Matchmaking for Multiplayer Games]({{ site.baseurl }}/2025/11/29/design-matchmaking-service-multiplayer-games/)
- [Design a Resource Loader (Game Engine)]({{ site.baseurl }}/2025/11/29/design-resource-loader-game-engine/)
- [Design a Chess Game (Undo/ELO)]({{ site.baseurl }}/2025/11/14/design-chess-game-undo-elo/)

#### AI, collaboration & infrastructure

- [System Design: ChatGPT-Style LLM Service]({{ site.baseurl }}/2025/10/29/system-design-chatgpt/)
- [Design a Global Translation Service]({{ site.baseurl }}/2025/11/14/design-global-translation-service-hybrid/)
- [System Design: GitHub]({{ site.baseurl }}/2025/10/29/system-design-github/)
- [Design a To-Do App with Multi-User Collaboration]({{ site.baseurl }}/2025/11/29/design-todo-list-app-multi-user-collaboration/)
- [Design a Distributed Job Scheduler]({{ site.baseurl }}/2025/11/03/design-distributed-job-scheduler/)
- [Design a Distributed Logging System]({{ site.baseurl }}/2025/11/17/design-distributed-logging-system/)
- [System Design: Metrics & Logging Pipeline]({{ site.baseurl }}/2025/10/29/system-design-metrics-logging-pipeline/)
- [Design a Change Data Capture (CDC) System]({{ site.baseurl }}/2025/11/29/design-change-data-capture-cdc/)

#### AR / glass & IoT (advanced product)

- [System Design: Meta Glass]({{ site.baseurl }}/2025/10/29/system-design-meta-glass/)
- [Design Glass System]({{ site.baseurl }}/2025/11/04/design-glass-system/)
- [Design Smart Glass: Voice-Controlled Memory Video]({{ site.baseurl }}/2025/11/08/design-smart-glass-voice-controlled-memory-video/)
- [Design QuickSet UEI (IoT/Smart Home)]({{ site.baseurl }}/2025/11/17/design-quickset-uei/)

---

### Level 4 — Technology depth (reference library)

**Goal:** Deep dive on components **when a Level 2–3 design needs them**—not required cover-to-cover.

| Area | Start here |
|------|------------|
| **Index** | [Technology List Quick Reference]({{ site.baseurl }}/2025/11/29/technology-list-quick-reference/) |
| **Caching** | [Redis]({{ site.baseurl }}/2025/11/08/redis-comprehensive-guide/) · [Memcached]({{ site.baseurl }}/2025/11/29/memcached-comprehensive-guide/) |
| **SQL** | [PostgreSQL]({{ site.baseurl }}/2025/11/09/postgresql-comprehensive-guide/) · [MySQL]({{ site.baseurl }}/2025/11/29/mysql-comprehensive-guide/) |
| **NoSQL** | [DynamoDB]({{ site.baseurl }}/2025/11/09/amazon-dynamodb-comprehensive-guide/) · [Cassandra]({{ site.baseurl }}/2025/11/09/apache-cassandra-comprehensive-guide/) · [MongoDB]({{ site.baseurl }}/2025/11/29/mongodb-comprehensive-guide/) |
| **Streaming** | [Kafka]({{ site.baseurl }}/2025/11/13/apache-kafka-guide/) · [Flink]({{ site.baseurl }}/2025/11/29/apache-flink-guide/) |
| **Queues** | [Amazon SQS]({{ site.baseurl }}/2025/11/13/amazon-sqs-guide/) · [RabbitMQ]({{ site.baseurl }}/2025/11/29/rabbitmq-comprehensive-guide/) |
| **Storage & CDN** | [Amazon S3]({{ site.baseurl }}/2025/11/13/amazon-s3-storage-guide/) · [CDN Guide]({{ site.baseurl }}/2025/11/29/cdn-content-delivery-network-guide/) |
| **Search** | [Elasticsearch]({{ site.baseurl }}/2025/11/29/elasticsearch-guide/) |
| **Infra** | [Kubernetes]({{ site.baseurl }}/2025/11/29/kubernetes-comprehensive-guide/) · [NGINX]({{ site.baseurl }}/2025/11/29/nginx-comprehensive-guide/) · [Load Balancer]({{ site.baseurl }}/2025/11/29/load-balancer-comprehensive-guide/) |
| **Theory** | [CAP Theorem]({{ site.baseurl }}/2025/11/29/cap-theorem-guide/) · [SQL vs NoSQL]({{ site.baseurl }}/2025/11/08/sql-vs-nosql-database-comparison/) |

Full technology tree: [Learning Path & Technology Index]({{ site.baseurl }}/2025/11/29/system-design-learning-path-index/#technology-tree)

---

### Level 5 — Specialized tracks (optional)

**Goal:** OS frameworks, embedded, Android native, or **hardware validation / DFT** interviews.

#### OS & middleware

1. [OS Frameworks System Design Guide]({{ site.baseurl }}/2025/11/03/os-frameworks-system-design/)
2. [OS/Frameworks 7-Day Prep Todo]({{ site.baseurl }}/2025/11/05/os-frameworks-7-day-prep-todo/)
3. [OS Internals Study Guide]({{ site.baseurl }}/2025/11/04/os-internals-study-guide/)
4. [Design a JNI Bridge]({{ site.baseurl }}/2025/11/03/design-jni-bridge/)
5. [Design a Local OS Framework System]({{ site.baseurl }}/2025/11/04/design-local-os-framework-system/)
6. [Kubernetes in System Design Scenarios]({{ site.baseurl }}/2025/11/17/kubernetes-system-design-scenarios/)

#### Embedded & client systems

- [Design Client-Side Embedded Report Events]({{ site.baseurl }}/2025/11/04/design-client-side-embedded-report-events/)
- [Design Embedded Report Event System]({{ site.baseurl }}/2025/11/04/design-embedded-report-event/)
- [Design an Embedded Local Redis Cache]({{ site.baseurl }}/2025/11/14/design-embedded-local-redis-cache/)
- [Design NDK: Merge Multiple .so Libraries]({{ site.baseurl }}/2025/11/09/design-ndk-merge-multiple-so-libraries/)

#### Hardware test & DFT

- [Hardware Design for Testing & DFT]({{ site.baseurl }}/2026/05/26/hardware-design-for-testing/) — ATE/DUT fixtures + silicon scan/BIST/JTAG

#### Interview question lists

- [Senior System Design Common Questions]({{ site.baseurl }}/2025/11/04/senior-system-design-common-questions/)
- [Backend System Design Questions]({{ site.baseurl }}/2025/11/04/backend-system-design-questions/)
- [Android Native System Design Questions]({{ site.baseurl }}/2025/11/04/android-native-system-design-questions/)
- [System Design LeetCode Practice]({{ site.baseurl }}/2025/11/13/system-design-leetcode-practice/)

---

## 2. How this blog is organized

**New to system design?** This section explains what kinds of posts exist, what order to read them in, and why some topics appear more than once. You do not need to read every post—use this map to pick the right starting point.

<figure class="diagram-figure">
  <img src="{{ '/assets/diagrams/c12b1fad2384752f.png' | relative_url }}" alt="System architecture diagram" class="diagram-img" loading="lazy" />
</figure>

<p class="diagram-caption">Read §1 first for the study path; use §3–§4 as lookup tables when you need a specific post.</p>

### The big picture (30 seconds)

1. Learn **how to run an interview** (framework, vocabulary, trade-offs).
2. Practice **classic design questions** (URL shortener, chat, news feed, …).
3. Look up **technologies** (Redis, Kafka, databases) only when a design needs them.

External courses ([Hello Interview](https://www.hellointerview.com/learn/system-design), [ByteByteGo](https://bytebytego.com/courses/system-design-interview)) pair well with this blog. Start with [References]({{ site.baseurl }}/2025/11/03/system-design-references/) and the [study path](#1-system-design-study-path) above.

### Recommended reading order

<figure class="diagram-figure">
  <img src="{{ '/assets/diagrams/5b9b8557b09c8bb0.png' | relative_url }}" alt="System architecture diagram" class="diagram-img" loading="lazy" />
</figure>

<p class="diagram-caption">Solid arrows = recommended order. Dashed lines = open a tech guide only when that design needs it.</p>

### Five types of posts (and when to use each)

Every post on this blog fits **one** of these buckets. Section [3](#3-all-posts-by-category) lists them all.

| Type | What it is | When to read it | Title often looks like |
|------|------------|-----------------|-------------------------|
| **Foundations & interview prep** | How to think, what to say in interviews, book/course links | **First 1–2 weeks** of study | “Interview framework”, “References”, “CAP theorem” |
| **System design problem** | Step-by-step answer to “Design a X” (requirements → API → diagram → scale) | **Main practice** after foundations | “Design a URL Shortener”, “Design a Chat System” |
| **Product-scale design** | Shorter notes on a famous product (Twitter, GitHub, …) | Quick review or second pass on a topic | “System Design: Twitter”, “System Design: YouTube” |
| **Technology guide** | Deep dive on one tool (Redis, Kafka, PostgreSQL, …) | When that tool appears in a design you are studying | “Redis comprehensive guide”, “Apache Kafka guide” |
| **OS / embedded prep** | OS frameworks, JNI, devices, glass, Android native, **hardware test & DFT** | Only if your role is OS/middleware/embedded/validation hardware | “OS frameworks”, “Hardware design for testing” |

**Not sure where to click?**

| Your goal | Start here |
|-----------|------------|
| I have never done a system design interview | [Interview framework]({{ site.baseurl }}/2025/10/04/system-design-interview-framework/) → [URL shortener]({{ site.baseurl }}/2026/05/26/design-url-shortener/) |
| I know basics; I want interview practice | [Level 2 & 3](#level-2--intermediate-distributed-systems) in the study path |
| I keep hearing “use Redis/Kafka” and feel lost | [Technology quick reference]({{ site.baseurl }}/2025/11/29/technology-list-quick-reference/) → pick one guide |
| I want one long curated list | [Learning path index]({{ site.baseurl }}/2025/11/29/system-design-learning-path-index/) |
| I need the full map of components | [Distributed system ecosystem]({{ site.baseurl }}/2026/05/26/distributed-system-design-ecosystem/) |

### Why the same topic sometimes has two posts

This is normal. Use the rule that fits your situation:

**A. Full guide + short notes (read the full one first)**  
The **full** post walks through requirements, APIs, scaling, and trade-offs. The **short** post is a quick recap—good for review right before an interview, not ideal as your first read.

| Topic | Read first (full) | Then review (short) |
|-------|-------------------|---------------------|
| URL shortener | [Full guide]({{ site.baseurl }}/2026/05/26/design-url-shortener/) | [Short notes]({{ site.baseurl }}/2025/10/29/system-design-url-shortener/) |
| Rate limiter | [Full guide]({{ site.baseurl }}/2026/05/26/design-rate-limiter/) | [Short notes]({{ site.baseurl }}/2025/10/29/system-design-rate-limiter/) |

**B. Simple version → harder version (go in order)**  
Start with the simpler problem, then read the scaled-up version.

| Start here | Then read |
|------------|-----------|
| [Web crawler]({{ site.baseurl }}/2025/11/13/design-web-crawler/) | [Distributed web crawler (10k nodes)]({{ site.baseurl }}/2025/11/14/design-distributed-web-crawler/) |
| [Social feed (local)]({{ site.baseurl }}/2025/11/24/design-social-media-feed-local/) | [News feed (distributed)]({{ site.baseurl }}/2025/11/13/design-news-feed/) |

**C. Product overview + focused deep dive (either order is OK)**  
One post covers the whole product; another zooms in on one piece (e.g. feed only).

| Product overview | Focused deep dive |
|------------------|-------------------|
| [System Design: Twitter]({{ site.baseurl }}/2025/10/29/system-design-twitter/) | [Design social media feed (Twitter)]({{ site.baseurl }}/2025/11/20/design-social-media-feed-twitter/) |
| [System Design: YouTube (short)]({{ site.baseurl }}/2025/10/29/system-design-youtube/) | [Design YouTube (full)]({{ site.baseurl }}/2025/11/14/design-youtube/) |

**D. Index page → many linked posts**  
Some posts are **tables of contents**, not lessons themselves.

| Index (start here) | What it links to |
|--------------------|------------------|
| [Technology quick reference]({{ site.baseurl }}/2025/11/29/technology-list-quick-reference/) | All technology guides (Redis, Kafka, databases, …) |
| [Learning path index]({{ site.baseurl }}/2025/11/29/system-design-learning-path-index/) | Level 1–3 design problems in study order |
| **This page** | Learning path + every post by category |

### How designs and technologies connect

You do **not** read every technology guide first. Use this loop while you practice:

| Step | What to do | Example on this blog |
|:----:|------------|----------------------|
| 1 | Learn how to structure an interview answer | [Interview framework]({{ site.baseurl }}/2025/10/04/system-design-interview-framework/) |
| 2 | Pick one **small** design and read it end-to-end | [URL shortener]({{ site.baseurl }}/2026/05/26/design-url-shortener/) |
| 3 | If the post names a tool you do not know, pause and open **only that** guide | “cache” → [Redis]({{ site.baseurl }}/2025/11/08/redis-comprehensive-guide/); “queue” → [Kafka]({{ site.baseurl }}/2025/11/13/apache-kafka-guide/) |
| 4 | Finish the design, then pick the **next** problem (repeat steps 2–3) | [Rate limiter]({{ site.baseurl }}/2026/05/26/design-rate-limiter/) → [News feed]({{ site.baseurl }}/2025/11/13/design-news-feed/) |
| 5 | After several designs, try **larger** systems | [Twitter]({{ site.baseurl }}/2025/10/29/system-design-twitter/) · [Uber]({{ site.baseurl }}/2025/11/20/design-ride-sharing-service-uber/) |
| 6 | Optional: see how pieces fit together | [Distributed system ecosystem]({{ site.baseurl }}/2026/05/26/distributed-system-design-ecosystem/) |

**Practice loop:** Interview basics → small design → unknown tool? open that tech guide → finish → repeat → larger systems.

<figure class="diagram-figure">
  <img src="{{ '/assets/diagrams/15eb886c6aac16e7.png' | relative_url }}" alt="System architecture diagram" class="diagram-img" loading="lazy" />
</figure>


**How to read the diagram:** Loop **② → ③ → ④** for each new problem. When **⑤** is “ready,” move to **⑥**—usually after several small/medium designs, not the first week.

### Optional: OS / embedded / hardware track

Only needed for OS framework, middleware, device, or **hardware validation** interviews—not for typical backend “Design Twitter” loops.

1. [OS frameworks guide]({{ site.baseurl }}/2025/11/03/os-frameworks-system-design/)  
2. [7-day prep todo]({{ site.baseurl }}/2025/11/05/os-frameworks-7-day-prep-todo/)  
3. [Hardware design for testing & DFT]({{ site.baseurl }}/2026/05/26/hardware-design-for-testing/) — ATE/DUT fixtures plus silicon DFT (scan, BIST, JTAG)  
4. Topic posts (JNI, embedded events, glass, etc.) — listed under **OS, embedded & domain prep** in [Section 3](#3-all-posts-by-category).

---

## 3. All posts by category

<details class="lp-collapse" markdown="1">
<summary>Expand full post lists by category ({{ site.posts.size }} posts)</summary>

{% assign posts_by_date = site.posts | sort: 'date' | reverse %}

{% assign categories = "Foundations & interview prep,System design problem,Product-scale design,Technology guide,OS, embedded & domain prep,Other" | split: "," %}

{% for category in categories %}
### {{ category }}

<ul class="post-index-list">
{% for post in posts_by_date %}
{% capture post_cat %}{% include post-category.html post=post %}{% endcapture %}
{% assign post_cat = post_cat | strip %}
{% if post_cat == category %}
<li>
  <a href="{{ post.url | relative_url }}">{{ post.title | escape }}</a>
  <span class="post-index-date">({{ post.date | date: "%Y-%m-%d" }})</span>
</li>
{% endif %}
{% endfor %}
</ul>
{% endfor %}

</details>

---

## 4. Complete post catalog

<details class="lp-collapse" markdown="1">
<summary>Expand alphabetical catalog (every post)</summary>

Alphabetical index — **every** post with category and link.

| Post | Category | Date |
|------|----------|------|
{% assign posts_alpha = site.posts | sort: 'title' %}
{% for post in posts_alpha %}
{% capture post_cat %}{% include post-category.html post=post %}{% endcapture %}
| [{{ post.title | escape }}]({{ post.url | relative_url }}) | {{ post_cat | strip }} | {{ post.date | date: "%Y-%m-%d" }} |
{% endfor %}

</details>

---

## Summary

| Metric | Value |
|--------|------:|
| Total posts | {{ site.posts.size }} |
| Categories | 6 |
| Last updated | {{ page.date | date: "%B %d, %Y" }} |

Use the **Learning Path** link in the top navigation to return here anytime.
