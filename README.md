# README #

gps3 is a python3 interface for gpsd.

gpsd (http://www.catb.org/gpsd/) is a fabulous application that deserves a Python3 interface.

The goal is to deliver a package to the Cheese Shop (https://pypi.python.org/pypi/gps3/0.1a1) that equals the quality of the source and craftsmanship behind it.

It is a match made in heaven.
![GPSD-OBJECTS.png](https://bitbucket.org/repo/nGqxd8/images/3787208142-GPSD-OBJECTS.png)

### gps3.py from the terminal ###
```
#!bash
me@work:~/SyPy_projects/gps3$ python3 gps3.py --help
usage: gps3.py [-h] [-human] [-host HOST] [-port PORT] [-metric] [-verbose]
               [-device DEVICEPATH] [-json] [-nautical] [-imperial] [-nmea]
               [-rare] [-raw] [-scaled] [-timimg] [-split24] [-pps]

optional arguments:
  -h, --help          show this help message and exit
  -human              DEFAULT Human Friendly
  -host HOST          DEFAULT "127.0.0.1"
  -port PORT          DEFAULT 2947
  -metric             DEFAULT METRIC units
  -verbose            increases verbosity, but not that much
  -device DEVICEPATH  alternate devicepath e.g.,"/dev/ttyUSB0"
  -json               /* output as JSON objects */
  -nautical           /* output in NAUTICAL units */
  -imperial           /* output in IMPERIAL units */
  -nmea               /* output in NMEA */
  -rare               /* output of packets in hex */
  -raw                /* output of raw packets */
  -scaled             /* scale output to floats */
  -timimg             /* timing information */
  -split24            /* split AIS Type 24s */
  -pps                /* enable PPS JSON */
me@work:~/SyPy_projects/gps3$ 
```

Currently not all options are implemented or fully  functional.
Commandline execution without options is the same as using the DEFAULT option flags.

Don't have a gps to experiment?  Try
```
#!bash
python3 gps3.py -host sypy.ddns.net
```
It's not moving, but you will have the gps jitter.