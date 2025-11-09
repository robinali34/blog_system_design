---
layout: post
title: "SQL Database Read and Write Consistency: A Deep Dive"
date: 2025-11-08
categories: [Database, SQL, ACID, Transactions, Consistency, System Design]
excerpt: "A comprehensive guide to understanding how SQL databases maintain read and write consistency, covering ACID properties, transaction isolation levels, concurrency control mechanisms, and real-world examples."
---

## Introduction

Consistency is one of the fundamental ACID properties that SQL databases guarantee. Understanding how databases maintain consistency during concurrent reads and writes is crucial for building reliable applications and avoiding data corruption, race conditions, and incorrect results.

This guide explores how SQL databases ensure read and write consistency through transaction isolation levels, locking mechanisms, and concurrency control strategies.

---

## ACID Properties Overview

### What is ACID?

ACID is an acronym for four key properties that guarantee reliable database transactions:

1. **Atomicity**: All operations in a transaction succeed or fail together
2. **Consistency**: Database remains in a valid state before and after transaction
3. **Isolation**: Concurrent transactions don't interfere with each other
4. **Durability**: Committed transactions persist even after system failure

### Consistency in Detail

**Consistency** ensures that:
- Database constraints are never violated
- Data integrity rules are maintained
- Transactions move database from one valid state to another
- No partial updates leave database in invalid state

**Examples of Consistency Rules:**
- Foreign key constraints
- Unique constraints
- Check constraints (e.g., age > 0)
- Referential integrity
- Business rules (e.g., account balance >= 0)

---

## Transaction Isolation Levels

Transaction isolation levels define how transactions interact with each other, controlling what data one transaction can see while another is in progress.

### ANSI SQL Isolation Levels

SQL standard defines four isolation levels (from weakest to strongest):

1. **Read Uncommitted**
2. **Read Committed**
3. **Repeatable Read**
4. **Serializable**

### Isolation Level Comparison

| Isolation Level | Dirty Reads | Non-Repeatable Reads | Phantom Reads | Serialization Anomalies |
|----------------|-------------|---------------------|---------------|------------------------|
| **Read Uncommitted** | ✅ Allowed | ✅ Allowed | ✅ Allowed | ✅ Allowed |
| **Read Committed** | ❌ Prevented | ✅ Allowed | ✅ Allowed | ✅ Allowed |
| **Repeatable Read** | ❌ Prevented | ❌ Prevented | ✅ Allowed | ✅ Allowed |
| **Serializable** | ❌ Prevented | ❌ Prevented | ❌ Prevented | ❌ Prevented |

---

## Read Consistency Models

### 1. Read Uncommitted

**Definition:** Lowest isolation level, allows reading uncommitted data.

**Characteristics:**
- Can read data modified by uncommitted transactions
- No read locks acquired
- Fastest but least safe
- Can see "dirty reads"

**Example:**
```sql
-- Transaction 1
BEGIN TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
-- Balance is now 900 (not yet committed)

-- Transaction 2 (Read Uncommitted)
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
BEGIN TRANSACTION;
SELECT balance FROM accounts WHERE id = 1;
-- Sees balance = 900 (uncommitted value)

-- If Transaction 1 rolls back, Transaction 2 saw incorrect data
```

**Use Cases:**
- Rarely used in production
- Reporting where approximate values acceptable
- Real-time dashboards (tolerate stale data)

**Problems:**
- **Dirty Reads**: Read uncommitted data that may be rolled back
- **Inconsistent Results**: Data may not reflect committed state

---

### 2. Read Committed

**Definition:** Default isolation level in most databases. Only reads committed data.

**Characteristics:**
- Prevents dirty reads
- Reads see only committed data
- Each read sees latest committed value
- Non-repeatable reads possible

**How It Works:**

**Locking-Based (SQL Server, MySQL InnoDB):**
- Acquires shared lock for read
- Lock released immediately after read
- Write locks block reads until commit

**MVCC-Based (PostgreSQL, Oracle):**
- Each transaction sees snapshot at start
- Reads don't block writes
- Writes don't block reads
- Uses version numbers/timestamps

