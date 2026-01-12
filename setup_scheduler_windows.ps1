# Windows Task Scheduler Setup Script for Daily News Delivery
# Run this script as Administrator in PowerShell

param(
    [string]$ProjectPath = $PSScriptRoot,
    [string]$Time = "05:00"
)

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Setting up Daily News Delivery Scheduler (Windows)" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Create logs directory
$LogsPath = Join-Path $ProjectPath "logs"
if (-not (Test-Path $LogsPath)) {
    New-Item -ItemType Directory -Path $LogsPath | Out-Null
    Write-Host "[OK] Created logs directory" -ForegroundColor Green
} else {
    Write-Host "[OK] Logs directory already exists" -ForegroundColor Green
}

# Task name
$TaskName = "KindleNewsDelivery"

# Check if task already exists
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($ExistingTask) {
    Write-Host "[INFO] Removing existing task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Script to run
$ScriptPath = Join-Path $ProjectPath "run_daily.bat"

# Create the action (what to run)
$Action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$ScriptPath`" > `"$LogsPath\daily_run.log`" 2>&1"

# Create triggers for Monday-Friday at 5:00 AM
$Triggers = @()

# Monday (1) through Friday (5)
1..5 | ForEach-Object {
    $Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek @{
        1 = "Monday"
        2 = "Tuesday"
        3 = "Wednesday"
        4 = "Thursday"
        5 = "Friday"
    }[$_] -At $Time
    $Triggers += $Trigger
}

# Use first trigger for registration, then add others
$PrimaryTrigger = $Triggers[0]

# Create settings
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2)

# Register the task (run whether user is logged on or not)
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType S4U -RunLevel Limited

Write-Host "[INFO] Registering scheduled task..." -ForegroundColor Yellow

try {
    # Register with primary trigger
    $Task = Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $Action `
        -Trigger $PrimaryTrigger `
        -Settings $Settings `
        -Principal $Principal `
        -Description "Automatically fetch NYT Business news and send to Kindle every weekday morning"

    # Add remaining triggers
    for ($i = 1; $i -lt $Triggers.Count; $i++) {
        $Task.Triggers += $Triggers[$i]
        $Task | Set-ScheduledTask | Out-Null
    }

    Write-Host "[OK] Successfully created scheduled task!" -ForegroundColor Green
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "Setup Complete!" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "The news delivery will run automatically:" -ForegroundColor White
    Write-Host "  - Monday-Friday at $Time" -ForegroundColor White
    Write-Host "  - Logs: $LogsPath" -ForegroundColor White
    Write-Host ""
    Write-Host "To check status:" -ForegroundColor Yellow
    Write-Host "  Get-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To run manually:" -ForegroundColor Yellow
    Write-Host "  Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To uninstall:" -ForegroundColor Yellow
    Write-Host "  .\uninstall_scheduler_windows.ps1" -ForegroundColor Cyan
    Write-Host ""

} catch {
    Write-Host "[ERROR] Failed to create scheduled task!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
