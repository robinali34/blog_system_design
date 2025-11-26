---
layout: post
title: "System Design: GitHub (Repos, Git Storage, PRs, CI)"
date: 2025-10-29 21:20:00 -0700
categories: system-design architecture devtools
permalink: /2025/10/29/system-design-github/
tags: [system-design, git, storage, code-review, ci, actions]
---

# System Design: GitHub (Repos, Git Storage, PRs, CI)

Scope: multi‑tenant git hosting, code browsing/search, pull requests, permissions, webhooks, CI runners.

## Git storage

- Sharded object storage for packfiles; replicas across AZs; maintenance (gc, repack) off the hot path.
- Smart HTTP/SSH; delta compression; quarantine on push; pre‑receive hooks for policy.

## Metadata and permissions

- Orgs/Teams/Repos/Branches/Tags; permissions matrix (admin/write/triage/read).
- Branch protection: required reviews, status checks; CODEOWNERS enforcement.

## Pull requests and code review

- PR model: base/head references; diff generation from git trees; comments stored in DB; draft reviews.
- Merge strategies: merge commit, squash, rebase; conflict detection; required checks gate merge.

## Search and code intel

- Indexer pipeline: parse repo events → fetch pack → index tokens/symbols to search backend (e.g., Zoekt/Elastic);
- Code navigation: LSIF uploads or on‑the‑fly language servers for hover/defs/refs.

## CI/CD (Actions)

- Workflow engine maps events (push/PR/schedule) to jobs; runners autoscale (K8s/VMs); sandboxing; cache/artifacts store.
- Secrets/vars with OIDC; concurrency groups and retry/backoff; matrix builds.

## Webhooks and integrations

- Event bus for repo/account events; delivery with retries/signatures; app marketplace.

## Reliability

- Read replicas for metadata; job isolation; abuse protection on runners; DDoS protection on git endpoints.

## APIs

```http
GET /repos/{owner}/{repo}
POST /repos/{owner}/{repo}/pulls
POST /repos/{owner}/{repo}/actions/workflows/{id}/dispatches
```

## Capacity & SLOs

- Repos: 100M; pushes peak 50k TPS; clones/reads peak 1M QPS; Actions jobs 500k/day.
- SLOs: Git fetch latency P95 < 200 ms (hot), PR load P95 < 300 ms, Actions start < 1 min P95.

## Consistency & integrity

- Git objects immutable; refs updates via transactional refs db; pre‑receive hooks enforce policies; background GC reconciles packs.

## Risks & mitigations

- Runner abuse/crypto‑mining → quotas, network egress limits, anomaly detection.
- Large monorepos → partial clones, sparse checkout, server‑side filtering.

## Detailed APIs

```http
POST /repos/{o}/{r}/pulls { base, head, title, body } -> { number }
GET  /repos/{o}/{r}/git/trees/{sha}?recursive=1
POST /repos/{o}/{r}/actions/workflows/{id}/dispatches { ref, inputs }
```

## Data model details

- Refs db: transactional table for branches/tags with CAS semantics; audit trail for force‑push.
- PR store: base/head SHAs, review comments, checks status, mergeability cache.

## Failure drills

- Packfile corruption → quarantine repo, rebuild from replicas; notify owners.
- Actions runner shortage → queue backoff, burst to cloud pool, reduce concurrency groups.

## What Interviewers Look For

### Git/Version Control Skills

1. **Git Storage Architecture**
   - Packfile storage
   - Object deduplication
   - Delta compression
   - **Red Flags**: Inefficient storage, no deduplication, poor compression

2. **Git Operations**
   - Smart HTTP/SSH
   - Partial clones
   - Sparse checkout
   - **Red Flags**: Inefficient operations, no optimization, poor performance

3. **Repository Management**
   - Sharding strategy
   - Replication
   - GC/maintenance
   - **Red Flags**: No sharding, single point of failure, no maintenance

### Developer Tools Skills

1. **Code Search & Navigation**
   - Indexing pipeline
   - Symbol extraction
   - LSIF support
   - **Red Flags**: No search, slow indexing, poor navigation

2. **Pull Request System**
   - Diff generation
   - Merge strategies
   - Conflict detection
   - **Red Flags**: Slow diffs, no merge strategies, poor conflict handling

3. **CI/CD Pipeline**
   - Workflow engine
   - Runner management
   - Job isolation
   - **Red Flags**: No CI/CD, poor isolation, security issues

### Problem-Solving Approach

1. **Scale Challenges**
   - Large monorepos
   - High push rates
   - Many concurrent clones
   - **Red Flags**: No scale consideration, bottlenecks, poor performance

2. **Edge Cases**
   - Packfile corruption
   - Runner abuse
   - DDoS attacks
   - **Red Flags**: Ignoring edge cases, no handling

3. **Trade-off Analysis**
   - Consistency vs availability
   - Performance vs cost
   - **Red Flags**: No trade-offs, dogmatic choices

### System Design Skills

1. **Component Design**
   - Git storage service
   - Metadata service
   - CI/CD service
   - **Red Flags**: Monolithic, unclear boundaries

2. **Security Design**
   - Permissions matrix
   - Branch protection
   - Runner sandboxing
   - **Red Flags**: No security, insecure, vulnerabilities

3. **Reliability Design**
   - Read replicas
   - Job isolation
   - Abuse protection
   - **Red Flags**: No redundancy, poor isolation, no protection

### Communication Skills

1. **Git Architecture Explanation**
   - Can explain packfile storage
   - Understands git internals
   - **Red Flags**: No understanding, vague explanations

2. **Scale Explanation**
   - Can explain scaling strategies
   - Understands bottlenecks
   - **Red Flags**: No understanding, vague

### Meta-Specific Focus

1. **Developer Tools Expertise**
   - Deep git knowledge
   - CI/CD understanding
   - **Key**: Show developer tools expertise

2. **Scale & Performance**
   - Large-scale git hosting
   - Performance optimization
   - **Key**: Demonstrate scale expertise
