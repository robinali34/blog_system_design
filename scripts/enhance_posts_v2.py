#!/usr/bin/env python3
"""Add key-flow sequence diagrams to design posts and Mermaid to tech guides."""

import re
import sys
from pathlib import Path

POSTS = Path(__file__).resolve().parent.parent / "_posts"

# Import archetype rules from sibling script
sys.path.insert(0, str(Path(__file__).parent))
from enhance_design_posts import RULES, pick_diagram  # noqa: E402

FLOW_MARKER = "### Key flows"
TECH_MARKER = "### Architecture at a glance"
TECH_READING_TIP = '<div class="post-reading-tip" markdown="1">'

CAPTION_FLOW = '<p class="diagram-caption">Typical request/data flow — use in interviews to explain the happy path.</p>'
CAPTION_TECH = '<p class="diagram-caption">Visual overview — expand optional ASCII detail below if present.</p>'

DESIGN_EXCLUDE = re.compile(
    r"questions|references|learning-path-index|trade-offs|common-domain|"
    r"common-non-distributed|common-technologies|leetcode-practice|"
    r"prep-todo|prep-guide|drill|breakdown|vs-product|scenarios|"
    r"in-domain-design|specswe|interview-framework|interview-guide|"
    r"os-frameworks-system-design\.md|os-frameworks-design-interview|"
    r"os-frameworks-domain|distributed-system-design-ecosystem|"
    r"overview-cloud|overview-embedded|android-os-design-overview",
    re.I,
)

ARCH_HEADING = re.compile(
    r"^## Architecture\s*$|^### High-Level Architecture\s*$",
    re.MULTILINE,
)

BOX = re.compile(r"[┌└│▼├─┤┬┴]")

# sequence / extra flow diagrams per archetype
FLOW_DIAGRAMS: dict[str, str] = {
    "url-shortener": """
sequenceDiagram
  participant C as Client
  participant S as API
  participant DB as Database
  C->>S: POST /urls
  S->>DB: store mapping
  DB-->>S: OK
  S-->>C: short_url
  C->>S: GET /code
  S->>DB: lookup
  DB-->>S: long_url
  S-->>C: 302 redirect
""",
    "rate-limiter": """
sequenceDiagram
  participant C as Client
  participant GW as Gateway
  participant RL as Rate Limiter
  participant R as Redis
  C->>GW: HTTP request
  GW->>RL: check limit
  RL->>R: atomic update
  R-->>RL: allowed/denied
  alt allowed
    GW-->>C: 200
  else denied
    GW-->>C: 429
  end
""",
    "news-feed": """
sequenceDiagram
  participant U as User
  participant API as Feed API
  participant C as Feed Cache
  participant DB as Post Store
  U->>API: GET /feed
  API->>C: read cached feed
  alt cache hit
    C-->>API: post ids
  else miss
    API->>DB: generate feed
    DB-->>API: posts
    API->>C: cache result
  end
  API-->>U: ranked feed
""",
    "social-media-feed": """
sequenceDiagram
  participant U as User
  participant TL as Timeline
  participant C as Cache
  U->>TL: load home timeline
  TL->>C: fetch precomputed feed
  C-->>TL: post ids
  TL-->>U: timeline JSON
""",
    "chat": """
sequenceDiagram
  participant A as User A
  participant GW as Gateway
  participant S as Chat Service
  participant B as User B
  A->>GW: send message
  GW->>S: persist + route
  S->>B: push via WebSocket
  S-->>A: ack delivered
""",
    "web-crawler": """
sequenceDiagram
  participant F as Frontier
  participant W as Worker
  participant WQ as Web
  participant S as Storage
  F->>W: next URL
  W->>WQ: HTTP GET
  WQ-->>W: HTML
  W->>S: store page
  W->>F: enqueue links
""",
    "pub-sub": """
sequenceDiagram
  participant P as Publisher
  participant B as Broker
  participant S as Subscriber
  P->>B: publish(topic, msg)
  B->>S: deliver
  S-->>B: ack
""",
    "ride-sharing": """
sequenceDiagram
  participant R as Rider
  participant API as API
  participant M as Matcher
  participant D as Driver
  R->>API: request ride
  API->>M: find nearby drivers
  M->>D: dispatch offer
  D-->>M: accept
  M-->>API: matched trip
  API-->>R: driver en route
""",
    "youtube": """
sequenceDiagram
  participant U as Uploader
  participant ING as Ingest
  participant TR as Transcoder
  participant CDN as CDN
  participant V as Viewer
  U->>ING: upload video
  ING->>TR: transcode job
  TR->>CDN: publish renditions
  V->>CDN: GET manifest
  CDN-->>V: stream chunks
""",
    "kafka-tech": """
sequenceDiagram
  participant P as Producer
  participant B as Broker
  participant C as Consumer Group
  P->>B: append records
  B-->>P: ack
  C->>B: poll/fetch
  B-->>C: batch
  C->>C: commit offset
""",
    "generic": """
sequenceDiagram
  participant C as Client
  participant API as Service
  participant DB as Data Store
  C->>API: request
  API->>DB: read / write
  DB-->>API: result
  API-->>C: response
""",
}

