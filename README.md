# README #
[![Coverage Status](https://coveralls.io/repos/wadda/gps3/badge.svg)](https://coveralls.io/r/wadda/gps3)

gps3 is a Python3 interface for gpsd.  It is backwards compatable with Python2.7

gpsd (http://www.catb.org/gpsd/) is a fabulous application/daemon for many geo-location devices.

The goal is to deliver a Python package to the Cheese Shop (https://pypi.python.org/pypi/gps3/0.11a)

![GPSD-OBJECTS.png](http://i.imgur.com/g5NvIUO.png)

### human.py for GPSD access for humans at a terminal ###
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

![Python3.5.png](http://i.imgur.com/ThZK7nt.png)   ![Python2.7.png](http://i.imgur.com/6ACJlEF.png)  

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

Similarly ***gpex3.py*** in the same directory as gps3.py creates a gpx log file at /tmp/gpx3.gpx.
```
#!bash
python3 gpex3.py
```

However, it is not currently Python2 compliant.




