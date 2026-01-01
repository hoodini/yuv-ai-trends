# Set encoding environment variables
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

# Start backend with environment variables inherited and output redirected
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = ".venv\Scripts\python.exe"
$psi.Arguments = "api.py"
$psi.UseShellExecute = $false
$psi.CreateNoWindow = $false
$psi.EnvironmentVariables["PYTHONIOENCODING"] = "utf-8"
$psi.EnvironmentVariables["PYTHONUTF8"] = "1"
$backend = [System.Diagnostics.Process]::Start($psi)
Write-Host "Backend started with PID: $($backend.Id)"

Set-Location ui
$frontend = Start-Process "npm.cmd" -ArgumentList "run dev" -PassThru -NoNewWindow
Write-Host "Frontend started with PID: $($frontend.Id)"

Write-Host "App is running! Open http://localhost:5173 in your browser."
Write-Host "Press Ctrl+C to stop (you may need to manually kill processes if this script exits)."
