param(
  [Parameter(Mandatory = $true)]
  [string]$RepoUrl,
  [Parameter(Mandatory = $true)]
  [string]$TargetPath,
  [Parameter(Mandatory = $true)]
  [string]$RelativeFilePath,
  [string]$Branch = "main"
)

$ErrorActionPreference = "Stop"

function Write-Info($msg) {
  Write-Host "[whitelist-update] $msg"
}

$tmpRoot = $null

try {
  if (-not ($RepoUrl -match '^https://github\.com/.+')) {
    throw "RepoUrl must be a GitHub HTTPS repository URL"
  }

  if (-not ($RepoUrl.ToLower().EndsWith(".git"))) {
    $RepoUrl = "$RepoUrl.git"
  }

  if ([string]::IsNullOrWhiteSpace($RelativeFilePath)) {
    throw "RelativeFilePath must not be empty"
  }

  if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "git command not found"
  }

  $targetDir = Split-Path -Parent $TargetPath
  if (-not [string]::IsNullOrWhiteSpace($targetDir)) {
    New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
  }

  $tmpRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("whitelist-git-" + [System.Guid]::NewGuid().ToString("N"))
  New-Item -ItemType Directory -Force -Path $tmpRoot | Out-Null

  Write-Info "Cloning: $RepoUrl (branch: $Branch)"
  git clone --depth 1 --branch $Branch -- $RepoUrl $tmpRoot | Out-Null

  $sourcePath = Join-Path $tmpRoot $RelativeFilePath
  if (-not (Test-Path $sourcePath)) {
    throw "File not found in repository: $RelativeFilePath"
  }

  $content = Get-Content -Raw -Encoding utf8 $sourcePath
  if ([string]::IsNullOrWhiteSpace($content)) {
    throw "Source file is empty: $RelativeFilePath"
  }

  Set-Content -Path $TargetPath -Encoding utf8 -Value $content
  Write-Info "Updated: $TargetPath"
  exit 0
}
catch {
  Write-Error "[whitelist-update] Failed: $($_.Exception.Message)"
  exit 1
}
finally {
  if ($tmpRoot -and (Test-Path $tmpRoot)) {
    Remove-Item -LiteralPath $tmpRoot -Recurse -Force -ErrorAction SilentlyContinue
  }
}
