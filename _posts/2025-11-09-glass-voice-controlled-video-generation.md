---
layout: post
title: "Smart Glass: Voice-Controlled Video Generation System Design"
date: 2025-11-09
categories: [System Design, AR Glass, AR, Voice Control, Video Processing, AI/ML, Architecture]
excerpt: "A comprehensive system design for smart glasses featuring voice-controlled automatic video generation, covering current smart glass architecture and the new feature to generate 2-minute memory videos from natural language commands."
---

## Introduction

Smart glasses represent the next generation of augmented reality devices, combining advanced computer vision, AI, and voice control to create immersive experiences. This post explores the current smart glass architecture and designs a new feature that enables users to generate personalized memory videos through natural language voice commands.

**Example Use Case:** User says "Create a 2-minute video of me and my wife's trip in Paris" and the system automatically finds, selects, and compiles relevant video clips into a polished memory video.

---

## Smart Glass Specifications

### Audio

**Speaker:**
- 2 custom-built open-ear speakers
- Loudness and bass: 76.1 dB(C)

**Microphone:**
- 6-mic system:
  - 2 microphones in left arm
  - 2 microphones in right arm
  - 1 microphone near nose pad
  - 1 contact microphone

### Camera

**Resolution:**
- 12 MP ultra-wide camera

**Image Acquisition:**
- 3024 × 4032 pixels

**Video Acquisition:**
- 1440 × 1920 pixels @ 30 FPS
- 3x digital zoom

### Battery

**Frame Capacity:**
- 960 mWh (248 mAh)
- Up to 6 hours mixed-use

**Frame Charging Case:**
- Up to 24 additional hours with fully charged case

**Neural Band:**
- Capacity: 134 mAh
- Usage time: Up to 18 hours

### Water Resistance

- **Frame**: IPx4 (splash resistant)
- **Neural Band**: IPx7 (water resistant up to 1 meter)

### Memory

**Internal Storage:**
- 32 GB Flash storage
- Stores up to 1,000 photos
- Stores 100+ 30-second videos

**RAM:**
- 2 GB LPDDR4x

### Connectivity

**Wi-Fi:**
- Wi-Fi 6 certified

**Bluetooth:**
- Bluetooth 5.3 (Frame)
- Bluetooth 5.2 (Neural Band)

**OS Compatibility:**
- iOS 15.2 and above
- Android 10 minimum

---

## Current Smart Glass Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────┐
│           Smart Glass Hardware                   │
│  (Cameras, Sensors, Display, Audio, Compute)   │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│         Smart Glass OS (AOSP-based)             │
│  (Android Runtime, AR Framework, Services)      │
└──────────────┬──────────────────────────────────┘
               │
       ┌───────┴───────┐
       │               │
┌──────▼──────┐  ┌─────▼──────┐
│  On-Device  │  │   Cloud     │
│  Services   │  │  Services   │
└─────────────┘  └─────────────┘
```

### Hardware Components

**1. Imaging System**
- **Camera**: 12 MP ultra-wide camera
- **Image Resolution**: 3024 × 4032 pixels
- **Video Resolution**: 1440 × 1920 pixels @ 30 FPS
- **Zoom**: 3x digital zoom
- **Storage Capacity**: Up to 1,000 photos, 100+ 30-second videos

**2. Display System**
- **Waveguide Display**: Transparent AR display overlay
- **Resolution**: High-resolution micro-displays
- **Field of View**: Wide FOV for immersive AR experience
- **Brightness**: High brightness for outdoor use

**3. Audio System**
- **Speakers**: 2 custom-built open-ear speakers
- **Audio Quality**: 76.1 dB(C) loudness and bass
- **Microphones**: 6-mic system for voice capture and noise cancellation:
  - 2 microphones in left arm
  - 2 microphones in right arm
  - 1 microphone near nose pad
  - 1 contact microphone
- **Spatial Audio**: 3D audio processing capabilities

**4. Compute Platform**
- **SoC**: Custom mobile SoC optimized for AR/ML workloads
- **AI Accelerator**: Dedicated NPU for on-device ML inference
- **Memory**: 2 GB LPDDR4x RAM
- **Storage**: 32 GB Flash storage
- **Battery**: 
  - Frame: 960 mWh (248 mAh), up to 6 hours mixed-use
  - Charging Case: Up to 24 additional hours
  - Neural Band: 134 mAh, up to 18 hours

**5. Connectivity**
- **Wi-Fi**: Wi-Fi 6 certified
- **Bluetooth**: Bluetooth 5.3 (Frame), Bluetooth 5.2 (Neural Band)
- **OS Support**: iOS 15.2+, Android 10+

**6. Sensors**
- **IMU**: Accelerometer, gyroscope, magnetometer
- **GPS**: Location tracking
- **Ambient Light**: Adaptive display brightness
- **Proximity**: Hand/object detection

**7. Water Resistance**
- **Frame**: IPx4 (splash resistant)
- **Neural Band**: IPx7 (water resistant up to 1 meter)

### Software Architecture

**1. Smart Glass OS Layer**

**Base:**
- Android-based OS (AOSP)
- Custom modifications for AR/VR
- Low-latency rendering pipeline

**Core Services:**
- **AR Framework**: SLAM (Simultaneous Localization and Mapping)
- **Camera Service**: Image/video capture and processing
- **Audio Service**: Voice capture, spatial audio
- **Display Service**: AR overlay rendering
- **Sensor Service**: Sensor fusion and tracking

**2. On-Device Services**

**Media Capture Service:**
- Real-time video recording
- Image capture
- Metadata extraction (GPS, timestamp, orientation)
- On-device compression

**AR Service:**
- SLAM tracking
- Object detection and tracking
- Plane detection
- Hand tracking
- Eye tracking

**AI/ML Service:**
- On-device ML inference
- Face detection and recognition
- Object detection
- Scene understanding
- Voice recognition (on-device)

**3. Cloud Services**

**Media Storage:**
- Video and image storage (blob storage)
- Metadata database
- Backup and sync

**AI/ML Services:**
- Advanced ML models (too large for device)
- Video analysis and understanding
- Natural language processing
- Content generation

**4. Application Layer**

**Core Apps:**
- Camera app
- AR apps
- Voice assistant
- Settings and configuration

---

## Current System Components

### 1. Media Capture Pipeline

**Flow:**
```
Camera Hardware → Camera HAL → Camera Service → Media Framework → Storage
```

**Components:**
- **Camera HAL**: Hardware abstraction layer
- **Camera Service**: Manages camera sessions
- **Media Framework**: Encoding, compression
- **Storage**: Local storage + cloud sync

**Features:**
- 1440 × 1920 @ 30 FPS video recording
- Real-time stabilization
- HDR processing
- Low-light enhancement
- 3x digital zoom

### 2. AR Framework

**SLAM System:**
- **Visual SLAM**: Camera-based tracking
- **IMU Fusion**: Sensor fusion for accuracy
- **Relocalization**: Recovery from tracking loss
- **Mapping**: Dense/sparse mapping

**Rendering Pipeline:**
- **Compositor**: AR overlay composition
- **Rendering Engine**: 3D graphics rendering
- **Display Driver**: Waveguide display control

### 3. Voice Assistant

**Hardware:**
- **6-mic system** for superior voice capture:
  - 2 microphones in left arm
  - 2 microphones in right arm
  - 1 microphone near nose pad
  - 1 contact microphone
- **2 custom-built open-ear speakers** (76.1 dB(C) loudness and bass)

**On-Device Components:**
- **Wake Word Detection**: "Hey Meta" detection
- **Voice Activity Detection**: Detect when user is speaking
- **Beamforming**: Use 6-mic array for noise cancellation and directional audio
- **On-Device NLU**: Basic intent recognition
- **Command Execution**: Execute simple commands locally

**Cloud Components:**
- **Advanced NLU**: Complex natural language understanding
- **Conversational AI**: Multi-turn conversations
- **Knowledge Graph**: Entity recognition and resolution

### 4. Cloud Infrastructure

**Storage:**
- **Blob Storage**: Video/image storage (S3-like)
- **Metadata DB**: Structured metadata (Cassandra/PostgreSQL)
- **Search Index**: Full-text and semantic search (Elasticsearch)

**Processing:**
- **Video Processing**: Transcoding, analysis
- **AI/ML Inference**: Large model inference
- **Content Generation**: Video editing, effects

---

## New Feature: Voice-Controlled Video Generation

### Feature Requirements

**User Command:** "Create a 2-minute video of me and my wife's trip in Paris"

**Functional Requirements:**
1. **Voice Command Recognition**
   - Understand natural language command
   - Extract entities (people, location, time, duration)
   - Parse intent (create memory video)

2. **Video Discovery**
   - Search user's video library
   - Filter by location (Paris)
   - Filter by people (user + wife)
   - Filter by time (trip dates)

3. **Video Selection**
   - Select best clips (10-20 clips)
   - Rank by relevance, quality, diversity
   - Ensure 2-minute total duration

4. **Video Generation**
   - Trim selected clips
   - Add transitions
   - Add music/effects
   - Generate final 2-minute video

5. **Delivery**
   - Return video quickly (< 5 seconds)
   - Store in user's library
   - Option to share

### Non-Functional Requirements

- **Latency**: Generate video in 2-5 seconds
- **Quality**: High-quality output (1080p minimum)
- **Scalability**: Handle millions of users
- **Reliability**: 99.9% success rate
- **Privacy**: Process user data securely

---

## System Architecture for New Feature

### High-Level Flow (Hybrid Mode)

```
User Voice Command (Smart Glass)
    ↓
