---
name: skill-creator
description: "Use this skill when designing, authoring, and structuring new Agent Skills for AI coding agents. It guides the agent through problem formulation, three-level taxonomy classification, frontmatter schema validation, step-by-step workflow authoring, edge case identification, and automated evaluation generation."
domain: meta
category: ecosystem
subcategory: creation
tags:
  - meta
  - skill-creation
  - agent-skills
  - authoring
  - taxonomy
technologies:
  - Python
  - Markdown
  - YAML
  - Git
complexity: advanced
maturity: stable
tools:
  - python
  - git
dependencies:
  - python >= 3.9
---
# Skill Creator

## Overview

A meta-skill that guides AI coding agents in designing, generating, and verifying new, high-quality Agent Skills. It guarantees that new skills conform to the strict 3-level taxonomy (`domain/category/subcategory/skill-name`), possess complete YAML frontmatter, provide deterministic workflows with explicit decision trees, and include verifiable acceptance criteria.

## When to Use

- Creating a new agent skill to automate a distinct engineering or operational task.
- Refactoring legacy or informal prompts into structured, reproducible Agent Skills.
- Packaging repetitive multi-step coding or operational procedures for agent reuse.
- Expanding the AI Skills Booster catalog into new domains or subdomains.

## When NOT to Use

- Simply answering a one-off user coding question without intending to persist a reusable skill.
- Modifying general system instructions or global personality prompts.

## Inputs & Prerequisites

- Target problem statement and workflow description.
- Target domain, category, and subcategory according to the repository taxonomy.
- List of tools (e.g. `git`, `docker`, `python`) and dependencies required by the workflow.

## Core Workflow

### 1. Problem Formulation & Scope Verification
1. Define the exact user problem the skill solves.
2. Confirm that the skill is not a generic stub or trivial duplicate of an existing skill.
3. Formulate the skill name in strict kebab-case describing the action (e.g. `postgres-query-performance-analysis`).

### 2. Taxonomy & Directory Assignment
Assign the skill to the appropriate 3-level hierarchy:
`skills/<domain>/<category>/<subcategory>/<skill-name>/`
Ensure the directory structure matches the frontmatter fields.

### 3. Frontmatter Construction
Populate complete YAML frontmatter:
- `name`: kebab-case skill identifier
- `description`: Crisp, specific summary answering what it does, when to use it, and what problem it solves.
- `domain`, `category`, `subcategory`
- `tags`: 3 to 8 searchable keywords
- `technologies`: List of relevant technologies
- `complexity`: `beginner`, `intermediate`, `advanced`, or `expert`
- `maturity`: `experimental`, `stable`, or `advanced`
- `tools` and `dependencies`

### 4. Authoring Standard Sections
Structure the markdown content with mandatory sections:
1. `## Overview`
2. `## When to Use`
3. `## When NOT to Use`
4. `## Inputs & Prerequisites`
5. `## Core Workflow` (with step-by-step procedural commands)
6. `## Decision Points & Edge Cases`
7. `## Validation & Acceptance Criteria`
8. `## Failure Handling & Recovery`
9. `## Expected Output & Artifacts`
10. `## Related Skills`

### 5. Automated Verification
Run repository validator:
```bash
python scripts/validate.py
python scripts/detect_duplicates.py
```

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Overlap with existing skill | Check `scripts/detect_duplicates.py`. If scope overlaps > 70%, specialize the new skill or merge improvements into the existing one. |
| Complex multi-step scripts needed | Place executable helper code in `scripts/` inside the skill directory rather than bloating `SKILL.md`. |
| Complex reference data | Place extensive manuals, specifications, or schema documentation in `references/`. |

## Validation & Acceptance Criteria

- [ ] Directory path matches `skills/<domain>/<category>/<subcategory>/<name>/SKILL.md`.
- [ ] Description is at least 40 characters and clearly states triggers and outcomes.
- [ ] Frontmatter contains valid tags, complexity, maturity, and tools.
- [ ] `python scripts/validate.py` passes with zero errors.

## Failure Handling & Recovery

- If validation reports missing fields or naming mismatches, adjust frontmatter or directory naming immediately before proceeding to git commit.

## Expected Output & Artifacts

- Fully compliant `SKILL.md` in the target directory.
- Optional `scripts/` or `evals/` supporting files.

## Related Skills

- `skill-reviewer`
- `skill-validator`
- `skill-evaluator`
