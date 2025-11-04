---
layout: post
title: "Design a Job Scheduling System - Robinhood Interview Example"
date: 2025-11-03
categories: [System Design, Interview Example, Robinhood, Fintech]
excerpt: "A detailed walkthrough of designing a job scheduling system for Robinhood, including requirements gathering, architecture design, and fintech-specific considerations."
---

## Introduction

This post provides a complete walkthrough of designing a job scheduling system, a common interview question at Robinhood and other fintech companies. We'll walk through the entire design process, from requirements gathering to detailed implementation, with a focus on fintech-specific requirements like reliability, real-time processing, and compliance.

## Problem Statement

**Design a job scheduling system for Robinhood that can:**
- Schedule one-time and recurring jobs
- Execute jobs reliably with retry mechanisms
- Handle millions of scheduled jobs
- Support job dependencies
- Provide real-time job status updates
- Ensure financial compliance (audit trails, data retention)

## Step 1: Requirements Gathering

### Functional Requirements

**Core Features:**
1. **Job Scheduling**
   - Schedule one-time jobs at a specific time
   - Schedule recurring jobs (daily, weekly, monthly, cron-based)
   - Cancel or modify scheduled jobs
   - View job history and status

2. **Job Execution**
   - Execute jobs at scheduled times
   - Support different job types (data processing, notifications, reports, etc.)
   - Handle job failures gracefully
   - Retry failed jobs with exponential backoff

3. **Job Dependencies**
   - Support job dependencies (Job B runs after Job A completes)
   - Handle dependency chains
   - Manage complex workflows

4. **Monitoring and Observability**
   - Real-time job status tracking
   - Job execution metrics
   - Failure alerts
   - Performance monitoring

### Non-Functional Requirements

**Scale:**
- Handle 10+ million scheduled jobs
- Process 100,000+ jobs per minute
- Support millions of users

**Performance:**
- Job execution latency: < 100ms for simple jobs
- Schedule job latency: < 50ms
- High availability: 99.99% uptime

**Reliability:**
- No job loss
- At-least-once execution guarantee
- Automatic retry for failed jobs
- Data durability and backup

**Financial Compliance:**
- Complete audit trail for all job executions
- Data retention per regulatory requirements
- Secure job execution (no data leakage)
- Compliance reporting

### Constraints

- Must integrate with existing Robinhood infrastructure
- Must comply with SEC/FINRA regulations
- Must handle time-sensitive financial operations
- Must support multi-region deployment

## Step 2: Scale Estimation

### Storage Estimates

**Job Metadata:**
- Each job: ~1KB metadata
- 10M active jobs: ~10GB
- With history (1 year): ~100GB

**Execution Logs:**
- Each execution: ~500 bytes
- 100K jobs/minute × 1440 minutes/day = 144M executions/day
- Daily logs: ~72GB
- Yearly logs: ~26TB

### Throughput Estimates

- **Read QPS**: 50,000 (job status queries, scheduling queries)
- **Write QPS**: 100,000 (job scheduling, status updates)
- **Execution QPS**: 100,000 (job executions)

### Network Bandwidth

- Job metadata updates: 100K QPS × 1KB = 100MB/s
- Execution results: 100K QPS × 500B = 50MB/s
- Total: ~150MB/s

