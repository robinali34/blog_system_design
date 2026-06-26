---
layout: page
title: "Learning Path"
permalink: /system-design-list.html
date: 2026-05-26
categories: [System Design, Learning Path, Reference]
---

# System Design Interview — Learning Path & Blog Index

<div class="lp-hero">
  <p class="lp-hero-lead"><strong>New to system design?</strong> This page is your map through <strong>{{ site.posts.size }} posts</strong> — follow the graphs below, then dive into Levels 0–5. Every design post includes <strong>architecture PNG diagrams</strong> you can skim before reading.</p>
  <div class="lp-stat-grid">
    <div class="lp-stat"><span class="lp-stat-num">6</span><span class="lp-stat-label">Study levels</span></div>
    <div class="lp-stat"><span class="lp-stat-num">58</span><span class="lp-stat-label">Design walkthroughs</span></div>
    <div class="lp-stat"><span class="lp-stat-num">50</span><span class="lp-stat-label">Tech guides</span></div>
    <div class="lp-stat"><span class="lp-stat-num">~10</span><span class="lp-stat-label">Weeks to advanced</span></div>
  </div>
  <nav class="lp-jump-nav" aria-label="Jump to study level">
    <a href="#new-here-start-in-30-minutes" class="lp-pill lp-pill-start">Start here</a>
    <a href="#level-0-orientation-references" class="lp-pill lp-pill-0">Level 0</a>
    <a href="#level-1-fundamentals-beginner" class="lp-pill lp-pill-1">Level 1</a>
    <a href="#level-2-intermediate-distributed-systems" class="lp-pill lp-pill-2">Level 2</a>
    <a href="#level-3-advanced-large-scale-systems" class="lp-pill lp-pill-3">Level 3</a>
    <a href="#level-4-technology-depth-reference-library" class="lp-pill lp-pill-4">Level 4</a>
    <a href="#level-5-specialized-tracks-optional" class="lp-pill lp-pill-5">Level 5</a>
  </nav>
</div>

---

## New here? Start in 30 minutes

If you have **never** done a system design interview, do exactly this before exploring the full index.

<figure class="diagram-figure diagram-figure-prominent">
  <img src="{{ '/assets/diagrams/lp-new-reader-journey.png' | relative_url }}" alt="New reader journey: framework, first design, then scale" class="diagram-img" loading="eager" />
</figure>

<div class="lp-start-steps">

| Step | Time | Do this | Why |
|:----:|:----:|---------|-----|
| **1** | 15 min | [Interview framework]({{ site.baseurl }}/2025/10/04/system-design-interview-framework/) | Learn how interviews are structured (requirements → API → diagram → scale) |
| **2** | 30 min | [Design a URL Shortener]({{ site.baseurl }}/2026/05/26/design-url-shortener/) — **skim the architecture diagrams first** | Your first end-to-end design with caching and scale |
| **3** | 20 min | [Design a Rate Limiter]({{ site.baseurl }}/2026/05/26/design-rate-limiter/) | Adds Redis, gateways, and a second classic question |

</div>

<p class="lp-cta-row">
  <a href="{{ site.baseurl }}/2025/10/04/system-design-interview-framework/" class="lp-cta-btn">Step 1 — Framework</a>
  <a href="{{ site.baseurl }}/2026/05/26/design-url-shortener/" class="lp-cta-btn lp-cta-primary">Step 2 — URL Shortener</a>
  <a href="#1-system-design-study-path" class="lp-cta-btn">Full study path ↓</a>
</p>

---

## Study path at a glance

Six levels from **orientation** to **large-scale products**. Level 4 (tech guides) and Level 5 (OS / hardware) branch off when your role or a design requires them.

<figure class="diagram-figure diagram-figure-prominent">
  <img src="{{ '/assets/diagrams/lp-level-roadmap.png' | relative_url }}" alt="Levels 0 through 5 study roadmap with topics" class="diagram-img" loading="lazy" />
</figure>

<p class="diagram-caption">Follow solid arrows in order. Dashed lines = open only when needed (tech guides or specialized tracks).</p>

