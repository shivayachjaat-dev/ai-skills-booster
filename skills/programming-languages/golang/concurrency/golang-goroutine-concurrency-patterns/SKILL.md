---
name: golang-goroutine-concurrency-patterns
description: "Use this skill when designing, implementing, and debugging concurrent systems in Go. It guides the agent through worker pool patterns, context cancellation propagation (context.Context), channel synchronization (buffered vs unbuffered), race condition prevention using the Go race detector (-race), errgroup error aggregation, and graceful shutdown."
domain: programming-languages
category: golang
subcategory: concurrency
tags:
  - golang
  - concurrency
  - goroutines
  - channels
  - go
  - multithreading
technologies:
  - Go
  - Golang
  - sync
  - errgroup
  - context
complexity: advanced
maturity: stable
tools:
  - go
dependencies:
  - go >= 1.21
---
# Golang Goroutine Concurrency Patterns

## Overview

A guide for architecting high-throughput, leak-free concurrent systems in Go. Grounded in the Go concurrency philosophy *"Do not communicate by sharing memory; instead, share memory by communicating"*, this skill instructs AI agents on building bounded worker pools, propagating cancellation across goroutine trees, preventing goroutine leaks, and detecting data races.

## When to Use

- Implementing parallel data processing pipelines, web scrapers, or batch ingestion workers in Go.
- Eliminating unbounded goroutine creation that leads to out-of-memory crashes.
- Propagating context cancellation, timeouts, and deadlines across nested background tasks.
- Diagnosing data races flagged by `go test -race` or `go run -race`.

## When NOT to Use

- Simple sequential operations where single-threaded execution is fast enough (< 10ms).
- Python or Node.js asynchronous programming (use `fastapi-async-api-design`).

## Inputs & Prerequisites

- Go 1.21+ toolchain installed.
- Understanding of Go channels (`chan`), sync primitives (`sync.WaitGroup`, `sync.Mutex`), and `context.Context`.

## Core Workflow

### 1. Bounded Worker Pool Pattern
Never spawn an unbounded goroutine per incoming item (`for _, item := range items { go process(item) }`). This exhausts memory and file descriptors. Implement a bounded worker pool:
```go
package main

import (
	"context"
	"fmt"
	"sync"
)

func WorkerPool(ctx context.Context, numWorkers int, jobs <-chan int, results chan<- int) {
	var wg sync.WaitGroup

	for i := 0; i < numWorkers; i++ {
		wg.Add(1)
		go func(workerID int) {
			defer wg.Done()
			for {
				select {
				case <-ctx.Done():
					return // Clean exit on cancellation
				case job, ok := <-jobs:
					if !ok {
						return // Channel closed, work complete
					}
					// Process work safely
					results <- job * 2
				}
			}
		}(i)
	}

	wg.Wait()
	close(results)
}
```

### 2. Error Aggregation with `errgroup`
When running parallel subtasks where ANY failure should cancel all sibling tasks and return the first error:
```go
import (
	"context"
	"golang.org/x/sync/errgroup"
)

func FetchAllData(ctx context.Context, userIDs []string) error {
	g, ctx := errgroup.WithContext(ctx)

	for _, id := range userIDs {
		userID := id // Pin loop variable (pre-Go 1.22)
		g.Go(func() error {
			return fetchUserProfile(ctx, userID)
		})
	}

	// Waits for all goroutines to complete; returns first non-nil error
	return g.Wait()
}
```

### 3. Preventing Goroutine Leaks
A goroutine leak occurs when a goroutine is blocked forever trying to write to an unbuffered channel or waiting on a lock that never releases:
- **Rule**: If a goroutine sends on a channel, ensure a receiver is guaranteed to read it, or use a buffered channel with adequate capacity.
- **Rule**: Always pass `ctx context.Context` as the first argument, and listen on `<-ctx.Done()` in every blocking select loop.

### 4. Detecting Races with the Race Detector
Always run tests and local benchmarks with the `-race` flag enabled:
```bash
go test -race ./...
go build -race -o service .
```
Fix any reported data races using `sync/atomic` primitives or `sync.RWMutex`.

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Read-heavy, write-infrequent shared state | Use `sync.RWMutex` (`RLock()` for parallel reads, `Lock()` for exclusive writes). |
| Single-value atomic state update (e.g. counter, flag) | Use `sync/atomic` (`atomic.AddInt64`, `atomic.Bool`) instead of a heavy Mutex. |
| Fan-in from multiple producer channels | Use a single `select` block or merge channels using reflection/worker loops with `sync.WaitGroup`. |

## Validation & Acceptance Criteria

- [ ] All goroutine creation is bounded (zero unbounded `go func()` in loops).
- [ ] Goroutines exit cleanly when `context.Context` is cancelled.
- [ ] `go test -race ./...` executes with zero race condition detections.
- [ ] Error aggregation implemented via `errgroup.WithContext`.
- [ ] Channels closed strictly by the producer/sender, never by the receiver.

## Failure Handling & Recovery

- If a worker panics, recover gracefully inside the worker goroutine using `defer func() { if r := recover(); r != nil { ... } }()` to prevent crashing the entire process.

## Expected Output & Artifacts

- Bounded worker pool implementation.
- Concurrency test suite executing under `-race`.
- Context cancellation benchmarks.

## Related Skills

- `rust-memory-safety-and-lifetimes`
- `grpc-service-implementation`
- `api-rate-limiting-and-throttling`
