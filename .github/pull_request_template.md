## Description

Brief summary of the changes or the new skill added.

## Skill Checklist

If adding or updating a skill:
- [ ] Follows 3-level taxonomy (`skills/<domain>/<category>/<subcategory>/<skill-name>/SKILL.md`)
- [ ] Has valid YAML frontmatter (name, description, domain, category, subcategory, tags, technologies, complexity, maturity, tools, dependencies)
- [ ] Description answers: What does it do? When should the agent use it? What problem does it solve?
- [ ] Contains all required sections (Overview, When to Use, When NOT to Use, Inputs, Core Workflow, Decision Points, Validation, Failure Handling, Expected Output, Related Skills)
- [ ] Passes `python scripts/validate.py` with zero errors
- [ ] Passes `python scripts/detect_duplicates.py` with zero duplicates
- [ ] Updated catalog and indexes via `python scripts/generate_catalog.py`
