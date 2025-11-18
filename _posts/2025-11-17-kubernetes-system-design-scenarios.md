---
layout: post
title: "Kubernetes (K8s) in System Design: Common Scenarios and Use Cases - Interview Guide"
date: 2025-11-17
categories: [System Design, Interview Preparation, Kubernetes, Container Orchestration, DevOps, Distributed Systems, Microservices]
excerpt: "A comprehensive guide to using Kubernetes (K8s) in system design interviews, covering key concepts, common scenarios, deployment patterns, scaling strategies, and how to incorporate K8s into your system design solutions."
---

## Introduction

Kubernetes (K8s) has become the de facto standard for container orchestration in modern distributed systems. Understanding how to incorporate Kubernetes into system design solutions is crucial for designing scalable, reliable, and maintainable systems.

This guide covers Kubernetes concepts, common use cases in system design interviews, deployment patterns, scaling strategies, and how to discuss K8s effectively during system design interviews.

## Table of Contents

1. [Kubernetes Overview](#kubernetes-overview)
2. [Key Kubernetes Concepts](#key-kubernetes-concepts)
3. [Common System Design Scenarios](#common-system-design-scenarios)
4. [Kubernetes Components in System Design](#kubernetes-components-in-system-design)
5. [Deployment Patterns](#deployment-patterns)
6. [Scaling Strategies](#scaling-strategies)
7. [High Availability and Fault Tolerance](#high-availability-and-fault-tolerance)
8. [Networking in Kubernetes](#networking-in-kubernetes)
9. [Storage in Kubernetes](#storage-in-kubernetes)
10. [Monitoring and Observability](#monitoring-and-observability)
11. [Security Considerations](#security-considerations)
12. [Trade-offs and Best Practices](#trade-offs-and-best-practices)
13. [Interview Tips](#interview-tips)
14. [Summary](#summary)

## Kubernetes Overview

### What is Kubernetes?

Kubernetes is an open-source container orchestration platform that automates the deployment, scaling, and management of containerized applications. It provides:

- **Container Orchestration**: Manages containers across multiple nodes
- **Self-Healing**: Automatically restarts failed containers
- **Auto-Scaling**: Scales applications based on demand
- **Service Discovery**: Enables services to find each other
- **Load Balancing**: Distributes traffic across pods
- **Rolling Updates**: Updates applications with zero downtime
- **Resource Management**: Allocates CPU and memory efficiently

### Why Kubernetes in System Design?

When designing systems, Kubernetes helps with:

1. **Scalability**: Easy horizontal scaling of services
2. **Reliability**: Self-healing and fault tolerance
3. **Resource Efficiency**: Better resource utilization
4. **Deployment Automation**: CI/CD integration
5. **Multi-Cloud**: Run anywhere (AWS, GCP, Azure, on-premises)
6. **Microservices**: Perfect for microservices architecture
7. **DevOps**: Infrastructure as code, GitOps

## Key Kubernetes Concepts

### Core Components

**Pod**: Smallest deployable unit in Kubernetes. Contains one or more containers sharing network and storage.

**Deployment**: Manages replica sets and provides declarative updates for Pods.

**Service**: Abstract way to expose an application running on Pods as a network service.

**Namespace**: Virtual cluster within a physical cluster, used for resource isolation.

**Node**: Worker machine (VM or physical) that runs containers.

**Cluster**: Set of nodes running containerized applications.

**ConfigMap**: Stores non-confidential configuration data.

**Secret**: Stores sensitive data (passwords, tokens, keys).

**Ingress**: Manages external access to services, typically HTTP/HTTPS.

**StatefulSet**: Manages stateful applications with stable network identities.

**DaemonSet**: Ensures all nodes run a copy of a Pod.

**Job**: Creates one or more Pods and ensures they complete successfully.

**CronJob**: Runs Jobs on a time-based schedule.

### Key Concepts for System Design

**ReplicaSet**: Ensures a specified number of Pod replicas are running.

**Horizontal Pod Autoscaler (HPA)**: Automatically scales the number of Pods based on CPU/memory usage.

**Vertical Pod Autoscaler (VPA)**: Automatically adjusts Pod resource requests/limits.

**Cluster Autoscaler**: Automatically adjusts cluster size based on demand.

**Service Mesh**: Infrastructure layer for microservices communication (Istio, Linkerd).

**Helm**: Package manager for Kubernetes applications.

## Common System Design Scenarios

### Scenario 1: Microservices Architecture

**Problem**: Design a microservices-based e-commerce platform.

**Kubernetes Solution**:

```
┌─────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                    │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │              Ingress Controller                   │  │
│  │         (NGINX / Traefik / AWS ALB)             │  │
│  └──────────────────┬───────────────────────────────┘  │
│                     │                                    │
│  ┌──────────────────┴───────────────────────────────┐  │
│  │              Service Mesh (Istio)                │  │
│  └──────────────────┬───────────────────────────────┘  │
│                     │                                    │
│  ┌──────────────────┴───────────────────────────────┐  │
│  │                                                  │  │
│  │  ┌──────────────┐  ┌──────────────┐           │  │
│  │  │   User       │  │   Product    │           │  │
│  │  │   Service    │  │   Service    │           │  │
│  │  │  (Deployment) │  │  (Deployment)│           │  │
│  │  └──────┬───────┘  └──────┬───────┘           │  │
│  │         │                 │                     │  │
│  │  ┌──────┴─────────────────┴───────┐           │  │
│  │  │      Order Service              │           │  │
│  │  │      (Deployment)               │           │  │
│  │  └──────────────────────────────────┘           │  │
│  │                                                  │  │
│  │  ┌──────────────┐  ┌──────────────┐           │  │
│  │  │   Payment    │  │  Inventory   │           │  │
│  │  │   Service    │  │   Service    │           │  │
│  │  │  (Deployment) │  │  (Deployment)│           │  │
│  │  └──────────────┘  └──────────────┘           │  │
│  │                                                  │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │         External Services                         │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐      │  │
│  │  │Database │  │  Redis   │  │  Kafka   │      │  │
│  │  │(Stateful│  │ (Deploy)  │  │ (Deploy) │      │  │
│  │  │  Set)   │  │           │  │          │      │  │
│  │  └──────────┘  └──────────┘  └──────────┘      │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

**Key Kubernetes Resources**:

```yaml
# User Service Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
      - name: user-service
        image: user-service:latest
        ports:
        - containerPort: 8080
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
---
apiVersion: v1
kind: Service
metadata:
  name: user-service
spec:
  selector:
    app: user-service
  ports:
  - port: 80
    targetPort: 8080
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: user-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: user-service
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**Benefits**:
- Each microservice runs in its own Pods
- Independent scaling per service
- Service discovery via Kubernetes Services
- Health checks and self-healing
- Rolling updates per service
- Resource isolation

---

### Scenario 2: High-Traffic Web Application

**Problem**: Design a web application handling 1M+ requests per second.

**Kubernetes Solution**:

```
┌─────────────────────────────────────────────────────────┐
│              Kubernetes Cluster (Multi-Zone)            │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Load Balancer (AWS ALB / GCP LB)         │  │
│  └──────────────────┬───────────────────────────────┘  │
│                     │                                    │
│  ┌──────────────────┴───────────────────────────────┐  │
│  │            Ingress Controller                      │  │
│  │         (NGINX with HPA)                          │  │
│  └──────────────────┬───────────────────────────────┘  │
│                     │                                    │
│  ┌──────────────────┴───────────────────────────────┐  │
│  │                                                  │  │
│  │  Zone 1          Zone 2          Zone 3        │  │
│  │  ┌─────┐        ┌─────┐        ┌─────┐        │  │
│  │  │ Pod │        │ Pod │        │ Pod │        │  │
│  │  │ Pod │        │ Pod │        │ Pod │        │  │
│  │  │ Pod │        │ Pod │        │ Pod │        │  │
│  │  └─────┘        └─────┘        └─────┘        │  │
│  │                                                  │  │
│  │  ┌──────────────────────────────────────────┐  │  │
│  │  │      Web App Deployment (100+ replicas)   │  │  │
│  │  │      HPA: CPU 70%, Memory 80%            │  │  │
│  │  └──────────────────────────────────────────┘  │  │
│  │                                                  │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Cache Layer (Redis)                       │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐      │  │
│  │  │ Redis    │  │ Redis    │  │ Redis    │      │  │
│  │  │ Master   │  │ Replica  │  │ Replica  │      │  │
│  │  │(Stateful │  │(Stateful │  │(Stateful │      │  │
│  │  │   Set)   │  │   Set)   │  │   Set)   │      │  │
│  │  └──────────┘  └──────────┘  └──────────┘      │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Database (PostgreSQL)                      │  │
│  │  ┌──────────┐  ┌──────────┐                      │  │
│  │  │ Primary  │  │ Replica  │                      │  │
│  │  │(Stateful │  │(Stateful │                      │  │
│  │  │   Set)   │  │   Set)   │                      │  │
│  │  └──────────┘  └──────────┘                      │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

**Key Features**:
- **Horizontal Pod Autoscaler**: Auto-scales based on CPU/memory
- **Cluster Autoscaler**: Adds/removes nodes based on demand
- **Pod Disruption Budget**: Ensures minimum availability during updates
- **Multi-Zone Deployment**: Distributes Pods across availability zones
- **Resource Quotas**: Limits resource usage per namespace

**Scaling Configuration**:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  minReplicas: 10
  maxReplicas: 500
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "100"
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      - type: Pods
        value: 10
        periodSeconds: 15
      selectPolicy: Max
```

---

### Scenario 3: Real-Time Data Processing Pipeline

**Problem**: Design a real-time data processing system with Kafka, Flink, and storage.

**Kubernetes Solution**:

```
┌─────────────────────────────────────────────────────────┐
│              Kubernetes Cluster                          │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Data Ingestion (Kafka)                    │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐      │  │
│  │  │ Kafka    │  │ Kafka    │  │ Kafka    │      │  │
│  │  │ Broker 1 │  │ Broker 2 │  │ Broker 3 │      │  │
│  │  │(Stateful │  │(Stateful │  │(Stateful │      │  │
│  │  │   Set)   │  │   Set)   │  │   Set)   │      │  │
│  │  └──────────┘  └──────────┘  └──────────┘      │  │
│  └──────────────────┬───────────────────────────────┘  │
│                     │                                    │
│  ┌──────────────────┴───────────────────────────────┐  │
│  │         Stream Processing (Flink)                 │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐      │  │
│  │  │ Flink    │  │ Flink    │  │ Flink    │      │  │
│  │  │TaskMgr 1 │  │TaskMgr 2 │  │TaskMgr 3 │      │  │
│  │  │(Deploy) │  │(Deploy) │  │(Deploy) │      │  │
│  │  └──────────┘  └──────────┘  └──────────┘      │  │
│  │                                                  │  │
│  │  ┌──────────┐                                   │  │
│  │  │ Flink    │                                   │  │
│  │  │JobMgr   │                                   │  │
│  │  │(Deploy) │                                   │  │
│  │  └──────────┘                                   │  │
│  └──────────────────┬───────────────────────────────┘  │
│                     │                                    │
│  ┌──────────────────┴───────────────────────────────┐  │
│  │         Storage Layer                             │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐      │  │
│  │  │Cassandra │  │Cassandra │  │Cassandra │      │  │
│  │  │ Node 1   │  │ Node 2   │  │ Node 3   │      │  │
│  │  │(Stateful │  │(Stateful │  │(Stateful │      │  │
│  │  │   Set)   │  │   Set)   │  │   Set)   │      │  │
│  │  └──────────┘  └──────────┘  └──────────┘      │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

**Key Kubernetes Resources**:

```yaml
# Kafka StatefulSet
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: kafka
spec:
  serviceName: kafka
  replicas: 3
  selector:
    matchLabels:
      app: kafka
  template:
    metadata:
      labels:
        app: kafka
    spec:
      containers:
      - name: kafka
        image: kafka:latest
        ports:
        - containerPort: 9092
        volumeMounts:
        - name: kafka-data
          mountPath: /var/lib/kafka
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
  volumeClaimTemplates:
  - metadata:
      name: kafka-data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: "fast-ssd"
      resources:
        requests:
          storage: 100Gi
---
# Flink JobManager Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flink-jobmanager
spec:
  replicas: 1
  selector:
    matchLabels:
      app: flink-jobmanager
  template:
    metadata:
      labels:
        app: flink-jobmanager
    spec:
      containers:
      - name: jobmanager
        image: flink:latest
        args: ["jobmanager"]
        ports:
        - containerPort: 6123
        - containerPort: 8081
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
---
# Flink TaskManager Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flink-taskmanager
spec:
  replicas: 5
  selector:
    matchLabels:
      app: flink-taskmanager
  template:
    metadata:
      labels:
        app: flink-taskmanager
    spec:
      containers:
      - name: taskmanager
        image: flink:latest
        args: ["taskmanager"]
        ports:
        - containerPort: 6122
        resources:
          requests:
            memory: "4Gi"
            cpu: "2000m"
          limits:
            memory: "8Gi"
            cpu: "4000m"
```

**Benefits**:
- StatefulSets for Kafka and Cassandra (stable network identities)
- Persistent volumes for data durability
- Independent scaling of Flink TaskManagers
- Resource limits prevent resource contention

---

### Scenario 4: CI/CD Pipeline with Kubernetes

**Problem**: Design a CI/CD system that deploys to Kubernetes.

**Kubernetes Solution**:

```
┌─────────────────────────────────────────────────────────┐
│              CI/CD Pipeline                              │
│                                                          │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │   Git     │───▶│ Jenkins  │───▶│  Build   │          │
│  │  Push     │    │ (K8s Job)│    │  Image   │          │
│  └──────────┘    └──────────┘    └────┬─────┘          │
│                                        │                 │
│                                        ▼                 │
│                                  ┌──────────┐           │
│                                  │ Container│           │
│                                  │ Registry │           │
│                                  │  (ECR)   │           │
│                                  └────┬─────┘           │
│                                       │                 │
│                                       ▼                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Kubernetes Cluster                        │  │
│  │                                                   │  │
│  │  ┌──────────┐                                    │  │
│  │  │ ArgoCD   │  (GitOps)                         │  │
│  │  │          │                                    │  │
│  │  │ Watches Git Repo                             │  │
│  │  │ Deploys to K8s                              │  │
│  │  └────┬─────┘                                    │  │
│  │       │                                          │  │
│  │       ▼                                          │  │
│  │  ┌──────────┐                                   │  │
│  │  │ Deployment│                                   │  │
│  │  │ (Rolling  │                                   │  │
│  │  │  Update)  │                                   │  │
│  │  └──────────┘                                   │  │
│  │                                                   │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

**Key Tools**:
- **Jenkins**: CI pipeline (runs as Kubernetes Jobs)
- **ArgoCD**: GitOps continuous delivery
- **Helm**: Package management
- **Kustomize**: Configuration management

**ArgoCD Configuration**:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
spec:
  project: default
  source:
    repoURL: https://github.com/org/repo
    targetRevision: main
    path: k8s/overlays/production
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
```

---

### Scenario 5: Multi-Tenant SaaS Platform

**Problem**: Design a multi-tenant SaaS platform with resource isolation.

**Kubernetes Solution**:

```
┌─────────────────────────────────────────────────────────┐
│              Kubernetes Cluster                         │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Tenant Isolation (Namespaces)            │  │
│  │                                                   │  │
│  │  ┌──────────────┐  ┌──────────────┐            │  │
│  │  │  Tenant A    │  │  Tenant B    │            │  │
│  │  │ (Namespace)  │  │ (Namespace)  │            │  │
│  │  │              │  │              │            │  │
│  │  │ ┌──────────┐ │  │ ┌──────────┐ │            │  │
│  │  │ │   App    │ │  │ │   App    │ │            │  │
│  │  │ │ (Deploy) │ │  │ │ (Deploy) │ │            │  │
│  │  │ └──────────┘ │  │ └──────────┘ │            │  │
│  │  │              │  │              │            │  │
│  │  │ ┌──────────┐ │  │ ┌──────────┐ │            │  │
│  │  │ │ Database  │ │  │ │ Database│ │            │  │
│  │  │ │(Stateful) │ │  │ │(Stateful)│ │            │  │
│  │  │ └──────────┘ │  │ └──────────┘ │            │  │
│  │  └──────────────┘  └──────────────┘            │  │
│  │                                                   │  │
│  │  ┌──────────────────────────────────────────┐  │  │
│  │  │      Resource Quotas                      │  │  │
│  │  │  - CPU: 4 cores per tenant               │  │  │
│  │  │  - Memory: 8Gi per tenant                │  │  │
│  │  │  - Pods: 20 per tenant                   │  │  │
│  │  └──────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

**Resource Quota Configuration**:

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: tenant-a-quota
  namespace: tenant-a
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    pods: "20"
    persistentvolumeclaims: "10"
    services: "5"
---
apiVersion: v1
kind: LimitRange
metadata:
  name: tenant-a-limits
  namespace: tenant-a
spec:
  limits:
  - default:
      memory: "512Mi"
      cpu: "500m"
    defaultRequest:
      memory: "256Mi"
      cpu: "250m"
    type: Container
```

**Benefits**:
- Resource isolation via namespaces
- Resource quotas prevent resource exhaustion
- Network policies for network isolation
- Cost allocation per tenant

---

## Kubernetes Components in System Design

### Deployments

**Use Cases**:
- Stateless applications
- Web servers
- API services
- Worker processes

**Key Features**:
- Rolling updates
- Rollback capability
- Replica management
- Health checks

**Example**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
spec:
  replicas: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 2
      maxUnavailable: 1
  selector:
    matchLabels:
      app: api-server
  template:
    metadata:
      labels:
        app: api-server
    spec:
      containers:
      - name: api-server
        image: api-server:v1.2.3
        ports:
        - containerPort: 8080
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### StatefulSets

**Use Cases**:
- Databases (MySQL, PostgreSQL, MongoDB)
- Message queues (Kafka, RabbitMQ)
- Stateful applications
- Applications requiring stable network identities

**Key Features**:
- Stable network identity (hostname)
- Ordered deployment/scaling
- Persistent storage per Pod
- Stable storage

**Example**:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  serviceName: mysql
  replicas: 3
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: password
        volumeMounts:
        - name: mysql-data
          mountPath: /var/lib/mysql
  volumeClaimTemplates:
  - metadata:
      name: mysql-data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: "fast-ssd"
      resources:
        requests:
          storage: 100Gi
```

### Services

**Types**:
- **ClusterIP**: Internal service (default)
- **NodePort**: Exposes service on node IP
- **LoadBalancer**: Cloud provider load balancer
- **ExternalName**: Maps to external DNS name

**Use Cases**:
- Service discovery
- Load balancing
- Abstracting Pod IPs
- Exposing services

**Example**:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: api-service
spec:
  selector:
    app: api-server
  ports:
  - port: 80
    targetPort: 8080
    protocol: TCP
  type: LoadBalancer
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800
```

### Ingress

**Use Cases**:
- HTTP/HTTPS routing
- SSL termination
- Path-based routing
- Host-based routing

**Example**:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.example.com
    secretName: api-tls
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 80
```

## Deployment Patterns

### Rolling Update (Default)

**Characteristics**:
- Gradual replacement of Pods
- Zero downtime
- Can be paused/resumed

**Use Cases**:
- Most applications
- When zero downtime is required

**Configuration**:

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 2          # Can create 2 extra pods
      maxUnavailable: 1    # Max 1 pod unavailable
```

### Blue-Green Deployment

**Implementation**: Two Deployments, switch Service selector

**Characteristics**:
- Instant switchover
- Easy rollback
- Requires 2x resources

**Use Cases**:
- Critical applications
- When instant rollback is needed

**Example**:

```yaml
# Blue Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-blue
spec:
  replicas: 5
  selector:
    matchLabels:
      app: myapp
      version: blue
  template:
    metadata:
      labels:
        app: myapp
        version: blue
    spec:
      containers:
      - name: app
        image: myapp:v1.0.0

---
# Green Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-green
spec:
  replicas: 5
  selector:
    matchLabels:
      app: myapp
      version: green
  template:
    metadata:
      labels:
        app: myapp
        version: green
    spec:
      containers:
      - name: app
        image: myapp:v2.0.0

---
# Service (switch selector to change)
apiVersion: v1
kind: Service
metadata:
  name: app-service
spec:
  selector:
    app: myapp
    version: blue  # Switch to 'green' for new version
  ports:
  - port: 80
    targetPort: 8080
```

### Canary Deployment

**Implementation**: Gradual traffic shift using Ingress or Service Mesh

**Characteristics**:
- Gradual rollout
- Risk mitigation
- A/B testing capability

**Use Cases**:
- New features
- Risk reduction
- A/B testing

**Example (Istio)**:

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: app-vs
spec:
  hosts:
  - app.example.com
  http:
  - match:
    - headers:
        canary:
          exact: "true"
    route:
    - destination:
        host: app
        subset: canary
      weight: 100
  - route:
    - destination:
        host: app
        subset: stable
      weight: 90
    - destination:
        host: app
        subset: canary
      weight: 10
```

## Scaling Strategies

### Horizontal Pod Autoscaler (HPA)

**Scales based on**:
- CPU utilization
- Memory utilization
- Custom metrics
- External metrics

**Example**:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app
  minReplicas: 3
  maxReplicas: 100
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "100"
```

### Vertical Pod Autoscaler (VPA)

**Scales**:
- Resource requests/limits
- Based on historical usage

**Use Cases**:
- Right-sizing Pods
- Optimizing resource usage

**Example**:

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: app-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: app
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 4
        memory: 8Gi
```

### Cluster Autoscaler

**Scales**:
- Number of nodes in cluster
- Based on Pod scheduling needs

**Use Cases**:
- Dynamic cluster sizing
- Cost optimization
- Handling traffic spikes

**Configuration** (cloud provider specific):

```yaml
# AWS EKS example
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-autoscaler-status
  namespace: kube-system
data:
  nodes.min: "3"
  nodes.max: "20"
  scale-down-delay: "10m"
  scale-down-unneeded-time: "10m"
```

## High Availability and Fault Tolerance

### Pod Disruption Budgets

**Purpose**: Ensure minimum availability during voluntary disruptions

**Example**:

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: app-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: myapp
```

### Multi-Zone Deployment

**Strategy**: Distribute Pods across availability zones

**Example**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  replicas: 6
  template:
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - myapp
              topologyKey: topology.kubernetes.io/zone
```

### Health Checks

**Liveness Probe**: Restarts container if unhealthy

**Readiness Probe**: Removes Pod from Service if not ready

**Example**:

```yaml
containers:
- name: app
  image: app:latest
  livenessProbe:
    httpGet:
      path: /health
      port: 8080
    initialDelaySeconds: 30
    periodSeconds: 10
    timeoutSeconds: 5
    failureThreshold: 3
  readinessProbe:
    httpGet:
      path: /ready
      port: 8080
    initialDelaySeconds: 5
    periodSeconds: 5
    timeoutSeconds: 3
    failureThreshold: 3
```

## Networking in Kubernetes

### Service Mesh (Istio)

**Features**:
- Traffic management
- Security (mTLS)
- Observability
- Circuit breaking

**Use Cases**:
- Microservices
- Complex routing
- Security requirements
- Observability needs

### Network Policies

**Purpose**: Control traffic between Pods

**Example**:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: app-network-policy
spec:
  podSelector:
    matchLabels:
      app: api-server
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: database
    ports:
    - protocol: TCP
      port: 5432
```

## Storage in Kubernetes

### Persistent Volumes

**Types**:
- **PV**: Cluster-wide storage
- **PVC**: User's request for storage
- **StorageClass**: Dynamic provisioning

**Example**:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: app-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: fast-ssd
  resources:
    requests:
      storage: 100Gi
```

### Volume Types

- **emptyDir**: Temporary storage
- **hostPath**: Node filesystem
- **nfs**: NFS mount
- **awsElasticBlockStore**: AWS EBS
- **gcePersistentDisk**: GCP Persistent Disk
- **azureDisk**: Azure Disk

## Monitoring and Observability

### Prometheus + Grafana

**Components**:
- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **Alertmanager**: Alerting

**Use Cases**:
- Metrics collection
- Dashboards
- Alerting

### ELK Stack

**Components**:
- **Elasticsearch**: Log storage
- **Logstash**: Log processing
- **Kibana**: Visualization

**Use Cases**:
- Log aggregation
- Log analysis
- Search

### Distributed Tracing

**Tools**:
- **Jaeger**: Distributed tracing
- **Zipkin**: Distributed tracing
- **OpenTelemetry**: Observability framework

**Use Cases**:
- Request tracing
- Performance analysis
- Debugging

## Security Considerations

### RBAC (Role-Based Access Control)

**Example**:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
subjects:
- kind: User
  name: developer
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

### Secrets Management

**Best Practices**:
- Use Kubernetes Secrets
- Encrypt at rest
- Use external secret managers (AWS Secrets Manager, HashiCorp Vault)
- Rotate secrets regularly

**Example**:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  username: YWRtaW4=  # base64 encoded
  password: cGFzc3dvcmQ=
```

### Pod Security Standards

**Levels**:
- **Privileged**: Unrestricted
- **Baseline**: Minimally restrictive
- **Restricted**: Highly restrictive

**Example**:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

## Trade-offs and Best Practices

### When to Use Kubernetes

**Use Kubernetes When**:
- Running microservices
- Need auto-scaling
- Multi-cloud or hybrid cloud
- Complex deployments
- Need service discovery
- Container orchestration needed

**Don't Use Kubernetes When**:
- Simple single-server application
- Small team without K8s expertise
- Cost-sensitive (can be expensive)
- Overkill for simple use cases

### Cost Considerations

**Cost Factors**:
- Cluster infrastructure (nodes)
- Load balancers
- Storage
- Network egress
- Management overhead

**Cost Optimization**:
- Right-size nodes
- Use spot instances
- Cluster autoscaling
- Resource quotas
- Pod resource limits

### Complexity Trade-offs

**Pros**:
- Powerful orchestration
- Rich ecosystem
- Industry standard
- Scalability

**Cons**:
- Steep learning curve
- Operational complexity
- Resource overhead
- Requires expertise

## Interview Tips

### How to Discuss Kubernetes in Interviews

1. **Mention K8s When Appropriate**:
   - Microservices architecture
   - Need for auto-scaling
   - Container orchestration
   - Multi-cloud deployment

2. **Explain Your Choices**:
   - Why Kubernetes vs. alternatives
   - Which components you'd use
   - How you'd configure scaling
   - Deployment strategy

3. **Show Understanding**:
   - Deployments vs. StatefulSets
   - Services and Ingress
   - HPA and scaling
   - Health checks

4. **Discuss Trade-offs**:
   - Complexity vs. benefits
   - Cost considerations
   - Operational overhead
   - Learning curve

### Common Interview Questions

**Q: How would you deploy a stateless web application?**
- Use Deployment
- Configure HPA for auto-scaling
- Use Service for load balancing
- Use Ingress for external access

**Q: How would you deploy a database?**
- Use StatefulSet for stable identity
- Persistent volumes for storage
- ConfigMaps/Secrets for configuration
- Consider replication and backups

**Q: How would you handle rolling updates?**
- Use Deployment with RollingUpdate strategy
- Configure maxSurge and maxUnavailable
- Health checks for zero downtime
- Consider canary deployments for risky changes

**Q: How would you scale the system?**
- HPA for Pod scaling
- Cluster Autoscaler for node scaling
- Consider VPA for right-sizing
- Multi-zone deployment for HA

## Summary

### Key Takeaways

1. **Kubernetes is Ideal For**:
   - Microservices architectures
   - Applications requiring auto-scaling
   - Multi-cloud deployments
   - Complex deployment scenarios

2. **Core Components**:
   - **Deployments**: Stateless applications
   - **StatefulSets**: Stateful applications
   - **Services**: Service discovery and load balancing
   - **Ingress**: External access and routing
   - **HPA**: Auto-scaling Pods
   - **ConfigMaps/Secrets**: Configuration management

3. **Common Patterns**:
   - Rolling updates for zero downtime
   - Blue-green for instant rollback
   - Canary for gradual rollout
   - Multi-zone for high availability

4. **Scaling Strategies**:
   - **HPA**: Scale Pods based on metrics
   - **VPA**: Right-size Pod resources
   - **Cluster Autoscaler**: Scale nodes

5. **Best Practices**:
   - Use health checks (liveness/readiness)
   - Set resource requests/limits
   - Use namespaces for isolation
   - Implement RBAC for security
   - Monitor and observe (Prometheus, Grafana)

### When to Mention Kubernetes in Interviews

- Designing microservices systems
- Need for container orchestration
- Auto-scaling requirements
- Multi-cloud or hybrid cloud
- Complex deployment needs
- Service discovery requirements

### When NOT to Mention Kubernetes

- Simple single-server application
- Small scale (< 10 servers)
- Team lacks K8s expertise
- Cost is primary concern
- Overkill for use case

Remember: Kubernetes is a powerful tool, but it's not always the right solution. Understand when to use it and be able to explain your reasoning in system design interviews.

