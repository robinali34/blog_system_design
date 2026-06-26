#!/usr/bin/env python3
"""Insert Architecture at a glance mermaid diagrams into system design posts."""

import re
from pathlib import Path

POSTS = Path(__file__).resolve().parent.parent / "_posts"

MARKER = "### Architecture at a glance"
CAPTION = '<p class="diagram-caption">High-level system diagram — read top to bottom or left to right.</p>'

HLD_HEADING = re.compile(
    r"^## (High-Level Design|High-Level Architecture|High‑level architecture|"
    r"High-level flow|Architecture overview|Architecture Overview|Architecture)\s*$",
    re.MULTILINE,
)

READING_TIP = re.compile(r'<div class="post-reading-tip"')

# slug fragment -> mermaid source (without fences)
DIAGRAMS: dict[str, str] = {
    "url-shortener": """
flowchart TB
  subgraph write [Create short URL]
    C1[Client] -->|POST /urls| LB[Load Balancer]
    LB --> WS[Shorten Service]
    WS --> CTR[Redis Counter]
    WS --> DBW[(DB Primary)]
  end
  subgraph read [Redirect — hot path]
    C2[Browser] -->|GET /code| CDN[CDN / Edge]
    CDN --> RR[Redirect Service]
    RR --> CACHE[(Redis Cache)]
    CACHE --> DBR[(DB Replicas)]
    RR -->|302 Location| C2
  end
""",
    "rate-limiter": """
flowchart LR
  C[Clients] --> GW[API Gateway / LB]
  GW -->|check limit| RL[Rate Limiter]
  RL --> R[(Redis Cluster)]
  GW -->|allowed| APP[App Services]
  GW -->|429| C
""",
    "news-feed": """
flowchart TB
  C[Clients] --> LB[Load Balancer]
  LB --> FS[Feed Service]
  FS --> CACHE[(Feed Cache)]
  FS --> FG[Feed Generator]
  FG --> GRAPH[(Social Graph DB)]
  FG --> POSTS[(Post Store)]
  PUB[Post Service] -->|new post| Q[Message Queue]
  Q --> FAN[Fan-out Workers]
  FAN --> CACHE
""",
    "social-media-feed": """
flowchart TB
  C[Clients] --> API[API Gateway]
  API --> TL[Timeline Service]
  TL --> HOT[(Hot Feed Cache)]
  TL --> COLD[(Precomputed Feeds)]
  W[Write Path] --> Q[Kafka]
  Q --> FAN[Fan-out Service]
  FAN --> COLD
""",
    "chat": """
flowchart LR
  C1[User A] --> WS[WebSocket Gateway]
  C2[User B] --> WS
  WS --> CHAT[Chat Service]
  CHAT --> PRES[(Presence Store)]
  CHAT --> MSG[(Message Store)]
  CHAT --> MQ[Pub/Sub or Kafka]
""",
    "web-crawler": """
flowchart TB
  SEED[Seed URLs] --> F[URL Frontier]
  F --> W1[Worker]
  F --> W2[Worker]
  W1 --> FETCH[Fetcher]
  FETCH --> PARSE[Parser]
  PARSE --> STORE[(Document Store)]
  PARSE --> F
""",
    "distributed-web-crawler": """
flowchart TB
  COORD[Coordinator] --> F[Distributed Frontier]
  F --> N1[Node 1..N]
  N1 --> DNS[DNS / Politeness]
  N1 --> S3[(Blob Storage)]
  N1 --> IDX[Indexer]
""",
    "pub-sub": """
flowchart LR
  P[Publishers] -->|publish| B[Broker Cluster]
  B --> T1[Topic A]
  B --> T2[Topic B]
  T1 --> S1[Subscriber Group]
  T2 --> S2[Subscriber Group]
""",
    "key-value-store": """
flowchart TB
  C[Clients] --> LB[Load Balancer]
  LB --> N1[KV Node]
  LB --> N2[KV Node]
  N1 --> R1[Replication]
  N2 --> R1
  N1 --> DISK[(Local SSTable / WAL)]
""",
    "blob-storage": """
flowchart TB
  C[Clients] --> API[Object API]
  API --> META[(Metadata DB)]
  API --> CHUNK[Chunk / Object Nodes]
  CHUNK --> DISK[(Disks / Erasure Coded)]
""",
    "file-storage-sync": """
flowchart LR
  C1[Client A] --> SYNC[Sync Service]
  C2[Client B] --> SYNC
  SYNC --> META[(File Metadata)]
  SYNC --> BLOB[(Block Storage)]
  SYNC --> NOTIF[Change Notifications]
""",
    "search-autocomplete": """
flowchart LR
  C[Clients] --> API[Query API]
  API --> TRIE[(Trie / FST Index)]
  API --> CACHE[(Hot Prefix Cache)]
  LOG[Search Logs] --> AGG[Aggregator]
  AGG --> TRIE
""",
    "leaderboard": """
flowchart LR
  G[Game Servers] --> ING[Score Ingest]
  ING --> ZSET[(Redis Sorted Set)]
  C[Clients] --> API[Leaderboard API]
  API --> ZSET
""",
    "auction": """
flowchart TB
  B[Bidders] --> API[Auction API]
  API --> AUC[Auction Engine]
  AUC --> BID[(Bid Store)]
  AUC --> WS[WebSocket Push]
  WS --> B
""",
    "hotel-reservation": """
flowchart LR
  U[Users] --> API[Booking API]
  API --> INV[Inventory Service]
  API --> PAY[Payment Service]
  INV --> DB[(Reservations DB)]
  INV --> LOCK[Distributed Locks]
""",
    "ticket": """
flowchart TB
  U[Users] --> API[API Gateway]
  API --> BOOK[Booking Service]
  BOOK --> SEAT[Seat Lock / Hold]
  SEAT --> DB[(Ticket DB)]
  BOOK --> PAY[Payment]
""",
    "ride-sharing": """
flowchart TB
  R[Rider App] --> API[API Gateway]
  D[Driver App] --> API
  API --> MATCH[Matching Service]
  API --> TRIP[Trip Service]
  MATCH --> GEO[(Geo Index)]
  TRIP --> LOC[Location Stream]
""",
    "youtube": """
flowchart LR
  U[Upload] --> ING[Ingest]
  ING --> TRANS[Transcoder Farm]
  TRANS --> CDN[CDN]
  V[Viewers] --> CDN
  META[(Metadata DB)] --> API[Video API]
""",
    "netflix": """
flowchart TB
  C[Clients] --> CDN[Open Connect CDN]
  CDN --> ORIGIN[Origin / Packager]
  API[Catalog API] --> REC[Recommendation]
  REC --> LOG[(Viewing Events)]
""",
    "facebook-live": """
flowchart LR
  B[Broadcaster] --> ING[Live Ingest]
  ING --> TRANS[Transcode]
  TRANS --> CDN[CDN]
  V[Viewers] --> CDN
  CHAT[Chat] --> RT[Real-time Channel]
""",
    "gaming": """
flowchart TB
  P[Players] --> GW[Game Gateway]
  GW --> MATCH[Matchmaking]
  GW --> WORLD[Game World Servers]
  MATCH --> Q[(Match Queue)]
  WORLD --> STATE[(Session State)]
""",
    "roblox": """
flowchart TB
  P[Players] --> CC[Client]
  CC --> GW[Game Gateway]
  GW --> SIM[Simulation Servers]
  GW --> ASSET[Asset CDN]
  SIM --> DATA[(Player Data Store)]
""",
    "matchmaking": """
flowchart LR
  P[Players] --> Q[Matchmaking Queue]
  Q --> MM[Matcher]
  MM --> RULE[(Skill / Latency Rules)]
  MM --> GS[Game Server Allocator]
""",
    "payment-scheduler": """
flowchart TB
  API[Payment API] --> SCHED[Scheduler Service]
  SCHED --> Q[Delayed Queue]
  Q --> WORK[Workers]
  WORK --> PAY[Payment Processor]
  SCHED --> DB[(Job State DB)]
""",
    "cdc": """
flowchart LR
  DB[(Primary DB)] --> LOG[Transaction Log]
  LOG --> CDC[CDC Connector]
  CDC --> K[Kafka]
  K --> DW[(Warehouse)]
  K --> CACHE[(Downstream Caches)]
""",
    "logging": """
flowchart LR
  APP[Services] --> AGENT[Log Agents]
  AGENT --> BUF[Kafka Buffer]
  BUF --> PROC[Stream Processors]
  PROC --> IDX[(Search Index)]
  PROC --> S3[(Cold Storage)]
""",
    "translation": """
flowchart TB
  C[Clients] --> API[Translation API]
  API --> ROUTE[Language Router]
  ROUTE --> MT[Machine Translation]
  ROUTE --> HUMAN[Human Post-edit Queue]
  MT --> CACHE[(Translation Cache)]
""",
    "proximity": """
flowchart LR
  C[Clients] --> API[Search API]
  API --> GEO[Geo Index]
  GEO --> SHARD[(Sharded Location DB)]
  API --> CACHE[(Query Cache)]
""",
    "price-tracker": """
flowchart TB
  SCRAPE[Scrapers] --> Q[Queue]
  Q --> PROC[Price Processor]
  PROC --> DB[(Price History)]
  PROC --> ALERT[Alert Service]
  U[Users] --> API[Tracker API]
  API --> DB
""",
    "top-k": """
flowchart LR
  EVENTS[Event Stream] --> AGG[Aggregator Nodes]
  AGG --> SKETCH[(Count-Min Sketch)]
  AGG --> HEAP[Local Top-K]
  HEAP --> MERGE[Merge Service]
  Q[Queries] --> MERGE
""",
    "like-unlike": """
flowchart LR
  C[Clients] --> API[Like API]
  API --> CTR[Counter Service]
  CTR --> CACHE[(Redis Counters)]
  CTR --> DB[(Like Table)]
  API --> FAN[Fan-out Events]
""",
    "todo-collaboration": """
flowchart TB
  C[Clients] --> API[API]
  API --> OT[OT / CRDT Engine]
  OT --> DOC[(Document Store)]
  API --> WS[WebSocket Sync]
  WS --> C
""",
    "job-scheduler": """
flowchart TB
  API[Scheduler API] --> MASTER[Scheduler Master]
  MASTER --> META[(Job Metadata)]
  MASTER --> W1[Worker Pool]
  W1 --> EXEC[Executors]
  EXEC --> RETRY[Retry / DLQ]
""",
    "configuration": """
flowchart LR
  C[Clients] --> API[Config API]
  API --> LRU[LRU Cache Layer]
  LRU --> DB[(Config Store)]
  ADMIN[Admin] -->|push| API
""",
    "chess": """
flowchart TB
  P[Players] --> API[Game API]
  API --> ENGINE[Game Engine]
  ENGINE --> STATE[(Game State + History)]
  ENGINE --> ELO[ELO Rating Service]
""",
    "instagram": """
flowchart TB
  C[Clients] --> API[API Gateway]
  API --> MEDIA[Media Service]
  API --> FEED[Feed Service]
  MEDIA --> S3[(Object Storage)]
  FEED --> GRAPH[(Social Graph)]
""",
    "distributed-job-scheduler": """
flowchart TB
  API[API] --> SCH[Scheduler Cluster]
  SCH --> ZK[(Coordination / Locks)]
  SCH --> WORK[Worker Fleet]
  WORK --> Q[(Task Queue)]
""",
    "glass": """
flowchart TB
  GL[Smart Glass] --> EDGE[On-device Pipeline]
  EDGE --> CLOUD[Cloud Services]
  CLOUD --> ASR[Speech / Vision]
  CLOUD --> STORE[(Memory Store)]
""",
    "jni": """
flowchart TB
  JAVA[Java / Framework] --> JNI[JNI Bridge]
  JNI --> NATIVE[Native Libraries]
  NATIVE --> HAL[Drivers / HAL]
""",
    "os-framework": """
flowchart TB
  APP[Applications] --> FW[OS Framework]
  FW --> SVC[System Services]
  SVC --> NATIVE[Native Layer]
  NATIVE --> KERNEL[Kernel / Drivers]
""",
    "ndk": """
flowchart LR
  APP[App] --> JNI[JNI]
  JNI --> SO1[libA.so]
  JNI --> SO2[libB.so]
  MERGE[Linker] --> SO1
  MERGE --> SO2
""",
    "embedded": """
flowchart LR
  DEV[Device] --> FW[Embedded Firmware]
  FW --> BUF[Event Buffer]
  BUF --> SYNC[Sync Agent]
  SYNC --> CLOUD[(Cloud Ingest)]
""",
    "local-lld": """
flowchart TB
  APP[Application] --> COMP[Core Component]
  COMP --> POOL[Worker / Resource Pool]
  POOL --> W1[Worker 1]
  POOL --> W2[Worker N]
  COMP --> STORE[(In-Memory Structure)]
""",
    "oop-system": """
flowchart TB
  UI[Client / UI] --> CTRL[Controller]
  CTRL --> SVC[Domain Services]
  SVC --> REPO[(Data Store)]
  SVC --> RULE[Business Rules]
""",
    "twitter": """
flowchart LR
  C[Clients] --> GW[API Gateway]
  GW --> TWEET[Tweet Service]
  GW --> TL[Timeline Service]
  TWEET --> FAN[Fan-out]
  FAN --> CACHE[(Timeline Cache)]
""",
    "github": """
flowchart TB
  DEV[Developers] --> API[Git / API]
  API --> GIT[Git Storage]
  API --> PR[PR / Review Service]
  API --> CI[CI Webhooks]
  GIT --> OBJ[(Object Storage)]
""",
    "chatgpt": """
flowchart TB
  C[Clients] --> GW[Gateway]
  GW --> ROUTE[Model Router]
  ROUTE --> GPU[GPU Inference Pool]
  ROUTE --> CACHE[(Prompt / KV Cache)]
  GW --> SAFE[Safety Filters]
""",
    "notification": """
flowchart LR
  APP[Services] --> N[Notification Service]
  N --> Q[Queue]
  Q --> PUSH[Push Providers]
  Q --> EMAIL[Email / SMS]
  N --> PREF[(User Preferences)]
""",
    "metrics": """
flowchart LR
  SVC[Services] --> AGENT[Agents]
  AGENT --> TS[(Time-series DB)]
  AGENT --> K[Kafka]
  K --> DASH[Dashboards / Alerts]
""",
    "api-gateway": """
flowchart TB
  C[Clients] --> REST[REST]
  C --> WS[WebSocket]
  C --> GRPC[gRPC]
  REST --> GW[API Gateway]
  WS --> GW
  GRPC --> GW
  GW --> SVC[Backend Services]
""",
    "robinhood": """
flowchart TB
  C[Clients] --> GW[API Gateway]
  GW --> ORD[Order Service]
  ORD --> MATCH[Matching Engine]
  ORD --> RISK[Risk Checks]
  MATCH --> LEDGER[(Trade Ledger)]
""",
    "generic": """
flowchart TB
  C[Clients] --> LB[Load Balancer]
  LB --> API[API / Service Layer]
  API --> CACHE[(Cache)]
  API --> DB[(Database)]
  API --> Q[Async Queue]
  Q --> WORK[Background Workers]
""",
}

