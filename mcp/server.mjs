#!/usr/bin/env node
/**
 * SAC MCP Node stdio adapter (primary Cursor entry).
 *
 * Thin wrapper: zero tag parse/heuristics. Spawns Python sac_scan.py and
 * returns JSON identical to CLI --json (COR-GATE-1 idempotence).
 *
 * Tools:
 *   list_sac_domains     — Route: locals from .sac/domains.md (no tag scan)
 *   discover_sac         — Discover: tags only under domain files:
 *   get_sac_context      — Context: anchors + all REGR/DEPRECATED + scoped hop1
 *   get_sac_constraints  — Verify: filepath optional in schema; empty →
 *                          filepath_required PAUSE (≡ CLI), zero matches
 *   assess_sac_capillarity — On-demand claims vs tags; never boot/L0
 *
 * Env:
 *   SAC_ROOT   — project root to scan (default: repo root above sac-context/)
 *   SAC_PYTHON — Python executable (default: python)
 *   SAC_TRIM_WARNINGS — cap warnings in lookup JSON (default: 20)
 *   SAC_ALLOW_UNSCOPED — CLI escape to allow lookup without --path (debug)
 *   SAC_ALLOW_FILEPATH_OUTSIDE_DOMAINS — allow Verify path not in domains files:
 *   SAC_ALLOW_HOP1_FULL_SCAN — allow hop1 full-root when domains exist (debug)
 */

import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/** Must match sac_domains.PAUSE_HINT (SSOT is Python; smoke asserts parity). */
export const PAUSE_HINT =
  "Qual domain_id expandir, ou informe filepath direto?";

/** Default project root: sac-context/mcp → ../.. */
export function resolveSacRoot() {
  if (process.env.SAC_ROOT && process.env.SAC_ROOT.trim()) {
    return path.resolve(process.env.SAC_ROOT.trim());
  }
  return path.resolve(__dirname, "..", "..");
}

export function resolvePython() {
  if (process.env.SAC_PYTHON && process.env.SAC_PYTHON.trim()) {
    return process.env.SAC_PYTHON.trim();
  }
  return "python";
}

export function resolveCliPath() {
  return path.resolve(__dirname, "..", "src", "sac_scan.py");
}

/**
 * Read and validate project version dynamically from package.json (SSOT).
 * Throws an explicit named error on failure — never falls back to a default version.
 */
export function resolvePackageVersion() {
  const pkgPath = path.resolve(__dirname, "package.json");
  try {
    const raw = fs.readFileSync(pkgPath, "utf-8");
    const parsed = JSON.parse(raw);
    if (!parsed.version || typeof parsed.version !== "string" || !parsed.version.trim()) {
      throw new Error(`Invalid or missing 'version' field in ${pkgPath}`);
    }
    return parsed.version.trim();
  } catch (err) {
    throw new Error(`Failed to resolve package version from ${pkgPath}: ${err.message}`);
  }
}

export const LOOKUP_TIMEOUT_MS = 30_000;

/**
 * Spawn CLI; return parsed JSON object.
 * @param {string[]} cliArgs args after sac_scan.py
 * @param {{ root?: string, python?: string, cliPath?: string, timeoutMs?: number, env?: Record<string,string> }} [opts]
 * @returns {Promise<object>}
 */
