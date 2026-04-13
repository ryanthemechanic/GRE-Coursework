param(
    [int]$Port = 8765,
    [string]$Token,
    [string]$RunnerScript = "C:\Users\ryanp\AxureBridge\run-pad-action.ps1"
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Token)) {
    throw "Token is required. Start with: .\\axure-bridge.ps1 -Token <your-secret>"
}

if (-not (Test-Path -LiteralPath $RunnerScript)) {
    throw "Runner script not found: $RunnerScript"
}

$allowedActions = @(
    "open_project",
    "add_page",
    "add_text",
    "add_button",
    "export_html",
    "save_project"
)

$listener = [System.Net.HttpListener]::new()
$listener.Prefixes.Add("http://127.0.0.1:$Port/")
$listener.Start()
Write-Host "Axure bridge listening on http://127.0.0.1:$Port/"

try {
    while ($listener.IsListening) {
        $context = $listener.GetContext()
        $request = $context.Request
        $response = $context.Response

        try {
            if ($request.HttpMethod -ne "POST") {
                throw "Only POST supported"
            }

            $reader = New-Object System.IO.StreamReader($request.InputStream, $request.ContentEncoding)
            $body = $reader.ReadToEnd()
            $reader.Dispose()

            if ([string]::IsNullOrWhiteSpace($body)) {
                throw "Request body is empty"
            }

            $cmd = $body | ConvertFrom-Json

            if ($cmd.token -ne $Token) {
                $unauth = @{ ok = $false; message = "Unauthorized"; errorCode = "UNAUTHORIZED" } | ConvertTo-Json
                $bytes = [System.Text.Encoding]::UTF8.GetBytes($unauth)
                $response.StatusCode = 401
                $response.ContentType = "application/json"
                $response.OutputStream.Write($bytes, 0, $bytes.Length)
                $response.OutputStream.Close()
                continue
            }

            if ($allowedActions -notcontains [string]$cmd.action) {
                throw "Action not allowed"
            }

            $payloadJson = if ($null -eq $cmd.payload) { "{}" } else { ($cmd.payload | ConvertTo-Json -Depth 20 -Compress) }

            $runnerOutput = & powershell -NoProfile -ExecutionPolicy Bypass -File $RunnerScript -Action ([string]$cmd.action) -PayloadJson $payloadJson -Token $Token 2>&1
            $runnerText = ($runnerOutput | Out-String).Trim()

            $resultObj = $null
            try {
                $resultObj = $runnerText | ConvertFrom-Json
            }
            catch {
                $resultObj = @{ ok = $false; action = [string]$cmd.action; message = "Runner output was not valid JSON"; details = @{ rawOutput = $runnerText } }
            }

            $resultJson = $resultObj | ConvertTo-Json -Depth 20
            $bytes = [System.Text.Encoding]::UTF8.GetBytes($resultJson)
            $response.StatusCode = if ($resultObj.ok) { 200 } else { 500 }
            $response.ContentType = "application/json"
            $response.OutputStream.Write($bytes, 0, $bytes.Length)
            $response.OutputStream.Close()
        }
        catch {
            $err = @{ ok = $false; message = $_.Exception.Message; errorCode = "REQUEST_FAILED" } | ConvertTo-Json
            $bytes = [System.Text.Encoding]::UTF8.GetBytes($err)
            $response.StatusCode = 400
            $response.ContentType = "application/json"
            $response.OutputStream.Write($bytes, 0, $bytes.Length)
            $response.OutputStream.Close()
        }
    }
}
finally {
    if ($listener) {
        $listener.Stop()
        $listener.Close()
    }
}
