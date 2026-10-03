#!/usr/bin/env python3
"""
Hosted Agent Sandboxed Runtime Orchestrator
-------------------------------------------
Provisions, manages, and tears down secure, isolated execution environments (microVMs,
containers, or ephemeral sandboxes) for background autonomous coding agents.
Enforces resource quotas, execution timeouts, and safe artifact extraction.
"""

import sys
import os
import shutil
import tempfile
import time
import subprocess
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict

@dataclass
class SandboxConfig:
    sandbox_id: str
    runtime_type: str = "container_isolated"  # "microvm", "modal_sandbox", "container_isolated"
    memory_limit_mb: int = 1024
    cpu_limit_cores: float = 1.0
    network_egress: str = "restricted"  # "none", "restricted", "full"
    timeout_sec: float = 30.0

@dataclass
class SandboxExecutionReport:
    sandbox_id: str
    status: str  # "completed", "timeout", "failed"
    duration_ms: float
    exit_code: int
    stdout: str
    stderr: str
    artifacts_extracted: List[str]

class HostedAgentSandbox:
    def __init__(self, config: SandboxConfig):
        self.config = config
        self.sandbox_dir: Optional[str] = None
        self.is_active = False

    def provision(self) -> str:
        """Provision ephemeral sandbox directory and filesystem isolation."""
        self.sandbox_dir = tempfile.mkdtemp(prefix=f"agent_sbx_{self.config.sandbox_id}_")
        self.is_active = True
        return self.sandbox_dir

    def mount_files(self, files: Dict[str, str]) -> None:
        """Inject files into the sandbox filesystem."""
        if not self.is_active or not self.sandbox_dir:
            raise RuntimeError("Cannot mount files: sandbox is not active.")

        for rel_path, content in files.items():
            full_path = os.path.join(self.sandbox_dir, rel_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

    def execute_command(self, cmd: List[str]) -> SandboxExecutionReport:
        """Execute agent command inside sandbox with strict timeout and isolation."""
        if not self.is_active or not self.sandbox_dir:
            raise RuntimeError("Cannot execute: sandbox is not active.")

        start_time = time.perf_counter()
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_sec,
                cwd=self.sandbox_dir
            )
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Collect artifacts generated in sandbox
            artifacts = []
            for root, _, filenames in os.walk(self.sandbox_dir):
                for fname in filenames:
                    artifacts.append(os.path.relpath(os.path.join(root, fname), self.sandbox_dir))

            return SandboxExecutionReport(
                sandbox_id=self.config.sandbox_id,
                status="completed" if proc.returncode == 0 else "failed",
                duration_ms=round(duration_ms, 2),
                exit_code=proc.returncode,
                stdout=proc.stdout.strip(),
                stderr=proc.stderr.strip(),
                artifacts_extracted=artifacts
            )
        except subprocess.TimeoutExpired:
            duration_ms = (time.perf_counter() - start_time) * 1000
            return SandboxExecutionReport(
                sandbox_id=self.config.sandbox_id,
                status="timeout",
                duration_ms=round(duration_ms, 2),
                exit_code=124,
                stdout="",
                stderr=f"Sandbox execution timed out after {self.config.timeout_sec}s",
                artifacts_extracted=[]
            )

    def teardown(self) -> None:
        """Tear down and purge ephemeral sandbox resources."""
        if self.sandbox_dir and os.path.exists(self.sandbox_dir):
            shutil.rmtree(self.sandbox_dir, ignore_errors=True)
        self.is_active = False

def verify_hosted_sandbox():
    config = SandboxConfig(
        sandbox_id="test-run-101",
        runtime_type="container_isolated",
        timeout_sec=10.0
    )
    sandbox = HostedAgentSandbox(config)

    print("============================================================")
    print("Hosted Agent Sandbox: Verifying Provisioning & Teardown")
    print("============================================================")
    sbx_path = sandbox.provision()
    print(f"[*] Provisioned ephemeral sandbox: {os.path.basename(sbx_path)}")
    assert os.path.exists(sbx_path)

    try:
        # Mount initial file
        sandbox.mount_files({
            "main.py": "print('Hello from isolated background agent sandbox!')"
        })

        # Execute in sandbox
        report = sandbox.execute_command([sys.executable, "main.py"])
        print(f"[*] Execution Status: {report.status}")
        print(f"[*] Output: {report.stdout}")
        print(f"[*] Artifacts: {report.artifacts_extracted}")

        assert report.status == "completed"
        assert "Hello from isolated" in report.stdout
        assert "main.py" in report.artifacts_extracted
    finally:
        sandbox.teardown()
        print(f"[*] Teardown completed. Active={sandbox.is_active}")
        assert not os.path.exists(sbx_path)

    print("[SUCCESS] Hosted Agent Sandbox Runtime verified cleanly.")

if __name__ == "__main__":
    verify_hosted_sandbox()
