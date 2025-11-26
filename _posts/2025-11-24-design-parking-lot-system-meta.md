---
layout: post
title: "Design a Parking Lot System - Meta System Design Interview"
date: 2025-11-24
categories: [System Design, Interview Example, Meta, Object-Oriented Design, State Management]
excerpt: "A comprehensive guide to designing a parking lot system focusing on object-oriented design, class hierarchy, state management, and edge case handling. Meta interview question emphasizing modeling real-world entities and managing rules rather than scalability."
---

## Introduction

Designing a parking lot system is a classic object-oriented design question at Meta that tests your ability to model real-world entities, manage state, and handle complex business rules. This question focuses on:

- **Object-oriented design**: Class hierarchy and relationships
- **State management**: Parking spot states, vehicle states
- **Edge case handling**: Different vehicle types, parking rules
- **Efficient tracking**: Occupancy management, spot finding

This guide covers the complete design of a parking lot system with proper class structure, state management, and efficient algorithms.

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Requirements](#requirements)
3. [Class Design](#class-design)
4. [State Management](#state-management)
5. [Core Operations](#core-operations)
6. [Edge Cases](#edge-cases)
7. [Efficient Tracking](#efficient-tracking)
8. [Implementation](#implementation)
9. [Summary](#summary)

## Problem Statement

**Design a parking lot system that:**

1. **Manages parking spots** of different types (compact, regular, large)
2. **Handles different vehicle types** (motorcycle, car, truck)
3. **Tracks occupancy** efficiently
4. **Finds available spots** for vehicles
5. **Handles parking rules** (vehicle can park in larger spots)
6. **Calculates fees** based on time
7. **Manages entry/exit** operations

**Scale Requirements:**
- Support 100-10,000 parking spots
- Handle multiple vehicle types
- Fast spot finding: < 10ms
- Efficient occupancy tracking

## Requirements

### Functional Requirements

1. **Park Vehicle**: Park a vehicle in appropriate spot
2. **Unpark Vehicle**: Remove vehicle and calculate fee
3. **Find Spot**: Find available spot for vehicle type
4. **Check Availability**: Check if spots available
5. **Calculate Fee**: Calculate parking fee based on time
6. **Track Occupancy**: Monitor spot usage

### Non-Functional Requirements

**Performance:**
- Spot finding: < 10ms
- Efficient memory usage
- Fast occupancy checks

**Correctness:**
- No double parking
- Correct fee calculation
- Proper state management

## Class Design

### Core Classes

```python
from enum import Enum
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass

class VehicleType(Enum):
    MOTORCYCLE = "motorcycle"
    CAR = "car"
    TRUCK = "truck"

class SpotType(Enum):
    COMPACT = "compact"
    REGULAR = "regular"
    LARGE = "large"

class SpotStatus(Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"

@dataclass
class Vehicle:
    license_plate: str
    vehicle_type: VehicleType
    parked_at: Optional[datetime] = None
    spot: Optional['ParkingSpot'] = None
    
    def can_park_in(self, spot_type: SpotType) -> bool:
        """Check if vehicle can park in spot type."""
        rules = {
            VehicleType.MOTORCYCLE: [SpotType.COMPACT, SpotType.REGULAR, SpotType.LARGE],
            VehicleType.CAR: [SpotType.REGULAR, SpotType.LARGE],
            VehicleType.TRUCK: [SpotType.LARGE]
        }
        return spot_type in rules[self.vehicle_type]

class ParkingSpot:
    def __init__(self, spot_id: int, spot_type: SpotType, floor: int):
        self.spot_id = spot_id
        self.spot_type = spot_type
        self.floor = floor
        self.status = SpotStatus.AVAILABLE
        self.vehicle: Optional[Vehicle] = None
        self.occupied_at: Optional[datetime] = None
    
    def is_available(self) -> bool:
        """Check if spot is available."""
        return self.status == SpotStatus.AVAILABLE
    
    def park_vehicle(self, vehicle: Vehicle) -> bool:
        """Park vehicle in spot."""
        if not self.is_available():
            return False
        
        if not vehicle.can_park_in(self.spot_type):
            return False
        
        self.vehicle = vehicle
        self.status = SpotStatus.OCCUPIED
        self.occupied_at = datetime.now()
        vehicle.spot = self
        vehicle.parked_at = datetime.now()
        return True
    
    def unpark_vehicle(self) -> Optional[Vehicle]:
        """Remove vehicle from spot."""
        if self.status != SpotStatus.OCCUPIED:
            return None
        
        vehicle = self.vehicle
        self.vehicle = None
        self.status = SpotStatus.AVAILABLE
        self.occupied_at = None
        vehicle.spot = None
        vehicle.parked_at = None
        
        return vehicle

class Floor:
    def __init__(self, floor_number: int):
        self.floor_number = floor_number
        self.spots: List[ParkingSpot] = []
        self.spot_map: dict = {}  # spot_id -> ParkingSpot
    
    def add_spot(self, spot: ParkingSpot):
        """Add spot to floor."""
        self.spots.append(spot)
        self.spot_map[spot.spot_id] = spot
    
    def get_available_spots(self, spot_type: Optional[SpotType] = None) -> List[ParkingSpot]:
        """Get available spots, optionally filtered by type."""
        available = [s for s in self.spots if s.is_available()]
        if spot_type:
            available = [s for s in available if s.spot_type == spot_type]
        return available
    
    def get_occupancy(self) -> dict:
        """Get occupancy statistics."""
        total = len(self.spots)
        occupied = sum(1 for s in self.spots if s.status == SpotStatus.OCCUPIED)
        return {
            'total': total,
            'occupied': occupied,
            'available': total - occupied,
            'occupancy_rate': occupied / total if total > 0 else 0
        }

class ParkingLot:
    def __init__(self, name: str):
        self.name = name
        self.floors: List[Floor] = []
        self.vehicles: dict = {}  # license_plate -> Vehicle
        self.spot_index: dict = {}  # spot_id -> ParkingSpot
        self.fee_rate = {
            VehicleType.MOTORCYCLE: 2.0,  # per hour
            VehicleType.CAR: 5.0,
            VehicleType.TRUCK: 10.0
        }
    
    def add_floor(self, floor: Floor):
        """Add floor to parking lot."""
        self.floors.append(floor)
        # Index all spots
        for spot in floor.spots:
            self.spot_index[spot.spot_id] = spot
    
    def park_vehicle(self, vehicle: Vehicle) -> Optional[ParkingSpot]:
        """Park vehicle in appropriate spot."""
        if vehicle.license_plate in self.vehicles:
            raise ValueError("Vehicle already parked")
        
        # Find suitable spot
        spot = self._find_spot(vehicle)
        if not spot:
            return None
        
        # Park vehicle
        if spot.park_vehicle(vehicle):
            self.vehicles[vehicle.license_plate] = vehicle
            return spot
        
        return None
    
    def unpark_vehicle(self, license_plate: str) -> Optional[float]:
        """Unpark vehicle and calculate fee."""
        if license_plate not in self.vehicles:
            return None
        
        vehicle = self.vehicles[license_plate]
        spot = vehicle.spot
        
        if not spot:
            return None
        
        # Calculate fee
        fee = self._calculate_fee(vehicle, spot)
        
        # Unpark
        spot.unpark_vehicle()
        del self.vehicles[license_plate]
        
        return fee
    
    def _find_spot(self, vehicle: Vehicle) -> Optional[ParkingSpot]:
        """Find suitable spot for vehicle."""
        # Get compatible spot types (vehicle can park in same or larger)
        compatible_types = self._get_compatible_spot_types(vehicle.vehicle_type)
        
        # Search floors in order
        for floor in self.floors:
            for spot_type in compatible_types:
                available_spots = floor.get_available_spots(spot_type)
                if available_spots:
                    # Return first available (or use better strategy)
                    return available_spots[0]
        
        return None
    
    def _get_compatible_spot_types(self, vehicle_type: VehicleType) -> List[SpotType]:
        """Get spot types compatible with vehicle type."""
        rules = {
            VehicleType.MOTORCYCLE: [SpotType.COMPACT, SpotType.REGULAR, SpotType.LARGE],
            VehicleType.CAR: [SpotType.REGULAR, SpotType.LARGE],
            VehicleType.TRUCK: [SpotType.LARGE]
        }
        return rules[vehicle_type]
    
    def _calculate_fee(self, vehicle: Vehicle, spot: ParkingSpot) -> float:
        """Calculate parking fee."""
        if not spot.occupied_at:
            return 0.0
        
        duration = datetime.now() - spot.occupied_at
        hours = duration.total_seconds() / 3600
        
        # Round up to nearest hour
        hours = max(1, int(hours) + (1 if duration.total_seconds() % 3600 > 0 else 0))
        
        rate = self.fee_rate[vehicle.vehicle_type]
        return hours * rate
    
    def get_availability(self, vehicle_type: VehicleType) -> dict:
        """Get availability for vehicle type."""
        compatible_types = self._get_compatible_spot_types(vehicle_type)
        total_available = 0
        
        for floor in self.floors:
            for spot_type in compatible_types:
                total_available += len(floor.get_available_spots(spot_type))
        
        return {
            'vehicle_type': vehicle_type.value,
            'available_spots': total_available
        }
    
    def get_occupancy_summary(self) -> dict:
        """Get overall occupancy summary."""
        total_spots = 0
        occupied_spots = 0
        
        for floor in self.floors:
            occupancy = floor.get_occupancy()
            total_spots += occupancy['total']
            occupied_spots += occupancy['occupied']
        
        return {
            'total_spots': total_spots,
            'occupied_spots': occupied_spots,
            'available_spots': total_spots - occupied_spots,
            'occupancy_rate': occupied_spots / total_spots if total_spots > 0 else 0
        }
```

## State Management

### Spot State Machine

```
AVAILABLE -> OCCUPIED (on park)
OCCUPIED -> AVAILABLE (on unpark)
AVAILABLE -> MAINTENANCE (admin action)
MAINTENANCE -> AVAILABLE (admin action)
AVAILABLE -> RESERVED (reservation)
RESERVED -> OCCUPIED (on park)
RESERVED -> AVAILABLE (reservation expired)
```

### State Transitions

```python
class ParkingSpot:
    def set_maintenance(self):
        """Set spot to maintenance mode."""
        if self.status == SpotStatus.OCCUPIED:
            raise ValueError("Cannot set occupied spot to maintenance")
        self.status = SpotStatus.MAINTENANCE
    
    def clear_maintenance(self):
        """Clear maintenance mode."""
        if self.status == SpotStatus.MAINTENANCE:
            self.status = SpotStatus.AVAILABLE
    
    def reserve(self):
        """Reserve spot."""
        if self.status != SpotStatus.AVAILABLE:
            raise ValueError("Can only reserve available spots")
        self.status = SpotStatus.RESERVED
    
    def cancel_reservation(self):
        """Cancel reservation."""
        if self.status == SpotStatus.RESERVED:
            self.status = SpotStatus.AVAILABLE
```

## Core Operations

### Parking Operation

```python
def park_vehicle(self, license_plate: str, vehicle_type: VehicleType) -> dict:
    """Park vehicle and return result."""
    # Check if already parked
    if license_plate in self.vehicles:
        return {
            'success': False,
            'message': 'Vehicle already parked'
        }
    
    # Create vehicle
    vehicle = Vehicle(license_plate, vehicle_type)
    
    # Find spot
    spot = self._find_spot(vehicle)
    if not spot:
        return {
            'success': False,
            'message': 'No available spots'
        }
    
    # Park
    if spot.park_vehicle(vehicle):
        self.vehicles[license_plate] = vehicle
        return {
            'success': True,
            'spot_id': spot.spot_id,
            'floor': spot.floor,
            'spot_type': spot.spot_type.value,
            'parked_at': vehicle.parked_at.isoformat()
        }
    
    return {
        'success': False,
        'message': 'Failed to park vehicle'
    }
```

### Unparking Operation

```python
def unpark_vehicle(self, license_plate: str) -> dict:
    """Unpark vehicle and return fee."""
    if license_plate not in self.vehicles:
        return {
            'success': False,
            'message': 'Vehicle not found'
        }
    
    vehicle = self.vehicles[license_plate]
    fee = self._calculate_fee(vehicle, vehicle.spot)
    
    vehicle.spot.unpark_vehicle()
    del self.vehicles[license_plate]
    
    return {
        'success': True,
        'fee': fee,
        'duration_hours': (datetime.now() - vehicle.parked_at).total_seconds() / 3600
    }
```

## Edge Cases

### Handling Different Vehicle Types

```python
def _find_spot(self, vehicle: Vehicle) -> Optional[ParkingSpot]:
    """Find spot with preference for exact match."""
    compatible_types = self._get_compatible_spot_types(vehicle.vehicle_type)
    
    # Prefer exact match first
    preferred_type = self._get_preferred_spot_type(vehicle.vehicle_type)
    
    # Try preferred type first
    for floor in self.floors:
        spots = floor.get_available_spots(preferred_type)
        if spots:
            return spots[0]
    
    # Try other compatible types
    for floor in self.floors:
        for spot_type in compatible_types:
            if spot_type != preferred_type:
                spots = floor.get_available_spots(spot_type)
                if spots:
                    return spots[0]
    
    return None

def _get_preferred_spot_type(self, vehicle_type: VehicleType) -> SpotType:
    """Get preferred spot type for vehicle."""
    preferences = {
        VehicleType.MOTORCYCLE: SpotType.COMPACT,
        VehicleType.CAR: SpotType.REGULAR,
        VehicleType.TRUCK: SpotType.LARGE
    }
    return preferences[vehicle_type]
```

### Handling Multiple Floors

```python
def _find_spot(self, vehicle: Vehicle, preferred_floor: Optional[int] = None) -> Optional[ParkingSpot]:
    """Find spot, optionally preferring specific floor."""
    compatible_types = self._get_compatible_spot_types(vehicle.vehicle_type)
    
    # If preferred floor specified, try it first
    if preferred_floor is not None:
        floor = next((f for f in self.floors if f.floor_number == preferred_floor), None)
        if floor:
            for spot_type in compatible_types:
                spots = floor.get_available_spots(spot_type)
                if spots:
                    return spots[0]
    
    # Search all floors
    for floor in self.floors:
        for spot_type in compatible_types:
            spots = floor.get_available_spots(spot_type)
            if spots:
                return spots[0]
    
    return None
```

## Efficient Tracking

### Occupancy Tracking

```python
class OccupancyTracker:
    def __init__(self, parking_lot: ParkingLot):
        self.parking_lot = parking_lot
        self.spot_availability = {}  # spot_type -> count
        self._initialize()
    
    def _initialize(self):
        """Initialize availability counts."""
        for spot_type in SpotType:
            self.spot_availability[spot_type] = 0
        
        for floor in self.parking_lot.floors:
            for spot in floor.spots:
                if spot.is_available():
                    self.spot_availability[spot.spot_type] += 1
    
    def update_on_park(self, spot: ParkingSpot):
        """Update counts when vehicle parks."""
        self.spot_availability[spot.spot_type] -= 1
    
    def update_on_unpark(self, spot: ParkingSpot):
        """Update counts when vehicle unparks."""
        self.spot_availability[spot.spot_type] += 1
    
    def get_availability(self, vehicle_type: VehicleType) -> int:
        """Get available spots for vehicle type."""
        compatible_types = self._get_compatible_spot_types(vehicle_type)
        return sum(self.spot_availability[t] for t in compatible_types)
    
    def _get_compatible_spot_types(self, vehicle_type: VehicleType) -> List[SpotType]:
        """Get compatible spot types."""
        rules = {
            VehicleType.MOTORCYCLE: [SpotType.COMPACT, SpotType.REGULAR, SpotType.LARGE],
            VehicleType.CAR: [SpotType.REGULAR, SpotType.LARGE],
            VehicleType.TRUCK: [SpotType.LARGE]
        }
        return rules[vehicle_type]
```

### Fast Spot Finding with Indexing

```python
class ParkingLot:
    def __init__(self, name: str):
        # ... existing code ...
        self.availability_index = {
            SpotType.COMPACT: [],
            SpotType.REGULAR: [],
            SpotType.LARGE: []
        }
        self._build_index()
    
    def _build_index(self):
        """Build index of available spots by type."""
        for floor in self.floors:
            for spot in floor.spots:
                if spot.is_available():
                    self.availability_index[spot.spot_type].append(spot)
    
    def _find_spot_fast(self, vehicle: Vehicle) -> Optional[ParkingSpot]:
        """Fast spot finding using index."""
        compatible_types = self._get_compatible_spot_types(vehicle.vehicle_type)
        
        for spot_type in compatible_types:
            available = self.availability_index[spot_type]
            if available:
                spot = available.pop(0)
                return spot
        
        return None
    
    def park_vehicle(self, vehicle: Vehicle) -> Optional[ParkingSpot]:
        """Park with index update."""
        spot = self._find_spot_fast(vehicle)
        if spot and spot.park_vehicle(vehicle):
            self.vehicles[vehicle.license_plate] = vehicle
            return spot
        return None
    
    def unpark_vehicle(self, license_plate: str) -> Optional[float]:
        """Unpark with index update."""
        if license_plate not in self.vehicles:
            return None
        
        vehicle = self.vehicles[license_plate]
        spot = vehicle.spot
        
        fee = self._calculate_fee(vehicle, spot)
        spot.unpark_vehicle()
        
        # Update index
        self.availability_index[spot.spot_type].append(spot)
        
        del self.vehicles[license_plate]
        return fee
```

## Implementation

### Complete Example

```python
# Create parking lot
parking_lot = ParkingLot("Downtown Parking")

# Add floors
floor1 = Floor(1)
floor1.add_spot(ParkingSpot(1, SpotType.COMPACT, 1))
floor1.add_spot(ParkingSpot(2, SpotType.REGULAR, 1))
floor1.add_spot(ParkingSpot(3, SpotType.LARGE, 1))
parking_lot.add_floor(floor1)

# Park vehicle
result = parking_lot.park_vehicle("ABC123", VehicleType.CAR)
print(result)  # {'success': True, 'spot_id': 2, ...}

# Check availability
availability = parking_lot.get_availability(VehicleType.CAR)
print(availability)  # {'vehicle_type': 'car', 'available_spots': 1}

# Unpark vehicle
result = parking_lot.unpark_vehicle("ABC123")
print(result)  # {'success': True, 'fee': 5.0, ...}
```

## What Interviewers Look For

### Object-Oriented Design Skills

1. **Class Design**
   - Proper class hierarchy and relationships
   - Clear separation of concerns
   - Appropriate use of inheritance/composition
   - **Red Flags**: God classes, poor encapsulation, unclear relationships

2. **Modeling Real-World Entities**
   - Can you model real-world concepts accurately?
   - Do classes represent entities correctly?
   - **Red Flags**: Missing key entities, incorrect relationships

3. **State Management**
   - Proper state transitions
   - State validation
   - **Red Flags**: Invalid state transitions, no state validation

### Problem-Solving Approach

1. **Edge Case Handling**
   - Different vehicle types
   - Full parking lot scenarios
   - Multiple floors
   - **Red Flags**: Ignoring edge cases, incomplete solutions

2. **Efficiency Considerations**
   - Fast spot finding algorithms
   - Efficient occupancy tracking
   - **Red Flags**: O(n) searches, inefficient data structures

3. **Extensibility**
   - Can design handle new vehicle types?
   - Easy to add new features?
   - **Red Flags**: Hard-coded logic, not extensible

### Code Quality

1. **Clean Code**
   - Readable, maintainable code
   - Proper naming conventions
   - **Red Flags**: Unclear code, poor naming

2. **Error Handling**
   - Proper validation
   - Meaningful error messages
   - **Red Flags**: No validation, unclear errors

### Meta-Specific Focus

1. **OOP Principles**
   - SOLID principles application
   - Design patterns usage
   - **Key**: Show strong OOP fundamentals

2. **Practical Design**
   - Real-world constraints consideration
   - Scalability thinking
   - **Key**: Balance correctness with efficiency

## Summary

### Key Takeaways

1. **Class Hierarchy**: Vehicle, ParkingSpot, Floor, ParkingLot
2. **State Management**: Spot states (available, occupied, maintenance)
3. **Vehicle Types**: Motorcycle, Car, Truck with different spot requirements
4. **Efficient Tracking**: Indexing for fast spot finding
5. **Edge Cases**: Different vehicle types, multiple floors, maintenance

### Common Interview Questions

1. **What classes would you create?**
   - Vehicle, ParkingSpot, Floor, ParkingLot
   - Enums for VehicleType, SpotType, SpotStatus

2. **How to handle different vehicle types?**
   - Compatibility rules (vehicle can park in same or larger spots)
   - Preferred spot type matching
   - Fallback to larger spots

3. **How would you track occupancy efficiently?**
   - Maintain availability index by spot type
   - Update index on park/unpark
   - O(1) availability checks

### Design Principles

1. **Encapsulation**: Each class manages its own state
2. **Separation of Concerns**: Clear responsibilities
3. **Extensibility**: Easy to add new vehicle/spot types
4. **Efficiency**: Fast spot finding with indexing
5. **Correctness**: Proper state management

Understanding parking lot design is crucial for Meta interviews focusing on:
- Object-oriented design
- State management
- Class hierarchy
- Edge case handling
- Efficient algorithms