**Example:**
```sql
-- Transaction 1
BEGIN TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
-- Balance changed to 900 (not committed)

-- Transaction 2 (Read Committed)
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
BEGIN TRANSACTION;
SELECT balance FROM accounts WHERE id = 1;
-- Sees balance = 1000 (committed value, not 900)
-- Transaction 2 doesn't see uncommitted changes

-- Transaction 1 commits
COMMIT;

-- Transaction 2 reads again
SELECT balance FROM accounts WHERE id = 1;
-- Now sees balance = 900 (new committed value)
-- This is a "non-repeatable read"
```

**Non-Repeatable Read Problem:**
- Same query executed twice in same transaction
- Returns different results
- Another transaction committed changes between reads

**Use Cases:**
- Default for most applications
- Good balance of consistency and performance
- Most web applications

**Trade-offs:**
- ✅ Prevents dirty reads
- ✅ Good performance
- ❌ Allows non-repeatable reads
- ❌ Allows phantom reads

---

### 3. Repeatable Read

**Definition:** Ensures same query returns same results throughout transaction.

**Characteristics:**
- Prevents dirty reads
- Prevents non-repeatable reads
- Each read sees consistent snapshot
- Phantom reads still possible

**How It Works:**

**Locking-Based:**
- Acquires shared locks on rows read
- Locks held until transaction ends
- Prevents other transactions from modifying read rows

**MVCC-Based:**
- Transaction sees snapshot at first read
- All subsequent reads use same snapshot
- Other transactions' commits not visible

**Example:**
```sql
-- Transaction 1
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
BEGIN TRANSACTION;
SELECT balance FROM accounts WHERE id = 1;
-- Sees balance = 1000

-- Transaction 2
BEGIN TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;
-- Balance is now 900 (committed)

-- Transaction 1 reads again
SELECT balance FROM accounts WHERE id = 1;
-- Still sees balance = 1000 (same as first read)
-- Consistent view throughout transaction
```

**Phantom Read Problem:**
```sql
-- Transaction 1
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
BEGIN TRANSACTION;
SELECT * FROM accounts WHERE balance > 500;
-- Returns 10 rows

-- Transaction 2
BEGIN TRANSACTION;
INSERT INTO accounts (id, balance) VALUES (11, 600);
COMMIT;

-- Transaction 1 reads again
SELECT * FROM accounts WHERE balance > 500;
-- Still returns 10 rows (doesn't see new row)
-- But if it does aggregate or count, might see different result
-- This is a "phantom read"
```

**Use Cases:**
- Financial transactions
- Reports requiring consistent data
- Analytics queries
- When you need consistent reads

**Trade-offs:**
- ✅ Prevents dirty reads
- ✅ Prevents non-repeatable reads
- ✅ Consistent view of data
- ❌ Allows phantom reads
- ❌ More locks held (locking-based)
- ❌ Can cause deadlocks

---

### 4. Serializable

**Definition:** Highest isolation level, transactions execute as if serialized.

**Characteristics:**
- Prevents all concurrency anomalies
- Transactions appear to execute one at a time
- Strongest consistency guarantee
- Highest isolation, lowest concurrency

**How It Works:**

**Locking-Based:**
- Range locks prevent phantoms
- Predicate locks on WHERE clauses
- Very restrictive locking

**MVCC-Based:**
- Serializable snapshot isolation (SSI)
- Detects serialization conflicts
- Aborts transactions causing conflicts

**Example:**
```sql
-- Transaction 1
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
BEGIN TRANSACTION;
SELECT SUM(balance) FROM accounts WHERE type = 'savings';
-- Locks all rows matching predicate

-- Transaction 2
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
BEGIN TRANSACTION;
INSERT INTO accounts (id, type, balance) VALUES (11, 'savings', 1000);
-- Blocked or causes conflict
-- Cannot insert because Transaction 1 has predicate lock
```

**Use Cases:**
- Critical financial operations
- When absolute consistency required
- Preventing all concurrency anomalies
- When correctness > performance

