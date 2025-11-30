---
layout: post
title: "Design a Change Data Capture (CDC) System - System Design Interview"
date: 2025-12-29
categories: [System Design, Interview Example, Distributed Systems, Data Engineering, Event Streaming, Database Replication]
excerpt: "A comprehensive guide to designing a Change Data Capture (CDC) system that captures database changes in real-time, streams them to downstream systems, and enables data replication, event-driven architectures, and real-time analytics."
---

## Introduction

Designing a Change Data Capture (CDC) system is a complex distributed systems problem that tests your ability to build real-time data synchronization infrastructure. CDC systems capture changes from source databases (inserts, updates, deletes) and stream them to downstream systems for replication, analytics, event-driven architectures, and real-time data pipelines.

This post provides a detailed walkthrough of designing a CDC system, covering key architectural decisions, different CDC approaches (log-based, trigger-based, polling), event streaming, data transformation, and scalability challenges. This is a common system design interview question that tests your understanding of distributed systems, database internals, event streaming, and data engineering.

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
7. [High-Level Design](#high-level-design)
8. [Deep Dive](#deep-dive)
   - [Component Design](#component-design)
   - [CDC Approaches](#cdc-approaches)
   - [Log-Based CDC](#log-based-cdc)
   - [Trigger-Based CDC](#trigger-based-cdc)
   - [Polling-Based CDC](#polling-based-cdc)
   - [Event Streaming](#event-streaming)
   - [Data Transformation](#data-transformation)
   - [Schema Evolution](#schema-evolution)
   - [Failure Handling](#failure-handling)
   - [Scalability Considerations](#scalability-considerations)
   - [Trade-offs and Optimizations](#trade-offs-and-optimizations)
9. [What Interviewers Look For](#what-interviewers-look-for)
10. [Summary](#summary)

## Problem Statement

**Design a Change Data Capture (CDC) system that:**

1. Captures database changes (INSERT, UPDATE, DELETE) in real-time
2. Streams changes to downstream systems (databases, data warehouses, event streams)
3. Supports multiple source databases (MySQL, PostgreSQL, MongoDB)
4. Handles schema changes and data transformations
5. Ensures exactly-once or at-least-once delivery semantics
6. Scales to handle millions of changes per second
7. Provides low-latency change propagation (< 1 second)

**Scale Requirements:**
- 10M+ database changes per day
- 100K+ changes per second (peak)
- Support 100+ source databases
- Support 1000+ downstream consumers
- < 1 second change propagation latency (P95)
- 99.9% availability

**Key Challenges:**
- Capturing changes without impacting source database performance
- Handling schema changes and migrations
- Ensuring data consistency across systems
- Managing backpressure and failure recovery
- Supporting multiple database types
- Low-latency change propagation

## Requirements

### Functional Requirements

**Core Features:**
1. **Change Capture**: Capture INSERT, UPDATE, DELETE operations from source databases
2. **Change Streaming**: Stream changes to downstream systems in real-time
3. **Multi-Database Support**: Support MySQL, PostgreSQL, MongoDB, and other databases
4. **Schema Tracking**: Track and propagate schema changes
5. **Data Transformation**: Transform data formats and structures
6. **Filtering**: Filter changes by table, column, or condition
7. **Replay**: Replay changes from a specific point in time
8. **Monitoring**: Monitor capture lag, throughput, and errors

**Change Types:**
- **INSERT**: New row added
- **UPDATE**: Row modified
- **DELETE**: Row removed
- **Schema Changes**: Table/column changes

**Out of Scope:**
- DDL changes (CREATE TABLE, ALTER TABLE) - focus on DML
- Cross-database transactions
- Conflict resolution (handled by downstream)
- Data validation (assume source data is valid)

### Non-Functional Requirements

1. **Availability**: 99.9% uptime
2. **Performance**: 
   - Change capture latency: < 100ms (P95)
   - Change propagation latency: < 1 second (P95)
   - Throughput: 100K+ changes/second
3. **Scalability**: Handle 10M+ changes/day, 100+ source databases
4. **Consistency**: 
   - Exactly-once delivery (preferred)
   - At-least-once delivery (acceptable with idempotency)
5. **Reliability**: No data loss, handle failures gracefully
6. **Low Impact**: Minimal impact on source database performance (< 5% overhead)

## Capacity Estimation

### Traffic Estimates

- **Daily Changes**: 10M+ changes per day
- **Peak Changes**: 100K changes per second
- **Average Change Size**: 1KB (row data + metadata)
- **Peak Bandwidth**: 100K × 1KB = 100MB/s = 800Mbps
- **Source Databases**: 100+
- **Downstream Consumers**: 1000+

### Storage Estimates

**Change Log Storage:**
- 10M changes/day × 1KB = 10GB/day
- 30-day retention: 10GB × 30 = 300GB
- 1-year archive: 10GB × 365 = 3.65TB

**Metadata Storage:**
- Schema versions: 100 tables × 10 versions × 10KB = 10MB
- Checkpoint data: 100 databases × 1KB = 100KB
- Total metadata: ~10MB

**Total Storage**: ~3.65TB per year (mostly change logs)

## Core Entities

### ChangeEvent
- **Attributes**: event_id, source_db, table_name, operation (INSERT/UPDATE/DELETE), before_data, after_data, timestamp, transaction_id, sequence_number
- **Relationships**: Belongs to source database and table
- **Purpose**: Represents a single database change

### SourceDatabase
- **Attributes**: db_id, db_type (MySQL/PostgreSQL/MongoDB), connection_string, status, last_captured_timestamp
- **Relationships**: Has many tables, generates many change events
- **Purpose**: Represents a source database being monitored

### TableSchema
- **Attributes**: schema_id, db_id, table_name, columns, version, updated_at
- **Relationships**: Belongs to source database
- **Purpose**: Tracks table schema for change interpretation

### Consumer
- **Attributes**: consumer_id, name, subscription_type, filters, status
- **Relationships**: Consumes change events
- **Purpose**: Represents a downstream system consuming changes

### Checkpoint
- **Attributes**: checkpoint_id, source_db, table_name, last_processed_sequence, timestamp
- **Relationships**: Tracks progress for source database
- **Purpose**: Enables resumption after failures

## API

### 1. Register Source Database
```
POST /api/v1/sources
Headers:
  - Authorization: Bearer <token>
Body:
  - db_type: string (mysql, postgresql, mongodb)
  - connection_string: string
  - tables: array<string> (optional, all tables if empty)
Response:
  - source_id: string
  - status: string (ACTIVE, INACTIVE)
```

### 2. Start Capture
```
POST /api/v1/sources/{source_id}/start
Headers:
  - Authorization: Bearer <token>
Response:
  - status: string (STARTED)
  - checkpoint: object
```

### 3. Stop Capture
```
POST /api/v1/sources/{source_id}/stop
Headers:
  - Authorization: Bearer <token>
Response:
  - status: string (STOPPED)
```

### 4. Subscribe to Changes
```
POST /api/v1/consumers
Headers:
  - Authorization: Bearer <token>
Body:
  - source_id: string
  - table_filter: array<string> (optional)
  - column_filter: array<string> (optional)
  - operation_filter: array<string> (optional, INSERT/UPDATE/DELETE)
Response:
  - consumer_id: string
  - kafka_topic: string (or other streaming endpoint)
```

### 5. Get Capture Status
```
GET /api/v1/sources/{source_id}/status
Headers:
  - Authorization: Bearer <token>
Response:
  - status: string
  - lag_seconds: integer
  - changes_per_second: integer
  - last_captured_timestamp: timestamp
```

### 6. Replay Changes
```
POST /api/v1/sources/{source_id}/replay
Headers:
  - Authorization: Bearer <token>
Body:
  - start_timestamp: timestamp
  - end_timestamp: timestamp (optional)
  - table_filter: array<string> (optional)
Response:
  - replay_id: string
  - kafka_topic: string
```

## Data Flow

### Change Capture Flow

```
1. Source Database:
   a. Transaction commits
   b. Change written to transaction log (binlog, WAL, oplog)
   
2. CDC Connector:
   a. Reads from transaction log
   b. Parses change events
   c. Extracts before/after data
   d. Creates ChangeEvent objects
   e. Publishes to message queue (Kafka)
   
3. Message Queue (Kafka):
   a. Stores change events
   b. Partitions by source_db + table_name
   c. Replicates for durability
   
4. Downstream Consumers:
   a. Subscribe to Kafka topics
   b. Process change events
   c. Apply to target systems
   d. Update checkpoints
```

### Change Processing Flow

```
1. Change Event Arrives:
   a. Parse change event
   b. Validate schema
   c. Apply filters (if any)
   
2. Transformation (Optional):
   a. Transform data format
   b. Apply business logic
   c. Enrich with additional data
   
3. Routing:
   a. Determine target consumers
   b. Route to appropriate topics/endpoints
   
4. Delivery:
   a. Send to downstream systems
   b. Wait for acknowledgment
   c. Update checkpoint on success
```

## High-Level Design

```
┌─────────────────────────────────────────────────────────┐
│              Source Databases                           │
│  (MySQL, PostgreSQL, MongoDB, etc.)                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Transaction Logs
                     │ (Binlog, WAL, Oplog)
                     │
┌────────────────────▼────────────────────────────────────┐
│            CDC Connectors                               │
│  (Read Logs, Parse Changes, Create Events)              │
└──────┬───────────────────────────────────┬──────────────┘
       │                                   │
       │                                   │
┌──────▼──────────┐              ┌─────────▼───────────┐
│  Schema Registry│              │  Change Parser      │
│  (Track Schemas)│              │  (Parse Logs)       │
└─────────────────┘              └─────────────────────┘
       │                                   │
       │                                   │
┌──────▼───────────────────────────────────▼───────────┐
│         Message Queue (Kafka)                        │
│  (Store Change Events, Enable Replay)                │
└──────┬───────────────────────────────────────────────┘
       │
       │
┌──────▼───────────────────────────────────────────────┐
│         Change Processors                            │
│  (Transform, Filter, Route Changes)                   │
└──────┬───────────────────────────────────────────────┘
       │
       │
┌──────▼───────────────────────────────────────────────┐
│         Downstream Consumers                         │
│  (Databases, Data Warehouses, Event Streams)         │
└─────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────┐
│         Checkpoint Service                           │
│  (Track Progress, Enable Recovery)                   │
└───────────────────────────────────────────────────────┘
```

## Deep Dive

### Component Design

#### 1. CDC Connector
- **Responsibilities**: Read transaction logs, parse changes, create events
- **Database-Specific**: Different connectors for MySQL, PostgreSQL, MongoDB
- **Optimization**: 
  - Efficient log reading
  - Minimal database impact
  - Low-latency parsing

#### 2. Schema Registry
- **Responsibilities**: Track table schemas, handle schema changes
- **Optimization**:
  - Schema versioning
  - Fast schema lookups
  - Schema evolution support

#### 3. Change Parser
- **Responsibilities**: Parse transaction log entries into change events
- **Optimization**:
  - Efficient parsing
  - Handle different log formats
  - Extract before/after data

#### 4. Message Queue (Kafka)
- **Responsibilities**: Store change events, enable replay
- **Optimization**:
  - Partitioning by source + table
  - Replication for durability
  - Retention policies

#### 5. Change Processor
- **Responsibilities**: Transform, filter, route changes
- **Optimization**:
  - Efficient filtering
  - Parallel processing
  - Low-latency routing

### CDC Approaches

#### Approach Comparison

**1. Log-Based CDC (Recommended)**
- **How**: Read database transaction logs (binlog, WAL, oplog)
- **Pros**: Low impact, real-time, captures all changes
- **Cons**: Database-specific, complex parsing
- **Use Case**: Production systems, high throughput

**2. Trigger-Based CDC**
- **How**: Database triggers write changes to change table
- **Pros**: Simple, database-agnostic
- **Cons**: Higher database impact, potential performance issues
- **Use Case**: Low-volume systems, simple requirements

**3. Polling-Based CDC**
- **How**: Periodically query database for changes (timestamp/version columns)
- **Pros**: Simple, no database modifications
- **Cons**: Higher latency, misses deletes, polling overhead
- **Use Case**: Legacy systems, low-latency not critical

### Log-Based CDC

#### MySQL Binlog CDC

**How It Works:**
1. Enable binlog on MySQL
2. Connect as replication client
3. Read binlog events
4. Parse INSERT/UPDATE/DELETE events
5. Extract row data

**Implementation:**
```python
import mysql.connector
from mysql.connector import replication

class MySQLBinlogConnector:
    def __init__(self, connection_config):
        self.config = connection_config
        self.stream = None
    
    def connect(self):
        """Connect to MySQL as replication client"""
        self.stream = replication.BinLogStreamReader(
            connection_settings=self.config,
            server_id=1,
            only_events=[
                replication.DeleteRowsEvent,
                replication.WriteRowsEvent,
                replication.UpdateRowsEvent
            ]
        )
    
    def read_changes(self):
        """Read and parse binlog events"""
        for binlog_event in self.stream:
            if isinstance(binlog_event, replication.WriteRowsEvent):
                # INSERT operation
                for row in binlog_event.rows:
                    change_event = ChangeEvent(
                        operation='INSERT',
                        table=binlog_event.table,
                        after_data=row['values'],
                        timestamp=binlog_event.timestamp
                    )
                    yield change_event
            
            elif isinstance(binlog_event, replication.UpdateRowsEvent):
                # UPDATE operation
                for row in binlog_event.rows:
                    change_event = ChangeEvent(
                        operation='UPDATE',
                        table=binlog_event.table,
                        before_data=row['before_values'],
                        after_data=row['after_values'],
                        timestamp=binlog_event.timestamp
                    )
                    yield change_event
            
            elif isinstance(binlog_event, replication.DeleteRowsEvent):
                # DELETE operation
                for row in binlog_event.rows:
                    change_event = ChangeEvent(
                        operation='DELETE',
                        table=binlog_event.table,
                        before_data=row['values'],
                        timestamp=binlog_event.timestamp
                    )
                    yield change_event
```

#### PostgreSQL WAL CDC

**How It Works:**
1. Enable logical replication on PostgreSQL
2. Create replication slot
3. Read WAL (Write-Ahead Log) changes
4. Parse logical replication messages
5. Extract row data

**Implementation:**
```python
import psycopg2
from psycopg2.extras import LogicalReplicationConnection

class PostgreSQLWALConnector:
    def __init__(self, connection_string):
        self.conn_string = connection_string
        self.slot_name = "cdc_slot"
    
    def create_replication_slot(self):
        """Create logical replication slot"""
        conn = psycopg2.connect(self.conn_string)
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM pg_create_logical_replication_slot(%s, 'pgoutput')",
            (self.slot_name,)
        )
        slot_name, lsn = cur.fetchone()
        conn.close()
        return slot_name, lsn
    
    def read_changes(self, start_lsn):
        """Read WAL changes"""
        conn = psycopg2.connect(
            self.conn_string,
            connection_factory=LogicalReplicationConnection
        )
        
        replication_conn = conn.replication_slot(self.slot_name, start_lsn)
        
        for message in replication_conn:
            if message.data_message:
                # Parse logical replication message
                change_event = self.parse_wal_message(message)
                yield change_event
```

#### MongoDB Oplog CDC

**How It Works:**
1. Connect to MongoDB replica set
2. Read from oplog (operations log)
3. Parse insert/update/delete operations
4. Extract document data

**Implementation:**
```python
from pymongo import MongoClient
from bson import Timestamp

class MongoDBOplogConnector:
    def __init__(self, connection_string):
        self.client = MongoClient(connection_string)
        self.oplog = self.client.local.oplog.rs
    
    def read_changes(self, last_timestamp=None):
        """Read oplog changes"""
        query = {}
        if last_timestamp:
            query['ts'] = {'$gt': last_timestamp}
        
        cursor = self.oplog.find(query).tailable()
        
        for oplog_entry in cursor:
            operation = oplog_entry['op']  # 'i', 'u', 'd'
            namespace = oplog_entry['ns']
            
            if operation == 'i':  # Insert
                change_event = ChangeEvent(
                    operation='INSERT',
                    table=namespace,
                    after_data=oplog_entry['o'],
                    timestamp=oplog_entry['ts']
                )
                yield change_event
            
            elif operation == 'u':  # Update
                change_event = ChangeEvent(
                    operation='UPDATE',
                    table=namespace,
                    before_data=oplog_entry.get('o2', {}),
                    after_data=oplog_entry['o'],
                    timestamp=oplog_entry['ts']
                )
                yield change_event
            
            elif operation == 'd':  # Delete
                change_event = ChangeEvent(
                    operation='DELETE',
                    table=namespace,
                    before_data=oplog_entry['o'],
                    timestamp=oplog_entry['ts']
                )
                yield change_event
```

### Trigger-Based CDC

#### Implementation

**Database Trigger:**
```sql
-- Create change log table
CREATE TABLE change_log (
    id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(255) NOT NULL,
    operation VARCHAR(10) NOT NULL,  -- INSERT, UPDATE, DELETE
    row_id BIGINT NOT NULL,
    before_data JSONB,
    after_data JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create trigger function
CREATE OR REPLACE FUNCTION log_change()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO change_log (table_name, operation, row_id, after_data)
        VALUES (TG_TABLE_NAME, 'INSERT', NEW.id, row_to_json(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO change_log (table_name, operation, row_id, before_data, after_data)
        VALUES (TG_TABLE_NAME, 'UPDATE', NEW.id, row_to_json(OLD), row_to_json(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO change_log (table_name, operation, row_id, before_data)
        VALUES (TG_TABLE_NAME, 'DELETE', OLD.id, row_to_json(OLD));
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Create trigger on table
CREATE TRIGGER users_change_trigger
AFTER INSERT OR UPDATE OR DELETE ON users
FOR EACH ROW EXECUTE FUNCTION log_change();
```

**CDC Connector:**
```python
class TriggerBasedConnector:
    def read_changes(self, last_id=0):
        """Poll change_log table"""
        query = """
            SELECT * FROM change_log 
            WHERE id > %s 
            ORDER BY id ASC 
            LIMIT 1000
        """
        
        while True:
            changes = db.execute(query, (last_id,))
            
            if not changes:
                time.sleep(1)  # Poll every second
                continue
            
            for change in changes:
                change_event = ChangeEvent(
                    operation=change.operation,
                    table=change.table_name,
                    before_data=change.before_data,
                    after_data=change.after_data,
                    timestamp=change.timestamp
                )
                yield change_event
                last_id = change.id
```

### Polling-Based CDC

#### Implementation

**Requires Timestamp/Version Column:**
```sql
-- Add updated_at column
ALTER TABLE users ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Create index
CREATE INDEX idx_users_updated_at ON users(updated_at);
```

**CDC Connector:**
```python
class PollingBasedConnector:
    def read_changes(self, last_timestamp=None):
        """Poll for changes using timestamp"""
        if not last_timestamp:
            last_timestamp = datetime.now() - timedelta(days=1)
        
        while True:
            query = """
                SELECT * FROM users 
                WHERE updated_at > %s 
                ORDER BY updated_at ASC 
                LIMIT 1000
            """
            
            rows = db.execute(query, (last_timestamp,))
            
            for row in rows:
                change_event = ChangeEvent(
                    operation='UPDATE',  # Assume update (can't detect inserts/deletes)
                    table='users',
                    after_data=row,
                    timestamp=row.updated_at
                )
                yield change_event
                last_timestamp = row.updated_at
            
            time.sleep(1)  # Poll every second
```

### Event Streaming

#### Kafka Integration

**Topic Design:**
- Topic per source database: `cdc-{source_db_id}`
- Partitioning: By `table_name` (or `table_name + partition_key`)
- Replication: 3 replicas for durability

**Change Event Format:**
```json
{
  "event_id": "evt_123",
  "source_db": "db_456",
  "table_name": "users",
  "operation": "UPDATE",
  "before_data": {
    "id": 1,
    "name": "John",
    "email": "john@example.com"
  },
  "after_data": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com"
  },
  "timestamp": "2025-12-29T10:00:00Z",
  "transaction_id": "txn_789",
  "sequence_number": 12345
}
```

**Producer:**
```python
from kafka import KafkaProducer
import json

class ChangeEventProducer:
    def __init__(self, kafka_brokers):
        self.producer = KafkaProducer(
            bootstrap_servers=kafka_brokers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',  # Wait for all replicas
            retries=3
        )
    
    def publish(self, change_event, source_db_id):
        """Publish change event to Kafka"""
        topic = f"cdc-{source_db_id}"
        partition_key = f"{change_event.table_name}"
        
        self.producer.send(
            topic,
            key=partition_key.encode('utf-8'),
            value=change_event.to_dict()
        )
```

### Data Transformation

#### Schema Mapping

**Transform between schemas:**
```python
class SchemaTransformer:
    def __init__(self, source_schema, target_schema):
        self.source_schema = source_schema
        self.target_schema = target_schema
        self.mapping = self.build_mapping()
    
    def build_mapping(self):
        """Build column mapping between schemas"""
        mapping = {}
        for source_col, target_col in zip(
            self.source_schema.columns,
            self.target_schema.columns
        ):
            mapping[source_col.name] = target_col.name
        return mapping
    
    def transform(self, change_event):
        """Transform change event to target schema"""
        transformed_before = None
        transformed_after = None
        
        if change_event.before_data:
            transformed_before = self.transform_row(
                change_event.before_data,
                self.mapping
            )
        
        if change_event.after_data:
            transformed_after = self.transform_row(
                change_event.after_data,
                self.mapping
            )
        
        return ChangeEvent(
            operation=change_event.operation,
            table=self.target_schema.table_name,
            before_data=transformed_before,
            after_data=transformed_after,
            timestamp=change_event.timestamp
        )
```

### Schema Evolution

#### Handling Schema Changes

**Challenge**: Source schema changes (add/remove columns).

**Solution**: Schema versioning + transformation

**Schema Registry:**
```python
class SchemaRegistry:
    def __init__(self):
        self.schemas = {}  # table_name -> [SchemaVersion]
    
    def register_schema(self, table_name, schema, version):
        """Register new schema version"""
        if table_name not in self.schemas:
            self.schemas[table_name] = []
        
        self.schemas[table_name].append({
            'version': version,
            'schema': schema,
            'created_at': datetime.now()
        })
    
    def get_schema(self, table_name, version=None):
        """Get schema for table"""
        if table_name not in self.schemas:
            return None
        
        if version:
            # Get specific version
            for schema_version in self.schemas[table_name]:
                if schema_version['version'] == version:
                    return schema_version['schema']
        else:
            # Get latest version
            return self.schemas[table_name][-1]['schema']
```

**Schema Migration:**
```python
class SchemaMigrator:
    def migrate(self, change_event, source_version, target_version):
        """Migrate change event between schema versions"""
        source_schema = schema_registry.get_schema(
            change_event.table_name,
            source_version
        )
        target_schema = schema_registry.get_schema(
            change_event.table_name,
            target_version
        )
        
        # Transform data
        transformer = SchemaTransformer(source_schema, target_schema)
        return transformer.transform(change_event)
```

### Failure Handling

#### Checkpoint Management

**Store Progress:**
```python
class CheckpointManager:
    def __init__(self, storage):
        self.storage = storage  # Redis or database
    
    def save_checkpoint(self, source_db_id, table_name, sequence_number, timestamp):
        """Save checkpoint"""
        key = f"checkpoint:{source_db_id}:{table_name}"
        checkpoint = {
            'sequence_number': sequence_number,
            'timestamp': timestamp.isoformat()
        }
        self.storage.set(key, json.dumps(checkpoint))
    
    def get_checkpoint(self, source_db_id, table_name):
        """Get last checkpoint"""
        key = f"checkpoint:{source_db_id}:{table_name}"
        data = self.storage.get(key)
        if data:
            return json.loads(data)
        return None
    
    def resume_from_checkpoint(self, source_db_id, table_name):
        """Resume from last checkpoint"""
        checkpoint = self.get_checkpoint(source_db_id, table_name)
        if checkpoint:
            return checkpoint['sequence_number'], checkpoint['timestamp']
        return None, None
```

#### Error Handling

**Retry Logic:**
```python
class ChangeProcessor:
    def process_change(self, change_event, retry_count=0):
        """Process change event with retry"""
        try:
            # Publish to Kafka
            producer.publish(change_event)
            
            # Update checkpoint
            checkpoint_manager.save_checkpoint(
                change_event.source_db,
                change_event.table_name,
                change_event.sequence_number,
                change_event.timestamp
            )
            
        except Exception as e:
            if retry_count < 3:
                # Retry with exponential backoff
                delay = 2 ** retry_count
                time.sleep(delay)
                return self.process_change(change_event, retry_count + 1)
            else:
                # Max retries, send to dead letter queue
                dead_letter_queue.send(change_event)
                raise
```

### Scalability Considerations

#### Horizontal Scaling

**CDC Connectors:**
- One connector per source database
- Independent scaling
- No shared state

**Change Processors:**
- Multiple processors consuming from Kafka
- Partition-based parallelism
- Stateless processing

**Kafka Partitioning:**
- Partition by `source_db + table_name`
- Even distribution
- Parallel consumption

#### Performance Optimization

**Batch Processing:**
```python
class BatchProcessor:
    def __init__(self, batch_size=1000):
        self.batch_size = batch_size
        self.batch = []
    
    def add_change(self, change_event):
        """Add change to batch"""
        self.batch.append(change_event)
        
        if len(self.batch) >= self.batch_size:
            self.flush()
    
    def flush(self):
        """Flush batch to Kafka"""
        if self.batch:
            producer.send_batch(self.batch)
            self.batch = []
```

**Connection Pooling:**
- Pool database connections
- Reuse connections
- Reduce overhead

### Trade-offs and Optimizations

#### Trade-offs

1. **Latency vs Throughput**
   - **Choice**: Batch processing for throughput
   - **Reason**: Balance latency and efficiency
   - **Benefit**: Higher throughput, acceptable latency

2. **Exactly-Once vs At-Least-Once**
   - **Choice**: At-least-once with idempotency
   - **Reason**: Simpler, acceptable for most use cases
   - **Benefit**: Lower complexity, good enough guarantees

3. **Log-Based vs Trigger-Based**
   - **Choice**: Log-based for production
   - **Reason**: Lower database impact
   - **Benefit**: Better performance, real-time

#### Optimizations

1. **Filtering**
   - Filter at source (table/column level)
   - Reduce downstream processing
   - Lower bandwidth

2. **Compression**
   - Compress change events
   - Reduce storage and bandwidth
   - Better performance

3. **Deduplication**
   - Idempotent processing
   - Handle duplicate events
   - Ensure correctness

## What Interviewers Look For

### Distributed Systems Skills

1. **Change Capture**
   - Understanding of database internals
   - Log-based vs trigger-based approaches
   - Low-impact capture strategies
   - **Red Flags**: High database impact, polling only, no log-based

2. **Event Streaming**
   - Kafka integration
   - Partitioning strategies
   - Exactly-once semantics
   - **Red Flags**: No streaming, poor partitioning, no guarantees

3. **Schema Evolution**
   - Handling schema changes
   - Version management
   - Backward compatibility
   - **Red Flags**: No schema handling, breaks on changes, no versioning

### Problem-Solving Approach

1. **CDC Approach Selection**
   - Log-based for production
   - Trigger-based for simplicity
   - Polling for legacy systems
   - **Red Flags**: Wrong approach, no trade-offs, one-size-fits-all

2. **Failure Handling**
   - Checkpoint management
   - Retry logic
   - Dead letter queues
   - **Red Flags**: No checkpoints, no retries, data loss

3. **Scalability**
   - Horizontal scaling
   - Partitioning strategies
   - Performance optimization
   - **Red Flags**: Vertical scaling only, no partitioning, bottlenecks

### System Design Skills

1. **Component Design**
   - Clear service boundaries
   - Proper abstractions
   - Efficient interfaces
   - **Red Flags**: Monolithic design, poor abstractions, inefficient APIs

2. **Data Flow**
   - End-to-end flow understanding
   - Change propagation
   - Consumer management
   - **Red Flags**: Unclear flow, missing steps, poor routing

3. **Multi-Database Support**
   - Database-specific connectors
   - Unified interface
   - Consistent behavior
   - **Red Flags**: Single database, no abstraction, inconsistent

### Communication Skills

1. **Clear Explanation**
   - Explains CDC approaches
   - Discusses trade-offs
   - Justifies design decisions
   - **Red Flags**: Unclear explanations, no justification, confusing

2. **Architecture Diagrams**
   - Clear component diagram
   - Shows data flow
   - CDC pipeline visualization
   - **Red Flags**: No diagrams, unclear diagrams, missing components

### Meta-Specific Focus

1. **Data Engineering**
   - Understanding of ETL/ELT
   - Real-time data pipelines
   - Change propagation
   - **Key**: Demonstrate data engineering expertise

2. **Database Internals**
   - Transaction logs
   - Replication mechanisms
   - Low-impact capture
   - **Key**: Show database internals knowledge

3. **Event-Driven Architecture**
   - Event streaming
   - Change events
   - Downstream processing
   - **Key**: Demonstrate event-driven thinking

## Summary

Designing a Change Data Capture (CDC) system requires careful consideration of database internals, event streaming, schema evolution, and scalability. Key design decisions include:

**Architecture Highlights:**
- Log-based CDC for low database impact and real-time capture
- Kafka for event streaming and replay capability
- Schema registry for handling schema changes
- Checkpoint management for failure recovery
- Multi-database support with database-specific connectors

**Key Patterns:**
- **Log-Based CDC**: Read transaction logs (binlog, WAL, oplog)
- **Event Streaming**: Kafka for change event distribution
- **Schema Evolution**: Version management and transformation
- **Checkpoint Management**: Track progress for recovery
- **Exactly-Once/At-Least-Once**: Delivery semantics with idempotency

**Scalability Solutions:**
- Horizontal scaling (multiple connectors and processors)
- Kafka partitioning (by source + table)
- Batch processing (improve throughput)
- Connection pooling (reduce overhead)

**Trade-offs:**
- Log-based vs trigger-based (log-based for production)
- Exactly-once vs at-least-once (at-least-once with idempotency)
- Latency vs throughput (batch processing)

This design handles 10M+ changes per day, 100K+ changes per second, and maintains < 1 second change propagation latency while ensuring minimal impact on source databases and reliable change delivery. The system is scalable, fault-tolerant, and optimized for real-time data synchronization.

