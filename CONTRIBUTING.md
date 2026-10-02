# Contributing to AI Skills Booster

Thank you for your interest in contributing to **AI Skills Booster**! Our mission is to build the premier, high-quality, open-source library of 2,400+ Agent Skills for AI coding agents.

## Core Principles

Every skill in this repository must solve a distinct, real-world engineering or workflow problem. We reject:
- Trivial variants (e.g. `react-basic`, `react-basic-v2`)
- Empty prompt files or generic "helpers"
- Unvalidated or unsafe execution instructions
- Skills missing actionable workflows, decision trees, or edge case handling

## Taxonomy Standard

Skills follow a strict three-level hierarchy:
```text
skills/
└── <domain>/
    └── <category>/
        └── <subcategory>/
            └── <skill-name>/
                ├── SKILL.md
                ├── references/   (optional)
                ├── scripts/      (optional)
                └── evals/        (optional)
```

## SKILL.md Specification

Every skill must have valid YAML frontmatter matching:

```yaml
---
name: skill-name-in-kebab-case
description: Use this skill when <specific trigger>. It guides the agent through <workflow> to solve <problem>, delivering <concrete output>.
domain: domain-name
category: category-name
subcategory: subcategory-name
tags:
  - tag1
  - tag2
  - tag3
technologies:
  - Tech1
  - Tech2
complexity: beginner | intermediate | advanced | expert
maturity: experimental | stable | advanced
tools:
  - tool1
dependencies:
  - dep1
---
```

### Required Sections in SKILL.md

1. `# <Skill Name>`
2. `## Overview` - Concrete description of the skill's capability.
3. `## When to Use` - Precise triggers and scenarios.
4. `## When NOT to Use` - Clear negative triggers / boundaries.
5. `## Inputs & Prerequisites` - Required environment, credentials, parameters.
6. `## Core Workflow` - Step-by-step instructions with decision logic.
7. `## Decision Points & Edge Cases` - Critical trade-offs, fallback paths.
8. `## Validation & Acceptance Criteria` - Verifiable test gates before completion.
9. `## Failure Handling & Recovery` - Explicit diagnosis and fix steps.
10. `## Expected Output & Artifacts` - Concrete deliverables produced.
11. `## Related Skills` - Graph links to complementary skills.

## Validation Before Submitting

Run the automated validation suite locally:

```bash
python scripts/validate.py
python scripts/detect_duplicates.py
```

All checks must pass with zero errors.

## Git Commit Standard

We follow Conventional Commits:
- `feat(skill): add <skill-name>` for new skills
- `fix(skill): update <skill-name>` for bug fixes or improvements
- `docs: update documentation`
- `build: update automation scripts`
