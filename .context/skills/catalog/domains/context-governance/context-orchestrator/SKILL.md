---
name: context-orchestrator
description: "Gate GO/NO-GO before execution (structural impact, refactors)."
version: 2.0.0
tags: [context, governance, gate, planning]
difficulty: intermediate
estimated_time: 1min
---
# context-orchestrator
trigger: [before_exec, architectural_change, security_data_release_req, ambiguous_scope, integrity_risk]

modes:{
  default: "max_6_reads",
  expanded: "max_10_reads (REQ: explicit user ack)"
}
mandatory_core:[".cursorrules",".antigravityignore",".context/active_context.md",".context/support/architecture_drawer_contract.md",".context/docs/pendentes/current_execution.md"]

policy_overlay:{
  default_max_1_option:[ 
    ".context/support/bootstrap_fill_state.md(if scaffold_recent)",
    ".context/support/context_read_order.md",
    "drawer:01_core_bootstrap.md",
    "drawer:02_engines_mechanisms.md",
    "drawer:03_presentation_routes.md",
    "drawer:04_data_sync_state.md",
    "drawer:05_ops_risks_observability.md"
  ],
  expanded_opts:[ "any unread cond", ".context/support/token_budget_policy.md", ".context/support/freshness_policy.md", ".context/support/context_contract.md", ".context/support/archive_policy.md"]
}
flow:[
  "classify:$type",
  "read_core: abort_if_missing_stale(NO-GO)",
  "route_drawer: mapping intent",
  "check_integrity: IF (editable_id OR ambiguous_match OR integrity_risk) THEN stop/req_fix(NO-GO)",
  "auto_trigger: IF (bootstrap_fill_state==needs_project_fill OR drawer_contract==pending) THEN auto_run(context-maintenance bootstrap-fill) AND restart_gate",
  "read_limit: enforce(default=6, expand=10)",
  "eval: output summary -> decide(GO|NO-GO)"
]
constraints:[
  "NO double conditionals in default.",
  "NO executing product code during gate.",
  "NO silent approval if identity/integrity risk is open.",
  "NO guessing rules/gaps."
]
output_format: "Classificacao:[cat]\nModo:[def|exp]\nReads:[qty]\nDrawer:[id|none]\nRules:[list]\nDecisao:[GO|NO-GO]\n[Auto-bootstrap-fill]:[skip|exec|fail]\n[Safety stop]:[none|risk]\n[Reason/Next]:[...]"
escalation:[
  "noise/duplicate/stale -> run context-maintenance -> re-gate",
  "pending_bootstrap -> auto_run context-maintenance bootstrap-fill -> update state ready -> re-gate",
  "recurrent_no_go -> run validating-context-efficacy -> fix -> re-gate"
]
