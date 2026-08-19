---
name: updating-project-status
description: "Updates current_execution.md with adaptive detail, sequential handoff targeting, and metadata consistency. LCR-A compressed."
version: 4.1.0
tags: [project-management, status, handoff-quality, token-economy]
difficulty: beginner
estimated_time: 5min
---
# updating-project-status
trigger:[end_of_sprint, session_focus_change, noisy_or_stale_status, planning_for_weak_executor]
prereq: "context-orchestrator GO required (ref .cursorrules chain)"
target_file: ".context/docs/pendentes/current_execution.md"

section_order:[Metadata, Current, Pending_Queue, Ready_Next, Risks]

steps:[
  "S1_read: open current_execution.md -> extract(metadata, current_task, pending_list, risks). IF file missing/corrupt -> NO-GO, run context-maintenance.",
  "S2_metadata: set/refresh{last_updated:TODAY_ISO, last_verified:TODAY_ISO, owner:agent, source_of_truth:current_execution.md, expiry_days:7}. FAIL if any field missing after step.",
  "S3_normalize: enforce section_order. Remove sections not in list. Move orphan content to correct section.",
  "S4_classify: assess Current task -> tier=S(target<=200L)|M(target<=260L)|L(target<=320L). Exceed only with explicit justification(safety|multi-module|unblock).",
  "S5_exec_pack(REQ if M|L): inject into Current:{goal:1_clear_sentence, do:[3-8_ordered_concrete_steps], files:[explicit_paths], checks:[exact_cmds_or_assertions], done_when:[measurable_criteria], pitfalls:[known_risks+rollback_note]}. Each step must be self-contained.",
  "S6_sequential_handoff: IF Current is sequential(multi-step|weak-executor|resume-later) THEN require fields{Sequential:true,Handoff File:<path|ASK_USER>,Handoff Policy}. IF missing/ASK_USER -> ask user before delegation/continuation. IF non-sequential -> set Sequential:false,Handoff File:none,Handoff Policy:none and do not ask.",
  "S7_active_ctx_snapshot: update .context/active_context.md ONLY at pause/end-of-cycle as compact restart snapshot{objective, phase, current_execution pointer, optional active handoff pointer}. Do not store execution pack or sequential details there.",
  "S8_prune: completed_max:5, canceled_max:3. Move excess to .context/archive/. Strip low-signal detail from all sections.",
  "S9_crosscheck: verify Current+Risks vs architecture_drawer_contract.md. IF contradiction -> fix status or flag in Risks.",
  "S10_metrics: recompute all counts/percentages from actual section content. NO estimates.",
  "S11_validate: run checklist{metadata_complete, current_has_1_task+progress+blocker+impact+next_action, tier_defined, sequential_fields_present, handoff_question_only_if_sequential, exec_pack_if_M_L, pending_ordered, metrics_match, no_contradictions, file_concise}. FAIL items -> fix before save."
]

pending_item_contract:{required:[impact(high|med|low), ai_load(low|med|high|extreme), budget_hint(conserve|normal|spend)]}

error_rules:[
  "IF file>tier_target: compress history -> archive. Keep only execution-relevant content.",
  "IF executor_cant_identify_files AND sequential=true: enrich exec_pack + declared handoff_file. Keep active_context as pointer only.",
  "IF executor_cant_identify_files AND sequential=false: clarify Current; do not ask for or create a handoff.",
  "IF metrics_mismatch: recount from sections before save. Never estimate."
]

success: "current_execution.md consistent+compact+decision-oriented. Sequential trails declare handoff target; non-sequential tasks do not ask for handoff. Next step explicit+testable."
related:[tagging-flash-handoffs(run_after_this_when_weak_executor_planned)]
