param(
    [string]$ApiBase = "http://127.0.0.1:3000",
    [string]$ComfyHost = "HOST_REMOTO",
    [string]$ComfyPort = "8188",
    [string]$Checkpoint = "sd_xl_base_1.0.safetensors",
    [int]$PollMaxAttempts = 90,
    [int]$PollSleepSeconds = 2
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$script:Results = @()
$script:RemoteBlocked = $false

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "=================================================="
    Write-Host $Title
    Write-Host "=================================================="
}

function Add-Result {
    param(
        [string]$Test,
        [string]$Status,
        [string]$Detail
    )
    $script:Results += [pscustomobject]@{
        test   = $Test
        status = $Status
        detail = $Detail
    }
}

function Get-TailscaleExe {
    $fromPath = Get-Command tailscale -ErrorAction SilentlyContinue
    if ($fromPath) {
        return $fromPath.Source
    }

    $commonPath = "C:\Program Files\Tailscale\tailscale.exe"
    if (Test-Path $commonPath) {
        return $commonPath
    }

    return $null
}

function Invoke-ApiJson {
    param(
        [Parameter(Mandatory = $true)][string]$Method,
        [Parameter(Mandatory = $true)][string]$Uri,
        [object]$Body = $null,
        [int]$TimeoutSec = 30
    )

    try {
        if ($null -ne $Body) {
            $json = $Body | ConvertTo-Json -Depth 60
            return Invoke-RestMethod -Uri $Uri -Method $Method -Body $json -ContentType "application/json" -TimeoutSec $TimeoutSec
        }
        return Invoke-RestMethod -Uri $Uri -Method $Method -TimeoutSec $TimeoutSec
    }
    catch {
        $statusCode = $null
        $responseBody = ""

        if ($_.Exception.Response) {
            try { $statusCode = [int]$_.Exception.Response.StatusCode } catch {}
            try {
                $stream = $_.Exception.Response.GetResponseStream()
                if ($stream) {
                    $reader = New-Object System.IO.StreamReader($stream)
                    $responseBody = $reader.ReadToEnd()
                    $reader.Close()
                }
            }
            catch {}
        }

        throw "HTTP $Method $Uri failed. status=$statusCode body=$responseBody error=$($_.Exception.Message)"
    }
}

function Test-ApiHealth {
    Write-Section "API local health"
    $health = Invoke-ApiJson -Method "GET" -Uri "$ApiBase/api/health" -TimeoutSec 20
    if (-not $health.ok) {
        throw "api/health devolvio ok=false"
    }
    Write-Host ($health | ConvertTo-Json -Depth 20)
    Add-Result -Test "API_HEALTH" -Status "PASS" -Detail "api/health ok=true"
}

function Preflight-Tailscale {
    Write-Section "1) Preflight Tailscale + entorno"

    $tailscaleExe = Get-TailscaleExe
    if (-not $tailscaleExe) {
        Add-Result -Test "TAILSCALE_CLI" -Status "FAIL" -Detail "tailscale.exe no encontrado"
        $script:RemoteBlocked = $true
    }
    else {
        try {
            & $tailscaleExe status | Out-Host
            Add-Result -Test "TAILSCALE_CLI" -Status "PASS" -Detail "tailscale status ejecutado"
        }
        catch {
            Add-Result -Test "TAILSCALE_CLI" -Status "FAIL" -Detail $_.Exception.Message
            $script:RemoteBlocked = $true
        }
    }

    if ([string]::IsNullOrWhiteSpace($ComfyHost) -or $ComfyHost -eq "HOST_REMOTO") {
        Add-Result -Test "COMFY_HOST" -Status "FAIL" -Detail "ComfyHost no definido"
        $script:RemoteBlocked = $true
    }
    else {
        Add-Result -Test "COMFY_HOST" -Status "PASS" -Detail "ComfyHost=$ComfyHost"
    }

    $env:COMFYUI_BASE_URL = "http://$ComfyHost`:$ComfyPort"
    $env:ENABLE_RENDER_CONTEXT_FLAGS = "true"
    Write-Host "COMFYUI_BASE_URL=$env:COMFYUI_BASE_URL"
    Write-Host "ENABLE_RENDER_CONTEXT_FLAGS=$env:ENABLE_RENDER_CONTEXT_FLAGS"

    if (-not $script:RemoteBlocked) {
        try {
            $probe = Invoke-WebRequest -UseBasicParsing -Uri "$env:COMFYUI_BASE_URL/system_stats" -Method Get -TimeoutSec 10
            if ($probe.StatusCode -ge 200 -and $probe.StatusCode -lt 300) {
                Add-Result -Test "COMFY_REMOTE_PROBE" -Status "PASS" -Detail "system_stats status=$($probe.StatusCode)"
            }
            else {
                Add-Result -Test "COMFY_REMOTE_PROBE" -Status "FAIL" -Detail "system_stats status=$($probe.StatusCode)"
                $script:RemoteBlocked = $true
            }
        }
        catch {
            Add-Result -Test "COMFY_REMOTE_PROBE" -Status "FAIL" -Detail $_.Exception.Message
            $script:RemoteBlocked = $true
        }
    }
}