Voice Recognition (On-Device)
    ↓
NLP Processing (On-Device or Cloud)
    ↓
WiFi Direct Connection to Phone
    ↓
Transfer Request to Phone App
    ↓
Phone App: Video Search (Local + Cloud Metadata)
    ↓
Phone App: Fetch Videos/Images via WiFi Direct
    ↓
Phone App: Video Selection Algorithm
    ↓
Phone App: Video Processing Pipeline (On-Phone)
    ↓
Phone App: Generate 2-minute Video
    ↓
Transfer Final Video to Smart Glass via WiFi Direct
    ↓
Display on Smart Glass
```

### Component Architecture (Hybrid Mode)

```
┌─────────────────────────────────────────┐
│      Smart Glass Device (Local)          │
│  ┌───────────────────────────────────┐ │
│  │ Voice Capture & Wake Word          │ │
│  │ On-Device NLU                      │ │
│  │ WiFi Direct Client                 │ │
│  │ Media Display                       │ │
│  └──────────────┬──────────────────────┘ │
└─────────────────┼───────────────────────┘
                  │
         ┌────────▼────────┐
         │  WiFi Direct   │
         │  (P2P Connection)│
         └────────┬────────┘
                  │
┌─────────────────▼───────────────────────┐
│      Phone App (Local Processing)       │
│  ┌───────────────────────────────────┐ │
│  │ WiFi Direct Server                │ │
│  │ Media Library Manager              │ │
│  │ Video Search Engine                │ │
│  │ Video Processing Engine            │ │
│  │ (FFmpeg, GPU Acceleration)        │ │
│  └──────────────┬──────────────────────┘ │
└─────────────────┼───────────────────────┘
                  │
         ┌────────┴────────┐
         │                 │
    ┌────▼────┐      ┌─────▼─────┐
    │  Phone  │      │   Cloud   │
    │ Storage │      │  Services │
    │ (Local) │      │ (Optional)│
    └─────────┘      └───────────┘
                           │
                    ┌──────▼──────┐
                    │  Metadata   │
                    │  Database   │
                    │  (Cloud)    │
                    └─────────────┘
```

### Hybrid Mode Architecture Details

**Primary Path: Phone-Based Processing (WiFi Direct)**

**Flow:**
1. **Smart Glass** captures voice command
2. **Smart Glass** processes intent locally or sends to cloud for NLP
3. **Smart Glass** establishes WiFi Direct connection to phone
4. **Phone App** receives request and searches local media library
5. **Phone App** fetches videos/images from phone storage (or cloud if needed)
6. **Phone App** processes videos locally (trimming, merging, effects)
7. **Phone App** generates final 2-minute video on phone
8. **Phone App** transfers final video to Smart Glass via WiFi Direct
9. **Smart Glass** displays video

**Fallback Path: Cloud Processing**

- If WiFi Direct unavailable → Use cloud processing
- If phone processing fails → Fallback to cloud
- If videos not on phone → Fetch from cloud storage

### Storage Architecture: Local vs Remote

**Storage Layers:**

**1. Local Storage (On Smart Glass Device)**
- **Purpose**: Temporary cache, recent media, offline access
- **Capacity**: 32 GB Flash storage (stores up to 1,000 photos, 100+ 30-second videos)
- **Use Cases**:
  - Recent videos/photos cache
  - Offline viewing
  - Quick access to frequently viewed content
  - Temporary storage before cloud sync

**2. Remote Storage (Cloud - S3/Azure Blob)**
- **Purpose**: Primary storage, long-term archive, backup
- **Capacity**: Unlimited (scales with usage)
- **Use Cases**:
  - All user videos and photos (primary storage)
  - Processed/generated videos
  - Long-term archive
  - Cross-device sync
  - Backup and disaster recovery

**Storage Flow:**
```
Smart Glass Device
    │
    ├─→ Local Cache (Recent videos, metadata cache)
    │   └─→ Limited capacity, fast access
    │
    └─→ Cloud Sync → Remote Blob Storage (S3)
        └─→ Unlimited capacity, accessible from anywhere
```

**Why Remote Storage (S3) is Used:**
- **Scalability**: Handle petabytes of video data
- **Durability**: 99.999999999% (11 9's) durability
- **Accessibility**: Access from any device, anywhere
- **Cost**: Cost-effective for large-scale storage
- **Backup**: Automatic backup and replication
- **Processing**: Cloud services can directly access videos for processing

**Hybrid Approach:**
- **Local**: Fast access, offline capability, recent content
- **Remote**: Unlimited storage, backup, cross-device sync, processing
- **Sync**: Automatic sync between local and remote

### Local WiFi Transfer Options

**Option 1: Direct WiFi Transfer (Phone ↔ Smart Glass)**

**Architecture:**
```
Phone (WiFi Direct/Hotspot) ←→ Smart Glass (WiFi Client)
    │                              │
    └──→ Local WiFi Network ───────┘