## Step 3: High-Level Design

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                       │
│  (Trading System, Portfolio Service, Notification Service)   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway                                │
│              (Authentication, Rate Limiting)                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Job Scheduler Service                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Scheduler   │  │   Executor   │  │  Dependency  │      │
│  │   Service   │  │   Service    │  │   Manager    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Database   │ │  Message     │ │   Cache      │
│  (PostgreSQL)│ │  Queue       │ │   (Redis)    │
│              │ │  (Kafka)     │ │              │
└──────────────┘ └──────────────┘ └──────────────┘
```

### Core Services

1. **Scheduler Service**: Schedules jobs and manages timing
2. **Executor Service**: Executes jobs and handles retries
3. **Dependency Manager**: Manages job dependencies
4. **API Gateway**: Handles client requests

### Data Stores

1. **Database (PostgreSQL)**: Stores job metadata, schedules, execution history
2. **Message Queue (Kafka)**: Async job execution queue
3. **Cache (Redis)**: Fast access to job status, recent executions

## Step 4: Detailed Design

### Database Schema

**Jobs Table:**
```sql
CREATE TABLE jobs (
    job_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    job_type VARCHAR(50) NOT NULL,
    job_config JSONB NOT NULL,
    schedule_type VARCHAR(20), -- 'one_time', 'recurring', 'cron'
    schedule_config JSONB,
    status VARCHAR(20), -- 'scheduled', 'running', 'completed', 'failed'
    priority INTEGER DEFAULT 0,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    next_execution_time TIMESTAMP,
    INDEX idx_next_execution (next_execution_time, status),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
);
```

**Job Executions Table:**
```sql
CREATE TABLE job_executions (
    execution_id UUID PRIMARY KEY,
    job_id UUID REFERENCES jobs(job_id),
    execution_time TIMESTAMP NOT NULL,
    status VARCHAR(20), -- 'success', 'failed', 'running'
    result JSONB,
    error_message TEXT,
    duration_ms INTEGER,
    created_at TIMESTAMP,
    INDEX idx_job_id (job_id),
    INDEX idx_execution_time (execution_time)
);
```

**Job Dependencies Table:**
```sql
CREATE TABLE job_dependencies (
    job_id UUID REFERENCES jobs(job_id),
    depends_on_job_id UUID REFERENCES jobs(job_id),
    PRIMARY KEY (job_id, depends_on_job_id)
);
```

### Scheduler Service Design

**Responsibilities:**
1. Accept job scheduling requests
2. Store job metadata in database
3. Calculate next execution time
4. Publish jobs to execution queue when due

**Key Components:**

```python
class SchedulerService:
    def schedule_job(self, job_request):
        # Validate job request
        # Calculate next execution time
        # Store in database
        # Add to execution queue if immediate
        pass
    
    def calculate_next_execution(self, schedule_type, schedule_config):
        # Handle one-time, recurring, cron schedules
        pass
    
    def poll_due_jobs(self):
        # Query database for jobs due for execution
        # Publish to Kafka queue
        pass
```

**Scheduling Algorithm:**
- Use database index on `next_execution_time` and `status`
- Poll every second for due jobs
- Batch process multiple due jobs
- Update `next_execution_time` for recurring jobs

### Executor Service Design

**Responsibilities:**
1. Consume jobs from Kafka queue
2. Execute job logic
3. Handle retries on failure
4. Update job status
5. Trigger dependent jobs

**Key Components:**

```python
class ExecutorService:
    def execute_job(self, job):
        try:
            # Load job handler based on job_type
            handler = self.get_handler(job.job_type)
            
            # Execute job
            result = handler.execute(job.job_config)
            
            # Update status
            self.update_job_status(job.job_id, 'completed', result)
            
            # Trigger dependent jobs
            self.trigger_dependent_jobs(job.job_id)
            
        except Exception as e:
            # Handle failure
            self.handle_job_failure(job, e)
    
    def handle_job_failure(self, job, error):
        if job.retry_count < job.max_retries:
            # Schedule retry with exponential backoff
            retry_delay = 2 ** job.retry_count  # seconds
            self.schedule_retry(job, retry_delay)
        else:
            # Mark as failed
            self.update_job_status(job.job_id, 'failed', error)
```

**Job Execution Flow:**
1. Job consumed from Kafka
2. Load job handler (registered by job type)
3. Execute job logic
4. Update execution record
5. If successful: trigger dependencies
6. If failed: retry or mark as failed

### Dependency Manager Design

**Responsibilities:**
1. Track job dependencies
2. Monitor job completion
3. Trigger dependent jobs when prerequisites complete

**Implementation:**

```python
class DependencyManager:
    def check_dependencies(self, job_id):
        # Query dependencies
        dependencies = self.get_dependencies(job_id)
        
        # Check if all dependencies completed
        all_completed = all(
            self.is_job_completed(dep_id) 
            for dep_id in dependencies
        )
        
        if all_completed:
            # Publish to execution queue
            self.publish_to_queue(job_id)
    
    def on_job_completed(self, job_id):
        # Find jobs that depend on this job
        dependent_jobs = self.get_dependent_jobs(job_id)
        
        # Check if each dependent job can now run
        for dep_job_id in dependent_jobs:
            self.check_dependencies(dep_job_id)
