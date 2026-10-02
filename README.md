# 🚀 AI Skills Booster

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Skills Status](https://img.shields.io/badge/skills-catalog-blue.svg)](SKILLS.md)
[![Validation](https://img.shields.io/badge/validation-passing-brightgreen.svg)](#validation)
[![Taxonomy](https://img.shields.io/badge/taxonomy-3--level-purple.svg)](docs/TAXONOMY.md)

**AI Skills Booster** is an autonomous, comprehensive, high-quality, open-source library of Agent Skills designed for modern AI coding agents.

It targets **2,400+ production-grade Agent Skills** expanding toward **5,000+**, providing standardized workflows, defensive guardrails, structured evaluation criteria, and automated discovery tools for software engineering, AI engineering, automation, cloud/DevOps, security, databases, testing, data science, and business workflows.

---

## 🎯 Tested Agent Compatibility

AI Skills Booster follows vendor-agnostic open agent standards and is directly compatible with:

- 🤖 **Google Antigravity** (`.gemini/` and custom skill dirs)
- 🟣 **Claude Code** (`.claude/skills/` and Claude plugins)
- 🟢 **OpenAI Codex** (`.codex/skills/`)
- ⚡ **Cursor** (`.cursor/skills/` & Rules)
- 🌊 **Windsurf** (`.windsurf/skills/` & Cascade)
- 💻 **OpenCode & CLI Agents**

---

## 🌟 Why AI Skills Booster?

Most prompt repositories and skill collections suffer from:
1. **Flat unorganized dumps**: Thousands of files thrown into a single directory without logical grouping.
2. **Generic placeholders**: Stubs like `react-helper` that contain no actionable workflows, edge cases, or failure handling.
3. **No validation or test gates**: Unverified scripts that execute destructive commands or fail silently.
4. **Poor discoverability**: Developers cannot find what they need.

**AI Skills Booster solves this with a factory-grade architecture:**
- **Strict 3-Level Taxonomy**: `domain` ➔ `category` ➔ `subcategory` ➔ `skill-name`
- **Rich Metadata**: Verified YAML frontmatter specifying complexity, maturity, tools, dependencies, and tags.
- **Deep Production Workflows**: Every skill includes explicit triggers, negative triggers, decision trees, acceptance criteria, and failure recovery.
- **Automated CLI & Search**: Search skills instantly by keyword, tech, tag, task, or role.
- **Defensive Security Standard**: Zero offensive attack tools; 100% focused on security auditing, detection, hardening, and defense.
- **Transparent Git History**: Every single skill is validated, indexed, committed, and pushed individually.

---

## 🧭 Navigation & Discovery

Find any skill within seconds using our multi-dimensional indexes:

| Browse Dimension | Documentation Link | Description |
|---|---|---|
| **Master Catalog** | [SKILLS.md](SKILLS.md) | Full tabular directory of every skill in the repository |
| **Category Map** | [docs/CATEGORIES.md](docs/CATEGORIES.md) | Human-friendly hierarchical map across domains |
| **Visual Taxonomy** | [docs/TAXONOMY.md](docs/TAXONOMY.md) | ASCII taxonomy tree showing domain-to-skill depth |
| **By Task Intent** | [docs/BY-TASK.md](docs/BY-TASK.md) | Grouped by user intent (Build, Debug, Review, Test, Optimize, Deploy, Secure) |
| **By Technology** | [docs/BY-TECHNOLOGY.md](docs/BY-TECHNOLOGY.md) | Grouped by stack (Python, TypeScript, PostgreSQL, Docker, React, K8s, etc.) |
| **By Role** | [docs/BY-ROLE.md](docs/BY-ROLE.md) | Curated for AI Engineers, DevOps, Security Engineers, Full Stack, QA |
| **Repository Stats** | [docs/STATISTICS.md](docs/STATISTICS.md) | Automated statistics on domains, complexity, maturity, scripts, and evals |
| **Provenance** | [docs/PROVENANCE.md](docs/PROVENANCE.md) | Attribution and lineage across open-source ecosystems |

---

## ⚡ CLI Search Engine

AI Skills Booster includes a standalone command-line search utility:

```bash
# Search by keyword
python scripts/search_skills.py postgres query

# Filter by domain or category
python scripts/search_skills.py --domain security
python scripts/search_skills.py --category code-review

# Filter by technology or tag
python scripts/search_skills.py --tech react
python scripts/search_skills.py --tag mcp

# Filter by complexity
python scripts/search_skills.py --complexity expert
```

---

## 📦 Starter Packs

Explore curated collections for immediate adoption in [packs/](packs/):

- 🧠 **[AI Engineer Pack](packs/ai-engineer.yml)**: RAG evaluation, agent memory, MCP scaffolds, tool reliability, prompt defense.
- 💻 **[Full Stack Developer Pack](packs/full-stack-developer.yml)**: React component architecture, API design, Postgres optimization, Playwright testing.
- 🛡️ **[Security Engineer Pack](packs/security-engineer.yml)**: PR security reviews, secret detection, supply chain defense, OWASP top 10.
- ⚙️ **[DevOps Engineer Pack](packs/devops-engineer.yml)**: Kubernetes debugging, CI/CD pipelines, container hardening, Terraform drift.

---

## 🛠️ The 3-Level Taxonomy

Every skill resides in an explicit hierarchy:

```text
skills/
├── ai-engineering/
│   ├── rag/
│   │   ├── evaluation/
│   │   │   └── rag-retrieval-evaluation/
│   │   │       ├── SKILL.md
│   │   │       └── evals/
│   │   └── chunking/
│   └── agents/
│       ├── memory/
│       │   └── agent-project-memory/
│       └── tools/
│
├── software-engineering/
│   ├── code-review/
│   │   ├── security/
│   │   └── architecture/
│   ├── debugging/
│   └── architecture/
│
├── security/
│   ├── code-review/
│   └── secret-management/
│
└── devops/
    ├── kubernetes/
    └── ci-cd/
```

---

## 🧪 Skill Quality & Anatomical Standard

Every `SKILL.md` implements a comprehensive architectural anatomy:

```yaml
---
name: github-pr-security-review
description: Use this skill when reviewing a GitHub pull request for security risks such as exposed secrets, unsafe dependencies, injection vulnerabilities, authentication flaws, authorization issues, dangerous file operations, or insecure CI/CD changes. It guides the agent through a structured security review and produces actionable findings with severity and remediation guidance.
domain: security
category: code-review
subcategory: github
tags:
  - github
  - security
  - code-review
  - devsecops
technologies:
  - GitHub
  - Git
complexity: advanced
maturity: stable
tools:
  - git
  - gh
---
```

### Sections Included in Each Skill:
1. **Overview**: Clear problem statement and agent capability.
2. **When to Use**: Specific scenarios, alerts, and triggers.
3. **When NOT to Use**: Boundary conditions and alternative skill routing.
4. **Inputs & Prerequisites**: Environment variables, file paths, credentials.
5. **Core Workflow**: Step-by-step procedural logic.
6. **Decision Points & Edge Cases**: Fallback paths and heuristic guidance.
7. **Validation & Acceptance Criteria**: Concrete verification gates.
8. **Failure Handling & Recovery**: Actionable triage for runtime anomalies.
9. **Expected Output & Artifacts**: Concrete deliverables.
10. **Related Skills**: Cross-links to related workflows.

---

## 🚦 Automated Validation

We maintain an automated verification pipeline:

```bash
# Validate frontmatter, structure, naming, and safety rules
python scripts/validate.py

# Detect exact, slug, and semantic duplicates
python scripts/detect_duplicates.py

# Generate and verify catalog consistency
python scripts/generate_catalog.py
```

---

## 🤝 Contributing

We welcome community contributions! Please review our [Contributing Guidelines](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md).

All proposals must follow the 3-level taxonomy and pass `python scripts/validate.py`.

---

## 📄 License

AI Skills Booster is open-source software licensed under the [MIT License](LICENSE).
