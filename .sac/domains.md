# SAC Domain Index

## sac_core
- intent: SAC scanner CLI, parser and verification engine
- onboarded: 2026-08-19
- drawer_file:
- drawer_refs:
- anchor_symbols: lookup, parse_sac_domains, validate
- files:
  - src/sac_diff.py
  - src/sac_domains.py
  - src/sac_engine.py
  - src/sac_scan.py
  - src/sac_validate.py
- on_edit: sac-execution-overlay + get_sac_context + get_sac_constraints
- known_gaps:
