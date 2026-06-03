$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location -LiteralPath $RepoRoot

$forbiddenPattern = "_local_ai_ops|\.zone_context\.md|(^|/)data/|\.env$|\.sqlite$|\.db$|qdrant_storage|postgres_data|redis_data|minio_data|prometheus_data|grafana_data|mlruns|artifacts|node_modules|(^|/)dist/|(^|/)build/|playwright-report|test-results|src-tauri/target"
$tracked = git ls-files
$offenders = $tracked | Where-Object { $_ -match $forbiddenPattern -and $_ -notmatch "\.env\.example$" }

if ($offenders.Count -gt 0) {
    Write-Host "Forbidden tracked files found:"
    $offenders | ForEach-Object { Write-Host " - $_" }
    exit 1
}

Write-Host "Repo hygiene check passed: no forbidden generated/private paths are tracked."
