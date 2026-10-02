---
name: websocket-realtime-communication
description: "Use this skill when designing, building, and scaling bi-directional real-time WebSocket applications. It guides the agent through WebSocket handshake upgrade, heartbeat ping/pong keepalive frames, horizontal clustering using Redis Pub/Sub backplanes, reconnection backoff with message replay buffers, and binary frame optimization."
domain: backend
category: realtime
subcategory: websocket
tags:
  - websocket
  - realtime
  - backend
  - networking
  - redis
  - concurrency
technologies:
  - WebSocket
  - Node.js
  - Python
  - Redis
  - TypeScript
complexity: advanced
maturity: stable
tools:
  - node
  - python
  - curl
dependencies:
  - ws or websockets
  - redis
---
# WebSocket Real-Time Communication

## Overview

An architectural framework for designing, implementing, and horizontally scaling persistent, bi-directional WebSocket connections. Enables AI agents to establish real-time collaboration, live streaming dashboards, financial tickers, and chat applications with sub-10ms delivery latencies.

## When to Use

- Low-latency bi-directional messaging where HTTP polling overhead is unacceptable.
- Collaborative multi-user editing, shared whiteboards, or live cursor tracking.
- Real-time financial market data feeds and stock price streaming.
- Multiplayer gaming or conversational streaming agent voice/text interfaces.

## When NOT to Use

- Pure one-way server-to-client notifications with infrequent updates (use Server-Sent Events / SSE).
- Standard CRUD resource management (use REST).

## Inputs & Prerequisites

- WebSocket server runtime (e.g. Node.js `ws`, Python `websockets` or FastAPI).
- Redis instance for horizontal multi-instance Pub/Sub broadcasting.
- Client connection authentication token (JWT or pre-signed ticket).

## Core Workflow

### 1. Connection Upgrade & Authentication
Authenticate during the initial HTTP upgrade request before the TCP socket transitions to WebSocket protocol:
```typescript
import { WebSocketServer } from "ws";
import http from "http";

const server = http.createServer();
const wss = new WebSocketServer({ noServer: true });

server.on("upgrade", (request, socket, head) => {
  const token = new URL(request.url, "http://localhost").searchParams.get("token");
  const user = verifyToken(token);
  
  if (!user) {
    socket.write("HTTP/1.1 401 Unauthorized\r\n\r\n");
    socket.destroy();
    return;
  }
  
  wss.handleUpgrade(request, socket, head, (ws) => {
    ws.userId = user.id;
    wss.emit("connection", ws, request);
  });
});
```

### 2. Heartbeat Keepalive & Dead Socket Termination
TCP sockets can silently die without generating a disconnect event (e.g. client enters sleep mode or wifi drops). Enforce an active ping/pong heartbeat:
```typescript
function setupHeartbeat(ws) {
  ws.isAlive = true;
  ws.on("pong", () => { ws.isAlive = true; });
}

const interval = setInterval(() => {
  wss.clients.forEach((ws) => {
    if (ws.isAlive === false) return ws.terminate();
    ws.isAlive = false;
    ws.ping();
  });
}, 30000); // 30-second ping interval
```

### 3. Horizontal Scaling via Redis Pub/Sub Backplane
A single server process can only hold connections for clients connected to its local port. Broadcast messages across a multi-server cluster using Redis:
1. When Server A receives a message from Client 1 in room `chat:42`, it publishes the event to Redis channel `room:42`.
2. All running servers (A, B, C) subscribed to `room:42` receive the event from Redis.
3. Each server broadcasts the event to its locally connected sockets.

### 4. Reconnection with Message Sequence Replay
When a mobile or browser client disconnects and reconnects:
1. Client sends last received message sequence ID: `{ type: "RESUME", last_seq: 142 }`.
2. Server queries an in-memory buffer or Redis stream for messages with `seq > 142`.
3. Server replays missed messages in order before resuming normal live streaming.

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Load balancer terminates idle connections after 60s | Send periodic WebSocket ping frames every 25 seconds to keep intermediary proxy timeouts active. |
| High throughput numeric data | Use binary data frames (`ArrayBuffer` / `Uint8Array`) with Protocol Buffers instead of JSON text frames to reduce CPU parsing overhead. |
| Client slow consumer / buffer bloat | Check `ws.bufferedAmount`. If backpressure exceeds 1MB, disconnect slow consumer to protect server memory. |

## Validation & Acceptance Criteria

- [ ] Authentication occurs during HTTP upgrade phase before connection acceptance.
- [ ] Ping/pong keepalive runs periodically, terminating unresponsive sockets.
- [ ] Multi-instance horizontal scaling verified via Redis Pub/Sub backplane.
- [ ] Backpressure monitored to prevent out-of-memory crashes on slow clients.
- [ ] Clients reconnect cleanly with exponential backoff and message replay.

## Failure Handling & Recovery

- If Redis backplane disconnects, fall back to local broadcasting and attempt automatic reconnection with exponential backoff.

## Expected Output & Artifacts

- WebSocket server implementation with authentication and heartbeat.
- Redis Pub/Sub integration adapter for cluster scaling.
- Client reconnection and replay protocol documentation.

## Related Skills

- `fastapi-async-api-design`
- `redis-caching-patterns`
- `api-and-interface-design`
