#!/usr/bin/env node
/**
 * Smoke without Cursor: Node runLookup JSON ≡ Python CLI --json.
 * Also: list-domains; discover; lookup without --path → filepath_required;
 * hop1 scoped to domain files:; membership by domain_id.
 *
 * Usage (from repo root or mcp/):
 *   node sac-context/mcp/smoke.mjs
 *   SAC_ROOT=<fixture> SAC_PYTHON=python node smoke.mjs
 */

import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  assessSacCapillarityPayload,
  discoverSacPayload,
  getSacContextPayload,
  getSacConstraintsPayload,
  resolveCliPath,
  resolvePython,
  resolveSacRoot,
  runCapillarity,
  runCliJson,
  runContext,
  runDiscover,
  runListDomains,
  runLookup,
} from "./server.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

function deepEqual(a, b) {
  return JSON.stringify(a) === JSON.stringify(b);
}

function cliLookup(symbol, root, filepath, python, cliPath, env = process.env, domainId) {
  const args = [cliPath, "lookup", symbol, "--root", root, "--json"];
  if (filepath) args.push("--path", filepath);
  if (domainId) args.push("--domain", domainId);
  const r = spawnSync(python, args, {
    encoding: "utf8",
    windowsHide: true,
    env,
  });
  if (r.error) {
    throw new Error(`CLI spawn failed: ${r.error.message}`);
  }
  const text = (r.stdout || "").trim();
  if (!text) {
    throw new Error(`CLI exit ${r.status}: ${(r.stderr || "").trim()}`);
  }
  const parsed = JSON.parse(text);
  return { status: r.status, parsed };
}

function writeFixture() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "sac_t2_smoke_"));
  const src = path.join(root, "src");
  fs.mkdirSync(src, { recursive: true });
  const tagged = path.join(src, "tagged.py");
  const hop = path.join(src, "hop.py");
  const outside = path.join(src, "outside.py");
  const dottedVerifyTargets = ["SmokeHop.method", "SmokeHop"];
  fs.writeFileSync(
    tagged,
    [
      "# SAC:ARCH: RULE - SmokeArch: MUST be reachable via Node MCP adapter.",
      "def SmokeArch():",
      "    pass",
      "",
      "# SAC:REGR: on=behavior_change - SmokeRegr: you MUST verify: SmokeHop.",
      "def SmokeRegr():",
      "    pass",
      "",
      `# SAC:REGR: on=verify_change - SmokeDottedVerify: you MUST verify: ${dottedVerifyTargets.join(", ")}.`,
      "def SmokeDottedVerify():",
      "    pass",
      "",
      "# SAC:ARCH: on=ordering - SmokeDeprecated: MUST remain a contiguous multi-tag declaration.",
      "# SAC:DEPRECATED: on=new_dependency - SmokeDeprecated: MUST NOT be used by new code; replacement: SmokeArch",
      "def SmokeDeprecated():",
      "    pass",
      "",
      "# SAC:DEPRECATED: on=new_dependency - SmokeMissingReplacement: MUST NOT be used by new code",
      "def SmokeMissingReplacement():",
      "    pass",
      "",
    ].join("\n"),
    "utf8",
  );
  fs.writeFileSync(
    hop,
    [
      "# SAC:ARCH: on=boundary - SmokeHop: MUST fill hop1 from domain scope.",
      "def SmokeHop():",
      "    pass",
      "",
    ].join("\n"),
    "utf8",
  );
  fs.writeFileSync(
    outside,
    [
      "# SAC:ARCH: on=boundary - SmokeOutside: MUST NOT appear in scoped hop1/discover.",
      "def SmokeOutside():",
      "    pass",
      "",
      "# SAC:ARCH: on=ssot - SmokeWeakArch: describes behavior without an imperative.",
      "def SmokeWeakArch():",
      "    pass",
      "",
      "# SAC:REGR: on=X - SmokeInvalidRegr: MUST preserve behavior.",
      "def SmokeInvalidRegr():",
      "    pass",
      "",
    ].join("\n"),
    "utf8",
  );
  // Minimal domains index so membership can be exercised positively
  const sacDir = path.join(root, ".sac");
  fs.mkdirSync(sacDir, { recursive: true });
  const relTagged = path.relative(root, tagged).replace(/\\/g, "/");
  const relHop = path.relative(root, hop).replace(/\\/g, "/");
  fs.writeFileSync(
    path.join(sacDir, "domains.md"),
    [
      "# SAC Domain Index",
      "",
      "## smoke_domain",
      "- intent: Smoke fixture domain for MCP parity",
      "- onboarded: 2026-07-20",
      "- drawer_file: .context/docs/architecture_drawers/02_engines_mechanisms.md",
      "- drawer_refs: MECH-SMOKE",
      "- anchor_symbols: SmokeArch, SmokeRegr, SmokeUnmappedAnchor",
      "- files:",
      `  - ${relTagged}`,
      `  - ${relHop}`,
      "- on_edit: sac-execution-overlay + get_sac_context + get_sac_constraints",
      "- known_gaps:",
      "",
    ].join("\n"),
    "utf8",
  );
  return { root, tagged, hop, outside, relTagged, relHop, dottedVerifyTargets };
}

