#!/usr/bin/env python3
"""
Folder-Specific Guidance Generator (CLAUDE.md & AGENTS.md)
----------------------------------------------------------
Detects subsystem technologies, build tools, and localized testing commands to generate
folder-scoped AGENTS.md and CLAUDE.md guidance files for autonomous coding agents.
"""

import sys
import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

@dataclass
class SubsystemContext:
    folder_path: str
    folder_name: str
    detected_language: str
    build_tool: str
    test_command: str
    lint_command: str
    key_invariants: List[str]

class FolderGuidanceGenerator:
    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)

    def probe_directory(self, target_dir: str) -> SubsystemContext:
        """Inspect directory contents to detect tech stack and appropriate commands."""
        abs_target = os.path.abspath(target_dir)
        fname = os.path.basename(abs_target)

        # Check markers
        if os.path.exists(os.path.join(abs_target, "package.json")):
            return SubsystemContext(
                folder_path=abs_target,
                folder_name=fname,
                detected_language="TypeScript / JavaScript",
                build_tool="npm / pnpm",
                test_command="npm test",
                lint_command="npm run lint",
                key_invariants=[
                    "Maintain strict TypeScript types; avoid 'any'.",
                    "Keep client-side and server-side components cleanly partitioned.",
                    "Verify all UI components render without console errors."
                ]
            )
        elif os.path.exists(os.path.join(abs_target, "Cargo.toml")):
            return SubsystemContext(
                folder_path=abs_target,
                folder_name=fname,
                detected_language="Rust",
                build_tool="cargo",
                test_command="cargo test",
                lint_command="cargo clippy -- -D warnings",
                key_invariants=[
                    "Zero unwrap() calls in production paths; use Result and Option propagation.",
                    "Enforce strict memory safety without unsafe blocks unless explicitly justified.",
                    "Ensure all public structs have comprehensive doc comments."
                ]
            )
        else:
            # Default to Python / General
            return SubsystemContext(
                folder_path=abs_target,
                folder_name=fname,
                detected_language="Python",
                build_tool="poetry / pip",
                test_command="pytest tests/",
                lint_command="ruff check .",
                key_invariants=[
                    "Adhere to PEP 8 conventions and type annotations.",
                    "All public API functions must include docstrings.",
                    "Mock external network I/O in local unit tests."
                ]
            )

    def generate_scoped_agents_md(self, target_dir: str, format_type: str = "AGENTS.md") -> str:
        """Generate a localized AGENTS.md or CLAUDE.md within target directory."""
        ctx = self.probe_directory(target_dir)
        filepath = os.path.join(ctx.folder_path, format_type)

        invariants_md = "\n".join(f"- {inv}" for inv in ctx.key_invariants)

        content = f"""# {format_type} — Scoped Guidance: {ctx.folder_name}

## Subsystem Overview
This directory governs the **{ctx.folder_name}** component of the repository.
- **Language / Runtime**: `{ctx.detected_language}`
- **Package / Build Tool**: `{ctx.build_tool}`

## Local Execution Commands
- **Run Tests**: `{ctx.test_command}`
- **Run Lint / Format**: `{ctx.lint_command}`

## Local Architecture Invariants
{invariants_md}

## Cross-Subsystem Boundaries
- Changes in this directory must **not** break root API contracts.
- Do not import internal private modules from sibling directories; use published public interfaces.
- Always run local tests (`{ctx.test_command}`) before committing changes to this folder.
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return filepath

def verify_folder_guidance():
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create mock frontend and backend subdirectories
        fe_dir = os.path.join(tmpdir, "frontend")
        be_dir = os.path.join(tmpdir, "backend")
        os.makedirs(fe_dir, exist_ok=True)
        os.makedirs(be_dir, exist_ok=True)

        with open(os.path.join(fe_dir, "package.json"), "w", encoding="utf-8") as f:
            f.write('{"name": "web-ui"}')

        with open(os.path.join(be_dir, "pyproject.toml"), "w", encoding="utf-8") as f:
            f.write('[tool.poetry]\nname = "api-service"')

        generator = FolderGuidanceGenerator(tmpdir)
        
        print("============================================================")
        print("Folder Guidance Generator: Generating Scoped Guidance Files")
        print("============================================================")
        fe_file = generator.generate_scoped_agents_md(fe_dir, "AGENTS.md")
        be_file = generator.generate_scoped_agents_md(be_dir, "CLAUDE.md")

        print(f"[*] Generated frontend guidance: {os.path.basename(fe_file)}")
        print(f"[*] Generated backend guidance: {os.path.basename(be_file)}")

        with open(fe_file, "r", encoding="utf-8") as f:
            fe_content = f.read()
        assert "npm test" in fe_content
        assert "TypeScript" in fe_content

        with open(be_file, "r", encoding="utf-8") as f:
            be_content = f.read()
        assert "pytest tests/" in be_content
        assert "Python" in be_content

        print("[SUCCESS] Folder-Specific Guidance Generator verified cleanly.")

if __name__ == "__main__":
    verify_folder_guidance()