# Extra comparison diagrams for specific topics
EXTRA_DIAGRAMS: dict[str, str] = {
    "news-feed": """
flowchart LR
  subgraph push [Push fan-out on write]
    NP[New post] --> FAN[Write to follower feeds]
  end
  subgraph pull [Pull on read]
    RD[Read feed] --> MERGE[Merge followed users]
  end
  subgraph hybrid [Hybrid]
    HOT[Celebrity: pull] --> MERGE
    FAN --> NORMAL[Regular users: push]
  end
""",
    "rate-limiter": """
flowchart TB
  FW[Fixed window] --> SW[Sliding window]
  SW --> TB[Token bucket]
  TB --> REC[Recommended for APIs]
""",
    "web-crawler": """
flowchart TB
  URL[URL] --> ROBOT{robots.txt OK?}
  ROBOT -->|yes| FETCH[Fetch]
  ROBOT -->|no| SKIP[Skip]
  FETCH --> PARSE[Parse links]
  PARSE --> DEDUP{Dedup?}
  DEDUP -->|new| FRONT[Frontier]
""",
}

TECH_DIAGRAMS: dict[str, str] = {
    "redis": """
flowchart LR
  APP[Applications] -->|GET/SET| R[Redis]
  R --> MEM[(In-memory structures)]
  R -.->|optional| AOF[(AOF / RDB)]
""",
    "kafka": """
flowchart LR
  P[Producers] --> B[Broker cluster]
  B --> T1[Topic partitions]
  T1 --> CG[Consumer groups]
""",
    "postgresql|mysql": """
flowchart TB
  APP[Apps] --> POOL[Connection pool]
  POOL --> PRI[(Primary)]
  PRI --> REP[(Read replicas)]
""",
    "mongodb": """
flowchart TB
  APP[Drivers] --> ROUTER[mongos router]
  ROUTER --> S1[Shard 1]
  ROUTER --> S2[Shard 2]
  CFG[(Config servers)]
""",
    "dynamodb": """
flowchart TB
  APP[SDK] --> API[DynamoDB API]
  API --> PART[Partitions]
  PART --> S3[(SSD storage)]
  API --> GSI[Global secondary indexes]
""",
    "cassandra": """
flowchart TB
  C[Clients] --> N1[Coordinator node]
  N1 --> R1[Replica ring]
  R1 --> N2[Peer nodes]
""",
    "elasticsearch": """
flowchart LR
  C[Clients] --> COORD[Coordinating node]
  COORD --> SH1[Shard]
  COORD --> SH2[Shard]
  SH1 --> REP[Replicas]
""",
    "kubernetes": """
flowchart TB
  KUBECTL[kubectl] --> API[API Server]
  API --> SCH[Scheduler]
  API --> CM[Controller Manager]
  SCH --> NODE[Worker nodes]
  NODE --> POD[Pods]
""",
    "docker": """
flowchart LR
  DF[Dockerfile] --> BUILD[docker build]
  BUILD --> IMG[Image]
  IMG --> REG[Registry]
  IMG --> RUN[Container runtime]
""",
    "terraform": """
flowchart TB
  DEV[.tf files] --> TF[Terraform Core]
  TF --> PLAN[plan]
  PLAN --> APPLY[apply]
  APPLY --> AWS[Cloud APIs]
  TF --> STATE[(State file)]
""",
    "nginx": """
flowchart LR
  C[Clients] --> NGX[NGINX]
  NGX --> U1[Upstream 1]
  NGX --> U2[Upstream 2]
  NGX --> CACHE[(Cache zone)]
""",
    "load-balancer": """
flowchart TB
  C[Clients] --> LB[Load Balancer]
  LB --> H[Health checks]
  LB --> S1[Server 1]
  LB --> S2[Server 2]
""",
    "rabbitmq": """
flowchart LR
  P[Publisher] --> EX[Exchange]
  EX --> Q1[Queue A]
  EX --> Q2[Queue B]
  Q1 --> CON[Consumers]
""",
    "grpc": """
flowchart LR
  C[gRPC Client] --> CH[HTTP/2 Channel]
  CH --> S[gRPC Server]
  S --> SVC[Service impl]
""",
    "graphql": """
flowchart TB
  C[Client] --> GQL[GraphQL server]
  GQL --> R1[Resolver: users]
  GQL --> R2[Resolver: posts]
  R1 --> DB[(Data sources)]
""",
    "prometheus": """
flowchart LR
  TGT[Targets] --> SCRAPE[Prometheus scrape]
  SCRAPE --> TSDB[(TSDB)]
  TSDB --> GRAF[Grafana / alerts]
""",
    "cdn": """
flowchart LR
  U[Users] --> EDGE[Edge PoP]
  EDGE -->|miss| ORIGIN[Origin]
  EDGE -->|hit| U
""",
    "etcd": """
flowchart TB
  APP[Cluster members] --> ETCD[etcd cluster]
  ETCD --> RAFT[Raft consensus]
  RAFT --> LOG[(Replicated log)]
""",
    "consul": """
flowchart LR
  SVC[Services] --> AGENT[Consul agent]
  AGENT --> SERF[Gossip / health]
  AGENT --> KV[(KV store)]
""",
    "spark": """
flowchart TB
  DRV[Driver] --> CL[Cluster manager]
  CL --> EX[Executors]
  EX --> DATA[(Partitions / HDFS)]
""",
    "flink": """
flowchart LR
  SRC[Sources] --> OP[Operators]
  OP --> CHK[Checkpoints]
  OP --> SINK[Sinks]
""",
    "s3": """
flowchart TB
  C[Clients] --> API[S3 API]
  API --> META[(Metadata)]
  API --> OBJ[(Object storage)]
""",
    "memcached": """
flowchart LR
  APP[Apps] --> MC[Memcached pool]
  MC --> N1[Node]
  MC --> N2[Node]
""",
    "websocket": """
flowchart LR
  B[Browser] --> WS[WebSocket server]
  WS --> HUB[Connection hub]
  HUB --> SVC[Backend services]
""",
    "generic-tech": """
flowchart TB
  USER[Users / apps] --> SVC[Service layer]
  SVC --> STORE[(Storage)]
  SVC --> CACHE[(Cache)]
""",
}