function assertRelativeAbsoluteRootBytes(root, python, cliPath) {
  const relativeRoot = path.relative(process.cwd(), root);
  const args = (rootArg) => [
    cliPath,
    "context",
    "--root",
    rootArg,
    "--domain",
    "smoke_domain",
    "--json",
  ];
  const relative = spawnSync(python, args(relativeRoot), {
    encoding: "buffer",
    windowsHide: true,
    env: process.env,
  });
  const absolute = spawnSync(python, args(root), {
    encoding: "buffer",
    windowsHide: true,
    env: process.env,
  });
  if (
    relative.status !== 0 ||
    absolute.status !== 0 ||
    !relative.stdout.equals(absolute.stdout)
  ) {
    console.error("[FAIL] relative/absolute --root byte parity", {
      relativeStatus: relative.status,
      absoluteStatus: absolute.status,
      relative: relative.stdout.toString("utf8"),
      absolute: absolute.stdout.toString("utf8"),
    });
    process.exit(1);
  }
  console.log(`[OK] relative/absolute --root byte parity bytes=${absolute.stdout.length}`);
}

async function assertDottedVerifyParity(root, tagged, python, cliPath, rawTargets) {
  const payload = await runLookup("SmokeDottedVerify", tagged, {
    root,
    python,
    cliPath,
    domainId: "smoke_domain",
  });
  const payloadTargets = payload.matches?.[0]?.verify;
  if (!deepEqual(rawTargets, payloadTargets)) {
    console.error("[FAIL] dotted verify raw-line/MCP parity", rawTargets, payloadTargets);
    process.exit(1);
  }
  console.log(`[OK] dotted verify raw-line≡MCP targets=${payloadTargets.join(",")}`);
}

async function assertParity(label, symbol, root, filepath, python, cliPath, domainId) {
  const { status, parsed: fromCli } = cliLookup(
    symbol,
    root,
    filepath,
    python,
    cliPath,
    process.env,
    domainId,
  );
  if (status !== 0) {
    console.error(`[FAIL] ${label}: CLI status ${status}`, fromCli);
    process.exit(1);
  }
  const fromNode = await runLookup(symbol, filepath, {
    root,
    python,
    cliPath,
    domainId,
  });
  if (fromNode.error) {
    console.error(`[FAIL] ${label}: Node error`, fromNode);
    process.exit(1);
  }
  if (!deepEqual(fromCli, fromNode)) {
    console.error(`[FAIL] ${label}: JSON mismatch`);
    console.error("CLI:", JSON.stringify(fromCli, null, 2));
    console.error("Node:", JSON.stringify(fromNode, null, 2));
    process.exit(1);
  }
  console.log(`[OK] ${label} found=${fromNode.found}`);
  return fromNode;
}

async function assertPythonMissing(filepath) {
  const bogus = path.join(
    os.tmpdir(),
    `sac-python-missing-${Date.now()}-noexist`,
  );
  try {
    await runLookup("x", filepath, {
      root: resolveSacRoot(),
      python: bogus,
      timeoutMs: 5_000,
    });
    console.error("[FAIL] expected error when python missing");
    process.exit(1);
  } catch (err) {
    const msg = err?.message ?? String(err);
    if (!/not found|ENOENT|Failed to spawn|spawn error/i.test(msg)) {
      console.error("[FAIL] unexpected missing-python error:", msg);
      process.exit(1);
    }
    console.log("[OK] python missing → explicit error");
  }
}

async function assertListDomains(root, python, cliPath) {
  const fromNode = await runListDomains({ root, python, cliPath });
  const r = spawnSync(
    python,
    [cliPath, "list-domains", "--root", root, "--json"],
    { encoding: "utf8", windowsHide: true, env: process.env },
  );
  if (r.status !== 0) {
    console.error("[FAIL] list-domains CLI", r.stderr);
    process.exit(1);
  }
  const fromCli = JSON.parse((r.stdout || "").trim());
  if (!deepEqual(fromCli, fromNode)) {
    console.error("[FAIL] list-domains catalog mismatch", fromCli, fromNode);
    process.exit(1);
  }
  if (fromNode.mode !== "catalog" || fromNode.count < 1) {
    console.error("[FAIL] expected catalog mode", fromNode);
    process.exit(1);
  }
  const card = fromNode.domains[0];
  const allowedCatalogKeys = new Set([
    "domain_id",
    "summary",
    "files_count",
  ]);
  const forbiddenCatalogKeys = [
    "files",
    "anchor_symbols",
    "anchor_hint",
    "drawer_file",
    "drawer_refs",
    "on_edit",
    "onboarded",
    "known_gaps",
    "intent",
    "path",
  ];
  for (const key of Object.keys(card)) {
    if (!allowedCatalogKeys.has(key)) {
      console.error("[FAIL] catalog card has non-minimal key", key, card);
      process.exit(1);
    }
  }
  for (const key of forbiddenCatalogKeys) {
    if (Object.prototype.hasOwnProperty.call(card, key)) {
      console.error("[FAIL] catalog must not include", key, card);
      process.exit(1);
    }
  }
  if (
    !card.domain_id ||
    !(card.files_count >= 1) ||
    !card.summary ||
    typeof card.summary !== "string"
  ) {
    console.error("[FAIL] catalog card incomplete", card);
    process.exit(1);
  }
  if (fromNode.path || fromNode.domains.some((d) => d.path)) {
    console.error("[FAIL] catalog must not expose absolute path", fromNode);
    process.exit(1);
  }

  const expanded = await runListDomains({
    root,
    python,
    cliPath,
    domainId: "smoke_domain",
  });
  if (expanded.mode !== "expand" || !expanded.domains?.[0]?.files?.length) {
    console.error("[FAIL] expand missing files", expanded);
    process.exit(1);
  }
  if (!expanded.domains[0].anchor_symbols?.length) {
    console.error("[FAIL] expand missing anchors", expanded);
    process.exit(1);
  }
  console.log(
    `[OK] list-domains catalog+expand count=${fromNode.count} files=${expanded.domains[0].files.length}`,
  );
}

