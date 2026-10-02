---
name: grpc-service-implementation
description: "Use this skill when designing, compiling, and implementing high-performance gRPC microservices with Protocol Buffers (proto3). It guides the agent through defining .proto service contracts, bidirectional streaming, gRPC interceptors for auth/logging, deadline/cancellation propagation, HTTP/2 multiplexing, and gRPC status code error handling."
domain: backend
category: grpc
subcategory: services
tags:
  - grpc
  - protobuf
  - backend
  - microservices
  - http2
  - streaming
  - rpc
technologies:
  - gRPC
  - Protocol Buffers
  - Go
  - Python
  - TypeScript
  - HTTP/2
complexity: advanced
maturity: stable
tools:
  - protoc
  - python
  - go
dependencies:
  - grpcio
  - protobuf
---
# gRPC Service Implementation

## Overview

A guide for building low-latency, strongly-typed internal microservices using Google's Remote Procedure Call (gRPC) framework and Protocol Buffers (proto3). Delivers up to 7x to 10x throughput advantages over JSON REST APIs through compact binary serialization, HTTP/2 connection multiplexing, and bi-directional streaming.

## When to Use

- High-throughput east-west communication between internal microservices.
- Low-latency real-time streaming (server streaming, client streaming, bi-directional streaming).
- Polyglot architectures (e.g. Go backend calling Python ML inference server) requiring strictly enforced type contracts.
- Enforcing deadline propagation across distributed microservice call graphs.

## When NOT to Use

- Public web APIs consumed directly by arbitrary third-party browser clients (use REST or GraphQL).
- Simple file storage transfers where chunked HTTP multipart is more practical.

## Inputs & Prerequisites

- `protoc` compiler installed or language-specific compiler toolchain (`grpc_tools.protoc`).
- Service definition specification (`.proto` file).

## Core Workflow

### 1. Protocol Buffer Contract Design (`.proto`)
Write the explicit interface definition in proto3:
```protobuf
syntax = "proto3";

package payment.v1;

option go_package = "github.com/company/payment/v1;paymentv1";

service PaymentService {
  rpc ProcessPayment (ProcessPaymentRequest) returns (ProcessPaymentResponse);
  rpc StreamTransactions (TransactionFilter) returns (stream TransactionEvent);
}

message ProcessPaymentRequest {
  string order_id = 1;
  int64 amount_cents = 2;
  string currency = 3;
  string idempotency_key = 4;
}

message ProcessPaymentResponse {
  string transaction_id = 1;
  PaymentStatus status = 2;
  int64 processed_at_unix = 3;
}

enum PaymentStatus {
  PAYMENT_STATUS_UNSPECIFIED = 0;
  PAYMENT_STATUS_COMPLETED = 1;
  PAYMENT_STATUS_DECLINED = 2;
  PAYMENT_STATUS_PENDING = 3;
}
```

### 2. Code Generation (Protoc)
Compile the `.proto` file into language stubs:
```bash
# Python example
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. payment.proto
```

### 3. Server Implementation & Deadlines
Implement the generated base class, honoring client deadlines:
```python
import grpc
import payment_pb2
import payment_pb2_grpc

class PaymentServicer(payment_pb2_grpc.PaymentServiceServicer):
    def ProcessPayment(self, request, context):
        # 1. Check Deadline / Cancellation
        if context.is_active() is False:
            context.abort(grpc.StatusCode.CANCELLED, "Client cancelled request")
            
        # 2. Validate Inputs
        if request.amount_cents <= 0:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Amount must be greater than zero")

        # 3. Process business logic...
        return payment_pb2.ProcessPaymentResponse(
            transaction_id="tx_987654",
            status=payment_pb2.PAYMENT_STATUS_COMPLETED,
            processed_at_unix=1700000000
        )
```

### 4. gRPC Interceptors for Cross-Cutting Concerns
Do not duplicate auth, tracing, and metric collection in individual RPC methods. Implement unary interceptors:
- **Authentication**: Inspect metadata header (`authorization: Bearer <token>`).
- **Telemetry**: Inject OpenTelemetry trace context into outgoing metadata.
- **Logging**: Log method name, duration, and status code.

### 5. Proper Status Code Mapping
Never return generic `UNKNOWN` or unhandled exceptions:
- `INVALID_ARGUMENT`: Input schema validation failed.
- `UNAUTHENTICATED`: Missing or invalid bearer token.
- `PERMISSION_DENIED`: Caller lacks required role.
- `NOT_FOUND`: Target entity does not exist.
- `ALREADY_EXISTS`: Duplicate key violation.
- `DEADLINE_EXCEEDED`: Downstream dependency exceeded timeout budget.

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Downstream service takes too long | Pass client context deadline downstream (`deadline = context.time_remaining()`) to abort cascading wasted work when client disconnects. |
| Browser client needs access | Deploy Envoy proxy with `grpc-web` filter to translate HTTP/1.1 JSON into HTTP/2 gRPC frames. |
| Breaking changes in protobuf | Never change existing field tag numbers (`1, 2, 3`). If a field is obsolete, mark it `reserved`. |

## Validation & Acceptance Criteria

- [ ] `.proto` files follow Google API Design Guide conventions.
- [ ] Interceptors handle authentication, logging, and error tracing globally.
- [ ] Context cancellation and deadlines checked during long-running tasks.
- [ ] Errors mapped to explicit `grpc.StatusCode` values.
- [ ] Integration tests verify client stub calls succeed over HTTP/2.

## Failure Handling & Recovery

- If gRPC connection drops, client channel should use exponential backoff with jitter to reconnect automatically.

## Expected Output & Artifacts

- Clean `.proto` contract specification.
- Generated client and server stub packages.
- Runnable server implementation with interceptor pipeline.

## Related Skills

- `api-and-interface-design`
- `fastapi-async-api-design`
- `kafka-event-driven-architecture`
