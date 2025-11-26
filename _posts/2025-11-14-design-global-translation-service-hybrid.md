---
layout: post
title: "Design a Global Translation Service with Hybrid Mode - System Design Interview"
date: 2025-11-14
categories: [System Design, Interview Example, Distributed Systems, Mobile Applications, Offline-First, Machine Learning, Edge Computing]
excerpt: "A comprehensive guide to designing a global translation service with hybrid mode that works offline using local translation models and switches to remote server translation when online, covering offline-first architecture, model management, network detection, caching strategies, and synchronization patterns."
---

## Introduction

A global translation service with hybrid mode provides seamless translation capabilities that work both offline and online. When offline, it uses local translation models stored on the device. When online, it can use remote server translation for better accuracy and support for more language pairs. This pattern is essential for mobile applications that need to work in areas with poor connectivity.

This post provides a detailed walkthrough of designing a hybrid translation service, covering offline-first architecture, local model management, network detection, remote translation API, caching strategies, model updates, and synchronization between local and remote translations. This is a common system design interview question that tests your understanding of distributed systems, mobile architecture, offline-first design, ML model deployment, and edge computing.

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

**Design a global translation service with hybrid mode that:**

1. Works offline using local translation models
2. Uses remote server translation when online (WiFi or cellular)
3. Automatically switches between local and remote modes
4. Supports 100+ language pairs
5. Caches translations for offline access
6. Updates local models periodically
7. Syncs translation history across devices
8. Provides consistent translation quality
9. Handles network failures gracefully
10. Supports batch translation

**Scale Requirements:**
- 100 million+ users
- 1 billion+ translations per day
- Peak: 100,000 translations per second
- Average translation length: 50 words
- Local model size: 50-200MB per language pair
- Must work completely offline
- Network detection latency: < 100ms
- Translation latency: < 500ms (local), < 2s (remote)

## Requirements

### Functional Requirements

**Core Features:**
1. **Translation**: Translate text between languages
2. **Hybrid Mode**: Automatic switching between local and remote
3. **Network Detection**: Detect WiFi, cellular, or offline
4. **Local Models**: Download and manage local translation models
5. **Translation Cache**: Cache translations for offline access
6. **Batch Translation**: Translate multiple texts at once
7. **Language Detection**: Auto-detect source language
8. **Model Updates**: Update local models periodically
9. **Translation History**: Store translation history
10. **Sync Across Devices**: Sync translations across user devices

**Out of Scope:**
- Real-time voice translation
- Image translation (OCR + translation)
- Video subtitle translation
- Translation quality scoring
- User authentication (assume existing auth system)

### Non-Functional Requirements

1. **Availability**: 99.9% uptime (remote), 100% availability (local)
2. **Reliability**: No translation loss, graceful degradation
3. **Performance**: 
   - Local translation: < 500ms
   - Remote translation: < 2 seconds
   - Network detection: < 100ms
   - Cache lookup: < 10ms
4. **Scalability**: Handle 100K+ translations per second
5. **Offline Support**: Full functionality offline
6. **Storage Efficiency**: Minimize local storage usage
7. **Battery Efficiency**: Minimize battery drain

## Capacity Estimation

### Traffic Estimates

- **Total Users**: 100 million
- **Daily Active Users (DAU)**: 10 million
- **Translations per Day**: 1 billion
- **Peak Translation Rate**: 100,000 per second
- **Normal Translation Rate**: 10,000 per second
- **Offline Translations**: 30% (300 million per day)
- **Online Translations**: 70% (700 million per day)
- **Average Text Length**: 50 words = 250 characters

### Storage Estimates

**Local Models (per device):**
- Popular language pairs: 20 pairs × 100MB = 2GB
- All language pairs: 100 pairs × 100MB = 10GB
- Average user: 5 pairs × 100MB = 500MB

**Translation Cache (per device):**
- 10,000 cached translations × 1KB = 10MB
- 100,000 cached translations × 1KB = 100MB

**Remote Storage:**
- Translation history: 1B translations/day × 500 bytes = 500GB/day
- 30-day retention: ~15TB
- Model storage: 100 language pairs × 200MB = 20GB

**Total Storage**: ~15TB

### Bandwidth Estimates

**Normal Traffic:**
- 10,000 translations/sec × 2KB = 20MB/s = 160Mbps
- Request + response data

**Peak Traffic:**
- 100,000 translations/sec × 2KB = 200MB/s = 1.6Gbps

**Model Downloads:**
- 1M model downloads/day × 100MB = 100TB/day = ~1.16GB/s = ~9.3Gbps

**Total Peak**: ~11Gbps

## Core Entities

### Translation Request
- `request_id` (UUID)
- `user_id` (UUID)
- `source_language` (VARCHAR)
- `target_language` (VARCHAR)
- `source_text` (TEXT)
- `translation_mode` (local, remote, hybrid)
- `network_status` (wifi, cellular, offline)
- `created_at` (TIMESTAMP)

