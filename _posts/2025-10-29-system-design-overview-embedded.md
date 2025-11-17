---
layout: post
title: "System Design Overview: Embedded Architectures"
date: 2025-10-29 21:50:00 -0700
categories: system-design embedded architecture
permalink: /2025/10/29/system-design-overview-embedded/
tags: [embedded, mcu, rtos, drivers, boot, power, security, connectivity]
---

# System Design Overview: Embedded Architectures

A concise map for MCU/embedded SoC designs: boot flow, drivers, concurrency, connectivity, data, power, security, and manufacturing.

## Reference stack

```
Boot ROM → Bootloader (secure) → Firmware (RTOS/Bare‑metal)
  ├─ HAL/Drivers (GPIO/I2C/SPI/UART/ADC/DMA)
  ├─ Services (Sensors, Storage, FS, Crypto)
  ├─ Connectivity (BLE/Wi‑Fi/Cell, MQTT/HTTP/CoAP)
  └─ Apps (Control, Telemetry, UI)

Peripherals: timers, watchdog, PMIC; Storage: NOR/NAND/EEPROM; Debug: SWD/JTAG/ETM
```

## Concurrency

- RTOS tasks + ISRs with mailboxes/queues; avoid long ISRs; DMA for bulk moves.
- Locking: priority inversion mitigation (priority inheritance); ring buffers between ISR↔task.

## Data & comms

- Protocols: TLV/CBOR/flat binary with CRC; versioned headers; backpressure policies.
- Storage: wear‑leveled flash (LittleFS/FlashDB); config KV with atomic updates.

## Power & thermal

- Modes: active/idle/sleep/stop/ship; budget current by mode; wake sources; thermal derating.

## Security

- Secure boot chain (hash+signature); device identity; key storage; debug port lockdown.
- Comms security: TLS/DTLS where feasible; app‑layer tokens; monotonic counters.

## OTA & diagnostics

- A/B slots with rollback; delta updates; watchdog‑guarded apply; health metrics and logs.

## Manufacturing & test

- Provisioning (keys/serials/calibration); boundary scan; factory test modes; golden sample.

## Interview checklist

- Boot→app flow, task breakdown, ISR boundaries, memory map, power modes, updates, and failure handling.

## Power & test templates

```text
Power budget: Active ____ mA (duty ____%), Idle ____ mA, Sleep ____ µA → avg ____ mA → battery life ____ h on ____ mAh.
Thermal: throttle thresholds ____ °C; degradation plan (fps/res/ML).
Test: HIL record/replay; RF link loss scenarios; OTA abort/resume.
```
