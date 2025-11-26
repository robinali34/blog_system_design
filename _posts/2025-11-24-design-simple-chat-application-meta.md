---
layout: post
title: "Design a Simple Chat Application - Meta System Design Interview"
date: 2025-11-24
categories: [System Design, Interview Example, Meta, Object-Oriented Modeling, Message Queues, Persistence]
excerpt: "A comprehensive guide to designing a simple chat application focusing on object-oriented modeling, message queues (local), persistence, and read/unread state. Meta interview question emphasizing data structures and correct modeling of user interactions, not on multi-server messaging."
---

## Introduction

Designing a simple chat application is a Meta interview question that tests your ability to model messaging systems, handle message persistence, and manage conversation state. This question focuses on:

- **Object-oriented modeling**: Users, Messages, Conversations
- **Message queues**: Local message handling
- **Persistence**: Storing messages and conversations
- **State management**: Read/unread status, online/offline

This guide covers the design of a simple chat application with proper entity modeling and message handling.

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Requirements](#requirements)
3. [Data Modeling](#data-modeling)
4. [Class Design](#class-design)
5. [Message Handling](#message-handling)
6. [Read/Unread State](#readunread-state)
7. [Message History](#message-history)
8. [Implementation](#implementation)
9. [Summary](#summary)

## Problem Statement

**Design a simple chat application that:**

1. **Manages users** and conversations
2. **Handles messages** (send, receive, store)
3. **Tracks read/unread** status
4. **Stores message history** for retrieval
5. **Supports conversations** (1-on-1, group)
6. **Handles online/offline** status

**Scale Requirements:**
- Support 1K-100K users
- Support 10K-1M messages
- Fast message delivery: < 50ms
- Efficient history retrieval

## Requirements

### Functional Requirements

1. **Send Message**: Send message to user or group
2. **Receive Message**: Receive and display messages
3. **Mark as Read**: Mark messages as read
4. **Get History**: Retrieve conversation history
5. **Create Conversation**: Start new conversation
6. **Get Unread Count**: Get unread message count

### Non-Functional Requirements

**Performance:**
- Fast message delivery
- Efficient history retrieval
- Quick read status updates

**Consistency:**
- No message loss
- Accurate read status
- Correct message ordering

## Data Modeling

### Database Schema

```sql
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'offline',  -- online, offline, away
    last_seen TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username)
);

CREATE TABLE conversations (
    conversation_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    conversation_type VARCHAR(20) DEFAULT 'direct',  -- direct, group
    name VARCHAR(100) NULL,  -- For group chats
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE conversation_participants (
    participant_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    conversation_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_read_at TIMESTAMP NULL,
    UNIQUE KEY unique_conversation_user (conversation_id, user_id),
    INDEX idx_user_id (user_id),
    INDEX idx_conversation_id (conversation_id),
    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE messages (
    message_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    conversation_id BIGINT NOT NULL,
    sender_id BIGINT NOT NULL,
    content TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text',  -- text, image, file
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_conversation_id (conversation_id),
    INDEX idx_created_at (created_at),
    INDEX idx_sender_id (sender_id),
    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id),
    FOREIGN KEY (sender_id) REFERENCES users(user_id)
);

CREATE TABLE message_reads (
    read_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    message_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_message_user (message_id, user_id),
    INDEX idx_message_id (message_id),
    INDEX idx_user_id (user_id),
    FOREIGN KEY (message_id) REFERENCES messages(message_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

### Data Model Classes

```python
from enum import Enum
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass

class ConversationType(Enum):
    DIRECT = "direct"
    GROUP = "group"

class UserStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    AWAY = "away"

@dataclass
class User:
    user_id: Optional[int]
    username: str
    email: str
    status: UserStatus
    last_seen: Optional[datetime]

@dataclass
class Conversation:
    conversation_id: Optional[int]
    conversation_type: ConversationType
    name: Optional[str]
    created_at: datetime
    updated_at: datetime
    participants: List[int]  # user_ids

@dataclass
class Message:
    message_id: Optional[int]
    conversation_id: int
    sender_id: int
    content: str
    message_type: str
    created_at: datetime
    read_by: List[int] = None  # user_ids who read
    
    def __post_init__(self):
        if self.read_by is None:
            self.read_by = []
```

## Class Design

### Chat Application

```python
class ChatApplication:
    def __init__(self, db):
        self.db = db
        self.message_queue = {}  # conversation_id -> List[Message]
        self.online_users = set()  # user_id set
    
    def create_user(self, username: str, email: str) -> User:
        """Create new user."""
        user = User(
            user_id=None,
            username=username,
            email=email,
            status=UserStatus.OFFLINE,
            last_seen=None
        )
        return self.db.create_user(user)
    
    def create_conversation(self, user_ids: List[int], 
                           conversation_type: ConversationType = ConversationType.DIRECT,
                           name: Optional[str] = None) -> Conversation:
        """Create new conversation."""
        if conversation_type == ConversationType.DIRECT and len(user_ids) != 2:
            raise ValueError("Direct conversation requires exactly 2 users")
        
        conversation = Conversation(
            conversation_id=None,
            conversation_type=conversation_type,
            name=name,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            participants=user_ids
        )
        
        conversation = self.db.create_conversation(conversation)
        
        # Add participants
        for user_id in user_ids:
            self.db.add_participant(conversation.conversation_id, user_id)
        
        return conversation
    
    def send_message(self, conversation_id: int, sender_id: int, 
                    content: str, message_type: str = 'text') -> Message:
        """Send message to conversation."""
        # Validate conversation and sender
        conversation = self.db.get_conversation(conversation_id)
        if not conversation:
            raise ValueError("Conversation not found")
        
        if sender_id not in conversation.participants:
            raise ValueError("User not in conversation")
        
        # Create message
        message = Message(
            message_id=None,
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=content,
            message_type=message_type,
            created_at=datetime.now()
        )
        
        message = self.db.create_message(message)
        
        # Update conversation timestamp
        conversation.updated_at = datetime.now()
        self.db.update_conversation(conversation)
        
        # Add to message queue for real-time delivery
        if conversation_id not in self.message_queue:
            self.message_queue[conversation_id] = []
        self.message_queue[conversation_id].append(message)
        
        return message
    
    def get_messages(self, conversation_id: int, user_id: int,
                    limit: int = 50, offset: int = 0) -> List[Message]:
        """Get conversation messages."""
        # Validate user is participant
        if not self.db.is_participant(conversation_id, user_id):
            raise ValueError("User not in conversation")
        
        messages = self.db.get_messages(conversation_id, limit=limit, offset=offset)
        
        # Mark as read for this user
        unread_messages = [m for m in messages if user_id not in m.read_by]
        for message in unread_messages:
            self.mark_as_read(message.message_id, user_id)
        
        return messages
    
    def mark_as_read(self, message_id: int, user_id: int) -> bool:
        """Mark message as read."""
        message = self.db.get_message(message_id)
        if not message:
            return False
        
        # Check if already read
        if self.db.is_message_read(message_id, user_id):
            return True
        
        # Mark as read
        self.db.mark_message_read(message_id, user_id)
        
        # Update participant's last_read_at
        self.db.update_participant_last_read(message.conversation_id, user_id)
        
        return True
    
    def mark_conversation_as_read(self, conversation_id: int, user_id: int):
        """Mark all messages in conversation as read."""
        # Get unread messages
        unread_messages = self.db.get_unread_messages(conversation_id, user_id)
        
        for message in unread_messages:
            self.mark_as_read(message.message_id, user_id)
        
        # Update last_read_at
        self.db.update_participant_last_read(conversation_id, user_id)
    
    def get_unread_count(self, user_id: int) -> dict:
        """Get unread message count per conversation."""
        conversations = self.db.get_user_conversations(user_id)
        unread_counts = {}
        
        for conversation in conversations:
            count = self.db.get_unread_count(conversation.conversation_id, user_id)
            if count > 0:
                unread_counts[conversation.conversation_id] = count
        
        return unread_counts
    
    def get_conversation_history(self, conversation_id: int, user_id: int,
                                limit: int = 50) -> List[Message]:
        """Get conversation history."""
        if not self.db.is_participant(conversation_id, user_id):
            raise ValueError("User not in conversation")
        
        return self.db.get_messages(conversation_id, limit=limit)
    
    def set_user_status(self, user_id: int, status: UserStatus):
        """Set user online/offline status."""
        user = self.db.get_user(user_id)
        if not user:
            return
        
        user.status = status
        user.last_seen = datetime.now()
        self.db.update_user(user)
        
        if status == UserStatus.ONLINE:
            self.online_users.add(user_id)
        else:
            self.online_users.discard(user_id)
```

## Message Handling

### Local Message Queue

```python
class ChatApplication:
    def __init__(self, db):
        # ... existing code ...
        self.message_queue = {}  # conversation_id -> queue.Queue
    
    def send_message(self, conversation_id: int, sender_id: int, content: str) -> Message:
        """Send message with queue."""
        # ... create message ...
        
        # Add to queue for delivery
        if conversation_id not in self.message_queue:
            self.message_queue[conversation_id] = queue.Queue()
        
        self.message_queue[conversation_id].put(message)
        
        # Notify participants (in real system, use WebSocket/SSE)
        self._notify_participants(conversation_id, message)
        
        return message
    
    def get_pending_messages(self, conversation_id: int, user_id: int) -> List[Message]:
        """Get pending messages from queue."""
        if conversation_id not in self.message_queue:
            return []
        
        messages = []
        queue_obj = self.message_queue[conversation_id]
        
        while not queue_obj.empty():
            try:
                message = queue_obj.get_nowait()
                # Only return messages not from this user
                if message.sender_id != user_id:
                    messages.append(message)
            except queue.Empty:
                break
        
        return messages
    
    def _notify_participants(self, conversation_id: int, message: Message):
        """Notify conversation participants of new message."""
        conversation = self.db.get_conversation(conversation_id)
        for user_id in conversation.participants:
            if user_id != message.sender_id and user_id in self.online_users:
                # Send notification (in real system, push via WebSocket)
                pass
```

## Read/Unread State

### Efficient Read Tracking

```python
class ChatApplication:
    def get_unread_messages(self, conversation_id: int, user_id: int) -> List[Message]:
        """Get unread messages for user."""
        # Get participant's last_read_at
        participant = self.db.get_participant(conversation_id, user_id)
        if not participant or not participant.last_read_at:
            # No read timestamp, all messages are unread
            return self.db.get_messages(conversation_id)
        
        # Get messages after last_read_at
        return self.db.get_messages_after(conversation_id, participant.last_read_at)
    
    def get_unread_count_fast(self, conversation_id: int, user_id: int) -> int:
        """Fast unread count using last_read_at."""
        participant = self.db.get_participant(conversation_id, user_id)
        if not participant or not participant.last_read_at:
            return self.db.get_message_count(conversation_id)
        
        return self.db.get_message_count_after(conversation_id, participant.last_read_at)
```

## Message History

### Pagination

```python
class ChatApplication:
    def get_message_history(self, conversation_id: int, user_id: int,
                           page: int = 1, page_size: int = 50) -> dict:
        """Get message history with pagination."""
        if not self.db.is_participant(conversation_id, user_id):
            raise ValueError("User not in conversation")
        
        offset = (page - 1) * page_size
        messages = self.db.get_messages(conversation_id, limit=page_size, offset=offset)
        total = self.db.get_message_count(conversation_id)
        
        return {
            'messages': messages,
            'page': page,
            'page_size': page_size,
            'total': total,
            'total_pages': (total + page_size - 1) // page_size
        }
```

## Implementation

### Complete Example

```python
# Initialize
db = Database()
chat_app = ChatApplication(db)

# Create users
user1 = chat_app.create_user("alice", "alice@example.com")
user2 = chat_app.create_user("bob", "bob@example.com")

# Create conversation
conversation = chat_app.create_conversation([user1.user_id, user2.user_id])

# Send messages
message1 = chat_app.send_message(conversation.conversation_id, user1.user_id, "Hello!")
message2 = chat_app.send_message(conversation.conversation_id, user2.user_id, "Hi there!")

# Get messages
messages = chat_app.get_messages(conversation.conversation_id, user1.user_id)

# Mark as read
chat_app.mark_as_read(message2.message_id, user1.user_id)

# Get unread count
unread = chat_app.get_unread_count(user1.user_id)
```

## What Interviewers Look For

### Object-Oriented Modeling Skills

1. **Entity Design**
   - Proper modeling of User, Message, Conversation
   - Clear relationships and responsibilities
   - **Red Flags**: Unclear entities, poor relationships

2. **State Management**
   - Read/unread state tracking
   - Online/offline status
   - **Red Flags**: Missing state, incorrect tracking

### Message Handling

1. **Message Queue Design**
   - Local queue implementation
   - Message delivery logic
   - **Red Flags**: No queue, incorrect delivery

2. **Persistence Strategy**
   - Message storage
   - History retrieval
   - **Red Flags**: No persistence, inefficient retrieval

### Problem-Solving Approach

1. **Read/Unread Tracking**
   - Efficient tracking mechanism
   - last_read_at approach
   - **Red Flags**: Inefficient tracking, wrong approach

2. **Message History**
   - Pagination implementation
   - Efficient queries
   - **Red Flags**: No pagination, slow queries

3. **Edge Cases**
   - Group conversations
   - Message ordering
   - Concurrent messages
   - **Red Flags**: Ignoring edge cases

### Code Quality

1. **Data Consistency**
   - Accurate read status
   - Correct message ordering
   - **Red Flags**: Wrong status, incorrect ordering

2. **Error Handling**
   - Validation of operations
   - Meaningful errors
   - **Red Flags**: No validation, unclear errors

### Meta-Specific Focus

1. **Local System Design**
   - No distributed messaging
   - Focus on data structures
   - **Key**: Show local system understanding

2. **State Management**
   - Proper state tracking
   - Efficient updates
   - **Key**: Demonstrate state management skills

## Summary

### Key Takeaways

1. **Entity Modeling**: Users, Conversations, Messages, Participants
2. **Message Handling**: Send, receive, store, queue
3. **Read/Unread State**: Track with last_read_at timestamp
4. **Message History**: Pagination for efficient retrieval
5. **State Management**: Online/offline, read status

### Common Interview Questions

1. **How would you model Users, Messages, and Conversations?**
   - Users: user_id, username, status
   - Messages: message_id, conversation_id, sender_id, content
   - Conversations: conversation_id, type, participants

2. **How would you mark messages as read/unread?**
   - Track last_read_at per participant
   - Messages after last_read_at are unread
   - Update on read action

3. **How would you handle message history retrieval?**
   - Pagination: limit/offset
   - Index on conversation_id, created_at
   - Efficient queries with proper indexes

Understanding chat application design is crucial for Meta interviews focusing on:
- Object-oriented modeling
- Message handling
- State management
- Persistence
- Read/unread tracking

