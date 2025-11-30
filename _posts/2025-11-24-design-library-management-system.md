---
layout: post
title: "Design a Library Management System - System Design Interview"
date: 2025-11-24
categories: [System Design, Interview Example, Relational Modeling, Object-Oriented Design, Inventory Management]
excerpt: "A comprehensive guide to designing a library management system focusing on relational modeling, object-oriented design, and inventory management. Interview question checking ability to design CRUD-heavy systems with realistic constraints."
---

## Introduction

Designing a library management system is a system design interview question that tests your ability to model complex relationships, handle inventory management, and design CRUD operations. This question focuses on:

- **Relational modeling**: Books, members, loans, reservations
- **Object-oriented design**: Class hierarchy and relationships
- **Inventory management**: Tracking availability, preventing double-booking
- **Business rules**: Overdue handling, renewals, reservations

This guide covers the complete design of a library management system with proper data modeling, state management, and business logic.

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Requirements](#requirements)
3. [Data Modeling](#data-modeling)
4. [Class Design](#class-design)
5. [Core Operations](#core-operations)
6. [Business Rules](#business-rules)
7. [Preventing Double-Booking](#preventing-double-booking)
8. [Implementation](#implementation)
9. [Summary](#summary)

## Problem Statement

**Design a library management system that:**

1. **Manages books** (catalog, copies, availability)
2. **Manages members** (registration, borrowing history)
3. **Handles loans** (checkout, return, renewal)
4. **Manages reservations** (hold requests, notifications)
5. **Tracks overdue books** and calculates fines
6. **Prevents double-booking** (same copy to multiple members)
7. **Supports renewals** with constraints

**Scale Requirements:**
- Support 10K-1M books
- Support 1K-100K members
- Handle concurrent operations
- Fast availability checks

## Requirements

### Functional Requirements

1. **Book Management**: Add books, manage copies
2. **Member Management**: Register members, track history
3. **Checkout**: Loan book to member
4. **Return**: Return book, calculate fines
5. **Renewal**: Renew loan if allowed
6. **Reservation**: Reserve book when unavailable
7. **Overdue Tracking**: Track and notify overdue books

### Non-Functional Requirements

**Consistency:**
- No double-booking
- Accurate availability
- Correct fine calculation

**Performance:**
- Fast availability checks
- Efficient search
- Quick loan processing

## Data Modeling

### Database Schema

```sql
CREATE TABLE books (
    book_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    isbn VARCHAR(20) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(100) NOT NULL,
    publication_year INT,
    category VARCHAR(50),
    total_copies INT DEFAULT 1,
    available_copies INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_isbn (isbn),
    INDEX idx_title (title),
    INDEX idx_author (author)
);

CREATE TABLE book_copies (
    copy_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    book_id BIGINT NOT NULL,
    copy_number INT NOT NULL,
    status VARCHAR(20) DEFAULT 'available',  -- available, checked_out, reserved, maintenance
    location VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_book_copy (book_id, copy_number),
    INDEX idx_book_id (book_id),
    INDEX idx_status (status),
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);

CREATE TABLE members (
    member_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    member_number VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    membership_type VARCHAR(20) DEFAULT 'regular',
    max_loans INT DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_member_number (member_number),
    INDEX idx_email (email)
);

CREATE TABLE loans (
    loan_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    member_id BIGINT NOT NULL,
    copy_id BIGINT NOT NULL,
    book_id BIGINT NOT NULL,
    checkout_date DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE NULL,
    status VARCHAR(20) DEFAULT 'active',  -- active, returned, overdue
    renewal_count INT DEFAULT 0,
    fine_amount DECIMAL(10, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_member_id (member_id),
    INDEX idx_copy_id (copy_id),
    INDEX idx_due_date (due_date),
    INDEX idx_status (status),
    FOREIGN KEY (member_id) REFERENCES members(member_id),
    FOREIGN KEY (copy_id) REFERENCES book_copies(copy_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);

CREATE TABLE reservations (
    reservation_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    member_id BIGINT NOT NULL,
    book_id BIGINT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, fulfilled, cancelled
    reserved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notified_at TIMESTAMP NULL,
    fulfilled_at TIMESTAMP NULL,
    INDEX idx_member_id (member_id),
    INDEX idx_book_id (book_id),
    INDEX idx_status (status),
    FOREIGN KEY (member_id) REFERENCES members(member_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);
```

### Data Model Classes

```python
from enum import Enum
from datetime import datetime, date, timedelta
from typing import Optional, List
from dataclasses import dataclass

class CopyStatus(Enum):
    AVAILABLE = "available"
    CHECKED_OUT = "checked_out"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"

class LoanStatus(Enum):
    ACTIVE = "active"
    RETURNED = "returned"
    OVERDUE = "overdue"

class ReservationStatus(Enum):
    PENDING = "pending"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"

@dataclass
class Book:
    book_id: Optional[int]
    isbn: str
    title: str
    author: str
    publication_year: Optional[int]
    category: Optional[str]
    total_copies: int
    available_copies: int

@dataclass
class BookCopy:
    copy_id: Optional[int]
    book_id: int
    copy_number: int
    status: CopyStatus
    location: Optional[str]

@dataclass
class Member:
    member_id: Optional[int]
    member_number: str
    name: str
    email: str
    phone: Optional[str]
    membership_type: str
    max_loans: int

@dataclass
class Loan:
    loan_id: Optional[int]
    member_id: int
    copy_id: int
    book_id: int
    checkout_date: date
    due_date: date
    return_date: Optional[date]
    status: LoanStatus
    renewal_count: int
    fine_amount: float

@dataclass
class Reservation:
    reservation_id: Optional[int]
    member_id: int
    book_id: int
    status: ReservationStatus
    reserved_at: datetime
    notified_at: Optional[datetime]
    fulfilled_at: Optional[datetime]
```

## Class Design

### Library Management System

```python
class LibraryManagementSystem:
    def __init__(self, db):
        self.db = db
        self.loan_duration_days = 14
        self.max_renewals = 2
        self.fine_per_day = 0.50
        self.max_loans_per_member = 5
    
    def add_book(self, isbn: str, title: str, author: str, 
                 num_copies: int = 1, **kwargs) -> Book:
        """Add new book to library."""
        book = Book(
            book_id=None,
            isbn=isbn,
            title=title,
            author=author,
            publication_year=kwargs.get('publication_year'),
            category=kwargs.get('category'),
            total_copies=num_copies,
            available_copies=num_copies
        )
        
        book = self.db.create_book(book)
        
        # Create copies
        for i in range(1, num_copies + 1):
            copy = BookCopy(
                copy_id=None,
                book_id=book.book_id,
                copy_number=i,
                status=CopyStatus.AVAILABLE,
                location=kwargs.get('location')
            )
            self.db.create_copy(copy)
        
        return book
    
    def register_member(self, name: str, email: str, 
                        member_number: str = None, **kwargs) -> Member:
        """Register new member."""
        if not member_number:
            member_number = self._generate_member_number()
        
        member = Member(
            member_id=None,
            member_number=member_number,
            name=name,
            email=email,
            phone=kwargs.get('phone'),
            membership_type=kwargs.get('membership_type', 'regular'),
            max_loans=self.max_loans_per_member
        )
        
        return self.db.create_member(member)
    
    def checkout_book(self, member_id: int, book_id: int) -> Optional[Loan]:
        """Checkout book to member."""
        # Validate member
        member = self.db.get_member(member_id)
        if not member:
            raise ValueError("Member not found")
        
        # Check member's current loans
        active_loans = self.db.get_active_loans(member_id)
        if len(active_loans) >= member.max_loans:
            raise ValueError(f"Member has reached max loans limit ({member.max_loans})")
        
        # Find available copy
        copy = self._find_available_copy(book_id)
        if not copy:
            raise ValueError("No available copies")
        
        # Create loan
        checkout_date = date.today()
        due_date = checkout_date + timedelta(days=self.loan_duration_days)
        
        loan = Loan(
            loan_id=None,
            member_id=member_id,
            copy_id=copy.copy_id,
            book_id=book_id,
            checkout_date=checkout_date,
            due_date=due_date,
            return_date=None,
            status=LoanStatus.ACTIVE,
            renewal_count=0,
            fine_amount=0.00
        )
        
        # Update copy status
        copy.status = CopyStatus.CHECKED_OUT
        self.db.update_copy(copy)
        
        # Update book availability
        book = self.db.get_book(book_id)
        book.available_copies -= 1
        self.db.update_book(book)
        
        # Save loan
        loan = self.db.create_loan(loan)
        
        return loan
    
    def return_book(self, loan_id: int) -> dict:
        """Return book and calculate fine."""
        loan = self.db.get_loan(loan_id)
        if not loan or loan.status != LoanStatus.ACTIVE:
            raise ValueError("Invalid loan")
        
        return_date = date.today()
        loan.return_date = return_date
        loan.status = LoanStatus.RETURNED
        
        # Calculate fine if overdue
        fine = 0.00
        if return_date > loan.due_date:
            days_overdue = (return_date - loan.due_date).days
            fine = days_overdue * self.fine_per_day
            loan.fine_amount = fine
        
        # Update copy status
        copy = self.db.get_copy(loan.copy_id)
        copy.status = CopyStatus.AVAILABLE
        self.db.update_copy(copy)
        
        # Update book availability
        book = self.db.get_book(loan.book_id)
        book.available_copies += 1
        self.db.update_book(book)
        
        # Check for pending reservations
        self._fulfill_reservation_if_available(loan.book_id)
        
        # Update loan
        self.db.update_loan(loan)
        
        return {
            'success': True,
            'fine': fine,
            'days_overdue': (return_date - loan.due_date).days if return_date > loan.due_date else 0
        }
    
    def renew_loan(self, loan_id: int) -> bool:
        """Renew loan if allowed."""
        loan = self.db.get_loan(loan_id)
        if not loan or loan.status != LoanStatus.ACTIVE:
            return False
        
        # Check renewal limit
        if loan.renewal_count >= self.max_renewals:
            return False
        
        # Check if book is reserved
        if self._has_pending_reservations(loan.book_id):
            return False
        
        # Renew loan
        loan.due_date = loan.due_date + timedelta(days=self.loan_duration_days)
        loan.renewal_count += 1
        
        self.db.update_loan(loan)
        return True
    
    def reserve_book(self, member_id: int, book_id: int) -> Reservation:
        """Reserve book when unavailable."""
        # Check if book exists
        book = self.db.get_book(book_id)
        if not book:
            raise ValueError("Book not found")
        
        # Check if already reserved by this member
        existing = self.db.get_pending_reservation(member_id, book_id)
        if existing:
            raise ValueError("Already reserved by this member")
        
        # Create reservation
        reservation = Reservation(
            reservation_id=None,
            member_id=member_id,
            book_id=book_id,
            status=ReservationStatus.PENDING,
            reserved_at=datetime.now(),
            notified_at=None,
            fulfilled_at=None
        )
        
        return self.db.create_reservation(reservation)
    
    def _find_available_copy(self, book_id: int) -> Optional[BookCopy]:
        """Find available copy of book."""
        copies = self.db.get_copies_by_book(book_id)
        for copy in copies:
            if copy.status == CopyStatus.AVAILABLE:
                return copy
        return None
    
    def _fulfill_reservation_if_available(self, book_id: int):
        """Fulfill oldest reservation if copy available."""
        # Get oldest pending reservation
        reservation = self.db.get_oldest_pending_reservation(book_id)
        if not reservation:
            return
        
        # Check if copy available
        copy = self._find_available_copy(book_id)
        if copy:
            # Mark copy as reserved
            copy.status = CopyStatus.RESERVED
            self.db.update_copy(copy)
            
            # Update reservation
            reservation.status = ReservationStatus.FULFILLED
            reservation.fulfilled_at = datetime.now()
            self.db.update_reservation(reservation)
            
            # Notify member (async)
            self._notify_member_reservation_ready(reservation.member_id, book_id)
    
    def _has_pending_reservations(self, book_id: int) -> bool:
        """Check if book has pending reservations."""
        reservations = self.db.get_pending_reservations(book_id)
        return len(reservations) > 0
    
    def _notify_member_reservation_ready(self, member_id: int, book_id: int):
        """Notify member that reserved book is available."""
        # Implementation: Send email/notification
        pass
    
    def _generate_member_number(self) -> str:
        """Generate unique member number."""
        # Implementation: Generate unique number
        import random
        return f"M{random.randint(100000, 999999)}"
```

## Preventing Double-Booking

### Database-Level Constraints

```sql
-- Ensure copy can only be checked out once
CREATE UNIQUE INDEX idx_active_loan_copy ON loans(copy_id) 
WHERE status = 'active';

-- Ensure member doesn't exceed max loans
-- (Application-level check with transaction)
```

### Application-Level Locking

```python
class LibraryManagementSystem:
    def __init__(self, db):
        # ... existing code ...
        self.copy_locks = {}  # copy_id -> Lock
        self.locks_lock = threading.Lock()
    
    def _get_copy_lock(self, copy_id: int) -> threading.Lock:
        """Get or create lock for copy."""
        with self.locks_lock:
            if copy_id not in self.copy_locks:
                self.copy_locks[copy_id] = threading.Lock()
            return self.copy_locks[copy_id]
    
    def checkout_book(self, member_id: int, book_id: int) -> Optional[Loan]:
        """Thread-safe checkout."""
        # Find available copy
        copy = self._find_available_copy(book_id)
        if not copy:
            raise ValueError("No available copies")
        
        # Lock copy to prevent double-booking
        lock = self._get_copy_lock(copy.copy_id)
        
        with lock:
            # Re-check copy status (double-check pattern)
            copy = self.db.get_copy(copy.copy_id)
            if copy.status != CopyStatus.AVAILABLE:
                raise ValueError("Copy no longer available")
            
            # Proceed with checkout
            # ... (rest of checkout logic)
```

## Business Rules

### Overdue Handling

```python
def check_overdue_loans(self):
    """Check and mark overdue loans."""
    today = date.today()
    active_loans = self.db.get_active_loans()
    
    for loan in active_loans:
        if loan.due_date < today and loan.status == LoanStatus.ACTIVE:
            loan.status = LoanStatus.OVERDUE
            self.db.update_loan(loan)
            
            # Calculate fine
            days_overdue = (today - loan.due_date).days
            fine = days_overdue * self.fine_per_day
            loan.fine_amount = fine
            self.db.update_loan(loan)
            
            # Notify member
            self._notify_overdue(loan.member_id, loan)
```

## What Interviewers Look For

### Relational Modeling Skills

1. **Database Schema Design**
   - Proper normalization
   - Correct relationships (one-to-many, many-to-many)
   - Appropriate constraints
   - **Red Flags**: Poor normalization, missing constraints

2. **Entity Relationships**
   - Can you model complex relationships?
   - Do you understand foreign keys?
   - **Red Flags**: Incorrect relationships, missing foreign keys

### Business Logic Implementation

1. **Rule Enforcement**
   - Overdue handling
   - Renewal limits
   - Reservation logic
   - **Red Flags**: Missing business rules, incorrect logic

2. **Preventing Double-Booking**
   - Database constraints
   - Application-level checks
   - **Red Flags**: No prevention mechanism, race conditions

### Problem-Solving Approach

1. **Edge Cases**
   - Overdue books
   - Multiple reservations
   - Book availability
   - **Red Flags**: Ignoring edge cases, incomplete handling

2. **Inventory Management**
   - Accurate copy tracking
   - Availability updates
   - **Red Flags**: Inconsistent inventory, no updates

### Code Quality

1. **Data Integrity**
   - Consistent state
   - Proper transactions
   - **Red Flags**: Inconsistent data, no transactions

2. **Error Handling**
   - Validation of operations
   - Meaningful errors
   - **Red Flags**: No validation, unclear errors

### Interview Focus

1. **CRUD Operations Mastery**
   - Complete CRUD implementation
   - Efficient queries
   - **Key**: Show strong database skills

2. **Business Logic Understanding**
   - Real-world constraints
   - Practical implementation
   - **Key**: Balance technical with practical

## Summary

### Key Takeaways

1. **Relational Modeling**: Books, copies, members, loans, reservations
2. **State Management**: Copy status, loan status, reservation status
3. **Preventing Double-Booking**: Database constraints + application locks
4. **Business Rules**: Renewals, overdue, fines, reservations
5. **Inventory Management**: Track available copies, update on checkout/return

### Common Interview Questions

1. **How would you model books, members, loans, and reservations?**
   - Books: ISBN, title, author, copies
   - Members: Member number, contact info, loan limits
   - Loans: Checkout/return dates, status, fines
   - Reservations: Pending/fulfilled status

2. **How to handle overdue books or renewals?**
   - Track due dates, mark overdue
   - Calculate fines per day
   - Limit renewals, check reservations

3. **How would you prevent double-booking of a book?**
   - Database unique constraint on active loans per copy
   - Application-level locking on copy
   - Double-check pattern before checkout

Understanding library management design is crucial for Meta interviews focusing on:
- Relational modeling
- Object-oriented design
- Inventory management
- State management
- Business rules

