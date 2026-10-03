# Fable Safe Prompt Technical Reference

## Intent Reframing & False-Positive Mitigation Specification

In automated AI engineering environments, automated safety filters frequently intercept legitimate technical queries that happen to use words common in both software engineering and malicious hacking (e.g. "kill process", "inject script", "exploit bug", "penetration testing"). These false-positive refusals block legitimate workflows.

### Semantic Reframing Flow

```
                      [ User Engineering Prompt ]
                                  |
                                  v
                   [ Intent Maliciousness Filter ]
                                  |
              +-------------------+-------------------+
              |                                       |
    [ Malicious Intent ]                      [ Benign Intent ]
              |                                       |
              v                                       v
    [ Hard Rejection / Block ]            [ Trigger Token Mapping ]
                                                      |
                                                      v
                                          [ Defensive Context Framing ]
                                                      |
                                                      v
                                          [ Neutralized Prompt Egress ]
```

### Safety & Policy Invariants

1. **Zero Policy Bypass**: Fable Safe Prompt is **not** a jailbreak engine. It never attempts to trick models into producing weaponized malware, biological harm, or hate speech.
2. **Intent Preservation**: The resulting prompt must preserve all technical identifiers, error codes, CVE IDs, function names, and structural requirements.
3. **Defensive Recontextualization**: Queries regarding vulnerabilities are framed through defensive engineering, patch verification, and remediation standards.
