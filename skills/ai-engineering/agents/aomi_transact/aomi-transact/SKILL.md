---
name: aomi-transact
description: "Use this skill to build, simulate, and execute natural-language crypto and DeFi transactions across EVM chains (Ethereum, Base, Arbitrum, Optimism, Polygon) using the Aomi agent CLI and Account Abstraction. It enforces forked-chain simulation before signing, drain-vector validation (recipient == msg.sender), multi-step batching (approve+swap), and non-custodial wallet signature gates."
domain: ai-engineering
category: agents
subcategory: aomi_transact
tags:
  - ai-engineering
  - agents
  - web3
  - defi
  - evm
  - account-abstraction
  - transaction-simulation
technologies:
  - Aomi CLI
  - Ethereum
  - ERC-4337
  - EIP-7702
  - Uniswap V3
  - Lido
  - Python
complexity: expert
maturity: stable
tools:
  - aomi
  - npx
  - python
  - bash
dependencies:
  - "@aomi-labs/client@>=0.1.30"
  - python@>=3.10
version: 1.0.0
author: Antigravity Team
---

# Aomi Transact: Natural-Language EVM & DeFi Transaction Orchestration

## Overview

A production engineering standard for transforming natural-language intents (e.g., *"swap 1 USDC for WETH on Uniswap V3"* or *"stake 0.01 ETH with Lido"*) into cryptographically verified, simulated, and wallet-signed transactions on EVM blockchains (Ethereum, Base, Arbitrum, Optimism, Polygon). Operating directly via the `@aomi-labs/client` CLI, this architecture enforces a non-custodial, simulation-first paradigm: transactions are staged in an offline queue, sequentially executed on a local forked chain to verify state transitions (such as token approvals before swaps), and audited against malicious drain vectors before the user is prompted to sign.

```
+--------------------------------------------------------------------------------+
|                         Aomi Natural-Language DeFi Flow                        |
|                                                                                |
|  [ Natural Language Prompt ] ---> [ Aomi Agent Intent & Route Resolution ]     |
|                                                  |                             |
|                                                  v                             |
|                           [ Transaction Queue Staging (aomi tx list) ]         |
|                            (tx-1: ERC20 approve, tx-2: Protocol swap)          |
|                                                  |                             |
|                                                  v                             |
|                        [ Forked Chain Simulation (aomi tx simulate) ]          |
|                                                  |                             |
|                                                  v                             |
|                        [ Drain Vector Security Filter ]                        |
|                         (Verify: recipient == msg.sender)                      |
|                                                  |                             |
|                                                  v                             |
|                             [ Explicit User Approval Gate ]                    |
|                                                  |                             |
|                        +-------------------------+-----------------------+     |
|                        | Approved                                        |     |
|                        v                                                 v     |
|          [ Account Abstraction Signing ]                       [ Discard Batch ]
|          (EIP-7702 / ERC-4337 Bundler)                                         |
|                        |                                                       |
|                        v                                                       |
|          [ On-Chain Broadcast & Receipt ]                                      |
+--------------------------------------------------------------------------------+
```

## When to Use

- Interacting with decentralized finance (DeFi) protocols (Uniswap, Aave, Lido, Morpho, GMX, Polymarket) via natural-language terminal agents.
- Simulating complex multi-step DeFi interactions (ERC-20 token approval followed by liquidity provision or swap) on forked chains prior to broadcasting.
- Enforcing Account Abstraction (EIP-7702 on Ethereum Mainnet, ERC-4337 on Layer 2 rollups) for gas sponsorship and batched execution.
- Validating transaction calldata to eliminate address spoofing and wallet-drain vulnerabilities.

## When NOT to Use

- Centralized exchange (CEX) trading or custodial account management (use Binance or Coinbase REST/WebSocket APIs).
- Non-EVM blockchain networks (Solana, Bitcoin, Cosmos; require dedicated SVM or UTXO tooling).
- Unmonitored automated trading without human signature approval gates.

## Inputs & Prerequisites

- Node.js 18+ and `@aomi-labs/client` v0.1.30+ installed (`npm install -g @aomi-labs/client`).
- Connected EVM wallet public key (`0x...`) with network access to the target chain RPC.
- Native gas token (ETH on Ethereum/Base/Arbitrum, POL on Polygon) for transaction execution.

## Core Workflow

### Step 1: Session Initialization & Read-Only Market Query
Initialize a dedicated session and verify asset quotes without queuing state-changing transactions:

```bash
# Query live market pricing in a new session
aomi --prompt "What is the current swap price of 1 ETH for USDC on Uniswap V3?" --new-session

# Verify no transactions are pending
aomi tx list
```

### Step 2: Multi-Step Transaction Construction
Request a multi-stage operation. Aomi automatically decomposes the intent into prerequisite approvals and contract calls:

```bash
# Example: Swap 100 USDC for WETH on Base
USER_WALLET="0x1234567890123456789012345678901234567890"

aomi chat "Swap 100 USDC for WETH on Uniswap V3, recipient is my wallet" \
  --public-key "$USER_WALLET" \
  --chain 8453 \
  --new-session
```

### Step 3: Inspecting Queued Transactions
Inspect the staged execution queue. A multi-step trade will stage both the token approval (`tx-1`) and the protocol swap (`tx-2`):

```bash
aomi tx list
```
*Expected Output:*
```text
[tx-1] ERC20.approve(spender: 0xUniswapV3Router, amount: 100000000)
[tx-2] SwapRouter.exactInputSingle(tokenIn: USDC, tokenOut: WETH, recipient: 0x1234...890)
```

### Step 4: Mandatory Forked-Chain Simulation
Never sign multi-step batches without sequential simulation. Simulation executes `tx-1` and `tx-2` sequentially against an ephemeral chain fork, ensuring `tx-2` has valid allowance:

```bash
aomi tx simulate tx-1 tx-2
```
*Verification:* Ensure the output indicates `Batch [tx-1, tx-2] passed simulation`. If simulation reverts, discard the batch and do NOT proceed to signing.

### Step 5: Drain Vector Audit & Human Signature Approval
Verify that the `recipient`, `to`, or `onBehalfOf` parameter strictly matches the sender's own public key:

```bash
# Run local safety auditor
python scripts/aomi_tx_simulator.py --audit-batch --wallet "$USER_WALLET"
```

Once safety verification passes, present the final batch summary to the user and await explicit approval. Only run signing when approved:

```bash
# Execute wallet signature and on-chain broadcast
aomi tx sign tx-1 tx-2
```

## Best Practices & Failure Modes

- **Strict Approval Gate**: Never combine `aomi chat` and `aomi tx sign` in an automated pipeline. The user must explicitly inspect `aomi tx list` and approve the specific transaction IDs.
- **Drain Vector Blocking**: If calldata redirects tokens to an unfamiliar address (`recipient != msg.sender`), immediately halt execution and alert the user.
- **Slippage & Deadline Management**: Market quotes expire rapidly. If transaction signing is delayed beyond 5 minutes, clear the queue (`aomi tx clear`) and re-simulate with fresh deadlines.
- **RPC Consistency**: Always match the `--rpc-url` parameter to the specific chain ID of the queued transaction, not just the session default.

## Verification & Testing

1. Validate CLI installation: `aomi --version` (must be $\ge$ 0.1.30).
2. Test simulation safety: Run `python scripts/aomi_tx_simulator.py --test-drain-block` to verify that calldata redirecting funds to unauthorized addresses is rejected.
3. Test dry-run Lido staking: Stage a test stake of `0.001 ETH` on Goerli/Sepolia testnet, simulate the transaction, and confirm gas estimation and ABI decoding.
