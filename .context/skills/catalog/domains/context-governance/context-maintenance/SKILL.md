---
name: context-maintenance
description: "Maintains .context/ as high-signal, low-token surfaces. Modes: update(weekly), initialization(first-fill), expanded(deep)."
version: 3.1.0
tags: [context, maintenance, token-economy, governance]
difficulty: intermediate
estimated_time: 5-10min
---
# context-maintenance
trigger:[end_of_cycle, stale_or_noisy_context, token_cost_rising, weekly_hygiene, bootstrap_pending]
prereq: "ref .cursorrules mandatory chain (5 core reads)"

invocation:{
  "context-maintenance": "alias for update",
  "context-maintenance update": "weekly/periodic hygiene. max_6_reads. Auto-promotes to initialization IF bootstrap/drawer pending detected.",
  "context-maintenance initialization": "first project-specific fill after scaffold/sync. target_8_reads, max_10_with_ack.",
  "context-maintenance bootstrap-fill": "backward alias for initialization.",
  "context-maintenance expanded": "deep maintenance. max_10_reads. REQ explicit user ack."
}

read_budget:{
  update: "core_5 + max_1_conditional(bootstrap_fill_state.md OR context_read_order.md). IF both needed -> ack + switch expanded.",
  initialization: "core_5 + target_3_extra(total_8). reads_9-10 REQ explicit ack.",
  expanded: "core_5 + up_to_5_extra(total_10). REQ explicit ack. Extras: token_budget_policy, freshness_policy, archive_policy, context_contract, unread_conditionals."
}

scaffold_contract:[
  "bootstrap/sync scripts: seed .context/docs/ .context/archive/ architecture_drawer_contract.md when missing.",
  "preserve existing project-specific content on sync/overwrite.",
  "update-project.ps1: ensure folders only, never overwrite .context/docs/* or .context/archive/*."
]

scan_commands_init_only:[
  "structure: rg --files | rg '^(lib|src|app|packages|modules|backend|frontend)/'",
  "bootstrap: rg -n 'main\\(|runApp\\(|configureDependencies|GetMaterialApp|ProviderScope|bootstrap|initialize' lib src app",
  "engines: rg -n 'class .*Service|class .*Repository|class .*UseCase|Orchestrator|Engine' lib src app",
  "routes: rg -n 'GetPage\\(|routes\\s*=|GoRoute\\(|AutoRoute|Binding|Controller|ViewModel' lib src app",
  "data: rg -n 'Drift|sqflite|Hive|Isar|Firestore|Supabase|sync|migration|DAO|Repository' lib src app",
  "ops: rg -n 'Sentry|Crashlytics|logger|analytics|feature flag|rollback|healthcheck|monitor' lib src app",
  "STOP: if scans insufficient -> req explicit user ack before broader scan."
]

workflow:[
  "W1_detect: check bootstrap_fill_state.md for needs_project_fill OR drawer_contract pending/TBD.",
  "W2_auto_switch: IF pending detected in update mode -> auto-switch to initialization. Report switch.",
  "W3_inventory: quick scan .context/* and .context/support/*. Confirm docs/ archive/ scaffold exists.",
  "W4_classify: each file -> restart_snapshot(active_context) | handoff(sequential_trails_only) | stable(low_change_refs) | cold(historical) | noise(stale/duplicated).",
  "W5_hygiene: delta-update active_context only as pause/end-of-cycle restart snapshot. Remove cross-file duplication(active_ctx vs arch vs status vs handoffs). Archive stale content with pointers.",
  "W6_init_fill(if initialization): execute init_targets via fill_routing below.",
  "W7_metadata: refresh freshness(last_verified, owner, source_of_truth, expiry_days) on all touched files.",
  "W8_completion: set bootstrap_fill_state -> ready_for_execution ONLY when core+drawer targets complete. Verify no pending/TBD remains.",
  "W9_report: output maintenance_report."
]

init_targets:[
  ".context/active_context.md",
  ".context/support/architecture_drawer_contract.md",
  ".context/docs/pendentes/current_execution.md",
  ".context/docs/context_index.md",
  ".context/docs/architecture_drawers/01-05*.md",
  ".context/support/{context_read_order,token_budget_policy,freshness_policy,context_contract,archive_policy}.md"
]

fill_routing:{
  "architecture_drawer_contract.md": "DELEGATE -> briefing-structural-architecture(default)",
  "current_execution.md": "DELEGATE -> updating-project-status",
  "architecture_drawers/*": "DELEGATE -> briefing-architecture-drawers (REQ when drawer contract active)",
  "active_context.md": "DIRECT fill: replace TBD with compact restart snapshot; include handoff pointer only if a sequential trail is active",
  "context_index.md": "DIRECT fill: list actual project docs",
  ".context/support/*": "CONFIRM only: verify inherited policies match project reality"
}
fill_order:[active_context, architecture_drawer_contract, architecture_drawers, current_execution, support_policies, context_index]
fill_done_signal:[
  "bootstrap_fill_state.md -> fill_status:ready_for_execution",
  "drawer_contract: no pending rows when drawer mode active",
  "drawer files: no critical TBD in mandatory sections"
]

hard_constraints:[
  "NO delete history without explicit user request. Prefer archive.",
  "active_context.md = compact restart snapshot ONLY; not a detailed execution handoff.",
  "Sequential execution details live in explicit local handoff_file only when a sequential trail is active.",
  "Do not ask for a handoff file during ordinary context maintenance or non-sequential tasks.",
  "NO duplicate truth across active_ctx/arch_contract/current_execution.",
  "read_budget: strict per mode (update=6, init=target8/cap10, expanded=10).",
  "initialization: NO TBD in core/drawer files at completion.",
  "update->initialization: auto-switch ONLY for bootstrap/drawer pending. Report it.",
  "expanded->initialization: NEVER implicit switch."
]

acceptance_gate:[
  "mandatory read order minimal+complete",
  "zero cross-file truth duplication",
  "stale content archived",
  "new files have clear execution purpose",
  "freshness metadata consistent with policy",
  "IF init: fill_state=ready_for_execution, no pending drawers, init reads<=8(default)"
]

output: "Report{mode, reads_used(N/budget), restart_snapshot_checked, handoff_policy_checked, stable_checked, archived, duplicates_removed, policy_gaps, drawer_status(ready|pending|mismatch), bootstrap_state, decision(HEALTHY|NEEDS_ACTION|NO-GO), next_step}"

return_path: "after completion -> re-run context-orchestrator. IF still NO-GO -> escalate to validating-context-efficacy."
related:[context-orchestrator(gate), validating-context-efficacy(systemic_audit), briefing-architecture-drawers(drawer_normalization)]
