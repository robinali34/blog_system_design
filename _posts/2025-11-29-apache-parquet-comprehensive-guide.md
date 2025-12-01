---
layout: post
title: "Apache Parquet: Comprehensive Guide to Columnar Storage Format"
date: 2025-11-29
categories: [Apache Parquet, Columnar Storage, Data Format, Big Data, System Design, Technology]
excerpt: "A comprehensive guide to Apache Parquet, covering columnar storage, compression, schema evolution, and best practices for efficient data storage and analytics."
---

## Introduction

Apache Parquet is a columnar storage file format designed for efficient data storage and analytics. It's optimized for analytical workloads and provides high compression ratios and fast query performance. Understanding Parquet is essential for system design interviews involving data storage and analytics.

This guide covers:
- **Parquet Fundamentals**: Columnar storage, row groups, and pages
- **Schema**: Nested data structures and type system
- **Compression**: Codecs and optimization
- **Schema Evolution**: Adding and removing columns
- **Best Practices**: File organization, partitioning, and performance

## What is Apache Parquet?

Apache Parquet is a columnar storage format that:
- **Columnar Storage**: Stores data by columns
- **Compression**: High compression ratios
- **Schema Evolution**: Supports schema changes
- **Nested Data**: Supports complex nested structures
- **Cross-Language**: Works across multiple languages

### Key Concepts

**File**: Parquet file containing data

**Row Group**: Horizontal partition of data

**Column Chunk**: Column data within a row group

**Page**: Unit of compression and encoding

**Schema**: Data structure definition

## Architecture

### High-Level Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Data      │────▶│   Data      │────▶│   Data      │
│   Source    │     │   Source    │     │   Source    │
│  (Database) │     │  (Files)    │     │  (Stream)   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                    │                    │
       └────────────────────┴────────────────────┘
                            │
                            │ Write Data
                            │
                            ▼
              ┌─────────────────────────┐
              │   Parquet Writer        │
              │                         │
              │  ┌──────────┐           │
              │  │ Schema   │           │
              │  │ Definition│           │
              │  └────┬─────┘           │
              │       │                 │
              │  ┌────┴─────┐           │
              │  │ Columnar │           │
              │  │ Encoding │           │
              │  └──────────┘           │
              │                         │
              │  ┌───────────────────┐  │
              │  │  Parquet File     │  │
              │  │  (Storage)        │  │
              │  └───────────────────┘  │
              └──────┬──────────────────┘
                     │
                     │ Read Data
                     │
       ┌─────────────┴─────────────┐
       │                           │
┌──────▼──────┐           ┌───────▼──────┐
│   Analytics │           │   Data       │
│   Engine    │           │   Warehouse  │
│  (Spark)    │           │  (S3/HDFS)   │
└─────────────┘           └─────────────┘
```

**Explanation:**
- **Data Sources**: Systems that produce data (e.g., databases, file systems, data streams).
- **Parquet Writer**: Converts data into Parquet columnar format with schema definition and columnar encoding.
- **Schema Definition**: Defines the structure of data (columns, types, nested structures).
- **Columnar Encoding**: Stores data column-by-column for efficient compression and querying.
- **Parquet File (Storage)**: Binary file format stored on disk or object storage (S3, HDFS).
- **Analytics Engine**: Systems that read Parquet files for analytics (e.g., Spark, Presto, Hive).
- **Data Warehouse**: Storage systems that store Parquet files (e.g., S3, HDFS, data lakes).

### Core Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Parquet File                                 │
│                                                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │         File Metadata                           │    │
│  │  (Schema, Row Groups, Statistics)                 │    │
│  └──────────────────────────────────────────────────┘    │
│                          │                                │
│  ┌──────────────────────────────────────────────────┐    │
│  │         Row Group 1                              │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐      │    │
│  │  │ Column 1 │  │ Column 2 │  │ Column 3 │      │    │
│  │  └──────────┘  └──────────┘  └──────────┘      │    │
│  └──────────────────────────────────────────────────┘    │
│                          │                                │
│  ┌──────────────────────────────────────────────────┐    │
│  │         Row Group 2                              │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐      │    │
│  │  │ Column 1 │  │ Column 2 │  │ Column 3 │      │    │
│  │  └──────────┘  └──────────┘  └──────────┘      │    │
│  └──────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────┘
```

