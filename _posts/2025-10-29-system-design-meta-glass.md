---
layout: post
title: "System Design: Meta Glass (Smart Glasses Platform)"
date: 2025-10-29 00:00:00 -0700
categories: system-design wearables iot edge-ml
permalink: /2025/10/29/system-design-meta-glass/
tags: [system-design, wearables, AR, camera, BLE, Wi‑Fi, edge-ML, streaming]
---

# System Design: Meta Glass (Smart Glasses Platform)

A high-level design for camera-enabled smart glasses that capture, process, and stream media while providing low-latency user interactions and companion‑app integrations.

## 1) Goals & Requirements

- Capture photos/video hands‑free; live preview and streaming
- Dual control: voice (hotword + commands) and phone app (BLE/Wi‑Fi)
- On‑device ML: scene understanding, speech keywords, object labels
- In‑glass display: notifications, capture status, minimal overlays (privacy‑aware)
- Companion phone app for control, media sync, and cloud relay
- Low power (all‑day light use; 1–2 hours continuous video)
- Privacy: explicit indicators, on‑device redaction, opt‑in cloud

Non‑functional:
- Latency: <150 ms live preview to phone and <50 ms display update
- Startup: <2 s to capture, <5 s to stream, <500 ms voice UI ready
- Robust over intermittent connectivity (BLE↔Wi‑Fi/Cell)

## 2) Hardware Building Blocks

- SoC: ARM CPU + low‑power ISP + NPU (e.g., 0.5–2 TOPS)
- Sensors: 1–2 cameras, IMU, mic array, touch/button
- Radios: BLE 5.x (control), dual‑band Wi‑Fi (media), optional LTE tether via phone
- Display: micro‑OLED/LCoS projector + waveguide/combiner; display driver
- Storage: eMMC/UFS + SPI NOR for firmware
- Power: single cell Li‑ion, PMIC, fuel gauge; haptics/LED privacy indicators

## 3) Software Stack (on‑device)

### 3.1 Android-based stack

- Boot: secure boot (ROM → bootloader → signed Android boot image)
- Kernel & Drivers: camera/ISP (V4L2), audio (ALSA/AAudio), sensors (IIO), power/thermal, display (DRM/KMS or vendor)
- Hardware Abstraction (HAL): Camera HAL3, Audio HAL, Sensors HAL, Display/Composer HAL
- Native (NDK, C++):
  - Image pipeline: AImageReader/NDK Camera, `AHardwareBuffer` zero‑copy, `ASharedMemory`/`AHB` for buffer exchange
  - Media: `AMediaCodec` (H.264/H.265), `AMediaMuxer`, `AAudio` for low‑latency audio
  - ML: NNAPI / vendor NPU runtime via NDK
  - Voice UI: hotword detector (keyword spotting), on‑device ASR (NNAPI) with small vocabulary; optional cloud ASR fallback
  - Display compositor: render minimal UI overlays to display surface (SurfaceFlinger/Composer)
  - IPC: AIDL/Binder (stable AIDL) between services and UI
  - JNI bridges exposing native APIs to Kotlin/Java UI
- App/UI (Android):
  - Foreground service for capture/stream; Jetpack (Lifecycle, WorkManager)
  - CameraX/Camera2 interop for preview surface; SurfaceTexture/SurfaceView
  - WebRTC (libwebrtc) or RTSP client/server; Notifications; Settings/Permissions (CAMERA, RECORD_AUDIO, BLUETOOTH)
  - Display controller: routes selected notifications/status to glass display with privacy filters

### 3.2 Services (functional)

- Capture service (NDK + Camera HAL3 → AImageReader → AMediaCodec)
- ML service (NNAPI/NPU: redaction/labels → metadata overlay)
- Streaming service (NDK WebRTC/RTSP) with hardware encoder and network QoS
- Control/Device service (BLE GATT via Android Bluetooth stack; Wi‑Fi control via Connectivity Manager)
- Voice service (hotword + command grammar → AIDL events to Control/Capture services)
- Display service (Composer/SurfaceFlinger target) for status/notifications/voice hints
- Storage sync (Scoped Storage, SAF; foreground upload when on charge + Wi‑Fi)

## 4) Phone Companion App

