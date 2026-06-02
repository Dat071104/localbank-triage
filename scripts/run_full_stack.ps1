param(
    [string[]]$Services = @(
        "postgres",
        "redis",
        "qdrant",
        "auth-service",
        "classifier-service",
        "urgency-service",
        "rag-service",
        "llm-service",
        "api-gateway",
        "worker-service"
    )
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location -LiteralPath $RepoRoot

Write-Host "Validating Docker Compose configuration..."
docker compose config --quiet

Write-Host "Starting LocalBank services: $($Services -join ', ')"
docker compose up -d @Services

Write-Host "Services requested. Run scripts\\smoke_full_stack.ps1 for health checks."
