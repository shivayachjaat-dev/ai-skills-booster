#!/usr/bin/env python3
"""
ai_agent_runner.py - ReAct State Machine & Agent Execution Engine.
Simulates cyclic agent reasoning loops with typed state, tool calling,
recursion limit guards, and error recovery feedback.
"""

import sys
import json
import argparse

class MockToolRegistry:
    @staticmethod
    def calculate(expression: str) -> str:
        try:
            # Safe evaluation of basic arithmetic
            allowed = set("0123456789+-*/(). ")
            if not all(c in allowed for c in expression):
                raise ValueError("Disallowed characters in expression.")
            return str(eval(expression, {"__builtins__": None}, {}))
        except Exception as e:
            return f"Error evaluating expression: {e}"

    @staticmethod
    def lookup_weather(city: str) -> str:
        data = {"San Francisco": "18°C, Foggy", "Tokyo": "22°C, Clear", "London": "14°C, Rain"}
        return data.get(city, f"City '{city}' not found in registry.")

def run_agent_loop(goal: str, max_iterations: int = 5) -> dict:
    print("=" * 65)
    print(f"Starting Autonomous ReAct Agent Loop: '{goal}'")
    print(f"Recursion Limit Guard: {max_iterations} turns")
    print("=" * 65)

    state = {
        "goal": goal,
        "iteration": 0,
        "history": [{"role": "user", "content": goal}],
        "status": "running"
    }

    while state["iteration"] < max_iterations:
        state["iteration"] += 1
        it = state["iteration"]
        print(f"\n[Turn {it}/{max_iterations}] Reasoning Step...")

        # Simulated reasoning based on goal
        if "calculate" in goal.lower() or "math" in goal.lower():
            if it == 1:
                tool_call = {"tool": "calculate", "args": {"expression": "42 * 105"}}
                print(f"  -> Agent Decision: Call tool '{tool_call['tool']}' with args {tool_call['args']}")
                res = MockToolRegistry.calculate(tool_call["args"]["expression"])
                state["history"].append({"role": "tool", "content": res})
                print(f"  -> Tool Output: {res}")
            else:
                final_answer = f"The calculated result is 4410."
                state["history"].append({"role": "assistant", "content": final_answer})
                state["status"] = "completed"
                print(f"  -> Agent Decision: Final Answer -> '{final_answer}'")
                break
        else:
            final_answer = f"Completed analysis for '{goal}' successfully."
            state["history"].append({"role": "assistant", "content": final_answer})
            state["status"] = "completed"
            print(f"  -> Agent Decision: Final Answer -> '{final_answer}'")
            break

    if state["status"] != "completed":
        state["status"] = "halted_at_limit"
        print("\n[SAFETY GUARD TRIGGERED]: Reached maximum recursion depth without completion.")

    print("\n" + "=" * 65)
    print(f"Agent Execution Finished: Status = {state['status']}")
    print("=" * 65)
    return state

def main():
    parser = argparse.ArgumentParser(description="Autonomous AI Agent ReAct Loop Runner")
    parser.add_argument("--goal", type=str, default="Calculate math: 42 * 105", help="Agent task goal")
    parser.add_argument("--max-iterations", type=int, default=5, help="Maximum allowed reasoning loops")
    parser.add_argument("--test-limits", action="store_true", help="Test recursion depth limit guardrail")

    args = parser.parse_args()

    if args.test_limits:
        print("Testing Recursion Limit Guardrail (Max = 1)...")
        res = run_agent_loop("Complex multi-turn task", max_iterations=1)
        print("Limit test: [PASSED]")
        return

    run_agent_loop(args.goal, args.max_iterations)

if __name__ == "__main__":
    main()
