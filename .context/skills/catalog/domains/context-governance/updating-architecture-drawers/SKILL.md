---
name: updating-architecture-drawers
description: "LCR-A (Level-A Compression Rule). IA-exclusive target. Update/compress architecture drawers."
---
# updating-architecture-drawers
mission: "Architecture drawers are IA-ONLY memory. Max density, zero human readability padding."
rules:[
  "LCR-A_REQUIRED: flatten tables/lists to arrays or key-value single strings.",
  "NO_MARKDOWN_SCAFFOLD: remove `|---|`, excess `##`, conversational text.",
  "HIGH_FIDELITY: Strip fluff but NEVER lose technical facts, ids, relationships or hard limits."
]
drawers_fixed_scope:[
  "01_core_bootstrap:[Mission,Scope,Global constraints,Entrypoints,DI_MAP,Boot_seq]",
  "02_engines_mechanisms:[Sync engines,Repos,API_integrations,Mutation_logic]",
  "03_presentation_routes:[Controllers,Routing,Views,Intent_nav,Reactivity]",
  "04_data_sync_state:[Schemas,DB_Models,LWW,Offline/Remote-first,Rehydrate_state]",
  "05_ops_risks_observability:[Active_Risks,Log_anchors,Release_checklists,Runbooks]"
]
operations:[
  "read_gate: lazy_small_context. NEVER glob/scan folder. Max 1 drawer by intent/evidence default, max 2 if deep dep.",
  "archive_stale: if obsolete, move detailed data to .context/archive/, leave pointer in original drawer."
]
metadata_standard: "meta(verified:YYYY-MM-DD, owner:[Author], source_of_truth:./path.md, expiry:[Days])"
