# Contributing to Semantic Architecture Context (SAC)

Thank you for your interest in contributing to SAC! We welcome contributions, bug reports, documentation improvements, and architectural extensions.

---

## Code of Conduct

All contributors are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## Development Prerequisites

- **Python:** Version 3.11 or higher (standard library only for `src/`).
- **Node.js:** Version 22 or higher (for `mcp/server.mjs`).
- **Git:** Standard git client.

---

## Local Setup & Quickstart

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/semantic-architecture-context.git
   cd semantic-architecture-context
   ```

2. **Install MCP dependencies:**
   ```bash
   cd mcp
   npm ci
   cd ..
   ```

3. **Run smoke tests:**
   ```bash
   node mcp/smoke.mjs
   ```

4. **Verify core engine CLI:**
   ```bash
   python src/sac_scan.py list-domains --root .
   ```

---

## Architecture & Code Guidelines

1. **Python Engine (`src/`):**
   - Must use **Python standard library only**. Do not introduce external dependencies in `src/`.
   - Preserve error handling contracts: environment errors must use `sac.environment.*` structured error codes.
   - Maintain parity between CLI subcommands and MCP tools.

2. **MCP Adapter (`mcp/`):**
   - Thin adapter layer forwarding commands to `src/sac_scan.py`.
   - Single Source of Truth (SSOT) for version is `mcp/package.json`.

3. **Public Skills (`skills/`):**
   - All skill files must use **relative file paths** (`./PROMPT.md`, `./SKILL.md`).
   - No absolute local machine paths or private monorepo references.
   - Ensure skill frontmatters remain distinct with non-overlapping trigger descriptions.

---

## Automated Hygiene & Quality Gates

Before opening a Pull Request, run the local verification gates:

```bash
# 1. Hygiene Gate (checks for bytecode, machine paths, forbidden references)
python .github/scripts/check_hygiene.py

# 2. Version SSOT Gate
python .github/scripts/check_version.py

# 3. MCP Smoke Tests (runs full CLI ≡ MCP parity suite)
node mcp/smoke.mjs

# 4. In-Code Tag Validation
python src/sac_scan.py validate --root . --warning-only
```

All four checks must pass with exit code `0`.

---

## Submitting a Pull Request (PR)

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. Commit your changes following [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat(engine): add support for python comment markers`
   - `fix(mcp): resolve edge case in domain membership check`
   - `docs(adr): add ADR-001 for multi-language parser`
3. For architectural or semantic changes, reference the corresponding ADR in `docs/adr/`.
4. Open a PR against `main`. CI runs automatically without requiring external secrets or credentials.
