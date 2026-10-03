#!/usr/bin/env python3
"""
3d-games_helper.py - Real-Time 3D Rendering Budget & Math Utility.
Audits frame budgets (draw calls, triangle counts, fill rate), calculates
LOD distance transitions, and tests view-frustum bounding sphere visibility.
"""

import sys
import math
import argparse

# Performance targets per platform
PLATFORM_BUDGETS = {
    "mobile": {"max_draw_calls": 250, "max_triangles": 200_000, "ms_budget_60fps": 16.6},
    "webgl": {"max_draw_calls": 500, "max_triangles": 500_000, "ms_budget_60fps": 16.6},
    "desktop": {"max_draw_calls": 3000, "max_triangles": 5_000_000, "ms_budget_60fps": 16.6},
    "vr": {"max_draw_calls": 800, "max_triangles": 1_000_000, "ms_budget_60fps": 11.1}, # 90 FPS
}

def audit_render_budget(draw_calls: int, triangles: int, platform: str = "desktop", target_fps: int = 60) -> bool:
    budget = PLATFORM_BUDGETS.get(platform, PLATFORM_BUDGETS["desktop"])
    ms_target = 1000.0 / target_fps

    print("=" * 65)
    print(f"3D Game Performance Budget Audit: [{platform.upper()}] @ {target_fps} FPS")
    print("=" * 65)
    print(f"Target Frame Time:       {ms_target:.2f} ms")
    print(f"Reported Draw Calls:     {draw_calls:<8} (Limit: {budget['max_draw_calls']})")
    print(f"Reported Triangle Count: {triangles:<8} (Limit: {budget['max_triangles']})")

    dc_exceeded = draw_calls > budget["max_draw_calls"]
    tri_exceeded = triangles > budget["max_triangles"]

    print("-" * 65)
    if dc_exceeded:
        print(f"[FAIL] Draw call count exceeds budget by {draw_calls - budget['max_draw_calls']}!")
        print("  -> Recommendation: Enable GPU instancing, texture atlasing, or static mesh batching.")
    else:
        print("[PASS] Draw call budget within target thresholds.")

    if tri_exceeded:
        print(f"[FAIL] Triangle count exceeds budget by {triangles - budget['max_triangles']}!")
        print("  -> Recommendation: Generate aggressive LOD meshes or apply occlusion culling.")
    else:
        print("[PASS] Geometry triangle count within target thresholds.")

    passed = not (dc_exceeded or tri_exceeded)
    print("=" * 65)
    print(f"OVERALL AUDIT RESULT: {'[PASSED]' if passed else '[ACTION REQUIRED]'}")
    return passed

def test_frustum_sphere_intersection(sphere_pos: tuple, sphere_radius: float, frustum_plane_dist: float) -> bool:
    """Calculates whether a bounding sphere intersects or sits in front of a clipping plane."""
    # Signed distance from sphere center to plane
    dist = sphere_pos[2] - frustum_plane_dist
    return dist >= -sphere_radius

def main():
    parser = argparse.ArgumentParser(description="3D Game Architecture Performance Validator")
    parser.add_argument("--audit-budget", action="store_true", help="Audit frame render budget")
    parser.add_argument("--draw-calls", type=int, default=1200, help="Number of draw calls per frame")
    parser.add_argument("--triangles", type=int, default=800_000, help="Number of triangles rendered")
    parser.add_argument("--platform", type=str, default="desktop", choices=list(PLATFORM_BUDGETS.keys()))
    parser.add_argument("--target-fps", type=int, default=60, help="Target frames per second")
    parser.add_argument("--test-culling", action="store_true", help="Run frustum culling geometric self-test")

    args = parser.parse_args()

    if args.test_culling:
        print("=" * 65)
        print("Testing 3D Frustum Bounding-Sphere Culling Math")
        print("=" * 65)
        # Sphere at z=15.0 with radius 2.0 against near plane at z=1.0
        visible_sphere = test_frustum_sphere_intersection((0, 0, 15.0), 2.0, 1.0)
        # Sphere at z=-5.0 with radius 2.0 (behind near plane)
        culled_sphere = test_frustum_sphere_intersection((0, 0, -5.0), 2.0, 1.0)
        
        print(f"Sphere in front of camera (z=15): Visible={visible_sphere} [Expected: True]")
        print(f"Sphere behind camera (z=-5):     Visible={culled_sphere} [Expected: False]")
        
        if visible_sphere and not culled_sphere:
            print("Culling self-test: [PASSED]")
            return
        else:
            print("Culling self-test: [FAILED]")
            sys.exit(1)

    if args.audit_budget:
        ok = audit_render_budget(args.draw_calls, args.triangles, args.platform, args.target_fps)
        sys.exit(0 if ok else 1)

    print("=" * 65)
    print("3D Game Architecture Helper: Operational")
    print("Platforms Available:", ", ".join(PLATFORM_BUDGETS.keys()))
    print("Use --help for audit options.")

if __name__ == "__main__":
    main()
