from beacontools import BeaconScanner, EddystoneTLMFrame, EddystoneFilter, IBeaconFilter

import logging, os, sys, time
from datetime import datetime
import threading
import csv, codecs
import pymongo
from datetime import datetime, timedelta
import time, socket, fcntl, struct
import statistics

if (len(sys.argv))!=6:
    print ("Please input your beacon minor, obstacle, distance from anchor, transmission power, and direction after program name")
    print ("example of a valid input after program name: 123 NONE 4m -4dBm N")
    sys.exit("Usage: beacon_minor obstacle distance transmission_power direction")
beacon_minor = int(sys.argv[1])
obstacle = sys.argv[2]
distance = sys.argv[3]
transmission_power = sys.argv[4]
direction = sys.argv[5]
scenario = obstacle + " " +  distance + " " +  transmission_power + " " +  direction

delay = None
while delay is None:
    user_input = input("Enter the number of seconds to delay the start of scanning by: ")
    try:
        delay = int(user_input)
    except ValueError:
        print("that is not a valid number, please enter a number")


#rssi packets and info will be stored in this list
data_entries = []

mongo_db_uri = "mongodb://---.---.-.---/" # TODO: change this to database ip...
#from Ruiqi and Ruixuan's code
#---------------------------------Connection-------------------------------------
try:
    assert mongo_db_uri is not None
except:
    raise Exception("\n\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\
                    \nYou need to change the above 'mongo_db_uri' from None to the ip of the database.\
                    \nYou can use ifconfig command in linux to find the ip address...\
                    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
myclient = pymongo.MongoClient(mongo_db_uri, 
                                connectTimeoutMS=200,
                                serverSelectionTimeoutMS=200, 
                                socketTimeoutMS=200
                            )
mydb = myclient["BBCT"] # db names
rawcol = mydb["beaconConfig"] # collection names
avgcol = mydb["beaconConfigStats"]

def getHwAddr(ifname = 'wlan0'):
    '''
    #from Ruiqi and Ruixuan's code
    Return the MAC address of the device.
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', bytes(ifname, 'utf-8')[:15]))
    return ':'.join('%02x' % b for b in info[18:24])
rpi_mac = getHwAddr()


def callback(bt_addr, rssi, packet, additional_info):
    timestamp = datetime.now()
    entry = {"time": timestamp.isoformat(), "beacon_MAC": bt_addr, "pi_MAC": rpi_mac, "RSSI": rssi, "obstacle": obstacle, "transmission_power":transmission_power, "distance": distance, "direction": direction}
    data_entries.append(entry)


if __name__ == "__main__":
    scanner = BeaconScanner(callback,
        # remove the following line to see packets from all beacons
        device_filter = IBeaconFilter(minor = beacon_minor), 
        packet_filter=None
    )
    time.sleep(delay)
    print("Scan started at ", datetime.now())
    scanner.start()

    #loop that stops scanning after 30 samples are collected. 
    #uploads all entries to database after
    while True:
        if len(data_entries) == 30:
            scanner.stop()
            print("Reached 30 samples, trial completed at ", datetime.now())
            break
    try:
        x = rawcol.insert_many(data_entries)
    except Exception as e:
        print("Writing errors to db:", e)

    rssi_list = [s["RSSI"] for s in data_entries]


    meanVal = sum(rssi_list)/len(rssi_list)
    minVal = min(rssi_list)
    maxVal = max(rssi_list)
    medianVal = statistics.median(rssi_list)
    std = statistics.stdev(rssi_list)

    print ("mean rssi: ", meanVal, " minimum rssi: ", minVal, " maximum rssi: ", maxVal)
    print ("median rssi: ", medianVal, "standard deviation: ", std)

    try:
        x = avgcol.insert_one({"scenario": scenario, "mean" : meanVal, "min": minVal, "max": maxVal, "median": medianVal, "std": std})
    except Exception as e:
        print("Writing errors to db:", e)
