---
name: multi-agent-consensus-protocol
description: "Use this skill when designing, orchestrating, and coordinating multi-agent systems requiring consensus, debate, and validation. It guides the agent through role-specialized multi-agent topologies (Generator-Critic, Committee Voting, Delphi Consensus), conflict resolution protocols, shared scratchpad synchronization, and infinite circular argument prevention."
domain: ai-engineering
category: agents
subcategory: orchestration
tags:
  - ai-agents
  - multi-agent
  - orchestration
  - consensus
  - llm-architecture
  - delphi-method
technologies:
  - Python
  - LangGraph
  - AutoGen
  - JSON
complexity: expert
maturity: stable
tools:
  - python
dependencies:
  - python >= 3.9
---
# Multi-Agent Consensus Protocol

## Overview

A multi-agent coordination protocol designed to achieve high-accuracy decisions, code architectures, and evaluations through structured agent collaboration. By combining specialized roles (Architect, Implementer, Security Auditor, Verifier) with formal consensus algorithms, this skill eliminates individual model hallucinations and achieves superior outputs compared to monolithic single-prompt agents.

## When to Use

- Mission-critical tasks (financial calculation, security vulnerability triage, high-risk code refactoring) where single-agent hallucinations carry severe consequences.
- Complex system design where diverse expert perspectives (security, performance, usability) must be balanced.
- Implementing Generator-Critic or Multi-Persona debate topologies.
- Resolving conflicting suggestions across distributed autonomous agents.

## When NOT to Use

- Simple, straightforward queries or code translations where single-turn generation is sufficient.
- Low-latency real-time chat where multi-agent roundtrips exceed latency budgets.

## Inputs & Prerequisites

- Multiple LLM model endpoints or diverse system prompt personas.
- Communication bus or shared blackboard state (e.g. structured JSON state graph).
- Pre-defined termination criteria and round limits.

## Core Workflow

### 1. Topology Selection
Select the orchestration topology matching the task complexity:
- **Generator-Critic-Refiner (Linear)**: Generator proposes solution $\rightarrow$ Critic inspects flaws and security risks $\rightarrow$ Refiner updates solution.
- **Committee Majority Voting**: Multiple diverse models (e.g. Claude + GPT + Gemini) generate independent answers; a Judge agent evaluates consensus and selects or synthesizes the majority view.
- **Delphi Multi-Round Consensus**: Agents submit anonymous initial estimates, review anonymized peer rationales, revise their positions, and converge toward a median consensus.

### 2. Structured Agent Roles & System Prompts
Assign non-overlapping, adversarial responsibilities:
```text
[ Orchestrator Agent ]
       │
  ┌────┴───────────────────────────┐
  ▼                                ▼
[ Architect Agent ]      [ Security Critic ]
(Proposes API contracts) (Attempts to break API)
  │                                │
  └───────────────┬────────────────┘
                  ▼
          [ Consensus Judge ]
        (Reconciles differences)
```

### 3. Conflict Resolution & Convergence Scoring
Measure agreement across agent outputs using structured JSON proposals:
```python
def evaluate_consensus(proposals, consensus_threshold=0.80):
    # proposals: list of structured dicts from agent personas
    # Compute agreement ratio across key decision fields
    agreements = {}
    for key in ["architecture_pattern", "database_choice", "auth_strategy"]:
        votes = [p[key] for p in proposals]
        most_common = max(set(votes), key=votes.count)
        agreement_ratio = votes.count(most_common) / len(votes)
        agreements[key] = (most_common, agreement_ratio)
        
    all_converged = all(ratio >= consensus_threshold for _, ratio in agreements.values())
    return all_converged, agreements
```

### 4. Preventing Infinite Argument Loops & Oscillation
Multi-agent debates can devolve into endless circular disagreement:
- **Hard Round Limits**: Enforce maximum 3 rounds of debate (`MAX_ROUNDS = 3`).
- **Diminishing Temperature**: Reduce temperature by 0.2 on each successive round to force convergence.
- **Tie-Breaker Authority**: Designate an explicit Lead Architect / Judge persona with unilateral veto and final decision authority if consensus is not reached by Round 3.

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Agents agree unanimously on a hallucinated fact | Inject external ground truth verification tools (e.g. run a real unit test or compiler) into the consensus loop to ground debate in reality. |
| One agent stubbornly dissents on minor style preference | Consensus Judge evaluates whether dissent concerns a functional invariant vs cosmetic preference; override cosmetic dissent. |
| Cost and token budget exhaustion | Limit full committee debate to high-level architecture decisions; delegate routine code writing to a single executor agent. |

## Validation & Acceptance Criteria

- [ ] Multi-agent state tracked in a structured, immutable state graph.
- [ ] Explicit role boundaries prevent agents from duplicating duties.
- [ ] Hard round limits (maximum 3 turns) enforce termination.
- [ ] Ground-truth verification tools (compilers, test runners) validate final consensus.
- [ ] Final output synthesizes resolved trade-offs transparently.

## Failure Handling & Recovery

- If models fail to reach consensus after maximum rounds, fall back to the most conservative security-first proposal and flag for human review.

## Expected Output & Artifacts

- Multi-agent state machine graph implementation.
- Consensus evaluation and debate transcript report.
- Synthesized consensus decision document.

## Related Skills

- `ai-agent-benchmark-evaluation`
- `agent-project-memory`
- `agent-tool-use-reliability`