export function runCliJson(cliArgs, opts = {}) {
  const root = opts.root ?? resolveSacRoot();
  const python = opts.python ?? resolvePython();
  const cliPath = opts.cliPath ?? resolveCliPath();
  const timeoutMs = opts.timeoutMs ?? LOOKUP_TIMEOUT_MS;

  const args = [cliPath, ...cliArgs];
  if (!cliArgs.includes("--root")) {
    args.push("--root", root);
  }

  const childEnv = { ...process.env, ...(opts.env || {}) };
  if (!childEnv.SAC_TRIM_WARNINGS) {
    childEnv.SAC_TRIM_WARNINGS = "20";
  }

  return new Promise((resolve, reject) => {
    let settled = false;
    let stdout = "";
    let stderr = "";

    let child;
    try {
      child = spawn(python, args, {
        env: childEnv,
        windowsHide: true,
      });
    } catch (err) {
      reject(
        new Error(
          `Failed to spawn SAC Python CLI (${python}): ${err?.message ?? err}`,
        ),
      );
      return;
    }

    const timer = setTimeout(() => {
      if (settled) return;
      settled = true;
      try {
        child.kill();
      } catch {
        /* ignore */
      }
      reject(new Error(`SAC CLI timed out after ${timeoutMs}ms`));
    }, timeoutMs);

    child.stdout.on("data", (chunk) => {
      stdout += chunk.toString("utf8");
    });
    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString("utf8");
    });

    child.on("error", (err) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      const code = err?.code;
      if (code === "ENOENT") {
        reject(
          new Error(
            `SAC Python not found (SAC_PYTHON=${python}). Install Python 3.12+ or set SAC_PYTHON.`,
          ),
        );
        return;
      }
      reject(
        new Error(
          `SAC Python spawn error (${python}): ${err?.message ?? err}`,
        ),
      );
    });

    child.on("close", (code) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      const text = stdout.trim();
      if (code !== 0) {
        if (text) {
          try {
            const parsed = JSON.parse(text);
            // Capillarity exits 1 when quality_status!=PASS but still returns
            // a canonical JSON payload (no error:true). Accept that shape.
            if (
              parsed &&
              (parsed.error || parsed.mode === "capillarity")
            ) {
              resolve(parsed);
              return;
            }
          } catch {
            /* fall through */
          }
        }
        reject(
          new Error(
            `SAC CLI exited ${code}. stderr: ${stderr.trim() || "(empty)"} stdout: ${text.slice(0, 200)}`,
          ),
        );
        return;
      }
      if (!text) {
        reject(
          new Error(
            `SAC CLI returned empty stdout. stderr: ${stderr.trim() || "(empty)"}`,
          ),
        );
        return;
      }
      try {
        resolve(JSON.parse(text));
      } catch (err) {
        reject(
          new Error(
            `SAC CLI returned non-JSON stdout: ${err?.message ?? err}. raw=${text.slice(0, 200)}`,
          ),
        );
      }
    });
  });
}

/**
 * Lookup via CLI. Omitting filepath yields filepath_required PAUSE (≡ CLI).
 * @param {string} symbolName
 * @param {string | undefined} filepath
 * @param {{ root?: string, python?: string, cliPath?: string, timeoutMs?: number, domainId?: string }} [opts]
 */
export function runLookup(symbolName, filepath, opts = {}) {
  const root = opts.root ?? resolveSacRoot();
  const args = ["lookup", symbolName, "--root", root, "--json"];
  const trimmed = filepath?.trim();
  if (trimmed) {
    args.push("--path", trimmed);
  }
  if (opts.domainId && String(opts.domainId).trim()) {
    args.push("--domain", String(opts.domainId).trim());
  }
  return runCliJson(args, opts);
}

/**
 * @param {{ root?: string, python?: string, cliPath?: string, timeoutMs?: number, domainId?: string }} [opts]
 */
export function runListDomains(opts = {}) {
  const root = opts.root ?? resolveSacRoot();
  const args = ["list-domains", "--root", root, "--json"];
  if (opts.domainId && String(opts.domainId).trim()) {
    args.push("--domain", String(opts.domainId).trim());
  }
  return runCliJson(args, opts);
}

/**
 * @param {{ root?: string, python?: string, cliPath?: string, timeoutMs?: number, domainId?: string }} [opts]
 */
export function runDiscover(opts = {}) {
  const root = opts.root ?? resolveSacRoot();
  const domainId = opts.domainId && String(opts.domainId).trim();
  const args = ["discover", "--root", root, "--json"];
  if (domainId) {
    args.push("--domain", domainId);
  } else {
    // CLI requires --domain; preserve its structured domain_id_required response
    args.push("--domain", "");
  }
  return runCliJson(args, opts);
}