function Check-Endpoints {
    Write-Section "2) Comprobacion endpoints"

    $config = Invoke-ApiJson -Method "GET" -Uri "$ApiBase/api/config" -TimeoutSec 20
    if (-not $config.ok -or -not $config.config) {
        throw "Contrato invalido en /api/config"
    }
    Write-Host ($config | ConvertTo-Json -Depth 30)
    Add-Result -Test "ENDPOINT_CONFIG" -Status "PASS" -Detail "/api/config responde"

    $ops = Invoke-ApiJson -Method "GET" -Uri "$ApiBase/api/ops/status" -TimeoutSec 20
    if (-not $ops.PSObject.Properties.Name.Contains("ok") -or -not $ops.comfyui) {
        throw "Contrato invalido en /api/ops/status"
    }
    Write-Host ($ops | ConvertTo-Json -Depth 30)
    Add-Result -Test "ENDPOINT_OPS_STATUS" -Status "PASS" -Detail "/api/ops/status responde"

    $jobs = Invoke-ApiJson -Method "GET" -Uri "$ApiBase/api/render/jobs?limit=5" -TimeoutSec 20
    if (-not $jobs.ok -or -not $jobs.PSObject.Properties.Name.Contains("jobs")) {
        throw "Contrato invalido en /api/render/jobs"
    }
    Write-Host ($jobs | ConvertTo-Json -Depth 30)
    Add-Result -Test "ENDPOINT_RENDER_JOBS_LIST" -Status "PASS" -Detail "/api/render/jobs responde"

    if ($config.config.comfyui_base_url -eq $env:COMFYUI_BASE_URL) {
        Add-Result -Test "CONFIG_COMFY_BASE_URL_ACTIVE" -Status "PASS" -Detail "api/config comfyui_base_url activo"
    }
    else {
        Add-Result -Test "CONFIG_COMFY_BASE_URL_ACTIVE" -Status "FAIL" -Detail "api/config comfyui_base_url=$($config.config.comfyui_base_url) env=$env:COMFYUI_BASE_URL"
    }
}

function Wait-RenderJob {
    param(
        [Parameter(Mandatory = $true)][string]$JobId,
        [int]$MaxAttempts = 90,
        [int]$SleepSeconds = 2
    )

    $terminal = @("succeeded", "failed", "timeout")
    $allowed = @("queued", "running", "succeeded", "failed", "timeout")

    for ($i = 0; $i -lt $MaxAttempts; $i++) {
        $jobResp = Invoke-ApiJson -Method "GET" -Uri "$ApiBase/api/render/jobs/$JobId" -TimeoutSec 20
        if (-not $jobResp.ok -or -not $jobResp.job) {
            throw "Contrato invalido en GET /api/render/jobs/$JobId"
        }

        $status = [string]$jobResp.job.status
        Write-Host "poll=$i job_id=$JobId status=$status"

        if ($allowed -notcontains $status) {
            throw "Estado desconocido: $status"
        }

        if ($terminal -contains $status) {
            return $jobResp
        }

        Start-Sleep -Seconds $SleepSeconds
    }

    throw "Timeout esperando estado terminal para job_id=$JobId"
}

function Has-RequestPayloadProperty {
    param(
        [Parameter(Mandatory = $true)]$Payload,
        [Parameter(Mandatory = $true)][string]$PropertyName
    )

    if ($null -eq $Payload) {
        return $false
    }

    if ($Payload -is [System.Collections.IDictionary]) {
        return $Payload.Contains($PropertyName)
    }

    $names = @($Payload.PSObject.Properties.Name)
    return ($names -contains $PropertyName)
}

