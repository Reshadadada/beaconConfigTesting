# BLETesting

## How to change beacon configurations
**Changing minor of a beacon**
On the BeaconSet app on your phone, click on the beacon you want to change the minor of and then choose settings. (If there are multiple and you are not sure which beacon is yours, read the mac address on the app and match it to the mac address written physically on your minew Beacon.) Click on "MINOR" and type a unique minor value that other beacons in the lab are not using. This will be the minor the program uses to scan for a specific beacon. Click "save" and then go down and click "Reboot iBeacon" and click OK after being prompted for a password.

**Changing transmission power of a beacon**
The transmission power will be shown as "Tx:" with the value next to it. An example being "Tx: -12dBm" 
Click on the beacon you want to change the transmission power of and then choose settings. (If there are multiple and you are not sure which beacon is yours, read the mac address on the app and match it to the mac address written physically on your minew Beacon.) Click on "Tranmission Power" and choose the setting you want to collect samples for next. Click "save" and then go down and click "Reboot iBeacon" and click OK after being prompted for a password.

## Python programs for running tests
### The main program recommended for testing is 'configTests.py'
Each test has a 3 second delay before scanning so that you have time to get into position after starting.
Before running any program, edit the python file and add your database ip into the 'mongo_db_uri' variable. Replace the dashes with the ip.

**configTests.py**
This program allows you to complete 4 tests (one for each direction) for a given distance.
For each test, it scans for 30 packets from a beacon then uploads each packet with scenario information to our database (in a collection titled "beaconConfig"). A summary of the trial with the mean, median, standard deviation, etc will also be added to our database in a seperate collection ("beaconConfigStats").
In order to start scanning, launch the program by typing 'python3 configTests.py' followed by your beacon minor, obstacle between anchor, distance from anchor, and transmission power. An example being 'python3 configTests.py 213 Desk 7m -8dBm'

**singularTest.py**
Allows you to specify and do only one specific test (so one given direction rather than all four).
In order to start scanning, launch the program by typing 'python3 singularTest.py' followed by your beacon minor, obstacle between anchor, distance from anchor, transmission power, and direction you are facing. An example being 'python3 singularTest.py 213 Desk 7m -8dBm N'
If there are no obstacles, type "NONE" 
For direction, type N for north, S for south, E for east, and W for west. North meaning you are facing towards the anchor, South meaning you are facing away from the anchor, and so on.
Hit Ctrl C to cancel the program if you mistype the minor value.


**completeConfigTests**
Simular to 'configTests.py' but does a test for each distance as well. In order to start scanning, launch the program by typing 'python3 completeConfigTests.py' followed by your beacon minor, obstacle between anchor, and transmission power. An example being 'python3 completeConfigTests.py 213 NONE -8dBm'
