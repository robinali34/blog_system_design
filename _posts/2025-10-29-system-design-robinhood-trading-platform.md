---
layout: post
title: "System Design: Robinhood-Style Retail Trading Platform"
date: 2025-10-29 20:00:00 -0700
categories: system-design architecture fintech
permalink: /2025/10/29/system-design-robinhood/
tags: [system-design, trading, market-data, orders, risk, compliance, reliability]
---

# System Design: Robinhood-Style Retail Trading Platform

Design a retail brokerage for equities/options/crypto with mobile clients, real‑time quotes, order placement, portfolio, funding, and regulatory/compliance controls.

## Product scope and requirements

Functional
- Accounts: KYC, funding (ACH/cards), portfolios, balances, tax lots.
- Market data: top‑of‑book quotes, candles, depth (level 2 optional), news.
- Trading: market/limit/stop, GTC/day, options (calls/puts), crypto spot.
- Risk/compliance: PATTERN‑DAY‑TRADER checks, buying power, margin, Reg‑T/Reg‑NMS, surveillance.
- Notifications: fills, corporate actions, margin calls, price alerts.

Non‑functional
- Latency: quote < 300 ms P95 to device; order ACK < 200 ms; fill notification < 1 s.
- Availability: 99.9%+ core during market hours; graceful degradation off‑hours.
- Consistency: strong within order state and balances; eventual for analytics/feeds.
- Throughput: 100k+ concurrent users; 10k+ orders/min bursts on events.

Out of scope
- Matching engine (we route to venues/MMs/crypto exchanges).

## High‑level architecture

```
Mobile/Web
   │
API Gateway (AuthZ, rate limit, routing)
   │
   ├── Market-Data API  ──► Quote Cache (Redis/Mem) ──► Market Data Ingest (Kafka) ─► Normalizers
   ├── Trade API        ──► OMS (Orders/Risk) ───────► Venue Routers ──► Exchanges/MMs
   ├── Portfolio API    ──► Positions, Cost Basis, PnL (Postgres + CQRS cache)
   ├── Accounts API     ──► KYC/Funding (ACH/Card), Ledgers (Double‑entry)
   └── Notify API       ──► Push/Webhooks/Email/SMS

Core Streams: Kafka topics (quotes, trades, fills, balances, audit)
State Stores: Postgres (ACID), Redis (hot), S3 (history), ClickHouse (analytics)
Secrets: KMS/HSM; Feature Flags: Consul
```

## Market data ingestion and delivery

- Feeds: SIP/OPRA/Direct, crypto exchange websockets.
- Normalization: parse → validate → enrich (symbol map) → publish to Kafka `quotes.v1`, `trades.v1`.
- Caching: in‑memory fanout service maintains latest NBBO/top‑of‑book per symbol; updates Redis for API fallback.
- Delivery: clients subscribe via server‑side websockets or poll; use delta compression and backpressure.

Latency path (quote)
1) Feed → Normalizer (<10 ms parse)
2) Kafka → Fanout (p99 < 50 ms)
3) Fanout → Client WS (edge POPs/CDN websockets where applicable)

## Order flow and OMS (Order Management System)

States: New → Accepted → Routed → PartiallyFilled/Filled → Canceled/Rejected

Workflow
1) Pre‑trade checks: auth, account status, symbol eligibility, market hours.
2) Buying power: compute in real‑time (cash/margin, option requirements, crypto balances).
3) Risk rules: PDT, max order size/notional, volatility guards, concentration limits.
4) Persistence: create Order row (Postgres) in a transaction with idempotency key.
5) Routing: choose venue/MM via smart‑router (fees, price improvement, liquidity).
6) Ack to client; async fills via venue FIX/WebSocket → Fill Handler → OMS.
7) Balance/position updates: double‑entry ledger; tax‑lot selection (HIFO/Specific ID).

Data model (simplified)
```text
orders(id, account_id, symbol, side, type, qty, limit_price, time_in_force, state, venue_id, created_at, ...) 
fills(id, order_id, venue, qty, price, ts)
positions(account_id, symbol, qty, cost_basis, updated_at)
ledger(id, account_id, delta_cash, delta_margin, reason, ref_id, ts)
```

Idempotency
- Client sends `Idempotency-Key` per order; OMS enforces uniqueness with unique index; safe retries.

## Risk and compliance

- Real‑time checks in OMS; slow/surveillance in async jobs.
- Margin engine: requirements per asset class; overnight vs. day.
- Pattern Day Trader: track intraday round trips; lock accounts exceeding thresholds.
- Reg‑NMS/Best‑ex: capture quotes at order time; venue decision audit trail.
- AML/Fraud: velocity, device fingerprinting, sanctions screening.

## Portfolio, PnL, and cost basis

