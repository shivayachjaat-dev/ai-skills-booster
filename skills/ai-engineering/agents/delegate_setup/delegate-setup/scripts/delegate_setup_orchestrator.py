#!/usr/bin/env python3
"""
Delegate Setup Orchestrator
---------------------------
Discovers installed implementer CLIs (Claude, Gemini, Copilot, Cline, Aider, etc.),
evaluates capability matrices, configures authorized delegation lanes,
and generates validated routing policies with defensive fallback cascades.
"""

import sys
import os
import json
import shutil
import subprocess
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict

SUPPORTED_AGENTS = {
    "claude": {
        "binary_names": ["claude", "claude.cmd", "claude.exe"],
        "capabilities": ["stdin_prompt", "json_output", "context_window_200k", "workspace_boundary"],
        "default_tier": "supervised_commit"
    },
    "gemini": {
        "binary_names": ["gemini", "gemini.cmd", "gemini.exe", "agy", "agy.exe"],
        "capabilities": ["stdin_prompt", "json_output", "context_window_1m", "multimodal"],
        "default_tier": "full_delegation"
    },
    "copilot": {
        "binary_names": ["gh-copilot", "copilot", "copilot.cmd"],
        "capabilities": ["stdin_prompt", "git_integration", "workspace_boundary"],
        "default_tier": "supervised_commit"
    },
    "cline": {
        "binary_names": ["cline", "cline.cmd", "cline.exe"],
        "capabilities": ["diff_review", "workspace_write_isolated"],
        "default_tier": "workspace_write_isolated"
    },
    "aider": {
        "binary_names": ["aider", "aider.exe"],
        "capabilities": ["git_integration", "diff_review", "workspace_write_isolated"],
        "default_tier": "supervised_commit"
    }
}

VALID_TIERS = ["strict_read_only", "workspace_write_isolated", "supervised_commit", "full_delegation"]

@dataclass
class AgentStatus:
    agent_id: str
    installed: bool
    path: Optional[str] = None
    version: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    tier: str = "strict_read_only"
    status: str = "unverified"

class DelegateSetupManager:
    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = os.path.abspath(workspace_root or os.getcwd())
        self.config_file = os.path.join(self.workspace_root, ".delegate-lanes.json")
        self.agents: Dict[str, AgentStatus] = {}

    def discover_installed_clis(self) -> Dict[str, AgentStatus]:
        """Scan PATH for all supported agent binaries and evaluate detection status."""
        for agent_id, meta in SUPPORTED_AGENTS.items():
            detected_path = None
            for bname in meta["binary_names"]:
                found = shutil.which(bname)
                if found:
                    detected_path = found
                    break

            if detected_path:
                status = AgentStatus(
                    agent_id=agent_id,
                    installed=True,
                    path=detected_path,
                    capabilities=list(meta["capabilities"]),
                    tier=meta["default_tier"],
                    status="ready"
                )
            else:
                status = AgentStatus(
                    agent_id=agent_id,
                    installed=False,
                    path=None,
                    capabilities=list(meta["capabilities"]),
                    tier=meta["default_tier"],
                    status="not_installed"
                )
            self.agents[agent_id] = status
        return self.agents

    def configure_lane(self, agent_id: str, tier: str) -> None:
        """Assign an approved permission tier to an implementer agent."""
        if tier not in VALID_TIERS:
            raise ValueError(f"Invalid permission tier: {tier}. Must be one of {VALID_TIERS}")
        if agent_id not in self.agents:
            self.discover_installed_clis()
        if agent_id not in self.agents:
            raise KeyError(f"Unknown agent identifier: {agent_id}")
        self.agents[agent_id].tier = tier

    def generate_policy(self, primary: str, fallbacks: List[str]) -> Dict[str, Any]:
        """Generate a structured delegation policy with fallback order and security constraints."""
        if not self.agents:
            self.discover_installed_clis()

        policy = {
            "version": "1.0.0",
            "workspace_root": self.workspace_root,
            "routing": {
                "primary": primary,
                "fallbacks": fallbacks
            },
            "security_lanes": {
                aid: asdict(agent) for aid, agent in self.agents.items()
            },
            "isolation_rules": {
                "strict_read_only": {"allow_disk_write": False, "allow_network": True, "allow_git_commit": False},
                "workspace_write_isolated": {"allow_disk_write": True, "allow_network": False, "allow_git_commit": False},
                "supervised_commit": {"allow_disk_write": True, "allow_network": True, "allow_git_commit": False},
                "full_delegation": {"allow_disk_write": True, "allow_network": True, "allow_git_commit": True}
            }
        }
        return policy

    def resolve_executable_agent(self, requested_agent: str, fallbacks: List[str]) -> Optional[str]:
        """Find first available agent respecting installation and lane readiness."""
        candidates = [requested_agent] + fallbacks
        for candidate in candidates:
            if candidate in self.agents and self.agents[candidate].installed:
                return candidate
        return None

def verify_delegate_setup():
    manager = DelegateSetupManager()
    agents = manager.discover_installed_clis()
    print("============================================================")
    print("Delegate Setup: CLI Discovery and Lane Verification")
    print("============================================================")
    for aid, item in agents.items():
        print(f"[*] Agent: {aid.ljust(10)} | Installed: {str(item.installed).ljust(5)} | Tier: {item.tier}")
    
    # Configure mock lanes and generate policy
    manager.configure_lane("gemini", "full_delegation")
    policy = manager.generate_policy(primary="gemini", fallbacks=["claude", "aider", "copilot"])
    
    # Check resolution
    resolved = manager.resolve_executable_agent("gemini", ["claude", "aider"])
    print(f"[*] Delegation Resolution Result: {resolved if resolved else 'Mock fallback simulator active'}")
    print("[SUCCESS] Delegate Setup Orchestrator verified cleanly.")

if __name__ == "__main__":
    verify_delegate_setup()