### Translation Result
- `result_id` (UUID)
- `request_id` (UUID)
- `translated_text` (TEXT)
- `confidence_score` (FLOAT)
- `translation_mode` (local, remote)
- `model_version` (VARCHAR)
- `latency_ms` (INT)
- `created_at` (TIMESTAMP)

### Translation Cache
- `cache_key` (VARCHAR, hash of source_text + languages)
- `source_text` (TEXT)
- `source_language` (VARCHAR)
- `target_language` (VARCHAR)
- `translated_text` (TEXT)
- `created_at` (TIMESTAMP)
- `last_accessed_at` (TIMESTAMP)
- `access_count` (INT)

### Local Model
- `model_id` (UUID)
- `language_pair` (VARCHAR, e.g., "en-fr")
- `model_version` (VARCHAR)
- `model_size_bytes` (BIGINT)
- `model_file_path` (VARCHAR)
- `download_url` (VARCHAR)
- `is_downloaded` (BOOLEAN)
- `download_progress` (INT, percentage)
- `last_updated_at` (TIMESTAMP)

### Translation History
- `history_id` (UUID)
- `user_id` (UUID)
- `source_text` (TEXT)
- `translated_text` (TEXT)
- `source_language` (VARCHAR)
- `target_language` (VARCHAR)
- `translation_mode` (VARCHAR)
- `device_id` (VARCHAR)
- `created_at` (TIMESTAMP)

## API

### 1. Translate Text
```
POST /api/v1/translate
Request:
{
  "source_text": "Hello, how are you?",
  "source_language": "en",
  "target_language": "fr",
  "mode": "auto",  // auto, local, remote
  "cache_enabled": true
}

Response:
{
  "request_id": "uuid",
  "translated_text": "Bonjour, comment allez-vous?",
  "source_language": "en",
  "target_language": "fr",
  "translation_mode": "local",
  "confidence_score": 0.95,
  "model_version": "v2.1",
  "latency_ms": 350,
  "cached": false
}
```

### 2. Batch Translate
```
POST /api/v1/translate/batch
Request:
{
  "texts": [
    "Hello",
    "Goodbye",
    "Thank you"
  ],
  "source_language": "en",
  "target_language": "fr",
  "mode": "auto"
}

Response:
{
  "translations": [
    {
      "source_text": "Hello",
      "translated_text": "Bonjour",
      "translation_mode": "local"
    },
    {
      "source_text": "Goodbye",
      "translated_text": "Au revoir",
      "translation_mode": "local"
    },
    {
      "source_text": "Thank you",
      "translated_text": "Merci",
      "translation_mode": "local"
    }
  ]
}
```

### 3. Detect Language
```
POST /api/v1/translate/detect
Request:
{
  "text": "Bonjour, comment allez-vous?"
}

Response:
{
  "detected_language": "fr",
  "confidence": 0.98
}
```

### 4. Get Available Languages
```
GET /api/v1/languages
Response:
{
  "languages": [
    {
      "code": "en",
      "name": "English",
      "local_model_available": true,
      "model_size_mb": 120
    },
    {
      "code": "fr",
      "name": "French",
      "local_model_available": true,
      "model_size_mb": 115
    }
  ],
  "total": 100
}
```

### 5. Download Local Model
```
POST /api/v1/models/download
Request:
{
  "language_pair": "en-fr",
  "priority": "high"
}

Response:
{
  "model_id": "uuid",
  "language_pair": "en-fr",
  "download_url": "https://...",
  "model_size_mb": 120,
  "estimated_download_time_seconds": 60
}
```

### 6. Get Translation History
```
GET /api/v1/translations/history?limit=20&offset=0
Response:
{
  "translations": [
    {
      "history_id": "uuid",
      "source_text": "Hello",
      "translated_text": "Bonjour",
      "source_language": "en",
      "target_language": "fr",
      "created_at": "2025-11-13T10:00:00Z"
    }
  ],
  "total": 100,
  "limit": 20,
  "offset": 0
}
```

## Data Flow

### Translation Flow (Online - Remote Mode)

1. **User Requests Translation**:
   - User submits text for translation
   - **Client SDK** detects network status (WiFi/cellular)
   - Chooses remote mode

2. **Cache Check**:
   - **Client SDK** checks local cache
   - Cache hit: Returns cached translation
   - Cache miss: Proceeds to remote

3. **Remote Translation**:
   - **Client SDK** sends request to **API Gateway**
   - **API Gateway** routes to **Translation Service**
   - **Translation Service**:
     - Uses remote ML model or API
     - Generates translation
     - Returns result

4. **Cache Update**:
   - **Client SDK** stores translation in local cache
   - Updates cache statistics

5. **Response**:
   - **Client SDK** returns translation to user
   - Updates UI

