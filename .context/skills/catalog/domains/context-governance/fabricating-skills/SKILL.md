---
name: fabricating-skills
description: "Factory for creating new reusable skills. Guides structured skill authoring, frontmatter compliance, registry entry generation, and propagation routing."
version: 1.0.0
tags: [context-governance, skill-factory, generation, propagation]
difficulty: intermediate
estimated_time: 10-15min
---

# fabricating-skills

trigger:[need_new_skill, automate_task, skill_request]

prereq: "Domain and intent of the new skill must be defined. Skill will live under skills/catalog/domains/<domain>/<skill-id>/"

workflow:[
  "W1_define: identify domain, function tags, scope (agnostic vs local), and trigger intents.",
  "W2_author: write SKILL.md with mandatory frontmatter (name, description, version, tags, difficulty, estimated_time).",
  "W3_registry: add entry to skills_registry.json with id, canonical_path, domain, functions, scope, intents.",
  "W4_rebuild: run rebuild-skills-catalog.ps1 to regenerate indexes.",
  "W5_mirror: run mirror-agnostic-skills.ps1 to propagate to templates/project-base/.context/skills/domains/.",
  "W6_validate: verify skill appears in INDEX_BY_DOMAIN.md and is discoverable."
]

rules:[
  "Skill name must be kebab-case, unique across catalog.",
  "Agnostic skills: reusable across any project. Local skills: rabelo-standards repo only.",
  "Intents must include 3-5 natural language trigger phrases.",
  "Always update registry before mirror. Mirror uses registry as source of truth.",
  "Never reference local-only skills in templates/project-base/.cursorrules."
]

guardrails:[
  "Do not create skills for one-off tasks.",
  "Do not duplicate existing skill coverage without explicit justification.",
  "Scope must be explicit: agnostic (propagated) or local (rabelo-standards only)."
]
