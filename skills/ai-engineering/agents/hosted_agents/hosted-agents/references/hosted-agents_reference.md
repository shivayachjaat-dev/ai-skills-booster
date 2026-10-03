# Hosted Agent Sandboxed Runtime Reference

## Sandboxing Architecture for Background AI Coding Agents

Running autonomous AI coding agents in production involves executing untrusted generated code, installing arbitrary dependencies, and running shell scripts. To prevent host privilege escalation, data exfiltration, and resource exhaustion, agents must execute inside isolated, ephemeral sandbox runtimes.

### Sandboxed Execution Topology

```
                  [ Agent Task Dispatcher ]
                              |
                              v
                [ Sandbox Lifecycle Controller ]
                              |
            +-----------------+-----------------+
            |                                   |
            v                                   v
  [ Ephemeral Provisioning ]         [ Resource Quota Guard ]
  - Firecracker MicroVM / Container  - CPU & Memory ceilings
  - Isolated overlay filesystem      - Egress network whitelist
            |                                   |
            +-----------------+-----------------+
                              |
                              v
                 [ Execution & Output Capture ]
                              |
                              v
             [ Artifact Extraction & Teardown ]
```

### Sandbox Security Standards

1. **Ephemeral Lifecycle**: Sandboxes exist only for the duration of the task. All temporary files and disk states are purged upon exit or timeout.
2. **Resource Boundaries**: Strict CPU cores (`1-2 cores`) and RAM quotas (`512MB - 2GB`) prevent runaway infinite loops or fork-bombs.
3. **Network Egress Filtering**: Restrict network egress to authorized package registries (e.g. PyPI, npm) and block internal VPC IP ranges (`10.0.0.0/8`, `192.168.0.0/16`, AWS metadata `169.254.169.254`).