function Get-RenderContextFromPayload {
    param([Parameter(Mandatory = $true)]$Payload)

    if (-not (Has-RequestPayloadProperty -Payload $Payload -PropertyName "metadata")) {
        return $null
    }

    $metadata = $null
    if ($Payload -is [System.Collections.IDictionary]) {
        $metadata = $Payload["metadata"]
    }
    else {
        $metadata = $Payload.metadata
    }

    if ($null -eq $metadata) {
        return $null
    }

    if ($metadata -is [System.Collections.IDictionary]) {
        if ($metadata.Contains("render_context")) {
            return $metadata["render_context"]
        }
        return $null
    }

    $metadataNames = @($metadata.PSObject.Properties.Name)
    if ($metadataNames -contains "render_context") {
        return $metadata.render_context
    }

    return $null
}

function Assert-FinalContract {
    param(
        [Parameter(Mandatory = $true)]$FinalJob,
        [Parameter(Mandatory = $true)][string]$Label
    )

    $status = [string]$FinalJob.job.status
    if ($status -eq "succeeded") {
        if (-not $FinalJob.job.result) {
            throw "${Label}: succeeded sin result"
        }
        return "succeeded"
    }

    if ($status -in @("failed", "timeout")) {
        if (-not $FinalJob.job.error) {
            throw "${Label}: $status sin error"
        }
        if ([string]::IsNullOrWhiteSpace([string]$FinalJob.job.error.code)) {
            throw "${Label}: $status sin error.code"
        }
        if ([string]::IsNullOrWhiteSpace([string]$FinalJob.job.error.message)) {
            throw "${Label}: $status sin error.message"
        }
        return "$status/$($FinalJob.job.error.code)"
    }

    throw "${Label}: estado final inesperado=$status"
}

function New-BasePrompt {
    param(
        [string]$CheckpointName,
        [string]$PositiveText,
        [string]$NegativeText,
        [int]$Seed
    )

    return [ordered]@{
        "3" = @{
            class_type = "KSampler"
            inputs = @{
                model        = @("4", 0)
                positive     = @("6", 0)
                negative     = @("7", 0)
                latent_image = @("5", 0)
                seed         = $Seed
                steps        = 20
                cfg          = 7
                sampler_name = "euler"
                scheduler    = "normal"
                denoise      = 1
            }
        }
        "4" = @{
            class_type = "CheckpointLoaderSimple"
            inputs = @{
                ckpt_name = $CheckpointName
            }
        }
        "5" = @{
            class_type = "EmptyLatentImage"
            inputs = @{
                width      = 1024
                height     = 1024
                batch_size = 1
            }
        }
        "6" = @{
            class_type = "CLIPTextEncode"
            inputs = @{
                text = $PositiveText
                clip = @("4", 1)
            }
        }
        "7" = @{
            class_type = "CLIPTextEncode"
            inputs = @{
                text = $NegativeText
                clip = @("4", 1)
            }
        }
        "8" = @{
            class_type = "VAEDecode"
            inputs = @{
                samples = @("3", 0)
                vae     = @("4", 2)
            }
        }
        "9" = @{
            class_type = "SaveImage"
            inputs = @{
                filename_prefix = "cai_smoke"
                images          = @("8", 0)
            }
        }
    }
}

function Submit-RenderJob {
    param(
        [Parameter(Mandatory = $true)][hashtable]$Body,
        [Parameter(Mandatory = $true)][string]$Label
    )

    Write-Section "POST $Label"
    $response = Invoke-ApiJson -Method "POST" -Uri "$ApiBase/api/render/jobs" -Body $Body -TimeoutSec 30
    Write-Host ($response | ConvertTo-Json -Depth 40)

    if (-not $response.ok -or -not $response.job) {
        throw "${Label}: contrato invalido en create"
    }
    if ([string]::IsNullOrWhiteSpace([string]$response.job.job_id)) {
        throw "${Label}: falta job.job_id"
    }

    return $response
}

function Run-TestA {
    $body = @{
        request_payload = @{
            prompt = (New-BasePrompt -CheckpointName $Checkpoint -PositiveText "masterpiece cinematic still" -NegativeText "lowres, blurry, bad anatomy" -Seed 12345)
        }
    }

    $created = Submit-RenderJob -Body $body -Label "A base"
    if (-not (Has-RequestPayloadProperty -Payload $created.job.request_payload -PropertyName "prompt")) {
        throw "A: request_payload.prompt ausente"
    }

    $final = Wait-RenderJob -JobId $created.job.job_id -MaxAttempts $PollMaxAttempts -SleepSeconds $PollSleepSeconds
    $contract = Assert-FinalContract -FinalJob $final -Label "A"

    Add-Result -Test "A_BASE" -Status "PASS" -Detail "job_id=$($created.job.job_id) final=$contract"
}

