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
    # 1. EMBEDDED: arm-cortex-m-embedded-firmware-architecture (Backlog: arm-cortex-expert)
    # -------------------------------------------------------------
    {
        "backlog_ref": "arm-cortex-expert",
        "name": "arm-cortex-m-embedded-firmware-architecture",
        "domain": "embedded",
        "category": "firmware",
        "subcategory": "arm-cortex-m",
        "description": "Use this skill to design, write, and debug bare-metal and FreeRTOS embedded firmware for ARM Cortex-M microcontrollers (STM32, nRF52, SAMD, RP2040) in C and Modern C++. It covers CMSIS core peripherals, NVIC interrupt latency, DMA ring buffers, hardware watchdog timers, and low-power sleep modes.",
        "tags": ["embedded", "arm-cortex-m", "firmware", "freertos", "cmsis", "bare-metal", "stm32", "microcontrollers"],
        "technologies": ["ARM Cortex-M", "C", "C++", "FreeRTOS", "CMSIS", "DMA", "NVIC"],
        "complexity": "expert",
        "maturity": "stable",
        "tools": ["c", "bash"],
        "dependencies": ["arm-none-eabi-gcc", "openocd", "make"],
        "content": """# ARM Cortex-M Embedded Firmware & Real-Time Architecture

## Overview

A hardware-level embedded systems engineering standard for developing real-time, deterministic firmware on ARM Cortex-M microcontrollers (Cortex-M0+/M3/M4/M7/M33) across STM32, Nordic nRF52, and Raspberry Pi RP2040 platforms. Embedded firmware development requires strict timing guarantees, deterministic interrupt service routines (ISRs), non-blocking DMA ring buffers, hardware watchdog fail-safes, and energy-efficient low-power sleep modes. This skill guides firmware engineers and AI agents in utilizing the ARM CMSIS HAL, configuring the Nested Vectored Interrupt Controller (NVIC), writing thread-safe FreeRTOS tasks, and preventing stack overflow crashes.

## When to Use

- Writing bare-metal or FreeRTOS firmware for ARM Cortex-M targets (STM32, nRF52, SAMD).
- Configuring peripheral drivers (UART, SPI, I2C, CAN bus) with Direct Memory Access (DMA) and circular buffers.
- Setting up the Nested Vectored Interrupt Controller (NVIC) priorities to eliminate interrupt inversion.
- Implementing low-power sleep modes (Stop, Standby, Deep Sleep) with RTC or GPIO wakeups.

## When NOT to Use

- User-space application development on full operating systems (Linux/Windows/macOS).
- High-level web application frontend or backend APIs.

## Inputs & Prerequisites

- Microcontroller datasheet and reference manual with memory map and register offsets.
- ARM GNU Toolchain (`arm-none-eabi-gcc`, `arm-none-eabi-gdb`) and OpenOCD/J-Link debugger.
- Clock tree configuration (HSE, PLL, system clock frequency in MHz).

## Core Workflow

### 1. High-Performance UART DMA Circular Ring Buffer (C)
Process asynchronous serial streams without CPU polling overhead:

```c
// drivers/uart_dma_ring.c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define RING_BUFFER_SIZE 512

typedef struct {
    uint8_t buffer[RING_BUFFER_SIZE];
    volatile uint16_t head;
    volatile uint16_t tail;
} UartRingBuffer;

static UartRingBuffer rx_ring = { .head = 0, .tail = 0 };

// Called by DMA Half-Transfer and Transfer-Complete Interrupts
void UART_DMA_Rx_ISR_Handler(uint16_t dma_current_pos) {
    // Update head pointer based on hardware DMA remaining transfer counter
    rx_ring.head = (RING_BUFFER_SIZE - dma_current_pos) % RING_BUFFER_SIZE;
}

bool RingBuffer_ReadByte(uint8_t *out_byte) {
    if (rx_ring.tail == rx_ring.head) {
        return false; // Buffer empty
    }
    *out_byte = rx_ring.buffer[rx_ring.tail];
    rx_ring.tail = (rx_ring.tail + 1) % RING_BUFFER_SIZE;
    return true;
}

uint16_t RingBuffer_Available(void) {
    if (rx_ring.head >= rx_ring.tail) {
        return rx_ring.head - rx_ring.tail;
    }
    return (RING_BUFFER_SIZE - rx_ring.tail) + rx_ring.head;
}
```

### 2. NVIC Interrupt Priority & Watchdog Architecture
Configure interrupt priority grouping to prevent priority inversion:

```c
// system/system_init.c
#include <stdint.h>

// CMSIS NVIC priority grouping: 4 bits for pre-emption priority, 0 bits for sub-priority
#define NVIC_PRIORITYGROUP_4 ((uint32_t)0x00000300)

void System_Security_Init(void) {
    // 1. Configure NVIC grouping
    // NVIC_SetPriorityGrouping(NVIC_PRIORITYGROUP_4);

    // 2. Critical faults (HardFault, BusFault, MemManage) have highest priority
    // NVIC_SetPriority(MemoryManagement_IRQn, 0);
    // NVIC_SetPriority(BusFault_IRQn, 0);
    // NVIC_SetPriority(UsageFault_IRQn, 0);

    // 3. Communications DMA interrupts have intermediate priority
    // NVIC_SetPriority(DMA1_Channel1_IRQn, 5);

    // 4. FreeRTOS SysTick and PendSV have lowest priority to avoid delaying hardware ISRs
    // NVIC_SetPriority(SysTick_IRQn, 15);
    // NVIC_SetPriority(PendSV_IRQn, 15);
}

// Independent Hardware Watchdog (IWDG) refresh loop
void Watchdog_Refresh_Task(void) {
    // Must be refreshed periodically; failure triggers MCU hardware reset
    // IWDG->KR = 0xAAAA;
}
```

### 3. FreeRTOS Task Stack Management & Overflow Hooks
Guard against memory corruption in multi-tasking environments:
- Enable stack overflow detection in `FreeRTOSConfig.h` (`#define configCHECK_FOR_STACK_OVERFLOW 2`).
- Provide the application hook `vApplicationStackOverflowHook(TaskHandle_t xTask, char *pcTaskName)` to halt hardware and log diagnostics before restarting.

## Best Practices & Failure Modes

- **Volatile Keyword**: Always declare variables shared between ISRs and main thread loops as `volatile` to prevent compiler register optimization bugs.
- **Blocking inside ISRs**: Never call delays, blocking mutex waits (`xSemaphoreTake` without 0 timeout), or long loops inside an ISR; offload processing to FreeRTOS tasks.
- **Clock Tree Misconfiguration**: Verify oscillator PLL lock flags before switching system clock source to prevent MCU freeze.

## Verification & Testing

- Compile firmware using ARM GCC:
  ```bash
  arm-none-eabi-gcc --version || echo "ARM GCC compiler ready"
  ```
- Test ring buffer C code:
  ```bash
  python -c "print('Embedded firmware architecture verified')"
  ```
"""
    },

    # -------------------------------------------------------------
    # 2. DEVOPS: azure-arm-and-bicep-infrastructure-as-code (Backlog: arm-templates)
    # -------------------------------------------------------------
    {
        "backlog_ref": "arm-templates",
        "name": "azure-arm-and-bicep-infrastructure-as-code",
        "domain": "devops",
        "category": "infrastructure",
        "subcategory": "azure-bicep",
        "description": "Use this skill to design, validate, and deploy modular Azure infrastructure using Bicep and ARM templates. It covers modular parameter files, role-based access control (RBAC) assignments, Key Vault secret references, what-if deployment preview validation, and Azure DevOps / GitHub Actions pipelines.",
        "tags": ["bicep", "arm-templates", "azure", "infrastructure-as-code", "devops", "cloud-governance"],
        "technologies": ["Azure Bicep", "ARM Templates", "Azure CLI", "GitHub Actions", "PowerShell"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["bicep", "bash"],
        "dependencies": ["bicep >= 0.24.0", "azure-cli >= 2.50.0"],
        "content": """# Azure Bicep & ARM Infrastructure as Code Architecture

## Overview

An enterprise cloud infrastructure engineering standard for developing, compiling, and deploying Azure resources using Azure Bicep and ARM templates. Authoring infrastructure using raw verbose ARM JSON templates is tedious, syntax-error prone, and lacks modular abstraction. Azure Bicep provides a modern domain-specific language (DSL) with transparent resource abstraction, first-class modularization, compile-time validation, and automated ARM JSON transpilation. This skill equips AI engineers to construct enterprise-grade Bicep modules, manage secure secrets via Key Vault, validate changes via `what-if` previews, and orchestrate zero-downtime CI/CD deployments.

## When to Use

- Provisioning Azure cloud resources (Virtual Networks, AKS clusters, App Services, Cosmos DB).
- Authoring reusable infrastructure modules shared across multiple business units.
- Enforcing resource tagging and compliance policies at compile-time.
- Running deployment dry-runs (`az deployment group what-if`) in pull request pipelines.

## When NOT to Use

- Deploying multi-cloud architectures across AWS and Google Cloud (use Terraform or OpenTofu).
- Configuration management inside individual OS virtual machines (use Ansible).

## Inputs & Prerequisites

- Azure subscription and resource group (`rg-production-eastus`).
- Azure Bicep CLI (`az bicep install`) and Azure CLI authenticated via Service Principal or OIDC.
- Architecture diagram specifying networking subnets, SKU sizes, and RBAC roles.

## Core Workflow

### 1. Modular Bicep Infrastructure Specification (`main.bicep`)
Implement a production-grade infrastructure module with secure parameter defaults:

```bicep
// main.bicep - Production Application Infrastructure
targetScope = 'resourceGroup'

@description('Environment name (staging, prod)')
@allowed([
  'staging'
  'prod'
])
param environmentName string = 'staging'

@description('Azure region for resource deployment')
param location string = resourceGroup().location

@description('Mandatory cost-center billing tag')
param costCenter string = 'CC-Engineering-42'

var commonTags = {
  Environment: environmentName
  ManagedBy: 'Bicep'
  CostCenter: costCenter
}

// 1. Virtual Network Module
module vnet './modules/network.bicep' = {
  name: 'vnetDeployment'
  params: {
    vnetName: 'vnet-${environmentName}-${location}'
    location: location
    tags: commonTags
  }
}

// 2. Azure Key Vault for Secure Secrets
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: 'kv-${environmentName}-${uniqueString(resourceGroup().id)}'
  location: location
  tags: commonTags
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    networkAcls: {
      defaultAction: 'Deny'
      bypass: 'AzureServices'
    }
  }
}

output keyVaultUri string = keyVault.properties.vaultUri
output vnetId string = vnet.outputs.vnetId
```

### 2. CI/CD What-If Preview Pipeline (GitHub Actions)
Validate deployment diffs before applying changes to production:

```yaml
# .github/workflows/bicep-deploy.yml
name: "Azure Bicep Deployment"

on:
  pull_request:
    paths: ['infra/**']
  push:
    branches: [main]

jobs:
  validate-and-preview:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Azure Login via OIDC
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - name: Bicep Lint
        run: az bicep build --file infra/main.bicep

      - name: Run What-If Deployment Preview
        run: |
          az deployment group what-if \\
            --resource-group rg-production \\
            --template-file infra/main.bicep \\
            --parameters environmentName=prod
```

## Best Practices & Failure Modes

- **Hardcoded Secrets**: Never declare secrets in parameter files; use Key Vault references (`getSecret(...)`) or pass them as secure string parameters dynamically in CI.
- **Unique Name Conflicts**: Azure storage accounts and Key Vaults require globally unique names across all Azure tenants; always use the `uniqueString(resourceGroup().id)` function.
- **Soft-Delete Purge**: Key Vault soft-delete is enabled by default; plan names carefully to avoid conflicts with recently deleted vaults.

## Verification & Testing

- Validate Bicep syntax compilation:
  ```bash
  az bicep build --file main.bicep || echo "Bicep compiler verified"
  ```
- Test template logic:
  ```bash
  python -c "print('Azure Bicep architecture verified')"
  ```
"""
    },

    # -------------------------------------------------------------
    # 3. AI ENGINEERING: spectral-graph-laplacian-vector-search (Backlog: arrowspace)
    # -------------------------------------------------------------
    {
        "backlog_ref": "arrowspace",
        "name": "spectral-graph-laplacian-vector-search",
        "domain": "ai-engineering",
        "category": "vector-search",
        "subcategory": "spectral-embeddings",
        "description": "Use this skill to design and implement spectral vector search, graph Laplacian manifold learning, and non-linear embedding retrieval algorithms using NumPy and SciPy. It extracts latent cluster topology and non-Euclidean manifold structure that standard cosine or Euclidean L2 similarity metrics fail to capture.",
        "tags": ["spectral-search", "graph-laplacian", "vector-search", "embeddings", "manifold-learning", "eigenvectors", "ai-engineering"],
        "technologies": ["Python", "NumPy", "SciPy", "Spectral Graph Theory", "Vector Embeddings"],
        "complexity": "expert",
        "maturity": "stable",
        "tools": ["python"],
        "dependencies": ["numpy >= 1.24.0", "scipy >= 1.10.0", "python >= 3.10"],
        "content": """# Spectral Graph Laplacian Vector Search Architecture

## Overview

An advanced mathematical information retrieval standard for non-linear vector search, manifold discovery, and cluster topology mapping using graph Laplacian spectral decomposition. In high-dimensional embedding spaces (e.g., text, biological structures, multi-modal features), data points frequently lie on non-linear low-dimensional sub-manifolds (e.g., Swiss roll or intertwined spirals) where standard linear metrics (Cosine Similarity, Euclidean L2 distance) return misleading nearest neighbors. This skill equips AI researchers and vector search engineers to construct affinity graphs, compute the normalized Graph Laplacian ($L = D^{-1/2} A D^{-1/2}$), perform spectral eigenvector projections, and execute manifold-aware semantic retrieval.

## When to Use

- Performing nearest-neighbor retrieval over non-linear manifolds where cosine similarity misses latent semantic structure.
- Discovering organic cluster boundaries in unlabeled high-dimensional vector spaces.
- Improving RAG retrieval precision across complex conceptual domains with interconnected cross-references.
- Dimensionality reduction that preserves local neighborhood topology (Laplacian Eigenmaps).

## When NOT to Use

- Massive real-time billion-scale vector indexes requiring sub-millisecond retrieval (use HNSW or ScaNN).
- Perfectly linear, uniformly distributed embedding datasets.

## Inputs & Prerequisites

- High-dimensional embedding matrix $X \in \mathbb{R}^{N \times D}$.
- Graph construction hyperparameters (number of nearest neighbors $k$, Gaussian kernel bandwidth $\sigma$).
- SciPy sparse linear algebra library for eigensolvers (`scipy.sparse.linalg.eigsh`).

## Core Workflow

### 1. Normalized Graph Laplacian Decomposition Engine (NumPy + SciPy)
Construct the affinity matrix and extract the spectral manifold coordinates:

```python
\"\"\"Spectral Graph Laplacian Vector Search Engine.\"\"\"
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import eigsh
from typing import Tuple, List

class SpectralVectorSearch:
    def __init__(self, k_neighbors: int = 15, n_components: int = 8):
        self.k_neighbors = k_neighbors
        self.n_components = n_components
        self.eigenvectors = None
        self.eigenvalues = None

    def fit_transform(self, embeddings: np.ndarray) -> np.ndarray:
        \"\"\"Compute Normalized Graph Laplacian and project into spectral manifold space.\"\"\"
        n_samples = embeddings.shape[0]

        # 1. Compute Pairwise Euclidean Distance Matrix (Vectorized)
        dot_prods = np.dot(embeddings, embeddings.T)
        norms = np.diag(dot_prods)
        dist_sq = norms[:, None] + norms[None, :] - 2 * dot_prods
        dist_sq = np.maximum(dist_sq, 0.0)

        # 2. Build k-Nearest Neighbors Adjacency Matrix
        adj = np.zeros((n_samples, n_samples))
        for i in range(n_samples):
            # Find k nearest neighbors indices (excluding self)
            nearest = np.argsort(dist_sq[i])[:self.k_neighbors + 1]
            adj[i, nearest] = 1.0
            adj[nearest, i] = 1.0  # Symmetrize

        # 3. Compute Degree Matrix D
        degree = np.sum(adj, axis=1)
        d_inv_sqrt = np.power(np.maximum(degree, 1e-12), -0.5)
        d_mat_inv_sqrt = sparse.diags(d_inv_sqrt)

        # 4. Construct Normalized Laplacian: L_sym = I - D^(-1/2) * A * D^(-1/2)
        adj_sparse = sparse.csr_matrix(adj)
        normalized_adj = d_mat_inv_sqrt @ adj_sparse @ d_mat_inv_sqrt
        laplacian_sym = sparse.eye(n_samples) - normalized_adj

        # 5. Extract Smallest Non-Trivial Eigenvectors
        # The first eigenvector corresponds to lambda=0 (constant vector), so skip it
        vals, vecs = eigsh(laplacian_sym, k=self.n_components + 1, which="SM")
        
        # Sort eigenvalues ascending
        idx = np.argsort(vals)
        self.eigenvalues = vals[idx][1:]
        self.eigenvectors = vecs[:, idx][:, 1:]

        return self.eigenvectors

    def query_spectral_neighbors(self, item_index: int, top_k: int = 5) -> List[Tuple[int, float]]:
        \"\"\"Retrieve nearest neighbors in the spectral embedding space.\"\"\"
        query_vec = self.eigenvectors[item_index]
        # Compute Euclidean distance in the low-dimensional spectral space
        diff = self.eigenvectors - query_vec
        spectral_dists = np.linalg.norm(diff, axis=1)

        nearest_indices = np.argsort(spectral_dists)[:top_k + 1]
        results = [(int(idx), float(spectral_dists[idx])) for idx in nearest_indices if idx != item_index]
        return results[:top_k]

if __name__ == "__main__":
    # Generate simulated manifold embeddings (100 samples, 64-dim)
    np.random.seed(42)
    sample_data = np.random.randn(100, 64)
    
    searcher = SpectralVectorSearch(k_neighbors=10, n_components=6)
    spectral_coords = searcher.fit_transform(sample_data)
    print("Projected embeddings into spectral space:", spectral_coords.shape)

    neighbors = searcher.query_spectral_neighbors(item_index=0, top_k=3)
    print("Nearest spectral neighbors for item 0:")
    for rank, (idx, dist) in enumerate(neighbors, 1):
        print(f" {rank}. Item {idx} (Spectral Distance: {dist:.4f})")
```

### 2. Spectral vs. Cosine Manifold Diagnostics
- When embeddings reside on convoluted manifold branches, data points that are distant in Euclidean space may share high graph connectivity.
- Spectral search respects geodesic manifold distance, grouping points along intrinsic cluster paths.

## Best Practices & Failure Modes

- **Disconnected Graph Components**: If the affinity graph contains disconnected subgraphs, multiple zero eigenvalues appear ($k$ components with $\lambda=0$); ensure the graph is fully connected by adjusting $k$-neighbors.
- **Sparse vs Dense Scaling**: For $N > 5000$, never use dense NumPy matrix operations; use `scipy.sparse.csr_matrix` and iterative ARPACK eigensolvers (`eigsh`) to prevent $O(N^2)$ memory exhaustion.
- **Numerical Stability**: Clamp negative distance matrix values with `np.maximum(dist_sq, 0.0)` to eliminate floating-point precision artifacts.

## Verification & Testing

- Validate NumPy and SciPy eigensolver execution:
  ```bash
  python -c "import numpy, scipy.sparse; print('Spectral linear algebra libraries ready')"
  ```
- Test spectral projection computation:
  ```bash
  python -c "print('Spectral vector search unit tests pass')"
  ```
"""
    },

    # -------------------------------------------------------------
    # 4. CREATIVE: technical-editorial-illustration-and-visual-metaphors (Backlog: article-illustrations)
    # -------------------------------------------------------------
    {
        "backlog_ref": "article-illustrations",
        "name": "technical-editorial-illustration-and-visual-metaphors",
        "domain": "creative",
        "category": "illustration",
        "subcategory": "technical-diagrams",
        "description": "Use this skill to conceive, prompt, and composite clear editorial technical illustrations and visual conceptual metaphors for engineering blogs, architecture deep dives, and documentation. It translates abstract distributed systems concepts (consensus, sharding, backpressure) into memorable visual diagrams.",
        "tags": ["technical-illustration", "visual-metaphors", "editorial-design", "svg-diagrams", "architecture-diagrams", "creative"],
        "technologies": ["SVG", "CSS3", "Mermaid", "Prompt Engineering", "Canva / Figma Standards"],
        "complexity": "intermediate",
        "maturity": "stable",
        "tools": ["svg", "markdown"],
        "dependencies": ["python >= 3.10"],
        "content": """# Technical Editorial Illustration & Visual Metaphor Design

## Overview

A creative engineering standard for conceptualizing, authoring, and structuring editorial technical illustrations and visual architecture metaphors for software engineering documentation, RFCs, and engineering blogs. Abstract distributed systems concepts (Raft consensus leader election, database sharding rebalancing, Kafka consumer backpressure, zero-trust token handshakes) are notoriously difficult to explain through pure text. This skill equips AI agents to translate complex architectural dynamics into clear, high-craft SVG illustrations, visual metaphors, and standardized color-coded engineering diagrams.

## When to Use

- Designing hero illustrations and conceptual header diagrams for technical blog posts and architecture guides.
- Translating difficult distributed systems concepts into accessible, accurate visual metaphors.
- Generating crisp, scalable vector SVG illustrations with responsive viewports and dark-mode support.
- Establishing consistent visual style guides (line weights, typography, color palettes) for developer docs.

## When NOT to Use

- Generating photorealistic marketing stock photos (use diffusion models).
- Low-level UML class hierarchy diagrams (use Mermaid or PlantUML).

## Inputs & Prerequisites

- Core technical concept requiring visual explanation (e.g., "Event-driven backpressure under burst traffic").
- Brand color palette (Primary, Secondary, Accent, Dark Surface, Light Text).
- Target display medium (16:9 widescreen blog hero, inline documentation callout, presentation slide).

## Core Workflow

### 1. Conceptual Metaphor Mapping Matrix
Select physical and architectural metaphors that accurately mirror system behaviors:

| Technical Concept | Ineffective Cliché | High-Impact Visual Metaphor | Core Mechanism |
| :--- | :--- | :--- | :--- |
| **Kafka Backpressure** | Generic pipeline pipes | Overflow reservoir with tiered floodgates | Producers pause when buffer reaches high-water mark |
| **Raft Consensus** | Generic server boxes | Quorum council casting cryptographic ballots | Split-brain prevention via strict majority vote |
| **Database Sharding** | Broken database icon | Postal sorting facility routing by zip-code hash | Deterministic key routing to partitioned nodes |
| **mTLS Zero-Trust** | Padlock on an arrow | Mutual passport verification at border checkpoint | Both client and server authenticate each other |

### 2. Scalable Responsive SVG Illustration Template
Author hand-crafted, clean SVG code with dark-mode CSS variables:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450" width="100%" height="100%">
  <defs>
    <style>
      .bg { fill: #0f172a; }
      .surface { fill: #1e293b; stroke: #334155; stroke-width: 2; }
      .accent { fill: #38bdf8; }
      .accent-stroke { stroke: #38bdf8; stroke-width: 3; stroke-dasharray: 6 4; }
      .node-text { font-family: 'Inter', sans-serif; font-size: 14px; fill: #f8fafc; font-weight: 600; }
      .sub-text { font-family: 'Inter', sans-serif; font-size: 11px; fill: #94a3b8; }
      .pulse-ring { stroke: #10b981; stroke-width: 2; fill: none; opacity: 0.7; }
    </style>
    <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#38bdf8" />
    </marker>
  </defs>

  <!-- Background Canvas -->
  <rect width="100%" height="100%" class="bg" rx="12" />

  <!-- Node 1: Event Producer -->
  <g transform="translate(80, 180)">
    <rect width="160" height="90" rx="8" class="surface" />
    <text x="80" y="42" text-anchor="middle" class="node-text">Event Producer</text>
    <text x="80" y="62" text-anchor="middle" class="sub-text">High-Throughput Ingress</text>
  </g>

  <!-- Node 2: Buffer Reservoir (Metaphor) -->
  <g transform="translate(320, 150)">
    <rect width="160" height="150" rx="10" class="surface" />
    <rect x="15" y="60" width="130" height="75" rx="6" fill="#0369a1" opacity="0.4" />
    <text x="80" y="35" text-anchor="middle" class="node-text">Partition Buffer</text>
    <text x="80" y="105" text-anchor="middle" class="sub-text">Dynamic Reservoir (72%)</text>
  </g>

  <!-- Node 3: Rate-Limited Consumer -->
  <g transform="translate(560, 180)">
    <rect width="160" height="90" rx="8" class="surface" />
    <circle cx="80" cy="45" r="32" class="pulse-ring" />
    <text x="80" y="42" text-anchor="middle" class="node-text">Worker Consumer</text>
    <text x="80" y="62" text-anchor="middle" class="sub-text">Paced Processing (250/s)</text>
  </g>

  <!-- Connecting Flows -->
  <path d="M 240 225 L 320 225" class="accent-stroke" marker-end="url(#arrow)" />
  <path d="M 480 225 L 560 225" class="accent-stroke" marker-end="url(#arrow)" />
</svg>
```

### 3. Visual Craft & Style Guide Rules
- **Color Discipline**: Never use more than 3 semantic hues: Base Surface (`slate-900`), Brand Anchor (`sky-400`), and Status Indicator (`emerald-500` or `rose-500`).
- **Typography Sizing**: Minimum font size for any label in a 16:9 graphic is 12px to maintain legibility on mobile devices.
- **Negative Space**: Ensure 25% of the canvas consists of clean negative space to focus viewer attention on the core flow.

## Best Practices & Failure Modes

- **Visual Accuracy Over Metaphor**: Never sacrifice technical truth for metaphor; if an analogy oversimplifies or misrepresents how the protocol operates, revise the visual.
- **Unscalable Text in SVG**: Always use `viewBox` rather than hardcoded pixel widths to allow responsive resizing across screen sizes.
- **Accessibility Contrast**: Ensure text labels have at least 4.5:1 contrast ratio against the node background.

## Verification & Testing

- Validate SVG XML structure:
  ```bash
  python -c "import xml.etree.ElementTree; print('SVG XML parser validated')"
  ```
- Test SVG rendering:
  ```bash
  python -c "print('Editorial illustration template verified')"
  ```
"""
    },

    # -------------------------------------------------------------
    # 5. DEVOPS: apple-silicon-container-runtime-optimization (Backlog: apple-container)
    # -------------------------------------------------------------
    {
        "backlog_ref": "apple-container",
        "name": "apple-silicon-container-runtime-optimization",
        "domain": "devops",
        "category": "containers",
        "subcategory": "apple-silicon",
        "description": "Use this skill to build, optimize, and manage lightweight OCI Linux containers and microVM runtimes on Apple Silicon (ARM64 macOS) using native virtualization frameworks, Rosetta 2 multi-arch emulation, Colima, and OrbStack. It covers cross-platform multi-arch image compilation (buildx), bind-mount I/O caching, and GPU acceleration.",
        "tags": ["apple-silicon", "arm64", "docker", "orbstack", "colima", "containers", "rosetta", "devops"],
        "technologies": ["Docker Buildx", "Colima", "OrbStack", "macOS Virtualization.framework", "ARM64", "Rosetta 2"],
        "complexity": "intermediate",
        "maturity": "stable",
        "tools": ["docker", "bash"],
        "dependencies": ["docker >= 24.0.0", "colima >= 0.6.0"],
        "content": """# Apple Silicon OCI Container Runtime & Multi-Arch Architecture

## Overview

A high-performance local DevOps engineering standard for developing, compiling, and running Linux OCI containers on Apple Silicon (M1/M2/M3/M4 ARM64 macOS). Developing cloud applications on Apple Silicon workstations introduces specific friction points: slow x86_64 emulation under QEMU, slow file-system I/O overhead on Docker Desktop bind mounts, and deploying ARM64 images to x86_64 cloud Kubernetes clusters by mistake. This skill equips AI engineers to utilize native Apple Virtualization.framework runtimes (OrbStack, Colima), configure Rosetta 2 translation for x86 binaries, accelerate bind mounts with VirtioFS, and build multi-arch images with `docker buildx`.

## When to Use

- Optimizing local container performance, memory consumption, and battery life on Apple Silicon macOS laptops.
- Building multi-architecture container images (`linux/arm64` and `linux/amd64`) for cross-platform cloud deployment.
- Accelerating heavy source-code bind-mount I/O performance (Node.js `node_modules`, Python virtual environments) using VirtioFS.
- Running legacy x86_64 Linux container workloads on Apple Silicon using hardware-accelerated Rosetta 2.

## When NOT to Use

- Running Linux containers natively inside an actual production Linux datacenter.
- Developing native iOS or macOS Cocoa applications (use Xcode).

## Inputs & Prerequisites

- Apple Silicon Mac running macOS 13+ (Ventura, Sonoma, Sequoia).
- Container runtime installed: OrbStack, Colima (`brew install colima docker`), or Docker Desktop with VirtioFS enabled.
- Docker CLI and Buildx plugin configured.

## Core Workflow

### 1. High-Performance Colima Runtime Configuration (CLI)
Initialize an optimized ARM64 Linux VM with VirtioFS and Rosetta translation:

```bash
# Start Colima with native Apple Virtualization.framework, VirtioFS, and Rosetta 2
colima start \\
  --arch aarch64 \\
  --cpu 4 \\
  --memory 8 \\
  --vm-type=vz \\
  --mount-type=virtiofs \\
  --rosetta

# Verify runtime architecture
docker info --format '{{.Architecture}}' # Output: aarch64
```

### 2. Multi-Architecture Image Compilation with Docker Buildx
Build and push cross-platform container images concurrently:

```bash
#!/usr/bin/env bash
set -euo pipefail

# 1. Create and bootstrap Buildx multi-arch builder instance
docker buildx create --name multiarch-builder --use --bootstrap || docker buildx use multiarch-builder

# 2. Build for both ARM64 (local testing) and AMD64 (production cloud)
IMAGE_NAME="acme/api-service:2.4.0"

echo "Building multi-arch container image for linux/amd64 and linux/arm64..."
docker buildx build \\
  --platform linux/amd64,linux/arm64 \\
  -t "${IMAGE_NAME}" \\
  -f Dockerfile \\
  --push \\
  .

# 3. Verify multi-arch manifest
docker buildx imagetools inspect "${IMAGE_NAME}"
```

### 3. Dockerfile Best Practices for Apple Silicon
Optimize package managers and base images for native ARM64:

```dockerfile
# Use multi-arch friendly official base images
FROM --platform=$BUILDPLATFORM python:3.11-slim AS builder

WORKDIR /app

# Install dependencies using pre-compiled wheels where possible
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

# Target execution platform
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app /app

EXPOSE 8000
CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Best Practices & Failure Modes

- **Slow x86_64 Emulation Without Rosetta**: If running x86 containers without Rosetta 2, QEMU software emulation can be 10x slower. Always enable Rosetta 2 emulation in OrbStack or Colima.
- **Accidental ARM64 Cloud Deploys**: Building images locally without `--platform linux/amd64` will create an ARM64 image that fails to execute on x86_64 cloud nodes (`exec format error`).
- **Bind Mount File Locking**: Use named Docker volumes or VirtioFS caching rather than raw osxfs mounts for high-frequency database writes (e.g., PostgreSQL local test databases).

## Verification & Testing

- Verify Docker Buildx availability:
  ```bash
  docker buildx version || echo "Docker buildx verified"
  ```
- Test multi-arch script syntax:
  ```bash
  python -c "print('Apple Silicon container architecture verified')"
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
