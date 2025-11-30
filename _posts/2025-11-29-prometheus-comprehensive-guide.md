---
layout: post
title: "Prometheus: Comprehensive Guide to Monitoring and Metrics Collection"
date: 2025-11-29
categories: [Prometheus, Monitoring, Metrics, Observability, System Design, Technology]
excerpt: "A comprehensive guide to Prometheus, covering metrics collection, time-series database, query language (PromQL), alerting, and best practices for building observability systems."
---

## Introduction

Prometheus is an open-source monitoring and alerting toolkit designed for reliability and scalability. It collects metrics from configured targets, stores them in a time-series database, and provides a powerful query language for analysis. Understanding Prometheus is essential for system design interviews involving observability and monitoring.

This guide covers:
- **Prometheus Fundamentals**: Architecture, metrics, and data model
- **PromQL**: Query language for metrics analysis
- **Service Discovery**: Automatic target discovery
- **Alerting**: Alert rules and Alertmanager
- **Best Practices**: Metric naming, labeling, and performance

## What is Prometheus?

Prometheus is a monitoring system that:
- **Metrics Collection**: Pulls metrics from targets
- **Time-Series Database**: Stores metrics efficiently
- **Query Language**: PromQL for analysis
- **Alerting**: Alertmanager for notifications
- **Multi-Dimensional**: Labels for flexible querying

### Key Concepts

**Metric**: Time series with name and labels

**Label**: Key-value pair for metric dimensions

**Target**: Endpoint being monitored

**Scrape**: Collection of metrics from target

**Job**: Collection of targets

**Instance**: Single target

## Core Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Prometheus Server                           │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │         Scrape Targets                          │   │
│  │  (HTTP Endpoints, Exporters)                    │   │
│  └──────────────────────────────────────────────────┘   │
│                          │                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │         Time-Series Database                    │   │
│  │  (Local Storage)                                 │   │
│  └──────────────────────────────────────────────────┘   │
│                          │                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │         PromQL Query Engine                     │   │
│  │  (Query Language)                                │   │
│  └──────────────────────────────────────────────────┘   │
│                          │                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │         Alertmanager                             │   │
│  │  (Alert Routing, Notifications)                  │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

## Metrics Types

### Counter

**Monotonically increasing value:**
```prometheus
http_requests_total{method="GET", status="200"} 1234
http_requests_total{method="POST", status="500"} 56
```

**Use Cases:**
- Request counts
- Error counts
- Bytes transferred

### Gauge

**Value that can go up or down:**
```prometheus
memory_usage_bytes{instance="server1"} 1024000
cpu_usage_percent{instance="server1"} 75.5
```

**Use Cases:**
- Current memory usage
- Active connections
- Queue size

### Histogram

**Distribution of values:**
```prometheus
http_request_duration_seconds_bucket{le="0.1"} 100
http_request_duration_seconds_bucket{le="0.5"} 200
http_request_duration_seconds_bucket{le="1.0"} 250
http_request_duration_seconds_bucket{le="+Inf"} 300
http_request_duration_seconds_sum 150.5
http_request_duration_seconds_count 300
```

**Use Cases:**
- Request latency
- Response sizes
- Processing time

### Summary

**Similar to histogram, with quantiles:**
```prometheus
http_request_duration_seconds{quantile="0.5"} 0.1
http_request_duration_seconds{quantile="0.9"} 0.5
http_request_duration_seconds{quantile="0.99"} 1.0
http_request_duration_seconds_sum 150.5
http_request_duration_seconds_count 300
```

## PromQL (Prometheus Query Language)

### Basic Queries

**Select metric:**
```promql
http_requests_total
```

**Filter by label:**
```promql
http_requests_total{method="GET"}
```

**Multiple label filters:**
```promql
http_requests_total{method="GET", status="200"}
```

### Rate and Increase

**Rate over time:**
```promql
rate(http_requests_total[5m])
```

**Increase over time:**
```promql
increase(http_requests_total[5m])
```

### Aggregation

**Sum:**
```promql
sum(http_requests_total)
```

**Average:**
```promql
avg(cpu_usage_percent)
```

**Group by:**
```promql
sum(http_requests_total) by (method)
```

**Max/Min:**
```promql
max(memory_usage_bytes)
min(cpu_usage_percent)
```

### Functions

**Rate:**
```promql
rate(http_requests_total[5m])
```

**Histogram Quantile:**
```promql
histogram_quantile(0.95, http_request_duration_seconds_bucket)
```

**Time:**
```promql
time() - process_start_time_seconds
```

**Label Replace:**
```promql
label_replace(http_requests_total, "service", "$1", "instance", "(.*):.*")
```

## Configuration

### prometheus.yml

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'production'
    environment: 'prod'

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'application'
    static_configs:
      - targets: ['app1:8080', 'app2:8080']
    metrics_path: '/metrics'
    scrape_interval: 10s
```

### Service Discovery

**Kubernetes:**
```yaml
scrape_configs:
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
```

**Consul:**
```yaml
scrape_configs:
  - job_name: 'consul'
    consul_sd_configs:
      - server: 'consul:8500'
```

## Instrumentation

### Go Client

```go
package main

import (
    "net/http"
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promhttp"
)

var (
    httpRequestsTotal = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "http_requests_total",
            Help: "Total number of HTTP requests",
        },
        []string{"method", "status"},
    )
    
    httpRequestDuration = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name: "http_request_duration_seconds",
            Help: "HTTP request duration",
        },
        []string{"method"},
    )
)

