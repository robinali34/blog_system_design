---
layout: post
title: "Amazon SQS: Comprehensive Guide with Use Cases and Deployment"
date: 2025-11-13
categories: [AWS, Message Queue, SQS, Tutorial, Use Cases, Deployment, Distributed Systems]
excerpt: "A comprehensive guide to Amazon SQS (Simple Queue Service), covering queue types, use cases, deployment strategies, best practices, and practical examples for building decoupled, scalable applications."
---

## Introduction

Amazon SQS (Simple Queue Service) is a fully managed message queuing service that enables you to decouple and scale microservices, distributed systems, and serverless applications. SQS eliminates the complexity and overhead associated with managing and operating message-oriented middleware, allowing you to focus on building applications.

This guide covers:
- **SQS Fundamentals**: Core concepts, queue types, and features
- **Use Cases**: Real-world applications and patterns
- **Deployment**: Step-by-step setup and configuration
- **Best Practices**: Performance, reliability, and cost optimization
- **Practical Examples**: Code samples and deployment scripts

## What is Amazon SQS?

Amazon SQS is a message queuing service that offers:
- **Fully Managed**: No infrastructure to manage
- **Scalability**: Handles any volume of messages
- **Reliability**: Messages are stored redundantly across multiple availability zones
- **Decoupling**: Decouple components of distributed systems
- **Asynchronous Processing**: Process messages asynchronously
- **Cost-Effective**: Pay only for what you use

### Key Concepts

**Queue**: A message queue that stores messages until they are processed.

**Message**: A unit of data sent between components. Messages can contain up to 256 KB of text data.

**Producer**: A component that sends messages to a queue.

**Consumer**: A component that receives and processes messages from a queue.

**Visibility Timeout**: The duration that a message is hidden after being received, allowing time for processing.

**Dead Letter Queue (DLQ)**: A queue for messages that couldn't be processed successfully.

## Queue Types

### Standard Queue

**Features:**
- Unlimited throughput
- At-least-once delivery
- Best-effort ordering
- High availability

**Use Cases:**
- High throughput scenarios
- Order doesn't matter
- Duplicate messages are acceptable

**Characteristics:**
- Messages may be delivered out of order
- Messages may be delivered more than once
- Maximum throughput: Nearly unlimited

### FIFO Queue

**Features:**
- Exactly-once processing
- First-In-First-Out ordering
- Limited throughput (3,000 messages/second with batching)
- Deduplication support

**Use Cases:**
- Order matters
- Duplicate messages are unacceptable
- Lower throughput requirements

**Characteristics:**
- Messages are delivered in order
- Messages are delivered exactly once
- Maximum throughput: 3,000 messages/second (300/second without batching)

## Common Use Cases

### 1. Decoupling Microservices

Decouple microservices to improve scalability and reliability.

**Use Cases:**
- Order processing systems
- E-commerce platforms
- Event-driven architectures

**Benefits:**
- Independent scaling
- Fault isolation
- Loose coupling

**Example:**
```python
import boto3
import json

sqs = boto3.client('sqs')
queue_url = 'https://sqs.us-east-1.amazonaws.com/123456789012/order-queue'

def send_order_message(order_data):
    """Producer: Send order to queue"""
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(order_data),
        MessageAttributes={
            'OrderId': {
                'StringValue': order_data['order_id'],
                'DataType': 'String'
            },
            'Priority': {
                'StringValue': order_data.get('priority', 'normal'),
                'DataType': 'String'
            }
        }
    )
    return response['MessageId']

def process_order_messages():
    """Consumer: Process orders from queue"""
    while True:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=20,  # Long polling
            MessageAttributeNames=['All']
        )
        
        messages = response.get('Messages', [])
        if not messages:
            continue
        
        for message in messages:
            try:
                order_data = json.loads(message['Body'])
                process_order(order_data)
                
                # Delete message after successful processing
                sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=message['ReceiptHandle']
                )
            except Exception as e:
                print(f"Error processing message: {e}")
                # Message will become visible again after visibility timeout
```

