---
layout: post
title: "Android OS Design Overview: IoT Device Controller"
date: 2025-10-29 22:00:00 -0700
categories: android system-design embedded
permalink: /2025/10/29/android-os-design-overview-iot-controller/
tags: [android, architecture, services, hal, aidl, bluetooth, permissions, power]
---

# Android OS Design Overview: IoT Device Controller

A practical overview of how to structure an Android‑based controller app/stack for IoT devices (BLE/Wi‑Fi/USB), from framework layers to services, permissions, background execution, power, and updates.

## Layered architecture

```
Apps (UI/Compose) ────────► App Services (Foreground + Worker) ──► Platform APIs
                                   │                                   │
                                   ▼                                   ▼
                           AIDL/Binder interface                HAL/Drivers (USB/BLE/Serial)
                                   │                                   │
                                   ▼                                   ▼
                            Native (NDK/JNI)                   Kernel/SoC (power, security)
```

Key principles
- Keep long‑running I/O in services (foreground or bound); UI remains thin.
- Use AIDL/Binder for clear process boundaries (controller service <-> UI app).
- For high‑throughput parsing, move hot paths to NDK/JNI, keep policy in Kotlin.

## Core components

- DeviceRepository: abstracts transports (BLE/Wi‑Fi/USB) and exposes high‑level ops.
- ControllerService (foreground): manages connections, sessions, retries, notifications.
- Worker jobs (WorkManager): scheduled sync/log uploads, firmware download.
- Local DB (Room): sessions, telemetry, device registry.
- Settings/Feature flags: SharedPreferences/Proto + remote flags.

## Example AIDL and service

`aidl/com/example/iot/IController.aidl`
```java
package com.example.iot;
interface IController {
  void connect(String deviceId);
  void disconnect(String deviceId);
  void sendCommand(String deviceId, in byte[] payload);
}
```

Service skeleton (Kotlin)
```kotlin
class ControllerService: Service() {
  private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
  private val binder = object : IController.Stub() {
    override fun connect(deviceId: String) { scope.launch { repo.connect(deviceId) } }
    override fun disconnect(deviceId: String) { scope.launch { repo.disconnect(deviceId) } }
    override fun sendCommand(deviceId: String, payload: ByteArray) { scope.launch { repo.send(deviceId, payload) } }
  }
  private lateinit var repo: DeviceRepository
  override fun onBind(intent: Intent?) = binder
  override fun onCreate() { super.onCreate(); repo = DeviceRepository(this); startForeground(/*notif*/1, buildNotif()) }
}
```

## Transport abstraction

```kotlin
interface Transport { suspend fun open(id: String); suspend fun close(id: String); suspend fun write(id: String, data: ByteArray); fun incoming(id: String): Flow<ByteArray> }
class BleTransport(...): Transport { /* GATT connect, notifications, MTU, retry */ }
class WifiTransport(...): Transport { /* sockets, TLS, backoff */ }
class UsbTransport(...): Transport { /* bulk transfers */ }
```

Parsing hot path (NDK/JNI) example
```cpp
extern "C" JNIEXPORT jbyteArray JNICALL
Java_com_example_iot_Native_parseFrame(JNIEnv* env, jclass, jbyteArray input) {
  // validate header, crc, return normalized payload
  return input; // demo
}
```

## Permissions and background execution

- Bluetooth: `BLUETOOTH_CONNECT`, `BLUETOOTH_SCAN` (runtime on Android 12+); location if required for scan visibility.
- Wi‑Fi: `CHANGE_WIFI_STATE`, `ACCESS_WIFI_STATE`, network requests via `ConnectivityManager`.
- USB Host: `android.hardware.usb.host` + permission intent.
- Foreground service type: `dataSync` or `connectedDevice`; post persistent notification during active sessions.
- Use WorkManager with constraints (unmetered, charging) for heavy uploads.

## Power and reliability

- Acquire `WakeLock` sparingly (partial) during critical transfers; release promptly.
- Exponential backoff with jitter; circuit breakers for flaky links; persist session state on crashes.
- Cache MTU/throughput tuning per device; prioritize deltas over full state.

## Security

- Per‑device trust (BLE: LE Secure Connections; Wi‑Fi: TLS with mutual auth where possible).
- Protect secrets in Android Keystore; scope tokens to device/fabric.
- Validate firmware signatures; staged rollouts and rollback.

## OTA updates (controller side)

- Download in background (WorkManager), verify signature/hash, then stream to device with resumable protocol and progress UI.

## Observability

- Structured logs (deviceId, sessionId), breadcrumbs for connection state; export anonymized metrics.
- Crash/ANR monitoring; in‑app diagnostics bundle export.

## Testing

- Instrumentation tests for permission flows; fake transports for deterministic IO.
- Record/replay frames; error‑injection for link loss and timeouts.

## Interview checklist

- Layers (UI, Service, Repo, Transport), background limits, permission model, power, recovery, OTA, and security posture.
