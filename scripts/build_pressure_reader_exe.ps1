param(
    [string]$PythonExe = "C:\nagasaka\python\testPressR\Scripts\python.exe",
    [switch]$DebugConsole
)

$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

if (!(Test-Path -LiteralPath $PythonExe)) {
    throw "Python executable not found: $PythonExe"
}

$entryScript = Join-Path $projectRoot "src\PressureReader.py"
$iconFile = Join-Path $projectRoot "src\PR_logo_2.ico"
$distPath = Join-Path $projectRoot "dist"
$workPath = Join-Path $projectRoot "build"
$specPath = $projectRoot
$hooksPath = Join-Path $projectRoot "build_hooks"

if (!(Test-Path -LiteralPath $entryScript)) {
    throw "Entry script not found: $entryScript"
}
if (!(Test-Path -LiteralPath $iconFile)) {
    throw "Icon file not found: $iconFile"
}
if (!(Test-Path -LiteralPath $hooksPath)) {
    throw "Hook directory not found: $hooksPath"
}

$exeName = if ($DebugConsole) { "PressureReader_debug" } else { "PressureReader" }
$modeArg = if ($DebugConsole) { "--console" } else { "--windowed" }

$args = @(
    "-m", "PyInstaller",
    "--noconfirm",
    "--clean",
    "--onefile",
    $modeArg,
    "--name", $exeName,
    "--icon", $iconFile,
    "--runtime-tmpdir", ".\_pressure_tmp",
    "--distpath", $distPath,
    "--workpath", $workPath,
    "--specpath", $specPath,
    "--additional-hooks-dir", $hooksPath,
    "--collect-submodules", "tkinter",
    "--add-data", "$projectRoot\src\pr_images;pr_images",
    "--add-data", "$projectRoot\src\config;config",
    "--add-data", "$projectRoot\src\poppler;poppler",
    "--add-data", "C:\Users\Z627956\AppData\Local\Programs\Python\Python313\tcl\tcl8.6;_tcl_data",
    "--add-data", "C:\Users\Z627956\AppData\Local\Programs\Python\Python313\tcl\tk8.6;_tk_data",
    $entryScript
)

Write-Host "Building $exeName ..."
& $PythonExe @args

$exePath = Join-Path $distPath "$exeName.exe"
if (!(Test-Path -LiteralPath $exePath)) {
    throw "Build finished, but exe not found: $exePath"
}

$exe = Get-Item -LiteralPath $exePath
Write-Host ""
Write-Host "Build complete."
Write-Host "Output : $($exe.FullName)"
Write-Host "Size   : $($exe.Length) bytes"
Write-Host "Time   : $($exe.LastWriteTime)"