### 2. Asynchronous Task Processing

Process long-running tasks asynchronously without blocking the main application.

**Use Cases:**
- Image processing
- Video transcoding
- Email sending
- Report generation

**Example:**
```python
import boto3
import json

sqs = boto3.client('sqs')
task_queue_url = 'https://sqs.us-east-1.amazonaws.com/123456789012/task-queue'

def submit_task(task_type, task_data):
    """Submit task for asynchronous processing"""
    message = {
        'task_type': task_type,
        'task_data': task_data,
        'timestamp': str(datetime.now())
    }
    
    sqs.send_message(
        QueueUrl=task_queue_url,
        MessageBody=json.dumps(message),
        MessageAttributes={
            'TaskType': {
                'StringValue': task_type,
                'DataType': 'String'
            }
        }
    )

def process_tasks():
    """Worker: Process tasks from queue"""
    while True:
        response = sqs.receive_message(
            QueueUrl=task_queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20,
            VisibilityTimeout=300  # 5 minutes for processing
        )
        
        messages = response.get('Messages', [])
        if not messages:
            continue
        
        for message in messages:
            try:
                task = json.loads(message['Body'])
                task_type = task['task_type']
                task_data = task['task_data']
                
                # Process based on task type
                if task_type == 'image_process':
                    process_image(task_data)
                elif task_type == 'send_email':
                    send_email(task_data)
                elif task_type == 'generate_report':
                    generate_report(task_data)
                
                # Delete message after successful processing
                sqs.delete_message(
                    QueueUrl=task_queue_url,
                    ReceiptHandle=message['ReceiptHandle']
                )
            except Exception as e:
                print(f"Error processing task: {e}")
                # Message will retry automatically
```

### 3. Event-Driven Architecture

Build event-driven systems that respond to events in real-time.

**Use Cases:**
- User activity tracking
- Audit logging
- Real-time notifications
- Data synchronization

**Example:**
```python
import boto3
import json

sqs = boto3.client('sqs')
event_queue_url = 'https://sqs.us-east-1.amazonaws.com/123456789012/event-queue'

def publish_event(event_type, event_data):
    """Publish event to queue"""
    event = {
        'event_type': event_type,
        'event_data': event_data,
        'timestamp': str(datetime.now()),
        'source': 'user-service'
    }
    
    sqs.send_message(
        QueueUrl=event_queue_url,
        MessageBody=json.dumps(event),
        MessageAttributes={
            'EventType': {
                'StringValue': event_type,
                'DataType': 'String'
            }
        }
    )

def handle_user_registration(user_data):
    """Example: Handle user registration event"""
    # Process registration
    user = create_user(user_data)
    
    # Publish events
    publish_event('user.created', {'user_id': user.id})
    publish_event('email.send', {
        'to': user.email,
        'template': 'welcome'
    })
    publish_event('analytics.track', {
        'event': 'user_registered',
        'user_id': user.id
    })

def process_events():
    """Event processor: Handle events from queue"""
    while True:
        response = sqs.receive_message(
            QueueUrl=event_queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=20
        )
        
        messages = response.get('Messages', [])
        if not messages:
            continue
        
        for message in messages:
            try:
                event = json.loads(message['Body'])
                event_type = event['event_type']
                event_data = event['event_data']
                
                # Route to appropriate handler
                if event_type == 'user.created':
                    handle_user_created(event_data)
                elif event_type == 'email.send':
                    handle_email_send(event_data)
                elif event_type == 'analytics.track':
                    handle_analytics_track(event_data)
                
                sqs.delete_message(
                    QueueUrl=event_queue_url,
                    ReceiptHandle=message['ReceiptHandle']
                )
            except Exception as e:
                print(f"Error processing event: {e}")
```

### 4. Load Leveling

Distribute workload evenly across multiple workers.

**Use Cases:**
- Batch processing
- Data ingestion
- Image processing pipelines