<div class="lp-diagram-row">
<figure class="diagram-figure">
  <img src="{{ '/assets/diagrams/lp-week-timeline.png' | relative_url }}" alt="Sample 10-week study timeline" class="diagram-img" loading="lazy" />
</figure>
<figure class="diagram-figure">
  <img src="{{ '/assets/diagrams/88d177a65e8ee5d5.png' | relative_url }}" alt="Blog content distribution by category" class="diagram-img" loading="lazy" />
</figure>
</div>

<p class="diagram-caption">Left: sample week-by-week pace. Right: how {{ site.posts.size }} posts split across categories.</p>

| Level | Focus | Time | You can design… |
|:-----:|-------|------|-----------------|
| **0** | Orientation | Week 0 | How interviews work; where to look things up |
| **1** | Fundamentals | Weeks 1–2 | URL shortener, rate limiter, parking lot, local chat |
| **2** | Distributed | Weeks 3–5 | Feeds, chat at scale, crawlers, KV store, pub/sub |
| **3** | Advanced | Weeks 6+ | Twitter, Uber, YouTube, schedulers, LLM-style APIs |
| **4** | Tech depth | On demand | Redis, Kafka, SQL, K8s — when a post names the tool |
| **5** | Specialized | Optional | OS frameworks, embedded, hardware test & DFT |

---

## What knowledge you'll build

Each level adds skills that stack. Posts on this blog mirror that growth — diagrams in every walkthrough show the architecture before the deep dive.

<figure class="diagram-figure diagram-figure-prominent">
  <img src="{{ '/assets/diagrams/lp-knowledge-growth.png' | relative_url }}" alt="Knowledge growth from interview skills to product systems" class="diagram-img" loading="lazy" />
</figure>

<details class="lp-collapse" markdown="1">
<summary>Expand full topic mind map</summary>

<figure class="diagram-figure">
  <img src="{{ '/assets/diagrams/lp-knowledge-mindmap.png' | relative_url }}" alt="System design topic mind map" class="diagram-img" loading="lazy" />
</figure>

</details>

### Pick your track

<div class="lp-card-grid">
  <div class="lp-audience-card">
    <h4>Complete beginner</h4>
    <p><a href="{{ site.baseurl }}/2025/10/04/system-design-interview-framework/">Framework</a> → <a href="{{ site.baseurl }}/2026/05/26/design-url-shortener/">URL shortener</a> → <a href="#level-1-fundamentals-beginner">Level 1 list</a></p>
  </div>
  <div class="lp-audience-card">
    <h4>Backend / platform interview</h4>
    <p><a href="#level-2-intermediate-distributed-systems">Level 2</a> → <a href="#level-3-advanced-large-scale-systems">Level 3</a>. Open <a href="{{ site.baseurl }}/2025/11/29/technology-list-quick-reference/">tech reference</a> when stuck.</p>
  </div>
  <div class="lp-audience-card">
    <h4>OS, embedded, or hardware</h4>
    <p>Jump to <a href="#level-5-specialized-tracks-optional">Level 5</a>: <a href="{{ site.baseurl }}/2025/11/03/os-frameworks-system-design/">OS frameworks</a> or <a href="{{ site.baseurl }}/2026/05/26/hardware-design-for-testing/">hardware test &amp; DFT</a>.</p>
  </div>
</div>

### Level previews (example architecture from each stage)

<p class="diagram-caption">Wide architecture diagrams — click any image to view full size.</p>

