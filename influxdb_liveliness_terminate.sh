#Script is executed by the service launching the initial py script when the stop service command is executed

#Checks pid of package create by python py-installer
influxdb_liveliness_PID=`pidof influxdb_liveness | cut -f5 -d " "`

#Passed pid to kill command 
kill -15 $influxdb_liveliness_PID

#Clean exit
exit