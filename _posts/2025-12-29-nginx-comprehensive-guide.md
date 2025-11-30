---
layout: post
title: "NGINX: Comprehensive Guide to Web Server and Reverse Proxy"
date: 2025-12-29
categories: [NGINX, Web Server, Reverse Proxy, Load Balancer, System Design, Technology]
excerpt: "A comprehensive guide to NGINX, covering web server, reverse proxy, load balancing, SSL termination, and best practices for building high-performance web applications and APIs."
---

## Introduction

NGINX (pronounced "engine-x") is a high-performance web server, reverse proxy, and load balancer. It's widely used for serving static content, proxying requests to application servers, and load balancing. Understanding NGINX is essential for system design interviews and building scalable web applications.

This guide covers:
- **NGINX Fundamentals**: Web server, reverse proxy, and load balancing
- **Configuration**: Server blocks, location blocks, and directives
- **Load Balancing**: Algorithms, health checks, and session persistence
- **SSL/TLS**: Certificate management and HTTPS configuration
- **Performance**: Caching, compression, and optimization

## What is NGINX?

NGINX is a web server and reverse proxy that:
- **Serves Static Content**: Fast static file serving
- **Reverse Proxy**: Routes requests to backend servers
- **Load Balancing**: Distributes traffic across servers
- **SSL Termination**: Handles HTTPS connections
- **High Performance**: Event-driven, non-blocking architecture

### Key Concepts

**Server Block**: Virtual host configuration

**Location Block**: URL path matching and processing

**Upstream**: Backend server group

**Directive**: Configuration instruction

**Worker Process**: Process that handles requests

## Core Architecture

