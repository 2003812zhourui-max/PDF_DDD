param(
    [string]$ProjectDir = "",
    [string]$PythonExe = ""
)

$ErrorActionPreference = "Stop"

if (-not $ProjectDir) {
    $ProjectDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

Set-Location -LiteralPath $ProjectDir

Write-Host ""
Write-Host "PDF_D custom time window runner"
Write-Host "Example: 2026-06-12 03:30:00"
Write-Host ""

$startTime = Read-Host "Start time"
$endTime = Read-Host "End time"
$whCodes = Read-Host "Warehouse codes [US02]"
if (-not $whCodes) { $whCodes = "US02" }

$statuses = Read-Host "Statuses [10,15,20,30]"
if (-not $statuses) { $statuses = "10,15,20,30" }

$workersText = Read-Host "Workers [5]"
if (-not $workersText) { $workersText = "5" }
$workers = [int]$workersText

$outputName = Read-Host "Output name [auto]"

$scriptPath = Join-Path $PSScriptRoot "run_window_batches_to_master.ps1"
$argsList = @(
    "-ExecutionPolicy", "Bypass",
    "-File", $scriptPath,
    "-StartTime", $startTime,
    "-EndTime", $endTime,
    "-WhCodes", $whCodes,
    "-Statuses", $statuses,
    "-Workers", [string]$workers,
    "-ProjectDir", $ProjectDir,
    "-StopOnError"
)

if ($PythonExe) {
    $argsList += @("-PythonExe", $PythonExe)
}
if ($outputName) {
    $argsList += @("-MasterOutputName", $outputName)
}

Write-Host ""
Write-Host "Running selected time window..."
& powershell @argsList

Write-Host ""
Read-Host "Done. Press Enter to close"
