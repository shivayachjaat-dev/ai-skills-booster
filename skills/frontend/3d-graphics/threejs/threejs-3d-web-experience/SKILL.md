---
name: threejs-3d-web-experience
description: "Use this skill when designing, implementing, and optimizing interactive 3D web experiences using Three.js and React Three Fiber (R3F). It guides the agent through scene graph architecture, GLTF/GLB model loading and compression (Draco/Meshopt), custom GLSL shaders, camera controls (OrbitControls), lighting and shadows, and 60 FPS mobile performance optimization."
domain: frontend
category: 3d-graphics
subcategory: threejs
tags:
  - threejs
  - webgl
  - 3d
  - react-three-fiber
  - r3f
  - shaders
  - frontend
technologies:
  - Three.js
  - React Three Fiber
  - WebGL
  - GLSL
  - GLTF
  - TypeScript
complexity: advanced
maturity: stable
tools:
  - npm
  - pnpm
  - gltf-pipeline
dependencies:
  - three >= 0.160.0
  - @types/three >= 0.160.0
---
# Three.js & React Three Fiber (R3F) 3D Web Architecture

## Overview

A definitive production frontend engineering standard for building interactive, high-performance 3D web experiences using Three.js and React Three Fiber (R3F). Bringing 3D to the web often results in sluggish frame rates, bloated asset downloads, and battery drain. This skill instructs AI agents on scene graph hierarchy, GLTF/GLB model optimization using Draco and Meshopt compression, custom GLSL shader materials, responsive canvas sizing, and maintaining consistent 60 FPS performance on mobile devices.

## When to Use

- Building interactive 3D product configurators, e-commerce showcases, and spatial portfolios.
- Integrating immersive WebGL canvas backgrounds that respond to scroll or mouse positions.
- Developing data visualizations in 3D space (topological maps, network graphs).
- Rendering animated 3D character avatars or procedural environments.

## When NOT to Use

- 2D websites where simple CSS animations or Canvas 2D achieve the desired effect without the 600 KB Three.js bundle overhead.
- Native AAA gaming where WebAssembly game engines (Unreal/Unity WebGL) are required.

## Inputs & Prerequisites

- Modern browser with WebGL 2.0 support.
- Node.js 18+ with TypeScript.
- 3D assets in optimized GLTF/GLB format.

## Core Workflow

### 1. Declarative 3D Scene in React Three Fiber (R3F)
Build a responsive, performant 3D scene with lighting, soft shadows, and orbit controls:

```tsx
// components/Scene3D.tsx
import React, { Suspense, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, useGLTF, Environment, Float } from '@react-three/drei';
import * as THREE from 'three';

interface ModelProps {
  url: string;
}

function ProductModel({ url }: ModelProps) {
  const { scene } = useGLTF(url);
  const meshRef = useRef<THREE.Group>(null);

  // Smooth continuous rotation in animation loop
  useFrame((state, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += delta * 0.5;
    }
  });

  return (
    <Float speed={2} rotationIntensity={0.5} floatIntensity={1}>
      <primitive ref={meshRef} object={scene} scale={1.5} dispose={null} />
    </Float>
  );
}

export const InteractiveCanvas: React.FC = () => {
  return (
    <div style={{ width: '100vw', height: '100vh', background: '#0a0a0c' }}>
      <Canvas
        camera={{ position: [0, 2, 5], fov: 45 }}
        gl={{ antialias: true, powerPreference: 'high-performance' }}
        dpr={[1, 2]} // Cap device pixel ratio at 2x for Retina mobile performance
      >
        <ambientLight intensity={0.7} />
        <directionalLight position={[5, 10, 5]} intensity={1.5} castShadow />
        <Suspense fallback={null}>
          <ProductModel url="/models/product-optimized.glb" />
          <Environment preset="city" />
        </Suspense>
        <OrbitControls enablePan={false} maxPolarAngle={Math.PI / 2} minDistance={2} maxDistance={10} />
      </Canvas>
    </div>
  );
};
```

### 2. GLTF Model Compression Pipeline
Compress unoptimized 3D models before publishing to web servers:

```bash
# Compress GLTF model using Draco geometry compression and KTX2 texture compression
gltf-pipeline -i raw_model.gltf -o model-draco.glb -d --draco.compressionLevel 7

# Inspect mesh triangle count and draw calls
npx gltf-transform inspect model-draco.glb
```

### 3. Custom GLSL Vertex and Fragment Shader Material
Create custom visual effects beyond standard materials:

```typescript
import { shaderMaterial } from '@react-three/drei';
import * as THREE from 'three';
import { extend } from '@react-three/fiber';

export const HologramMaterial = shaderMaterial(
  { uTime: 0, uColor: new THREE.Color(0.2, 0.8, 1.0) },
  // Vertex Shader
  `
    varying vec2 vUv;
    varying vec3 vNormal;
    void main() {
      vUv = uv;
      vNormal = normalize(normalMatrix * normal);
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  // Fragment Shader
  `
    uniform float uTime;
    uniform vec3 uColor;
    varying vec2 vUv;
    varying vec3 vNormal;
    void main() {
      float fresnel = pow(1.0 - dot(vNormal, vec3(0.0, 0.0, 1.0)), 2.0);
      float scanline = sin(vUv.y * 100.0 + uTime * 5.0) * 0.1;
      gl_FragColor = vec4(uColor + scanline, fresnel * 0.8);
    }
  `
);

extend({ HologramMaterial });
```

## Best Practices & Failure Modes

1. **Uncapped Device Pixel Ratio (DPR)**: Rendering at native 3x or 4x DPR on high-end mobile phones forces the GPU to fill 4x more pixels, causing immediate thermal throttling and drops to 15 FPS. Always cap DPR with `dpr={[1, 2]}`.
2. **Memory Leaks from Undisposed Geometries**: In Three.js, removing a mesh from the scene does not free GPU memory. Always traverse and dispose geometries, textures, and materials: `mesh.geometry.dispose()`, `mesh.material.dispose()`.
3. **Draw Call Overload**: Having hundreds of separate meshes creates hundreds of WebGL draw calls. Merge static meshes using `THREE.BufferGeometryUtils.mergeGeometries` or use `InstancedMesh` for repeated objects.

## Verification & Testing

- Monitor frame rates using `r3f-perf`:
  ```tsx
  import { Perf } from 'r3f-perf';
  <Canvas><Perf position="top-left" /></Canvas>
  ```
  *Verify that draw calls are < 50 and FPS remains at 60.*