## Schema Definition

### Simple Schema

**Python:**
```python
import pyarrow as pa

schema = pa.schema([
    ('id', pa.int64()),
    ('name', pa.string()),
    ('age', pa.int32()),
    ('salary', pa.float64())
])
```

**Java:**
```java
MessageType schema = new MessageType(
    "schema",
    new PrimitiveType(Type.Repetition.REQUIRED, PrimitiveType.PrimitiveTypeName.INT64, "id"),
    new PrimitiveType(Type.Repetition.OPTIONAL, PrimitiveType.PrimitiveTypeName.BINARY, "name"),
    new PrimitiveType(Type.Repetition.OPTIONAL, PrimitiveType.PrimitiveTypeName.INT32, "age"),
    new PrimitiveType(Type.Repetition.OPTIONAL, PrimitiveType.PrimitiveTypeName.DOUBLE, "salary")
);
```

### Nested Schema

**Python:**
```python
schema = pa.schema([
    ('id', pa.int64()),
    ('name', pa.string()),
    ('address', pa.struct([
        ('street', pa.string()),
        ('city', pa.string()),
        ('zip', pa.string())
    ])),
    ('tags', pa.list_(pa.string()))
])
```

## Writing Parquet Files

### Python (PyArrow)

```python
import pyarrow as pa
import pyarrow.parquet as pq

# Create table
data = {
    'id': [1, 2, 3],
    'name': ['John', 'Jane', 'Bob'],
    'age': [30, 25, 35],
    'salary': [50000.0, 60000.0, 70000.0]
}
table = pa.Table.from_pydict(data)

# Write to Parquet
pq.write_table(table, 'data.parquet', compression='snappy')
```

### Java

```java
import org.apache.parquet.hadoop.ParquetWriter;
import org.apache.parquet.hadoop.metadata.CompressionCodecName;

ParquetWriter<Group> writer = ExampleParquetWriter.builder(new Path("data.parquet"))
    .withCompressionCodec(CompressionCodecName.SNAPPY)
    .withSchema(schema)
    .build();

Group group = factory.newGroup()
    .append("id", 1L)
    .append("name", "John")
    .append("age", 30)
    .append("salary", 50000.0);
writer.write(group);
writer.close();
```

## Reading Parquet Files

### Python (PyArrow)

```python
import pyarrow.parquet as pq

# Read entire file
table = pq.read_table('data.parquet')

# Read specific columns
table = pq.read_table('data.parquet', columns=['id', 'name'])

# Read with filters
table = pq.read_table('data.parquet', 
    filters=[('age', '>', 25)])
```

### Java

```java
import org.apache.parquet.hadoop.ParquetReader;

ParquetReader<Group> reader = ParquetReader.builder(new GroupReadSupport(), new Path("data.parquet"))
    .build();

Group group;
while ((group = reader.read()) != null) {
    long id = group.getLong("id", 0);
    String name = group.getString("name", 0);
    // Process data
}
reader.close();
```

## Compression

### Compression Codecs

**Snappy:**
```python
pq.write_table(table, 'data.parquet', compression='snappy')
```

**Gzip:**
```python
pq.write_table(table, 'data.parquet', compression='gzip')
```

**Zstd:**
```python
pq.write_table(table, 'data.parquet', compression='zstd')
```

**LZ4:**
```python
pq.write_table(table, 'data.parquet', compression='lz4')
```

### Compression Comparison

- **Snappy**: Fast compression, moderate ratio
- **Gzip**: Slower compression, better ratio
- **Zstd**: Balanced compression and speed
- **LZ4**: Very fast compression, lower ratio

## Schema Evolution

### Adding Columns