**Example:**
```python
import boto3
import json
from concurrent.futures import ThreadPoolExecutor

sqs = boto3.client('sqs')
work_queue_url = 'https://sqs.us-east-1.amazonaws.com/123456789012/work-queue'

def distribute_work(items):
    """Distribute work items across queue"""
    for item in items:
        sqs.send_message(
            QueueUrl=work_queue_url,
            MessageBody=json.dumps(item)
        )

def worker():
    """Worker process: Process work items"""
    while True:
        response = sqs.receive_message(
            QueueUrl=work_queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20,
            VisibilityTimeout=60
        )
        
        messages = response.get('Messages', [])
        if not messages:
            continue
        
        for message in messages:
            try:
                work_item = json.loads(message['Body'])
                process_work_item(work_item)
                
                sqs.delete_message(
                    QueueUrl=work_queue_url,
                    ReceiptHandle=message['ReceiptHandle']
                )
            except Exception as e:
                print(f"Error processing work item: {e}")

# Run multiple workers
def run_workers(num_workers=5):
    """Run multiple worker threads"""
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        for _ in range(num_workers):
            executor.submit(worker)
```

### 5. Delayed Processing

Schedule messages to be processed at a later time.

**Use Cases:**
- Scheduled tasks
- Retry with delay
- Time-based workflows

**Example:**
```python
import boto3
import json

sqs = boto3.client('sqs')
queue_url = 'https://sqs.us-east-1.amazonaws.com/123456789012/delayed-queue'

def schedule_message(message_data, delay_seconds):
    """Schedule message to be processed after delay"""
    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message_data),
        DelaySeconds=delay_seconds  # 0-900 seconds (15 minutes)
    )

# Schedule email reminder for 1 hour later
schedule_message(
    {'type': 'email_reminder', 'user_id': '123'},
    delay_seconds=3600
)

# Schedule cleanup task for 24 hours later
schedule_message(
    {'type': 'cleanup', 'resource_id': '456'},
    delay_seconds=86400  # Maximum is 900 seconds, use Step Functions for longer delays
)
```

### 6. Dead Letter Queue Pattern

Handle messages that fail processing repeatedly.

**Use Cases:**
- Error handling
- Failed message analysis
- Retry logic

**Example:**
```python
import boto3
import json

sqs = boto3.client('sqs')
main_queue_url = 'https://sqs.us-east-1.amazonaws.com/123456789012/main-queue'
dlq_url = 'https://sqs.us-east-1.amazonaws.com/123456789012/dlq'

def configure_dlq():
    """Configure Dead Letter Queue"""
    # Set redrive policy on main queue
    redrive_policy = {
        'deadLetterTargetArn': 'arn:aws:sqs:us-east-1:123456789012:dlq',
        'maxReceiveCount': 3  # Move to DLQ after 3 failed attempts
    }
    
    sqs.set_queue_attributes(
        QueueUrl=main_queue_url,
        Attributes={
            'RedrivePolicy': json.dumps(redrive_policy)
        }
    )

def process_with_dlq():
    """Process messages with DLQ handling"""
    while True:
        response = sqs.receive_message(
            QueueUrl=main_queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20,
            VisibilityTimeout=60
        )
        
        messages = response.get('Messages', [])
        if not messages:
            continue
        
        for message in messages:
            try:
                data = json.loads(message['Body'])
                process_message(data)
                
                sqs.delete_message(
                    QueueUrl=main_queue_url,
                    ReceiptHandle=message['ReceiptHandle']
                )
            except Exception as e:
                print(f"Error processing message: {e}")
                # Message will be retried automatically
                # After maxReceiveCount, it will move to DLQ

def process_dlq():
    """Process messages from Dead Letter Queue"""
    while True:
        response = sqs.receive_message(
            QueueUrl=dlq_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=20
        )
        
        messages = response.get('Messages', [])
        if not messages:
            continue
        
        for message in messages:
            # Analyze failed messages
            failed_message = json.loads(message['Body'])
            analyze_failed_message(failed_message)
            
            # Optionally reprocess or notify
            notify_administrator(failed_message)
            
            sqs.delete_message(
                QueueUrl=dlq_url,
                ReceiptHandle=message['ReceiptHandle']
            )
```

