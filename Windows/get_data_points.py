# %%
#%pip install requests
import requests
import time

# %%
def getContent():
    url = "http://192.168.11.140/stats.json"
    while True:
        try:
            resp = requests.get(url)
        except Exception as e:
            print(e)
        if resp.status_code == 200:
            #print(resp.content) 
            return resp.content
        time.sleep(20)
#print(resp.status_code)
#print((resp.content))

# %%
def serializor():
    import json
    e = json.loads(getContent())
    time = e.get("EpochDate")
    hostname = e.get("Hostname")
    mem = e.get("MemUsage")
    disk = e.get("DiskUsage")
    cpu = e.get("CPUUsage")
    stats = [time, hostname, mem, disk, cpu]
    return stats

# %%
def gen_cpu_data_point():
    tags = {}
    tags["Hostname"] = serializor()[1]
    fields = {}
    fields["cpu_percent"] = serializor()[-1]

    cpu_stats = {
        "measurement" : "Cpu_stats",
        "tags": tags,
        "fields": fields,
        "time" : serializor()[0]
    }
    return cpu_stats


# %%
def gen_mem_data_point():
    tags = {}
    tags["Hostname"] = serializor()[1]
    fields = {}
    fields["used_ram"] = serializor()[2]

    mem_stats = {
        "measurement" : "mem_stats",
        "tags": tags,
        "fields": fields,
        "time": serializor()[0]
    }
    return mem_stats


# %%
def gen_disk_data_point():
    tags = {}
    tags["Hostname"] = serializor()[1]
    fields = {}
    
    partitions = list(serializor()[-2].keys())
    partitions_usage = list(serializor()[-2].values())

    for a in range(len(partitions)):
        fields[partitions[a] + " usage"] = partitions_usage[a]


    disk_stats = {
      "measurement" : "disk_stats",
      "tags": tags,
      "fields": fields,
      "time": serializor()[0]
    }

    return disk_stats




