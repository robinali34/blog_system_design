---
layout: post
title: "Design a Ticket Booking System (Cinema/Events) - Meta System Design Interview"
date: 2025-11-24
categories: [System Design, Interview Example, Meta, Class Design, State Management, Atomicity]
excerpt: "A comprehensive guide to designing a ticket booking system focusing on class design, state management, handling atomicity locally (like seat reservation), and booking logic. Meta interview question emphasizing consistency and correctness without distributed coordination."
---

## Introduction

Designing a ticket booking system is a Meta interview question that tests your ability to model real-world booking scenarios, handle state management, and ensure atomicity in seat reservations. This question focuses on:

- **Class design**: Shows, seats, bookings, users
- **State management**: Seat states, booking states
- **Atomicity**: Preventing double booking
- **Booking logic**: Seat selection, payment, confirmation

This guide covers the complete design of a ticket booking system with proper state management and atomic operations.

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Requirements](#requirements)
3. [Class Design](#class-design)
4. [State Management](#state-management)
5. [Booking Flow](#booking-flow)
6. [Preventing Double Booking](#preventing-double-booking)
7. [Data Structures for Efficiency](#data-structures-for-efficiency)
8. [Implementation](#implementation)
9. [Summary](#summary)

## Problem Statement

**Design a ticket booking system for cinema/events that:**

1. **Manages shows** (movies, events with time slots)
2. **Manages seats** (rows, numbers, types)
3. **Handles bookings** (seat selection, payment, confirmation)
4. **Prevents double booking** (same seat to multiple users)
5. **Supports seat availability** checks
6. **Handles booking expiration** (timeout for pending bookings)

**Scale Requirements:**
- Support 100-10,000 seats per show
- Handle concurrent bookings
- Fast availability checks: < 10ms
- Ensure no double booking

## Requirements

### Functional Requirements

1. **Show Management**: Create shows, manage schedules
2. **Seat Management**: Define seats, track availability
3. **Book Seats**: Select and book seats
4. **Check Availability**: Check seat availability
5. **Cancel Booking**: Cancel confirmed booking
6. **View Booking**: Get booking details

### Non-Functional Requirements

**Consistency:**
- No double booking
- Atomic seat reservation
- Accurate availability

**Performance:**
- Fast availability checks
- Efficient seat finding
- Quick booking processing

## Class Design

### Core Classes

```python
from enum import Enum
from datetime import datetime, timedelta
from typing import Optional, List, Set
from dataclasses import dataclass

class SeatStatus(Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"  # Temporarily held
    BOOKED = "booked"      # Confirmed booking
    MAINTENANCE = "maintenance"

class BookingStatus(Enum):
    PENDING = "pending"      # Seat reserved, payment pending
    CONFIRMED = "confirmed"  # Payment received
    CANCELLED = "cancelled"
    EXPIRED = "expired"

@dataclass
class Seat:
    seat_id: int
    row: str
    number: int
    seat_type: str  # regular, premium, vip
    status: SeatStatus
    show_id: Optional[int] = None
    
    def __hash__(self):
        return hash((self.seat_id, self.show_id))
    
    def __eq__(self, other):
        return self.seat_id == other.seat_id and self.show_id == other.show_id

@dataclass
class Show:
    show_id: Optional[int]
    name: str
    show_time: datetime
    venue: str
    total_seats: int
    available_seats: int
    seats: List[Seat]

@dataclass
class Booking:
    booking_id: Optional[int]
    user_id: int
    show_id: int
    seat_ids: List[int]
    status: BookingStatus
    reserved_at: datetime
    expires_at: Optional[datetime]
    confirmed_at: Optional[datetime]
    total_amount: float
    payment_id: Optional[str] = None

class TicketBookingSystem:
    def __init__(self):
        self.shows: dict = {}  # show_id -> Show
        self.bookings: dict = {}  # booking_id -> Booking
        self.seat_locks: dict = {}  # (show_id, seat_id) -> Lock
        self.reservation_timeout = timedelta(minutes=15)
    
    def create_show(self, name: str, show_time: datetime, venue: str,
                   rows: List[str], seats_per_row: int) -> Show:
        """Create new show with seats."""
        show_id = len(self.shows) + 1
        seats = []
        seat_id = 1
        
        for row in rows:
            for seat_num in range(1, seats_per_row + 1):
                seat = Seat(
                    seat_id=seat_id,
                    row=row,
                    number=seat_num,
                    seat_type='regular',
                    status=SeatStatus.AVAILABLE,
                    show_id=show_id
                )
                seats.append(seat)
                seat_id += 1
        
        show = Show(
            show_id=show_id,
            name=name,
            show_time=show_time,
            venue=venue,
            total_seats=len(seats),
            available_seats=len(seats),
            seats=seats
        )
        
        self.shows[show_id] = show
        return show
    
    def check_availability(self, show_id: int, seat_ids: Optional[List[int]] = None) -> dict:
        """Check seat availability."""
        if show_id not in self.shows:
            return {'available': False, 'message': 'Show not found'}
        
        show = self.shows[show_id]
        
        if seat_ids:
            # Check specific seats
            available = []
            unavailable = []
            for seat_id in seat_ids:
                seat = next((s for s in show.seats if s.seat_id == seat_id), None)
                if seat and seat.status == SeatStatus.AVAILABLE:
                    available.append(seat_id)
                else:
                    unavailable.append(seat_id)
            
            return {
                'available': len(unavailable) == 0,
                'available_seats': available,
                'unavailable_seats': unavailable
            }
        else:
            # Return all available seats
            available_seats = [s.seat_id for s in show.seats if s.status == SeatStatus.AVAILABLE]
            return {
                'available': True,
                'available_seats': available_seats,
                'total_available': len(available_seats)
            }
    
    def reserve_seats(self, user_id: int, show_id: int, seat_ids: List[int]) -> Optional[Booking]:
        """Reserve seats (temporary hold)."""
        if show_id not in self.shows:
            return None
        
        show = self.shows[show_id]
        
        # Lock seats in sorted order to prevent deadlock
        seat_keys = sorted([(show_id, seat_id) for seat_id in seat_ids])
        locks = [self._get_seat_lock(key) for key in seat_keys]
        
        try:
            # Acquire all locks
            for lock in locks:
                lock.acquire()
            
            # Check all seats are available
            unavailable = []
            for seat_id in seat_ids:
                seat = next((s for s in show.seats if s.seat_id == seat_id), None)
                if not seat or seat.status != SeatStatus.AVAILABLE:
                    unavailable.append(seat_id)
            
            if unavailable:
                return None
            
            # Reserve seats
            for seat_id in seat_ids:
                seat = next((s for s in show.seats if s.seat_id == seat_id), None)
                seat.status = SeatStatus.RESERVED
            
            # Create booking
            booking = Booking(
                booking_id=len(self.bookings) + 1,
                user_id=user_id,
                show_id=show_id,
                seat_ids=seat_ids,
                status=BookingStatus.PENDING,
                reserved_at=datetime.now(),
                expires_at=datetime.now() + self.reservation_timeout,
                confirmed_at=None,
                total_amount=self._calculate_amount(show, seat_ids)
            )
            
            self.bookings[booking.booking_id] = booking
            show.available_seats -= len(seat_ids)
            
            return booking
            
        finally:
            # Release all locks
            for lock in locks:
                lock.release()
    
    def confirm_booking(self, booking_id: int, payment_id: str) -> bool:
        """Confirm booking after payment."""
        if booking_id not in self.bookings:
            return False
        
        booking = self.bookings[booking_id]
        
        if booking.status != BookingStatus.PENDING:
            return False
        
        # Check if expired
        if booking.expires_at and datetime.now() > booking.expires_at:
            self._expire_booking(booking_id)
            return False
        
        # Lock seats
        seat_keys = sorted([(booking.show_id, seat_id) for seat_id in booking.seat_ids])
        locks = [self._get_seat_lock(key) for key in seat_keys]
        
        try:
            for lock in locks:
                lock.acquire()
            
            # Confirm booking
            booking.status = BookingStatus.CONFIRMED
            booking.confirmed_at = datetime.now()
            booking.payment_id = payment_id
            
            # Update seat status
            show = self.shows[booking.show_id]
            for seat_id in booking.seat_ids:
                seat = next((s for s in show.seats if s.seat_id == seat_id), None)
                if seat:
                    seat.status = SeatStatus.BOOKED
            
            return True
            
        finally:
            for lock in locks:
                lock.release()
    
    def cancel_booking(self, booking_id: int) -> bool:
        """Cancel booking and release seats."""
        if booking_id not in self.bookings:
            return False
        
        booking = self.bookings[booking_id]
        
        if booking.status == BookingStatus.CANCELLED:
            return False
        
        # Lock seats
        seat_keys = sorted([(booking.show_id, seat_id) for seat_id in booking.seat_ids])
        locks = [self._get_seat_lock(key) for key in seat_keys]
        
        try:
            for lock in locks:
                lock.acquire()
            
            # Cancel booking
            booking.status = BookingStatus.CANCELLED
            
            # Release seats
            show = self.shows[booking.show_id]
            for seat_id in booking.seat_ids:
                seat = next((s for s in show.seats if s.seat_id == seat_id), None)
                if seat:
                    seat.status = SeatStatus.AVAILABLE
            
            show.available_seats += len(booking.seat_ids)
            
            return True
            
        finally:
            for lock in locks:
                lock.release()
    
    def _expire_booking(self, booking_id: int):
        """Expire booking and release seats."""
        booking = self.bookings[booking_id]
        booking.status = BookingStatus.EXPIRED
        
        # Release seats
        show = self.shows[booking.show_id]
        for seat_id in booking.seat_ids:
            seat = next((s for s in show.seats if s.seat_id == seat_id), None)
            if seat:
                seat.status = SeatStatus.AVAILABLE
        
        show.available_seats += len(booking.seat_ids)
    
    def _calculate_amount(self, show: Show, seat_ids: List[int]) -> float:
        """Calculate booking amount."""
        # Simple calculation: $10 per seat
        return len(seat_ids) * 10.0
    
    def _get_seat_lock(self, key: tuple) -> threading.Lock:
        """Get or create lock for seat."""
        if key not in self.seat_locks:
            self.seat_locks[key] = threading.Lock()
        return self.seat_locks[key]
```

## Preventing Double Booking

### Strategy 1: Lock-Based (Recommended)

```python
def reserve_seats(self, user_id: int, show_id: int, seat_ids: List[int]) -> Optional[Booking]:
    """Thread-safe seat reservation."""
    # Sort seat keys to prevent deadlock
    seat_keys = sorted([(show_id, seat_id) for seat_id in seat_ids])
    locks = [self._get_seat_lock(key) for key in seat_keys]
    
    try:
        # Acquire all locks (in consistent order)
        for lock in locks:
            lock.acquire()
        
        # Double-check availability
        show = self.shows[show_id]
        for seat_id in seat_ids:
            seat = next((s for s in show.seats if s.seat_id == seat_id), None)
            if not seat or seat.status != SeatStatus.AVAILABLE:
                return None  # No longer available
        
        # Reserve seats
        # ... (reservation logic)
        
    finally:
        # Always release locks
        for lock in locks:
            lock.release()
```

### Strategy 2: Database Constraints

```sql
-- Ensure seat can only be booked once per show
CREATE UNIQUE INDEX idx_booking_seat_show 
ON bookings(show_id, seat_id) 
WHERE status IN ('pending', 'confirmed');
```

## Data Structures for Efficiency

### Seat Availability Index

```python
class TicketBookingSystem:
    def __init__(self):
        # ... existing code ...
        self.availability_index = {}  # show_id -> Set[seat_id]
        self._build_index()
    
    def _build_index(self):
        """Build availability index."""
        for show_id, show in self.shows.items():
            available = {s.seat_id for s in show.seats if s.status == SeatStatus.AVAILABLE}
            self.availability_index[show_id] = available
    
    def check_availability_fast(self, show_id: int) -> int:
        """Fast availability check using index."""
        return len(self.availability_index.get(show_id, set()))
    
    def reserve_seats(self, user_id: int, show_id: int, seat_ids: List[int]) -> Optional[Booking]:
        """Reserve with index update."""
        # ... reservation logic ...
        
        # Update index
        available = self.availability_index[show_id]
        for seat_id in seat_ids:
            available.discard(seat_id)
        
        return booking
```

## What Interviewers Look For

### Class Design Skills

1. **Entity Modeling**
   - Proper class structure (Show, Seat, Booking)
   - Clear relationships
   - Appropriate state management
   - **Red Flags**: Poor class design, unclear relationships

2. **State Management**
   - Seat states (available, reserved, booked)
   - Booking states (pending, confirmed, cancelled)
   - **Red Flags**: Missing states, invalid transitions

### Atomicity & Consistency

1. **Preventing Double Booking**
   - Lock-based approach
   - Database constraints
   - Double-check pattern
   - **Red Flags**: No prevention, race conditions

2. **Transaction Handling**
   - Atomic seat reservation
   - Rollback on failure
   - **Red Flags**: Partial updates, no rollback

### Problem-Solving Approach

1. **Efficient Data Structures**
   - Fast availability checks
   - Efficient seat finding
   - **Red Flags**: O(n) searches, inefficient structures

2. **Edge Cases**
   - Concurrent bookings
   - Expired reservations
   - Full shows
   - **Red Flags**: Ignoring concurrency, no expiration handling

### Code Quality

1. **Thread Safety**
   - Proper locking
   - Deadlock prevention
   - **Red Flags**: No locking, deadlock-prone

2. **Correctness**
   - No double booking
   - Accurate availability
   - **Red Flags**: Double booking possible, wrong counts

### Meta-Specific Focus

1. **Local Consistency**
   - Emphasis on correctness
   - No distributed coordination needed
   - **Key**: Show understanding of local atomicity

2. **Practical Implementation**
   - Real-world booking scenarios
   - Efficient algorithms
   - **Key**: Balance correctness with efficiency

## Summary

### Key Takeaways

1. **Class Design**: Show, Seat, Booking with proper relationships
2. **State Management**: Seat status, booking status
3. **Atomicity**: Lock-based seat reservation
4. **Double Booking Prevention**: Locks + double-check pattern
5. **Efficiency**: Indexing for fast availability checks

### Common Interview Questions

1. **How would you model seats and shows?**
   - Show: ID, name, time, venue, seats
   - Seat: ID, row, number, type, status

2. **How would you prevent double booking?**
   - Lock seats in sorted order
   - Double-check availability after lock
   - Database constraints

3. **What data structures would make seat availability checks efficient?**
   - Set-based index: show_id -> Set[available_seat_ids]
   - O(1) availability check
   - Update on reserve/release

Understanding ticket booking design is crucial for Meta interviews focusing on:
- Class design
- State management
- Atomicity
- Preventing race conditions
- Efficient data structures

