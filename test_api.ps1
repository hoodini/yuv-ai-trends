$body = @{
    time_range = "daily"
    limit = 50
    disable_ai = $false
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/generate" -Method Post -Body $body -ContentType "application/json"
