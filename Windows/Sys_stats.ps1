$cpuCounter = Get-Counter '\Processor(_Total)\% Processor Time'
$cpuUsage = [math]::Round($cpuCounter.CounterSamples.CookedValue, 2)



$memoryInfo = Get-CimInstance -ClassName Win32_OperatingSystem
$totalMemory = [math]::Round($memoryInfo.TotalVisibleMemorySize / 1MB, 2)
$freeMemory = [math]::Round($memoryInfo.FreePhysicalMemory / 1MB, 2)
$usedMemory_percentage = (($totalMemory - $freeMemory) / $totalMemory ) * 100


$diskInfo = Get-WmiObject Win32_LogicalDisk -Filter "DriveType=3"


#[System.Collections.Generic.List]$diskStats = @()
$diskStats = [Ordered]@{}


foreach ($disk in $diskInfo) {
    $driveLetter = $disk.DeviceId
    $totalSpace = $disk.Size
    $freeSpace = $disk.FreeSpace
    $usedSpace = $totalSpace - $freeSpace
    $UsedPercentage = [math]::Round(($usedSpace/$totalSpace ) * 100, 2)
    #$diskStats += $UsedPercentage
    $diskStats.Add($driveLetter, $UsedPercentage
    )
}

Write-Host "CPU Usage: $cpuUsage"
Write-Host "Memory Usage: $usedMemory_percentage"
Write-Host "Disk Usage: "  $diskStats