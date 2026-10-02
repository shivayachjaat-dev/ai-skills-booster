---
name: wireguard-site-to-site-mesh-vpn
description: "Use this skill when designing, configuring, and maintaining secure site-to-site and point-to-point mesh VPN networks using WireGuard. It covers Curve25519 cryptographic key generation, wg-quick configuration files, AllowedIPs routing tables, persistent keepalives behind NAT, and network firewall forwarding rules."
domain: security
category: network-security
subcategory: wireguard
tags:
  - wireguard
  - vpn
  - networking
  - mesh-vpn
  - security
  - cryptography
  - linux
technologies:
  - WireGuard
  - Linux Kernel
  - iptables
  - wg-quick
  - OpenBSD
complexity: advanced
maturity: stable
tools:
  - wg
  - wg-quick
  - iptables
  - ip
dependencies:
  - wireguard-tools >= 1.0.0
---
# WireGuard Site-to-Site & Mesh VPN Architecture

## Overview

A comprehensive engineering guide for architecting ultra-fast, state-of-the-art encrypted virtual private networks using WireGuard. Operating directly in Linux kernel space using modern cryptography (Noise protocol framework, Curve25519, ChaCha20-Poly1305, BLAKE2s), this skill instructs AI agents on peer key management, `wg-quick` configuration, `AllowedIPs` routing topology design, NAT traversal with persistent keepalives, and IP packet forwarding.

## When to Use

- Interconnecting private cloud VPCs (AWS, GCP, Azure) across providers without expensive managed VPN gateways.
- Establishing secure site-to-site tunnels between on-premises data centers and cloud clusters.
- Creating zero-trust mesh communication between globally distributed edge nodes and servers.
- Replacing legacy OpenVPN or IPsec tunnels with high-throughput (line-rate) cryptographic routing.

## When NOT to Use

- Application-layer service routing where HTTP/gRPC load balancing and path rewriting are required (use Istio or Envoy).
- Simple client-to-browser user authentication (use Cloudflare Access, Tailscale, or WireGuard-based managed overlays).

## Inputs & Prerequisites

- Linux servers with Linux kernel >= 5.6 (native WireGuard support) or `wireguard-dkms`.
- UDP port (default: 51820) opened on public firewalls/security groups.
- `wireguard-tools` installed (`apt install wireguard-tools` / `yum install wireguard-tools`).

## Core Workflow

### 1. Cryptographic Keypair Generation
Generate private/public keys with strict Unix permissions:

```bash
umask 077
wg genkey | tee privatekey | wg pubkey > publickey
```

### 2. Hub / Gateway Configuration (`/etc/wireguard/wg0.conf`)
Configure the central hub node with IP forwarding and NAT routing rules:

```ini
[Interface]
Address = 10.100.0.1/24
ListenPort = 51820
PrivateKey = <HUB_PRIVATE_KEY>

# Enable IP forwarding and NAT masquerade for traffic heading to LAN (eth0)
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -A FORWARD -o wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -D FORWARD -o wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

# Peer: Site A (Remote Branch Office)
[Peer]
PublicKey = <SITE_A_PUBLIC_KEY>
AllowedIPs = 10.100.0.2/32, 192.168.1.0/24

# Peer: Site B (Cloud VPC)
[Peer]
PublicKey = <SITE_B_PUBLIC_KEY>
AllowedIPs = 10.100.0.3/32, 172.16.0.0/16
```

### 3. Spoke / Branch Node Configuration (`/etc/wireguard/wg0.conf`)
Configure the remote spoke node with NAT traversal:

```ini
[Interface]
Address = 10.100.0.2/24
PrivateKey = <SITE_A_PRIVATE_KEY>

[Peer]
PublicKey = <HUB_PUBLIC_KEY>
Endpoint = 203.0.113.50:51820
# Routes all internal subnets through tunnel
AllowedIPs = 10.100.0.0/24, 172.16.0.0/16
# Send keepalive packet every 25 seconds to keep NAT mapping open on outbound firewall
PersistentKeepalive = 25
```

### 4. Service Activation & Kernel Tuning
Enable packet forwarding and start the tunnel via `systemd`:

```bash
# Enable IPv4 forwarding
echo "net.ipv4.ip_forward = 1" | sudo tee -a /etc/sysctl.d/99-wireguard.conf
sudo sysctl -p /etc/sysctl.d/99-wireguard.conf

# Start and enable WireGuard interface
sudo systemctl enable --now wg-quick@wg0
```

## Best Practices & Failure Modes

1. **`AllowedIPs` Misconfiguration Trap**: In WireGuard, `AllowedIPs` acts as both a routing table and an access control list. If a remote host sends a packet with a source IP not listed in `AllowedIPs`, the kernel drops the packet silently without logging. Always explicitly enumerate routed CIDR blocks.
2. **Missing `PersistentKeepalive` Behind NAT**: When a peer sits behind stateful NAT (AWS NAT Gateway, home routers), incoming packets cannot initiate connections. Setting `PersistentKeepalive = 25` maintains outbound connection states.
3. **MTU Black Hole Issues**: Encapsulating packets in WireGuard adds 32 bytes (IPv4) or 40 bytes (IPv6) of overhead. If the underlying path MTU is 1500, setting WireGuard MTU too high causes packet fragmentation or drops. Set `MTU = 1420` in the `[Interface]` section for reliable performance.

## Verification & Testing

- Inspect active tunnel handshakes and transfer metrics:
  ```bash
  sudo wg show
  ```
  *Verify that `latest handshake` is less than 3 minutes old and `transfer` counts are incrementing.*
- Test ICMP ping across the tunnel interface:
  ```bash
  ping -c 3 10.100.0.1
  ```
