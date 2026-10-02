---
name: rust-memory-safety-and-lifetimes
description: "Use this skill when designing, writing, and refactoring Rust code to navigate the borrow checker, manage explicit lifetimes ('a), prevent allocations through zero-copy borrowing, handle interior mutability (RefCell/Mutex), and structure safe concurrency without data races."
domain: programming-languages
category: rust
subcategory: memory-safety
tags:
  - rust
  - memory-safety
  - borrow-checker
  - lifetimes
  - systems-programming
  - zero-copy
technologies:
  - Rust
  - Cargo
  - Tokio
  - Clippy
complexity: expert
maturity: stable
tools:
  - cargo
  - rustc
dependencies:
  - rust >= 1.75
---
# Rust Memory Safety and Lifetimes

## Overview

A guide for mastering Rust's ownership, borrowing, and lifetime systems. Instructs AI agents on satisfying the borrow checker without excessive `.clone()` allocations, structuring explicit lifetime annotations (`'a`), implementing safe interior mutability (`Arc<Mutex<T>>`), designing zero-copy parsers, and writing safe concurrent systems with compile-time memory safety guarantees.

## When to Use

- Resolving complex compiler borrow checker errors (`E0502`, `E0499`, `E0382`).
- Designing zero-copy data structures and parsers (`&str`, `&[u8]`, `Cow<'a, str>`).
- Sharing state across multi-threaded asynchronous tasks using Tokio and `Arc`.
- Structuring self-referential or circular data structures using generational arenas.

## When NOT to Use

- High-level glue scripts where rapid iteration in Python or TypeScript is preferable.
- Raw unsafe pointer arithmetic without explicit architectural justification.

## Inputs & Prerequisites

- Rust 1.75+ toolchain installed via `rustup`.
- Basic understanding of Rust ownership rules (one owner, arbitrary shared references XOR one mutable reference).

## Core Workflow

### 1. Lifetime Annotation Syntax & Invariants
Lifetimes describe how long references are valid relative to each other:
```rust
// Invariant: The returned reference is valid as long as BOTH 'a and 'b live
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}
```
- Lifetimes do NOT change how long a value lives; they declare compile-time constraints so the compiler can prove no reference outlives its referent (dangling pointer prevention).

### 2. Avoiding Unnecessary Cloning with `Cow` (Clone-On-Write)
Instead of unconditionally calling `.clone()` or `.to_string()`, use `Cow<'a, str>`:
```rust
use std::borrow::Cow;

// Returns borrowed &str if no modification needed; allocates String only when modified
fn sanitize_input<'a>(input: &'a str) -> Cow<'a, str> {
    if input.contains("<script>") {
        Cow::Owned(input.replace("<script>", ""))
    } else {
        Cow::Borrowed(input) // Zero allocation!
    }
}
```

### 3. Thread-Safe Shared Mutability
Choose the appropriate wrapper pattern:
- **Single-Threaded Interior Mutability**: `Rc<RefCell<T>>` (runtime borrow checking).
- **Multi-Threaded Shared Mutability**: `Arc<Mutex<T>>` or `Arc<RwLock<T>>` for read-heavy workloads.
- **Lock-Free Concurrency**: `std::sync::atomic` for atomic primitives (`AtomicBool`, `AtomicUsize`).

### 4. Structuring Data Structures to Avoid Self-Referential Traps
In Rust, a struct cannot hold both an owned buffer and a reference pointing into that same buffer:
- **Solution A**: Use indices or integer offsets into a shared vector instead of raw references.
- **Solution B**: Use the `rental` or `ouroboros` crate if self-referential structs are unavoidable.
- **Solution C**: Separate storage from indexing (Generational Arena pattern).

### 5. Automated Linting with Clippy
Enforce strict idiomatic Rust standards:
```bash
cargo clippy --all-targets --all-features -- -D warnings
```

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Borrow checker complains about simultaneous mutable and immutable borrows | Narrow the scope of the mutable borrow by placing it inside an explicit `{ ... }` block to release the borrow before the next read. |
| High-performance string parsing | Use `&str` slices instead of allocating new `String` objects for tokens. |
| Deadlocks across multiple Mutexes | Enforce strict acquisition ordering across all threads, or wrap related fields into a single struct protected by one Mutex. |

## Validation & Acceptance Criteria

- [ ] Code compiles cleanly with zero borrow checker errors.
- [ ] `cargo clippy` passes with zero warnings.
- [ ] No speculative `.clone()` calls where zero-copy borrowing is feasible.
- [ ] Multi-threaded shared state implements `Arc<Mutex<T>>` or atomic types safely.
- [ ] No `unsafe` blocks unless accompanied by an explicit `// SAFETY:` rationale.

## Failure Handling & Recovery

- If a complex generic lifetime error cannot be proven by the compiler, refactor from references to owned types (`Box<T>`, `String`) or use reference-counted handles (`Arc<T>`).

## Expected Output & Artifacts

- Idiomatic, memory-safe Rust source modules.
- Cargo test suite demonstrating zero-copy borrowing.
- Clippy validation logs.

## Related Skills

- `golang-goroutine-concurrency-patterns`
- `docker-container-optimization`
- `api-and-interface-design`
