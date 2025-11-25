---
layout: post
title: "Design an In-Memory Gaming Platform with Matchmaking Queue - System Design Interview"
date: 2025-11-24
categories: [System Design, Interview Example, Low-Level Design, In-Memory Systems, Gaming, Matchmaking, Queue Management, Concurrency]
excerpt: "A comprehensive guide to designing an in-memory gaming platform with matchmaking queues, covering player level management, queue system design, game session creation, concurrency handling, and low-level code implementation. This is a common system design interview question that tests your understanding of data structures, thread safety, queue management, and in-memory system design."
---

## Introduction

Designing an in-memory gaming platform with matchmaking queues is a common system design interview question that focuses on low-level design and code implementation. Unlike high-level distributed system design questions, this problem requires you to design data structures, implement queue management logic, handle concurrency, and write actual code.

**Interview Context**: This question often catches candidates off guard because:
1. It's an in-memory design (not distributed)
2. It requires actual code implementation (not just architecture)
3. It involves game-specific concepts (player levels, matchmaking)
4. It tests understanding of data structures and concurrency

This post provides a detailed walkthrough of designing an in-memory gaming platform with matchmaking queues, including complete code implementation, thread-safe queue management, player level handling, and game session creation.

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Requirements](#requirements)
   - [Functional Requirements](#functional-requirements)
   - [Non-Functional Requirements](#non-functional-requirements)
3. [Core Entities](#core-entities)
4. [Data Structures Design](#data-structures-design)
5. [API Design](#api-design)
6. [Implementation](#implementation)
   - [Player Management](#player-management)
   - [Queue Management](#queue-management)
   - [Matchmaking Logic](#matchmaking-logic)
   - [Game Session Management](#game-session-management)
   - [Concurrency Handling](#concurrency-handling)
7. [Code Examples](#code-examples)
8. [Edge Cases and Error Handling](#edge-cases-and-error-handling)
9. [Performance Considerations](#performance-considerations)
10. [Scalability Considerations](#scalability-considerations)
11. [Summary](#summary)

## Problem Statement

**Design an in-memory gaming platform with the following requirements:**

1. Players have different levels (e.g., 1-100)
2. Players can join a matchmaking queue
3. A game session starts when the queue reaches 100 players
4. Each player can only be in one queue at a time
5. Players can leave the queue before a game starts
6. The system should handle concurrent operations (multiple players joining/leaving simultaneously)
7. All data must be stored in memory (no database)

**Key Constraints:**
- In-memory only (no persistence)
- Thread-safe operations
- Efficient queue management
- Handle concurrent access
- Support multiple game queues (different game modes/types)

## Requirements

### Functional Requirements

1. **Player Management**:
   - Register players with unique IDs
   - Track player levels
   - Track player status (idle, in_queue, in_game)

2. **Queue Management**:
   - Players can join a queue
   - Players can leave a queue
   - Check queue status (number of players waiting)
   - Prevent players from joining multiple queues

3. **Matchmaking**:
   - When queue reaches 100 players, create a game session
   - Remove 100 players from queue
   - Assign game session ID to players
   - Notify players that game is starting

4. **Game Session Management**:
   - Create game sessions with unique IDs
   - Track players in each game session
   - Track game session status (waiting, active, finished)

### Non-Functional Requirements

1. **Performance**:
   - Join queue: O(1) average case
   - Leave queue: O(1) average case
   - Check queue status: O(1)
   - Matchmaking check: O(1)

2. **Thread Safety**:
   - All operations must be thread-safe
   - Handle concurrent joins/leaves
   - Prevent race conditions

3. **Memory Efficiency**:
   - Minimize memory overhead
   - Efficient data structures

4. **Scalability**:
   - Support multiple queues (different game modes)
   - Handle thousands of concurrent players

## Core Entities

### Player

```python
class Player:
    def __init__(self, player_id: str, level: int):
        self.player_id = player_id
        self.level = level
        self.status = PlayerStatus.IDLE  # IDLE, IN_QUEUE, IN_GAME
        self.queue_id = None  # Which queue player is in
        self.game_session_id = None  # Which game session player is in
        self.join_time = None  # When player joined queue
```

### Queue

```python
class Queue:
    def __init__(self, queue_id: str, game_mode: str):
        self.queue_id = queue_id
        self.game_mode = game_mode
        self.players = []  # List of Player objects
        self.lock = threading.Lock()  # For thread safety
        self.target_size = 100  # Players needed to start game
```

### Game Session

```python
class GameSession:
    def __init__(self, session_id: str, queue_id: str):
        self.session_id = session_id
        self.queue_id = queue_id
        self.players = []  # List of Player objects
        self.status = GameStatus.WAITING  # WAITING, ACTIVE, FINISHED
        self.created_at = time.time()
```

## Data Structures Design

### Queue Data Structure

**Option 1: List-based Queue**
- Simple list of players
- O(1) append, O(n) removal
- Good for small queues

**Option 2: Deque-based Queue**
- Collections.deque for O(1) operations on both ends
- Better for frequent joins/leaves

**Option 3: Set + List**
- Set for O(1) membership check
- List for ordered queue
- Best for preventing duplicate joins

**Recommended: Deque + Set**
- Deque for O(1) join/leave
- Set for O(1) membership check
- Thread-safe with locks

### Player Lookup

**HashMap/Dictionary**:
- `player_id -> Player` mapping
- O(1) lookup
- Track player status and queue

### Queue Lookup

**HashMap/Dictionary**:
- `queue_id -> Queue` mapping
- O(1) queue access
- Support multiple game modes

### Game Session Storage

**HashMap/Dictionary**:
- `session_id -> GameSession` mapping
- `player_id -> session_id` mapping (for quick lookup)

## API Design

### Player APIs

```python
# Register player
def register_player(player_id: str, level: int) -> bool:
    """
    Register a new player with given level.
    Returns True if successful, False if player already exists.
    """
    pass

# Get player status
def get_player_status(player_id: str) -> dict:
    """
    Get player's current status (idle, in_queue, in_game).
    Returns player status and queue/game info.
    """
    pass
```

### Queue APIs

```python
# Join queue
def join_queue(player_id: str, queue_id: str) -> bool:
    """
    Add player to queue.
    Returns True if successful, False if player already in queue or invalid.
    """
    pass

# Leave queue
def leave_queue(player_id: str) -> bool:
    """
    Remove player from queue.
    Returns True if successful, False if player not in queue.
    """
    pass

# Get queue status
def get_queue_status(queue_id: str) -> dict:
    """
    Get current queue status (number of players waiting).
    Returns queue size and estimated wait time.
    """
    pass
```

### Matchmaking APIs

```python
# Check and create game session
def check_and_create_game(queue_id: str) -> Optional[str]:
    """
    Check if queue has enough players (100).
    If yes, create game session and return session_id.
    Returns None if not enough players.
    """
    pass
```

## Implementation

### Player Management

```python
import threading
from enum import Enum
from typing import Optional, Dict
from collections import deque
import time
import uuid

class PlayerStatus(Enum):
    IDLE = "idle"
    IN_QUEUE = "in_queue"
    IN_GAME = "in_game"

class GameStatus(Enum):
    WAITING = "waiting"
    ACTIVE = "active"
    FINISHED = "finished"

class Player:
    def __init__(self, player_id: str, level: int):
        self.player_id = player_id
        self.level = level
        self.status = PlayerStatus.IDLE
        self.queue_id: Optional[str] = None
        self.game_session_id: Optional[str] = None
        self.join_time: Optional[float] = None
    
    def __repr__(self):
        return f"Player(id={self.player_id}, level={self.level}, status={self.status.value})"

class GameSession:
    def __init__(self, session_id: str, queue_id: str, players: list):
        self.session_id = session_id
        self.queue_id = queue_id
        self.players = players
        self.status = GameStatus.WAITING
        self.created_at = time.time()
    
    def __repr__(self):
        return f"GameSession(id={self.session_id}, players={len(self.players)}, status={self.status.value})"

class Queue:
    def __init__(self, queue_id: str, game_mode: str, target_size: int = 100):
        self.queue_id = queue_id
        self.game_mode = game_mode
        self.target_size = target_size
        self.players_deque = deque()  # Ordered queue
        self.players_set = set()  # For O(1) membership check
        self.lock = threading.RLock()  # Reentrant lock
    
    def add_player(self, player: Player) -> bool:
        """
        Add player to queue.
        Returns True if successful, False if player already in queue.
        """
        with self.lock:
            if player.player_id in self.players_set:
                return False
            
            self.players_deque.append(player)
            self.players_set.add(player.player_id)
            player.status = PlayerStatus.IN_QUEUE
            player.queue_id = self.queue_id
            player.join_time = time.time()
            return True
    
    def remove_player(self, player_id: str) -> bool:
        """
        Remove player from queue.
        Returns True if successful, False if player not in queue.
        """
        with self.lock:
            if player_id not in self.players_set:
                return False
            
            # Remove from set
            self.players_set.remove(player_id)
            
            # Remove from deque (O(n) but necessary for ordered removal)
            # In practice, we can optimize by marking as removed
            for i, player in enumerate(self.players_deque):
                if player.player_id == player_id:
                    self.players_deque.remove(player)
                    player.status = PlayerStatus.IDLE
                    player.queue_id = None
                    player.join_time = None
                    return True
            
            return False
    
    def get_players(self, count: int) -> list:
        """
        Get and remove first N players from queue.
        Returns list of players.
        """
        with self.lock:
            players = []
            for _ in range(min(count, len(self.players_deque))):
                if self.players_deque:
                    player = self.players_deque.popleft()
                    self.players_set.discard(player.player_id)
                    players.append(player)
            return players
    
    def size(self) -> int:
        """Get current queue size."""
        with self.lock:
            return len(self.players_deque)
    
    def contains(self, player_id: str) -> bool:
        """Check if player is in queue."""
        with self.lock:
            return player_id in self.players_set
```

### Gaming Platform Implementation

```python
class GamingPlatform:
    def __init__(self):
        # Player storage: player_id -> Player
        self.players: Dict[str, Player] = {}
        self.players_lock = threading.RLock()
        
        # Queue storage: queue_id -> Queue
        self.queues: Dict[str, Queue] = {}
        self.queues_lock = threading.RLock()
        
        # Game session storage: session_id -> GameSession
        self.game_sessions: Dict[str, GameSession] = {}
        # Player to session mapping: player_id -> session_id
        self.player_to_session: Dict[str, str] = {}
        self.sessions_lock = threading.RLock()
        
        # Background thread for matchmaking
        self.matchmaking_thread = None
        self.running = False
    
    def register_player(self, player_id: str, level: int) -> bool:
        """
        Register a new player.
        Returns True if successful, False if player already exists.
        """
        with self.players_lock:
            if player_id in self.players:
                return False
            
            player = Player(player_id, level)
            self.players[player_id] = player
            return True
    
    def get_player(self, player_id: str) -> Optional[Player]:
        """Get player by ID."""
        with self.players_lock:
            return self.players.get(player_id)
    
    def create_queue(self, queue_id: str, game_mode: str, target_size: int = 100) -> bool:
        """
        Create a new queue.
        Returns True if successful, False if queue already exists.
        """
        with self.queues_lock:
            if queue_id in self.queues:
                return False
            
            queue = Queue(queue_id, game_mode, target_size)
            self.queues[queue_id] = queue
            return True
    
    def join_queue(self, player_id: str, queue_id: str) -> bool:
        """
        Add player to queue.
        Returns True if successful, False if:
        - Player doesn't exist
        - Queue doesn't exist
        - Player already in a queue
        - Player already in this queue
        """
        # Get player
        player = self.get_player(player_id)
        if not player:
            return False
        
        # Check if player is already in a queue or game
        if player.status == PlayerStatus.IN_QUEUE:
            return False  # Already in a queue
        if player.status == PlayerStatus.IN_GAME:
            return False  # Currently in a game
        
        # Get queue
        with self.queues_lock:
            queue = self.queues.get(queue_id)
            if not queue:
                return False
        
        # Add player to queue
        return queue.add_player(player)
    
    def leave_queue(self, player_id: str) -> bool:
        """
        Remove player from queue.
        Returns True if successful, False if player not in queue.
        """
        player = self.get_player(player_id)
        if not player:
            return False
        
        if player.status != PlayerStatus.IN_QUEUE:
            return False
        
        queue_id = player.queue_id
        if not queue_id:
            return False
        
        with self.queues_lock:
            queue = self.queues.get(queue_id)
            if not queue:
                return False
        
        return queue.remove_player(player_id)
    
    def get_queue_status(self, queue_id: str) -> Optional[dict]:
        """
        Get queue status.
        Returns dict with queue size and info, or None if queue doesn't exist.
        """
        with self.queues_lock:
            queue = self.queues.get(queue_id)
            if not queue:
                return None
        
        size = queue.size()
        return {
            "queue_id": queue_id,
            "game_mode": queue.game_mode,
            "current_size": size,
            "target_size": queue.target_size,
            "players_needed": max(0, queue.target_size - size),
            "estimated_wait_time": self._estimate_wait_time(queue_id)
        }
    
    def _estimate_wait_time(self, queue_id: str) -> float:
        """
        Estimate wait time based on current queue size and join rate.
        Simple implementation: assume constant join rate.
        """
        # This is a simplified estimation
        # In practice, you'd track join rate over time
        return 0.0  # Placeholder
    
    def check_and_create_game(self, queue_id: str) -> Optional[str]:
        """
        Check if queue has enough players and create game session.
        Returns session_id if game created, None otherwise.
        """
        with self.queues_lock:
            queue = self.queues.get(queue_id)
            if not queue:
                return None
        
        # Check queue size
        if queue.size() < queue.target_size:
            return None
        
        # Get players from queue
        players = queue.get_players(queue.target_size)
        if len(players) != queue.target_size:
            # Not enough players, put them back
            for player in players:
                queue.add_player(player)
            return None
        
        # Create game session
        session_id = str(uuid.uuid4())
        game_session = GameSession(session_id, queue_id, players)
        
        # Update player statuses
        with self.sessions_lock:
            self.game_sessions[session_id] = game_session
            for player in players:
                player.status = PlayerStatus.IN_GAME
                player.game_session_id = session_id
                player.queue_id = None
                player.join_time = None
                self.player_to_session[player.player_id] = session_id
        
        return session_id
    
    def get_game_session(self, session_id: str) -> Optional[GameSession]:
        """Get game session by ID."""
        with self.sessions_lock:
            return self.game_sessions.get(session_id)
    
    def get_player_game_session(self, player_id: str) -> Optional[GameSession]:
        """Get player's current game session."""
        with self.sessions_lock:
            session_id = self.player_to_session.get(player_id)
            if session_id:
                return self.game_sessions.get(session_id)
            return None
    
    def start_matchmaking_service(self):
        """Start background thread for automatic matchmaking."""
        self.running = True
        self.matchmaking_thread = threading.Thread(
            target=self._matchmaking_loop,
            daemon=True
        )
        self.matchmaking_thread.start()
    
    def stop_matchmaking_service(self):
        """Stop background matchmaking thread."""
        self.running = False
        if self.matchmaking_thread:
            self.matchmaking_thread.join(timeout=1.0)
    
    def _matchmaking_loop(self):
        """Background thread that periodically checks queues and creates games."""
        while self.running:
            try:
                # Check all queues
                with self.queues_lock:
                    queue_ids = list(self.queues.keys())
                
                for queue_id in queue_ids:
                    session_id = self.check_and_create_game(queue_id)
                    if session_id:
                        print(f"Game session {session_id} created from queue {queue_id}")
                
                # Sleep for a short time before next check
                time.sleep(0.1)  # Check every 100ms
            except Exception as e:
                print(f"Error in matchmaking loop: {e}")
                time.sleep(1.0)
```

## Code Examples

### Basic Usage

```python
# Create platform
platform = GamingPlatform()

# Register players
platform.register_player("player1", level=10)
platform.register_player("player2", level=20)
platform.register_player("player3", level=30)
# ... register 100 players

# Create queue
platform.create_queue("queue1", game_mode="battle_royale", target_size=100)

# Players join queue
platform.join_queue("player1", "queue1")
platform.join_queue("player2", "queue1")
platform.join_queue("player3", "queue1")
# ... 97 more players join

# Check queue status
status = platform.get_queue_status("queue1")
print(f"Queue size: {status['current_size']}, Players needed: {status['players_needed']}")

# Start matchmaking service (automatically creates games when queue is full)
platform.start_matchmaking_service()

# When 100th player joins, game session is automatically created
platform.join_queue("player100", "queue1")

# Get game session
session = platform.get_game_session(session_id)
print(f"Game session created with {len(session.players)} players")
```

### Thread-Safe Concurrent Operations

```python
import threading

def simulate_concurrent_joins(platform, player_ids, queue_id):
    """Simulate multiple players joining queue concurrently."""
    def join_queue(player_id):
        result = platform.join_queue(player_id, queue_id)
        print(f"Player {player_id} join result: {result}")
    
    threads = []
    for player_id in player_ids:
        thread = threading.Thread(target=join_queue, args=(player_id,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()

# Example: 50 players join concurrently
player_ids = [f"player{i}" for i in range(1, 51)]
simulate_concurrent_joins(platform, player_ids, "queue1")
```

### Complete Example

```python
def main():
    # Initialize platform
    platform = GamingPlatform()
    
    # Create a queue
    platform.create_queue("battle_royale", "Battle Royale", target_size=100)
    
    # Register 150 players
    for i in range(1, 151):
        platform.register_player(f"player{i}", level=i % 100 + 1)
    
    # Start matchmaking service
    platform.start_matchmaking_service()
    
    # Players join queue
    print("Players joining queue...")
    for i in range(1, 101):
        platform.join_queue(f"player{i}", "battle_royale")
        if i % 10 == 0:
            status = platform.get_queue_status("battle_royale")
            print(f"Queue size: {status['current_size']}, Players needed: {status['players_needed']}")
    
    # Wait for game creation
    time.sleep(1.0)
    
    # Check if game was created
    # (In real implementation, you'd use callbacks or events)
    print("\nMatchmaking complete!")
    
    # Stop service
    platform.stop_matchmaking_service()

if __name__ == "__main__":
    main()
```

## Edge Cases and Error Handling

### Edge Cases

1. **Player tries to join multiple queues**:
   - Check player status before joining
   - Return False if player already in queue

2. **Player leaves queue while matchmaking**:
   - Thread-safe removal
   - Handle case where player is removed during game creation

3. **Queue size drops below 100 during game creation**:
   - Atomic operation: get players and remove in one transaction
   - If not enough players, put them back

4. **Concurrent joins/leaves**:
   - Use locks to ensure thread safety
   - Prevent race conditions

5. **Player doesn't exist**:
   - Validate player exists before operations
   - Return appropriate error

6. **Queue doesn't exist**:
   - Validate queue exists before operations
   - Return appropriate error

### Error Handling

```python
class GamingPlatformError(Exception):
    """Base exception for gaming platform errors."""
    pass

class PlayerNotFoundError(GamingPlatformError):
    """Raised when player doesn't exist."""
    pass

class QueueNotFoundError(GamingPlatformError):
    """Raised when queue doesn't exist."""
    pass

class PlayerAlreadyInQueueError(GamingPlatformError):
    """Raised when player tries to join queue while already in one."""
    pass

class PlayerNotInQueueError(GamingPlatformError):
    """Raised when player tries to leave queue but not in one."""
    pass

# Updated join_queue with better error handling
def join_queue(self, player_id: str, queue_id: str) -> bool:
    """Join queue with proper error handling."""
    player = self.get_player(player_id)
    if not player:
        raise PlayerNotFoundError(f"Player {player_id} not found")
    
    if player.status == PlayerStatus.IN_QUEUE:
        raise PlayerAlreadyInQueueError(f"Player {player_id} already in queue")
    
    if player.status == PlayerStatus.IN_GAME:
        raise PlayerAlreadyInQueueError(f"Player {player_id} currently in game")
    
    with self.queues_lock:
        queue = self.queues.get(queue_id)
        if not queue:
            raise QueueNotFoundError(f"Queue {queue_id} not found")
    
    return queue.add_player(player)
```

## Performance Considerations

### Time Complexity

- **Join Queue**: O(1) - Deque append + Set add
- **Leave Queue**: O(n) worst case (deque removal), but can be optimized
- **Check Queue Size**: O(1) - len(deque)
- **Create Game**: O(k) where k = target_size (100)
- **Player Lookup**: O(1) - HashMap lookup

### Optimizations

1. **Optimize Leave Queue**:
   ```python
   # Instead of O(n) deque removal, use lazy removal
   class Queue:
       def __init__(self):
           self.players_deque = deque()
           self.players_set = set()
           self.removed_players = set()  # Track removed players
       
       def remove_player(self, player_id: str) -> bool:
           with self.lock:
               if player_id not in self.players_set:
                   return False
               self.players_set.remove(player_id)
               self.removed_players.add(player_id)
               return True
       
       def get_players(self, count: int) -> list:
           with self.lock:
               players = []
               while len(players) < count and self.players_deque:
                   player = self.players_deque.popleft()
                   if player.player_id not in self.removed_players:
                       players.append(player)
                   # Clean up removed players
               self.removed_players.clear()
               return players
   ```

2. **Batch Operations**:
   - Batch player removals
   - Batch game session creation

3. **Lock Granularity**:
   - Use fine-grained locks where possible
   - Minimize lock contention

4. **Memory Management**:
   - Clean up finished game sessions
   - Remove old players (if needed)

## Scalability Considerations

### Single Server Limitations

- **Memory**: Limited by server RAM
- **CPU**: Single-threaded matchmaking can be bottleneck
- **Concurrency**: Python GIL limits true parallelism

### Scaling Strategies

1. **Multiple Queues**:
   - Support different game modes
   - Each queue independent

2. **Distributed System** (if needed):
   - Shard players by region
   - Use message queue for cross-server communication
   - Use distributed cache (Redis) for shared state

3. **Load Balancing**:
   - Multiple game servers
   - Route players to appropriate server

4. **Async Processing**:
   - Use async/await for I/O operations
   - Use thread pool for CPU-intensive tasks

### Example: Multi-Queue Support

```python
# Support multiple game modes
platform.create_queue("battle_royale", "Battle Royale", target_size=100)
platform.create_queue("team_deathmatch", "Team Deathmatch", target_size=20)
platform.create_queue("capture_the_flag", "Capture the Flag", target_size=50)

# Players join different queues
platform.join_queue("player1", "battle_royale")
platform.join_queue("player2", "team_deathmatch")
platform.join_queue("player3", "capture_the_flag")
```

## Summary

### Key Takeaways

1. **Data Structures**:
   - Use Deque + Set for O(1) queue operations
   - Use HashMap for O(1) player/queue lookups
   - Thread-safe data structures with locks

2. **Thread Safety**:
   - Use locks (RLock) for all shared data access
   - Minimize lock contention
   - Handle race conditions

3. **Queue Management**:
   - Atomic operations for game creation
   - Handle edge cases (concurrent joins/leaves)
   - Efficient player removal

4. **Matchmaking**:
   - Background thread for automatic matchmaking
   - Check queues periodically
   - Create games when threshold reached

5. **Error Handling**:
   - Validate inputs
   - Handle edge cases
   - Return appropriate errors

### Implementation Highlights

- **Player Management**: HashMap for O(1) lookups
- **Queue Management**: Deque + Set for efficient operations
- **Thread Safety**: Locks for concurrent access
- **Matchmaking**: Background thread with periodic checks
- **Game Sessions**: HashMap for session tracking

### Common Interview Questions

1. **How do you ensure thread safety?**
   - Use locks (RLock) for all shared data structures
   - Minimize critical sections
   - Handle race conditions

2. **What if a player leaves while matchmaking?**
   - Thread-safe removal
   - Atomic game creation (get players and remove in one operation)
   - Handle case where queue size drops

3. **How do you optimize for performance?**
   - O(1) data structures (HashMap, Set, Deque)
   - Minimize lock contention
   - Batch operations where possible

4. **How would you scale this?**
   - Multiple queues for different game modes
   - Distributed system with sharding
   - Message queue for cross-server communication
   - Distributed cache (Redis) for shared state

5. **What data structures did you choose and why?**
   - Deque: O(1) append/popleft operations
   - Set: O(1) membership check
   - HashMap: O(1) player/queue/session lookup

This design provides a solid foundation for an in-memory gaming platform with matchmaking queues, covering all major components, thread safety, and code implementation.