<div class="lp-level-preview-grid">
  <article class="lp-level-preview-card">
    <button type="button" class="lp-level-thumb-wrap" data-caption="Level 0 — Orientation (ecosystem map)" aria-label="Enlarge Level 0 architecture diagram">
      <img src="{{ '/assets/diagrams/bbe2f91ff3a48969.png' | relative_url }}" alt="Distributed ecosystem map" class="lp-level-thumb" loading="lazy" />
      <span class="lp-level-zoom-hint">Click to enlarge</span>
    </button>
    <a href="#level-0-orientation-references" class="lp-level-preview-meta">
      <span class="lp-level-badge-sm">0</span>
      <strong>Orientation</strong>
      <span>Ecosystem &amp; interview prep</span>
    </a>
  </article>
  <article class="lp-level-preview-card">
    <button type="button" class="lp-level-thumb-wrap" data-caption="Level 1 — Fundamentals (URL shortener)" aria-label="Enlarge Level 1 architecture diagram">
      <img src="{{ '/assets/diagrams/037c7cb2141b4861.png' | relative_url }}" alt="URL shortener architecture" class="lp-level-thumb" loading="lazy" />
      <span class="lp-level-zoom-hint">Click to enlarge</span>
    </button>
    <a href="#level-1-fundamentals-beginner" class="lp-level-preview-meta">
      <span class="lp-level-badge-sm">1</span>
      <strong>Fundamentals</strong>
      <span>URL shortener, rate limiter</span>
    </a>
  </article>
  <article class="lp-level-preview-card">
    <button type="button" class="lp-level-thumb-wrap" data-caption="Level 2 — Distributed (news feed)" aria-label="Enlarge Level 2 architecture diagram">
      <img src="{{ '/assets/diagrams/970eda851480690d.png' | relative_url }}" alt="News feed architecture" class="lp-level-thumb" loading="lazy" />
      <span class="lp-level-zoom-hint">Click to enlarge</span>
    </button>
    <a href="#level-2-intermediate-distributed-systems" class="lp-level-preview-meta">
      <span class="lp-level-badge-sm">2</span>
      <strong>Distributed</strong>
      <span>Feeds, chat, crawlers</span>
    </a>
  </article>
  <article class="lp-level-preview-card">
    <button type="button" class="lp-level-thumb-wrap" data-caption="Level 3 — Advanced (Uber ride-sharing)" aria-label="Enlarge Level 3 architecture diagram">
      <img src="{{ '/assets/diagrams/c9204feca2c1f288.png' | relative_url }}" alt="Uber ride-sharing architecture" class="lp-level-thumb" loading="lazy" />
      <span class="lp-level-zoom-hint">Click to enlarge</span>
    </button>
    <a href="#level-3-advanced-large-scale-systems" class="lp-level-preview-meta">
      <span class="lp-level-badge-sm">3</span>
      <strong>Advanced</strong>
      <span>Uber, Twitter, YouTube</span>
    </a>
  </article>
  <article class="lp-level-preview-card">
    <button type="button" class="lp-level-thumb-wrap" data-caption="Level 4 — Tech guides (Redis)" aria-label="Enlarge Level 4 architecture diagram">
      <img src="{{ '/assets/diagrams/5621851955d16bc0.png' | relative_url }}" alt="Redis architecture" class="lp-level-thumb" loading="lazy" />
      <span class="lp-level-zoom-hint">Click to enlarge</span>
    </button>
    <a href="#level-4-technology-depth-reference-library" class="lp-level-preview-meta">
      <span class="lp-level-badge-sm">4</span>
      <strong>Tech guides</strong>
      <span>Redis, Kafka, K8s…</span>
    </a>
  </article>
  <article class="lp-level-preview-card">
    <button type="button" class="lp-level-thumb-wrap" data-caption="Level 5 — Specialized (hardware test &amp; DFT)" aria-label="Enlarge Level 5 architecture diagram">
      <img src="{{ '/assets/diagrams/6287173f7349ca1f.png' | relative_url }}" alt="Hardware test architecture" class="lp-level-thumb" loading="lazy" />
      <span class="lp-level-zoom-hint">Click to enlarge</span>
    </button>
    <a href="#level-5-specialized-tracks-optional" class="lp-level-preview-meta">
      <span class="lp-level-badge-sm">5</span>
      <strong>Specialized</strong>
      <span>OS, embedded, DFT</span>
    </a>
  </article>
</div>

<dialog id="lp-diagram-lightbox" class="lp-diagram-lightbox" aria-label="Enlarged architecture diagram">
  <form method="dialog">
    <button type="submit" class="lp-lightbox-close" aria-label="Close">×</button>
  </form>
  <img src="" alt="" class="lp-lightbox-img" />
  <p class="lp-lightbox-caption"></p>