```

### Job Types and Handlers

**Common Job Types at Robinhood:**

1. **Portfolio Rebalancing**: Rebalance user portfolios
2. **Market Data Aggregation**: Aggregate market data
3. **Notification Jobs**: Send alerts and notifications
4. **Report Generation**: Generate financial reports
5. **Data Sync**: Sync data between services
6. **Compliance Checks**: Run compliance validations
7. **Risk Calculations**: Calculate risk metrics

**Handler Registration:**

```python
class JobHandlerRegistry:
    handlers = {
        'portfolio_rebalancing': PortfolioRebalancingHandler(),
        'market_data_aggregation': MarketDataHandler(),
        'notification': NotificationHandler(),
        'report_generation': ReportHandler(),
        # ...
    }
    
    def get_handler(self, job_type):
        return self.handlers.get(job_type)
```

## Step 5: Fintech-Specific Considerations

### 1. Audit Trail and Compliance

**Requirements:**
- Log all job executions
- Retain logs per SEC/FINRA requirements (7 years)
- Immutable audit logs
- Compliance reporting

**Implementation:**
- Store all executions in database
- Archive old logs to cold storage (S3)
- Implement audit log service
- Generate compliance reports

### 2. Data Consistency

**Critical Requirements:**
- Financial calculations must be accurate
- No duplicate job execution
- Transaction integrity

**Solutions:**
- Use database transactions for job updates
- Idempotent job execution
- Distributed locks for critical jobs
- Two-phase commit for multi-step jobs

### 3. Reliability and Fault Tolerance

**Strategies:**
- **Multi-region deployment**: Active-active across regions
- **Database replication**: Primary-replica setup
- **Queue replication**: Kafka replication across regions
- **Health checks**: Monitor service health
- **Circuit breakers**: Prevent cascading failures
- **Graceful degradation**: Continue operating with reduced functionality

### 4. Security

**Security Measures:**
- **Authentication**: All API calls authenticated
- **Authorization**: Role-based access control
- **Encryption**: Encrypt sensitive job data
- **Audit logging**: Log all access attempts
- **Rate limiting**: Prevent abuse

### 5. Real-time Monitoring

**Monitoring Requirements:**
- Job execution metrics (latency, throughput, success rate)
- Queue depth monitoring
- Database performance metrics
- Error rate tracking
- Alerting on failures

## Step 6: Scaling and Optimization

### Database Scaling

**Strategies:**
1. **Read Replicas**: Scale reads
2. **Sharding**: Shard by user_id or job_id
3. **Partitioning**: Partition execution logs by date
4. **Indexing**: Optimize queries with proper indexes

**Sharding Strategy:**
- Shard jobs table by `user_id` (hash-based)
- Shard executions table by `execution_time` (time-based)
- Use distributed transactions for cross-shard operations

### Caching Strategy

**Cache Layers:**
1. **L1 Cache**: In-memory cache for recent job status
2. **L2 Cache**: Redis for job metadata and status
3. **CDN**: Cache static job results

**Cache Invalidation:**
- TTL-based expiration
- Event-driven invalidation
- Cache-aside pattern

### Queue Optimization

**Kafka Configuration:**
- Multiple partitions for parallel processing
- Consumer groups for scaling
- Replication factor 3 for reliability
- Retention policy for job replay

### Load Balancing

- **API Gateway**: Distribute client requests
- **Executor Services**: Multiple instances processing jobs
- **Database**: Connection pooling and read replicas

## Step 7: API Design

### Schedule Job

```http
POST /api/v1/jobs
Content-Type: application/json

{
  "job_type": "portfolio_rebalancing",
  "job_config": {
    "user_id": "user123",
    "portfolio_id": "portfolio456"
  },
  "schedule_type": "recurring",
  "schedule_config": {
    "frequency": "daily",
    "time": "09:00:00",
    "timezone": "America/New_York"
  },
  "priority": 10,
  "max_retries": 3
}