**Trade-offs:**
- ✅ Prevents all anomalies
- ✅ Strongest consistency
- ❌ Lowest concurrency
- ❌ Highest lock contention
- ❌ Can cause many aborts (MVCC)
- ❌ Slowest performance

---

## Write Consistency Models

### Write Operations and Consistency

**Write Consistency Ensures:**
- Only one transaction can modify a row at a time
- Writes are atomic (all or nothing)
- Writes don't corrupt data
- Constraints are checked before commit

### Write Locks

**Exclusive Locks (Write Locks):**
- Acquired when writing data
- Prevents other transactions from reading or writing
- Held until transaction commits or rolls back
- Only one exclusive lock per row

**Example:**
```sql
-- Transaction 1
BEGIN TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
-- Acquires exclusive lock on row id=1

-- Transaction 2
BEGIN TRANSACTION;
UPDATE accounts SET balance = balance + 50 WHERE id = 1;
-- Blocked! Waiting for Transaction 1's lock

-- Transaction 1 commits
COMMIT;
-- Lock released, Transaction 2 can proceed
```

### Write-Write Conflicts

**Scenario:** Two transactions try to modify same row.

**Behavior:**
- Second transaction waits for first to commit
- If first commits, second proceeds with new value
- If first rolls back, second proceeds with original value
- Prevents lost updates

**Lost Update Problem (Without Locks):**
```sql
-- Initial balance: 1000

-- Transaction 1
BEGIN TRANSACTION;
SELECT balance FROM accounts WHERE id = 1;  -- Reads 1000
-- Calculates: balance = 1000 - 100 = 900
UPDATE accounts SET balance = 900 WHERE id = 1;
COMMIT;

-- Transaction 2 (concurrent)
BEGIN TRANSACTION;
SELECT balance FROM accounts WHERE id = 1;  -- Reads 1000 (before Transaction 1 commits)
-- Calculates: balance = 1000 + 50 = 1050
UPDATE accounts SET balance = 1050 WHERE id = 1;
COMMIT;

-- Final balance: 1050 (incorrect! Should be 950)
-- Transaction 1's update was lost
```

**Solution with Locks:**
```sql
-- Transaction 1
BEGIN TRANSACTION;
SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;  -- Acquires lock
-- Reads 1000, calculates 900
UPDATE accounts SET balance = 900 WHERE id = 1;
COMMIT;  -- Releases lock

-- Transaction 2 (waits)
BEGIN TRANSACTION;
SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;  -- Waits for lock
-- After Transaction 1 commits, reads 900, calculates 950
UPDATE accounts SET balance = 950 WHERE id = 1;
COMMIT;

-- Final balance: 950 (correct!)
```

---

## Concurrency Control Mechanisms

### 1. Two-Phase Locking (2PL)

**Phase 1: Growing Phase**
- Acquire locks as needed
- Cannot release any locks
- Can acquire new locks

**Phase 2: Shrinking Phase**
- Release locks
- Cannot acquire new locks
- Continues until all locks released

**Strict 2PL:**
- All locks held until transaction commits/aborts
- Most databases use this variant
- Ensures recoverability

**Example:**
```sql
BEGIN TRANSACTION;
-- Growing phase starts
SELECT * FROM accounts WHERE id = 1;  -- Acquire shared lock
UPDATE accounts SET balance = 900 WHERE id = 1;  -- Upgrade to exclusive lock
-- Cannot release locks yet

COMMIT;
-- Shrinking phase starts
-- Release all locks
```

**Problems:**
- **Deadlocks**: Two transactions waiting for each other's locks
- **Lock Contention**: Many transactions waiting for locks
- **Reduced Concurrency**: Locks prevent parallel access

---

### 2. Multi-Version Concurrency Control (MVCC)

**Concept:** Maintain multiple versions of data for different transactions.

**How It Works:**
- Each row has version number or timestamp
- Write creates new version
- Read sees appropriate version based on isolation level
- Old versions cleaned up when no longer needed