</dialog>

<div class="lp-quick-links">
  <strong>Also useful:</strong>
  <a href="{{ site.baseurl }}/2025/11/29/technology-list-quick-reference/">Tech reference</a>
  <a href="{{ site.baseurl }}/2025/11/03/system-design-references/">Books & courses</a>
  <a href="{{ site.baseurl }}/2026/05/26/distributed-system-design-ecosystem/">Ecosystem map</a>
  <a href="{{ site.baseurl }}/posts/">All posts</a>
</div>

**2026 highlights:** [URL shortener]({{ site.baseurl }}/2026/05/26/design-url-shortener/) · [Rate limiter]({{ site.baseurl }}/2026/05/26/design-rate-limiter/) · [Ecosystem map]({{ site.baseurl }}/2026/05/26/distributed-system-design-ecosystem/) · [Hardware test & DFT]({{ site.baseurl }}/2026/05/26/hardware-design-for-testing/)

---

## 1. System Design Study Path — full post lists

Detailed links for every level. If you are new, complete [Start in 30 minutes](#new-here-start-in-30-minutes) first, then work through Levels 0 → 3 in order.

| Level | Focus | Time hint | Outcome |
|:-----:|-------|-----------|---------|
| **0** | Orientation & references | Week 0 | Know where to study and how interviews run |
| **1** | Fundamentals & small designs | Weeks 1–2 | Explain requirements, API, data model on simple problems |
| **2** | Distributed building blocks | Weeks 3–5 | Design cache, queues, feeds, crawlers with scale hooks |
| **3** | Large-scale products | Weeks 6+ | Twitter, Uber, schedulers, LLM-style systems |
| **4** | Technology guides (on demand) | As needed | Redis, Kafka, DBs, K8s when a design requires them |
| **5** | Specialized tracks (optional) | Role-specific | OS/middleware, embedded, hardware test & DFT |
{: .lp-level-table}

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

**Skim the diagram, then use the tables** — you do not need to read every post. Each design article includes **architecture PNGs** at the top; open a [tech guide]({{ site.baseurl }}/2025/11/29/technology-list-quick-reference/) only when a design names a tool you do not know.

<figure class="diagram-figure">
  <img src="{{ '/assets/diagrams/c2e6caca6c0f8bc2.png' | relative_url }}" alt="Blog content tracks: interview path, reference library, specialized" class="diagram-img" loading="lazy" />
</figure>

<figure class="diagram-figure">
  <img src="{{ '/assets/diagrams/c12b1fad2384752f.png' | relative_url }}" alt="Page sections map" class="diagram-img" loading="lazy" />
</figure>

<p class="diagram-caption">Top: three content tracks. Bottom: how sections on this page fit together.</p>

### Content categories

<div class="lp-bar-chart" aria-label="Post counts by category">
  <div class="lp-bar-row"><span class="lp-bar-label">Design problems</span><div class="lp-bar-track"><div class="lp-bar-fill" style="width:34%"></div></div><span class="lp-bar-count">58</span></div>
  <div class="lp-bar-row"><span class="lp-bar-label">Technology guides</span><div class="lp-bar-track"><div class="lp-bar-fill" style="width:29%"></div></div><span class="lp-bar-count">50</span></div>
  <div class="lp-bar-row"><span class="lp-bar-label">OS / embedded</span><div class="lp-bar-track"><div class="lp-bar-fill" style="width:18%"></div></div><span class="lp-bar-count">31</span></div>
  <div class="lp-bar-row"><span class="lp-bar-label">Foundations</span><div class="lp-bar-track"><div class="lp-bar-fill" style="width:13%"></div></div><span class="lp-bar-count">22</span></div>
  <div class="lp-bar-row"><span class="lp-bar-label">Product notes</span><div class="lp-bar-track"><div class="lp-bar-fill" style="width:6%"></div></div><span class="lp-bar-count">11</span></div>
</div>

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
