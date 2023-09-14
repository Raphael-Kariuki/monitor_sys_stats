
function Get-CpuStats{
    $cpuCounter = Get-Counter '\Processor(_Total)\% Processor Time'
    $cpuUsage = [math]::Round($cpuCounter.CounterSamples.CookedValue, 2)

    return @{"CpuUsage"=$cpuUsage}

}


function Get-MemStats{
    $memoryInfo = Get-CimInstance -ClassName Win32_OperatingSystem
    $totalMemory = [math]::Round($memoryInfo.TotalVisibleMemorySize / 1MB, 2)
    $freeMemory = [math]::Round($memoryInfo.FreePhysicalMemory / 1MB, 2)
    $usedMemory_percentage = (($totalMemory - $freeMemory) / $totalMemory ) * 100
    
    return @{"MemUsage"=$usedMemory_percentage}
}

function Get-DiskStats {
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
        $diskStats.Add($driveLetter, $UsedPercentage)
    }
    return $diskStats
    
}

function Get-Hostname{
    $hostname = HOSTNAME.EXE
    return @{"Hostname"=$hostname}
}


Write-Output "[" > stats.json
Get-Hostname | ConvertTo-Json >> stats.json
Write-Output "," >> stats.json
Get-CpuStats| ConvertTo-Json >> stats.json
Write-Output "," >> stats.json
Get-DiskStats| ConvertTo-Json >> stats.json
Write-Output "," >> stats.json
Get-MemStats| ConvertTo-Json >> stats.json
Write-Output "]" >> stats.json



