---
layout: post
title: "Apache Airflow: Comprehensive Guide to Workflow Orchestration"
date: 2025-11-29
categories: [Apache Airflow, Workflow Orchestration, Data Pipeline, ETL, System Design, Technology]
excerpt: "A comprehensive guide to Apache Airflow, covering DAGs, tasks, operators, scheduling, and best practices for building and managing data pipelines and workflows."
---

## Introduction

Apache Airflow is an open-source platform for programmatically authoring, scheduling, and monitoring workflows. It's designed to manage complex data pipelines and ETL processes. Understanding Airflow is essential for system design interviews involving data pipelines and workflow orchestration.

This guide covers:
- **Airflow Fundamentals**: DAGs, tasks, operators, and execution
- **Scheduling**: Cron expressions, dependencies, and triggers
- **Operators**: Built-in and custom operators
- **Monitoring**: Logs, metrics, and alerting
- **Best Practices**: DAG design, performance, and reliability

## What is Apache Airflow?

Apache Airflow is a workflow orchestration platform that:
- **DAG-Based**: Workflows defined as Directed Acyclic Graphs
- **Python-Based**: Define workflows in Python
- **Scheduling**: Cron-based scheduling
- **Monitoring**: Web UI for monitoring and debugging
- **Extensible**: Custom operators and plugins

### Key Concepts

**DAG (Directed Acyclic Graph)**: Workflow definition

**Task**: Unit of work in a DAG

**Operator**: Template for a task

**Task Instance**: Specific execution of a task

**Scheduler**: Component that triggers DAGs

**Executor**: Component that executes tasks

## Architecture

### High-Level Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   User      │────▶│   User      │────▶│   User      │
│  (DevOps)   │     │  (Data Eng) │     │  (Analyst)  │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                    │                    │
       └────────────────────┴────────────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │   Airflow Web UI        │
              │   (DAG Management)      │
              └──────┬──────────────────┘
                     │
                     ▼
              ┌─────────────────────────┐
              │   Airflow Scheduler    │
              │   (DAG Parsing,        │
              │    Task Scheduling)     │
              └──────┬──────────────────┘
                     │
                     ▼
              ┌─────────────────────────┐
              │   Executor              │
              │   (Task Execution)      │
              └──────┬──────────────────┘
                     │
       ┌─────────────┴─────────────┐
       │                           │
┌──────▼──────┐           ┌───────▼──────┐
│   Worker    │           │   Worker     │
│   Node 1    │           │   Node 2     │
│  (Tasks)    │           │  (Tasks)     │
└─────────────┘           └─────────────┘
```

**Explanation:**
- **Users**: Data engineers, DevOps engineers, and analysts who create and manage workflows (DAGs).
- **Airflow Web UI**: Web interface for monitoring DAGs, viewing task logs, and managing workflows.
- **Airflow Scheduler**: Parses DAGs, schedules tasks based on dependencies and schedules, and manages task execution.
- **Executor**: Component that determines how tasks are executed (e.g., LocalExecutor, CeleryExecutor, KubernetesExecutor).
- **Worker Nodes**: Machines that execute tasks. Workers pull tasks from the queue and execute them.

### Core Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Airflow Cluster                             │
│                                                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │         Scheduler                                 │    │
│  │  (DAG Parsing, Task Scheduling)                   │    │
│  └──────────────────────────────────────────────────┘    │
│                          │                                │
│  ┌──────────────────────────────────────────────────┐    │
│  │         Executor                                  │    │
│  │  (Task Execution, Resource Management)            │    │
│  └──────────────────────────────────────────────────┘    │
│                          │                                │
│  ┌──────────────────────────────────────────────────┐    │
│  │         Workers                                   │    │
│  │  (Task Execution)                                  │    │
│  └──────────────────────────────────────────────────┘    │
│                          │                                │
│  ┌──────────────────────────────────────────────────┐    │
│  │         Metadata Database                         │    │
│  │  (DAG State, Task History)                        │    │
│  └──────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────┘
```

## DAG Definition

### Basic DAG

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'my_dag',
    default_args=default_args,
    description='A simple DAG',
    schedule_interval=timedelta(days=1),
    catchup=False,
)

# Define tasks
task1 = BashOperator(
    task_id='task1',
    bash_command='echo "Hello from task1"',
    dag=dag,
)

