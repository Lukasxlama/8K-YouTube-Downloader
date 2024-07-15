$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$scriptPath = Join-Path $scriptDir "__main__.py"

$startInfo = New-Object System.Diagnostics.ProcessStartInfo
$startInfo.FileName = "python"
$startInfo.Arguments = "`"$scriptPath`""
$startInfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden

[System.Diagnostics.Process]::Start($startInfo)