**Advantages:**
- Reads don't block writes
- Writes don't block reads
- Better concurrency than locking
- Non-blocking reads

**Disadvantages:**
- More storage (multiple versions)
- Overhead for version management
- Need garbage collection for old versions

**Example (PostgreSQL):**
```sql
-- Transaction 1 (starts at time T1)
BEGIN TRANSACTION;
SELECT balance FROM accounts WHERE id = 1;
-- Sees version created before T1

-- Transaction 2 (starts at time T2, T2 > T1)
BEGIN TRANSACTION;
UPDATE accounts SET balance = 900 WHERE id = 1;
-- Creates new version with timestamp T2
COMMIT;

-- Transaction 1 reads again
SELECT balance FROM accounts WHERE id = 1;
-- Still sees version before T1 (consistent snapshot)
-- Doesn't see Transaction 2's update
```

**Version Cleanup:**
- Old versions kept while transactions might need them
- VACUUM process removes old versions
- Can cause bloat if not run regularly

---

### 3. Optimistic Concurrency Control

**Concept:** Assume conflicts are rare, detect and resolve if they occur.

**How It Works:**
1. Read data without locks
2. Make modifications
3. At commit, check if data changed
4. If changed, abort and retry
5. If unchanged, commit

**Example:**
```sql
-- Transaction 1
BEGIN TRANSACTION;
SELECT balance, version FROM accounts WHERE id = 1;
-- Reads: balance=1000, version=5
-- Calculates: new_balance=900

-- Transaction 2 (concurrent)
BEGIN TRANSACTION;
UPDATE accounts SET balance = 950, version = version + 1 WHERE id = 1;
COMMIT;
-- Balance is now 950, version=6

-- Transaction 1 tries to commit
UPDATE accounts SET balance = 900, version = version + 1 
WHERE id = 1 AND version = 5;
-- Fails! Version is now 6, not 5
-- Transaction 1 aborts and retries
```

**Use Cases:**
- Low conflict scenarios
- When conflicts are rare
- When retries are acceptable

**Trade-offs:**
- ✅ No locks (better concurrency)
- ✅ Good for low contention
- ❌ Aborts on conflicts
- ❌ Retries needed
- ❌ Not good for high contention

---

## Read-Write Interaction Examples

### Example 1: Read Committed with Locking

**Scenario:** Read while write in progress.

```sql
-- Transaction 1 (Write)
BEGIN TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
-- Acquires exclusive lock on row id=1
-- Balance changed to 900 (not committed)

-- Transaction 2 (Read)
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
BEGIN TRANSACTION;
SELECT balance FROM accounts WHERE id = 1;
-- Blocked! Waiting for Transaction 1's exclusive lock
-- Cannot read until Transaction 1 commits or aborts

-- Transaction 1 commits
COMMIT;
-- Lock released

-- Transaction 2 can now read
-- Sees balance = 900 (committed value)
```

**Behavior:**
- Write blocks read (locking-based)
- Read waits for write to complete
- Read sees committed value

---

### Example 2: Read Committed with MVCC

**Scenario:** Read while write in progress (MVCC).

```sql
-- Transaction 1 (Write)
BEGIN TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
-- Creates new version, balance = 900 (not committed)

-- Transaction 2 (Read, starts before Transaction 1 commits)
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
BEGIN TRANSACTION;
SELECT balance FROM accounts WHERE id = 1;
-- Not blocked! Reads old version (balance = 1000)
-- MVCC allows concurrent reads and writes

-- Transaction 1 commits
COMMIT;

-- Transaction 2 reads again
SELECT balance FROM accounts WHERE id = 1;
-- Now sees new committed version (balance = 900)
```

**Behavior:**
- Write doesn't block read (MVCC)
- Read sees old version until write commits
- After commit, read sees new version
- Better concurrency than locking

---

### Example 3: Repeatable Read with MVCC

**Scenario:** Consistent reads throughout transaction.

