# Context Engineering & Attention Allocation Technical Reference

## 1. Attention Dynamics & "Lost in the Middle"

Empirical evaluations of large transformer architectures reveal that retrieval and reasoning accuracy follow a **U-shaped curve** across the prompt context window:

```
Accuracy (%)
  100 | \                                            /
   90 |  \                                          /
   80 |   \                                        /
   70 |    \______________________________________/
      +------------------------------------------------
       0% (Primacy)       50% (Middle)       100% (Recency)
                     Relative Prompt Position
```

### Strategic Placement Rules:
1. **Primacy Zone ($0\text{--}15\%$ of context)**: Place system boundaries, safety constraints, role invariants, and architectural rules.
2. **Intermediate Zone ($15\text{--}80\%$ of context)**: Place passive reference materials: API documentation, library definitions, and AST source slices.
3. **Recency Zone ($80\text{--}100\%$ of context)**: Place the immediate user objective, the specific file to modify, and the failing test stack trace.

---

## 2. AST-Driven Context Distillation

Feeding entire 3,000-line source files into LLM context wastes tokens and increases distraction. Use Python's Abstract Syntax Tree (AST) to extract minimal subgraphs:
- Parse module into AST nodes (`ast.parse`).
- Traverse down to target `FunctionDef` or `ClassDef`.
- Extract source segment via `ast.get_source_segment`.
- Replace auxiliary helper functions with single-line docstring stubs (`def helper(): ...`).

---

## 3. Log Noise Suppression & Signal Maximization

Automated test runner output frequently spans thousands of lines of successful passes before emitting a single failure.
- Strip all standard pass output.
- Anchor log filtering to `"Traceback (most recent call last):"` or `"FAILED tests/"`.
- Bound captured error snippets to a strict 15-20 line maximum.
