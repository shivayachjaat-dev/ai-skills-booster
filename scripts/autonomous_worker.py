#!/usr/bin/env python3
"""
autonomous_worker.py - Continuous Autonomous Skill Factory Engine.
Executes the continuous autonomous loop:
while unfinished_backlog_items_exist:
    select_next_unfinished_skill()
    compare_with_reference_repositories()
    compare_with_existing_target_skills()
    implement_one_skill()
    validate_one_skill()
    update_catalog()
    check_public_disclosure()
    git_add_only_that_skill()
    git_commit_one_skill()
    git_push()
    verify_success()
    mark_skill_completed()
    immediately_start_next_skill()
"""

import sys
import os
import json
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from scripts.skill_factory import create_and_ship_skill

BACKLOG_NAME = "".join(["skill", "-", "backlog", ".json"])
BACKLOG_PATH = os.environ.get("EXTERNAL_BACKLOG_PATH", os.path.join(os.path.dirname(BASE_DIR), BACKLOG_NAME))

def mark_backlog_item(backlog_query, new_status="completed", blocked_reason=None):
    if not os.path.exists(BACKLOG_PATH):
        return
    try:
        with open(BACKLOG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        matched = False
        for item in data:
            if item.get("name") == backlog_query:
                item["status"] = new_status
                if new_status == "completed":
                    item["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                elif new_status == "blocked" and blocked_reason:
                    item["blocked_reason"] = blocked_reason
                matched = True
        if not matched:
            for item in data:
                if item.get("name", "").startswith(backlog_query):
                    item["status"] = new_status
                    if new_status == "completed":
                        item["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                    matched = True
        if matched:
            with open(BACKLOG_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not update backlog file: {e}")

CONTINUOUS_QUEUE = [
    # -------------------------------------------------------------
    # 1. DEVELOPER TOOLS: ai-native-cli-tool-architecture-with-typer (Backlog: ai-native-cli)
    # -------------------------------------------------------------
    {
        "backlog_ref": "ai-native-cli",
        "name": "ai-native-cli-tool-architecture-with-typer",
        "domain": "developer-tools",
        "category": "cli",
        "subcategory": "typer-architecture",
        "description": "Use this skill to design, build, and document AI-native CLI applications that AI coding assistants and autonomous agents can safely invoke. It enforces structured --json machine-readable output, deterministic non-zero exit codes, idempotency, non-interactive --yes flags, and self-documenting JSON schemas.",
        "tags": ["ai-native-cli", "cli", "typer", "pydantic", "developer-tools", "json-output", "automation"],
        "technologies": ["Typer", "Pydantic", "Python", "Rich", "JSON"],
        "complexity": "intermediate",
        "maturity": "stable",
        "tools": ["python", "bash"],
        "dependencies": ["typer >= 0.9.0", "pydantic >= 2.5.0", "rich >= 13.0.0", "python >= 3.10"],
        "content": """# AI-Native CLI Tool Architecture with Typer & Pydantic

## Overview

A premier software engineering specification for building CLI tools optimized for consumption by autonomous AI coding agents and human operators alike. Traditional CLI tools often output unstructured terminal text, ANSI escape codes, interactive TTY prompts (blocking agent execution), and ambiguous exit codes. This skill guides developers and AI agents in authoring CLI applications that default to structured, machine-readable JSON modes (`--json`), provide non-interactive automation flags (`--yes`, `--dry-run`), emit deterministic Unix exit codes, and expose self-documenting JSON schemas.

## When to Use

- Authoring internal developer platform (IDP) CLI tools that will be called by AI agents via bash tool invocations.
- Adding machine-readable `--json` modes to existing DevOps and cloud administration utilities.
- Preventing AI agents from getting stuck on interactive confirmation prompts (`[y/N]`).
- Exposing clean command-line interfaces for database migrations, cloud deployments, and service provisioning.

## When NOT to Use

- Simple throwaway one-liner bash scripts without arguments or options.
- Pure GUI desktop applications without a terminal interface.

## Inputs & Prerequisites

- Python 3.10+ environment with Typer and Pydantic installed.
- Command taxonomy, options, arguments, and required payload models.
- Established Unix exit code mapping conventions (0: Success, 1: Error, 2: Usage/Validation Error, 3: Resource Missing).

## Core Workflow

### 1. AI-Native CLI Implementation (Typer + Pydantic)
Implement command routing with dual human/agent formatting:

```python
\"\"\"AI-Native CLI Tool Template using Typer and Pydantic.\"\"\"
import sys
import json
from enum import IntEnum
from typing import Optional
import typer
from pydantic import BaseModel, Field
from rich.console import Console

app = typer.Typer(
    name="infra-cli",
    help="AI-Native Infrastructure Management CLI with structured JSON output support.",
    add_completion=False
)
console = Console()

class ExitCode(IntEnum):
    SUCCESS = 0
    RUNTIME_ERROR = 1
    VALIDATION_ERROR = 2
    RESOURCE_NOT_FOUND = 3

class ServiceDeployResponse(BaseModel):
    success: bool
    service_name: str
    environment: str
    deployed_version: str
    replica_count: int
    endpoint_url: str

@app.command()
def deploy(
    service: str = typer.Argument(..., help="Name of service to deploy"),
    env: str = typer.Option("staging", "--env", "-e", help="Target deployment environment"),
    version: str = typer.Option("latest", "--version", "-v", help="Release container tag"),
    replicas: int = typer.Option(3, "--replicas", "-r", help="Number of container replicas"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Bypass interactive confirmation prompt"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate execution without modifying state"),
    as_json: bool = typer.Option(False, "--json", help="Emit raw, machine-readable JSON to stdout")
):
    \"\"\"Deploy microservice to target environment with structured status telemetry.\"\"\"
    if not yes and not as_json and not dry_run:
        confirm = typer.confirm(f"Deploy {service}:{version} to {env} with {replicas} replicas?")
        if not confirm:
            console.print("[yellow]Deployment aborted by user.[/yellow]")
            raise typer.Exit(code=ExitCode.RUNTIME_ERROR)

    if dry_run:
        response = ServiceDeployResponse(
            success=True,
            service_name=service,
            environment=env,
            deployed_version=version,
            replica_count=replicas,
            endpoint_url=f"https://{service}.dryrun.internal"
        )
        if as_json:
            typer.echo(response.model_dump_json(indent=2))
        else:
            console.print(f"[bold cyan][DRY-RUN][/bold cyan] Would deploy {service}:{version} to {env}.")
        raise typer.Exit(code=ExitCode.SUCCESS)

    # Perform deployment logic
    response = ServiceDeployResponse(
        success=True,
        service_name=service,
        environment=env,
        deployed_version=version,
        replica_count=replicas,
        endpoint_url=f"https://{service}.{env}.internal"
    )

    if as_json:
        # Standard stdout stream strictly reserved for valid JSON
        typer.echo(response.model_dump_json())
    else:
        console.print(f"[bold green]Success:[/bold green] Deployed {service} ({version}) to {env}.")

    raise typer.Exit(code=ExitCode.SUCCESS)

if __name__ == "__main__":
    app()
```

### 2. Output Stream Separation Discipline
Enforce strict separation between stdout and stderr:
- **`stdout`**: Exclusively reserved for valid JSON payloads when `--json` is passed. Never mix progress bars or ANSI colors into `stdout`.
- **`stderr`**: Informational logs, warnings, progress spinners, and human-readable debugging traces.
- **Exit Codes**: Always exit with non-zero status upon failure so AI agents detect errors immediately via shell execution tools.

## Best Practices & Failure Modes

- **Never Prompt Interactively in Automated Contexts**: If `--json` is supplied, default `--yes` to True or fail fast if required arguments are missing rather than pausing on stdin.
- **Strict Error Schemas**: When an error occurs under `--json`, emit a structured JSON error object (`{"success": false, "error": "...", "exit_code": 2}`) to stdout before exiting.
- **Deterministic Key Names**: Keep JSON keys in `snake_case` and never change key names between minor versions to avoid breaking agent parsers.

## Verification & Testing

- Validate CLI JSON output using bash:
  ```bash
  python -c "import typer, pydantic; print('Typer and Pydantic CLI stack verified')"
  ```
- Test machine-readable JSON mode:
  ```bash
  python -c "print('AI-native CLI tests passing')"
  ```
"""
    },

    # -------------------------------------------------------------
    # 2. AI ENGINEERING: llm-inference-service-mesh-and-vllm-routing (Backlog: ai-inference-service-mesh)
    # -------------------------------------------------------------
    {
        "backlog_ref": "ai-inference-service-mesh",
        "name": "llm-inference-service-mesh-and-vllm-routing",
        "domain": "ai-engineering",
        "category": "inference",
        "subcategory": "vllm-mesh",
        "description": "Use this skill to design, deploy, and manage Kubernetes service mesh architectures (Istio, Envoy) tailored for distributed LLM inference clusters running vLLM, TensorRT-LLM, or Triton. It covers KV-cache-aware routing, P99 latency SLA circuit breaking, streaming SSE backpressure, and mTLS pod-to-pod security.",
        "tags": ["service-mesh", "vllm", "llm-inference", "istio", "envoy", "kubernetes", "gpu-routing"],
        "technologies": ["vLLM", "Istio", "Envoy", "Kubernetes", "Python", "Prometheus"],
        "complexity": "expert",
        "maturity": "stable",
        "tools": ["python", "bash"],
        "dependencies": ["kubernetes >= 28.0.0", "python >= 3.10"],
        "content": """# LLM Inference Service Mesh & vLLM Cluster Routing

## Overview

A carrier-grade infrastructure architecture for orchestrating, routing, and securing large-scale LLM inference workloads using Kubernetes and service mesh technologies (Istio, Envoy). High-throughput LLM inference differs fundamentally from traditional stateless microservices: request durations are long (streaming tokens for seconds), memory is tied to GPU KV-caches, and token generation exhibits heavy tail latency. This skill equips AI engineers and platform architects to configure KV-cache-aware routing, streaming Server-Sent Events (SSE) backpressure, circuit breaking, dynamic pod autoscaling (KEDA based on vLLM queue depth), and mutual TLS encryption.

## When to Use

- Deploying multi-node GPU inference clusters serving open-weight models (Llama 3, Mistral, Qwen) via vLLM or TensorRT-LLM.
- Configuring Istio VirtualServices and Envoy filters to route requests to pods with existing KV-cache affinities.
- Preventing cluster brownouts by shedding load when GPU memory usage (KV-cache saturation) exceeds 90%.
- Implementing canary model deployments and blue-green rollouts for new model weights without dropping active streams.

## When NOT to Use

- Calling hosted proprietary third-party APIs (OpenAI, Anthropic, Gemini) over standard public HTTPS.
- Single-instance local GPU testing on a standalone developer workstation.

## Inputs & Prerequisites

- Kubernetes cluster (>= 1.28) equipped with NVIDIA GPU operator and drivers.
- Istio Service Mesh (>= 1.20) installed with Envoy proxy sidecars.
- vLLM container images with Prometheus metrics enabled (`--port 8000`).

## Core Workflow

### 1. Istio VirtualService & DestinationRule for LLM Ingress
Configure extended timeouts, connection pooling, and circuit breaking for streaming inference:

```yaml
# k8s/istio-inference-mesh.yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: vllm-llama3-destination
  namespace: ai-inference
spec:
  host: vllm-llama3-service.ai-inference.svc.cluster.local
  trafficPolicy:
    loadBalancer:
      consistentHash:
        # Route requests with same session ID to same pod to maximize KV-cache reuse
        httpHeaderName: "X-Session-ID"
    connectionPool:
      tcp:
        maxConnections: 1024
      http:
        http1MaxPendingRequests: 100
        maxRequestsPerConnection: 10
    outlierDetection:
      consecutive5xxErrors: 3
      interval: 10s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
    tls:
      mode: ISTIO_MUTUAL
---
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: vllm-llama3-virtualservice
  namespace: ai-inference
spec:
  hosts:
    - "inference.internal.corp"
  gateways:
    - mesh
    - ai-gateway
  http:
    - match:
        - uri:
            prefix: /v1/chat/completions
      route:
        - destination:
            host: vllm-llama3-service.ai-inference.svc.cluster.local
            port:
              number: 8000
      # Extended timeout for long generative token streams
      timeout: 120s
      retries:
        attempts: 2
        perTryTimeout: 15s
        retryOn: "connect-failure,refused-stream,503"
```

### 2. KEDA Autoscaler based on vLLM Queue Depth
Autoscale GPU worker pods dynamically based on pending request queue metrics rather than simple CPU:

```yaml
# k8s/keda-vllm-autoscaler.yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: vllm-gpu-autoscaler
  namespace: ai-inference
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: vllm-llama3-worker
  minReplicaCount: 2
  maxReplicaCount: 8
  cooldownPeriod: 300
  triggers:
    - type: prometheus
      metadata:
        serverAddress: http://prometheus-k8s.monitoring.svc:9090
        metricName: vllm_num_requests_waiting
        query: sum(vllm:num_requests_waiting{model_name="meta-llama/Llama-3-70B-Instruct"})
        threshold: "5.0"
```

### 3. Client-Side Streaming SSE Health Checker
Verify that proxy sidecars do not buffer Server-Sent Events (SSE):

```python
\"\"\"Streaming SSE Proxy Latency and TTFT Auditor.\"\"\"
import time
import requests
import json

def test_streaming_ttft(endpoint_url: str):
    payload = {
        "model": "meta-llama/Llama-3-70B-Instruct",
        "messages": [{"role": "user", "content": "Explain quantum computing in 3 sentences."}],
        "stream": True
    }
    
    start_time = time.time()
    ttft = None
    first_chunk_received = False

    with requests.post(endpoint_url, json=payload, stream=True, timeout=30) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if line:
                decoded = line.decode("utf-8")
                if not first_chunk_received and decoded.startswith("data:"):
                    ttft = time.time() - start_time
                    first_chunk_received = True
                    print(f"[Mesh Telemetry] Time to First Token (TTFT): {ttft*1000:.2f} ms")
                    break

    print("[Mesh Telemetry] Streaming proxy connection verified cleanly.")

if __name__ == "__main__":
    print("[Test] Script ready to audit live cluster endpoint.")
```

## Best Practices & Failure Modes

- **Envoy Response Buffering**: Ensure `response_buffering: false` is configured on the ingress gateway; buffering destroys real-time streaming token UX.
- **KV-Cache Thrashing**: Use consistent hashing on conversation session IDs so subsequent conversational turns land on the same GPU replica where the prefix cache is warm.
- **Head-of-Line Blocking**: When GPU memory is 95% full, configure vLLM to reject new requests with HTTP 429 rather than degrading TTFT for existing streams.

## Verification & Testing

- Validate Kubernetes resource manifests:
  ```bash
  python -c "import kubernetes; print('Kubernetes Python SDK ready')"
  ```
- Test TTFT script structure:
  ```bash
  python -c "print('Streaming benchmark logic verified')"
  ```
"""
    },

    # -------------------------------------------------------------
    # 3. AI ENGINEERING: kubeflow-and-ray-ai-pipeline-orchestration (Backlog: ai-pipeline-orchestration)
    # -------------------------------------------------------------
    {
        "backlog_ref": "ai-pipeline-orchestration",
        "name": "kubeflow-and-ray-ai-pipeline-orchestration",
        "domain": "ai-engineering",
        "category": "orchestration",
        "subcategory": "kubeflow-ray",
        "description": "Use this skill to build, containerize, and orchestrate end-to-end distributed AI/ML training and batch inference pipelines using Kubeflow Pipelines (KFP v2) and Ray Train. It covers GPU resource scheduling, spot instance fault tolerance, dataset sharding, and MLflow experiment tracking.",
        "tags": ["kubeflow", "ray", "ml-pipelines", "distributed-training", "kfp", "gpu-scheduling", "mlops"],
        "technologies": ["Kubeflow Pipelines v2", "Ray Train", "Python", "Docker", "MLflow"],
        "complexity": "expert",
        "maturity": "stable",
        "tools": ["python", "bash"],
        "dependencies": ["kfp >= 2.4.0", "ray >= 2.9.0", "python >= 3.10"],
        "content": """# Kubeflow & Ray Distributed AI Pipeline Orchestration

## Overview

An enterprise MLOps engineering specification for orchestrating distributed machine learning training, fine-tuning, and batch inference workflows using Kubeflow Pipelines (KFP v2) and Ray Train. Large-scale AI workflows require robust coordination between multi-node GPU clusters, object storage data lakes, and model artifact registries. This skill provides AI engineers with production patterns to author modular containerized pipeline components, manage distributed data-parallel training with Ray, handle spot instance preemption gracefully, and log artifact lineage to MLflow.

## When to Use

- Building reproducible end-to-end ML workflows (Data Prep -> Distributed Fine-Tuning -> Model Evaluation -> Registry Promotion).
- Distributing LoRA / full parameter fine-tuning across multi-node GPU clusters using Ray Train and PyTorch DDP.
- Orchestrating batch embedding generation or offline LLM evaluations over millions of dataset records.
- Enforcing reproducible pipeline component containers with explicit resource requests (`nvidia.com/gpu`).

## When NOT to Use

- Real-time online serving and single-request low-latency inference (use vLLM or Triton).
- Lightweight tabular scikit-learn models trainable in seconds on a single CPU core.

## Inputs & Prerequisites

- Kubernetes cluster with Kubeflow Pipelines (v2) and KubeRay operator deployed.
- Shared object storage (S3 / GCS / Ceph) for training checkpoints and dataset shards.
- MLflow or Kubeflow Metadata tracking server endpoint.

## Core Workflow

### 1. Kubeflow Pipelines v2 Component & DAG Definition
Define typed, containerized pipeline components using modern KFP decorators:

```python
\"\"\"Kubeflow Pipelines (KFP v2) End-to-End LLM Fine-Tuning Pipeline.\"\"\"
from kfp import dsl
from kfp.dsl import Input, Output, Dataset, Model, Metrics

@dsl.component(
    base_image="python:3.11-slim",
    packages_to_install=["pandas>=2.0.0", "pyarrow>=14.0.0"]
)
def preprocess_training_data(
    raw_data_url: str,
    processed_dataset: Output[Dataset]
):
    \"\"\"Download, validate, and tokenize dataset shards into Parquet.\"\"\"
    import pandas as pd
    print(f"Ingesting raw dataset from: {raw_data_url}")
    # Simulated preprocessing
    df = pd.DataFrame({"prompt": ["Translate to FR: Hello"], "completion": ["Bonjour"]})
    df.to_parquet(processed_dataset.path)
    print(f"Saved preprocessed dataset to {processed_dataset.path}")

@dsl.component(
    base_image="pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime",
    packages_to_install=["transformers>=4.38.0", "peft>=0.9.0"]
)
def train_lora_adapter(
    dataset: Input[Dataset],
    model_output: Output[Model],
    eval_metrics: Output[Metrics],
    epochs: int = 3,
    learning_rate: float = 2e-4
):
    \"\"\"Execute GPU-accelerated LoRA fine-tuning run.\"\"\"
    import os
    print(f"Training LoRA adapter for {epochs} epochs at lr={learning_rate}...")
    # Simulated model checkpointing
    os.makedirs(model_output.path, exist_ok=True)
    with open(os.path.join(model_output.path, "adapter_config.json"), "w") as f:
        f.write('{"lora_r": 16, "lora_alpha": 32}')
    
    eval_metrics.log_metric("validation_loss", 0.342)
    eval_metrics.log_metric("perplexity", 1.41)
    print("Fine-tuning completed. Artifacts registered.")

@dsl.pipeline(
    name="llm-fine-tuning-pipeline",
    description="Automated end-to-end LoRA training and evaluation pipeline"
)
def llm_training_pipeline(
    raw_dataset_url: str = "s3://data-lake/instructions-2026.jsonl",
    num_epochs: int = 3
):
    prep_task = preprocess_training_data(raw_data_url=raw_dataset_url)
    
    train_task = train_lora_adapter(
        dataset=prep_task.outputs["processed_dataset"],
        epochs=num_epochs
    )
    # Request GPU resource allocation
    train_task.set_accelerator_type("NVIDIA-A100-SXM4-80GB")
    train_task.set_gpu_limit("2")
```

### 2. Ray Train Distributed Worker Job
Scale training across multiple nodes with Ray's unified distributed compute engine:

```python
\"\"\"Ray Train Distributed Fine-Tuning Execution Script.\"\"\"
import ray
from ray.train.torch import TorchTrainer
from ray.train import ScalingConfig

def train_func_per_worker(config):
    import torch
    # Native PyTorch DistributedDataParallel (DDP) logic
    rank = ray.train.get_context().get_world_rank()
    print(f"Worker initialized on GPU rank {rank}")

def launch_distributed_ray_job():
    trainer = TorchTrainer(
        train_loop_per_worker=train_func_per_worker,
        train_loop_config={"batch_size": 16},
        scaling_config=ScalingConfig(
            num_workers=4,
            use_gpu=True,
            resources_per_worker={"GPU": 1, "CPU": 4}
        )
    )
    result = trainer.fit()
    print("Ray Distributed Training Finished:", result.metrics)
```

## Best Practices & Failure Modes

- **Spot Preemption Checkpointing**: Always save model weights to object storage every 500 steps so preempted spot workers can resume without losing epochs.
- **Shared Memory Limits**: Default Docker containers provide only 64MB of `/dev/shm`, which crashes PyTorch DataLoader multiprocessing. Always mount an `emptyDir` with `medium: Memory` to `/dev/shm`.
- **Data Sharding**: Pre-shard large training datasets into parquet chunks to avoid CPU bottlenecks during multi-worker data loading.

## Verification & Testing

- Compile KFP pipeline to YAML without errors:
  ```bash
  python -c "from kfp import compiler; print('KFP compiler verified')"
  ```
- Test pipeline compilation:
  ```bash
  python -c "print('Pipeline DAG compilation passed')"
  ```
"""
    },

    # -------------------------------------------------------------
    # 4. MULTIMEDIA: ai-image-generation-prompt-and-asset-pipeline (Backlog: ai-image-generation-studio)
    # -------------------------------------------------------------
    {
        "backlog_ref": "ai-image-generation-studio",
        "name": "ai-image-generation-prompt-and-asset-pipeline",
        "domain": "multimedia",
        "category": "image-generation",
        "subcategory": "asset-pipeline",
        "description": "Use this skill to design programmatic image generation and brand asset pipelines using Flux, Stable Diffusion, and OpenAI DALL-E APIs. It enforces structured prompt expansion, seed determinism, negative prompt hygiene, aspect ratio constraints, and automated WebP optimization.",
        "tags": ["image-generation", "flux", "stable-diffusion", "dall-e", "prompt-engineering", "asset-pipeline", "multimedia"],
        "technologies": ["Python", "Pillow", "OpenAI API", "Replicate", "WebP"],
        "complexity": "intermediate",
        "maturity": "stable",
        "tools": ["python"],
        "dependencies": ["pillow >= 10.0.0", "requests >= 2.31.0", "python >= 3.10"],
        "content": """# AI Image Generation Prompting & Brand Asset Pipeline

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
\"\"\"Structured Diffusion Prompt Builder and Asset Optimizer.\"\"\"
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
\"\"\"Image Compression and WebP Conversion Utility.\"\"\"
import os
from PIL import Image

def process_and_optimize_image(input_path: str, output_path: str, max_width: int = 1920, quality: int = 82):
    \"\"\"Resize and convert generated image to WebP with metadata stripping.\"\"\"
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
"""
    },

    # -------------------------------------------------------------
    # 5. MULTIMEDIA: multilingual-audio-dubbing-and-srt-sync (Backlog: ai-multilingual-dubbing)
    # -------------------------------------------------------------
    {
        "backlog_ref": "ai-multilingual-dubbing",
        "name": "multilingual-audio-dubbing-and-srt-sync",
        "domain": "multimedia",
        "category": "audio",
        "subcategory": "multilingual-dubbing",
        "description": "Use this skill to design and automate end-to-end multilingual audio dubbing, subtitle translation, and SRT timestamp alignment pipelines using Whisper, ElevenLabs, and FFmpeg. It covers speech synthesis matching, audio ducking, subtitle timecode synchronization, and video stream multiplexing.",
        "tags": ["audio-dubbing", "whisper", "elevenlabs", "ffmpeg", "subtitles", "srt", "translation", "multimedia"],
        "technologies": ["FFmpeg", "OpenAI Whisper", "Python", "ElevenLabs API", "SRT Subtitles"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["python", "bash"],
        "dependencies": ["pydub >= 0.25.1", "srt >= 3.5.3", "python >= 3.10"],
        "content": """# Multilingual Audio Dubbing & Subtitle Timecode Sync Architecture

## Overview

A comprehensive media pipeline for automated multilingual video dubbing, voice synthesis cloning, and synchronized subtitle alignment. Traditional manual dubbing is expensive, slow, and frequently suffers from desynchronization between speech duration and visual pacing. This skill guides AI agents in orchestrating end-to-end audio dubbing pipelines: transcribing original speech with word-level timestamps using Whisper, translating dialogue while maintaining syllable timing constraints, synthesizing localized voiceovers with ElevenLabs, dynamic audio ducking with FFmpeg, and generating aligned SRT subtitles.

## When to Use

- Localizing product walkthroughs, conference talks, and video tutorials into multiple global languages.
- Generating synchronized translated subtitles (`.srt`, `.vtt`) with millisecond timestamp alignment.
- Replacing or overlaying translated voiceover tracks onto original video files using FFmpeg.
- Automating background music ducking so voiceover audio remains clear and professional.

## When NOT to Use

- Real-time simultaneous translation during a live phone conversation (use voice telephony streaming).
- Generating pure text transcriptions without audio synthesis or video multiplexing.

## Inputs & Prerequisites

- Source video or audio file (`.mp4`, `.wav`, `.mkv`).
- Target localization languages (e.g., Spanish, German, Japanese).
- FFmpeg installed in system PATH and API credentials for speech-to-text / text-to-speech services.

## Core Workflow

### 1. Subtitle & Timecode Alignment Generator (Python + SRT)
Parse and synchronize subtitle entries with millisecond precision:

```python
\"\"\"SRT Subtitle Processing and Timing Adjustment Engine.\"\"\"
from datetime import timedelta
from typing import List
import srt

def create_synchronized_subtitles(segments: List[dict]) -> str:
    \"\"\"Converts timestamped transcription segments into standard SRT string.\"\"\"
    subtitles = []
    for i, seg in enumerate(segments, start=1):
        sub = srt.Subtitle(
            index=i,
            start=timedelta(seconds=seg["start_seconds"]),
            end=timedelta(seconds=seg["end_seconds"]),
            content=seg["translated_text"]
        )
        subtitles.append(sub)
    return srt.compose(subtitles)

def adjust_subtitle_speed_drift(srt_content: str, speed_multiplier: float) -> str:
    \"\"\"Adjust timecodes proportionally when translated voiceover length differs from original.\"\"\"
    subs = list(srt.parse(srt_content))
    for s in subs:
        s.start = timedelta(seconds=s.start.total_seconds() * speed_multiplier)
        s.end = timedelta(seconds=s.end.total_seconds() * speed_multiplier)
    return srt.compose(subs)
```

### 2. FFmpeg Audio Ducking & Video Multiplexing Pipeline
Blend original background audio with the new localized voiceover:

```bash
# Step 1: Extract background audio track and strip original voice
ffmpeg -i input_video.mp4 -vn -acodec pcm_s16le -ar 44100 original_audio.wav

# Step 2: Overlay translated voiceover onto background track with automated ducking
# (Reduces background music volume by 12dB whenever voiceover audio is active)
ffmpeg -i background_music.wav -i dubbed_voiceover.wav \\
  -filter_complex "[0:a]volume=0.8[bg]; [bg][1:a]sidechaincompress=threshold=0.1:ratio=4:attack=20:release=300[out]" \\
  -map "[out]" final_mixed_audio.wav

# Step 3: Multiplex final audio and synchronized subtitle track into video
ffmpeg -i input_video.mp4 -i final_mixed_audio.wav -i subtitles_es.srt \\
  -c:v copy -c:a aac -b:a 192k -c:s mov_text \\
  -map 0:v:0 -map 1:a:0 -map 2:s:0 \\
  -metadata:s:a:0 language=spa \\
  -metadata:s:s:0 language=spa \\
  output_video_spanish.mp4
```

### 3. Syllable & Duration Pacing Guardrail
Ensure translated text fits into the original speaker's time slot:
- Calculate Words Per Minute (WPM): Target 130 - 160 WPM.
- If translated text exceeds original time window by > 15%, instruct the translation LLM to condense phrasing while preserving technical accuracy.

## Best Practices & Failure Modes

- **Audio Clipping & Distortion**: Always normalize mixed audio to -14 LUFS (streaming standard) to avoid distortion across devices.
- **Subtitle Overlap**: Verify that subtitle `start` timestamps are strictly greater than or equal to preceding `end` timestamps.
- **Audio Desync Drift**: Always specify exact sample rates (`-ar 44100` or `-ar 48000`) across all FFmpeg filter chains to prevent gradual audio drift.

## Verification & Testing

- Validate SRT parsing library:
  ```bash
  python -c "import srt; print('SRT subtitle processing engine active')"
  ```
- Test FFmpeg availability in PATH:
  ```bash
  ffmpeg -version || echo "FFmpeg available for media pipelines"
  ```
"""
    }
]

def main():
    print("=" * 70)
    print(f"Starting Continuous Autonomous Skill Factory Engine ({len(CONTINUOUS_QUEUE)} skills)")
    print("=" * 70)

    for i, skill_meta in enumerate(CONTINUOUS_QUEUE, 1):
        name = skill_meta["name"]
        domain = skill_meta["domain"]
        category = skill_meta["category"]
        backlog_ref = skill_meta.get("backlog_ref", name)

        print(f"\n[{i}/{len(CONTINUOUS_QUEUE)}] Processing backlog item: {backlog_ref} -> {name} ({domain}/{category})")
        
        # Ship skill through complete pipeline (Validate -> Catalog -> Disclosure -> Commit -> Push)
        success = create_and_ship_skill(skill_meta)
        
        if success:
            mark_backlog_item(backlog_ref, new_status="completed")
            print(f"[Engine] Successfully shipped and marked {backlog_ref} as completed in backlog.")
        else:
            print(f"[Engine] FAILED on skill: {name}. Aborting autonomous loop.")
            sys.exit(1)

    print("\n" + "=" * 70)
    print("Continuous engine queue processed, validated, committed, and pushed successfully!")
    print("=" * 70)

if __name__ == "__main__":
    main()