task2 = BashOperator(
    task_id='task2',
    bash_command='echo "Hello from task2"',
    dag=dag,
)

# Set dependencies
task1 >> task2
```

### DAG with Multiple Tasks

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

def process_data():
    print("Processing data...")
    return "Data processed"

dag = DAG(
    'data_pipeline',
    default_args=default_args,
    schedule_interval='@daily',
)

extract = BashOperator(
    task_id='extract',
    bash_command='python extract.py',
    dag=dag,
)

transform = PythonOperator(
    task_id='transform',
    python_callable=process_data,
    dag=dag,
)

load = BashOperator(
    task_id='load',
    bash_command='python load.py',
    dag=dag,
)

# Define dependencies
extract >> transform >> load
```

## Operators

### Built-in Operators

**BashOperator:**
```python
from airflow.operators.bash import BashOperator

task = BashOperator(
    task_id='bash_task',
    bash_command='echo "Hello World"',
    dag=dag,
)
```

**PythonOperator:**
```python
from airflow.operators.python import PythonOperator

def my_function():
    print("Hello from Python")

task = PythonOperator(
    task_id='python_task',
    python_callable=my_function,
    dag=dag,
)
```

**SQLOperator:**
```python
from airflow.providers.postgres.operators.postgres import PostgresOperator

task = PostgresOperator(
    task_id='sql_task',
    postgres_conn_id='postgres_default',
    sql='SELECT * FROM users',
    dag=dag,
)
```

**EmailOperator:**
```python
from airflow.operators.email import EmailOperator

task = EmailOperator(
    task_id='send_email',
    to='user@example.com',
    subject='Airflow Alert',
    html_content='<h1>Task completed</h1>',
    dag=dag,
)
```

### Custom Operator

```python
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class MyCustomOperator(BaseOperator):
    @apply_defaults
    def __init__(self, my_param, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.my_param = my_param
    
    def execute(self, context):
        print(f"Executing with param: {self.my_param}")
        # Your custom logic here
```

## Task Dependencies

### Linear Dependencies

```python
# Method 1: Using >>
task1 >> task2 >> task3

# Method 2: Using set_downstream
task1.set_downstream(task2)
task2.set_downstream(task3)
```

### Parallel Dependencies

```python
# Multiple tasks depend on one
task1 >> [task2, task3, task4]

# One task depends on multiple
[task2, task3, task4] >> task5
```

### Complex Dependencies

```python
# Complex graph
task1 >> task2
task1 >> task3
task2 >> task4
task3 >> task4
task4 >> task5
```

## Scheduling

### Schedule Interval

**Cron Expression:**
```python
dag = DAG(
    'my_dag',
    schedule_interval='0 0 * * *',  # Daily at midnight
    dag=dag,
)
```

**Timedelta:**
```python
dag = DAG(
    'my_dag',
    schedule_interval=timedelta(hours=1),  # Every hour
    dag=dag,
)
```

**Preset:**
```python
dag = DAG(
    'my_dag',
    schedule_interval='@daily',  # Daily
    dag=dag,
)
```

### Catchup

**Disable Catchup:**
```python
dag = DAG(
    'my_dag',
    catchup=False,  # Don't backfill
    dag=dag,
)
```

## Variables and Connections

### Variables

**Set Variable:**
```python
from airflow.models import Variable

# In code
Variable.set("my_key", "my_value")

# In UI: Admin > Variables
```

**Use Variable:**
```python
from airflow.models import Variable

my_value = Variable.get("my_key")
```

### Connections

**Create Connection:**
```python
from airflow.models import Connection
from airflow import settings

conn = Connection(
    conn_id='my_postgres',
    conn_type='postgres',
    host='localhost',
    login='user',
    password='password',
    port=5432,
    schema='mydb'
)
session = settings.Session()
session.add(conn)
session.commit()
```

**Use Connection:**
```python
from airflow.hooks.postgres_hook import PostgresHook

hook = PostgresHook(postgres_conn_id='my_postgres')
records = hook.get_records('SELECT * FROM users')
```

## XComs (Cross-Communication)

### Push and Pull Values

