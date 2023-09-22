# %%
from influxdb_client import InfluxDBClient
from influxdb_client.client.exceptions import InfluxDBError
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.domain.write_precision import WritePrecision
import time
# import sys_stats
def check_influxdb_liveliness():
    try:
        with InfluxDBClient.from_config_file("creds.toml","r", encoding="utf-8") as client:
            ping_result = client.ping()
            # if ping_result == True:
            #     return True
            # else:
            #     return False
            return ping_result
    except Exception as e:
        return f"False2 {e}"
print(check_influxdb_liveliness() != True)
x=0
while 1:
    # check_influxdb_liveliness()
    x = x + 1
    if check_influxdb_liveliness() == True:
        import get_data_points

        #Works on linux, not windows
        import sys
        sys.exit(get_data_points.main())
    elif x == 5:
        exit()
    else:
        time.sleep(3)
        
    