#!/usr/bin/env python3
"""
Architecture Decision Record (ADR) & Documentation Engine
---------------------------------------------------------
Automates the lifecycle, validation, indexing, and superseding of Architecture Decision
Records (ADRs) following MADR 3.0 standards for human engineers and autonomous agents.
"""

import sys
import os
import re
import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict

VALID_STATUSES = ["Proposed", "Accepted", "Rejected", "Deprecated", "Superseded"]

@dataclass
class ADR:
    number: int
    title: str
    status: str
    date: str
    deciders: List[str]
    context: str
    decision: str
    consequences: Dict[str, List[str]]
    supersedes: Optional[int] = None
    superseded_by: Optional[int] = None

class ADREngine:
    def __init__(self, doc_root: str):
        self.doc_root = os.path.abspath(doc_root)
        self.adrs_dir = os.path.join(self.doc_root, "adrs")

    def init_repository(self) -> None:
        """Ensure adrs directory exists."""
        os.makedirs(self.adrs_dir, exist_ok=True)

    def _slugify(self, title: str) -> str:
        slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title).strip().lower()
        return re.sub(r'[\s-]+', '-', slug)

    def get_next_number(self) -> int:
        """Scan directory for existing ADR numbers and return the next integer."""
        if not os.path.exists(self.adrs_dir):
            return 1
        existing = []
        for fname in os.listdir(self.adrs_dir):
            match = re.match(r'^(\d{4})-.*\.md$', fname)
            if match:
                existing.append(int(match.group(1)))
        return max(existing, default=0) + 1

    def create_adr(
        self,
        title: str,
        deciders: List[str],
        context: str,
        decision: str,
        consequences: Dict[str, List[str]],
        status: str = "Accepted",
        supersedes: Optional[int] = None
    ) -> str:
        """Create a new MADR formatted decision record and return its file path."""
        self.init_repository()
        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid status: {status}. Must be one of {VALID_STATUSES}")

        number = self.get_next_number()
        today = datetime.date.today().isoformat()
        slug = self._slugify(title)
        filename = f"{number:04d}-{slug}.md"
        filepath = os.path.join(self.adrs_dir, filename)

        positives = "\n".join(f"- Positive: {p}" for p in consequences.get("positive", []))
        negatives = "\n".join(f"- Negative: {n}" for n in consequences.get("negative", []))
        neutral = "\n".join(f"- Neutral: {x}" for x in consequences.get("neutral", []))

        content = f"""# {number:04d}. {title}

Date: {today}
Status: {status}
Deciders: {', '.join(deciders)}
{"Supersedes: ADR-" + f"{supersedes:04d}" if supersedes else ""}

## Context and Problem Statement
{context.strip()}

## Decision Outcome
{decision.strip()}

## Consequences
### Positive Consequences
{positives if positives else "- None noted."}

### Negative Consequences
{negatives if negatives else "- None noted."}

### Neutral Consequences
{neutral if neutral else "- None noted."}
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        if supersedes:
            self._mark_superseded(supersedes, number)

        self.update_index()
        return filepath

    def _mark_superseded(self, target_num: int, superseding_num: int) -> None:
        """Mark an earlier ADR as superseded by target number."""
        for fname in os.listdir(self.adrs_dir):
            if fname.startswith(f"{target_num:04d}-"):
                target_path = os.path.join(self.adrs_dir, fname)
                with open(target_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                content = re.sub(r'Status:\s*Accepted', f'Status: Superseded by ADR-{superseding_num:04d}', content)
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write(content)
                break

    def update_index(self) -> str:
        """Regenerate README index of all ADRs."""
        self.init_repository()
        records = []
        for fname in sorted(os.listdir(self.adrs_dir)):
            if fname.endswith(".md") and fname != "README.md":
                match = re.match(r'^(\d{4})-(.*)\.md$', fname)
                if match:
                    num = match.group(1)
                    title = match.group(2).replace("-", " ").title()
                    fpath = os.path.join(self.adrs_dir, fname)
                    with open(fpath, "r", encoding="utf-8") as f:
                        text = f.read()
                    status_match = re.search(r'Status:\s*(.+)', text)
                    status = status_match.group(1).strip() if status_match else "Unknown"
                    records.append({"num": num, "title": title, "file": fname, "status": status})

        index_path = os.path.join(self.adrs_dir, "README.md")
        lines = [
            "# Architecture Decision Records (ADRs)",
            "",
            "This directory contains all architectural and systemic decisions governing the codebase.",
            "",
            "| ID | Title | Status | Link |",
            "| :--- | :--- | :--- | :--- |"
        ]
        for r in records:
            lines.append(f"| {r['num']} | {r['title']} | `{r['status']}` | [{r['file']}](./{r['file']}) |")

        with open(index_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

        return index_path

def verify_adr_engine():
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = ADREngine(tmpdir)
        print("============================================================")
        print("ADR Engine: Verifying Decision Record Management")
        print("============================================================")
        
        # Create ADR 0001
        p1 = engine.create_adr(
            title="Adopt Asynchronous Message Broker",
            deciders=["Lead Architect", "Infrastructure Agent"],
            context="Synchronous REST calls between microservices caused latency spikes under load.",
            decision="Adopt RabbitMQ with dead-letter queue isolation for asynchronous event delivery.",
            consequences={
                "positive": ["Decouples order processing from email notifications", "Provides backpressure absorption"],
                "negative": ["Introduces broker cluster maintenance overhead"]
            }
        )
        print(f"[*] Created initial record: {os.path.basename(p1)}")
        
        # Create ADR 0002 superseding ADR 0001
        p2 = engine.create_adr(
            title="Migrate to Managed Cloud Event Stream",
            deciders=["Cloud Architect"],
            context="Self-hosted message broker requires significant maintenance during regional failovers.",
            decision="Migrate to fully managed event streaming service with IAM auth.",
            consequences={
                "positive": ["Eliminates patch maintenance", "Native cross-region replication"],
                "negative": ["Higher per-message egress cost"]
            },
            supersedes=1
        )
        print(f"[*] Created superseding record: {os.path.basename(p2)}")
        
        index_file = os.path.join(engine.adrs_dir, "README.md")
        with open(index_file, "r", encoding="utf-8") as f:
            index_content = f.read()
        
        assert "0001" in index_content
        assert "0002" in index_content
        assert "Superseded by ADR-0002" in index_content
        print("[SUCCESS] ADR & Documentation Engine verified cleanly.")

if __name__ == "__main__":
    verify_adr_engine()