Response:
{
  "job_id": "uuid-here",
  "status": "scheduled",
  "next_execution_time": "2025-11-04T09:00:00Z"
}
```

### Get Job Status

```http
GET /api/v1/jobs/{job_id}

Response:
{
  "job_id": "uuid-here",
  "status": "completed",
  "last_execution": {
    "execution_id": "exec-uuid",
    "execution_time": "2025-11-03T09:00:00Z",
    "status": "success",
    "duration_ms": 150
  },
  "next_execution_time": "2025-11-04T09:00:00Z"
}
```

### Cancel Job

```http
DELETE /api/v1/jobs/{job_id}

Response:
{
  "job_id": "uuid-here",
  "status": "cancelled"
}
```

### Get Job History

```http
GET /api/v1/jobs/{job_id}/executions?limit=10&offset=0

Response:
{
  "executions": [
    {
      "execution_id": "exec-uuid-1",
      "execution_time": "2025-11-03T09:00:00Z",
      "status": "success",
      "duration_ms": 150
    },
    // ...
  ],
  "total": 100
}
```

## Step 8: Trade-offs and Alternatives

### Database Choice

**PostgreSQL vs. NoSQL:**
- **PostgreSQL**: Strong consistency, ACID transactions, complex queries
- **NoSQL (Cassandra)**: Better write scalability, eventual consistency

**Decision**: PostgreSQL for strong consistency in financial operations

### Execution Model

**Synchronous vs. Asynchronous:**
- **Synchronous**: Simpler, but blocks scheduler
- **Asynchronous**: Better scalability, decoupled

**Decision**: Asynchronous with Kafka queue for scalability

### Retry Strategy

**Exponential Backoff vs. Fixed Delay:**
- **Exponential**: Reduces load on failing systems
- **Fixed**: Predictable timing

**Decision**: Exponential backoff to avoid overwhelming failing systems

## Step 9: Failure Scenarios and Handling

### Database Failure

**Scenario**: Primary database fails
**Handling**: 
- Automatic failover to replica
- Queue jobs for later processing
- Retry failed operations

### Queue Failure

**Scenario**: Kafka broker fails
**Handling**:
- Kafka replication (multiple brokers)
- Persist jobs to database as backup
- Resume from database when queue recovers

### Executor Service Failure

**Scenario**: Executor service crashes during job execution
**Handling**:
- Job timeout detection
- Automatic retry from queue
- Idempotent job execution
- Checkpoint intermediate state

### Network Partition

**Scenario**: Network partition between services
**Handling**:
- Circuit breakers
- Queue buffering
- Graceful degradation
- Health checks

## Step 10: Monitoring and Observability

### Key Metrics

**Job Metrics:**
- Jobs scheduled per minute
- Jobs executed per minute
- Job success rate
- Average job execution time
- Job retry rate

**System Metrics:**
- API latency (p50, p95, p99)
- Database query latency
- Queue depth
- Error rate
- System availability

### Alerting

**Critical Alerts:**
- Job execution failure rate > 5%
- Queue depth > 1M
- Database connection failures
- Service downtime

**Warning Alerts:**
- Job execution latency > 1s (p95)
- Retry rate > 10%
- Cache hit rate < 80%

## Conclusion

Designing a job scheduling system for Robinhood requires balancing:

1. **Scalability**: Handle millions of jobs
2. **Reliability**: No job loss, high availability
3. **Performance**: Low latency execution
4. **Compliance**: Audit trails, data retention
5. **Consistency**: Accurate financial calculations

Key design decisions:
- PostgreSQL for strong consistency
- Kafka for async job execution
- Redis for caching
- Multi-region deployment for reliability
- Comprehensive audit logging for compliance

The system should be designed with fintech-specific requirements in mind, ensuring reliability, security, and compliance while maintaining high performance and scalability.

## Key Takeaways for Interview

1. **Ask clarifying questions**: Understand scale, requirements, constraints
2. **Consider fintech specifics**: Compliance, reliability, security
3. **Design for scale**: Think about millions of jobs
4. **Handle failures**: Design for fault tolerance
5. **Think about trade-offs**: Consistency vs. availability, performance vs. cost
6. **Communicate clearly**: Explain your reasoning and design decisions

Good luck with your Robinhood system design interview!