- BLE session for pairing, control, settings, firmware OTA
- Wi‑Fi direct/local network for high‑bandwidth preview/transfer
- Background uploader to cloud library; share links; push notifications

## 5) Cloud Services

- Media ingest API (signed URLs), storage (S3‑like), CDN
- WebRTC TURN/STUN for remote preview; notification service
- Analytics pipeline (quality, crashes, battery/thermal trends)

## 6) Data Flows

- Firmware (drivers) → Camera HAL3 → NDK (AImageReader) →
  - UI preview: Surface(SurfaceView/TextureView) with zero‑copy `AHardwareBuffer`
  - Encoder: `AMediaCodec` → RTP/RTSP/WebRTC → Phone/Cloud
  - File: `AMediaMuxer` → Scoped Storage → Sync Agent → Phone/Cloud
- Control:
  - Phone: UI/Phone → BLE GATT/AIDL/Binder → Native services (start/stop, modes, LEDs, display intents)
  - Voice: Mic → Voice service (hotword → command) → AIDL events → Capture/Display/Control services
- Display:
  - Status/notifications: Display service → Composer/Display HAL → micro‑display (minimal text/icons, capture timer, battery, privacy)
- ML: NDK acquires frames (`ImageReader_acquireNextImage`) → NNAPI/NPU → overlay via GPU/Composition → UI/Stream metadata

## 7) Power & Thermal Strategy

- DVFS; big.LITTLE affinity (encode on ISP/NPU where possible)
- Duty‑cycled sensors; adaptive fps/bitrate; display off or dim by default; AOD‑like minimal mode
- Thermal watcher: degrade resolution/fps; pause ML/voice under heat; reduce display brightness

## 8) Connectivity & Resilience

- BLE only for setup/control; switch to Wi‑Fi for media
- Store‑and‑forward when offline; conflict‑free filenames + manifests
- Exponential backoff; resumable uploads (chunked with checksums)

## 9) Privacy & Security

- Hardware privacy indicators (LED), audible shutter; on‑screen privacy glyph
- On‑device face/license‑plate blur; geo‑privacy zones
- TEE/KeyMint for keys; end‑to‑end TLS; signed OTA; rollback
- Runtime permissions; background capture policies; data retention

## 10) APIs (sketch)

- AIDL Services:
  - Capture: `startCapture(mode, fps, res, surface)`, `stopCapture()`
  - Display: `showStatus(text/icon, durationMs)`, `setBrightness(level)`, `enablePrivacyGlyph(enabled)`
  - Voice: event stream `onHotword()`, `onCommand(commandId, args)`
- Control (BLE GATT / gRPC):
  - POST /capture/start {mode, fps, res}
  - GET /status {battery, thermals, storage}

## 11) Observability & Metrics

- Device: fps, encode latency, NPU util, battery drain mA, temp °C, display on‑time/brightness histogram
- Voice: hotword false‑positive/false‑negative rates, command latency p50/p95
- Network: RTT, packet loss, bitrate, reconnects, upload success rate
- App: ANRs/crashes, foreground service uptime, preview/display latency p50/p95/p99

## 12) Risks & Mitigations

- Thermal throttling → adaptive quality, ML/voice scheduling, display dim/off
- Permission friction → clear UX, education, transparent indicators
- Privacy backlash → local‑first defaults, granular controls, explicit display glyphs
- Battery life → accelerator offload, aggressive idle, codec tuning, display duty cycling

## 13) MVP → V2 Roadmap

- MVP: Camera HAL3 + NDK encoder + UI preview; BLE control; voice hotword + basic commands; minimal display (status/recording indicator); local save + phone sync
- V2: WebRTC remote stream; richer voice grammar; notifications mirroring; third‑party SDK; advanced redaction; multi‑cam stitching

## 14) Capacity, SLOs, and Failure Drills

Capacity & sizing
- Video 1080p30 H.264 baseline ~2–4 Mbps; preview to phone target 1–2 Mbps with adaptive bitrate.
- Storage: 1 hour @ 2 Mbps ≈ ~0.9 GB; local buffer target 10–20 GB; daily sync on charge+Wi‑Fi.
- BLE control messages < 10 KB/s; Wi‑Fi throughput target > 20 Mbps for burst transfers.

