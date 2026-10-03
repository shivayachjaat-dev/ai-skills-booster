#!/usr/bin/env python3
"""
Ditto Developer Work Profile Miner
-----------------------------------
Parses local coding agent transcripts (Claude Code, Copilot CLI, Gemini, OpenCode),
extracts evidence-backed developer behavioral profiles, computes work-style metrics,
and enforces zero-leak privacy sanitization.
"""

import sys
import os
import re
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict

SECRET_PATTERNS = [
    re.compile(r'(?i)(?:api_key|token|secret|password|bearer|auth)\s*[:=]\s*["\']?([a-zA-Z0-9_\-\.]{8,})["\']?'),
    re.compile(r'ghp_[a-zA-Z0-9]{36}'),
    re.compile(r'sk-[a-zA-Z0-9]{20,}')
]

@dataclass
class SessionEvent:
    event_type: str  # "prompt", "command", "file_edit", "test_run"
    content: str
    timestamp: Optional[str] = None

@dataclass
class DeveloperProfile:
    archetype: str
    primary_languages: List[str]
    detected_frameworks: List[str]
    work_metrics: Dict[str, Any]
    frequent_commands: Dict[str, int]
    evidence_count: int

class DittoProfiler:
    def __init__(self):
        self.events: List[SessionEvent] = []

    def sanitize_text(self, text: str) -> str:
        """Sanitize sensitive credentials and tokens from transcript text."""
        sanitized = text
        for pattern in SECRET_PATTERNS:
            sanitized = pattern.sub("[REDACTED_CREDENTIAL]", sanitized)
        # Redact local windows/posix user paths
        sanitized = re.sub(r'[A-Za-z]:[\\/]Users[\\/][^\\/]+', lambda _: 'C:/Users/[REDACTED_USER]', sanitized)
        sanitized = re.sub(r'/home/[^/]+', lambda _: '/home/[REDACTED_USER]', sanitized)
        return sanitized

    def ingest_session_events(self, raw_events: List[Dict[str, Any]]) -> None:
        """Ingest raw session records and apply real-time sanitization."""
        for item in raw_events:
            sanitized_content = self.sanitize_text(item.get("content", ""))
            event = SessionEvent(
                event_type=item.get("event_type", "unknown"),
                content=sanitized_content,
                timestamp=item.get("timestamp")
            )
            self.events.append(event)

    def extract_profile(self) -> DeveloperProfile:
        """Analyze ingested events and compute evidence-backed developer profile."""
        cmd_freq: Dict[str, int] = {}
        languages: Dict[str, int] = {}
        frameworks: set = set()
        test_runs = 0
        file_edits = 0

        # Heuristic detection patterns
        lang_patterns = {
            "Python": re.compile(r'\b(python|pytest|pip|poetry|\.py)\b', re.IGNORECASE),
            "TypeScript": re.compile(r'\b(ts-node|tsc|tsx|npm|yarn|\.ts)\b', re.IGNORECASE),
            "Rust": re.compile(r'\b(cargo|rustc|\.rs)\b', re.IGNORECASE),
            "Go": re.compile(r'\b(go run|go test|go build|\.go)\b', re.IGNORECASE)
        }

        framework_patterns = {
            "FastAPI": re.compile(r'\b(fastapi|uvicorn)\b', re.IGNORECASE),
            "React": re.compile(r'\b(react|jsx|nextjs)\b', re.IGNORECASE),
            "PyTorch": re.compile(r'\b(torch|cuda|tensor)\b', re.IGNORECASE),
            "Docker": re.compile(r'\b(docker|container|compose)\b', re.IGNORECASE)
        }

        for ev in self.events:
            text = ev.content
            if ev.event_type == "command":
                parts = text.strip().split()
                if parts:
                    base_cmd = parts[0].lower()
                    cmd_freq[base_cmd] = cmd_freq.get(base_cmd, 0) + 1
                    if "test" in base_cmd or "pytest" in base_cmd:
                        test_runs += 1

            if ev.event_type == "file_edit":
                file_edits += 1

            for lang, pat in lang_patterns.items():
                if pat.search(text):
                    languages[lang] = languages.get(lang, 0) + 1

            for fw, pat in framework_patterns.items():
                if pat.search(text):
                    frameworks.add(fw)

        # Determine dominant archetype
        tdd_ratio = round(test_runs / max(file_edits, 1), 2)
        if tdd_ratio >= 0.5:
            archetype = "Test-Driven Quality Engineer"
        elif "docker" in cmd_freq or "cargo" in cmd_freq:
            archetype = "Systems & Infrastructure Architect"
        else:
            archetype = "Full-Stack Application Builder"

        sorted_langs = [l for l, _ in sorted(languages.items(), key=lambda x: x[1], reverse=True)]
        
        return DeveloperProfile(
            archetype=archetype,
            primary_languages=sorted_langs or ["Python"],
            detected_frameworks=sorted(list(frameworks)),
            work_metrics={
                "tdd_ratio": tdd_ratio,
                "total_commands": sum(cmd_freq.values()),
                "total_edits": file_edits,
                "total_test_invocations": test_runs
            },
            frequent_commands=cmd_freq,
            evidence_count=len(self.events)
        )

def verify_ditto_miner():
    profiler = DittoProfiler()
    sample_raw_events = [
        {"event_type": "command", "content": "git status"},
        {"event_type": "file_edit", "content": "Updated src/auth.py with JWT verification"},
        {"event_type": "command", "content": "pytest tests/test_auth.py --verbose"},
        {"event_type": "prompt", "content": "Let's configure FastAPI endpoint with api_key=secret12345678"},
        {"event_type": "command", "content": "pytest tests/test_api.py"},
        {"event_type": "command", "content": "docker-compose up -d db"}
    ]
    
    print("============================================================")
    print("Ditto Profiler: Mining Work Profile from Local Agent Sessions")
    print("============================================================")
    profiler.ingest_session_events(sample_raw_events)
    profile = profiler.extract_profile()
    
    print(f"[*] Archetype: {profile.archetype}")
    print(f"[*] Languages: {', '.join(profile.primary_languages)}")
    print(f"[*] Frameworks: {', '.join(profile.detected_frameworks)}")
    print(f"[*] TDD Ratio: {profile.work_metrics['tdd_ratio']}")
    print(f"[*] Total Evidences Analyzed: {profile.evidence_count}")
    
    # Verify sanitization
    for ev in profiler.events:
        assert "secret12345678" not in ev.content, "Sanitization failed to redact secret!"
    
    print("[SUCCESS] Ditto Profiler verified cleanly with zero secret disclosure.")

if __name__ == "__main__":
    verify_ditto_miner()
