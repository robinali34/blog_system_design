---
layout: post
title: "CDN (Content Delivery Network): Comprehensive Guide to Global Content Distribution"
date: 2025-12-29
categories: [CDN, Content Delivery, Distributed Systems, System Design, Technology, Performance, Cloud]
excerpt: "A comprehensive guide to Content Delivery Networks (CDN), covering architecture, caching strategies, edge computing, performance optimization, and best practices for delivering content globally with low latency and high availability."
---

## Introduction

A Content Delivery Network (CDN) is a distributed network of servers that delivers web content to users based on their geographic location. CDNs improve performance, reduce latency, and increase availability by caching content at edge locations closer to end users.

This guide covers:
- **CDN Fundamentals**: Core concepts, architecture, and how CDNs work
- **Caching Strategies**: Cache control, invalidation, and optimization
- **Edge Computing**: Processing at the edge for lower latency
- **Use Cases**: Static assets, dynamic content, media streaming
- **Best Practices**: Performance, security, and cost optimization

## What is a CDN?

A Content Delivery Network (CDN) is a geographically distributed network of servers that:
- **Caches Content**: Stores copies of content at edge locations
- **Reduces Latency**: Serves content from locations closer to users
- **Improves Performance**: Faster content delivery and page load times
- **Increases Availability**: Redundancy and failover capabilities
- **Reduces Origin Load**: Offloads traffic from origin servers

### Key Concepts

**Origin Server**: The original server that hosts the content

**Edge Server**: CDN server located close to end users

**Cache Hit**: Content served from CDN cache (fast)

**Cache Miss**: Content fetched from origin server (slower)

**TTL (Time To Live)**: How long content is cached

**Cache Invalidation**: Removing content from cache before TTL expires

**Edge Location**: Geographic location of CDN servers (PoP - Point of Presence)

**Origin Shield**: Additional caching layer between edge and origin

## Core Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    End Users                              │
│  (US, Europe, Asia, etc.)                                │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTP/HTTPS Requests
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼────────┐      ┌─────────▼──────────┐
│  Edge Server   │      │   Edge Server      │
│  (US East)     │      │   (Europe)         │
│                │      │                    │
│  ┌──────────┐  │      │  ┌──────────┐     │
│  │  Cache   │  │      │  │  Cache   │     │
│  └──────────┘  │      │  └──────────┘     │
└───────┬────────┘      └─────────┬──────────┘
        │                         │
        │ Cache Miss              │ Cache Miss
        │                         │
        └────────────┬────────────┘
                     │
                     │ Origin Requests
                     │
        ┌────────────▼────────────┐
        │    Origin Shield         │
        │    (Regional Cache)      │
        └────────────┬─────────────┘
                     │
                     │ Cache Miss
                     │
        ┌────────────▼────────────┐
        │    Origin Server         │
        │    (Application Server)  │
        └─────────────────────────┘
```

## How CDNs Work

### 1. Content Request Flow

**Step 1: User Request**
- User requests content (e.g., `https://example.com/image.jpg`)
- DNS resolves to nearest edge server

**Step 2: Edge Server Check**
- Edge server checks cache
- **Cache Hit**: Serves from cache (fast)
- **Cache Miss**: Fetches from origin

**Step 3: Origin Fetch (if cache miss)**
- Edge server requests from origin
- Origin server responds with content
- Edge server caches content
- Edge server serves to user

**Step 4: Subsequent Requests**
- Same content served from cache
- Much faster response time

### 2. DNS-Based Routing

CDNs use DNS to route users to nearest edge server:

```
User Request → DNS Query → CDN DNS Server
                              ↓
                    Geographic Routing
                              ↓
                    Nearest Edge Server
                              ↓
                    IP Address Returned
                              ↓
                    User Connects to Edge
```

**Geographic Routing Methods:**
- **GeoIP**: Based on user's IP location
- **Anycast**: Same IP address, routes to nearest server
- **DNS-based**: DNS server returns nearest edge IP

### 3. Caching Strategy