```

**Implementation Approaches:**

**1. WiFi Direct (Peer-to-Peer)**
- **Technology**: WiFi Direct (P2P)
- **Setup**: Direct connection between devices (no router needed)
- **Speed**: Up to 250 Mbps (WiFi 5) or 1+ Gbps (WiFi 6)
- **Range**: ~200 meters
- **Use Case**: Fast local transfer, no internet required

**Flow:**
```
1. Phone creates WiFi Direct group
2. Smart Glass discovers and connects
3. Phone acts as Group Owner (GO)
4. Transfer media files directly
5. No internet connection needed
```

**Pros:**
- ✅ Fast transfer speed
- ✅ No internet required
- ✅ Private (local only)
- ✅ No data charges
- ✅ Low latency

**Cons:**
- ❌ Requires both devices nearby
- ❌ Setup complexity
- ❌ Battery drain on both devices

**2. Local WiFi Network (Same Network)**
- **Technology**: Standard WiFi (802.11)
- **Setup**: Both devices on same WiFi network
- **Speed**: Depends on WiFi standard (WiFi 6: 1+ Gbps)
- **Range**: WiFi router range
- **Use Case**: Home/office sync, multiple devices

**Flow:**
```
1. Phone and Smart Glass connect to same WiFi router
2. Devices discover each other via mDNS/Bonjour
3. Establish direct connection (IP addresses)
4. Transfer media files over local network
5. No data leaves local network
```

**Pros:**
- ✅ Fast transfer (local network speed)
- ✅ No internet required
- ✅ Can sync multiple devices
- ✅ Works with existing WiFi
- ✅ Lower battery drain than WiFi Direct

**Cons:**
- ❌ Requires WiFi router
- ❌ Both devices must be on same network
- ❌ Router range limitation

**3. Phone Hotspot Mode**
- **Technology**: Phone creates WiFi hotspot
- **Setup**: Phone creates hotspot, Smart Glass connects
- **Speed**: Depends on phone's WiFi capability
- **Use Case**: On-the-go sync, no router available

**Flow:**
```
1. Phone enables WiFi hotspot
2. Smart Glass connects to phone's hotspot
3. Phone and Smart Glass on same network
4. Transfer media files
5. Phone uses cellular data for internet (if needed)
```

**Pros:**
- ✅ Works anywhere (no router needed)
- ✅ Phone controls connection
- ✅ Can use cellular data for cloud sync
- ✅ Portable

**Cons:**
- ❌ Phone battery drain
- ❌ Slower than WiFi Direct
- ❌ May use cellular data (if enabled)

**Implementation Details:**

**Discovery Protocol:**
```python
# mDNS/Bonjour for device discovery
import zeroconf

class DeviceDiscovery:
    def discover_devices(self):
        # Discover Smart Glass devices on local network
        zeroconf.Zeroconf().browse_services(
            "_metaglass._tcp.local.",
            "_services._dns-sd._udp.local."
        )
```

**Transfer Protocol:**
```python
# HTTP server on phone, client on Smart Glass
# Or use WebRTC for peer-to-peer transfer

class LocalTransfer:
    def transfer_media(self, phone_ip, files):
        # Connect to phone's local HTTP server
        for file in files:
            download(f"http://{phone_ip}:8080/media/{file}")
```

**Security:**
- **Pairing**: Initial pairing via QR code or Bluetooth
- **Encryption**: TLS/SSL for transfer
- **Authentication**: Device certificates or tokens
- **Authorization**: User approval for transfers

**Option 2: Hybrid Approach (Local + Cloud)**

**Smart Sync Strategy:**
```
Priority 1: Local WiFi Transfer (if available)
    ↓ (if local transfer fails or unavailable)
Priority 2: Cloud Sync (via internet)
```

**Benefits:**
- Fast local transfer when devices are nearby
- Fallback to cloud when devices are apart
- Best of both worlds

**Implementation:**
```python
class SmartSync:
    def sync_media(self, files):
        # Try local WiFi first
        if self.is_local_wifi_available():
            try:
                self.transfer_via_local_wifi(files)
                return "Local transfer successful"
            except Exception as e:
                # Fallback to cloud
                pass
        
        # Fallback to cloud sync
        self.sync_via_cloud(files)
        return "Cloud sync initiated"
```

**Option 3: Background Sync Service**

**Continuous Sync:**
- Background service on phone
- Automatically syncs new media when devices are on same network
- Incremental sync (only new/changed files)
- Low power consumption

**Features:**
- **Auto-Discovery**: Automatically find Smart Glass when on same network
- **Incremental Sync**: Only transfer new/changed files
- **Background Processing**: Sync without user intervention
- **Bandwidth Management**: Throttle during active use
- **Resume Support**: Resume interrupted transfers

**Comparison of Options:**

| Option | Speed | Setup | Internet Required | Battery Impact | Use Case |
|--------|-------|-------|-------------------|----------------|----------|
| **WiFi Direct** | Very Fast | Medium | No | High | Fast one-time transfer |
| **Local WiFi** | Fast | Easy | No | Low | Regular sync at home |
| **Phone Hotspot** | Medium | Easy | Optional | Medium | On-the-go sync |
| **Cloud Sync** | Medium | Easy | Yes | Low | Always available |

**Recommended Approach: Hybrid**

**Implementation Strategy:**
1. **Primary**: Local WiFi transfer when devices are on same network
2. **Fallback**: Cloud sync when local transfer unavailable
3. **User Choice**: Allow user to choose sync method
4. **Auto-Detection**: Automatically detect best method

**Example User Flow:**
```
User opens Smart Glass app on phone
    ↓
App detects Smart Glass on local WiFi
    ↓
"Sync media via local WiFi?" → User confirms
    ↓
Fast local transfer (no internet, no data charges)
    ↓
Media available on Smart Glass immediately
```

**Technical Implementation:**

**Phone Side (Server):**
```python
# Flask/FastAPI server on phone
from flask import Flask, send_file

app = Flask(__name__)

@app.route('/media/<filename>')
def get_media(filename):
    return send_file(f'/storage/media/{filename}')

@app.route('/sync/initiate')
def initiate_sync():
    # Return list of available media
    return {'files': list_media_files()}
```

**Smart Glass Side (Client):**
```python
# Client on Smart Glass
class MediaSyncClient:
    def sync_from_phone(self, phone_ip):
        # Discover phone
        phone_url = f"http://{phone_ip}:8080"
        
        # Get file list
        files = requests.get(f"{phone_url}/sync/initiate").json()
        
        # Download files
        for file in files['files']:
            download(f"{phone_url}/media/{file}")
```

**Benefits of Local WiFi Transfer:**
- ✅ **Speed**: Much faster than cloud (local network speed)
- ✅ **Privacy**: Data never leaves local network
- ✅ **Cost**: No data charges
- ✅ **Reliability**: Works offline
- ✅ **Latency**: Lower latency than cloud
- ✅ **Bandwidth**: Doesn't consume internet bandwidth

---

## Detailed Component Design

### 1. Voice Recognition Service

**On-Device (Smart Glass):**

**Wake Word Detection:**
- Always-on wake word detection ("Hey Meta")
- Low-power DSP processing
- < 100ms latency

**Voice Capture:**
- **6-mic system**:
  - 2 microphones in left arm
  - 2 microphones in right arm
  - 1 microphone near nose pad
  - 1 contact microphone
- **Beamforming**: Use mic array for directional audio capture
- **Noise cancellation**: Multi-mic noise reduction
- **Voice activity detection**: Detect when user is speaking
- **Audio quality**: Optimized for voice commands

**On-Device NLU (Basic):**
- Simple command recognition
- Intent classification (create_video, take_photo, etc.)
- Basic entity extraction
- Fallback to cloud for complex queries

**Cloud NLU (Advanced):**

**Natural Language Understanding:**
```python
# Example: "Create a 2-minute video of me and my wife's trip in Paris"

Intent: CREATE_MEMORY_VIDEO
Entities:
  - Duration: 2 minutes
  - People: ["me", "wife"]
  - Location: "Paris"
  - Time: (infer from context - recent trip)
  - Relationship: "wife" → person_id mapping
```

**NLP Pipeline:**
1. **Speech-to-Text**: Convert audio to text
2. **Intent Recognition**: Classify intent
3. **Entity Extraction**: Extract entities (NER)
4. **Relationship Resolution**: Map "wife" to person_id
5. **Query Generation**: Generate search query

**Technology:**
- **Speech-to-Text**: Whisper, Google Speech-to-Text
- **NLU**: BERT-based models, GPT models
- **Entity Recognition**: spaCy, NER models
- **Knowledge Graph**: Resolve relationships

### 2. WiFi Direct Connection Service

**On Smart Glass (Client):**

**WiFi Direct Client:**
- Discover phone devices
- Connect to phone's WiFi Direct group
- Maintain connection
- Handle reconnection

**Implementation:**
```kotlin
// Android WiFi Direct API
class WiFiDirectClient {
    fun discoverPeers() {
        val manager = context.getSystemService(Context.WIFI_P2P_SERVICE) as WifiP2pManager
        manager.discoverPeers(channel, object : WifiP2pManager.ActionListener {
            override fun onSuccess() {
                // Peers discovered
            }
            override fun onFailure(reasonCode: Int) {
                // Handle failure
            }
        })
    }
    
