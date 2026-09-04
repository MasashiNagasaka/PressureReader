param(
  [Parameter(Mandatory = $true)]
  [string]$Url,
  [Parameter(Mandatory = $true)]
  [string]$TargetPath
)

$ErrorActionPreference = "Stop"

function Write-Info($msg) {
  Write-Host "[whitelist-update] $msg"
}

try {
  if (-not ($Url -match '^https?://')) {
    throw "URL must start with http:// or https://"
  }

  $targetDir = Split-Path -Parent $TargetPath
  if (-not [string]::IsNullOrWhiteSpace($targetDir)) {
    New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
  }

  $tmpPath = "$TargetPath.tmp"

  Write-Info "Downloading: $Url"
  Invoke-WebRequest -Uri $Url -UseBasicParsing -OutFile $tmpPath

  $content = Get-Content -Raw -Encoding utf8 $tmpPath
  if ([string]::IsNullOrWhiteSpace($content)) {
    Remove-Item -Force $tmpPath
    throw "Downloaded file is empty"
  }

  Move-Item -Force $tmpPath $TargetPath
  Write-Info "Updated: $TargetPath"
  exit 0
}
catch {
  if (Test-Path "$TargetPath.tmp") {
    Remove-Item -Force "$TargetPath.tmp"
  }
  Write-Error "[whitelist-update] Failed: $($_.Exception.Message)"
  exit 1
}

