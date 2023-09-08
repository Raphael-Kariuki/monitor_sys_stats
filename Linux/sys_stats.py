# %%
import os, re, subprocess, psutil, platform
from datetime import datetime, timezone, timedelta


# %%
# %pip install influxdb_client
from influxdb_client import InfluxDBClient
from influxdb_client.client.exceptions import InfluxDBError
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.domain.write_precision import WritePrecision
import time

# %%

def get_cpu_stats():
    cpu_statistics = {}

    physical_cpu_count = psutil.cpu_count(logical=False)
    logical_cpu_count = psutil.cpu_count(logical=True)
    cpufreq = psutil.cpu_freq()
    cpupercent = psutil.cpu_percent()
    cpu_statistics['physical_cpu_count'] = physical_cpu_count
    cpu_statistics['logical_cpu_count'] = logical_cpu_count
    cpu_statistics['cpufreq'] = cpufreq.current
    cpu_statistics['cpupercent'] = cpupercent


    cpu_load = [x for x in os.getloadavg()]
    cpu_statistics['cpu_load_1'] = cpu_load[0]
    cpu_statistics['cpu_load_5'] = cpu_load[-2]
    cpu_statistics['cpu_load_15'] = cpu_load[-1]

    return cpu_statistics

# %%
# def get_size(bytes, suffix="B"):
#     """
#     Scale bytes to its proper format
#     e.g:
#         1253656 => '1.20MB'
#         1253656678 => '1.17GB'
#     """
#     factor = 1024
#     for unit in ["", "K", "M", "G", "T", "P"]:
#         if bytes < factor:
#             return f"{bytes:.2f}{unit}{suffix}"
#         bytes /= factor

# %%
def get_mem_stats():

    mem_statisctics = {}
    svmem = psutil.virtual_memory()

    # mem_statisctics["total_ram"] = get_size(svmem.total)
    # mem_statisctics["available_ram"] = get_size(svmem.available)
    mem_statisctics["used_ram"] = (((svmem.used) / (svmem.total)) * 100)
    # svmem
    return mem_statisctics

# %%
def get_disk_stats():

    disk_statistics = {}

    partitions = psutil.disk_partitions()

    for partition in partitions:
        disk_statistics[f"Mountpoint {partition.device}"] = partition.mountpoint
        # disk_statistics["fstype"] = partition.fstype

        try:
            partition_usage = psutil.disk_usage(disk_statistics[f"Mountpoint {partition.device}"])
        except Exception as e:
            print(e)
        finally:
            disk_statistics[f"{partition.device} Usage "] = partition_usage.percent
    return disk_statistics
# partitions

# %%
# print(get_cpu_stats())
# print(get_disk_stats())
# print(get_mem_stats())

# %%
def get_hostname():
    uname = platform.uname()
    return uname.node


# %% [markdown]
# measurement, tagset fieldset timestamp
# "measurement" : "cpu_stats",
# "tagset" : "hostname",
# "fieldset" : json.dumps(get_cpu_stats),
# "time" :  int(datetime.timestamp(datetime.now(timezone(+timedelta(hours=3)))))
# 
# 
#             #prepare points
#             tags = {}
#             tags["Host"]= ip
# 
#             fields = {}
#             fields["Latency"] = ping_ip(ip)
# 
#             unixtime =  int(datetime.timestamp(datetime.now(timezone(+timedelta(hours=3)))))
#             
#             ping_record = {
#                 "measurement": "PingTime",
#                 "tags": tags,
#                 "fields": fields,
#                 "time": unixtime
#             }
# 
# 

# %%
def gen_cpu_data_point():
    tags = {}
    tags["Hostname"] = get_hostname()

    fields = get_cpu_stats()
    unixtime =  int(datetime.timestamp(datetime.now(timezone(+timedelta(hours=3)))))

    cpu_stats = {
                "measurement": "cpu_stats",
                "tags": tags,
                "fields": fields,
                "time": unixtime
            }
    return cpu_stats
    

# %%
def gen_mem_data_point():
    tags = {}
    tags["Hostname"] = get_hostname()

    fields = get_mem_stats()
    unixtime =  int(datetime.timestamp(datetime.now(timezone(+timedelta(hours=3)))))

    mem_stats = {
                "measurement": "mem_stats",
                "tags": tags,
                "fields": fields,
                "time": unixtime
            }
    return mem_stats

# %%
def gen_disk_data_point():
    tags = {}
    tags["Hostname"] = get_hostname()

    fields = get_disk_stats()
    unixtime =  int(datetime.timestamp(datetime.now(timezone(+timedelta(hours=3)))))

    disk_stats = {
                "measurement": "disk_stats",
                "tags": tags,
                "fields": fields,
                "time": unixtime
            }
    return disk_stats

# %%
# gen_disk_data_point()

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