    fun connectToDevice(device: WifiP2pDevice) {
        val config = WifiP2pConfig().apply {
            deviceAddress = device.deviceAddress
        }
        manager.connect(channel, config, connectionListener)
    }
}
```

**On Phone App (Server):**

**WiFi Direct Server:**
- Create WiFi Direct group
- Accept connections from Smart Glass
- Serve media files
- Handle video generation requests

**Implementation:**
```kotlin
class WiFiDirectServer {
    fun createGroup() {
        manager.createGroup(channel, object : WifiP2pManager.ActionListener {
            override fun onSuccess() {
                // Group created, phone is Group Owner
            }
            override fun onFailure(reasonCode: Int) {
                // Handle failure
            }
        })
    }
    
    fun startMediaServer() {
        // Start HTTP server for media transfer
        val server = NanoHTTPD(8080)
        server.start()
    }
}
```

### 3. Phone App: Video Search Service

**Search Strategy (Hybrid):**

**1. Local Search (Primary):**
- Search phone's local media library
- Use MediaStore API (Android)
- Filter by location, date, people
- Fast, no network required

**2. Cloud Metadata Search (Optional):**
- Query cloud metadata database for video locations
- Download videos not on phone if needed
- Sync metadata for better search

**Phone App Implementation:**
```kotlin
class PhoneVideoSearch {
    fun searchLocalVideos(query: VideoQuery): List<Video> {
        // Search local MediaStore
        val projection = arrayOf(
            MediaStore.Video.Media._ID,
            MediaStore.Video.Media.DATA,
            MediaStore.Video.Media.DATE_TAKEN,
            MediaStore.Video.Media.DURATION
        )
        
        val selection = buildSelection(query)
        val cursor = contentResolver.query(
            MediaStore.Video.Media.EXTERNAL_CONTENT_URI,
            projection,
            selection,
            null,
            null
        )
        
        return cursor?.use { parseVideos(it) } ?: emptyList()
    }
    
    fun searchCloudMetadata(query: VideoQuery): List<VideoMetadata> {
        // Query cloud metadata database
        // Return metadata for videos (including those not on phone)
        return cloudService.searchMetadata(query)
    }
    
    fun fetchVideoIfNeeded(metadata: VideoMetadata): File? {
        // If video not on phone, download from cloud
        if (!isVideoOnPhone(metadata.videoId)) {
            return downloadFromCloud(metadata.blobUrl)
        }
        return getLocalVideoFile(metadata.videoId)
    }
}
```

**Local Metadata Storage (SQLite on Phone):**
```sql
CREATE TABLE local_video_metadata (
    video_id TEXT PRIMARY KEY,
    file_path TEXT,
    timestamp INTEGER,
    location_name TEXT,
    gps_lat REAL,
    gps_lon REAL,
    detected_faces TEXT,  -- JSON array
    duration_seconds INTEGER,
    file_size INTEGER,
    last_modified INTEGER
);

CREATE INDEX idx_location ON local_video_metadata(location_name);
CREATE INDEX idx_timestamp ON local_video_metadata(timestamp);
```

**Search Query (Phone App):**
```kotlin
fun searchVideos(location: String, people: List<String>, timeRange: TimeRange): List<Video> {
    // 1. Search local videos first
    val localVideos = searchLocalVideos(location, people, timeRange)
    
    // 2. If not enough results, search cloud metadata
    if (localVideos.size < MIN_RESULTS) {
        val cloudMetadata = searchCloudMetadata(location, people, timeRange)
        val cloudVideos = cloudMetadata.map { fetchVideoIfNeeded(it) }
        return localVideos + cloudVideos.filterNotNull()
    }
    
    return localVideos
}
```

### 4. Phone App: Video Selection Algorithm

**Location: Phone App (Local Processing)**

**Selection Criteria:**

**1. Relevance Score:**
- Location match (Paris)
- People match (user + wife)
- Time match (trip dates)
- Semantic similarity

**2. Quality Score:**
- Video resolution
- Stability (no shake)
- Lighting quality
- Audio quality

**3. Diversity Score:**
- Different scenes/locations
- Different times of day
- Different activities
- Temporal distribution

**Selection Algorithm (Phone App):**
```kotlin
class VideoSelectionEngine {
    fun selectClips(videos: List<Video>, targetDuration: Int = 120): List<VideoClip> {
        // Score and rank videos
        val scoredVideos = videos.map { video ->
            val score = (
                relevanceScore(video) * 0.5f +
                qualityScore(video) * 0.3f +
                diversityScore(video, selected) * 0.2f
            )
            Pair(video, score)
        }.sortedByDescending { it.second }
        
        // Select clips to fill duration
        val selected = mutableListOf<VideoClip>()
        var totalDuration = 0
        
        for ((video, score) in scoredVideos) {
            // Extract best segment (e.g., 10-15 seconds)
            val segment = extractBestSegment(video, duration = 12)
            
            if (totalDuration + segment.duration <= targetDuration) {
                selected.add(segment)
                totalDuration += segment.duration
            } else {
                // Fill remaining time
                val remaining = targetDuration - totalDuration
                if (remaining > 5) {  // Minimum segment length
                    val finalSegment = extractSegment(video, duration = remaining)
                    selected.add(finalSegment)
                }
                break
            }
        }
        
        return selected
    }
    
    private fun extractBestSegment(video: Video, duration: Int): VideoClip {
        // Analyze video for interesting moments
        val sceneChanges = detectSceneChanges(video)
        val keyFrames = identifyKeyFrames(video)
        
        // Extract segment around most interesting part
        val bestStart = findBestStartTime(video, sceneChanges, keyFrames)
        return VideoClip(video, bestStart, bestStart + duration)
    }
}
```

**Best Segment Extraction:**
- Analyze video for interesting moments
- Detect scene changes
- Identify key frames
- Extract segments around highlights

### 5. Phone App: Video Processing Pipeline

**Location: Phone App (Local Processing with GPU Acceleration)**

**Processing Steps:**

**1. Video Trimming:**
- Extract selected segments from source videos
- Precise frame-level trimming using FFmpeg
- Maintain audio sync
- Use MediaCodec API for hardware acceleration

**2. Transitions:**
- Add smooth transitions between clips
- Fade in/out
- Crossfade
- Wipe transitions

**3. Enhancement:**
- Color correction
- Stabilization (if needed)
- Audio normalization
- Noise reduction

**4. Music/Effects:**
- Add background music (user preference or auto-select)
- Match music tempo to video pace
- Add sound effects (optional)
- Audio mixing

**5. Final Assembly:**
- Combine all segments
- Add title/credits (optional)
- Final encoding (H.264/H.265)
- Generate thumbnail

**Processing Pipeline (Phone App):**
```kotlin
class PhoneVideoProcessor {
    private val ffmpeg = FFmpeg.getInstance(context)
    
    suspend fun processVideo(clips: List<VideoClip>, config: VideoConfig): File {
        // Step 1: Trim clips
        val trimmedClips = clips.map { clip ->
            trimVideo(clip.source, clip.startTime, clip.endTime)
        }
        
        // Step 2: Add transitions
        val withTransitions = addTransitions(trimmedClips)
        
        // Step 3: Enhance
        val enhanced = enhanceVideo(withTransitions)
        
        // Step 4: Add music
        val withMusic = addMusic(enhanced, config.musicTrack)
        
        // Step 5: Final assembly
        val finalVideo = assembleVideo(withMusic)
        
        return finalVideo
    }
    