## Deployment Guide

### Prerequisites

1. **AWS Account**: Sign up at [aws.amazon.com](https://aws.amazon.com)
2. **AWS CLI**: Install AWS CLI
3. **IAM User**: Create IAM user with SQS permissions
4. **Credentials**: Configure AWS credentials

### Step 1: Install AWS CLI

See the S3 guide for AWS CLI installation instructions.

### Step 2: Configure AWS Credentials

```bash
aws configure
```

### Step 3: Create SQS Queue

**Using AWS CLI:**

**Standard Queue:**
```bash
# Create standard queue
aws sqs create-queue --queue-name my-queue

# Get queue URL
aws sqs get-queue-url --queue-name my-queue

# List all queues
aws sqs list-queues
```

**FIFO Queue:**
```bash
# Create FIFO queue (must end with .fifo)
aws sqs create-queue \
  --queue-name my-queue.fifo \
  --attributes FifoQueue=true,ContentBasedDeduplication=true
```

**Using Python (boto3):**
```python
import boto3

sqs = boto3.client('sqs')

# Create standard queue
def create_standard_queue(queue_name):
    response = sqs.create_queue(
        QueueName=queue_name,
        Attributes={
            'VisibilityTimeout': '30',
            'MessageRetentionPeriod': '345600',  # 4 days
            'ReceiveMessageWaitTimeSeconds': '20'  # Long polling
        }
    )
    return response['QueueUrl']

# Create FIFO queue
def create_fifo_queue(queue_name):
    response = sqs.create_queue(
        QueueName=f'{queue_name}.fifo',
        Attributes={
            'FifoQueue': 'true',
            'ContentBasedDeduplication': 'true',
            'VisibilityTimeout': '30',
            'MessageRetentionPeriod': '345600'
        }
    )
    return response['QueueUrl']

# Create queue with Dead Letter Queue
def create_queue_with_dlq(queue_name, dlq_name):
    # Create DLQ first
    dlq_response = sqs.create_queue(QueueName=dlq_name)
    dlq_arn = sqs.get_queue_attributes(
        QueueUrl=dlq_response['QueueUrl'],
        AttributeNames=['QueueArn']
    )['Attributes']['QueueArn']
    
    # Create main queue with redrive policy
    redrive_policy = {
        'deadLetterTargetArn': dlq_arn,
        'maxReceiveCount': 3
    }
    
    response = sqs.create_queue(
        QueueName=queue_name,
        Attributes={
            'RedrivePolicy': json.dumps(redrive_policy),
            'VisibilityTimeout': '30'
        }
    )
    return response['QueueUrl']
```

**Using Terraform:**
```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# Standard Queue
resource "aws_sqs_queue" "standard_queue" {
  name                      = "my-standard-queue"
  visibility_timeout_seconds = 30
  message_retention_seconds  = 345600  # 4 days
  receive_wait_time_seconds  = 20     # Long polling
  
  tags = {
    Environment = "Production"
  }
}

# FIFO Queue
resource "aws_sqs_queue" "fifo_queue" {
  name                        = "my-fifo-queue.fifo"
  fifo_queue                  = true
  content_based_deduplication = true
  visibility_timeout_seconds  = 30
  message_retention_seconds   = 345600
}

# Dead Letter Queue
resource "aws_sqs_queue" "dlq" {
  name = "my-dlq"
}

# Main Queue with DLQ
resource "aws_sqs_queue" "main_queue" {
  name                      = "my-main-queue"
  visibility_timeout_seconds = 30
  
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = 3
  })
}
```

### Step 4: Configure Queue Attributes

**Using AWS CLI:**
```bash
# Set visibility timeout
aws sqs set-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/my-queue \
  --attributes VisibilityTimeout=60

# Set message retention period
aws sqs set-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/my-queue \
  --attributes MessageRetentionPeriod=1209600  # 14 days

# Enable long polling
aws sqs set-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/my-queue \
  --attributes ReceiveMessageWaitTimeSeconds=20
```

**Using Python:**
```python
import boto3

sqs = boto3.client('sqs')

def configure_queue(queue_url):
    """Configure queue attributes"""
    sqs.set_queue_attributes(
        QueueUrl=queue_url,
        Attributes={
            'VisibilityTimeout': '60',
            'MessageRetentionPeriod': '1209600',  # 14 days
            'ReceiveMessageWaitTimeSeconds': '20',  # Long polling
            'MaximumMessageSize': '262144',  # 256 KB
            'DelaySeconds': '0'
        }
    )
```

### Step 5: Set Up IAM Permissions

**IAM Policy for SQS Access:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sqs:SendMessage",
        "sqs:ReceiveMessage",
        "sqs:DeleteMessage",
        "sqs:GetQueueAttributes",
        "sqs:GetQueueUrl"
      ],
      "Resource": "arn:aws:sqs:us-east-1:123456789012:my-queue"
    }
  ]
}
```

**Queue Policy for Cross-Account Access:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowCrossAccountAccess",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::987654321098:root"
      },
      "Action": [
        "sqs:SendMessage",
        "sqs:ReceiveMessage"
      ],
      "Resource": "arn:aws:sqs:us-east-1:123456789012:my-queue"
    }
  ]
}
```

