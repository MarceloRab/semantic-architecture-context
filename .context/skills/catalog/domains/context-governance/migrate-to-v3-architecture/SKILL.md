---
name: migrate-to-v3-architecture
description: Migration skill for upgrading child projects from PROJECT_ARCHITECTURE.md (v2) to drawer-based architecture (v3). Triggers include 'migrate architecture', 'upgrade architecture', 'migrate to v3', 'drawer migration'. Use when a child project needs to adopt the new architecture model.
version: 1.0.0
tags: [migration, architecture, context, governance]
difficulty: intermediate
estimated_time: 15-20min
---

# Migrate to v3 Architecture

## When to use this skill

- When a child project still uses `PROJECT_ARCHITECTURE.md` as architecture source.
- When upgrading `rabelo-standards` to v3 in downstream projects.
- After running `update-project.ps1` when standards have been updated.
- When `context-orchestrator` reports missing architecture router.

## Prerequisites

- Access to the child project directory.
- Child project has `PROJECT_ARCHITECTURE.md` (old model).
- Child project does NOT yet have `.context/support/architecture_drawer_contract.md`.

## Migration overview

### What changes

| Old (v2) | New (v3) |
| --- | --- |
| `PROJECT_ARCHITECTURE.md` (213 lines, mandatory) | DELETED |
| Architecture in single file | `.context/support/architecture_drawer_contract.md` (router) + 5 drawer files |
| Mandatory read: 5 files | Mandatory read: 5 files (same count, better distribution) |
| Deep details in PROJECT_ARCHITECTURE.md | Deep details in intent-matched drawers |

### What stays the same

- `.cursorrules` (updated)
- `.antigravityignore` (unchanged)
- `.context/active_context.md` (unchanged)
- `project_status.md` (unchanged)
- `.context/support/*` policies (updated)
- Skills in `.context/skills/domains/*` (updated)

### Files to DELETE

```text
PROJECT_ARCHITECTURE.md
```

### Files to CREATE

```text
.context/support/architecture_drawer_contract.md
```

### Files to UPDATE

```text
.cursorrules
.context/support/context_read_order.md
.context/support/context_contract.md
.context/docs/architecture_drawers/01_core_bootstrap.md
.context/docs/architecture_drawers/02_engines_mechanisms.md
.context/docs/architecture_drawers/03_presentation_routes.md
.context/docs/architecture_drawers/04_data_sync_state.md
.context/docs/architecture_drawers/05_ops_risks_observability.md
.context/skills/domains/*/SKILL.md (all skills that reference PROJECT_ARCHITECTURE.md)
```

## Migration workflow

- [ ] **1. Validate prerequisites** — Confirm child project exists and has old architecture model.
- [ ] **2. Read old architecture** — Read `PROJECT_ARCHITECTURE.md` to extract project-specific facts.
- [ ] **3. Create router** — Create `.context/support/architecture_drawer_contract.md` with extracted facts.
- [ ] **4. Distribute to drawers** — Move detailed content to appropriate drawer files.
- [ ] **5. Update .cursorrules** — Replace `PROJECT_ARCHITECTURE.md` with `architecture_drawer_contract.md` in mandatory read order.
- [ ] **6. Update context_read_order.md** — Update core sequence.
- [ ] **7. Update context_contract.md** — Update ownership references.
- [ ] **8. Delete PROJECT_ARCHITECTURE.md** — Remove old file.
- [ ] **9. Update bootstrap_fill_state.md** — Update fill targets list.
- [ ] **10. Validate migration** — Run `context-orchestrator` to confirm `GO`.
- [ ] **11. Update skills** — Mirror updated skills from `rabelo-standards/templates/project-base/.context/skills/domains/*`.

## Content extraction guide

### From PROJECT_ARCHITECTURE.md to router_contract.md

| Section in old file | Section in new file |
| --- | --- |
| Metadata | Metadata (with new source_of_truth) |
| Mission | Mission |
| Scope | Scope |
| System model (CEP) | System model (CEP) |
| Context governance | Context governance integration |
| Quality rules | Quality and safety rules |
| Success criteria | Success criteria |
| Drawer intent routing | Drawer set table |

### From PROJECT_ARCHITECTURE.md to drawer files

| Content type | Destination drawer |
| --- | --- |
| Bootstrap surfaces, init order | `01_core_bootstrap.md` |
| Mechanisms, engines, propagation | `02_engines_mechanisms.md` |
| Routes, presentation, interaction | `03_presentation_routes.md` |
| Sync matrix, preservation, state | `04_data_sync_state.md` |
| Risks, observability, escalation | `05_ops_risks_observability.md` |

## Manual migration commands

```powershell
# Run from rabelo-standards repository
cd C:\Users\Rabelo\projects\rabelo-standards

# Update child project with new standards
.\scripts\update-project.ps1 -TargetPath "C:\Users\Rabelo\projects\YOUR_PROJECT"

# Then manually:
# 1. Read PROJECT_ARCHITECTURE.md in child project
# 2. Create .context/support/architecture_drawer_contract.md
# 3. Update drawer files with project-specific facts
# 4. Delete PROJECT_ARCHITECTURE.md
# 5. Update .cursorrules and context_read_order.md
# 6. Mirror skills from templates/project-base/.context/skills/domains/*
```

## Automated migration script

For convenience, run this migration script after `update-project.ps1`:

```powershell
# migrate-architecture-v3.ps1
# Run in child project directory after standards update

param([string]$ProjectPath)

# 1. Read old PROJECT_ARCHITECTURE.md if exists
$oldArchPath = Join-Path $ProjectPath "PROJECT_ARCHITECTURE.md"
if (-not (Test-Path $oldArchPath)) {
    Write-Host "PROJECT_ARCHITECTURE.md not found - already migrated or new project."
    exit 0
}

# 2. Create new router file
$routerPath = Join-Path $ProjectPath ".context/support/architecture_drawer_contract.md"
if (-not (Test-Path $routerPath)) {
    Write-Host "Creating architecture_drawer_contract.md..."
    # Copy from template and customize
}

# 3. Delete old file after migration
# 4. Update references in other files
# 5. Validate with context-orchestrator
```

## Validation checklist

After migration:

- [ ] `PROJECT_ARCHITECTURE.md` is deleted
- [ ] `.context/support/architecture_drawer_contract.md` exists with project-specific content
- [ ] All drawer files exist with required metadata
- [ ] `.cursorrules` references `architecture_drawer_contract.md` instead of `PROJECT_ARCHITECTURE.md`
- [ ] `context_read_order.md` has correct core sequence
- [ ] `context_contract.md` has correct ownership references
- [ ] `bootstrap_fill_state.md` has updated fill targets
- [ ] `context-orchestrator` returns `GO`

## Rollback

If migration fails:

1. Restore `PROJECT_ARCHITECTURE.md` from version control.
2. Revert `.cursorrules`, `context_read_order.md`, `context_contract.md`.
3. Delete `.context/support/architecture_drawer_contract.md`.
4. Run `context-orchestrator` to validate old model works.

## Related skills

- `context-orchestrator` (validation gate)
- `context-maintenance` (post-migration cleanup)
- `briefing-structural-architecture` (architecture generation)

## Changelog

### v1.0.0 (2026-03-24)

- Initial release for v2 → v3 architecture migration.
- Supports migration from PROJECT_ARCHITECTURE.md to drawer-based model.