**Read with New Schema:**
```python
# Original schema
original_schema = pa.schema([
    ('id', pa.int64()),
    ('name', pa.string())
])

# New schema with additional column
new_schema = pa.schema([
    ('id', pa.int64()),
    ('name', pa.string()),
    ('email', pa.string())  # New column
])

# Read with new schema (email will be null)
table = pq.read_table('data.parquet', schema=new_schema)
```

### Removing Columns

**Read Subset:**
```python
# Read only specific columns
table = pq.read_table('data.parquet', columns=['id', 'name'])
```

## Partitioning

### Directory Partitioning

**Hive-Style Partitioning:**
```
data/
  year=2024/
    month=01/
      data.parquet
    month=02/
      data.parquet
  year=2023/
    month=12/
      data.parquet
```

**Read Partitioned Data:**
```python
dataset = pq.ParquetDataset('data/', 
    filters=[('year', '=', 2024), ('month', '=', 1)])
table = dataset.read()
```

## Best Practices

### 1. File Organization

- Use appropriate row group size (128MB-1GB)
- Partition by query patterns
- Co-locate related columns
- Use consistent schemas

### 2. Compression

- Use Snappy for balanced performance
- Use Gzip for better compression
- Test compression ratios
- Consider query patterns

### 3. Schema Design

- Use appropriate data types
- Minimize nested structures when possible
- Plan for schema evolution
- Document schema changes

### 4. Performance

- Use column projection
- Filter at file level
- Optimize row group size
- Monitor file sizes

## What Interviewers Look For

### Data Storage Understanding

1. **Parquet Concepts**
   - Understanding of columnar storage
   - Compression strategies
   - Schema evolution
   - **Red Flags**: No Parquet understanding, wrong storage, no schema evolution

2. **Storage Optimization**
   - Compression selection
   - File organization
   - Partitioning strategies
   - **Red Flags**: No compression, poor organization, no partitioning

3. **Performance**
   - Column projection
   - Filter pushdown
   - File size optimization
   - **Red Flags**: No optimization, poor performance, no filtering

### Problem-Solving Approach

1. **Storage Design**
   - File organization
   - Compression strategy
   - Partitioning design
   - **Red Flags**: Poor organization, wrong compression, no partitioning

2. **Schema Design**
   - Data type selection
   - Schema evolution planning
   - Nested structure design
   - **Red Flags**: Wrong types, no evolution, poor nesting

### System Design Skills

1. **Data Storage Architecture**
   - Parquet file organization
   - Compression strategy
   - Partitioning design
   - **Red Flags**: No architecture, poor compression, no partitioning

2. **Performance Optimization**
   - Column projection
   - Filter optimization
   - File size management
   - **Red Flags**: No optimization, poor performance, no management

### Communication Skills

1. **Clear Explanation**
   - Explains Parquet concepts
   - Discusses trade-offs
   - Justifies design decisions
   - **Red Flags**: Unclear explanations, no justification, confusing

### Meta-Specific Focus

1. **Data Storage Expertise**
   - Understanding of columnar storage
   - Parquet mastery
   - Compression optimization
   - **Key**: Demonstrate data storage expertise

2. **System Design Skills**
   - Can design storage systems
   - Understands storage challenges
   - Makes informed trade-offs
   - **Key**: Show practical storage design skills

## Summary

**Apache Parquet Key Points:**
- **Columnar Storage**: Optimized for analytical queries
- **High Compression**: Efficient data storage
- **Schema Evolution**: Supports schema changes
- **Nested Data**: Complex data structures
- **Cross-Language**: Works across languages

**Common Use Cases:**
- Data warehousing
- Analytics storage
- Big data processing
- Data lake storage
- ETL pipelines
- Query optimization

**Best Practices:**
- Use appropriate compression
- Partition by query patterns
- Optimize row group size
- Use column projection
- Filter at file level
- Plan for schema evolution
- Monitor file sizes

Apache Parquet is a powerful columnar storage format optimized for analytical workloads and efficient data storage.