async function assertContext(root, python, cliPath) {
  const args = [
    cliPath,
    "context",
    "--domain",
    "smoke_domain",
    "--root",
    root,
    "--json",
  ];
  const r = spawnSync(python, args, {
    encoding: "utf8",
    windowsHide: true,
    env: process.env,
  });
  if (r.status !== 0) {
    console.error("[FAIL] context CLI", r.stderr, r.stdout);
    process.exit(1);
  }
  const fromCli = JSON.parse((r.stdout || "").trim());
  const fromNode = await runContext({
    root,
    python,
    cliPath,
    domainId: "smoke_domain",
  });
  if (!deepEqual(fromCli, fromNode)) {
    console.error("[FAIL] context MCP≡CLI mismatch", fromCli, fromNode);
    process.exit(1);
  }
  const constraints = fromNode.constraints || [];
  const symbols = new Set(constraints.map((item) => item.symbol));
  if (
    fromNode.mode !== "context" ||
    !symbols.has("SmokeArch") ||
    !symbols.has("SmokeRegr") ||
    !symbols.has("SmokeDeprecated") ||
    !symbols.has("SmokeMissingReplacement") ||
    symbols.has("SmokeOutside")
  ) {
    console.error("[FAIL] context selection", fromNode);
    process.exit(1);
  }
  if (!(fromNode.warnings || []).some((w) => w.includes("deprecated_replacement_required"))) {
    console.error("[FAIL] context missing deprecated replacement warning", fromNode);
    process.exit(1);
  }
  const deprecated = constraints.find((item) => item.symbol === "SmokeDeprecated");
  if (deprecated?.replacement !== "SmokeArch") {
    console.error("[FAIL] context deprecated replacement", deprecated);
    process.exit(1);
  }
  const regr = constraints.find((item) => item.symbol === "SmokeRegr");
  if (!regr?.hop1?.some((item) => item.symbol === "SmokeHop" && item.found)) {
    console.error("[FAIL] context scoped hop1", regr);
    process.exit(1);
  }
  const viaHandler = await getSacContextPayload("smoke_domain", {
    root,
    python,
    cliPath,
  });
  if (!deepEqual(fromCli, viaHandler)) {
    console.error("[FAIL] getSacContextPayload mismatch");
    process.exit(1);
  }

  const limited = await runContext({
    root,
    python,
    cliPath,
    domainId: "smoke_domain",
    env: { SAC_CONTEXT_MAX_BYTES: "512" },
  });
  if (
    limited.code !== "context_payload_too_large" ||
    limited.constraints ||
    !(limited.source_payload_bytes > limited.max_payload_bytes)
  ) {
    console.error("[FAIL] context payload limit must halt explicitly", limited);
    process.exit(1);
  }
  console.log(
    `[OK] context MCP≡CLI selected=${fromNode.selected_count}; payload limit explicit`,
  );
}

async function assertDiscover(root, python, cliPath) {
  const r = spawnSync(
    python,
    [cliPath, "discover", "--domain", "smoke_domain", "--root", root, "--json"],
    { encoding: "utf8", windowsHide: true, env: process.env },
  );
  if (r.status !== 0) {
    console.error("[FAIL] discover CLI", r.stderr, r.stdout);
    process.exit(1);
  }
  const fromCli = JSON.parse((r.stdout || "").trim());
  const fromNode = await runDiscover({
    root,
    python,
    cliPath,
    domainId: "smoke_domain",
  });
  if (!deepEqual(fromCli, fromNode)) {
    console.error("[FAIL] discover MCP≡CLI mismatch", fromCli, fromNode);
    process.exit(1);
  }
  if (fromNode.mode !== "discover" || fromNode.tag_count < 6) {
    console.error("[FAIL] discover expected tags", fromNode);
    process.exit(1);
  }
  const symbols = new Set((fromNode.tags || []).map((t) => t.symbol));
  if (
    !symbols.has("SmokeArch") ||
    !symbols.has("SmokeHop") ||
    !symbols.has("SmokeDeprecated") ||
    !symbols.has("SmokeMissingReplacement")
  ) {
    console.error("[FAIL] discover missing domain symbols", symbols);
    process.exit(1);
  }
  if (symbols.has("SmokeOutside")) {
    console.error("[FAIL] discover leaked outside-domain tag", fromNode);
    process.exit(1);
  }
  const allowedTagKeys = new Set([
    "file",
    "line",
    "tag_type",
    "symbol",
    "verify",
    "replacement",
  ]);
  if (!(fromNode.warnings || []).some((w) => w.includes("deprecated_replacement_required"))) {
    console.error("[FAIL] discover missing deprecated replacement warning", fromNode);
    process.exit(1);
  }
  const deprecated = (fromNode.tags || []).find(
    (tag) =>
      tag.symbol === "SmokeDeprecated" && tag.tag_type === "DEPRECATED",
  );
  if (deprecated?.replacement !== "SmokeArch") {
    console.error("[FAIL] discover deprecated replacement", deprecated);
    process.exit(1);
  }
  const forbiddenTagKeys = ["constraint", "trigger"];
  for (const tag of fromNode.tags || []) {
    for (const key of Object.keys(tag)) {
      if (!allowedTagKeys.has(key)) {
        console.error("[FAIL] discover tag has non-slim key", key, tag);
        process.exit(1);
      }
    }
    for (const key of forbiddenTagKeys) {
      if (Object.prototype.hasOwnProperty.call(tag, key)) {
        console.error("[FAIL] discover must not include", key, tag);
        process.exit(1);
      }
    }
  }

  const viaHandler = await discoverSacPayload("smoke_domain", {
    root,
    python,
    cliPath,
  });
  if (!deepEqual(fromCli, viaHandler)) {
    console.error("[FAIL] discoverSacPayload mismatch");
    process.exit(1);
  }
  console.log(`[OK] discover MCP≡CLI tag_count=${fromNode.tag_count}`);
}