# Order matters: more specific patterns first
RULES: list[tuple[str, str]] = [
    (r"design-url-shortener|system-design-url-shortener", "url-shortener"),
    (r"rate-limiter", "rate-limiter"),
    (r"social-media-feed-twitter|system-design-twitter", "twitter"),
    (r"design-news-feed|social-media-feed-local", "news-feed"),
    (r"design-chat-system|simple-chat|system-design-chat-service", "chat"),
    (r"distributed-web-crawler", "distributed-web-crawler"),
    (r"web-crawler", "web-crawler"),
    (r"pub-sub", "pub-sub"),
    (r"key-value-store", "key-value-store"),
    (r"blob-storage|like-s3", "blob-storage"),
    (r"file-storage-sync", "file-storage-sync"),
    (r"search-autocomplete", "search-autocomplete"),
    (r"leaderboard", "leaderboard"),
    (r"auction", "auction"),
    (r"hotel-reservation", "hotel-reservation"),
    (r"ticketmaster|ticket-booking", "ticket"),
    (r"ride-sharing|uber", "ride-sharing"),
    (r"design-youtube|system-design-youtube", "youtube"),
    (r"design-netflix", "netflix"),
    (r"facebook-live", "facebook-live"),
    (r"roblox-studio|design-roblox", "roblox"),
    (r"matchmaking|gaming-platform", "matchmaking"),
    (r"in-memory-gaming", "gaming"),
    (r"delayed-payment", "payment-scheduler"),
    (r"change-data-capture|cdc", "cdc"),
    (r"distributed-logging|metrics-logging", "logging"),
    (r"global-translation", "translation"),
    (r"proximity-service|yelp", "proximity"),
    (r"price-drop|camelcamelcamel|price-tracker", "price-tracker"),
    (r"top-k-heavy", "top-k"),
    (r"like-unlike", "like-unlike"),
    (r"todo-list.*collaboration", "todo-collaboration"),
    (r"distributed-job-scheduler", "distributed-job-scheduler"),
    (r"configuration-service", "configuration"),
    (r"chess-game", "chess"),
    (r"design-instagram", "instagram"),
    (r"smart-glass|design-glass|meta-glass", "glass"),
    (r"jni-bridge", "jni"),
    (r"local-os-framework|os-framework", "os-framework"),
    (r"ndk-merge", "ndk"),
    (r"embedded-report|embedded-local|client-side-embedded|quickset", "embedded"),
    (r"thread-pool|connection-pool|producer-consumer|circular-buffer|memory-allocator|local-logger|task-scheduler-single|file-system-in-memory|resource-loader", "local-lld"),
    (r"parking-lot|library-management|atm-banking|online-shopping|text-editor", "oop-system"),
    (r"system-design-github", "github"),
    (r"system-design-chatgpt|chatgpt", "chatgpt"),
    (r"notification-service", "notification"),
    (r"metrics-logging", "metrics"),
    (r"client-api-gateway", "api-gateway"),
    (r"robinhood", "robinhood"),
    (r"design-a-|design-an-|system-design-", "generic"),
]