```sql
-- Transaction 1 (Read)
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
BEGIN TRANSACTION;
SELECT balance FROM accounts WHERE id = 1;
-- Sees balance = 1000 (snapshot at transaction start)

-- Transaction 2 (Write)
BEGIN TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;
-- Balance is now 900 (committed)

-- Transaction 1 reads again
SELECT balance FROM accounts WHERE id = 1;
-- Still sees balance = 1000 (same snapshot)
-- Consistent view throughout transaction
```

**Behavior:**
- Transaction sees consistent snapshot
- Other transactions' commits not visible
- Prevents non-repeatable reads
- Good for reports and analytics

---

## Common Consistency Problems

### 1. Dirty Read

**Problem:** Read uncommitted data that may be rolled back.

**Example:**
```sql
-- Transaction 1
BEGIN TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
-- Balance changed to 900

-- Transaction 2 (Read Uncommitted)
SELECT balance FROM accounts WHERE id = 1;
-- Sees 900 (uncommitted)

-- Transaction 1 rolls back
ROLLBACK;
-- Balance back to 1000

-- Transaction 2 saw incorrect value (900)
```

**Solution:** Use Read Committed or higher isolation level.

---

### 2. Non-Repeatable Read

**Problem:** Same query returns different results in same transaction.

**Example:**
```sql
-- Transaction 1
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
BEGIN TRANSACTION;
SELECT balance FROM accounts WHERE id = 1;
-- Returns 1000

-- Transaction 2
BEGIN TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;
-- Balance is now 900

-- Transaction 1 reads again
SELECT balance FROM accounts WHERE id = 1;
-- Returns 900 (different from first read)
```

**Solution:** Use Repeatable Read or Serializable isolation level.

---

### 3. Phantom Read

**Problem:** Same query returns different number of rows.

**Example:**
```sql
-- Transaction 1
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
BEGIN TRANSACTION;
SELECT COUNT(*) FROM accounts WHERE balance > 500;
-- Returns 10

-- Transaction 2
BEGIN TRANSACTION;
INSERT INTO accounts (id, balance) VALUES (11, 600);
COMMIT;

-- Transaction 1 reads again
SELECT COUNT(*) FROM accounts WHERE balance > 500;
-- Still returns 10 (doesn't see new row)
-- But if it does different query, might see different result
```

**Solution:** Use Serializable isolation level.

---

### 4. Lost Update

**Problem:** Two transactions overwrite each other's changes.

**Example:**
```sql
-- Initial: balance = 1000

-- Transaction 1
BEGIN TRANSACTION;
SELECT balance FROM accounts WHERE id = 1;  -- Reads 1000
UPDATE accounts SET balance = 900 WHERE id = 1;  -- Writes 900
COMMIT;

-- Transaction 2 (concurrent, without proper locking)
BEGIN TRANSACTION;
SELECT balance FROM accounts WHERE id = 1;  -- Reads 1000 (before Transaction 1 commits)
UPDATE accounts SET balance = 1050 WHERE id = 1;  -- Writes 1050
COMMIT;

-- Final: balance = 1050 (incorrect! Should be 950)
-- Transaction 1's update was lost
```

**Solution:** Use `SELECT FOR UPDATE` or proper locking.

---

### 5. Write Skew

**Problem:** Two transactions read different data and make conflicting writes.

**Example:**
```sql
-- Constraint: At least one doctor must be on call

-- Transaction 1
BEGIN TRANSACTION;
SELECT COUNT(*) FROM doctors WHERE on_call = true;
-- Returns 2 (doctors A and B on call)
-- Decides doctor A can take leave
UPDATE doctors SET on_call = false WHERE id = 'A';
COMMIT;

-- Transaction 2 (concurrent)
BEGIN TRANSACTION;
SELECT COUNT(*) FROM doctors WHERE on_call = true;
-- Returns 2 (doctors A and B on call, before Transaction 1 commits)
-- Decides doctor B can take leave
UPDATE doctors SET on_call = false WHERE id = 'B';
COMMIT;

-- Result: No doctors on call (violates constraint!)
```

**Solution:** Use Serializable isolation level or application-level checks.