    private suspend fun trimVideo(
        source: File, 
        start: Long, 
        end: Long
    ): File {
        // Use FFmpeg or MediaCodec for trimming
        val output = File(context.cacheDir, "trimmed_${System.currentTimeMillis()}.mp4")
        
        val command = arrayOf(
            "-i", source.absolutePath,
            "-ss", start.toString(),
            "-t", (end - start).toString(),
            "-c", "copy",  // Fast copy mode
            output.absolutePath
        )
        
        ffmpeg.execute(command)
        return output
    }
    
    private suspend fun assembleVideo(clips: List<File>): File {
        // Create concat file for FFmpeg
        val concatFile = createConcatFile(clips)
        val output = File(context.getExternalFilesDir(null), "final_video.mp4")
        
        val command = arrayOf(
            "-f", "concat",
            "-safe", "0",
            "-i", concatFile.absolutePath,
            "-c", "copy",
            output.absolutePath
        )
        
        ffmpeg.execute(command)
        return output
    }
}
```

**Technology (Phone App):**
- **FFmpeg Mobile**: FFmpeg for Android/iOS
- **MediaCodec API**: Hardware-accelerated encoding/decoding (Android)
- **VideoToolbox**: Hardware acceleration (iOS)
- **GPU Acceleration**: Use device GPU for processing
- **ML Kit**: On-device ML for scene detection (optional)

**Performance Optimization:**
- **Hardware Acceleration**: Use MediaCodec/VideoToolbox
- **Parallel Processing**: Process multiple clips in parallel
- **Background Threading**: Use coroutines/async tasks
- **Memory Management**: Stream processing for large videos
- **Battery Optimization**: Throttle processing to save battery

### 5. Caching and Optimization

**Caching Strategy:**

**1. Query Result Cache:**
```
Key: user:{user_id}:query:{query_hash}
Value: {video_ids: [...], metadata: {...}}
TTL: 10 minutes
```

**2. Processed Video Cache:**
```
Key: user:{user_id}:video:{video_hash}
Value: Processed video URL
TTL: 24 hours
```

**3. Metadata Cache:**
```
Key: video:{video_id}:metadata
Value: Video metadata JSON
TTL: 1 hour
```

**Optimization:**
- **Pre-computation**: Pre-generate popular memories
- **Lazy Generation**: Generate on-demand, cache result
- **Progressive Loading**: Return partial results quickly
- **Parallel Processing**: Process multiple segments in parallel

### 6. Phone App: Video Delivery Service

**Delivery Flow (Hybrid Mode):**

**1. WiFi Direct Transfer (Primary):**
```
Video Generated on Phone → Transfer via WiFi Direct → Smart Glass
↓
Display on Smart Glass immediately
↓
No cloud upload needed (local only)
```

**2. Cloud Sync (Optional):**
```
Video Generated on Phone → Upload to Cloud (background) → 
Available on other devices
```

**Phone App Implementation:**
```kotlin
class VideoDeliveryService {
    suspend fun deliverVideo(video: File, toMetaGlass: Boolean) {
        if (toMetaGlass) {
            // Transfer via WiFi Direct
            wifiDirectService.sendFile(video, metaGlassAddress)
        }
        
        // Optionally sync to cloud in background
        lifecycleScope.launch {
            cloudService.uploadVideo(video)
        }
    }
}
```

---

## Data Flow: Complete Example (Hybrid Mode)

### Scenario: "Create a 2-minute video of me and my wife's trip in Paris"

**Step 1: Voice Capture (Smart Glass)**
```
User: "Hey Meta, create a 2-minute video of me and my wife's trip in Paris"
↓
Wake word detected → Voice capture → On-device NLU or Cloud NLP
```

**Step 2: NLP Processing (Smart Glass or Cloud)**
```
Speech-to-Text: "create a 2-minute video of me and my wife's trip in Paris"
↓
Intent Recognition: CREATE_MEMORY_VIDEO
↓
Entity Extraction:
  - Duration: 120 seconds
  - People: ["me", "wife"]
  - Location: "Paris"
  - Time: (infer from recent trip dates)
↓
Map "wife" → person_id (from user profile)
```

**Step 3: WiFi Direct Connection (Smart Glass → Phone)**
```
Smart Glass discovers phone via WiFi Direct
↓
Establish P2P connection
↓
Send video generation request to phone app
↓
Request: {
  intent: "CREATE_MEMORY_VIDEO",
  duration: 120,
  location: "Paris",
  people: [user_id, wife_person_id],
  timeRange: [trip_start, trip_end]
}
```

**Step 4: Video Search (Phone App)**
```
Phone App receives request
↓
Search Local Media Library:
  - Query MediaStore for videos in Paris
  - Filter by date range (trip dates)
  - Filter by detected faces (user + wife)
↓
If not enough local videos:
  - Query cloud metadata database
  - Download missing videos from cloud
↓
Return: 50 candidate videos (local + cloud)
```

**Step 5: Video Selection (Phone App)**
```
Phone App: Score videos:
  - Relevance: Location, people, time match
  - Quality: Resolution, stability, lighting
  - Diversity: Different scenes, times
↓
Select top 15-20 clips
↓
Extract best segments (10-15 seconds each)
↓
Total duration: ~120 seconds
```

**Step 6: Video Processing (Phone App)**
```
Phone App: Trim selected segments
  - Use FFmpeg or MediaCodec (hardware accelerated)
↓
Phone App: Add transitions between clips
↓
Phone App: Enhance video (color, stabilization)
↓
Phone App: Add background music
↓
Phone App: Assemble final video
↓
Phone App: Encode to H.264 (1080p)
↓
Generated video stored on phone
```

**Step 7: Video Delivery (Phone → Smart Glass via WiFi Direct)**
```
Phone App: Transfer final video to Smart Glass
  - Via WiFi Direct (fast local transfer)
  - No internet required
