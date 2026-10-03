# 3D Game Engine Graphics & Physics Technical Reference

## Real-Time Rendering Subsystems
1. **Vertex Buffers & Memory Layout**:
   - Interleaved Vertex Buffer Objects (VBO) containing position (`vec3`), normal (`vec3`), UV coordinates (`vec2`), and tangent vectors (`vec4`) deliver optimal L1/L2 GPU cache locality.
   - Index Buffer Objects (IBO) using `uint16` or `uint32` indices prevent duplicate vertex transformations.
2. **PBR Material Channels**:
   - **Albedo**: Base color in linear color space (sRGB textures must be decoded upon sampling).
   - **Roughness / Metallic**: Packed into single ORM (Occlusion, Roughness, Metallic) texture channels to reduce texture sampler binds.
   - **Normal Maps**: Tangent-space normal vectors ($[0, 1]$ mapped to $[-1, 1]$).

## Physics & Spatial Partitioning
| Structure | Best Suited For | Query Complexity | Rebuild Cost |
|---|---|---|---|
| **BVH (Bounding Volume Hierarchy)** | Dynamic moving meshes, ray tracing | $O(\log N)$ | Moderate (refit per frame) |
| **Octree** | Sparse outdoor worlds, static geometry | $O(\log N)$ | High (build offline) |
| **Grid / Spatial Hash** | High-density dynamic particle/debris checks | $O(1)$ amortized | Low (rehash per frame) |

## Camera Projection & Frustum Math
- Near clipping plane: Keep as far as acceptable (e.g. $0.1\text{ m}$ to $0.3\text{ m}$) to maximize 24-bit/32-bit depth buffer precision ($Z$-fighting mitigation).
- Vertical Field of View (FOV): $60^\circ - 75^\circ$ for standard third-person, $90^\circ - 110^\circ$ for first-person PC gaming.