TECH_RULES: list[tuple[str, str]] = [
    (r"redis", "redis"),
    (r"kafka", "kafka"),
    (r"postgresql|mysql", "postgresql|mysql"),
    (r"mongodb", "mongodb"),
    (r"dynamodb", "dynamodb"),
    (r"cassandra", "cassandra"),
    (r"elasticsearch", "elasticsearch"),
    (r"kubernetes", "kubernetes"),
    (r"docker", "docker"),
    (r"terraform", "terraform"),
    (r"nginx", "nginx"),
    (r"load-balancer", "load-balancer"),
    (r"rabbitmq", "rabbitmq"),
    (r"grpc", "grpc"),
    (r"graphql", "graphql"),
    (r"prometheus", "prometheus"),
    (r"cdn-content", "cdn"),
    (r"etcd", "etcd"),
    (r"consul", "consul"),
    (r"spark", "spark"),
    (r"flink", "flink"),
    (r"amazon-s3|s3-storage", "s3"),
    (r"memcached", "memcached"),
    (r"websocket", "websocket"),
    (r"guide|comprehensive", "generic-tech"),
]


def pick_flow_key(filename: str) -> str:
    name = filename.lower()
    for pattern, key in RULES:
        if re.search(pattern, name):
            return key
    return "generic"


def pick_flow_diagram(filename: str) -> str:
    key = pick_flow_key(filename)
    return FLOW_DIAGRAMS.get(key, FLOW_DIAGRAMS["generic"]).strip()


def pick_extra_diagram(filename: str) -> str | None:
    key = pick_flow_key(filename)
    return EXTRA_DIAGRAMS.get(key)


def pick_tech_diagram(filename: str) -> str:
    name = filename.lower()
    for pattern, key in TECH_RULES:
        if re.search(pattern, name):
            return TECH_DIAGRAMS[key].strip()
    return TECH_DIAGRAMS["generic-tech"].strip()


def mermaid(source: str) -> str:
    return f"```mermaid\n{source.strip()}\n```\n\n"


