# Monitor system statistics

There are tools to monitor system statistics, however, what are their insides. 
Purpose is to read sys stats. Fullstop, no funny business.

Implementing python and influxdb with grafana for dashboards, provides simple visuals.

![Grafana dashboard displaying system stats](./Imgs/Grafana.png)


> **HINT** The final execution of writes to db happens in loops. Three different loops. 
    The way to execute three loops synchronously is as processes


```
from multiprocessing import Process

bucket_name=""
org=""

def loop_a():
    write_cpuStats_to_influxdb(30,bucket_name,org)

def loop_b():
    write_memStats_to_influxdb(30,bucket_name,org)
def loop_c():
    write_diskStats_to_influxdb(1200,bucket_name,org)

def main():
    Process(target=loop_a).start()
    Process(target=loop_b).start()
    Process(target=loop_c).start()

```
> **HINT** Python implementation on windows varies from on Linux
