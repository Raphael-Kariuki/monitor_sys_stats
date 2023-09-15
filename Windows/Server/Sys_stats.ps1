
function Get-CpuStats{
    $cpuCounter = Get-Counter '\Processor(_Total)\% Processor Time'
    #$cpuUsage = [math]::Round($cpuCounter.CounterSamples.CookedValue, 2)
    $cpuUsage = $cpuCounter.CounterSamples.CookedValue

    #return @{"CpuUsage"=$cpuUsage}
    return $cpuUsage

}


function Get-MemStats{
    $memoryInfo = Get-CimInstance -ClassName Win32_OperatingSystem
    #$totalMemory = [math]::Round($memoryInfo.TotalVisibleMemorySize / 1MB, 2)
    $totalMemory = $memoryInfo.TotalVisibleMemorySize
    #$freeMemory = [math]::Round($memoryInfo.FreePhysicalMemory / 1MB, 2)
    $freeMemory = $memoryInfo.FreePhysicalMemory
    $usedMemory_percentage = (($totalMemory - $freeMemory) / $totalMemory ) * 100
    
    #return @{"MemUsage"=$usedMemory_percentage}
    return $usedMemory_percentage
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
        #$UsedPercentage = [math]::Round(($usedSpace/$totalSpace ) * 100, 2)
        $UsedPercentage = ($usedSpace/$totalSpace ) * 100
        #$diskStats += $UsedPercentage
        $diskStats.Add($driveLetter, $UsedPercentage)
    }
    return $diskStats
    
}

function Get-Hostname{
    $hostname = HOSTNAME.EXE
    #return @{"Hostname"=$hostname}
    return $hostname
}

function Get-EpochDate{
    $date = Get-Date -UFormat %s
    return $date
}


function Get-JsonStats{

    $sys_stats = [Ordered]@{}
    $hostname = Get-Hostname
    $disk = Get-DiskStats
    $mem = Get-MemStats
    $cpu = Get-CpuStats
    $date = Get-EpochDate

    #"Hostname"| Out-File -FilePath <path>
    #Add-Content -Path <path> -Value $hostname

    $sys_stats.Add("EpochDate",$date)
    $sys_stats.Add("Hostname",$hostname)
    $sys_stats.Add("MemUsage",$mem)
    $sys_stats.Add("DiskUsage",$disk)
    $sys_stats.Add("CPUUsage",$cpu)

    #Convert to json coz why not, #parsability is key
    $json = $sys_stats | ConvertTo-Json
    #Write-Output, Out-File, {}>, >>} -> Redirectors - All tend to add some characters at the start of the file content, so add the delete file 
    Add-Content -Path "C:\Users\test\Downloads\monitor_sys_stats\Windows\IIS\stats.json"  -Value $json
}



while (1 -eq 1) {
    Write-Host "Running after deletion"
    try {
        Remove-Item -Path <path>
    }
    catch {
        "" > <path>
    }
   
    Get-JsonStats
    Write-Host "Sleeping"
    Start-Sleep -Milliseconds 30000
    
}





