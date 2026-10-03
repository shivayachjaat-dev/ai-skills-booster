#!/usr/bin/env python3
"""
terminal_multiplexer_manager.py - Production Terminal Multiplexer & Agent Topology Manager

Features:
- Prefixed reference syntax validation (workspace:N, pane:N, surface:N)
- ANSI terminal escape sequence stripping for log parsing
- Hierarchical multiplexer topology data structures
- Screen capture buffer analyzer
"""

import sys
import os
import re
import argparse
from typing import Dict, Any, List, Optional, Tuple

REF_PATTERN = re.compile(r"^(workspace|pane|surface):([a-zA-Z0-9_\-]+)$")
ANSI_PATTERN = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def parse_and_validate_ref(raw_ref: str, expected_type: Optional[str] = None) -> Tuple[str, str]:
    """
    Validates prefixed reference format.
    Raises ValueError on bare numbers or mismatched types.
    """
    clean = raw_ref.strip()
    match = REF_PATTERN.match(clean)
    if not match:
        raise ValueError(
            f"Invalid reference '{raw_ref}'. Must be formatted as 'type:id' (e.g. 'surface:10'). "
            "Bare numbers are prohibited to prevent index collisions."
        )

    ref_type, ref_id = match.groups()
    if expected_type and ref_type != expected_type:
        raise ValueError(f"Type mismatch: Expected '{expected_type}', got '{ref_type}'")

    return ref_type, ref_id


def sanitize_screen_buffer(raw_screen: str) -> str:
    """
    Strips ANSI color codes, cursor positioning, and escape sequences.
    """
    return ANSI_PATTERN.sub("", raw_screen)


class MultiplexerTopology:
    def __init__(self):
        # workspace_id -> list of panes
        self.workspaces: Dict[str, Dict[str, Any]] = {}

    def create_workspace(self, name: str, cwd: str) -> str:
        ws_id = f"workspace:{len(self.workspaces) + 1}"
        self.workspaces[ws_id] = {
            "id": ws_id,
            "name": name,
            "cwd": cwd,
            "panes": {}
        }
        return ws_id

    def add_pane(self, workspace_id: str, direction: str = "right") -> str:
        if workspace_id not in self.workspaces:
            raise KeyError(f"Workspace {workspace_id} not found")
        
        ws = self.workspaces[workspace_id]
        pane_id = f"pane:{len(ws['panes']) + 1}"
        surface_id = f"surface:{len(ws['panes']) + 1}"
        
        ws["panes"][pane_id] = {
            "id": pane_id,
            "direction": direction,
            "surfaces": [surface_id]
        }
        return pane_id

    def list_surfaces(self, workspace_id: str) -> List[str]:
        if workspace_id not in self.workspaces:
            return []
        surfaces = []
        for p in self.workspaces[workspace_id]["panes"].values():
            surfaces.extend(p["surfaces"])
        return surfaces


def run_unit_tests():
    print("=" * 60)
    print("Running Terminal Multiplexer Manager Verification")
    print("=" * 60)

    # Test 1: Reference syntax validation
    t1, id1 = parse_and_validate_ref("surface:42", "surface")
    assert t1 == "surface" and id1 == "42", "Ref validation failed"
    print(f"[*] Validated Prefixed Ref: {t1}:{id1}")

    # Test 2: Bare integer rejection
    try:
        parse_and_validate_ref("42", "surface")
        assert False, "Bare number must be rejected"
    except ValueError as e:
        print(f"[*] Rejected Bare Number as expected: {e}")

    # Test 3: ANSI escape sequence stripping
    colored_text = "\x1b[31m[ERROR]\x1b[0m \x1b[1mProcess failed with code 1\x1b[0m"
    clean_text = sanitize_screen_buffer(colored_text)
    print(f"[*] ANSI Sanitization: '{clean_text}'")
    assert clean_text == "[ERROR] Process failed with code 1", "ANSI stripping mismatch"

    # Test 4: Topology creation
    topo = MultiplexerTopology()
    ws = topo.create_workspace("auth-feature", "/repos/auth")
    p1 = topo.add_pane(ws, "right")
    p2 = topo.add_pane(ws, "down")
    surfaces = topo.list_surfaces(ws)
    print(f"[*] Workspace {ws} contains panes: {p1}, {p2} with surfaces: {surfaces}")
    assert len(surfaces) == 2, "Topology surface tracking failed"

    print("\n[SUCCESS] Terminal Multiplexer Manager verified cleanly.")


def main():
    parser = argparse.ArgumentParser(description="Terminal Multiplexer Manager")
    parser.add_argument("--test-all", action="store_true", help="Run self-tests")
    args = parser.parse_args()

    run_unit_tests()


if __name__ == "__main__":
    main()