↓
Smart Glass: Receive video
↓
Smart Glass: Display video in UI
↓
Optional: Phone App uploads to cloud in background
```

**Total Time: 2-5 seconds (processing on phone, transfer via WiFi Direct)**

---

## Timing and Data Size Analysis

### Step-by-Step Timing Breakdown

**Scenario: Generate 2-minute video from 50 candidate videos**

| Step | Operation | Location | Time | Notes |
|------|-----------|----------|------|-------|
| **1** | Voice Capture | Smart Glass | 50-200ms | Audio capture duration |
| **2** | Voice Recognition | Smart Glass/Cloud | 100-500ms | On-device: 100ms, Cloud: 500ms |
| **3** | NLP Processing | Smart Glass/Cloud | 200-800ms | Intent + entity extraction |
| **4** | WiFi Direct Connection | Smart Glass ↔ Phone | 500-2000ms | Discovery + connection setup |
| **5** | Request Transfer | Smart Glass → Phone | 10-50ms | Small JSON payload |
| **6** | Video Search (Local) | Phone | 100-500ms | MediaStore query |
| **7** | Video Search (Cloud) | Phone → Cloud | 200-1000ms | If needed, metadata query |
| **8** | Video Selection | Phone | 50-200ms | Algorithm execution |
| **9** | Video Processing | Phone | 1000-3000ms | Trimming, merging, encoding |
| **10** | Video Transfer | Phone → Smart Glass | 200-1000ms | WiFi Direct transfer |
| **11** | Display | Smart Glass | 50-100ms | Video playback start |

**Total Time: 2.3-9.2 seconds**

**Optimized Path (Best Case):**
- On-device NLP: 100ms
- Fast WiFi Direct: 500ms
- Local search only: 100ms
- Optimized processing: 1000ms
- Fast transfer: 200ms
- **Total: ~1.9 seconds**

**Worst Case (Cloud Fallback):**
- Cloud NLP: 800ms
- Slow WiFi Direct: 2000ms
- Cloud search: 1000ms
- Complex processing: 3000ms
- Slow transfer: 1000ms
- **Total: ~7.8 seconds**

### Detailed Timing Analysis

#### 1. Voice Recognition Timing

**On-Device Processing:**
- Wake word detection: 50-100ms
- Voice capture: 100-200ms (depends on command length)
- On-device NLU: 100-300ms
- **Subtotal: 250-600ms**

**Cloud Processing (Fallback):**
- Voice capture: 100-200ms
- Upload audio: 200-500ms (depends on network)
- Cloud NLP: 500-1000ms
- **Subtotal: 800-1700ms**

#### 2. WiFi Direct Connection Timing

**Connection Setup:**
- Device discovery: 200-1000ms
- Pairing/authentication: 100-500ms
- Connection establishment: 200-500ms
- **Subtotal: 500-2000ms**

**Optimization:**
- Maintain persistent connection: 0ms (reuse)
- Auto-reconnect: 100-300ms
- Connection pooling: Reduce setup time

#### 3. Video Search Timing

**Local Search (Phone MediaStore):**
- Query MediaStore: 50-200ms
- Filter by location: 50-100ms
- Filter by date: 50-100ms
- Filter by faces: 100-200ms (if metadata cached)
- **Subtotal: 250-600ms**

**Cloud Metadata Search (If Needed):**
- Network request: 100-300ms
- Database query: 50-200ms
- Response processing: 50-100ms
- **Subtotal: 200-600ms**

**Video Download (If Not on Phone):**
- Download 50MB video: 500-2000ms (depends on connection)
- **Can be parallelized or skipped if using local videos only**

#### 4. Video Selection Timing

**Algorithm Execution:**
- Score calculation: 10-50ms per video
- 50 videos: 500-2500ms (can be parallelized)
- Sort and select: 10-50ms
- **Subtotal: 510-2550ms**

**Optimization:**
- Parallel scoring: Reduce to 100-500ms
- Early termination: Stop when enough clips found
- Cached scores: Reuse previous calculations

#### 5. Video Processing Timing

**Per Video Clip Processing:**

**Trimming (15 clips × 12 seconds each):**
- Single clip trim: 50-200ms (hardware accelerated)
- 15 clips sequential: 750-3000ms
- 15 clips parallel: 200-500ms (optimized)
- **Subtotal: 200-3000ms**

**Transitions:**
- Add transitions: 100-300ms
- **Subtotal: 100-300ms**

**Enhancement:**
- Color correction: 50-200ms
- Stabilization: 100-500ms (if needed)
- Audio normalization: 50-100ms
- **Subtotal: 200-800ms**

**Music Addition:**
- Audio mixing: 100-300ms
- **Subtotal: 100-300ms**

**Final Assembly:**
- Concatenate clips: 200-500ms
- Encode final video: 500-1500ms (hardware accelerated)
- Generate thumbnail: 50-100ms
- **Subtotal: 750-2100ms**

**Total Processing Time: 1350-6500ms**

**Optimized Processing (Parallel + Hardware):**
- Parallel trimming: 200ms
- Transitions: 100ms
- Enhancement: 200ms
- Music: 100ms
- Assembly: 500ms
- **Total: ~1100ms**

#### 6. Video Transfer Timing

**WiFi Direct Transfer:**

**2-minute video (1080p, H.264):**
- Video size: ~30-60MB (depending on bitrate)
- WiFi Direct speed: 100-500 Mbps (typical)
- Transfer time: 480-4800ms (30MB at 500Mbps = 480ms)
- **Subtotal: 500-5000ms**

**Optimization:**
- Compression: Reduce to 20MB → 320ms
- Progressive transfer: Start playback while transferring
- Quality adjustment: Lower quality for faster transfer

### Data Size Analysis

#### Input Data Sizes

**Source Videos:**
- **Smart Glass native format**: 1440 × 1920 @ 30 FPS
- **Average video**: 50-60MB (1440×1920, 30 seconds, H.264)
- **50 candidate videos**: 2.5-3GB total
- **15 selected clips**: 750-900MB (15 × 50-60MB)

**Metadata:**
- **Per video metadata**: ~2-5KB (JSON)
- **50 videos metadata**: 100-250KB
- **Search index**: Negligible (in-memory)

**Request Payload:**
- **Voice command**: 10-50KB (audio file)
- **NLP request**: 1-5KB (JSON)
- **Video search request**: 1-2KB (JSON)
- **Total request**: 12-57KB

#### Processing Data Sizes

**Intermediate Files:**

**Trimmed Clips:**
- **Per clip**: 10-25MB (12 seconds, 1440×1920)
- **15 clips**: 150-375MB
- **Storage**: Temporary (cleaned after processing)

**Enhanced Clips:**
- **Per clip**: 12-25MB (after enhancement)
- **15 clips**: 180-375MB
- **Storage**: Temporary

**Final Video:**
- **2-minute video (1440×1920 @ 30 FPS - Smart Glass native)**: 30-60MB
- **2-minute video (1080p)**: 30-60MB
- **2-minute video (720p)**: 15-30MB
- **Recommended**: 1440×1920 @ 30 FPS (30-60MB) - matches Smart Glass native resolution

#### Transfer Data Sizes

**WiFi Direct Transfer:**

**Request (Smart Glass → Phone):**
- **Size**: 1-5KB (JSON)
- **Time**: 10-50ms

**Video Transfer (Phone → Smart Glass):**
- **Size**: 30-60MB (final video)
- **Time**: 500-5000ms (depends on WiFi Direct speed)
- **Bandwidth**: 100-500 Mbps typical

**Cloud Transfer (If Used):**
- **Upload request**: 1-5KB
- **Download videos**: 50MB per video (if not on phone)
- **Upload final video**: 30-60MB

#### Storage Requirements

**On Phone:**

**Source Videos:**
- **Average user**: 10GB-100GB
- **Power user**: 100GB-500GB
- **Storage**: Phone internal storage or SD card

**Processed Videos:**
- **Per generated video**: 30-60MB
- **10 videos**: 300-600MB
- **100 videos**: 3-6GB
- **Storage**: Phone storage (can be cleaned periodically)

**Metadata (SQLite):**
- **Per video**: 2-5KB
- **1000 videos**: 2-5MB
- **Storage**: Negligible

**On Smart Glass:**

**Cached Videos:**
- **Total storage**: 32 GB Flash storage
- **Available for media**: ~24-27GB (after system/OS)
- **Recent videos**: 1-5GB
- **Metadata cache**: 10-50MB
- **Capacity**: Stores up to 1,000 photos, 100+ 30-second videos

**Cloud Storage (Optional):**

**Backup Storage:**
- **Per user average**: 50GB-200GB
- **Per user power user**: 200GB-1TB
- **Storage**: S3/Azure Blob (scalable)

### Bandwidth Analysis

#### WiFi Direct Bandwidth

**Smart Glass Wi-Fi Specification:**
- **Wi-Fi 6 certified** (802.11ax)
- Supports WiFi Direct over Wi-Fi 6

**Theoretical Speeds:**
- **WiFi 5 (802.11ac)**: Up to 433 Mbps (single stream)
- **WiFi 6 (802.11ax)**: Up to 1.2 Gbps (Smart Glass supports this)
- **WiFi 6E**: Up to 1.2 Gbps (6GHz band)

**Practical Speeds (WiFi Direct with Wi-Fi 6):**
- **Typical**: 100-500 Mbps
- **Optimal conditions**: 500-1000 Mbps (Wi-Fi 6 advantage)
- **Poor conditions**: 50-200 Mbps

**Transfer Time for 2-minute Video:**

| Video Size | WiFi Speed | Transfer Time |
|------------|------------|---------------|
| 30MB | 100 Mbps | 2.4 seconds |
| 30MB | 500 Mbps | 0.48 seconds |
| 60MB | 100 Mbps | 4.8 seconds |
| 60MB | 500 Mbps | 0.96 seconds |

#### Cloud Bandwidth (Fallback)

**Upload (Phone → Cloud):**
- **Cellular 4G**: 10-50 Mbps
- **Cellular 5G**: 100-1000 Mbps
- **WiFi**: 50-500 Mbps

**Download (Cloud → Phone):**
- **Cellular 4G**: 20-100 Mbps
- **Cellular 5G**: 200-2000 Mbps
- **WiFi**: 100-1000 Mbps

### Performance Targets

**Latency Targets:**

| Operation | Target | Current (Optimized) |
|-----------|--------|-------------------|
| **Voice Recognition** | < 500ms | 100-300ms |
| **WiFi Direct Connection** | < 1s | 500ms (reused) |
| **Video Search** | < 500ms | 100-500ms |
| **Video Selection** | < 500ms | 50-200ms |
| **Video Processing** | < 3s | 1-2s |
| **Video Transfer** | < 2s | 0.5-1s |
| **End-to-End** | < 5s | 2-3s |

**Throughput Targets:**

| Operation | Target | Achieved |
|-----------|--------|----------|
| **Video Search** | 1000 videos/sec | 2000+ videos/sec (local) |
| **Video Processing** | 1 video/min | 2-3 videos/min (phone) |
| **WiFi Direct Transfer** | 100 Mbps | 100-500 Mbps |

### Resource Usage Analysis

#### Phone Resource Usage

**CPU Usage:**
- **Video processing**: 50-80% (during processing)
- **Idle**: 5-10%
- **Peak**: 80-100% (intensive processing)

**Memory Usage:**
- **App memory**: 200-500MB
- **Video processing**: +500MB-2GB (temporary)
- **Total peak**: 700MB-2.5GB

**Battery Impact:**
- **Video processing**: 5-15% battery per video
- **WiFi Direct**: 2-5% battery per transfer
- **Total per request**: 7-20% battery

**Storage Usage:**
- **Source videos**: 10-100GB (user dependent)
- **Processed videos**: 300MB-6GB (cache)
- **App data**: 100-500MB

#### Smart Glass Resource Usage

**CPU Usage:**
- **Voice recognition**: 10-20%
- **WiFi Direct**: 5-10%
- **Video playback**: 20-40%

**Memory Usage:**
- **Total RAM**: 2 GB LPDDR4x
- **App memory**: 100-300MB
- **Video cache**: 200-500MB (limited by 2GB RAM)
- **OS and system**: ~500-800MB
- **Available for apps**: ~700MB-1.2GB

**Storage Usage:**
- **Total storage**: 32 GB Flash storage
- **System/OS**: ~5-8GB
- **Available for media**: ~24-27GB
- **Video cache**: 1-5GB (stores up to 1,000 photos, 100+ 30-second videos)
- **Metadata cache**: 10-50MB

**Battery Impact:**
- **Frame battery**: 960 mWh (248 mAh), up to 6 hours mixed-use
- **Voice command**: 1-2% battery (~6-12 minutes)
- **WiFi Direct**: 2-5% battery (~12-30 minutes)
- **Video playback**: 3-5% battery per minute
- **Total per request**: 6-12% battery (~36-72 minutes of usage)
- **With charging case**: Up to 24 additional hours

### Optimization Strategies

#### Timing Optimization

**1. Parallel Processing:**
- Process multiple clips simultaneously
- **Savings**: 3-5x faster processing

**2. Hardware Acceleration:**
- Use MediaCodec/VideoToolbox
- **Savings**: 2-3x faster encoding

**3. Caching:**
- Cache search results
- Cache processed videos
- **Savings**: 50-90% faster for repeated queries

**4. Progressive Processing:**
- Start transfer while processing
- Stream results as available
- **Savings**: Perceived latency reduced

#### Data Size Optimization

**1. Video Compression:**
- Use H.265 (HEVC) instead of H.264
- **Savings**: 30-50% smaller files

**2. Adaptive Quality:**
- Lower quality for faster transfer
- Higher quality for final storage
- **Savings**: 50-70% faster transfer

**3. Selective Download:**
- Only download needed videos
- Skip videos already on phone
- **Savings**: Reduce transfer by 80-90%

**4. Incremental Sync:**
- Only sync new/changed videos
- **Savings**: Reduce sync time by 90%+

### Cost Analysis

#### Phone Processing Costs

**Battery Cost:**
- **Per video generation**: 7-20% battery
- **Daily usage (10 videos)**: 70-200% battery (requires charging)

**Storage Cost:**
- **Phone storage**: User-owned (no cost)
- **SD card**: Optional, $50-200 for 256GB-1TB

**Processing Cost:**
- **CPU/GPU usage**: No direct cost (device owned)
- **Wear on device**: Minimal (modern devices handle it well)

#### Cloud Costs (If Used)

**Storage Costs:**
- **S3 Standard**: $0.023/GB/month
- **100GB/user**: $2.30/month
- **1M users**: $2.3M/month

**Processing Costs:**
- **EC2 instances**: $0.10-0.50/hour
- **Per video**: $0.001-0.01 (if processed in cloud)
- **1M videos/month**: $1K-10K/month

**Transfer Costs:**
- **Data transfer**: $0.09/GB (outbound)
- **Per video (60MB)**: $0.0054
- **1M videos**: $5.4K/month

**Total Cloud Cost (1M users):**
- **Storage**: $2.3M/month
- **Processing**: $1K-10K/month
- **Transfer**: $5.4K/month
- **Total**: ~$2.3M/month

**Hybrid Mode Savings:**
- **Processing on phone**: Save $1K-10K/month
- **Local transfer**: Save $5.4K/month
- **Reduced storage**: Save 50-80% (only backup needed)
- **Total savings**: Significant cost reduction

---

## Benefits of Hybrid Mode (Phone Processing + WiFi Direct)

### Advantages of Phone-Based Processing

**1. Privacy**
- ✅ Videos processed locally on phone
- ✅ No video data sent to cloud (unless user chooses)
- ✅ User has full control over data
- ✅ Meets privacy regulations (GDPR, etc.)

**2. Performance**
- ✅ Faster processing (no network latency)
- ✅ WiFi Direct transfer is very fast (1+ Gbps)
- ✅ Lower latency than cloud processing
- ✅ No dependency on internet connection

**3. Cost**
- ✅ No cloud processing costs
- ✅ No data transfer charges
- ✅ Reduced cloud storage usage
- ✅ Lower infrastructure costs

**4. Reliability**
- ✅ Works offline (no internet needed)
- ✅ No cloud service dependencies
- ✅ More reliable for local processing
- ✅ Better user experience

**5. Scalability**
- ✅ Processing distributed across user devices
- ✅ No cloud processing bottleneck
- ✅ Scales naturally with user base
- ✅ Reduced cloud infrastructure needs

### When Cloud Processing is Used (Fallback)

**Fallback Scenarios:**
- WiFi Direct unavailable (devices too far apart)
- Phone processing fails (insufficient resources)
- Videos not on phone (need to fetch from cloud)
- Complex processing requiring cloud ML models
- User preference for cloud processing

**Hybrid Strategy:**
```
Try Phone Processing First (WiFi Direct)
    ↓ (if fails or unavailable)
