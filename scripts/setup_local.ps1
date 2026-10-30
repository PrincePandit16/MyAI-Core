$ErrorActionPreference = "Stop"

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
}

function New-RandomSecret([int]$Bytes = 48) {
    $randomBytes = New-Object byte[] $Bytes
    $random = [Security.Cryptography.RandomNumberGenerator]::Create()
    try {
        $random.GetBytes($randomBytes)
    } finally {
        $random.Dispose()
    }
    return [Convert]::ToBase64String($randomBytes) -replace "[/+=]", ""
}

$updates = @{
    POSTGRES_PASSWORD = New-RandomSecret 32
    JWT_SECRET_KEY = New-RandomSecret 48
    MINIO_ACCESS_KEY = "myai-minio-$(New-RandomSecret 16)"
    MINIO_SECRET_KEY = New-RandomSecret 32
    GRAFANA_ADMIN_PASSWORD = New-RandomSecret 32
    COOKIE_SECURE = "false"
}

$lines = Get-Content .env
foreach ($key in $updates.Keys) {
    $value = $updates[$key]
    $pattern = "^$key=.*$"
    if ($lines | Where-Object { $_ -match $pattern }) {
        $lines = $lines | ForEach-Object { if ($_ -match $pattern) { "$key=$value" } else { $_ } }
    } else {
        $lines += "$key=$value"
    }
}

$lines = $lines | ForEach-Object {
    if ($_ -match '^DATABASE_URL=') { "DATABASE_URL=postgresql+psycopg://assistant:$($updates.POSTGRES_PASSWORD)@postgres:5432/assistant" } else { $_ }
}

$lines | Set-Content .env
Write-Host "Local environment configured in .env"
Write-Host "Run: docker compose -f infra/docker-compose.yml up --build"