```python
from airflow.operators.python import PythonOperator

def push_value(**context):
    context['ti'].xcom_push(key='my_key', value='my_value')

def pull_value(**context):
    value = context['ti'].xcom_pull(key='my_key')
    print(f"Pulled value: {value}")

task1 = PythonOperator(
    task_id='push',
    python_callable=push_value,
    dag=dag,
)

task2 = PythonOperator(
    task_id='pull',
    python_callable=pull_value,
    dag=dag,
)

task1 >> task2
```

## Sensors

### File Sensor

```python
from airflow.sensors.filesystem import FileSensor

file_sensor = FileSensor(
    task_id='wait_for_file',
    filepath='/path/to/file',
    poke_interval=60,
    timeout=3600,
    dag=dag,
)
```

### SQL Sensor

```python
from airflow.sensors.sql import SqlSensor

sql_sensor = SqlSensor(
    task_id='wait_for_data',
    conn_id='postgres_default',
    sql="SELECT COUNT(*) FROM users WHERE created_at > '2024-01-01'",
    poke_interval=60,
    dag=dag,
)
```

## Best Practices

### 1. DAG Design

- Keep DAGs focused and modular
- Use descriptive task IDs
- Set appropriate retries
- Handle failures gracefully

### 2. Performance

- Use appropriate operators
- Avoid long-running tasks
- Use sensors efficiently
- Monitor resource usage

### 3. Reliability

- Set retry policies
- Use idempotent tasks
- Handle dependencies properly
- Monitor task failures

### 4. Security

- Secure connections
- Use variables for secrets
- Limit permissions
- Audit access

## What Interviewers Look For

### Workflow Orchestration Understanding

1. **Airflow Concepts**
   - Understanding of DAGs, tasks, operators
   - Scheduling mechanisms
   - Task dependencies
   - **Red Flags**: No Airflow understanding, wrong concepts, poor dependencies

2. **Data Pipeline Design**
   - ETL patterns
   - Error handling
   - Monitoring and alerting
   - **Red Flags**: Poor patterns, no error handling, no monitoring

3. **Scalability**
   - Worker management
   - Resource allocation
   - Performance optimization
   - **Red Flags**: No scaling, poor resources, no optimization

### Problem-Solving Approach

1. **DAG Design**
   - Task organization
   - Dependency management
   - Error handling
   - **Red Flags**: Poor organization, wrong dependencies, no error handling

2. **Pipeline Design**
   - ETL patterns
   - Data quality checks
   - Monitoring strategies
   - **Red Flags**: Poor patterns, no quality checks, no monitoring

### System Design Skills

1. **Workflow Architecture**
   - Airflow cluster design
   - DAG organization
   - Resource management
   - **Red Flags**: No architecture, poor organization, no resource management

2. **Scalability**
   - Worker scaling
   - Resource optimization
   - Performance tuning
   - **Red Flags**: No scaling, poor optimization, no tuning

### Communication Skills

1. **Clear Explanation**
   - Explains Airflow concepts
   - Discusses trade-offs
   - Justifies design decisions
   - **Red Flags**: Unclear explanations, no justification, confusing

### Meta-Specific Focus

1. **Data Pipeline Expertise**
   - Understanding of workflow orchestration
   - Airflow mastery
   - ETL patterns
   - **Key**: Demonstrate data pipeline expertise

2. **System Design Skills**
   - Can design workflow systems
   - Understands orchestration challenges
   - Makes informed trade-offs
   - **Key**: Show practical workflow design skills

## Summary

**Apache Airflow Key Points:**
- **DAG-Based**: Workflows as Directed Acyclic Graphs
- **Python-Based**: Define workflows in Python
- **Scheduling**: Cron-based scheduling
- **Operators**: Built-in and custom operators
- **Monitoring**: Web UI for monitoring and debugging
- **Extensible**: Custom operators and plugins

**Common Use Cases:**
- ETL pipelines
- Data processing workflows
- Scheduled jobs
- Data quality checks
- Report generation
- Machine learning pipelines

**Best Practices:**
- Keep DAGs focused and modular
- Use appropriate operators
- Set retry policies
- Handle dependencies properly
- Monitor task failures
- Use variables for configuration
- Secure connections and secrets

Apache Airflow is a powerful platform for orchestrating complex data pipelines and workflows with reliability and scalability.

