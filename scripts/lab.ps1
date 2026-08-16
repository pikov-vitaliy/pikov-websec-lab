<#
.SYNOPSIS
Starts one local, disposable Pikov WebSec Lab instance for a learner pair.

.EXAMPLE
.\scripts\lab.ps1 -Action start -Pair pair-01 -Mode vulnerable -Port 8080
.\scripts\lab.ps1 -Action stop  -Pair pair-01 -Mode vulnerable -Port 8080
#>
[CmdletBinding()]
param(
    [ValidateSet("start", "stop", "status", "logs", "preflight")]
    [string]$Action = "start",

    [ValidateSet("vulnerable", "hardened")]
    [string]$Mode = "vulnerable",

    [ValidatePattern("^[a-z0-9][a-z0-9-]{0,30}$")]
    [string]$Pair = "pair-01",

    [ValidateRange(1024, 65535)]
    [int]$Port = 8080
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repositoryRoot = Split-Path -Parent $PSScriptRoot
$projectName = "pikov-lab-$Pair-$Mode"
$composeInvocation = @("compose", "-p", $projectName, "-f", "docker-compose.yml")
$labHost = "127.0.0.1"
$labUrl = "http://${labHost}:$Port"

function Invoke-DockerCompose {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$ComposeArguments)

    & docker @composeInvocation @ComposeArguments
    if ($LASTEXITCODE -ne 0) {
        throw "Docker Compose exited with code $LASTEXITCODE."
    }
}

function Get-LabConfig {
    $rawConfig = & docker @composeInvocation config --format json
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to render Docker Compose configuration."
    }
    return $rawConfig | ConvertFrom-Json
}

function Invoke-Preflight {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        throw "Docker Desktop / Docker Engine is required."
    }

    $config = Get-LabConfig
    $service = $config.services.'svg-chat'
    $gateway = $config.services.gateway
    if ($gateway.ports[0].host_ip -ne $labHost) {
        throw "Refusing to start: the lab is not bound to $labHost."
    }
    if (-not $service.read_only -or -not $gateway.read_only -or $service.restart -ne "no" -or $gateway.restart -ne "no") {
        throw "Refusing to start: expected read-only, non-persistent lab settings."
    }
    if (-not $config.networks.'isolated-lab'.internal -or $service.networks.PSObject.Properties.Name -notcontains "isolated-lab") {
        throw "Refusing to start: the application network must be internal."
    }

    Write-Host "Preflight passed. $projectName will be reachable only at $labUrl"
}

$env:LAB_MODE = $Mode
$env:LAB_PORT = "$Port"

Push-Location $repositoryRoot
try {
    switch ($Action) {
        "preflight" { Invoke-Preflight }
        "start" {
            Invoke-Preflight
            Invoke-DockerCompose up --build --detach --wait
            Write-Host "Lab started: $labUrl"
            Write-Host "Open $labUrl in separate browser profiles for Attacker and Victim."
            Write-Host "If no INSTRUCTOR_TOKEN was supplied, retrieve the temporary token with:"
            Write-Host "  docker compose -p $projectName -f docker-compose.yml logs svg-chat"
        }
        "stop" {
            Invoke-DockerCompose down --remove-orphans
            Write-Host "Stopped scoped lab project $projectName. Its tmpfs uploads were discarded."
        }
        "status" { Invoke-DockerCompose ps }
        "logs" { Invoke-DockerCompose logs --tail 100 svg-chat }
    }
}
finally {
    Pop-Location
}
