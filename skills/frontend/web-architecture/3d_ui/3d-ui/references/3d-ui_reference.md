# Spatial 3D UI & Cross-Platform Transformations Reference

## Platform Matrix & API Comparison
| Platform | Perspective Control | Rotation Syntax | Layer Stacking (Z-Depth) | Performance Impact |
|---|---|---|---|---|
| **Web (CSS 3D)** | `perspective: 1000px;` | `transform: rotateX(15deg) rotateY(-10deg);` | `transform: translateZ(40px);` | Creates new GPU compositing layer |
| **iOS (SwiftUI)** | `perspective: 0.5` | `.rotation3DEffect(.degrees(x), axis: (0, 1, 0))` | `ZStack` + `.offset(z:)` | Metal hardware accelerated |
| **Android (Compose)** | `cameraDistance = 12f * density` | `rotationX = -offset.y; rotationY = offset.x;` | `graphicsLayer` elevation | RenderNode hardware pipeline |
| **Flutter** | `Matrix4.identity()..setEntry(3, 2, 0.001)` | `..rotateX(angle)..rotateY(angle)` | `Transform(transform: ...)` | Skia / Impeller canvas transform |

## Hardware Compositing & Memory Rules
1. **Layer Promotion**:
   Applying `transform-style: preserve-3d` forces the browser to create a separate backing store texture on the GPU. Limit simultaneous interactive 3D elements to $< 20$ per viewport to avoid VRAM exhaustion on mobile devices.
2. **Reduced Motion Compliance**:
   Always wrap spatial animations in media query / platform checks:
   - CSS: `@media (prefers-reduced-motion: reduce)`
   - SwiftUI: `@Environment(\.accessibilityReduceMotion) var reduceMotion`
   - Compose: LocalLifecycleOwner / system animator duration scales.