Fallback to Cloud Processing
    ↓
Sync result back to phone/Smart Glass
```

---

## Performance Optimization

### Phone Processing Optimization

**1. Hardware Acceleration:**
- Use MediaCodec API (Android) for hardware encoding/decoding
- Use VideoToolbox (iOS) for hardware acceleration
- GPU acceleration for video processing
- NPU acceleration for ML inference (if available)

**2. Parallel Processing:**
- Process multiple video segments in parallel
- Use coroutines/async tasks for concurrent operations
- Background threading to avoid blocking UI

**3. Memory Management:**
- Stream processing for large videos
- Reuse buffers to reduce allocations
- Clear temporary files after processing
- Monitor memory usage

**4. Battery Optimization:**
- Throttle processing when battery is low
- Process during charging when possible
- Optimize CPU/GPU usage
- Background processing with low priority

**5. Caching:**
- Cache processed videos on phone
- Cache search results
- Cache metadata locally
- Avoid reprocessing same videos

### WiFi Direct Optimization

**1. Connection Management:**
- Maintain persistent connection
- Auto-reconnect on disconnect
- Connection pooling
- Efficient discovery

**2. Transfer Optimization:**
- Chunked file transfer
- Compression for transfer
- Resume interrupted transfers
- Parallel transfers for multiple files

**3. Bandwidth Management:**
- Prioritize video transfer
- Throttle during active use
- Background transfer when idle
- Adaptive quality based on connection

### Scalability (Hybrid Mode)

**Distributed Processing:**
- Processing distributed across user phones
- No central processing bottleneck
- Scales naturally with user base
- Reduced cloud infrastructure

**Cloud Fallback:**
- Cloud processing for complex cases
- Auto-scale cloud workers when needed
- Load balancing for cloud services
- CDN for video delivery (when using cloud)

---

## Privacy and Security

### Data Privacy

**On-Device Processing:**
- Process sensitive data locally when possible
- Minimize data sent to cloud
- Encrypt data in transit

**User Consent:**
- Explicit consent for video processing
- User controls for data sharing
- Right to delete data

**Data Encryption:**
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3)
- End-to-end encryption (optional)

### Security

**Authentication:**
- OAuth 2.0 / JWT tokens
- Device authentication
- Biometric authentication

**Authorization:**
- User can only access own videos
- Role-based access control
- API key management

---

## Monitoring and Observability

### Key Metrics

**Performance:**
- Voice recognition latency
- Video search latency
- Video generation time
- End-to-end latency

**Quality:**
- Video generation success rate
- User satisfaction (ratings)
- Video quality metrics
- Search relevance

**System:**
- Request rate
- Error rate
- Resource utilization
- Queue depth

### Logging

**Structured Logging:**
- All requests logged with correlation IDs
- Error tracking and alerting
- Performance profiling
- User behavior analytics

---

## Technology Stack (Hybrid Mode)

| Component | Technology | Location | Rationale |
|-----------|-----------|----------|-----------|
| **Voice Recognition** | On-Device ML, Whisper | Smart Glass/Phone | Low latency, privacy |
| **NLP** | On-Device NLU, Cloud BERT/GPT | Smart Glass/Cloud | Hybrid processing |
| **WiFi Direct** | Android WiFi P2P API | Phone ↔ Smart Glass | Fast local transfer |
| **Video Search** | MediaStore API, SQLite | Phone (Local) | Fast local search |
| **Metadata DB** | SQLite (Phone), Cassandra (Cloud) | Phone/Cloud | Local + cloud hybrid |
| **Video Processing** | FFmpeg Mobile, MediaCodec | Phone | Hardware acceleration |
| **Storage** | Phone Storage, S3 (Optional) | Phone/Cloud | Local primary, cloud backup |
| **Cache** | In-Memory Cache (Phone) | Phone | Fast local caching |

---

## Future Enhancements

1. **Real-Time Preview**
   - Show preview while generating on phone
   - Allow user to adjust selection
   - Interactive editing

2. **Advanced AI Features**
   - On-device ML for scene detection
   - Automatic music selection (on phone)
   - Story generation
   - Emotion detection

3. **AR Integration**
   - Preview video in AR overlay
   - Share in AR space
   - Collaborative editing

4. **Personalization**
   - Learn user preferences (on device)
   - Custom video styles
   - Personalized music selection

5. **Offline Mode**
   - Full functionality without internet
   - Sync when online
   - Background sync

---

## What Interviewers Look For

### Hybrid Architecture Skills

1. **Phone-Cloud Hybrid Design**
   - Phone-based processing (primary)
   - Cloud fallback
   - WiFi Direct for local transfer
   - **Red Flags**: Cloud-only, no fallback, poor local processing

2. **Local-First Processing**
   - Privacy-preserving
   - Performance optimization
   - Offline support
   - **Red Flags**: No local processing, always cloud, privacy issues

3. **Device Coordination**
   - Smart Glass ↔ Phone communication
   - WiFi Direct setup
   - Sync strategies
   - **Red Flags**: Poor coordination, no sync, connection issues

### Video Processing Skills

1. **Video Search & Selection**
   - Semantic search
   - Clip selection algorithm
   - Relevance ranking
   - **Red Flags**: No search, poor selection, irrelevant clips

2. **Video Processing Pipeline**
   - FFmpeg processing
   - Hardware acceleration
   - Phone resource management
   - **Red Flags**: Slow processing, no acceleration, resource issues

3. **Memory Video Generation**
   - Clip trimming
   - Merging with transitions
   - 2-minute target duration
   - **Red Flags**: Poor quality, wrong duration, no transitions

### Problem-Solving Approach

1. **Privacy & Performance Balance**
   - Local processing for privacy
   - Performance optimization
   - **Red Flags**: No privacy consideration, poor performance

2. **Edge Cases**
   - Phone unavailable
   - WiFi Direct failures
   - Processing failures
   - **Red Flags**: Ignoring edge cases, no handling

3. **Trade-off Analysis**
   - Phone resources vs performance
   - Local vs cloud
   - **Red Flags**: No trade-offs, dogmatic choices

### System Design Skills

1. **Component Design**
   - Voice recognition service
   - Video search service
   - Processing service
   - **Red Flags**: Monolithic, unclear boundaries

2. **Connectivity Design**
   - WiFi Direct setup
   - Fallback mechanisms
   - **Red Flags**: Poor connectivity, no fallback, unreliable

3. **Resource Management**
   - Phone CPU/GPU usage
   - Battery optimization
   - Storage management
   - **Red Flags**: High resource usage, poor battery, storage issues

### Communication Skills

1. **Hybrid Architecture Explanation**
   - Can explain phone-cloud hybrid
   - Understands trade-offs
   - **Red Flags**: No understanding, vague explanations

2. **Processing Pipeline Explanation**
   - Can explain video processing
   - Understands optimization
   - **Red Flags**: No understanding, vague

### Meta-Specific Focus

1. **Hybrid Systems Expertise**
   - Local-cloud architecture
   - Privacy-first design
   - **Key**: Show hybrid systems expertise

2. **Edge Computing Knowledge**
   - Phone processing
   - Resource optimization
   - **Key**: Demonstrate edge computing knowledge

## Conclusion

This hybrid mode system design enables Smart Glass users to generate personalized memory videos through natural language voice commands, with processing primarily happening on the user's phone via WiFi Direct connection.

**Key Architecture Decisions:**

1. **Hybrid Processing**: Phone-based processing (primary) + Cloud fallback
2. **WiFi Direct**: Fast local transfer between phone and Smart Glass
3. **Local-First**: Process videos on phone for privacy and performance
4. **Cloud Optional**: Use cloud only when needed (fallback, sync)

**Key Components:**
1. **Voice Recognition**: On-device + cloud NLP
2. **WiFi Direct**: P2P connection between devices
3. **Phone App**: Video search, selection, and processing
4. **Local Processing**: FFmpeg + hardware acceleration on phone
5. **Delivery**: WiFi Direct transfer to Smart Glass

**Benefits:**
- **Privacy**: Videos processed locally, no cloud upload required
- **Performance**: Faster processing (no network latency)
- **Cost**: Reduced cloud infrastructure costs
- **Reliability**: Works offline, no internet dependency
- **Scalability**: Distributed processing across user devices

**Trade-offs:**
- **Phone Resources**: Uses phone CPU/GPU/battery
- **Device Dependency**: Requires phone nearby
- **Storage**: Uses phone storage
- **Complexity**: More complex than pure cloud solution

The hybrid approach provides the best balance of privacy, performance, and user experience while maintaining the flexibility to fall back to cloud processing when needed.

