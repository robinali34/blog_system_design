---
layout: post
title: "Design a Text Editor - Meta System Design Interview"
date: 2025-11-24
categories: [System Design, Interview Example, Meta, Data Structures, Algorithms, Memory Efficiency]
excerpt: "A comprehensive guide to designing a text editor focusing on data structures (rope, gap buffer), command handling, undo/redo logic, and memory-efficient design. Meta interview question emphasizing algorithmic and memory-efficient design, not distributed syncing."
---

## Introduction

Designing a text editor is a Meta interview question that tests your understanding of efficient data structures for text manipulation, command patterns, and memory management. This question focuses on:

- **Data structures**: Rope, gap buffer, piece table
- **Command handling**: Insert, delete, undo/redo
- **Memory efficiency**: Handling large files
- **Performance**: Fast insertions/deletions

This guide covers the design of a text editor with efficient data structures and undo/redo functionality.

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Requirements](#requirements)
3. [Data Structure Options](#data-structure-options)
4. [Gap Buffer Implementation](#gap-buffer-implementation)
5. [Rope Implementation](#rope-implementation)
6. [Command Pattern](#command-pattern)
7. [Undo/Redo System](#undoredo-system)
8. [Implementation](#implementation)
9. [Summary](#summary)

## Problem Statement

**Design a text editor that:**

1. **Handles text insertion** efficiently
2. **Handles text deletion** efficiently
3. **Supports undo/redo** operations
4. **Handles large files** (MB to GB)
5. **Supports cursor movement** and selection
6. **Provides fast operations** (< 10ms for typical operations)

**Scale Requirements:**
- Support files from KB to GB
- Fast insert/delete: O(log n) or better
- Memory efficient
- Handle millions of operations

## Requirements

### Functional Requirements

1. **Insert Text**: Insert text at cursor position
2. **Delete Text**: Delete text at cursor or selection
3. **Move Cursor**: Move cursor position
4. **Select Text**: Select text range
5. **Undo**: Undo last operation
6. **Redo**: Redo undone operation
7. **Get Text**: Retrieve full or partial text

### Non-Functional Requirements

**Performance:**
- Fast insertions: O(log n) or O(1) amortized
- Fast deletions: O(log n) or O(1) amortized
- Efficient memory usage

**Reliability:**
- Correct undo/redo
- No data loss
- Handle edge cases

## Data Structure Options

### 1. Simple String (Naive)
- **Pros**: Simple, O(1) access
- **Cons**: O(n) insert/delete
- **Use**: Small files only

### 2. Gap Buffer (Recommended for Meta Interview)
- **Pros**: O(1) insert/delete at cursor, simple
- **Cons**: O(n) for cursor movement far from gap
- **Use**: Good for typical editing

### 3. Rope (Best for Large Files)
- **Pros**: O(log n) operations, handles large files
- **Cons**: More complex implementation
- **Use**: Large files, complex operations

### 4. Piece Table
- **Pros**: Efficient for large files, good undo
- **Cons**: Complex implementation
- **Use**: Professional editors

## Gap Buffer Implementation

### Gap Buffer Data Structure

```python
class GapBuffer:
    def __init__(self, initial_text: str = ""):
        # Buffer with gap in the middle
        self.buffer = list(initial_text)
        self.gap_start = len(initial_text)
        self.gap_end = len(initial_text) + 10  # Initial gap size
        self.buffer.extend(['\0'] * 10)  # Gap represented by null chars
        self.cursor = 0
    
    def insert(self, text: str):
        """Insert text at cursor position."""
        for char in text:
            # Move gap to cursor if needed
            self._move_gap_to_cursor()
            
            # Insert character
            self.buffer[self.gap_start] = char
            self.gap_start += 1
            self.cursor += 1
            
            # Expand gap if needed
            if self.gap_start >= self.gap_end:
                self._expand_gap()
    
    def delete(self, count: int = 1):
        """Delete characters before cursor."""
        if count <= 0:
            return
        
        # Move gap to cursor
        self._move_gap_to_cursor()
        
        # Delete by moving gap forward
        delete_count = min(count, self.cursor)
        self.gap_start -= delete_count
        self.cursor -= delete_count
    
    def delete_forward(self, count: int = 1):
        """Delete characters after cursor."""
        if count <= 0:
            return
        
        # Move gap to cursor
        self._move_gap_to_cursor()
        
        # Delete by moving gap end
        available = len(self.buffer) - self.gap_end
        delete_count = min(count, available)
        self.gap_end += delete_count
    
    def move_cursor(self, position: int):
        """Move cursor to position."""
        self.cursor = max(0, min(position, len(self)))
    
    def get_text(self) -> str:
        """Get full text."""
        return ''.join(self.buffer[:self.gap_start] + self.buffer[self.gap_end:])
    
    def get_text_range(self, start: int, end: int) -> str:
        """Get text in range."""
        text = self.get_text()
        return text[start:end]
    
    def _move_gap_to_cursor(self):
        """Move gap to cursor position."""
        if self.cursor == self.gap_start:
            return  # Gap already at cursor
        
        if self.cursor < self.gap_start:
            # Move gap left
            move_count = self.gap_start - self.cursor
            self.buffer[self.gap_end - move_count:self.gap_end] = \
                self.buffer[self.cursor:self.gap_start]
            self.gap_start = self.cursor
            self.gap_end -= move_count
        else:
            # Move gap right
            move_count = self.cursor - self.gap_start
            self.buffer[self.gap_start:self.gap_start + move_count] = \
                self.buffer[self.gap_end:self.gap_end + move_count]
            self.gap_start = self.cursor
            self.gap_end += move_count
    
    def _expand_gap(self):
        """Expand gap size."""
        expansion = max(10, len(self.buffer) // 2)
        insert_pos = self.gap_start
        self.buffer[insert_pos:insert_pos] = ['\0'] * expansion
        self.gap_end += expansion
    
    def __len__(self) -> int:
        """Get text length."""
        return len(self.buffer) - (self.gap_end - self.gap_start)
```

## Rope Implementation

### Rope Data Structure

```python
class RopeNode:
    def __init__(self, text: str = "", left=None, right=None):
        self.text = text
        self.left = left
        self.right = right
        self.length = len(text)
        if left:
            self.length += left.length
        if right:
            self.length += right.length
    
    def get_char(self, index: int) -> str:
        """Get character at index."""
        if self.left:
            if index < self.left.length:
                return self.left.get_char(index)
            index -= self.left.length
        
        if index < len(self.text):
            return self.text[index]
        
        if self.right:
            return self.right.get_char(index - len(self.text))
        
        raise IndexError("Index out of range")
    
    def get_text(self, start: int = 0, end: int = None) -> str:
        """Get text in range."""
        if end is None:
            end = self.length
        
        result = []
        if self.left and start < self.left.length:
            left_end = min(end, self.left.length)
            result.append(self.left.get_text(start, left_end))
            start = max(0, start - self.left.length)
            end -= self.left.length
        
        if start < len(self.text):
            text_start = max(0, start)
            text_end = min(len(self.text), end)
            result.append(self.text[text_start:text_end])
            end -= len(self.text)
        
        if self.right and end > 0:
            result.append(self.right.get_text(0, end))
        
        return ''.join(result)

class Rope:
    def __init__(self, text: str = ""):
        self.root = RopeNode(text) if text else None
        self.leaf_size = 10  # Max characters per leaf
    
    def insert(self, position: int, text: str):
        """Insert text at position."""
        if not self.root:
            self.root = RopeNode(text)
            return
        
        left, right = self._split(self.root, position)
        new_node = RopeNode(text)
        self.root = self._concat(left, self._concat(new_node, right))
    
    def delete(self, start: int, end: int):
        """Delete text in range."""
        if not self.root:
            return
        
        left, temp = self._split(self.root, start)
        _, right = self._split(temp, end - start)
        self.root = self._concat(left, right)
    
    def get_text(self) -> str:
        """Get full text."""
        if not self.root:
            return ""
        return self.root.get_text()
    
    def _split(self, node: RopeNode, position: int) -> tuple:
        """Split rope at position."""
        if not node:
            return None, None
        
        if position <= 0:
            return None, node
        
        if position >= node.length:
            return node, None
        
        if node.left:
            if position < node.left.length:
                left_left, left_right = self._split(node.left, position)
                return left_left, self._concat(left_right, node.right)
            position -= node.left.length
        
        if position < len(node.text):
            left_text = node.text[:position]
            right_text = node.text[position:]
            return (
                self._concat(node.left, RopeNode(left_text)),
                RopeNode(right_text, node.right)
            )
        
        if node.right:
            right_left, right_right = self._split(node.right, position - len(node.text))
            return (
                self._concat(node.left, RopeNode(node.text, None, right_left)),
                right_right
            )
        
        return node, None
    
    def _concat(self, left: RopeNode, right: RopeNode) -> RopeNode:
        """Concatenate two ropes."""
        if not left:
            return right
        if not right:
            return left
        return RopeNode("", left, right)
```

## Command Pattern

### Command Interface

```python
from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self):
        pass
    
    @abstractmethod
    def undo(self):
        pass

class InsertCommand(Command):
    def __init__(self, editor, position: int, text: str):
        self.editor = editor
        self.position = position
        self.text = text
    
    def execute(self):
        self.editor.insert(self.position, self.text)
    
    def undo(self):
        self.editor.delete(self.position, self.position + len(self.text))

class DeleteCommand(Command):
    def __init__(self, editor, start: int, end: int):
        self.editor = editor
        self.start = start
        self.end = end
        self.deleted_text = None
    
    def execute(self):
        self.deleted_text = self.editor.get_text_range(self.start, self.end)
        self.editor.delete(self.start, self.end)
    
    def undo(self):
        if self.deleted_text:
            self.editor.insert(self.start, self.deleted_text)
```

## Undo/Redo System

### Undo/Redo Manager

```python
class TextEditor:
    def __init__(self, initial_text: str = ""):
        self.buffer = GapBuffer(initial_text)
        self.undo_stack = []
        self.redo_stack = []
        self.cursor = 0
    
    def insert(self, position: int, text: str):
        """Insert text with undo support."""
        command = InsertCommand(self, position, text)
        command.execute()
        self.undo_stack.append(command)
        self.redo_stack.clear()  # Clear redo on new action
        self.cursor = position + len(text)
    
    def delete(self, start: int, end: int):
        """Delete text with undo support."""
        command = DeleteCommand(self, start, end)
        command.execute()
        self.undo_stack.append(command)
        self.redo_stack.clear()
        self.cursor = start
    
    def undo(self):
        """Undo last operation."""
        if not self.undo_stack:
            return
        
        command = self.undo_stack.pop()
        command.undo()
        self.redo_stack.append(command)
    
    def redo(self):
        """Redo last undone operation."""
        if not self.redo_stack:
            return
        
        command = self.redo_stack.pop()
        command.execute()
        self.undo_stack.append(command)
    
    def get_text(self) -> str:
        """Get full text."""
        return self.buffer.get_text()
    
    def get_text_range(self, start: int, end: int) -> str:
        """Get text in range."""
        return self.buffer.get_text_range(start, end)
```

## Implementation

### Complete Example

```python
# Create editor
editor = TextEditor("Hello World")

# Insert text
editor.insert(5, ", Beautiful")
print(editor.get_text())  # "Hello, Beautiful World"

# Delete text
editor.delete(5, 16)
print(editor.get_text())  # "Hello World"

# Undo
editor.undo()
print(editor.get_text())  # "Hello, Beautiful World"

# Redo
editor.redo()
print(editor.get_text())  # "Hello World"
```

## What Interviewers Look For

### Data Structures Knowledge

1. **Understanding of Text Data Structures**
   - Gap buffer vs Rope trade-offs
   - When to use which structure
   - Complexity analysis
   - **Red Flags**: No understanding of trade-offs, wrong choice

2. **Algorithm Efficiency**
   - O(1) vs O(log n) operations
   - Memory efficiency
   - **Red Flags**: Inefficient algorithms, high memory usage

### Command Pattern Implementation

1. **Undo/Redo Design**
   - Command pattern usage
   - Stack-based implementation
   - **Red Flags**: No undo/redo, incorrect implementation

2. **Command Encapsulation**
   - Proper command interface
   - Execute/undo methods
   - **Red Flags**: Poor encapsulation, no undo

### Problem-Solving Approach

1. **Large File Handling**
   - Memory-efficient approaches
   - Lazy loading considerations
   - **Red Flags**: Loads entire file, memory issues

2. **Performance Optimization**
   - Efficient insertions/deletions
   - Cursor movement optimization
   - **Red Flags**: Slow operations, no optimization

### Code Quality

1. **Algorithm Implementation**
   - Correct gap buffer/rope implementation
   - Proper edge case handling
   - **Red Flags**: Incorrect implementation, bugs

2. **Memory Management**
   - Efficient memory usage
   - No memory leaks
   - **Red Flags**: High memory usage, leaks

### Meta-Specific Focus

1. **Data Structures Mastery**
   - Deep understanding of structures
   - Trade-off analysis
   - **Key**: Show strong CS fundamentals

2. **Algorithmic Thinking**
   - Complexity analysis
   - Optimization strategies
   - **Key**: Demonstrate algorithmic skills

## Summary

### Key Takeaways

1. **Data Structures**: Gap buffer (simple), Rope (complex, efficient)
2. **Insert/Delete**: O(1) with gap buffer, O(log n) with rope
3. **Undo/Redo**: Command pattern with stacks
4. **Large Files**: Rope handles GB files efficiently
5. **Memory**: Gap buffer expands as needed, rope uses tree structure

### Common Interview Questions

1. **How would you efficiently insert/delete text?**
   - Gap buffer: O(1) at cursor, move gap as needed
   - Rope: O(log n) with tree structure

2. **How would you implement undo/redo?**
   - Command pattern: Each operation is a command
   - Undo stack: Store executed commands
   - Redo stack: Store undone commands

3. **How would you handle large files?**
   - Rope: Tree structure, O(log n) operations
   - Piece table: Store original + changes
   - Lazy loading: Load file in chunks

Understanding text editor design is crucial for Meta interviews focusing on:
- Data structures
- Algorithms
- Memory efficiency
- Command patterns
- Performance optimization

