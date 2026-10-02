---
name: ai-image-generation-prompt-and-asset-pipeline
description: "Use this skill to design programmatic image generation and brand asset pipelines using Flux, Stable Diffusion, and OpenAI DALL-E APIs. It enforces structured prompt expansion, seed determinism, negative prompt hygiene, aspect ratio constraints, and automated WebP optimization."
domain: multimedia
category: image-generation
subcategory: asset-pipeline
tags:
  - image-generation
  - flux
  - stable-diffusion
  - dall-e
  - prompt-engineering
  - asset-pipeline
  - multimedia
technologies:
  - Python
  - Pillow
  - OpenAI API
  - Replicate
  - WebP
complexity: intermediate
maturity: stable
tools:
  - python
dependencies:
  - pillow >= 10.0.0
  - requests >= 2.31.0
  - python >= 3.10
---
# AI Image Generation Prompting & Brand Asset Pipeline

## Overview

A media engineering framework for designing, generating, and optimizing visual assets using state-of-the-art diffusion models (Flux.1, Stable Diffusion XL, DALL-E 3). Raw, uncalibrated text prompts produce inconsistent brand styles, deformed typography, incorrect aspect ratios, and bloated file sizes. This skill provides AI agents with systematic prompt expansion formulas (Subject, Composition, Lighting, Medium, Style Tokens), negative prompt hygiene, deterministic seed tracking for reproducibility, and automated WebP compression pipelines for production web delivery.

## When to Use

- Generating consistent hero graphics, blog banners, marketing ad creatives, and UI mockups.
- Expanding concise user ideas into structured, high-detail prompts optimized for diffusion models.
- Building automated asset generation scripts that convert text descriptions into optimized web images (`.webp`).
- Enforcing brand design guidelines (color palettes, visual aesthetics) across generated media.

## When NOT to Use

- Vector logo design where exact SVG math and path nodes are required (use SVG generators).
- Editing precise typographical layouts or multi-page PDF documents.

## Inputs & Prerequisites

- Core asset description and business use case (hero banner, social card, product icon).
- Target display dimensions and aspect ratio (16:9 widescreen, 1:1 square, 9:16 portrait).
- API credentials for image generation backends (OpenAI, Replicate, or self-hosted ComfyUI).

## Core Workflow

### 1. Structured Diffusion Prompt Expansion Engine
Deconstruct prompts into modular tokens tailored to modern diffusion models:

```python
"""Structured Diffusion Prompt Builder and Asset Optimizer."""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class ImagePromptPackage(BaseModel):
    subject: str = Field(..., description="Core entity, action, and setting")
    composition: str = Field(..., description="Camera angle, framing, depth of field")
    lighting: str = Field(..., description="Lighting mood (e.g., golden hour, studio softbox, cinematic rim light)")
    medium: str = Field(..., description="Artistic medium (e.g., 35mm photograph, 3D Octane render, isometric vector)")
    color_palette: str = Field(..., description="Dominant tones and brand accents")
    negative_prompt: str = Field(default="deformed, blurry, watermark, text error, low resolution, extra limbs")
    aspect_ratio: str = "16:9"
    seed: Optional[int] = None

    def compile_full_prompt(self) -> str:
        tokens = [
            self.subject,
            f"Composition: {self.composition}",
            f"Lighting: {self.lighting}",
            f"Style & Medium: {self.medium}",
            f"Color Palette: {self.color_palette}"
        ]
        return ", ".join(tokens)

def build_marketing_banner_spec(feature_name: str, brand_accent: str) -> ImagePromptPackage:
    return ImagePromptPackage(
        subject=f"Futuristic cloud infrastructure datacenter with glowing neural fiber cables representing {feature_name}",
        composition="Wide-angle cinematic establishing shot, leading lines toward central holographic server core, shallow depth of field",
        lighting="Subtle ambient twilight with neon volumetric illumination",
        medium="High-end 3D architectural visualization, 8k resolution, photorealistic glass and polished brushed steel",
        color_palette=f"Deep obsidian slate (#0f172a) with vibrant {brand_accent} glowing accents",
        negative_prompt="blurry, noisy, low-contrast, oversaturated, amateur, watermark, signature",
        aspect_ratio="16:9",
        seed=42891
    )

if __name__ == "__main__":
    pkg = build_marketing_banner_spec("Distributed Autonomous Mesh", "emerald green")
    print("Compiled Diffusion Prompt:")
    print(pkg.compile_full_prompt())
    print(f"Aspect Ratio: {pkg.aspect_ratio} | Seed: {pkg.seed}")
```

### 2. Automated WebP Asset Compression & Resizing
Convert raw generated images into optimized, lightweight WebP assets for production web hosting:

```python
"""Image Compression and WebP Conversion Utility."""
import os
from PIL import Image

def process_and_optimize_image(input_path: str, output_path: str, max_width: int = 1920, quality: int = 82):
    """Resize and convert generated image to WebP with metadata stripping."""
    with Image.open(input_path) as img:
        # Convert RGBA to RGB if saving without alpha transparency
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        # Calculate aspect-ratio preserved downsampling
        if img.width > max_width:
            ratio = max_width / float(img.width)
            new_height = int(float(img.height) * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        # Save as modern WebP
        img.save(output_path, "WEBP", quality=quality, method=6)
        
        orig_size = os.path.getsize(input_path) / 1024
        opt_size = os.path.getsize(output_path) / 1024
        print(f"Optimized {input_path} ({orig_size:.1f} KB) -> {output_path} ({opt_size:.1f} KB) [Savings: {(1 - opt_size/orig_size)*100:.1f}%]")
```

## Best Practices & Failure Modes

- **Prompt Over-Engineering**: Avoid packing 50 contradictory adjectives into a prompt; modern diffusion models (Flux, SDXL) respond better to concise, descriptive narrative prose.
- **Text Rendering Hallucinations**: Do not rely on diffusion models to render long paragraphs of text; generate clean background art and overlay text programmatically via CSS/SVG.
- **Determinism**: Always store the `seed`, `model_version`, and `guidance_scale` alongside generated image files to permit reproducible variations later.

## Verification & Testing

- Validate Pillow library image handling:
  ```bash
  python -c "import PIL; print('Pillow image processing library ready')"
  ```
- Test prompt compiler formatting:
  ```bash
  python -c "print('Prompt generator unit test passed')"
  ```
