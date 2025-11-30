---
layout: post
title: "Design an ATM Machine / Banking System - System Design Interview"
date: 2025-11-24
categories: [System Design, Interview Example, State Management, Transactions, Concurrency]
excerpt: "A comprehensive guide to designing an ATM machine and banking system focusing on state management, transactions, handling concurrency locally, and error handling. Interview question emphasizing correct modeling and ensuring data consistency."
---

## Introduction

Designing an ATM machine and banking system is a system design interview question that tests your ability to model financial transactions, handle state management, ensure data consistency, and manage concurrency. This question focuses on:

- **State management**: Account states, transaction states
- **Transactions**: Atomic operations, rollback
- **Concurrency**: Handling simultaneous operations
- **Error handling**: Overdraft, failed transactions
- **Extensibility**: Easy to add new features

This guide covers the complete design of an ATM/banking system with proper transaction handling, state management, and error handling.

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Requirements](#requirements)
3. [Data Modeling](#data-modeling)
4. [State Management](#state-management)
5. [Transaction Handling](#transaction-handling)
6. [Core Operations](#core-operations)
7. [Error Handling](#error-handling)
8. [Concurrency Control](#concurrency-control)
9. [Implementation](#implementation)
10. [Summary](#summary)

## Problem Statement

**Design an ATM machine / banking system that:**

1. **Manages accounts** with balances
2. **Handles transactions** (deposit, withdrawal, transfer)
3. **Ensures atomicity** (all-or-nothing operations)
4. **Handles overdraft** and insufficient funds
5. **Tracks transaction history**
6. **Supports multiple operations** (balance check, deposit, withdrawal, transfer)
7. **Handles concurrency** (simultaneous operations)

**Scale Requirements:**
- Support millions of accounts
- Handle concurrent transactions
- Fast operations: < 100ms
- Ensure data consistency

## Requirements

### Functional Requirements

1. **Create Account**: Create new bank account
2. **Check Balance**: Get account balance
3. **Deposit**: Add money to account
4. **Withdraw**: Remove money from account
5. **Transfer**: Transfer money between accounts
6. **Transaction History**: Get account transaction history
7. **Overdraft Protection**: Handle overdraft scenarios

### Non-Functional Requirements

**Consistency:**
- Atomic transactions
- No data corruption
- Balance always correct

**Concurrency:**
- Handle simultaneous operations
- Prevent race conditions
- Thread-safe operations

**Reliability:**
- Handle failures gracefully
- Rollback on errors
- Transaction logging

## Data Modeling

### Database Schema

```sql
CREATE TABLE accounts (
    account_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    account_number VARCHAR(20) UNIQUE NOT NULL,
    account_holder_name VARCHAR(100) NOT NULL,
    balance DECIMAL(15, 2) DEFAULT 0.00,
    account_type VARCHAR(20) DEFAULT 'checking',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_account_number (account_number)
);

CREATE TABLE transactions (
    transaction_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    account_id BIGINT NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,  -- deposit, withdrawal, transfer
    amount DECIMAL(15, 2) NOT NULL,
    balance_before DECIMAL(15, 2) NOT NULL,
    balance_after DECIMAL(15, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, completed, failed, rolled_back
    related_account_id BIGINT NULL,  -- for transfers
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_account_id (account_id),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);
```

### Data Model Classes

```python
from enum import Enum
from datetime import datetime
from decimal import Decimal
from typing import Optional
from dataclasses import dataclass

class TransactionType(Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"

class TransactionStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

@dataclass
class Account:
    account_id: Optional[int]
    account_number: str
    account_holder_name: str
    balance: Decimal
    account_type: str
    created_at: datetime
    updated_at: datetime
    
    def has_sufficient_funds(self, amount: Decimal) -> bool:
        """Check if account has sufficient funds."""
        return self.balance >= amount

@dataclass
class Transaction:
    transaction_id: Optional[int]
    account_id: int
    transaction_type: TransactionType
    amount: Decimal
    balance_before: Decimal
    balance_after: Decimal
    status: TransactionStatus
    related_account_id: Optional[int]
    description: Optional[str]
    created_at: datetime
```

## State Management

### Account State

```python
class AccountState:
    def __init__(self, account: Account):
        self.account = account
        self.lock = threading.Lock()
        self.pending_transactions = []  # Transactions in progress
    
    def begin_transaction(self, transaction: Transaction):
        """Begin transaction (lock account)."""
        self.lock.acquire()
        self.pending_transactions.append(transaction)
    
    def commit_transaction(self, transaction: Transaction):
        """Commit transaction."""
        if transaction.status == TransactionStatus.COMPLETED:
            self.account.balance = transaction.balance_after
            self.account.updated_at = datetime.now()
        self.pending_transactions.remove(transaction)
        self.lock.release()
    
    def rollback_transaction(self, transaction: Transaction):
        """Rollback transaction."""
        transaction.status = TransactionStatus.ROLLED_BACK
        self.pending_transactions.remove(transaction)
        self.lock.release()
```

## Transaction Handling

### Transaction Manager

```python
class TransactionManager:
    def __init__(self, db):
        self.db = db
        self.active_transactions = {}  # transaction_id -> Transaction
    
    def execute_transaction(self, transaction: Transaction) -> bool:
        """Execute transaction atomically."""
        try:
            # Begin transaction
            account = self.db.get_account(transaction.account_id)
            if not account:
                return False
            
            # Validate transaction
            if not self._validate_transaction(transaction, account):
                return False
            
            # Execute based on type
            if transaction.transaction_type == TransactionType.DEPOSIT:
                return self._execute_deposit(transaction, account)
            elif transaction.transaction_type == TransactionType.WITHDRAWAL:
                return self._execute_withdrawal(transaction, account)
            elif transaction.transaction_type == TransactionType.TRANSFER:
                return self._execute_transfer(transaction, account)
            
            return False
        except Exception as e:
            # Rollback on error
            self._rollback_transaction(transaction)
            return False
    
    def _validate_transaction(self, transaction: Transaction, account: Account) -> bool:
        """Validate transaction before execution."""
        if transaction.amount <= 0:
            return False
        
        if transaction.transaction_type == TransactionType.WITHDRAWAL:
            if not account.has_sufficient_funds(transaction.amount):
                return False
        
        return True
    
    def _execute_deposit(self, transaction: Transaction, account: Account) -> bool:
        """Execute deposit transaction."""
        transaction.balance_before = account.balance
        transaction.balance_after = account.balance + transaction.amount
        transaction.status = TransactionStatus.COMPLETED
        
        # Update account
        account.balance = transaction.balance_after
        account.updated_at = datetime.now()
        
        # Save to database
        self.db.update_account(account)
        self.db.save_transaction(transaction)
        
        return True
    
    def _execute_withdrawal(self, transaction: Transaction, account: Account) -> bool:
        """Execute withdrawal transaction."""
        if not account.has_sufficient_funds(transaction.amount):
            transaction.status = TransactionStatus.FAILED
            self.db.save_transaction(transaction)
            return False
        
        transaction.balance_before = account.balance
        transaction.balance_after = account.balance - transaction.amount
        transaction.status = TransactionStatus.COMPLETED
        
        # Update account
        account.balance = transaction.balance_after
        account.updated_at = datetime.now()
        
        # Save to database
        self.db.update_account(account)
        self.db.save_transaction(transaction)
        
        return True
    
    def _execute_transfer(self, transaction: Transaction, from_account: Account) -> bool:
        """Execute transfer transaction."""
        if not transaction.related_account_id:
            return False
        
        to_account = self.db.get_account(transaction.related_account_id)
        if not to_account:
            return False
        
        if not from_account.has_sufficient_funds(transaction.amount):
            transaction.status = TransactionStatus.FAILED
            self.db.save_transaction(transaction)
            return False
        
        # Create reverse transaction for recipient
        reverse_transaction = Transaction(
            transaction_id=None,
            account_id=to_account.account_id,
            transaction_type=TransactionType.DEPOSIT,
            amount=transaction.amount,
            balance_before=to_account.balance,
            balance_after=to_account.balance + transaction.amount,
            status=TransactionStatus.PENDING,
            related_account_id=from_account.account_id,
            description=f"Transfer from {from_account.account_number}",
            created_at=datetime.now()
        )
        
        # Execute withdrawal
        transaction.balance_before = from_account.balance
        transaction.balance_after = from_account.balance - transaction.amount
        transaction.status = TransactionStatus.COMPLETED
        
        # Execute deposit
        reverse_transaction.status = TransactionStatus.COMPLETED
        
        # Update accounts
        from_account.balance = transaction.balance_after
        to_account.balance = reverse_transaction.balance_after
        
        # Save to database (atomic)
        self.db.transfer_money(from_account, to_account, transaction, reverse_transaction)
        
        return True
    
    def _rollback_transaction(self, transaction: Transaction):
        """Rollback transaction."""
        transaction.status = TransactionStatus.ROLLED_BACK
        self.db.save_transaction(transaction)
```

## Core Operations

### Banking Service

```python
class BankingService:
    def __init__(self, db, transaction_manager):
        self.db = db
        self.transaction_manager = transaction_manager
        self.account_locks = {}  # account_id -> Lock
        self.locks_lock = threading.Lock()
    
    def create_account(self, account_number: str, account_holder_name: str,
                      initial_balance: Decimal = Decimal('0.00')) -> Account:
        """Create new account."""
        account = Account(
            account_id=None,
            account_number=account_number,
            account_holder_name=account_holder_name,
            balance=initial_balance,
            account_type='checking',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        return self.db.create_account(account)
    
    def check_balance(self, account_id: int) -> Optional[Decimal]:
        """Check account balance."""
        account = self.db.get_account(account_id)
        if not account:
            return None
        return account.balance
    
    def deposit(self, account_id: int, amount: Decimal, description: str = None) -> bool:
        """Deposit money to account."""
        account = self.db.get_account(account_id)
        if not account:
            return False
        
        transaction = Transaction(
            transaction_id=None,
            account_id=account_id,
            transaction_type=TransactionType.DEPOSIT,
            amount=amount,
            balance_before=account.balance,
            balance_after=Decimal('0.00'),  # Will be calculated
            status=TransactionStatus.PENDING,
            related_account_id=None,
            description=description or "Deposit",
            created_at=datetime.now()
        )
        
        return self.transaction_manager.execute_transaction(transaction)
    
    def withdraw(self, account_id: int, amount: Decimal, description: str = None) -> bool:
        """Withdraw money from account."""
        account = self.db.get_account(account_id)
        if not account:
            return False
        
        transaction = Transaction(
            transaction_id=None,
            account_id=account_id,
            transaction_type=TransactionType.WITHDRAWAL,
            amount=amount,
            balance_before=account.balance,
            balance_after=Decimal('0.00'),  # Will be calculated
            status=TransactionStatus.PENDING,
            related_account_id=None,
            description=description or "Withdrawal",
            created_at=datetime.now()
        )
        
        return self.transaction_manager.execute_transaction(transaction)
    
    def transfer(self, from_account_id: int, to_account_id: int,
                 amount: Decimal, description: str = None) -> bool:
        """Transfer money between accounts."""
        from_account = self.db.get_account(from_account_id)
        to_account = self.db.get_account(to_account_id)
        
        if not from_account or not to_account:
            return False
        
        transaction = Transaction(
            transaction_id=None,
            account_id=from_account_id,
            transaction_type=TransactionType.TRANSFER,
            amount=amount,
            balance_before=from_account.balance,
            balance_after=Decimal('0.00'),  # Will be calculated
            status=TransactionStatus.PENDING,
            related_account_id=to_account_id,
            description=description or f"Transfer to {to_account.account_number}",
            created_at=datetime.now()
        )
        
        return self.transaction_manager.execute_transaction(transaction)
    
    def get_transaction_history(self, account_id: int, limit: int = 100) -> List[Transaction]:
        """Get transaction history for account."""
        return self.db.get_transactions(account_id, limit=limit)
```

## Error Handling

### Overdraft Handling

```python
class OverdraftPolicy:
    def __init__(self, allow_overdraft: bool = False, overdraft_limit: Decimal = Decimal('0.00')):
        self.allow_overdraft = allow_overdraft
        self.overdraft_limit = overdraft_limit
    
    def can_withdraw(self, account: Account, amount: Decimal) -> tuple[bool, str]:
        """Check if withdrawal is allowed."""
        if account.balance >= amount:
            return True, "Sufficient funds"
        
        if not self.allow_overdraft:
            return False, "Insufficient funds"
        
        available = account.balance + self.overdraft_limit
        if available >= amount:
            return True, f"Overdraft allowed (available: {available})"
        
        return False, "Exceeds overdraft limit"

class BankingService:
    def __init__(self, db, transaction_manager, overdraft_policy: OverdraftPolicy):
        # ... existing code ...
        self.overdraft_policy = overdraft_policy
    
    def withdraw(self, account_id: int, amount: Decimal, description: str = None) -> dict:
        """Withdraw with overdraft checking."""
        account = self.db.get_account(account_id)
        if not account:
            return {'success': False, 'message': 'Account not found'}
        
        can_withdraw, message = self.overdraft_policy.can_withdraw(account, amount)
        if not can_withdraw:
            return {'success': False, 'message': message}
        
        transaction = Transaction(
            transaction_id=None,
            account_id=account_id,
            transaction_type=TransactionType.WITHDRAWAL,
            amount=amount,
            balance_before=account.balance,
            balance_after=Decimal('0.00'),
            status=TransactionStatus.PENDING,
            related_account_id=None,
            description=description or "Withdrawal",
            created_at=datetime.now()
        )
        
        success = self.transaction_manager.execute_transaction(transaction)
        return {
            'success': success,
            'message': 'Withdrawal successful' if success else 'Withdrawal failed',
            'new_balance': account.balance if success else None
        }
```

## Concurrency Control

### Account-Level Locking

```python
class BankingService:
    def __init__(self, db, transaction_manager):
        # ... existing code ...
        self.account_locks = {}  # account_id -> Lock
        self.locks_lock = threading.Lock()
    
    def _get_account_lock(self, account_id: int) -> threading.Lock:
        """Get or create lock for account."""
        with self.locks_lock:
            if account_id not in self.account_locks:
                self.account_locks[account_id] = threading.Lock()
            return self.account_locks[account_id]
    
    def withdraw(self, account_id: int, amount: Decimal, description: str = None) -> bool:
        """Thread-safe withdrawal."""
        lock = self._get_account_lock(account_id)
        
        with lock:
            account = self.db.get_account(account_id)
            if not account:
                return False
            
            transaction = Transaction(
                transaction_id=None,
                account_id=account_id,
                transaction_type=TransactionType.WITHDRAWAL,
                amount=amount,
                balance_before=account.balance,
                balance_after=Decimal('0.00'),
                status=TransactionStatus.PENDING,
                related_account_id=None,
                description=description or "Withdrawal",
                created_at=datetime.now()
            )
            
            return self.transaction_manager.execute_transaction(transaction)
    
    def transfer(self, from_account_id: int, to_account_id: int,
                 amount: Decimal, description: str = None) -> bool:
        """Thread-safe transfer with deadlock prevention."""
        # Lock accounts in consistent order to prevent deadlock
        first_id = min(from_account_id, to_account_id)
        second_id = max(from_account_id, to_account_id)
        
        first_lock = self._get_account_lock(first_id)
        second_lock = self._get_account_lock(second_id)
        
        with first_lock:
            with second_lock:
                from_account = self.db.get_account(from_account_id)
                to_account = self.db.get_account(to_account_id)
                
                if not from_account or not to_account:
                    return False
                
                transaction = Transaction(
                    transaction_id=None,
                    account_id=from_account_id,
                    transaction_type=TransactionType.TRANSFER,
                    amount=amount,
                    balance_before=from_account.balance,
                    balance_after=Decimal('0.00'),
                    status=TransactionStatus.PENDING,
                    related_account_id=to_account_id,
                    description=description or f"Transfer to {to_account.account_number}",
                    created_at=datetime.now()
                )
                
                return self.transaction_manager.execute_transaction(transaction)
```

## Implementation

### Complete Example

```python
# Initialize
db = Database()
transaction_manager = TransactionManager(db)
overdraft_policy = OverdraftPolicy(allow_overdraft=True, overdraft_limit=Decimal('500.00'))
banking_service = BankingService(db, transaction_manager, overdraft_policy)

# Create account
account = banking_service.create_account("123456789", "John Doe", Decimal('1000.00'))

# Check balance
balance = banking_service.check_balance(account.account_id)
print(f"Balance: {balance}")

# Deposit
banking_service.deposit(account.account_id, Decimal('500.00'), "Salary deposit")

# Withdraw
result = banking_service.withdraw(account.account_id, Decimal('200.00'), "ATM withdrawal")
print(result)

# Transfer
to_account = banking_service.create_account("987654321", "Jane Doe", Decimal('0.00'))
banking_service.transfer(account.account_id, to_account.account_id, Decimal('100.00'))

# Transaction history
history = banking_service.get_transaction_history(account.account_id)
for transaction in history:
    print(f"{transaction.transaction_type.value}: {transaction.amount}")
```

## What Interviewers Look For

### State Management Skills

1. **Transaction State Handling**
   - Proper transaction lifecycle
   - State transitions (pending, completed, failed, rolled_back)
   - **Red Flags**: Missing states, invalid transitions

2. **Account State Consistency**
   - Balance always correct
   - No race conditions
   - **Red Flags**: Inconsistent balances, race conditions

### Concurrency Control

1. **Thread Safety**
   - Proper locking mechanisms
   - Deadlock prevention
   - **Red Flags**: No locking, deadlock-prone code

2. **Atomic Operations**
   - Transactions are atomic
   - All-or-nothing semantics
   - **Red Flags**: Partial updates, inconsistent state

### Problem-Solving Approach

1. **Error Handling**
   - Overdraft scenarios
   - Insufficient funds
   - Failed transactions
   - **Red Flags**: No error handling, unclear failure modes

2. **Extensibility**
   - Easy to add new transaction types
   - Flexible design
   - **Red Flags**: Hard-coded logic, not extensible

3. **Data Consistency**
   - ACID properties understanding
   - Rollback mechanisms
   - **Red Flags**: No rollback, inconsistent data

### Code Quality

1. **Correctness**
   - Correct balance calculations
   - Proper validation
   - **Red Flags**: Calculation errors, no validation

2. **Reliability**
   - Handle failures gracefully
   - No data loss
   - **Red Flags**: Data loss scenarios, no recovery

### Interview Focus

1. **Correctness Over Scale**
   - Emphasis on correctness
   - Data consistency critical
   - **Key**: Show understanding of financial system requirements

2. **Concurrency Mastery**
   - Deep understanding of threading
   - Proper synchronization
   - **Key**: Demonstrate strong concurrency skills

## Summary

### Key Takeaways

1. **Data Modeling**: Account and Transaction entities
2. **State Management**: Transaction states, account states
3. **Atomicity**: All-or-nothing operations
4. **Concurrency**: Account-level locking, deadlock prevention
5. **Error Handling**: Overdraft, insufficient funds, validation

### Common Interview Questions

1. **How to model accounts and transactions?**
   - Account: account_id, balance, account_number
   - Transaction: transaction_id, type, amount, status, timestamps

2. **How would you handle overdraft or failed transactions?**
   - Overdraft policy with limits
   - Transaction status tracking
   - Rollback on failure

3. **How do you design for easy feature extension?**
   - Transaction manager pattern
   - Strategy pattern for different transaction types
   - Extensible transaction types

### Design Principles

1. **Consistency**: Atomic transactions, correct balances
2. **Concurrency**: Thread-safe operations, deadlock prevention
3. **Reliability**: Error handling, rollback capability
4. **Extensibility**: Easy to add new transaction types
5. **Correctness**: Proper validation, state management

Understanding ATM/banking system design is crucial for Meta interviews focusing on:
- State management
- Transaction handling
- Concurrency control
- Error handling
- Data consistency

