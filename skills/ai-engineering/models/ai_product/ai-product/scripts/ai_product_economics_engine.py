#!/usr/bin/env python3
"""
ai_product_economics_engine.py - Production AI Product Economics & SLA Management Engine

Features:
- Unit economics (COGS, revenue, gross margin) evaluation for AI SaaS products
- Per-user token quota allocation and spending caps
- Latency budget profiler & SLA compliance evaluation
- Schema contract validation and graceful degradation fallback
"""

import sys
import os
import json
import argparse
from typing import Dict, Any, List, Tuple


def calculate_product_economics(
    monthly_subscription_usd: float,
    daily_active_prompts: int,
    avg_prompt_tokens: int,
    avg_completion_tokens: int,
    cost_per_m_input_usd: float = 0.50,
    cost_per_m_output_usd: float = 1.50,
    target_gross_margin: float = 0.75
) -> Dict[str, Any]:
    """
    Computes monthly unit economics for an active user on an AI tier.
    """
    days_per_month = 30
    monthly_prompts = daily_active_prompts * days_per_month

    total_input_tokens = monthly_prompts * avg_prompt_tokens
    total_output_tokens = monthly_prompts * avg_completion_tokens
    total_tokens = total_input_tokens + total_output_tokens

    input_cost = (total_input_tokens / 1_000_000.0) * cost_per_m_input_usd
    output_cost = (total_output_tokens / 1_000_000.0) * cost_per_m_output_usd
    total_cogs = input_cost + output_cost

    gross_profit = monthly_subscription_usd - total_cogs
    margin_pct = (gross_profit / monthly_subscription_usd * 100.0) if monthly_subscription_usd > 0 else 0.0

    compliant = margin_pct >= (target_gross_margin * 100.0)

    return {
        "monthly_prompts": monthly_prompts,
        "total_tokens_consumed": total_tokens,
        "monthly_inference_cogs_usd": round(total_cogs, 4),
        "gross_profit_usd": round(gross_profit, 4),
        "gross_margin_pct": round(margin_pct, 2),
        "target_margin_pct": target_gross_margin * 100.0,
        "is_economically_viable": compliant
    }


def evaluate_latency_sla(
    ttft_ms: float,
    total_latency_ms: float,
    max_allowed_ttft_ms: float = 800.0,
    max_allowed_total_ms: float = 4000.0
) -> Dict[str, Any]:
    """
    Assesses Time-To-First-Token (TTFT) and Total Latency against product SLAs.
    """
    ttft_ok = ttft_ms <= max_allowed_ttft_ms
    total_ok = total_latency_ms <= max_allowed_total_ms

    return {
        "ttft_ms": ttft_ms,
        "total_latency_ms": total_latency_ms,
        "ttft_sla_passed": ttft_ok,
        "total_sla_passed": total_ok,
        "overall_sla_met": ttft_ok and total_ok
    }


def validate_contract_with_fallback(
    payload: Dict[str, Any],
    required_keys: List[str]
) -> Tuple[bool, Dict[str, Any]]:
    """
    Validates payload against required schema keys.
    If missing keys, injects deterministic defaults and flags fallback.
    """
    missing = [k for k in required_keys if k not in payload or payload[k] is None]
    if not missing:
        return True, payload

    repaired = dict(payload)
    for m in missing:
        repaired[m] = "DEFAULT_UNAVAILABLE"
    repaired["_fallback_applied"] = True
    repaired["_missing_keys"] = missing
    return False, repaired


def run_unit_tests():
    print("=" * 60)
    print("Running AI Product Economics & SLA Verification Suite")
    print("=" * 60)

    # Test 1: Economics of a profitable user tier ($20/mo subscription)
    econ_pro = calculate_product_economics(
        monthly_subscription_usd=20.0,
        daily_active_prompts=15,
        avg_prompt_tokens=800,
        avg_completion_tokens=250,
        cost_per_m_input_usd=0.15,
        cost_per_m_output_usd=0.60,
        target_gross_margin=0.75
    )
    print(f"[*] Pro Tier Economics: COGS=${econ_pro['monthly_inference_cogs_usd']}, Margin={econ_pro['gross_margin_pct']}%")
    assert econ_pro["is_economically_viable"] is True, "Pro tier must meet 75% margin target"

    # Test 2: Economics of an unprofitable runaway user tier ($5/mo with frontier models)
    econ_unviable = calculate_product_economics(
        monthly_subscription_usd=5.0,
        daily_active_prompts=50,
        avg_prompt_tokens=2000,
        avg_completion_tokens=1000,
        cost_per_m_input_usd=3.00,
        cost_per_m_output_usd=15.00,
        target_gross_margin=0.75
    )
    print(f"[*] Uncapped Tier Economics: COGS=${econ_unviable['monthly_inference_cogs_usd']}, Margin={econ_unviable['gross_margin_pct']}%")
    assert econ_unviable["is_economically_viable"] is False, "Overconsuming tier must fail viability gate"

    # Test 3: Latency SLA evaluation
    sla_good = evaluate_latency_sla(ttft_ms=450.0, total_latency_ms=2100.0)
    assert sla_good["overall_sla_met"] is True, "Fast latency should pass SLA"

    sla_slow = evaluate_latency_sla(ttft_ms=1200.0, total_latency_ms=5500.0)
    assert sla_slow["overall_sla_met"] is False, "Slow latency must fail SLA"
    print("[*] Latency SLA Evaluation: OK")

    # Test 4: Schema Contract Fallback
    test_data = {"summary": "Great feature", "confidence": 0.95}
    valid, res = validate_contract_with_fallback(test_data, ["summary", "confidence", "category"])
    assert valid is False and res["_fallback_applied"] is True, "Expected fallback repair"
    assert res["category"] == "DEFAULT_UNAVAILABLE", "Default fallback key failed"
    print("[*] Schema Contract Fallback: OK")

    print("\n[SUCCESS] AI Product Economics Engine verified cleanly.")


def main():
    parser = argparse.ArgumentParser(description="AI Product Economics & SLA Engine")
    parser.add_argument("--test-all", action="store_true", help="Run full test suite")
    parser.add_argument("--calc-margin", action="store_true", help="Calculate margin for parameters")
    parser.add_argument("--sub-price", type=float, default=20.0, help="Subscription price USD")
    parser.add_argument("--daily-prompts", type=int, default=20, help="Daily prompts per user")

    args = parser.parse_args()

    if args.calc_margin:
        res = calculate_product_economics(
            monthly_subscription_usd=args.sub_price,
            daily_active_prompts=args.daily_prompts,
            avg_prompt_tokens=1000,
            avg_completion_tokens=300
        )
        print(json.dumps(res, indent=2))
        return

    run_unit_tests()


if __name__ == "__main__":
    main()
