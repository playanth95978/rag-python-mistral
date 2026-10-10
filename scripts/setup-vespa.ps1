$ErrorActionPreference = 'Stop'
Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    docker compose up -d --wait --wait-timeout 180
    if ($LASTEXITCODE -ne 0) { throw 'Echec du demarrage Vespa. Verifier Docker Desktop.' }
    & .\.venv\Scripts\mistral-vespa.exe migrate --app-dir ./vespa_app --config-server http://localhost:19075 --query-port 8085
    if ($LASTEXITCODE -ne 0) { throw 'Echec du deploiement du schema Vespa.' }
    Write-Host 'Vespa prêt sur http://127.0.0.1:8085'
} finally {
    Pop-Location
}
