---
layout: post
title: "Meta Glass: Voice-Controlled Video Generation System Design"
date: 2025-11-09
categories: [System Design, Meta Glass, AR, Voice Control, Video Processing, AI/ML, Architecture]
excerpt: "A comprehensive system design for Meta Glass featuring voice-controlled automatic video generation, covering current Meta Glass architecture and the new feature to generate 2-minute memory videos from natural language commands."
---

## Introduction

Meta Glass represents the next generation of augmented reality smart glasses, combining advanced computer vision, AI, and voice control to create immersive experiences. This post explores the current Meta Glass architecture and designs a new feature that enables users to generate personalized memory videos through natural language voice commands.

**Example Use Case:** User says "Create a 2-minute video of me and my wife's trip in Paris" and the system automatically finds, selects, and compiles relevant video clips into a polished memory video.

---

## Current Meta Glass Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────┐
│           Meta Glass Hardware                   │
│  (Cameras, Sensors, Display, Audio, Compute)   │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│         Meta Glass OS (AOSP-based)             │
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
- **Dual Cameras**: Front-facing cameras for AR overlay and world capture
- **Depth Sensors**: Time-of-flight (ToF) sensors for depth perception
- **Eye Tracking**: Cameras for gaze tracking and interaction
- **Resolution**: 12MP+ cameras, 4K video recording capability

**2. Display System**
- **Waveguide Display**: Transparent AR display overlay
- **Resolution**: High-resolution micro-displays
- **Field of View**: Wide FOV for immersive AR experience
- **Brightness**: High brightness for outdoor use

**3. Audio System**
- **Spatial Audio**: 3D audio processing
- **Microphones**: Multiple microphones for voice capture and noise cancellation
- **Speakers**: Bone conduction or open-ear audio

**4. Compute Platform**
- **SoC**: Custom or high-end mobile SoC (Snapdragon XR, Apple Silicon)
- **AI Accelerator**: Dedicated NPU for on-device ML inference
- **Memory**: 8GB+ RAM, fast storage
- **Battery**: Long-lasting battery with efficient power management

**5. Sensors**
- **IMU**: Accelerometer, gyroscope, magnetometer
- **GPS**: Location tracking
- **Ambient Light**: Adaptive display brightness
- **Proximity**: Hand/object detection

### Software Architecture

**1. Meta Glass OS Layer**

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
- 4K video recording
- Real-time stabilization
- HDR processing
- Low-light enhancement

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

**On-Device Components:**
- **Wake Word Detection**: "Hey Meta" detection
- **Voice Activity Detection**: Detect when user is speaking
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
User Voice Command (Meta Glass)
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
Transfer Final Video to Meta Glass via WiFi Direct
    ↓
Display on Meta Glass
```

### Component Architecture (Hybrid Mode)

```
┌─────────────────────────────────────────┐
│      Meta Glass Device (Local)          │
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
1. **Meta Glass** captures voice command
2. **Meta Glass** processes intent locally or sends to cloud for NLP
3. **Meta Glass** establishes WiFi Direct connection to phone
4. **Phone App** receives request and searches local media library
5. **Phone App** fetches videos/images from phone storage (or cloud if needed)
6. **Phone App** processes videos locally (trimming, merging, effects)
7. **Phone App** generates final 2-minute video on phone
8. **Phone App** transfers final video to Meta Glass via WiFi Direct
9. **Meta Glass** displays video

**Fallback Path: Cloud Processing**

- If WiFi Direct unavailable → Use cloud processing
- If phone processing fails → Fallback to cloud
- If videos not on phone → Fetch from cloud storage

### Storage Architecture: Local vs Remote

**Storage Layers:**

**1. Local Storage (On Meta Glass Device)**
- **Purpose**: Temporary cache, recent media, offline access
- **Capacity**: Limited (64GB-256GB typical)
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
Meta Glass Device
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

