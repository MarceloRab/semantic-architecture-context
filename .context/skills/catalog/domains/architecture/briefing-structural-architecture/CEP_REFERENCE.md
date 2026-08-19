# CEP Reference — Detailed Brief Layout

> This file is the reference for producing **Artifact B** (detailed CEP brief) in `expanded` mode.
> Do not read this file in `default` mode — it is only needed when generating the full architecture brief.

---

## Core Philosophy

> **Non-omissive + Non-verbose = Intelligent compression.**
> Every mechanism appears. No mechanism is over-explained.

## Definitions

- **Mechanism**: Any systemic behavior that alters state, integrates systems, executes tasks, validates domain, or controls flow.
  Examples: auth, routing, state management, persistence, sync, queues, cache, fallback, retry, outbox, notifications, AI, scheduled jobs, observability, migrations, security, permissions, feature flags, billing, etc.
- **Non-omissive**: Every mechanism appears in the **Mechanism Catalog** (even as 1 line).
- **Non-verbose**: Deep details live only as **pointers** to sections/files.

## Compression Rules (anti-verbosity)

1. Each section has a **hard line limit** (defined below).
2. If a section exceeds its limit:
   - Summarize to fit, AND
   - Move overflow to **"Pointers & Evidence"**.
3. **Forbidden content**:
   - History, long justifications, storytelling
   - Generic term repetition
   - "Didactic explanations" that don't help operate/maintain

---

## 🎨 Visual Requirements (MANDATORY)

The output brief **must** include rich visual elements. Plain prose walls are **rejected**.

### Required Visual Elements

| Element                           | Minimum            | Where                                                                          |
| --------------------------------- | ------------------ | ------------------------------------------------------------------------------ |
| ASCII/Unicode diagram with arrows | 3                  | §2 Boot Pipeline, §4 High-Level Map, §6 Mechanism Topology                     |
| Tables with headers               | 6                  | §1 DI, §3 Mechanism Catalog, §5 Modules, §7 Routes, §9 State, §10 Integrations |
| Status indicators                 | In every table row | 🟢 Active 🟡 Partial 🔴 Missing ⚪ N/A                                         |
| Flow notation with arrows         | 1 per flow         | §8 Critical Flows                                                              |

### Arrow & Symbol Reference (use these)

```text
Arrows:     →  ←  ↔  ⇒  ⇐  ⇔  ──▶  ◀──
Hierarchy:  ├── └── │   ┌── ┐   ┘   ┤
Boxes:      ┌─────┐  │     │  └─────┘
Status:     🟢 active  🟡 partial  🔴 missing  ⚪ n/a
Separators: ─── ═══ ···
Bullets:    ▸ ▹ ◆ ◇ ● ○
```

### Optional (Recommended for complex projects)

- **Mermaid diagrams** for flows that benefit from rendered visualization.

---

## Output Layout (Mandatory Sections for Artifact B / CEP Brief)

> **Title**: `PROJECT CEP ARCHITECTURE BRIEF`
> **Last updated**: (current date)
> **Sources used**: short list (max 8 items)

---

### §0 — Executive Card (max 20 lines)

Rapid orientation: what it is, how it's assembled, main risks.

