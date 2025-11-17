---
layout: post
title: "Design Quickset with UEI - System Design Interview"
date: 2025-11-17
categories: [System Design, Interview Example, IoT, Smart Home, Device Management, Real-time Systems, Home Automation]
excerpt: "A comprehensive guide to designing Quickset with UEI integration, a smart home platform connecting Quickset TV mounts with UEI remote controls and smart devices, covering IoT device management, real-time control, device discovery, automation, and architectural patterns for supporting millions of connected devices."
---

## Introduction

Quickset with UEI is a smart home integration platform that connects Quickset TV mounting solutions with UEI (Universal Electronics Inc) remote controls and smart home devices. The system enables users to control their TV mounts, entertainment systems, and smart home devices through a unified platform, supporting device discovery, real-time control, automation, and voice integration.

This post provides a detailed walkthrough of designing Quickset with UEI, covering IoT device management, device discovery and pairing, real-time control protocols, automation rules, cloud synchronization, and integration with voice assistants. This is a system design interview question that tests your understanding of IoT systems, device management, real-time communication, automation, and handling millions of connected devices.

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Requirements](#requirements)
   - [Functional Requirements](#functional-requirements)
   - [Non-Functional Requirements](#non-functional-requirements)
3. [Capacity Estimation](#capacity-estimation)
   - [Traffic Estimates](#traffic-estimates)
   - [Storage Estimates](#storage-estimates)
   - [Bandwidth Estimates](#bandwidth-estimates)
4. [Core Entities](#core-entities)
5. [API](#api)
6. [Data Flow](#data-flow)
7. [Database Design](#database-design)
   - [Schema Design](#schema-design)
   - [Database Sharding Strategy](#database-sharding-strategy)
8. [High-Level Design](#high-level-design)
9. [Deep Dive](#deep-dive)
   - [Component Design](#component-design)
   - [Detailed Design](#detailed-design)
   - [Scalability Considerations](#scalability-considerations)
   - [Security Considerations](#security-considerations)
   - [Monitoring & Observability](#monitoring--observability)
   - [Trade-offs and Optimizations](#trade-offs-and-optimizations)
10. [Summary](#summary)

## Problem Statement

**Design Quickset with UEI, a smart home integration platform with the following features:**

1. Device discovery and pairing for Quickset mounts and UEI devices
2. Real-time control of TV mounts (tilt, swivel, extend)
3. Remote control functionality for entertainment devices via UEI
4. Device grouping and scene creation
5. Automation rules and scheduling
6. Voice assistant integration (Alexa, Google Assistant)
7. Mobile app for control and monitoring
8. Cloud synchronization and backup
9. Multi-user support with permissions
10. Firmware updates and device management

**Scale Requirements:**
- 50 million+ registered users
- 200 million+ connected devices (mounts, remotes, smart devices)
- 10 million+ concurrent active sessions
- 100K+ commands per second
- Must support real-time control with < 200ms latency
- Must handle device discovery in < 5 seconds
- Global deployment across multiple regions

## Requirements

### Functional Requirements

**Core Features:**
1. **Device Discovery**: Automatically discover Quickset mounts and UEI devices on local network
2. **Device Pairing**: Secure pairing and registration of devices
3. **Mount Control**: Control TV mount position (tilt, swivel, extend, retract)
4. **Remote Control**: Send IR/RF commands via UEI remotes to entertainment devices
5. **Device Groups**: Group multiple devices for coordinated control
6. **Scenes**: Create and execute scenes (e.g., "Movie Night" - adjust mount, turn on TV, dim lights)
7. **Automation**: Create rules based on time, events, or conditions
8. **Scheduling**: Schedule device actions at specific times
9. **Voice Control**: Integration with Alexa, Google Assistant, Siri
10. **Mobile App**: iOS and Android apps for control
11. **Multi-User**: Support multiple users per household with permissions
12. **Firmware Updates**: Over-the-air firmware updates for devices
13. **Device Status**: Real-time status monitoring and notifications
14. **History & Analytics**: Track device usage and energy consumption

**Out of Scope:**
- Device manufacturing (assume devices exist)
- Payment processing (assume existing)
- User authentication (assume existing OAuth)
- Video streaming (focus on control)

### Non-Functional Requirements

1. **Availability**: 99.9% uptime
2. **Reliability**: No command loss, device state consistency
3. **Performance**: 
   - Command latency: < 200ms for local devices, < 500ms for cloud
   - Device discovery: < 5 seconds
   - Scene execution: < 2 seconds
   - App responsiveness: < 100ms
4. **Scalability**: Handle 200M+ devices, 10M+ concurrent sessions
5. **Consistency**: Eventual consistency for device state, strong for critical commands
6. **Security**: End-to-end encryption, secure device pairing, authentication
7. **Offline Support**: Local control works offline, cloud sync when online

## Capacity Estimation

### Traffic Estimates

**Assumptions:**
- 50 million registered users
- 10 million daily active users (20% DAU rate)
- Average user has 4 devices
- Each device sends 10 status updates per hour
- Each user sends 20 commands per day
- Peak traffic: 3x average

**Read Traffic:**
- Status queries: 10M users × 4 devices × 10 updates/hour = 400M updates/hour = 111K updates/sec
- Device list queries: 10M users × 5 queries/day = 50M queries/day = 580 queries/sec
- Scene queries: 10M users × 2 queries/day = 20M queries/day = 231 queries/sec
- **Total reads**: ~112K reads/sec (peak: ~336K reads/sec)

**Write Traffic:**
- Commands: 10M users × 20 commands/day = 200M commands/day = 2.3K commands/sec
- Device registrations: 1M new devices/day = 12 registrations/sec
- Scene creations: 1M scenes/day = 12 scenes/sec
- Automation rules: 500K rules/day = 6 rules/sec
- **Total writes**: ~2.3K writes/sec (peak: ~7K writes/sec)

### Storage Estimates

**Assumptions:**
- Device metadata: 1KB per device
- Command history: 100 bytes per command, keep 90 days
- Scene data: 5KB per scene
- Automation rules: 2KB per rule
- User preferences: 2KB per user
- Firmware: 10MB per device type

**Storage Calculations:**
- Device metadata: 200M devices × 1KB = 200GB
- Command history: 200M commands/day × 90 days × 100 bytes = 1.8TB
- Scenes: 50M scenes × 5KB = 250GB
- Automation rules: 20M rules × 2KB = 40GB
- User preferences: 50M users × 2KB = 100GB
- Firmware: 100 device types × 10MB = 1GB
- **Total storage**: ~2.2TB (growing ~20GB/day)

### Bandwidth Estimates

**Assumptions:**
- Command: 500 bytes
- Status update: 200 bytes
- Device discovery: 2KB
- Firmware update: 10MB

**Bandwidth Calculations:**
- Commands: 2.3K commands/sec × 500 bytes = 1.15MB/sec = 9.2Mbps
- Status updates: 111K updates/sec × 200 bytes = 22.2MB/sec = 177.6Mbps
- Device discovery: 12 discoveries/sec × 2KB = 24KB/sec = 0.2Mbps
- Firmware updates: 100K updates/day × 10MB = 1TB/day = 92.6Mbps average
- **Total bandwidth**: ~280Mbps average, ~1Gbps peak

## Core Entities

**User**
- UserID, Email, Name, CreatedAt, LastLogin, Preferences

**Device**
- DeviceID, UserID, DeviceType (Mount/Remote/SmartDevice), Model, SerialNumber, MACAddress, IPAddress, FirmwareVersion, Status (Online/Offline), LastSeen, Location, Capabilities

**Mount**
- DeviceID, MountType (Fixed/Tilt/Swivel/FullMotion), MaxWeight, MaxTVSize, CurrentPosition (TiltAngle, SwivelAngle, Extension), Presets

**Remote**
- DeviceID, RemoteType (IR/RF/Bluetooth), SupportedDevices, BatteryLevel, LastUsed

**DeviceGroup**
- GroupID, UserID, Name, DeviceIDs[], CreatedAt

**Scene**
- SceneID, UserID, Name, Actions[], CreatedAt, LastExecuted

**AutomationRule**
- RuleID, UserID, Name, Trigger (Time/Event/Condition), Actions[], Enabled, CreatedAt

**Command**
- CommandID, UserID, DeviceID, CommandType, Parameters, Status (Pending/Success/Failed), Timestamp, ResponseTime

**FirmwareUpdate**
- UpdateID, DeviceType, Version, FileURL, ReleaseNotes, ReleasedAt, RolloutPercentage

## API

### Device Management

```http
POST /api/v1/devices/discover
Response: { devices: [Device] }

POST /api/v1/devices/pair
Body: { deviceId, pairingCode }
Response: { deviceId, accessToken }

GET /api/v1/devices
Response: { devices: [Device] }

GET /api/v1/devices/{deviceId}
Response: { device: Device }

PUT /api/v1/devices/{deviceId}
Body: { name, location }
Response: { device: Device }

DELETE /api/v1/devices/{deviceId}
Response: { success: true }
```

### Mount Control

```http
POST /api/v1/devices/{deviceId}/mount/position
Body: { tilt, swivel, extension }
Response: { success: true, position: {...} }

GET /api/v1/devices/{deviceId}/mount/position
Response: { position: { tilt, swivel, extension } }

POST /api/v1/devices/{deviceId}/mount/preset
Body: { presetName, position }
Response: { success: true }

POST /api/v1/devices/{deviceId}/mount/preset/{presetName}/recall
Response: { success: true }
```

### Remote Control

```http
POST /api/v1/devices/{deviceId}/remote/send
Body: { command, deviceType, repeat }
Response: { success: true }

POST /api/v1/devices/{deviceId}/remote/macro
Body: { commands: [{ command, delay }] }
Response: { success: true }
```

### Scenes & Automation

```http
POST /api/v1/scenes
Body: { name, actions: [{ deviceId, action, parameters }] }
Response: { scene: Scene }

POST /api/v1/scenes/{sceneId}/execute
Response: { success: true, executionTime }

GET /api/v1/scenes
Response: { scenes: [Scene] }

POST /api/v1/automations
Body: { name, trigger, actions, enabled }
Response: { automation: AutomationRule }

GET /api/v1/automations
Response: { automations: [AutomationRule] }
```

### Device Groups

```http
POST /api/v1/groups
Body: { name, deviceIds: [] }
Response: { group: DeviceGroup }

POST /api/v1/groups/{groupId}/control
Body: { action, parameters }
Response: { success: true }
```

## Data Flow

### Device Discovery Flow

1. User opens app and taps "Discover Devices"
2. App sends discovery request to Cloud Service
3. Cloud Service broadcasts discovery message via MQTT to local gateways
4. Local gateway (hub/router) performs mDNS/Bonjour discovery on local network
5. Devices respond with device info (type, model, capabilities)
6. Gateway aggregates responses and sends to Cloud Service
7. Cloud Service returns discovered devices to app
8. User selects device to pair
9. App initiates pairing flow with device
10. Device generates pairing code and displays it
11. User enters pairing code in app
12. App sends pairing request with code to Cloud Service
13. Cloud Service validates code and creates device registration
14. Device receives confirmation and establishes secure connection
15. App receives device registration confirmation

### Command Execution Flow

1. User sends command via mobile app (e.g., "Tilt mount 15 degrees")
2. App sends command to Cloud Service API
3. Cloud Service validates user permissions and device ownership
4. Cloud Service checks if device is online (local or cloud)
5. **Local Path** (device on same network):
   - Cloud Service routes command to Local Gateway via MQTT
   - Gateway forwards command to device via local protocol (WiFi/Bluetooth/Zigbee)
   - Device executes command and sends status update
   - Gateway forwards status to Cloud Service
   - Cloud Service updates device state in database
   - Cloud Service sends status update to app via WebSocket
6. **Cloud Path** (device not on local network):
   - Cloud Service sends command directly to device via MQTT/CoAP
   - Device executes command and sends status update
   - Cloud Service updates device state
   - Cloud Service sends status update to app
7. App receives status update and updates UI

### Scene Execution Flow

1. User taps scene button in app (e.g., "Movie Night")
2. App sends scene execution request to Cloud Service
3. Cloud Service retrieves scene definition from database
4. Cloud Service validates all devices in scene are accessible
5. Cloud Service executes scene actions in parallel:
   - For each action, follows command execution flow
   - Tracks execution status for each action
6. Cloud Service aggregates results and sends to app
7. App displays execution status

### Automation Rule Trigger Flow

1. Automation engine checks triggers periodically (time-based) or listens for events (event-based)
2. When trigger condition is met:
   - Automation engine retrieves rule from database
   - Validates rule is enabled and conditions are met
   - Executes rule actions (similar to scene execution)
   - Logs execution result
3. If rule has notifications enabled, sends notification to user

## Database Design

### Schema Design

**users**
```sql
CREATE TABLE users (
    user_id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    preferences JSONB,
    INDEX idx_email (email)
);
```

**devices**
```sql
CREATE TABLE devices (
    device_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    device_type ENUM('MOUNT', 'REMOTE', 'SMART_DEVICE') NOT NULL,
    model VARCHAR(100),
    serial_number VARCHAR(100) UNIQUE,
    mac_address VARCHAR(17) UNIQUE,
    ip_address VARCHAR(45),
    firmware_version VARCHAR(20),
    status ENUM('ONLINE', 'OFFLINE', 'UPDATING') DEFAULT 'OFFLINE',
    last_seen TIMESTAMP,
    location VARCHAR(100),
    capabilities JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_last_seen (last_seen)
);
```

**mounts**
```sql
CREATE TABLE mounts (
    device_id VARCHAR(36) PRIMARY KEY,
    mount_type ENUM('FIXED', 'TILT', 'SWIVEL', 'FULL_MOTION') NOT NULL,
    max_weight DECIMAL(5,2),
    max_tv_size INT,
    current_tilt DECIMAL(5,2),
    current_swivel DECIMAL(5,2),
    current_extension DECIMAL(5,2),
    presets JSONB,
    FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE
);
```

**remotes**
```sql
CREATE TABLE remotes (
    device_id VARCHAR(36) PRIMARY KEY,
    remote_type ENUM('IR', 'RF', 'BLUETOOTH') NOT NULL,
    supported_devices JSONB,
    battery_level INT,
    last_used TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE
);
```

**device_groups**
```sql
CREATE TABLE device_groups (
    group_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    INDEX idx_user_id (user_id)
);

CREATE TABLE device_group_members (
    group_id VARCHAR(36),
    device_id VARCHAR(36),
    PRIMARY KEY (group_id, device_id),
    FOREIGN KEY (group_id) REFERENCES device_groups(group_id) ON DELETE CASCADE,
    FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE
);
```

**scenes**
```sql
CREATE TABLE scenes (
    scene_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    actions JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_executed TIMESTAMP,
    execution_count INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    INDEX idx_user_id (user_id)
);
```

**automation_rules**
```sql
CREATE TABLE automation_rules (
    rule_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    trigger_type ENUM('TIME', 'EVENT', 'CONDITION') NOT NULL,
    trigger_config JSONB NOT NULL,
    actions JSONB NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_triggered TIMESTAMP,
    trigger_count INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    INDEX idx_user_id (user_id),
    INDEX idx_enabled (enabled),
    INDEX idx_trigger_type (trigger_type)
);
```

**commands**
```sql
CREATE TABLE commands (
    command_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    device_id VARCHAR(36),
    command_type VARCHAR(50) NOT NULL,
    parameters JSONB,
    status ENUM('PENDING', 'SUCCESS', 'FAILED', 'TIMEOUT') DEFAULT 'PENDING',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_time INT,
    error_message TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (device_id) REFERENCES devices(device_id),
    INDEX idx_user_id (user_id),
    INDEX idx_device_id (device_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_status (status)
) PARTITION BY RANGE (timestamp);
```

**firmware_updates**
```sql
CREATE TABLE firmware_updates (
    update_id VARCHAR(36) PRIMARY KEY,
    device_type VARCHAR(50) NOT NULL,
    version VARCHAR(20) NOT NULL,
    file_url VARCHAR(500),
    release_notes TEXT,
    released_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rollout_percentage INT DEFAULT 0,
    status ENUM('DRAFT', 'ROLLING_OUT', 'COMPLETED', 'ROLLED_BACK') DEFAULT 'DRAFT',
    INDEX idx_device_type (device_type),
    INDEX idx_status (status)
);
```

### Database Sharding Strategy

**Sharding by UserID:**
- Shard key: `user_id` (hash-based)
- Number of shards: 1000 (supports 50M users, ~50K users per shard)
- Benefits:
  - User data co-located (devices, scenes, automations)
  - Efficient queries for user-specific data
  - Easy to scale horizontally

**Partitioning for Time-Series Data:**
- `commands` table partitioned by `timestamp` (monthly partitions)
- Benefits:
  - Efficient queries for recent commands
  - Easy to archive old data
  - Better query performance

**Read Replicas:**
- 3 read replicas per shard for read scaling
- Read replicas handle status queries, device lists
- Write to primary, read from replicas

## High-Level Design

```
┌─────────────┐
│ Mobile Apps │ (iOS, Android)
└──────┬──────┘
       │ HTTPS/WebSocket
       │
┌──────▼──────────────────────────────────────────────┐
│              API Gateway / Load Balancer            │
└──────┬──────────────────────────────────────────────┘
       │
       ├─────────────────┬─────────────────┐
       │                 │                 │
┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐
│  API        │   │  WebSocket  │   │  Voice      │
│  Service    │   │  Service    │   │  Service    │
└──────┬──────┘   └──────┬──────┘   └──────┬──────┘
       │                 │                 │
       └─────────┬───────┴─────────────────┘
                 │
    ┌────────────▼────────────┐
    │   Message Queue (Kafka) │
    └────────────┬────────────┘
                 │
    ┌────────────┴────────────┐
    │                          │
┌───▼──────────┐      ┌───────▼────────┐
│  Device      │      │  Automation     │
│  Service     │      │  Service        │
└───┬──────────┘      └─────────────────┘
    │
    ├──────────────────┬──────────────────┐
    │                  │                  │
┌───▼──────────┐  ┌───▼──────────┐  ┌───▼──────────┐
│  Local       │  │  Cloud       │  │  Firmware    │
│  Gateway     │  │  Gateway     │  │  Service     │
│  Service     │  │  Service     │  │              │
└───┬──────────┘  └───┬──────────┘  └───┬──────────┘
    │                 │                  │
    │ MQTT/CoAP      │ MQTT/CoAP        │
    │                 │                  │
┌───▼──────────┐  ┌───▼──────────┐  ┌───▼──────────┐
│  Local       │  │  Cloud       │  │  Devices     │
│  Devices     │  │  Devices     │  │  (via        │
│  (WiFi/      │  │  (MQTT/      │  │  Gateway)    │
│  Bluetooth)  │  │  CoAP)       │  │              │
└──────────────┘  └──────────────┘  └──────────────┘

┌─────────────────────────────────────────────────────┐
│              Data Layer                              │
├─────────────────────────────────────────────────────┤
│  SQL Database (Sharded)  │  Redis Cache  │  S3     │
│  - Users, Devices        │  - Device     │  -      │
│  - Scenes, Automations    │    State      │  Firmware│
│  - Commands (partitioned) │  - Sessions   │         │
└─────────────────────────────────────────────────────┘
```

## Deep Dive

### Component Design

#### 1. API Service

**Responsibilities:**
- Handle HTTP requests from mobile apps
- Authentication and authorization
- Request validation and rate limiting
- Route requests to appropriate services
- Aggregate responses from multiple services

**Technology:**
- REST API: Node.js/Go/Python
- API Gateway: AWS API Gateway / Kong
- Rate Limiting: Redis-based rate limiter
- Authentication: JWT tokens

**Key Features:**
- Request validation and sanitization
- Rate limiting per user (1000 requests/minute)
- Request/response logging
- Circuit breakers for downstream services
- Response caching for device lists

#### 2. WebSocket Service

**Responsibilities:**
- Maintain persistent connections with mobile apps
- Push real-time device status updates
- Push notification events (automation triggers, device offline)
- Handle connection management and reconnection

**Technology:**
- WebSocket server: Node.js with Socket.io / Go with Gorilla WebSocket
- Connection management: Redis for connection state
- Message queue: Kafka for event distribution

**Key Features:**
- Connection pooling and load balancing
- Heartbeat mechanism (ping every 30 seconds)
- Automatic reconnection handling
- Message queuing for offline clients
- Room-based subscriptions (user-specific rooms)

**Scalability:**
- Horizontal scaling with sticky sessions
- Redis pub/sub for cross-server communication
- Connection limit: 10K connections per server

#### 3. Device Service

**Responsibilities:**
- Device registration and management
- Device discovery coordination
- Device state management
- Command routing (local vs cloud)
- Device health monitoring

**Technology:**
- Microservice: Go/Java
- State store: Redis
- Message queue: Kafka

**Key Features:**
- Device registry with capabilities
- Device state cache (Redis)
- Command queue management
- Device health checks (ping every 60 seconds)
- Offline detection (mark offline after 5 minutes of no response)

**Device State Management:**
- In-memory cache (Redis) for fast access
- Database for persistence
- Cache invalidation on state updates
- TTL-based expiration for offline devices

#### 4. Local Gateway Service

**Responsibilities:**
- Bridge between cloud and local network devices
- Handle local device discovery (mDNS/Bonjour)
- Route commands to local devices
- Aggregate device status updates
- Handle local network protocols (WiFi, Bluetooth, Zigbee)

**Technology:**
- Gateway software: Python/Go
- Local protocols: mDNS, CoAP, MQTT
- Network discovery: Bonjour, UPnP

**Key Features:**
- Automatic local network discovery
- Protocol translation (cloud MQTT → local protocols)
- Local command execution (low latency)
- Device status aggregation
- Offline operation support

**Architecture:**
- Runs on user's router/hub or dedicated gateway device
- Connects to cloud via MQTT
- Maintains local device registry
- Handles local device authentication

#### 5. Cloud Gateway Service

**Responsibilities:**
- Handle devices connected directly to cloud (not on local network)
- MQTT/CoAP message broker
- Device-to-cloud communication
- Command delivery to cloud-connected devices

**Technology:**
- MQTT Broker: Mosquitto / AWS IoT Core / HiveMQ
- CoAP Server: CoAP library
- Message queue: Kafka

**Key Features:**
- MQTT topic management (per device/user)
- QoS levels (0, 1, 2)
- Retained messages for device state
- Last Will and Testament for offline detection
- Message persistence

**MQTT Topics:**
- `devices/{deviceId}/commands` - Commands to device
- `devices/{deviceId}/status` - Status updates from device
- `users/{userId}/events` - User events (automations, notifications)

#### 6. Automation Service

**Responsibilities:**
- Evaluate automation rule triggers
- Execute automation actions
- Schedule time-based automations
- Handle event-based triggers
- Log automation executions

**Technology:**
- Microservice: Python/Go
- Scheduler: Cron / Quartz / Temporal
- Event stream: Kafka

**Key Features:**
- Time-based trigger evaluation (cron expressions)
- Event-based trigger listening (Kafka consumers)
- Condition evaluation engine
- Action execution orchestration
- Execution logging and monitoring

**Trigger Types:**
1. **Time-based**: Cron expressions, specific times
2. **Event-based**: Device state changes, user actions
3. **Condition-based**: Device state conditions, sensor readings

**Scalability:**
- Distributed scheduler (leader election)
- Partition automation rules by user
- Parallel execution of independent automations

#### 7. Firmware Service

**Responsibilities:**
- Manage firmware versions
- Coordinate firmware rollouts
- Handle firmware downloads
- Track update status
- Rollback failed updates

**Technology:**
- Microservice: Go/Python
- Storage: S3 for firmware files
- CDN: CloudFront for distribution

**Key Features:**
- Staged rollouts (1% → 10% → 50% → 100%)
- A/B testing support
- Rollback mechanism
- Update status tracking
- Delta updates (only send changes)

**Rollout Strategy:**
- Canary deployment: 1% → monitor → 10% → monitor → full rollout
- Device filtering: by model, region, firmware version
- Automatic rollback on high failure rate (>5%)

### Detailed Design

#### Device Discovery Process

**Step 1: Local Network Discovery**
1. User initiates discovery from mobile app
2. App sends discovery request to API Service
3. API Service checks if user has local gateway
4. If gateway exists:
   - API Service sends discovery command to Local Gateway via MQTT
   - Gateway performs mDNS/Bonjour scan on local network
   - Gateway sends discovered devices to API Service
5. If no gateway:
   - API Service performs cloud-based discovery (slower)
   - Checks device registry for unpaired devices in user's area

**Step 2: Device Pairing**
1. User selects device from discovered list
2. Device displays pairing code (6 digits)
3. User enters code in app
4. App sends pairing request: `POST /api/v1/devices/pair { deviceId, pairingCode }`
5. API Service validates pairing code with device
6. Device generates access token and returns to API Service
7. API Service creates device record in database
8. API Service establishes MQTT subscription for device
9. App receives device registration confirmation

**Security:**
- Pairing codes expire after 5 minutes
- One-time use pairing codes
- TLS encryption for pairing process
- Device authentication via certificates

#### Command Execution

**Local Command Path (Optimized):**
1. User sends command via app
2. API Service checks device location (local vs cloud)
3. If device is local:
   - API Service sends command to Local Gateway via MQTT
   - Gateway forwards to device via local protocol (WiFi/Bluetooth)
   - Device executes command (< 50ms latency)
   - Device sends status update to gateway
   - Gateway forwards to API Service via MQTT
   - API Service updates device state in Redis and database
   - API Service pushes status update to app via WebSocket
   - **Total latency: < 200ms**

**Cloud Command Path:**
1. User sends command via app
2. API Service routes to Cloud Gateway
3. Cloud Gateway publishes command to MQTT topic: `devices/{deviceId}/commands`
4. Device receives command via MQTT
5. Device executes command
6. Device publishes status to: `devices/{deviceId}/status`
7. Cloud Gateway forwards to API Service
8. API Service updates state and pushes to app
9. **Total latency: < 500ms**

**Command Reliability:**
- MQTT QoS 1 (at least once delivery)
- Command acknowledgment required
- Retry mechanism (3 retries, exponential backoff)
- Command timeout (5 seconds)
- Command status tracking in database

#### Scene Execution

**Parallel Execution:**
1. User triggers scene
2. API Service retrieves scene definition
3. API Service validates all devices are accessible
4. API Service executes actions in parallel:
   - Creates command tasks for each action
   - Executes commands concurrently
   - Tracks execution status
5. API Service aggregates results
6. API Service sends execution summary to app

**Error Handling:**
- If device is offline: skip action, log error
- If command fails: retry once, then mark failed
- Partial success: return success with failed actions list
- Rollback: optional rollback on critical failures

#### Automation Rule Engine

**Time-Based Triggers:**
- Distributed cron scheduler
- Evaluates rules every minute
- Executes matching rules
- Handles timezone correctly

**Event-Based Triggers:**
- Kafka consumer listens to device events
- Filters events matching trigger conditions
- Evaluates additional conditions
- Executes actions if all conditions met

**Condition Evaluation:**
- Supports: equals, greater than, less than, contains, regex
- Boolean logic: AND, OR, NOT
- Device state conditions
- Time-based conditions
- User presence conditions

**Execution:**
- Similar to scene execution
- Logs all executions
- Rate limiting (max 10 executions per rule per hour)
- Failure notifications

### Scalability Considerations

#### Horizontal Scaling

**API Service:**
- Stateless design enables horizontal scaling
- Load balancer distributes requests
- Session state in Redis (not server memory)
- Auto-scaling based on CPU/memory metrics

**WebSocket Service:**
- Sticky sessions for connection affinity
- Redis pub/sub for cross-server communication
- Connection limit: 10K per server
- Auto-scaling based on connection count

**Device Service:**
- Partitioned by user ID
- Stateless design
- Cache layer (Redis) for device state
- Database read replicas for scaling reads

**Message Queue:**
- Kafka partitions for parallel processing
- Partition by user ID for ordering
- Consumer groups for parallel consumption
- Auto-scaling consumers

#### Caching Strategy

**Redis Cache Layers:**
1. **Device State Cache**: TTL 5 minutes
   - Key: `device:{deviceId}:state`
   - Value: JSON device state
2. **User Device List Cache**: TTL 1 minute
   - Key: `user:{userId}:devices`
   - Value: List of device IDs
3. **Scene Cache**: TTL 5 minutes
   - Key: `scene:{sceneId}`
   - Value: Scene definition
4. **Session Cache**: TTL 24 hours
   - Key: `session:{sessionId}`
   - Value: User session data

**Cache Invalidation:**
- Device state: invalidate on state update
- Device list: invalidate on device add/remove
- Scene: invalidate on scene update
- Write-through cache for critical data

#### Database Optimization

**Indexing:**
- User ID indexes for user queries
- Device ID indexes for device queries
- Timestamp indexes for time-range queries
- Composite indexes for common query patterns

**Query Optimization:**
- Avoid N+1 queries (batch loading)
- Use database connection pooling
- Read from replicas for non-critical queries
- Pagination for large result sets

**Partitioning:**
- Commands table partitioned by timestamp (monthly)
- Archive old partitions to cold storage
- Reduces query time for recent data

### Security Considerations

#### Authentication & Authorization

**User Authentication:**
- OAuth 2.0 / JWT tokens
- Token expiration: 24 hours
- Refresh tokens: 30 days
- Multi-factor authentication (optional)

**Device Authentication:**
- Certificate-based authentication
- Device certificates issued during pairing
- Certificate rotation every 90 days
- Revocation list for compromised devices

**Authorization:**
- Role-based access control (RBAC)
- User permissions: Owner, Admin, Guest
- Device-level permissions
- Scene/automation permissions

#### Data Encryption

**In Transit:**
- TLS 1.3 for all API communication
- MQTT over TLS (MQTTS)
- WebSocket over TLS (WSS)
- End-to-end encryption for sensitive commands

**At Rest:**
- Database encryption (AES-256)
- Encrypted backups
- Key management via AWS KMS / HashiCorp Vault

#### Device Security

**Pairing Security:**
- Time-limited pairing codes (5 minutes)
- One-time use codes
- Rate limiting on pairing attempts
- IP-based restrictions

**Command Security:**
- Command signing (HMAC)
- Replay attack prevention (nonces)
- Command validation on device
- Rate limiting per device

**Firmware Security:**
- Signed firmware updates
- Secure boot verification
- Rollback protection
- Update authentication

#### Network Security

**Local Network:**
- Device isolation (VLAN)
- Firewall rules
- Intrusion detection
- Network segmentation

**Cloud Security:**
- DDoS protection (Cloudflare)
- Rate limiting
- IP whitelisting for gateways
- VPN for gateway connections

### Monitoring & Observability

#### Metrics

**System Metrics:**
- Request rate (QPS)
- Error rate (4xx, 5xx)
- Latency (p50, p95, p99)
- Throughput

**Device Metrics:**
- Online device count
- Command success rate
- Average command latency
- Device discovery time
- Firmware update success rate

**Business Metrics:**
- Daily active users
- Devices per user
- Commands per user
- Scene executions
- Automation triggers

**Monitoring Tools:**
- Prometheus for metrics collection
- Grafana for visualization
- CloudWatch / Datadog for cloud metrics
- Custom dashboards

#### Logging

**Log Levels:**
- ERROR: Failures, exceptions
- WARN: Degraded performance, retries
- INFO: Important events, state changes
- DEBUG: Detailed debugging information

**Log Aggregation:**
- Centralized logging (ELK Stack / Splunk)
- Structured logging (JSON)
- Log retention: 30 days
- Search and analysis capabilities

**Key Log Events:**
- Device discovery and pairing
- Command executions
- Scene executions
- Automation triggers
- Firmware updates
- Error conditions

#### Alerting

**Critical Alerts:**
- Service downtime
- High error rate (>1%)
- High latency (p95 > 1s)
- Database connection failures
- Message queue backlog

**Warning Alerts:**
- Elevated error rate (>0.5%)
- High latency (p95 > 500ms)
- Low device online rate
- High command failure rate

**Alert Channels:**
- PagerDuty for critical alerts
- Slack for warnings
- Email for informational alerts
- SMS for on-call engineers

#### Distributed Tracing

**Tracing:**
- OpenTelemetry / Jaeger
- Trace requests across services
- Identify bottlenecks
- Debug distributed issues

**Trace Points:**
- API request entry
- Service calls
- Database queries
- Message queue operations
- External API calls

### Trade-offs and Optimizations

#### Local vs Cloud Control

**Trade-off:**
- Local control: Lower latency (< 200ms) but requires gateway
- Cloud control: Higher latency (< 500ms) but works everywhere

**Optimization:**
- Prefer local control when gateway available
- Fallback to cloud control
- Hybrid approach: local for commands, cloud for state sync

#### Consistency vs Availability

**Trade-off:**
- Strong consistency: Slower, more complex
- Eventual consistency: Faster, simpler

**Decision:**
- Eventual consistency for device state (acceptable delay)
- Strong consistency for critical commands (mount position)
- Conflict resolution for concurrent updates

#### Caching vs Freshness

**Trade-off:**
- Aggressive caching: Better performance, stale data
- Less caching: Fresh data, higher latency

**Optimization:**
- Cache device state (TTL 5 minutes)
- Invalidate on updates
- Use WebSocket for real-time updates
- Cache device lists (TTL 1 minute)

#### Batch vs Individual Commands

**Trade-off:**
- Individual commands: Simpler, higher overhead
- Batch commands: More efficient, more complex

**Optimization:**
- Batch commands in scenes
- Individual commands for single actions
- Command queuing for offline devices

#### Synchronous vs Asynchronous Processing

**Trade-off:**
- Synchronous: Simpler, blocks request
- Asynchronous: More complex, non-blocking

**Decision:**
- Synchronous for simple commands
- Asynchronous for scenes and automations
- Background processing for firmware updates

## Summary

**Key Takeaways:**

1. **Architecture**: Microservices architecture with API Gateway, WebSocket service, Device service, Local/Cloud gateways, Automation service, and Firmware service

2. **Device Communication**: Hybrid approach with local gateway for low-latency local control and cloud gateway for remote access

3. **Scalability**: Horizontal scaling with stateless services, caching (Redis), database sharding, and message queues (Kafka)

4. **Real-Time Updates**: WebSocket for app updates, MQTT for device communication, Redis pub/sub for service communication

5. **Device Discovery**: mDNS/Bonjour for local discovery, cloud-based discovery as fallback

6. **Automation**: Distributed rule engine with time-based, event-based, and condition-based triggers

7. **Security**: End-to-end encryption, certificate-based device authentication, secure pairing, command signing

8. **Reliability**: Command retries, offline support, device health monitoring, graceful degradation

**Design Highlights:**

- **Low Latency**: Local gateway enables < 200ms command latency
- **Offline Support**: Local control works offline, cloud sync when online
- **Scalability**: Handles 200M+ devices, 10M+ concurrent sessions
- **Reliability**: 99.9% uptime, no command loss, device state consistency
- **Security**: End-to-end encryption, secure device pairing, authentication

**Common Interview Topics Covered:**
- IoT device management
- Real-time communication (WebSocket, MQTT)
- Device discovery and pairing
- Automation and scheduling
- Microservices architecture
- Caching strategies
- Database sharding
- Message queues
- Security and encryption
- Monitoring and observability

This design demonstrates how to build a scalable, reliable, and secure IoT platform that connects millions of devices while maintaining low latency and high availability. The hybrid local/cloud architecture optimizes for both performance and accessibility.