export function runContext(opts = {}) {
  const root = opts.root ?? resolveSacRoot();
  const domainId = opts.domainId && String(opts.domainId).trim();
  const args = [
    "context",
    "--root",
    root,
    "--json",
    "--domain",
    domainId || "",
  ];
  return runCliJson(args, opts);
}

export function runCapillarity(opts = {}) {
  const root = opts.root ?? resolveSacRoot();
  const domainId = opts.domainId && String(opts.domainId).trim();
  const args = [
    "capillarity",
    "--root",
    root,
    "--json",
    "--domain",
    domainId || "",
  ];
  return runCliJson(args, opts);
}

export function jsonToolResult(obj, isError = false) {
  return {
    isError: Boolean(isError || obj?.error),
    content: [
      {
        type: "text",
        text: serializePayload(obj),
      },
    ],
  };
}

export function serializePayload(obj) {
  return JSON.stringify(obj, null, 1);
}

/**
 * MCP-only envelope (COR-GATE-1: CLI payloads stay unchanged).
 * @param {string} tool
 * @param {number} startedAt performance.now() at handler entry
 * @param {object} payload CLI JSON or error object
 * @param {Record<string, unknown>} [extra]
 */
export function withPerf(tool, startedAt, payload, extra = {}) {
  const result = {
    ...payload,
    _perf: {
      tool,
      elapsed_ms: Math.round(performance.now() - startedAt),
      ...extra,
      payload_bytes: 0,
    },
  };
  let measured = -1;
  while (result._perf.payload_bytes !== measured) {
    measured = result._perf.payload_bytes;
    result._perf.payload_bytes = Buffer.byteLength(serializePayload(result), "utf8");
  }
  return result;
}

/**
 * Handler body for get_sac_constraints (exported for smoke parity).
 * @param {string} symbolName
 * @param {string | undefined} filepath
 * @param {{ root?: string, python?: string, cliPath?: string, timeoutMs?: number, domainId?: string }} [opts]
 */
export async function getSacConstraintsPayload(symbolName, filepath, opts = {}) {
  return runLookup(symbolName, filepath, opts);
}

/**
 * @param {string | undefined} domainId
 * @param {{ root?: string, python?: string, cliPath?: string, timeoutMs?: number }} [opts]
 */
export async function discoverSacPayload(domainId, opts = {}) {
  return runDiscover({ ...opts, domainId });
}

export async function getSacContextPayload(domainId, opts = {}) {
  return runContext({ ...opts, domainId });
}

export async function assessSacCapillarityPayload(domainId, opts = {}) {
  return runCapillarity({ ...opts, domainId });
}

export function isEnvironmentError(err) {
  const msg = err?.message ?? String(err);
  return (
    err?.code?.startsWith?.("sac.environment.") ||
    /not found|ENOENT|SAC_PYTHON|spawn error|Failed to spawn|timed out/i.test(msg)
  );
}

export function formatMcpCatchError(tool, err, extra = {}) {
  const msg = err?.message ?? String(err);
  if (isEnvironmentError(err)) {
    const isMissingPython = /not found|ENOENT|SAC_PYTHON/i.test(msg);
    const isTimeout = /timed out/i.test(msg);
    return {
      error: true,
      code: isMissingPython
        ? "sac.environment.python_missing"
        : isTimeout
          ? "sac.environment.timeout"
          : (err?.code || "sac.environment_error"),
      message: msg,
      remediation: isMissingPython
        ? "Install Python 3.12+ or set SAC_PYTHON to a valid Python executable."
        : "Check environment, permissions, and command arguments.",
      pause_hint: PAUSE_HINT,
      hint_tool: "list_sac_domains",
      ...extra,
    };
  }

  const fallbackCodes = {
    list_sac_domains: "list_domains_failed",
    get_sac_context: "context_failed",
    discover_sac: "discover_failed",
    get_sac_constraints: "lookup_failed",
    assess_sac_capillarity: "capillarity_failed",
  };

  return {
    error: true,
    code: fallbackCodes[tool] || "unknown_error",
    message: msg,
    pause_hint: PAUSE_HINT,
    hint_tool: "list_sac_domains",
    ...extra,
  };
}

export function createServer() {
  const version = resolvePackageVersion();
  const server = new McpServer({
    name: "sac",
    version,
  });

  server.tool(
    "list_sac_domains",
    `MANDATORY FIRST CALL for code or architecture work in a SAC-enabled project. Route (L0) returns ONLY domain_id + summary + files_count. Auto-select and expand only when exactly one intent matches; zero matches → bounded-unmapped search; multiple matches → pause. Never dump files or expand multiple domains. Pause: "${PAUSE_HINT}"`,
    {
      domain_id: z
        .string()
        .optional()
        .describe(
          "Omit = L0 catalog. Set only after the user or an unambiguous single-intent route selected one domain.",
        ),
    },
    async (args) => {
      const startedAt = performance.now();
      const domainId = args?.domain_id?.trim() || undefined;
      try {
        const result = await runListDomains({ domainId });
        return jsonToolResult(
          withPerf("list_sac_domains", startedAt, result, {
            domain_id: domainId ?? null,
          }),
          Boolean(result?.error),
        );
      } catch (err) {
        return jsonToolResult(
          withPerf(
            "list_sac_domains",
            startedAt,
            formatMcpCatchError("list_sac_domains", err, { domain_id: domainId ?? null }),
            { domain_id: domainId ?? null },
          ),
          true,
        );
      }
    },
  );

  server.tool(
    "get_sac_context",
    `Context fast path: after exactly one domain is selected, return constraints for its anchors plus every REGR and DEPRECATED tag and scoped hop1 in one compact payload. A DEPRECATED tag includes replacement and blocks new use. Constraints always come from source SAC tags. Over SAC_CONTEXT_MAX_BYTES (default 12288) returns explicit context_payload_too_large with no constraints — MUST discover_sac then get_sac_constraints; MUST NOT thin files:/tags/claims. Ambiguous route → do not call.`,
    {
      domain_id: z
        .string()
        .describe("Required domain_id selected by an unambiguous L0 route."),
    },
    async (args) => {
      const startedAt = performance.now();
      const domainId = args?.domain_id?.trim() || "";
      try {
        const result = await getSacContextPayload(domainId);
        return jsonToolResult(
          withPerf("get_sac_context", startedAt, result, {
            domain_id: domainId,
          }),
          Boolean(result?.error),
        );
      } catch (err) {
        return jsonToolResult(
          withPerf(
            "get_sac_context",
            startedAt,
            formatMcpCatchError("get_sac_context", err, { domain_id: domainId || null }),
            { domain_id: domainId || null },
          ),
          true,
        );
      }
    },
  );

  server.tool(
    "discover_sac",
    `Discover (L1): scan SAC tags ONLY under files: of one domain_id — no full-repo walk, no rg. Returns SLIM cards only: file, line, tag_type, symbol (+ verify[] for REGR). NO constraint/trigger here — those come from get_sac_constraints. FORBIDDEN: dump full JSON to chat; use overlay skill.`,
    {
      domain_id: z
        .string()
        .describe("Required domain_id from list_sac_domains catalog/expand."),
    },
    async (args) => {
      const startedAt = performance.now();
      const domainId = args?.domain_id?.trim() || "";
      try {
        const result = await discoverSacPayload(domainId);
        return jsonToolResult(
          withPerf("discover_sac", startedAt, result, { domain_id: domainId }),
          Boolean(result?.error),
        );
      } catch (err) {
        return jsonToolResult(
          withPerf(
            "discover_sac",
            startedAt,
            formatMcpCatchError("discover_sac", err, { domain_id: domainId || null }),
            { domain_id: domainId || null },
          ),
          true,
        );
      }
    },
  );

  server.tool(
    "get_sac_constraints",
    `Verify (L2): SAC JSON ≡ CLI lookup. filepath optional in schema; if omitted/empty returns filepath_required PAUSE (zero matches) — same JSON as CLI. Optional domain_id scopes membership + hop1 to that domain's files:. Then ask user: "${PAUSE_HINT}" Do NOT invent filepath. Do NOT retry with guessed path. Do NOT dump full JSON to chat.`,
    {
      symbol_name: z.string().describe("Tagged symbol name to look up"),
      filepath: z
        .string()
        .optional()
        .describe(
          "Relative path under .sac/domains.md files:. Omit to receive filepath_required PAUSE (then list_sac_domains or ask user).",
        ),
      domain_id: z
        .string()
        .optional()
        .describe(
          "Optional. When set, filepath must belong to this domain; hop1 scopes to its files:.",
        ),
    },
    async ({ symbol_name, filepath, domain_id }) => {
      const startedAt = performance.now();
      const trimmedPath = filepath?.trim() || undefined;
      const domainId = domain_id?.trim() || undefined;
      try {
        const result = await getSacConstraintsPayload(symbol_name, trimmedPath, {
          domainId,
        });
        return jsonToolResult(
          withPerf("get_sac_constraints", startedAt, result, {
            symbol_name,
            filepath: trimmedPath ?? null,
            domain_id: domainId ?? null,
          }),
          Boolean(result?.error),
        );
      } catch (err) {
        return jsonToolResult(
          withPerf(
            "get_sac_constraints",
            startedAt,
            formatMcpCatchError("get_sac_constraints", err, {
              symbol_name,
              filepath: trimmedPath ?? null,
              domain_id: domainId ?? null,
            }),
            {
              symbol_name,
              filepath: trimmedPath ?? null,
              domain_id: domainId ?? null,
            },
          ),
          true,
        );
      }
    },
  );

  server.tool(
    "assess_sac_capillarity",
    `On-demand capillarity assessor (NOT part of boot/L0). After an unambiguous domain_id, compare declared coverage_claims against physical SAC tags in domain files. Returns (A) status UNRATED|INVALID_CONTRACT|INSUFFICIENT|SUFFICIENT, (B) fitness_status TOO_THIN|UNFIT|OVER_SELECT|FIT, (C) payload_status OK|OVER_BUDGET plus optional payload_warn. quality_status=PASS when SUFFICIENT and fitness_status=FIT and payload is OK or OVER_BUDGET (OVER_BUDGET is WARN-only — MUST NOT thin domain to chase PASS). Call only on explicit audit/onboard/suspected_stale/context overflow — never during normal Route→Context boot. MCP payload ≡ CLI capillarity --json plus _perf.`,
    {
      domain_id: z
        .string()
        .describe("Required domain_id selected for on-demand capillarity assessment."),
    },
    async (args) => {
      const startedAt = performance.now();
      const domainId = args?.domain_id?.trim() || "";
      try {
        const result = await assessSacCapillarityPayload(domainId);
        return jsonToolResult(
          withPerf("assess_sac_capillarity", startedAt, result, {
            domain_id: domainId,
          }),
          Boolean(result?.error) || result?.quality_status === "FAIL",
        );
      } catch (err) {
        return jsonToolResult(
          withPerf(
            "assess_sac_capillarity",
            startedAt,
            formatMcpCatchError("assess_sac_capillarity", err, { domain_id: domainId || null }),
            { domain_id: domainId || null },
          ),
          true,
        );
      }
    },
  );

  return server;
}

async function main() {
  const server = createServer();
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

const isMain =
  process.argv[1] &&
  path.resolve(process.argv[1]) === path.resolve(__filename);

if (isMain) {
  main().catch((err) => {
    console.error(err?.message ?? err);
    process.exit(1);
  });
}
