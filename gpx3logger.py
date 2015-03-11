#!/usr/bin/env python
# coding=utf-8
""" gpx logger to create and append a gpx formatted log of gpsd data """  # <--for scale
import os
import time
import gps3
from datetime import datetime

__author__ = 'Moe'
__copyright__ = "Copyright 2015, Moe"
__license__ = "MIT"
__version__ = "0.1a"
__maintainer__ = "HA!"
__email__ = "waddagit@wadda.org"
__status__ = "Flammable"
__created__ = '11 / 03 / 2015'  # TODO: fix template generator

the_connection = gps3.GPSDSocket()
the_fix = gps3.Fix()
the_log = '/tmp/gpx3.gpx'

creation = datetime.utcnow()
fmt = '%Y-%m-%d %H:%M:%S %Z%z'
genesis = creation.strftime(fmt)

if not os.path.isfile(the_log):
    header = ('<?xml version = "1.0" encoding = "utf-8"?>\n'
              '<gpx version = "1.1" '
              'creator = "GPSD 3.9 - http://catb.org/gpsd" '
              'client = "gps3.py - http://github.com/wadda/gps3"'
              'xmlns:xsi = "http://www.w3.org/2001/XMLSchema-instance"'
              'xmlns = "http://www.topografix.com/GPX/1/1"'
              'xsi:schemaLocation = "http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">\n '
              '<metadata>\n '
              '     <time>{}\n'
              '</metadata>\n').format(genesis)
    log = open(the_log, 'w')
    log.write(header)
    log.close()

try:
    for new_data in the_connection:
        if new_data:
            the_fix.refresh(new_data)
            if not isinstance(the_fix.TPV['lat'], str):  # lat/lon might be a better determinate of when data is 'valid'
                speed = the_fix.TPV['speed']
                latitude = the_fix.TPV['lat']
                longitude = the_fix.TPV['lon']
                altitude = the_fix.TPV['alt']
                time = the_fix.TPV['time']
                mode = the_fix.TPV['mode']
                tag = the_fix.TPV['tag']

                sats = the_fix.satellites_used()
                hdop = the_fix.SKY['hdop']
                vdop = the_fix.SKY['vdop']
                pdop = the_fix.SKY['pdop']

                trackpoint = ('<trkpt lat = {} lon = {}>\n'
                              '    <ele>{}</ele>\n'
                              '    <time>{}</time>\n'
                              '    <src>GPSD tag ="{}"</src>\n'
                              '    <fix>{}</fix >\n'
                              '    <sat>{}</sat>\n'
                              '    <hdop>{}</hdop>\n'
                              '    <vdop>{}</vdop>\n'
                              '    <pdop>{}</pdop>\n'
                              '</trkpt>\n').format(latitude, longitude, altitude, time, tag, mode, sats[1], hdop, vdop,
                                                   pdop)
                addendum = open(the_log, 'a')
                addendum.write(trackpoint)
                addendum.close()

except Exception as error:
    print('Danger-Danger', error)