async function assertUnscopedBlocked(root, python, cliPath) {
  const { status, parsed: fromCli } = cliLookup(
    "SmokeArch",
    root,
    undefined,
    python,
    cliPath,
  );
  if (status === 0 || fromCli.code !== "filepath_required") {
    console.error("[FAIL] expected filepath_required without --path", fromCli);
    process.exit(1);
  }
  if (!fromCli.pause_hint || fromCli.hint_tool !== "list_sac_domains") {
    console.error("[FAIL] missing pause_hint/hint_tool", fromCli);
    process.exit(1);
  }
  if (fromCli.matches || fromCli.found === true || fromCli.hop1) {
    console.error("[FAIL] PAUSE must not include matches/found/hop1", fromCli);
    process.exit(1);
  }

  const fromNode = await getSacConstraintsPayload("SmokeArch", undefined, {
    root,
    python,
    cliPath,
  });
  if (!deepEqual(fromCli, fromNode)) {
    console.error("[FAIL] MCP≡CLI negative parity mismatch");
    console.error("CLI:", JSON.stringify(fromCli, null, 2));
    console.error("Node:", JSON.stringify(fromNode, null, 2));
    process.exit(1);
  }
  console.log("[OK] MCP≡CLI filepath_required (zero matches)");
}

async function assertOutsideDomainsParity(root, python, cliPath) {
  const { status, parsed: fromCli } = cliLookup(
    "SmokeArch",
    root,
    "no/such/file.py",
    python,
    cliPath,
  );
  if (status === 0 || fromCli.code !== "filepath_not_in_sac_domains") {
    console.error("[FAIL] expected filepath_not_in_sac_domains", fromCli);
    process.exit(1);
  }
  const fromNode = await getSacConstraintsPayload(
    "SmokeArch",
    "no/such/file.py",
    { root, python, cliPath },
  );
  if (!deepEqual(fromCli, fromNode)) {
    console.error("[FAIL] MCP≡CLI membership mismatch", fromCli, fromNode);
    process.exit(1);
  }
  if (fromNode.matches || fromNode.found === true) {
    console.error("[FAIL] membership PAUSE leaked matches", fromNode);
    process.exit(1);
  }
  console.log("[OK] MCP≡CLI filepath_not_in_sac_domains");
}

async function assertDomainMembership(root, tagged, python, cliPath) {
  const { status, parsed: fromCli } = cliLookup(
    "SmokeArch",
    root,
    tagged,
    python,
    cliPath,
    process.env,
    "missing_domain",
  );
  if (status === 0 || fromCli.code !== "domain_not_found") {
    console.error("[FAIL] expected domain_not_found", fromCli);
    process.exit(1);
  }
  const fromNode = await getSacConstraintsPayload("SmokeArch", tagged, {
    root,
    python,
    cliPath,
    domainId: "missing_domain",
  });
  if (!deepEqual(fromCli, fromNode)) {
    console.error("[FAIL] domain_not_found MCP≡CLI mismatch", fromCli, fromNode);
    process.exit(1);
  }
  console.log("[OK] MCP≡CLI domain_not_found on Verify");
}

async function assertHop1Scoped(root, tagged, python, cliPath) {
  const result = await assertParity(
    "REGR+path hop1 scoped",
    "SmokeRegr",
    root,
    tagged,
    python,
    cliPath,
    "smoke_domain",
  );
  const hop1 = result.matches?.[0]?.hop1 || [];
  const hopFound = hop1.find((h) => h.symbol === "SmokeHop" && h.found);
  if (!hopFound) {
    console.error("[FAIL] expected SmokeHop in scoped hop1", hop1);
    process.exit(1);
  }
  const warnings = (result.warnings || []).join("\n");
  if (
    !/hop1_domain_scan_no_index|hop1_via_symbol_index_scoped/.test(warnings)
  ) {
    console.error("[FAIL] expected scoped hop1 warning", result.warnings);
    process.exit(1);
  }
  if (/hop1_full_scan_no_index/.test(warnings)) {
    console.error("[FAIL] full scan should not run when domain scoped", warnings);
    process.exit(1);
  }
  console.log("[OK] hop1 scoped (no full-root scan)");
}