### Translation Flow (Offline - Local Mode)

1. **User Requests Translation**:
   - User submits text for translation
   - **Client SDK** detects offline status
   - Chooses local mode

2. **Cache Check**:
   - **Client SDK** checks local cache
   - Cache hit: Returns cached translation
   - Cache miss: Proceeds to local model

3. **Local Model Translation**:
   - **Client SDK**:
     - Loads local translation model
     - Runs inference on device
     - Generates translation

4. **Cache Update**:
   - **Client SDK** stores translation in local cache
   - Updates cache statistics

5. **Response**:
   - **Client SDK** returns translation to user
   - Updates UI

### Translation Flow (Hybrid Mode - Auto)

1. **User Requests Translation**:
   - User submits text for translation
   - **Client SDK** detects network status

2. **Mode Selection**:
   - **Network Manager**:
     - Checks network connectivity
     - Checks network quality (WiFi vs cellular)
     - Checks local model availability
     - Selects optimal mode

3. **Translation Execution**:
   - If online + good connection: Use remote
   - If online + poor connection: Use local
   - If offline: Use local
   - If local model unavailable: Use remote (if online)

4. **Fallback Handling**:
   - If remote fails: Fallback to local
   - If local fails: Return error or cached result

5. **Response**:
   - **Client SDK** returns translation
   - Updates UI

### Model Download Flow

1. **User Requests Model Download**:
   - User selects language pair to download
   - **Client SDK** sends download request

2. **Download Preparation**:
   - **Model Service**:
     - Validates language pair
     - Gets model metadata
     - Generates download URL

3. **Model Download**:
   - **Client SDK**:
     - Downloads model file
     - Shows progress
     - Validates download integrity

4. **Model Installation**:
   - **Client SDK**:
     - Extracts model file
     - Stores in local storage
     - Registers model with translation engine

5. **Verification**:
   - **Client SDK** verifies model works
   - Updates model status

## Database Design

### Schema Design

**Translation History Table (Sharded by user_id):**
```sql
CREATE TABLE translation_history_0 (
    history_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    source_text TEXT NOT NULL,
    translated_text TEXT NOT NULL,
    source_language VARCHAR(10) NOT NULL,
    target_language VARCHAR(10) NOT NULL,
    translation_mode VARCHAR(20) NOT NULL,
    device_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at DESC),
    INDEX idx_user_created (user_id, created_at DESC)
);
-- Similar tables: translation_history_1, ..., translation_history_N
```

**Translation Cache Table (Local - SQLite/Realm):**
```sql
CREATE TABLE translation_cache (
    cache_key VARCHAR(64) PRIMARY KEY,
    source_text TEXT NOT NULL,
    source_language VARCHAR(10) NOT NULL,
    target_language VARCHAR(10) NOT NULL,
    translated_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_accessed_at TIMESTAMP DEFAULT NOW(),
    access_count INT DEFAULT 1,
    INDEX idx_languages (source_language, target_language),
    INDEX idx_last_accessed (last_accessed_at DESC)
);
```

**Local Models Table (Local - SQLite/Realm):**
```sql
CREATE TABLE local_models (
    model_id UUID PRIMARY KEY,
    language_pair VARCHAR(20) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    model_size_bytes BIGINT NOT NULL,
    model_file_path VARCHAR(500) NOT NULL,
    is_downloaded BOOLEAN DEFAULT FALSE,
    download_progress INT DEFAULT 0,
    last_updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE KEY uk_language_pair (language_pair)
);
```

**Model Metadata Table:**
```sql
CREATE TABLE model_metadata (
    model_id UUID PRIMARY KEY,
    language_pair VARCHAR(20) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    model_size_bytes BIGINT NOT NULL,
    download_url VARCHAR(1000) NOT NULL,
    checksum VARCHAR(64) NOT NULL,
    supported_features JSON,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE KEY uk_language_version (language_pair, model_version)
);
```

### Database Sharding Strategy

**Translation History Table Sharding:**
- Shard by user_id using consistent hashing
- 1000 shards: `shard_id = hash(user_id) % 1000`
- All translations for a user in same shard
- Enables efficient user history queries

**Shard Key Selection:**
- `user_id` ensures all translations for a user are in same shard
- Enables efficient queries for user translation history
- Prevents cross-shard queries for single user

**Replication:**
- Each shard replicated 3x for high availability
- Master-replica setup for read scaling
- Writes go to master, reads can go to replicas

## High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Mobile/Web Client                         │
│                                                              │
│  ┌──────────────┐                                           │
│  │ Client SDK   │                                           │
│  │ - Network   │                                           │
│  │   Detection  │                                           │
│  │ - Mode      │                                           │
│  │   Selection │                                           │
│  │ - Cache     │                                           │
│  │   Manager   │                                           │
│  └──────┬───────┘                                           │
│         │                                                    │
│         ├──────────────────┬──────────────────┐            │
│         │                  │                  │            │
│  ┌──────▼──────┐  ┌───────▼──────┐  ┌───────▼──────┐     │
│  │ Local       │  │ Remote       │  │ Cache         │     │
│  │ Translation │  │ Translation  │  │ Manager       │     │
│  │ Engine      │  │ Client       │  │               │     │
│  └──────┬──────┘  └───────┬──────┘  └───────┬──────┘     │
│         │                  │                  │            │
│  ┌──────▼──────────────────▼──────────────────▼──────┐     │
│  │         Local Storage (SQLite/Realm)              │     │
│  │  - Translation models                             │     │
│  │  - Translation cache                               │     │
│  │  - Translation history                             │     │
│  └───────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
         │
         │ HTTP/HTTPS (when online)
         │
┌────────▼───────────────────────────────────────────────────┐
│        API Gateway / Load Balancer                           │
│        - Rate Limiting                                       │
│        - Request Routing                                     │
└────────┬───────────────────────────────────────────────────┘
         │
         │
┌────────▼───────────────────────────────────────────────────┐
│         Translation Service                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│  │ ML Model │  │ API      │  │ Cache    │                │
│  │ Service  │  │ Gateway  │  │ Service  │                │
│  └──────────┘  └──────────┘  └──────────┘                │
└────────┬───────────────────────────────────────────────────┘
         │
         │
┌────────▼───────────────────────────────────────────────────┐
│         Model Service                                        │
│         - Model metadata                                     │
│         - Model downloads                                    │
│         - Model updates                                      │
└────────┬───────────────────────────────────────────────────┘
         │
         │
┌────────▼───────────────────────────────────────────────────┐
│         Database Cluster (Sharded)                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│  │ History  │  │ Model    │  │ Cache    │                │
│  │ (Sharded)│  │ Metadata │  │ DB       │                │
│  └──────────┘  └──────────┘  └──────────┘                │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│         Object Storage (S3)                                  │
│         - Translation models                                │
│         - Model versions                                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│         CDN                                                   │
│         - Model distribution                                 │
│         - Fast downloads                                     │
└─────────────────────────────────────────────────────────────┘
```

## Deep Dive

### Component Design

#### 1. Network Detection Manager

**Responsibilities:**
- Detect network connectivity
- Determine network type (WiFi, cellular, offline)
- Measure network quality
- Provide network status to translation service

**Key Design Decisions:**
- **Fast Detection**: < 100ms detection latency
- **Accurate Status**: Reliable network detection
- **Battery Efficient**: Minimal battery drain
- **Platform Agnostic**: Works on iOS, Android, Web

**Implementation:**
```python
class NetworkDetectionManager:
    def __init__(self):
        self.network_status = 'unknown'
        self.last_check = None
        self.check_interval = 5  # seconds
    
    def get_network_status(self):
        """Get current network status"""
        # Check if cached status is recent
        if self.last_check and (time.time() - self.last_check) < self.check_interval:
            return self.network_status
        
        # Detect network
        status = self.detect_network()
        self.network_status = status
        self.last_check = time.time()
        
        return status
    
    def detect_network(self):
        """Detect network connectivity"""
        try:
            # Try to reach a lightweight endpoint
            response = requests.get(
                'https://api.translation.com/health',
                timeout=0.1  # 100ms timeout
            )
            
            if response.status_code == 200:
                # Check connection type
                connection_type = self.get_connection_type()
                return {
                    'status': 'online',
                    'type': connection_type,  # wifi, cellular
                    'quality': self.measure_quality()
                }
        except:
            pass
        
        return {
            'status': 'offline',
            'type': None,
            'quality': None
        }
    
    def get_connection_type(self):
        """Get connection type (WiFi or cellular)"""
        # Platform-specific implementation
        # iOS: Use Reachability framework
        # Android: Use ConnectivityManager
        # Web: Use Network Information API
        
        # Example for web
        if hasattr(navigator, 'connection'):
            connection = navigator.connection
            if connection.type == 'wifi':
                return 'wifi'
            elif connection.type in ['cellular', '2g', '3g', '4g', '5g']:
                return 'cellular'
        
        return 'unknown'
    
    def measure_quality(self):
        """Measure network quality"""
        # Measure latency and bandwidth
        # Return: 'excellent', 'good', 'poor'
        
        try:
            start = time.time()
            requests.get('https://api.translation.com/ping', timeout=1)
            latency = (time.time() - start) * 1000  # ms
            
            if latency < 100:
                return 'excellent'
            elif latency < 500:
                return 'good'
            else:
                return 'poor'
        except:
            return 'poor'
    
    def should_use_remote(self, network_status):
        """Determine if should use remote translation"""
        if network_status['status'] == 'offline':
            return False
        
        if network_status['type'] == 'wifi':
            return True
        
        if network_status['type'] == 'cellular':
            # Use remote only if quality is good
            return network_status['quality'] in ['excellent', 'good']
        
        return False
