---
layout: post
title: "Design a Basic Online Shopping Cart - Meta System Design Interview"
date: 2025-11-24
categories: [System Design, Interview Example, Meta, Object-Oriented Design, Entity Relationships, Session Management]
excerpt: "A comprehensive guide to designing an online shopping cart focusing on object-oriented design, entity relationships, session management, and state handling. Meta interview question emphasizing handling state, operations, and edge cases rather than scaling to millions of users."
---

## Introduction

Designing an online shopping cart is a Meta interview question that tests your ability to model e-commerce entities, manage state, and handle complex operations. This question focuses on:

- **Object-oriented design**: Cart, Product, Inventory entities
- **Entity relationships**: Cart-Item-Product relationships
- **Session management**: User sessions, cart persistence
- **State management**: Cart state, inventory state
- **Atomic operations**: Inventory updates, checkout

This guide covers the complete design of an online shopping cart system with proper entity modeling and state management.

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Requirements](#requirements)
3. [Entity Design](#entity-design)
4. [Class Design](#class-design)
5. [Core Operations](#core-operations)
6. [Inventory Management](#inventory-management)
7. [Checkout Process](#checkout-process)
8. [Session Management](#session-management)
9. [Implementation](#implementation)
10. [Summary](#summary)

## Problem Statement

**Design an online shopping cart system that:**

1. **Manages products** (catalog, inventory, pricing)
2. **Manages carts** (user carts, items, quantities)
3. **Handles cart operations** (add, remove, update quantity)
4. **Manages inventory** (track stock, prevent overselling)
5. **Handles checkout** (calculate total, process payment)
6. **Supports sessions** (guest and logged-in users)

**Scale Requirements:**
- Support 1K-100K products
- Handle 1K-10K concurrent carts
- Fast cart operations: < 50ms
- Accurate inventory tracking

## Requirements

### Functional Requirements

1. **Add to Cart**: Add product to cart
2. **Remove from Cart**: Remove item from cart
3. **Update Quantity**: Change item quantity
4. **View Cart**: Get cart contents and total
5. **Checkout**: Process order and payment
6. **Inventory Check**: Verify product availability

### Non-Functional Requirements

**Consistency:**
- Accurate inventory
- No overselling
- Correct pricing

**Performance:**
- Fast cart operations
- Efficient inventory checks
- Quick checkout

## Entity Design

### Database Schema

```sql
CREATE TABLE products (
    product_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT DEFAULT 0,
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sku (sku),
    INDEX idx_category (category)
);

CREATE TABLE carts (
    cart_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NULL,  -- NULL for guest carts
    session_id VARCHAR(100) NULL,  -- For guest carts
    status VARCHAR(20) DEFAULT 'active',  -- active, abandoned, checked_out
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_session_id (session_id)
);

CREATE TABLE cart_items (
    item_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    cart_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,  -- Snapshot of price
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_cart_product (cart_id, product_id),
    INDEX idx_cart_id (cart_id),
    INDEX idx_product_id (product_id),
    FOREIGN KEY (cart_id) REFERENCES carts(cart_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE orders (
    order_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    cart_id BIGINT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, paid, shipped, cancelled
    payment_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    FOREIGN KEY (cart_id) REFERENCES carts(cart_id)
);
```

### Data Model Classes

```python
from enum import Enum
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from dataclasses import dataclass

class CartStatus(Enum):
    ACTIVE = "active"
    ABANDONED = "abandoned"
    CHECKED_OUT = "checked_out"

@dataclass
class Product:
    product_id: Optional[int]
    sku: str
    name: str
    description: Optional[str]
    price: Decimal
    stock_quantity: int
    category: Optional[str]

@dataclass
class CartItem:
    item_id: Optional[int]
    cart_id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    product: Optional[Product] = None  # For convenience
    
    @property
    def subtotal(self) -> Decimal:
        return Decimal(self.quantity) * self.unit_price

@dataclass
class Cart:
    cart_id: Optional[int]
    user_id: Optional[int]
    session_id: Optional[str]
    status: CartStatus
    items: List[CartItem]
    created_at: datetime
    updated_at: datetime
    
    @property
    def total(self) -> Decimal:
        return sum(item.subtotal for item in self.items)
    
    @property
    def item_count(self) -> int:
        return sum(item.quantity for item in self.items)
```

## Class Design

### Shopping Cart System

```python
class ShoppingCartSystem:
    def __init__(self, db):
        self.db = db
        self.cart_timeout = timedelta(days=7)  # Abandon cart after 7 days
    
    def create_cart(self, user_id: Optional[int] = None, 
                   session_id: Optional[str] = None) -> Cart:
        """Create new cart."""
        cart = Cart(
            cart_id=None,
            user_id=user_id,
            session_id=session_id,
            status=CartStatus.ACTIVE,
            items=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        return self.db.create_cart(cart)
    
    def get_cart(self, cart_id: Optional[int] = None,
                user_id: Optional[int] = None,
                session_id: Optional[str] = None) -> Optional[Cart]:
        """Get cart by ID, user ID, or session ID."""
        if cart_id:
            return self.db.get_cart(cart_id)
        elif user_id:
            return self.db.get_user_cart(user_id)
        elif session_id:
            return self.db.get_session_cart(session_id)
        return None
    
    def add_to_cart(self, cart_id: int, product_id: int, quantity: int = 1) -> bool:
        """Add product to cart."""
        cart = self.db.get_cart(cart_id)
        if not cart or cart.status != CartStatus.ACTIVE:
            return False
        
        product = self.db.get_product(product_id)
        if not product:
            return False
        
        # Check inventory
        if product.stock_quantity < quantity:
            return False
        
        # Check if item already in cart
        existing_item = next((item for item in cart.items if item.product_id == product_id), None)
        
        if existing_item:
            # Update quantity
            new_quantity = existing_item.quantity + quantity
            if new_quantity > product.stock_quantity:
                return False  # Exceeds available stock
            
            existing_item.quantity = new_quantity
            self.db.update_cart_item(existing_item)
        else:
            # Add new item
            cart_item = CartItem(
                item_id=None,
                cart_id=cart_id,
                product_id=product_id,
                quantity=quantity,
                unit_price=product.price
            )
            self.db.add_cart_item(cart_item)
        
        # Update cart timestamp
        cart.updated_at = datetime.now()
        self.db.update_cart(cart)
        
        return True
    
    def remove_from_cart(self, cart_id: int, product_id: int) -> bool:
        """Remove product from cart."""
        cart = self.db.get_cart(cart_id)
        if not cart:
            return False
        
        item = next((item for item in cart.items if item.product_id == product_id), None)
        if not item:
            return False
        
        self.db.remove_cart_item(item.item_id)
        
        cart.updated_at = datetime.now()
        self.db.update_cart(cart)
        
        return True
    
    def update_quantity(self, cart_id: int, product_id: int, quantity: int) -> bool:
        """Update item quantity."""
        if quantity <= 0:
            return self.remove_from_cart(cart_id, product_id)
        
        cart = self.db.get_cart(cart_id)
        if not cart:
            return False
        
        item = next((item for item in cart.items if item.product_id == product_id), None)
        if not item:
            return False
        
        product = self.db.get_product(product_id)
        if quantity > product.stock_quantity:
            return False
        
        item.quantity = quantity
        self.db.update_cart_item(item)
        
        cart.updated_at = datetime.now()
        self.db.update_cart(cart)
        
        return True
    
    def get_cart_total(self, cart_id: int) -> Optional[dict]:
        """Get cart total and summary."""
        cart = self.db.get_cart(cart_id)
        if not cart:
            return None
        
        return {
            'cart_id': cart.cart_id,
            'item_count': cart.item_count,
            'total': float(cart.total),
            'items': [
                {
                    'product_id': item.product_id,
                    'quantity': item.quantity,
                    'unit_price': float(item.unit_price),
                    'subtotal': float(item.subtotal)
                }
                for item in cart.items
            ]
        }
```

## Inventory Management

### Atomic Inventory Updates

```python
class InventoryManager:
    def __init__(self, db):
        self.db = db
        self.product_locks = {}  # product_id -> Lock
        self.locks_lock = threading.Lock()
    
    def _get_product_lock(self, product_id: int) -> threading.Lock:
        """Get or create lock for product."""
        with self.locks_lock:
            if product_id not in self.product_locks:
                self.product_locks[product_id] = threading.Lock()
            return self.product_locks[product_id]
    
    def reserve_inventory(self, product_id: int, quantity: int) -> bool:
        """Reserve inventory atomically."""
        lock = self._get_product_lock(product_id)
        
        with lock:
            product = self.db.get_product(product_id)
            if not product:
                return False
            
            if product.stock_quantity < quantity:
                return False
            
            # Update inventory
            product.stock_quantity -= quantity
            self.db.update_product(product)
            
            return True
    
    def release_inventory(self, product_id: int, quantity: int):
        """Release reserved inventory."""
        lock = self._get_product_lock(product_id)
        
        with lock:
            product = self.db.get_product(product_id)
            if product:
                product.stock_quantity += quantity
                self.db.update_product(product)
    
    def check_availability(self, product_id: int, quantity: int) -> bool:
        """Check if product is available in requested quantity."""
        product = self.db.get_product(product_id)
        if not product:
            return False
        return product.stock_quantity >= quantity
```

## Checkout Process

### Checkout Implementation

```python
class ShoppingCartSystem:
    def checkout(self, cart_id: int, payment_info: dict) -> Optional[dict]:
        """Process checkout."""
        cart = self.db.get_cart(cart_id)
        if not cart or cart.status != CartStatus.ACTIVE:
            return None
        
        if not cart.items:
            return {'success': False, 'message': 'Cart is empty'}
        
        # Validate inventory for all items
        inventory_manager = InventoryManager(self.db)
        reservations = []
        
        try:
            # Reserve inventory for all items
            for item in cart.items:
                if not inventory_manager.reserve_inventory(item.product_id, item.quantity):
                    # Release already reserved items
                    for reserved in reservations:
                        inventory_manager.release_inventory(reserved['product_id'], reserved['quantity'])
                    return {'success': False, 'message': f'Insufficient stock for product {item.product_id}'}
                
                reservations.append({
                    'product_id': item.product_id,
                    'quantity': item.quantity
                })
            
            # Process payment (simplified)
            payment_result = self._process_payment(cart.total, payment_info)
            if not payment_result['success']:
                # Release inventory
                for reserved in reservations:
                    inventory_manager.release_inventory(reserved['product_id'], reserved['quantity'])
                return {'success': False, 'message': 'Payment failed'}
            
            # Create order
            order = self._create_order(cart, payment_result['payment_id'])
            
            # Update cart status
            cart.status = CartStatus.CHECKED_OUT
            self.db.update_cart(cart)
            
            return {
                'success': True,
                'order_id': order.order_id,
                'total': float(cart.total),
                'payment_id': payment_result['payment_id']
            }
            
        except Exception as e:
            # Rollback: release inventory
            for reserved in reservations:
                inventory_manager.release_inventory(reserved['product_id'], reserved['quantity'])
            return {'success': False, 'message': str(e)}
    
    def _process_payment(self, amount: Decimal, payment_info: dict) -> dict:
        """Process payment (simplified)."""
        # In real system, integrate with payment gateway
        payment_id = f"PAY_{datetime.now().timestamp()}"
        return {
            'success': True,
            'payment_id': payment_id
        }
    
    def _create_order(self, cart: Cart, payment_id: str):
        """Create order from cart."""
        order = {
            'user_id': cart.user_id,
            'cart_id': cart.cart_id,
            'total_amount': cart.total,
            'payment_id': payment_id,
            'status': 'paid'
        }
        return self.db.create_order(order)
```

## Session Management

### Guest Cart Management

```python
class ShoppingCartSystem:
    def get_or_create_guest_cart(self, session_id: str) -> Cart:
        """Get or create cart for guest user."""
        cart = self.db.get_session_cart(session_id)
        if not cart:
            cart = self.create_cart(session_id=session_id)
        return cart
    
    def merge_carts(self, guest_cart_id: int, user_id: int) -> Cart:
        """Merge guest cart into user cart on login."""
        guest_cart = self.db.get_cart(guest_cart_id)
        user_cart = self.db.get_user_cart(user_id)
        
        if not guest_cart:
            return user_cart
        
        if not user_cart:
            # Convert guest cart to user cart
            guest_cart.user_id = user_id
            guest_cart.session_id = None
            self.db.update_cart(guest_cart)
            return guest_cart
        
        # Merge items
        for guest_item in guest_cart.items:
            existing = next((item for item in user_cart.items 
                           if item.product_id == guest_item.product_id), None)
            if existing:
                # Update quantity
                existing.quantity += guest_item.quantity
                self.db.update_cart_item(existing)
            else:
                # Add item
                guest_item.cart_id = user_cart.cart_id
                self.db.add_cart_item(guest_item)
        
        # Delete guest cart
        self.db.delete_cart(guest_cart_id)
        
        return user_cart
```

## What Interviewers Look For

### Object-Oriented Design Skills

1. **Entity Relationships**
   - Proper modeling of Cart, Product, CartItem
   - Clear relationships and responsibilities
   - **Red Flags**: Unclear relationships, poor separation

2. **State Management**
   - Cart state (active, abandoned, checked_out)
   - Inventory state tracking
   - **Red Flags**: Missing states, inconsistent state

### Session Management

1. **Guest vs Logged-in Users**
   - Handling guest carts
   - Cart merging on login
   - **Red Flags**: No guest support, no merge logic

2. **Cart Persistence**
   - Storing cart state
   - Session management
   - **Red Flags**: No persistence, lost carts

### Problem-Solving Approach

1. **Atomic Inventory Updates**
   - Preventing overselling
   - Lock-based updates
   - **Red Flags**: Race conditions, overselling possible

2. **Checkout Process**
   - Complete checkout flow
   - Error handling
   - Rollback mechanisms
   - **Red Flags**: Incomplete checkout, no rollback

3. **Edge Cases**
   - Out of stock during checkout
   - Price changes
   - Cart expiration
   - **Red Flags**: Ignoring edge cases

### Code Quality

1. **Data Consistency**
   - Accurate inventory
   - Correct pricing
   - **Red Flags**: Inconsistent data, wrong calculations

2. **Error Handling**
   - Validation of operations
   - Meaningful errors
   - **Red Flags**: No validation, unclear errors

### Meta-Specific Focus

1. **Entity Modeling**
   - Strong OOP skills
   - Clear relationships
   - **Key**: Show understanding of entity design

2. **State Management**
   - Proper state handling
   - Session management
   - **Key**: Demonstrate state management skills

## Summary

### Key Takeaways

1. **Entity Design**: Product, Cart, CartItem, Order
2. **State Management**: Cart status, inventory state
3. **Atomic Operations**: Inventory reservation, checkout
4. **Session Management**: Guest and user carts
5. **Inventory Updates**: Lock-based atomic updates

### Common Interview Questions

1. **How would you model Cart, Product, Inventory?**
   - Cart: user_id, items, status
   - Product: SKU, price, stock
   - CartItem: product_id, quantity, unit_price

2. **How would you handle checkout?**
   - Reserve inventory atomically
   - Process payment
   - Create order
   - Rollback on failure

3. **How would you handle inventory updates atomically?**
   - Lock-based: Product-level locks
   - Database transactions
   - Reserve before checkout

Understanding shopping cart design is crucial for Meta interviews focusing on:
- Object-oriented design
- Entity relationships
- State management
- Atomic operations
- Session management