function assertPreOnboardLookup(root, outside, python, cliPath) {
  const args = [
    cliPath,
    "lookup",
    "SmokeOutside",
    "--root",
    root,
    "--path",
    outside,
    "--pre-onboard",
    "--json",
  ];
  const valid = spawnSync(python, args, {
    encoding: "utf8",
    windowsHide: true,
    env: process.env,
  });
  const validReport = JSON.parse((valid.stdout || "").trim());
  if (valid.status !== 0 || validReport.found !== true) {
    console.error("[FAIL] pre-onboard lookup must find explicit outside-domain file", validReport);
    process.exit(1);
  }
  const warnings = (validReport.warnings || []).join("\n");
  for (const expected of [
    "arch_imperative_required",
    "invalid_trigger tag=REGR trigger=X allowed=[a-z][a-z0-9_]{2,47}",
    "regr_verify_required",
  ]) {
    if (!warnings.includes(expected)) {
      console.error("[FAIL] missing canonical contract warning", expected, validReport);
      process.exit(1);
    }
  }

  const invalid = spawnSync(python, [...args, "--domain", "smoke_domain"], {
    encoding: "utf8",
    windowsHide: true,
    env: process.env,
  });
  const invalidReport = JSON.parse((invalid.stdout || "").trim());
  if (invalid.status !== 1 || invalidReport.code !== "pre_onboard_domain_forbidden") {
    console.error("[FAIL] pre-onboard lookup must reject --domain", invalidReport);
    process.exit(1);
  }
  console.log("[OK] pre-onboard lookup bounded + canonical contract warnings");
}

async function assertValidateTagBlocks(root, python, cliPath) {
  const args = [cliPath, "validate", "--root", root, "--json"];
  const valid = spawnSync(python, args, {
    encoding: "utf8",
    windowsHide: true,
    env: process.env,
  });
  const validReport = JSON.parse((valid.stdout || "").trim());
  if (valid.status !== 0 || validReport.count !== 0) {
    console.error("[FAIL] contiguous SAC tag block must validate", validReport);
    process.exit(1);
  }
  if (
    !(validReport.warnings || []).some((warning) =>
      warning.includes(
        "UNMAPPED_ANCHOR_SYMBOL domain=smoke_domain symbol=SmokeUnmappedAnchor",
      ),
    )
  ) {
    console.error("[FAIL] validate must report unmapped anchor symbol", validReport);
    process.exit(1);
  }

  const orphan = path.join(root, "src", "orphan.py");
  fs.writeFileSync(
    orphan,
    "# SAC:DEPRECATED: on=new_dependency - SmokeOrphan: MUST NOT be used; replacement: none\n",
    "utf8",
  );
  const invalid = spawnSync(python, args, {
    encoding: "utf8",
    windowsHide: true,
    env: process.env,
  });
  const invalidReport = JSON.parse((invalid.stdout || "").trim());
  if (
    invalid.status !== 1 ||
    invalidReport.count !== 1 ||
    invalidReport.orphans?.[0]?.tag_type !== "DEPRECATED"
  ) {
    console.error("[FAIL] orphan DEPRECATED must fail validate", invalidReport);
    process.exit(1);
  }
  fs.rmSync(orphan, { force: true });
  console.log("[OK] validate contiguous tag block + DEPRECATED orphan");
}