Apply queue policy:
```bash
aws sqs set-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/my-queue \
  --attributes Policy=file://queue-policy.json
```

### Step 6: Send Messages

**Using AWS CLI:**
```bash
# Send message
aws sqs send-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/my-queue \
  --message-body "Hello, SQS!"

# Send message with attributes
aws sqs send-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/my-queue \
  --message-body "Hello, SQS!" \
  --message-attributes 'Priority={DataType=String,StringValue=High}'

# Send message with delay
aws sqs send-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/my-queue \
  --message-body "Delayed message" \
  --delay-seconds 60
```

**Using Python:**
```python
import boto3
import json

sqs = boto3.client('sqs')
queue_url = 'https://sqs.us-east-1.amazonaws.com/123456789012/my-queue'

# Send single message
def send_message(message_body):
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=message_body
    )
    return response['MessageId']

# Send message with attributes
def send_message_with_attributes(message_body, attributes):
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=message_body,
        MessageAttributes=attributes,
        DelaySeconds=0
    )
    return response['MessageId']

# Send batch messages
def send_batch_messages(messages):
    entries = []
    for i, msg in enumerate(messages):
        entries.append({
            'Id': str(i),
            'MessageBody': json.dumps(msg),
            'MessageAttributes': {
                'Priority': {
                    'StringValue': msg.get('priority', 'normal'),
                    'DataType': 'String'
                }
            }
        })
    
    response = sqs.send_message_batch(
        QueueUrl=queue_url,
        Entries=entries
    )
    return response
```

### Step 7: Receive Messages

**Using AWS CLI:**
```bash
# Receive messages
aws sqs receive-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/my-queue

# Receive with long polling
aws sqs receive-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/my-queue \
  --wait-time-seconds 20 \
  --max-number-of-messages 10
```

**Using Python:**
```python
import boto3
import json

sqs = boto3.client('sqs')
queue_url = 'https://sqs.us-east-1.amazonaws.com/123456789012/my-queue'

def receive_messages(max_messages=10, wait_time=20):
    """Receive messages with long polling"""
    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=max_messages,
        WaitTimeSeconds=wait_time,  # Long polling
        MessageAttributeNames=['All']
    )
    return response.get('Messages', [])

def process_messages():
    """Process messages from queue"""
    while True:
        messages = receive_messages()
        
        if not messages:
            continue
        
        for message in messages:
            try:
                body = json.loads(message['Body'])
                process_message(body)
                
                # Delete message after processing
                sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=message['ReceiptHandle']
                )
            except Exception as e:
                print(f"Error processing message: {e}")
                # Message will become visible again after visibility timeout
```