- CQRS: write model in Postgres (positions/ledger), read model cached in Redis for fast portfolio loads.
- Tax lots: lot table with FIFO/HIFO; corporate actions processor adjusts lots (splits/dividends).
- PnL: intraday via mark‑to‑market (latest quote); end‑of‑day snapshots to S3 for statements.

## Accounts, funding, and ledgers

- KYC/AML onboarding; Plaid/ACH micro‑deposits or instant auth; card pushes for small amounts.
- Double‑entry ledger ensures debits=credits (cash, unsettled, margin interest, fees).

## Reliability and scale

- Backpressure: shed quote fanout for non‑subscribed symbols; rate‑limit order spam per account.
- Graceful degradation: if real‑time feed down, fall back to last quote + warning banner.
- Regional redundancy: active‑active read (market data); active‑passive for OMS (to avoid split‑brain).
- Replayable streams: Kafka with compaction/retention; rebuild read models from topics.

## Consistency model

- Strong consistency for orders/fills/balances within OMS transaction boundaries.
- Eventual consistency for derived views (portfolio charts, analytics).

## Security and privacy

- OAuth2/OIDC; device binding; WebAuthn for step‑up.
- Secrets in KMS/HSM; PII encryption at rest; PCI DSS for card data.
- Least privilege between services; audit logs immutable (WORM storage).

## APIs (examples)

```http
POST /v1/orders
{
  "symbol": "AAPL", "side": "buy", "type": "limit", "qty": 10, "limit_price": 180.00, "time_in_force": "day"
}

GET /v1/quotes?symbols=AAPL,TSLA
GET /v1/portfolio
GET /v1/orders/{id}
```

WebSocket events
```json
{ "type": "quote", "symbol": "AAPL", "bid": 179.95, "ask": 180.00, "ts": 1730330000 }
{ "type": "fill", "order_id": "...", "qty": 10, "price": 179.98, "ts": 1730330002 }
```

## Testing and observability

- Synthetic orders in sandbox; venue simulators; chaos testing during off‑hours.
- Tracing (OpenTelemetry) across gateway→OMS→router; SLOs for ACK latency and fill notification.
- Circuit breakers on venue connectors; auto‑failover to alternate venues.

## Common pitfalls and mitigations

- Quote storms: symbol throttling, coalescing, and per‑client subscription limits.
- Regulatory outages: venue‑specific halts; propagate limit‑up/limit‑down to UI.
- Clock skew: NTP tightly; use exchange timestamps for price/lot accounting where possible.
- Idempotency gaps: ensure dedupe at gateway and OMS levels.

## Interview drill‑downs

- How do you ensure best‑execution evidence? Capture NBBO snapshot and router decision.
- What if Kafka lags? Backpressure fanout, prioritize hot symbols, degrade analytics.
- How to avoid double fills on retry? Idempotent order keys and venue orderId mapping.
- How to compute buying power for options spreads? Margin engine with strategy recognition.

## Capacity & regulatory readiness

- Capacity: assume 1M DAU market hours, 100k peak concurrent; 20k TPS orders burst. Partition OMS by account id; pre‑allocate order ids; ensure venue connectors scale horizontally.
- Data retention: WORM storage for audit/Reg‑NMS artifacts; 7‑year retention for trade/ledger per jurisdiction.
- SLOs: Order ACK P95 < 200 ms; balance update P95 < 500 ms; quote fanout P95 < 150 ms.

## Consistency & correctness

- Strong consistency for orders/positions/ledger via single‑writer txns; eventual for portfolio charts.
- Idempotency and exactly‑once semantics on order create with constraint indexes; reconcile fills vs. venue daily.

## Failure drills

- Venue outage: auto‑reroute; if all venues fail, place orders into park queue and inform clients.
- Partial ledger failure: circuit‑break trading; reconcile and recover from Kafka with compensating entries.

## Evolution

- Start with equities cash accounts; add margin, options, and crypto with separate risk engines; move to multi‑region read replicas, with OMS in primary only.

## Detailed APIs

```http
POST /v1/orders { account_id, symbol, side, type, qty, limit_price?, tif } -> { id }
GET  /v1/orders/{id}
GET  /v1/quotes?symbols=AAPL,TSLA
```

## Data models (DDL sketch)

```sql
CREATE TABLE orders (
  id bigint PRIMARY KEY,
  account_id bigint,
  symbol text,
  side smallint,
  type smallint,
  qty numeric(18,4),
  limit_price numeric(18,4),
  tif smallint,
  state smallint,
  created_at timestamptz
);
```

## Failure drills

- OMS db failover → promote replica; halt routing; reconcile from Kafka; resume.
- Exchange reject storm → auto‑throttle; switch venues; client messaging.

## Test plan

- Simulated market opens; PDT rule edge cases; ledger reconciliation fuzzing; venue connector chaos tests.