---

## Database-Specific Implementations

### PostgreSQL

**Default Isolation Level:** Read Committed

**Concurrency Control:** MVCC (Multi-Version Concurrency Control)

**Characteristics:**
- Reads don't block writes
- Writes don't block reads
- Snapshot isolation for Repeatable Read
- Serializable Snapshot Isolation (SSI) for Serializable

**Example:**
```sql
-- PostgreSQL uses MVCC
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
-- Gets snapshot at transaction start
-- All reads use this snapshot
```

---

### MySQL (InnoDB)

**Default Isolation Level:** Repeatable Read

**Concurrency Control:** MVCC with locking

**Characteristics:**
- MVCC for consistent reads
- Locking for writes
- Next-key locking prevents phantoms
- Gap locks for range queries

**Example:**
```sql
-- InnoDB uses MVCC + locking
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
BEGIN TRANSACTION;
-- Consistent reads use MVCC
-- Writes use locking
```

---

### SQL Server

**Default Isolation Level:** Read Committed

**Concurrency Control:** Locking-based

**Characteristics:**
- Row-level locking
- Shared locks for reads
- Exclusive locks for writes
- Lock escalation to page/table if needed

**Example:**
```sql
-- SQL Server uses locking
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
BEGIN TRANSACTION;
-- Acquires locks for reads and writes
```

---

### Oracle

**Default Isolation Level:** Read Committed

**Concurrency Control:** MVCC

**Characteristics:**
- Multi-version read consistency
- Undo segments store old versions
- Reads don't block writes
- Serializable uses SSI

**Example:**
```sql
-- Oracle uses MVCC
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
BEGIN TRANSACTION;
-- Reads use undo segments for consistency
```

---

## Best Practices

### 1. Choose Appropriate Isolation Level

**Guidelines:**
- **Read Committed**: Default for most applications
- **Repeatable Read**: For reports, analytics, financial calculations
- **Serializable**: Only when absolute consistency required
- **Read Uncommitted**: Rarely used

**Consider:**
- Consistency requirements
- Performance needs
- Concurrency requirements
- Application tolerance for anomalies

### 2. Keep Transactions Short

**Why:**
- Reduce lock contention
- Lower deadlock probability
- Better concurrency
- Faster commits

**How:**
- Do work outside transaction when possible
- Batch operations efficiently
- Avoid user interaction in transactions
- Use appropriate transaction boundaries

### 3. Use Explicit Locking When Needed

**SELECT FOR UPDATE:**
```sql
-- Prevent lost updates
SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
```

**Use Cases:**
- Preventing lost updates
- Ensuring consistent reads before writes
- Critical sections

### 4. Handle Deadlocks

**Deadlock Detection:**
- Databases detect and abort one transaction
- Application should retry aborted transaction

**Prevention:**
- Acquire locks in consistent order
- Keep transactions short
- Use lower isolation levels when possible

### 5. Monitor Lock Contention

**Metrics to Watch:**
- Lock wait time
- Deadlock frequency
- Lock escalation events
- Transaction duration

**Tools:**
- Database monitoring tools
- Query performance insights
- Lock wait statistics

---

## Conclusion

SQL databases maintain read and write consistency through:

1. **Transaction Isolation Levels**: Control what transactions can see
2. **Concurrency Control**: Locking or MVCC mechanisms
3. **ACID Properties**: Guarantee reliable transactions
4. **Constraint Enforcement**: Ensure data integrity

**Key Takeaways:**

- **Read Committed** is default and sufficient for most applications
- **MVCC** provides better concurrency than locking
- **Repeatable Read** ensures consistent reads within transaction
- **Serializable** provides strongest consistency but lowest concurrency
- **Proper locking** prevents lost updates and race conditions
- **Short transactions** reduce contention and improve performance

Understanding these mechanisms helps you:
- Choose appropriate isolation levels
- Design transactions correctly
- Avoid consistency problems
- Optimize database performance
- Build reliable applications

Consistency is a trade-off between correctness and performance. Choose the right balance for your application's needs.