| Item                           | Count     |
| ------------------------------ | --------- |
| What it is / who it's for      | 1-2 lines |
| Core (how it's assembled)      | 2-3 lines |
| Engines (top 5-8 mechanisms)   | 2-3 lines |
| Presentation (how UI is built) | 1-2 lines |
| SSOT (where truth lives)       | 1 line    |
| System invariants              | 3         |
| Hard/irreversible decisions    | 3         |
| Top technical risks            | 3         |

**Example (format reference):**

```text
▸ Core: DI registers all services at boot; lazy initialization for heavy deps.
▸ Engines: Auth, Sync, AI/LLM, Notifications, Cache, Retry.
▸ Presentation: Route-based navigation with per-route dependency binding.
▸ SSOT: Local DB is single source of truth; remote is mirror only.
▸ Invariant: All writes go to local first, then sync outbound.
▸ Hard Decision: Drift chosen as local DB — no ORM swap viable.
▸ Risk: Sync conflicts on multi-device with weak connectivity.
```

---

### §1 — Composition Root & Global DI (table, max 25 lines)

Goal: See the trunk of the system — what gets injected and how.

| Global Service    | Responsibility | Lifecycle      | Consumers   | Registration Point | Status |
| ----------------- | -------------- | -------------- | ----------- | ------------------ | ------ |
| AuthService       | Authentication | Singleton      | All modules | `InitialBinding`   | 🟢     |
| SyncEngine        | Data sync      | Lazy singleton | Repos, Jobs | `CoreModule`       | 🟢     |
| _...more rows..._ |                |                |             |                    |        |

**Rules:**

- `Lifecycle`: Singleton / Lazy / Factory / Session-scoped / Transient
- `Registration Point`: file/class/binding where it's registered
- If unknown → mark `❓` and add to **Gaps**

---

### §2 — Boot Pipeline (ASCII diagram, 12–25 lines)

Goal: Exact path from `main()` to the app running.

```text
main()
  → bootstrap(env/flags/config)
  → registerCoreDI()
  → registerModules()
  → runApp(App)
      → AppRoot(...)
          → initialBinding(...)
          → routeDefinitions(...)
          → routing(...)
```

_Reflect the actual boot sequence of the project._

---

### §3 — High-Level Map (ASCII diagram, 12–25 lines)

Must include: **arrows**, **layer boundaries**, **clear labels**.

```text
┌─────────────────────────────────────────────────┐
│                    UI Layer                      │
│  [Views] ──→ [Controllers/ViewModels]            │
└──────────────────────┬──────────────────────────┘
                       │ events/state
                       ▼
┌─────────────────────────────────────────────────┐
│               Domain / Services                  │
│  [UseCases] ──→ [Services] ──→ [Validators]      │
└──────────┬───────────────────────┬──────────────┘
           │                       │
           ▼                       ▼
┌──────────────────┐    ┌──────────────────────────┐
│   Local Storage  │    │    Remote / External      │
│  [ORM/SQLite]    │    │  [Cloud DB] [REST API]    │
│  [Preferences]   │    │  [AI/ML] [Notifications]  │
└──────────────────┘    └──────────────────────────┘
```

---

### §4 — Mechanism Catalog (table, max 35 lines)

**Goal**: Guarantee non-omission. One row per mechanism. Stable IDs for cross-reference.

| ID                | Mechanism | Where (module/file)          | Trigger        | SSOT/State     | Input → Output         | Typical Failures  | Observability | Status |
| ----------------- | --------- | ---------------------------- | -------------- | -------------- | ---------------------- | ----------------- | ------------- | ------ |
| MECH-001          | Auth      | `lib/auth/`                  | App start      | Firebase Auth  | Credentials → Token    | Token expiry      | 🟢 Logs       | 🟢     |
| MECH-002          | Sync      | `lib/services/sync_svc.dart` | Timer + manual | Local → Remote | Local changes → Remote | Conflict, offline | 🟡 Partial    | 🟡     |
| _...more rows..._ |           |                              |                |                |                        |                   |               |        |

**Rules:**

- `ID` is stable: `MECH-001`, `MECH-002`, ... (used in Pointers & Evidence)
- Every row must have **Trigger** (when it happens) and **SSOT** (who owns truth)
- If "Where" is unknown → mark `❓ UNKNOWN` and add to **Gaps**
- If mechanism depends on 3rd party → cite it
- If no evidence → mark `INFERRED` and add to **Gaps**
- **Status column is mandatory**: 🟢 🟡 🔴 ⚪

---

### §5 — Mechanism Topology (ASCII diagram, max 35 lines)

Goal: Show how mechanisms chain together — the "engine room" wiring.

```text
[UI Action] ──→ [Controller] ──→ [UseCase] ──→ [Repository]
                                    │                │
                                    ▼                ▼
                                [Validator]     [Local DB SSOT]
                                    │                │
                                    ▼                ▼
                                [Outbox] ──→ [Sync Engine] ──→ [Remote]
                                    │
                                    ▼
                            [NotifyManager/Jobs] ──→ [Push/DeepLink] ──→ [UI Route]
```

_Adapt to the actual mechanisms discovered in the project._

---

### §6 — Module Boundaries (table, max 35 lines)

Goal: Audit the branches — what each module owns, uses, and produces.

| Module       | Responsibility | Entry points (Routes/Triggers) | Controllers | Repos/Services | Engines used       | Outputs (views/events) | Status |
| ------------ | -------------- | ------------------------------ | ----------- | -------------- | ------------------ | ---------------------- | ------ |
| Home         | Dashboard      | `/home`                        | HomeCtrl    | UserRepo       | MECH-001, MECH-002 | HomeView, NavEvents    | 🟢     |
| _...more..._ |                |                                |             |                |                    |                        |        |

---

### §7 — Routes → Bindings → Views (table, max 40 lines)

Goal: "How do I get to the UI?" — complete presentation layer mapping.

| Route        | View     | Binding     | Controller(s)  | Observed State      | Engines Touched    | Status |
| ------------ | -------- | ----------- | -------------- | ------------------- | ------------------ | ------ |
| `/home`      | HomeView | HomeBinding | HomeController | userList, isLoading | MECH-001, MECH-003 | 🟢     |
| _...more..._ |          |             |                |                     |                    |        |

**Universal flow to screen (reference, max 14 lines):**

```text
Navigation/Event
  → RouteDefinition(route, view, binding)
      → Binding registers Controller/Deps
          → Controller.onInit()
              → UseCase/Repo
                  → Local/Remote/Engines
              → State update (reactive)
  → Widget build/react
```

_Adapt to your framework's navigation pattern._

---

### §8 — Critical Flows (max 6 flows, each max 8 lines)

Each flow uses **arrow notation** and covers:

```text
┌─ Flow: [Name]
│  Trigger:      [what starts it]
│  Path:         [A] → [B] → [C] → [D]
│  Persistence:  [where data lands]
│  Engines:      [MECH-IDs involved]
│  Failure pts:  [what can go wrong]
│  Observability:[logs/events/metrics]
└─ Status: 🟢
```

---

### §9 — State & Persistence (table, max 25 lines)

| Data Type    | SSOT     | Replica  | Strategy (sync/cache) | Conflicts | Migrations | Offline Risk | Status |
| ------------ | -------- | -------- | --------------------- | --------- | ---------- | ------------ | ------ |
| User profile | Local DB | Cloud DB | Push on change        | LWW       | v2→v3      | Low          | 🟢     |
| Session      | Memory   | None     | Ephemeral             | N/A       | N/A        | None         | 🟢     |

---

### §10 — External Integrations (table, max 20 lines)

| Integration | Purpose     | Where       | Auth/Secrets | Rate Limit | Fallback Plan   | Status |
| ----------- | ----------- | ----------- | ------------ | ---------- | --------------- | ------ |
| Cloud Auth  | Login       | `lib/auth/` | API Key      | N/A        | Cached token    | 🟢     |
| LLM API     | AI analysis | `lib/ai/`   | API Key      | 60 RPM     | Cached response | 🟡     |

---

### §11 — Observability & Debug (max 25 lines, prefer table + bullets)

| Category | What          | Where                   | How to access  |
| -------- | ------------- | ----------------------- | -------------- |
| Logs     | App events    | `lib/utils/logger.dart` | Console / file |
| Metrics  | Token cost    | `lib/ai/telemetry.dart` | Dashboard      |
| Errors   | Crash reports | Crash reporting service | Console        |

Include:

- **Mandatory events/logs** (short list)
- **Cost-relevant metrics** (tokens, API calls) if applicable
- **Audit points**: which mechanisms to verify first
- **Classic failures + where to look** (1-line bullets)

---

### §12 — Key Relationships (ASCII diagram, max 25 lines)

Show the **most important** class/module relationships with arrows.

```text
UserController ──→ UserService ──→ UserRepository ──→ LocalUserDao
                                          └──→ RemoteUserApi

GoalController ──→ GoalService ──→ GoalRepository ──→ ORM / CloudDB

NotifyManager  ──→ Scheduler / Push / Proxy
```

---

### §13 — Pointers & Evidence (max 60 lines)

Link catalog entries to source of truth using stable IDs:

```text
▸ MECH-001 (Auth)    → lib/auth/auth_service.dart (main logic)
▸ MECH-002 (Sync)    → lib/services/sync_service.dart#_pullData
▸ ROUTE /home        → lib/routes/app_pages.dart#home
▸ Binding HomeBinding→ lib/modules/home/bindings/home_binding.dart
▸ Architecture       → docs/architecture.md#layers
▸ Domain Rules       → lib/domain/validators/ (all validators)
```

**Rule**: Every Mechanism Catalog entry must have ≥1 pointer here **OR** appear in Gaps.

---

### §14 — Gaps (mandatory if any unknown exists, max 20 lines)

- Mechanisms cited but without source
- Triggers not found
- SSOT not determinable
- Routes/bindings incomplete
- Inferred parts (not confirmed)

Format:

```text
🔴 [MECH-ID / Item] — Reason — Impact level (high/med/low)
```

---

## 💡 Stack Examples (adapt to your stack)

> The tables and diagrams above are **framework-agnostic**. Below are concrete examples for a **Flutter + GetX + Drift** stack to illustrate how to fill them. **Skip or replace** if your stack differs.

### DI & Boot (§1, §2)

| Agnostic Concept     | Flutter + GetX Example                                                                 |
| -------------------- | -------------------------------------------------------------------------------------- |
| DI Container         | `Get.put()` / `Get.lazyPut()` inside a `Bindings` class                                |
| Registration Point   | `InitialBinding extends Bindings` → `dependencies()` method                            |
| Boot Pipeline        | `main() → initServices() → runApp(GetMaterialApp(initialBinding: ..., getPages: ...))` |
| Lifecycle: Singleton | `Get.put(AuthService(), permanent: true)`                                              |
| Lifecycle: Lazy      | `Get.lazyPut(() => SyncService())`                                                     |
| Lifecycle: Factory   | `Get.create(() => FormValidator())`                                                    |

### Presentation (§7)

| Agnostic Concept       | Flutter + GetX Example                                                        |
| ---------------------- | ----------------------------------------------------------------------------- |
| Route definition       | `GetPage(name: '/home', page: () => HomeView(), binding: HomeBinding())`      |
| Binding registers deps | `class HomeBinding extends Bindings { dependencies() { Get.lazyPut(...); } }` |
| Controller init        | `class HomeController extends GetxController { @override onInit() {...} }`    |
| Reactive state         | `final name = ''.obs;` → UI: `Obx(() => Text(ctrl.name.value))`               |
| Navigation             | `Get.toNamed('/detail', arguments: {...})`                                    |

### Persistence (§9)

| Agnostic Concept | Flutter + Drift Example                                          |
| ---------------- | ---------------------------------------------------------------- |
| Local ORM        | `@DriftDatabase(tables: [Users, Goals])` → generates DAO classes |
| DAO pattern      | `class UserDao extends DatabaseAccessor<AppDb> { ... }`          |
| Migration        | `@override int get schemaVersion => 3;` + `MigrationStrategy`    |
| SSOT location    | Drift SQLite DB (local) — remote Firestore is replica            |

---

## Anti-Patterns (what NOT to generate)

| ❌ Don't                                        | ✅ Do Instead                                |
| ----------------------------------------------- | -------------------------------------------- |
| Walls of prose explaining each module           | Tables with 1-line descriptions              |
| Generic architecture diagrams from textbooks    | Project-specific diagrams with real names    |
| Repeating info across sections                  | Use pointers (MECH-IDs) to link sections     |
| Omitting "boring" mechanisms (logging, caching) | List everything in Mechanism Catalog         |
| Making diagrams without arrows                  | Every diagram needs directional flow         |
| Using only plain text                           | Mix tables + diagrams + status indicators    |
| Assertions without evidence                     | Mark as INFERRED and add to Gaps             |
| Copying stack examples verbatim                 | Inspect actual code and fill with real names |
| Skipping DI / boot / routes mapping             | These are Core and Presentation — mandatory  |

---

## Error Handling

### Common Issue: Source files not found

**Symptom:** Agent cannot locate structural files.
**Solution:** Ask user for primary source path. Document missing files in Gaps section with 🔴 marker.

### Common Issue: Output exceeds line limits

**Symptom:** Section grows beyond allowed lines.
**Solution:** Summarize to fit limit. Move details to Pointers & Evidence with format: `▸ MECH-NNN → [file/section] (overflow from §N)`.

### Common Issue: Mechanisms missed

**Symptom:** Validation checklist shows catalog gaps.
**Solution:** Re-scan source files for: auth, routing, state, persistence, sync, cache, retry, outbox, notifications, AI, jobs, observability, migrations, security, permissions, feature flags, billing. Each must appear even as 1-line entry.

### Common Issue: DI/Boot not clear

**Symptom:** Cannot determine composition root or boot sequence.
**Solution:** Search for `main()` or app entry point. Trace initialization calls. If framework uses auto-DI, document the convention. Mark unknowns as INFERRED.