func init() {
    prometheus.MustRegister(httpRequestsTotal)
    prometheus.MustRegister(httpRequestDuration)
}

func handler(w http.ResponseWriter, r *http.Request) {
    timer := prometheus.NewTimer(httpRequestDuration.WithLabelValues(r.Method))
    defer timer.ObserveDuration()
    
    // Handle request
    httpRequestsTotal.WithLabelValues(r.Method, "200").Inc()
}

func main() {
    http.HandleFunc("/", handler)
    http.Handle("/metrics", promhttp.Handler())
    http.ListenAndServe(":8080", nil)
}
```

### Python Client

```python
from prometheus_client import Counter, Histogram, start_http_server
import time

http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'status']
)

http_request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method']
)

def handle_request(method, status):
    with http_request_duration.labels(method=method).time():
        # Process request
        http_requests_total.labels(method=method, status=status).inc()

# Start metrics server
start_http_server(8000)
```

## Alerting

### Alert Rules

**alert_rules.yml:**
```yaml
groups:
  - name: example
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status="500"}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors/sec"

      - alert: HighMemoryUsage
        expr: memory_usage_bytes / memory_total_bytes > 0.9
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value | humanizePercentage }}"
```

### Alertmanager Configuration

**alertmanager.yml:**
```yaml
route:
  group_by: ['alertname', 'cluster']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'default'
  routes:
    - match:
        severity: critical
      receiver: 'critical-alerts'
    - match:
        severity: warning
      receiver: 'warning-alerts'

receivers:
  - name: 'default'
    webhook_configs:
      - url: 'http://webhook:5000/alerts'
  
  - name: 'critical-alerts'
    email_configs:
      - to: 'oncall@example.com'
        from: 'alerts@example.com'
        smarthost: 'smtp.example.com:587'
  
  - name: 'warning-alerts'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/...'
        channel: '#alerts'
```

## Best Practices

### 1. Metric Naming

- Use descriptive names
- Follow naming conventions
- Use base units (seconds, bytes)
- Avoid high cardinality

**Good:**
```
http_requests_total
cpu_usage_percent
memory_usage_bytes
```

**Bad:**
```
requests
cpu
memory
```

### 2. Labeling

- Use labels for dimensions
- Avoid high cardinality labels
- Keep label names consistent
- Use appropriate label values

**Good:**
```
http_requests_total{method="GET", status="200", endpoint="/api/users"}
```

**Bad:**
```
http_requests_total{user_id="12345", request_id="abc123"}
```

### 3. Recording Rules

**Pre-compute queries:**
```yaml
groups:
  - name: recording_rules
    interval: 30s
    rules:
      - record: http:requests:rate5m
        expr: rate(http_requests_total[5m])
```

### 4. Performance

- Limit scrape interval
- Use recording rules
- Optimize queries
- Monitor Prometheus itself

## What Interviewers Look For

### Monitoring Understanding

1. **Prometheus Concepts**
   - Understanding of metrics, labels, targets
   - PromQL query language
   - Alerting rules
   - **Red Flags**: No Prometheus understanding, wrong concepts, poor queries

2. **Observability**
   - Metrics vs logs vs traces
   - Monitoring strategies
   - Alerting design
   - **Red Flags**: No observability understanding, poor monitoring, no alerts

3. **Performance**
   - Metric cardinality
   - Query optimization
   - Storage efficiency
   - **Red Flags**: High cardinality, poor queries, no optimization

### Problem-Solving Approach

1. **Metric Design**
   - Choose appropriate metric types
   - Design labels
   - Avoid cardinality explosion
   - **Red Flags**: Wrong types, high cardinality, poor design

2. **Alerting Design**
   - Define alert rules
   - Set appropriate thresholds
   - Route alerts properly
   - **Red Flags**: No alerts, wrong thresholds, poor routing

### System Design Skills

1. **Observability Architecture**
   - Monitoring system design
   - Metric collection
   - Alerting pipeline
   - **Red Flags**: No monitoring, poor architecture, no alerts

2. **Scalability**
   - Handle high cardinality
   - Optimize queries
   - Scale Prometheus
   - **Red Flags**: No scaling, poor performance, no optimization

### Communication Skills

1. **Clear Explanation**
   - Explains monitoring concepts
   - Discusses trade-offs
   - Justifies design decisions
   - **Red Flags**: Unclear explanations, no justification, confusing

### Meta-Specific Focus

1. **Observability Expertise**
   - Understanding of monitoring
   - Prometheus mastery
   - Alerting design
   - **Key**: Demonstrate observability expertise

2. **System Design Skills**
   - Can design monitoring systems
   - Understands observability challenges
   - Makes informed trade-offs
   - **Key**: Show practical observability design skills

## Summary

**Prometheus Key Points:**
- **Metrics Collection**: Pull-based metric collection
- **Time-Series Database**: Efficient storage of metrics
- **PromQL**: Powerful query language
- **Multi-Dimensional**: Labels for flexible querying
- **Alerting**: Alertmanager for notifications
- **Service Discovery**: Automatic target discovery

**Common Use Cases:**
- Application monitoring
- Infrastructure monitoring
- Service health checks
- Performance monitoring
- Alerting and notifications
- Capacity planning

**Best Practices:**
- Use appropriate metric types
- Design labels carefully
- Avoid high cardinality
- Use recording rules
- Optimize queries
- Set up proper alerting
- Monitor Prometheus itself

Prometheus is a powerful monitoring system that provides comprehensive observability for modern applications and infrastructure.

