param(
    [switch]$SkipFrontendBuild
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$FrontendRoot = Join-Path $RepoRoot "frontend-app"
$TauriConfig = Join-Path $RepoRoot "src-tauri\tauri.conf.json"
Set-Location -LiteralPath $RepoRoot

function Get-ToolVersion {
    param(
        [string]$Name,
        [string[]]$ToolArgs = @("--version")
    )
    $command = Get-Command $Name -ErrorAction SilentlyContinue
    if ($null -eq $command) {
        return @{ available = $false; version = "NOT FOUND" }
    }
    try {
        $version = & $Name @ToolArgs 2>&1 | Select-Object -First 1
        return @{ available = $true; version = "$version" }
    }
    catch {
        return @{ available = $false; version = "ERROR: $($_.Exception.Message)" }
    }
}

Write-Host "LocalBank desktop readiness check"
Write-Host "Repo: $RepoRoot"

$node = Get-ToolVersion "node"
$npm = Get-ToolVersion "npm"
$rustc = Get-ToolVersion "rustc"
$cargo = Get-ToolVersion "cargo"

Write-Host "Node:  $($node.version)"
Write-Host "npm:   $($npm.version)"
Write-Host "rustc: $($rustc.version)"
Write-Host "cargo: $($cargo.version)"
Write-Host "Windows prerequisites: install Microsoft C++ Build Tools and WebView2 Runtime for Tauri Windows bundles."
Write-Host "Rust install: https://rustup.rs/ then open a new shell and rerun this check."

$configOk = $false
if (Test-Path -LiteralPath $TauriConfig) {
    try {
        $config = Get-Content -LiteralPath $TauriConfig -Raw | ConvertFrom-Json
        $configOk = [bool]$config.identifier -and [bool]$config.build.frontendDist
        Write-Host "Tauri config: PASS identifier=$($config.identifier) frontendDist=$($config.build.frontendDist)"
    }
    catch {
        Write-Host "Tauri config: FAIL $($_.Exception.Message)"
    }
}
else {
    Write-Host "Tauri config: FAIL missing src-tauri\tauri.conf.json"
}

$frontendOk = $false
if ($SkipFrontendBuild) {
    $frontendOk = Test-Path -LiteralPath (Join-Path $FrontendRoot "dist\index.html")
    $frontendStatus = if ($frontendOk) { "PASS existing dist found" } else { "NOT RUN and no existing dist found" }
    Write-Host "Frontend build: $frontendStatus"
}
elseif (Test-Path -LiteralPath (Join-Path $FrontendRoot "package.json")) {
    Push-Location -LiteralPath $FrontendRoot
    try {
        npm run build
        $frontendOk = $true
        Write-Host "Frontend build: PASS"
    }
    catch {
        Write-Host "Frontend build: FAIL $($_.Exception.Message)"
    }
    finally {
        Pop-Location
    }
}
else {
    Write-Host "Frontend build: FAIL missing frontend-app\package.json"
}

if ($node.available -and $npm.available -and $rustc.available -and $cargo.available -and $configOk -and $frontendOk) {
    Write-Host "Desktop readiness verdict: PASS - Tauri build prerequisites are visible in this shell."
    exit 0
}

Write-Host "Desktop readiness verdict: PARTIAL - web demo can still run, but desktop installer build is blocked until missing prerequisites/config/build issues are fixed."
exit 0
