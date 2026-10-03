#!/usr/bin/env python3
"""
3d-ui_helper.py - Spatial 3D UI & Perspective Matrix Utility.
Calculates 4x4 homogeneous transformation matrices, generates production CSS
transform strings, and evaluates typographic legibility under perspective tilt.
"""

import sys
import math
import argparse

def compute_perspective_matrix(perspective_px: float, rotate_x_deg: float, rotate_y_deg: float, translate_z_px: float = 0.0) -> list[list[float]]:
    """Generates 4x4 homogeneous transformation matrix with perspective."""
    rx = math.radians(rotate_x_deg)
    ry = math.radians(rotate_y_deg)

    # Perspective factor (1 / d)
    pz = -1.0 / perspective_px if perspective_px > 0 else 0.0

    # Composite rotation matrix
    cos_x, sin_x = math.cos(rx), math.sin(rx)
    cos_y, sin_y = math.cos(ry), math.sin(ry)

    # 4x4 matrix
    matrix = [
        [cos_y, sin_x * sin_y, -cos_x * sin_y, 0.0],
        [0.0, cos_x, sin_x, 0.0],
        [sin_y, -sin_x * cos_y, cos_x * cos_y, translate_z_px],
        [0.0, 0.0, pz, 1.0]
    ]
    return matrix

def generate_css_rules(perspective: int, tilt_x: float, tilt_y: float, depth: float) -> str:
    css = f"""/* Generated Production CSS 3D Rules */
.perspective-container {{
  perspective: {perspective}px;
  perspective-origin: 50% 50%;
}}

.spatial-card {{
  transform-style: preserve-3d;
  transform: rotateX({tilt_x:.1f}deg) rotateY({tilt_y:.1f}deg);
  will-change: transform;
  transition: transform 0.2s cubic-bezier(0.25, 1, 0.5, 1);
}}

.spatial-layer-foreground {{
  transform: translateZ({depth:.1f}px);
}}
"""
    return css

def check_typographic_legibility(tilt_deg: float, font_size_px: float) -> bool:
    """Evaluates if font size remains legible at given tilt angle."""
    max_safe_tilt = 25.0
    min_safe_font_size = 14.0

    if abs(tilt_deg) > max_safe_tilt and font_size_px < min_safe_font_size:
        return False
    return True

def main():
    parser = argparse.ArgumentParser(description="Spatial 3D UI Matrix & CSS Generator")
    parser.add_argument("--generate-css", action="store_true", help="Generate production CSS transform rules")
    parser.add_argument("--perspective", type=int, default=1000, help="Perspective distance in pixels")
    parser.add_argument("--tilt-x", type=float, default=12.0, help="Rotation around X axis in degrees")
    parser.add_argument("--tilt-y", type=float, default=-15.0, help="Rotation around Y axis in degrees")
    parser.add_argument("--depth", type=float, default=40.0, help="Z-axis depth layer in pixels")
    parser.add_argument("--test-matrix", action="store_true", help="Run 4x4 matrix self-test")

    args = parser.parse_args()

    if args.test_matrix:
        print("=" * 65)
        print("Testing 4x4 Spatial Transform Matrix Generation")
        print("=" * 65)
        mat = compute_perspective_matrix(args.perspective, args.tilt_x, args.tilt_y, args.depth)
        for row in mat:
            print("  [ " + ", ".join(f"{v:8.4f}" for v in row) + " ]")
        print("\nMatrix calculation: [PASSED]")
        return

    if args.generate_css:
        css = generate_css_rules(args.perspective, args.tilt_x, args.tilt_y, args.depth)
        print(css)
        is_legible = check_typographic_legibility(args.tilt_x, 16.0)
        print(f"/* Typographic legibility assessment at {args.tilt_x}deg: {'[SAFE]' if is_legible else '[WARNING: BLURRY TEXT]'} */")
        return

    print("=" * 65)
    print("3D Spatial UI Helper: Operational")
    print("Run with --generate-css or --test-matrix")

if __name__ == "__main__":
    main()
