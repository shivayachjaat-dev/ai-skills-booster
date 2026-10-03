---
name: 3d-games
description: "Use this skill to design, architect, and optimize real-time 3D game systems across Unity, Unreal Engine, Godot, and Three.js. It covers rendering pipeline selection (Forward+ vs Deferred), custom shader development, collision physics geometry optimization, spring-arm camera systems, and hierarchical Level of Detail (LOD) management."
domain: software-engineering
category: architecture
subcategory: patterns
tags:
  - software-engineering
  - game-development
  - 3d-graphics
  - shaders
  - physics
  - rendering-pipeline
technologies:
  - 3D Games
  - GLSL
  - HLSL
  - Three.js
  - Unity
  - Unreal Engine
  - Godot
complexity: advanced
maturity: stable
tools:
  - python
  - bash
dependencies:
  - python@>=3.10
version: 1.0.0
author: Antigravity Team
---

# 3D Game Architecture & Real-Time Engine Engineering

## Overview

A comprehensive software architecture standard and performance optimization guide for real-time 3D game engines (Unreal Engine 5, Unity, Godot 4, and WebGPU/Three.js). Modern 3D interactive applications require balancing visual fidelity against strict per-frame millisecond budgets (16.6ms for 60 FPS, 8.3ms for 120 FPS). This skill guides game developers, graphics engineers, and AI coding agents in structuring the primary subsystems of a 3D game: rendering pipelines, custom shader authoring, rigid-body and kinematic collision physics, responsive camera controllers, and distance-based asset culling.

```
+--------------------------------------------------------------------------------+
|                         3D Game Frame Execution Lifecycle                      |
|                                                                                |
|  [ Input Sampling ] ---> [ Gameplay & AI Tick ] ---> [ Physics Step (FixedTick)]
|                                                            |                   |
|                                                            v                   |
|  [ Camera Spring-Arm Collision ] <--- [ Transform Hierarchy & Animation Update]|
|               |                                                                |
|               v                                                                |
|  [ Scene Culling: Frustum Culling + Occlusion Culling + LOD Selection ]        |
|               |                                                                |
|               v                                                                |
|  [ Render Dispatch: Draw Call Batching / GPU Instancing ]                      |
|               |                                                                |
|               v                                                                |
|  [ GPU Pipeline: Vertex Shading -> Rasterization -> Fragment Shading -> Post ] |
+--------------------------------------------------------------------------------+
```

## When to Use

- Architecting gameplay mechanics, physics interactions, or camera controllers for 3D games or interactive simulations.
- Profiling and resolving frame rate drops caused by draw call saturation, unbatched materials, or over-complex physics colliders.
- Authoring custom vertex and fragment shaders for stylized effects (toon shading, procedural water, dissolving meshes) or PBR materials.
- Designing distance-scaled Level of Detail (LOD) hierarchies and shadow-cascade split distances.

## When NOT to Use

- Pure 2D sprite-based games without 3D depth, perspective projection, or spatial lighting (use 2D game architecture standards).
- Offline pre-rendered CGI or ray-traced film rendering without real-time interactive frame budget constraints.

## Inputs & Prerequisites

- Game engine environment (Unreal Engine 5.x, Unity 2022/6000 LTS, Godot 4.x, or Node.js with Three.js).
- Target platform performance profile (Desktop PC, Console, Mobile, or WebGL/WebGPU).
- 3D asset pipeline supporting standard exchange formats (glTF 2.0, FBX, or USD).

## Core Workflow

### Step 1: Rendering Pipeline Selection & Draw Call Budgeting
Select between Forward+ and Deferred rendering based on target platform and lighting complexity:

| Architecture | Best Suited For | Multiple Dynamic Lights | MSAA Support | Memory Bandwidth |
|---|---|---|---|---|
| **Forward+** | VR, Mobile, WebGPU, stylization | Good (Tiled/Clustered culling) | Native hardware MSAA | Low G-Buffer bandwidth |
| **Deferred** | High-end Desktop/Console, AAA PBR | Excellent (hundreds of lights) | Requires TAA / FXAA | High (Heavy G-Buffer writes) |

Enforce strict draw call budgets:
- Mobile / WebGL: $< 300$ draw calls per frame, $< 250,000$ triangles visible.
- PC / Console: $< 2,500$ draw calls per frame, $< 5,000,000$ triangles visible.

### Step 2: Custom Shader Development (Stylized Toon / PBR)
Implement shaders that calculate lighting efficiently using standard dot-product approximations:

```glsl
// Custom Toon Shading Fragment Shader (GLSL / Three.js / Godot)
precision highp float;

varying vec3 vNormal;
varying vec3 vViewPosition;

uniform vec3 uLightDirection; // Normalized directional light vector
uniform vec3 uBaseColor;
uniform vec3 uShadowColor;

void main() {
    vec3 normal = normalize(vNormal);
    vec3 lightDir = normalize(uLightDirection);
    
    // Lambertian diffuse coefficient
    float NdotL = dot(normal, lightDir);
    
    // Quantize light into discrete steps (cel shading)
    float lightIntensity = smoothstep(-0.05, 0.05, NdotL);
    vec3 finalColor = mix(uShadowColor, uBaseColor, lightIntensity);
    
    // Rim lighting (Fresnel effect)
    vec3 viewDir = normalize(vViewPosition);
    float fresnel = 1.0 - max(0.0, dot(normal, viewDir));
    float rim = smoothstep(0.6, 0.8, fresnel) * max(0.0, NdotL);
    
    gl_FragColor = vec4(finalColor + vec3(rim * 0.4), 1.0);
}
```

### Step 3: Collision Physics Optimization
Never attach complex triangle mesh colliders to moving dynamic actors. Follow the collision hierarchy:
1. **Characters / Pawns**: Use single vertical Capsule Colliders (`height`, `radius`).
2. **Dynamic Crates / Debris**: Use simple Box or Sphere primitives.
3. **Static Architecture**: Use decomposed convex hulls or simplified compound boxes.
4. **Complex Terrain**: Use static Heightfield / Mesh colliders only.

```python
# Verify collision matrix rules to avoid quadratic collision checks
def should_collide(layer_a: int, layer_b: int, collision_mask: dict) -> bool:
    """Evaluates bitmask collision filtering."""
    return bool(collision_mask.get(layer_a, 0) & (1 << layer_b))
```

### Step 4: Spring-Arm Camera Controller with Collision Avoidance
Implement a third-person camera that prevents clipping through world geometry:

```python
import math

class SpringArmCamera:
    def __init__(self, target_arm_length=4.5, min_arm_length=0.5):
        self.target_arm_length = target_arm_length
        self.min_arm_length = min_arm_length
        self.current_arm_length = target_arm_length

    def update(self, pivot_position: tuple, camera_rotation_pitch_yaw: tuple, raycast_hit_dist: float = None):
        target_dist = self.target_arm_length
        
        # If raycast detected obstacle between character and desired camera position
        if raycast_hit_dist is not None and raycast_hit_dist < target_dist:
            target_dist = max(self.min_arm_length, raycast_hit_dist - 0.2)
            
        # Smooth interpolation (lerp) to avoid jarring camera pops
        self.current_arm_length += (target_dist - self.current_arm_length) * 0.15
        return self.current_arm_length
```

### Step 5: Level of Detail (LOD) Strategy
Configure distance-based LOD thresholds to maintain geometric density without GPU saturation:
- **LOD 0** ($0 - 15\text{ m}$): 100% vertex count, full shader complexity.
- **LOD 1** ($15 - 40\text{ m}$): 50% vertex count, disabled vertex displacement.
- **LOD 2** ($40 - 100\text{ m}$): 25% vertex count, simplified lighting.
- **LOD 3** ($> 100\text{ m}$): Billboard imposter quad (2 triangles).

## Best Practices & Failure Modes

- **Never Update Transform Hierarchy Out-of-Order**: Ensure parent transforms evaluate before child components (e.g., character skeleton evaluates before weapon attachments).
- **Avoid Dynamic Memory Allocations in Gameplay Ticks**: Pre-allocate object pools for projectiles, particle emitters, and audio sources. Garbage collection spikes freeze the render loop.
- **Shadow Cascade Overlap**: Ensure directional light shadow cascade splits have a 10% transition blend zone to eliminate visible shadow popping when moving.

## Verification & Testing

1. Test frame budget calculations: Run `python scripts/3d-games_helper.py --audit-budget --draw-calls 1200 --triangles 450000 --target-fps 60`.
2. Verify frustum culling math: Run `python scripts/3d-games_helper.py --test-culling` to validate sphere-frustum intersection logic.
3. Profile draw call batching: Confirm GPU instancing reduces draw calls by $>60\%$ on duplicate static meshes in the scene view.