**Cacheable Content:**
- Static assets (images, CSS, JS)
- Media files (videos, audio)
- API responses (with appropriate headers)
- HTML pages (with cache control)

**Cache Headers:**
```
Cache-Control: public, max-age=3600
ETag: "abc123"
Last-Modified: Wed, 21 Oct 2024 07:28:00 GMT
```

**Cache Control Directives:**
- `public`: Can be cached by any cache
- `private`: Only browser can cache
- `no-cache`: Must revalidate before serving
- `max-age`: Time in seconds content is fresh
- `s-maxage`: Max age for shared caches (CDN)

## CDN Features

### 1. Static Content Delivery

**Use Cases:**
- Images, CSS, JavaScript files
- Fonts, icons, logos
- Static HTML pages

**Benefits:**
- Fast delivery from edge
- Reduced origin load
- Global distribution

**Example:**
```
Origin: https://example.com/static/image.jpg
CDN: https://cdn.example.com/image.jpg
```

### 2. Dynamic Content Acceleration

**Use Cases:**
- API responses
- Personalized content
- Real-time data

**Techniques:**
- **Edge Caching**: Cache dynamic content with short TTL
- **ESI (Edge Side Includes)**: Combine cached and dynamic content
- **Query String Handling**: Cache based on query parameters

**Example:**
```
GET /api/user/123?cache=true
Cache-Control: public, max-age=60
```

### 3. Media Streaming

**Use Cases:**
- Video on demand (VOD)
- Live streaming
- Audio streaming

**Features:**
- **Adaptive Bitrate**: Adjust quality based on bandwidth
- **Chunked Delivery**: Stream in segments
- **Multi-Format Support**: HLS, DASH, etc.

**Example:**
```
Video: https://cdn.example.com/video/playlist.m3u8
Segments: segment1.ts, segment2.ts, ...
```

### 4. Security Features

**DDoS Protection:**
- Absorbs attack traffic at edge
- Protects origin servers
- Rate limiting and filtering

**SSL/TLS Termination:**
- HTTPS at edge
- Certificate management
- TLS version control

**WAF (Web Application Firewall):**
- SQL injection protection
- XSS protection
- Bot detection

**Access Control:**
- Signed URLs
- Token authentication
- Geographic restrictions

### 5. Edge Computing

**Use Cases:**
- Serverless functions at edge
- Request/response modification
- A/B testing
- Personalization

**Benefits:**
- Lower latency
- Reduced origin load
- Global processing

**Example:**
```
Edge Function:
- Modify headers
- Add authentication
- Transform responses
- Route requests
```

## CDN Providers

### Major CDN Providers

**Cloudflare:**
- Global network (200+ cities)
- Free tier available
- DDoS protection
- Edge computing (Workers)

**Amazon CloudFront:**
- AWS integration
- Global edge locations
- Lambda@Edge
- Real-time metrics

**Fastly:**
- Real-time purging
- Edge computing (VCL)
- High performance
- Developer-friendly

**Akamai:**
- Largest network
- Enterprise focus
- Advanced security
- Media delivery

**Google Cloud CDN:**
- GCP integration
- Global network
- Load balancing integration
- Cost-effective

## Cache Invalidation

### Methods

**1. TTL-Based Expiration**
```
Cache-Control: max-age=3600
```
- Content expires after TTL
- Automatic refresh
- Simple to implement

**2. Manual Purging**
```
PURGE /path/to/content
```
- Immediate invalidation
- API-based
- Granular control

**3. Versioning**
```
/image.jpg?v=123
/style.css?v=456
```
- URL-based versioning
- No invalidation needed
- Cache busting

**4. Tag-Based Invalidation**
```
Cache-Tag: product-123, category-456
```
- Invalidate by tags
- Bulk operations
- Efficient

### Best Practices

**Cache Invalidation Strategy:**
- Use versioning for static assets
- Use TTL for dynamic content
- Use purging for urgent updates
- Monitor cache hit ratio

**Example:**
```javascript
// Version static assets
const version = process.env.BUILD_VERSION;
const imageUrl = `https://cdn.example.com/image.jpg?v=${version}`;

