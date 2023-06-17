# 树莓派数据与控制

import os
# Return CPU temperature as a character string                                     

def getCPUtemperature():
    res =os.popen('vcgencmd measure_temp').readline()
    return(res.replace("temp=","").replace("'C\n",""))
 
# Return RAM information (unit=kb) in a list                                      
# Index 0: total RAM                                                              
# Index 1: used RAM                                                                
# Index 2: free RAM                                                                
def getRAMinfo():
    p =os.popen('free')
    i =0
    while 1:
        i =i +1
        line =p.readline()
        if i==2:
            return(line.split()[1:4])
 
# Return % of CPU used by user as a character string                               
def getCPUuse():
    data = os.popen("top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip()
    return(data)
 
# Return information about disk space as a list (unit included)                    
# Index 0: total disk space                                                        
# Index 1: used disk space                                                        
# Index 2: remaining disk space                                                    
# Index 3: percentage of disk used                                                 
def getDiskSpace():
    p =os.popen("df -h /")
    i =0
    while True:
        i =i +1
        line =p.readline()
        if i==2:
            return(line.split()[1:5])
def  powerLed(swatch):
    led = open('/sys/class/leds/led1/brightness', 'w', 1)
    led.write(str(swatch))
    led.close()

# LED灯状态检测
def getLed():
	led = open('/sys/class/leds/led1/brightness', 'r', 1)
	state=led.read()
	led.close()
	return state
    
if __name__ == "__main__":
 
    # CPU informatiom
    CPU_temp =getCPUtemperature()
    CPU_usage =getCPUuse()
    print(CPU_usage)
    # RAM information
    # Output is in kb, here I convert it in Mb for readability
    RAM_stats =getRAMinfo()

    RAM_total = round(int(RAM_stats[0]) /1000,1)
    RAM_used = round(int(RAM_stats[1]) /1000,1)
    RAM_free = round(int(RAM_stats[2]) /1000,1)
    print(RAM_total,RAM_used,RAM_free)
    # Disk information
    DISK_stats =getDiskSpace()

    DISK_total = DISK_stats[0][:-1]
    DISK_used = DISK_stats[1][:-1]
    DISK_perc = DISK_stats[3][:-1]
    print(DISK_total,DISK_used,DISK_perc)