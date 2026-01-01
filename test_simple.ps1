try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/generate" `
        -Method POST `
        -Body '{"time_range":"daily","limit":5,"disable_ai":true}' `
        -ContentType "application/json" `
        -TimeoutSec 30

    Write-Host "Success! Status Code: $($response.StatusCode)"
    Write-Host "Content: $($response.Content)"
} catch {
    Write-Host "Error occurred:"
    Write-Host "Status Code: $($_.Exception.Response.StatusCode.value__)"
    Write-Host "Status Description: $($_.Exception.Response.StatusDescription)"

    # Try to read the response body
    $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
    $responseBody = $reader.ReadToEnd()
    Write-Host "Response Body: $responseBody"
}