// Set appropriate TTL
app.get('/api/data', (req, res) => {
  res.set('Cache-Control', 'public, max-age=300');
  res.json(data);
});
```

## Performance Optimization

### 1. Cache Hit Ratio

**Target: 90%+ cache hit ratio**

**Optimization:**
- Increase TTL for static content
- Cache more content types
- Use origin shield
- Monitor and adjust

**Metrics:**
```
Cache Hit Ratio = (Cache Hits / Total Requests) × 100
```

### 2. Compression

**Enable compression:**
- Gzip/Brotli compression
- Reduce bandwidth
- Faster delivery
- Lower costs

**Example:**
```
Accept-Encoding: gzip, br
Content-Encoding: gzip
```

### 3. HTTP/2 and HTTP/3

**Benefits:**
- Multiplexing
- Header compression
- Server push
- Lower latency

### 4. Image Optimization

**Techniques:**
- WebP format
- Lazy loading
- Responsive images
- Compression

**Example:**
```html
<picture>
  <source srcset="image.webp" type="image/webp">
  <img src="image.jpg" alt="Image">
</picture>
```

## Use Cases

### 1. Static Website Hosting

**Benefits:**
- Fast global delivery
- High availability
- Cost-effective
- Easy to scale

**Example:**
```
Static Site → CDN → Global Users
```

### 2. E-Commerce

**Use Cases:**
- Product images
- CSS/JavaScript
- Fonts and icons
- Static pages

**Benefits:**
- Faster page loads
- Better user experience
- Higher conversion rates

### 3. Media Delivery

**Use Cases:**
- Video streaming
- Image galleries
- Audio files
- Downloads

**Benefits:**
- Smooth streaming
- Reduced buffering
- Global reach

### 4. API Acceleration

**Use Cases:**
- API responses
- GraphQL queries
- REST endpoints

**Techniques:**
- Edge caching
- Query string handling
- Header-based caching

### 5. Mobile Applications

**Use Cases:**
- App assets
- Media content
- API responses

**Benefits:**
- Lower latency
- Reduced data usage
- Better performance

## Best Practices

### 1. Cache Strategy

**Static Content:**
```
Cache-Control: public, max-age=31536000, immutable
```

**Dynamic Content:**
```
Cache-Control: public, max-age=300, must-revalidate
```

**Private Content:**
```
Cache-Control: private, no-cache
```

### 2. Security

**HTTPS:**
- Always use HTTPS
- HSTS headers
- Certificate management

**Access Control:**
- Signed URLs for private content
- Token authentication
- Geographic restrictions

**WAF:**
- Enable WAF rules
- Monitor threats
- Update rules regularly

### 3. Monitoring

**Key Metrics:**
- Cache hit ratio
- Response time
- Bandwidth usage
- Error rates
- Origin load

**Tools:**
- CDN analytics
- Real-time monitoring
- Alerts and notifications

### 4. Cost Optimization

**Strategies:**
- Optimize cache hit ratio
- Use compression
- Choose right pricing tier
- Monitor usage
- Use origin shield

### 5. Content Optimization

**Techniques:**
- Minify CSS/JS
- Optimize images
- Use modern formats (WebP, AVIF)
- Enable compression
- Lazy load content

## Code Examples

### 1. CDN Configuration (Nginx)

```nginx
# Origin server configuration
server {
    listen 80;
    server_name example.com;
    
    location /static/ {
        # Set cache headers
        add_header Cache-Control "public, max-age=31536000, immutable";
        add_header Vary "Accept-Encoding";
        
        # Enable compression
        gzip on;
        gzip_types text/css application/javascript image/svg+xml;
        
        # Serve from CDN
        proxy_pass http://cdn.example.com;
    }
}
```

### 2. Cache Invalidation (API)

```javascript
// Invalidate CDN cache
async function invalidateCDN(paths) {
  const response = await fetch('https://api.cdn.example.com/purge', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ paths })
  });
  
  return response.json();
}