def tech_reading_tip() -> str:
    return (
        '<div class="post-reading-tip" markdown="1">\n\n'
        "**How to read this guide:** Start with the **architecture diagram**, then use sections as "
        "reference during system design interviews when this technology appears in a design.\n\n"
        "</div>\n\n"
    )


def wrap_ascii_fence(match: re.Match) -> str:
    body = match.group("body")
    if not BOX.search(body):
        return match.group(0)
    if "<details" in body:
        return match.group(0)
    return (
        '<details class="lp-collapse" markdown="1">\n'
        "<summary>Expanded ASCII diagram (optional detail)</summary>\n\n"
        f"```\n{body}```\n\n"
        "</details>\n\n"
    )


def collapse_ascii_after_marker(content: str, marker: str) -> str:
    idx = content.find(marker)
    if idx == -1:
        return content
    return _collapse_next_ascii_fence(content, idx)


def collapse_ascii_after_heading(content: str, heading: str) -> str:
    idx = content.find(heading)
    if idx == -1:
        return content
    return _collapse_next_ascii_fence(content, idx)


def _collapse_next_ascii_fence(content: str, start_idx: int) -> str:
    tail = content[start_idx:]
    pat = re.compile(r"```\n(?P<body>.*?)```", re.DOTALL)
    for m in pat.finditer(tail):
        body = m.group("body")
        if "flowchart" in body or "sequenceDiagram" in body or "graph " in body:
            continue
        if not BOX.search(body):
            continue
        if "<details" in body:
            continue
        start = start_idx + m.start()
        end = start_idx + m.end()
        wrapped = wrap_ascii_fence(m)
        return content[:start] + wrapped + content[end:]
    return content


def add_design_flows(path: Path) -> bool:
    name = path.name
    if not re.search(r"design-|system-design-", name, re.I):
        return False
    if DESIGN_EXCLUDE.search(name):
        return False
    text = path.read_text(encoding="utf-8")
    if FLOW_MARKER in text or "sequenceDiagram" in text:
        return False
    if "### Architecture at a glance" not in text:
        return False
    flow = pick_flow_diagram(name)
    extra = pick_extra_diagram(name)
    block = f"\n{FLOW_MARKER}\n\n{mermaid(flow)}{CAPTION_FLOW}\n"
    if extra:
        block += f"### Design patterns\n\n{mermaid(extra)}{CAPTION_FLOW}\n"
    # Insert after first diagram-caption following Architecture at a glance
    pat = re.compile(
        r"(### Architecture at a glance\n\n```mermaid.*?```\n\n"
        r'<p class="diagram-caption">.*?</p>\n*)',
        re.DOTALL,
    )
    m = pat.search(text)
    if not m:
        return False
    new = text[: m.end()] + block + text[m.end() :]
    path.write_text(new, encoding="utf-8")
    return True


def add_tech_guide_enhancements(path: Path) -> bool:
    name = path.name.lower()
    if not re.search(r"guide|comprehensive", name):
        return False
    if re.search(r"learning-path|leetcode|interview-guide|study-guide|prep", name):
        return False
    text = path.read_text(encoding="utf-8")
    changed = False

    if TECH_READING_TIP not in text:
        for anchor in ("## What is", "## Introduction", "## Overview", "## Architecture"):
            idx = text.find(anchor)
            if idx != -1 and anchor != "## Architecture":
                text = text[:idx] + tech_reading_tip() + text[idx:]
                changed = True
                break

    if TECH_MARKER not in text:
        m = ARCH_HEADING.search(text)
        if m:
            diagram = pick_tech_diagram(name)
            block = (
                f"\n{TECH_MARKER}\n\n{mermaid(diagram)}{CAPTION_TECH}\n"
            )
            text = text[: m.end()] + block + text[m.end() :]
            changed = True

    if TECH_MARKER in text:
        new = collapse_ascii_after_marker(text, TECH_MARKER)
        if new != text:
            text = new
            changed = True
        # Also collapse ASCII under ### High-Level Architecture
        new2 = collapse_ascii_after_heading(text, "### High-Level Architecture")
        if new2 != text:
            text = new2
            changed = True

    if changed:
        path.write_text(text, encoding="utf-8")
    return changed


def main() -> None:
    design_n = tech_n = 0
    for path in sorted(POSTS.glob("*.md")):
        if add_design_flows(path):
            design_n += 1
            print(f"flows: {path.name}")
        if add_tech_guide_enhancements(path):
            tech_n += 1
            print(f"tech:  {path.name}")
    print(f"\nAdded flows to {design_n} design posts.")
    print(f"Enhanced {tech_n} technology guides.")


if __name__ == "__main__":
    main()
