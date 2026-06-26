---
layout: post
title: "Hardware Design for Testing & DFT (ATE, DUT, and Silicon)"
date: 2026-05-26
categories: [System Design, Hardware, ATE, DFT, Test Engineering, Interview Preparation]
excerpt: "ATE/DUT system design plus Design-for-Testability (DFT): scan, BIST, JTAG, compression, at-speed test, and deep dives on scan chains, MBIST, IJTAG, ATPG, AI accelerators, automotive ISO 26262, and interview questions."
---

## Introduction

**Hardware design for testing** spans two complementary worlds:

1. **ATE / DUT system design** — building the rack, fixture, and sequencer that tests boards and devices in the lab or on the production line.
2. **Design-for-Testability (DFT)** — architectural and structural practices in **silicon, IP, board, and system** that make chips easier to test, debug, validate, and manufacture at scale.

This post covers both: the instrument stack from test controller to loadboard, then industry-standard **DFT techniques** (scan, BIST, JTAG, compression, at-speed test) and deep dives for interviews and advanced SoC programs.

<div class="post-reading-tip" markdown="1">

**How to read this post:** Skim the **layer diagrams** first (ATE stack, then SoC DFT). Part A is for fixture/instrument interviews; Part B–C are for silicon validation and DFT roles.

</div>

## Table of Contents

**Part A — ATE / DUT system design**

