#!/usr/bin/env python
# coding=utf-8
""" banana """
import os

__author__ = 'moe'
__copyright__ = "Copyright 2015, Wadda Big Deal"
__credits__ = ["Moe"]
__license__ = "MIT"
__version__ = "0.1a"
__maintainer__ = "HA!, None"
__email__ = "waddagit@wadda.org"
__status__ = "Flammable"
__created__ = '11 / 03 / 2015'  # TODO: fix template generator

import time
import gps3

the_connection = gps3.GPSDSocket()
the_fix = gps3.Fix()
the_log = '/tmp/gpx3.gpx'  # AFAIK, 'Links' call href on time events or entry/exit  Multiple href may be possible.


try:
    for new_data in the_connection:
        if new_data:
            the_fix.refresh(new_data)
        if not isinstance(the_fix.TPV['speed'], str):  # lat/lon might be a better determinate of when data is 'valid'
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

            print(latitude, longitude, altitude, time, tag, mode, sats[1], hdop, vdop, pdop)
except Exception as error:
    print(error)