async function assertCapillarity(root, python, cliPath) {
  // Dedicated clean domain: ARCH+REGR only so fitness can be FIT with full claims.
  const capSrc = path.join(root, "src", "cap_clean.py");
  fs.writeFileSync(
    capSrc,
    [
      "# SAC:ARCH: on=ssot - CapArch: MUST remain the SUMMARY/EXTEND anchor.",
      "def CapArch():",
      "    pass",
      "",
      "# SAC:REGR: on=anchor_change - CapRegr: you MUST verify: CapArch.",
      "def CapRegr():",
      "    pass",
      "",
    ].join("\n"),
    "utf8",
  );
  const relCap = path.relative(root, capSrc).replace(/\\/g, "/");
  const domainsPath = path.join(root, ".sac", "domains.md");
  const existing = fs.readFileSync(domainsPath, "utf8");
  fs.writeFileSync(
    domainsPath,
    [
      existing.trimEnd(),
      "",
      "## cap_domain",
      "- intent: Capillarity budget/fitness fixture",
      "- onboarded: 2026-07-27",
      "- drawer_file: .context/docs/architecture_drawers/02_engines_mechanisms.md",
      "- drawer_refs: MECH-CAP",
      "- anchor_symbols: CapArch, CapRegr",
      "- files:",
      `  - ${relCap}`,
      "- context_scenarios: SUMMARY, EXTEND, REGRESSION",
      "- coverage_claims:",
      `  - CAP_SUMMARY | SUMMARY | ARCH | CapArch | ${relCap}`,
      `  - CAP_EXTEND | EXTEND | ARCH | CapArch | ${relCap}`,
      `  - CAP_REGR | REGRESSION | REGR | CapRegr | ${relCap}`,
      "- on_edit: sac-execution-overlay + get_sac_context + get_sac_constraints",
      "- known_gaps:",
      "",
    ].join("\n"),
    "utf8",
  );

  // Case A: complete domain under default budget → PASS + payload OK
  const okCli = spawnSync(
    python,
    [cliPath, "capillarity", "--domain", "cap_domain", "--root", root, "--json"],
    { encoding: "utf8", windowsHide: true, env: process.env },
  );
  const okPayload = JSON.parse((okCli.stdout || "").trim());
  const okNode = await assessSacCapillarityPayload("cap_domain", {
    root,
    python,
    cliPath,
  });
  if (!deepEqual(okPayload, okNode)) {
    console.error("[FAIL] capillarity MCP≡CLI mismatch", okPayload, okNode);
    process.exit(1);
  }
  if (
    okCli.status !== 0 ||
    okPayload.status !== "SUFFICIENT" ||
    okPayload.fitness_status !== "FIT" ||
    okPayload.payload_status !== "OK" ||
    okPayload.payload_warn != null ||
    okPayload.quality_status !== "PASS"
  ) {
    console.error("[FAIL] capillarity case A expected PASS under budget", okPayload);
    process.exit(1);
  }

  // Case A': OVER_BUDGET must NOT fail quality when coverage+fitness sound
  const overCli = spawnSync(
    python,
    [cliPath, "capillarity", "--domain", "cap_domain", "--root", root, "--json"],
    {
      encoding: "utf8",
      windowsHide: true,
      env: { ...process.env, SAC_CONTEXT_MAX_BYTES: "512" },
    },
  );
  const overPayload = JSON.parse((overCli.stdout || "").trim());
  const overNode = await runCapillarity({
    root,
    python,
    cliPath,
    domainId: "cap_domain",
    env: { SAC_CONTEXT_MAX_BYTES: "512" },
  });
  if (!deepEqual(overPayload, overNode)) {
    console.error(
      "[FAIL] capillarity OVER_BUDGET MCP≡CLI mismatch",
      overPayload,
      overNode,
    );
    process.exit(1);
  }
  if (
    overCli.status !== 0 ||
    overPayload.status !== "SUFFICIENT" ||
    overPayload.fitness_status !== "FIT" ||
    overPayload.payload_status !== "OVER_BUDGET" ||
    overPayload.payload_warn !== "OVER_BUDGET" ||
    overPayload.quality_status !== "PASS"
  ) {
    console.error(
      "[FAIL] capillarity case A' OVER_BUDGET must PASS with payload_warn",
      overPayload,
    );
    process.exit(1);
  }

  // Case B: insufficient claims → still FAIL
  fs.writeFileSync(
    domainsPath,
    [
      existing.trimEnd(),
      "",
      "## cap_domain",
      "- intent: Capillarity budget/fitness fixture",
      "- onboarded: 2026-07-27",
      "- drawer_file: .context/docs/architecture_drawers/02_engines_mechanisms.md",
      "- drawer_refs: MECH-CAP",
      "- anchor_symbols: CapArch, CapRegr",
      "- files:",
      `  - ${relCap}`,
      "- context_scenarios: SUMMARY, EXTEND, REGRESSION",
      "- coverage_claims:",
      `  - CAP_SUMMARY | SUMMARY | ARCH | CapArch | ${relCap}`,
      `  - CAP_EXTEND | EXTEND | ARCH | CapArch | ${relCap}`,
      `  - CAP_REGR | REGRESSION | REGR | CapMissing | ${relCap}`,
      "- on_edit: sac-execution-overlay + get_sac_context + get_sac_constraints",
      "- known_gaps:",
      "",
    ].join("\n"),
    "utf8",
  );
  const insuffCli = spawnSync(
    python,
    [cliPath, "capillarity", "--domain", "cap_domain", "--root", root, "--json"],
    { encoding: "utf8", windowsHide: true, env: process.env },
  );
  const insuffPayload = JSON.parse((insuffCli.stdout || "").trim());
  if (
    insuffCli.status === 0 ||
    insuffPayload.status !== "INSUFFICIENT" ||
    insuffPayload.quality_status !== "FAIL"
  ) {
    console.error("[FAIL] capillarity case B expected INSUFFICIENT FAIL", insuffPayload);
    process.exit(1);
  }

  // Case C: extreme overflow still explicit on Context (no truncate) — covered in assertContext
  console.log(
    "[OK] capillarity A/A'/B: PASS under budget; PASS+WARN over budget; INSUFFICIENT FAIL",
  );
}