**Option 1: Direct WiFi Transfer (Phone ↔ Meta Glass)**

**Architecture:**
```
Phone (WiFi Direct/Hotspot) ←→ Meta Glass (WiFi Client)
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
2. Meta Glass discovers and connects
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
1. Phone and Meta Glass connect to same WiFi router
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
- **Setup**: Phone creates hotspot, Meta Glass connects
- **Speed**: Depends on phone's WiFi capability
- **Use Case**: On-the-go sync, no router available

**Flow:**
```
1. Phone enables WiFi hotspot
2. Meta Glass connects to phone's hotspot
3. Phone and Meta Glass on same network
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
        # Discover Meta Glass devices on local network
        zeroconf.Zeroconf().browse_services(
            "_metaglass._tcp.local.",
            "_services._dns-sd._udp.local."
        )
```

**Transfer Protocol:**
```python
# HTTP server on phone, client on Meta Glass
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
- **Auto-Discovery**: Automatically find Meta Glass when on same network
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
User opens Meta Glass app on phone
    ↓
App detects Meta Glass on local WiFi
    ↓
"Sync media via local WiFi?" → User confirms
    ↓
Fast local transfer (no internet, no data charges)
    ↓
Media available on Meta Glass immediately
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

**Meta Glass Side (Client):**
```python
# Client on Meta Glass
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

**On-Device (Meta Glass):**

**Wake Word Detection:**
- Always-on wake word detection ("Hey Meta")
- Low-power DSP processing
- < 100ms latency

**Voice Capture:**
- Multi-microphone array
- Noise cancellation
- Beamforming for direction
- Voice activity detection

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

**On Meta Glass (Client):**

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
- Accept connections from Meta Glass
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
Video Generated on Phone → Transfer via WiFi Direct → Meta Glass
↓
Display on Meta Glass immediately
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

**Step 1: Voice Capture (Meta Glass)**
```
User: "Hey Meta, create a 2-minute video of me and my wife's trip in Paris"
↓
Wake word detected → Voice capture → On-device NLU or Cloud NLP
```

**Step 2: NLP Processing (Meta Glass or Cloud)**
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

**Step 3: WiFi Direct Connection (Meta Glass → Phone)**
```
Meta Glass discovers phone via WiFi Direct
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

**Step 7: Video Delivery (Phone → Meta Glass via WiFi Direct)**
```
Phone App: Transfer final video to Meta Glass
  - Via WiFi Direct (fast local transfer)
  - No internet required
↓
Meta Glass: Receive video
↓
Meta Glass: Display video in UI
↓
Optional: Phone App uploads to cloud in background
```

**Total Time: 2-5 seconds (processing on phone, transfer via WiFi Direct)**

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
Sync result back to phone/Meta Glass
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
| **Voice Recognition** | On-Device ML, Whisper | Meta Glass/Phone | Low latency, privacy |
| **NLP** | On-Device NLU, Cloud BERT/GPT | Meta Glass/Cloud | Hybrid processing |
| **WiFi Direct** | Android WiFi P2P API | Phone ↔ Meta Glass | Fast local transfer |
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

## Conclusion

This hybrid mode system design enables Meta Glass users to generate personalized memory videos through natural language voice commands, with processing primarily happening on the user's phone via WiFi Direct connection.

**Key Architecture Decisions:**

1. **Hybrid Processing**: Phone-based processing (primary) + Cloud fallback
2. **WiFi Direct**: Fast local transfer between phone and Meta Glass
3. **Local-First**: Process videos on phone for privacy and performance
4. **Cloud Optional**: Use cloud only when needed (fallback, sync)

**Key Components:**
1. **Voice Recognition**: On-device + cloud NLP
2. **WiFi Direct**: P2P connection between devices
3. **Phone App**: Video search, selection, and processing
4. **Local Processing**: FFmpeg + hardware acceleration on phone
5. **Delivery**: WiFi Direct transfer to Meta Glass

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