```

#### 2. Translation Mode Selector

**Responsibilities:**
- Select optimal translation mode
- Balance between local and remote
- Handle fallbacks
- Optimize for user experience

**Key Design Decisions:**
- **Smart Selection**: Choose best mode based on context
- **Fallback Strategy**: Graceful fallback on failure
- **User Preference**: Respect user preferences
- **Performance**: Fast mode selection

**Implementation:**
```python
class TranslationModeSelector:
    def __init__(self, network_manager, cache_manager, model_manager):
        self.network_manager = network_manager
        self.cache_manager = cache_manager
        self.model_manager = model_manager
    
    def select_mode(self, source_language, target_language, user_preference='auto'):
        """Select optimal translation mode"""
        # Check user preference
        if user_preference == 'local':
            return self._select_local_mode(source_language, target_language)
        elif user_preference == 'remote':
            return self._select_remote_mode()
        else:  # auto
            return self._select_auto_mode(source_language, target_language)
    
    def _select_auto_mode(self, source_language, target_language):
        """Automatically select best mode"""
        network_status = self.network_manager.get_network_status()
        
        # Check if local model available
        local_model_available = self.model_manager.has_model(
            source_language, target_language
        )
        
        # Decision logic
        if network_status['status'] == 'offline':
            # Must use local
            if local_model_available:
                return 'local'
            else:
                raise OfflineTranslationError("No local model available")
        
        if network_status['status'] == 'online':
            # Prefer remote if good connection
            if self.network_manager.should_use_remote(network_status):
                return 'remote'
            else:
                # Poor connection, use local if available
                if local_model_available:
                    return 'local'
                else:
                    # Fallback to remote even with poor connection
                    return 'remote'
        
        return 'local'  # Default to local
    
    def _select_local_mode(self, source_language, target_language):
        """Select local mode"""
        if not self.model_manager.has_model(source_language, target_language):
            raise LocalModelNotAvailableError("Local model not available")
        return 'local'
    
    def _select_remote_mode(self):
        """Select remote mode"""
        network_status = self.network_manager.get_network_status()
        if network_status['status'] == 'offline':
            raise OfflineError("Cannot use remote mode offline")
        return 'remote'
```

#### 3. Local Translation Engine

**Responsibilities:**
- Load and manage local translation models
- Execute translation inference
- Handle model lifecycle
- Optimize for mobile performance

**Key Design Decisions:**
- **Model Format**: Use optimized format (TFLite, CoreML, ONNX)
- **Lazy Loading**: Load models on demand
- **Memory Management**: Efficient memory usage
- **Performance**: Fast inference (< 500ms)

**Implementation:**
```python
class LocalTranslationEngine:
    def __init__(self, model_manager):
        self.model_manager = model_manager
        self.loaded_models = {}  # Cache loaded models
    
    def translate(self, source_text, source_language, target_language):
        """Translate using local model"""
        # Get model
        model = self.get_model(source_language, target_language)
        
        if not model:
            raise LocalModelNotAvailableError("Model not available")
        
        # Run inference
        start_time = time.time()
        translated_text = model.translate(source_text)
        latency = (time.time() - start_time) * 1000  # ms
        
        return {
            'translated_text': translated_text,
            'mode': 'local',
            'latency_ms': latency,
            'confidence_score': 0.9  # Local models typically have high confidence
        }
    
    def get_model(self, source_language, target_language):
        """Get translation model"""
        language_pair = f"{source_language}-{target_language}"
        
        # Check cache
        if language_pair in self.loaded_models:
            return self.loaded_models[language_pair]
        
        # Load model
        model = self.model_manager.load_model(source_language, target_language)
        if model:
            self.loaded_models[language_pair] = model
        
        return model
    
    def batch_translate(self, texts, source_language, target_language):
        """Translate multiple texts"""
        model = self.get_model(source_language, target_language)
        if not model:
            raise LocalModelNotAvailableError("Model not available")
        
        # Batch inference
        translations = model.batch_translate(texts)
        
        return [
            {
                'source_text': text,
                'translated_text': translation,
                'mode': 'local'
            }
            for text, translation in zip(texts, translations)
        ]