async function assertGateBypassedAttestation(root, tagged, outside, python, cliPath) {
  // 1. SAC_ALLOW_UNSCOPED:
  // Off:
  const unscopedOffCli = cliLookup("SmokeArch", root, undefined, python, cliPath);
  if (unscopedOffCli.parsed.gates_bypassed !== undefined) {
    console.error("[FAIL] gates_bypassed must be omitted when SAC_ALLOW_UNSCOPED is off", unscopedOffCli);
    process.exit(1);
  }
  const unscopedOffNode = await getSacConstraintsPayload("SmokeArch", undefined, { root, python, cliPath });
  if (unscopedOffNode.gates_bypassed !== undefined) {
    console.error("[FAIL] gates_bypassed must be omitted in Node when SAC_ALLOW_UNSCOPED is off", unscopedOffNode);
    process.exit(1);
  }
  if (!deepEqual(unscopedOffCli.parsed, unscopedOffNode)) {
    console.error("[FAIL] parity mismatch for unscoped off", unscopedOffCli.parsed, unscopedOffNode);
    process.exit(1);
  }

  // On:
  const envUnscoped = { ...process.env, SAC_ALLOW_UNSCOPED: "1" };
  const unscopedOnCli = cliLookup("SmokeArch", root, undefined, python, cliPath, envUnscoped);
  if (
    !Array.isArray(unscopedOnCli.parsed.gates_bypassed) ||
    !unscopedOnCli.parsed.gates_bypassed.includes("SAC_ALLOW_UNSCOPED") ||
    !(unscopedOnCli.parsed.warnings || []).includes("Gate bypassed by environment override: SAC_ALLOW_UNSCOPED")
  ) {
    console.error("[FAIL] SAC_ALLOW_UNSCOPED on must attest gates_bypassed and warning", unscopedOnCli.parsed);
    process.exit(1);
  }
  const unscopedOnNode = await getSacConstraintsPayload("SmokeArch", undefined, {
    root,
    python,
    cliPath,
    env: { SAC_ALLOW_UNSCOPED: "1" },
  });
  if (!deepEqual(unscopedOnCli.parsed, unscopedOnNode)) {
    console.error("[FAIL] parity mismatch for SAC_ALLOW_UNSCOPED on", unscopedOnCli.parsed, unscopedOnNode);
    process.exit(1);
  }

  // 2. SAC_ALLOW_FILEPATH_OUTSIDE_DOMAINS:
  // Off:
  const outsideOffCli = cliLookup("SmokeOutside", root, outside, python, cliPath);
  if (outsideOffCli.parsed.gates_bypassed !== undefined) {
    console.error("[FAIL] gates_bypassed must be omitted when SAC_ALLOW_FILEPATH_OUTSIDE_DOMAINS is off", outsideOffCli);
    process.exit(1);
  }
  const outsideOffNode = await getSacConstraintsPayload("SmokeOutside", outside, { root, python, cliPath });
  if (outsideOffNode.gates_bypassed !== undefined) {
    console.error("[FAIL] gates_bypassed must be omitted in Node when SAC_ALLOW_FILEPATH_OUTSIDE_DOMAINS is off", outsideOffNode);
    process.exit(1);
  }
  if (!deepEqual(outsideOffCli.parsed, outsideOffNode)) {
    console.error("[FAIL] parity mismatch for outside domains off", outsideOffCli.parsed, outsideOffNode);
    process.exit(1);
  }

  // On:
  const envOutside = { ...process.env, SAC_ALLOW_FILEPATH_OUTSIDE_DOMAINS: "1" };
  const outsideOnCli = cliLookup("SmokeOutside", root, outside, python, cliPath, envOutside);
  if (
    !Array.isArray(outsideOnCli.parsed.gates_bypassed) ||
    !outsideOnCli.parsed.gates_bypassed.includes("SAC_ALLOW_FILEPATH_OUTSIDE_DOMAINS") ||
    !(outsideOnCli.parsed.warnings || []).includes("Gate bypassed by environment override: SAC_ALLOW_FILEPATH_OUTSIDE_DOMAINS")
  ) {
    console.error("[FAIL] SAC_ALLOW_FILEPATH_OUTSIDE_DOMAINS on must attest gates_bypassed and warning", outsideOnCli.parsed);
    process.exit(1);
  }
  const outsideOnNode = await getSacConstraintsPayload("SmokeOutside", outside, {
    root,
    python,
    cliPath,
    env: { SAC_ALLOW_FILEPATH_OUTSIDE_DOMAINS: "1" },
  });
  if (!deepEqual(outsideOnCli.parsed, outsideOnNode)) {
    console.error("[FAIL] parity mismatch for SAC_ALLOW_FILEPATH_OUTSIDE_DOMAINS on", outsideOnCli.parsed, outsideOnNode);
    process.exit(1);
  }

  // 3. SAC_ALLOW_HOP1_FULL_SCAN:
  // Off:
  const hop1OffCli = cliLookup("SmokeRegr", root, tagged, python, cliPath);
  if (hop1OffCli.parsed.gates_bypassed !== undefined) {
    console.error("[FAIL] gates_bypassed must be omitted when SAC_ALLOW_HOP1_FULL_SCAN is off", hop1OffCli);
    process.exit(1);
  }
  const hop1OffNode = await getSacConstraintsPayload("SmokeRegr", tagged, { root, python, cliPath });
  if (hop1OffNode.gates_bypassed !== undefined) {
    console.error("[FAIL] gates_bypassed must be omitted in Node when SAC_ALLOW_HOP1_FULL_SCAN is off", hop1OffNode);
    process.exit(1);
  }
  if (!deepEqual(hop1OffCli.parsed, hop1OffNode)) {
    console.error("[FAIL] parity mismatch for hop1 off", hop1OffCli.parsed, hop1OffNode);
    process.exit(1);
  }

  // On:
  const envHop1 = { ...process.env, SAC_ALLOW_HOP1_FULL_SCAN: "1" };
  const hop1OnCli = cliLookup("SmokeRegr", root, tagged, python, cliPath, envHop1);
  if (
    !Array.isArray(hop1OnCli.parsed.gates_bypassed) ||
    !hop1OnCli.parsed.gates_bypassed.includes("SAC_ALLOW_HOP1_FULL_SCAN") ||
    !(hop1OnCli.parsed.warnings || []).includes("Gate bypassed by environment override: SAC_ALLOW_HOP1_FULL_SCAN")
  ) {
    console.error("[FAIL] SAC_ALLOW_HOP1_FULL_SCAN on must attest gates_bypassed and warning", hop1OnCli.parsed);
    process.exit(1);
  }
  const hop1OnNode = await getSacConstraintsPayload("SmokeRegr", tagged, {
    root,
    python,
    cliPath,
    env: { SAC_ALLOW_HOP1_FULL_SCAN: "1" },
  });
  if (!deepEqual(hop1OnCli.parsed, hop1OnNode)) {
    console.error("[FAIL] parity mismatch for SAC_ALLOW_HOP1_FULL_SCAN on", hop1OnCli.parsed, hop1OnNode);
    process.exit(1);
  }

  console.log("[OK] gates_bypassed attestation & warnings (3 escapes on/off, CLI≡MCP)");
}

