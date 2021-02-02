from beacontools import BeaconScanner, EddystoneTLMFrame, EddystoneFilter, IBeaconFilter

import logging, os, sys, time
from datetime import datetime
import threading
import csv, codecs
import pymongo
from datetime import datetime, timedelta
import time, socket, fcntl, struct
import statistics

if (len(sys.argv))!=5:
    print ("Please input your beacon minor, obstacle, and transmission power after program name")
    print ("example of a valid input after program name: 123 NONE -4dBm")
    sys.exit("Usage: beacon_minor obstacle transmission_power")
beacon_minor = int(sys.argv[1])
obstacle = sys.argv[2]
distance = "0m"
transmission_power = sys.argv[4]
direction = " "
scenario = obstacle + " " +  distance + " " +  transmission_power + " " +  direction

#rssi packets and info will be stored in this list
data_entries = []
direction_list = ["North","East","West","South"]
distance_list = ["0m", "1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m"]

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
statcol = mydb["beaconConfigStats"]


def callback(bt_addr, rssi, packet, additional_info):
    timestamp = datetime.now()
    entry = {"time": timestamp.isoformat(), "beacon_MAC": bt_addr, "RSSI": rssi, "obstacle": obstacle, "transmission_power": transmission_power, "distance": distance, "direction": direction}
    data_entries.append(entry)


if __name__ == "__main__":
    for dist in distance_list:
        distance = dist
        print ("Please be ", distance, " away from the anchor")
        for direc in direction_list:
            direction = direc
            scenario = obstacle + " " +  distance + " " +  transmission_power + " " +  direction
            input("Press Enter then face " + str(direction))
            scanner = BeaconScanner(callback,
                # remove the following line to see packets from all beacons
                device_filter = IBeaconFilter(minor = beacon_minor), 
                packet_filter=None
            )
            time.sleep(3)
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
            data_entries.clear()

            meanVal = sum(rssi_list)/len(rssi_list)
            minVal = min(rssi_list)
            maxVal = max(rssi_list)
            medianVal = statistics.median(rssi_list)
            std = statistics.stdev(rssi_list)

            print ("mean rssi: ", meanVal, " maximum rssi: ", maxVal)
            print ("median rssi: ", medianVal, "standard deviation: ", std)

            try:
                x = statcol.insert_one({"scenario": scenario, "mean" : meanVal, "min": minVal, "max": maxVal, "median": medianVal, "std": std})
            except Exception as e:
                print("Writing errors to db:", e)
            rssi_list.clear()
