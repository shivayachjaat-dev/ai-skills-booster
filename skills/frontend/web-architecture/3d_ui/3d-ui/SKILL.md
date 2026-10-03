---
name: 3d-ui
description: "Use this skill to design, build, and optimize spatial 3D interactive user interfaces and perspective-transformed components across Web (CSS 3D, React Three Fiber), iOS (SwiftUI), Android (Jetpack Compose), and Flutter. It covers perspective matrix math, cursor/gyroscope parallax tilting, spring damping physics, and accessibility adaptations (prefers-reduced-motion)."
domain: frontend
category: web-architecture
subcategory: 3d_ui
tags:
  - frontend
  - 3d-ui
  - spatial-computing
  - css-3d
  - swiftui
  - jetpack-compose
  - flutter
  - parallax
technologies:
  - CSS 3D Transforms
  - Three.js
  - SwiftUI
  - Jetpack Compose
  - Flutter
  - TypeScript
complexity: advanced
maturity: stable
tools:
  - css
  - typescript
  - swift
  - kotlin
  - dart
  - python
dependencies:
  - python@>=3.10
version: 1.0.0
author: Antigravity Team
---

# Spatial 3D UI & Perspective Transformation Architecture

## Overview

A modern multi-platform engineering standard for designing and implementing interactive 3D spatial user interfaces, parallax card tilts, and perspective transformations across the Web (CSS 3D, WebGL/Three.js), iOS (SwiftUI), Android (Jetpack Compose), and Flutter. Flat 2D user interfaces often feel disconnected from physical tactile interaction. By projecting elements onto a virtual 3D plane with dynamic camera vanishing points, spatial UI delivers intuitive depth cues, depth-layer popouts (`translateZ`), and interactive momentum while respecting strict device accessibility constraints (`prefers-reduced-motion`).

```
+--------------------------------------------------------------------------------+
|                         Spatial 3D UI Interaction Model                        |
|                                                                                |
|  [ User Input: Pointer Move / Gyroscope / Drag Gesture ]                       |
|                             |                                                  |
|                             v                                                  |
|  [ Normalized Spatial Coordinates ($X \in [-1, 1], Y \in [-1, 1]$) ]           |
|                             |                                                  |
|                             v                                                  |
|  [ Spring Damping & Physics Interpolation (Hooke's Law / Lerp) ]               |
|                             |                                                  |
|                             v                                                  |
|  [ Perspective Matrix Transformation ($M_{\text{proj}} \times R_x \times R_y$) ]|
|                             |                                                  |
|             +---------------+---------------+---------------+                  |
|             v                               v               v                  |
|     [ Web: CSS 3D ]                [ iOS: SwiftUI ]  [ Android: Compose ]      |
|  (transform-style: preserve-3d)    (.rotation3DEffect) (graphicsLayer camera)  |
+--------------------------------------------------------------------------------+
```

## When to Use

- Designing engaging product showcase cards, dashboard widgets, and interactive landing page heroes with tactile depth.
- Implementing gyroscope-driven mobile UI tilt interactions for iOS and Android.
- Building multi-layered spatial interfaces where background textures, content cards, and floating badges occupy distinct Z-index depths (`translateZ`).
- Converting flat UI components to subtle, responsive spatial elements without the overhead of heavy 3D game engines.

## When NOT to Use

- Data-dense administrative tables, financial spreadsheets, or reading-intensive document layouts where geometric distortion impairs legibility.
- Users who have enabled accessibility reduced-motion settings (`prefers-reduced-motion: reduce`).
- Low-power embedded displays or legacy browsers lacking hardware-accelerated CSS 3D transforms.

## Inputs & Prerequisites

- Platform rendering context: Web browser (Modern Chromium/Safari/Firefox), Xcode 15+ (SwiftUI 5+), Android Studio Hedgehog+ (Compose 1.5+), or Flutter 3.x.
- Knowledge of 3D transform matrices (Euler rotation angles on $X$ and $Y$ axes, Z-axis camera distance).

## Core Workflow

### Step 1: Web Implementation (CSS 3D & Hardware Acceleration)
Structure the DOM hierarchy with explicit perspective nesting. The container declares `perspective`, the card declares `preserve-3d`, and child elements declare relative `translateZ` offsets:

```css
/* Container establishing 3D viewport */
.perspective-viewport {
  perspective: 1000px;
  perspective-origin: center;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* Interactive card preserving 3D space */
.spatial-card {
  width: 320px;
  height: 440px;
  border-radius: 20px;
  transform-style: preserve-3d;
  will-change: transform;
  transition: transform 0.15s cubic-bezier(0.2, 0, 0, 1);
  background: linear-gradient(135deg, #1e1e38 0%, #0d0d1a 100%);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
}

/* Floating content layer pushed closer to viewer */
.spatial-content {
  transform: translateZ(40px); /* Pops 40px towards camera */
}

.spatial-badge {
  transform: translateZ(60px); /* Floats above content */
}

/* Accessibility: Disable transforms on reduced motion */
@media (prefers-reduced-motion: reduce) {
  .spatial-card {
    transition: none !important;
    transform: none !important;
  }
}
```

### Step 2: Native iOS Implementation (SwiftUI)
Leverage `.rotation3DEffect` with drag gestures and interactive spring animation:

```swift
import SwiftUI

struct SpatialCardView: View {
    @State private var dragOffset = CGSize.zero

    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "cube.transparent")
                .font(.system(size: 64))
                .foregroundColor(.cyan)
            Text("Spatial Interface")
                .font(.title2.bold())
                .foregroundColor(.white)
        }
        .frame(width: 300, height: 420)
        .background(
            RoundedRectangle(cornerRadius: 24)
                .fill(LinearGradient(colors: [.indigo, .purple], startPoint: .topLeading, endPoint: .bottomTrailing))
        )
        .shadow(color: .black.opacity(0.3), radius: 20, x: 0, y: 15)
        // 3D rotation along Y and X axes
        .rotation3DEffect(
            .degrees(Double(dragOffset.width / 12)),
            axis: (x: 0, y: 1, z: 0),
            perspective: 0.5
        )
        .rotation3DEffect(
            .degrees(Double(-dragOffset.height / 12)),
            axis: (x: 1, y: 0, z: 0),
            perspective: 0.5
        )
        .gesture(
            DragGesture()
                .onChanged { value in
                    withAnimation(.interactiveSpring(response: 0.2, dampingFraction: 0.6)) {
                        dragOffset = value.translation
                    }
                }
                .onEnded { _ in
                    withAnimation(.spring(response: 0.4, dampingFraction: 0.7)) {
                        dragOffset = .zero
                    }
                }
        )
    }
}
```

### Step 3: Native Android Implementation (Jetpack Compose)
In Jetpack Compose, manipulate `graphicsLayer` with camera distance to define perspective depth:

```kotlin
import androidx.compose.animation.core.animateOffsetAsState
import androidx.compose.animation.core.spring
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

@Composable
fun SpatialCardCompose() {
    var rawOffset by remember { mutableStateOf(Offset.Zero) }
    val animatedOffset by animateOffsetAsState(
        targetValue = rawOffset,
        animationSpec = spring(dampingRatio = 0.6f, stiffness = 400f)
    )

    Box(
        modifier = Modifier
            .size(300.dp, 420.dp)
            .pointerInput(Unit) {
                detectDragGestures(
                    onDrag = { change, dragAmount ->
                        change.consume()
                        rawOffset += dragAmount
                    },
                    onDragEnd = { rawOffset = Offset.Zero },
                    onDragCancel = { rawOffset = Offset.Zero }
                )
            }
            .graphicsLayer {
                // Pitch and Yaw angles
                rotationX = -animatedOffset.y * 0.08f
                rotationY = animatedOffset.x * 0.08f
                // Critical: Camera distance sets perspective distortion (higher = flatter)
                cameraDistance = 12f * density
                shadowElevation = 24.dp.toPx()
                shape = RoundedCornerShape(24.dp)
                clip = true
            }
            .background(Brush.linearGradient(listOf(Color(0xFF2E0854), Color(0xFF180B2D))))
    ) {
        Text(
            text = "Compose 3D",
            color = Color.White,
            fontSize = 28.sp,
            modifier = Modifier.align(Alignment.Center)
        )
    }
}
```

### Step 4: Flutter Matrix4 Implementation
In Flutter, modify row 3, column 2 of the 4x4 transform matrix for true perspective:

```dart
import 'package:flutter/material.dart';

class SpatialCardFlutter extends StatefulWidget {
  const SpatialCardFlutter({super.key});

  @override
  State<SpatialCardFlutter> createState() => _SpatialCardFlutterState();
}

class _SpatialCardFlutterState extends State<SpatialCardFlutter> {
  Offset _dragOffset = Offset.zero;

  @override
  Widget build(BuildContext context) {
    // 4x4 matrix with perspective vanishing coefficient
    final transform = Matrix4.identity()
      ..setEntry(3, 2, 0.0015) // Perspective factor
      ..rotateX(-_dragOffset.dy * 0.008)
      ..rotateY(_dragOffset.dx * 0.008);

    return GestureDetector(
      onPanUpdate: (d) => setState(() => _dragOffset += d.delta),
      onPanEnd: (_) => setState(() => _dragOffset = Offset.zero),
      child: TweenAnimationBuilder<Offset>(
        tween: Tween<Offset>(begin: Offset.zero, end: _dragOffset),
        duration: const Duration(milliseconds: 180),
        curve: Curves.easeOutCubic,
        builder: (context, offset, child) {
          return Transform(
            transform: transform,
            alignment: FractionalOffset.center,
            child: Container(
              width: 300,
              height: 420,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(24),
                gradient: const LinearGradient(colors: [Colors.deepPurple, Colors.indigo]),
                boxShadow: const [BoxShadow(color: Colors.black38, blurRadius: 25)],
              ),
              alignment: Alignment.center,
              child: const Text('Flutter 3D', style: TextStyle(color: Colors.white, fontSize: 30)),
            ),
          );
        },
      ),
    );
  }
}
```

## Best Practices & Failure Modes

- **Never Tilt Small Typography**: Avoid applying strong 3D rotation to body text ($< 16\text{ px}$). Subpixel antialiasing under perspective transforms blurs glyphs, degrading reading accessibility.
- **Hardware Acceleration Bottlenecks**: Avoid excessive nesting of `preserve-3d` contexts. Browsers allocate separate GPU compositing layers for 3D elements; having $>50$ simultaneous 3D cards causes GPU memory thrashing.
- **Spring Damping Physics**: Always attach return-to-center physics (damping ratio $\approx 0.7$) so rotated cards snap smoothly back to neutral orientation when released.

## Verification & Testing

1. Validate perspective matrix math: Run `python scripts/3d-ui_helper.py --test-matrix` to verify 4x4 transformation matrix calculations.
2. Check CSS generator: Run `python scripts/3d-ui_helper.py --generate-css --perspective 1200 --tilt-x 15 --tilt-y -10 --depth 40`.
3. Verify reduced motion compliance: Ensure testing environments verify that setting `prefers-reduced-motion: reduce` neutralizes all spatial rotations.
