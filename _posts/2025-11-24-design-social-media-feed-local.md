---
layout: post
title: "Design a Social Media Feed (Local / Single-User) - System Design Interview"
date: 2025-11-24
categories: [System Design, Interview Example, Data Modeling, Sorting, Local Caching]
excerpt: "A comprehensive guide to designing a local social media feed focusing on data modeling, sorting/filtering, and local caching. Interview question emphasizing basic feed generation without distributed concerns like sharding."
---

## Introduction

Designing a social media feed is a system design interview question that tests your ability to model social media entities, implement feed generation algorithms, and handle local data efficiently. This question focuses on:

- **Data modeling**: Posts, comments, likes, users
- **Feed generation**: Sorting, filtering, pagination
- **Local caching**: Efficient retrieval
- **Content management**: Deletion, edits, updates

This guide covers the design of a local social media feed system with proper data modeling and efficient feed generation.

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Requirements](#requirements)
3. [Data Modeling](#data-modeling)
4. [Feed Generation](#feed-generation)
5. [Sorting and Filtering](#sorting-and-filtering)
6. [Content Management](#content-management)
7. [Implementation](#implementation)
8. [Summary](#summary)

## Problem Statement

**Design a local social media feed system that:**

1. **Stores posts** (text, images, timestamps)
2. **Stores comments** and likes on posts
3. **Generates user timeline** (posts from followed users)
4. **Supports sorting** (chronological, popularity)
5. **Handles content deletion** and edits
6. **Provides efficient retrieval** (< 100ms)

**Scale Requirements:**
- Support 10K-1M posts
- Support 100K-10M comments/likes
- Fast feed generation: < 100ms
- Efficient storage and retrieval

## Requirements

### Functional Requirements

1. **Create Post**: Create new post
2. **Get Feed**: Get user's timeline feed
3. **Add Comment**: Comment on post
4. **Like Post**: Like/unlike post
5. **Delete Post**: Delete post and related data
6. **Edit Post**: Update post content
7. **Follow/Unfollow**: Manage user relationships

### Non-Functional Requirements

**Performance:**
- Fast feed generation
- Efficient sorting
- Quick content retrieval

**Consistency:**
- Accurate feed content
- Handle deletions properly
- Update on edits

## Data Modeling

### Database Schema

```sql
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username)
);

CREATE TABLE posts (
    post_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    content TEXT NOT NULL,
    post_type VARCHAR(20) DEFAULT 'text',  -- text, image, video
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    like_count INT DEFAULT 0,
    comment_count INT DEFAULT 0,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    INDEX idx_deleted_at (deleted_at),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE comments (
    comment_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    post_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    INDEX idx_post_id (post_id),
    INDEX idx_user_id (user_id),
    FOREIGN KEY (post_id) REFERENCES posts(post_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE likes (
    like_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    post_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_post_user (post_id, user_id),
    INDEX idx_post_id (post_id),
    INDEX idx_user_id (user_id),
    FOREIGN KEY (post_id) REFERENCES posts(post_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE follows (
    follow_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    follower_id BIGINT NOT NULL,
    followee_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_follow (follower_id, followee_id),
    INDEX idx_follower (follower_id),
    INDEX idx_followee (followee_id),
    FOREIGN KEY (follower_id) REFERENCES users(user_id),
    FOREIGN KEY (followee_id) REFERENCES users(user_id)
);
```

### Data Model Classes

```python
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class User:
    user_id: Optional[int]
    username: str
    email: str
    created_at: datetime

@dataclass
class Post:
    post_id: Optional[int]
    user_id: int
    content: str
    post_type: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]
    like_count: int
    comment_count: int
    user: Optional[User] = None  # For convenience
    
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

@dataclass
class Comment:
    comment_id: Optional[int]
    post_id: int
    user_id: int
    content: str
    created_at: datetime
    deleted_at: Optional[datetime]

@dataclass
class Like:
    like_id: Optional[int]
    post_id: int
    user_id: int
    created_at: datetime
```

## Feed Generation

### Basic Feed Generation

```python
class SocialMediaFeed:
    def __init__(self, db):
        self.db = db
    
    def get_user_feed(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Post]:
        """Get user's timeline feed."""
        # Get users that this user follows
        followees = self.db.get_followees(user_id)
        followee_ids = [f.followee_id for f in followees]
        
        # Include own posts
        followee_ids.append(user_id)
        
        # Get posts from followed users
        posts = self.db.get_posts_by_users(followee_ids, limit=limit, offset=offset)
        
        # Filter deleted posts
        posts = [p for p in posts if not p.is_deleted()]
        
        # Sort by created_at (newest first)
        posts.sort(key=lambda p: p.created_at, reverse=True)
        
        return posts
    
    def get_user_feed_chronological(self, user_id: int, limit: int = 20) -> List[Post]:
        """Get feed sorted chronologically."""
        followees = self.db.get_followees(user_id)
        followee_ids = [f.followee_id for f in followees] + [user_id]
        
        posts = self.db.get_posts_by_users_chronological(followee_ids, limit=limit)
        return [p for p in posts if not p.is_deleted()]
    
    def get_user_feed_popular(self, user_id: int, limit: int = 20) -> List[Post]:
        """Get feed sorted by popularity (likes + comments)."""
        followees = self.db.get_followees(user_id)
        followee_ids = [f.followee_id for f in followees] + [user_id]
        
        posts = self.db.get_posts_by_users(followee_ids)
        posts = [p for p in posts if not p.is_deleted()]
        
        # Sort by engagement score
        posts.sort(key=lambda p: p.like_count + p.comment_count, reverse=True)
        
        return posts[:limit]
```

## Sorting and Filtering

### Efficient Sorting

```python
class SocialMediaFeed:
    def get_user_feed_sorted(self, user_id: int, sort_by: str = 'time',
                            limit: int = 20) -> List[Post]:
        """Get feed with different sorting options."""
        followees = self.db.get_followees(user_id)
        followee_ids = [f.followee_id for f in followees] + [user_id]
        
        if sort_by == 'time':
            return self._get_sorted_by_time(followee_ids, limit)
        elif sort_by == 'popular':
            return self._get_sorted_by_popularity(followee_ids, limit)
        elif sort_by == 'recent':
            return self._get_sorted_by_recent_activity(followee_ids, limit)
        else:
            return self._get_sorted_by_time(followee_ids, limit)
    
    def _get_sorted_by_time(self, user_ids: List[int], limit: int) -> List[Post]:
        """Sort by creation time."""
        posts = self.db.get_posts_by_users(user_ids, limit=limit * 2)
        posts = [p for p in posts if not p.is_deleted()]
        posts.sort(key=lambda p: p.created_at, reverse=True)
        return posts[:limit]
    
    def _get_sorted_by_popularity(self, user_ids: List[int], limit: int) -> List[Post]:
        """Sort by engagement (likes + comments)."""
        posts = self.db.get_posts_by_users(user_ids, limit=limit * 2)
        posts = [p for p in posts if not p.is_deleted()]
        posts.sort(key=lambda p: (p.like_count + p.comment_count, p.created_at), 
                  reverse=True)
        return posts[:limit]
    
    def _get_sorted_by_recent_activity(self, user_ids: List[int], limit: int) -> List[Post]:
        """Sort by recent activity (comments/likes)."""
        posts = self.db.get_posts_by_users(user_ids, limit=limit * 2)
        posts = [p for p in posts if not p.is_deleted()]
        
        # Get most recent activity for each post
        for post in posts:
            recent_comment = self.db.get_most_recent_comment(post.post_id)
            recent_like = self.db.get_most_recent_like(post.post_id)
            
            recent_activity = max(
                recent_comment.created_at if recent_comment else post.created_at,
                recent_like.created_at if recent_like else post.created_at
            )
            post.recent_activity = recent_activity
        
        posts.sort(key=lambda p: p.recent_activity, reverse=True)
        return posts[:limit]
```

## Content Management

### Post Operations

```python
class SocialMediaFeed:
    def create_post(self, user_id: int, content: str, post_type: str = 'text') -> Post:
        """Create new post."""
        post = Post(
            post_id=None,
            user_id=user_id,
            content=content,
            post_type=post_type,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            deleted_at=None,
            like_count=0,
            comment_count=0
        )
        return self.db.create_post(post)
    
    def delete_post(self, post_id: int, user_id: int) -> bool:
        """Delete post (soft delete)."""
        post = self.db.get_post(post_id)
        if not post or post.user_id != user_id:
            return False
        
        # Soft delete
        post.deleted_at = datetime.now()
        self.db.update_post(post)
        
        # Delete related comments and likes (optional: soft delete)
        # self.db.delete_comments_by_post(post_id)
        # self.db.delete_likes_by_post(post_id)
        
        return True
    
    def edit_post(self, post_id: int, user_id: int, new_content: str) -> bool:
        """Edit post content."""
        post = self.db.get_post(post_id)
        if not post or post.user_id != user_id:
            return False
        
        if post.is_deleted():
            return False
        
        post.content = new_content
        post.updated_at = datetime.now()
        self.db.update_post(post)
        
        return True
    
    def add_comment(self, post_id: int, user_id: int, content: str) -> Comment:
        """Add comment to post."""
        post = self.db.get_post(post_id)
        if not post or post.is_deleted():
            raise ValueError("Post not found or deleted")
        
        comment = Comment(
            comment_id=None,
            post_id=post_id,
            user_id=user_id,
            content=content,
            created_at=datetime.now(),
            deleted_at=None
        )
        
        comment = self.db.create_comment(comment)
        
        # Update comment count
        post.comment_count += 1
        self.db.update_post(post)
        
        return comment
    
    def like_post(self, post_id: int, user_id: int) -> bool:
        """Like or unlike post."""
        post = self.db.get_post(post_id)
        if not post or post.is_deleted():
            return False
        
        existing_like = self.db.get_like(post_id, user_id)
        
        if existing_like:
            # Unlike
            self.db.delete_like(existing_like.like_id)
            post.like_count -= 1
        else:
            # Like
            like = Like(
                like_id=None,
                post_id=post_id,
                user_id=user_id,
                created_at=datetime.now()
            )
            self.db.create_like(like)
            post.like_count += 1
        
        self.db.update_post(post)
        return True
```

## Local Caching

### Feed Caching

```python
class SocialMediaFeed:
    def __init__(self, db, cache=None):
        self.db = db
        self.cache = cache  # Optional cache (e.g., Redis, in-memory)
        self.cache_ttl = 300  # 5 minutes
    
    def get_user_feed_cached(self, user_id: int, limit: int = 20) -> List[Post]:
        """Get feed with caching."""
        cache_key = f"feed:{user_id}:{limit}"
        
        # Check cache
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                return cached
        
        # Generate feed
        feed = self.get_user_feed(user_id, limit=limit)
        
        # Cache result
        if self.cache:
            self.cache.set(cache_key, feed, ttl=self.cache_ttl)
        
        return feed
    
    def invalidate_feed_cache(self, user_id: int):
        """Invalidate feed cache for user."""
        if self.cache:
            # Invalidate for user and their followers
            followers = self.db.get_followers(user_id)
            for follower in followers:
                self.cache.delete(f"feed:{follower.follower_id}:*")
```

## Implementation

### Complete Example

```python
# Initialize
db = Database()
cache = Cache()
feed_system = SocialMediaFeed(db, cache)

# Create users
user1 = feed_system.create_user("alice", "alice@example.com")
user2 = feed_system.create_user("bob", "bob@example.com")

# Follow
feed_system.follow(user1.user_id, user2.user_id)

# Create posts
post1 = feed_system.create_post(user2.user_id, "Hello World!")
post2 = feed_system.create_post(user1.user_id, "My first post")

# Get feed
feed = feed_system.get_user_feed(user1.user_id)
for post in feed:
    print(f"{post.user.username}: {post.content}")

# Like and comment
feed_system.like_post(post1.post_id, user1.user_id)
feed_system.add_comment(post1.post_id, user1.user_id, "Nice post!")
```

## What Interviewers Look For

### Data Modeling Skills

1. **Relational Design**
   - Proper schema for posts, comments, likes
   - Correct relationships and foreign keys
   - Appropriate indexes
   - **Red Flags**: Poor schema, missing indexes

2. **Entity Relationships**
   - User-Post-Comment-Like relationships
   - Follow relationships
   - **Red Flags**: Incorrect relationships, missing entities

### Algorithm Implementation

1. **Feed Generation**
   - Efficient querying
   - Proper sorting algorithms
   - **Red Flags**: Inefficient queries, slow sorting

2. **Sorting Strategies**
   - Chronological vs popularity sorting
   - Efficient implementation
   - **Red Flags**: No sorting options, inefficient

### Problem-Solving Approach

1. **Content Management**
   - Soft delete implementation
   - Edit handling
   - **Red Flags**: Hard delete, no edit support

2. **Caching Strategy**
   - Local caching approach
   - Cache invalidation
   - **Red Flags**: No caching, incorrect invalidation

3. **Edge Cases**
   - Deleted posts in feed
   - Empty feeds
   - Large result sets
   - **Red Flags**: Ignoring edge cases

### Code Quality

1. **Query Efficiency**
   - Proper use of indexes
   - Efficient joins
   - **Red Flags**: Slow queries, missing indexes

2. **Data Consistency**
   - Accurate counts
   - Consistent state
   - **Red Flags**: Wrong counts, inconsistent data

### Interview Focus

1. **Data Modeling**
   - Strong database design skills
   - Efficient queries
   - **Key**: Show database expertise

2. **Local System Design**
   - No distributed concerns
   - Focus on correctness
   - **Key**: Demonstrate local system understanding

## Summary

### Key Takeaways

1. **Data Modeling**: Users, Posts, Comments, Likes, Follows
2. **Feed Generation**: Get posts from followed users, sort by time/popularity
3. **Content Management**: Create, edit, delete posts with soft delete
4. **Local Caching**: Cache feeds for fast retrieval
5. **Efficient Retrieval**: Index on user_id, created_at for fast queries

### Common Interview Questions

1. **How would you store posts, comments, and likes?**
   - Posts: user_id, content, timestamps, counts
   - Comments: post_id, user_id, content
   - Likes: post_id, user_id (unique constraint)

2. **How would you retrieve a user's timeline efficiently?**
   - Get followees, query posts by user_ids
   - Sort by created_at or engagement
   - Use indexes on user_id, created_at

3. **How would you handle content deletion or edits?**
   - Soft delete: Set deleted_at timestamp
   - Filter deleted posts in queries
   - Update content and updated_at for edits

Understanding social media feed design is crucial for Meta interviews focusing on:
- Data modeling
- Feed generation algorithms
- Sorting and filtering
- Local caching
- Content management