### Step 8: Delete Messages

**Using AWS CLI:**
```bash
# Delete single message (requires receipt handle from receive-message)
aws sqs delete-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/my-queue \
  --receipt-handle "receipt-handle-here"

# Purge all messages
aws sqs purge-queue \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/my-queue
```

**Using Python:**
```python
import boto3

sqs = boto3.client('sqs')
queue_url = 'https://sqs.us-east-1.amazonaws.com/123456789012/my-queue'

def delete_message(receipt_handle):
    """Delete single message"""
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )

def delete_batch_messages(messages):
    """Delete multiple messages"""
    entries = []
    for i, msg in enumerate(messages):
        entries.append({
            'Id': str(i),
            'ReceiptHandle': msg['ReceiptHandle']
        })
    
    sqs.delete_message_batch(
        QueueUrl=queue_url,
        Entries=entries
    )

def purge_queue():
    """Purge all messages from queue"""
    sqs.purge_queue(QueueUrl=queue_url)
```

## Best Practices

### 1. Use Long Polling

Long polling reduces API calls and costs while improving efficiency.

```python
# Enable long polling (20 seconds)
sqs.receive_message(
    QueueUrl=queue_url,
    WaitTimeSeconds=20  # Long polling
)
```

**Benefits:**
- Reduces API calls by up to 80%
- Lower latency for message delivery
- Lower costs

### 2. Set Appropriate Visibility Timeout

Set visibility timeout based on processing time.

```python
# Set visibility timeout to processing time + buffer
processing_time = 30  # seconds
buffer = 10  # seconds
visibility_timeout = processing_time + buffer

sqs.set_queue_attributes(
    QueueUrl=queue_url,
    Attributes={
        'VisibilityTimeout': str(visibility_timeout)
    }
)
```

**Best Practices:**
- Set timeout to processing time + buffer
- Too short: Messages become visible before processing completes
- Too long: Failed messages take longer to retry

### 3. Use Batch Operations

Batch operations reduce API calls and costs.

```python
# Send batch (up to 10 messages)
sqs.send_message_batch(
    QueueUrl=queue_url,
    Entries=[
        {'Id': '1', 'MessageBody': 'message1'},
        {'Id': '2', 'MessageBody': 'message2'},
        # ... up to 10 messages
    ]
)

# Delete batch (up to 10 messages)
sqs.delete_message_batch(
    QueueUrl=queue_url,
    Entries=[
        {'Id': '1', 'ReceiptHandle': 'handle1'},
        {'Id': '2', 'ReceiptHandle': 'handle2'},
        # ... up to 10 messages
    ]
)
```

### 4. Implement Dead Letter Queues

Handle messages that fail processing repeatedly.

```python
# Configure DLQ
redrive_policy = {
    'deadLetterTargetArn': dlq_arn,
    'maxReceiveCount': 3  # Move to DLQ after 3 failures
}

sqs.set_queue_attributes(
    QueueUrl=queue_url,
    Attributes={
        'RedrivePolicy': json.dumps(redrive_policy)
    }
)
```

### 5. Use Message Attributes

Add metadata to messages for filtering and routing.

```python
sqs.send_message(
    QueueUrl=queue_url,
    MessageBody=json.dumps(data),
    MessageAttributes={
        'Priority': {
            'StringValue': 'high',
            'DataType': 'String'
        },
        'Source': {
            'StringValue': 'user-service',
            'DataType': 'String'
        }
    }
)
```

### 6. Handle Idempotency

Ensure operations are idempotent to handle duplicate messages.

```python
def process_order(order_id, order_data):
    """Idempotent order processing"""
    # Check if already processed
    if is_order_processed(order_id):
        return  # Already processed, skip
    
    # Process order
    process_order_logic(order_data)
    
    # Mark as processed
    mark_order_processed(order_id)
```

