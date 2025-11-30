---
layout: post
title: "Design a To-Do List App with Multi-User Collaboration - System Design Interview"
date: 2025-11-29
categories: [System Design, Interview Example, Distributed Systems, Real-time Systems, Collaboration]
excerpt: "A comprehensive guide to designing a to-do list application with multi-user collaboration, covering task lists, sharing, real-time synchronization, date/time reminders, notifications, and conflict resolution for collaborative task management."
---

## Introduction

Designing a to-do list application with multi-user collaboration is a complex distributed systems problem that tests your ability to build real-time collaborative systems. The application must support task lists, sharing with collaborators, real-time synchronization, date/time reminders, and notifications to all collaborators.

This post provides a detailed walkthrough of designing a collaborative to-do list application, covering key architectural decisions, real-time synchronization, conflict resolution, reminder scheduling, and notification delivery. This is a common system design interview question that tests your understanding of distributed systems, real-time collaboration, WebSocket connections, and event-driven architectures.

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
   - [Real-Time Synchronization](#real-time-synchronization)
   - [Conflict Resolution](#conflict-resolution)
   - [Reminder System](#reminder-system)
   - [Notification System](#notification-system)
   - [Sharing and Permissions](#sharing-and-permissions)
   - [Scalability Considerations](#scalability-considerations)
   - [Failure Handling](#failure-handling)
   - [Trade-offs and Optimizations](#trade-offs-and-optimizations)
10. [What Interviewers Look For](#what-interviewers-look-for)
11. [Summary](#summary)

## Problem Statement

**Design a to-do list application similar to iPhone's Reminder app that:**

1. Allows users to create task lists
2. Share lists with other users for collaboration
3. Set date/time reminders that notify all collaborators
4. Real-time synchronization of changes across all collaborators
5. Handle concurrent edits and conflicts
6. Support offline mode with sync when online

**Scale Requirements:**
- 100M+ users
- 50M+ daily active users
- 1B+ tasks across all lists
- 10M+ shared lists
- 1M+ reminder notifications per hour
- Real-time updates with < 200ms latency
- Support lists with up to 50 collaborators

**Key Challenges:**
- Real-time synchronization across multiple clients
- Conflict resolution for concurrent edits
- Reminder scheduling and notification delivery
- Sharing permissions and access control
- Offline support with eventual consistency
- Handling high-frequency updates

## Requirements

### Functional Requirements

**Core Features:**
1. **Task Lists**: Users can create, edit, and delete task lists
2. **Tasks**: Users can create, edit, complete, and delete tasks within lists
3. **Sharing**: Users can share lists with other users (read-only or read-write)
4. **Real-Time Sync**: Changes appear instantly for all collaborators
5. **Reminders**: Users can set date/time reminders for tasks
6. **Notifications**: All collaborators receive notifications for reminders
7. **Offline Support**: App works offline, syncs when online
8. **Conflict Resolution**: Handle concurrent edits gracefully

**Task Features:**
- Title, description, notes
- Due date and time
- Priority (low, medium, high)
- Completion status
- Subtasks (nested tasks)
- Attachments (optional)

**Sharing Features:**
- Share list with specific users
- Permission levels: owner, editor, viewer
- Add/remove collaborators
- View who's currently viewing/editing

**Reminder Features:**
- Date/time reminders
- Recurring reminders (daily, weekly, monthly)
- Location-based reminders (optional)
- Notification to all collaborators

**Out of Scope:**
- Voice input for tasks
- Task templates
- Task dependencies
- Time tracking
- Advanced analytics

### Non-Functional Requirements

1. **Availability**: 99.9% uptime
2. **Reliability**: No data loss, all changes persisted
3. **Performance**: 
   - Create/update task: < 200ms (P95)
   - Real-time sync latency: < 200ms
   - List load time: < 500ms (P95)
   - Reminder notification: < 1 second from scheduled time
4. **Scalability**: Handle 50M+ DAU, 1B+ tasks
5. **Consistency**: 
   - Strong consistency for task updates (within list)
   - Eventual consistency acceptable for cross-list operations
6. **Real-Time**: Changes must appear instantly for online collaborators
7. **Offline Support**: App must work offline, sync when online

## Capacity Estimation

### Traffic Estimates

- **Daily Active Users (DAU)**: 50 million
- **Tasks Created**: 200M per day = 2,315 tasks/second average
- **Task Updates**: 500M per day = 5,787 updates/second average
- **List Shares**: 1M per day = 12 shares/second average
- **Reminder Notifications**: 1M per hour = 278 notifications/second average
- **Real-Time Updates**: 10M per day = 116 updates/second average
- **Peak Traffic**: 3x average = 7,000 tasks/second, 17,000 updates/second

### Storage Estimates

**Tasks:**
- 1B total tasks
- Average task size: 512 bytes (task_id, list_id, title, description, due_date, etc.)
- Total task storage: 1B × 512 bytes = 512GB

**Lists:**
- 100M lists
- Average list size: 256 bytes (list_id, name, owner_id, etc.)
- Total list storage: 100M × 256 bytes = 25.6GB

**Shares:**
- 10M shared lists
- Average share record: 128 bytes (list_id, user_id, permission)
- Total share storage: 10M × 128 bytes = 1.28GB

**Reminders:**
- 100M active reminders
- Average reminder size: 256 bytes (reminder_id, task_id, scheduled_time, etc.)
- Total reminder storage: 100M × 256 bytes = 25.6GB

**Total Storage**: ~565GB (mostly tasks)

## Core Entities

### List
- **Attributes**: list_id, name, owner_id, created_at, updated_at, color, icon
- **Relationships**: Has many tasks, has many shares, has many collaborators
- **Purpose**: Container for tasks

### Task
- **Attributes**: task_id, list_id, title, description, notes, due_date, due_time, priority, completed, created_at, updated_at, created_by, completed_by
- **Relationships**: Belongs to list, can have subtasks, can have reminders
- **Purpose**: Individual to-do item

### Share
- **Attributes**: share_id, list_id, user_id, permission (owner, editor, viewer), shared_at, shared_by
- **Relationships**: Links list to user with permission
- **Purpose**: Manage list sharing and permissions

### Reminder
- **Attributes**: reminder_id, task_id, scheduled_time, recurring_pattern, timezone, created_at
- **Relationships**: Belongs to task
- **Purpose**: Schedule and trigger notifications

### Notification
- **Attributes**: notification_id, user_id, task_id, list_id, type, message, sent_at, read_at
- **Relationships**: Sent to user, related to task/list
- **Purpose**: Deliver reminders and updates to users

### CollaborationEvent
- **Attributes**: event_id, list_id, user_id, event_type, event_data, timestamp
- **Event Types**: TASK_CREATED, TASK_UPDATED, TASK_COMPLETED, TASK_DELETED, LIST_UPDATED
- **Purpose**: Track changes for real-time sync and conflict resolution

## API

### 1. Create List
```
POST /api/v1/lists
Headers:
  - Authorization: Bearer <token>
Body:
  - name: string
  - color: string (optional)
  - icon: string (optional)
Response:
  - list_id: string
  - name: string
  - created_at: timestamp
```

### 2. Get Lists
```
GET /api/v1/lists
Headers:
  - Authorization: Bearer <token>
Query Parameters:
  - include_shared: boolean (default: true)
Response:
  - lists: array of list objects
```

### 3. Create Task
```
POST /api/v1/lists/{list_id}/tasks
Headers:
  - Authorization: Bearer <token>
Body:
  - title: string
  - description: string (optional)
  - due_date: date (optional)
  - due_time: time (optional)
  - priority: string (low, medium, high) (optional)
  - parent_task_id: string (optional, for subtasks)
Response:
  - task_id: string
  - title: string
  - created_at: timestamp
```

### 4. Update Task
```
PATCH /api/v1/tasks/{task_id}
Headers:
  - Authorization: Bearer <token>
Body:
  - title: string (optional)
  - description: string (optional)
  - due_date: date (optional)
  - due_time: time (optional)
  - priority: string (optional)
  - completed: boolean (optional)
Response:
  - task_id: string
  - updated_at: timestamp
```

### 5. Share List
```
POST /api/v1/lists/{list_id}/share
Headers:
  - Authorization: Bearer <token>
Body:
  - user_id: string
  - permission: string (editor, viewer)
Response:
  - share_id: string
  - user_id: string
  - permission: string
```

### 6. Set Reminder
```
POST /api/v1/tasks/{task_id}/reminders
Headers:
  - Authorization: Bearer <token>
Body:
  - scheduled_time: timestamp
  - recurring_pattern: string (optional, e.g., "daily", "weekly")
  - timezone: string
Response:
  - reminder_id: string
  - scheduled_time: timestamp
```

### 7. Real-Time Updates (WebSocket)
```
WebSocket: wss://api.example.com/v1/lists/{list_id}/updates
Events:
  - task_created: { task_id, list_id, title, created_by }
  - task_updated: { task_id, changes, updated_by }
  - task_completed: { task_id, completed_by }
  - task_deleted: { task_id, deleted_by }
  - list_updated: { list_id, changes, updated_by }
  - collaborator_joined: { user_id, list_id }
  - collaborator_left: { user_id, list_id }
```

### 8. Get Task History
```
GET /api/v1/tasks/{task_id}/history
Headers:
  - Authorization: Bearer <token>
Query Parameters:
  - limit: integer (default: 50)
  - cursor: string (pagination)
Response:
  - events: array of collaboration events
  - next_cursor: string
```

## Data Flow

### Create Task Flow

```
1. Client → API Gateway
2. API Gateway → Auth Service (validate token)
3. API Gateway → Task Service
4. Task Service:
   a. Validate user has permission (editor/owner)
   b. Create task record in database
   c. Create collaboration event
   d. Publish event to message queue
   e. Broadcast to WebSocket connections (real-time)
   f. Return task_id
5. Real-Time Service:
   a. Receives event from queue
   b. Broadcasts to all WebSocket connections for list
   c. Clients receive update instantly
```

### Real-Time Sync Flow

```
1. User A updates task:
   a. Client sends update to API
   b. API updates database
   c. API publishes event to Kafka
   d. Real-Time Service receives event
   e. Real-Time Service broadcasts to all WebSocket connections
   
2. User B receives update:
   a. WebSocket receives event
   b. Client applies update locally
   c. UI updates instantly
```

### Reminder Flow

```
1. Reminder Scheduler (Background Worker):
   a. Polls reminders table for due reminders
   b. Finds reminders where scheduled_time <= now()
   c. For each reminder:
      - Get task and list details
      - Get all collaborators for list
      - Create notification for each collaborator
      - Send push notification
      - Update reminder status
```

### Share List Flow

```
1. User A shares list with User B:
   a. Client sends share request
   b. API validates User A is owner/editor
   c. API creates share record
   d. API sends notification to User B
   e. User B receives notification
   f. User B can now access list
```

## Database Design

### Schema Design

#### Lists Table
```sql
CREATE TABLE lists (
    list_id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    owner_id BIGINT NOT NULL,
    color VARCHAR(50),
    icon VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    version INT DEFAULT 0, -- For optimistic locking
    INDEX idx_owner (owner_id),
    INDEX idx_updated (updated_at)
) ENGINE=InnoDB;

-- Sharded by list_id
```

#### Tasks Table
```sql
CREATE TABLE tasks (
    task_id VARCHAR(100) PRIMARY KEY,
    list_id VARCHAR(100) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    notes TEXT,
    due_date DATE,
    due_time TIME,
    priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    parent_task_id VARCHAR(100), -- For subtasks
    created_by BIGINT NOT NULL,
    completed_by BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    version INT DEFAULT 0, -- For optimistic locking
    INDEX idx_list (list_id, created_at),
    INDEX idx_due_date (due_date, completed),
    INDEX idx_parent (parent_task_id),
    FOREIGN KEY (list_id) REFERENCES lists(list_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Sharded by list_id (aligned with lists)
```

#### Shares Table
```sql
CREATE TABLE shares (
    share_id VARCHAR(100) PRIMARY KEY,
    list_id VARCHAR(100) NOT NULL,
    user_id BIGINT NOT NULL,
    permission ENUM('owner', 'editor', 'viewer') NOT NULL,
    shared_by BIGINT NOT NULL,
    shared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_list (list_id),
    INDEX idx_user (user_id),
    UNIQUE KEY uk_list_user (list_id, user_id),
    FOREIGN KEY (list_id) REFERENCES lists(list_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Sharded by list_id (aligned with lists)
```

#### Reminders Table
```sql
CREATE TABLE reminders (
    reminder_id VARCHAR(100) PRIMARY KEY,
    task_id VARCHAR(100) NOT NULL,
    scheduled_time TIMESTAMP NOT NULL,
    recurring_pattern VARCHAR(50), -- "daily", "weekly", "monthly", etc.
    timezone VARCHAR(50) NOT NULL,
    status ENUM('pending', 'sent', 'cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_scheduled (scheduled_time, status),
    INDEX idx_task (task_id),
    FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Sharded by scheduled_time (for efficient polling)
```

#### Notifications Table
```sql
CREATE TABLE notifications (
    notification_id VARCHAR(100) PRIMARY KEY,
    user_id BIGINT NOT NULL,
    task_id VARCHAR(100),
    list_id VARCHAR(100),
    type VARCHAR(50) NOT NULL, -- 'reminder', 'task_updated', 'list_shared', etc.
    message TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP,
    INDEX idx_user (user_id, sent_at),
    INDEX idx_task (task_id),
    INDEX idx_list (list_id)
) ENGINE=InnoDB;

-- Sharded by user_id
```

#### CollaborationEvents Table
```sql
CREATE TABLE collaboration_events (
    event_id VARCHAR(100) PRIMARY KEY,
    list_id VARCHAR(100) NOT NULL,
    user_id BIGINT NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    task_id VARCHAR(100),
    event_data JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_list (list_id, timestamp),
    INDEX idx_user (user_id, timestamp),
    INDEX idx_task (task_id)
) ENGINE=InnoDB;

-- Sharded by list_id (aligned with lists)
```

### Database Sharding Strategy

**Lists Table:**
- **Shard Key**: `list_id`
- **Sharding Strategy**: Hash-based sharding
- **Number of Shards**: 100 shards
- **Reasoning**: Lists are accessed by list_id

**Tasks Table:**
- **Shard Key**: `list_id` (aligned with lists)
- **Sharding Strategy**: Hash-based sharding
- **Number of Shards**: 100 shards
- **Reasoning**: Tasks are always accessed with list_id

**Shares Table:**
- **Shard Key**: `list_id` (aligned with lists)
- **Sharding Strategy**: Hash-based sharding
- **Number of Shards**: 100 shards
- **Reasoning**: Shares are accessed with list_id

**Reminders Table:**
- **Shard Key**: `scheduled_time` (time-based sharding)
- **Sharding Strategy**: Range-based sharding by time
- **Number of Shards**: 100 shards
- **Reasoning**: Reminders are queried by scheduled_time

**Notifications Table:**
- **Shard Key**: `user_id`
- **Sharding Strategy**: Hash-based sharding
- **Number of Shards**: 100 shards
- **Reasoning**: Notifications are accessed by user_id

**CollaborationEvents Table:**
- **Shard Key**: `list_id` (aligned with lists)
- **Sharding Strategy**: Hash-based sharding
- **Number of Shards**: 100 shards
- **Reasoning**: Events are accessed with list_id

## High-Level Design

```
┌─────────────────────────────────────────────────────────┐
│                    Client Applications                   │
│              (iOS, Android, Web)                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTPS / WebSocket
                     │
┌────────────────────▼────────────────────────────────────┐
│                  API Gateway / LB                        │
│              (Rate Limiting, Auth)                       │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
┌────────▼────────┐    ┌─────────▼─────────┐
│  Task Service  │    │  List Service     │
│ (CRUD Tasks)   │    │ (CRUD Lists)      │
└────────┬────────┘    └─────────┬──────────┘
         │                       │
         │                       │
┌────────▼───────────────────────▼──────────┐
│         Real-Time Service                │
│  (WebSocket, Event Broadcasting)         │
└────────┬──────────────────────────────────┘
         │
         │
┌────────▼──────────────────────────────────┐
│         Message Queue (Kafka)             │
│  (Collaboration Events, Notifications)    │
└────────┬──────────────────────────────────┘
         │
         │
┌────────▼──────────────────────────────────┐
│         Database Cluster                   │
│  (Lists, Tasks, Shares, Reminders)         │
└────────┬───────────────────────────────────┘
         │
         │
┌────────▼──────────────────────────────────┐
│      Reminder Scheduler Service           │
│  (Background Worker, Polls Reminders)      │
└────────┬──────────────────────────────────┘
         │
         │
┌────────▼──────────────────────────────────┐
│      Notification Service                  │
│  (Push Notifications, Email, SMS)         │
└────────────────────────────────────────────┘
```

## Deep Dive

### Component Design

#### 1. Task Service
- **Responsibilities**: Create, update, delete tasks, validate permissions
- **Optimization**: 
  - Fast task operations
  - Permission checking
  - Optimistic locking for conflict resolution

#### 2. List Service
- **Responsibilities**: Create, update, delete lists, manage shares
- **Optimization**:
  - Fast list operations
  - Share management
  - Permission validation

#### 3. Real-Time Service
- **Responsibilities**: WebSocket connections, event broadcasting
- **Optimization**:
  - Connection pooling
  - Efficient message routing
  - Presence management

#### 4. Reminder Scheduler Service
- **Responsibilities**: Poll reminders, trigger notifications
- **Optimization**:
  - Efficient polling (sorted by scheduled_time)
  - Batch processing
  - Timezone handling

#### 5. Notification Service
- **Responsibilities**: Send push notifications, email, SMS
- **Optimization**:
  - Multi-channel delivery
  - Batching
  - Retry logic

### Real-Time Synchronization

#### WebSocket Connection Management

**Connection Per List:**
- Each client opens WebSocket connection per active list
- Connection key: `ws:{user_id}:{list_id}`
- Heartbeat to keep connection alive

**Message Types:**
```json
// Task created
{
  "type": "task_created",
  "task_id": "task_123",
  "list_id": "list_456",
  "title": "Buy groceries",
  "created_by": "user_789",
  "timestamp": "2025-11-25T10:00:00Z"
}

// Task updated
{
  "type": "task_updated",
  "task_id": "task_123",
  "changes": {
    "title": "Buy groceries and cook",
    "priority": "high"
  },
  "updated_by": "user_789",
  "timestamp": "2025-11-25T10:05:00Z"
}

// Task completed
{
  "type": "task_completed",
  "task_id": "task_123",
  "completed_by": "user_789",
  "timestamp": "2025-11-25T10:10:00Z"
}
```

**Event Broadcasting:**
```python
def broadcast_task_update(list_id, event):
    # Get all WebSocket connections for list
    connections = websocket_manager.get_connections(list_id)
    
    # Broadcast to all connections
    for connection in connections:
        connection.send(json.dumps(event))
```

#### Event Sourcing

**Store All Events:**
- Every change stored as event
- Events used for:
  - Real-time sync
  - Conflict resolution
  - Audit trail
  - Offline sync

**Event Ordering:**
- Use timestamp + sequence number
- Client can replay events in order
- Handle out-of-order events

### Conflict Resolution

#### Challenge
Multiple users editing same task simultaneously.

#### Solution: Optimistic Locking + Operational Transformation

**Optimistic Locking:**
```python
def update_task(task_id, changes, user_id, expected_version):
    # Check version
    task = db.query("""
        SELECT version 
        FROM tasks 
        WHERE task_id = ?
    """, task_id)
    
    if task.version != expected_version:
        # Conflict detected
        raise ConflictError("Task was modified by another user")
    
    # Update task
    db.execute("""
        UPDATE tasks 
        SET title = ?, 
            version = version + 1,
            updated_at = NOW()
        WHERE task_id = ? 
        AND version = ?
    """, changes['title'], task_id, expected_version)
    
    # Create event
    create_event("task_updated", task_id, changes, user_id)
```

**Operational Transformation (OT):**
- Transform concurrent operations
- Apply operations in correct order
- Resolve conflicts automatically

**Last-Write-Wins (Simpler Alternative):**
- Accept last update
- Show conflict notification to user
- Let user choose which version to keep

### Reminder System

#### Reminder Scheduling

**Database Polling:**
```python
def poll_reminders():
    while True:
        # Get due reminders
        now = datetime.now()
        reminders = db.query("""
            SELECT * FROM reminders 
            WHERE scheduled_time <= ? 
            AND status = 'pending'
            ORDER BY scheduled_time ASC
            LIMIT 1000
        """, now)
        
        for reminder in reminders:
            # Get task and list
            task = get_task(reminder.task_id)
            list = get_list(task.list_id)
            
            # Get all collaborators
            collaborators = get_list_collaborators(list.list_id)
            
            # Create notifications
            for collaborator in collaborators:
                create_notification(
                    user_id=collaborator.user_id,
                    task_id=task.task_id,
                    list_id=list.list_id,
                    type='reminder',
                    message=f"Reminder: {task.title}"
                )
            
            # Update reminder status
            if reminder.recurring_pattern:
                # Schedule next occurrence
                next_time = calculate_next_occurrence(
                    reminder.scheduled_time,
                    reminder.recurring_pattern
                )
                db.execute("""
                    UPDATE reminders 
                    SET scheduled_time = ?
                    WHERE reminder_id = ?
                """, next_time, reminder.reminder_id)
            else:
                # Mark as sent
                db.execute("""
                    UPDATE reminders 
                    SET status = 'sent'
                    WHERE reminder_id = ?
                """, reminder.reminder_id)
        
        time.sleep(1)  # Poll every second
```

**Optimization:**
- Index on `scheduled_time` and `status`
- Batch processing (process 1000 at a time)
- Timezone handling (store timezone with reminder)

### Notification System

#### Multi-Channel Notifications

**Push Notifications:**
- iOS (APNs)
- Android (FCM)
- Web (Web Push)

**Email Notifications:**
- For important reminders
- Daily digest option

**In-App Notifications:**
- Real-time via WebSocket
- Notification badge

**Notification Delivery:**
```python
def send_notification(user_id, notification):
    # Get user preferences
    preferences = get_notification_preferences(user_id)
    
    # Send via preferred channels
    if preferences.push_enabled:
        send_push_notification(user_id, notification)
    
    if preferences.email_enabled:
        send_email_notification(user_id, notification)
    
    # Store notification
    db.execute("""
        INSERT INTO notifications 
        (notification_id, user_id, task_id, list_id, type, message)
        VALUES (?, ?, ?, ?, ?, ?)
    """, generate_id(), user_id, notification.task_id, 
           notification.list_id, notification.type, notification.message)
```

### Sharing and Permissions

#### Permission Model

**Permission Levels:**
- **Owner**: Full control (edit, delete, share)
- **Editor**: Can edit tasks, cannot delete list
- **Viewer**: Read-only access

**Permission Checking:**
```python
def check_permission(user_id, list_id, required_permission):
    # Get user's permission for list
    share = db.query("""
        SELECT permission 
        FROM shares 
        WHERE list_id = ? AND user_id = ?
    """, list_id, user_id)
    
    if not share:
        # Check if user is owner
        list = get_list(list_id)
        if list.owner_id == user_id:
            return True
        return False
    
    # Check permission level
    permission_levels = {'owner': 3, 'editor': 2, 'viewer': 1}
    required_level = permission_levels[required_permission]
    user_level = permission_levels[share.permission]
    
    return user_level >= required_level
```

### Scalability Considerations

#### Horizontal Scaling

**Task Service:**
- Stateless service
- Horizontal scaling (multiple instances)
- Load balanced

**Real-Time Service:**
- Multiple WebSocket servers
- Connection routing by list_id
- Message queue for cross-server communication

**Reminder Scheduler:**
- Multiple scheduler workers
- Partition reminders by scheduled_time
- Each worker handles subset of reminders

#### Database Scaling

**Read Replicas:**
- Use read replicas for queries
- Reduces load on primary database

**Sharding:**
- Shard by list_id, user_id, scheduled_time
- Distribute load across shards

**Caching:**
- Cache frequently accessed lists
- Cache user permissions
- Cache reminder schedules

### Failure Handling

#### WebSocket Connection Failure

**Scenario**: WebSocket connection drops.

**Solution:**
- Client reconnects automatically
- Server sends missed events on reconnect
- Use event sequence numbers to detect gaps

#### Reminder Missed

**Scenario**: Reminder not triggered (scheduler down).

**Solution:**
- Reconciliation job (find missed reminders)
- Retry missed reminders
- Alert on missed reminders

#### Conflict Resolution Failure

**Scenario**: Conflict cannot be resolved automatically.

**Solution:**
- Store conflict for manual resolution
- Notify users of conflict
- Provide conflict resolution UI

### Trade-offs and Optimizations

#### Trade-offs

1. **Consistency vs Latency**
   - **Choice**: Eventual consistency for cross-list operations
   - **Reason**: Better performance, lower latency
   - **Benefit**: Fast updates, good UX

2. **Real-Time vs Scalability**
   - **Choice**: WebSocket for real-time, message queue for scale
   - **Reason**: WebSocket for instant updates, queue for reliability
   - **Benefit**: Best of both worlds

3. **Conflict Resolution Complexity**
   - **Choice**: Optimistic locking + last-write-wins (simpler)
   - **Reason**: Balance correctness and complexity
   - **Benefit**: Good enough for most cases

#### Optimizations

1. **Event Batching**
   - Batch multiple events in single message
   - Reduces WebSocket messages
   - Better throughput

2. **Connection Pooling**
   - Pool WebSocket connections
   - Pool database connections
   - Better resource utilization

3. **Caching**
   - Cache list metadata
   - Cache user permissions
   - Cache reminder schedules
   - Reduces database queries

4. **Lazy Loading**
   - Load tasks on demand
   - Paginate task lists
   - Reduces initial load time

## What Interviewers Look For

### Distributed Systems Skills

1. **Real-Time Synchronization**
   - WebSocket architecture
   - Event broadcasting
   - Low-latency updates
   - **Red Flags**: Polling, high latency, no real-time

2. **Conflict Resolution**
   - Optimistic locking
   - Operational transformation
   - Conflict handling
   - **Red Flags**: No conflict handling, data loss, poor UX

3. **Event-Driven Architecture**
   - Event sourcing
   - Message queues
   - Event ordering
   - **Red Flags**: No events, no ordering, no audit trail

### Problem-Solving Approach

1. **Collaboration Design**
   - Real-time sync strategy
   - Conflict resolution approach
   - Permission model
   - **Red Flags**: No sync, no conflicts, no permissions

2. **Reminder System**
   - Scheduling approach
   - Notification delivery
   - Timezone handling
   - **Red Flags**: No scheduling, no notifications, no timezones

3. **Scalability**
   - Horizontal scaling
   - Database sharding
   - Caching strategy
   - **Red Flags**: Vertical scaling only, no sharding, no caching

### System Design Skills

1. **Component Design**
   - Clear service boundaries
   - Proper API design
   - Data flow understanding
   - **Red Flags**: Monolithic design, unclear boundaries, poor APIs

2. **Database Design**
   - Proper sharding strategy
   - Index design
   - Relationship modeling
   - **Red Flags**: No sharding, poor indexes, wrong relationships

3. **Real-Time Systems**
   - WebSocket management
   - Connection handling
   - Message routing
   - **Red Flags**: Poor connection handling, no routing, no management

### Communication Skills

1. **Clear Explanation**
   - Explains real-time sync approach
   - Discusses conflict resolution
   - Justifies design decisions
   - **Red Flags**: Unclear explanations, no justification, confusing

2. **Architecture Diagrams**
   - Clear component diagram
   - Shows data flow
   - Real-time sync flow
   - **Red Flags**: No diagrams, unclear diagrams, missing components

### Meta-Specific Focus

1. **Collaborative Systems**
   - Understanding of real-time collaboration
   - Conflict resolution patterns
   - Event-driven architecture
   - **Key**: Demonstrate collaborative systems expertise

2. **Real-Time Systems**
   - WebSocket expertise
   - Low-latency requirements
   - Event broadcasting
   - **Key**: Show real-time systems mastery

3. **Notification Systems**
   - Multi-channel delivery
   - Scheduling patterns
   - Reliability
   - **Key**: Demonstrate notification system expertise

## Summary

Designing a to-do list application with multi-user collaboration requires careful consideration of real-time synchronization, conflict resolution, reminder scheduling, and notification delivery. Key design decisions include:

**Architecture Highlights:**
- WebSocket for real-time synchronization
- Event-driven architecture with message queues
- Optimistic locking for conflict resolution
- Database polling for reminder scheduling
- Multi-channel notification delivery

**Key Patterns:**
- **Real-Time Sync**: WebSocket + event broadcasting
- **Conflict Resolution**: Optimistic locking + version numbers
- **Event Sourcing**: Store all changes as events
- **Reminder Scheduling**: Database polling with efficient indexing
- **Notification Delivery**: Multi-channel (push, email, in-app)

**Scalability Solutions:**
- Horizontal scaling (multiple service instances)
- Database sharding (by list_id, user_id, scheduled_time)
- Caching (lists, permissions, reminders)
- Connection pooling (WebSocket, database)

**Trade-offs:**
- Consistency vs latency (eventual consistency for better performance)
- Real-time vs scalability (WebSocket + message queue)
- Conflict resolution complexity (optimistic locking + last-write-wins)

This design handles 50M+ DAU, 1B+ tasks, and maintains < 200ms real-time sync latency while ensuring no data loss and proper conflict resolution. The system is scalable, fault-tolerant, and optimized for collaborative task management.