// Usage
await invalidateCDN([
  '/static/image.jpg',
  '/api/products/123'
]);
```

### 3. Signed URLs

```javascript
// Generate signed URL for private content
const crypto = require('crypto');

function generateSignedURL(path, expiresIn = 3600) {
  const expires = Math.floor(Date.now() / 1000) + expiresIn;
  const secret = process.env.CDN_SECRET;
  const stringToSign = `${path}${expires}`;
  const signature = crypto
    .createHmac('sha256', secret)
    .update(stringToSign)
    .digest('hex');
  
  return `https://cdn.example.com${path}?expires=${expires}&signature=${signature}`;
}

// Usage
const url = generateSignedURL('/private/video.mp4', 3600);
```

### 4. Cache Control Headers

```javascript
// Express.js cache headers
app.get('/static/*', (req, res, next) => {
  // Static assets - long cache
  res.set('Cache-Control', 'public, max-age=31536000, immutable');
  res.set('ETag', generateETag(req.path));
  next();
});

app.get('/api/*', (req, res, next) => {
  // API responses - short cache
  res.set('Cache-Control', 'public, max-age=300, must-revalidate');
  res.set('Vary', 'Accept-Encoding');
  next();
});

app.get('/private/*', (req, res, next) => {
  // Private content - no cache
  res.set('Cache-Control', 'private, no-cache, must-revalidate');
  next();
});
```

## What Interviewers Look For

### CDN Understanding

1. **CDN Fundamentals**
   - Understanding of how CDNs work
   - Cache hit/miss concepts
   - Geographic distribution
   - **Red Flags**: No CDN understanding, wrong concepts, no geographic awareness

2. **Caching Strategy**
   - Cache control headers
   - TTL management
   - Cache invalidation
   - **Red Flags**: No caching strategy, wrong headers, no invalidation

3. **Performance Optimization**
   - Cache hit ratio optimization
   - Compression
   - Content optimization
   - **Red Flags**: No optimization, poor hit ratio, no compression

### Problem-Solving Approach

1. **Use Case Identification**
   - When to use CDN
   - What content to cache
   - Cache strategy selection
   - **Red Flags**: Wrong use cases, caching everything, no strategy

2. **Performance Analysis**
   - Cache hit ratio analysis
   - Latency reduction
   - Bandwidth optimization
   - **Red Flags**: No metrics, no analysis, poor optimization

### System Design Skills

1. **Architecture Design**
   - CDN integration
   - Origin server design
   - Failover strategies
   - **Red Flags**: No CDN, poor integration, no failover

2. **Cost Optimization**
   - Bandwidth optimization
   - Cache hit ratio
   - Pricing understanding
   - **Red Flags**: No cost awareness, poor optimization, high costs

### Communication Skills

1. **Clear Explanation**
   - Explains CDN concepts
   - Discusses trade-offs
   - Justifies design decisions
   - **Red Flags**: Unclear explanations, no justification, confusing

### Meta-Specific Focus

1. **Performance Expertise**
   - Understanding of performance optimization
   - CDN mastery
   - Real-world application
   - **Key**: Demonstrate performance optimization expertise

2. **Global Systems**
   - Understanding of global distribution
   - Latency optimization
   - Geographic awareness
   - **Key**: Show global system design skills

## Summary

**CDN Key Points:**
- **Global Distribution**: Content served from edge locations
- **Caching**: Reduces latency and origin load
- **Performance**: Faster content delivery and page loads
- **Scalability**: Handles high traffic globally
- **Security**: DDoS protection, WAF, SSL/TLS

**Common Use Cases:**
- Static asset delivery (images, CSS, JS)
- Media streaming (video, audio)
- API acceleration
- Global content distribution
- Mobile app content

**Best Practices:**
- Optimize cache hit ratio (90%+)
- Use appropriate cache headers
- Enable compression
- Monitor performance metrics
- Implement cache invalidation strategy
- Use HTTPS and security features
- Optimize content (images, code)

CDNs are essential for building high-performance, globally distributed applications with low latency and high availability.

