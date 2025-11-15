---
layout: post
title: "Design a Chess Game System with Unlimited Undo and ELO Rating - System Design Interview"
date: 2025-11-14
categories: [System Design, Interview Example, Distributed Systems, Gaming, Real-time Systems, Rating Systems]
excerpt: "A comprehensive guide to designing a chess game system that supports unlimited undo moves and ELO rating calculation, covering game state management, move history, undo functionality, ELO rating system, real-time gameplay, and architectural patterns for handling millions of concurrent games."
---

## Introduction

A chess game system with unlimited undo and ELO rating requires managing game state, move history, undo operations, and player ratings. Systems like Chess.com and Lichess handle millions of games, support unlimited move undo, and maintain accurate ELO ratings for millions of players.

This post provides a detailed walkthrough of designing a chess game system with unlimited undo and ELO rating, covering game state management, move history storage, undo/redo operations, ELO calculation, real-time gameplay, and handling concurrent games. This is a common system design interview question that tests your understanding of distributed systems, state management, data structures, rating algorithms, and real-time communication.

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Requirements](#requirements)
   - [Functional Requirements](#functional-requirements)
   - [Non-Functional Requirements](#non-functional-requirements)
3. [Capacity Estimation](#capacity-estimation)
   - [Traffic Estimates](#traffic-estimates)
   - [Storage Estimates](#storage-estimates)
   - [Bandwidth Estimates](#bandwidth-estimates)
4. [Core Entities](#core-entities)
5. [API](#api)
6. [Data Flow](#data-flow)
7. [Database Design](#database-design)
   - [Schema Design](#schema-design)
   - [Database Sharding Strategy](#database-sharding-strategy)
8. [High-Level Design](#high-level-design)
9. [Deep Dive](#deep-dive)
   - [Component Design](#component-design)
   - [Detailed Design](#detailed-design)
   - [Scalability Considerations](#scalability-considerations)
   - [Security Considerations](#security-considerations)
   - [Monitoring & Observability](#monitoring--observability)
   - [Trade-offs and Optimizations](#trade-offs-and-optimizations)
10. [Summary](#summary)

## Problem Statement

**Design a chess game system with unlimited undo and ELO rating with the following features:**

1. Create and manage chess games
2. Make moves and validate them
3. Support unlimited undo moves
4. Support redo moves (after undo)
5. Calculate and update ELO ratings
6. Real-time game updates
7. Game history and replay
8. Support multiple game modes (blitz, rapid, classical)
9. Handle time controls and clocks
10. Support game analysis and move suggestions

**Scale Requirements:**
- 10 million+ users
- 1 million+ active games simultaneously
- 100 million+ moves per day
- Peak: 10,000 moves per second
- Average moves per game: 40
- Maximum undo depth: Unlimited
- Must support real-time gameplay
- ELO rating updates after each game

## Requirements

### Functional Requirements

**Core Features:**
1. **Game Management**: Create, join, leave games
2. **Move Making**: Make valid chess moves
3. **Move Validation**: Validate moves according to chess rules
4. **Unlimited Undo**: Undo any number of moves
5. **Redo Support**: Redo moves after undo
6. **ELO Rating**: Calculate and update ELO ratings
7. **Real-Time Updates**: Broadcast moves to both players
8. **Game History**: Store complete game history
9. **Game Replay**: Replay games from history
10. **Time Controls**: Support different time controls

**Out of Scope:**
- Chess engine integration (focus on game management)
- Move analysis (focus on basic gameplay)
- Tournament management
- Spectator mode
- Mobile app (focus on web API)

### Non-Functional Requirements

1. **Availability**: 99.9% uptime
2. **Reliability**: No move loss, accurate game state
3. **Performance**: 
   - Move processing: < 100ms
   - Undo operation: < 50ms
   - Real-time update: < 200ms
   - ELO calculation: < 10ms
4. **Scalability**: Handle 10K+ moves per second
5. **Consistency**: Strong consistency for game state
6. **Data Integrity**: Accurate move history and ELO ratings

## Capacity Estimation

### Traffic Estimates

- **Total Users**: 10 million
- **Daily Active Users (DAU)**: 1 million
- **Active Games**: 1 million simultaneously
- **Moves per Day**: 100 million
- **Average Moves per Game**: 40
- **Peak Move Rate**: 10,000 per second
- **Normal Move Rate**: 1,000 per second
- **Undo Operations**: 10% of moves = 10 million per day
- **ELO Updates**: 2.5 million per day (games completed)

### Storage Estimates

**Game Data:**
- 1M active games × 5KB = 5GB
- Game state, move history, metadata

**Move History:**
- 100M moves/day × 200 bytes = 20GB/day
- 30-day retention: ~600GB
- 1-year archive: ~7.3TB

**Game Archive:**
- 2.5M completed games/day × 10KB = 25GB/day
- 1-year retention: ~9TB

**Player Data:**
- 10M users × 1KB = 10GB
- User profiles, ELO ratings

**ELO History:**
- 2.5M ELO updates/day × 100 bytes = 250MB/day
- 1-year retention: ~90GB

**Total Storage**: ~16TB

### Bandwidth Estimates

**Normal Traffic:**
- 1,000 moves/sec × 2KB = 2MB/s = 16Mbps
- Move data, game state updates

**Peak Traffic:**
- 10,000 moves/sec × 2KB = 20MB/s = 160Mbps

**Real-Time Updates:**
- 1,000 moves/sec × 2KB × 2 players = 4MB/s = 32Mbps

**Total Peak**: ~160Mbps

## Core Entities

### Game
- `game_id` (UUID)
- `white_player_id` (user_id)
- `black_player_id` (user_id)
- `game_status` (waiting, active, finished, abandoned)
- `current_turn` (white, black)
- `board_state` (FEN string)
- `move_count` (INT)
- `time_control` (blitz, rapid, classical)
- `white_time_remaining` (INT, milliseconds)
- `black_time_remaining` (INT, milliseconds)
- `result` (white_wins, black_wins, draw, ongoing)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)
- `finished_at` (TIMESTAMP)

### Move
- `move_id` (UUID)
- `game_id` (UUID)
- `move_number` (INT)
- `player_id` (user_id)
- `color` (white, black)
- `from_square` (VARCHAR, e.g., "e2")
- `to_square` (VARCHAR, e.g., "e4")
- `piece` (pawn, rook, knight, bishop, queen, king)
- `captured_piece` (VARCHAR, optional)
- `promotion` (VARCHAR, optional)
- `is_castle` (BOOLEAN)
- `is_en_passant` (BOOLEAN)
- `is_check` (BOOLEAN)
- `is_checkmate` (BOOLEAN)
- `board_state_after` (FEN string)
- `timestamp` (TIMESTAMP)
- `is_undone` (BOOLEAN)

### Undo History
- `undo_id` (UUID)
- `game_id` (UUID)
- `move_id` (UUID)
- `undo_timestamp` (TIMESTAMP)
- `redo_timestamp` (TIMESTAMP, optional)
- `is_redone` (BOOLEAN)

### Player
- `user_id` (UUID)
- `username` (VARCHAR)
- `elo_rating` (INT)
- `elo_blitz` (INT)
- `elo_rapid` (INT)
- `elo_classical` (INT)
- `games_played` (INT)
- `games_won` (INT)
- `games_lost` (INT)
- `games_drawn` (INT)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

### ELO History
- `elo_history_id` (UUID)
- `user_id` (UUID)
- `game_id` (UUID)
- `time_control` (VARCHAR)
- `old_elo` (INT)
- `new_elo` (INT)
- `elo_change` (INT)
- `opponent_elo` (INT)
- `result` (win, loss, draw)
- `timestamp` (TIMESTAMP)

## API

### 1. Create Game
```
POST /api/v1/games
Request:
{
  "time_control": "blitz",
  "initial_time_minutes": 5,
  "increment_seconds": 3
}

Response:
{
  "game_id": "uuid",
  "white_player_id": "user123",
  "black_player_id": null,
  "game_status": "waiting",
  "time_control": "blitz",
  "created_at": "2025-11-13T10:00:00Z"
}
```

### 2. Make Move
```
POST /api/v1/games/{game_id}/moves
Request:
{
  "from_square": "e2",
  "to_square": "e4",
  "promotion": null
}

Response:
{
  "move_id": "uuid",
  "game_id": "uuid",
  "move_number": 1,
  "from_square": "e2",
  "to_square": "e4",
  "board_state": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
  "is_check": false,
  "is_checkmate": false,
  "current_turn": "black",
  "timestamp": "2025-11-13T10:01:00Z"
}
```

### 3. Undo Move
```
POST /api/v1/games/{game_id}/undo
Request:
{
  "move_count": 1
}

Response:
{
  "game_id": "uuid",
  "moves_undone": 1,
  "current_move_number": 0,
  "board_state": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "current_turn": "white",
  "undo_history": [
    {
      "move_id": "uuid",
      "move_number": 1,
      "undone_at": "2025-11-13T10:02:00Z"
    }
  ]
}
```

### 4. Redo Move
```
POST /api/v1/games/{game_id}/redo
Request:
{
  "move_count": 1
}

Response:
{
  "game_id": "uuid",
  "moves_redone": 1,
  "current_move_number": 1,
  "board_state": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
  "current_turn": "black"
}
```

### 5. Get Game State
```
GET /api/v1/games/{game_id}
Response:
{
  "game_id": "uuid",
  "white_player": {...},
  "black_player": {...},
  "current_turn": "white",
  "board_state": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "move_count": 0,
  "move_history": [],
  "time_remaining": {
    "white": 300000,
    "black": 300000
  },
  "game_status": "active"
}
```

### 6. Get Move History
```
GET /api/v1/games/{game_id}/moves?limit=50&offset=0
Response:
{
  "moves": [
    {
      "move_id": "uuid",
      "move_number": 1,
      "from_square": "e2",
      "to_square": "e4",
      "piece": "pawn",
      "timestamp": "2025-11-13T10:01:00Z",
      "is_undone": false
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

### 7. Finish Game
```
POST /api/v1/games/{game_id}/finish
Request:
{
  "result": "white_wins",
  "reason": "checkmate"
}

Response:
{
  "game_id": "uuid",
  "result": "white_wins",
  "elo_updates": {
    "white": {
      "old_elo": 1500,
      "new_elo": 1516,
      "change": 16
    },
    "black": {
      "old_elo": 1500,
      "new_elo": 1484,
      "change": -16
    }
  }
}
```

## Data Flow

### Move Making Flow

1. **Player Makes Move**:
   - Player submits move (from_square, to_square)
   - **Client** sends request to **API Gateway**
   - **API Gateway** routes to **Game Service**

2. **Move Validation**:
   - **Game Service**:
     - Validates it's player's turn
     - Validates move is legal (chess rules)
     - Checks game is active
     - Validates time remaining

3. **Move Processing**:
   - **Game Service**:
     - Creates move record
     - Updates board state (FEN)
     - Increments move count
     - Switches turn
     - Updates time remaining
     - Checks for check/checkmate

4. **State Update**:
   - **Game Service**:
     - Updates game state in **Database**
     - Stores move in **Move History**
     - Publishes move event to **Message Queue**

5. **Real-Time Notification**:
   - **Notification Service**:
     - Broadcasts move to both players via **WebSocket**
     - Updates game state for both clients

6. **Response**:
   - **Game Service** returns move details
   - **Client** updates UI

### Undo Move Flow

1. **Player Requests Undo**:
   - Player clicks undo button
   - **Client** sends undo request
   - **API Gateway** routes to **Game Service**

2. **Undo Validation**:
   - **Game Service**:
     - Validates game is active
     - Validates moves exist to undo
     - Validates undo is allowed (not opponent's turn)

3. **Move Undo**:
   - **Game Service**:
     - Gets last move(s) from history
     - Reverts board state to previous position
     - Marks moves as undone
     - Updates move count
     - Switches turn back
     - Restores time remaining

4. **Undo History**:
   - **Game Service**:
     - Creates undo history record
     - Stores previous board state
     - Enables redo capability

5. **State Update**:
   - **Game Service**:
     - Updates game state in **Database**
     - Publishes undo event

6. **Notification**:
   - **Notification Service** broadcasts undo to both players

### ELO Calculation Flow

1. **Game Finished**:
   - Game ends (checkmate, resignation, draw, timeout)
   - **Game Service** determines result

2. **ELO Calculation**:
   - **ELO Service**:
     - Gets both players' current ELO ratings
     - Calculates expected score for each player
     - Calculates ELO change based on actual result
     - Updates player ELO ratings

3. **ELO Update**:
   - **ELO Service**:
     - Updates player ELO in **Database**
     - Creates ELO history record
     - Updates player statistics

4. **Notification**:
   - **Notification Service** notifies players of ELO changes

## Database Design

### Schema Design

**Games Table:**
```sql
CREATE TABLE games (
    game_id UUID PRIMARY KEY,
    white_player_id UUID NOT NULL,
    black_player_id UUID NOT NULL,
    game_status VARCHAR(50) NOT NULL,
    current_turn VARCHAR(10) NOT NULL,
    board_state VARCHAR(100) NOT NULL,
    move_count INT DEFAULT 0,
    time_control VARCHAR(50) NOT NULL,
    white_time_remaining INT NOT NULL,
    black_time_remaining INT NOT NULL,
    result VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    finished_at TIMESTAMP NULL,
    INDEX idx_white_player (white_player_id),
    INDEX idx_black_player (black_player_id),
    INDEX idx_status (game_status),
    INDEX idx_created_at (created_at DESC)
);
```

**Moves Table (Sharded by game_id):**
```sql
CREATE TABLE moves_0 (
    move_id UUID PRIMARY KEY,
    game_id UUID NOT NULL,
    move_number INT NOT NULL,
    player_id UUID NOT NULL,
    color VARCHAR(10) NOT NULL,
    from_square VARCHAR(2) NOT NULL,
    to_square VARCHAR(2) NOT NULL,
    piece VARCHAR(20) NOT NULL,
    captured_piece VARCHAR(20),
    promotion VARCHAR(20),
    is_castle BOOLEAN DEFAULT FALSE,
    is_en_passant BOOLEAN DEFAULT FALSE,
    is_check BOOLEAN DEFAULT FALSE,
    is_checkmate BOOLEAN DEFAULT FALSE,
    board_state_after VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    is_undone BOOLEAN DEFAULT FALSE,
    INDEX idx_game_id (game_id),
    INDEX idx_game_move_number (game_id, move_number),
    INDEX idx_is_undone (is_undone)
);
-- Similar tables: moves_1, moves_2, ..., moves_N
```

**Undo History Table:**
```sql
CREATE TABLE undo_history (
    undo_id UUID PRIMARY KEY,
    game_id UUID NOT NULL,
    move_id UUID NOT NULL,
    move_number INT NOT NULL,
    board_state_before VARCHAR(100) NOT NULL,
    undo_timestamp TIMESTAMP DEFAULT NOW(),
    redo_timestamp TIMESTAMP NULL,
    is_redone BOOLEAN DEFAULT FALSE,
    INDEX idx_game_id (game_id),
    INDEX idx_move_id (move_id),
    INDEX idx_is_redone (is_redone)
);
```

**Players Table:**
```sql
CREATE TABLE players (
    user_id UUID PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    elo_rating INT DEFAULT 1500,
    elo_blitz INT DEFAULT 1500,
    elo_rapid INT DEFAULT 1500,
    elo_classical INT DEFAULT 1500,
    games_played INT DEFAULT 0,
    games_won INT DEFAULT 0,
    games_lost INT DEFAULT 0,
    games_drawn INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_username (username),
    INDEX idx_elo_rating (elo_rating DESC)
);
```

**ELO History Table:**
```sql
CREATE TABLE elo_history (
    elo_history_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    game_id UUID NOT NULL,
    time_control VARCHAR(50) NOT NULL,
    old_elo INT NOT NULL,
    new_elo INT NOT NULL,
    elo_change INT NOT NULL,
    opponent_elo INT NOT NULL,
    result VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_id (user_id),
    INDEX idx_game_id (game_id),
    INDEX idx_timestamp (timestamp DESC)
);
```

### Database Sharding Strategy

**Moves Table Sharding:**
- Shard by game_id using consistent hashing
- 1000 shards: `shard_id = hash(game_id) % 1000`
- All moves for a game in same shard
- Enables efficient move history queries

**Shard Key Selection:**
- `game_id` ensures all moves for a game are in same shard
- Enables efficient queries for game move history
- Prevents cross-shard queries for single game

**Replication:**
- Each shard replicated 3x for high availability
- Master-replica setup for read scaling
- Writes go to master, reads can go to replicas

## High-Level Design

```
┌─────────────┐
│   Client    │
│  (Web App)  │
└──────┬──────┘
       │
       │ HTTP/WebSocket
       │
┌──────▼──────────────────────────────────────────────┐
│        API Gateway / Load Balancer                   │
│        - Rate Limiting                               │
│        - Request Routing                             │
└──────┬──────────────────────────────────────────────┘
       │
       ├──────────────┬──────────────┬──────────────┬──────────────┐
       │              │              │              │              │
┌──────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
│  Game       │ │  Move      │ │  ELO       │ │ Notification│ │  Chess     │
│  Service    │ │  Validator  │ │  Service   │ │  Service    │ │  Engine    │
└──────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
       │              │              │              │              │
       │              │              │              │              │
┌──────▼──────────────▼──────────────▼──────────────▼──────────────▼──────┐
│              Message Queue (Kafka)                                        │
│              - Move events                                                 │
│              - Undo events                                                │
│              - Game events                                                 │
└──────┬───────────────────────────────────────────────────────────────────┘
       │
       │
┌──────▼───────────────────────────────────────────────────────────────────┐
│         Database Cluster (Sharded)                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                              │
│  │ Games    │  │ Moves    │  │ Players   │                              │
│  │ DB       │  │ (Sharded)│  │ DB        │                              │
│  └──────────┘  └──────────┘  └──────────┘                              │
│                                                                           │
│  ┌──────────┐  ┌──────────┐                                              │
│  │ Undo     │  │ ELO      │                                              │
│  │ History  │  │ History  │                                              │
│  │ DB       │  │ DB       │                                              │
│  └──────────┘  └──────────┘                                              │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│              Cache Layer (Redis)                                          │
│  - Active game states                                                     │
│  - Move history (recent)                                                  │
│  - Player ELO ratings                                                      │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│         WebSocket Service                                                  │
│         - Real-time move updates                                          │
│         - Game state synchronization                                       │
└───────────────────────────────────────────────────────────────────────────┘
```

## Deep Dive

### Component Design

#### 1. Game Service

**Responsibilities:**
- Manage game lifecycle
- Handle move making
- Manage undo/redo operations
- Update game state

**Key Design Decisions:**
- **State Machine**: Use state machine for game status
- **Move History**: Store complete move history
- **Board State**: Use FEN notation for board representation
- **Undo Stack**: Maintain undo stack for redo capability

**Implementation:**
```python
class GameService:
    def __init__(self):
        self.db = Database()
        self.move_validator = MoveValidator()
        self.chess_engine = ChessEngine()
        self.cache = RedisCache()
    
    def make_move(self, game_id, player_id, from_square, to_square, promotion=None):
        # Get game
        game = self.get_game(game_id)
        
        # Validate turn
        if not self.is_player_turn(game, player_id):
            raise InvalidMoveError("Not your turn")
        
        # Validate move
        if not self.move_validator.is_valid_move(
            game.board_state, from_square, to_square, game.current_turn
        ):
            raise InvalidMoveError("Invalid move")
        
        # Make move
        new_board_state = self.chess_engine.make_move(
            game.board_state, from_square, to_square, promotion
        )
        
        # Check game state
        is_check = self.chess_engine.is_check(new_board_state, game.current_turn)
        is_checkmate = self.chess_engine.is_checkmate(new_board_state, game.current_turn)
        
        # Create move record
        move = Move(
            game_id=game_id,
            move_number=game.move_count + 1,
            player_id=player_id,
            color=game.current_turn,
            from_square=from_square,
            to_square=to_square,
            board_state_after=new_board_state,
            is_check=is_check,
            is_checkmate=is_checkmate
        )
        move.save()
        
        # Update game state
        game.board_state = new_board_state
        game.move_count += 1
        game.current_turn = 'black' if game.current_turn == 'white' else 'white'
        game.updated_at = datetime.now()
        game.save()
        
        # Clear undo stack (can't redo after new move)
        self.clear_redo_stack(game_id)
        
        # Publish move event
        self.publish_move_event(game_id, move)
        
        return move
    
    def undo_move(self, game_id, player_id, move_count=1):
        # Get game
        game = self.get_game(game_id)
        
        # Validate undo is allowed
        if game.move_count == 0:
            raise InvalidOperationError("No moves to undo")
        
        # Get moves to undo
        moves_to_undo = self.db.get_last_moves(game_id, move_count)
        
        if not moves_to_undo:
            raise InvalidOperationError("Not enough moves to undo")
        
        # Undo moves
        undone_moves = []
        for move in reversed(moves_to_undo):
            # Get previous board state
            if move.move_number == 1:
                # Initial position
                previous_state = self.get_initial_board_state()
            else:
                previous_move = self.db.get_move_by_number(game_id, move.move_number - 1)
                previous_state = previous_move.board_state_after
            
            # Mark move as undone
            move.is_undone = True
            move.save()
            
            # Create undo history
            undo_history = UndoHistory(
                game_id=game_id,
                move_id=move.move_id,
                move_number=move.move_number,
                board_state_before=previous_state
            )
            undo_history.save()
            
            undone_moves.append(move)
        
        # Update game state
        if undone_moves:
            last_undone = undone_moves[-1]
            if last_undone.move_number == 1:
                game.board_state = self.get_initial_board_state()
                game.move_count = 0
                game.current_turn = 'white'
            else:
                previous_move = self.db.get_move_by_number(
                    game_id, last_undone.move_number - 1
                )
                game.board_state = previous_move.board_state_after
                game.move_count = previous_move.move_number - 1
                game.current_turn = previous_move.color
        
        game.updated_at = datetime.now()
        game.save()
        
        # Publish undo event
        self.publish_undo_event(game_id, undone_moves)
        
        return {
            'moves_undone': len(undone_moves),
            'current_move_number': game.move_count,
            'board_state': game.board_state
        }
    
    def redo_move(self, game_id, player_id, move_count=1):
        # Get game
        game = self.get_game(game_id)
        
        # Get undone moves that can be redone
        undone_moves = self.db.get_undone_moves_for_redo(game_id, move_count)
        
        if not undone_moves:
            raise InvalidOperationError("No moves to redo")
        
        # Redo moves
        redone_moves = []
        for move in undone_moves:
            # Mark move as not undone
            move.is_undone = False
            move.save()
            
            # Update undo history
            undo_history = self.db.get_undo_history_by_move_id(move.move_id)
            if undo_history:
                undo_history.is_redone = True
                undo_history.redo_timestamp = datetime.now()
                undo_history.save()
            
            redone_moves.append(move)
        
        # Update game state to last redone move
        if redone_moves:
            last_redone = redone_moves[-1]
            game.board_state = last_redone.board_state_after
            game.move_count = last_redone.move_number
            game.current_turn = 'black' if last_redone.color == 'white' else 'white'
        
        game.updated_at = datetime.now()
        game.save()
        
        # Publish redo event
        self.publish_redo_event(game_id, redone_moves)
        
        return {
            'moves_redone': len(redone_moves),
            'current_move_number': game.move_count,
            'board_state': game.board_state
        }
```

#### 2. ELO Service

**Responsibilities:**
- Calculate ELO rating changes
- Update player ELO ratings
- Track ELO history
- Handle different time controls

**Key Design Decisions:**
- **ELO Formula**: Use standard ELO formula
- **K-Factor**: Different K-factors for different ratings
- **Time Control**: Separate ELO for blitz, rapid, classical
- **History Tracking**: Track all ELO changes

**Implementation:**
```python
class ELOService:
    def __init__(self):
        self.db = Database()
        self.k_factor_new = 32  # For new players (< 30 games)
        self.k_factor_standard = 16  # For standard players
        self.k_factor_expert = 10  # For expert players (> 2400)
    
    def calculate_elo_change(self, player_elo, opponent_elo, result):
        """
        Calculate ELO change using standard formula
        
        result: 1 for win, 0.5 for draw, 0 for loss
        """
        # Expected score
        expected_score = 1 / (1 + 10 ** ((opponent_elo - player_elo) / 400))
        
        # Determine K-factor
        k_factor = self.get_k_factor(player_elo)
        
        # Calculate ELO change
        elo_change = k_factor * (result - expected_score)
        
        return round(elo_change)
    
    def get_k_factor(self, elo_rating):
        """Get K-factor based on rating"""
        if elo_rating < 2100:
            return self.k_factor_standard
        elif elo_rating < 2400:
            return self.k_factor_standard
        else:
            return self.k_factor_expert
    
    def update_elo_ratings(self, game_id, white_player_id, black_player_id, result):
        """Update ELO ratings after game"""
        # Get current ratings
        white_player = self.db.get_player(white_player_id)
        black_player = self.db.get_player(black_player_id)
        
        # Determine result (1 = white wins, 0.5 = draw, 0 = black wins)
        if result == 'white_wins':
            white_result = 1
            black_result = 0
        elif result == 'black_wins':
            white_result = 0
            black_result = 1
        else:  # draw
            white_result = 0.5
            black_result = 0.5
        
        # Get game time control
        game = self.db.get_game(game_id)
        time_control = game.time_control
        
        # Calculate ELO changes
        white_elo_change = self.calculate_elo_change(
            white_player.get_elo(time_control),
            black_player.get_elo(time_control),
            white_result
        )
        
        black_elo_change = self.calculate_elo_change(
            black_player.get_elo(time_control),
            white_player.get_elo(time_control),
            black_result
        )
        
        # Update player ELOs
        white_new_elo = white_player.get_elo(time_control) + white_elo_change
        black_new_elo = black_player.get_elo(time_control) + black_elo_change
        
        white_player.set_elo(time_control, white_new_elo)
        black_player.set_elo(time_control, black_new_elo)
        
        # Update statistics
        white_player.games_played += 1
        black_player.games_played += 1
        
        if result == 'white_wins':
            white_player.games_won += 1
            black_player.games_lost += 1
        elif result == 'black_wins':
            black_player.games_won += 1
            white_player.games_lost += 1
        else:
            white_player.games_drawn += 1
            black_player.games_drawn += 1
        
        white_player.save()
        black_player.save()
        
        # Create ELO history records
        self.create_elo_history(
            white_player_id, game_id, time_control,
            white_player.get_elo(time_control) - white_elo_change,
            white_new_elo, white_elo_change,
            black_player.get_elo(time_control), white_result
        )
        
        self.create_elo_history(
            black_player_id, game_id, time_control,
            black_player.get_elo(time_control) - black_elo_change,
            black_new_elo, black_elo_change,
            white_player.get_elo(time_control), black_result
        )
        
        return {
            'white': {
                'old_elo': white_player.get_elo(time_control) - white_elo_change,
                'new_elo': white_new_elo,
                'change': white_elo_change
            },
            'black': {
                'old_elo': black_player.get_elo(time_control) - black_elo_change,
                'new_elo': black_new_elo,
                'change': black_elo_change
            }
        }
    
    def create_elo_history(self, user_id, game_id, time_control, old_elo, new_elo, 
                          elo_change, opponent_elo, result):
        """Create ELO history record"""
        elo_history = ELOHistory(
            user_id=user_id,
            game_id=game_id,
            time_control=time_control,
            old_elo=old_elo,
            new_elo=new_elo,
            elo_change=elo_change,
            opponent_elo=opponent_elo,
            result='win' if result == 1 else ('draw' if result == 0.5 else 'loss')
        )
        elo_history.save()
```

#### 3. Move Validator

**Responsibilities:**
- Validate chess moves
- Check move legality
- Validate game rules

**Key Design Decisions:**
- **Chess Engine**: Use chess library for validation
- **Rule Checking**: Check all chess rules (check, castling, en passant)
- **Performance**: Fast validation (< 10ms)

**Implementation:**
```python
class MoveValidator:
    def __init__(self):
        self.chess_engine = ChessEngine()
    
    def is_valid_move(self, board_state, from_square, to_square, color):
        """Validate if move is legal"""
        try:
            # Parse board state
            board = self.chess_engine.parse_fen(board_state)
            
            # Check if it's the correct color's turn
            if board.turn != color:
                return False
            
            # Check if move is legal
            move = self.chess_engine.create_move(from_square, to_square)
            if move not in board.legal_moves:
                return False
            
            return True
        except Exception as e:
            return False
    
    def validate_move_details(self, board_state, from_square, to_square, promotion=None):
        """Validate move and return details"""
        board = self.chess_engine.parse_fen(board_state)
        move = self.chess_engine.create_move(from_square, to_square, promotion)
        
        if move not in board.legal_moves:
            raise InvalidMoveError("Illegal move")
        
        # Get move details
        piece = board.piece_at(from_square)
        captured_piece = board.piece_at(to_square)
        is_castle = board.is_castling(move)
        is_en_passant = board.is_en_passant(move)
        
        # Make move to check for check/checkmate
        board.push(move)
        is_check = board.is_check()
        is_checkmate = board.is_checkmate()
        board.pop()
        
        return {
            'piece': piece.symbol(),
            'captured_piece': captured_piece.symbol() if captured_piece else None,
            'is_castle': is_castle,
            'is_en_passant': is_en_passant,
            'is_check': is_check,
            'is_checkmate': is_checkmate
        }
```

### Detailed Design

#### Unlimited Undo Implementation

**Challenge:** Support unlimited undo while maintaining performance

**Solution:**
- **Move History**: Store all moves in database
- **Undo Stack**: Maintain undo stack in memory
- **Board State Reconstruction**: Reconstruct from move history
- **Efficient Storage**: Store FEN strings for board states

**Implementation:**
```python
def undo_unlimited(self, game_id, move_count):
    """Undo any number of moves"""
    # Get all moves up to current position
    current_moves = self.db.get_moves_up_to_current(game_id)
    
    if len(current_moves) < move_count:
        raise InvalidOperationError("Not enough moves to undo")
    
    # Undo moves
    moves_to_undo = current_moves[-move_count:]
    
    for move in reversed(moves_to_undo):
        move.is_undone = True
        move.save()
        
        # Create undo history
        undo_history = UndoHistory(
            game_id=game_id,
            move_id=move.move_id,
            move_number=move.move_number
        )
        undo_history.save()
    
    # Reconstruct board state
    remaining_moves = current_moves[:-move_count]
    if remaining_moves:
        last_move = remaining_moves[-1]
        board_state = last_move.board_state_after
        move_count = last_move.move_number
    else:
        board_state = self.get_initial_board_state()
        move_count = 0
    
    # Update game
    game = self.get_game(game_id)
    game.board_state = board_state
    game.move_count = move_count
    game.current_turn = 'white' if move_count % 2 == 0 else 'black'
    game.save()
```

#### ELO Rating Calculation

**Challenge:** Calculate accurate ELO ratings

**Solution:**
- **Standard ELO Formula**: Use proven ELO formula
- **K-Factor Adjustment**: Adjust K-factor based on player strength
- **Expected Score**: Calculate expected score from rating difference
- **Rating Update**: Update based on actual vs expected score

**Formula:**
```
Expected Score = 1 / (1 + 10^((Opponent Rating - Player Rating) / 400))
ELO Change = K * (Actual Score - Expected Score)
New Rating = Old Rating + ELO Change
```

### Scalability Considerations

#### Horizontal Scaling

**Game Service:**
- Stateless service, horizontally scalable
- Multiple instances behind load balancer
- Shared database and cache
- WebSocket connections distributed

#### Caching Strategy

**Redis Cache:**
- **Active Games**: Cache active game states
- **Recent Moves**: Cache recent move history
- **Player ELO**: Cache player ELO ratings
- **TTL**: 1 hour for active games

### Security Considerations

#### Move Validation

- **Server-Side Validation**: Always validate moves server-side
- **Cheat Prevention**: Detect impossible moves
- **Rate Limiting**: Limit move rate per player

#### Game Integrity

- **State Verification**: Verify game state consistency
- **Move Ordering**: Ensure moves are processed in order
- **Undo Restrictions**: Prevent undo abuse

### Monitoring & Observability

#### Key Metrics

**Game Metrics:**
- Active games count
- Moves per second
- Undo operations per second
- Average game duration
- Games completed per day

**Performance Metrics:**
- Move processing latency
- Undo operation latency
- ELO calculation latency
- WebSocket message latency

**Business Metrics:**
- Total players
- Average ELO rating
- Games played per player
- ELO distribution

### Trade-offs and Optimizations

#### Trade-offs

**1. Undo Storage: Full History vs Snapshot**
- **Full History**: More storage, faster undo
- **Snapshot**: Less storage, slower undo
- **Decision**: Full history for unlimited undo

**2. Board State: FEN vs Full State**
- **FEN**: Compact, requires parsing
- **Full State**: Larger, faster access
- **Decision**: FEN for storage, parsed in memory

**3. ELO Update: Real-Time vs Batch**
- **Real-Time**: Immediate updates, higher load
- **Batch**: Delayed updates, lower load
- **Decision**: Real-time for user experience

#### Optimizations

**1. Move History Compression**
- Compress move history
- Reduce storage
- Improve performance

**2. Board State Caching**
- Cache parsed board states
- Reduce parsing overhead
- Improve move validation speed

**3. Batch ELO Updates**
- Batch ELO calculations
- Reduce database writes
- Improve throughput

## Summary

Designing a chess game system with unlimited undo and ELO rating requires careful consideration of:

1. **Game State Management**: Efficient board state representation and storage
2. **Unlimited Undo**: Complete move history with efficient undo/redo
3. **Move Validation**: Fast and accurate move validation
4. **ELO Calculation**: Accurate rating system with proper K-factors
5. **Real-Time Updates**: WebSocket-based real-time game updates
6. **Move History**: Complete move history for replay and analysis
7. **Scalability**: Handle 10K+ moves per second
8. **Data Integrity**: Accurate game state and ELO ratings
9. **Performance**: Sub-100ms move processing
10. **Undo/Redo**: Efficient undo/redo with state reconstruction

Key architectural decisions:
- **FEN Notation** for board state representation
- **Complete Move History** for unlimited undo
- **Standard ELO Formula** for rating calculation
- **Sharded Database** for move storage
- **WebSocket** for real-time updates
- **Redis Cache** for active game states
- **Horizontal Scaling** for all services

The system handles 10,000 moves per second, supports unlimited undo operations, maintains accurate ELO ratings, and provides real-time gameplay with sub-200ms update latency.

