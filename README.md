#### README #####
![GPSD-OBJECTS.png](http://i.imgur.com/jm1rYT8.png)
```
GPS3 (gps3.py) is a Python 2.7-3.5 GPSD interface (http://www.catb.org/gpsd)
Defaults host='127.0.0.1', port=2947, gpsd_protocol='json'
GPS3 has two classes.
1) 'GPSDSocket' to create a socket connection and retreive the output from GPSD.
2) 'Fix' unpacks the streamed gpsd data into python dictionaries.
These dictionaries are populated from the JSON data packet sent from the GPSD.
Import           import gps3
Instantiate      gps_connection = gps3.GPSDSocket(host='192.168.0.4')
                 gps_fix = gps3.Fix()
Iterate          for new_data in gps_connection:
                     if new_data:
                        gps_fix.refresh(new_data)
Use                     print('Altitude = ',gps_fix.TPV['alt'])
                        print('Latitude = ',gps_fix.TPV['lat'])
Consult Lines 153-ff for Attribute/Key possibilities.
or http://www.catb.org/gpsd/gpsd_json.html
Run human.py; python[X] human.py [arguments] for a human experience.

```

##### human.py access demo for gps3.py, for humans at a terminal #####
```
#!bash
me@work:~/projects/gps3$ python3 human.py --help
usage: human.py [-h] [-host HOST] [-port PORT] [-device DEVICEPATH] [-json] [-nmea]
               [-rare] [-raw] [-scaled] [-timimg] [-split24] [-pps]

optional arguments:
  -h, --help          show this help message and exit
  -host HOST          DEFAULT "127.0.0.1"
  -port PORT          DEFAULT 2947
  -json               DEFAULT JSON objects */
  -device DEVICEPATH  alternate devicepath e.g.,"-device /dev/ttyUSB4"
  -nmea               */ output in NMEA */
  -rare               */ output of packets in hex */
  -raw                */ output of raw packets */
  -scaled             */ scale output to floats */
  -timimg             */ timing information */
  -split24            */ split AIS Type 24s */
  -pps                */ enable PPS JSON */
me@work:~/projects/gps3$
```
Commandline execution without options is the same as using the DEFAULT option flags.

![Python3.5.png](http://i.imgur.com/hG1cFq3.png)   ![Python2.7.png](http://i.imgur.com/gUoZfHd.png)  

Don't have a gps to experiment?   Try
```
#!bash
python3 human.py -host gps.ddns.net  # python human.py -host gps.ddns.net
```
See if a remote gpsd is running.  While it's not moving, it does return basic data.

A trivial demonstration of functionality found in
```
#!bash
python3 demo_gegps3.py  # python demo_gegps3.py
```
Presently, when placed in same directory as gps3.py, creates a keyhole (.kml) file for Google Earth (GE defaults 4 second refreshing) with age < 1 sec from refresh.
Open the generated file (/tmp/gps3_live.kml) with Google Earth and watch the jitter and track scratch that way, all day.
