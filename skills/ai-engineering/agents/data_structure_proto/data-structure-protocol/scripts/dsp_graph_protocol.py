#!/usr/bin/env python3
"""
dsp_graph_protocol.py - Production Data Structure Protocol (DSP) Codebase Graph Engine

Features:
- Deterministic entity UID generation (obj-<8hex>, func-<8hex>)
- Dependency edge tracking with explicit connection rationales
- Reverse dependency index builder
- Refactoring blast-radius & impact analyzer (transitive dependent traversal)
"""

import sys
import os
import hashlib
import json
import argparse
from typing import Dict, Any, List, Set, Tuple


def generate_entity_uid(kind: str, namespace: str, name: str) -> str:
    """
    Computes deterministic 8-hex UID for a codebase entity.
    kind: 'obj' or 'func'
    """
    if kind not in ("obj", "func"):
        raise ValueError("Entity kind must be 'obj' or 'func'")
    seed = f"{namespace}:{name}".encode("utf-8")
    hex_digest = hashlib.sha256(seed).hexdigest()[:8]
    return f"{kind}-{hex_digest}"


class DSPGraph:
    def __init__(self):
        # uid -> metadata dict
        self.entities: Dict[str, Dict[str, Any]] = {}
        # target_uid -> list of { source_uid, reason }
        self.reverse_index: Dict[str, List[Dict[str, str]]] = {}

    def register_entity(self, uid: str, name: str, file_path: str, exports: List[str] = None) -> None:
        self.entities[uid] = {
            "uid": uid,
            "name": name,
            "file_path": file_path,
            "exports": exports or [],
            "imports": []
        }

    def record_dependency(self, source_uid: str, target_uid: str, reason: str) -> None:
        if source_uid in self.entities:
            self.entities[source_uid]["imports"].append({
                "target_uid": target_uid,
                "reason": reason
            })
            
        if target_uid not in self.reverse_index:
            self.reverse_index[target_uid] = []
        self.reverse_index[target_uid].append({
            "source_uid": source_uid,
            "reason": reason
        })

    def analyze_blast_radius(self, target_uid: str) -> List[Dict[str, str]]:
        """
        Traverses downstream dependencies to compute all entities impacted by mutating target_uid.
        """
        impacted = []
        queue = [target_uid]
        visited = set()

        while queue:
            curr = queue.pop(0)
            if curr in visited:
                continue
            visited.add(curr)

            dependents = self.reverse_index.get(curr, [])
            for dep in dependents:
                src = dep["source_uid"]
                impacted.append({
                    "entity_uid": src,
                    "entity_name": self.entities.get(src, {}).get("name", "unknown"),
                    "file_path": self.entities.get(src, {}).get("file_path", "unknown"),
                    "breakage_reason": dep["reason"]
                })
                queue.append(src)

        return impacted


def run_unit_tests():
    print("=" * 60)
    print("Running Data Structure Protocol (DSP) Graph Engine Verification")
    print("=" * 60)

    # Test 1: UID generation
    uid_db = generate_entity_uid("obj", "src.storage", "DatabasePool")
    uid_auth = generate_entity_uid("func", "src.auth", "verify_password")
    print(f"[*] Generated UIDs: DatabasePool={uid_db}, verify_password={uid_auth}")
    assert uid_db.startswith("obj-") and len(uid_db) == 12, "Object UID formatting failed"
    assert uid_auth.startswith("func-") and len(uid_auth) == 13, "Function UID formatting failed"

    # Test 2: Graph construction & dependency recording
    graph = DSPGraph()
    graph.register_entity(uid_db, "DatabasePool", "src/storage/db.py")
    
    uid_user_svc = generate_entity_uid("obj", "src.services", "UserService")
    graph.register_entity(uid_user_svc, "UserService", "src/services/user.py")
    
    uid_api_route = generate_entity_uid("obj", "src.routes", "LoginRoute")
    graph.register_entity(uid_api_route, "LoginRoute", "src/routes/login.py")

    # UserService imports DatabasePool
    graph.record_dependency(uid_user_svc, uid_db, "Queries user credentials from database pool")
    # LoginRoute imports UserService
    graph.record_dependency(uid_api_route, uid_user_svc, "Validates credentials during HTTP login")

    # Test 3: Blast radius evaluation
    # If DatabasePool changes, both UserService and LoginRoute should be in blast radius
    blast = graph.analyze_blast_radius(uid_db)
    print(f"[*] Blast Radius for DatabasePool ({uid_db}): {len(blast)} impacted entities")
    for b in blast:
        print(f"    -> Impacted: {b['entity_name']} [{b['entity_uid']}] | Reason: {b['breakage_reason']}")
        
    assert len(blast) == 2, f"Expected 2 impacted entities, got {len(blast)}"
    impacted_names = [b["entity_name"] for b in blast]
    assert "UserService" in impacted_names and "LoginRoute" in impacted_names

    print("\n[SUCCESS] Data Structure Protocol Graph Engine verified cleanly.")


def main():
    parser = argparse.ArgumentParser(description="Data Structure Protocol Graph Engine")
    parser.add_argument("--test-all", action="store_true", help="Run self-tests")
    args = parser.parse_args()

    run_unit_tests()


if __name__ == "__main__":
    main()