async function assertEnvironmentErrors(root, python, cliPath) {
  // 1. Root inexistente
  const nonexistentRoot = path.join(os.tmpdir(), `sac_nonexistent_root_${Date.now()}`);
  const rootMissingCli = spawnSync(
    python,
    [cliPath, "lookup", "SmokeArch", "--root", nonexistentRoot, "--json"],
    { encoding: "utf8", windowsHide: true, env: process.env },
  );
  if (rootMissingCli.status !== 2) {
    console.error("[FAIL] root_not_found CLI exit code must be 2, got", rootMissingCli.status);
    process.exit(1);
  }
  const rootMissingCliPayload = JSON.parse((rootMissingCli.stdout || "").trim());
  if (
    !rootMissingCliPayload.error ||
    rootMissingCliPayload.code !== "sac.environment.root_not_found" ||
    !rootMissingCliPayload.remediation
  ) {
    console.error("[FAIL] root_not_found CLI payload invalid", rootMissingCliPayload);
    process.exit(1);
  }

  const rootMissingNode = await runLookup("SmokeArch", "src/tagged.py", {
    root: nonexistentRoot,
    python,
    cliPath,
  });
  if (!deepEqual(rootMissingCliPayload, rootMissingNode)) {
    console.error("[FAIL] root_not_found parity mismatch", rootMissingCliPayload, rootMissingNode);
    process.exit(1);
  }

  // 2. Root não-diretório (root is a file)
  const fileRoot = path.join(root, "src", "tagged.py");
  const rootFileCli = spawnSync(
    python,
    [cliPath, "lookup", "SmokeArch", "--root", fileRoot, "--json"],
    { encoding: "utf8", windowsHide: true, env: process.env },
  );
  if (rootFileCli.status !== 2) {
    console.error("[FAIL] root_not_directory CLI exit code must be 2, got", rootFileCli.status);
    process.exit(1);
  }
  const rootFileCliPayload = JSON.parse((rootFileCli.stdout || "").trim());
  if (
    !rootFileCliPayload.error ||
    rootFileCliPayload.code !== "sac.environment.root_not_directory" ||
    !rootFileCliPayload.remediation
  ) {
    console.error("[FAIL] root_not_directory CLI payload invalid", rootFileCliPayload);
    process.exit(1);
  }

  const rootFileNode = await runLookup("SmokeArch", "src/tagged.py", {
    root: fileRoot,
    python,
    cliPath,
  });
  if (!deepEqual(rootFileCliPayload, rootFileNode)) {
    console.error("[FAIL] root_not_directory parity mismatch", rootFileCliPayload, rootFileNode);
    process.exit(1);
  }

  // 3. Argumentos inválidos (missing symbol)
  const invalidArgsCli = spawnSync(
    python,
    [cliPath, "lookup", "--root", root, "--json"],
    { encoding: "utf8", windowsHide: true, env: process.env },
  );
  if (invalidArgsCli.status !== 2) {
    console.error("[FAIL] invalid_arguments CLI exit code must be 2, got", invalidArgsCli.status);
    process.exit(1);
  }
  const invalidArgsCliPayload = JSON.parse((invalidArgsCli.stdout || "").trim());
  if (
    !invalidArgsCliPayload.error ||
    invalidArgsCliPayload.code !== "sac.environment.invalid_arguments" ||
    invalidArgsCliPayload.remediation !== "Check command-line syntax."
  ) {
    console.error("[FAIL] invalid_arguments CLI payload invalid", invalidArgsCliPayload);
    process.exit(1);
  }

  const invalidArgsNode = await runCliJson(["lookup", "--root", root, "--json"], {
    root,
    python,
    cliPath,
  });
  if (!deepEqual(invalidArgsCliPayload, invalidArgsNode)) {
    console.error("[FAIL] invalid_arguments parity mismatch", invalidArgsCliPayload, invalidArgsNode);
    process.exit(1);
  }

  console.log("[OK] sac.environment.* error class (root_not_found, root_not_directory, invalid_arguments, CLI≡MCP)");
}

async function main() {
  const python = resolvePython();
  const cliPath = resolveCliPath();
  if (!fs.existsSync(cliPath)) {
    console.error(`[FAIL] CLI missing: ${cliPath}`);
    process.exit(1);
  }

  const { root, tagged, outside, dottedVerifyTargets } = writeFixture();
  assertRelativeAbsoluteRootBytes(root, python, cliPath);
  try {
    await assertListDomains(root, python, cliPath);
    await assertContext(root, python, cliPath);
    await assertDiscover(root, python, cliPath);
    await assertCapillarity(root, python, cliPath);
    await assertUnscopedBlocked(root, python, cliPath);
    await assertOutsideDomainsParity(root, python, cliPath);
    assertPreOnboardLookup(root, outside, python, cliPath);
    await assertDomainMembership(root, tagged, python, cliPath);
    await assertParity(
      "ARCH+path",
      "SmokeArch",
      root,
      tagged,
      python,
      cliPath,
    );
    await assertDottedVerifyParity(root, tagged, python, cliPath, dottedVerifyTargets);
    await assertHop1Scoped(root, tagged, python, cliPath);
    await assertGateBypassedAttestation(root, tagged, outside, python, cliPath);
    await assertEnvironmentErrors(root, python, cliPath);
    await assertValidateTagBlocks(root, python, cliPath);
    await assertPythonMissing(tagged);
    console.log("[OK] smoke exit 0");
    console.log(`SAC_ROOT default would be: ${resolveSacRoot()}`);
    console.log(`mcp dir: ${__dirname}`);
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
}

main().catch((err) => {
  console.error("[FAIL]", err?.message ?? err);
  process.exit(1);
});
