#Requires -Version 7.4
<#
.SYNOPSIS
    Local SAC CI guard wrapper for pre-push / manual validation.

.DESCRIPTION
    Runs sac-context/src/sac_scan.py diff-check against a git base ref and propagates the
    exit code. Optionally also runs validate to detect orphan SAC tags.
    Use this script on Windows before pushing, or integrate it in a
    local pre-push hook.

.PARAMETER Base
    Git base ref to diff against (default: origin/main).

.PARAMETER SkipValidate
    Skip the validate step (orphan tag detection).

.EXAMPLE
    .\scripts\sac_ci_guard.ps1
    .\scripts\sac_ci_guard.ps1 -Base origin/develop
    .\scripts\sac_ci_guard.ps1 -SkipValidate
#>
[CmdletBinding()]
param(
    [string]$Base = "origin/main",
    [switch]$SkipValidate,
    [switch]$WarningOnly
)

$ErrorActionPreference = "Stop"

# Verify we are inside a git repository.
$gitRoot = git rev-parse --show-toplevel 2>$null
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($gitRoot)) {
    Write-Error "sac_ci_guard must be run from inside a git repository."
    exit 2
}

# Resolve the script location so it works regardless of invocation directory.
# The script lives at <repoRoot>/sac-context/ci/sac_ci_guard.ps1.
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)
$scanner = Join-Path $repoRoot "sac-context" "src" "sac_scan.py"

if (-not (Test-Path $scanner)) {
    Write-Error "SAC scanner not found: $scanner"
    exit 2
}

Write-Host "Running SAC diff-check against base: $Base" -ForegroundColor Cyan

& python $scanner diff-check --base $Base
$diffExitCode = $LASTEXITCODE

switch ($diffExitCode) {
    0 {
        Write-Host "SAC diff-check passed." -ForegroundColor Green
    }
    1 {
        Write-Host "SAC diff-check FAILED: a SAC:REGR target was changed without coverage or explicit ACK." -ForegroundColor Red
        Write-Host "To override a specific symbol, include this exact line in the PR body or in a commit message:" -ForegroundColor Yellow
        Write-Host "    SAC-ACK: <symbol_name>" -ForegroundColor Yellow
        Write-Host "The token 'SAC-ACK: all' is ignored." -ForegroundColor Yellow
    }
    2 {
        Write-Host "SAC diff-check usage or I/O error." -ForegroundColor Red
    }
    default {
        Write-Host "SAC diff-check exited with unexpected code: $diffExitCode" -ForegroundColor Red
    }
}

if ($diffExitCode -ne 0) {
    exit $diffExitCode
}

if (-not $SkipValidate) {
    Write-Host "Running SAC validate..." -ForegroundColor Cyan
    $validateArgs = @("validate", "--root", $repoRoot)
    if ($WarningOnly) {
        $validateArgs += "--warning-only"
        Write-Host "Warning-only mode: orphan tags will not fail the guard." -ForegroundColor Yellow
    }
    & python $scanner @validateArgs
    $validateExitCode = $LASTEXITCODE

    switch ($validateExitCode) {
        0 {
            if ($WarningOnly) {
                Write-Host "SAC validate completed (warning-only)." -ForegroundColor Green
            }
            else {
                Write-Host "SAC validate passed." -ForegroundColor Green
            }
        }
        1 {
            Write-Host "SAC validate FAILED: orphan SAC:ARCH/SAC:REGR/SAC:DEPRECATED tags found." -ForegroundColor Red
            Write-Host "To ACK an orphan symbol, add a comment on its line with:" -ForegroundColor Yellow
            Write-Host "    SAC-ACK: <symbol_name>" -ForegroundColor Yellow
        }
        2 {
            Write-Host "SAC validate usage or I/O error." -ForegroundColor Red
        }
        default {
            Write-Host "SAC validate exited with unexpected code: $validateExitCode" -ForegroundColor Red
        }
    }

    exit $validateExitCode
}

exit $diffExitCode
