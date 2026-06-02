$ErrorActionPreference = "Stop"
$checks = @(
    @{ Name = "auth-service"; Url = "http://127.0.0.1:8000/health" },
    @{ Name = "classifier-service"; Url = "http://127.0.0.1:8001/health" },
    @{ Name = "urgency-service"; Url = "http://127.0.0.1:8002/health" },
    @{ Name = "rag-service"; Url = "http://127.0.0.1:8003/health" },
    @{ Name = "llm-service"; Url = "http://127.0.0.1:8004/health" },
    @{ Name = "api-gateway"; Url = "http://127.0.0.1:8005/health" },
    @{ Name = "qdrant"; Url = "http://127.0.0.1:6333/readyz" }
)

$failed = @()
foreach ($check in $checks) {
    try {
        $response = Invoke-WebRequest -Uri $check.Url -UseBasicParsing -TimeoutSec 5
        Write-Host "PASS $($check.Name) $($response.StatusCode)"
    }
    catch {
        Write-Host "FAIL $($check.Name): $($_.Exception.Message)"
        $failed += $check.Name
    }
}

if ($failed.Count -gt 0) {
    Write-Host "Failed health checks: $($failed -join ', ')"
    exit 1
}

Write-Host "Full-stack smoke health checks passed."
