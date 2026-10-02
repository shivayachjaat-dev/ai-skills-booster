---
name: multi-agent-debate-and-reflection
description: "Use this skill when designing, implementing, and evaluating multi-agent debate, reflection, and self-correction workflows. It guides the agent through constructing multi-turn debate topologies (Proposer, Critic, Reflector), consensus scoring mechanisms, majority voting, eliminating groupthink and confirmation bias, and improving reasoning accuracy on complex tasks."
domain: ai-engineering
category: agents
subcategory: autogen
tags:
  - multi-agent
  - agent-debate
  - reflection
  - autogen
  - crewai
  - self-correction
  - reasoning
technologies:
  - Python
  - OpenAI
  - Anthropic
  - AutoGen
  - CrewAI
complexity: advanced
maturity: stable
tools:
  - python
dependencies:
  - python >= 3.10
---
# Multi-Agent Debate & Reflection Architecture

## Overview

A definitive production AI engineering standard for constructing multi-agent debate, reflection, and peer-review systems. Single-agent LLM systems frequently suffer from hallucinations, reasoning blind spots, and confirmation bias. This skill instructs AI agents on architecting multi-perspective collaborative networks: orchestrating adversarial Proposer-Critic debates, iterative self-reflection loops, round-robin consensus scoring, and final synthesis arbitration to achieve high factual accuracy on complex analytical tasks.

## When to Use

- Solving high-stakes, multi-step logical problems, mathematical reasoning, or security code audits.
- Eliminating hallucinations in fact-intensive research and regulatory compliance tasks.
- Stress-testing architectural plans or technical proposals through structured adversarial debate.
- Reaching objective consensus across differing model families (e.g. GPT-4o vs Claude 3.5 Sonnet).

## When NOT to Use

- Real-time sub-second conversational chatbots where multi-turn agent debate latency is unacceptable.
- Simple factual lookups or extractive retrieval where standard RAG is sufficient.

## Inputs & Prerequisites

- Python 3.10+ runtime.
- Access to one or more LLM provider APIs.
- Well-defined complex prompt or problem statement.

## Core Workflow

### 1. Adversarial Debate & Reflection Orchestrator
Coordinate interaction between a Proposer agent, an adversarial Critic, and a Judge:

```python
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class DebateRound:
    round_num: int
    proposal: str
    critique: str
    rebuttal: str

class MultiAgentDebatePipeline:
    def __init__(self, proposer_llm, critic_llm, judge_llm):
        self.proposer = proposer_llm
        self.critic = critic_llm
        self.judge = judge_llm

    def execute_debate(self, task_prompt: str, max_rounds: int = 2) -> Dict[str, Any]:
        # Step 1: Initial Solution Generation
        current_solution = self.proposer.generate(
            system_prompt="You are a Principal Solutions Architect. Produce a detailed, concrete solution.",
            user_prompt=task_prompt
        )

        history: List[DebateRound] = []

        # Step 2: Multi-Round Debate & Reflection
        for round_idx in range(1, max_rounds + 1):
            # Adversarial Critique
            critique = self.critic.generate(
                system_prompt=(
                    "You are a rigorous Adversarial Reviewer. Your goal is to find edge cases, "
                    "logical errors, unstated assumptions, and performance bottlenecks in the proposed solution. "
                    "Be relentlessly critical and point out specific flaws."
                ),
                user_prompt=f"Task: {task_prompt}\nProposed Solution:\n{current_solution}"
            )

            # Rebuttal and Refined Solution
            refined_solution = self.proposer.generate(
                system_prompt=(
                    "You are the Proposer. Review the critical feedback. Defend your choices where valid, "
                    "concede genuine flaws, and output an improved, revised solution that addresses all valid critiques."
                ),
                user_prompt=f"Previous Solution:\n{current_solution}\n\nCritique:\n{critique}"
            )

            history.append(DebateRound(round_idx, current_solution, critique, refined_solution))
            current_solution = refined_solution

        # Step 3: Impartial Judge Adjudication & Synthesis
        verdict = self.judge.generate(
            system_prompt=(
                "You are an impartial Judge. Review the original problem, the debate history, and the final solution. "
                "Synthesize the definitive, high-accuracy conclusion incorporating the strongest arguments."
            ),
            user_prompt=f"Problem: {task_prompt}\nFinal Revised Solution:\n{current_solution}"
        )

        return {
            "final_solution": verdict,
            "debate_rounds": len(history),
            "history": history
        }
```

### 2. Majority Voting with Heterogeneous Agents
Query three diverse model architectures and aggregate consensus:

```python
def majority_vote_consensus(agents: list, problem_prompt: str) -> str:
    votes = []
    for agent in agents:
        ans = agent.generate(
            system_prompt="Answer the question directly and conclude with 'FINAL ANSWER: <answer>'.",
            user_prompt=problem_prompt
        )
        votes.append(extract_final_answer(ans))

    # Majority count
    from collections import Counter
    counts = Counter(votes)
    most_common, frequency = counts.most_common(1)[0]
    
    if frequency > len(agents) // 2:
        return most_common
    else:
        # Fallback to secondary arbitration if no clear consensus
        return arbitrate_split_decision(agents, votes)
```

## Best Practices & Failure Modes

1. **Sycophantic Agreement Decay**: Without explicitly adversarial system prompts, LLM critics tend to agree with the proposer ("Your solution is great, no changes needed!"). Explicitly instruct the critic to uncover at least 2 subtle flaws or vulnerabilities.
2. **Infinite Debate Thrashing**: In circular debates, agents continuously argue back and forth without converging. Enforce strict round caps (`max_rounds = 2` or `3`) and terminate with an authoritative Judge synthesis.
3. **Compound Token Costs**: Running multi-agent debates multiplies token consumption by 3x-6x per query. Reserve multi-agent debate workflows for complex reasoning or high-impact decisions, rather than routine queries.

## Verification & Testing

- Unit test verifying debate loop convergence:
  ```python
  class MockLLM:
      def __init__(self, responses):
          self.responses = responses
          self.call_count = 0
      def generate(self, system_prompt, user_prompt):
          resp = self.responses[self.call_count % len(self.responses)]
          self.call_count += 1
          return resp

  def test_multi_agent_pipeline():
      proposer = MockLLM(["Initial proposal", "Revised proposal"])
      critic = MockLLM(["Critique of proposal"])
      judge = MockLLM(["Final synthesized answer"])

      pipeline = MultiAgentDebatePipeline(proposer, critic, judge)
      res = pipeline.execute_debate("Design a high-scale cache", max_rounds=1)
      assert res["final_solution"] == "Final synthesized answer"
      assert len(res["history"]) == 1
  ```
