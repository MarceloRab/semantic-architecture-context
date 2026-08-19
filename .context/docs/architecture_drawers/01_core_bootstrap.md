meta(verified:2026-08-19, owner:TBD, source_of_truth:./01_core_bootstrap.md, expiry:30)
# D01-Core+Bootstrap
scope:[app_entrypoints, global_DI_registrations, startup_init_sequence, boot_invariants]
composition_root:[
  "TBD[file:TBD, lifecycle:singleton|scoped|transient, consumers:TBD, status:TBD]"
]
boot_pipeline: "main()->init_platform->register_global_services->resolve_initial_route->run_app"
constraints:[TBD]
gaps:[TBD]
ptr:[architecture_drawer_contract.md, current_execution.md]

