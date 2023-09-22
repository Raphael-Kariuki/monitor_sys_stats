# %%
#%pip install requests
import requests
import time

# %%
# %pip install influxdb_client
from influxdb_client import InfluxDBClient
from influxdb_client.client.exceptions import InfluxDBError
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.domain.write_precision import WritePrecision
import time

# %%
def getContent():
    url = "http://<url>/stats.json"
    # while True:
    try:
        resp = requests.get(url)
    except Exception as e:
        print(e)
    if resp.status_code == 200:
        #print(resp.content) 
        return resp.content
        # time.sleep(20)
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



# %%
def write_cpuStats_to_influxdb(pause,bucket_name,org):
    #flag set so that while the function goes in a loop. it doesn't endup making GET requests over and over again. Should be done once
    #Will be set to Tue after the 1st successfull bucket creation and posting OR posting
    bucket_present = False

    while 1:
        with InfluxDBClient.from_config_file("creds.toml","r", encoding="utf-8") as client:
            with client.write_api(write_options=SYNCHRONOUS) as write_api:
                try:
                    #Create the ping records dictionary to be postedgen_mem_data_point()
                    # gen_ping_records()
                    #check whether GET has been run atleast once
                    if not bucket_present:
                        # Create a BucketsApi instance
                        buckets_api = client.buckets_api()
                    
                        # Check existence of bucket
                        # bucket_name = "pingspeed"
                        bucket = buckets_api.find_bucket_by_name(bucket_name)

                        #if target bucket doesn't exist, create one.
                        if bucket == None:
                            buckets_api.create_bucket(bucket_name=bucket_name
                            , org=org
                            ,retention_rules=[{
                                "type": "expire",
                                "everySeconds": 604800,
                                "shardGroupDurationSeconds": 86400
                            }]
                            )
                            
                            #The write to the bucket
                            write_api.write(bucket=bucket_name, record=gen_cpu_data_point(), write_precision=WritePrecision.S)
                            print(f"Successfully wrote {len(gen_cpu_data_point())} metrics")

                            #Finally set as True so that GET request won't be run again
                            bucket_present = True
                        else:
                            #If bucket exists, just POST
                            write_api.write(bucket=bucket_name, record=gen_cpu_data_point(), write_precision=WritePrecision.S)
                            print(f"Successfully wrote {len(gen_cpu_data_point())} metrics")
                            bucket_present = True    
                    else:
                        #If bucket present coz func to check and create was already run atmost once
                        write_api.write(bucket=bucket_name, record=gen_cpu_data_point(), write_precision=WritePrecision.S)
                        print(f"Successfully wrote {len(gen_cpu_data_point())} metrics")
                        bucket_present = True

                    #Close the API
                    write_api.close()
                    #Set timer to sleep before loop
                    time.sleep(pause)
                except InfluxDBError as e:
                    print(e)




# %%

def write_diskStats_to_influxdb(pause,bucket_name,org):
    #flag set so that while the function goes in a loop. it doesn't endup making GET requests over and over again. Should be done once
    #Will be set to Tue after the 1st successfull bucket creation and posting OR posting
    bucket_present = False

    while 1:
        with InfluxDBClient.from_config_file("creds.toml","r", encoding="utf-8") as client:
            with client.write_api(write_options=SYNCHRONOUS) as write_api:
                try:
                    #Create the ping records dictionary to be posted
                    # gen_ping_records()
                    #check whether GET has been run atleast once
                    if not bucket_present:
                        # Create a BucketsApi instance
                        buckets_api = client.buckets_api()
                    
                        # Check existence of bucket
                        # bucket_name = "pingspeed"
                        bucket = buckets_api.find_bucket_by_name(bucket_name)

                        #if target bucket doesn't exist, create one.
                        if bucket == None:
                            buckets_api.create_bucket(bucket_name=bucket_name
                            , org=org
                            ,retention_rules=[{
                                "type": "expire",
                                "everySeconds": 604800,
                                "shardGroupDurationSeconds": 86400
                            }]
                            )
                            
                            #The write to the bucket
                            write_api.write(bucket=bucket_name, record=gen_disk_data_point(), write_precision=WritePrecision.S)
                            print(f"Successfully wrote {len(gen_disk_data_point())} metrics")

                            #Finally set as True so that GET request won't be run again
                            bucket_present = True
                        else:
                            #If bucket exists, just POST
                            write_api.write(bucket=bucket_name, record=gen_disk_data_point(), write_precision=WritePrecision.S)
                            print(f"Successfully wrote {len(gen_disk_data_point())} metrics")
                            bucket_present = True    
                    else:
                        #If bucket present coz func to check and create was already run atmost once
                        write_api.write(bucket=bucket_name, record=gen_disk_data_point(), write_precision=WritePrecision.S)
                        print(f"Successfully wrote {len(gen_disk_data_point())} metrics")
                        bucket_present = True

                    #Close the API
                    write_api.close()
                    #Set timer to sleep before loop
                    time.sleep(pause)
                except InfluxDBError as e:
                    print(e)

# %%
def write_memStats_to_influxdb(pause,bucket_name,org):
    #flag set so that while the function goes in a loop. it doesn't endup making GET requests over and over again. Should be done once
    #Will be set to Tue after the 1st successfull bucket creation and posting OR posting
    bucket_present = False

    while 1:
        with InfluxDBClient.from_config_file("creds.toml","r", encoding="utf-8") as client:
            with client.write_api(write_options=SYNCHRONOUS) as write_api:
                try:
                    #Create the ping records dictionary to be posted
                    # gen_ping_records()
                    #check whether GET has been run atleast once
                    if not bucket_present:
                        # Create a BucketsApi instance
                        buckets_api = client.buckets_api()
                    
                        # Check existence of bucket
                        # bucket_name = "pingspeed"
                        bucket = buckets_api.find_bucket_by_name(bucket_name)

                        #if target bucket doesn't exist, create one.
                        if bucket == None:
                            buckets_api.create_bucket(bucket_name=bucket_name
                            , org=org
                            ,retention_rules=[{
                                "type": "expire",
                                "everySeconds": 604800,
                                "shardGroupDurationSeconds": 86400
                            }]
                            )
                            
                            #The write to the bucket
                            write_api.write(bucket=bucket_name, record=gen_mem_data_point(), write_precision=WritePrecision.S)
                            print(f"Successfully wrote {len(gen_mem_data_point())} metrics")

                            #Finally set as True so that GET request won't be run again
                            bucket_present = True
                        else:
                            #If bucket exists, just POST
                            write_api.write(bucket=bucket_name, record=gen_mem_data_point(), write_precision=WritePrecision.S)
                            print(f"Successfully wrote {len(gen_mem_data_point())} metrics")
                            bucket_present = True    
                    else:
                        #If bucket present coz func to check and create was already run atmost once
                        write_api.write(bucket=bucket_name, record=gen_mem_data_point(), write_precision=WritePrecision.S)
                        print(f"Successfully wrote {len(gen_mem_data_point())} metrics")
                        bucket_present = True

                    #Close the API
                    write_api.close()
                    #Set timer to sleep before loop
                    time.sleep(pause)
                except InfluxDBError as e:
                    print(e)


# %%
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