SLOs
- TTFF (preview) < 2 s p95; shutter latency < 150 ms p95; voice command to action < 300 ms p95.
- Upload success rate > 99% within 24 h; background crash rate < 0.1% DAU.

Failure drills
- Camera HAL error → restart pipeline (AImageReader/MediaCodec) with exponential backoff.
- Thermal limit → degrade fps/resolution/ML first; pause streaming; surface UX banner.
- Connectivity drop → buffer locally; resume with checksums; prevent duplicates via manifests.

Consistency & privacy
- Local‑first capture; explicit user action to share; redact PII on‑device before cloud; immutable audit of uploads.

## 15) Detailed APIs (sketch)

```http
POST /v1/capture/start { mode, fps, res } -> { session_id }
POST /v1/capture/stop { session_id } -> 204
GET  /v1/device/status -> { battery, thermals, storage }
POST /v1/ota/apply { version, url, sig } -> { job_id }
```

## 16) Test plan

- Media pipeline: soak tests 2h @1080p30; encoder latency p50/p95; dropped frame rate.
- Voice: hotword FAR/FRR benchmarks; command p50/p95 latencies; noise environments.
- Thermal: chamber profiles; degrade thresholds validated.
- Connectivity: BLE/Wi‑Fi swap under load; offline store‑and‑forward; resume with dedupe.

---

This Android‑based architecture maps firmware drivers through HALs into NDK services for low‑latency media and display handling, with clean AIDL/JNI bridges into a Kotlin/Jetpack UI. It supports dual control (voice + phone) and an in‑glass display while balancing power, privacy, and developer ergonomics.

## What Interviewers Look For

### Embedded/Wearable Systems Skills

1. **Hardware Integration**
   - Camera/ISP pipeline
   - Display drivers
   - Sensor integration
   - **Red Flags**: No hardware understanding, poor integration, inefficient

2. **Power Management**
   - Battery optimization
   - Thermal management
   - Duty cycling
   - **Red Flags**: Poor battery life, thermal issues, no optimization

3. **Low-Latency Design**
   - Preview latency < 150ms
   - Display update < 50ms
   - Voice command < 300ms
   - **Red Flags**: High latency, slow operations, poor UX

### Android/OS Systems Skills

1. **NDK/Native Development**
   - Camera HAL3
   - MediaCodec
   - NNAPI/ML
   - **Red Flags**: No native knowledge, inefficient, poor performance

2. **System Services**
   - AIDL services
   - Binder IPC
   - HAL abstraction
   - **Red Flags**: No system knowledge, poor architecture, inefficient

3. **Android Architecture**
   - Jetpack components
   - Lifecycle management
   - Background services
   - **Red Flags**: Poor architecture, lifecycle issues, inefficient

### Problem-Solving Approach

1. **Privacy & Security**
   - On-device processing
   - Privacy indicators
   - Secure boot
   - **Red Flags**: No privacy, insecure, poor UX

2. **Edge Cases**
   - Thermal throttling
   - Connectivity drops
   - Permission issues
   - **Red Flags**: Ignoring edge cases, no handling

3. **Trade-off Analysis**
   - Power vs performance
   - Privacy vs features
   - **Red Flags**: No trade-offs, dogmatic choices

### System Design Skills

1. **Component Design**
   - Capture service
   - ML service
   - Display service
   - **Red Flags**: Monolithic, unclear boundaries

2. **Connectivity Design**
   - BLE for control
   - WiFi for media
   - Offline support
   - **Red Flags**: Poor connectivity, no offline, inefficient

3. **Cloud Integration**
   - Media upload
   - Sync strategy
   - Conflict resolution
   - **Red Flags**: No cloud, poor sync, conflicts

### Communication Skills

1. **Embedded Systems Explanation**
   - Can explain hardware integration
   - Understands power management
   - **Red Flags**: No understanding, vague explanations

2. **Android Architecture Explanation**
   - Can explain NDK/HAL
   - Understands system services
   - **Red Flags**: No understanding, vague

### Meta-Specific Focus

1. **Embedded Systems Expertise**
   - Hardware knowledge
   - Power optimization
   - **Key**: Show embedded systems expertise

2. **Privacy-First Design**
   - On-device processing
   - User control
   - **Key**: Demonstrate privacy focus