def pick_diagram(filename: str) -> str:
    name = filename.lower()
    for pattern, key in RULES:
        if re.search(pattern, name):
            return DIAGRAMS[key].strip()
    return DIAGRAMS["generic"].strip()


def mermaid_block(source: str) -> str:
    return f"```mermaid\n{source}\n```\n\n{CAPTION}\n\n"


def reading_tip_block() -> str:
    return (
        '<div class="post-reading-tip" markdown="1">\n\n'
        "**How to read this post:** Skim the **architecture diagram** under High-Level Design first, "
        "then walk through requirements → API → deep dives. Diagrams render as interactive visuals in the browser.\n\n"
        "</div>\n\n"
    )


def insert_reading_tip(content: str) -> str:
    if READING_TIP.search(content):
        return content
    # After introduction section: before ## Problem Statement or ## Table of Contents end
    for anchor in ("## Problem Statement", "## Requirements", "## Table of Contents"):
        idx = content.find(anchor)
        if idx != -1:
            return content[:idx] + reading_tip_block() + content[idx:]
    # Fallback: after first ##
    m = re.search(r"^## ", content, re.MULTILINE)
    if m:
        return content[: m.start()] + reading_tip_block() + content[m.start() :]
    return content


def insert_diagram(content: str, diagram: str) -> str:
    if MARKER in content:
        return content
    block = f"\n{MARKER}\n\n{mermaid_block(diagram)}"
    m = HLD_HEADING.search(content)
    if m:
        insert_at = m.end()
        return content[:insert_at] + block + content[insert_at:]
    # No HLD: insert before Summary or Deep Dive
    for anchor in ("## Deep Dive", "## Deep Dives", "## Summary", "## Final"):
        idx = content.find(anchor)
        if idx != -1:
            section = f"\n## High-Level Design\n{block}"
            return content[:idx] + section + content[idx:]
    return content + f"\n## High-Level Design\n{block}"


