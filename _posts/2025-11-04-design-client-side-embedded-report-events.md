---
layout: post
title: "Design Client-Side Embedded Report Events System (C++)"
date: 2025-11-04
categories: [System Design, Interview Example, Client-Side, Embedded Systems, Analytics, C++]
excerpt: "A detailed walkthrough of designing a client-side embedded report events system in C++, including native SDK implementation, event tracking, embedded widgets, platform-specific optimization, and client-side processing."
---

## Introduction

This post provides a comprehensive walkthrough of designing a client-side embedded report events system in C++. This system focuses on the client-side implementation—native C++ SDK, event tracking, embedded report widgets, and platform-specific optimization. This is a common system design question for companies building analytics and reporting platforms that need to be embedded in native desktop and mobile applications.

## Table of Contents

1. [Requirements](#requirements)
   - [Functional Requirements](#functional-requirements)
   - [Non-Functional Requirements](#non-functional-requirements)
2. [Capacity Estimation](#capacity-estimation)
3. [High-Level Design](#high-level-design)
4. [Core Entities](#core-entities)
5. [API](#api)
6. [Data Flow](#data-flow)
7. [Database Design](#database-design)
   - [Schema Design](#schema-design)
   - [Database Sharding Strategy](#database-sharding-strategy)
8. [Deep Dive](#deep-dive)
   - [Component Design](#component-design)
   - [Detailed Design](#detailed-design)
   - [Performance Optimization](#performance-optimization)
   - [Privacy and Security](#privacy-and-security)
   - [Cross-Platform Support](#cross-platform-support)
   - [Monitoring and Debugging](#monitoring-and-debugging)
   - [Testing and Quality Assurance](#testing-and-quality-assurance)
9. [Conclusion](#conclusion)

## Requirements

### Functional Requirements

**Design a client-side embedded report events system that:**

1. **Client-Side Event Tracking**: Track events from native applications (desktop, mobile)
2. **Embedded Report Widgets**: Embed report widgets/dashboards in customer applications
3. **C++ SDK**: Provide native C++ SDK for easy integration
4. **Real-Time Updates**: Update embedded reports in real-time
5. **Performance Optimization**: Minimize impact on host application performance
6. **Privacy and Security**: Respect user privacy and secure data transmission
7. **Cross-Platform Support**: Support desktop (Windows, macOS, Linux), mobile (iOS/Android), and embedded systems

**Describe the architecture, C++ SDK design, widget embedding, and how to optimize for performance, privacy, and reliability.**

**Core Features:**

1. **Event Tracking**
   - Track page views, clicks, conversions, custom events
   - Automatic event tracking (page views, scroll depth)
   - Manual event tracking (custom events)
   - Event batching and queuing
   - Offline event storage

2. **Embedded Report Widgets**
   - Embed dashboards in customer applications
   - Multiple widget types (charts, tables, metrics)
   - Responsive design
   - Customizable styling
   - Interactive widgets (filtering, drill-down)

3. **C++ SDK**
   - Easy integration (header-only or library)
   - Automatic initialization
   - API for manual tracking
   - Configuration options
   - Cross-platform compatibility (Windows, macOS, Linux)

4. **Real-Time Updates**
   - Real-time dashboard updates
   - WebSocket/SSE connections
   - Efficient update propagation
   - Connection management

5. **Performance**
   - Minimal impact on page load
   - Lazy loading of widgets
   - Efficient event batching
   - Resource optimization

6. **Privacy and Security**
   - GDPR/CCPA compliance
   - Cookie consent management
   - Data anonymization
   - Secure data transmission (HTTPS)
   - Do-not-track support

### Non-Functional Requirements

**Performance:**
- SDK load time: < 50ms
- Event tracking latency: < 10ms
- Widget load time: < 500ms
- Page load impact: < 5% overhead

**Reliability:**
- No blocking of host application
- Graceful error handling
- Offline event storage
- Automatic retry on failures

**Compatibility:**
- Desktop platforms (Windows, macOS, Linux)
- Mobile platforms (iOS, Android)
- Embedded systems
- Cross-compilation support

**Privacy:**
- Cookie consent management
- Opt-out mechanisms
- Data anonymization
- Minimal data collection

### Clarifying Questions

**Integration:**
- Q: How should customers integrate?
- A: Include header file or link library, similar to other C++ libraries

**Event Types:**
- Q: What events should be tracked automatically?
- A: Page views, clicks, scroll depth, form submissions

**Widget Types:**
- Q: What types of widgets?
- A: Time-series charts, pie charts, tables, metric cards, funnels

**Real-Time:**
- Q: How real-time should updates be?
- A: Updates within 1-2 seconds of events

**Privacy:**
- Q: What privacy requirements?
- A: GDPR, CCPA, cookie consent, opt-out support

## Capacity Estimation

### Client-Side Estimates

**SDK Loads:**
- 1M websites using SDK
- Average: 1000 page views per site per day
- Total: 1B page views per day
- SDK loads: ~11,500 loads/second

**Event Tracking:**
- 1B page views/day
- Average: 5 events per page view
- Total: 5B events/day
- Peak: ~58,000 events/second

**Widget Embeds:**
- 100K websites with embedded widgets
- Average: 10 widgets per page
- Total: 1M widget loads/day
- Peak: ~12,000 widget loads/second

**Storage (Browser):**
- LocalStorage: ~5-10MB per domain
- IndexedDB: ~50MB+ per domain
- Event queue: ~10KB per 100 events
- Widget cache: ~100KB per widget

### Network Bandwidth

**Per Page Load:**
- SDK download: ~50KB (gzipped)
- Event tracking: ~1KB per event
- Widget assets: ~100KB per widget
- Total: ~200KB per page load

**Total System:**
- SDK downloads: 1B × 50KB = 50TB/day
- Event tracking: 5B × 1KB = 5TB/day
- Widget assets: 1M × 100KB = 100GB/day
- Total: ~55TB/day

## High-Level Design

### Client-Side Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Customer Website                          │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Embedded Report Widgets                      │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │  │
│  │  │   Chart      │  │   Table      │  │   Metric   │ │  │
│  │  │   Widget     │  │   Widget     │  │   Widget   │ │  │
│  │  └──────────────┘  └──────────────┘  └────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          JavaScript SDK                                │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │  │
│  │  │  Event       │  │  Queue       │  │  Storage   │ │  │
│  │  │  Tracker     │  │  Manager     │  │  Manager   │ │  │
│  │  └──────────────┘  └──────────────┘  └────────────┘ │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │  │
│  │  │  Network     │  │  Privacy     │  │  Config    │ │  │
│  │  │  Manager     │  │  Manager     │  │  Manager   │ │  │
│  │  └──────────────┘  └──────────────┘  └────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ HTTPS / WebSocket
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    CDN / Edge Network                        │
│  (SDK Distribution, Widget Assets, Static Content)           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend Services                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Event       │  │  Widget      │  │  Real-Time   │      │
│  │  Collector   │  │  Service     │  │  Streamer    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

**Client-Side Components:**

1. **C++ SDK**: Main SDK library (native implementation)
2. **Event Tracker**: Tracks user events
3. **Queue Manager**: Manages event queue (thread-safe)
4. **Storage Manager**: File system storage management
5. **Network Manager**: HTTP requests (libcurl), batching, retries
6. **Privacy Manager**: Privacy consent, opt-out, anonymization
7. **Widget Loader**: Loads and renders embedded widgets (platform-specific UI)
8. **Real-Time Connector**: WebSocket connection (websocketpp)

## Core Entities

### Event
- **Attributes**: event_id, event_name, properties, timestamp, user_id, session_id
- **Relationships**: Belongs to SDK instance, tracked by application

### Widget
- **Attributes**: widget_id, widget_type, data, config, cache_key
- **Relationships**: Embedded in application, displays report data

### SDK Instance
- **Attributes**: sdk_id, api_key, config, initialized_at, version
- **Relationships**: Tracks events, manages widgets

## API

### Event Collection API
```http
POST /api/v1/events
Content-Type: application/json
Authorization: Bearer {api_key}

{
  "events": [
    {
      "event_id": "uuid",
      "event_name": "page_view",
      "properties": {...},
      "timestamp": "2025-11-04T10:00:00Z",
      "user_id": "user-123",
      "session_id": "session-456"
    }
  ]
}

Response: 200 OK
{
  "status": "success",
  "processed": 1,
  "failed": 0
}
```

### Widget API
```http
GET /api/v1/widgets/{widget_id}
Authorization: Bearer {api_key}

Response: 200 OK
{
  "widget_id": "uuid",
  "widget_type": "chart",
  "data": {
    "series": [
      {"time": "2025-11-01", "value": 1000},
      {"time": "2025-11-02", "value": 1200}
    ]
  }
}
```

## Data Flow

### Event Tracking Flow
1. User action occurs → Application
2. Application → C++ SDK (track event)
3. SDK → Event Queue (batch events)
4. SDK → Local Storage (persist offline)
5. SDK → API Gateway (send events when online)
6. API Gateway → Event Processing Service
7. Event Processing Service → Database (store events)
8. Response returned to SDK

### Widget Rendering Flow
1. Application loads page → Application
2. Application → C++ SDK (initialize widget)
3. SDK → Widget API (request widget data)
4. Widget API → Report Service (generate report)
5. Report Service → Database (query event data)
6. Report Service → Widget API (return widget data)
7. Widget API → SDK (return data)
8. SDK → Application (render widget)

## Database Design

### Schema Design

**Events Table:**
```sql
CREATE TABLE events (
    event_id VARCHAR(36) PRIMARY KEY,
    sdk_id VARCHAR(36) NOT NULL,
    event_name VARCHAR(255) NOT NULL,
    properties JSON,
    user_id VARCHAR(36),
    session_id VARCHAR(36),
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP,
    INDEX idx_sdk_timestamp (sdk_id, timestamp),
    INDEX idx_event_name (event_name),
    INDEX idx_user_id (user_id)
);
```

**Widgets Table:**
```sql
CREATE TABLE widgets (
    widget_id VARCHAR(36) PRIMARY KEY,
    sdk_id VARCHAR(36) NOT NULL,
    widget_type VARCHAR(50) NOT NULL,
    config JSON,
    cache_key VARCHAR(255),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    INDEX idx_sdk_id (sdk_id)
);
```

### Database Sharding Strategy

**Shard by SDK ID:**
- SDK data, events, and widgets on same shard
- Enables efficient SDK queries
- Use consistent hashing for distribution

## Deep Dive

### Component Design

#### Detailed Design

### C++ SDK Design

**SDK Initialization:**
```cpp
// Customer integration
#include "analytics_sdk.h"

int main() {
    // Initialize SDK
    AnalyticsSDK::Config config;
    config.api_key = "customer-api-key";
    config.endpoint = "https://api.example.com";
    config.options.auto_track = true;
    config.options.batch_events = true;
    config.options.batch_size = 10;
    config.options.flush_interval = 5000; // milliseconds
    config.options.enable_privacy = true;
    
    AnalyticsSDK::getInstance().initialize(config);
    
    // Track events
    AnalyticsSDK::getInstance().track("page_view", {
        {"path", "/products"},
        {"referrer", "https://google.com"}
    });
    
    return 0;
}
```

**SDK Core Implementation:**
```cpp
#include <string>
#include <map>
#include <vector>
#include <memory>
#include <mutex>
#include <chrono>
#include <thread>
#include <uuid/uuid.h>
#include "event_queue.h"
#include "storage_manager.h"
#include "network_manager.h"
#include "privacy_manager.h"

class AnalyticsSDK {
public:
    struct Config {
        std::string api_key;
        std::string endpoint;
        struct Options {
            bool auto_track = true;
            bool batch_events = true;
            int batch_size = 10;
            int flush_interval = 5000; // milliseconds
            bool enable_privacy = true;
        } options;
    };
    
    struct Event {
        std::string event_id;
        std::string event_name;
        std::map<std::string, std::string> properties;
        std::string timestamp;
        std::string user_id;
        std::string session_id;
    };
    
    static AnalyticsSDK& getInstance() {
        static AnalyticsSDK instance;
        return instance;
    }
    
    void initialize(const Config& config) {
        std::lock_guard<std::mutex> lock(mutex_);
        
        config_ = config;
        queue_ = std::make_unique<EventQueue>();
        storage_ = std::make_unique<StorageManager>();
        network_ = std::make_unique<NetworkManager>(config.endpoint);
        privacy_ = std::make_unique<PrivacyManager>();
        
        // Check privacy consent
        if (!privacy_->hasConsent()) {
            privacy_->showConsentBanner();
            return;
        }
        
        // Load queued events from storage
        loadQueuedEvents();
        
        // Start auto-tracking if enabled
        if (config.options.auto_track) {
            startAutoTracking();
        }
        
        // Start batch flushing
        if (config.options.batch_events) {
            startBatchFlushing();
        }
    }
    
    void track(const std::string& event_name, 
               const std::map<std::string, std::string>& properties = {}) {
        std::lock_guard<std::mutex> lock(mutex_);
        
        // Check privacy consent
        if (!privacy_->hasConsent()) {
            return;
        }
        
        // Create event
        Event event;
        event.event_id = generateEventId();
        event.event_name = event_name;
        event.properties = properties;
        event.timestamp = getCurrentTimestamp();
        event.user_id = getUserId();
        event.session_id = getSessionId();
        
        // Add to queue
        queue_->add(event);
        
        // Flush if batch size reached
        if (queue_->size() >= config_.options.batch_size) {
            flush();
        }
    }
    
    void flush() {
        std::vector<Event> events = queue_->getAll();
        if (events.empty()) return;
        
        // Send to server
        network_->send("/events", events, config_.api_key, 
            [this, events](bool success) {
                if (success) {
                    // Clear queue on success
                    queue_->clear();
                    storage_->remove("queued_events");
                } else {
                    // Store in local storage for retry
                    storage_->set("queued_events", events);
                }
            });
    }
    
private:
    Config config_;
    std::unique_ptr<EventQueue> queue_;
    std::unique_ptr<StorageManager> storage_;
    std::unique_ptr<NetworkManager> network_;
    std::unique_ptr<PrivacyManager> privacy_;
    std::mutex mutex_;
    bool initialized_ = false;
    
    void loadQueuedEvents() {
        auto events = storage_->get("queued_events");
        if (!events.empty()) {
            for (const auto& event : events) {
                queue_->add(event);
            }
        }
    }
    
    void startAutoTracking() {
        // Auto-tracking implementation depends on platform
        // For example, in a GUI application, hook into UI events
        // This is platform-specific
    }
    
    void startBatchFlushing() {
        std::thread([this]() {
            while (true) {
                std::this_thread::sleep_for(
                    std::chrono::milliseconds(config_.options.flush_interval)
                );
                flush();
            }
        }).detach();
    }
    
    std::string generateEventId() {
        uuid_t uuid;
        uuid_generate_random(uuid);
        char uuid_str[37];
        uuid_unparse(uuid, uuid_str);
        return std::string(uuid_str);
    }
    
    std::string getCurrentTimestamp() {
        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);
        std::stringstream ss;
        ss << std::put_time(std::gmtime(&time_t), "%Y-%m-%dT%H:%M:%SZ");
        return ss.str();
    }
    
    std::string getUserId() {
        // Get or create user ID
        auto user_id = storage_->get("user_id");
        if (user_id.empty()) {
            user_id = generateEventId();
            storage_->set("user_id", user_id);
        }
        return user_id;
    }
    
    std::string getSessionId() {
        // Get or create session ID
        auto session_id = storage_->get("session_id");
        if (session_id.empty()) {
            session_id = generateEventId();
            storage_->set("session_id", session_id);
        }
        return session_id;
    }
};
```

### Event Queue Manager

**Implementation:**
```cpp
#include <vector>
#include <deque>
#include <mutex>
#include <algorithm>

class EventQueue {
public:
    explicit EventQueue(size_t max_size = 100) 
        : max_size_(max_size) {}
    
    void add(const AnalyticsSDK::Event& event) {
        std::lock_guard<std::mutex> lock(mutex_);
        
        events_.push_back(event);
        
        // Limit queue size
        if (events_.size() > max_size_) {
            // Remove oldest events
            events_.erase(events_.begin(), 
                         events_.begin() + (events_.size() - max_size_));
        }
    }
    
    std::vector<AnalyticsSDK::Event> getAll() {
        std::lock_guard<std::mutex> lock(mutex_);
        return std::vector<AnalyticsSDK::Event>(events_.begin(), events_.end());
    }
    
    void clear() {
        std::lock_guard<std::mutex> lock(mutex_);
        events_.clear();
    }
    
    size_t size() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return events_.size();
    }
    
private:
    std::deque<AnalyticsSDK::Event> events_;
    size_t max_size_;
    mutable std::mutex mutex_;
};
```

### Storage Manager

**Implementation:**
```cpp
#include <string>
#include <map>
#include <fstream>
#include <sstream>
#include <filesystem>
#include <nlohmann/json.hpp>
#include <mutex>

class StorageManager {
public:
    StorageManager() {
        // Determine storage path
        storage_path_ = getStoragePath();
        
        // Create storage directory if it doesn't exist
        std::filesystem::create_directories(storage_path_);
        
        // Load existing data
        loadFromDisk();
    }
    
    void set(const std::string& key, const std::vector<AnalyticsSDK::Event>& value) {
        std::lock_guard<std::mutex> lock(mutex_);
        
        // Convert events to JSON
        nlohmann::json json_value = nlohmann::json::array();
        for (const auto& event : value) {
            nlohmann::json event_json;
            event_json["event_id"] = event.event_id;
            event_json["event_name"] = event.event_name;
            event_json["properties"] = event.properties;
            event_json["timestamp"] = event.timestamp;
            event_json["user_id"] = event.user_id;
            event_json["session_id"] = event.session_id;
            json_value.push_back(event_json);
        }
        
        storage_[key] = json_value.dump();
        
        // Persist to disk
        saveToDisk();
    }
    
    void set(const std::string& key, const std::string& value) {
        std::lock_guard<std::mutex> lock(mutex_);
        storage_[key] = value;
        saveToDisk();
    }
    
    std::vector<AnalyticsSDK::Event> getEvents(const std::string& key) {
        std::lock_guard<std::mutex> lock(mutex_);
        
        auto it = storage_.find(key);
        if (it == storage_.end()) {
            return {};
        }
        
        try {
            nlohmann::json json_value = nlohmann::json::parse(it->second);
            std::vector<AnalyticsSDK::Event> events;
            
            for (const auto& event_json : json_value) {
                AnalyticsSDK::Event event;
                event.event_id = event_json["event_id"];
                event.event_name = event_json["event_name"];
                event.properties = event_json["properties"].get<std::map<std::string, std::string>>();
                event.timestamp = event_json["timestamp"];
                event.user_id = event_json["user_id"];
                event.session_id = event_json["session_id"];
                events.push_back(event);
            }
            
            return events;
        } catch (...) {
            return {};
        }
    }
    
    std::string get(const std::string& key) {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = storage_.find(key);
        return (it != storage_.end()) ? it->second : "";
    }
    
    void remove(const std::string& key) {
        std::lock_guard<std::mutex> lock(mutex_);
        storage_.erase(key);
        saveToDisk();
    }
    
private:
    std::map<std::string, std::string> storage_;
    std::string storage_path_;
    mutable std::mutex mutex_;
    
    std::string getStoragePath() {
        // Platform-specific storage path
        #ifdef _WIN32
            return std::string(std::getenv("APPDATA")) + "/AnalyticsSDK";
        #elif __APPLE__
            return std::string(std::getenv("HOME")) + "/Library/Application Support/AnalyticsSDK";
        #else
            return std::string(std::getenv("HOME")) + "/.analytics_sdk";
        #endif
    }
    
    void loadFromDisk() {
        std::string file_path = storage_path_ + "/storage.json";
        if (!std::filesystem::exists(file_path)) {
            return;
        }
        
        std::ifstream file(file_path);
        if (!file.is_open()) {
            return;
        }
        
        try {
            nlohmann::json json_data;
            file >> json_data;
            
            for (auto& [key, value] : json_data.items()) {
                storage_[key] = value.dump();
            }
        } catch (...) {
            // Ignore parse errors
        }
    }
    
    void saveToDisk() {
        std::string file_path = storage_path_ + "/storage.json";
        std::ofstream file(file_path);
        
        if (!file.is_open()) {
            return;
        }
        
        try {
            nlohmann::json json_data;
            for (const auto& [key, value] : storage_) {
                json_data[key] = nlohmann::json::parse(value);
            }
            file << json_data.dump(2);
        } catch (...) {
            // Ignore save errors
        }
    }
};
```

### Network Manager

**Implementation:**
```cpp
#include <string>
#include <vector>
#include <functional>
#include <thread>
#include <chrono>
#include <curl/curl.h>
#include <nlohmann/json.hpp>
#include <mutex>

class NetworkManager {
public:
    explicit NetworkManager(const std::string& endpoint) 
        : endpoint_(endpoint), retry_attempts_(3), retry_delay_(1000) {
        curl_global_init(CURL_GLOBAL_DEFAULT);
    }
    
    ~NetworkManager() {
        curl_global_cleanup();
    }
    
    void send(const std::string& path, 
              const std::vector<AnalyticsSDK::Event>& events,
              const std::string& api_key,
              std::function<void(bool)> callback) {
        // Build request payload
        nlohmann::json payload;
        payload["api_key"] = api_key;
        payload["events"] = nlohmann::json::array();
        
        for (const auto& event : events) {
            nlohmann::json event_json;
            event_json["event_id"] = event.event_id;
            event_json["event_name"] = event.event_name;
            event_json["properties"] = event.properties;
            event_json["timestamp"] = event.timestamp;
            event_json["user_id"] = event.user_id;
            event_json["session_id"] = event.session_id;
            payload["events"].push_back(event_json);
        }
        
        std::string url = endpoint_ + path;
        std::string json_data = payload.dump();
        
        // Send asynchronously
        std::thread([this, url, json_data, callback]() {
            bool success = sendRequest(url, json_data);
            if (callback) {
                callback(success);
            }
        }).detach();
    }
    
private:
    std::string endpoint_;
    int retry_attempts_;
    int retry_delay_;
    std::mutex mutex_;
    
    bool sendRequest(const std::string& url, const std::string& data) {
        CURL* curl = curl_easy_init();
        if (!curl) {
            return false;
        }
        
        struct curl_slist* headers = nullptr;
        headers = curl_slist_append(headers, "Content-Type: application/json");
        
        std::string response_data;
        
        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, data.c_str());
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, writeCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response_data);
        curl_easy_setopt(curl, CURLOPT_TIMEOUT, 10L);
        curl_easy_setopt(curl, CURLOPT_CONNECTTIMEOUT, 5L);
        
        CURLcode res = curl_easy_perform(curl);
        long http_code = 0;
        curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &http_code);
        
        curl_slist_free_all(headers);
        curl_easy_cleanup(curl);
        
        if (res == CURLE_OK && http_code == 200) {
            return true;
        }
        
        // Retry on failure
        return retry(url, data, 0);
    }
    
    bool retry(const std::string& url, const std::string& data, int attempt) {
        if (attempt >= retry_attempts_) {
            return false;
        }
        
        // Exponential backoff
        int delay = retry_delay_ * (1 << attempt);
        std::this_thread::sleep_for(std::chrono::milliseconds(delay));
        
        return sendRequest(url, data);
    }
    
    static size_t writeCallback(void* contents, size_t size, size_t nmemb, void* userp) {
        ((std::string*)userp)->append((char*)contents, size * nmemb);
        return size * nmemb;
    }
};
```

### Privacy Manager

**Implementation:**
```cpp
#include <string>
#include <functional>
#include <openssl/sha.h>
#include <sstream>
#include <iomanip>
#include "storage_manager.h"

class PrivacyManager {
public:
    PrivacyManager() 
        : consent_key_("analytics_consent"), opt_out_key_("analytics_opt_out") {}
    
    bool hasConsent() {
        std::string consent = getConsent();
        return consent == "granted";
    }
    
    std::string getConsent() {
        // Check storage
        auto storage = StorageManager::getInstance();
        std::string stored = storage->get(consent_key_);
        
        if (!stored.empty()) {
            return stored;
        }
        
        // Check for opt-out
        if (isOptedOut()) {
            return "denied";
        }
        
        // No consent given yet
        return "";
    }
    
    void showConsentBanner(std::function<void(bool)> callback) {
        // Show consent banner (platform-specific UI)
        // This is a callback-based approach for native applications
        consent_callback_ = callback;
        
        // Platform-specific: Show native dialog/UI
        // For example, on Qt: QMessageBox
        // For example, on GTK: GtkDialog
        // For CLI: Print to console and wait for input
    }
    
    void grantConsent() {
        auto storage = StorageManager::getInstance();
        storage->set(consent_key_, "granted");
        
        if (consent_callback_) {
            consent_callback_(true);
        }
    }
    
    void denyConsent() {
        auto storage = StorageManager::getInstance();
        storage->set(consent_key_, "denied");
        
        if (consent_callback_) {
            consent_callback_(false);
        }
    }
    
    bool isOptedOut() {
        // Check storage for opt-out flag
        auto storage = StorageManager::getInstance();
        std::string opt_out = storage->get(opt_out_key_);
        return opt_out == "true";
    }
    
    AnalyticsSDK::Event anonymizeData(const AnalyticsSDK::Event& event) {
        AnalyticsSDK::Event anonymized = event;
        
        // Anonymize IP address (if included in properties)
        auto it = anonymized.properties.find("ip_address");
        if (it != anonymized.properties.end()) {
            it->second = anonymizeIP(it->second);
        }
        
        // Remove PII
        anonymized.properties.erase("email");
        anonymized.properties.erase("phone");
        anonymized.properties.erase("phone_number");
        
        // Hash user ID if needed
        if (!anonymized.user_id.empty() && hash_user_id_) {
            anonymized.user_id = hashString(anonymized.user_id);
        }
        
        return anonymized;
    }
    
    std::string anonymizeIP(const std::string& ip) {
        // Anonymize last octet of IPv4
        size_t pos = ip.find_last_of('.');
        if (pos != std::string::npos) {
            return ip.substr(0, pos + 1) + "0";
        }
        
        // Anonymize IPv6 (simplified)
        pos = ip.find_last_of(':');
        if (pos != std::string::npos) {
            return ip.substr(0, pos + 1) + "0";
        }
        
        return ip;
    }
    
    std::string hashString(const std::string& input) {
        unsigned char hash[SHA256_DIGEST_LENGTH];
        SHA256_CTX sha256;
        SHA256_Init(&sha256);
        SHA256_Update(&sha256, input.c_str(), input.length());
        SHA256_Final(hash, &sha256);
        
        std::stringstream ss;
        for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
            ss << std::hex << std::setw(2) << std::setfill('0') << (int)hash[i];
        }
        return ss.str();
    }
    
    void setHashUserId(bool hash) {
        hash_user_id_ = hash;
    }
    
private:
    std::string consent_key_;
    std::string opt_out_key_;
    std::function<void(bool)> consent_callback_;
    bool hash_user_id_ = false;
};
```

### Embedded Widget Loader

**Widget Embedding (Platform-Specific UI):**
```cpp
// For Qt applications
#include <QWidget>
#include <QWebEngineView>

// For GTK applications
#include <gtk/gtk.h>
#include <webkit2/webkit2.h>

// For native applications
class WidgetLoader {
public:
    struct WidgetOptions {
        std::string widget_id;
        std::string api_key;
        std::map<std::string, std::string> config;
        int width = 800;
        int height = 400;
        bool iframe = true;
    };
    
    void loadWidget(const WidgetOptions& options) {
        // Check if already loaded
        if (loaded_widgets_.find(options.widget_id) != loaded_widgets_.end()) {
            return;
        }
        
        // Load widget iframe or render directly
        if (options.iframe) {
            loadWidgetIframe(options);
        } else {
            loadWidgetDirect(options);
        }
        
        // Connect for real-time updates
        connectRealTime(options.widget_id);
    }
    
private:
    std::map<std::string, void*> loaded_widgets_; // Platform-specific widget handle
    std::map<std::string, WebSocketConnection*> websocket_connections_;
    std::string endpoint_;
    
    void loadWidgetIframe(const WidgetOptions& options) {
        // Platform-specific iframe/widget creation
        // For Qt:
        // QWebEngineView* web_view = new QWebEngineView();
        // web_view->setUrl(QUrl(getWidgetUrl(options.widget_id, options)));
        // loaded_widgets_[options.widget_id] = web_view;
        
        // For GTK:
        // WebKitWebView* web_view = WEBKIT_WEB_VIEW(webkit_web_view_new());
        // webkit_web_view_load_uri(web_view, getWidgetUrl(options.widget_id, options).c_str());
        // loaded_widgets_[options.widget_id] = web_view;
    }
    
    void loadWidgetDirect(const WidgetOptions& options) {
        // Load widget data via API
        std::string url = endpoint_ + "/widgets/" + options.widget_id;
        
        NetworkManager network(endpoint_);
        network.get(url, [this, options](const std::string& response) {
            // Parse widget data
            nlohmann::json data = nlohmann::json::parse(response);
            
            // Render widget (platform-specific)
            renderWidget(data, options);
        });
    }
    
    void renderWidget(const nlohmann::json& data, const WidgetOptions& options) {
        std::string widget_type = data["type"];
        
        if (widget_type == "chart") {
            renderChart(data, options);
        } else if (widget_type == "table") {
            renderTable(data, options);
        } else if (widget_type == "metric") {
            renderMetric(data, options);
        }
    }
    
    void connectRealTime(const std::string& widget_id) {
        // Connect via WebSocket for real-time updates
        std::string ws_url = ws_endpoint_ + "/widgets/" + widget_id;
        
        WebSocketConnection* ws = new WebSocketConnection(ws_url);
        ws->onMessage([this, widget_id](const std::string& message) {
            nlohmann::json update = nlohmann::json::parse(message);
            updateWidget(widget_id, update);
        });
        
        ws->onError([this, widget_id]() {
            // Fallback to polling
            startPolling(widget_id);
        });
        
        websocket_connections_[widget_id] = ws;
    }
    
    void updateWidget(const std::string& widget_id, const nlohmann::json& update) {
        auto it = loaded_widgets_.find(widget_id);
        if (it == loaded_widgets_.end()) return;
        
        std::string update_type = update["type"];
        
        if (update_type == "data") {
            updateWidgetData(widget_id, update["data"]);
        } else if (update_type == "refresh") {
            refreshWidget(widget_id);
        }
    }
    
    std::string getWidgetUrl(const std::string& widget_id, const WidgetOptions& options) {
        std::stringstream ss;
        ss << endpoint_ << "/embed?widget_id=" << widget_id
           << "&api_key=" << options.api_key
           << "&theme=" << options.config.at("theme")
           << "&height=" << options.height;
        return ss.str();
    }
};
```

### Real-Time Connection Manager

**WebSocket Implementation:**
```cpp
#include <string>
#include <functional>
#include <thread>
#include <chrono>
#include <websocketpp/config/asio_client.hpp>
#include <websocketpp/client.hpp>
#include <nlohmann/json.hpp>

typedef websocketpp::client<websocketpp::config::asio_tls_client> client;
typedef websocketpp::lib::shared_ptr<websocketpp::lib::asio::ssl::context> context_ptr;

class RealTimeConnector {
public:
    RealTimeConnector(const std::string& endpoint, const std::string& api_key)
        : endpoint_(endpoint), api_key_(api_key), 
          reconnect_attempts_(0), max_reconnect_attempts_(5), 
          reconnect_delay_(1000), connected_(false) {
        client_.init_asio();
        client_.set_message_handler([this](websocketpp::connection_hdl hdl, client::message_ptr msg) {
            onMessage(hdl, msg);
        });
        client_.set_open_handler([this](websocketpp::connection_hdl hdl) {
            onConnected(hdl);
        });
        client_.set_close_handler([this](websocketpp::connection_hdl hdl) {
            onDisconnected(hdl);
        });
        client_.set_fail_handler([this](websocketpp::connection_hdl hdl) {
            onError(hdl);
        });
    }
    
    void connect() {
        try {
            std::string uri = endpoint_ + "?api_key=" + api_key_;
            websocketpp::lib::error_code ec;
            client::connection_ptr con = client_.get_connection(uri, ec);
            
            if (ec) {
                // Fallback to polling
                startPolling();
                return;
            }
            
            client_.connect(con);
            
            // Run in separate thread
            std::thread([this]() {
                client_.run();
            }).detach();
            
        } catch (const std::exception& e) {
            // Fallback to polling
            startPolling();
        }
    }
    
private:
    client client_;
    std::string endpoint_;
    std::string api_key_;
    int reconnect_attempts_;
    int max_reconnect_attempts_;
    int reconnect_delay_;
    bool connected_;
    std::function<void(const nlohmann::json&)> widget_update_callback_;
    std::function<void(const nlohmann::json&)> metric_update_callback_;
    
    void onConnected(websocketpp::connection_hdl hdl) {
        connected_ = true;
        reconnect_attempts_ = 0;
        
        // Subscribe to widget updates
        subscribeToWidgets();
    }
    
    void onMessage(websocketpp::connection_hdl hdl, client::message_ptr msg) {
        try {
            nlohmann::json message = nlohmann::json::parse(msg->get_payload());
            
            std::string type = message["type"];
            if (type == "widget_update") {
                handleWidgetUpdate(message);
            } else if (type == "metric_update") {
                handleMetricUpdate(message);
            }
        } catch (...) {
            // Ignore parse errors
        }
    }
    
    void onDisconnected(websocketpp::connection_hdl hdl) {
        connected_ = false;
        
        // Attempt to reconnect
        if (reconnect_attempts_ < max_reconnect_attempts_) {
            std::this_thread::sleep_for(
                std::chrono::milliseconds(reconnect_delay_ * (1 << reconnect_attempts_))
            );
            reconnect_attempts_++;
            connect();
        } else {
            // Fallback to polling
            startPolling();
        }
    }
    
    void onError(websocketpp::connection_hdl hdl) {
        // Fallback to polling
        startPolling();
    }
    
    void startPolling() {
        // Fallback to polling if WebSocket fails
        std::thread([this]() {
            while (true) {
                std::this_thread::sleep_for(std::chrono::seconds(5));
                pollForUpdates();
            }
        }).detach();
    }
    
    void pollForUpdates() {
        NetworkManager network(endpoint_);
        network.get("/updates", [this](const std::string& response) {
            try {
                nlohmann::json updates = nlohmann::json::parse(response);
                for (const auto& update : updates) {
                    handleWidgetUpdate(update);
                }
            } catch (...) {
                // Ignore errors
            }
        });
    }
    
    void subscribeToWidgets() {
        nlohmann::json subscribe_msg;
        subscribe_msg["type"] = "subscribe";
        subscribe_msg["channels"] = nlohmann::json::array({"widget_updates", "metric_updates"});
        
        // Send subscription message
        // client_.send(hdl, subscribe_msg.dump(), websocketpp::frame::opcode::text);
    }
    
    void handleWidgetUpdate(const nlohmann::json& message) {
        if (widget_update_callback_) {
            widget_update_callback_(message);
        }
    }
    
    void handleMetricUpdate(const nlohmann::json& message) {
        if (metric_update_callback_) {
            metric_update_callback_(message);
        }
    }
};
```

### Performance Optimization

### SDK Optimization

**Minification and Compression:**
- Minify JavaScript code
- Gzip/Brotli compression
- Tree shaking to remove unused code
- Code splitting for different features

**Lazy Loading:**
- Load SDK asynchronously
- Defer non-critical code
- Load widgets on demand
- Lazy load analytics features

**Resource Hints:**
```html
<!-- Preconnect to API -->
<link rel="preconnect" href="https://api.example.com">
<link rel="dns-prefetch" href="https://api.example.com">

<!-- Prefetch SDK -->
<link rel="prefetch" href="https://cdn.example.com/sdk/v1/analytics.min.js">
```

### Event Batching

**Batch Strategy:**
```cpp
#include <vector>
#include <chrono>
#include <thread>
#include <mutex>

class EventBatcher {
public:
    struct Options {
        size_t batch_size = 10;
        int flush_interval = 5000; // milliseconds
        int max_wait_time = 30000; // milliseconds
    };
    
    explicit EventBatcher(const Options& options) 
        : options_(options), last_flush_(std::chrono::steady_clock::now()) {
        startAutoFlush();
    }
    
    void add(const AnalyticsSDK::Event& event) {
        std::lock_guard<std::mutex> lock(mutex_);
        
        batch_.push_back(event);
        
        // Flush if batch size reached
        if (batch_.size() >= options_.batch_size) {
            flush();
        }
        // Flush if max wait time exceeded
        else {
            auto now = std::chrono::steady_clock::now();
            auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(
                now - last_flush_
            ).count();
            
            if (elapsed > options_.max_wait_time) {
                flush();
            }
        }
    }
    
    void flush() {
        std::vector<AnalyticsSDK::Event> events;
        
        {
            std::lock_guard<std::mutex> lock(mutex_);
            if (batch_.empty()) return;
            
            events = batch_;
            batch_.clear();
            last_flush_ = std::chrono::steady_clock::now();
        }
        
        // Send batch
        sendBatch(events);
    }
    
private:
    Options options_;
    std::vector<AnalyticsSDK::Event> batch_;
    std::chrono::steady_clock::time_point last_flush_;
    std::mutex mutex_;
    std::function<void(const std::vector<AnalyticsSDK::Event>&)> send_batch_callback_;
    
    void startAutoFlush() {
        std::thread([this]() {
            while (true) {
                std::this_thread::sleep_for(
                    std::chrono::milliseconds(options_.flush_interval)
                );
                flush();
            }
        }).detach();
    }
    
    void sendBatch(const std::vector<AnalyticsSDK::Event>& events) {
        if (send_batch_callback_) {
            send_batch_callback_(events);
        }
    }
};
```

### Widget Optimization

**Lazy Loading Widgets:**
```cpp
#include <vector>
#include <functional>
#include <mutex>

class LazyWidgetLoader {
public:
    struct WidgetInfo {
        std::string widget_id;
        void* container; // Platform-specific widget container
        bool loaded = false;
    };
    
    LazyWidgetLoader() {
        // Platform-specific: Set up visibility detection
        // For Qt: Use QWidget::isVisible() and timers
        // For GTK: Use gtk_widget_get_visible() and timeouts
        // For native: Use platform-specific visibility APIs
    }
    
    void observeWidget(const std::string& widget_id, void* container) {
        std::lock_guard<std::mutex> lock(mutex_);
        
        WidgetInfo info;
        info.widget_id = widget_id;
        info.container = container;
        widgets_.push_back(info);
        
        // Check if widget is visible
        checkVisibility();
    }
    
    void checkVisibility() {
        // Platform-specific visibility check
        // Periodically check if widgets are visible
        std::thread([this]() {
            while (true) {
                std::this_thread::sleep_for(std::chrono::milliseconds(100));
                
                std::lock_guard<std::mutex> lock(mutex_);
                for (auto& widget : widgets_) {
                    if (!widget.loaded && isWidgetVisible(widget.container)) {
                        loadWidget(widget);
                        widget.loaded = true;
                    }
                }
            }
        }).detach();
    }
    
private:
    std::vector<WidgetInfo> widgets_;
    std::mutex mutex_;
    
    bool isWidgetVisible(void* container) {
        // Platform-specific visibility check
        // For Qt: return qobject_cast<QWidget*>(container)->isVisible();
        // For GTK: return gtk_widget_get_visible(GTK_WIDGET(container));
        // For native: Use platform APIs
        return true; // Placeholder
    }
    
    void loadWidget(const WidgetInfo& widget) {
        // Load widget using Analytics SDK
        WidgetLoader::WidgetOptions options;
        options.widget_id = widget.widget_id;
        // ... set other options
        
        WidgetLoader loader;
        loader.loadWidget(options);
    }
};
```

### Privacy and Security

### GDPR/CCPA Compliance

**Cookie Consent:**
- Show consent banner on first visit
- Store consent preference
- Respect opt-out requests
- Clear data on opt-out

**Data Minimization:**
- Collect only necessary data
- Anonymize data when possible
- Hash user identifiers
- Remove PII before sending

### Security Measures

**HTTPS Only:**
- All API calls over HTTPS
- Enforce secure connections
- HSTS headers

**API Key Security:**
- Store API keys securely
- Use token-based authentication
- Rotate keys regularly
- Rate limiting

**Content Security Policy:**
```html
<meta http-equiv="Content-Security-Policy" 
      content="script-src 'self' https://cdn.example.com; 
               connect-src 'self' https://api.example.com;">
```

### Cross-Platform Support

### Mobile SDK (iOS)

**Swift Implementation:**
```swift
class AnalyticsSDK {
    static let shared = AnalyticsSDK()
    
    private var apiKey: String?
    private var endpoint: String
    private var eventQueue: [Event] = []
    
    func initialize(apiKey: String, endpoint: String) {
        self.apiKey = apiKey
        self.endpoint = endpoint
        self.loadQueuedEvents()
        self.startAutoTracking()
    }
    
    func track(eventName: String, properties: [String: Any]?) {
        let event = Event(
            eventId: UUID().uuidString,
            eventName: eventName,
            properties: properties ?? [:],
            timestamp: Date(),
            userId: self.getUserId(),
            sessionId: self.getSessionId()
        )
        
        self.eventQueue.append(event)
        
        if self.eventQueue.count >= 10 {
            self.flush()
        }
    }
    
    func flush() {
        guard let apiKey = self.apiKey else { return }
        
        let events = self.eventQueue
        self.eventQueue.removeAll()
        
        // Send to server
        self.sendEvents(events, apiKey: apiKey) { success in
            if !success {
                // Store for retry
                self.storeEvents(events)
            }
        }
    }
}
```

### Mobile SDK (Android)

**Kotlin Implementation:**
```kotlin
class AnalyticsSDK private constructor() {
    companion object {
        @Volatile
        private var INSTANCE: AnalyticsSDK? = null
        
        fun getInstance(): AnalyticsSDK {
            return INSTANCE ?: synchronized(this) {
                INSTANCE ?: AnalyticsSDK().also { INSTANCE = it }
            }
        }
    }
    
    private var apiKey: String? = null
    private var endpoint: String = ""
    private val eventQueue = mutableListOf<Event>()
    
    fun initialize(apiKey: String, endpoint: String) {
        this.apiKey = apiKey
        this.endpoint = endpoint
        loadQueuedEvents()
        startAutoTracking()
    }
    
    fun track(eventName: String, properties: Map<String, Any>? = null) {
        val event = Event(
            eventId = UUID.randomUUID().toString(),
            eventName = eventName,
            properties = properties ?: emptyMap(),
            timestamp = System.currentTimeMillis(),
            userId = getUserId(),
            sessionId = getSessionId()
        )
        
        eventQueue.add(event)
        
        if (eventQueue.size >= 10) {
            flush()
        }
    }
    
    fun flush() {
        val events = eventQueue.toList()
        eventQueue.clear()
        
        sendEvents(events) { success ->
            if (!success) {
                storeEvents(events)
            }
        }
    }
}
```

## Step 8: API Design

### Event Collection API

```http
POST /api/v1/events
Content-Type: application/json
Authorization: Bearer {api_key}

{
  "events": [
    {
      "event_id": "uuid",
      "event_name": "page_view",
      "properties": {...},
      "timestamp": "2025-11-04T10:00:00Z",
      "user_id": "user-123",
      "session_id": "session-456"
    }
  ]
}

Response: 200 OK
{
  "status": "success",
  "processed": 1,
  "failed": 0
}
```

### Widget API

```http
GET /api/v1/widgets/{widget_id}
Authorization: Bearer {api_key}

Response: 200 OK
{
  "widget_id": "uuid",
  "widget_type": "chart",
  "data": {
    "series": [
      {"time": "2025-11-01", "value": 1000},
      {"time": "2025-11-02", "value": 1200}
    ]
  },
  "config": {
    "theme": "light",
    "height": 400
  }
}
```

### Embedding API

```http
GET /api/v1/embed?widget_id={widget_id}&api_key={api_key}

Response: 200 OK
{
  "embed_code": "<iframe src='...'></iframe>",
  "embed_url": "https://embed.example.com/widget?token=...",
  "javascript_sdk": "<script src='...'></script>"
}
```

## Step 9: Monitoring and Debugging

### Client-Side Monitoring

**Error Tracking:**
```cpp
#include <exception>
#include <stdexcept>
#include <mutex>

class ErrorTracker {
public:
    ErrorTracker(AnalyticsSDK& sdk) : sdk_(sdk) {
        setupErrorHandling();
    }
    
    void trackError(const std::exception& error, const std::map<std::string, std::string>& context) {
        std::map<std::string, std::string> properties = context;
        properties["error_message"] = error.what();
        properties["error_type"] = typeid(error).name();
        
        sdk_.track("error", properties);
    }
    
    void setupErrorHandling() {
        // Platform-specific error handling
        // For Qt: Connect to QApplication::notify() or use qInstallMessageHandler
        // For GTK: Use g_log_set_handler
        // For native: Use std::set_terminate or signal handlers
        
        // Set up global exception handler
        std::set_terminate([this]() {
            try {
                std::rethrow_exception(std::current_exception());
            } catch (const std::exception& e) {
                trackError(e, {{"type", "terminate_handler"}});
            }
        });
    }
    
private:
    AnalyticsSDK& sdk_;
};
```

### Performance Monitoring

**Performance Metrics:**
```cpp
#include <chrono>
#include <map>

class PerformanceMonitor {
public:
    PerformanceMonitor(AnalyticsSDK& sdk) : sdk_(sdk) {
        start_time_ = std::chrono::steady_clock::now();
    }
    
    void trackPerformance() {
        auto now = std::chrono::steady_clock::now();
        auto page_load_time = std::chrono::duration_cast<std::chrono::milliseconds>(
            now - start_time_
        ).count();
        
        std::map<std::string, std::string> properties;
        properties["page_load_time"] = std::to_string(page_load_time);
        properties["dom_ready_time"] = std::to_string(getDOMReadyTime());
        properties["first_paint"] = std::to_string(getFirstPaint());
        
        sdk_.track("performance", properties);
    }
    
private:
    AnalyticsSDK& sdk_;
    std::chrono::steady_clock::time_point start_time_;
    
    int64_t getDOMReadyTime() {
        // Platform-specific: Measure DOM ready time
        // This is application-specific
        return 0;
    }
    
    int64_t getFirstPaint() {
        // Platform-specific: Measure first paint
        // This is application-specific
        return 0;
    }
};
```

### Testing and Quality Assurance

### Testing Strategy

**Unit Tests:**
- Test event tracking
- Test queue management
- Test storage operations
- Test network requests

**Integration Tests:**
- Test SDK initialization
- Test widget loading
- Test real-time updates
- Test error handling

**Browser Compatibility:**
- Test on all major browsers
- Test on mobile browsers
- Test on legacy browsers
- Test with different network conditions

## Conclusion

Designing a client-side embedded report events system requires:

1. **Lightweight SDK**: Minimal impact on page load
2. **Efficient Event Tracking**: Batching and queuing
3. **Offline Support**: Store events when offline
4. **Privacy Compliance**: GDPR/CCPA support
5. **Widget Embedding**: Easy integration
6. **Real-Time Updates**: WebSocket/SSE connections
7. **Cross-Platform**: Web, iOS, Android support
8. **Performance**: Optimize for speed and efficiency

**Key Design Principles:**
- **Non-Blocking**: Never block host application
- **Privacy-First**: Default to privacy-preserving
- **Offline-Capable**: Work without connectivity
- **Performant**: Minimal performance impact
- **Easy Integration**: Single script tag
- **Error Resilient**: Graceful error handling

This system design demonstrates understanding of client-side architecture, browser APIs, performance optimization, privacy compliance, and cross-platform development—all critical for building production-grade embedded analytics systems.

