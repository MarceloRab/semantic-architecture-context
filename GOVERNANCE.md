# Governance Model — Semantic Architecture Context (SAC)

This document defines how the Semantic Architecture Context (SAC) standard, its core engine, MCP interfaces, and governance skills evolve over time.

---

## 1. Principles of Evolution

SAC is governed by principles of **determinism, contract safety, and verifiable evidence**:

1. **In-Code Tags are SSOT:** Source code comments (`// SAC:ARCH:...`, `// SAC:REGR:...`, `// SAC:DEPRECATED:...`) are the immutable runtime source of truth. Indexes and manifests are derived boundaries, not authorities.
2. **Explicit Errors Beat Guessed Recovery:** No silent fallback, heuristic guessing, or error masking is permitted. If an environment or syntax precondition is violated, the system emits an explicit, actionable error.
3. **Surgical Evolution:** Changes must be minimal, traceable, and strictly scoped. Structural changes require formal Architectural Decision Records (ADRs).
4. **Interface Parity:** Every capability exposed through the Model Context Protocol (MCP) server must have an equivalent CLI command with identical structured output.
5. **Runtime Minimalism:** The Python engine (`src/`) must remain 100% Python standard library (`stdlib-only`) with zero third-party dependencies.

---

## 2. Standard Evolution Workflow

Any material semantic change, syntax extension, pipeline modification, or contract adjustment follows a 4-stage lifecycle:

```
[ 1. GitHub Issue ] ──> [ 2. Architecture Decision Record (ADR) ] ──> [ 3. Pull Request ] ──> [ 4. Review & Merge ]
```

### Stage 1: Issue & Problem Definition
- Open a GitHub Issue detailing the problem, evidence of limitation, failure mode, or workflow bottleneck.
- Issues must include reproduction steps, affected domains/languages, and expected behavior.

### Stage 2: Architecture Decision Record (ADR)
- For any change affecting:
  - Tag grammar or comment markers;
  - Error codes or exit behaviors;
  - Protocol payloads or MCP tool schemas;
  - Domain manifest (`.sac/domains.md`) format or semantics;
  - Execution overlay pipeline stages (L0–L4);
- An ADR must be drafted under `docs/adr/ADR-XXX-<title>.md` using the template provided in [`docs/adr/README.md`](docs/adr/README.md).
- The ADR documents context, alternatives considered, chosen decision, invariants, and backward compatibility paths.

### Stage 3: Implementation & Pull Request (PR)
- Implement changes adhering strictly to the approved ADR.
- PRs must satisfy all automated gates:
  - Hygiene gate (`python .github/scripts/check_hygiene.py`);
  - Version consistency gate (`python .github/scripts/check_version.py`);
  - Smoke tests (`node mcp/smoke.mjs`);
  - Engine validation (`python src/sac_scan.py validate`).

### Stage 4: Adversarial Review & Merge
- Changes are reviewed against the Definition of Done (DoD) of the corresponding ADR.
- All criteria must have reproducible evidence before approval and merge into `main`.

---

## 3. Governance Boundaries

| Area | Governed In | Process |
|---|---|---|
| Tag Grammar & Semantics | `docs/SAC_V2.md`, `skills/sac-context/` | ADR required |
| Execution Gates & Overlay | `skills/sac-execution-overlay/` | ADR required |
| Domain Onboarding & Tag Maintenance | `skills/sac-onboard/` | ADR required |
| Core Engine (`src/`) | `src/sac_engine.py`, `src/sac_domains.py` | Issue + PR + Smoke |
| MCP Server Adapter (`mcp/`) | `mcp/server.mjs`, `mcp/package.json` | Issue + PR + Smoke |
| Installer & Tooling | `install.py`, `templates/` | Issue + PR |

---

## 4. Release & Versioning Policy

SAC adheres to [Semantic Versioning 2.0.0](https://semver.org/):
- **MAJOR (`X.0.0`):** Incompatible tag grammar changes, removed MCP tools, or breaking protocol alterations.
- **MINOR (`0.X.0`):** New tag types, new MCP tools, new supported languages, or backward-compatible feature additions.
- **PATCH (`0.0.X`):** Bug fixes, parser optimizations, documentation improvements, and internal refactors.

Pre-1.0.0 releases (`0.x.y`) maintain strict stability guarantees on core tag contracts while allowing rapid evolution of tooling and host adapters.
