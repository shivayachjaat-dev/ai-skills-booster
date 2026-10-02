# Attack Tree Methodology Guide

## Bruce Schneier Attack Tree Notation
Attack trees were popularized by Bruce Schneier in 1999 as a formal method to evaluate cyber-physical and information security systems:
- Nodes represent sub-goals.
- Leaves represent individual attack vectors.
- Operators (AND / OR) quantify whether attackers need parallel conditions or choices.

## Node Scoring Matrix
| Metric | Low (1 pt) | Medium (3 pts) | High (5 pts) | Extreme (10 pts) |
|---|---|---|---|---|
| Attacker Cost | < $100 | $100 - $5,000 | $5,000 - $50,000 | > $50,000 |
| Skill Needed | Script Kiddie | Experienced Dev | Penetration Tester | Nation-State APT |
| Equipment | Standard Laptop | Commercial Tools | Specialized Hardware | Zero-Day Research Lab |
