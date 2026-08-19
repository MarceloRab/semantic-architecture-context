# Architecture Drawers - semantic-architecture-context
format: LCR-A (IA-only target, max density, zero human padding)
router: .context/support/architecture_drawer_contract.md
drawers:[01_core_bootstrap, 02_engines_mechanisms, 03_presentation_routes, 04_data_sync_state, 05_ops_risks_observability]
rules:[
  "max 1 drawer per task default. 2nd only with evidence+dependency.",
  "NO duplicating facts across drawers.",
  "stale data -> .context/archive/ with pointer in original.",
  "metadata: meta(verified:DATE, owner:X, source_of_truth:path, expiry:N)"
]

