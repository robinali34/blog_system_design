---
layout: post
title: "Design a Delayed Payment Scheduler Service - System Design Interview"
date: 2025-11-29
categories: [System Design, Interview Example, Distributed Systems, Financial Systems, Scheduling, High-Throughput Systems]
excerpt: "A comprehensive guide to designing a delayed payment scheduler service that handles scheduled virtual currency transfers with durable timers, idempotent execution, account contention handling, and scalability to millions of pending jobs."
---

## Introduction

Designing a delayed payment scheduler service is a complex distributed systems problem that tests your ability to build reliable, correct financial systems. The service must schedule future payments, ensure they execute even after failures, handle money-movement workflows correctly, and scale to millions of pending jobs.

This post provides a detailed walkthrough of designing a delayed payment scheduler service, covering key architectural decisions, durable timer implementation, payment execution workflows, idempotency patterns, account contention handling, and observability. This is a common system design interview question that tests your understanding of distributed systems, financial systems, scheduling, and correctness guarantees.

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Requirements](#requirements)
   - [Functional Requirements](#functional-requirements)
   - [Non-Functional Requirements](#non-functional-requirements)
3. [Capacity Estimation](#capacity-estimation)
   - [Traffic Estimates](#traffic-estimates)
   - [Storage Estimates](#storage-estimates)
4. [Core Entities](#core-entities)
5. [API](#api)
6. [Data Flow](#data-flow)
7. [Database Design](#database-design)
   - [Schema Design](#schema-design)
   - [Database Sharding Strategy](#database-sharding-strategy)
8. [High-Level Design](#high-level-design)
9. [Deep Dive](#deep-dive)
   - [Component Design](#component-design)
   - [Durable Timers](#durable-timers)
   - [Payment Execution Workflow](#payment-execution-workflow)
   - [Idempotency](#idempotency)
   - [Account Contention Handling](#account-contention-handling)
   - [Scalability](#scalability)
   - [Observability](#observability)
   - [Failure Handling](#failure-handling)
   - [Trade-offs and Optimizations](#trade-offs-and-optimizations)
10. [What Interviewers Look For](#what-interviewers-look-for)
11. [Summary](#summary)

## Problem Statement

**Design a delayed payment scheduler service that:**

1. Allows users to schedule delayed payments of virtual currency (Robux)
2. Automatically transfers specified amount from one user to another after designated time period
3. Ensures payments execute even if system fails (durable timers)
4. Guarantees correctness (no duplicate transfers, no lost payments)
5. Handles contention on hot accounts (many payments to same account)
6. Scales to millions of pending scheduled payments
7. Provides observability and operability

**Scale Requirements:**
- 10M+ scheduled payments per day
- 1M+ pending payments at any time
- 100k+ payment executions per hour
- Support delays from seconds to months
- < 1 second accuracy for payment timing
- 99.99% reliability (no lost payments)

**Key Challenges:**
- Durable timers (payments must execute even after failures)
- Money-movement correctness (financial accuracy)
- Idempotent transfers (handle retries safely)
- Account contention (many concurrent transfers to same account)
- Scaling to millions of pending jobs
- Observability (monitoring, alerting, debugging)

## Requirements

### Functional Requirements

**Core Features:**
1. **Schedule Payment**: User schedules a payment with amount, from_account, to_account, and delay
2. **Cancel Payment**: User can cancel scheduled payment before execution
3. **Payment Execution**: System automatically executes payment at scheduled time
4. **Payment Status**: Users can check status of scheduled payments
5. **Payment History**: Users can view history of executed payments
6. **Idempotency**: Multiple execution attempts don't result in duplicate transfers

**Payment Rules:**
- Minimum delay: 1 second
- Maximum delay: 1 year
- Minimum amount: 1 Robux
- Maximum amount: 1M Robux (configurable per user)
- Source account must have sufficient balance at execution time
- Payment is atomic (all-or-nothing)

**Out of Scope:**
- Payment gateway integration (assume internal currency system)
- Fraud detection (assume trusted users)
- Payment disputes/refunds (separate system)
- Recurring payments (one-time scheduled payments only)

### Non-Functional Requirements

1. **Availability**: 99.99% uptime
2. **Reliability**: 
   - No lost payments (all scheduled payments execute)
   - No duplicate payments (idempotent execution)
   - At-least-once execution guarantee
3. **Performance**: 
   - Schedule payment: < 100ms (P95)
   - Payment execution: < 500ms (P95)
   - Status query: < 50ms (P95)
4. **Scalability**: Handle 10M+ scheduled payments/day, 1M+ pending payments
5. **Consistency**: 
   - Strong consistency for account balances
   - Eventual consistency acceptable for payment status (can be slightly stale)
6. **Accuracy**: Payment timing accuracy < 1 second
7. **Observability**: Comprehensive logging, metrics, and alerting

## Capacity Estimation

### Traffic Estimates

- **Scheduled Payments**: 10M per day = 116 payments/second average
- **Peak Scheduling**: 3x average = 350 payments/second
- **Payment Executions**: 10M per day = 116 executions/second average
- **Peak Executions**: 3x average = 350 executions/second
- **Status Queries**: 1M per day = 12 queries/second average
- **Cancel Requests**: 100k per day = 1.2 requests/second average

### Storage Estimates

**Scheduled Payments:**
- 1M pending payments at any time
- Average record size: 256 bytes (payment_id, from_account, to_account, amount, scheduled_time, status)
- Pending storage: 1M × 256 bytes = 256MB

**Payment History:**
- 10M payments/day × 365 = 3.65B payments/year
- Average record size: 512 bytes (includes execution details, timestamps)
- Annual storage: 3.65B × 512 bytes = 1.87TB/year

**Account Balances:**
- 100M accounts
- Average record size: 64 bytes (account_id, balance, updated_at)
- Total storage: 100M × 64 bytes = 6.4GB

**Total Storage**: ~2TB per year (mostly payment history)

## Core Entities

### ScheduledPayment
- **Attributes**: payment_id, from_account_id, to_account_id, amount, scheduled_time, status, created_at, executed_at, cancelled_at
- **Status**: PENDING, EXECUTING, COMPLETED, FAILED, CANCELLED
- **Relationships**: Links from_account to to_account

### PaymentExecution
- **Attributes**: execution_id, payment_id, status, executed_at, error_message, retry_count
- **Status**: PENDING, IN_PROGRESS, SUCCESS, FAILED
- **Purpose**: Track execution attempts for idempotency

### Account
- **Attributes**: account_id, balance, updated_at, version (for optimistic locking)
- **Relationships**: Can be source or destination of payments
- **Purpose**: Track account balances

### PaymentEvent
- **Attributes**: event_id, payment_id, event_type, event_data, timestamp
- **Event Types**: SCHEDULED, EXECUTING, COMPLETED, FAILED, CANCELLED
- **Purpose**: Audit trail and event sourcing

## API

### 1. Schedule Payment
```
POST /api/v1/payments/schedule
Headers:
  - Authorization: Bearer <token>
  - Idempotency-Key: <unique_key>
Body:
  - from_account_id: string
  - to_account_id: string
  - amount: integer (Robux)
  - delay_seconds: integer (delay in seconds)
  - description: string (optional)
Response:
  - payment_id: string
  - scheduled_time: timestamp
  - status: string (PENDING)
```

### 2. Cancel Payment
```
DELETE /api/v1/payments/{payment_id}/cancel
Headers:
  - Authorization: Bearer <token>
Response:
  - success: boolean
  - status: string (CANCELLED)
```

### 3. Get Payment Status
```
GET /api/v1/payments/{payment_id}
Headers:
  - Authorization: Bearer <token>
Response:
  - payment_id: string
  - from_account_id: string
  - to_account_id: string
  - amount: integer
  - scheduled_time: timestamp
  - status: string
  - executed_at: timestamp (if executed)
  - error_message: string (if failed)
```

### 4. List Payments
```
GET /api/v1/payments
Headers:
  - Authorization: Bearer <token>
Query Parameters:
  - account_id: string (filter by account)
  - status: string (filter by status)
  - limit: integer (default: 20, max: 100)
  - cursor: string (pagination)
Response:
  - payments: array of payment objects
  - next_cursor: string
```

### 5. Execute Payment (Internal)
```
POST /api/v1/internal/payments/{payment_id}/execute
Headers:
  - X-Internal-Auth: <internal_token>
Body:
  - execution_id: string (idempotency key)
Response:
  - success: boolean
  - execution_id: string
```

## Data Flow

### Schedule Payment Flow

```
1. Client → API Gateway
2. API Gateway → Auth Service (validate token)
3. API Gateway → Payment Scheduler Service
4. Payment Scheduler Service:
   a. Validate request (amount, accounts, delay)
   b. Check idempotency key (prevent duplicates)
   c. Calculate scheduled_time = now + delay
   d. Create scheduled_payment record (status: PENDING)
   e. Schedule timer (durable timer service)
   f. Return payment_id and scheduled_time
```

### Payment Execution Flow

```
1. Timer Service → Payment Executor Service:
   a. Timer fires at scheduled_time
   b. Notify executor with payment_id

2. Payment Executor Service:
   a. Check payment status (still PENDING?)
   b. Create execution record (idempotency)
   c. Acquire distributed lock (payment_id)
   d. Check payment status again (double-check)
   e. If already executed, return (idempotent)
   f. Update payment status to EXECUTING
   g. Execute transfer:
      - Check from_account balance
      - Deduct from from_account
      - Add to to_account
      - Record transaction
   h. Update payment status to COMPLETED
   i. Release lock
   j. Publish event (payment completed)
```

### Cancel Payment Flow

```
1. Client → API Gateway
2. API Gateway → Payment Scheduler Service
3. Payment Scheduler Service:
   a. Check payment status (must be PENDING)
   b. Update payment status to CANCELLED
   c. Cancel timer (if not yet fired)
   d. Return success
```

## Database Design

### Schema Design

#### ScheduledPayments Table
```sql
CREATE TABLE scheduled_payments (
    payment_id VARCHAR(100) PRIMARY KEY,
    from_account_id BIGINT NOT NULL,
    to_account_id BIGINT NOT NULL,
    amount BIGINT NOT NULL,
    scheduled_time TIMESTAMP NOT NULL,
    status ENUM('PENDING', 'EXECUTING', 'COMPLETED', 'FAILED', 'CANCELLED') DEFAULT 'PENDING',
    idempotency_key VARCHAR(100) UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    executed_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    error_message TEXT,
    INDEX idx_scheduled_time (scheduled_time, status),
    INDEX idx_from_account (from_account_id, status),
    INDEX idx_to_account (to_account_id, status),
    INDEX idx_status (status, scheduled_time)
) ENGINE=InnoDB;

-- Sharded by payment_id
-- Partition key: payment_id
```

#### PaymentExecutions Table
```sql
CREATE TABLE payment_executions (
    execution_id VARCHAR(100) PRIMARY KEY,
    payment_id VARCHAR(100) NOT NULL,
    status ENUM('PENDING', 'IN_PROGRESS', 'SUCCESS', 'FAILED') DEFAULT 'PENDING',
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    retry_count INT DEFAULT 0,
    INDEX idx_payment (payment_id),
    INDEX idx_status (status, executed_at),
    UNIQUE KEY uk_payment_execution (payment_id, execution_id)
) ENGINE=InnoDB;

-- Sharded by payment_id (aligned with scheduled_payments)
```

#### Accounts Table
```sql
CREATE TABLE accounts (
    account_id BIGINT PRIMARY KEY,
    balance BIGINT NOT NULL DEFAULT 0,
    version INT NOT NULL DEFAULT 0, -- For optimistic locking
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_balance (balance)
) ENGINE=InnoDB;

-- Sharded by account_id
-- Partition key: account_id
```

#### Transactions Table (Audit Trail)
```sql
CREATE TABLE transactions (
    transaction_id VARCHAR(100) PRIMARY KEY,
    payment_id VARCHAR(100),
    from_account_id BIGINT NOT NULL,
    to_account_id BIGINT NOT NULL,
    amount BIGINT NOT NULL,
    transaction_type ENUM('PAYMENT', 'REFUND', 'ADJUSTMENT') DEFAULT 'PAYMENT',
    status ENUM('PENDING', 'COMPLETED', 'FAILED') DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    INDEX idx_payment (payment_id),
    INDEX idx_from_account (from_account_id, created_at),
    INDEX idx_to_account (to_account_id, created_at)
) ENGINE=InnoDB;

-- Sharded by transaction_id
```

#### PaymentEvents Table (Event Sourcing)
```sql
CREATE TABLE payment_events (
    event_id VARCHAR(100) PRIMARY KEY,
    payment_id VARCHAR(100) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_data JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_payment (payment_id, timestamp),
    INDEX idx_event_type (event_type, timestamp)
) ENGINE=InnoDB;

-- Sharded by payment_id
```

### Database Sharding Strategy

**ScheduledPayments Table:**
- **Shard Key**: `payment_id`
- **Sharding Strategy**: Hash-based sharding
- **Number of Shards**: 100 shards
- **Reasoning**: Payments are accessed by payment_id

**PaymentExecutions Table:**
- **Shard Key**: `payment_id` (aligned with scheduled_payments)
- **Sharding Strategy**: Hash-based sharding
- **Number of Shards**: 100 shards
- **Reasoning**: Executions are always accessed with payment_id

**Accounts Table:**
- **Shard Key**: `account_id`
- **Sharding Strategy**: Hash-based sharding
- **Number of Shards**: 100 shards
- **Reasoning**: Account operations are by account_id

**Transactions Table:**
- **Shard Key**: `transaction_id`
- **Sharding Strategy**: Hash-based sharding
- **Number of Shards**: 100 shards
- **Reasoning**: Transactions are accessed by transaction_id

## High-Level Design

```
┌─────────────────────────────────────────────────────────┐
│                    Client Applications                   │
│              (Web, Mobile, API Clients)                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTPS
                     │
┌────────────────────▼────────────────────────────────────┐
│                  API Gateway / LB                        │
│              (Rate Limiting, Auth)                       │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
┌────────▼────────┐    ┌─────────▼─────────┐
│ Payment Scheduler│    │ Payment Executor  │
│   Service        │    │   Service         │
│ (Schedule/Cancel)│    │ (Execute Payments)│
└────────┬────────┘    └─────────┬──────────┘
         │                       │
         │                       │
┌────────▼───────────────────────▼──────────┐
│         Durable Timer Service               │
│  (Scheduled Payment Triggers)               │
└────────┬───────────────────────────────────┘
         │
         │
┌────────▼───────────────────────────────────┐
│         Redis Cluster                       │
│  (Locks, Cache, Queue State)                │
└────────┬───────────────────────────────────┘
         │
         │
┌────────▼───────────────────────────────────┐
│         Database Cluster                   │
│  (Payments, Accounts, Transactions)        │
└────────┬───────────────────────────────────┘
         │
         │
┌────────▼───────────────────────────────────┐
│         Account Service                    │
│  (Balance Management, Transfers)             │
└────────────────────────────────────────────┘

┌───────────────────────────────────────────┐
│      Message Queue (Kafka)                │
│  (Payment Events, Audit Trail)            │
└───────────────────────────────────────────┘

┌───────────────────────────────────────────┐
│      Monitoring & Observability          │
│  (Metrics, Logs, Alerts)                  │
└───────────────────────────────────────────┘
```

## Deep Dive

### Component Design

#### 1. Payment Scheduler Service
- **Responsibilities**: Schedule payments, cancel payments, status queries
- **Optimization**: 
  - Idempotency key checking
  - Fast payment creation
  - Efficient status queries

#### 2. Durable Timer Service
- **Responsibilities**: Store scheduled payments, trigger executions
- **Implementation Options**:
  - **Option 1**: Database polling (query scheduled payments)
  - **Option 2**: Redis Sorted Sets (score = scheduled_time)
  - **Option 3**: Time-based message queue (Kafka with delayed messages)
  - **Option 4**: Dedicated timer service (Quartz, Temporal)
- **Recommended**: Hybrid (Redis + Database for durability)

#### 3. Payment Executor Service
- **Responsibilities**: Execute payments, handle retries, ensure idempotency
- **Optimization**:
  - Distributed locks for payment execution
  - Idempotency checks
  - Retry logic with exponential backoff

#### 4. Account Service
- **Responsibilities**: Manage account balances, execute transfers
- **Optimization**:
  - Optimistic locking for account updates
  - Batch updates where possible
  - Account balance caching

#### 5. Redis Cluster
- **Distributed Locks**: For payment execution (prevent duplicates)
- **Cache**: Account balances, payment status
- **Timer State**: Sorted sets for scheduled payments

### Durable Timers

#### Challenge
How to ensure payments execute even if system fails?

#### Solution: Hybrid Approach (Redis + Database)

**Approach 1: Database Polling**
```python
# Background worker polls database for due payments
def poll_due_payments():
    while True:
        due_payments = db.query("""
            SELECT payment_id 
            FROM scheduled_payments 
            WHERE status = 'PENDING' 
            AND scheduled_time <= NOW()
            LIMIT 1000
        """)
        
        for payment in due_payments:
            executor.execute_payment(payment.payment_id)
        
        time.sleep(1)  # Poll every second
```

**Pros**: Simple, durable (database is source of truth)
**Cons**: Polling overhead, latency (up to 1 second)

**Approach 2: Redis Sorted Sets**
```python
# Add payment to sorted set (score = scheduled_time)
def schedule_payment(payment_id, scheduled_time):
    redis.zadd("scheduled_payments", {payment_id: scheduled_time.timestamp()})
    # Also store in database for durability

# Worker polls sorted set for due payments
def poll_redis_timers():
    while True:
        now = time.time()
        due_payments = redis.zrangebyscore("scheduled_payments", 0, now, limit=100)
        
        if due_payments:
            for payment_id in due_payments:
                redis.zrem("scheduled_payments", payment_id)
                executor.execute_payment(payment_id)
        
        time.sleep(0.1)  # Poll every 100ms
```

**Pros**: Fast, low latency, efficient
**Cons**: Not durable (Redis can lose data)

**Approach 3: Hybrid (Recommended)**
```python
# Schedule payment: Store in both Redis and Database
def schedule_payment(payment_id, scheduled_time):
    # Store in database (durable)
    db.execute("""
        INSERT INTO scheduled_payments 
        (payment_id, scheduled_time, status) 
        VALUES (?, ?, 'PENDING')
    """, payment_id, scheduled_time)
    
    # Store in Redis (fast access)
    redis.zadd("scheduled_payments", {payment_id: scheduled_time.timestamp()})

# Worker: Poll Redis (fast), fallback to database (durable)
def poll_timers():
    while True:
        # Try Redis first (fast)
        now = time.time()
        due_payments = redis.zrangebyscore("scheduled_payments", 0, now, limit=100)
        
        if not due_payments:
            # Fallback to database (durable)
            due_payments = db.query("""
                SELECT payment_id 
                FROM scheduled_payments 
                WHERE status = 'PENDING' 
                AND scheduled_time <= NOW()
                LIMIT 100
            """)
        
        for payment_id in due_payments:
            executor.execute_payment(payment_id)
        
        time.sleep(0.1)
```

**Benefits**:
- Fast (Redis for active timers)
- Durable (Database as source of truth)
- Resilient (fallback to database if Redis fails)

### Payment Execution Workflow

#### Atomic Transfer

**Challenge**: Ensure payment is atomic (all-or-nothing).

**Solution**: Database Transaction + Distributed Lock

```python
def execute_payment(payment_id, execution_id):
    # Acquire distributed lock (prevent concurrent execution)
    lock_key = f"payment_lock:{payment_id}"
    lock = acquire_lock(lock_key, timeout=30)
    
    try:
        # Check idempotency (already executed?)
        execution = db.query("""
            SELECT * FROM payment_executions 
            WHERE payment_id = ? AND execution_id = ?
        """, payment_id, execution_id)
        
        if execution and execution.status == 'SUCCESS':
            return {"status": "already_executed", "execution_id": execution_id}
        
        # Get payment details
        payment = db.query("""
            SELECT * FROM scheduled_payments 
            WHERE payment_id = ? AND status = 'PENDING'
        """, payment_id)
        
        if not payment:
            return {"status": "not_found_or_executed"}
        
        # Create execution record (idempotency)
        db.execute("""
            INSERT INTO payment_executions 
            (execution_id, payment_id, status) 
            VALUES (?, ?, 'IN_PROGRESS')
            ON DUPLICATE KEY UPDATE status = 'IN_PROGRESS'
        """, execution_id, payment_id)
        
        # Execute transfer in transaction
        with db.transaction():
            # Update payment status
            db.execute("""
                UPDATE scheduled_payments 
                SET status = 'EXECUTING' 
                WHERE payment_id = ?
            """, payment_id)
            
            # Check from_account balance
            from_account = db.query("""
                SELECT balance, version 
                FROM accounts 
                WHERE account_id = ?
                FOR UPDATE
            """, payment.from_account_id)
            
            if from_account.balance < payment.amount:
                raise InsufficientBalanceError()
            
            # Deduct from from_account (optimistic locking)
            db.execute("""
                UPDATE accounts 
                SET balance = balance - ?, 
                    version = version + 1 
                WHERE account_id = ? 
                AND version = ?
            """, payment.amount, payment.from_account_id, from_account.version)
            
            # Add to to_account (optimistic locking)
            to_account = db.query("""
                SELECT version 
                FROM accounts 
                WHERE account_id = ?
                FOR UPDATE
            """, payment.to_account_id)
            
            db.execute("""
                UPDATE accounts 
                SET balance = balance + ?, 
                    version = version + 1 
                WHERE account_id = ? 
                AND version = ?
            """, payment.amount, payment.to_account_id, to_account.version)
            
            # Create transaction record
            transaction_id = generate_id()
            db.execute("""
                INSERT INTO transactions 
                (transaction_id, payment_id, from_account_id, to_account_id, amount, status)
                VALUES (?, ?, ?, ?, ?, 'COMPLETED')
            """, transaction_id, payment_id, payment.from_account_id, 
                   payment.to_account_id, payment.amount)
            
            # Update payment status
            db.execute("""
                UPDATE scheduled_payments 
                SET status = 'COMPLETED', executed_at = NOW()
                WHERE payment_id = ?
            """, payment_id)
            
            # Update execution status
            db.execute("""
                UPDATE payment_executions 
                SET status = 'SUCCESS', completed_at = NOW()
                WHERE execution_id = ?
            """, execution_id)
        
        # Publish event
        publish_event("payment_completed", payment_id)
        
        return {"status": "success", "execution_id": execution_id}
        
    except InsufficientBalanceError:
        # Update payment status to FAILED
        db.execute("""
            UPDATE scheduled_payments 
            SET status = 'FAILED', 
                error_message = 'Insufficient balance'
            WHERE payment_id = ?
        """, payment_id)
        
        db.execute("""
            UPDATE payment_executions 
            SET status = 'FAILED', 
                error_message = 'Insufficient balance'
            WHERE execution_id = ?
        """, execution_id)
        
        return {"status": "failed", "error": "Insufficient balance"}
        
    except Exception as e:
        # Retry logic
        retry_count = get_retry_count(execution_id)
        if retry_count < 3:
            schedule_retry(payment_id, execution_id, retry_count + 1)
        else:
            mark_failed(payment_id, execution_id, str(e))
        
        return {"status": "failed", "error": str(e)}
        
    finally:
        release_lock(lock_key)
```

### Idempotency

#### Challenge
Ensure payment executes exactly once, even with retries.

#### Solution: Execution ID + Status Check

**Idempotency Key**: `execution_id` (unique per execution attempt)

**Idempotency Check**:
```python
def execute_payment(payment_id, execution_id):
    # Check if already executed with this execution_id
    execution = db.query("""
        SELECT status 
        FROM payment_executions 
        WHERE payment_id = ? AND execution_id = ?
    """, payment_id, execution_id)
    
    if execution and execution.status == 'SUCCESS':
        # Already executed, return success
        return {"status": "already_executed"}
    
    # Check if payment already completed (different execution_id)
    payment = db.query("""
        SELECT status 
        FROM scheduled_payments 
        WHERE payment_id = ?
    """, payment_id)
    
    if payment.status == 'COMPLETED':
        # Payment already completed, return success
        return {"status": "already_completed"}
    
    # Proceed with execution...
```

**Benefits**:
- Safe retries (same execution_id = no duplicate)
- Handles network failures (retry with same execution_id)
- Handles duplicate timer triggers (same execution_id = idempotent)

### Account Contention Handling

#### Challenge
Many concurrent payments to same account (hot account).

#### Solution: Optimistic Locking + Batching

**Optimistic Locking**:
```python
# Use version field for optimistic locking
def update_account_balance(account_id, delta, expected_version):
    result = db.execute("""
        UPDATE accounts 
        SET balance = balance + ?, 
            version = version + 1 
        WHERE account_id = ? 
        AND version = ?
    """, delta, account_id, expected_version)
    
    if result.rows_affected == 0:
        # Version mismatch, retry
        raise VersionConflictError()
```

**Batching** (for high-contention accounts):
```python
# Batch multiple payments to same account
def batch_update_account(account_id, payments):
    # Group payments by account
    total_delta = sum(p.amount for p in payments if p.to_account_id == account_id)
    total_delta -= sum(p.amount for p in payments if p.from_account_id == account_id)
    
    # Single update instead of multiple
    db.execute("""
        UPDATE accounts 
        SET balance = balance + ? 
        WHERE account_id = ?
    """, total_delta, account_id)
```

**Account Sharding**:
- Shard accounts by account_id
- Distribute load across shards
- Reduces contention per shard

### Scalability

#### Horizontal Scaling

**Payment Scheduler Service**:
- Stateless service
- Horizontal scaling (multiple instances)
- Load balanced

**Timer Workers**:
- Multiple workers polling timers
- Partition timers by payment_id hash
- Each worker handles subset of timers

**Payment Executor Service**:
- Multiple executor instances
- Process payments in parallel
- Distributed locks prevent duplicates

#### Database Scaling

**Read Replicas**:
- Use read replicas for status queries
- Reduces load on primary database

**Sharding**:
- Shard by payment_id, account_id
- Distribute load across shards

**Connection Pooling**:
- Efficient database connections
- Reduces connection overhead

### Observability

#### Metrics

**Key Metrics**:
- Scheduled payments rate (per second)
- Payment execution rate (per second)
- Payment success rate (%)
- Payment failure rate (%)
- Average execution latency (P50, P95, P99)
- Pending payments count
- Account balance updates rate

**Monitoring**:
- Prometheus for metrics
- Grafana for dashboards
- Alert on high failure rate
- Alert on high latency
- Alert on pending payment backlog

#### Logging

**Structured Logging**:
```python
logger.info("payment_scheduled", extra={
    "payment_id": payment_id,
    "from_account_id": from_account_id,
    "to_account_id": to_account_id,
    "amount": amount,
    "scheduled_time": scheduled_time
})

logger.info("payment_executed", extra={
    "payment_id": payment_id,
    "execution_id": execution_id,
    "status": "success",
    "latency_ms": latency
})
```

**Log Aggregation**:
- Centralized logging (ELK stack, Splunk)
- Searchable logs
- Log retention (30 days)

#### Alerting

**Critical Alerts**:
- Payment execution failure rate > 1%
- Payment execution latency P95 > 1 second
- Pending payment backlog > 1M
- Account balance inconsistencies
- Timer service down

**Warning Alerts**:
- Payment execution failure rate > 0.1%
- Payment execution latency P95 > 500ms
- High account contention

### Failure Handling

#### Timer Service Failure

**Scenario**: Timer service crashes, payments not triggered.

**Solution**:
- Database polling fallback (always poll database)
- Reconciliation job (find missed payments)
- Retry missed payments

#### Payment Execution Failure

**Scenario**: Payment execution fails (network, database, etc.).

**Solution**:
- Retry with exponential backoff
- Max retries: 3
- Dead letter queue for failed payments
- Manual intervention for persistent failures

#### Account Balance Inconsistency

**Scenario**: Account balance doesn't match transactions.

**Solution**:
- Reconciliation job (recalculate balances from transactions)
- Alert on inconsistencies
- Manual correction process

#### Duplicate Execution

**Scenario**: Payment executed twice (timer fired twice).

**Solution**:
- Idempotency keys (execution_id)
- Distributed locks
- Status checks before execution

### Trade-offs and Optimizations

#### Trade-offs

1. **Latency vs Durability**
   - **Choice**: Hybrid (Redis + Database)
   - **Reason**: Fast (Redis) + Durable (Database)
   - **Benefit**: Best of both worlds

2. **Consistency vs Performance**
   - **Choice**: Strong consistency for balances, eventual for status
   - **Reason**: Balances must be accurate, status can be slightly stale
   - **Benefit**: Better performance, lower latency

3. **Accuracy vs Overhead**
   - **Choice**: 100ms polling (1 second accuracy)
   - **Reason**: Balance accuracy vs polling overhead
   - **Benefit**: Good accuracy with reasonable overhead

#### Optimizations

1. **Timer Batching**
   - Batch multiple payments in single execution
   - Reduces database queries
   - Better throughput

2. **Account Balance Caching**
   - Cache account balances in Redis
   - Reduces database queries
   - Faster reads

3. **Payment Status Caching**
   - Cache payment status in Redis
   - Reduces database queries
   - Faster status checks

4. **Connection Pooling**
   - Pool database connections
   - Pool Redis connections
   - Better resource utilization

## What Interviewers Look For

### Distributed Systems Skills

1. **Durable Timers**
   - Ensuring payments execute after failures
   - Hybrid approach (Redis + Database)
   - Reconciliation for missed payments
   - **Red Flags**: No durability, single point of failure, no reconciliation

2. **Money-Movement Correctness**
   - Atomic transfers (all-or-nothing)
   - Account balance consistency
   - Transaction integrity
   - **Red Flags**: No transactions, race conditions, balance inconsistencies

3. **Idempotency**
   - Idempotent payment execution
   - Handling retries safely
   - Execution ID pattern
   - **Red Flags**: No idempotency, duplicate payments, no retry handling

### Problem-Solving Approach

1. **Separation of Concerns**
   - Scheduling vs execution separation
   - Timer service vs executor service
   - Clear service boundaries
   - **Red Flags**: Monolithic design, tight coupling, unclear boundaries

2. **Account Contention**
   - Optimistic locking
   - Batching for high-contention accounts
   - Account sharding
   - **Red Flags**: No locking, race conditions, no batching

3. **Scalability**
   - Horizontal scaling
   - Database sharding
   - Timer partitioning
   - **Red Flags**: Vertical scaling only, no sharding, no partitioning

### System Design Skills

1. **Component Design**
   - Clear service boundaries
   - Proper API design
   - Data flow understanding
   - **Red Flags**: Monolithic design, unclear boundaries, poor APIs

2. **Database Design**
   - Proper sharding strategy
   - Index design
   - Transaction design
   - **Red Flags**: No sharding, poor indexes, no transactions

3. **Observability**
   - Comprehensive metrics
   - Structured logging
   - Alerting strategy
   - **Red Flags**: No metrics, no logging, no alerting

### Communication Skills

1. **Clear Explanation**
   - Explains durable timer approach
   - Discusses idempotency patterns
   - Justifies design decisions
   - **Red Flags**: Unclear explanations, no justification, confusing

2. **Architecture Diagrams**
   - Clear component diagram
   - Shows data flow
   - Timer execution flow
   - **Red Flags**: No diagrams, unclear diagrams, missing components

### Meta-Specific Focus

1. **Financial Systems Correctness**
   - Understanding of money-movement correctness
   - Atomic operations
   - Balance consistency
   - **Key**: Demonstrate financial systems expertise

2. **Durable Scheduling**
   - Timer durability
   - Reconciliation patterns
   - Failure recovery
   - **Key**: Show durable scheduling expertise

3. **Observability and Operability**
   - Comprehensive monitoring
   - Alerting strategy
   - Debugging capabilities
   - **Key**: Demonstrate observability thinking

## Summary

Designing a delayed payment scheduler service requires careful consideration of durable timers, money-movement correctness, idempotency, account contention, and scalability. Key design decisions include:

**Architecture Highlights:**
- Hybrid timer approach (Redis + Database) for speed and durability
- Separation of scheduling and execution services
- Atomic payment execution with distributed locks
- Idempotent execution with execution IDs
- Optimistic locking for account contention

**Key Patterns:**
- **Durable Timers**: Hybrid approach (Redis for speed, Database for durability)
- **Idempotency**: Execution ID pattern for safe retries
- **Atomic Transfers**: Database transactions for all-or-nothing execution
- **Account Contention**: Optimistic locking + batching
- **Observability**: Comprehensive metrics, logging, and alerting

**Scalability Solutions:**
- Horizontal scaling (multiple service instances)
- Database sharding (by payment_id, account_id)
- Timer partitioning (distribute timers across workers)
- Connection pooling (efficient resource usage)

**Trade-offs:**
- Latency vs durability (hybrid timer approach)
- Consistency vs performance (strong for balances, eventual for status)
- Accuracy vs overhead (100ms polling for 1 second accuracy)

This design handles 10M+ scheduled payments per day, 1M+ pending payments, and maintains < 1 second payment timing accuracy while ensuring no lost payments and no duplicate transfers. The system is scalable, fault-tolerant, and optimized for correctness and reliability.