```

#### 4. Remote Translation Client

**Responsibilities:**
- Communicate with remote translation API
- Handle API requests and responses
- Manage API errors and retries
- Optimize for network efficiency

**Key Design Decisions:**
- **HTTP/2**: Use HTTP/2 for better performance
- **Request Batching**: Batch multiple translations
- **Retry Logic**: Retry on failures
- **Compression**: Compress requests/responses

**Implementation:**
```python
class RemoteTranslationClient:
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept-Encoding': 'gzip'
        })
    
    def translate(self, source_text, source_language, target_language):
        """Translate using remote API"""
        url = f"{self.api_base_url}/api/v1/translate"
        
        payload = {
            'source_text': source_text,
            'source_language': source_language,
            'target_language': target_language
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                url,
                json=payload,
                timeout=5
            )
            latency = (time.time() - start_time) * 1000  # ms
            
            response.raise_for_status()
            data = response.json()
            
            return {
                'translated_text': data['translated_text'],
                'mode': 'remote',
                'latency_ms': latency,
                'confidence_score': data.get('confidence_score', 0.85)
            }
        except requests.Timeout:
            raise RemoteTranslationTimeoutError("Translation timeout")
        except requests.RequestException as e:
            raise RemoteTranslationError(f"Translation failed: {str(e)}")
    
    def batch_translate(self, texts, source_language, target_language):
        """Batch translate using remote API"""
        url = f"{self.api_base_url}/api/v1/translate/batch"
        
        payload = {
            'texts': texts,
            'source_language': source_language,
            'target_language': target_language
        }
        
        try:
            response = self.session.post(
                url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            return [
                {
                    'source_text': text,
                    'translated_text': translation['translated_text'],
                    'mode': 'remote'
                }
                for text, translation in zip(texts, data['translations'])
            ]
        except requests.RequestException as e:
            raise RemoteTranslationError(f"Batch translation failed: {str(e)}")
```

#### 5. Translation Cache Manager

**Responsibilities:**
- Cache translations locally
- Manage cache size and eviction
- Provide fast cache lookups
- Sync cache across devices

**Key Design Decisions:**
- **LRU Eviction**: Evict least recently used entries
- **Size Limit**: Limit cache size (e.g., 10MB)
- **Fast Lookup**: < 10ms cache lookup
- **Persistence**: Persist cache to disk

**Implementation:**
```python
class TranslationCacheManager:
    def __init__(self, max_size_mb=10):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.cache = {}  # In-memory cache
        self.access_order = []  # For LRU
        self.current_size = 0
        self.db = CacheDatabase()  # Persistent storage
    
    def get(self, source_text, source_language, target_language):
        """Get translation from cache"""
        cache_key = self._generate_key(source_text, source_language, target_language)
        
        # Check in-memory cache
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            self._update_access_order(cache_key)
            entry['last_accessed_at'] = datetime.now()
            entry['access_count'] += 1
            return entry['translated_text']
        
        # Check persistent cache
        entry = self.db.get(cache_key)
        if entry:
            # Load into memory cache
            self._add_to_memory_cache(cache_key, entry)
            return entry['translated_text']
        
        return None
    
    def put(self, source_text, source_language, target_language, translated_text):
        """Store translation in cache"""
        cache_key = self._generate_key(source_text, source_language, target_language)
        
        entry = {
            'source_text': source_text,
            'source_language': source_language,
            'target_language': target_language,
            'translated_text': translated_text,
            'created_at': datetime.now(),
            'last_accessed_at': datetime.now(),
            'access_count': 1
        }
        
        entry_size = self._calculate_size(entry)
        
        # Check if need to evict
        while self.current_size + entry_size > self.max_size_bytes:
            self._evict_lru()
        
        # Add to cache
        self._add_to_memory_cache(cache_key, entry)
        self.db.put(cache_key, entry)
    
    def _generate_key(self, source_text, source_language, target_language):
        """Generate cache key"""
        key_string = f"{source_language}:{target_language}:{source_text}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _add_to_memory_cache(self, cache_key, entry):
        """Add entry to memory cache"""
        if cache_key in self.cache:
            # Update existing
            old_entry = self.cache[cache_key]
            self.current_size -= self._calculate_size(old_entry)
        
        self.cache[cache_key] = entry
        self.current_size += self._calculate_size(entry)
        self._update_access_order(cache_key)
    
    def _evict_lru(self):
        """Evict least recently used entry"""
        if not self.access_order:
            return
        
        lru_key = self.access_order.pop(0)
        if lru_key in self.cache:
            entry = self.cache[lru_key]
            self.current_size -= self._calculate_size(entry)
            del self.cache[lru_key]
```

### Detailed Design

#### Hybrid Mode Implementation

**Challenge:** Seamlessly switch between local and remote modes

**Solution:**
- **Unified Interface**: Single API for both modes
- **Automatic Switching**: Auto-detect and switch modes
- **Fallback Strategy**: Fallback to alternative mode on failure
- **Transparent to User**: User doesn't need to know which mode

**Implementation:**
```python
class HybridTranslationService:
    def __init__(self):
        self.network_manager = NetworkDetectionManager()
        self.mode_selector = TranslationModeSelector(
            self.network_manager,
            CacheManager(),
            ModelManager()
        )
        self.local_engine = LocalTranslationEngine(ModelManager())
        self.remote_client = RemoteTranslationClient(API_BASE_URL)
        self.cache_manager = TranslationCacheManager()
    
    def translate(self, source_text, source_language, target_language, 
                  mode='auto', use_cache=True):
        """Translate with hybrid mode support"""
        # Check cache first
        if use_cache:
            cached = self.cache_manager.get(
                source_text, source_language, target_language
            )
            if cached:
                return {
                    'translated_text': cached,
                    'mode': 'cache',
                    'cached': True
                }
        
        # Select mode
        selected_mode = self.mode_selector.select_mode(
            source_language, target_language, mode
        )
        
        # Translate
        try:
            if selected_mode == 'local':
                result = self.local_engine.translate(
                    source_text, source_language, target_language
                )
            else:  # remote
                result = self.remote_client.translate(
                    source_text, source_language, target_language
                )
            
            # Cache result
            if use_cache:
                self.cache_manager.put(
                    source_text, source_language, target_language,
                    result['translated_text']
                )
            
            return result
        
        except Exception as e:
            # Fallback to alternative mode
            return self._fallback_translate(
                source_text, source_language, target_language,
                selected_mode, use_cache
            )
    
    def _fallback_translate(self, source_text, source_language, target_language,
                           failed_mode, use_cache):
        """Fallback to alternative mode"""
        if failed_mode == 'local':
            # Try remote
            try:
                result = self.remote_client.translate(
                    source_text, source_language, target_language
                )
                if use_cache:
                    self.cache_manager.put(
                        source_text, source_language, target_language,
                        result['translated_text']
                    )
                return result
            except:
                pass
        else:  # remote failed
            # Try local
            try:
                result = self.local_engine.translate(
                    source_text, source_language, target_language
                )
                if use_cache:
                    self.cache_manager.put(
                        source_text, source_language, target_language,
                        result['translated_text']
                    )
                return result
            except:
                pass
        
        # Both failed, return error
        raise TranslationError("Translation failed in both modes")
```

#### Model Management

**Challenge:** Manage local models efficiently

**Solution:**
- **Lazy Download**: Download models on demand
- **Version Management**: Track model versions
- **Update Mechanism**: Update models periodically
- **Storage Optimization**: Compress models, remove unused

**Implementation:**
```python
class ModelManager:
    def __init__(self):
        self.local_storage = LocalStorage()
        self.model_service = ModelService()
        self.downloaded_models = set()
    
    def has_model(self, source_language, target_language):
        """Check if model is available locally"""
        language_pair = f"{source_language}-{target_language}"
        return language_pair in self.downloaded_models
    
    def download_model(self, source_language, target_language, callback=None):
        """Download model"""
        language_pair = f"{source_language}-{target_language}"
        
        # Get model metadata
        metadata = self.model_service.get_model_metadata(language_pair)
        
        # Download model
        model_path = self.local_storage.download_file(
            metadata['download_url'],
            f"models/{language_pair}.tflite",
            callback=callback
        )
        
        # Verify checksum
        if not self._verify_checksum(model_path, metadata['checksum']):
            raise ModelDownloadError("Checksum verification failed")
        
        # Register model
        self.downloaded_models.add(language_pair)
        self.local_storage.save_model_info(language_pair, metadata)
        
        return model_path
    
    def load_model(self, source_language, target_language):
        """Load model into memory"""
        language_pair = f"{source_language}-{target_language}"
        
        if language_pair not in self.downloaded_models:
            return None
        
        # Load from storage
        model_path = self.local_storage.get_model_path(language_pair)
        return self._load_model_file(model_path)
    
    def update_model(self, source_language, target_language):
        """Update model to latest version"""
        language_pair = f"{source_language}-{target_language}"
        
        # Get current version
        current_info = self.local_storage.get_model_info(language_pair)
        
        # Get latest version
        latest_metadata = self.model_service.get_latest_model_metadata(language_pair)
        
        if latest_metadata['model_version'] != current_info['model_version']:
            # Download new version
            return self.download_model(source_language, target_language)
        
        return None
```

### Scalability Considerations

#### Horizontal Scaling

**Translation Service:**
- Stateless service, horizontally scalable
- Multiple instances behind load balancer
- Auto-scaling based on load
- Model serving on GPU instances

#### Caching Strategy

**Multi-Level Cache:**
- **Client Cache**: Local cache on device
- **CDN Cache**: Cache popular translations
- **Application Cache**: Cache in translation service
- **Database Cache**: Cache in database layer

### Security Considerations

#### Data Privacy

- **Encryption**: Encrypt sensitive translations
- **Local Storage**: Secure local model storage
- **API Security**: Secure API communication
- **User Data**: Don't log sensitive user data

#### Model Security

- **Model Integrity**: Verify model checksums
- **Model Updates**: Secure model update mechanism
- **Malicious Models**: Scan models for malware

### Monitoring & Observability

#### Key Metrics

**Performance Metrics:**
- Translation latency (local vs remote)
- Cache hit rate
- Model load time
- Network detection latency

**Usage Metrics:**
- Translations per second
- Offline vs online usage
- Language pair distribution
- Model download rate

**Quality Metrics:**
- Translation accuracy
- User satisfaction
- Error rate

### Trade-offs and Optimizations

#### Trade-offs

**1. Model Size: Small vs Large**
- **Small**: Less storage, lower accuracy
- **Large**: More storage, higher accuracy
- **Decision**: Balance based on device storage

**2. Cache Size: Large vs Small**
- **Large**: More cache hits, more storage
- **Small**: Less storage, more misses
- **Decision**: 10-100MB based on device

**3. Mode Selection: Aggressive vs Conservative**
- **Aggressive**: Prefer remote, better quality
- **Conservative**: Prefer local, better offline
- **Decision**: Adaptive based on network

#### Optimizations

**1. Model Compression**
- Quantize models
- Reduce model size
- Maintain accuracy

**2. Batch Translation**
- Batch multiple texts
- Reduce API calls
- Improve throughput

**3. Predictive Model Download**
- Download models before needed
- Reduce wait time
- Improve UX

## What Interviewers Look For

### Hybrid Architecture Skills

1. **Mode Switching**
   - Seamless local/remote switching
   - Network detection
   - Automatic fallback
   - **Red Flags**: Manual switching, no detection, no fallback

2. **Local Model Management**
   - Efficient model storage
   - Model updates
   - **Red Flags**: No local models, inefficient storage, no updates

3. **Offline Support**
   - Full offline functionality
   - Local translation
   - **Red Flags**: No offline, network required, poor UX

### Distributed Systems Skills

1. **Network Detection**
   - Fast detection
   - Accurate status
   - **Red Flags**: Slow detection, inaccurate, no detection

2. **Caching Strategy**
   - Multi-level caching
   - High cache hit rate
   - **Red Flags**: No caching, low hit rate, poor performance

3. **Scalability Design**
   - Horizontal scaling
   - Load balancing
   - **Red Flags**: Vertical scaling, no load balancing, bottlenecks

### Problem-Solving Approach

1. **Performance Optimization**
   - Sub-500ms local translation
   - Sub-2s remote translation
   - **Red Flags**: High latency, no optimization, poor UX

2. **Edge Cases**
   - Network failures
   - Model updates
   - Large texts
   - **Red Flags**: Ignoring edge cases, no handling

3. **Trade-off Analysis**
   - Local vs remote
   - Accuracy vs speed
   - **Red Flags**: No trade-offs, dogmatic choices

### System Design Skills

1. **Component Design**
   - Translation service
   - Model management service
   - Network detection service
   - **Red Flags**: Monolithic, unclear boundaries

2. **Fallback Strategy**
   - Graceful degradation
   - Error handling
   - **Red Flags**: No fallback, errors, poor UX

3. **Model Updates**
   - Efficient updates
   - Version management
   - **Red Flags**: No updates, inefficient, version conflicts

### Communication Skills

1. **Hybrid Architecture Explanation**
   - Can explain mode switching
   - Understands local/remote trade-offs
   - **Red Flags**: No understanding, vague

2. **Performance Explanation**
   - Can explain optimization strategies
   - Understands caching
   - **Red Flags**: No understanding, vague

### Meta-Specific Focus

1. **Hybrid Systems Expertise**
   - Local/remote architecture
   - Offline-first design
   - **Key**: Show hybrid systems knowledge

2. **User Experience Focus**
   - Transparent switching
   - Seamless operation
   - **Key**: Demonstrate UX thinking

## Summary

Designing a global translation service with hybrid mode requires careful consideration of:

1. **Hybrid Architecture**: Seamless switching between local and remote
2. **Network Detection**: Fast and accurate network status detection
3. **Local Models**: Efficient model management and storage
4. **Caching Strategy**: Multi-level caching for performance
5. **Offline Support**: Full functionality without network
6. **Mode Selection**: Smart mode selection based on context
7. **Fallback Strategy**: Graceful fallback on failures
8. **Model Updates**: Efficient model update mechanism
9. **Performance**: Sub-500ms local, sub-2s remote translation
10. **User Experience**: Transparent mode switching

Key architectural decisions:
- **Hybrid Mode** for seamless online/offline operation
- **Network Detection** for automatic mode switching
- **Local Models** for offline translation
- **Multi-Level Cache** for performance
- **Smart Mode Selection** based on network and context
- **Fallback Strategy** for reliability
- **Model Management** for efficient storage
- **Horizontal Scaling** for remote service

The system handles 100,000 translations per second, works completely offline with local models, automatically switches between local and remote modes, and provides sub-500ms local translation latency with > 90% cache hit rate.

