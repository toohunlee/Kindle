# Uninstall Windows Task Scheduler for Daily News Delivery

$TaskName = "KindleNewsDelivery"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Uninstalling Daily News Delivery Scheduler" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if task exists
$Task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if ($Task) {
    Write-Host "[INFO] Removing scheduled task..." -ForegroundColor Yellow

    try {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "[OK] Successfully removed scheduled task!" -ForegroundColor Green
        Write-Host ""
        Write-Host "The automatic news delivery has been disabled." -ForegroundColor White
        Write-Host "You can still run manually with: python main.py" -ForegroundColor White
    } catch {
        Write-Host "[ERROR] Failed to remove task!" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[INFO] Scheduled task not found. Nothing to uninstall." -ForegroundColor Yellow
}