1. [Problem Statement](#problem-statement)
2. [Architecture Overview](#architecture-overview)
3. [System Layers](#system-layers)
4. [Three Design Problems That Dominate Real Projects](#three-design-problems-that-dominate-real-projects)

**Part B — Design-for-Testability (DFT)**

5. [DFT Overview](#design-for-testability-dft-overview)
6. [Common DFT Techniques (Industry Categories)](#common-dft-techniques-industry-categories)
7. [Modern SoC DFT Architecture](#modern-soc-dft-architecture)
8. [DFT Tradeoffs, Tools, and Flow](#dft-tradeoffs-tools-and-flow)

**Part C — Deep dives**

9. [ASIC vs FPGA DFT Differences](#asic-vs-fpga-dft-differences)
10. [Scan Chain Architecture in Detail](#scan-chain-architecture-in-detail)
11. [MBIST Algorithms](#mbist-algorithms)
12. [IJTAG Architecture (IEEE 1687)](#ijtag-architecture-ieee-1687)
13. [ATPG Algorithms and Fault Coverage Math](#atpg-algorithms-and-fault-coverage-math)
14. [Physical-Design Impacts of DFT](#physical-design-impacts-of-dft)
15. [DFT for AI Accelerators](#dft-for-ai-accelerators)
16. [Automotive DFT and ISO 26262](#automotive-dft-and-iso-26262)
17. [DFT Interview Questions](#dft-interview-questions)

18. [Summary](#summary)

## Problem Statement

**Design (or architect) a hardware test system that:**

1. Sequences tests under software control (pass/fail, limits, logging)
2. Stimulates and measures the DUT across DC, analog, digital, and optionally RF
3. Routes many instrument channels to many DUT pins (or many DUT sites) reliably
4. Powers the DUT in the correct order with protection
5. Supports environmental stress when required (temperature, burn-in)
6. Feeds results into analysis (yield, SPC, limit tuning)

**Typical contexts:** IC characterization, module/PCBA functional test, smartphone/RF front-end validation, power-management IC bring-up, reliability (HALT/HASS).

## Architecture Overview

Think in **layers**—each layer has clear ownership. Problems usually appear at **interfaces** (fixture ↔ DUT, switch ↔ RF path, trigger ↔ digitizer).

<figure class="diagram-figure">
  <img src="{{ '/assets/diagrams/6287173f7349ca1f.png' | relative_url }}" alt="System architecture diagram" class="diagram-img" loading="lazy" />
</figure>


```text
┌─────────────────────────────────────────────────────────────┐
│  Test controller (TestStand, LabVIEW, Python/PyVISA, …)     │
├─────────────────────────────────────────────────────────────┤
│  Instrument bus (PXI/PXIe, LXI, coax for GHz RF)            │
├──────────┬──────────┬──────────┬──────────┬───────────────┤
│   SMU    │   AWG    │ Digitizer│ VNA/SA   │ Digital I/O   │
├──────────┴──────────┴──────────┴──────────┴───────────────┤
│  DUT interface: loadboard → conditioning → switch → Kelvin  │
├─────────────────────────────────────────────────────────────┤
│  Power subsystem (sequencing, bulk rails, protection)         │
├─────────────────────────────────────────────────────────────┤
│  Thermal / environmental (optional)                         │
├─────────────────────────────────────────────────────────────┤
│  Data & analysis (logging, SPC, Cpk, limit feedback)        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                            [ DUT ]
```

## System Layers

### Layer 0 — Test controller

The **software brain** of the system. It owns:

- Test order and branching (setup → measure → teardown)
- Pass/fail against limits
- Data logging and MES/handoff to factory systems
- Driver calls to every instrument

**Common platforms:** NI TestStand, LabVIEW, Python with **PyVISA** / **PyVISA-py**, C# with IVI drivers, or a custom sequencer built in-house.

**Design note:** Keep **instrument abstraction** in software (which resource is the “3.3 V SMU on site 2”) separate from **physical routing** in the fixture—otherwise every engineering change becomes a code change.

---

### Layer 1 — Instrument bus

The **physical backplane** (or cabling plan) that ties instruments together.

| Bus | Typical use | Strengths | Watch-outs |
|-----|-------------|-----------|------------|
| **PXI / PXIe** | Production ATE, tight multi-instrument sync | Star trigger, 10 MHz ref, modular density | Chassis size, vendor lock-in, thermal in rack |
| **LXI** | Bench and distributed racks over LAN | Familiar networking, room to spread instruments | Sync via **IEEE 1588 PTP**; not as tight as PXI for ns-level alignment |
| **Coax / point-to-point** | RF above a few GHz | Best SI for VNA/SA paths | No shared backplane—routing is fixture design |

For **RF work**, you often leave the shared digital backplane and route **coax** from VNA ports through the switch matrix to the DUT launch.

---

### Layer 2 — Instruments (functional blocks)

Mix and match these five blocks per DUT needs:

| Block | Role | Typical measurements / stimulus |
|-------|------|----------------------------------|
| **SMU** (Source Measure Unit) | Source V/I and measure simultaneously | Id–Vd curves, leakage, PMIC rails, parametric IC test |
| **AWG** (Arbitrary Waveform Generator) | Time-domain stimulus | Protocol emulation, stress waveforms, baseband IQ |
| **Digitizer / scope** (PXI module) | High-speed capture | Eye diagrams, burst capture, time-aligned acquisition in ATE |
| **VNA / spectrum analyzer** | Frequency-domain / RF | S-parameters, return loss, NF, EVM, power flatness |
| **Digital I/O / pattern generator** | Digital functional test | JTAG, UART, SPI, I2C, high-speed pattern playback |

**SMU vs bulk power:** SMUs are for **precision** per-pin or per-rail characterization. **Bulk DC supplies** (next layer) feed main rails with higher current and simpler regulation.

---

### Layer 3 — DUT interface (where most hardware design happens)

The **bridge** between instruments and the DUT.

#### Loadboard / fixture

- Custom PCB: **pogo pins**, ZIF, or socketed DUT
- Requirements: **signal integrity**, controlled impedance, mechanical repeatability at volume
- Document stack-up, via strategy, and keep-out for handlers/probers

#### Signal conditioning

- Attenuators, amps, **impedance matching**, DC blocks between instrument and DUT
- Match instrument output impedance to DUT pin expectation (especially RF and high-speed digital)

#### Switch matrix

- Routes **one instrument → many DUT pins** or **many DUTs → one instrument**
- Critical for **throughput** in multi-site test
- RF matrices use SPDT/SP4T **relay or solid-state** switches—each path adds **insertion loss** and needs **calibration**

#### Kelvin (4-wire) sensing

- Separate **force** and **sense** pairs
- Removes cable and contact resistance from measurement
- Essential for sub-milliohm resistance and precision current sourcing

---

### Layer 4 — Power subsystem

Separate from SMUs:

| Element | Purpose |
|---------|---------|
| **Bulk DC supplies** | Main rails (5 V, 3.3 V, battery emulator, …) |
| **Sequencing** | Power-on order (core before I/O, rails before RF)—wrong order damages many ICs |
| **Per-rail monitoring** | Current draw per rail for fault detection |
| **OVP / OCP** | Protect DUT and fixture on short or plug misalignment |

**Design tip:** Define a **power state machine** (OFF → PRECHARGE → ON → MEASURE → OFF) and interlock with the sequencer so tests never run on an illegal rail state.

---

### Layer 5 — Thermal / environmental

| Mode | Use |
|------|-----|
| **Temperature forcing** | Hot/cold plate, chamber—characterize over spec |
| **Burn-in / HALT / HASS** | Reliability screens, early life failure |
| **Humidity / vibration** | Specialized reliability (less common in standard ATE) |

Environmental hardware must be reflected in **safety interlocks** (door open → rails off) and **soak timers** in the test plan.

---

### Layer 6 — Data and analysis

Closes the loop from hardware to factory quality:

- **Results database** — per-unit serial, per-test value, timestamp, station ID
- **SPC** — Cpk, control charts, drift detection across stations
- **Limit sets** — adjusted from statistical feedback (with change control in production)

Without this layer, the bench “works” but the line cannot **prove** yield or debug systemic failures.

## Three Design Problems That Dominate Real Projects

### 1. Signal integrity on the fixture

| Concern | Mitigation |
|---------|------------|
| Controlled impedance traces | Match Zo to system (50 Ω RF, 100 Ω diff digital, etc.) |
| Stub length on high-speed pins | Keep stubs short; route critical nets first in layout |
| RF launch | Proper ground co-planarity, launch transition to coax |
| Crosstalk | Guard traces, spacing, differential pairs where possible |

At **GHz test rates**, the fixture is part of the measurement—not just a wire bundle.

### 2. Switch matrix architecture

| Topology | Pros | Cons |
|----------|------|------|
| **Full crossbar** | Flexible routing, lower path count for some routes | Cost, complexity, isolation challenges |
| **Sparse tree (multiplex tree)** | Cheaper, fewer relays | Higher insertion loss, longer paths |
| **Segmented** | Balance cost and sites | Engineering trade per product family |

**RF reality:** Every relay adds roughly **0.5–1 dB insertion loss** (typical order of magnitude—verify per part). Budget loss in your **VNA calibration** and margin to spec.

### 3. Timing and synchronization

Multi-instrument tests need **deterministic triggering**:

- **PXI:** Star trigger bus + **10 MHz reference**—industry default for aligned AWG + digitizer + digital pattern
- **LXI:** **IEEE 1588 PTP** for sub-microsecond sync over Ethernet when PXI is not used

Misaligned triggers show up as “random” failures on digital capture or RF measurements that only fail on some stations.

---

## Design-for-Testability (DFT) Overview

In **Design-for-Testability (DFT)**, “common system design” means architectural and structural practices that make silicon (and the systems built from it) **controllable, observable, and diagnosable** during manufacturing test and bring-up.

DFT exists at **multiple levels**:

| Level | What you are testing | Typical access |
|-------|----------------------|----------------|
| **Chip (die)** | Logic, memories, analog macros | Scan, BIST, JTAG, probe pads |
| **Subsystem / IP** | CPU core, NoC, PHY, NPU tile | Wrapped cores (IEEE 1500), IJTAG |
| **Board** | Interconnect, power, boot | Boundary scan, functional ATE |
| **System** | OS boot, workloads, thermal | System-level test (SLT), field diagnostics |

<figure class="diagram-figure">
  <img src="{{ '/assets/diagrams/05b09cb2b27d8b3e.png' | relative_url }}" alt="System architecture diagram" class="diagram-img" loading="lazy" />
</figure>


---

## Common DFT Techniques (Industry Categories)

### 1. Scan-based design (most common DFT method)

Scan replaces ordinary flip-flops with **scan flip-flops** so internal state becomes **controllable** (shift in patterns) and **observable** (shift out results).

| Concept | Description |
|---------|-------------|
| **Scan chains** | Flip-flops connected serially; shift in test vectors, shift out responses |
| **Full scan** | Nearly all sequential elements in scan—highest coverage, more area/timing impact |
| **Partial scan** | Only selected flops scanned—lower overhead, reduced controllability |
| **Multiple scan chains** | Parallel chains to reduce shift time and tester depth |

**Benefits:** Very high fault coverage, enables **ATPG** (Automatic Test Pattern Generation), industry standard for ASICs and SoCs.

---

### 2. Built-In Self-Test (BIST)

On-chip hardware tests itself—reduces tester pattern volume and enables field/diagnostic test.

| Type | Targets | Typical blocks |
|------|---------|----------------|
| **Logic BIST (LBIST)** | Combinational + sequential logic | LFSR (pattern generator), MISR (signature analyzer) |
| **Memory BIST (MBIST)** | SRAM, DRAM, embedded memories | March engines, retention, address-decoder tests |
| **Analog / mixed-signal BIST** | PLL, ADC/DAC, SerDes | Loopback, DC/AC stimulus, signature comparison |

---

### 3. Boundary scan / JTAG (IEEE 1149.1)

Standardized **chip- and board-level** test access without physical probes on every net.

| Element | Role |
|---------|------|
| **TAP controller** | State machine driven by TCK, TMS |
| **TDI / TDO** | Serial scan in/out |
| **Boundary scan cells** | Around I/O—test interconnect and pin logic |

**Uses:** Board connectivity (opens/shorts), pin testing, FPGA configuration, debug, in-system programming.

**Common in:** CPUs, FPGAs, networking gear, automotive ECUs.

---

### 4. Design partitioning for test

Architectural organization to simplify test and diagnosis.

- Modular hierarchy and **IP wrappers** (IEEE 1500)
- Independent **clock domains** and **power domains**
- **Test isolation** (clamp outputs, disable functional paths)
- **Wrapper insertion** around reusable IPs

**Benefits:** Easier diagnosis, parallel test of blocks, simpler patterns per partition.

---

### 5. Clock and reset DFT design

Clocks and resets are primary DFT risk areas.

| Technique | Purpose |
|-----------|---------|
| **Test clocks** | Controlled, slower or muxed clocks in test mode |
| **Scan-enable clocks** | Safe shifting without functional clock glitches |
| **Clock multiplexers** | Select functional vs test clock |
| **Reset controllability** | Known state before scan capture |
| **CDC test support** | Avoid metastability during scan/at-speed |

**Goals:** Reliable scan operation, **at-speed** test feasibility, timing closure in test mode.

---

### 6. At-speed testing

Tests logic at **operational frequency**—catches delay defects missed by slow scan.

| Method | Idea |
|--------|------|
| **Launch-on-capture (LOC)** | Launch transition with functional clock edge; capture on capture edge |
| **Launch-on-shift (LOS)** | Launch during shift (where allowed by methodology) |

**Targets:** Transition faults, path delay faults, small-delay defects.

**Critical for:** High-performance CPUs, GPUs, networking ASICs.

---

### 7. Test compression

Advanced nodes produce enormous scan data volume.

| Method | Benefit |
|--------|---------|
| **Scan compression** | Fewer tester cycles and less ATE memory |
| **Embedded deterministic test (EDT)** | On-chip decompressor feeds scan chains |
| **Compactors** | Compress scan-out before sending to tester |

Essential for cost-effective manufacturing on large SoCs.

---

### 8. Memory repair and redundancy

Improves **manufacturing yield** for dense SRAM arrays.

- Spare rows/columns
- **Fuse / eFuse** programming of repair addresses
- Redundant memory blocks (cache repair)

Heavily used in SRAM, cache, and on-chip memory subsystems.

---

### 9. Power-aware DFT

Test modes can draw **more power** than functional modes (all nodes toggling during scan).

| Technique | Purpose |
|-----------|---------|
| **Scan chain staggering** | Limit simultaneous switching |
| **Shift-power reduction** | Reduce toggling during shift |
| **Power-domain-aware scan** | Respect isolation in multi-VD designs |
| **Low-power ATPG** | Patterns that minimize switching |
| **Clock gating in test mode** | Block unnecessary clock trees |

Important for mobile SoCs, AI accelerators, and battery-powered devices.

---

### 10. IEEE DFT standards

| Standard | Purpose |
|----------|---------|
| **IEEE 1149.1** | JTAG / boundary scan |
| **IEEE 1500** | Embedded core test (wrapper registers) |
| **IEEE 1687** | IJTAG — internal instrument access network |
| **IEEE 1149.6** | High-speed AC interconnect test |
| **IEEE 1838** | 3D IC die-stack test access |

---

### 11. Debug and observability (often paired with DFT)

Not strictly manufacturing test, but co-planned with DFT.

- Trace buffers and **embedded logic analyzers**
- Performance counters
- Silicon debug buses
- Error logging registers

Common in CPUs, FPGA SoCs, and automotive SoCs for post-silicon debug.

---

### 12. Fault models used in DFT

DFT structures target specific defect mechanisms:

| Fault model | What it represents |
|-------------|-------------------|
| **Stuck-at (SA)** | Node stuck at 0 or 1 |
| **Transition** | Slow-to-rise / slow-to-fall |
| **Bridging** | Two nets shorted |
| **Open** | Broken connection (variant modeling) |
| **Path delay** | Excessive delay on a path |
| **Small-delay defect** | Subtle timing failures at speed |

---

### 13. System-level test (SLT)

Performed **after** manufacturing structural test—runs realistic workloads.

| Characteristic | Examples |
|----------------|----------|
| Real software stacks | Boot OS, run drivers |
| Stress interaction | Memory stress, thermal + performance |
| Use cases | Servers, AI accelerators, automotive ECUs |

Examples: booting Linux, running memory stress, validating high-speed links under traffic.

---

## Modern SoC DFT Architecture

A typical advanced SoC integrates:

```text
┌────────────────────────────────────────────────────────────┐
│  Hierarchical scan chains + compression (EDT)              │
│  MBIST controllers (per memory cluster)                      │
│  JTAG / IJTAG network (debug + instrument access)           │
│  On-chip clock controller (OCC) for at-speed test            │
│  Power-aware scan + domain isolation                       │
│  Repair / fuse controller (memory yield)                     │
│  LBIST (optional, field/mission-mode test)                 │
└────────────────────────────────────────────────────────────┘
```

---

## DFT Tradeoffs, Tools, and Flow

### Tradeoffs

| Goal | Typical tradeoff |
|------|------------------|
| Higher coverage | More area and routing overhead |
| Faster test time | More scan chains, compression logic, tester channels |
| Better observability | Higher shift power, longer patterns |
| More compression | More design complexity, timing on decompressor |
| At-speed testing | Harder timing closure in test mode |

### Common tool vendors

| Vendor | Typical tool categories |
|--------|-------------------------|
| **Synopsys** | DFT Compiler, TetraMAX ATPG, TestMAX |
| **Cadence** | Modus DFT, Virtuoso integration |
| **Siemens EDA** | Tessent (scan, ATPG, diagnosis) |

Categories: scan insertion, ATPG, MBIST synthesis, formal DFT verification, pattern simulation, diagnosis.

### Typical DFT flow

```text
RTL design
  → DFT rule checking (lint for testability)
  → Scan insertion
  → MBIST insertion
  → ATPG pattern generation
  → Fault simulation / coverage analysis
  → Pattern validation (timing, power)
  → Silicon manufacturing test (wafer + package)
  → Diagnosis and yield analysis
```

---

## ASIC vs FPGA DFT Differences

| Aspect | ASIC (standard-cell SoC) | FPGA |
|--------|--------------------------|------|
| **Scan** | Full custom scan insertion, ATPG, compression | Limited—device is pre-fabricated; use vendor **internal scan** or soft logic test |
| **MBIST** | Custom MBIST for embedded SRAMs | Use FPGA block RAM test features or soft MBIST IP |
| **BIST** | LBIST/MBIST designed into tapeout | Rare on-die LBIST; rely on **configuration bitstream** checks |
| **JTAG** | Custom TAP + IEEE 1500/1687 | Vendor **hardware JTAG** for config and debug (Xilinx Vitis, Intel Quartus) |
| **At-speed** | LOC/LOS with OCC on functional clocks | Timing validated by static timing analysis; at-speed via **functional test** on board |
| **Repair** | eFuse repair for memories | Not applicable—defective parts discarded |
| **Cost model** | DFT affects **yield and tester $/die** | DFT affects **bring-up time** and board test, not wafer yield |

**Interview sound bite:** ASIC DFT is about **manufacturing fault coverage at scale**; FPGA DFT is about **configuration integrity, boundary scan on the board, and debug access** to pre-built silicon.

---

## Scan Chain Architecture in Detail

### Scan flip-flop structure

A scan cell multiplexes **functional mode** vs **scan mode**:

```text
Functional: D → [FF] → Q  (normal operation)

Scan mode:  scan_in → [FF] → scan_out
            (serial shift when scan_enable active)
```

### Scan operations (classic flow)

| Phase | Action |
|-------|--------|
| **Shift** | Apply scan_enable; pulse test clock to load/unload chain |
| **Capture** | Release scan_enable; one functional clock captures combinational response into flops |
| **Compare** | Shift out captured values; compare to golden response (on tester or MISR for BIST) |

### Multi-chain architecture

```text
         ┌── Chain 0 ──┐
Tester ──┼── Chain 1 ──┼── Parallel load/unload (fewer cycles)
         └── Chain N ──┘
              │
         Decompressor (EDT)  ← compressed patterns from tester
              │
         Compactor  → compressed scan-out to tester
```

**Design rules:**

- Balance chain lengths to minimize **shift time** waste
- Avoid long combinatorial paths between chains without pipeline consideration
- Place **lockup latches** on clock-domain boundaries crossing into scan paths

---

## MBIST Algorithms

MBIST engines apply algorithmic **March** tests to memory arrays.

### Common March tests (conceptual)

| Test / variant | What it detects (simplified) |
|----------------|------------------------------|
| **March C / C−** | Stuck-at faults in cells, some coupling |
| **Checkerboard** | Adjacent-cell interaction patterns |
| **Walking 1/0** | Address decoder and cell faults |
| **Retention** | Hold time / leakage-related memory loss |

A **March element** is often written as operations on each cell, e.g. ↑(w0); ↑(r0,w1); … meaning traverse addresses ascending with write/read operations.

### MBIST block diagram

```text
[ MBIST controller ] ──► [ Address generator ]
        │                      │
        ▼                      ▼
   [ Algorithm ROM ]     [ Memory under test ]
        │                      │
        └──── Compare ◄── Read data / expected
```

**Production flow:** MBIST runs on tester or self-started after reset; failures map to **repair fuse** records if redundancy exists.

---

## IJTAG Architecture (IEEE 1687)

**IJTAG** extends JTAG to access **internal instruments** (sensors, monitors, custom TDRs) through a standardized network—not only pad boundary cells.

| Concept | Role |
|---------|------|
| **SIB** (Segment Insertion Bit) | Enables/disables branches of instrument network |
| **TDR** (Test Data Register) | Holds control/status for an instrument |
| **Host scan path** | IEEE 1149.1 TAP still provides entry |
| **Instrument connectivity language (ICL)** | Describes network topology (like BSDL for 1149.1) |

```text
TAP (1149.1) → Host interface → SIB → Instrument TDR → [PLL monitor]
                              └→ SIB → [Temperature sensor]
                              └→ SIB → [Custom IP status]
```

**Why it matters:** Hierarchical SoCs need **post-silicon bring-up** without adding pads per internal node. IJTAG is the plumbing for power, clock, and analog bring-up scripts.

---

## ATPG Algorithms and Fault Coverage Math

### Fault coverage definition

**Fault coverage** = (number of detected faults ÷ total faults in fault list) × 100%

In practice:

- **Fault list** is generated from netlist + fault model (e.g. all SA faults on gates/ports)
- **Detected** = fault causes observable difference on outputs for at least one pattern
- **Redundant / untestable** faults are often excluded from denominator (methodology-dependent)

### Stuck-at fault model

Each net/site modeled as **SA0** and **SA1**. For N fault sites, up to **2N** stuck-at faults (fewer after equivalence collapsing).

### Transition fault model

Each gate output has **slow-to-rise** and **slow-to-fall** faults—requires **two-pattern** tests (init + launch) and often **at-speed** capture.

### Common ATPG algorithms (names to know)

| Algorithm | Idea |
|-----------|------|
| **D-algorithm** | Five-valued logic (0,1,X,D,D'); propagates fault effects to outputs |
| **PODEM** | Backtrack on inputs to justify and propagate faults |
| **FAN** | Improved PODEM with multiple backtrack reduction |
| **Timing-aware ATPG** | Uses SDF timing for delay and small-delay defects |

Modern commercial tools combine **structural ATPG** + **compression** + **low-power fill**.

### Example coverage reporting

If fault list has 1,000,000 collapsed SA faults and patterns detect 995,000, **coverage = 99.5%**.

Remaining faults may be **redundant**, **partially detected**, or need **additional patterns** / **fault model** (transition, bridging).

---

## Physical-Design Impacts of DFT

DFT is not “logic only”—it reshapes **floorplan, routing, and timing**.

| Impact area | DFT effect |
|-------------|------------|
| **Area** | Scan MUX on flops (~5–15% sequential area, design-dependent) |
| **Routing congestion** | Scan chains snake across die—compete with functional routes |
| **Timing** | Scan mode mux delays; **hold** fixes on shift paths |
| **Clock tree** | Extra muxes, OCC, separate test clock roots |
| **Power grid** | Shift/capture current spikes—IR drop analysis in test mode |
| **Pad frame** | JTAG pins, compression IO, MBIST status pins |
| **Fuse banks** | Repair metadata—physical region near memories |

**Sign-off:** Static timing in **functional mode** and **scan/at-speed test modes**; power analysis for worst-case shift.

---

## DFT for AI Accelerators

AI/ML silicon (GPUs, TPUs, NPUs) stresses DFT differently:

| Challenge | DFT response |
|-----------|--------------|
| **Massive SRAM** (weights, activations) | Distributed **MBIST** per bank + repair |
| **Large regular arrays** | Partitioned scan; tile-level wrappers |
| **High power density** | Aggressive **shift staggering**, low-power ATPG |
| **SerDes / HBM interfaces** | Boundary + loopback BIST; AC JTAG (1149.6) |
| **Reduced numeric precision** | Functional SLT with tensor ops—catches array interaction bugs |
| **Multi-die (chiplet)** | IEEE 1838 die-to-die test access |

**SLT is critical:** Structural scan won't catch many **data-path interaction** bugs in systolic arrays—workload-based test (short inference kernels) complements ATPG.

---

## Automotive DFT and ISO 26262

Automotive ECUs require DFT that supports **safety**, not only yield.

| ISO 26262 theme | DFT / test connection |
|-----------------|----------------------|
| **Fault detection** | Manufacturing test proves low **latent defect rate** |
| **Diagnostic coverage** | LBIST, watchdogs, ECC on memories—aligned with safety mechanisms |
| **Lifecycle** | Field logging + debug (JTAG/IJTAG) for failure analysis |
| **Independence** | Safety-critical blocks tested with known good patterns; **FMEDA** uses DPPM from test data |
| **Requirements trace** | DFT features documented in safety case (what manufacturing test guarantees) |

**Practice:** Automotive programs often require **100% stuck-at** (or agreed coverage) + **transition** coverage targets + **MBIST** on all safety-related memories + **scan chain integrity** tests on every lot.

---

## DFT Interview Questions

### Fundamentals

1. What is the difference between **DFT** and **design for debug**?
2. Why is **scan** the dominant manufacturing test method for digital ASICs?
3. Explain **stuck-at** vs **transition** fault models.
4. What problem does **scan compression** solve?

### Scan and ATPG

5. Walk through **shift → capture → shift-out** in a scan test.
6. What is **full scan** vs **partial scan**?
7. What is **launch-on-capture** and when do you need an **OCC**?
8. How do you calculate **fault coverage**? What are redundant faults?

### BIST and memory

9. Compare **LBIST** vs **MBIST** vs external ATPG.
10. What is a **March** test? Why are multiple March elements used?
11. How does **memory repair** improve yield?

### Standards and system

12. What signals does **IEEE 1149.1 JTAG** provide?
13. How does **IJTAG (1687)** differ from boundary scan?
14. What is **SLT** and why is it used after wafer/final test?
15. **ASIC vs FPGA:** how does DFT differ?

### Architecture / tradeoffs

16. Trade off **more scan chains** vs **fewer, longer chains**.
17. How does **power-aware DFT** reduce shift-induced IR drop?
18. Name three **physical design** impacts of inserting scan.

### Scenario

19. An SoC fails only at **high temperature** on SLT but passes scan at room—what might you suspect?
20. **AI accelerator** has 512 MB on-chip SRAM—outline your DFT strategy.

---

## Summary

### Part A — ATE / DUT

| Layer | You are designing… |
|-------|---------------------|
| **Controller** | Sequencer, limits, logging, drivers |
| **Bus** | PXIe vs LXI vs coax RF plan |
| **Instruments** | SMU, AWG, digitizer, VNA/SA, digital I/O mix |
| **DUT interface** | Loadboard, conditioning, switches, Kelvin |
| **Power** | Sequencing, bulk rails, protection |
| **Environment** | Temp, burn-in (when required) |
| **Data** | DB, SPC, limit feedback |

**ATE focus:** Most custom hardware effort is the **fixture + switch matrix + power sequencing**; most debug time is **SI, switch loss, and trigger alignment**.

### Part B — Silicon DFT

| Technique | Primary purpose |
|-----------|-----------------|
| **Scan + ATPG** | Manufacturing digital fault coverage |
| **MBIST / LBIST** | Memory and logic self-test |
| **JTAG / IJTAG** | Board test, debug, instrument access |
| **Compression** | Tester time and cost |
| **At-speed** | Delay and transition defects |
| **Repair / power-aware** | Yield and safe test power |
| **SLT** | Real workload validation after structural test |

**DFT focus:** Scan and compression dominate **digital ASIC** cost and quality; **MBIST + repair** dominate **memory yield**; **JTAG/IJTAG** bridge silicon to board and bring-up.

### Related topics on this blog

- [System Design Overview: Embedded Architectures]({{ site.baseurl }}/2025/10/29/system-design-overview-embedded/) — broader embedded/validation context
- [Design Quickset UEI (IoT / device test)]({{ site.baseurl }}/2025/11/17/design-quickset-uei/) — connected device validation at scale
- [Distributed System Design Ecosystem]({{ site.baseurl }}/2026/05/26/distributed-system-design-ecosystem/) — when test data and factory systems meet cloud/MES pipelines