### 7. Monitor Queue Metrics

Monitor queue depth and processing metrics.

```python
import boto3

cloudwatch = boto3.client('cloudwatch')
sqs = boto3.client('sqs')

def get_queue_metrics(queue_url):
    """Get queue metrics"""
    queue_name = queue_url.split('/')[-1]
    
    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/SQS',
        MetricName='ApproximateNumberOfMessagesVisible',
        Dimensions=[
            {'Name': 'QueueName', 'Value': queue_name}
        ],
        StartTime=datetime.now() - timedelta(hours=1),
        EndTime=datetime.now(),
        Period=300,
        Statistics=['Average']
    )
    return response
```

## Common Patterns

### 1. Producer-Consumer Pattern

```python
# Producer
def producer():
    for i in range(100):
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=f"Message {i}"
        )

# Consumer
def consumer():
    while True:
        messages = receive_messages()
        for message in messages:
            process_message(message['Body'])
            delete_message(message['ReceiptHandle'])
```

### 2. Fan-Out Pattern

Distribute messages to multiple queues.

```python
def fan_out(message, queue_urls):
    """Send message to multiple queues"""
    for queue_url in queue_urls:
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=message
        )
```

### 3. Priority Queue Pattern

Use message attributes for priority handling.

```python
def send_priority_message(message, priority='normal'):
    """Send message with priority"""
    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=message,
        MessageAttributes={
            'Priority': {
                'StringValue': priority,  # 'high', 'normal', 'low'
                'DataType': 'String'
            }
        }
    )
```

### 4. Request-Reply Pattern

Use message attributes for correlation.

```python
import uuid

def send_request(request_data):
    """Send request and wait for reply"""
    correlation_id = str(uuid.uuid4())
    
    sqs.send_message(
        QueueUrl=request_queue_url,
        MessageBody=json.dumps(request_data),
        MessageAttributes={
            'CorrelationId': {
                'StringValue': correlation_id,
                'DataType': 'String'
            }
        }
    )
    
    # Wait for reply
    return wait_for_reply(correlation_id)
```

## Troubleshooting

### Common Issues

**1. Messages Not Being Processed**
- Check visibility timeout
- Verify consumer is running
- Check IAM permissions
- Monitor queue metrics

**2. High Costs**
- Use long polling
- Use batch operations
- Optimize message size
- Review queue retention

**3. Duplicate Messages**
- Use FIFO queue for exactly-once processing
- Implement idempotency
- Use content-based deduplication

**4. Messages Stuck in Queue**
- Check consumer health
- Review visibility timeout
- Check for processing errors
- Monitor Dead Letter Queue

## Cost Optimization

**Tips:**
1. Use long polling to reduce API calls
2. Use batch operations (up to 10 messages)
3. Optimize message size (max 256 KB)
4. Set appropriate retention periods
5. Use Standard queues when order doesn't matter
6. Monitor and optimize queue depth

**Pricing:**
- First 1 million requests/month: Free
- Additional requests: $0.40 per million requests
- Data transfer: Standard AWS data transfer pricing

## Conclusion

Amazon SQS is a powerful message queuing service that enables you to build scalable, decoupled, and reliable applications. Key takeaways:

1. **Choose the right queue type** (Standard vs FIFO)
2. **Use long polling** to reduce costs and improve efficiency
3. **Implement Dead Letter Queues** for error handling
4. **Use batch operations** to reduce API calls
5. **Set appropriate visibility timeouts** based on processing time
6. **Monitor queue metrics** for performance optimization

Whether you're building microservices, processing tasks asynchronously, or implementing event-driven architectures, SQS provides the reliability and scalability you need.

## References

- [AWS SQS Documentation](https://docs.aws.amazon.com/sqs/)
- [AWS SQS Best Practices](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-best-practices.html)
- [boto3 SQS Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html)
- [AWS CLI SQS Commands](https://docs.aws.amazon.com/cli/latest/reference/sqs/)