def process_file(path: Path, dry_run: bool = False) -> bool:
    name = path.name
    if not re.search(r"design-|system-design-", name, re.I):
        return False
    if re.search(
        r"questions|references|learning-path-index|trade-offs|common-domain|"
        r"common-non-distributed|common-technologies|leetcode-practice|"
        r"prep-todo|prep-guide|drill|breakdown|vs-product|scenarios|"
        r"in-domain-design|specswe|interview-framework|interview-guide|"
        r"os-frameworks-system-design\.md|os-frameworks-design-interview|"
        r"os-frameworks-domain|distributed-system-design-ecosystem|"
        r"overview-cloud|overview-embedded|android-os-design-overview|"
        r"hardware-design-for-testing",
        name,
        re.I,
    ):
        return False
    content = path.read_text(encoding="utf-8")
    original = content
    diagram = pick_diagram(name)
    content = insert_reading_tip(content)
    content = insert_diagram(content, diagram)
    if content == original:
        return False
    if not dry_run:
        path.write_text(content, encoding="utf-8")
    return True


def main() -> None:
    updated = 0
    for path in sorted(POSTS.glob("*.md")):
        if process_file(path):
            updated += 1
            print(f"updated: {path.name}")
    print(f"\nDone. Updated {updated} posts.")


if __name__ == "__main__":
    main()