function Run-TestB {
    $body = @{
        render_context = $null
        request_payload = @{
            prompt = (New-BasePrompt -CheckpointName $Checkpoint -PositiveText "cinematic still" -NegativeText "lowres, blurry" -Seed 12346)
        }
    }

    $created = Submit-RenderJob -Body $body -Label "B render_context null"
    $rc = Get-RenderContextFromPayload -Payload $created.job.request_payload
    if ($null -ne $rc) {
        throw "B: metadata.render_context deberia ser null/ausente"
    }

    $final = Wait-RenderJob -JobId $created.job.job_id -MaxAttempts $PollMaxAttempts -SleepSeconds $PollSleepSeconds
    $contract = Assert-FinalContract -FinalJob $final -Label "B"

    Add-Result -Test "B_NULL_CONTEXT" -Status "PASS" -Detail "job_id=$($created.job.job_id) final=$contract"
}

function Run-TestC {
    $body = @{
        render_context = @{
            character_id  = "char_001"
            use_ipadapter = $true
        }
        request_payload = @{
            prompt = (New-BasePrompt -CheckpointName $Checkpoint -PositiveText "cinematic portrait" -NegativeText "lowres, blurry" -Seed 12347)
        }
    }

    $created = Submit-RenderJob -Body $body -Label "C character_id + use_ipadapter"
    $final = Wait-RenderJob -JobId $created.job.job_id -MaxAttempts $PollMaxAttempts -SleepSeconds $PollSleepSeconds
    $contract = Assert-FinalContract -FinalJob $final -Label "C"

    $rc = Get-RenderContextFromPayload -Payload $created.job.request_payload
    if ($null -eq $rc) {
        throw "C: metadata.render_context ausente (flag no activa en proceso API o no aplicada). final=$contract"
    }
    if ([string]$rc.character_id -ne "char_001") {
        throw "C: metadata.render_context.character_id invalido"
    }
    if ($rc.use_ipadapter -ne $true) {
        throw "C: metadata.render_context.use_ipadapter invalido"
    }

    Add-Result -Test "C_CHARACTER_IPADAPTER" -Status "PASS" -Detail "job_id=$($created.job.job_id) final=$contract"
}

function Run-TestD {
    $body = @{
        render_context = @{
            character_id  = "INVALID_ID"
            use_ipadapter = $true
        }
        request_payload = @{
            prompt = (New-BasePrompt -CheckpointName $Checkpoint -PositiveText "cinematic portrait" -NegativeText "lowres, blurry" -Seed 12348)
        }
    }

    $created = Submit-RenderJob -Body $body -Label "D character_id invalido"
    $final = Wait-RenderJob -JobId $created.job.job_id -MaxAttempts $PollMaxAttempts -SleepSeconds $PollSleepSeconds
    $contract = Assert-FinalContract -FinalJob $final -Label "D"

    $rc = Get-RenderContextFromPayload -Payload $created.job.request_payload
    if ($null -eq $rc) {
        throw "D: metadata.render_context ausente (flag no activa en proceso API o no aplicada). final=$contract"
    }
    if ([string]$rc.character_id -ne "INVALID_ID") {
        throw "D: metadata.render_context.character_id invalido"
    }

    Add-Result -Test "D_INVALID_CHARACTER" -Status "PASS" -Detail "job_id=$($created.job.job_id) final=$contract"
}

function Safe-Run {
    param(
        [string]$Name,
        [scriptblock]$Block
    )
    try {
        & $Block
    }
    catch {
        Add-Result -Test $Name -Status "FAIL" -Detail $_.Exception.Message
    }
}

try {
    Preflight-Tailscale
    Test-ApiHealth
    Check-Endpoints

    Safe-Run -Name "A_BASE" -Block { Run-TestA }
    Safe-Run -Name "B_NULL_CONTEXT" -Block { Run-TestB }
    Safe-Run -Name "C_CHARACTER_IPADAPTER" -Block { Run-TestC }
    Safe-Run -Name "D_INVALID_CHARACTER" -Block { Run-TestD }
}
catch {
    Add-Result -Test "UNHANDLED_ERROR" -Status "FAIL" -Detail $_.Exception.Message
}

Write-Section "RESUMEN FINAL"
$script:Results | Format-Table -AutoSize

$failCount = @($script:Results | Where-Object { $_.status -eq "FAIL" }).Count
if ($script:RemoteBlocked) {
    Write-Host ""
    Write-Host "BLOQUEADO POR REMOTO: SI"
}
else {
    Write-Host ""
    Write-Host "BLOQUEADO POR REMOTO: NO"
}

if ($failCount -gt 0) {
    exit 1
}

exit 0
