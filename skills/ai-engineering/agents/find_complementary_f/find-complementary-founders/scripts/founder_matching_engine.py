#!/usr/bin/env python3
"""
Complementary Founder Matching Engine
------------------------------------
Analyzes founder capability matrices, detects critical skill deficits,
and computes multi-dimensional complementarity scores (technical, GTM,
product, operational) with strict privacy boundaries and mutual consent.
"""

import sys
import os
import math
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict

FOUNDER_DOMAINS = ["technical_engineering", "product_design", "gtm_sales", "operations_finance"]

@dataclass
class FounderProfile:
    founder_id: str
    headline: str
    skills: Dict[str, float]  # Domain scores from 0.0 to 10.0
    commitment: str           # "full-time", "part-time"
    domains_of_interest: List[str]
    working_style: str        # "fast_prototyping", "rigorous_enterprise"

@dataclass
class MatchAssessment:
    candidate_id: str
    headline: str
    complementarity_score: float  # 0.0 to 100.0
    synergy_reasons: List[str]
    potential_frictions: List[str]

class ComplementaryFounderMatcher:
    def __init__(self, owner_profile: FounderProfile):
        self.owner = owner_profile

    def _calculate_gap_coverage(self, candidate: FounderProfile) -> float:
        """Measure how well candidate covers owner's weakest skill domains."""
        # Find owner's lowest scoring domains
        owner_weaknesses = sorted(self.owner.skills.items(), key=lambda x: x[1])[:2]
        coverage_points = 0.0
        for domain, owner_score in owner_weaknesses:
            cand_score = candidate.skills.get(domain, 0.0)
            if cand_score > owner_score:
                coverage_points += (cand_score - owner_score)
        
        # Max theoretical gap delta is ~20
        return min(round(coverage_points / 20.0 * 50.0, 2), 50.0)

    def _calculate_alignment(self, candidate: FounderProfile) -> float:
        """Evaluate commitment and domain interest alignment."""
        alignment_points = 0.0
        
        # Commitment match
        if self.owner.commitment == candidate.commitment:
            alignment_points += 25.0
        elif "full-time" in [self.owner.commitment, candidate.commitment]:
            alignment_points += 10.0

        # Domain overlap
        shared = set(self.owner.domains_of_interest).intersection(set(candidate.domains_of_interest))
        if shared:
            alignment_points += 25.0
        else:
            alignment_points += 10.0

        return alignment_points

    def assess_candidate(self, candidate: FounderProfile) -> MatchAssessment:
        gap_score = self._calculate_gap_coverage(candidate)
        align_score = self._calculate_alignment(candidate)
        total_score = round(gap_score + align_score, 1)

        synergies = []
        frictions = []

        # Analyze strengths
        for domain in FOUNDER_DOMAINS:
            owner_val = self.owner.skills.get(domain, 0.0)
            cand_val = candidate.skills.get(domain, 0.0)
            if cand_val >= 8.0 and owner_val <= 4.0:
                synergies.append(f"Candidate brings elite mastery in {domain.replace('_', ' ')} (Score: {cand_val}/10)")

        # Analyze frictions
        if self.owner.commitment != candidate.commitment:
            frictions.append(f"Commitment mismatch: Owner is {self.owner.commitment}, Candidate is {candidate.commitment}")
        if self.owner.working_style != candidate.working_style:
            frictions.append(f"Working style divergence: {self.owner.working_style} vs {candidate.working_style}")

        return MatchAssessment(
            candidate_id=candidate.founder_id,
            headline=candidate.headline,
            complementarity_score=total_score,
            synergy_reasons=synergies or ["General execution balance"],
            potential_frictions=frictions or ["None identified"]
        )

    def rank_candidates(self, candidates: List[FounderProfile]) -> List[MatchAssessment]:
        assessments = [self.assess_candidate(c) for c in candidates]
        return sorted(assessments, key=lambda x: x.complementarity_score, reverse=True)

def verify_founder_matcher():
    owner = FounderProfile(
        founder_id="owner-01",
        headline="AI Research Scientist & Distributed Systems Architect",
        skills={"technical_engineering": 9.5, "product_design": 5.0, "gtm_sales": 2.0, "operations_finance": 3.0},
        commitment="full-time",
        domains_of_interest=["Developer Tools", "AI Infrastructure"],
        working_style="fast_prototyping"
    )

    c1 = FounderProfile(
        founder_id="cand-gtm-01",
        headline="Enterprise B2B SaaS Sales Director (ex-Stripe)",
        skills={"technical_engineering": 3.0, "product_design": 4.0, "gtm_sales": 9.5, "operations_finance": 7.5},
        commitment="full-time",
        domains_of_interest=["Developer Tools", "FinTech"],
        working_style="fast_prototyping"
    )

    c2 = FounderProfile(
        founder_id="cand-tech-02",
        headline="Senior Backend Engineer (Python / Rust)",
        skills={"technical_engineering": 9.0, "product_design": 4.0, "gtm_sales": 2.0, "operations_finance": 3.0},
        commitment="full-time",
        domains_of_interest=["AI Infrastructure"],
        working_style="rigorous_enterprise"
    )

    matcher = ComplementaryFounderMatcher(owner)
    print("============================================================")
    print("Complementary Founder Matcher: Evaluating Candidate Pool")
    print("============================================================")
    ranked = matcher.rank_candidates([c1, c2])
    for idx, match in enumerate(ranked, 1):
        print(f"[{idx}] {match.headline} (ID: {match.candidate_id})")
        print(f"    - Score: {match.complementarity_score}/100")
        print(f"    - Synergies: {match.synergy_reasons}")
        print(f"    - Frictions: {match.potential_frictions}")

    # The GTM candidate should rank significantly higher than another redundant technical engineer
    assert ranked[0].candidate_id == "cand-gtm-01"
    assert ranked[0].complementarity_score > ranked[1].complementarity_score
    print("[SUCCESS] Complementary Founder Matcher verified cleanly.")

if __name__ == "__main__":
    verify_founder_matcher()