```
┌─────────────────────────────────────────────────────────┐
│              NGINX Master Process                      │
│                                                          │
│  ┌──────────────────────────────────────────────────┐ │
│  │         Worker Process 1                           │ │
│  │  (Event-driven, Non-blocking)                      │ │
│  └──────────────────────────────────────────────────┘ │
│                                                          │
│  ┌──────────────────────────────────────────────────┐ │
│  │         Worker Process 2                         │ │
│  │  (Event-driven, Non-blocking)                     │ │
│  └──────────────────────────────────────────────────┘ │
│                                                          │
│  ┌──────────────────────────────────────────────────┐ │
│  │         Worker Process N                         │ │
│  │  (Event-driven, Non-blocking)                     │ │
│  └──────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

## Web Server Configuration

### Basic Server Block

```nginx
server {
    listen 80;
    server_name example.com;
    
    root /var/www/html;
    index index.html;
    
    location / {
        try_files $uri $uri/ =404;
    }
}
```

### Static File Serving

```nginx
server {
    listen 80;
    server_name example.com;
    
    root /var/www/html;
    
    location /static/ {
        alias /var/www/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## Reverse Proxy

### Basic Reverse Proxy

```nginx
server {
    listen 80;
    server_name api.example.com;
    
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

upstream backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
}
```

### Advanced Proxy Configuration

```nginx
location /api/ {
    proxy_pass http://backend;
    
    # Headers
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # Timeouts
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
    
    # Buffering
    proxy_buffering on;
    proxy_buffer_size 4k;
    proxy_buffers 8 4k;
    
    # Error handling
    proxy_next_upstream error timeout invalid_header http_500 http_502 http_503;
}
```

## Load Balancing

### Upstream Configuration

```nginx
upstream backend {
    # Round robin (default)
    server 192.168.1.10:8000;
    server 192.168.1.11:8000;
    server 192.168.1.12:8000;
}
```

### Load Balancing Methods

**1. Round Robin (Default):**
```nginx
upstream backend {
    server 192.168.1.10:8000;
    server 192.168.1.11:8000;
}
```

**2. Least Connections:**
```nginx
upstream backend {
    least_conn;
    server 192.168.1.10:8000;
    server 192.168.1.11:8000;
}
```

**3. IP Hash:**
```nginx
upstream backend {
    ip_hash;
    server 192.168.1.10:8000;
    server 192.168.1.11:8000;
}
```

**4. Weighted:**
```nginx
upstream backend {
    server 192.168.1.10:8000 weight=3;
    server 192.168.1.11:8000 weight=2;
    server 192.168.1.12:8000 weight=1;
}
```

### Health Checks

```nginx
upstream backend {
    server 192.168.1.10:8000 max_fails=3 fail_timeout=30s;
    server 192.168.1.11:8000 max_fails=3 fail_timeout=30s;
    server 192.168.1.12:8000 backup;
}
```

## SSL/TLS Configuration

### Basic HTTPS

```nginx
server {
    listen 443 ssl;
    server_name example.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://backend;
    }
}
```

### Advanced SSL Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;
    
    # Certificates
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_trusted_certificate /path/to/chain.pem;
    
    # SSL Protocols
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # SSL Session
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
}
```

### HTTP to HTTPS Redirect

```nginx
server {
    listen 80;
    server_name example.com;
    return 301 https://$server_name$request_uri;
}
```

## Caching

### Proxy Caching

```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=1g inactive=60m;

server {
    location / {
        proxy_pass http://backend;
        proxy_cache my_cache;
        proxy_cache_valid 200 60m;
        proxy_cache_valid 404 1m;
        proxy_cache_use_stale error timeout updating;
        add_header X-Cache-Status $upstream_cache_status;
    }
}
```

### Cache Control

```nginx
location /api/ {
    proxy_pass http://backend;
    proxy_cache my_cache;
    proxy_cache_key "$scheme$request_method$host$request_uri";
    proxy_cache_bypass $http_pragma $http_authorization;
    proxy_no_cache $http_pragma $http_authorization;
}
```

## Compression

### Gzip Compression

```nginx
gzip on;
gzip_vary on;
gzip_min_length 1000;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

server {
    location / {
        gzip_static on;
        proxy_pass http://backend;
    }
}
```

## Rate Limiting

### Basic Rate Limiting

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

server {
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        proxy_pass http://backend;
    }
}
```

### Connection Limiting

```nginx
limit_conn_zone $binary_remote_addr zone=conn_limit:10m;

server {
    location / {
        limit_conn conn_limit 10;
        proxy_pass http://backend;
    }
}
```

## Security

### Security Headers

```nginx
server {
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}
```

### Access Control

```nginx
location /admin/ {
    allow 192.168.1.0/24;
    deny all;
    proxy_pass http://backend;
}
```

## Performance Optimization

### Worker Configuration

```nginx
worker_processes auto;
worker_connections 1024;
worker_rlimit_nofile 2048;

events {
    use epoll;
    multi_accept on;
}
```

### Keep-Alive Connections

```nginx
http {
    keepalive_timeout 65;
    keepalive_requests 100;
    
    upstream backend {
        keepalive 32;
        server 192.168.1.10:8000;
    }
}
```

### File Caching

```nginx
open_file_cache max=1000 inactive=20s;
open_file_cache_valid 30s;
open_file_cache_min_uses 2;
open_file_cache_errors on;
```

## Best Practices

### 1. Configuration Organization

- Separate server blocks
- Use include directives
- Comment configurations
- Version control configs

### 2. Security

- Enable SSL/TLS
- Use security headers
- Implement rate limiting
- Restrict access

### 3. Performance

- Enable compression
- Use caching
- Optimize worker processes
- Monitor performance

### 4. Monitoring

- Log access and errors
- Monitor upstream health
- Track performance metrics
- Set up alerts

## What Interviewers Look For

### Web Server Understanding

1. **NGINX Concepts**
   - Understanding of web server, reverse proxy, load balancing
   - Configuration management
   - Performance optimization
   - **Red Flags**: No NGINX understanding, wrong configuration, no optimization

2. **Load Balancing**
   - Algorithm selection
   - Health checks
   - Session persistence
   - **Red Flags**: Wrong algorithm, no health checks, poor persistence

3. **SSL/TLS**
   - Certificate management
   - HTTPS configuration
   - Security best practices
   - **Red Flags**: No SSL, poor configuration, security issues

### Problem-Solving Approach

1. **Configuration Design**
   - Server block design
   - Location block matching
   - Upstream configuration
   - **Red Flags**: Poor configuration, wrong patterns, no design

2. **Performance Optimization**
   - Caching strategies
   - Compression
   - Worker optimization
   - **Red Flags**: No optimization, poor performance, no caching

### System Design Skills

1. **Architecture Design**
   - Reverse proxy setup
   - Load balancing design
   - High availability
   - **Red Flags**: No proxy, single server, no HA

2. **Security**
   - SSL/TLS configuration
   - Security headers
   - Access control
   - **Red Flags**: No security, poor configuration, vulnerabilities

### Communication Skills

1. **Clear Explanation**
   - Explains NGINX concepts
   - Discusses trade-offs
   - Justifies design decisions
   - **Red Flags**: Unclear explanations, no justification, confusing

### Meta-Specific Focus

1. **Web Infrastructure Expertise**
   - Understanding of web servers
   - NGINX mastery
   - Performance optimization
   - **Key**: Demonstrate web infrastructure expertise

2. **System Design Skills**
   - Can design web architecture
   - Understands load balancing
   - Makes informed trade-offs
   - **Key**: Show practical web design skills

## Summary

**NGINX Key Points:**
- **Web Server**: Fast static file serving
- **Reverse Proxy**: Routes requests to backend servers
- **Load Balancing**: Distributes traffic across servers
- **SSL/TLS**: HTTPS handling and certificate management
- **High Performance**: Event-driven, non-blocking architecture
- **Caching**: Proxy caching and static file caching

**Common Use Cases:**
- Web server for static content
- Reverse proxy for APIs
- Load balancer for microservices
- SSL termination
- Rate limiting and security
- Content delivery

**Best Practices:**
- Organize configuration files
- Enable SSL/TLS
- Implement caching
- Use compression
- Configure rate limiting
- Monitor performance
- Implement security headers

NGINX is a powerful web server and reverse proxy that's essential for building high-performance, scalable web applications.

