# Kill all Python and Node processes
Get-Process python,node -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Host "All processes killed"
